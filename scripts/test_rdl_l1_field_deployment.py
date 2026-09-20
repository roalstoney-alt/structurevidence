#!/usr/bin/env python3
"""Targeted tests for the authorized CML-PDRE-001 field-deployment L1."""

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD_DIR = ROOT / "rdl/research/records/CML-PDRE-001-L1-FIELD-DEPLOYMENT-2026-09-20"
RECORD_PATH = RECORD_DIR / "research-record.json"
EVIDENCE_PATH = RECORD_DIR / "field-deployment-evidence.json"
CLASSIFICATION_PATH = RECORD_DIR / "source-classification.json"
AUTH_PATH = ROOT / "rdl/research/authorization/L1-CML-PDRE-001-FIELD-DEPLOYMENT-VERIFY.json"
ENTRY_SHA = "356e5baf38363af69ad22841523cae8e5f76734b"
sys.path.insert(0, str(ROOT / "rdl/research/validation"))
import validator  # noqa: E402


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class L1FieldDeploymentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = load(RECORD_PATH)
        cls.payload = cls.record["research_record"]
        cls.evidence = load(EVIDENCE_PATH)
        cls.classification = load(CLASSIFICATION_PATH)
        cls.authorization = load(AUTH_PATH)

    def test_a_entry_and_authorization(self):
        self.assertEqual(
            subprocess.run(["git", "merge-base", "--is-ancestor", ENTRY_SHA, "HEAD"], cwd=ROOT, check=False).returncode,
            0,
        )
        self.assertEqual(self.authorization["authorization_id"], "L1-CML-PDRE-001-FIELD-DEPLOYMENT-VERIFY")
        self.assertEqual(self.authorization["allowed_research_level"], "L1_VERIFY")
        self.assertEqual(self.authorization["authorized_l1_count_contribution"], 1)
        self.assertEqual(self.authorization["authorized_l2_count_contribution"], 0)
        self.assertEqual(self.authorization["authorized_l3_count_contribution"], 0)

    def test_b_one_question_and_budget(self):
        self.assertEqual(self.classification["research_question_count"], 1)
        self.assertLessEqual(self.classification["query_count"], 8)
        self.assertLessEqual(self.classification["deep_source_review_count"], 5)
        self.assertEqual(self.classification["query_count"], len(self.classification["queries"]))

    def test_c_exactly_one_primary_stop_outcome(self):
        self.assertEqual(self.classification["primary_result"], "QUALIFYING_FIELD_DEPLOYMENT_EVIDENCE_FOUND")
        self.assertEqual(self.classification["stop_reason"], "QUALIFYING_RECORD_FOUND")
        self.assertTrue(self.classification["search_stopped_immediately_after_qualifying_review"])

    def test_d_source_classification_counts(self):
        sources = self.classification["sources"]
        self.assertEqual(len(sources), self.classification["sources_checked"])
        self.assertEqual(sum(row["disposition"] == "USED" for row in sources), self.classification["sources_used"])
        self.assertEqual(sum(row["disposition"] == "REJECTED_FOR_L1_QUESTION" for row in sources), self.classification["sources_rejected"])
        self.assertEqual(self.classification["duplicate_sources"], 0)
        self.assertTrue(all(row["classification"] in {"QUALIFYING_EVIDENCE", "COUNTER_EVIDENCE", "NON_QUALIFYING_TECHNICAL_EVIDENCE", "DERIVATIVE_SOURCE", "DUPLICATE", "IRRELEVANT"} for row in sources))
        self.assertTrue(all(row["why_not_field_deployment"] for row in sources if row["disposition"] == "REJECTED_FOR_L1_QUESTION"))

    def test_e_qualifying_evidence_has_event_and_knowledge_time(self):
        core = self.evidence["core"]
        payload = self.evidence["evidence"]
        self.assertEqual(payload["classification"], "QUALIFYING_EVIDENCE")
        self.assertEqual(payload["qualifying_state"], "FIELD_OPERATION")
        self.assertNotEqual(payload["event_time"], payload["knowledge_time"])
        self.assertNotEqual(core["effective_at"], core["known_at"])
        self.assertIn("commercial operation", " ".join(payload["claim_summary"]).lower())

    def test_f_evidence_core_and_hashes(self):
        validator.schema_validate({"core": self.evidence["core"], "research_record": self.record["research_record"]})
        evidence_core = dict(self.evidence["core"])
        evidence_actual = evidence_core.pop("record_hash")
        self.assertEqual(evidence_actual, digest({"core": evidence_core, "evidence": self.evidence["evidence"]}))
        self.assertEqual(self.evidence["core"]["input_hash"], hashlib.sha256(self.evidence["evidence"]["url"].encode()).hexdigest())

    def test_g_rdl_record_validates_and_hashes(self):
        result = validator.validate(self.record)
        self.assertEqual(result["research_level"], "L1_VERIFY")
        self.assertEqual(result["stop_reason"], "EVIDENCE_SUFFICIENT")
        self.assertEqual(result["new_evidence_count"], 1)
        bundle = {
            path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            for path in sorted(self.record["core"]["source_refs"])
        }
        self.assertEqual(self.record["core"]["input_hash"], digest(bundle))
        core = dict(self.record["core"])
        actual = core.pop("record_hash")
        self.assertEqual(actual, digest({"core": core, "payload": self.payload}))

    def test_h_decision_changes_but_cml_readiness_does_not(self):
        self.assertEqual(self.payload["decision_before"], "R5_FIELD_DEPLOYED_NOT_ESTABLISHED")
        self.assertEqual(self.classification["primary_result"], "QUALIFYING_FIELD_DEPLOYMENT_EVIDENCE_FOUND")
        self.assertEqual(self.payload["decision_after"], "R5_ARCHITECTURE_FIELD_DEPLOYMENT_EVIDENCE_ACCEPTED_SINGLE_INSTANCE")
        self.assertTrue(self.payload["decision_changed"])
        self.assertIn("UNCHANGED_PENDING_HUMAN_CML_REVIEW", self.payload["readiness_after"])
        changed = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD", "--", "technical-risk/cml-v1.1/pdre/CML-PDRE-001"],
            cwd=ROOT,
            text=True,
        ).splitlines()
        self.assertEqual(changed, [])

    def test_i_no_l2_l3_or_phase3_activity(self):
        self.assertTrue(all(action["research_level"] == "L1_VERIFY" for action in self.payload["research_actions"]))
        serialized = json.dumps(self.record)
        self.assertNotIn("L2_INVESTIGATE", serialized)
        self.assertNotIn("L3_DEEP", serialized)
        self.assertNotIn("PHASE_3_STARTED", serialized)

    def test_j_unknown_cost_and_usage_are_not_zero(self):
        telemetry = self.payload["telemetry"]
        for field in ("model_calls", "tool_calls", "estimated_tokens", "observed_input_tokens", "observed_output_tokens", "observed_model_cost", "data_cost"):
            self.assertEqual(telemetry[field]["status"], "UNKNOWN")
            self.assertIsNone(telemetry[field]["value"])

    def test_k_historical_preservation(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import cml_v11_regression

        self.assertEqual(cml_v11_regression.historical_mutations(), [])


if __name__ == "__main__":
    unittest.main()
