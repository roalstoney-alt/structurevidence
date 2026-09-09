from __future__ import annotations

import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ASSETS = ["BNB", "SOL", "TRX", "XLM"]
R1 = "DIGITAL-ASSET-BATCH-01-R1"
TODAY = "2026-09-09"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def esc(value) -> str:
    return str(value if value is not None else "GAP").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def nav() -> str:
    return '<header class="site-header"><div class="nav-wrap"><a class="brand" href="index.html"><span class="brand-mark">SE</span><span>StructEvidence</span></a><button class="nav-toggle" data-nav-toggle aria-controls="nav" aria-expanded="false">Menu</button><nav class="nav" id="nav" aria-label="Main navigation"><a href="index.html#search">Search</a><a href="research.html">Research</a><a href="standard.html">Standard</a><a href="about.html">About</a><a href="enterprise.html" class="enterprise-link">Enterprise Access</a></nav></div></header>'


def footer() -> str:
    return '<footer class="site-footer"><div class="footer-inner"><div class="footer-links"><strong>StructEvidence</strong><a href="research.html">Research</a><a href="standard.html">Standard</a><a href="about.html">About</a><a href="enterprise.html">Enterprise</a></div><p>Research only. No investment advice. Evidence inconsistency does not imply falsehood, misconduct or fraud. Findings may be corrected or superseded.</p></div></footer><script src="assets/site.js"></script>'


def paths(asset: str) -> dict[str, Path]:
    base = ROOT / "research" / "digital-assets" / "batch-01-r1" / asset
    freeze = ROOT / "evidence-freeze" / R1 / asset
    return {
        "base": base,
        "freeze": freeze,
        "canonical": base / "CANONICAL_RESEARCH_R1.json",
        "observations": base / "OBSERVATION_REGISTRY.json",
        "claims": base / "CLAIM_REGISTRY.json",
        "hypotheses": base / "HYPOTHESIS_REGISTRY.json",
        "counter": base / "COUNTER_EVIDENCE_SEARCH_LOG.json",
        "source_dependency": base / "SOURCE_DEPENDENCY_GRAPH.json",
        "manifest": freeze / "MANIFEST.json",
        "structural_report": base / "STRUCTURAL_DYNAMICS_REPORT_R1.md",
        "evidence_report": base / "PUBLIC_EVIDENCE_RESEARCH_REPORT_R1.md",
        "v01_structural": ROOT / "research" / "digital-assets" / asset / f"{asset}_STRUCTURAL_DYNAMICS_REPORT_v0.1.md",
    }


def asset_data(asset: str) -> dict:
    p = paths(asset)
    return {
        "asset": asset,
        "canonical": read_json(p["canonical"]),
        "observations": read_json(p["observations"]),
        "claims": read_json(p["claims"]),
        "hypotheses": read_json(p["hypotheses"]),
        "counter": read_json(p["counter"]),
        "source_dependency": read_json(p["source_dependency"]),
        "manifest": read_json(p["manifest"]),
    }


def source_class(asset: str, source_id: str) -> str:
    inv = read_json(paths(asset)["base"] / "SOURCE_INVENTORY.json")
    for row in inv:
        if row.get("source_id") == source_id:
            return row.get("source_type") or "GAP"
    return "GAP"


def old_state(asset: str) -> dict:
    return read_json(ROOT / "research" / "digital-assets" / "batch-01" / asset / "CANONICAL_RESEARCH.json")


