from pathlib import Path
import tempfile
import unittest

from mastercore.domain.errors import PermissionDeniedError, ValidationError
from mastercore.infrastructure.paths import PathPolicy, resolve_authorized_path


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

    def test_existing_type_can_be_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            folder = root / "folder"
            folder.mkdir()
            with self.assertRaises(ValidationError):
                resolve_authorized_path(
                    "folder",
                    PathPolicy(root),
                    must_exist=True,
                    expect_file=True,
                )

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


if __name__ == "__main__":
    unittest.main()
