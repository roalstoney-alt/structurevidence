import hashlib
import json
import re
import unittest
from pathlib import Path
from xml.etree import ElementTree

from scripts.se_unified_ops import build_event_x_candidate, validate_event_record, validate_review


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "data/ops/se/reconciliations/pr26-sungrow-20261018-01.json"
EVENT = "cases/800vdc/events/sungrow-enerneo-certification-2026"
AUTHORIZED_COMMERCIAL_EVOLUTION = {
    "deploy/cloudflare-landing/README.md",
    "deploy/cloudflare-landing/commercial-upgrade.js",
    "deploy/cloudflare-landing/test/commercial-upgrade.test.js",
    "deploy/cloudflare-landing/test/intake.test.js",
    "deploy/cloudflare-landing/worker.js",
    "deploy/cloudflare-landing/wrangler.jsonc",
}


def load(path):
    return json.loads((ROOT / path).read_text())


class PR26AppendOnlyTest(unittest.TestCase):
    def test_existing_projection_entries_are_unchanged(self):
        baseline = load(MANIFEST)["projection_baseline"]
        for path in ("cases/800vdc/events/index.json", "cases/800vdc/index.json"):
            before = baseline[path]["value"]
            after = load(path)
            self.assertEqual(after["events"][:-1], before["events"])
            self.assertEqual({k: v for k, v in after.items() if k != "events"},
                             {k: v for k, v in before.items() if k != "events"})
        page = (ROOT / "cases/index.html").read_text()
        page = re.sub(r'<section class="product-section" aria-labelledby="sungrow-supplement-title">.*?</section>\n', "", page)
        self.assertEqual(hashlib.sha256(page.encode()).hexdigest(), baseline["cases/index.html"]["sha256"])
        sitemap = (ROOT / "sitemap.xml").read_text()
        sitemap = re.sub(r'<url><loc>https://structurevidence.org/' + EVENT + r'/[^<]*</loc><lastmod>2026-10-18</lastmod></url>\n', "", sitemap)
        self.assertEqual(hashlib.sha256(sitemap.encode()).hexdigest(), baseline["sitemap.xml"]["sha256"])

    def test_all_protected_baseline_bytes_are_preserved(self):
        manifest = load(MANIFEST)
        self.assertEqual(manifest["baseline_main_sha"], "5a3bd2883af40969c5ca63c0581d15afdc7b30b4")
        self.assertEqual(manifest["source_commit_sha"], "0c8b940c3a3a6079e6260ddde89f2af5ca354d93")
        for path, expected in manifest["protected_sha256"].items():
            # Phase D and SE-IREN-INTAKE-HARDENING-001 deliberately evolve only
            # the commercial front office. Dedicated guards freeze prices, D1
            # privacy/defaults, and every .org evidence record.
            if path in AUTHORIZED_COMMERCIAL_EVOLUTION:
                continue
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), expected)

    def test_supplement_is_distinct_and_links_both_original_records(self):
        manifest = load(MANIFEST)
        supplement = load(manifest["review_path"])
        original = load(supplement["existing_daily_review"]["path"])
        self.assertNotEqual(supplement["review_id"], original["review_id"])
        self.assertEqual(supplement["review_id"], manifest["supplemental_review_id"])
        self.assertEqual(supplement["original_record"], manifest["original_record"])
        self.assertTrue(supplement["not_a_new_source_review"])
        self.assertEqual(supplement, load("data/case-watch/reviews/2026-10-17/CML-PDRE-001-SUPP-PR26-01.json"))
        validate_review(supplement)
        self.assertEqual(original["reviewed_at"], "2026-10-17T14:02:37Z")

    def test_source_clocks_hashes_and_evidence_limits(self):
        event = load(EVENT + "/index.json")
        validate_event_record(event)
        source = load(EVENT + "/source-v1.json")
        snapshot = load(EVENT + "/snapshot-v1.json")
        self.assertEqual(event["published_at"], "2026-10-15")
        self.assertEqual(event["retrieved_at"], "2026-10-17T14:04:05Z")
        self.assertEqual(source["first_observed_at"], event["retrieved_at"])
        self.assertEqual(snapshot["captured_at"], event["retrieved_at"])
        digest = hashlib.sha256((ROOT / event["snapshot_path"]).read_bytes()).hexdigest()
        self.assertEqual(digest, event["snapshot_sha256"])
        self.assertEqual(digest, source["snapshot_sha256"])
        self.assertEqual(digest, "574c58de9d696546fed3f268b9fa02786e4a50ffe4e04616ddd0e06fdaf69f2a")
        self.assertFalse(snapshot["raw_file_saved"])
        self.assertEqual(source["independent_issuer_verification"], "NOT_ESTABLISHED")
        self.assertFalse(event["state_changed"])
        self.assertEqual(event["old_stop"], event["candidate_stop"])
        self.assertNotIn("NEW_EVENT", event["classifications"])
        blocked = build_event_x_candidate("2026-10-17", event, None)
        self.assertEqual(blocked["approval_gate"], "BLOCKED")
        self.assertEqual(blocked["x_post_sent"], 0)

    def test_existing_event_remains_first_and_new_event_is_unique(self):
        event = load(EVENT + "/index.json")
        ledger = load("cases/800vdc/events/index.json")
        self.assertEqual(len(ledger["events"]), 2)
        self.assertEqual(ledger["events"][0]["event_id"], "SE-EVENT-CML-PDRE-001-20261013-SOLAREDGE-OCP")
        self.assertEqual(ledger["events"][1]["event_id"], event["event_id"])
        self.assertEqual(len({x["event_id"] for x in ledger["events"]}), 2)
        self.assertEqual(load("cases/800vdc/index.json")["events"], ledger["events"])
        state = load("cases/800vdc/index.json")
        self.assertEqual(state["current_state"], "HUMAN-REVIEWED SINGLE-INSTANCE EVIDENCE")
        self.assertEqual(state["as_of"], "2026-09-20T10:46:47Z")

    def test_mirrors_and_sitemap_are_consistent(self):
        files = {x.relative_to(ROOT / "cases") for x in (ROOT / "cases").rglob("*") if x.is_file()}
        mirrors = {x.relative_to(ROOT / "docs/cases") for x in (ROOT / "docs/cases").rglob("*") if x.is_file()}
        self.assertEqual(files, mirrors)
        for path in files:
            self.assertEqual((ROOT / "cases" / path).read_bytes(), (ROOT / "docs/cases" / path).read_bytes())
        self.assertEqual((ROOT / "sitemap.xml").read_bytes(), (ROOT / "docs/sitemap.xml").read_bytes())
        urls = [x.text for x in ElementTree.parse(ROOT / "sitemap.xml").findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        self.assertEqual(len(urls), len(set(urls)))
        self.assertEqual(urls.count("https://structurevidence.org/" + EVENT + "/"), 1)


if __name__ == "__main__":
    unittest.main()
