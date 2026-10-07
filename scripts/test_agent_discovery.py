#!/usr/bin/env python3
"""Validate Agent Discovery Layer v0.1 boundaries A-W."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
# Authoritative main at the start of the Irkutsk publication branch.
ENTRY_SHA = "73af88f2ca7f28214a3030a1d7188c868a386c53"
CASES = {
    "CML-PDRE-001": "800vdc",
    "SE-BESS-SODIUM-001": "sodium-ion-bess",
    "SE-ONC-NSQNSCLC-CN-001": "nsq-nsclc-china",
}
PRIMITIVES = [
    "cases/800vdc/index.html",
    "cases/800vdc/state-v0.1.json",
    "cases/800vdc/stop-v0.1.html",
    "technical-risk/cml-v1.1/pdre/CML-PDRE-001/publication-control.json",
    "cases/sodium-ion-bess/index.html",
    "cases/sodium-ion-bess/state-v0.1.json",
    "cases/sodium-ion-bess/stop-v0.1.html",
    "cases/sodium-ion-bess/publication-control-v0.1.json",
    "cases/sodium-ion-bess/decision-memory-v0.1.json",
    "cases/nsq-nsclc-china/index.html",
    "cases/nsq-nsclc-china/state-v0.1.json",
    "cases/nsq-nsclc-china/stop-v0.1.html",
    "cases/nsq-nsclc-china/publication-control-v0.1.json",
    "cases/nsq-nsclc-china/decision-memory-v0.1.json",
]
PROTECTED_EXISTING_CASES = [
    "cases/800vdc",
    "cases/sodium-ion-bess",
    "cases/nsq-nsclc-china",
    "docs/cases/800vdc",
    "docs/cases/sodium-ion-bess",
    "docs/cases/nsq-nsclc-china",
    "technical-risk/cml-v1.1",
    "rdl",
    "data/case-watch/backfill",
    "data/case-watch/weekly",
    "docs/case-watch/daily",
    "docs/case-watch/weekly",
    "publication/weekly",
]
STATIC = [
    ".well-known/structurevidence.json",
    "method-contract.json",
    "claims/index.json",
    "changes.json",
    "agent/index.html",
]
REQUIRED_FIELDS = {
    "claim_id", "case_id", "version", "statement", "state", "as_of", "scope",
    "supports", "does_not_support", "unknowns", "counter_evidence", "next_observable",
    "provenance", "canonical_url", "state_url", "stop_point_url", "method_contract",
    "citation_requirements",
}


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def load_builder():
    spec = importlib.util.spec_from_file_location("build_agent_discovery", ROOT / "scripts/build_agent_discovery.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class AgentDiscoveryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = load("agent-discovery/claim-registry-v0.1.json")
        cls.claims = {
            item["claim_id"]: load(f"claims/{item['claim_id']}.json")
            for item in cls.registry["claims"]
        }

    def test_a_primitive_baseline_completeness(self):
        self.assertTrue(all((ROOT / path).is_file() for path in PRIMITIVES))

    def test_b_discovery_manifest_existence(self):
        manifest = load(".well-known/structurevidence.json")
        self.assertEqual(manifest["type"], "temporal_evidence_resolution_layer")
        self.assertEqual(set(manifest["public_cases"]), set(CASES))
        self.assertEqual(manifest["resolve_endpoint"], "https://api.structurevidence.org/resolve")

    def test_c_method_contract_validation(self):
        contract = load("method-contract.json")
        ids = {item["id"] for item in contract["principles"]}
        self.assertIn("UNKNOWN_MUST_NOT_BE_INFERRED", ids)
        self.assertIn("DOES_NOT_SUPPORT", "_".join(contract["required_claim_fields"]).upper())

    def test_d_claim_id_uniqueness(self):
        ids = [item["claim_id"] for item in self.registry["claims"]]
        self.assertEqual(len(ids), 26)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(Counter(item["case_id"] for item in self.registry["claims"]), {
            "CML-PDRE-001": 9,
            "SE-BESS-SODIUM-001": 9,
            "SE-ONC-NSQNSCLC-CN-001": 8,
        })

    def test_e_claim_source_traceability(self):
        roles = {"PRIMARY_PUBLIC_EVIDENCE_STATE", "PUBLICATION_AUTHORITY", "HUMAN_CITATION_BOUNDARY"}
        for claim in self.claims.values():
            self.assertTrue(REQUIRED_FIELDS.issubset(claim), claim["claim_id"])
            self.assertTrue(roles.issubset({item["source_role"] for item in claim["provenance"]}))
            for item in claim["provenance"]:
                self.assertTrue((ROOT / item["source_ref"]).is_file(), item["source_ref"])

    def test_f_claim_projection_determinism(self):
        builder = load_builder()
        for relative, expected in builder.build_outputs().items():
            self.assertEqual((ROOT / relative).read_bytes(), expected, relative)

    def test_g_primitive_consistency(self):
        builder = load_builder()
        bundles = {case_id: builder.source_bundle(case_id) for case_id in CASES}
        builder.validate_primitives(self.registry, bundles)

    def test_h_exact_state_preservation(self):
        cml = load("cases/800vdc/state-v0.1.json")
        sodium = load("cases/sodium-ion-bess/state-v0.1.json")
        nsclc = load("cases/nsq-nsclc-china/state-v0.1.json")
        nsclc_claims = {item["claim_id"]: item["status"] for item in nsclc["claims"]}
        dm = load("cases/nsq-nsclc-china/decision-memory-v0.1.json")["decision_memory"]
        dm_states = {item["state_id"]: item["status"] for item in dm["evidence_states"]}
        for row in self.registry["claims"]:
            if row["case_id"] == "CML-PDRE-001":
                expected = cml["states"][row["source_key"]]
            elif row["case_id"] == "SE-BESS-SODIUM-001":
                expected = sodium["current_state"][row["source_key"]]
            elif row["source_kind"] == "nsclc_claim":
                expected = nsclc_claims[row["source_key"]]
            else:
                expected = dm_states[row["source_key"]]
            self.assertEqual(self.claims[row["claim_id"]]["state"], expected, row["claim_id"])

    def test_i_does_not_support_presence(self):
        for claim in self.claims.values():
            self.assertTrue(claim["does_not_support"], claim["claim_id"])

    def test_j_as_of_presence(self):
        for claim in self.claims.values():
            source = load(f"cases/{CASES[claim['case_id']]}/state-v0.1.json")
            self.assertEqual(claim["as_of"], source["knowledge_cutoff"])

    def test_k_no_unsupported_inference_or_external_research(self):
        self.assertNotIn("http://", (ROOT / "agent-discovery/claim-registry-v0.1.json").read_text())
        for claim in self.claims.values():
            self.assertEqual(claim["counter_evidence"], [])
            self.assertTrue(all(item["source_ref"].startswith(("cases/", "technical-risk/")) for item in claim["provenance"]))

    def test_l_root_docs_parity(self):
        paths = STATIC + [f"claims/{claim_id}.json" for claim_id in self.claims]
        for relative in paths:
            self.assertEqual((ROOT / relative).read_bytes(), (ROOT / "docs" / relative).read_bytes(), relative)

    def test_m_p_resolver_contract_is_read_only_and_bounded(self):
        text = (ROOT / "deploy/cloudflare-evidence-resolver/worker.js").read_text(encoding="utf-8")
        self.assertIn("MATCHED", text)
        self.assertIn("NO_MATCH", text)
        self.assertIn("UNRESOLVED", text)
        self.assertIn("BOUNDED_SUPPORT", text)
        self.assertNotIn("fetch(\"http", text)
        self.assertNotIn("env.DB", text)
        self.assertNotIn("AUTHORIZED", text)

    def test_q_capabilities_human_authorization_boundary(self):
        text = (ROOT / "deploy/cloudflare-landing/capabilities.js").read_text(encoding="utf-8")
        payload = json.loads(text.split(" = ", 1)[1].rsplit(";", 1)[0])
        self.assertEqual([item["service_id"] for item in payload["services"]], ["VERIFY_CLAIM", "CUSTOMER_CONTEXT", "DECISION_PACK"])
        self.assertTrue(all(item["human_authorization_required"] is True for item in payload["services"]))
        self.assertTrue(all(item["automatic_research_authorization"] is False for item in payload["services"]))

    def test_r_no_customer_or_admin_exposure(self):
        content = (ROOT / "deploy/cloudflare-landing/capabilities.js").read_text(encoding="utf-8").lower()
        self.assertNotIn("/admin", content)
        self.assertNotIn("customer_data", content)
        self.assertNotIn("d1", content)

    def test_s_medical_boundary(self):
        medical = self.claims["SE-ONC-NSQNSCLC-CN-001.PATIENT_SPECIFIC_SUCCESS_PROBABILITY"]
        self.assertEqual(medical["state"], "NOT_ESTABLISHED")
        resolver = (ROOT / "deploy/cloudflare-evidence-resolver/worker.js").read_text(encoding="utf-8")
        self.assertIn("This public evidence object does not provide patient-specific medical advice.", resolver)

    def test_t_u_v_existing_histories_and_snapshots_are_immutable(self):
        result = subprocess.run(
            ["git", "diff", "--exit-code", ENTRY_SHA, "--", *PROTECTED_EXISTING_CASES],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_w_daily_weekly_case_watch_compatibility(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_case_watch.py")],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