def asset_page(asset: str) -> str:
    data = asset_data(asset)
    can = data["canonical"]
    old = old_state(asset)
    obs_items = []
    for row in data["observations"][:5]:
        obs_items.append(f"<li><strong>{esc(row['observation_id'])}</strong> [{esc(source_class(asset, row['source_id']))}] {esc(row['statement'])}</li>")
    hyp_items = []
    for h in data["hypotheses"]:
        hyp_items.append(f"<li><strong>{esc(h['hypothesis_id'])}</strong> {esc(h['description'])} Status: <code>{esc(h['status'])}</code>. Falsifier: {esc(h['potential_falsifier'])}</li>")
    counter_items = []
    for c in data["counter"][:5]:
        found = "; ".join(c.get("counter_evidence_found") or ["No overturning evidence recorded in the targeted log."])
        counter_items.append(f"<li><strong>{esc(c['hypothesis_id'])}</strong> {esc(c['impact'])} Remaining uncertainty: {esc(c['remaining_uncertainty'])} Recorded result: {esc(found)}</li>")
    groups = data["source_dependency"].get("groups") or []
    gap_text = "GAP" if not groups else "; ".join(f"{g.get('dependency_group', 'GAP')} ({len(g.get('source_ids', []))} source ids)" for g in groups)
    sol_conflict = ""
    if asset == "SOL":
        sol_conflict = """
    <div class="callout"><h3>SOL POTENTIAL_CONFLICT Parties</h3><p><strong>Party / claim A:</strong> Execution scale and client-diversity work are visible in fee, delegation and client-status artifacts.</p><p><strong>Party / claim B:</strong> Production resilience is not established where client diversity may still be implementation-transition evidence rather than completed voting-client diversity.</p></div>
"""
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{asset} R1 Human Verify - StructEvidence</title>
  <meta name="description" content="Human-verifiable R1 research surface for {asset}.">
  <link rel="canonical" href="https://structurevidence.org/{asset.lower()}.html">
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>
  {nav()}
  <main>
    <section class="hero"><div class="hero-copy"><p class="eyebrow">R1 Research Support</p><h1>{asset} Human-Verifiable Research Surface</h1><p class="lead">{esc(can['summary'])}</p></div></section>
    <section class="result-grid"><article class="card structural"><h2>Structural State</h2><p class="code big">{esc(can['structural_state_final'])}</p><p><span class="status">ENTITY ID: {esc(can['research_id'])}</span><span class="status">DECISION_USEFULNESS: NOT_ESTABLISHED</span></p></article><article class="card evidence"><h2>Evidence State</h2><p class="code big">{esc(can['evidence_state_final'])}</p><p><span class="status">RESEARCH STATUS: {esc(can['publication_status'])}</span><span class="status">SOURCE COVERAGE: {esc(can['source_coverage'])}</span><span class="status">MATERIAL INCONSISTENCY: {esc(can['material_inconsistency'])}</span><span class="status">LAST REVIEWED: {esc(can['last_reviewed'])}</span></p></article></section>
    <section><h2>1. Mechanism Judgment</h2><p>{esc(can['summary'])}</p></section>
    <section><h2>2. Supporting Observations</h2><ul>{''.join(obs_items)}</ul></section>
    <section><h2>3. Rival Hypotheses / ACH</h2><ul>{''.join(hyp_items)}</ul></section>
    <section><h2>4. Counter-Evidence</h2><ul>{''.join(counter_items)}</ul>{sol_conflict}</section>
    <section><h2>5. Evidence Gaps</h2><p>Source coverage is <code>{esc(can['source_coverage'])}</code>. Dependency groups: {esc(gap_text)}. This is a source-independence boundary, not a decision-usefulness upgrade.</p></section>
    <section><h2>6. Diff vs v0.1</h2><p>v0.1 structural label: <code>{esc(old['structural_state'])}</code>. R1 structural label: <code>{esc(can['structural_state_final'])}</code>. v0.1 evidence label: <code>{esc(old['evidence_state'])}</code>. R1 evidence label: <code>{esc(can['evidence_state_final'])}</code>. Supersession is <code>{esc(can['supersession_status'])}</code> because R1 narrowed or clarified the pilot claim while preserving access to the earlier method-pilot artifact.</p></section>
    <section><h2>Links</h2><p><a href="verify-r1.html#{asset.lower()}">Inspect R1 Research Chain</a></p><p><a href="research/digital-assets/batch-01-r1/{asset}/STRUCTURAL_DYNAMICS_REPORT_R1.md">R1 structural report</a></p><p><a href="research/digital-assets/batch-01-r1/{asset}/PUBLIC_EVIDENCE_RESEARCH_REPORT_R1.md">R1 evidence report</a></p><p><a href="research/digital-assets/batch-01-r1/{asset}/CANONICAL_RESEARCH_R1.json">Canonical JSON</a></p><p><a href="evidence-freeze/{R1}/{asset}/MANIFEST.json">Manifest</a></p><p><a href="research/digital-assets/{asset}/{asset}_STRUCTURAL_DYNAMICS_REPORT_v0.1.md">Previous Method Pilot v0.1</a></p></section>
  </main>
  {footer()}
