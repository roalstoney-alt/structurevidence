#!/usr/bin/env python3
"""Targeted and adversarial tests for RDL_RESEARCH_RECORD_v0.1."""

import copy
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATION_DIR = ROOT / "rdl/research/validation"
sys.path.insert(0, str(VALIDATION_DIR))
import validator  # noqa: E402


FIXTURE_DIR = ROOT / "rdl/research/fixtures"
SCHEMA_PATH = ROOT / "rdl/research/schema/research-record.schema.json"
TEMPLATE_PATH = ROOT / "rdl/research/templates/research-record.template.json"
PHASE1_RECORD_PATH = ROOT / "rdl/research/records/RDL-METHODOLOGY-PHASE-1-2026-09-19.json"


def load(path):
    return json.loads(Path(path).read_text())


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class RDLResearchRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = {path.name: load(path) for path in sorted(FIXTURE_DIR.glob("*.json"))}

    def assert_rejects(self, record):
        with self.assertRaises((ValueError, Exception)):
            validator.validate(record)

    def test_all_six_required_fixtures_validate(self):
        self.assertEqual(len(self.fixtures), 6)
        results = [validator.validate(record) for record in self.fixtures.values()]
        self.assertEqual(len(results), 6)

    def test_template_is_schema_valid_but_not_ingested(self):
        validator.schema_validate(load(TEMPLATE_PATH))
        self.assertIn("REPLACE_BEFORE_INGESTION", TEMPLATE_PATH.read_text())

    def test_phase1_canonical_record_validates_as_l0(self):
        record = load(PHASE1_RECORD_PATH)
        result = validator.validate(record)
        self.assertEqual(result["research_level"], "L0_REUSE")
        self.assertEqual(result["stop_reason"], "PHASE_COMPLETE")
        self.assertFalse(result["evidence_store_created"])
        self.assertTrue(all(not row["external_research"] for row in record["research_record"]["research_actions"]))

    def test_phase1_record_hashes_bind_inputs_and_payload(self):
        record = load(PHASE1_RECORD_PATH)
        input_bundle = {
            path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            for path in sorted(record["core"]["source_refs"])
        }
        self.assertEqual(record["core"]["input_hash"], digest(input_bundle))
        core = dict(record["core"])
        actual = core.pop("record_hash")
        self.assertEqual(actual, digest({"core": core, "payload": record["research_record"]}))

    def test_existing_evidence_core_is_reused(self):
        schema = load(SCHEMA_PATH)
        self.assertEqual(
            schema["properties"]["core"]["$ref"],
            "../../../evidence/core/schema/evidence_core_record.schema.json",
        )
        self.assertFalse((ROOT / "rdl/research/evidence").exists())

    def test_l0_reuse_has_no_external_research(self):
        record = self.fixtures["fixture-a-l0-reuse.json"]
        result = validator.validate(record)
        self.assertEqual(result["research_level"], "L0_REUSE")
        self.assertTrue(all(not row["external_research"] for row in record["research_record"]["research_actions"]))

    def test_l1_verification_resolves_one_unknown(self):
        record = self.fixtures["fixture-b-l1-verification.json"]
        result = validator.validate(record)
        self.assertEqual(result["new_evidence_count"], 1)
        self.assertEqual(record["research_record"]["unknowns_resolved"], ["FACT-B"])

    def test_duplicate_only_is_valid_failed_research(self):
        result = validator.validate(self.fixtures["fixture-c-duplicate-only.json"])
        self.assertEqual(result["stop_reason"], "DUPLICATE_ONLY")
        self.assertEqual(result["new_evidence_count"], 0)
        self.assertEqual(result["duplicate_evidence_count"], 1)

    def test_public_data_insufficient_with_no_new_evidence_is_valid(self):
        result = validator.validate(self.fixtures["fixture-d-public-data-insufficient.json"])
        self.assertEqual(result["stop_reason"], "PUBLIC_DATA_INSUFFICIENT")
        self.assertEqual(result["new_evidence_count"], 0)

    def test_decision_change_requires_actual_delta_and_reason(self):
        record = copy.deepcopy(self.fixtures["fixture-e-decision-changed.json"])
        validator.validate(record)
        record["research_record"]["decision_after"] = record["research_record"]["decision_before"]
        self.assert_rejects(record)
        record = copy.deepcopy(self.fixtures["fixture-e-decision-changed.json"])
        record["research_record"]["decision_change_reason"] = None
        self.assert_rejects(record)

    def test_unknown_telemetry_is_null_not_zero(self):
        record = copy.deepcopy(self.fixtures["fixture-f-unknown-telemetry.json"])
        for field, value in record["research_record"]["telemetry"].items():
            if isinstance(value, dict):
                self.assertEqual(value["status"], "UNKNOWN")
                self.assertIsNone(value["value"])
        record["research_record"]["telemetry"]["observed_input_tokens"]["value"] = 0
        self.assert_rejects(record)

    def test_estimated_and_observed_cost_are_distinct(self):
        record = copy.deepcopy(self.fixtures["fixture-b-l1-verification.json"])
        self.assertEqual(record["research_record"]["telemetry"]["estimated_model_cost"]["status"], "ESTIMATED")
        self.assertEqual(record["research_record"]["telemetry"]["observed_model_cost"]["status"], "UNKNOWN")
        record["research_record"]["telemetry"]["estimated_model_cost"]["status"] = "OBSERVED"
        self.assert_rejects(record)

    def test_event_evidence_cannot_be_new_and_duplicate(self):
        record = copy.deepcopy(self.fixtures["fixture-b-l1-verification.json"])
        record["research_record"]["duplicate_evidence_refs"] = ["EV-B-NEW"]
        self.assert_rejects(record)

    def test_used_or_rejected_source_must_have_been_checked(self):
        record = copy.deepcopy(self.fixtures["fixture-b-l1-verification.json"])
        record["research_record"]["source_refs_checked"] = []
        self.assert_rejects(record)

    def test_l2_l3_require_external_authorization_state(self):
        record = copy.deepcopy(self.fixtures["fixture-b-l1-verification.json"])
        record["research_record"]["research_level"] = "L2_INVESTIGATE"
        record["research_record"]["research_actions"][0]["research_level"] = "L2_INVESTIGATE"
        self.assert_rejects(record)
        record["research_record"]["authorization"] = {
            "status": "REQUIRED_PENDING",
            "authorization_ref": None,
            "authority": "HUMAN",
        }
        validator.validate(record)

    def test_authorized_l3_requires_authorization_reference(self):
        record = copy.deepcopy(self.fixtures["fixture-b-l1-verification.json"])
        record["research_record"]["research_level"] = "L3_DEEP"
        record["research_record"]["research_actions"][0]["research_level"] = "L3_DEEP"
        record["research_record"]["authorization"] = {
            "status": "AUTHORIZED",
            "authorization_ref": None,
            "authority": "HUMAN",
        }
        self.assert_rejects(record)
        record["research_record"]["authorization"]["authorization_ref"] = "HUMAN-AUTH-001"
        validator.validate(record)

    def test_rdl_cannot_claim_structural_authority(self):
        record = copy.deepcopy(self.fixtures["fixture-a-l0-reuse.json"])
        record["research_record"]["structural_interpretation_authority"] = "RDL"
        self.assert_rejects(record)

    def test_public_company_does_not_imply_customer_specific_research(self):
        record = copy.deepcopy(self.fixtures["fixture-a-l0-reuse.json"])
        record["research_record"]["customer_case_id"] = "COMPANY-IN-PUBLIC-EVIDENCE"
        self.assert_rejects(record)

    def test_private_raw_data_and_opaque_scores_are_rejected(self):
        for field in ("raw_private_prompt", "confidence_score", "mev_score"):
            record = copy.deepcopy(self.fixtures["fixture-a-l0-reuse.json"])
            record["research_record"][field] = "PROHIBITED"
            self.assert_rejects(record)

    def test_stop_reason_extension_is_forward_compatible(self):
        record = copy.deepcopy(self.fixtures["fixture-a-l0-reuse.json"])
        record["research_record"]["stop_reason"] = "EXTENSION_DOMAIN_SPECIFIC_STOP"
        validator.validate(record)

    def test_corrections_must_preserve_original(self):
        record = copy.deepcopy(self.fixtures["fixture-a-l0-reuse.json"])
        record["research_record"]["revision_history"][0]["preserves_original"] = False
        self.assert_rejects(record)

    def test_search_memory_lookup_fields_are_present(self):
        required = {"claim_refs", "hypothesis_refs", "entity_refs", "component_refs", "standard_refs", "migration_path_refs"}
        for record in self.fixtures.values():
            self.assertEqual(set(record["research_record"]["lookup_keys"]), required)

    def test_existing_cml_historical_files_remain_unchanged(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import cml_v11_regression

        self.assertEqual(cml_v11_regression.historical_mutations(), [])

    def test_rdl_freshness_implementation_is_unmodified(self):
        changed = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD", "--", "rdl/freshness"],
            cwd=ROOT,
            text=True,
        ).splitlines()
        self.assertEqual(changed, [])


if __name__ == "__main__":
    unittest.main()
