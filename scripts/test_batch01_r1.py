from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ["BNB", "SOL", "TRX", "XLM"]
R1 = "DIGITAL-ASSET-BATCH-01-R1"
PROHIBITED_FIELDS = {"score", "rank", "rating", "price_target", "trading_signal"}
PROHIBITED_PHRASES = ["buy", "sell signal", "bullish", "bearish", "price target", "top asset", "worst asset", "validated asset", "a-rated"]
OLD_STATE_PARTS = [
    "SUPPLY_" + "CONTRACTION_WITH_ECOSYSTEM_UTILITY",
    "PERFORMANCE_" + "EXPANSION_WITH_CLIENT_DIVERSIFICATION",
    "STABLECOIN_" + "SETTLEMENT_RESOURCE_REGIME",
    "FOUNDATION_" + "FUNDED_PAYMENT_NETWORK",
    "COMPLE" + "MENTARY",
    "CON" + "SISTENT",
    "SEMANTIC_" + "TENSION_BUT_RECONCILABLE",
]


def fail(message: str) -> None:
    raise SystemExit(message)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def check_schema_and_freeze() -> None:
    required = {
        "research_id", "asset", "observation_window", "structural_state_primary", "structural_state_reviewer",
        "structural_state_final", "structural_agreement", "evidence_state_primary", "evidence_state_reviewer",
        "evidence_state_final", "evidence_agreement", "material_inconsistency", "source_coverage",
        "artifact_coverage", "numerical_reconciliations", "hypotheses", "counter_evidence", "open_questions",
        "what_would_change_conclusion", "supersession_status", "publication_status", "method_version", "last_reviewed",
    }
    ids = set()
    for asset in ASSETS:
        base = ROOT / "research" / "digital-assets" / "batch-01-r1" / asset
        freeze = ROOT / "evidence-freeze" / R1 / asset
        docs_base = ROOT / "docs" / "research" / "digital-assets" / "batch-01-r1" / asset
        for path in [base, freeze, docs_base]:
            if not path.exists():
                fail(f"missing r1 directory {path}")
        can = load(base / "CANONICAL_RESEARCH_R1.json")
        missing = required - set(can)
        if missing:
            fail(f"missing canonical keys {asset}: {sorted(missing)}")
        if PROHIBITED_FIELDS & set(can):
            fail(f"prohibited canonical fields {asset}: {PROHIBITED_FIELDS & set(can)}")
        if can["research_id"] in ids:
            fail(f"duplicate research id {can['research_id']}")
        ids.add(can["research_id"])
        if len(can["hypotheses"]) < 4:
            fail(f"too few hypotheses {asset}")
        if len(can["counter_evidence"]) != len(can["hypotheses"]):
            fail(f"counter-evidence coverage mismatch {asset}")
        if len(can["numerical_reconciliations"]) < 3:
            fail(f"numerical depth limited {asset}")
        sums = freeze / "SHA256SUMS.txt"
        if not sums.exists():
            fail(f"missing sums {asset}")
        for line in sums.read_text(encoding="utf-8").splitlines():
            digest, filename = line.split("  ", 1)
            actual = hashlib.sha256((freeze / filename).read_bytes()).hexdigest()
            if digest != actual:
                fail(f"hash mismatch {asset}/{filename}")


def check_anti_preset() -> None:
    source = (ROOT / "scripts" / "publish_batch01_r1.py").read_text(encoding="utf-8")
    for old in OLD_STATE_PARTS:
        if old in source:
            fail(f"old state preset in r1 generator: {old}")


def check_hypothesis_specificity() -> None:
    descriptions = []
    for asset in ASSETS:
        can = load(ROOT / "research" / "digital-assets" / "batch-01-r1" / asset / "CANONICAL_RESEARCH_R1.json")
        descriptions.extend(h["description"].lower() for h in can["hypotheses"])
    duplicates = {d for d in descriptions if descriptions.count(d) > 1}
    if duplicates:
        fail(f"duplicate ach descriptions: {duplicates}")
    if any("structural state is driven by protocol" in d for d in descriptions):
        fail("generic old ACH template detected")


