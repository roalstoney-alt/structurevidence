from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ["BNB", "SOL", "TRX", "XLM"]
PROHIBITED_FIELDS = {"score", "rank", "rating", "price_target", "trading_signal"}
PROHIBITED_PHRASES = [
    "sell signal",
    "bullish",
    "bearish",
    "price target",
    "top asset",
    "worst asset",
    "86/100",
]


def fail(message: str) -> None:
    raise SystemExit(message)


def check_canonical() -> None:
    ids = set()
    for asset in ASSETS:
        path = ROOT / "research" / "digital-assets" / "batch-01" / asset / "CANONICAL_RESEARCH.json"
        if not path.exists():
            fail(f"missing canonical {asset}")
        data = json.loads(path.read_text(encoding="utf-8"))
        if data["research_id"] in ids:
            fail(f"duplicate research_id {data['research_id']}")
        ids.add(data["research_id"])
        if PROHIBITED_FIELDS & set(data):
            fail(f"prohibited fields in {asset}: {PROHIBITED_FIELDS & set(data)}")
        for key in ["structural_state", "evidence_state", "material_inconsistency", "source_coverage", "last_reviewed"]:
            if not data.get(key):
                fail(f"missing {key} in {asset}")
        if data["material_inconsistency"] == "YES":
            fail(f"human review required before public publication for {asset}")


def check_search() -> None:
    index = json.loads((ROOT / "docs" / "assets" / "entities.json").read_text(encoding="utf-8"))
    covered = {item["ticker"].lower(): item for item in index if item.get("covered")}
    for asset in ASSETS:
        if asset.lower() not in covered:
            fail(f"missing covered search alias {asset}")
        if not (ROOT / "docs" / covered[asset.lower()]["result_url"]).exists():
            fail(f"missing result page for {asset}")
    for query in ["tether", "usdt", "uniswap", "binance", "unknown asset"]:
        if query in covered:
            fail(f"uncovered query incorrectly covered: {query}")


def check_freeze() -> None:
    for asset in ASSETS:
        freeze = ROOT / "evidence-freeze" / "DIGITAL-ASSET-BATCH-01" / asset
        sums = freeze / "SHA256SUMS.txt"
        if not sums.exists():
            fail(f"missing SHA256SUMS for {asset}")
        for line in sums.read_text(encoding="utf-8").splitlines():
            digest, name = line.split("  ", 1)
            actual = hashlib.sha256((freeze / name).read_bytes()).hexdigest()
            if actual != digest:
                fail(f"hash mismatch {asset}/{name}")


def check_language() -> None:
    paths = list((ROOT / "docs").rglob("*.html")) + list((ROOT / "research" / "digital-assets").rglob("*.md"))
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for phrase in PROHIBITED_PHRASES:
            if phrase in text:
                fail(f"prohibited phrase {phrase!r} in {path}")
        original = path.read_text(encoding="utf-8")
        if re.search(r"(?<![A-Z0-9])A[+-](?![A-Z0-9])", original):
            fail(f"prohibited rating token in {path}")


def main() -> None:
    check_canonical()
    check_search()
    check_freeze()
    check_language()
    print("BATCH01_TESTS_PASS")


if __name__ == "__main__":
    main()
