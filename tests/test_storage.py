import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from mastercore.domain.errors import SchemaValidationError, StorageError
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