</body>
</html>"""
    return html


def refinement_table() -> str:
    rows = []
    gap_by_asset = {
        "BNB": "Validator selection and source dependence forced narrowing from utility language to a burn-linked utility regime with control constraints.",
        "SOL": "Client-diversity evidence remains partly implementation-transition evidence, producing POTENTIAL_CONFLICT rather than a stronger alignment claim.",
        "TRX": "Transaction-count evidence supports stablecoin materiality, while resource economy and governance constraints prevent overclaiming full dominance.",
        "XLM": "Treasury and SDF mandate evidence remain material, while payments/RWA adoption does not independently displace foundation dependence.",
    }
    for asset in ASSETS:
        can = asset_data(asset)["canonical"]
        old = old_state(asset)
        rows.append(f"<tr><td><a href=\"../../../../{asset.lower()}.html\">{asset}</a></td><td>{esc(old['structural_state'])} / {esc(old['evidence_state'])}</td><td>{esc(can['structural_state_final'])} / {esc(can['evidence_state_final'])}</td><td>{esc(gap_by_asset.get(asset, 'SOURCE_GAP'))}</td><td>REFINED</td></tr>")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Batch01 R1 Refinement Table - StructEvidence</title><link rel="stylesheet" href="../../../../assets/style.css"></head><body>{nav().replace('href="', 'href="../../../../')}<main><section class="hero"><div class="hero-copy"><p class="eyebrow">Batch01 R1</p><h1>Refinement Table</h1><p class="lead">R1 comparison against v0.1 method-pilot labels. This is not ranking and does not establish decision usefulness.</p></div></section><section><div class="table-wrap"><table><thead><tr><th>Asset</th><th>v0.1 overclaim</th><th>R1 narrowed claim</th><th>Counter-evidence or gap that forced narrowing</th><th>Supersession</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section></main>{footer().replace('href="', 'href="../../../../').replace('src="', 'src="../../../../')}</body></html>"""


