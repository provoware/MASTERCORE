"""Accessible single-window desktop presentation for project startup."""

from __future__ import annotations

import json
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from mastercore.application.startup import StartupService
from mastercore.domain.startup import EventStatus, StartupEvent
from mastercore.infrastructure.paths import PathPolicy
from mastercore.infrastructure.storage import atomic_write_text

COLORS = {
    EventStatus.INFO: "#1f5f99",
    EventStatus.PASS: "#18733c",
    EventStatus.WARN: "#8a5a00",
    EventStatus.FAIL: "#b42318",
}


class StartupWindow:
    """Keep selection, progress, guidance and diagnostics in one window."""

    def __init__(self, root: tk.Tk, service: StartupService) -> None:
        self.root = root
        self.service = service
        self.events: list[StartupEvent] = []
        self.pending: queue.Queue[StartupEvent] = queue.Queue()
        self.project = tk.StringVar(value=str(Path.cwd()))
        self.status = tk.StringVar(value="Bereit. Wählen Sie einen Projektordner.")
        self._busy = False
        self._build()
        self.root.after(100, self._drain_events)

    def _build(self) -> None:
        self.root.title("MASTERCORE – Sicher starten")
        self.root.geometry("920x620")
        self.root.minsize(640, 440)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        controls = ttk.Frame(self.root, padding=16)
        controls.grid(row=0, column=0, sticky="ew")
        controls.columnconfigure(1, weight=1)
        ttk.Label(controls, text="Projektordner:").grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 8),
        )
        self.path_entry = ttk.Entry(
            controls,
            textvariable=self.project,
            takefocus=True,
        )
        self.path_entry.grid(row=0, column=1, sticky="ew")
        self.choose_button = ttk.Button(
            controls,
            text="Ordner wählen…",
            command=self._choose,
            takefocus=True,
        )
        self.choose_button.grid(row=0, column=2, padx=8)
        self.start_button = ttk.Button(
            controls,
            text="Prüfen und starten",
            command=self._start,
            takefocus=True,
        )
        self.start_button.grid(row=0, column=3)

        output_frame = ttk.LabelFrame(
            self.root,
            text="Ereignisse und Lösungen",
            padding=8,
        )
        output_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 8))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        self.output = tk.Text(
            output_frame,
            wrap="word",
            state="disabled",
            padx=8,
            pady=8,
            takefocus=True,
        )
        self.output.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(output_frame, command=self.output.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.output.configure(yscrollcommand=scrollbar.set)
        for state, color in COLORS.items():
            self.output.tag_configure(state.value, foreground=color)

        footer = ttk.Frame(self.root, padding=(16, 0, 16, 16))
        footer.grid(row=2, column=0, sticky="ew")
        footer.columnconfigure(0, weight=1)
        ttk.Label(footer, textvariable=self.status).grid(row=0, column=0, sticky="w")
        self.export_button = ttk.Button(
            footer,
            text="JSON-Protokoll speichern…",
            command=self._export,
            takefocus=True,
        )
        self.export_button.grid(row=0, column=1)
        self.root.bind("<Control-o>", lambda _event: self._choose())
        self.root.bind("<Control-Return>", lambda _event: self._start())
        self.path_entry.focus_set()

    def _choose(self) -> None:
        selected = filedialog.askdirectory(title="Projektordner auswählen")
        if selected:
            self.project.set(selected)

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        self.start_button.configure(state="disabled" if busy else "normal")

    def _start(self) -> None:
        if self._busy:
            return
        self.events.clear()
        self._clear_output()
        self._set_busy(True)
        self.status.set("Start läuft. Bitte warten…")
        threading.Thread(
            target=self.service.run,
            args=(self.project.get(), self.pending.put),
            daemon=True,
        ).start()

    def _drain_events(self) -> None:
        while True:
            try:
                event = self.pending.get_nowait()
            except queue.Empty:
                break
            self.events.append(event)
            self._append_event(event)
            if event.status in {EventStatus.FAIL, EventStatus.PASS} and event.step == "Backend":
                self._set_busy(False)
            if event.status is EventStatus.FAIL:
                self._set_busy(False)
                self.status.set(
                    "Start fehlgeschlagen. Lösung und Details stehen im Protokoll."
                )
            else:
                self.status.set(f"{event.status.value}: {event.message}")
        self.root.after(100, self._drain_events)

    def _append_event(self, event: StartupEvent) -> None:
        lines = [f"[{event.status.value}] {event.step}: {event.message}"]
        if event.solution:
            lines.append(f"Lösung: {event.solution}")
        if event.details:
            lines.append(f"Technische Details: {event.details}")
        self.output.configure(state="normal")
        self.output.insert("end", "\n".join(lines) + "\n\n", event.status.value)
        self.output.see("end")
        self.output.configure(state="disabled")

    def _clear_output(self) -> None:
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")

    def _export(self) -> None:
        if not self.events:
            messagebox.showinfo("Noch kein Protokoll", "Starten Sie zuerst eine Prüfung.")
            return
        selected = filedialog.asksaveasfilename(
            title="JSON-Protokoll speichern",
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
        )
        if not selected:
            return
        target = Path(selected).expanduser().resolve(strict=False)
        payload = json.dumps(
            [json.loads(event.to_json()) for event in self.events],
            ensure_ascii=False,
            indent=2,
        )
        atomic_write_text(target.name, payload + "\n", PathPolicy(target.parent))
        messagebox.showinfo(
            "Gespeichert",
            "Das maschinenlesbare Protokoll wurde sicher gespeichert.",
        )


def run_window() -> None:
    root = tk.Tk()
    StartupWindow(root, StartupService())
    root.mainloop()
