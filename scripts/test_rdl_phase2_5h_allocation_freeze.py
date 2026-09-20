#!/usr/bin/env python3
"""Targeted tests for Phase 2.5H human allocation freeze."""

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "rdl/research/records/CML-PDRE-001-PHASE-2/future-l1-candidates.json"
MACHINE_PATH = ROOT / "rdl/research/allocation/CML_PDRE_001_PHASE_2_5_ALLOCATION.json"
DECISIONS_PATH = ROOT / "rdl/research/allocation/CML_PDRE_001_PHASE_2_5_HUMAN_DECISIONS.json"
RESCOPE_PATH = ROOT / "rdl/research/allocation/CML_PDRE_001_PHASE_2_5H_CANDIDATE_001_RESCOPE.json"
DECOMPOSITION_PATH = ROOT / "rdl/research/allocation/CML_PDRE_001_PHASE_2_5H_CANDIDATE_005_DECOMPOSITION.json"
AUTH_DIR = ROOT / "rdl/research/authorization"
AUTH_PATH = AUTH_DIR / "L1-CML-PDRE-001-FIELD-DEPLOYMENT-VERIFY.json"
RECORD_PATH = ROOT / "rdl/research/records/CML-PDRE-001-PHASE-2-5H/research-record.json"
BASELINE_SHA = "c690e2a890878056aecc057dc0afafbd3729164f"
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


