#!/usr/bin/env python3
"""Run MASTERCORE G0-G8 quality gates and emit JSON evidence."""

from __future__ import annotations

import argparse
from pathlib import Path

from quality_engine import GateStatus, run_quality_gates, write_json_evidence


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        choices=("ci", "local"),
        default="ci",
        help="ci requires all automated release-independent gates; local requires G0/G1",
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=Path("quality-evidence.json"),
        help="path for machine-readable evidence",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    repo = Path(__file__).resolve().parents[1]
    report = run_quality_gates(repo, profile=args.profile)
    write_json_evidence(report, repo / args.json)

    for gate in report.gates:
        marker = "*" if gate.gate in report.required_gates else "-"
        print(f"{marker} {gate.gate} {gate.status.value}: {gate.summary}")
        for detail in gate.details:
            print(f"    {detail}")
    print(f"OVERALL {report.overall_status.value}")
    print(f"EVIDENCE {args.json}")
    return 0 if report.overall_status in {GateStatus.PASS, GateStatus.WARN} else 1


if __name__ == "__main__":
    raise SystemExit(main())
