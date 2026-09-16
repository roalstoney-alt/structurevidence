#!/usr/bin/env python3
"""Positive and adversarial tests for the Phase A boundary (no output writes)."""
import copy
import unittest
from unittest.mock import patch

import jsonschema

import validate_cml_ov_phase_a as ov


class PhaseATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = [ov.load(row["path"]) for row in ov.load(ov.PREFIX + "/INDEX.json")["records"]]

    def mutate(self, path, value):
        record = copy.deepcopy(self.records[0])
        node = record
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
        return record

    def assert_gate_fails(self, record, gate):
        with self.assertRaises((ValueError, KeyError, jsonschema.ValidationError)):
            ov.GATES[gate](record)

    def test_four_initializations_and_package(self):
        jsonschema.Draft202012Validator.check_schema(ov.load(ov.PREFIX + "/schema/record.schema.json"))
        self.assertEqual(ov.package_gate()["records"], 4)
        for record in self.records:
            with self.subTest(record=record["core"]["record_id"]):
                rows = ov.evaluate(record)
                self.assertTrue(all(row["status"] == "PASS" for row in rows), rows)
                self.assertEqual(ov.release_effect(record)["paid_delivery"], "BLOCK")

    def test_package_rejects_missing_mapping_and_manifest_tampering(self):
        original_load = ov.load
        for target, key, value in [
            ("INDEX.json", "records", []),
            ("PHASE_A_MANIFEST.json", "artifact_hashes", {}),
            ("PHASE_A_MANIFEST.json", "release_state", "ALLOW"),
        ]:
            changed = copy.deepcopy(original_load(ov.PREFIX + "/" + target))
            changed[key] = value

            def fixture(path):
                return changed if path == ov.PREFIX + "/" + target else original_load(path)

            with self.subTest(target=target, key=key), patch.object(ov, "load", side_effect=fixture):
                with self.assertRaises(ValueError):
                    ov.package_gate()

    def test_pain_efficiency_and_improvement_cannot_be_inferred(self):
        for layer, field in [("problem_persistence", "active_customer_pain"), ("problem_persistence", "internal_resolution"), ("current_solution_audit", "solution_efficiency"), ("solution_improvement_potential", "measurable_improvement")]:
            with self.subTest(field=field):
                record = self.mutate(["opportunity_validation", layer, field], {"state": "SUPPORTED", "value": True, "evidence_refs": ["PUBLIC_LIFECYCLE"]})
                self.assert_gate_fails(record, "OV-A05_UNASSESSED")
                self.assert_gate_fails(record, "OV-A01_SCHEMA")

    def test_lower_unit_price_cannot_establish_total_savings(self):
        record = self.mutate(["opportunity_validation", "solution_improvement_potential", "cost_assessment", "total_migration_cost", "value"], -100)
        self.assert_gate_fails(record, "OV-A05_UNASSESSED")

    def test_all_private_fields_and_numeric_scores_rejected(self):
        fields = ov.load("technical-risk/config/public_private_boundary.json")["private"] + ["risk_score", "replacement_probability"]
        for key in fields:
            with self.subTest(key=key):
                record = self.mutate(["opportunity_validation", "current_solution_audit", key], {"nested": "private"})
                self.assert_gate_fails(record, "OV-A06_BOUNDARY")
                self.assert_gate_fails(record, "OV-A01_SCHEMA")

    def test_baseline_mapping_states_conflicts_and_clock_preserved(self):
        for key, value in {"record_hash": "0" * 64, "record_path": "../../other.json", "lifecycle_state": "ACTIVE", "qualification_state": "CUSTOMER_APPROVED", "counter_evidence": "none", "unknowns": [], "event_known_at": "2030-01-01T00:00:00Z", "identity_scope": "FAMILY_EVENT"}.items():
            with self.subTest(key=key):
                self.assert_gate_fails(self.mutate(["opportunity_validation", "baseline", key], value), "OV-A02_BASELINE")

    def test_ov03_active_and_ov04_family_scope(self):
        self.assertEqual(self.records[2]["opportunity_validation"]["baseline"]["lifecycle_state"], "ACTIVE")
        self.assertEqual(self.records[3]["opportunity_validation"]["baseline"]["identity_scope"], "FAMILY_EVENT")

    def test_hash_tampering_and_domain_identity(self):
        self.assert_gate_fails(self.mutate(["core", "record_hash"], "0" * 64), "OV-A04_HASH_INTEGRITY")
        for key, value in {"domain": "OTHER", "subject_id": "OTHER_PART", "known_at": "2030-01-01T00:00:00Z", "source_refs": [], "artifact_refs": [], "correction_status": "MATERIAL_CORRECTION_OPEN", "supersession_status": "SUPERSEDED"}.items():
            with self.subTest(key=key):
                self.assert_gate_fails(self.mutate(["core", key], value), "OV-A03_SHARED_ENVELOPE")

    def test_authority_and_freshness_cannot_be_promoted(self):
        for key in ["public_release", "paid_delivery", "solution_development", "opportunity_qualification"]:
            self.assert_gate_fails(self.mutate(["opportunity_validation", "governance", key], "ALLOW"), "OV-A07_GOVERNANCE")
        self.assert_gate_fails(self.mutate(["opportunity_validation", "freshness_state"], "CURRENT"), "OV-A07_GOVERNANCE")

    def test_missing_layers_extra_claims_and_malformed_record_fail_closed(self):
        record = copy.deepcopy(self.records[0])
        del record["opportunity_validation"]["current_solution_audit"]
        self.assert_gate_fails(record, "OV-A01_SCHEMA")
        record = self.mutate(["opportunity_validation", "drop_in_claim"], True)
        self.assert_gate_fails(record, "OV-A01_SCHEMA")
        result = ov.release_effect({})
        self.assertEqual(result["public_release"], "BLOCK")
        self.assertEqual(result["reason"], "PHASE_A_VALIDATION_FAILED")


if __name__ == "__main__":
    unittest.main()
