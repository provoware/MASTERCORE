"""Project startup use case independent from the user interface."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from mastercore.domain.startup import EventStatus, StartupEvent
from mastercore.infrastructure.project_runtime import (
    detect_backend_command,
    ensure_virtual_environment,
    inspect_project,
    install_requirements,
    run_streamed,
)

EventHandler = Callable[[StartupEvent], None]


class StartupService:
    """Perform validate → prepare → validate → run with observable events."""

    def run(self, selected_project: str | Path, emit: EventHandler) -> None:
        try:
            emit(StartupEvent(EventStatus.INFO, "Vorprüfung", "Projektordner wird sicher geprüft."))
            project, requirements = inspect_project(selected_project)
            emit(
                StartupEvent(
                    EventStatus.PASS, "Vorprüfung", "Projektordner ist gültig und lesbar."
                )
            )

            emit(
                StartupEvent(
                    EventStatus.INFO,
                    "Abhängigkeiten",
                    "Isolierte Python-Umgebung wird geprüft.",
                )
            )
            python = ensure_virtual_environment(project)
            install_requirements(python, requirements, lambda line: self._output(line, emit))
            emit(StartupEvent(EventStatus.PASS, "Abhängigkeiten", "Abhängigkeiten sind aufgelöst."))

            command = detect_backend_command(project, python)
            emit(StartupEvent(EventStatus.PASS, "Nachprüfung", "Backend-Startpunkt ist gültig."))
            emit(StartupEvent(EventStatus.INFO, "Backend", "Backend wurde gestartet."))
            run_streamed(command, project, lambda line: self._output(line, emit))
            emit(StartupEvent(EventStatus.PASS, "Backend", "Backend wurde sauber beendet."))
        except Exception as exc:
            emit(
                StartupEvent(
                    EventStatus.FAIL,
                    "Start abgebrochen",
                    "Die Startroutine konnte nicht sicher abgeschlossen werden.",
                    "Prüfen Sie Projektordner, requirements.txt und den Backend-Startpunkt.",
                    f"{type(exc).__name__}: {exc}",
                )
            )

    @staticmethod
    def _output(line: str, emit: EventHandler) -> None:
        if line:
            emit(StartupEvent(EventStatus.INFO, "Prozessausgabe", line))
