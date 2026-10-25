#!/usr/bin/env python3
"""Phase B guards for the grounded 800VDC Source Dependency View."""

from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from collections import Counter
from pathlib import Path

from source_dependency_v01 import deterministic_metrics, validate_registry


ROOT = Path(__file__).resolve().parents[1]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class SourceDependencyViewPhaseBTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = load("protocol/source-dependency/registry-v0.1.json")
        cls.rules = load("protocol/source-dependency/qualification-rules-v0.2.json")
        cls.view = load("cases/800vdc/source-dependency-v0.1.json")
        cls.rows = cls.registry["rows"]

    def test_a_deterministic_build_is_clean(self):
        result = subprocess.run(
            ["python3", "-B", "scripts/build_source_dependency_view_phase_b.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SOURCE_DEPENDENCY_BUILD = PASS", result.stdout)

    def test_b_registry_is_valid_and_every_record_hash_is_unique(self):
        validate_registry(self.registry, self.rules)
        self.assertEqual(len(self.rows), 18)
        hashes = [row["record_hash"] for row in self.rows]
        self.assertEqual(len(hashes), len(set(hashes)))
        self.assertTrue(all(len(value) == 64 for value in hashes))

    def test_c_each_real_url_is_assessed_once_per_gap(self):
        expected_urls = {
            "https://www.chindatagroup.com/media/news/533.html",
            "https://press.siemens.com/global/en/pressrelease/siemens-and-reinhausen-develop-direct-current-power-solutions-ai-data-centers",
            "https://www.vertiv.com/en-us/about/news-and-events/events/2026/dcd-power-innovation-day-2026/",
            "https://solaredge.gcs-web.com/news-releases/news-release-details/solaredge-showcases-mvac-800-vdc-ai-factory-power-technology",
            "https://solaredge.gcs-web.com/node/15356/pdf",
            "https://www.businesswire.com/news/home/20261013444026/en/",
            "https://cn.sungrowpower.com/news/1749.html",
            "https://investors.power.com/news/news-details/2026/Power-Integrations-and-Ideal-Power-Collaborate-on-Efficient-Always-On-Solid-State-Circuit-Breakers-for-800-VDC-AI-Data-Centers/default.aspx",
            "https://vantage-dc.com/news/vantage-and-heron-power-electronics-announce-gigawatt-scale-800-vdc-agreement-to-accelerate-ai-infrastructure-delivery/",
        }
        for gap_id in ("OEG-CML-001", "OEG-CML-002"):
            rows = [row for row in self.rows if row["gap_id"] == gap_id]
            self.assertEqual({row["immutable_source"]["url"] for row in rows}, expected_urls)

    def test_d_evidence_levels_and_dependency_classes_are_grounded(self):
        rows = [row for row in self.rows if row["gap_id"] == "OEG-CML-001"]
        self.assertEqual(Counter(row["evidence_level"] for row in rows), Counter({"E2": 5, "E0": 2, "E4": 1, "E1": 1}))
        self.assertEqual(Counter(row["dependency_class"] for row in rows), Counter({"ISSUER_AUTHORED": 6, "DERIVED": 2, "PARTIALLY_DEPENDENT": 1}))
        self.assertNotIn("INDEPENDENT", {row["dependency_class"] for row in rows})
        self.assertNotIn("UNKNOWN", {row["dependency_class"] for row in rows})

    def test_e_chindata_e4_does_not_qualify_for_either_gap(self):
        rows = [row for row in self.rows if "CHINDATA-533" in row["source_row_id"]]
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row["evidence_level"] == "E4" for row in rows))
        self.assertTrue(all(row["dependency_class"] == "ISSUER_AUTHORED" for row in rows))
        self.assertTrue(all(row["qualification_status"] == "NOT_QUALIFIED" for row in rows))
        reasons = " ".join(row["qualification_reason"] for row in rows)
        self.assertIn("OBSERVATION_PERIOD", reasons)
        self.assertIn("ADDITIONAL_ENTITY_OR_SITE", reasons)

    def test_f_v02_closes_replication_self_count_without_rewriting_v01(self):
        old = ROOT / "protocol/source-dependency/qualification-rules-v0.1.json"
        self.assertEqual(hashlib.sha256(old.read_bytes()).hexdigest(), "46301ea80334b3c043e3ef2c9de493734c3c4f20520de10f575393d04c4270ec")
        replication = next(rule for rule in self.rules["rules"] if rule["gap_id"] == "OEG-CML-002")
        self.assertIn("ADDITIONAL_ENTITY_OR_SITE", replication["required_evidence_facets"])
        self.assertTrue(replication["qualification_rule_id"].endswith("v0.2"))

    def test_g_derived_copies_share_one_solaredge_lineage(self):
        for gap_id in ("OEG-CML-001", "OEG-CML-002"):
            rows = [row for row in self.rows if row["gap_id"] == gap_id]
            solar = [row for row in rows if row["originator_id"] == "ORIGINATOR-SOLAREDGE"]
            self.assertEqual(Counter(row["dependency_class"] for row in solar), Counter({"DERIVED": 2, "ISSUER_AUTHORED": 1}))
            registry = {"schema_version": self.registry["schema_version"], "rubric_version": self.registry["rubric_version"], "rows": rows}
            metrics = deterministic_metrics(registry, {"gap_id": gap_id})
            self.assertEqual(metrics["reviewed_urls"]["value"], 9)
            self.assertEqual(metrics["distinct_evidence_lineages"]["value"], 7)

    def test_h_zero_results_are_bounded_and_row_linked(self):
        self.assertIn("not proof", self.view["zero_interpretation"])
        for gap_id, metrics in self.view["metrics"].items():
            self.assertEqual(metrics["qualified_evidence_rows"]["value"], 0, gap_id)
            self.assertEqual(metrics["independent_originators"]["value"], 0, gap_id)
            self.assertEqual(metrics["reviewed_urls"]["value"], 9, gap_id)
            self.assertEqual(len(metrics["reviewed_urls"]["source_row_ids"]), 9)
            self.assertEqual(metrics["reviewed_urls"]["scope"]["evidence_cutoff"], "2026-10-22T14:02:00Z")

    def test_i_one_actual_reviewer_is_recorded_without_double_review_claim(self):
        self.assertEqual(self.view["review_policy"]["actual_reviewer_records"], 1)
        self.assertEqual(self.view["review_policy"]["second_review_status"], "PENDING_HUMAN_REVIEW")
        self.assertTrue(all(len(row["reviewers"]) == 1 for row in self.rows))
        self.assertTrue(all(row["reviewer_disagreement"]["detected"] is False for row in self.rows))

    def test_j_original_public_records_and_case_state_are_unchanged(self):
        baseline = load("docs/implementation/SE-DUAL-SITE-002-BASELINE-SHA256.json")
        for relative, expected in baseline["protected_paths"].items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, relative)
        self.assertFalse(self.view["case_state_changed"])
        self.assertEqual(self.view["case_state"], "HUMAN-REVIEWED SINGLE-INSTANCE EVIDENCE")
        self.assertEqual(self.view["case_state_as_of"], "2026-09-20T10:46:47Z")

    def test_k_source_packet_hashes_are_reproducible(self):
        report = load("docs/implementation/SE-DUAL-SITE-002-PHASE-B-HASHES.json")
        self.assertEqual(report["protected_originals_changed"], [])
        self.assertEqual(report["source_packet_hash_mismatches"], [])
        for relative, expected in report["source_packet_sha256"].items():
            self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), expected, relative)

    def test_l_root_docs_and_protocol_publication_mirrors_match(self):
        pairs = [
            ("cases/800vdc/index.html", "docs/cases/800vdc/index.html"),
            ("cases/800vdc/source-dependency/index.html", "docs/cases/800vdc/source-dependency/index.html"),
            ("cases/800vdc/source-dependency-v0.1.json", "docs/cases/800vdc/source-dependency-v0.1.json"),
            ("assets/source-dependency.css", "docs/assets/source-dependency.css"),
            ("protocol/source-dependency/registry-v0.1.json", "docs/protocol/source-dependency/registry-v0.1.json"),
            ("protocol/source-dependency/qualification-rules-v0.1.json", "docs/protocol/source-dependency/qualification-rules-v0.1.json"),
            ("protocol/source-dependency/qualification-rules-v0.2.json", "docs/protocol/source-dependency/qualification-rules-v0.2.json"),
            ("protocol/source-dependency/schema-v0.1.json", "docs/protocol/source-dependency/schema-v0.1.json"),
        ]
        for left, right in pairs:
            self.assertEqual((ROOT / left).read_bytes(), (ROOT / right).read_bytes(), left)

    def test_m_reader_view_is_accessible_responsive_and_auditable(self):
        page = (ROOT / "cases/800vdc/source-dependency/index.html").read_text(encoding="utf-8")
        css = (ROOT / "assets/source-dependency.css").read_text(encoding="utf-8")
        self.assertIn('id="source-dependency-view" aria-labelledby="source-dependency-title"', page)
        self.assertIn("Who is actually saying this?", page)
        self.assertIn("<caption>", page)
        self.assertEqual(page.count('scope="col"'), 4)
        self.assertEqual(page.count("<tbody>"), 1)
        self.assertGreaterEqual(page.count("<tr><td>"), 9)
        self.assertIn("@media(max-width:620px)", css)
        self.assertIn("overflow-wrap:anywhere", css)
        self.assertIn("/zh-cn/", page)
        self.assertIn("/es/", page)
        frozen_case = (ROOT / "cases/800vdc/index.html").read_text(encoding="utf-8")
        self.assertNotIn("SE-SOURCE-DEPENDENCY-VIEW:BEGIN", frozen_case)

    def test_n_challenge_routes_are_human_gated_and_no_state_write_is_exposed(self):
        page = (ROOT / "cases/800vdc/source-dependency/index.html").read_text(encoding="utf-8")
        for gap_id in ("OEG-CML-001", "OEG-CML-002"):
            route = self.view["challenge_routes"][gap_id]
            self.assertEqual(route["effect"], "HUMAN_REVIEW_REQUIRED; NO_AUTOMATIC_STATE_CHANGE")
            self.assertIn(f'/gaps/{gap_id}/', page)
        self.assertIn("cannot automatically change a claim or case state", page)

    def test_o_no_commercial_private_or_price_files_are_changed(self):
        changed = subprocess.check_output(
            ["git", "diff", "--name-only", "origin/main"], cwd=ROOT, text=True
        ).splitlines()
        forbidden = [path for path in changed if path.startswith("deploy/") or "price" in path.lower()]
        self.assertEqual(forbidden, [])

    def test_p_page_and_machine_records_reject_executable_markup(self):
        page = (ROOT / "cases/800vdc/source-dependency/index.html").read_text(encoding="utf-8").lower()
        self.assertNotIn("javascript:", page)
        self.assertNotIn("onerror=", page)
        serialized = json.dumps(self.registry).lower()
        self.assertNotIn("<script", serialized)
        self.assertNotIn("javascript:", serialized)


if __name__ == "__main__":
    unittest.main()
