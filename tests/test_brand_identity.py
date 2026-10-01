from __future__ import annotations

import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEGACY_CAMEL = "Structure" + "Evidence"
LEGACY_SPACED = "Structure" + " " + "Evidence"
PUBLIC_PAGES = [
    "index.html",
    "en/index.html",
    "zh-cn/index.html",
    "es/index.html",
    "about.html",
    "method.html",
    "cases/index.html",
    "cases/800vdc/index.html",
    "cases/sodium-ion-bess/index.html",
    "changes/index.html",
]
CANONICALS = {
    "index.html": "https://structurevidence.org/",
    "en/index.html": "https://structurevidence.org/en/",
    "zh-cn/index.html": "https://structurevidence.org/zh-cn/",
    "es/index.html": "https://structurevidence.org/es/",
    "about.html": "https://structurevidence.org/about.html",
    "method.html": "https://structurevidence.org/method.html",
    "cases/index.html": "https://structurevidence.org/cases/",
    "cases/800vdc/index.html": "https://structurevidence.org/cases/800vdc/",
    "cases/sodium-ion-bess/index.html": "https://structurevidence.org/cases/sodium-ion-bess/",
    "changes/index.html": "https://structurevidence.org/changes/",
}
IMMUTABLE_HTML = {
    "cases/800vdc/stop-v0.1.html",
    "cases/nsq-nsclc-china/stop-v0.1.html",
    "cases/sodium-ion-bess/stop-v0.1.html",
    "docs/cases/800vdc/stop-v0.1.html",
    "docs/cases/nsq-nsclc-china/stop-v0.1.html",
    "docs/cases/sodium-ion-bess/stop-v0.1.html",
}


class MetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.canonical: str | None = None
        self.jsonld: list[str] = []
        self._in_jsonld = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "link" and values.get("rel") == "canonical":
            self.canonical = values.get("href")
        if tag == "script" and values.get("type") == "application/ld+json":
            self._in_jsonld = True
            self.jsonld.append("")

    def handle_endtag(self, tag):
        if tag == "script":
            self._in_jsonld = False

    def handle_data(self, data):
        if self._in_jsonld:
            self.jsonld[-1] += data


def walk_objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_objects(child)


class BrandIdentityTest(unittest.TestCase):
    def test_public_pages_use_current_brand(self):
        for relative in PUBLIC_PAGES:
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("StructEvidence", text, relative)
            self.assertNotIn(LEGACY_CAMEL, text, relative)
            self.assertNotIn(LEGACY_SPACED, text, relative)

    def test_all_public_html_excludes_legacy_display_name(self):
        for path in ROOT.rglob("*.html"):
            if str(path.relative_to(ROOT)) in IMMUTABLE_HTML:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            self.assertNotIn(LEGACY_CAMEL, text, str(path.relative_to(ROOT)))
            self.assertNotIn(LEGACY_SPACED, text, str(path.relative_to(ROOT)))

    def test_domains_are_preserved(self):
        corpus = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in PUBLIC_PAGES)
        self.assertIn("https://structurevidence.org", corpus)
        self.assertIn("https://structevidence.com", corpus)

    def test_canonical_links_are_preserved(self):
        for relative, expected in CANONICALS.items():
            parser = MetadataParser()
            parser.feed((ROOT / relative).read_text(encoding="utf-8"))
            self.assertEqual(parser.canonical, expected, relative)

    def test_jsonld_brand_fields(self):
        pages = ["index.html", "cases/800vdc/index.html", "cases/sodium-ion-bess/index.html"]
        found_brand_field = False
        for relative in pages:
            parser = MetadataParser()
            parser.feed((ROOT / relative).read_text(encoding="utf-8"))
            self.assertTrue(parser.jsonld, relative)
            for payload in parser.jsonld:
                data = json.loads(payload)
                for obj in walk_objects(data):
                    if obj.get("@type") in {"Organization", "WebSite"} or "creator" in obj or "publisher" in obj:
                        serialized = json.dumps(obj, ensure_ascii=False)
                        self.assertNotIn(LEGACY_CAMEL, serialized, relative)
                    if obj.get("@type") == "Organization":
                        found_brand_field = True
                        self.assertEqual(obj.get("name"), "StructEvidence", relative)
        self.assertTrue(found_brand_field)

    def test_generated_evidence_pages_use_current_brand(self):
        pages = sorted((ROOT / "e").glob("*/index.html"))
        self.assertTrue(pages)
        for path in pages:
            text = path.read_text(encoding="utf-8")
            self.assertIn("StructEvidence", text, str(path.relative_to(ROOT)))
            self.assertNotIn(LEGACY_CAMEL, text, str(path.relative_to(ROOT)))

    def test_current_generators_cannot_reintroduce_legacy_display_name(self):
        generators = [
            ROOT / "scripts/export_public_records.py",
            ROOT / "scripts/build_agent_discovery.py",
            *ROOT.glob("scripts/build_*.py"),
            *ROOT.glob("scripts/publish_*.py"),
        ]
        for path in sorted(set(generators)):
            text = path.read_text(encoding="utf-8")
            display_legacy = re.findall(
                rf"(?<![A-Z_]){re.escape(LEGACY_CAMEL)}(?![A-Za-z0-9_])|{re.escape(LEGACY_SPACED)}",
                text,
            )
            self.assertEqual(display_legacy, [], str(path.relative_to(ROOT)))


if __name__ == "__main__":
    unittest.main()
