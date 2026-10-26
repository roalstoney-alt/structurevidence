#!/usr/bin/env python3
"""Regression guards for SE-LISTED-PROJECT-TRACKER-IREN-001."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from listed_project_tracker_iren_v01 import (  # noqa: E402
    TrackerProtocolError, digest, validate_events, validate_financial_attributes, validate_tracker,
)

OUT = ROOT / "research/internal/listed-projects/iren"
BASELINE = "305bbef43f2ccdef9d025ac802dfca6b6ad6a8df"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class IrenTrackerV01Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inventory = load(OUT / "source-inventory-v0.1.json")
        cls.sources = cls.inventory["sources"]
        cls.tracker = load(OUT / "tracker-v0.1.json")
        cls.bet = load(OUT / "corporate-bet-register-v0.1.json")
        cls.events = [json.loads(line) for line in (OUT / "change-events-v0.1.jsonl").read_text(encoding="utf-8").splitlines()]
        cls.claims = {item["claim_id"]: item for item in cls.tracker["claims"]}

    def test_01_draft_is_human_gated_and_case_state_unchanged(self):
        self.assertEqual(self.tracker["publication_status"], "INTERNAL_DRAFT_NOT_PUBLICLY_ACTIVATED")
        self.assertIn("HUMAN", self.tracker["human_gate"])
        self.assertFalse(self.tracker["case_state_changed"])

    def test_02_tracker_and_source_records_validate(self):
        validate_tracker(self.tracker, self.sources)

    def test_03_financial_axes_are_independent_and_d4_dimensions_are_distinct(self):
        schema = load(ROOT / "protocol/listed-project-tracker/schema-v0.1.json")
        enum = schema["properties"]["disclosure_stages"]["items"]["enum"]
        self.assertIn("D4a", enum)
        self.assertIn("D4b", enum)
        self.assertNotEqual(enum.index("D4a"), enum.index("D4b"))
        validate_financial_attributes({
            "source_dependency": "UNKNOWN", "liability_regime": "UNDETERMINED",
            "assurance": "UNKNOWN", "assurance_scope": "explicit unknown", "disclosure_stages": ["D4a", "D4b"],
        })

    def test_04_contract_does_not_become_revenue_or_cash(self):
        stages = self.claims["IREN-C004"]["financial_attributes"]["disclosure_stages"]
        self.assertEqual(stages, ["D1"])
        self.assertNotIn("D3", stages)
        self.assertNotIn("D4a", stages)

    def test_05_issuer_acceptance_is_not_customer_confirmation(self):
        stages = self.claims["IREN-C005"]["financial_attributes"]["disclosure_stages"]
        self.assertEqual(stages, ["D2"])
        self.assertNotIn("D4b", stages)
        self.assertEqual(self.claims["IREN-N001"]["state"], "NOT_ESTABLISHED_WITHIN_REVIEWED_SCOPE")

    def test_06_target_is_not_delivered_capacity(self):
        stages = self.claims["IREN-C006"]["financial_attributes"]["disclosure_stages"]
        self.assertEqual(stages, ["D0"])
        self.assertEqual(self.claims["IREN-N002"]["state"], "NOT_ESTABLISHED_WITHIN_REVIEWED_SCOPE")

    def test_07_arr_is_not_gaap_revenue(self):
        claim = self.claims["IREN-C011"]
        self.assertEqual(claim["financial_attributes"]["liability_regime"], "FURNISHED")
        self.assertIn("not recognized revenue", claim["plain_language_record"])
        self.assertEqual(self.claims["IREN-N004"]["state"], "NOT_ESTABLISHED_WITHIN_REVIEWED_SCOPE")

    def test_08_furnished_treatment_is_source_specific(self):
        sources = {item["source_id"]: item for item in self.sources}
        for source_id in ("IREN-S07", "IREN-S08", "IREN-S09"):
            self.assertEqual(sources[source_id]["liability_regime"], "FURNISHED")
        self.assertEqual(sources["IREN-S10"]["liability_regime"], "FILED")

    def test_09_annual_report_audit_scope_is_not_overextended(self):
        for claim_id in ("IREN-C007", "IREN-C008", "IREN-C009", "IREN-C010"):
            scope = self.claims[claim_id]["financial_attributes"]["assurance_scope"].lower()
            self.assertIn("financial statement", scope)
        self.assertIn("not classified as audited", self.claims["IREN-C003"]["financial_attributes"]["assurance_scope"])

    def test_10_investment_right_is_not_cash_received(self):
        self.assertNotIn("D4a", self.claims["IREN-C013"]["financial_attributes"]["disclosure_stages"])
        self.assertNotIn("D4b", self.claims["IREN-C013"]["financial_attributes"]["disclosure_stages"])
        self.assertEqual(self.claims["IREN-N005"]["state"], "NOT_ESTABLISHED_WITHIN_REVIEWED_SCOPE")

    def test_11_inaccessible_raw_bytes_never_get_fabricated_hashes(self):
        failures = [item for item in self.sources if item["byte_capture_status"] == "RETRIEVAL_FAILED"]
        self.assertEqual(len(failures), 9)
        self.assertTrue(all(item["sha256"] is None for item in failures))
        self.assertTrue(all("403" in item["access_boundary"] for item in failures))

    def test_12_captured_nvidia_origin_has_exact_byte_hash(self):
        source = next(item for item in self.sources if item["source_id"] == "IREN-S11")
        self.assertEqual(source["sha256"], "a77aab4585b2ce334e6cc0a40b2bc1f1121dda90e875e44dbe0b68736be45c97")
        self.assertEqual(source["byte_capture_status"], "CAPTURED")
        index = next(item for item in self.sources if item["source_id"] == "IREN-S12")
        self.assertEqual(index["sha256"], "0135337d188cb46f00803d3fc727a648459b13f7789d3e611b1483b72080cb77")

    def test_13_no_duplicate_sources_or_claims(self):
        self.assertEqual(len(self.sources), len({item["source_id"] for item in self.sources}))
        self.assertEqual(len(self.sources), len({item["url"] for item in self.sources}))
        self.assertEqual(len(self.tracker["claims"]), len(self.claims))

    def test_13b_prior_case_is_hashed_but_not_promoted_to_primary_evidence(self):
        prior = self.inventory["prior_case_inventory"]
        self.assertEqual(prior["sha256"], "96507322272876e5b6dba8e788e626ac9fdc0fd9b6a29485783d072e90f5176d")
        self.assertEqual(prior["evidentiary_role"], "DERIVED_BASELINE_NOT_A_QUALIFYING_PRIMARY_SOURCE")
        self.assertNotIn("SE-NEW-BUSINESS-001", {source["source_id"] for source in self.sources})

    def test_14_every_claim_has_provenance_cutoff_hash_and_review(self):
        for claim in self.tracker["claims"]:
            self.assertTrue(claim["source_ids"])
            self.assertEqual(len(claim["source_ids"]), len(claim["source_record_sha256"]))
            self.assertEqual(claim["evidence_cutoff"], "2026-10-26")
            self.assertRegex("".join(claim["source_record_sha256"]), r"^[0-9a-f]+$")
            self.assertEqual(claim["review_status"], "PENDING_REAL_HUMAN_REVIEW")
            self.assertEqual(claim["client_action"], "UNSPECIFIED")

    def test_15_append_only_event_chain_and_mutation_guard(self):
        validate_events(self.events)
        mutated = copy.deepcopy(self.events)
        mutated[2]["summary"] = "rewritten history"
        with self.assertRaises(TrackerProtocolError):
            validate_events(mutated)
        self.assertIn("DEFINITION_DRIFT", {item["event_type"] for item in self.events})

    def test_16_bet_register_keeps_actions_and_decision_owner_unknown(self):
        for item in self.bet["commitments"]:
            self.assertEqual(item["client_defined_threshold"], "UNSPECIFIED")
            self.assertEqual(item["client_action"], "UNSPECIFIED")
            self.assertEqual(item["decision_owner"], "UNKNOWN")
        self.assertEqual(self.bet["snapshot_sha256"], digest({key: value for key, value in self.bet.items() if key != "snapshot_sha256"}))

    def test_17_no_trading_signal_score_or_roi_claim(self):
        tracker_text = (OUT / "tracker-v0.1.md").read_text(encoding="utf-8")
        bet_text = (OUT / "corporate-bet-register-v0.1.json").read_text(encoding="utf-8")
        combined = tracker_text + bet_text
        self.assertNotRegex(combined, re.compile(r"\b(BUY|SELL|HOLD)\b"))
        self.assertNotRegex(combined, re.compile(r"\b(score|rating)\s*[:=]\s*\d", re.I))
        self.assertNotRegex(combined, re.compile(r"\bROI\s*[:=]\s*[+\-]?\d", re.I))

    def test_18_no_private_customer_fields_or_secrets(self):
        combined = "\n".join(path.read_text(encoding="utf-8") for path in OUT.iterdir() if path.is_file())
        for forbidden in ("customer_email", "customer_name", "api_key", "bearer_token", "private decision threshold"):
            self.assertNotIn(forbidden, combined.lower())

    def test_19_internal_draft_is_not_added_to_public_routes(self):
        public = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in ("sitemap.xml", "docs/sitemap.xml", "cases/index.html", "index.html"))
        self.assertNotIn("listed-projects/iren", public)
        self.assertNotIn("SE-LISTED-PROJECT-TRACKER-IREN-001", public)

    def test_20_existing_cases_commercial_and_deploy_files_are_untouched(self):
        result = subprocess.run(["git", "diff", "--name-only", f"{BASELINE}...HEAD"], cwd=ROOT, capture_output=True, text=True, check=True)
        for path in result.stdout.splitlines():
            self.assertFalse(path.startswith(("cases/", "deploy/", "evidence/", "claims/")), path)

    def test_21_digest_template_and_pilot_are_not_live(self):
        weekly = (OUT / "weekly-digest-template-v0.1.md").read_text(encoding="utf-8")
        pilot = (OUT / "eight-week-pilot-protocol-v0.1.md").read_text(encoding="utf-8")
        self.assertIn("NO AUTOMATIC DISTRIBUTION", weekly)
        self.assertIn("No qualifying change", weekly)
        self.assertIn("NOT STARTED", pilot)
        self.assertIn("PUBLIC_PILOT_START", pilot)

    def test_22_conflicts_declaration_is_not_fabricated(self):
        policy = (OUT / "neutrality-conflicts-policy-v0.1.md").read_text(encoding="utf-8")
        self.assertIn("DECLARATION_NOT_COLLECTED", policy)
        self.assertIn("legal", policy.lower())

    def test_23_hash_report_matches_every_generated_file(self):
        report = load(ROOT / "docs/implementation/SE-LISTED-PROJECT-TRACKER-IREN-001-HASHES.json")
        for relative, expected in report["files"].items():
            self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), expected, relative)
        for relative, expected in report["implementation_files"].items():
            self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), expected, relative)
        unsigned = {key: value for key, value in report.items() if key != "report_sha256"}
        self.assertEqual(report["report_sha256"], digest(unsigned))
        self.assertEqual(report["original_records_changed"], 0)
        self.assertFalse(report["case_state_changed"])

    def test_24_builder_is_byte_deterministic(self):
        tracked = sorted(OUT.iterdir()) + [ROOT / "docs/implementation/SE-LISTED-PROJECT-TRACKER-IREN-001-HASHES.json"]
        before = {path: path.read_bytes() for path in tracked}
        result = subprocess.run([sys.executable, str(ROOT / "scripts/build_listed_project_tracker_iren_v01.py")], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, {path: path.read_bytes() for path in tracked})

    def test_25_schema_accepts_generated_financial_attributes_when_available(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed")
        validator = jsonschema.Draft202012Validator(load(ROOT / "protocol/listed-project-tracker/schema-v0.1.json"))
        for claim in self.tracker["claims"]:
            validator.validate(claim["financial_attributes"])


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(IrenTrackerV01Tests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"IREN_LISTED_PROJECT_TRACKER_GUARDS = {'PASS' if result.wasSuccessful() else 'FAIL'}")
    print(f"TESTS_RUN = {result.testsRun}")
    raise SystemExit(0 if result.wasSuccessful() else 1)
