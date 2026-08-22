from pathlib import Path
import json
import unittest


class ContractTests(unittest.TestCase):
    def test_quality_contract_has_required_safety_rules(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        contract = json.loads(
            (repo / "quality-contract.json").read_text(encoding="utf-8")
        )
        rules = contract["rules"]
        self.assertFalse(rules["guess_patch_locations"])
        self.assertFalse(rules["report_unrun_checks_as_pass"])
        self.assertFalse(rules["mix_user_and_app_data"])
        self.assertTrue(rules["require_pre_and_post_validation_for_writes"])


if __name__ == "__main__":
    unittest.main()
