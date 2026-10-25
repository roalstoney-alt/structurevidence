#!/usr/bin/env python3
"""Phase E Decision Boundary Pilot protocol and regression guards."""

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

from build_decision_boundary_pilot_phase_e import (  # noqa: E402
    CONTEXT_PATH, EVENTS_PATH, HASH_REPORT_PATH, MIRRORS, REPORT_MD_PATH, REPORT_PATH, draft, fixture, units,
)
from decision_boundary_pilot_v01 import (  # noqa: E402
    EVENT_TYPES, PilotProtocolError, append_event, build_report, seal_event, validate_context,
    validate_events, validate_report,
)


PROTECTED_SHA256 = {
    "cases/800vdc/source-dependency/index.html": "e42b94dcbce09900c9b79bc2374bf09b53ace2d1b9e897a50fb544715272ba38",
    "cases/800vdc/source-dependency-v0.1.json": "9038817ab15e1202ea5ae8ca374f515f5381b6480fce22f2ff137d3267cd7705",
    "cases/800vdc/decision-conditions/index.html": "a50ab5f0985decd60aab105b90365ea3c10f4c0e5195d8c779c544649fd4d581",
    "cases/800vdc/decision-conditions-v0.1.json": "c451662988a44c9907c906e6e245b1ee64e5c204fc5dca7b4d06c26f4b49f040",
    "cases/800vdc/decision-conditions-v0.1.md": "bafe2695ee79f6cc0a9b5ed033546d1a36a84071d7a447f9ffed247eb6fe9fea",
    "protocol/source-dependency/registry-v0.1.json": "172172ccc1c9fe8587224c1dcf51ae8354be74d951603da6b5f96b1e7fa68203",
    "deploy/cloudflare-landing/migrations/0001_customer_intake.sql": "156cea56e8278abc280315c10b98af03616cc9c2f71a5bc8a2b02a358c47b851",
    "deploy/cloudflare-landing/locales/en.json": "b85af98ab67ad66bc05f0d90c01e6030a2577a37199f4de9ce022393b84c6cfe",
    "deploy/cloudflare-landing/locales/zh-CN.json": "1dab213b5f6f1356d70cf2d4ec551af4aef822f2ff43d22cbc1baa0d1683e310",
    "deploy/cloudflare-landing/locales/es.json": "89d74f1e785c59927f20f92ca6cf19d1bc55d0300eeedd76a2463ada2b2b58af",
}


def load_json(path: str | Path) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def load_events() -> list[dict]:
    return [json.loads(line) for line in (ROOT / EVENTS_PATH).read_text(encoding="utf-8").splitlines() if line]


