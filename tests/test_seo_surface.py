from __future__ import annotations

import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES = ["800vdc", "sodium-ion-bess"]


class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical = None
        self.description = None
        self.in_title = False
        self.title = ""
        self.jsonld: list[str] = []
        self.in_jsonld = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")
        if tag == "meta" and attrs.get("name") == "description":
            self.description = attrs.get("content")
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.in_jsonld = True
            self.jsonld.append("")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "script":
            self.in_jsonld = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_jsonld:
            self.jsonld[-1] += data


class SeoSurfaceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sitemap = (ROOT / "sitemap.xml").read_text()
        ET.fromstring(cls.sitemap)
        cls.robots = (ROOT / "robots.txt").read_text()

    def test_flagship_surfaces(self):
        for slug in CASES:
            text = (ROOT / f"cases/{slug}/index.html").read_text()
            parser = HeadParser()
            parser.feed(text)
            self.assertEqual(parser.canonical, f"https://structurevidence.org/cases/{slug}/")
            self.assertTrue(parser.title.strip(), slug)
            self.assertTrue(parser.description, slug)
            self.assertTrue(parser.jsonld, slug)
            for value in parser.jsonld:
                json.loads(value)
            self.assertIn('class="breadcrumbs"', text)
            self.assertRegex(text, r"As of|Knowledge cutoff")
            self.assertIn("Questions this record addresses", text)
            self.assertIn("Evidence", text)
            self.assertIn("/changes/", text)
            self.assertIn(f"https://structurevidence.org/cases/{slug}/", self.sitemap)
            self.assertNotIn("Disallow: /\n", self.robots)

    def test_homepage_organization_and_website_jsonld(self):
        parser = HeadParser()
        parser.feed((ROOT / "index.html").read_text())
        types = []
        for value in parser.jsonld:
            data = json.loads(value)
            graph = data.get("@graph", [data])
            types.extend(item.get("@type") for item in graph)
        self.assertIn("Organization", types)
        self.assertIn("WebSite", types)

    def test_sitemap_has_meaningful_lastmod(self):
        for slug in CASES:
            block = re.search(rf"<url><loc>https://structurevidence.org/cases/{slug}/</loc><lastmod>([^<]+)</lastmod>", self.sitemap)
            self.assertIsNotNone(block, slug)


if __name__ == "__main__":
    unittest.main()
