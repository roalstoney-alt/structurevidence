from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE = "b3d4d25dec622baf55d5cefa72450b8c43e8a517"
ASSETS = ["BNB", "SOL", "TRX", "XLM"]
REQUIRED = [
    "OBSERVATION_REGISTRY.json",
    "CLAIM_REGISTRY.json",
    "HYPOTHESIS_REGISTRY.json",
    "COUNTER_EVIDENCE_SEARCH_LOG.json",
    "ECL_AXIS_ANALYSIS.md",
    "ECL_FINAL_SYNTHESIS.md",
    "BLIND_REVIEW_OUTPUT.md",
    "AGREEMENT_DIVERGENCE_AUDIT.md",
]
ALLOWED_STRUCTURAL = {
    "BURN_LINKED_ECOSYSTEM_UTILITY_REGIME",
    "EXECUTION_SCALE_WITH_PARTIAL_CLIENT_DIVERSITY",
    "STABLECOIN_RESOURCE_SETTLEMENT_REGIME",
    "SDF_TREASURY_DEPENDENT_PAYMENT_NETWORK",
}
ALLOWED_EVIDENCE = {"ALIGNED", "TEMPORAL_CHANGE", "POTENTIAL_CONFLICT", "UNRECONCILED", "INSUFFICIENT"}
ALLOWED_SUPERSESSION = {"UNCHANGED", "REFINED", "SUPERSEDED", "WITHDRAWN"}


