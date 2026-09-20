#!/usr/bin/env python3
"""Targeted tests for Phase 2.5 human research-capital allocation."""

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "rdl/research/records/CML-PDRE-001-PHASE-2/future-l1-candidates.json"
CANDIDATE_SET_PATH = ROOT / "rdl/research/allocation/CML_PDRE_001_PHASE_2_5_CANDIDATES.json"
ALLOCATION_PATH = ROOT / "rdl/research/allocation/CML_PDRE_001_PHASE_2_5_ALLOCATION.json"
RECORD_PATH = ROOT / "rdl/research/records/CML-PDRE-001-PHASE-2-5/research-record.json"
INDEX_PATH = ROOT / "technical-risk/cml-v1.1/pdre/CML-PDRE-001/evidence-index.jsonl"
BASELINE_SHA = "c690e2a890878056aecc057dc0afafbd3729164f"
SOURCE_SHA = "f2f87855e2a448b5b5322b342feff46e6027c8d1fd85eec9bf638499b1d97d3e"
sys.path.insert(0, str(ROOT / "rdl/research/validation"))
import validator  # noqa: E402


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def keys(value):
    if isinstance(value, dict):
        return set(value) | set().union(*(keys(child) for child in value.values()), set())
    if isinstance(value, list):
        return set().union(*(keys(child) for child in value), set())
    return set()


