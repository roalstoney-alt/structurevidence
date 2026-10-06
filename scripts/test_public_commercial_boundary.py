#!/usr/bin/env python3
"""Regression checks for the frozen public/commercial boundary."""

from __future__ import annotations

import json
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
    "cases/800vdc/index.html": ("OEG-CML-001", "OEG-CML-002"),
    "cases/sodium-ion-bess/index.html": ("OEG-BESS-001", "OEG-BESS-002"),
    "cases/nsq-nsclc-china/index.html": ("OEG-ONC-001", "OEG-ONC-002"),
}


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    boundary = json.loads(read("data/vortex-activation/public-commercial-boundary-v0.1.json"))
    require(boundary["challenge_requires_payment"] is False, "challenge cannot require payment")
    require(boundary["challenge_enters_sales_funnel"] is False, "challenge cannot enter sales funnel")
    require(boundary["commercial_verify_required_for_challenge"] is False, "commercial verify cannot gate challenge")
    require(boundary["no_auto_state_change"] is True, "no-auto-state-change must remain frozen")
    require(boundary["oil_status"] == "PAUSED", "OIL must remain paused")

    index = read("gaps/index.html")
    require(sum(f'data-gap-id="{gap_id}"' in index for gap_id in GAP_IDS) == 6, "index must render six Gap records")
    for field in (
        "GAP_ID", "CASE_ID", "CLAIM", "CURRENT STATE", "SCOPE", "EVIDENCE CUTOFF",
        "WHAT IS ESTABLISHED", "WHAT IS NOT ESTABLISHED", "WHAT WOULD CHANGE THIS",
        "ACCEPTABLE SOURCES", "NON-QUALIFYING SOURCES",
    ):
        require(field in index, f"index missing {field}")
    require("USD " not in index and "Request a quote" not in index, "Gap index contains commercial pricing or quote copy")

    for gap_id in GAP_IDS:
        relative = f"gaps/{gap_id}/index.html"
        detail = read(relative)
        require((ROOT / "docs" / relative).read_bytes() == (ROOT / relative).read_bytes(), f"root/docs drift: {relative}")
        require(f'<link rel="alternate" type="application/json" href="https://structevidence.com/api/gaps/{gap_id}">' in detail, f"alternate API missing: {gap_id}")
        require(f'action="https://structevidence.com/api/gaps/{gap_id}/challenge"' in detail, f"wrong POST target: {gap_id}")
        effects = re.findall(r'<option value="(SUPPORT|CONTRADICT|NARROW_SCOPE|CORRECT_ATTRIBUTION)">', detail)
        attributions = re.findall(r'<option value="(NAMED|ORGANIZATION_ONLY|ANONYMOUS)">', detail)
        require(effects == ["SUPPORT", "CONTRADICT", "NARROW_SCOPE", "CORRECT_ATTRIBUTION"], f"effect vocabulary drift: {gap_id}")
        require(attributions == ["NAMED", "ORGANIZATION_ONLY", "ANONYMOUS"], f"attribution vocabulary drift: {gap_id}")
        require("Submission does not automatically change the claim state." in detail, f"no-auto-change warning missing: {gap_id}")
        require("Public attribution is optional." in detail, f"attribution warning missing: {gap_id}")
        require("USD " not in detail and "Request a quote" not in detail, f"commercial pricing found: {gap_id}")
        require('href="https://structevidence.com/verify/">Open commercial verification</a>' in detail, f"secondary commercial CTA missing: {gap_id}")

    for case_path, gap_ids in CASE_GAPS.items():
        case = read(case_path)
        require(case.count(">Challenge this gap</a>") == 2, f"case must expose exactly two Gap CTAs: {case_path}")
        for gap_id in gap_ids:
            require(f'href="/gaps/{gap_id}/">Challenge this gap</a>' in case, f"incorrect case routing: {gap_id}")
        require("Verify this gap" not in case and "/verify/?case=" not in case, f"legacy Gap CTA remains: {case_path}")
        require('href="https://structevidence.com/verify/">Need this evaluated for your decision?</a>' in case, f"secondary commercial CTA missing: {case_path}")

    legacy = read("cases/submit-evidence/index.html")
    require("Legacy / fallback contact route" in legacy, "legacy submit route not reclassified")
    require('href="/gaps/">Open Evidence Gaps</a>' in legacy, "legacy route does not prefer Gap workflow")

    wrangler = read("deploy/cloudflare-landing/wrangler.jsonc")
    require("https://structurevidence.org" in wrangler, "research origin missing from Worker configuration")
    require("https://www.structurevidence.org" in wrangler, "www research origin missing from Worker configuration")
    require('"PUBLIC_ORIGINS": "*"' not in wrangler, "wildcard POST CORS is forbidden")

    oil = json.loads(read("data/vortex-activation/oil-genesis-001-pause-sync.json"))
    require(oil["oil_state"]["current_status"] == "PAUSED", "OIL status changed")

    require((ROOT / "docs/gaps/index.html").read_bytes() == (ROOT / "gaps/index.html").read_bytes(), "Gap index root/docs drift")
    require((ROOT / "docs/assets/gap-challenge.js").read_bytes() == (ROOT / "assets/gap-challenge.js").read_bytes(), "Gap form script root/docs drift")

    print("PASS: public/commercial boundary freeze")
    print("PASS: .org Gap index and six detail pages")
    print("PASS: exact challenge form vocabularies and canonical POST targets")
    print("PASS: case CTA hierarchy and legacy fallback routing")
    print("PASS: explicit research-origin CORS, privacy boundary, and OIL pause")


if __name__ == "__main__":
    main()