class DecisionBoundaryPilotPhaseE(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.context, cls.events, cls.report = fixture()

    def test_01_fixture_is_explicitly_not_a_customer_pilot(self):
        self.assertEqual(self.context["classification"], "PUBLIC_ILLUSTRATION_NOT_CUSTOMER_PILOT")
        self.assertEqual(self.context["real_customer_authorization"], "NOT_GRANTED")
        self.assertTrue(self.context["test_fixture_only"])

    def test_02_all_required_event_types_are_declared(self):
        schema = load_json("protocol/decision-boundary-pilot/schema-v0.1.json")
        self.assertEqual(set(EVENT_TYPES), set(schema["properties"]["event_type"]["enum"]))

    def test_03_append_only_chain_and_hashes_validate(self):
        validate_events(self.events, self.context)
        self.assertIsNone(self.events[0]["previous_event_sha256"])
        for prior, current in zip(self.events, self.events[1:]):
            self.assertEqual(current["previous_event_sha256"], prior["event_sha256"])

    def test_04_mutation_breaks_hash_chain(self):
        events = copy.deepcopy(self.events)
        events[3]["payload"]["reason"] = "rewritten"
        with self.assertRaises(PilotProtocolError):
            validate_events(events, self.context)

    def test_05_exact_replay_is_idempotent(self):
        last = self.events[-1]
        replay = {key: copy.deepcopy(value) for key, value in last.items() if key not in {"sequence", "previous_event_sha256", "event_sha256"}}
        self.assertEqual(append_event(self.events, replay, self.context), self.events)

    def test_06_conflicting_replay_is_rejected(self):
        last = self.events[-1]
        replay = {key: copy.deepcopy(value) for key, value in last.items() if key not in {"sequence", "previous_event_sha256", "event_sha256"}}
        replay["payload"]["stop_status"] = "CONFLICT"
        with self.assertRaises(PilotProtocolError):
            append_event(self.events, replay, self.context)

    def test_07_baseline_must_be_first_and_complete(self):
        with self.assertRaises(PilotProtocolError):
            append_event([], draft(99, "REVIEW_STARTED", "2026-10-25T14:00:00Z", {"work_units": units()}), self.context)

        events = copy.deepcopy(self.events)
        events[0]["payload"]["decision_question"] = "mutated T0"
        events[0] = seal_event(events[0])
        with self.assertRaises(PilotProtocolError):
            validate_events(events, self.context)

    def test_08_supersession_preserves_original_event(self):
        by_id = {event["event_id"]: event for event in self.events}
        supersession = next(event for event in self.events if event["event_type"] == "SUPERSEDED")
        target = supersession["payload"]["supersedes_event_id"]
        self.assertIn(target, by_id)
        self.assertEqual(by_id[target]["event_type"], "RULE_CHECKED")
        self.assertEqual(supersession["payload"]["work_units"]["revisions_supersessions"], 1)

    def test_09_real_customer_requires_independent_authorization(self):
        context = copy.deepcopy(self.context)
        context.update({"classification": "REAL_CUSTOMER_PILOT", "data_boundary": "PRIVATE_CUSTOMER_RECORD_NOT_PUBLIC_EXPORT"})
        with self.assertRaises(PilotProtocolError):
            validate_context(context)

    def test_10_public_records_reject_private_identifiers(self):
        context = copy.deepcopy(self.context)
        context["email"] = "not-allowed@example.invalid"
        with self.assertRaises(PilotProtocolError):
            validate_context(context)

    def test_11_fixture_cannot_record_client_decision_or_outcome(self):
        decision = draft(10, "CLIENT_DECISION_RECORDED", "2026-10-25T16:10:00Z", {
            "decision_source": "CLIENT_SUPPLIED", "work_units": units()
        })
        outcome = draft(10, "OUTCOME_OBSERVED", "2026-10-25T16:10:00Z", {
            "observation_status": "INDEPENDENTLY_OBSERVED_AND_PERMITTED", "work_units": units()
        })
        for item in (decision, outcome):
            with self.assertRaises(PilotProtocolError):
                append_event(self.events, item, self.context)

    def test_12_report_is_deterministic_and_sealed(self):
        self.assertEqual(build_report(self.context, self.events), build_report(self.context, self.events))
        validate_report(self.report, self.context, self.events)
        unsealed = {key: value for key, value in self.report.items() if key != "report_sha256"}
        digest = hashlib.sha256(json.dumps(unsealed, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(digest, self.report["report_sha256"])

    def test_13_missing_actual_baseline_stays_insufficient(self):
        comparison = self.report["baseline_comparison"]
        self.assertEqual(comparison["status"], "INSUFFICIENT_DATA")
        self.assertEqual(comparison["causal_attribution"], "NOT_ESTABLISHED")
        self.assertEqual(comparison["roi_status"], "NOT_EVALUATED")
        self.assertIsNone(self.report["observed_telemetry"]["values"])

    def test_14_no_false_roi_or_avoided_loss_claim(self):
        text = (ROOT / REPORT_MD_PATH).read_text(encoding="utf-8")
        self.assertNotRegex(text, re.compile(r"\bROI\s*[:=]\s*[+\-]?\d", re.I))
        self.assertNotRegex(text, re.compile(r"\b(saved|savings|avoided loss)\s+[\$€£]?\d", re.I))
        self.assertIn("not a customer pilot", text)
        self.assertIn("INSUFFICIENT_DATA", text)

    def test_15_work_unit_totals_are_expected(self):
        telemetry = self.report["simulation_telemetry"]
        self.assertEqual(telemetry["researcher_minutes"], 125)
        self.assertEqual(telemetry["reviewer_touch_minutes"], 50)
        self.assertEqual(telemetry["source_acquisition_cost_minor_units"], 2000)
        self.assertEqual(telemetry["decision_condition_citations"], 2)

    def test_16_generated_files_equal_in_memory_projection(self):
        self.assertEqual(load_json(CONTEXT_PATH), self.context)
        self.assertEqual(load_events(), self.events)
        self.assertEqual(load_json(REPORT_PATH), self.report)

    def test_17_root_docs_mirrors_are_byte_identical(self):
        for source, mirror in MIRRORS.items():
            self.assertEqual((ROOT / source).read_bytes(), (ROOT / mirror).read_bytes(), str(source))

    def test_18_protected_evidence_state_price_privacy_and_locales_do_not_drift(self):
        for path, expected in PROTECTED_SHA256.items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), expected, path)

    def test_19_pages_audit_records_exact_trigger_and_live_proof(self):
        audit = (ROOT / "docs/implementation/SE-DUAL-SITE-002-PHASE-E-PAGES-AUDIT.md").read_text(encoding="utf-8")
        for value in (
            "95219314309e01af6bf4042831b2bf4ba18fbc02", "40198754542", "dynamic/pages/pages-build-deployment",
            "path: .", "VERIFIED", "180be9ffe40acf35a7e2b341552caafc4673d7e4d98f9b2a45d6fde52eb3c24e",
        ):
            self.assertIn(value, audit)
        self.assertIn("Settings > Pages", audit)
        self.assertIn("UNVERIFIED", audit)

    def test_20_schema_accepts_every_generated_event_when_available(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed")
        validator = jsonschema.Draft202012Validator(load_json("protocol/decision-boundary-pilot/schema-v0.1.json"), format_checker=jsonschema.FormatChecker())
        for event in self.events:
            validator.validate(event)

    def test_21_builder_is_byte_deterministic(self):
        tracked = [CONTEXT_PATH, EVENTS_PATH, REPORT_PATH, REPORT_MD_PATH, HASH_REPORT_PATH]
        before = {path: (ROOT / path).read_bytes() for path in tracked}
        result = subprocess.run([sys.executable, str(ROOT / "scripts/build_decision_boundary_pilot_phase_e.py")], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, {path: (ROOT / path).read_bytes() for path in tracked})


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(DecisionBoundaryPilotPhaseE)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"PHASE_E_DECISION_BOUNDARY_PILOT = {'PASS' if result.wasSuccessful() else 'FAIL'}")
    print(f"TESTS_RUN = {result.testsRun}")
    raise SystemExit(0 if result.wasSuccessful() else 1)
