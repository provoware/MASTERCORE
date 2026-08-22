import tkinter as tk
from tkinter import font as tkfont
import unittest

from mastercore.application.startup import StartupService
from mastercore.domain.startup import EventStatus, StartupEvent
from mastercore.presentation.startup_window import StartupWindow


class StartupWindowAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = tk.Tk()
        self.root.geometry("920x620+0+0")
        self.window = StartupWindow(self.root, StartupService())
        self.root.update()

    def tearDown(self) -> None:
        self.root.destroy()

    def test_initial_focus_and_keyboard_shortcuts_are_available(self) -> None:
        self.assertIs(self.root.focus_lastfor(), self.window.path_entry)
        self.assertTrue(self.root.bind("<Control-o>"))
        self.assertTrue(self.root.bind("<Control-Return>"))

    def test_primary_controls_are_keyboard_focusable(self) -> None:
        controls = (
            self.window.path_entry,
            self.window.choose_button,
            self.window.start_button,
            self.window.output,
            self.window.export_button,
        )
        for control in controls:
            self.assertEqual(str(control.cget("takefocus")), "1")

    def test_small_and_large_window_layouts_remain_inside_bounds(self) -> None:
        for width, height in ((640, 440), (1440, 900)):
            with self.subTest(width=width, height=height):
                self.root.geometry(f"{width}x{height}+0+0")
                self.root.update()
                self._assert_descendants_fit(self.root)

    def test_large_default_font_keeps_controls_visible(self) -> None:
        default_font = tkfont.nametofont("TkDefaultFont")
        original_size = int(default_font.cget("size"))
        try:
            default_font.configure(size=18)
            self.root.geometry("1024x720+0+0")
            self.root.update()
            self._assert_descendants_fit(self.root)
            self.assertTrue(self.window.start_button.winfo_viewable())
            self.assertTrue(self.window.export_button.winfo_viewable())
        finally:
            default_font.configure(size=original_size)

    def test_failure_state_is_textual_recoverable_and_not_color_only(self) -> None:
        event = StartupEvent(
            EventStatus.FAIL,
            "Backend",
            "Backend konnte nicht gestartet werden.",
            solution="Projektdatei prüfen und erneut starten.",
            details="exit_code=2",
        )
        self.window._set_busy(True)
        self.window.pending.put(event)
        self.window._drain_events()
        self.root.update_idletasks()

        self.assertFalse(self.window._busy)
        self.assertEqual(str(self.window.start_button.cget("state")), "normal")
        self.assertIn("Start fehlgeschlagen", self.window.status.get())
        output = self.window.output.get("1.0", "end")
        self.assertIn("[FAIL] Backend", output)
        self.assertIn("Lösung:", output)
        self.assertIn("Technische Details:", output)

    def test_status_vocabulary_is_visible_as_text(self) -> None:
        for status in EventStatus:
            self.window._append_event(
                StartupEvent(status, "Test", f"Status {status.value}")
            )
        output = self.window.output.get("1.0", "end")
        for status in EventStatus:
            self.assertIn(f"[{status.value}]", output)

    def _assert_descendants_fit(self, parent: tk.Misc) -> None:
        tolerance = 2
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        for child in parent.winfo_children():
            if not child.winfo_ismapped():
                continue
            self.assertGreaterEqual(child.winfo_x(), 0)
            self.assertGreaterEqual(child.winfo_y(), 0)
            self.assertLessEqual(
                child.winfo_x() + child.winfo_width(),
                parent_width + tolerance,
            )
            self.assertLessEqual(
                child.winfo_y() + child.winfo_height(),
                parent_height + tolerance,
            )
            self._assert_descendants_fit(child)


if __name__ == "__main__":
    unittest.main()
