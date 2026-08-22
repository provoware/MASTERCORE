from pathlib import Path
import hashlib
import tempfile
import unittest

from mastercore.infrastructure.paths import PathPolicy
from mastercore.infrastructure.storage import atomic_write_text


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

    def test_existing_file_is_atomically_replaced(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = root / "value.txt"
            target.write_text("old", encoding="utf-8")
            atomic_write_text(
                "value.txt",
                "new",
                PathPolicy(root),
                fsync=False,
            )
            self.assertEqual(target.read_text(encoding="utf-8"), "new")
            self.assertEqual(list(root.glob(".*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
