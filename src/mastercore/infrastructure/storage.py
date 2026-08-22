"""Verified atomic filesystem writes with rollback and failure injection."""

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
    StorageError,
)
from mastercore.infrastructure._storage_io import (
    RollbackSnapshot,
    create_rollback_snapshot,
    create_temp_file,
    fsync_directory,
    open_verified_directory,
    replace_in_directory,
    restore_previous_state,
    revalidate_target,
    safe_close,
    sha256_file,
    unlink_in_directory,
    verify_file_in_directory,
    verify_original_state,
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
    after replacement, the previous state is restored and verified.
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
    rollback: RollbackSnapshot | None = None
    stage_name: str | None = None
    dir_fd: int | None = None
    replaced = False

    try:
        dir_fd = open_verified_directory(parent)
        revalidate_target(relative_path, target, policy, parent, dir_fd)

        if original_existed:
            rollback = create_rollback_snapshot(target, parent, dir_fd, fsync)
            if backup_hook is not None:
                backup_path = backup_hook(target)
                if backup_path is not None and not Path(backup_path).is_file():
                    raise RecoveryError(
                        f"Backup hook did not produce a readable file: {backup_path}"
                    )
                revalidate_target(relative_path, target, policy, parent, dir_fd)

        stage_name, stage_path, stage_fd = create_temp_file(parent, target.name, dir_fd)
        try:
            with os.fdopen(stage_fd, "wb") as handle:
                handle.write(data)
                handle.flush()
                if fsync:
                    os.fsync(handle.fileno())
        except BaseException:
            safe_close(stage_fd)
            raise

        _inject(fault_injector, "after_stage_write", stage_path)
        verify_file_in_directory(
            stage_name,
            parent,
            dir_fd,
            len(data),
            expected_hash,
            "staged",
        )
        _inject(fault_injector, "after_stage_validate", stage_path)

        revalidate_target(relative_path, target, policy, parent, dir_fd)
        _inject(fault_injector, "before_replace", target)
        verify_original_state(
            target.name,
            parent,
            dir_fd,
            original_existed,
            rollback,
        )
        replace_in_directory(stage_name, target.name, parent, dir_fd)
        stage_name = None
        replaced = True

        if fsync:
            fsync_directory(parent, dir_fd)

        _inject(fault_injector, "after_replace", target)
        _verify_committed_target(
            relative_path,
            target,
            policy,
            parent,
            dir_fd,
            len(data),
            expected_hash,
        )
        _inject(fault_injector, "after_final_verify", target)
        _verify_committed_target(
            relative_path,
            target,
            policy,
            parent,
            dir_fd,
            len(data),
            expected_hash,
        )

        if rollback is not None:
            unlink_in_directory(rollback.name, parent, dir_fd)
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
                restore_previous_state(
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
            unlink_in_directory(stage_name, parent, dir_fd, missing_ok=True)
        if rollback is not None:
            unlink_in_directory(rollback.name, parent, dir_fd, missing_ok=True)
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
        digest = sha256_file(source)
        backup_path = root / f"{source.name}.{digest[:12]}.bak"
        if backup_path.exists():
            if sha256_file(backup_path) != digest:
                raise DataIntegrityError(f"Existing backup hash mismatch: {backup_path}")
            return backup_path

        temp = root / f".{backup_path.name}.{secrets.token_hex(6)}.tmp"
        try:
            shutil.copy2(source, temp, follow_symlinks=False)
            if sha256_file(temp) != digest:
                raise DataIntegrityError("Backup copy failed hash verification")
            os.replace(temp, backup_path)
            return backup_path
        finally:
            temp.unlink(missing_ok=True)

    return backup


def _verify_committed_target(
    relative_path: str | Path,
    target: Path,
    policy: PathPolicy,
    parent: Path,
    dir_fd: int | None,
    expected_size: int,
    expected_hash: str,
) -> None:
    revalidate_target(relative_path, target, policy, parent, dir_fd)
    verify_file_in_directory(
        target.name,
        parent,
        dir_fd,
        expected_size,
        expected_hash,
        "final",
    )


def _inject(injector: FaultInjector | None, point: str, path: Path) -> None:
    if injector is not None:
        injector(point, path)
