"""Verified atomic filesystem writes with rollback and failure-injection hooks."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
from typing import Any

from mastercore.domain.errors import (
    DataIntegrityError,
    MastercoreError,
    RecoveryError,
    SchemaValidationError,
    StateConflictError,
    StorageError,
)
from mastercore.infrastructure.paths import (
    PathPolicy,
    WriteConstraints,
    resolve_authorized_path,
    validate_write_target,
)

FaultInjector = Callable[[str, Path], None]
BackupHook = Callable[[Path], Path | None]
JsonValidator = Callable[[Any], None]


@dataclass(frozen=True, slots=True)
class WriteReceipt:
    """Evidence returned after a verified write."""

    path: Path
    size: int
    sha256: str
    backup_path: Path | None = None


@dataclass(frozen=True, slots=True)
class _RollbackSnapshot:
    name: str
    size: int
    sha256: str


def atomic_write_bytes(
    relative_path: str | Path,
    data: bytes,
    policy: PathPolicy,
    *,
    constraints: WriteConstraints | None = None,
    create_parents: bool = True,
    fsync: bool = True,
    backup_hook: BackupHook | None = None,
    fault_injector: FaultInjector | None = None,
) -> WriteReceipt:
    """Write bytes by authorize → stage → verify → replace → verify.

    Existing targets receive an internal rollback snapshot. If anything fails
    after replacement, MASTERCORE restores the original file before surfacing
    the error. ``fault_injector`` exists only for deterministic resilience tests.
    """

    target = resolve_authorized_path(relative_path, policy)
    parent = target.parent

    if create_parents:
        parent.mkdir(parents=True, exist_ok=True)
    elif not parent.is_dir():
        raise StorageError(f"Parent directory does not exist: {parent}")

    target = resolve_authorized_path(relative_path, policy)
    validate_write_target(target, len(data), constraints)

    expected_hash = hashlib.sha256(data).hexdigest()
    original_existed = target.exists()
    backup_path: Path | None = None
    rollback: _RollbackSnapshot | None = None
    stage_name: str | None = None
    dir_fd: int | None = None
    replaced = False

    try:
        dir_fd = _open_verified_directory(parent)
        _revalidate_target(relative_path, target, policy, parent, dir_fd)

        if original_existed:
            rollback = _create_rollback_snapshot(target, parent, dir_fd, fsync)
            if backup_hook is not None:
                backup_path = backup_hook(target)
                if backup_path is not None and not Path(backup_path).is_file():
                    raise RecoveryError(
                        f"Backup hook did not produce a readable file: {backup_path}"
                    )

        stage_name, stage_path, stage_fd = _create_temp_file(parent, target.name, dir_fd)
        try:
            with os.fdopen(stage_fd, "wb") as handle:
                handle.write(data)
                handle.flush()
                if fsync:
                    os.fsync(handle.fileno())
        except BaseException:
            _safe_close(stage_fd)
            raise

        _inject(fault_injector, "after_stage_write", stage_path)
        _verify_file(stage_path, len(data), expected_hash, "staged")
        _inject(fault_injector, "after_stage_validate", stage_path)

        _revalidate_target(relative_path, target, policy, parent, dir_fd)
        _inject(fault_injector, "before_replace", target)
        _verify_original_state(target, original_existed, rollback)
        _replace_in_directory(stage_name, target.name, parent, dir_fd)
        stage_name = None
        replaced = True

        if fsync:
            _fsync_directory(parent, dir_fd)

        _inject(fault_injector, "after_replace", target)
        _verify_file(target, len(data), expected_hash, "final")
        _inject(fault_injector, "after_final_verify", target)

        if rollback is not None:
            _unlink_in_directory(rollback.name, parent, dir_fd)
            rollback = None

        return WriteReceipt(
            path=target,
            size=len(data),
            sha256=expected_hash,
            backup_path=Path(backup_path) if backup_path is not None else None,
        )
    except BaseException as exc:
        recovery_error: BaseException | None = None
        if replaced:
            try:
                _restore_previous_state(
                    target=target,
                    parent=parent,
                    dir_fd=dir_fd,
                    original_existed=original_existed,
                    rollback=rollback,
                    fsync=fsync,
                )
                rollback = None
            except BaseException as restore_exc:
                recovery_error = restore_exc

        if recovery_error is not None:
            raise RecoveryError(
                f"Write failed and rollback also failed for {target}: {recovery_error}"
            ) from exc
        if isinstance(exc, MastercoreError):
            raise
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        raise StorageError(f"Atomic write failed safely for {target}: {exc}") from exc
    finally:
        if stage_name is not None:
            _unlink_in_directory(stage_name, parent, dir_fd, missing_ok=True)
        if rollback is not None:
            _unlink_in_directory(rollback.name, parent, dir_fd, missing_ok=True)
        if dir_fd is not None:
            os.close(dir_fd)


def atomic_write_text(
    relative_path: str | Path,
    text: str,
    policy: PathPolicy,
    *,
    encoding: str = "utf-8",
    constraints: WriteConstraints | None = None,
    create_parents: bool = True,
    fsync: bool = True,
    backup_hook: BackupHook | None = None,
    fault_injector: FaultInjector | None = None,
) -> WriteReceipt:
    """Encode text and delegate to the verified binary writer."""

    return atomic_write_bytes(
        relative_path,
        text.encode(encoding),
        policy,
        constraints=constraints,
        create_parents=create_parents,
        fsync=fsync,
        backup_hook=backup_hook,
        fault_injector=fault_injector,
    )


def atomic_write_json(
    relative_path: str | Path,
    payload: Any,
    policy: PathPolicy,
    *,
    validator: JsonValidator | None = None,
    constraints: WriteConstraints | None = None,
    fsync: bool = True,
    backup_hook: BackupHook | None = None,
    fault_injector: FaultInjector | None = None,
) -> WriteReceipt:
    """Validate structured data before serializing and atomically writing JSON."""

    if validator is not None:
        try:
            validator(payload)
        except MastercoreError:
            raise
        except Exception as exc:
            raise SchemaValidationError(f"JSON schema validation failed: {exc}") from exc

    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    limits = constraints or WriteConstraints(allowed_suffixes=frozenset({".json"}))
    return atomic_write_text(
        relative_path,
        text,
        policy,
        constraints=limits,
        fsync=fsync,
        backup_hook=backup_hook,
        fault_injector=fault_injector,
    )


def make_verified_backup_hook(backup_root: Path) -> BackupHook:
    """Return a verified backup hook that preserves overwritten user files."""

    root = backup_root.expanduser().resolve(strict=False)

    def backup(source: Path) -> Path:
        root.mkdir(parents=True, exist_ok=True)
        digest = _sha256_file(source)
        stem = source.name.replace(os.sep, "_")
        backup_path = root / f"{stem}.{digest[:12]}.bak"
        if backup_path.exists():
            if _sha256_file(backup_path) != digest:
                raise DataIntegrityError(f"Existing backup hash mismatch: {backup_path}")
            return backup_path
        temp = root / f".{backup_path.name}.{secrets.token_hex(6)}.tmp"
        try:
            shutil.copy2(source, temp, follow_symlinks=False)
            if _sha256_file(temp) != digest:
                raise DataIntegrityError("Backup copy failed hash verification")
            os.replace(temp, backup_path)
            return backup_path
        finally:
            temp.unlink(missing_ok=True)

    return backup


def _open_verified_directory(parent: Path) -> int | None:
    """Open and bind the parent directory where supported to reduce TOCTOU risk."""

    if os.name == "nt" or os.open not in getattr(os, "supports_dir_fd", set()):
        return None
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(parent, flags)
    except OSError as exc:
        raise StorageError(f"Cannot safely open target directory {parent}: {exc}") from exc

    try:
        descriptor_stat = os.fstat(fd)
        path_stat = os.stat(parent, follow_symlinks=False)
        if (descriptor_stat.st_dev, descriptor_stat.st_ino) != (
            path_stat.st_dev,
            path_stat.st_ino,
        ):
            raise StateConflictError(f"Target directory changed during validation: {parent}")
    except BaseException:
        os.close(fd)
        raise
    return fd


def _revalidate_target(
    relative_path: str | Path,
    expected: Path,
    policy: PathPolicy,
    parent: Path,
    dir_fd: int | None,
) -> None:
    current = resolve_authorized_path(relative_path, policy)
    if current != expected:
        raise StateConflictError(f"Target path changed during write: {expected}")
    if dir_fd is not None:
        descriptor_stat = os.fstat(dir_fd)
        path_stat = os.stat(parent, follow_symlinks=False)
        if (descriptor_stat.st_dev, descriptor_stat.st_ino) != (
            path_stat.st_dev,
            path_stat.st_ino,
        ):
            raise StateConflictError(f"Parent directory changed during write: {parent}")


def _create_temp_file(
    parent: Path,
    target_name: str,
    dir_fd: int | None,
) -> tuple[str, Path, int]:
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


def _create_rollback_snapshot(
    target: Path,
    parent: Path,
    dir_fd: int | None,
    fsync: bool,
) -> _RollbackSnapshot:
    rollback_name, rollback_path, rollback_fd = _create_temp_file(
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
        rollback_size = rollback_path.stat().st_size
        if _sha256_file(rollback_path) != rollback_hash:
            raise DataIntegrityError("Rollback snapshot failed hash verification")
        return _RollbackSnapshot(rollback_name, rollback_size, rollback_hash)
    except BaseException:
        if source_fd is not None:
            _safe_close(source_fd)
        if rollback_fd >= 0:
            _safe_close(rollback_fd)
        _unlink_in_directory(rollback_name, parent, dir_fd, missing_ok=True)
        raise


def _verify_original_state(
    target: Path,
    original_existed: bool,
    rollback: _RollbackSnapshot | None,
) -> None:
    """Detect concurrent target changes before the destructive replace."""

    if original_existed:
        if rollback is None:
            raise StateConflictError("Original file has no rollback snapshot")
        if not target.is_file():
            raise StateConflictError(f"Original target disappeared before replace: {target}")
        try:
            _verify_file(target, rollback.size, rollback.sha256, "original")
        except DataIntegrityError as exc:
            raise StateConflictError(
                f"Original target changed concurrently before replace: {target}"
            ) from exc
    elif target.exists():
        raise StateConflictError(f"New target appeared concurrently before replace: {target}")


def _restore_previous_state(
    *,
    target: Path,
    parent: Path,
    dir_fd: int | None,
    original_existed: bool,
    rollback: _RollbackSnapshot | None,
    fsync: bool,
) -> None:
    if original_existed:
        if rollback is None:
            raise RecoveryError("Rollback snapshot missing for replaced file")
        _replace_in_directory(rollback.name, target.name, parent, dir_fd)
    else:
        _unlink_in_directory(target.name, parent, dir_fd, missing_ok=True)
    if fsync:
        _fsync_directory(parent, dir_fd)


def _replace_in_directory(
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


def _unlink_in_directory(
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


def _verify_file(path: Path, expected_size: int, expected_hash: str, label: str) -> None:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise DataIntegrityError(f"Cannot inspect {label} file {path}: {exc}") from exc
    if size != expected_size:
        raise DataIntegrityError(
            f"{label.capitalize()} file size mismatch: {size} != {expected_size}"
        )
    if _sha256_file(path) != expected_hash:
        raise DataIntegrityError(f"{label.capitalize()} file hash mismatch")


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fsync_directory(path: Path, dir_fd: int | None) -> None:
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


def _inject(injector: FaultInjector | None, point: str, path: Path) -> None:
    if injector is not None:
        injector(point, path)


def _safe_close(fd: int) -> None:
    try:
        os.close(fd)
    except OSError:
        pass
