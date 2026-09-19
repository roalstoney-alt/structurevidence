#!/usr/bin/env python3
"""Targeted tests for the CML-PDRE-001 Phase 2 L0 reuse audit."""

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "technical-risk/cml-v1.1/pdre/CML-PDRE-001"
PHASE2_DIR = ROOT / "rdl/research/records/CML-PDRE-001-PHASE-2"
RECORD_PATH = PHASE2_DIR / "research-record.json"
sys.path.insert(0, str(ROOT / "rdl/research/validation"))
import validator  # noqa: E402


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def all_keys(value):
    if isinstance(value, dict):
        return set(value) | set().union(*(all_keys(child) for child in value.values()), set())
    if isinstance(value, list):
        return set().union(*(all_keys(child) for child in value), set())
    return set()


class Phase2ReuseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = load(RECORD_PATH)
        cls.inventory = load(PHASE2_DIR / "evidence-inventory.json")
        cls.dependencies = load(PHASE2_DIR / "dependency-mappings.json")
        cls.gaps = load(PHASE2_DIR / "qualification-gaps.json")
        cls.candidates = load(PHASE2_DIR / "future-l1-candidates.json")
        cls.observations = load(PHASE2_DIR / "reuse-observations.json")
        cls.index_rows = [json.loads(line) for line in (CASE_DIR / "evidence-index.jsonl").read_text().splitlines()]
        cls.canonical_ids = {row["evidence_id"] for row in cls.index_rows if "evidence_id" in row}

    def test_a_all_research_actions_are_l0_without_external_research(self):
        payload = self.record["research_record"]
        self.assertEqual(payload["research_level"], "L0_REUSE")
        self.assertTrue(payload["research_actions"])
        for action in payload["research_actions"]:
            self.assertEqual(action["research_level"], "L0_REUSE")
            self.assertFalse(action["external_research"])

    def test_b_every_inventory_reference_resolves(self):
        self.assertEqual({row["evidence_id"] for row in self.inventory["evidence_items"]}, self.canonical_ids)
        for row in self.inventory["evidence_items"]:
            path = row["existing_record_ref"].split("#", 1)[0]
            self.assertTrue((ROOT / path).is_file(), path)

    def test_c_inventory_is_reference_view_not_parallel_evidence_store(self):
        self.assertFalse((ROOT / "rdl/research/evidence").exists())
        self.assertNotIn("claims", all_keys(self.inventory))
        self.assertIn("canonical_index_ref", self.inventory)
        self.assertEqual(self.inventory["normalization_policy"], "References only; canonical evidence content remains in the CML case container.")

    def test_d_unknown_qualification_is_not_false_zero_or_unsupported(self):
        self.assertEqual(len(self.gaps["dimensions"]), 14)
        self.assertTrue(all(row["state"] == "UNKNOWN" for row in self.gaps["dimensions"]))
        self.assertEqual(self.gaps["summary"]["UNSUPPORTED"], 0)

    def test_e_counter_evidence_is_preserved_and_separate(self):
        counter = {row["evidence_id"] for row in self.inventory["evidence_items"] if row["reuse_status"] == "REUSED_AS_COUNTER_EVIDENCE"}
        self.assertEqual(counter, {"EV-006", "EV-007"})
        self.assertEqual(set(self.record["research_record"]["counter_evidence_refs"]), counter)

    def test_f_event_and_knowledge_time_are_independent(self):
        for row in self.inventory["evidence_items"]:
            self.assertIn("event_time", row)
            self.assertIn("knowledge_time", row)
            self.assertNotEqual(row["event_time"], row["knowledge_time"])
        month = next(row for row in self.inventory["evidence_items"] if row["evidence_id"] == "EV-004")
        year = next(row for row in self.inventory["evidence_items"] if row["evidence_id"] == "EV-007")
        self.assertEqual(month["event_time_precision"], "MONTH")
        self.assertEqual(year["event_time_precision"], "YEAR")

    def test_g_tracked_historical_scopes_are_unchanged(self):
        changed = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD", "--", "technical-risk", "evidence", "rdl/freshness", "rtp", "ecn", "gdr"],
            cwd=ROOT,
            text=True,
        ).splitlines()
        self.assertEqual(changed, [])
        sys.path.insert(0, str(ROOT / "scripts"))
        import cml_v11_regression

        self.assertEqual(cml_v11_regression.historical_mutations(), [])

    def test_h_phase2_rdl_record_validates(self):
        result = validator.validate(self.record)
        self.assertEqual(result["research_level"], "L0_REUSE")
        self.assertEqual(result["new_evidence_count"], 0)
        self.assertFalse(result["evidence_store_created"])

    def test_i_record_hashes_bind_inputs_and_payload(self):
        bundle = {
            path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            for path in sorted(self.record["core"]["source_refs"])
        }
        self.assertEqual(self.record["core"]["input_hash"], digest(bundle))
        core = dict(self.record["core"])
        actual = core.pop("record_hash")
        self.assertEqual(actual, digest({"core": core, "payload": self.record["research_record"]}))

    def test_j_reuse_observables_and_ratio_are_transparent(self):
        counts = self.observations["counts"]
        self.assertEqual(counts["TOTAL_EXISTING_EVIDENCE_ITEMS"], 7)
        self.assertEqual(counts["TOTAL_EVIDENCE_ITEMS_INSPECTED"], 7)
        numerator = counts["REUSED_DIRECTLY_COUNT"] + counts["REUSED_WITH_NORMALIZATION_COUNT"] + counts["COUNTER_EVIDENCE_REUSED_COUNT"]
        ratio = self.observations["research_reuse_ratio"]
        self.assertEqual((numerator, ratio["denominator"], ratio["value"]), (7, 7, 1.0))
        self.assertTrue(ratio["not_a_score"])

    def test_k_no_opaque_score_or_private_customer_data(self):
        prohibited_keys = {"gap_score", "research_score", "commercial_score", "mev_score", "private_bom", "private_pricing", "customer_secret"}
        for artifact in (self.inventory, self.dependencies, self.gaps, self.candidates, self.observations, self.record):
            self.assertFalse({key.lower() for key in all_keys(artifact)} & prohibited_keys)
        self.assertIsNone(self.record["research_record"]["customer_case_id"])

    def test_l_cml_readiness_is_reused_not_reassigned(self):
        mapping_a, mapping_b = self.dependencies["mappings"]
        self.assertEqual(mapping_a["migration_readiness"], "R3_SAMPLE_BENCH_TESTED")
        self.assertEqual(mapping_a["structural_exposure"], "UNKNOWN")
        self.assertEqual(mapping_b["migration_readiness"], "NOT_ASSIGNED")
        self.assertEqual(mapping_b["structural_exposure"], "UNKNOWN")
        self.assertEqual(self.record["research_record"]["structural_interpretation_authority"], "CML_REFERENCE_ONLY")

    def test_m_freshness_unknown_is_not_promoted_to_current(self):
        self.assertTrue(all(row["freshness_state"] == "UNKNOWN_FRESHNESS" for row in self.inventory["evidence_items"]))
        freshness = self.observations["freshness"]
        self.assertEqual(freshness["CURRENT"], 0)
        self.assertEqual(freshness["UNKNOWN_FRESHNESS"], 7)

    def test_n_future_l1_candidates_are_not_executed_or_scored(self):
        self.assertFalse(self.candidates["execution_authorized"])
        self.assertEqual(len(self.candidates["candidates"]), 6)
        self.assertTrue(all(row["recommended_research_level"] in {"L1_VERIFY", "DO_NOT_RESEARCH"} for row in self.candidates["candidates"]))
        self.assertFalse({"gap_score", "research_score", "commercial_score", "MEV_score"} & all_keys(self.candidates))

    def test_o_phase1_schema_and_validator_are_unchanged(self):
        expected = {
            "rdl/research/schema/research-record.schema.json": "55f733e68798bf53bf8fe41e14b2e1cc56fae67e75ad811cfa1cb3cc1a0b1d1d",
            "rdl/research/validation/validator.py": "f891cdba07d32d866633513a3e1d139bfaaec08b5d2984bb49b57440921faf66",
        }
        actual = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in expected}
        self.assertEqual(actual, expected)

    def test_p_all_reusable_assets_resolve(self):
        for path in self.record["research_record"]["reusable_asset_refs"]:
            self.assertTrue((ROOT / path).is_file(), path)


if __name__ == "__main__":
    unittest.main()
