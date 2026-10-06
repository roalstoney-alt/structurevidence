#!/usr/bin/env python3
"""Validate the .org Open Evidence Gap discovery and challenge surface."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAP_IDS = (
    "OEG-CML-001",
    "OEG-CML-002",
    "OEG-BESS-001",
    "OEG-BESS-002",
    "OEG-ONC-001",
    "OEG-ONC-002",
)
CASE_GAPS = {
    "cases/800vdc/index.html": {"OEG-CML-001", "OEG-CML-002"},
    "cases/sodium-ion-bess/index.html": {"OEG-BESS-001", "OEG-BESS-002"},
    "cases/nsq-nsclc-china/index.html": {"OEG-ONC-001", "OEG-ONC-002"},
}


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    gaps = read("gaps/index.html")
    require(gaps == read("docs/gaps/index.html"), "root/docs gaps discovery drift")
    require('rel="canonical" href="https://structurevidence.org/gaps/"' in gaps, "missing .org canonical")
    require(
        '<link rel="alternate" type="application/json" href="https://structevidence.com/api/gaps">' in gaps,
        "missing canonical machine endpoint metadata",
    )
    require(gaps.count('data-gap-id="') == 6, "discovery page must contain exactly six gap records")
    require(gaps.count(">Challenge this gap</a>") == 6, "discovery page must contain six primary challenge CTAs")
    require(gaps.count(">View case</a>") == 6, "discovery page must contain six case CTAs")

    for gap_id in GAP_IDS:
        require(gaps.count(f'data-gap-id="{gap_id}"') == 1, f"missing or duplicate discovery record: {gap_id}")
        require(
            f'href="/gaps/{gap_id}/">Challenge this gap</a>' in gaps,
            f"incorrect .org challenge target: {gap_id}",
        )

    for relative, expected in CASE_GAPS.items():
        html = read(relative)
        linked = set(re.findall(r'href="/gaps/(OEG-[A-Z]+-\d{3})/"', html))
        require(linked == expected, f"case-to-gap links differ for {relative}: {linked}")
        require("Verify this gap" not in html, f"stale commercial gap CTA in {relative}")
        require("https://structevidence.com/verify/?case=" not in html, f"gap still routed to /verify/ in {relative}")
        require("https://structevidence.com/verify/" in html, f"commercial verification path not separately retained in {relative}")
        require(html == read(f"docs/{relative}"), f"root/docs case drift: {relative}")

    for relative in ("index.html", "cases/index.html"):
        require('href="/gaps/">Open Evidence Gaps</a>' in read(relative), f"missing navigation link: {relative}")
        require(read(relative) == read(f"docs/{relative}"), f"root/docs navigation drift: {relative}")

    architecture_copy = (
        "Public evidence challenges are accepted against defined Open Evidence Gaps. "
        "Submissions enter human review and never change claim state automatically."
    )
    require(architecture_copy in read("architecture.html"), "architecture copy was not updated")
    require(read("architecture.html") == read("docs/architecture.html"), "root/docs architecture drift")
    require("https://structurevidence.org/gaps/" in read("sitemap.xml"), "gaps page missing from sitemap")
    require(read("sitemap.xml") == read("docs/sitemap.xml"), "root/docs sitemap drift")
    print("PASS: .org Open Evidence Gap discovery page exposes exactly six canonical challenge links")
    print("PASS: all three case pages route to their exact two Open Evidence Gaps")
    print("PASS: commercial /verify/ remains separate and no gap CTA routes there")
    print("PASS: architecture copy, navigation, sitemap, API metadata, and root/docs parity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
