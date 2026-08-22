"""Verified atomic filesystem writes."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import tempfile

from mastercore.domain.errors import DataIntegrityError, StorageError
from mastercore.infrastructure.paths import PathPolicy, resolve_authorized_path


@dataclass(frozen=True, slots=True)
class WriteReceipt:
    """Evidence returned after a verified write."""

    path: Path
    size: int
    sha256: str


def atomic_write_bytes(
    relative_path: str | Path,
    data: bytes,
    policy: PathPolicy,
    *,
    create_parents: bool = True,
    fsync: bool = True,
) -> WriteReceipt:
    """Write bytes by stage → validate → atomic replace → verify."""

    target = resolve_authorized_path(relative_path, policy)
    parent = target.parent

    if create_parents:
        parent.mkdir(parents=True, exist_ok=True)
    elif not parent.is_dir():
        raise StorageError(f"Parent directory does not exist: {parent}")

    expected_hash = hashlib.sha256(data).hexdigest()
    temp_path: Path | None = None

    try:
        fd, raw_temp = tempfile.mkstemp(
            prefix=f".{target.name}.",
            suffix=".tmp",
            dir=parent,
        )
        temp_path = Path(raw_temp)
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            if fsync:
                os.fsync(handle.fileno())

        if temp_path.stat().st_size != len(data):
            raise DataIntegrityError("Staged file size does not match input.")

        staged_hash = _sha256_file(temp_path)
        if staged_hash != expected_hash:
            raise DataIntegrityError("Staged file hash does not match input.")

        os.replace(temp_path, target)
        temp_path = None

        if fsync:
            _fsync_directory(parent)

        final_size = target.stat().st_size
        final_hash = _sha256_file(target)
        if final_size != len(data) or final_hash != expected_hash:
            raise DataIntegrityError("Final file failed post-write verification.")

        return WriteReceipt(path=target, size=final_size, sha256=final_hash)
    except (OSError, DataIntegrityError) as exc:
        if isinstance(exc, DataIntegrityError):
            raise
        raise StorageError(f"Atomic write failed for {target}: {exc}") from exc
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass


def atomic_write_text(
    relative_path: str | Path,
    text: str,
    policy: PathPolicy,
    *,
    encoding: str = "utf-8",
    create_parents: bool = True,
    fsync: bool = True,
) -> WriteReceipt:
    """Encode text and delegate to the verified binary writer."""

    return atomic_write_bytes(
        relative_path,
        text.encode(encoding),
        policy,
        create_parents=create_parents,
        fsync=fsync,
    )


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fsync_directory(path: Path) -> None:
    """Best-effort directory metadata sync on platforms that support it."""

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