class Phase25HFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load(SOURCE_PATH)
        cls.machine = load(MACHINE_PATH)
        cls.decisions = load(DECISIONS_PATH)
        cls.rescope = load(RESCOPE_PATH)
        cls.decomposition = load(DECOMPOSITION_PATH)
        cls.auth = load(AUTH_PATH)
        cls.record = load(RECORD_PATH)
        cls.decision_by_id = {row["candidate_id"]: row for row in cls.decisions["decisions"]}
        cls.machine_by_id = {row["candidate_id"]: row for row in cls.machine["allocation_cards"]}

    def test_a_baseline_and_candidate_set_are_preserved(self):
        self.assertEqual(subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), BASELINE_SHA)
        source_ids = [row["gap_id"] for row in self.source["candidates"]]
        self.assertEqual(len(source_ids), 6)
        self.assertEqual(set(source_ids), set(self.decision_by_id))

    def test_b_six_human_decisions_and_counts_are_exact(self):
        counts = self.decisions["counts"]
        self.assertEqual(len(self.decisions["decisions"]), 6)
        self.assertEqual(counts["human_decisions_recorded"], 6)
        self.assertEqual(
            {key: counts[key] for key in ("APPROVE_L1", "REQUEST_RESCOPING", "DEFER", "WATCH", "APPROVE_L2", "APPROVE_L3")},
            {"APPROVE_L1": 1, "REQUEST_RESCOPING": 2, "DEFER": 2, "WATCH": 1, "APPROVE_L2": 0, "APPROVE_L3": 0},
        )

    def test_c_machine_recommendations_are_not_overwritten(self):
        self.assertTrue(all(card["human_decision"] == "PENDING" for card in self.machine["allocation_cards"]))
        for candidate_id, decision in self.decision_by_id.items():
            self.assertEqual(decision["codex_recommendation"], self.machine_by_id[candidate_id]["codex_recommended_action"])

    def test_d_candidate_001_is_rescoped_without_authorization(self):
        decision = self.decision_by_id["L1-CANDIDATE-001"]
        self.assertEqual(decision["human_decision"], "REQUEST_RESCOPING")
        self.assertEqual(decision["authorization_state"], "NOT_AUTHORIZED")
        self.assertIsNone(decision["authorized_research_level"])
        self.assertEqual(self.rescope["qualification_dimension"], "ELECTRICAL")
        self.assertEqual(self.rescope["final_state"], "RESCOPED_PENDING_FUTURE_HUMAN_REVIEW")
        self.assertFalse(self.rescope["external_research_performed"])
        for field in ("question", "system_boundary", "decision_affected", "minimum_new_evidence", "acceptable_source_class", "stop_condition"):
            self.assertTrue(self.rescope[field])

    def test_e_candidate_002_has_exactly_one_future_l1_specification(self):
        decision = self.decision_by_id["L1-CANDIDATE-002"]
        self.assertEqual(decision["human_decision"], "APPROVE_L1")
        self.assertEqual(decision["authorized_research_level"], "L1_VERIFY")
        self.assertEqual([path.name for path in AUTH_DIR.glob("*.json")], [AUTH_PATH.name])
        self.assertEqual(self.auth["authorization_id"], "L1-CML-PDRE-001-FIELD-DEPLOYMENT-VERIFY")
        self.assertEqual(self.auth["research_scope"], "VERY_NARROW")
        self.assertEqual(self.auth["allowed_research_level"], "L1_VERIFY")
        self.assertEqual(self.auth["execution_status"], "NOT_STARTED")
        self.assertFalse(self.auth["external_research_performed_in_phase_2_5h"])

    def test_f_l1_stop_conditions_preserve_bounded_not_found_semantics(self):
        self.assertEqual(len(self.auth["stop_conditions"]), 3)
        exhausted = next(row for row in self.auth["stop_conditions"] if row["code"] == "BOUNDED_SEARCH_EXHAUSTED")
        self.assertEqual(exhausted["required_result"], "NOT_FOUND_WITHIN_BOUNDED_SEARCH")
        self.assertEqual(exhausted["prohibited_result"], "NO_DEPLOYMENT_EXISTS")
        self.assertTrue(any("management narrative" in row for row in self.auth["prohibited_future_actions"]))

    def test_g_candidates_003_004_and_006_match_human_decisions(self):
        self.assertEqual(self.decision_by_id["L1-CANDIDATE-003"]["human_decision"], "DEFER")
        self.assertEqual(self.decision_by_id["L1-CANDIDATE-004"]["human_decision"], "DEFER")
        self.assertEqual(self.decision_by_id["L1-CANDIDATE-006"]["human_decision"], "WATCH")
        for candidate_id in ("L1-CANDIDATE-003", "L1-CANDIDATE-004", "L1-CANDIDATE-006"):
            self.assertEqual(self.decision_by_id[candidate_id]["authorization_state"], "NOT_AUTHORIZED")

    def test_h_candidate_005_has_four_unanswered_decomposition_questions(self):
        decision = self.decision_by_id["L1-CANDIDATE-005"]
        self.assertEqual(decision["human_decision"], "REQUEST_RESCOPING")
        self.assertEqual(decision["authorization_state"], "NOT_AUTHORIZED")
        self.assertEqual([row["sub_question_id"] for row in self.decomposition["sub_questions"]], ["005-A", "005-B", "005-C", "005-D"])
        for row in self.decomposition["sub_questions"]:
            for field in ("question", "current_repository_evidence", "decision_affected", "minimum_missing_evidence"):
                self.assertTrue(row[field])
        self.assertEqual(self.decomposition["minimum_first_question"]["sub_question_id"], "005-A")
        self.assertEqual(self.decomposition["final_state"], "DECOMPOSED_PENDING_FUTURE_HUMAN_REVIEW")
        self.assertFalse(self.decomposition["external_research_performed"])

    def test_i_authorization_counts_are_one_zero_zero(self):
        counts = self.decisions["counts"]
        self.assertEqual(
            (counts["AUTHORIZED_L1_COUNT"], counts["AUTHORIZED_L2_COUNT"], counts["AUTHORIZED_L3_COUNT"]),
            (1, 0, 0),
        )
        authorized = [row for row in self.decisions["decisions"] if row["authorization_state"] == "AUTHORIZED_FOR_FUTURE_EXECUTION"]
        self.assertEqual([row["candidate_id"] for row in authorized], ["L1-CANDIDATE-002"])

    def test_j_phase_2_5h_remains_l0_without_external_research(self):
        payload = self.record["research_record"]
        self.assertEqual(payload["research_level"], "L0_REUSE")
        self.assertTrue(all(action["research_level"] == "L0_REUSE" for action in payload["research_actions"]))
        self.assertTrue(all(not action["external_research"] for action in payload["research_actions"]))
        self.assertFalse(self.decisions["external_research_performed"])
        self.assertEqual(payload["new_evidence_refs"], [])

    def test_k_original_and_human_decisions_remain_distinct(self):
        differing = [
            row for row in self.decisions["decisions"]
            if row["codex_recommendation"] != row["human_decision"]
        ]
        self.assertTrue(differing)
        self.assertIn("CODEX_RECOMMENDATION != HUMAN_DECISION", self.decisions["semantic_rules"])

    def test_l_rdl_record_validates_and_binds_authorization(self):
        result = validator.validate(self.record)
        self.assertEqual(result["research_level"], "L0_REUSE")
        self.assertEqual(result["stop_reason"], "PHASE_COMPLETE")
        self.assertEqual(result["new_evidence_count"], 0)
        authorization = self.record["research_record"]["authorization"]
        self.assertEqual(authorization["status"], "AUTHORIZED")
        self.assertEqual(authorization["authorization_ref"], "rdl/research/authorization/L1-CML-PDRE-001-FIELD-DEPLOYMENT-VERIFY.json")

    def test_m_rdl_record_hashes_bind_inputs_and_payload(self):
        bundle = {
            path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            for path in sorted(self.record["core"]["source_refs"])
        }
        self.assertEqual(self.record["core"]["input_hash"], digest(bundle))
        core = dict(self.record["core"])
        actual = core.pop("record_hash")
        self.assertEqual(actual, digest({"core": core, "payload": self.record["research_record"]}))

    def test_n_no_opaque_score_fields(self):
        prohibited = {"voi_score", "mev_score", "research_priority_score", "composite_score", "commercial_score"}
        for artifact in (self.decisions, self.rescope, self.decomposition, self.auth, self.record):
            self.assertFalse({key.lower() for key in keys(artifact)} & prohibited)

    def test_o_historical_cml_rtp_ecn_gdr_are_unchanged(self):
        changed = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD", "--", "technical-risk", "rtp", "ecn", "gdr", "evidence", "rdl/freshness"],
            cwd=ROOT,
            text=True,
        ).splitlines()
        self.assertEqual(changed, [])
        staged = subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).splitlines()
        self.assertEqual(staged, [])
        sys.path.insert(0, str(ROOT / "scripts"))
        import cml_v11_regression

        self.assertEqual(cml_v11_regression.historical_mutations(), [])


if __name__ == "__main__":
    unittest.main()
