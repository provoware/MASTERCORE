"""Validated Python project inspection and process execution."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from mastercore.domain.errors import ConfigurationError, PermissionDeniedError
from mastercore.infrastructure.paths import PathPolicy, resolve_authorized_path

OutputHandler = Callable[[str], None]


def inspect_project(raw_project: str | Path) -> tuple[Path, Path | None]:
    """Validate a project root and its optional requirements file."""

    selected = Path(raw_project).expanduser()
    if selected.is_symlink():
        raise PermissionDeniedError("Ein Projektordner als Verknüpfung ist nicht erlaubt.")
    project = selected.resolve(strict=True)
    if not project.is_dir():
        raise ConfigurationError("Der gewählte Projektpfad ist kein Ordner.")
    if not os.access(project, os.R_OK | os.X_OK):
        raise PermissionDeniedError("Der Projektordner ist nicht lesbar oder zugänglich.")

    requirements = resolve_authorized_path(
        "requirements.txt", PathPolicy(project), must_exist=None, expect_file=True
    )
    if not requirements.exists():
        return project, None
    if requirements.stat().st_size > 1_000_000:
        raise ConfigurationError("requirements.txt ist größer als das Sicherheitslimit von 1 MB.")
    requirements.read_text(encoding="utf-8")
    return project, requirements


def ensure_virtual_environment(project: Path) -> Path:
    """Create or validate the isolated project environment."""

    environment = resolve_authorized_path(".venv", PathPolicy(project))
    python = _environment_python(environment)
    if not python.exists():
        if not os.access(project, os.W_OK):
            raise PermissionDeniedError(
                "Für die isolierte Umgebung fehlt die Schreibberechtigung im Projektordner."
            )
        subprocess.run(
            [sys.executable, "-m", "venv", str(environment)],
            cwd=project,
            check=True,
            timeout=120,
        )
    if not python.is_file() or not os.access(python, os.X_OK):
        raise ConfigurationError("Die Python-Umgebung ist unvollständig oder nicht ausführbar.")
    return python


def install_requirements(
    python: Path, requirements: Path | None, on_output: OutputHandler
) -> None:
    """Install declared dependencies without invoking a command shell."""

    if requirements is None:
        on_output("Keine requirements.txt gefunden; Installation übersprungen.")
        return
    run_streamed(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "-r",
            str(requirements),
        ],
        requirements.parent,
        on_output,
        timeout=900,
    )


def detect_backend_command(project: Path, python: Path) -> list[str]:
    """Choose only a small set of explicit, conventional Python entry files."""

    for name in ("run.py", "main.py", "app.py"):
        candidate = resolve_authorized_path(name, PathPolicy(project), expect_file=True)
        if candidate.exists():
            return [str(python), str(candidate)]
    raise ConfigurationError(
        "Kein Backend-Startpunkt gefunden. Erwartet wird run.py, main.py oder app.py."
    )


def run_streamed(
    command: Sequence[str],
    cwd: Path,
    on_output: OutputHandler,
    *,
    timeout: int | None = None,
) -> int:
    """Run an argument-vector process and forward merged output line by line."""

    process = subprocess.Popen(
        list(command),
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    try:
        assert process.stdout is not None
        for line in process.stdout:
            on_output(line.rstrip())
        return_code = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        process.terminate()
        process.wait(timeout=10)
        raise ConfigurationError(
            f"Der Prozess überschritt das Zeitlimit von {timeout} Sekunden."
        ) from exc
    if return_code:
        raise ConfigurationError(f"Der Prozess wurde mit Fehlercode {return_code} beendet.")
    return return_code


def _environment_python(environment: Path) -> Path:
    return environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
