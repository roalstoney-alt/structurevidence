#!/usr/bin/env python3
"""Targeted ingestion tests for approved packet CML-PDRE-001-EVP-001."""

import hashlib
import json
import unittest
from pathlib import Path

import validate_cml_v11_core as core_validator


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "technical-risk/cml-v1.1/pdre/CML-PDRE-001"
PACKET_ID = "CML-PDRE-001-EVP-001"
EVIDENCE_IDS = {f"EV-{number:03d}" for number in range(1, 8)}
CRITICAL_TRANSFERS = {
    "DC_DC_CONVERSION",
    "DC_PROTECTION",
    "DC_ARC_FLASH",
    "HVDC_CONNECTOR_BUSWAY",
    "ENERGY_STORAGE",
    "INSULATION",
    "FAULT_ISOLATION",
    "THERMAL_MANAGEMENT",
}


def load(name):
    return json.loads((CASE_DIR / name).read_text())


def load_jsonl(name):
    return [json.loads(line) for line in (CASE_DIR / name).read_text().splitlines() if line.strip()]


def digest(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


class CMLPDRE001EVP001Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = load("CASE.json")
        cls.record = load("pdre-record.json")
        cls.payload = cls.record["pdre_record"]
        cls.evidence_log = load_jsonl("evidence-index.jsonl")
        cls.evidence = {row["evidence_id"]: row for row in cls.evidence_log[1:]}
        cls.timeline = load_jsonl("timeline.jsonl")
        cls.states = load_jsonl("state-history.jsonl")
        cls.transfer = load("dependency-transfer.json")

    def test_canonical_record_passes_accepted_cml_validator(self):
        result = core_validator.validate_pdre(self.record)
        self.assertEqual(result["pdre_id"], "PDRE-001A")
        self.assertEqual(result["readiness"], "R3")
        self.assertEqual(result["evidence_items"], 7)

    def test_evidence_core_hashes_bind_packet_and_record(self):
        expected_input = digest({"packet_id": PACKET_ID, "evidence": self.evidence_log[1:]})
        self.assertEqual(self.record["core"]["input_hash"], expected_input)
        core = dict(self.record["core"])
        actual_record_hash = core.pop("record_hash")
        expected_record_hash = digest({"core": core, "payload": self.payload})
        self.assertEqual(actual_record_hash, expected_record_hash)

    def test_exactly_seven_authorized_evidence_records_are_ingested(self):
        self.assertEqual(set(self.evidence), EVIDENCE_IDS)
        self.assertTrue(all(row["packet_id"] == PACKET_ID for row in self.evidence.values()))
        self.assertTrue(all(row["research_unit"] == "PDRE-001A" for row in self.evidence.values()))
        self.assertTrue(all(row["known_at"] == "2026-09-17" for row in self.evidence.values()))

    def test_event_and_knowledge_time_are_distinct_without_invented_precision(self):
        source_events = self.timeline[1:8]
        self.assertTrue(all(row["effective_at"] != row["known_at"] for row in source_events))
        by_ref = {row["evidence_refs"][0]: row for row in source_events}
        self.assertEqual(by_ref["EV-004"]["effective_at"], "2026-05")
        self.assertEqual(by_ref["EV-004"]["event_time_precision"], "MONTH")
        self.assertEqual(by_ref["EV-007"]["effective_at"], "2026")
        self.assertEqual(by_ref["EV-007"]["event_time_precision"], "YEAR")

    def test_readiness_transition_is_exactly_not_assigned_to_r3(self):
        transition = self.states[-1]
        self.assertEqual(transition["previous_migration_readiness"], "NOT_ASSIGNED")
        self.assertEqual(transition["migration_readiness"], "R3")
        self.assertEqual(transition["migration_readiness_name"], "SAMPLE_BENCH_TESTED")
        self.assertEqual(transition["interpretation"], "TECHNICALLY_CREDIBLE")
        self.assertEqual(transition["pdre_status"], "CANDIDATE")

    def test_no_readiness_above_r3_or_company_assessment_is_created(self):
        readiness = self.payload["migration_readiness"]
        self.assertEqual(readiness["code"], "R3")
        self.assertFalse(readiness["supports_company_structural_assessment"])
        chain = {row["stage"]: row for row in self.payload["pdre"]["pdre_evidence_chain"]}
        for stage in ("QUALIFICATION", "PRODUCTION", "FIELD_DEPLOYMENT", "MULTI_USER_MULTI_OEM_REPLICATION"):
            self.assertNotEqual(chain[stage]["status"], "ESTABLISHED")

    def test_pdre_001b_is_not_merged_into_r3(self):
        units = {row["pdre_unit_id"]: row for row in self.case["research_units"]}
        unit_b = units["PDRE-001B"]
        self.assertEqual(unit_b["research_status"], "ACTIVE_SUBHYPOTHESIS")
        self.assertEqual(unit_b["migration_readiness"]["assignment_status"], "NOT_ASSIGNED")
        self.assertIsNone(unit_b["migration_readiness"]["code"])
        for row in self.transfer["categories"]:
            self.assertEqual(row["PDRE-001B"]["dependency_release"], "UNKNOWN")
            self.assertEqual(row["PDRE-001B"]["dependency_transfer"], "UNKNOWN")

    def test_dependency_release_and_transfer_remain_separate(self):
        self.assertEqual(self.transfer["dependency_release_scope"]["status"], "CANDIDATE")
        rows = {row["category"]: row for row in self.transfer["categories"]}
        actual = {
            category
            for category, row in rows.items()
            if row["PDRE-001A"]["dependency_transfer"] == "NEW_CRITICAL_DEPENDENCY"
        }
        self.assertEqual(actual, CRITICAL_TRANSFERS)
        self.assertEqual(rows["COPPER"]["PDRE-001A"]["dependency_release"], "CURRENT_REDUCTION_DERIVED")
        self.assertEqual(rows["COPPER"]["PDRE-001A"]["dependency_transfer"], "UNKNOWN")

    def test_vendor_claims_are_not_promoted_to_independent_facts(self):
        known = {row["evidence_id"]: row for row in self.payload["known_evidence"]}
        self.assertTrue(all(not row["structural_fact"] for row in known.values()))
        self.assertIn("NOT_INDEPENDENTLY_VERIFIED", self.case["economic_state"]["COPPER_REDUCTION"])
        self.assertIn("NOT_INDEPENDENTLY_VERIFIED", self.case["economic_state"]["EFFICIENCY"])
        self.assertEqual(self.payload["economics"]["performance"]["assessment"], "UNKNOWN")

    def test_standardization_is_not_field_deployment(self):
        self.assertIn("FIELD_DEPLOYMENT", self.evidence["EV-005"]["prohibited_uses"])
        chain = {row["stage"]: row for row in self.payload["pdre"]["pdre_evidence_chain"]}
        self.assertEqual(chain["FIELD_DEPLOYMENT"]["status"], "NOT_ESTABLISHED")
        self.assertIn("EV-005", chain["FIELD_DEPLOYMENT"]["evidence_refs"])

    def test_economic_boundaries_remain_explicit(self):
        economics = self.case["economic_state"]
        self.assertEqual(economics["CURRENT_REDUCTION"], "DERIVED")
        self.assertEqual(economics["RACK_SPACE"], "SOURCE_QUANTIFIED")
        self.assertEqual(economics["CAPEX"], "UNKNOWN")
        self.assertEqual(economics["FULL_ROI"], "NOT_CALCULABLE")
        self.assertEqual(economics["PAYBACK"], "NOT_CALCULABLE")

    def test_case_remains_private_and_unvalidated_market_state(self):
        self.assertEqual(self.case["publication_status"], "PRIVATE_DRAFT")
        self.assertEqual(self.payload["real_world_response"]["status"], "NOT_EVALUATED")
        self.assertEqual(self.payload["market_validation"]["status"], "NOT_EVALUATED")
        self.assertEqual(self.payload["structural_exposure"]["company"], [])
        self.assertEqual(self.payload["beneficiary_map"]["beneficiaries"], [])


if __name__ == "__main__":
    unittest.main()
