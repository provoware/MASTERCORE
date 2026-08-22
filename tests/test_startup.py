import json
import tempfile
import unittest
from pathlib import Path

from mastercore.domain.errors import ConfigurationError, PermissionDeniedError
from mastercore.domain.startup import EventStatus, StartupEvent
from mastercore.infrastructure.project_runtime import (
    detect_backend_command,
    inspect_project,
)


class StartupContractTests(unittest.TestCase):
    def test_event_is_machine_readable_and_keeps_plain_language(self) -> None:
        event = StartupEvent(EventStatus.FAIL, "Prüfung", "Nicht lesbar.", "Rechte prüfen.")
        payload = json.loads(event.to_json())
        self.assertEqual(payload["status"], "FAIL")
        self.assertEqual(payload["solution"], "Rechte prüfen.")
        self.assertTrue(payload["timestamp"])

    def test_project_and_requirements_are_validated(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            requirements = root / "requirements.txt"
            requirements.write_text("example==1.0\n", encoding="utf-8")
            project, discovered = inspect_project(root)
            self.assertEqual(project, root)
            self.assertEqual(discovered, requirements)

    def test_backend_detection_uses_virtual_environment_python(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "main.py").write_text("print('ok')\n", encoding="utf-8")
            python = root / ".venv" / "bin" / "python"
            self.assertEqual(
                detect_backend_command(root, python),
                [str(python), str(root / "main.py")],
            )

    def test_missing_backend_has_actionable_failure(self) -> None:
        with (
            tempfile.TemporaryDirectory() as raw,
            self.assertRaisesRegex(ConfigurationError, "run.py"),
        ):
            detect_backend_command(Path(raw), Path(raw) / "python")

    def test_project_root_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = root / "target"
            target.mkdir()
            link = root / "link"
            try:
                link.symlink_to(target, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            with self.assertRaises(PermissionDeniedError):
                inspect_project(link)


if __name__ == "__main__":
    unittest.main()
