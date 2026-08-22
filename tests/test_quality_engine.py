import tempfile
import unittest
from pathlib import Path

from tools.quality_engine import (
    GateResult,
    GateStatus,
    QualityReport,
    aggregate_status,
    write_json_evidence,
)


class QualityEngineTests(unittest.TestCase):
    def test_required_not_run_is_failure(self) -> None:
        gates = (
            GateResult("G0", "Scope", GateStatus.PASS, "ok"),
            GateResult("G1", "Static", GateStatus.NOT_RUN, "missing tool"),
        )
        self.assertEqual(
            aggregate_status(gates, frozenset({"G0", "G1"})),
            GateStatus.FAIL,
        )

    def test_optional_not_run_does_not_break_required_pass(self) -> None:
        gates = (
            GateResult("G0", "Scope", GateStatus.PASS, "ok"),
            GateResult("G6", "UI", GateStatus.NOT_RUN, "not configured"),
        )
        self.assertEqual(
            aggregate_status(gates, frozenset({"G0"})),
            GateStatus.PASS,
        )

    def test_missing_required_gate_is_failure(self) -> None:
        gates = (GateResult("G0", "Scope", GateStatus.PASS, "ok"),)
        self.assertEqual(
            aggregate_status(gates, frozenset({"G0", "G1"})),
            GateStatus.FAIL,
        )

    def test_json_evidence_is_written_atomically(self) -> None:
        report = QualityReport(
            profile="ci",
            overall_status=GateStatus.PASS,
            required_gates=frozenset({"G0"}),
            gates=(GateResult("G0", "Scope", GateStatus.PASS, "ok"),),
            generated_at="2026-08-22T00:00:00+00:00",
        )
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "quality-evidence.json"
            write_json_evidence(report, target)
            text = target.read_text(encoding="utf-8")
            self.assertIn('"overall_status": "PASS"', text)
            self.assertEqual(list(target.parent.glob(".*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