def verify_page() -> str:
    blocks = []
    required = [
        "OBSERVATION_REGISTRY.json", "CLAIM_REGISTRY.json", "HYPOTHESIS_REGISTRY.json", "COUNTER_EVIDENCE_SEARCH_LOG.json",
        "ECL_AXIS_ANALYSIS.md", "ECL_FINAL_SYNTHESIS.md", "BLIND_REVIEW_INPUT.json", "BLIND_REVIEW_OUTPUT.md",
        "AGREEMENT_DIVERGENCE_AUDIT.md",
    ]
    for asset in ASSETS:
        p = paths(asset)
        manifest = data = read_json(p["manifest"])
        can = read_json(p["canonical"])
        sums_path = p["freeze"] / "SHA256SUMS.txt"
        hashes = {}
        if sums_path.exists():
            for line in sums_path.read_text(encoding="utf-8").splitlines():
                digest, filename = line.split("  ", 1)
                hashes[filename] = digest
        gate_rows = []
        for name in required:
            exists = (p["freeze"] / name).exists()
            gate_rows.append(f"<tr><td>{esc(name)}</td><td>{'PASS' if exists else 'FAIL'}</td><td><a href=\"evidence-freeze/{R1}/{asset}/{esc(name)}\">evidence-freeze/{R1}/{asset}/{esc(name)}</a></td><td>{esc(hashes.get(name, 'GAP'))}</td></tr>")
        file_rows = []
        for name in manifest.get("files", []):
            digest = "EXPECTED_SELF_HASH_EXCLUSION" if name == "SHA256SUMS.txt" else hashes.get(name, "GAP")
            file_rows.append(f"<tr><td>{esc(name)}</td><td><a href=\"evidence-freeze/{R1}/{asset}/{esc(name)}\">artifact</a></td><td>{esc(digest)}</td></tr>")
        blocks.append(f"""<section id="{asset.lower()}"><h2>{asset}</h2><p><span class="status">producer_source: R1 derivation artifacts</span><span class="status">reviewer_artifact: BLIND_REVIEW_OUTPUT.md</span><span class="status">SEPARATION: FILENAME_ONLY</span><span class="status">Research Status: {esc(can['publication_status'])}</span><span class="status">Decision usefulness: NOT_ESTABLISHED</span></p><h3>Required Artifact Gates</h3><div class="table-wrap"><table><thead><tr><th>Artifact</th><th>Gate</th><th>Path</th><th>Hash</th></tr></thead><tbody>{''.join(gate_rows)}</tbody></table></div><h3>Manifest Artifact List</h3><div class="table-wrap"><table><thead><tr><th>Artifact</th><th>Path</th><th>Hash</th></tr></thead><tbody>{''.join(file_rows)}</tbody></table></div></section>""")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Batch01 R1 Verify - StructEvidence</title><link rel="stylesheet" href="assets/style.css"></head><body>{nav()}<main><section class="hero"><div class="hero-copy"><p class="eyebrow">Human Verify</p><h1>Batch01 R1 Research Chain</h1><p class="lead">Artifact gates rendered from R1 manifests and canonical JSON. Missing required artifacts render as FAIL.</p></div></section>{''.join(blocks)}</main>{footer()}</body></html>"""


def state_vocab() -> str:
    labels = {
        "BURN_LINKED_ECOSYSTEM_UTILITY_REGIME": ["issuance/burn", "settlement object", "governance dependence"],
        "EXECUTION_SCALE_WITH_PARTIAL_CLIENT_DIVERSITY": ["client/validator structure", "governance dependence"],
        "STABLECOIN_RESOURCE_SETTLEMENT_REGIME": ["settlement object", "governance dependence"],
        "SDF_TREASURY_DEPENDENT_PAYMENT_NETWORK": ["treasury dependence", "settlement object", "client/validator structure"],
    }
    mappings = "\n".join(f"- `{k}`: {', '.join(v)}" for k, v in labels.items())
    return f"""# StructEvidence State Vocabulary

## Structural State Axes
- issuance/burn
- settlement object
- governance dependence
- client/validator structure
- treasury dependence

New structural labels must register at least one axis before use. Future batches fail closed on free-form labels.

## Evidence State Enum
`ALIGNED | TEMPORAL_CHANGE | POTENTIAL_CONFLICT | UNRECONCILED | INSUFFICIENT`

## Supersession Enum
`UNCHANGED | REFINED | SUPERSEDED | WITHDRAWN`

## Current R1 Label Axis Map
{mappings}

