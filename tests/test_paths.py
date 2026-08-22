from pathlib import Path
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

from mastercore.domain.errors import PermissionDeniedError, StorageLimitError, ValidationError
from mastercore.infrastructure.paths import (
    PathPolicy,
    WriteConstraints,
    resolve_authorized_path,
    validate_write_target,
)


class PathValidationTests(unittest.TestCase):
    def test_relative_path_stays_below_root(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = resolve_authorized_path("a/b.txt", PathPolicy(root))
            self.assertEqual(target, root / "a" / "b.txt")

    def test_parent_traversal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            with self.assertRaises(PermissionDeniedError):
                resolve_authorized_path("../escape.txt", PathPolicy(root))

    def test_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            outside = root.parent / f"{root.name}-outside"
            outside.mkdir(exist_ok=True)
            link = root / "link"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            try:
                with self.assertRaises(PermissionDeniedError):
                    resolve_authorized_path("link/x.txt", PathPolicy(root))
            finally:
                link.unlink(missing_ok=True)
                try:
                    outside.rmdir()
                except OSError:
                    pass

    def test_payload_size_limit_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "x.bin"
            with self.assertRaises(StorageLimitError):
                validate_write_target(target, 11, WriteConstraints(max_bytes=10))

    def test_suffix_allowlist_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "x.txt"
            with self.assertRaises(ValidationError):
                validate_write_target(
                    target,
                    1,
                    WriteConstraints(allowed_suffixes=frozenset({".json"})),
                )

    def test_free_space_reserve_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "x.bin"
            with mock.patch(
                "mastercore.infrastructure.paths.shutil.disk_usage",
                return_value=SimpleNamespace(total=100, used=90, free=10),
            ):
                with self.assertRaises(StorageLimitError):
                    validate_write_target(
                        target,
                        5,
                        WriteConstraints(min_free_bytes=10),
                    )

    @unittest.skipIf(os.name == "nt", "POSIX permission bits required")
    def test_missing_write_bits_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = root / "x.bin"
            root.chmod(0o500)
            try:
                with self.assertRaises(PermissionDeniedError):
                    validate_write_target(target, 1)
            finally:
                root.chmod(0o700)


if __name__ == "__main__":
    unittest.main()
