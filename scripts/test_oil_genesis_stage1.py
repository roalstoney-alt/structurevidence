#!/usr/bin/env python3
"""Stage 1 schema-boundary tests for OIL-GENESIS-001."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DICTIONARY_PATH = ROOT / "data/open-intent-lab/genesis-001/claim-dictionary.json"
FREEZE_PATH = ROOT / "docs/open-intent-lab/genesis/OIL_GENESIS_001_DOMAIN_FREEZE.md"
BASE_SHA = "f81fcbcbcab4891d0043eee8617f0a7b7f632ad2"

EXPECTED_STATUS_TERMS = {
    "SUPPORTED",
    "OBSERVED",
    "UNKNOWN",
    "NOT_ESTABLISHED",
    "CONTRADICTED",
}
CANONICAL_STATES = {
    "SUPPORTED",
    "OBSERVED",
    "UNKNOWN",
    "NOT_ESTABLISHED",
    "CONTRADICTED",
}
EXPECTED_VISIBILITY = ["PUBLIC", "AUTHORIZED_BUYER", "TRANSACTION_PRIVATE"]
EXPECTED_ORIGINS = [
    "GENESIS_SUBMISSION",
    "SUPPLIER_UPDATE",
    "DEMAND_TRIGGERED",
    "OUTCOME_GENERATED",
    "STRUCTEVIDENCE_RESEARCH",
]
EXPECTED_EVIDENCE_TYPES = {
    "THIRD_PARTY_CERTIFICATE",
    "THIRD_PARTY_TEST_REPORT",
    "MANUFACTURER_DATASHEET",
    "MANUFACTURER_DECLARATION",
    "FACTORY_DOCUMENT",
    "PHYSICAL_SAMPLE_OBSERVATION",
    "BUYER_TEST",
    "TRANSACTION_OUTCOME",
    "PUBLIC_CORPORATE_RECORD",
}
REQUIRED_CLAIM_FIELDS = {
    "claim_id",
    "claim_name",
    "claim_type",
    "normalized_claim",
    "scope",
    "unit",
    "operator",
    "value",
    "evidence_examples",
    "prohibited_overinterpretation",
}
FORBIDDEN_KEYS = {
    "supplier",
    "supplier_id",
    "provider_id",
    "legal_name",
    "trading_name",
    "official_domain",
    "identity_evidence_refs",
    "demand",
    "demand_id",
    "principal_ref",
    "decision_window",
    "rank",
    "ranking",
    "score",
    "confidence",
    "confidence_score",
    "evidence_records",
    "evidence_refs",
    "source_refs",
    "provenance_records",
    "capability_facts",
    "verified_capability_facts",
}


def load_dictionary() -> dict:
    with DICTIONARY_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_keys(child)


class StageOneDictionaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_dictionary()
        cls.claims = cls.data["claims"]

    def test_domain_identity_and_claim_count(self):
        self.assertEqual(self.data["domain_id"], "OIL-DOMAIN-001")
        self.assertEqual(self.data["domain_version"], "v0.1")
        self.assertEqual(self.data["experiment"], "OIL-GENESIS-001")
        self.assertEqual(len(self.claims), 7)

    def test_claim_ids_are_unique_and_stable_shape(self):
        ids = [claim["claim_id"] for claim in self.claims]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, [f"OIL-CAP-SIL-{index:03d}" for index in range(1, 8)])

    def test_claim_schema_units_operators_and_evidence_examples(self):
        allowed_units = set(self.data["allowed_units"])
        allowed_operators = set(self.data["allowed_operators"])
        evidence_types = set(self.data["evidence_type_enum"])
        for claim in self.claims:
            self.assertEqual(set(claim), REQUIRED_CLAIM_FIELDS)
            self.assertIn(claim["unit"], allowed_units)
            self.assertIn(claim["operator"], allowed_operators)
            self.assertTrue(claim["evidence_examples"])
            self.assertLessEqual(set(claim["evidence_examples"]), evidence_types)

    def test_status_mapping_is_exactly_one_to_one(self):
        mapping = self.data["canonical_status_mapping"]
        self.assertEqual(set(mapping), EXPECTED_STATUS_TERMS)
        self.assertEqual({entry["state"] for entry in mapping.values()}, CANONICAL_STATES)
        self.assertEqual(
            {term: entry["state"] for term, entry in mapping.items()},
            {term: term for term in EXPECTED_STATUS_TERMS},
        )
        self.assertNotEqual(mapping["OBSERVED"]["state"], "SUPPORTED")
        self.assertEqual(
            set(mapping["OBSERVED"]["required_fields"]),
            {"observation_scope", "source", "as_of"},
        )

    def test_supported_and_observed_coexist_in_append_only_history(self):
        rule = self.data["status_history_rule"]
        self.assertEqual(rule["update_mode"], "APPEND_ONLY")
        self.assertTrue(rule["coexisting_statuses_allowed"])
        self.assertTrue(rule["supported_and_observed_may_coexist"])
        self.assertFalse(rule["historic_overwrite_allowed"])

        history = [
            {"at": "T1", "state": "SUPPORTED"},
            {"at": "T2", "state": "OBSERVED"},
        ]
        self.assertEqual([record["state"] for record in history], ["SUPPORTED", "OBSERVED"])
        self.assertEqual(len(history), 2)

    def test_visibility_origin_and_evidence_type_enums(self):
        self.assertEqual(self.data["visibility_enum"], EXPECTED_VISIBILITY)
        self.assertEqual(self.data["fact_origin_enum"], EXPECTED_ORIGINS)
        self.assertEqual(set(self.data["evidence_type_enum"]), EXPECTED_EVIDENCE_TYPES)

    def test_dictionary_contains_definitions_not_operational_records(self):
        keys = set(walk_keys(self.data))
        self.assertFalse(keys & FORBIDDEN_KEYS, keys & FORBIDDEN_KEYS)
        self.assertNotIn("facts", keys)
        self.assertNotIn("outcomes", keys)
        self.assertNotIn("demands", keys)
        self.assertNotIn("providers", keys)

    def test_no_duplicate_evidence_truth_model(self):
        keys = set(walk_keys(self.data))
        self.assertNotIn("evidence_records", keys)
        self.assertNotIn("provenance_records", keys)
        self.assertNotIn("verified_capability_facts", keys)
        for claim in self.claims:
            self.assertTrue(all(isinstance(item, str) for item in claim["evidence_examples"]))

    def test_required_freeze_sections_exist(self):
        document = FREEZE_PATH.read_text(encoding="utf-8")
        required_sections = [
            "DOMAIN_ID",
            "DOMAIN_NAME",
            "WHY_SELECTED",
            "TESTABILITY",
            "EVIDENCE_ACCESSIBILITY",
            "REUSE_POTENTIAL",
            "OUTCOME_OBSERVABILITY",
            "REGULATORY_FRICTION",
            "FROZEN_CLAIM_DICTIONARY",
            "DEFERRED_CLAIMS",
            "REMOVED_CLAIMS",
            "CLAIM_ID_CONVENTION",
            "UNIT_NORMALIZATION",
            "STATUS_MAPPING",
            "AS_OF_RULE",
            "VISIBILITY_ENUM",
            "ACCESS_FAIL_CLOSED_RULE",
            "PROVIDER_MINIMUM_FIELDS",
            "DEMAND_TYPES",
            "FACT_ORIGIN_ENUM",
            "EVIDENCE_TYPE_MAPPING",
            "STOP_POINT_RULES",
            "OPEN_GAPS",
        ]
        for section in required_sections:
            self.assertIn(f"## {section}", document)

    def test_no_public_case_changes_from_authoritative_base(self):
        completed = subprocess.run(
            [
                "git",
                "diff",
                "--name-only",
                BASE_SHA,
                "--",
                "cases",
                "claims",
                "evidence",
                "docs/cases",
                "public",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
