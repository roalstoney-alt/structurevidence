#!/usr/bin/env python3
"""Audit internal links and required parent/state relationships."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
HREF = re.compile(r'''href=["']([^"']+)["']''', re.I)


def local_target(source: Path, href: str) -> Path | None:
    parsed = urlparse(href)
    if parsed.scheme or parsed.netloc or href.startswith(("mailto:", "tel:", "#")):
        return None
    path = unquote(parsed.path)
    target = ROOT / path.lstrip("/") if path.startswith("/") else source.parent / path
    if path.endswith("/"):
        target /= "index.html"
    elif not target.suffix:
        target = target / "index.html" if (target / "index.html").exists() else target
    return target.resolve()


def main() -> int:
    sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    html_files: list[Path] = []
    for loc in sitemap.findall("sm:url/sm:loc", namespace):
        path = urlparse(loc.text or "").path
        if path.endswith((".json", ".xml", ".pdf")):
            continue
        candidate = ROOT / path.lstrip("/")
        candidate = candidate / "index.html" if path.endswith("/") else candidate
        if candidate.is_file() and candidate.suffix == ".html":
            html_files.append(candidate)
    html_files = sorted(set(html_files))
    broken: list[str] = []
    linked: set[Path] = set()
    for source in html_files:
        for href in HREF.findall(source.read_text(encoding="utf-8", errors="ignore")):
            target = local_target(source, href)
            if target is None:
                continue
            linked.add(target)
            if not target.exists():
                broken.append(f"{source.relative_to(ROOT)} -> {href}")
    case_json = sorted(ROOT.glob("cases/*/index.json"))
    case_without_state = []
    evidence_without_parent = []
    for path in case_json:
        record = json.loads(path.read_text(encoding="utf-8"))
        if not record.get("current_state") or not record.get("history"):
            case_without_state.append(str(path.relative_to(ROOT)))
    for path in ROOT.glob("e/*/index.json"):
        record = json.loads(path.read_text(encoding="utf-8"))
        if not record.get("parent_case") or not record.get("parent_case_url"):
            evidence_without_parent.append(str(path.relative_to(ROOT)))
    public_records = {path.parent / "index.html" for path in case_json} | set(ROOT.glob("e/*/index.html"))
    entrypoints = {ROOT / "index.html", ROOT / "cases/index.html", ROOT / "changes/index.html"}
    orphans = sorted(str(path.relative_to(ROOT)) for path in public_records if path not in linked and path not in entrypoints)
    print(f"ORPHAN_PAGE_COUNT = {len(orphans)}")
    print(f"BROKEN_INTERNAL_LINK_COUNT = {len(broken)}")
    print(f"CASE_WITHOUT_STATE_COUNT = {len(case_without_state)}")
    print(f"EVIDENCE_WITHOUT_PARENT_COUNT = {len(evidence_without_parent)}")
    for item in orphans + broken + case_without_state + evidence_without_parent:
        print(item)
    return 1 if orphans or broken or case_without_state or evidence_without_parent else 0


if __name__ == "__main__":
    raise SystemExit(main())
