"""MASTERCORE G0-G8 quality gate engine."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from time import perf_counter

ENGINE_VERSION = "2.2.0"
OUTPUT_LIMIT = 20_000
CI_REQUIRED_GATES = frozenset({"G0", "G1", "G2", "G3", "G4", "G5", "G7"})


class GateStatus(StrEnum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    NOT_RUN = "NOT_RUN"


@dataclass(frozen=True, slots=True)
class CommandEvidence:
    command: tuple[str, ...]
    return_code: int | None
    duration_ms: int
    stdout: str
    stderr: str

    @property
    def passed(self) -> bool:
        return self.return_code == 0

    def as_dict(self) -> dict[str, object]:
        return {
            "command": list(self.command),
            "return_code": self.return_code,
            "duration_ms": self.duration_ms,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


@dataclass(frozen=True, slots=True)
class GateResult:
    gate: str
    name: str
    status: GateStatus
    summary: str
    evidence: tuple[CommandEvidence, ...] = ()
    details: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "gate": self.gate,
            "name": self.name,
            "status": self.status.value,
            "summary": self.summary,
            "evidence": [item.as_dict() for item in self.evidence],
            "details": list(self.details),
        }


@dataclass(frozen=True, slots=True)
class QualityReport:
    profile: str
    overall_status: GateStatus
    required_gates: frozenset[str]
    gates: tuple[GateResult, ...]
    generated_at: str

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "engine_version": ENGINE_VERSION,
            "generated_at": self.generated_at,
            "profile": self.profile,
            "overall_status": self.overall_status.value,
            "required_gates": sorted(self.required_gates),
            "gates": [gate.as_dict() for gate in self.gates],
        }


def aggregate_status(
    gates: tuple[GateResult, ...],
    required_gates: frozenset[str],
) -> GateStatus:
    selected = [gate for gate in gates if gate.gate in required_gates]
    if len(selected) != len(required_gates):
        return GateStatus.FAIL
    if any(
        gate.status in {GateStatus.FAIL, GateStatus.NOT_RUN}
        for gate in selected
    ):
        return GateStatus.FAIL
    if any(gate.status is GateStatus.WARN for gate in selected):
        return GateStatus.WARN
    return GateStatus.PASS


def run_quality_gates(repo: Path, *, profile: str = "ci") -> QualityReport:
    root = repo.resolve(strict=True)
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(root / "src")

    gates = (
        _g0(root),
        _command_gate(
            "G1",
            "Static",
            root,
            environment,
            (
                (
                    sys.executable,
                    "-m",
                    "compileall",
                    "-q",
                    "src",
                    "tools",
                    "tests",
                ),
                (
                    "ruff",
                    "check",
                    "--output-format",
                    "concise",
                    "src",
                    "tools",
                    "tests",
                ),
                ("mypy", "src/mastercore"),
            ),
        ),
        _test_gate("G2", "Functional", root, environment, "test_startup.py"),
        _multi_test_gate(
            "G3",
            "Negative",
            root,
            environment,
            ("test_paths.py", "test_storage_failures.py"),
        ),
        _multi_test_gate(
            "G4",
            "Data Integrity",
            root,
            environment,
            ("test_storage.py", "test_contract.py"),
        ),
        _test_gate(
            "G5",
            "Recovery",
            root,
            environment,
            "test_storage_failures.py",
        ),
        GateResult(
            "G6",
            "UI / Accessibility",
            GateStatus.NOT_RUN,
            "No automated UI acceptance harness configured yet.",
        ),
        _test_gate("G7", "Regression", root, environment, "test_*.py"),
        GateResult(
            "G8",
            "Release",
            GateStatus.NOT_RUN,
            "Release artifact validation is outside the normal PR profile.",
        ),
    )
    required = (
        CI_REQUIRED_GATES
        if profile == "ci"
        else frozenset({"G0", "G1"})
    )
    return QualityReport(
        profile=profile,
        overall_status=aggregate_status(gates, required),
        required_gates=required,
        gates=gates,
        generated_at=datetime.now(UTC).isoformat(),
    )


def write_json_evidence(report: QualityReport, destination: Path) -> None:
    target = destination.resolve(strict=False)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.tmp")
    payload = json.dumps(
        report.as_dict(),
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    temporary.write_text(payload + "\n", encoding="utf-8")
    os.replace(temporary, target)


def _g0(repo: Path) -> GateResult:
    failures = validate_repository_contract(repo)
    if failures:
        return GateResult(
            "G0",
            "Scope / Contract",
            GateStatus.FAIL,
            "Repository contract is inconsistent.",
            details=tuple(failures),
        )
    return GateResult(
        "G0",
        "Scope / Contract",
        GateStatus.PASS,
        "Repository contract and mandatory structure are consistent.",
    )


def validate_repository_contract(repo: Path) -> list[str]:
    failures: list[str] = []
    required = (
        "AGENTS.md",
        "README.md",
        "INPUT_FUER_TODO.md",
        "quality-contract.json",
        "docs/GLOBAL_STANDARDS.md",
        "docs/QUALITY_GATES.md",
        "docs/DATA_STORAGE_CONTRACT.md",
        "docs/PATCH_AND_VALIDATION_PROTOCOL.md",
        "docs/UI_UX_ACCESSIBILITY_STANDARD.md",
        "docs/RELEASE_GOVERNANCE.md",
        "pyproject.toml",
        ".github/workflows/quality.yml",
    )
    for relative in required:
        if not (repo / relative).is_file():
            failures.append(f"missing required file: {relative}")

    try:
        contract = json.loads(
            (repo / "quality-contract.json").read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"quality-contract unreadable: {exc}")
        return failures

    if set(contract.get("validation_statuses", [])) != {
        "PASS",
        "WARN",
        "FAIL",
        "NOT_RUN",
    }:
        failures.append("validation_statuses are incomplete or inconsistent")
    if len(contract.get("quality_gates", [])) != 9:
        failures.append("quality_gates must contain G0-G8 concepts")
    return failures


def _test_gate(
    gate: str,
    name: str,
    repo: Path,
    environment: dict[str, str],
    pattern: str,
) -> GateResult:
    command = (
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        pattern,
        "-v",
    )
    return _command_gate(gate, name, repo, environment, (command,))


def _multi_test_gate(
    gate: str,
    name: str,
    repo: Path,
    environment: dict[str, str],
    patterns: tuple[str, ...],
) -> GateResult:
    commands = tuple(
        (
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            pattern,
            "-v",
        )
        for pattern in patterns
    )
    return _command_gate(gate, name, repo, environment, commands)


def _command_gate(
    gate: str,
    name: str,
    repo: Path,
    environment: dict[str, str],
    commands: tuple[tuple[str, ...], ...],
) -> GateResult:
    evidence = tuple(
        _run_command(command, repo, environment)
        for command in commands
    )
    if any(item.return_code is None for item in evidence):
        return GateResult(
            gate,
            name,
            GateStatus.NOT_RUN,
            "A required tool is unavailable.",
            evidence=evidence,
        )

    failed = [item for item in evidence if not item.passed]
    if failed:
        return GateResult(
            gate,
            name,
            GateStatus.FAIL,
            f"{len(failed)} of {len(evidence)} checks failed.",
            evidence=evidence,
        )
    return GateResult(
        gate,
        name,
        GateStatus.PASS,
        f"{len(evidence)} of {len(evidence)} checks passed.",
        evidence=evidence,
    )


def _run_command(
    command: tuple[str, ...],
    repo: Path,
    environment: dict[str, str],
) -> CommandEvidence:
    started = perf_counter()
    try:
        completed = subprocess.run(
            command,
            cwd=repo,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
            timeout=180,
        )
    except FileNotFoundError as exc:
        return CommandEvidence(
            command,
            None,
            _elapsed_ms(started),
            "",
            _bounded(str(exc)),
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return CommandEvidence(
            command,
            124,
            _elapsed_ms(started),
            _bounded(stdout),
            _bounded(f"timeout\n{stderr}"),
        )

    return CommandEvidence(
        command,
        completed.returncode,
        _elapsed_ms(started),
        _bounded(completed.stdout),
        _bounded(completed.stderr),
    )


def _bounded(text: str) -> str:
    if len(text) <= OUTPUT_LIMIT:
        return text
    return text[:OUTPUT_LIMIT] + "\n...[truncated]"


def _elapsed_ms(started: float) -> int:
    return round((perf_counter() - started) * 1000)
