"""Keep the frozen research audit distinct from active evidence trackers."""
import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SLUG = "ekn-necessity"
URL = f"https://structurevidence.org/cases/{SLUG}/"


class Surface(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


class FrozenResearchPublicationTest(unittest.TestCase):
    def test_frozen_machine_state_and_authorization(self):
        state = json.loads((ROOT / f"cases/{SLUG}/state-v1.0.json").read_text())
        expected = {
            "case_id": "SE-EKN-001", "project_id": "EKN-001",
            "record_type": "RESEARCH_DECISION_AUDIT", "version": "1.0",
            "as_of": "2026-10-18T09:05:06+08:00",
            "decision": "HOLD_NEEDS_EVIDENCE", "project_disposition": "FROZEN",
            "novelty_status": "NOT_ESTABLISHED", "evidence_gaps_reported": 11,
            "experiment_authorized": False, "g0c_executed": False,
            "g1_authorized": False, "paid_experiment_runs": 0,
            "independent_reproductions": 0, "outreach_sent": 0,
            "ekn_deployed": False, "human_gate_required": True,
            "frozen_ekn_v1_sha256": "21e0d5b95f36e4eec2622676a06684d97a355d6b03ef34654de675923bde886d",
        }
        properties = {key: {"const": value} for key, value in expected.items()}
        for key in ("paid_experiment_runs", "independent_reproductions", "outreach_sent", "evidence_gaps_reported"):
            properties[key]["type"] = "integer"
        schema = {"type": "object", "required": list(expected), "properties": properties}
        self.assertEqual(list(Draft202012Validator(schema).iter_errors(state)), [])

    def test_all_publication_mirrors_match(self):
        for file in ("index.html", "case.md", "state-v1.0.json"):
            self.assertEqual((ROOT / f"cases/{SLUG}/{file}").read_bytes(),
                             (ROOT / f"docs/cases/{SLUG}/{file}").read_bytes())
        for file in ("cases/index.html", "sitemap.xml"):
            self.assertEqual((ROOT / file).read_bytes(), (ROOT / "docs" / file).read_bytes())
        def files(directory):
            return {str(path.relative_to(directory)): path.read_bytes()
                    for path in directory.rglob("*")
                    if path.is_file() and "__pycache__" not in path.parts}
        self.assertEqual(files(ROOT / "cases"), files(ROOT / "docs/cases"))

    def test_complete_english_paper_and_versioned_citations(self):
        markdown = (ROOT / f"cases/{SLUG}/case.md").read_text()
        html = (ROOT / f"cases/{SLUG}/index.html").read_text()
        self.assertEqual(len(re.findall(r"^## \d+\.", markdown, re.M)), 10)
        self.assertIn("## Abstract", markdown)
        self.assertIn("n=26", markdown)
        for version in ("2511.06309v1", "2608.23691v1", "2606.10402v1",
                        "2606.10402v2", "2610.08927v1", "2609.33357v1"):
            self.assertIn(version, markdown)
            self.assertIn(version, html)
        for text in (markdown, html):
            self.assertNotIn("/workspace", text)
            self.assertNotIn("sediment://", text)
            self.assertIn("not a peer-reviewed", re.sub(r"<[^>]+>|\*", "", text))

    def test_canonical_navigation_and_local_link_targets(self):
        path = ROOT / f"cases/{SLUG}/index.html"
        surface = Surface(path.read_text())
        attrs = [a for _, a in surface.elements]
        ids = [a["id"] for a in attrs if "id" in a]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn(("html", {"lang": "en"}), surface.elements)
        self.assertEqual([a["href"] for tag, a in surface.elements
                          if tag == "link" and a.get("rel") == "canonical"], [URL])
        self.assertFalse(any("hreflang" in a for a in attrs))
        for a in attrs:
            for key in ("aria-controls", "aria-labelledby"):
                for target in a.get(key, "").split():
                    self.assertIn(target, ids)
            if "href" not in a:
                continue
            parsed = urlsplit(a["href"])
            if parsed.scheme or parsed.netloc:
                continue
            target = ROOT / unquote(parsed.path).lstrip("/") if parsed.path.startswith("/") else path.parent / unquote(parsed.path)
            if parsed.path.endswith("/"):
                target /= "index.html"
            if parsed.path:
                self.assertTrue(target.exists(), a["href"])
            elif parsed.fragment:
                self.assertIn(unquote(parsed.fragment), ids)

    def test_discovery_without_monitoring_registration(self):
        index = (ROOT / "cases/index.html").read_text()
        self.assertEqual(index.count(f'href="/cases/{SLUG}/"'), 1)
        self.assertIn("Frozen research decision audit", index)
        self.assertIn("Four evidence trackers", index)
        table = index.split('<table class="watch-table case-index">', 1)[1].split("</table>", 1)[0]
        self.assertNotIn("SE-EKN-001", table)
        self.assertEqual(table.count("data-case-id="), 4)
        for file in ("cases/review-status.json", "data/case-watch/monitoring-status.json"):
            self.assertNotIn("SE-EKN-001", (ROOT / file).read_text())
        tree = ET.fromstring((ROOT / "sitemap.xml").read_text())
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        matches = [e for e in tree.findall("s:url", ns) if e.findtext("s:loc", namespaces=ns) == URL]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].findtext("s:lastmod", namespaces=ns), "2026-10-18")


if __name__ == "__main__":
    unittest.main()
