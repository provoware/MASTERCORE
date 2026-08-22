"""Path normalization, authorization and write-capability checks.

All filesystem consumers should resolve paths through this module before I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import stat

from mastercore.domain.errors import (
    PermissionDeniedError,
    StorageLimitError,
    ValidationError,
)


@dataclass(frozen=True, slots=True)
class PathPolicy:
    """Restricts an operation to one canonical root."""

    root: Path
    allow_symlinks: bool = False

    def canonical_root(self) -> Path:
        return self.root.expanduser().resolve(strict=False)


@dataclass(frozen=True, slots=True)
class WriteConstraints:
    """Operation-specific limits applied before filesystem mutation."""

    max_bytes: int | None = None
    min_free_bytes: int = 0
    allowed_suffixes: frozenset[str] | None = None

    def __post_init__(self) -> None:
        if self.max_bytes is not None and self.max_bytes < 0:
            raise ValueError("max_bytes must be >= 0")
        if self.min_free_bytes < 0:
            raise ValueError("min_free_bytes must be >= 0")


def resolve_authorized_path(
    candidate: str | Path,
    policy: PathPolicy,
    *,
    must_exist: bool | None = None,
    expect_file: bool | None = None,
) -> Path:
    """Normalize and authorize *candidate* below ``policy.root``."""

    root = policy.canonical_root()
    raw = Path(candidate).expanduser()
    target = raw if raw.is_absolute() else root / raw
    canonical = target.resolve(strict=False)

    try:
        canonical.relative_to(root)
    except ValueError as exc:
        raise PermissionDeniedError(
            f"Path escapes authorized root: {canonical}"
        ) from exc

    if not policy.allow_symlinks:
        _reject_symlink_chain(root, target)

    exists = canonical.exists()
    if must_exist is True and not exists:
        raise ValidationError(f"Path does not exist: {canonical}")
    if must_exist is False and exists:
        raise ValidationError(f"Path already exists: {canonical}")

    if exists and expect_file is True and not canonical.is_file():
        raise ValidationError(f"Expected file: {canonical}")
    if exists and expect_file is False and not canonical.is_dir():
        raise ValidationError(f"Expected directory: {canonical}")

    return canonical


def validate_write_target(
    target: Path,
    data_size: int,
    constraints: WriteConstraints | None = None,
) -> None:
    """Validate size, suffix, permission and free-space constraints."""

    limits = constraints or WriteConstraints()
    if limits.max_bytes is not None and data_size > limits.max_bytes:
        raise StorageLimitError(
            f"Payload size {data_size} exceeds limit {limits.max_bytes} bytes"
        )

    if limits.allowed_suffixes is not None:
        normalized = {suffix.lower() for suffix in limits.allowed_suffixes}
        if target.suffix.lower() not in normalized:
            raise ValidationError(
                f"File suffix {target.suffix or '<none>'} is not allowed"
            )

    parent = target.parent
    if not parent.is_dir():
        raise ValidationError(f"Parent directory does not exist: {parent}")
    _assert_directory_writable(parent)

    required_free = data_size + limits.min_free_bytes
    try:
        free = shutil.disk_usage(parent).free
    except OSError as exc:
        raise PermissionDeniedError(
            f"Cannot inspect free space for {parent}: {exc}"
        ) from exc
    if free < required_free:
        raise StorageLimitError(
            f"Insufficient free space: need {required_free}, available {free}"
        )


def _assert_directory_writable(path: Path) -> None:
    """Fail early for directories without any write bit or access permission."""

    try:
        mode = path.stat().st_mode
    except OSError as exc:
        raise PermissionDeniedError(f"Cannot inspect directory permissions: {path}") from exc

    if os.name != "nt":
        write_bits = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
        if mode & write_bits == 0:
            raise PermissionDeniedError(f"Directory has no write permission: {path}")
    if not os.access(path, os.W_OK):
        raise PermissionDeniedError(f"Directory is not writable: {path}")


def _reject_symlink_chain(root: Path, target: Path) -> None:
    """Reject symlinks from root to the requested target."""

    root = root.resolve(strict=False)
    lexical = target if target.is_absolute() else root / target
    try:
        relative = lexical.relative_to(root)
    except ValueError:
        return

    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise PermissionDeniedError(f"Symlink is not allowed: {current}")
