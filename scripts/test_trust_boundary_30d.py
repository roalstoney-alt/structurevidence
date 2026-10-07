#!/usr/bin/env python3
"""Regression checks for TRUST_BOUNDARY_30D_001 launch controls."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / "ops/growth/TRUST_BOUNDARY_30D_001"

EXPECTED_ASSETS = {
    "decision-cn.pdf": "a96f220ca4e79259f9cf50c9fd5d15e3ccef862df3351e0c5dac595b7905f065",
    "decision-en.pdf": "ca3e6e2bef66a9c64030afd690371668e2d371cdbb90ea7c30dcfd4e165c6bd2",
    "investor-cn.pdf": "54a878aeb3af99356f576476e93d08f4306f4742a3d64835040b37e031a607d1",
    "investor-en.pdf": "c3862d36285ee0dceccd0c662da8fd310a88ce945a69b6b50043ecd33b98c70f",
}

PROHIBITED = (
    "guaranteed",
    "proven true",
    "investment recommendation",
    "approval basis",
    "investment grade",
    "legal assurance",
    "we replace due diligence",
    "best technology",
    "safe investment",
    "unipat is wrong",
    "experts cannot be trusted",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pdf_page_count(path: Path) -> int:
    data = path.read_bytes()
    return len(re.findall(rb"/Type\s*/Page\b", data))


def require_csv_header(path: Path, expected: list[str]) -> None:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        assert next(reader) == expected, f"Unexpected header: {path}"


def main() -> None:
    state = json.loads((CAMPAIGN / "CAMPAIGN_STATE.json").read_text(encoding="utf-8"))
    assert state["campaign_id"] == "TRUST_BOUNDARY_30D_001"
    assert state["window"] == {"start": "2026-10-08", "end": "2026-11-06"}
    assert state["positioning_locked"] is True
    assert state["channels"]["x"]["max_public_posts_per_day"] == 1
    assert state["channels"]["x"]["automated_dm"] is False

    lock = (CAMPAIGN / "POSITIONING_LOCK.md").read_text(encoding="utf-8")
    for phrase in (
        "验证过的结果，仍然不等于事实。",
        "A verified result is still not a fact.",
        "谁来验证验证者？",
        "Who verifies the verifier?",
    ):
        assert phrase in lock

    for filename, expected_hash in EXPECTED_ASSETS.items():
        root_asset = ROOT / "onepager" / filename
        docs_asset = ROOT / "docs/onepager" / filename
        assert root_asset.is_file()
        assert docs_asset.is_file()
        assert sha256(root_asset) == expected_hash
        assert sha256(docs_asset) == expected_hash
        assert root_asset.read_bytes() == docs_asset.read_bytes()
        assert pdf_page_count(root_asset) == 1

        public_url = f"https://structurevidence.org/onepager/{filename}"
        assert public_url in (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        assert public_url in (ROOT / "docs/sitemap.xml").read_text(encoding="utf-8")

    with (CAMPAIGN / "CALENDAR.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 30
    expected_dates = [date(2026, 10, 8) + timedelta(days=i) for i in range(30)]
    assert [row["date"] for row in rows] == [value.isoformat() for value in expected_dates]
    assert rows[0]["status"] == "PREPARED"
    assert rows[1]["status"] == "CHANNEL_READY"

    require_csv_header(
        CAMPAIGN / "METRICS.csv",
        [
            "date",
            "channel",
            "post_url",
            "asset_id",
            "artifact_opens",
            "qualified_dialogues",
            "written_scopes",
            "paid_verifications",
            "memo_or_minutes_citations",
            "boundary_challenges",
            "valid_corrections",
        ],
    )
    require_csv_header(
        CAMPAIGN / "PROSPECTS.csv",
        [
            "prospect_id",
            "company",
            "person",
            "current_role",
            "public_role_evidence",
            "relevant_decision_context",
            "why_trust_boundary_matters",
            "public_contact_route",
            "language",
            "onepager_choice",
            "outreach_status",
        ],
    )

    d1 = (CAMPAIGN / "drafts/D1_2026-10-08_CN_DECISION_MAKER.md").read_text(
        encoding="utf-8"
    )
    assert "PREPARE_ONLY" in d1
    assert "Do not publish automatically" in d1

    d2_path = CAMPAIGN / "posts/x/D2_2026-10-09_Q2_INVESTOR.md"
    d2 = d2_path.read_text(encoding="utf-8")
    assert "CHANNEL_READY" in d2
    assert "Publish before 2026-10-09: PROHIBITED" in d2
    post_copy = d2.split("## Post copy\n", 1)[1].split("\n## Boundary checks", 1)[0].strip()
    assert len(post_copy) <= 280, f"D2 X post is {len(post_copy)} characters"
    lowered = post_copy.lower()
    for phrase in PROHIBITED:
        assert phrase not in lowered, f"Prohibited phrase in D2 post: {phrase}"

    print("TRUST_BOUNDARY_30D_001: PASS")
    print(f"D2_X_CHARACTERS={len(post_copy)}")
    print("ASSETS=4/4")
    print("CALENDAR_DAYS=30/30")


if __name__ == "__main__":
    main()
