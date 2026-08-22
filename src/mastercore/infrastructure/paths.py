"""Path normalization and authorization.

All filesystem consumers should resolve paths through this module before I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mastercore.domain.errors import PermissionDeniedError, ValidationError


@dataclass(frozen=True, slots=True)
class PathPolicy:
    """Restricts an operation to one canonical root."""

    root: Path
    allow_symlinks: bool = False

    def canonical_root(self) -> Path:
        return self.root.expanduser().resolve(strict=False)


def resolve_authorized_path(
    candidate: str | Path,
    policy: PathPolicy,
    *,
    must_exist: bool | None = None,
    expect_file: bool | None = None,
) -> Path:
    """Normalize and authorize *candidate* below ``policy.root``.

    ``must_exist=None`` skips the existence requirement.
    ``expect_file=True`` requires a file when the path exists.
    ``expect_file=False`` requires a directory when the path exists.
    """

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


def _reject_symlink_chain(root: Path, target: Path) -> None:
    """Reject symlinks from root to the requested target.

    This intentionally checks lexical path components before final resolution,
    so a symlink cannot silently redirect an apparently safe relative path.
    """

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
