import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from mastercore.domain.errors import (
    DataIntegrityError,
    PermissionDeniedError,
    SchemaValidationError,
    StateConflictError,
    StorageError,
)
from mastercore.infrastructure.paths import PathPolicy, WriteConstraints
from mastercore.infrastructure.storage import (
    atomic_write_json,
    atomic_write_text,
    make_verified_backup_hook,
)


class AtomicStorageTests(unittest.TestCase):
    def test_write_returns_verified_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            receipt = atomic_write_text(
                "nested/example.txt",
                "MASTERCORE",
                PathPolicy(root),
                fsync=False,
            )
            expected = hashlib.sha256(b"MASTERCORE").hexdigest()
            self.assertEqual(receipt.sha256, expected)
            self.assertEqual(receipt.size, len(b"MASTERCORE"))
            self.assertEqual(receipt.path.read_text(encoding="utf-8"), "MASTERCORE")

    def test_existing_file_is_atomically_replaced_without_temp_leaks(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = root / "value.txt"
            target.write_text("old", encoding="utf-8")
            atomic_write_text("value.txt", "new", PathPolicy(root), fsync=False)
            self.assertEqual(target.read_text(encoding="utf-8"), "new")
            self.assertEqual(list(root.glob(".*.tmp")), [])

    def test_interrupted_write_before_replace_keeps_original(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = root / "value.txt"
            target.write_text("old", encoding="utf-8")

            def fail(point: str, _path: Path) -> None:
                if point == "before_replace":
                    raise StorageError("injected interruption")

            with self.assertRaises(StorageError):
                atomic_write_text(
                    "value.txt",
                    "new",
                    PathPolicy(root),
                    fsync=False,
                    fault_injector=fail,
                )
            self.assertEqual(target.read_text(encoding="utf-8"), "old")
            self.assertEqual(list(root.glob(".*.tmp")), [])

    def test_failure_after_replace_rolls_back_original(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = root / "value.txt"
            target.write_text("old", encoding="utf-8")

            def fail(point: str, _path: Path) -> None:
                if point == "after_replace":
                    raise StorageError("injected post-commit failure")

            with self.assertRaises(StorageError):
                atomic_write_text(
                    "value.txt",
                    "new",
                    PathPolicy(root),
                    fsync=False,
                    fault_injector=fail,
                )
            self.assertEqual(target.read_text(encoding="utf-8"), "old")
            self.assertEqual(list(root.glob(".*.tmp")), [])

    def test_failure_after_new_file_replace_removes_partial_result(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)

            def fail(point: str, _path: Path) -> None:
                if point == "after_replace":
                    raise StorageError("injected")

            with self.assertRaises(StorageError):
                atomic_write_text(
                    "new.txt",
                    "new",
                    PathPolicy(root),
                    fsync=False,
                    fault_injector=fail,
                )
            self.assertFalse((root / "new.txt").exists())

    def test_concurrent_change_before_replace_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = root / "value.txt"
            target.write_text("old", encoding="utf-8")

            def external_change(point: str, path: Path) -> None:
                if point == "before_replace":
                    path.write_text("external", encoding="utf-8")

            with self.assertRaises(StateConflictError):
                atomic_write_text(
                    "value.txt",
                    "new",
                    PathPolicy(root),
                    fsync=False,
                    fault_injector=external_change,
                )
            self.assertEqual(target.read_text(encoding="utf-8"), "external")

    def test_concurrent_creation_of_new_target_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = root / "value.txt"

            def external_create(point: str, path: Path) -> None:
                if point == "before_replace":
                    path.write_text("external", encoding="utf-8")

            with self.assertRaises(StateConflictError):
                atomic_write_text(
                    "value.txt",
                    "new",
                    PathPolicy(root),
                    fsync=False,
                    fault_injector=external_create,
                )
            self.assertEqual(target.read_text(encoding="utf-8"), "external")

    def test_corrupted_stage_is_detected_before_replace(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = root / "value.txt"
            target.write_text("old", encoding="utf-8")

            def corrupt(point: str, path: Path) -> None:
                if point == "after_stage_write":
                    path.write_bytes(b"corrupt")

            with self.assertRaises(DataIntegrityError):
                atomic_write_text(
                    "value.txt",
                    "new",
                    PathPolicy(root),
                    fsync=False,
                    fault_injector=corrupt,
                )
            self.assertEqual(target.read_text(encoding="utf-8"), "old")

    def test_corrupted_final_file_is_detected_and_original_restored(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = root / "value.txt"
            target.write_text("old", encoding="utf-8")

            def corrupt(point: str, path: Path) -> None:
                if point == "after_replace":
                    path.write_bytes(b"corrupt")

            with self.assertRaises(DataIntegrityError):
                atomic_write_text(
                    "value.txt",
                    "new",
                    PathPolicy(root),
                    fsync=False,
                    fault_injector=corrupt,
                )
            self.assertEqual(target.read_text(encoding="utf-8"), "old")

    @unittest.skipIf(os.name == "nt", "dir-fd TOCTOU defense is POSIX-specific")
    def test_parent_swap_during_replace_does_not_write_into_swapped_directory(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            root = base / "root"
            moved = base / "root-moved"
            root.mkdir()
            target = root / "value.txt"
            target.write_text("old", encoding="utf-8")

            def swap_parent(point: str, _path: Path) -> None:
                if point == "before_replace":
                    root.rename(moved)
                    root.mkdir()

            with self.assertRaises(StateConflictError):
                atomic_write_text(
                    "value.txt",
                    "new",
                    PathPolicy(root),
                    fsync=False,
                    fault_injector=swap_parent,
                )
            self.assertFalse((root / "value.txt").exists())
            self.assertEqual((moved / "value.txt").read_text(encoding="utf-8"), "old")

    @unittest.skipIf(os.name == "nt", "POSIX permission bits required")
    def test_atomic_write_rejects_directory_without_write_bits(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            root.chmod(0o500)
            try:
                with self.assertRaises(PermissionDeniedError):
                    atomic_write_text("blocked.txt", "x", PathPolicy(root), fsync=False)
            finally:
                root.chmod(0o700)
            self.assertFalse((root / "blocked.txt").exists())

    def test_backup_hook_preserves_previous_version(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "data"
            backups = Path(raw) / "backups"
            root.mkdir()
            target = root / "value.txt"
            target.write_text("old", encoding="utf-8")
            receipt = atomic_write_text(
                "value.txt",
                "new",
                PathPolicy(root),
                fsync=False,
                backup_hook=make_verified_backup_hook(backups),
            )
            self.assertIsNotNone(receipt.backup_path)
            assert receipt.backup_path is not None
            self.assertEqual(receipt.backup_path.read_text(encoding="utf-8"), "old")
            self.assertEqual(target.read_text(encoding="utf-8"), "new")

    def test_json_validator_runs_before_write(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)

            def validate(payload: object) -> None:
                if not isinstance(payload, dict) or "version" not in payload:
                    raise ValueError("version missing")

            with self.assertRaises(SchemaValidationError):
                atomic_write_json(
                    "config.json",
                    {"wrong": True},
                    PathPolicy(root),
                    validator=validate,
                    fsync=False,
                )
            self.assertFalse((root / "config.json").exists())

            atomic_write_json(
                "config.json",
                {"version": 1},
                PathPolicy(root),
                validator=validate,
                fsync=False,
            )
            parsed = json.loads((root / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(parsed, {"version": 1})

    def test_size_constraint_fails_before_file_creation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            with self.assertRaises(StorageError):
                atomic_write_text(
                    "too-big.txt",
                    "12345",
                    PathPolicy(root),
                    constraints=WriteConstraints(max_bytes=4),
                    fsync=False,
                )
            self.assertFalse((root / "too-big.txt").exists())


if __name__ == "__main__":
    unittest.main()