def fail(message: str) -> None:
    raise SystemExit(message)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_show(rel: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{BASELINE}:{rel}"], cwd=ROOT)


def current_hash(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def baseline_hash(rel: str) -> str:
    return hashlib.sha256(git_show(rel)).hexdigest()


def check_required_artifacts() -> None:
    for asset in ASSETS:
        base = ROOT / "research" / "digital-assets" / "batch-01-r1" / asset
        freeze = ROOT / "evidence-freeze" / "DIGITAL-ASSET-BATCH-01-R1" / asset
        for name in REQUIRED:
            if not (base / name).exists():
                fail(f"missing research artifact {asset}/{name}")
            if not (freeze / name).exists():
                fail(f"missing freeze artifact {asset}/{name}")


def check_pages_and_labels() -> None:
    entities = {e["ticker"]: e for e in read_json(ROOT / "assets" / "entities.json") if e.get("ticker") in ASSETS}
    headings = [
        "1. Mechanism Judgment",
        "2. Supporting Observations",
        "3. Rival Hypotheses / ACH",
        "4. Counter-Evidence",
        "5. Evidence Gaps",
        "6. Diff vs v0.1",
    ]
    for asset in ASSETS:
        can = read_json(ROOT / "research" / "digital-assets" / "batch-01-r1" / asset / "CANONICAL_RESEARCH_R1.json")
        html = (ROOT / f"{asset.lower()}.html").read_text(encoding="utf-8")
        docs_html = (ROOT / "docs" / f"{asset.lower()}.html").read_text(encoding="utf-8")
        last = -1
        for heading in headings:
            pos = html.find(heading)
            if pos <= last:
                fail(f"missing or unordered block {asset}: {heading}")
            last = pos
            if heading not in docs_html:
                fail(f"docs mirror missing block {asset}: {heading}")
        root_contract = html[html.find(headings[0]):html.find("<h2>Links</h2>")]
        docs_contract = docs_html[docs_html.find(headings[0]):docs_html.find("<h2>Links</h2>")]
        if root_contract != docs_contract:
            fail(f"root/docs six-block divergence {asset}")
        entity = entities[asset]
        for value in [
            can["research_id"],
            can["structural_state_final"],
            can["evidence_state_final"],
            can["publication_status"],
            can["source_coverage"],
            can["material_inconsistency"],
            can["last_reviewed"],
            entity["structural_state"],
            entity["evidence_state"],
        ]:
            if value not in html:
                fail(f"page/entity/canonical mismatch {asset}: {value}")
        if "DECISION_USEFULNESS: NOT_ESTABLISHED" not in html:
            fail(f"decision usefulness changed {asset}")
        if "verify-r1.html#" + asset.lower() not in html:
            fail(f"human verify cta missing {asset}")
        pilot = f"research/digital-assets/{asset}/{asset}_STRUCTURAL_DYNAMICS_REPORT_v0.1.md"
        if pilot not in html or not (ROOT / pilot).exists():
            fail(f"v0.1 pilot missing or unlinked {asset}")
        if can["material_inconsistency"] == "YES" and can["supersession_status"] == "REFINED":
            fail(f"material inconsistency cannot publish refined-only status {asset}")
    sol = (ROOT / "sol.html").read_text(encoding="utf-8")
    if "Party / claim A" not in sol or "Party / claim B" not in sol:
        fail("SOL conflict parties hidden")


def check_reports_conclusion_distinct() -> None:
    for asset in ASSETS:
        base = ROOT / "research" / "digital-assets" / "batch-01-r1" / asset
        structural = (base / "STRUCTURAL_DYNAMICS_REPORT_R1.md").read_text(encoding="utf-8").splitlines()
        evidence = (base / "PUBLIC_EVIDENCE_RESEARCH_REPORT_R1.md").read_text(encoding="utf-8").splitlines()
        s_tail = " ".join(line.strip() for line in structural[-8:] if line.strip())
        e_tail = " ".join(line.strip() for line in evidence[-8:] if line.strip())
        if s_tail == e_tail:
            fail(f"identical conclusion tail {asset}")


def check_vocab() -> None:
    vocab = (ROOT / "docs" / "STATE_VOCAB.md").read_text(encoding="utf-8")
    for phrase in ["issuance/burn", "settlement object", "governance dependence", "client/validator structure", "treasury dependence"]:
        if phrase not in vocab:
            fail(f"missing vocab axis {phrase}")
    for asset in ASSETS:
        can = read_json(ROOT / "research" / "digital-assets" / "batch-01-r1" / asset / "CANONICAL_RESEARCH_R1.json")
        if can["structural_state_final"] not in ALLOWED_STRUCTURAL:
            fail(f"unknown structural label {asset}")
        if can["evidence_state_final"] not in ALLOWED_EVIDENCE:
            fail(f"unknown evidence enum {asset}")
        if can["supersession_status"] not in ALLOWED_SUPERSESSION:
            fail(f"unknown supersession enum {asset}")


def check_verify_and_refinement() -> None:
    verify = (ROOT / "verify-r1.html").read_text(encoding="utf-8")
    table = (ROOT / "research" / "digital-assets" / "batch-01-r1" / "REFINEMENT_TABLE.html").read_text(encoding="utf-8")
    digital = (ROOT / "digital-assets.html").read_text(encoding="utf-8")
    research = (ROOT / "research.html").read_text(encoding="utf-8")
    for asset in ASSETS:
        if f'id="{asset.lower()}"' not in verify:
            fail(f"verify block missing {asset}")
        if asset not in table:
            fail(f"refinement table missing {asset}")
    for text in [digital, research]:
        if "REFINEMENT_TABLE.html" not in text or "verify-r1.html" not in text:
            fail("front office links missing")
    if "Five covered entities" not in digital or "Decision usefulness is not established" not in digital:
        fail("coverage count or decision boundary missing")
    if "EXPECTED_SELF_HASH_EXCLUSION" not in verify or ">GAP<" in verify:
        fail("verify self-hash exclusion not labeled")
    for phrase in ["producer_source", "reviewer_artifact", "SEPARATION: FILENAME_ONLY"]:
        if phrase not in verify:
            fail(f"verify separation copy missing: {phrase}")


def check_homepage_contract() -> None:
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    docs_index = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    for text in [index, docs_index]:
        for required in ["Monitor structural change.", 'action="monitor.html"', "BNB structural and evidence state", "Executive insight", "How the observed structure changed", "reports.html"]:
            if required not in text:
                fail(f"homepage missing required text/link: {required}")
        for removed in ["Asset states", ">SOL<", ">TRX<", ">XLM<", ">MSTR<"]:
            if removed in text:
                fail(f"homepage still exposes removed coverage content: {removed}")
        for moved in ["coverage-index", "SOL is featured as the conflict demonstration case", "REFINEMENT_TABLE.html", "verify-r1.html"]:
            if moved in text:
                fail(f"homepage still exposes moved research detail: {moved}")
        for forbidden in ["Health Score", "HEALTH SCORE", "Health Card", "HEALTH CARD"]:
            if forbidden in text:
                fail(f"homepage old score/rating copy remains: {forbidden}")
    for path in [ROOT / "assets" / "site.js", ROOT / "docs" / "assets" / "site.js"]:
        text = path.read_text(encoding="utf-8")
        for forbidden in ["Health Score", "HEALTH SCORE", "Health Card", "HEALTH CARD", "View Full Audit"]:
            if forbidden in text:
                fail(f"search renderer old score/rating copy remains in {path}: {forbidden}")


def check_strategy_and_old_batch_unchanged() -> None:
    strategy_fields = read_json(ROOT / "assets" / "entities.json")[0]
    if strategy_fields["ticker"] != "MSTR":
        fail("strategy entity order changed unexpectedly")
    if strategy_fields["structural_state"] != "HYBRID_ACCUMULATION_MONETIZATION":
        fail("strategy structural field changed")
    if strategy_fields["evidence_state"] != "SEMANTIC_TENSION_BUT_RECONCILABLE":
        fail("strategy evidence field changed")
    for rel in [
        "docs/research/Strategy_2026_Public_Evidence_Research_Report_v0.1_CN.md",
        "docs/research/Strategy_2026_Structural_Dynamics_Report_v0.1_CN.md",
        "docs/research/Structural_Dynamics_Evidence_Dynamics_Method_Paper_v0.1_CN.md",
        "docs/research/PUBLICATION_PACKAGE_MANIFEST.json",
    ]:
        if current_hash(rel) != baseline_hash(rel):
            fail(f"strategy file changed: {rel}")
    old_paths = subprocess.check_output(["git", "diff", "--name-only", BASELINE, "--", "research/digital-assets/batch-01", "evidence-freeze/DIGITAL-ASSET-BATCH-01", "docs/evidence-freeze/DIGITAL-ASSET-BATCH-01"], cwd=ROOT, text=True)
    if old_paths.strip():
        fail(f"old batch paths changed: {old_paths}")


def main() -> None:
    check_required_artifacts()
    check_pages_and_labels()
    check_reports_conclusion_distinct()
    check_vocab()
    check_verify_and_refinement()
    check_homepage_contract()
    check_strategy_and_old_batch_unchanged()
    print("R1_HUMAN_SURFACE_TESTS_PASS")


if __name__ == "__main__":
    main()
