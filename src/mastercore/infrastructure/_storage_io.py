"""Low-level descriptor-bound helpers for MASTERCORE storage writes."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import secrets

from mastercore.domain.errors import (
    DataIntegrityError,
    RecoveryError,
    StateConflictError,
    StorageError,
)
from mastercore.infrastructure.paths import PathPolicy, resolve_authorized_path


@dataclass(frozen=True, slots=True)
class RollbackSnapshot:
    """Internal verified copy of the pre-write target."""

    name: str
    size: int
    sha256: str


def open_verified_directory(parent: Path) -> int | None:
    """Bind the parent directory where supported to reduce TOCTOU risk."""

    if os.name == "nt" or os.open not in getattr(os, "supports_dir_fd", set()):
        return None
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(parent, flags)
    except OSError as exc:
        raise StorageError(f"Cannot safely open target directory {parent}: {exc}") from exc

    try:
        _assert_directory_identity(parent, fd)
    except BaseException:
        os.close(fd)
        raise
    return fd


def revalidate_target(
    relative_path: str | Path,
    expected: Path,
    policy: PathPolicy,
    parent: Path,
    dir_fd: int | None,
) -> None:
    """Re-check path authorization and bound-directory identity."""

    current = resolve_authorized_path(relative_path, policy)
    if current != expected:
        raise StateConflictError(f"Target path changed during write: {expected}")
    if dir_fd is not None:
        _assert_directory_identity(parent, dir_fd)


def create_temp_file(
    parent: Path,
    target_name: str,
    dir_fd: int | None,
) -> tuple[str, Path, int]:
    """Create a unique no-follow staging file in the bound directory."""

    for _ in range(128):
        name = f".{target_name}.{secrets.token_hex(8)}.tmp"
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        try:
            path = name if dir_fd is not None else parent / name
            fd = os.open(path, flags, 0o600, dir_fd=dir_fd)
            return name, parent / name, fd
        except FileExistsError:
            continue
        except TypeError:
            fd = os.open(parent / name, flags, 0o600)
            return name, parent / name, fd
    raise StorageError(f"Could not allocate unique stage file in {parent}")


def create_rollback_snapshot(
    target: Path,
    parent: Path,
    dir_fd: int | None,
    fsync: bool,
) -> RollbackSnapshot:
    """Copy and verify the original target before destructive replacement."""

    rollback_name, _rollback_path, rollback_fd = create_temp_file(
        parent,
        f"{target.name}.rollback",
        dir_fd,
    )
    source_flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    source_fd: int | None = None
    try:
        try:
            source_fd = os.open(
                target.name if dir_fd is not None else target,
                source_flags,
                dir_fd=dir_fd,
            )
        except TypeError:
            source_fd = os.open(target, source_flags)

        source_hash = hashlib.sha256()
        with os.fdopen(source_fd, "rb", closefd=True) as source, os.fdopen(
            rollback_fd, "wb", closefd=True
        ) as dest:
            source_fd = None
            rollback_fd = -1
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                source_hash.update(chunk)
                dest.write(chunk)
            dest.flush()
            if fsync:
                os.fsync(dest.fileno())

        rollback_hash = source_hash.hexdigest()
        rollback_size, verified_hash = file_size_and_hash(
            rollback_name,
            parent,
            dir_fd,
        )
        if verified_hash != rollback_hash:
            raise DataIntegrityError("Rollback snapshot failed hash verification")
        return RollbackSnapshot(rollback_name, rollback_size, rollback_hash)
    except BaseException:
        if source_fd is not None:
            safe_close(source_fd)
        if rollback_fd >= 0:
            safe_close(rollback_fd)
        unlink_in_directory(rollback_name, parent, dir_fd, missing_ok=True)
        raise


def verify_original_state(
    target_name: str,
    parent: Path,
    dir_fd: int | None,
    original_existed: bool,
    rollback: RollbackSnapshot | None,
) -> None:
    """Refuse to overwrite a target that changed after the snapshot."""

    if original_existed:
        if rollback is None:
            raise StateConflictError("Original file has no rollback snapshot")
        try:
            verify_file_in_directory(
                target_name,
                parent,
                dir_fd,
                rollback.size,
                rollback.sha256,
                "original",
            )
        except DataIntegrityError as exc:
            raise StateConflictError(
                f"Original target changed concurrently before replace: {parent / target_name}"
            ) from exc
    elif exists_in_directory(target_name, parent, dir_fd):
        raise StateConflictError(
            f"New target appeared concurrently before replace: {parent / target_name}"
        )


def restore_previous_state(
    *,
    target: Path,
    parent: Path,
    dir_fd: int | None,
    original_existed: bool,
    rollback: RollbackSnapshot | None,
    fsync: bool,
) -> None:
    """Restore the pre-write state and verify the recovery result."""

    if original_existed:
        if rollback is None:
            raise RecoveryError("Rollback snapshot missing for replaced file")
        replace_in_directory(rollback.name, target.name, parent, dir_fd)
        verify_file_in_directory(
            target.name,
            parent,
            dir_fd,
            rollback.size,
            rollback.sha256,
            "restored",
        )
    else:
        unlink_in_directory(target.name, parent, dir_fd, missing_ok=True)
        if exists_in_directory(target.name, parent, dir_fd):
            raise RecoveryError(f"New target could not be removed during rollback: {target}")
    if fsync:
        fsync_directory(parent, dir_fd)


def replace_in_directory(
    source: str,
    destination: str,
    parent: Path,
    dir_fd: int | None,
) -> None:
    try:
        if dir_fd is not None:
            os.replace(source, destination, src_dir_fd=dir_fd, dst_dir_fd=dir_fd)
        else:
            os.replace(parent / source, parent / destination)
    except (TypeError, NotImplementedError):
        os.replace(parent / source, parent / destination)


def unlink_in_directory(
    name: str,
    parent: Path,
    dir_fd: int | None,
    *,
    missing_ok: bool = False,
) -> None:
    try:
        if dir_fd is not None:
            os.unlink(name, dir_fd=dir_fd)
        else:
            (parent / name).unlink()
    except FileNotFoundError:
        if not missing_ok:
            raise
    except (TypeError, NotImplementedError):
        try:
            (parent / name).unlink()
        except FileNotFoundError:
            if not missing_ok:
                raise


def verify_file_in_directory(
    name: str,
    parent: Path,
    dir_fd: int | None,
    expected_size: int,
    expected_hash: str,
    label: str,
) -> None:
    try:
        size, digest = file_size_and_hash(name, parent, dir_fd)
    except OSError as exc:
        raise DataIntegrityError(
            f"Cannot inspect {label} file {parent / name}: {exc}"
        ) from exc
    if size != expected_size:
        raise DataIntegrityError(
            f"{label.capitalize()} file size mismatch: {size} != {expected_size}"
        )
    if digest != expected_hash:
        raise DataIntegrityError(f"{label.capitalize()} file hash mismatch")


def file_size_and_hash(
    name: str,
    parent: Path,
    dir_fd: int | None,
    chunk_size: int = 1024 * 1024,
) -> tuple[int, str]:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    path = name if dir_fd is not None else parent / name
    try:
        fd = os.open(path, flags, dir_fd=dir_fd)
    except TypeError:
        fd = os.open(parent / name, flags)
    digest = hashlib.sha256()
    with os.fdopen(fd, "rb", closefd=True) as handle:
        size = os.fstat(handle.fileno()).st_size
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return size, digest.hexdigest()


def exists_in_directory(name: str, parent: Path, dir_fd: int | None) -> bool:
    try:
        if dir_fd is not None:
            os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
        else:
            os.stat(parent / name, follow_symlinks=False)
        return True
    except FileNotFoundError:
        return False
    except (TypeError, NotImplementedError):
        return (parent / name).exists()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fsync_directory(path: Path, dir_fd: int | None) -> None:
    if dir_fd is not None:
        try:
            os.fsync(dir_fd)
        except OSError:
            pass
        return
    flags = getattr(os, "O_DIRECTORY", 0) | os.O_RDONLY
    try:
        fd = os.open(path, flags)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def safe_close(fd: int) -> None:
    try:
        os.close(fd)
    except OSError:
        pass


def _assert_directory_identity(parent: Path, dir_fd: int) -> None:
    descriptor_stat = os.fstat(dir_fd)
    path_stat = os.stat(parent, follow_symlinks=False)
    if (descriptor_stat.st_dev, descriptor_stat.st_ino) != (
        path_stat.st_dev,
        path_stat.st_ino,
    ):
        raise StateConflictError(f"Parent directory changed during write: {parent}")