class Phase25AllocationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load(SOURCE_PATH)
        cls.candidate_set = load(CANDIDATE_SET_PATH)
        cls.allocation = load(ALLOCATION_PATH)
        cls.record = load(RECORD_PATH)
        cls.cards = cls.allocation["allocation_cards"]
        cls.index_ids = {
            row["evidence_id"]
            for row in (json.loads(line) for line in INDEX_PATH.read_text(encoding="utf-8").splitlines())
            if "evidence_id" in row
        }

    def test_a_baseline_and_annotated_tag_match(self):
        self.assertEqual(subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), BASELINE_SHA)
        self.assertEqual(
            subprocess.check_output(["git", "rev-parse", "structevidence-rdl-research-baseline-v0.1^{}"], cwd=ROOT, text=True).strip(),
            BASELINE_SHA,
        )
        self.assertEqual(subprocess.check_output(["git", "cat-file", "-t", "structevidence-rdl-research-baseline-v0.1"], cwd=ROOT, text=True).strip(), "tag")

    def test_b_human_entry_exception_is_exact(self):
        gate = self.candidate_set["entry_gate"]
        self.assertEqual(gate["status"], "PASS_WITH_HUMAN_EXCEPTION")
        self.assertEqual(gate["tracked_baseline_mutation_count"], 0)
        self.assertEqual(gate["staged_change_count"], 0)
        self.assertEqual(gate["unexpected_relevant_untracked_path_count"], 0)
        self.assertEqual(
            {row["path"] for row in gate["approved_ignore_set"]},
            {"carepathchina-update/", "stoneyrola-update/"},
        )
        for row in gate["approved_ignore_set"]:
            self.assertEqual(row["human_status"], "HUMAN_CLASSIFIED_UNRELATED")
            self.assertEqual(row["gate_treatment"], "IGNORED_FOR_PHASE_ENTRY_GATE")

    def test_c_candidate_source_hash_and_freeze(self):
        self.assertEqual(hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest(), SOURCE_SHA)
        source_ids = [row["gap_id"] for row in self.source["candidates"]]
        self.assertEqual(self.candidate_set["source_sha256"], SOURCE_SHA)
        self.assertEqual(self.candidate_set["candidate_count"], 6)
        self.assertEqual(self.candidate_set["candidate_ids"], source_ids)
        self.assertFalse(self.candidate_set["set_mutation_allowed"])

    def test_d_input_and_output_candidate_sets_are_identical(self):
        source = {row["gap_id"]: row["question"] for row in self.source["candidates"]}
        output = {row["candidate_id"]: row["question"] for row in self.cards}
        self.assertEqual(len(source), 6)
        self.assertEqual(len(output), 6)
        self.assertEqual(output, source)

    def test_e_all_rdl_actions_are_l0_without_external_research(self):
        payload = self.record["research_record"]
        self.assertEqual(payload["research_level"], "L0_REUSE")
        self.assertTrue(all(action["research_level"] == "L0_REUSE" for action in payload["research_actions"]))
        self.assertTrue(all(not action["external_research"] for action in payload["research_actions"]))
        self.assertFalse(self.allocation["external_research_performed"])

    def test_f_authorization_and_human_decisions_remain_pending(self):
        self.assertEqual(len(self.cards), 6)
        self.assertTrue(all(card["authorized_research_level"] == "PENDING_HUMAN_DECISION" for card in self.cards))
        self.assertTrue(all(card["human_decision"] == "PENDING" for card in self.cards))
        self.assertEqual(self.allocation["summary"]["authorized_l1_count"], 0)
        self.assertEqual(self.allocation["summary"]["human_decisions_pending"], 6)

    def test_g_no_l1_execution_or_new_evidence(self):
        self.assertFalse(self.allocation["l1_execution_performed"])
        self.assertFalse(self.candidate_set["execution_authorized"])
        self.assertEqual(self.record["research_record"]["new_evidence_refs"], [])
        self.assertEqual(self.record["research_record"]["authorization"]["status"], "REQUIRED_PENDING")

    def test_h_current_evidence_references_resolve(self):
        for card in self.cards:
            for ref in card["current_evidence_refs"] + card["counter_evidence_refs"]:
                self.assertIn(ref["evidence_id"], self.index_ids)
                path = ref["artifact_ref"].split("#", 1)[0]
                self.assertTrue((ROOT / path).is_file(), path)

    def test_i_every_card_has_required_allocation_fields(self):
        required = {
            "candidate_id", "question", "source_gap_ref", "current_state", "current_evidence_refs",
            "counter_evidence_refs", "current_unknown", "freshness_state", "decision_affected",
            "decision_before_research", "decision_possible_after_research", "can_current_decision_proceed_without_research",
            "minimum_new_evidence_needed", "minimum_source_class_needed", "research_scope",
            "expected_information_gain", "expected_decision_impact", "expected_reuse", "expected_commercial_relevance",
            "estimated_model_cost", "estimated_data_cost", "estimated_human_cost", "estimated_engineering_cost",
            "cost_confidence", "stop_condition", "codex_recommended_action", "recommendation_reason",
            "authorized_research_level", "human_decision", "human_decision_reason",
        }
        for card in self.cards:
            self.assertEqual(set(card), required)

    def test_j_cost_unknown_is_not_zero(self):
        fields = ("estimated_model_cost", "estimated_data_cost", "estimated_human_cost", "estimated_engineering_cost")
        for card in self.cards:
            for field in fields:
                self.assertEqual(card[field]["status"], "UNKNOWN")
                self.assertIsNone(card[field]["value"])
            self.assertEqual(card["cost_confidence"], "UNKNOWN")
        self.assertEqual(self.record["research_record"]["telemetry"]["data_cost"]["value"], 0)

    def test_k_scope_and_recommendation_rules_hold(self):
        allowed = {"L1_VERIFY", "WATCH", "DEFER", "DEFER_L2_REVIEW", "DO_NOT_RESEARCH"}
        for card in self.cards:
            self.assertIn(card["codex_recommended_action"], allowed)
            if card["codex_recommended_action"] == "L1_VERIFY":
                self.assertIn(card["research_scope"], {"VERY_NARROW", "NARROW"})
            if card["research_scope"] == "BOUNDED_MULTI_SOURCE":
                self.assertEqual(card["codex_recommended_action"], "DEFER_L2_REVIEW")
            if card["research_scope"] == "UNCERTAIN":
                self.assertEqual(card["codex_recommended_action"], "DEFER")

    def test_l_recommendation_counts_are_exact(self):
        summary = self.allocation["summary"]
        self.assertEqual(summary["input_candidate_count"], 6)
        self.assertEqual(summary["output_allocation_card_count"], 6)
        self.assertEqual(
            {key: summary[key] for key in ("L1_VERIFY", "WATCH", "DEFER", "DEFER_L2_REVIEW", "DO_NOT_RESEARCH")},
            {"L1_VERIFY": 1, "WATCH": 1, "DEFER": 0, "DEFER_L2_REVIEW": 4, "DO_NOT_RESEARCH": 0},
        )

    def test_m_no_opaque_score_fields(self):
        prohibited = {"voi_score", "mev_score", "research_priority_score", "composite_score", "commercial_score"}
        for artifact in (self.candidate_set, self.allocation, self.record):
            self.assertFalse({key.lower() for key in keys(artifact)} & prohibited)

    def test_n_rdl_record_validates(self):
        result = validator.validate(self.record)
        self.assertEqual(result["research_level"], "L0_REUSE")
        self.assertEqual(result["stop_reason"], "HUMAN_REVIEW_REQUIRED")
        self.assertEqual(result["new_evidence_count"], 0)
        self.assertFalse(result["evidence_store_created"])

    def test_o_rdl_record_hashes_bind_inputs_and_payload(self):
        bundle = {
            path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            for path in sorted(self.record["core"]["source_refs"])
        }
        self.assertEqual(self.record["core"]["input_hash"], digest(bundle))
        core = dict(self.record["core"])
        actual = core.pop("record_hash")
        self.assertEqual(actual, digest({"core": core, "payload": self.record["research_record"]}))

    def test_p_unrelated_paths_are_not_inputs_evidence_or_outputs(self):
        prohibited = {"carepathchina-update/", "stoneyrola-update/"}
        core = self.record["core"]
        payload = self.record["research_record"]
        referenced = set(core["source_refs"]) | set(core["artifact_refs"]) | set(payload["source_refs_checked"]) | set(payload["source_refs_used"])
        self.assertFalse(prohibited & referenced)
        for action in payload["research_actions"]:
            self.assertFalse(prohibited & set(action["input_refs"]))
            self.assertFalse(prohibited & set(action["output_refs"]))

    def test_q_no_tracked_historical_mutation(self):
        changed = subprocess.check_output(["git", "diff", "--name-only", "HEAD"], cwd=ROOT, text=True).splitlines()
        self.assertEqual(changed, [])
        staged = subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).splitlines()
        self.assertEqual(staged, [])
        sys.path.insert(0, str(ROOT / "scripts"))
        import cml_v11_regression

        self.assertEqual(cml_v11_regression.historical_mutations(), [])


if __name__ == "__main__":
    unittest.main()
