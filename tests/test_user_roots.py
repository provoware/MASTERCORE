from pathlib import Path
import tempfile
import unittest

from mastercore.domain.data_classes import DataClass
from mastercore.domain.errors import ConfigurationError
from mastercore.infrastructure.user_roots import resolve_user_roots


class UserRootTests(unittest.TestCase):
    def test_linux_xdg_roots_are_separated(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            home = Path(raw)
            env = {
                "XDG_CONFIG_HOME": str(home / "cfg"),
                "XDG_DATA_HOME": str(home / "data"),
                "XDG_CACHE_HOME": str(home / "cache"),
                "XDG_STATE_HOME": str(home / "state"),
            }
            roots = resolve_user_roots(home=home, env=env, platform="linux")
            self.assertEqual(roots.config, home / "cfg" / "MASTERCORE")
            self.assertEqual(roots.content, home / "data" / "MASTERCORE" / "content")
            self.assertEqual(roots.cache, home / "cache" / "MASTERCORE")
            self.assertEqual(roots.logs, home / "state" / "MASTERCORE" / "logs")
            self.assertEqual(roots.backups, home / "data" / "MASTERCORE" / "backups")

    def test_windows_roots_use_roaming_and_local(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            home = Path(raw)
            env = {
                "APPDATA": str(home / "roaming"),
                "LOCALAPPDATA": str(home / "local"),
            }
            roots = resolve_user_roots(home=home, env=env, platform="win32")
            self.assertEqual(roots.config, home / "roaming" / "MASTERCORE")
            self.assertEqual(roots.content, home / "local" / "MASTERCORE" / "content")

    def test_data_classes_map_to_separate_mutable_roots(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            roots = resolve_user_roots(home=Path(raw), env={}, platform="linux")
            self.assertEqual(roots.for_data_class(DataClass.USER_CONFIG), roots.config)
            self.assertEqual(roots.for_data_class(DataClass.USER_CONTENT), roots.content)
            self.assertEqual(roots.for_data_class(DataClass.DERIVED_DATA), roots.cache)
            self.assertEqual(roots.for_data_class(DataClass.OPERATIONAL_DATA), roots.logs)
            self.assertEqual(roots.for_data_class(DataClass.RECOVERY_DATA), roots.backups)
            with self.assertRaises(ConfigurationError):
                roots.for_data_class(DataClass.IMMUTABLE_APP_DATA)

    def test_ensure_creates_mutable_roots(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            home = Path(raw)
            roots = resolve_user_roots(home=home, env={}, platform="linux")
            roots.ensure()
            self.assertTrue(all(path.is_dir() for path in roots.all()))

    def test_app_name_cannot_escape(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            with self.assertRaises(ConfigurationError):
                resolve_user_roots("../escape", home=Path(raw), env={}, platform="linux")


if __name__ == "__main__":
    unittest.main()
