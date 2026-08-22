#!/usr/bin/env python3
"""Zero-dependency MASTERCORE repository self-check."""

from __future__ import annotations

import json
from pathlib import Path
import re

REQUIRED_STATUS = {"PASS", "WARN", "FAIL", "NOT_RUN"}
REQUIRED_WORKFLOW = [
    "discover",
    "classify",
    "design",
    "patch",
    "verify",
    "prove",
    "record",
]
REQUIRED_DATA_CLASSES = {
    "immutable_app_data",
    "user_config",
    "user_content",
    "derived_data",
    "operational_data",
    "recovery_data",
}


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    failures: list[str] = []

    contract_path = repo / "quality-contract.json"
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL contract unreadable: {exc}")
        return 1

    version = str(contract.get("standard_version", ""))
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        failures.append("quality-contract standard_version is not SemVer")

    if contract.get("workflow") != REQUIRED_WORKFLOW:
        failures.append("workflow differs from canonical order")

    if set(contract.get("validation_statuses", [])) != REQUIRED_STATUS:
        failures.append("validation_statuses are incomplete or inconsistent")

    if set(contract.get("data_classes", [])) != REQUIRED_DATA_CLASSES:
        failures.append("data_classes are incomplete or inconsistent")

    required_files = [
        "AGENTS.md",
        "README.md",
        "INPUT_FUER_TODO.md",
        "docs/GLOBAL_STANDARDS.md",
        "docs/QUALITY_GATES.md",
        "docs/DATA_STORAGE_CONTRACT.md",
        "docs/PATCH_AND_VALIDATION_PROTOCOL.md",
        "docs/UI_UX_ACCESSIBILITY_STANDARD.md",
        "docs/RELEASE_GOVERNANCE.md",
    ]
    for relative in required_files:
        path = repo / relative
        if not path.is_file():
            failures.append(f"missing required file: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        if relative in {"AGENTS.md", "README.md", "docs/GLOBAL_STANDARDS.md"}:
            if version not in text:
                failures.append(
                    f"version {version} not referenced by {relative}"
                )

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1

    print(f"PASS MASTERCORE contract {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
