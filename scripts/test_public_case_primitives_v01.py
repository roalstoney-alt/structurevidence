#!/usr/bin/env python3
"""Validate public-case primitive completion without research-state mutation."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
BASELINE = "8d4b028d3d0e113290ed5309e868fe300b5b9efd"
BRAND_BASELINE = "4ed39b2389ad40f4f4dcb902c3436aff4c5ba352"
BRAND_ONLY_SURFACES = {
    "cases/nsq-nsclc-china/index.html",
    "docs/cases/nsq-nsclc-china/index.html",
}
PAIRS = [
    ("cases/800vdc/state-v0.1.json", "docs/cases/800vdc/state-v0.1.json"),
    (
        "cases/sodium-ion-bess/publication-control-v0.1.json",
        "docs/cases/sodium-ion-bess/publication-control-v0.1.json",
    ),
    (
        "cases/nsq-nsclc-china/publication-control-v0.1.json",
        "docs/cases/nsq-nsclc-china/publication-control-v0.1.json",
    ),
    (
        "cases/nsq-nsclc-china/decision-memory-v0.1.json",
        "docs/cases/nsq-nsclc-china/decision-memory-v0.1.json",
    ),
]
PROTECTED = [
    "cases/800vdc/stop-v0.1.html",
    "docs/cases/800vdc/stop-v0.1.html",
    "cases/sodium-ion-bess/state-v0.1.json",
    "cases/sodium-ion-bess/stop-v0.1.html",
    "cases/sodium-ion-bess/decision-memory-v0.1.json",
    "docs/cases/sodium-ion-bess/state-v0.1.json",
    "docs/cases/sodium-ion-bess/stop-v0.1.html",
    "docs/cases/sodium-ion-bess/decision-memory-v0.1.json",
    "cases/nsq-nsclc-china/index.html",
    "cases/nsq-nsclc-china/state-v0.1.json",
    "cases/nsq-nsclc-china/stop-v0.1.html",
    "docs/cases/nsq-nsclc-china/index.html",
    "docs/cases/nsq-nsclc-china/state-v0.1.json",
    "docs/cases/nsq-nsclc-china/stop-v0.1.html",
    "technical-risk/cml-v1.1/pdre/CML-PDRE-001",
    "rdl/research/records/CML-PDRE-001-L1-FIELD-DEPLOYMENT-2026-09-20",
    "data/case-watch/weekly/2026-W40.json",
    "docs/case-watch/daily/2026-09-29.md",
    "docs/case-watch/weekly/2026-W40.md",
    "publication/weekly/2026-W40-publication-manifest.json",
]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def git_blob(revision: str, relative: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{revision}:{relative}"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout


def apply_brand_normalization(content: bytes) -> bytes:
    return content.replace(b"StructureEvidence", b"StructEvidence")


class PublicCasePrimitiveTest(unittest.TestCase):
    def test_a_required_primitives_exist(self):
        for root_file, docs_file in PAIRS:
            self.assertTrue((ROOT / root_file).is_file(), root_file)
            self.assertTrue((ROOT / docs_file).is_file(), docs_file)

    def test_b_root_docs_parity(self):
        for root_file, docs_file in PAIRS:
            self.assertEqual((ROOT / root_file).read_bytes(), (ROOT / docs_file).read_bytes())

    def test_c_historical_immutability_and_no_research_mutation(self):
        result = subprocess.run(
            ["git", "diff", "--name-only", BASELINE, "--", *PROTECTED],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        changed = {line for line in result.stdout.splitlines() if line}
        self.assertEqual(changed - BRAND_ONLY_SURFACES, set())
        for relative in changed:
            historical = git_blob(BRAND_BASELINE, relative)
            self.assertEqual(
                (ROOT / relative).read_bytes(),
                apply_brand_normalization(historical),
                relative,
            )

    def test_d_cml_state_is_derived_without_state_change(self):
        state = load("cases/800vdc/state-v0.1.json")
        stop = (ROOT / "cases/800vdc/stop-v0.1.html").read_text(encoding="utf-8")
        self.assertEqual(state["current_bounded_state"], "HUMAN-REVIEWED SINGLE-INSTANCE EVIDENCE")
        self.assertIn(state["current_bounded_state"], stop)
        self.assertFalse(state["pdre_full_validation"])
        self.assertTrue(state["single_deployment_not_industry_adoption"])
        self.assertFalse(state["historical_research_mutation"])
        self.assertFalse(state["research_state_mutation"])
        self.assertTrue(state["derived_from_existing_records_only"])

    def test_e_publication_semantics_are_separate_from_research_state(self):
        for relative in [
            "cases/sodium-ion-bess/publication-control-v0.1.json",
            "cases/nsq-nsclc-china/publication-control-v0.1.json",
        ]:
            control = load(relative)
            self.assertEqual(control["publication_status"], "PUBLICATION_APPROVED")
            self.assertEqual(control["public_projection_status"], "PUBLIC_PROJECTION_ACTIVE")
            self.assertFalse(control["historical_research_mutation"])
            self.assertFalse(control["research_state_mutation"])
            self.assertTrue(control["derived_from_existing_records_only"])
            self.assertEqual(control["human_authority"], "NOT_RECORDED")
            self.assertEqual(control["decision_date"], "NOT_RECORDED")

    def test_f_nsclc_decision_memory_uses_existing_schema_and_hashes(self):
        schema = load("evidence/decision-memory/schema/decision-memory-record.schema.json")
        schema["properties"]["core"] = load("evidence/core/schema/evidence_core_record.schema.json")
        record = load("cases/nsq-nsclc-china/decision-memory-v0.1.json")
        errors = sorted(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record),
            key=lambda error: list(error.path),
        )
        self.assertEqual(errors, [], "; ".join(error.message for error in errors))

        source_paths = [
            ROOT / "cases/nsq-nsclc-china/state-v0.1.json",
            ROOT / "cases/nsq-nsclc-china/stop-v0.1.html",
        ]
        historical_index = git_blob(BRAND_BASELINE, "cases/nsq-nsclc-china/index.html")
        self.assertEqual(
            (ROOT / "cases/nsq-nsclc-china/index.html").read_bytes(),
            apply_brand_normalization(historical_index),
        )
        input_digest = hashlib.sha256()
        for path in source_paths:
            input_digest.update(path.read_bytes())
        input_digest.update(historical_index)
        self.assertEqual(record["core"]["input_hash"], input_digest.hexdigest())

        core = dict(record["core"])
        actual = core.pop("record_hash")
        canonical = json.dumps(
            {"core": core, "payload": record["decision_memory"]},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode()
        self.assertEqual(actual, hashlib.sha256(canonical).hexdigest())

    def test_g_medical_boundary(self):
        record = load("cases/nsq-nsclc-china/decision-memory-v0.1.json")["decision_memory"]
        states = {state["state_id"]: state["status"] for state in record["evidence_states"]}
        self.assertEqual(states["patient_specific_probability"], "NOT_ESTABLISHED")
        self.assertEqual(states["cross_modality_ranking"], "NOT_ESTABLISHED")
        self.assertEqual(states["hospital_aggregate_outcome_data"], "NOT_ESTABLISHED")
        excluded = " ".join(record["scope"]["excluded"]).lower()
        self.assertIn("patient-specific treatment recommendations", excluded)
        self.assertIn("personal success probabilities", excluded)
        self.assertIn("cross-stage or cross-modality ranking", excluded)
        self.assertEqual(record["decision_state"]["status"], "CONTEXT_REQUIRED")

    def test_h_no_new_external_source_urls(self):
        new_text = "\n".join((ROOT / root_file).read_text(encoding="utf-8") for root_file, _ in PAIRS)
        new_urls = set(re.findall(r"https://[^\"\\s]+", new_text))
        source_text = "\n".join(
            (ROOT / relative).read_text(encoding="utf-8")
            for relative in [
                "cases/800vdc/index.html",
                "cases/800vdc/stop-v0.1.html",
                "cases/sodium-ion-bess/index.html",
                "cases/nsq-nsclc-china/index.html",
                "sitemap.xml",
            ]
        )
        self.assertTrue(all(url in source_text for url in new_urls), new_urls)

    def test_i_case_watch_compatibility(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_case_watch.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        manifest = load("publication/weekly/2026-W40-publication-manifest.json")
        self.assertTrue(all(case["publication_approved"] is False for case in manifest["cases"]))
        self.assertTrue(all(case["decision"] == "NO_STATE_CHANGE" for case in manifest["cases"]))


if __name__ == "__main__":
    unittest.main()
