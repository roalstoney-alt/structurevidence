#!/usr/bin/env python3
"""Targeted tests for the evidence-empty CML-PDRE-001 case container."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "technical-risk/cml-v1.1/pdre/CML-PDRE-001"
EXPECTED_FILES = {
    "CASE.json",
    "README.md",
    "dependency-transfer.json",
    "evidence-index.jsonl",
    "state-history.jsonl",
    "timeline.jsonl",
}
TRACKING_DIMENSIONS = {
    "ARCHITECTURE",
    "MIGRATION_READINESS",
    "ADOPTION_FRICTION",
    "STRUCTURAL_EXPOSURE",
    "BENEFICIARY_MAP",
    "DEPENDENCY_RELEASE",
    "DEPENDENCY_TRANSFER",
    "ECONOMICS",
    "REAL_WORLD_RESPONSE",
    "MARKET_VALIDATION",
}
TRANSFER_CATEGORIES = [
    "COPPER",
    "POWER_SEMICONDUCTOR",
    "DC_PROTECTION",
    "DC_DC_CONVERSION",
    "HIGH_FREQUENCY_TRANSFORMER",
    "MAGNETIC_MATERIAL",
    "INSULATION",
    "PARTIAL_DISCHARGE",
    "THERMAL_MANAGEMENT",
    "CONNECTOR_BUSWAY",
    "ENERGY_STORAGE",
]


def load_jsonl(name):
    lines = (CASE_DIR / name).read_text().splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def walk(value):
    yield value
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


class CMLPDRE001InitializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = json.loads((CASE_DIR / "CASE.json").read_text())
        cls.transfer = json.loads((CASE_DIR / "dependency-transfer.json").read_text())

    def test_expected_container_files_exist(self):
        self.assertEqual({path.name for path in CASE_DIR.iterdir()}, EXPECTED_FILES)

    def test_case_identity_and_private_discovery_state(self):
        self.assertEqual(self.case["case_id"], "CML-PDRE-001")
        self.assertEqual(self.case["method_version"], "CML_v1.1")
        self.assertEqual(self.case["research_status"], "DISCOVERY_ACTIVE")
        self.assertEqual(self.case["publication_status"], "PRIVATE_DRAFT")
        self.assertTrue(self.case["initialization_only"])
        self.assertEqual(self.case["approved_evidence_packet_count"], 0)
        self.assertEqual(
            self.case["pdre_record_status"],
            "NOT_INSTANTIATED_PENDING_APPROVED_EVIDENCE",
        )

    def test_research_units_are_explicit_and_distinct(self):
        units = {item["pdre_unit_id"]: item for item in self.case["research_units"]}
        self.assertEqual(set(units), {"PDRE-001A", "PDRE-001B"})
        self.assertEqual(units["PDRE-001A"]["old_path"], "54V in-rack distribution")
        self.assertEqual(units["PDRE-001A"]["new_path"], "800VDC sidecar / power rack")
        self.assertEqual(
            units["PDRE-001B"]["old_path"],
            "Traditional facility AC conversion chain",
        )
        self.assertEqual(units["PDRE-001B"]["new_path"], "Centralized 800VDC / SST")

    def test_no_migration_readiness_level_is_assigned(self):
        for unit in self.case["research_units"]:
            readiness = unit["migration_readiness"]
            self.assertEqual(readiness["assignment_status"], "NOT_ASSIGNED")
            self.assertIsNone(readiness["code"])
            self.assertEqual(readiness["evidence_refs"], [])
        assigned_codes = {f"R{number}" for number in range(8)}
        self.assertFalse(
            any(
                isinstance(value, str) and value in assigned_codes
                for value in walk(self.case)
            )
        )

    def test_all_required_dimensions_are_tracked_without_inferred_results(self):
        self.assertEqual(set(self.case["tracking_dimensions"]), TRACKING_DIMENSIONS)
        self.assertEqual(self.case["tracking_dimensions"]["MIGRATION_READINESS"], "NOT_ASSIGNED")
        self.assertNotIn("PASS", self.case["tracking_dimensions"].values())
        self.assertNotIn("FAIL", self.case["tracking_dimensions"].values())

    def test_dependency_transfer_categories_are_complete_and_unknown(self):
        rows = self.transfer["categories"]
        self.assertEqual([row["category"] for row in rows], TRANSFER_CATEGORIES)
        self.assertEqual(self.transfer["assessment_status"], "NOT_ASSESSED")
        for row in rows:
            for unit_id in ("PDRE-001A", "PDRE-001B"):
                self.assertEqual(row[unit_id]["dependency_release"], "UNKNOWN")
                self.assertEqual(row[unit_id]["dependency_transfer"], "UNKNOWN")
                self.assertEqual(row[unit_id]["evidence_refs"], [])

    def test_evidence_index_and_append_only_logs_are_initialized_without_evidence(self):
        evidence = load_jsonl("evidence-index.jsonl")
        timeline = load_jsonl("timeline.jsonl")
        states = load_jsonl("state-history.jsonl")
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0]["status"], "NO_APPROVED_EVIDENCE_PACKET")
        self.assertEqual(evidence[0]["approved_evidence_packet_count"], 0)
        self.assertEqual(evidence[0]["evidence_refs"], [])
        self.assertEqual(timeline[0]["event_domain"], "RESEARCH_ADMINISTRATION")
        self.assertEqual(timeline[0]["evidence_refs"], [])
        self.assertEqual(states[0]["research_status"], "DISCOVERY_ACTIVE")
        self.assertEqual(states[0]["publication_status"], "PRIVATE_DRAFT")
        self.assertEqual(states[0]["evidence_refs"], [])

    def test_schema_bindings_reuse_accepted_cml_v11_schemas(self):
        bindings = self.case["schema_bindings"]
        self.assertEqual(
            set(bindings),
            {
                "pdre_record",
                "dependency_record",
                "structural_exposure",
                "beneficiary_map",
                "real_world_response",
                "market_validation",
            },
        )
        for relative_path in bindings.values():
            self.assertTrue((ROOT / relative_path).is_file(), relative_path)

    def test_no_url_or_external_source_was_added(self):
        url_pattern = re.compile(r"https?://", re.IGNORECASE)
        for path in CASE_DIR.iterdir():
            self.assertIsNone(url_pattern.search(path.read_text()), path.name)
        self.assertFalse(any(key == "source_refs" for key in walk(self.case)))

    def test_scope_statements_are_labeled_not_evidence(self):
        paths = self.case["scope_paths"]
        for path in paths.values():
            self.assertEqual(path["provenance"], "USER_PROVIDED_RESEARCH_SCOPE")
            self.assertEqual(path["evidence_status"], "NOT_EVIDENCE")
        for unit in self.case["research_units"]:
            self.assertEqual(unit["scope_provenance"], "USER_PROVIDED_RESEARCH_SCOPE")


if __name__ == "__main__":
    unittest.main()
