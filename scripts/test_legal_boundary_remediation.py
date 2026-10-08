#!/usr/bin/env python3
import importlib.util
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "bfeeae97babd6a245faf9b0bdee4109dd6d2417c"


class LegalBoundaryRemediationTest(unittest.TestCase):
    def test_featured_cards_are_exactly_three_and_bounded_in_all_locales(self):
        for path in ("en/index.html", "zh-cn/index.html", "es/index.html"):
            text = (ROOT / path).read_text()
            self.assertIn('data-featured-case-count="3"', text, path)
            self.assertEqual(text.count('data-featured-case="'), 3, path)
            self.assertNotIn('data-featured-case="SE-ONC-NSQNSCLC-CN-001"', text, path)
        en = (ROOT / "en/index.html").read_text()
        for value in ("2026-09-20T10:46:47Z", "2026-09-24", "2026-10-08T06:15:59+08:00", "REVIEW INCOMPLETE"):
            self.assertIn(value, en)

    def test_scientific_case_files_are_not_copy_edited(self):
        changed = subprocess.check_output(
            ["git", "diff", "--name-only", BASE, "--", "cases", "docs/cases"], cwd=ROOT, text=True
        ).splitlines()
        self.assertEqual(changed, [])
        review = json.loads((ROOT / "cases/review-status.json").read_text())
        by_id = {item["case_id"]: item for item in review["cases"]}
        self.assertEqual(by_id["CML-PDRE-001"]["evidence_state_as_of"], "2026-09-20T10:46:47Z")
        self.assertEqual(by_id["SE-BESS-SODIUM-001"]["evidence_state_as_of"], "2026-09-24")
        self.assertIsNone(by_id["SE-ONC-NSQNSCLC-CN-001"]["last_reviewed_at"])

    def test_projection_uses_existing_cutoffs_and_explicit_limits(self):
        data = json.loads((ROOT / "data/public-evidence-presentation.json").read_text())
        records = {item["case_id"]: item for item in data["cases"]}
        self.assertEqual(set(records), {"CML-PDRE-001", "SE-BESS-SODIUM-001", "SE-IRK-LAB-001", "SE-ONC-NSQNSCLC-CN-001"})
        self.assertEqual(records["SE-BESS-SODIUM-001"]["evidence_state_as_of"], "2026-09-24")
        self.assertIn("that no such site exists anywhere", records["SE-BESS-SODIUM-001"]["not_implied"])
        self.assertEqual(records["SE-IRK-LAB-001"]["review_completeness"], "REVIEW_INCOMPLETE")

    def test_restricted_projection_never_returns_payload(self):
        spec = importlib.util.spec_from_file_location("publication_policy", ROOT / "scripts/publication_policy.py")
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        record = json.loads((ROOT / "tests/fixtures/publication-restricted.json").read_text())
        projected = module.public_projection(record)
        self.assertNotIn("restricted_payload", projected)
        self.assertNotIn("SYNTHETIC_PRIVATE_TEXT", json.dumps(projected))
        self.assertEqual(projected["public_status"], "RESTRICTED")

    def test_org_legal_mirrors_and_commercial_contract_are_consistent(self):
        for name in ("privacy.html", "terms-of-sale.html", "refund-policy.html", "corrections-policy.html"):
            self.assertEqual((ROOT / name).read_bytes(), (ROOT / "docs" / name).read_bytes(), name)
        terms = (ROOT / "deploy/cloudflare-landing/commercial-upgrade.js").read_text()
        self.assertIn("confirmed service error is corrected without requiring another purchase", terms)
        self.assertIn("New evidence, a new source universe, a new cut-off or a new question", terms)
        self.assertNotIn("superseded evidence state is corrected automatically", terms)

    def test_notice_is_versioned_and_customer_text_is_not_event_note(self):
        worker = (ROOT / "deploy/cloudflare-landing/worker.js").read_text()
        migration = (ROOT / "deploy/cloudflare-landing/migrations/0003_legal_boundary_notices.sql").read_text()
        self.assertIn('PRIVACY_NOTICE_VERSION = "2026-10-08"', worker)
        self.assertIn("input.privacy_notice_ack !== true", worker)
        self.assertIn("input.confidentiality_ack !== true", worker)
        self.assertIn("'REQUEST_SUBMITTED', ?, 'CUSTOMER', NULL, ?, NULL", worker)
        self.assertIn("CREATE TABLE request_private_context", migration)


if __name__ == "__main__":
    unittest.main()
