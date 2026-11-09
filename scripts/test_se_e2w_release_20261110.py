#!/usr/bin/env python3
"""Release guards for SE-E2W-RELEASE-20261110."""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVENT = "cases/800vdc/events/envision-galaxy-800vdc-2026"
RECORD = ROOT / "rdl/research/records/CML-PDRE-001-ENVISION-2026-11-10"


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EvidenceWebsiteReleaseTests(unittest.TestCase):
    def test_root_docs_projection_parity(self):
        for relative in (
            "cases/index.html",
            "cases/review-status.json",
            "cases/800vdc/index.html",
            "cases/800vdc/index.json",
            "cases/800vdc/events/index.json",
            f"{EVENT}/index.html",
            f"{EVENT}/index.json",
            "sitemap.xml",
            "execution/SE_E2W_PRODUCTION_BASELINE_20261110.json",
            "execution/SE_EVIDENCE_WEBSITE_PUBLICATION_AUDIT_20261110.md",
        ):
            self.assertEqual((ROOT / relative).read_bytes(), (ROOT / "docs" / relative).read_bytes(), relative)

    def test_event_identity_and_boundary(self):
        event = load(f"{EVENT}/index.json")
        self.assertEqual(event["case_id"], "CML-PDRE-001")
        self.assertEqual(event["event_id"], "CML-PDRE-001-EV-ENVISION-20261108-001")
        self.assertEqual(event["claim_ref"], "ENVISION_GALAXY_800VDC_LIVE_DEPLOYMENT")
        self.assertEqual(event["claim_status"], "OPERATOR_REPORTED_LIVE_DEPLOYMENT")
        self.assertEqual(event["source_role"], "OPERATOR_AUTHORED")
        self.assertTrue(event["case_index_visible"])
        self.assertFalse(event["state_changed"])
        self.assertFalse(event["historical_transition"]["canonical_readiness_changed"])
        self.assertFalse(event["historical_transition"]["public_state_mutated"])
        self.assertTrue(all(value == "UNKNOWN" for value in event["unknowns"].values()))

    def test_projection_matches_merged_evidence_record(self):
        public = load(f"{EVENT}/index.json")
        evidence = json.loads((RECORD / "evidence-event.json").read_text(encoding="utf-8"))
        claim = json.loads((RECORD / "claim-ledger.jsonl").read_text(encoding="utf-8"))
        transition = json.loads((RECORD / "state-transition.jsonl").read_text(encoding="utf-8"))
        self.assertEqual(public["event_id"], evidence["event_id"])
        self.assertEqual(public["claim"], claim["proposition"])
        self.assertEqual(public["claim_ref"], claim["claim_id"])
        self.assertEqual(public["historical_transition"]["previous_recorded_state"], transition["previous_recorded_state"])
        self.assertEqual(public["historical_transition"]["new_evidence_state"], transition["new_evidence_state"])

    def test_capture_hashes_match_merged_snapshots(self):
        public = load(f"{EVENT}/index.json")
        by_id = {row["source_id"]: row for row in public["source_refs"]}
        expected = {
            "CML-PDRE-001-SRC-ENVISION-PRN-20261102": RECORD / "sources/envision-prnewswire-20261102.snapshot.json",
            "CML-PDRE-001-SRC-ENVISION-ESN-20261104": RECORD / "sources/envision-energy-storage-news-20261104.snapshot.json",
        }
        for source_id, path in expected.items():
            self.assertEqual(by_id[source_id]["capture_sha256"], sha256(path))

    def test_event_ledger_append_and_frozen_case_projection(self):
        expected_ledger = {
            "SE-EVENT-CML-PDRE-001-20261013-SOLAREDGE-OCP",
            "SE-EVENT-CML-PDRE-001-20261015-SUNGROW-CERTIFICATION",
            "SE-EVENT-CML-PDRE-001-20261021-VANTAGE-HERON",
            "CML-PDRE-001-EV-ENVISION-20261108-001",
        }
        ledger = load("cases/800vdc/events/index.json")
        ledger_ids = [row["event_id"] for row in ledger["events"]]
        self.assertEqual(len(ledger_ids), len(set(ledger_ids)))
        self.assertEqual(set(ledger_ids), expected_ledger)

        frozen = load("cases/800vdc/index.json")
        self.assertEqual(
            [row["event_id"] for row in frozen["events"]],
            [
                "SE-EVENT-CML-PDRE-001-20261013-SOLAREDGE-OCP",
                "SE-EVENT-CML-PDRE-001-20261015-SUNGROW-CERTIFICATION",
            ],
        )
        self.assertEqual(
            sha256(ROOT / "cases/800vdc/index.html"),
            "06c69bfdbca2ccb5bce25c487319d04ecd5067eea7ff54d2c9228f5f42222cfa",
        )
        self.assertEqual(
            sha256(ROOT / "cases/800vdc/index.json"),
            "2459f070ae48f6bb44904e22eb1f1a6b06750e29f29ef501267f820f6d3f7bdc",
        )

    def test_html_discloses_required_fields(self):
        text = (ROOT / EVENT / "index.html").read_text(encoding="utf-8")
        for required in (
            "CML-PDRE-001",
            "Galaxy AI Data Center",
            "Ulanqab",
            "10kV AC → SST → 800VDC",
            "OPERATOR_REPORTED_LIVE_DEPLOYMENT",
            "CML-PDRE-001-EV-ENVISION-20261108-001",
            "ENVISION_GALAXY_800VDC_LIVE_DEPLOYMENT",
            "Independent acceptance",
            "Actual commissioned IT MW",
            "Planned capacity boundary",
            "Complete GitHub evidence record",
        ):
            self.assertIn(required, text)

    def test_sitemap_and_audit_receipts(self):
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        self.assertIn("/cases/800vdc/events/envision-galaxy-800vdc-2026/", sitemap)
        self.assertIn("/cases/800vdc/events/envision-galaxy-800vdc-2026/index.json", sitemap)
        case_index = (ROOT / "cases/index.html").read_text(encoding="utf-8")
        self.assertIn("/cases/800vdc/events/envision-galaxy-800vdc-2026/", case_index)
        self.assertIn("canonical state unchanged", case_index)
        audit = (ROOT / "execution/SE_EVIDENCE_WEBSITE_PUBLICATION_AUDIT_20261110.md").read_text(encoding="utf-8")
        self.assertIn("Merged PRs audited: **57**", audit)
        self.assertIn("`RDL-DOD-BEAM-001`", audit)
        self.assertIn("`INCOMPLETE_CHAIN`", audit)


if __name__ == "__main__":
    unittest.main()