def check_reports_and_traceability() -> None:
    for asset in ASSETS:
        base = ROOT / "research" / "digital-assets" / "batch-01-r1" / asset
        obs_ids = {o["observation_id"] for o in load(base / "OBSERVATION_REGISTRY.json")}
        src_ids = {s["source_id"] for s in load(base / "SOURCE_INVENTORY.json")}
        claim_sources = {c["source_id"] for c in load(base / "CLAIM_REGISTRY.json")}
        if not claim_sources <= src_ids:
            fail(f"claim traceability source gap {asset}")
        report = (base / "STRUCTURAL_DYNAMICS_REPORT_R1.md").read_text(encoding="utf-8")
        if not any(obs_id in report for obs_id in obs_ids):
            fail(f"report lacks observation trace anchor {asset}")
        section_headers = re.findall(r"(?m)^\d\d\s+[^\n]+$", report)
        if len(section_headers) < 19:
            fail(f"too few substantive structural sections {asset}")
        paragraphs = [p.strip() for p in report.split("\n\n") if len(p.strip()) > 80 and "Research only" not in p]
        repeats = {p for p in paragraphs if paragraphs.count(p) > 1}
        if repeats:
            fail(f"repeated report paragraph {asset}")


def check_search_and_pages() -> None:
    index = load(ROOT / "docs" / "assets" / "entities.json")
    covered = {item.get("ticker"): item for item in index if item.get("covered")}
    for asset in ASSETS:
        item = covered.get(asset)
        if not item:
            fail(f"missing search entity {asset}")
        if item.get("research_status") != "R1 RESEARCH SUPPORT":
            fail(f"search card not r1 {asset}")
        for key in ["result_url", "structural_report_url", "evidence_report_url", "research_chain_url"]:
            target = ROOT / "docs" / item[key].split("#", 1)[0]
            if not target.exists():
                fail(f"missing linked target {asset}: {item[key]}")


def check_language() -> None:
    paths = [ROOT / "docs" / f"{asset.lower()}.html" for asset in ASSETS]
    paths += [ROOT / "docs" / "digital-assets.html", ROOT / "docs" / "assets" / "entities.json"]
    paths += list((ROOT / "research" / "digital-assets" / "batch-01-r1").rglob("*.md"))
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for phrase in PROHIBITED_PHRASES:
            if phrase in text:
                fail(f"prohibited phrase {phrase!r} in {path}")
        original = path.read_text(encoding="utf-8")
        if re.search(r"(?<![A-Z0-9])A[+-](?![A-Z0-9])", original):
            fail(f"rating token in {path}")


def check_old_unchanged() -> None:
    expected_strategy = {
        "docs/research/Strategy_2026_Public_Evidence_Research_Report_v0.1_CN.md": "81f9c8810b7cabd86426f6fc115f62ee20cc953494259a878c7a4a1f5c044fc0",
        "docs/research/Strategy_2026_Structural_Dynamics_Report_v0.1_CN.md": "75dfb5cd4eab564bf4c3989662ede851ceac16a6ed34c85587366760566697f7",
        "docs/research/Structural_Dynamics_Evidence_Dynamics_Method_Paper_v0.1_CN.md": "fe7c8f696cf14c3f5b3b470bc21d116c304b78d7bf60f949f043bfd335b4da8b",
        "docs/research/PUBLICATION_PACKAGE_MANIFEST.json": "272036c9da4075b44241cbb9473798d7b9ce5cb098b81bdbd98d6acdc26a4554",
    }
    for rel, digest in expected_strategy.items():
        if hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() != digest:
            fail(f"strategy hash changed: {rel}")
    for asset in ASSETS:
        if not (ROOT / "research" / "digital-assets" / "batch-01" / asset / "CANONICAL_RESEARCH.json").exists():
            fail(f"old batch canonical missing {asset}")


def main() -> None:
    check_schema_and_freeze()
    check_anti_preset()
    check_hypothesis_specificity()
    check_reports_and_traceability()
    check_search_and_pages()
    check_language()
    check_old_unchanged()
    print("BATCH01_R1_TESTS_PASS")


if __name__ == "__main__":
    main()