These labels are not renamed in this commit. `R1 RESEARCH SUPPORT` identifies method version and publication status only; it is not evidence strength, ranking, rating or decision usefulness.
"""


def update_entities() -> None:
    for rel in [DOCS / "assets" / "entities.json", ROOT / "assets" / "entities.json"]:
        entities = read_json(rel)
        for item in entities:
            ticker = item.get("ticker")
            if ticker in ASSETS:
                item["human_verify_url"] = f"verify-r1.html#{ticker.lower()}"
                item["research_chain_url"] = f"verify-r1.html#{ticker.lower()}"
        rel.write_text(json.dumps(entities, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def update_front_office() -> None:
    cards = '<tr><td><a href="strategy-2026.html">Strategy</a></td><td>HYBRID_ACCUMULATION_MONETIZATION</td><td>SEMANTIC_TENSION_BUT_RECONCILABLE</td><td>Existing publication</td><td>NOT_ESTABLISHED</td></tr>'
    cards += "".join(f'<tr><td><a href="{a.lower()}.html">{a}</a></td><td>{esc(asset_data(a)["canonical"]["structural_state_final"])}</td><td>{esc(asset_data(a)["canonical"]["evidence_state_final"])}</td><td>{esc(asset_data(a)["canonical"]["publication_status"])}</td><td>{esc(asset_data(a)["canonical"]["decision_usefulness"])}</td></tr>' for a in ASSETS)
    digital = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Digital Assets - StructEvidence</title><link rel="stylesheet" href="assets/style.css"></head><body>{nav()}<main><section class="hero"><div class="hero-copy"><p class="eyebrow">Digital Assets</p><h1>Batch01 R1 Coverage Monitor</h1><p class="lead">Five covered entities are published: Strategy, BNB, SOL, TRX and XLM. The list is alphabetical by asset section and is not a ranking. Decision usefulness is not established.</p></div></section><section><h2>Demonstration Case</h2><p>SOL is the demonstration case for visible POTENTIAL_CONFLICT handling because execution-scale evidence and production client-diversity evidence remain distinct claims.</p></section><section><p><a href="research/digital-assets/batch-01-r1/REFINEMENT_TABLE.html">Open R1 Refinement Table</a> | <a href="verify-r1.html">Open Human Verify</a></p><div class="table-wrap"><table><thead><tr><th>Asset</th><th>Structural State</th><th>Evidence State</th><th>Research Status</th><th>Decision Usefulness</th></tr></thead><tbody>{cards}</tbody></table></div></section></main>{footer()}</body></html>"""
    for root in [ROOT, DOCS]:
        write(root / "digital-assets.html", digital)
        idx = root / "index.html"
        text = idx.read_text(encoding="utf-8")
        text = re.sub(r'(<p id="search-note" class="microcopy">).*?(</p>)', r'\1Coverage count: 5 covered entities. Decision usefulness not established. SOL demonstrates visible POTENTIAL_CONFLICT handling.\2', text)
        text = text.replace("Structural & Evidence Health Card", "Structural & Evidence Research Record")
        text = text.replace("HEALTH CARD != HEALTH SCORE", "NOT A SCORE OR RANKING")
        text = text.replace("View Full Audit", "View Research Record")
        coverage_section = f"""<section class="coverage-index">
  <h2>Covered Entities</h2>
  <p>Coverage is 5 entities; decision usefulness is not established. SOL is featured as the conflict demonstration case.</p>
  <p><a href="digital-assets.html">Digital Assets</a> | <a href="verify-r1.html">Human Verify</a> | <a href="research/digital-assets/batch-01-r1/REFINEMENT_TABLE.html">R1 Refinement Table</a></p>
  <div class="table-wrap"><table><thead><tr><th>Entity</th><th>Structural State</th><th>Evidence State</th><th>Research Status</th><th>Decision Usefulness</th></tr></thead><tbody>{cards}</tbody></table></div>
</section>"""
        if "coverage-index" not in text:
            text = text.replace('<section class="deliverables">', coverage_section + '\n<section class="deliverables">')
        idx.write_text(text, encoding="utf-8")
        research = root / "research.html"
        text = research.read_text(encoding="utf-8")
        marker = "</tbody></table>"
        links = '<tr><td>2026-09-09</td><td>Batch01 R1</td><td>Human verification</td><td>NOT_APPLICABLE</td><td>NOT_APPLICABLE</td><td><a href="verify-r1.html">Verify</a> | <a href="research/digital-assets/batch-01-r1/REFINEMENT_TABLE.html">Refinement Table</a></td></tr>'
        if "REFINEMENT_TABLE.html" not in text:
            text = text.replace(marker, links + marker)
        research.write_text(text, encoding="utf-8")


def main() -> None:
    write(DOCS / "STATE_VOCAB.md", state_vocab())
    for asset in ASSETS:
        html = asset_page(asset)
        write(ROOT / f"{asset.lower()}.html", html)
        shutil.copy2(ROOT / f"{asset.lower()}.html", DOCS / f"{asset.lower()}.html")
    table = refinement_table()
    write(ROOT / "research" / "digital-assets" / "batch-01-r1" / "REFINEMENT_TABLE.html", table)
    write(DOCS / "research" / "digital-assets" / "batch-01-r1" / "REFINEMENT_TABLE.html", table)
    verify = verify_page()
    write(ROOT / "verify-r1.html", verify)
    shutil.copy2(ROOT / "verify-r1.html", DOCS / "verify-r1.html")
    update_entities()
    update_front_office()


if __name__ == "__main__":
    main()
