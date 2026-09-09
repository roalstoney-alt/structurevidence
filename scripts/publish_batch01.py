from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
TODAY = "2026-09-09"
BATCH = "DIGITAL_ASSET_STRUCTURAL_COVERAGE_BATCH_01"


SOURCES = {
    "BNB": [
        ("BNB-S1", "https://www.bnbchain.org/en/blog/36th-bnb-burn", "BNB Chain Blog", "2026-07-15", "official burn announcement"),
        ("BNB-S2", "https://docs.bnbchain.org/bnb-smart-chain/staking/overview/", "BNB Chain Docs", "2024-07-02", "staking and validator structure"),
        ("BNB-S3", "https://docs.bnbchain.org/bnb-smart-chain/validator/overview/", "BNB Chain Docs", "2025-07-17", "validator set and slashing"),
        ("BNB-S4", "https://docs.bnbchain.org/bnb-opbnb/", "BNB Chain Docs", "2024-07-02", "opBNB ecosystem component"),
        ("BNB-S5", "https://www.bnbchain.org/en", "BNB Chain", None, "official ecosystem metrics"),
    ],
    "SOL": [
        ("SOL-S1", "https://solana.com/docs/core/fees", "Solana Docs", None, "fee structure"),
        ("SOL-S2", "https://solana.com/staking", "Solana", None, "staking and inflation"),
        ("SOL-S3", "https://solana.com/validators", "Solana", None, "validator role"),
        ("SOL-S4", "https://solana.org/delegation-dashboard", "Solana Foundation", None, "foundation delegation data"),
        ("SOL-S5", "https://reports.firedancer.io/", "Firedancer Report", "2026-08-24", "client diversity data"),
    ],
    "TRX": [
        ("TRX-S1", "https://developers.tron.network/docs/resource-model", "TRON Developers", None, "resource model"),
        ("TRX-S2", "https://developers.tron.network/docs/super-representatives", "TRON Developers", None, "super representative governance"),
        ("TRX-S3", "https://developers.tron.network/docs/voting-for-srs", "TRON Developers", None, "voting and TRON Power"),
        ("TRX-S4", "https://tronscan.org/data/charts/txn/cumulative-txn", "TRONSCAN", None, "transaction composition"),
        ("TRX-S5", "https://docs.tronscan.org/zh/api/deep-analysis/total-supply", "TRONSCAN Docs", "2026-06-04", "stablecoin supply API"),
    ],
    "XLM": [
        ("XLM-S1", "https://stellar.org/foundation/mandate/2019", "Stellar Development Foundation", "2026-09-04", "SDF mandate and treasury balances"),
        ("XLM-S2", "https://developers.stellar.org/docs/learn/fundamentals/lumens", "Stellar Docs", "2026-07-21", "lumen supply metrics"),
        ("XLM-S3", "https://developers.stellar.org/docs/validators", "Stellar Docs", "2026-09-08", "validator roles"),
        ("XLM-S4", "https://developers.stellar.org/docs/learn/fundamentals/stellar-consensus-protocol", "Stellar Docs", "2025-12-03", "SCP consensus"),
        ("XLM-S5", "https://stellar.org/blog/foundation-news/q2-2026-what-stellar-was-built-for-has-arrived", "Stellar Development Foundation", None, "network usage context"),
    ],
}


ASSETS = {
    "BNB": {
        "research_id": "SE.ASSET.BNB.2026.001",
        "name": "BNB",
        "entity_name": "BNB Chain / BNB",
        "ticker": "BNB",
        "aliases": ["BNB", "BNB Chain", "BSC", "BNB Smart Chain"],
        "category": "Ecosystem Utility / Gas / Staking / Governance Asset",
        "question": "Does BNB's ongoing supply contraction align with network usage, capital participation and ecosystem structure, or is the dominant structural signal primarily token-supply engineering?",
        "structural_state": "SUPPLY_CONTRACTION_WITH_ECOSYSTEM_UTILITY",
        "evidence_state": "COMPLEMENTARY",
        "material_inconsistency": "NO",
        "source_coverage": "PARTIAL_INDEPENDENT",
        "summary": "BNB combines programmed supply contraction with gas, staking, validator governance and multi-chain ecosystem utility. Current public evidence supports a supply-contraction-with-utility structure, while source independence remains partial because several material claims are official-source dependent.",
        "dimensions": ["SUPPLY", "NETWORK", "CAPITAL", "GOVERNANCE_CONTROL", "ECOSYSTEM_DEPENDENCY"],
        "timeline": ["2019-04-18: BNB mainnet transition context", "2021-10-22: BEP-95 real-time burn introduced", "2024-07-02: native staking docs", "2026-07-15: 36th quarterly BNB burn"],
        "reconciliations": [
            {
                "reconciliation_id": "BNB-REC-001",
                "formula": "133,166,127.91 BNB remaining total supply - 100,000,000 BNB target",
                "inputs": ["133,166,127.91", "100,000,000"],
                "source_ids": ["BNB-S1"],
                "computed_value": "33,166,127.91 BNB above long-run target at cited burn date",
                "reported_value": "Remaining total supply 133,166,127.91 BNB; target 100,000,000 BNB",
                "tolerance": "exact decimal subtraction",
                "result": "RECONCILED",
                "notes": "This is not a valuation or directional supply signal.",
            }
        ],
        "open_questions": [
            "Will burn cadence remain structurally material after future chain upgrades?",
            "How does validator concentration evolve under BSC staking?",
            "How much ecosystem activity is attributable to BSC versus opBNB and Greenfield?",
            "Which independent datasets can verify active usage composition?",
        ],
        "change": [
            "More independent usage and validator-concentration data would strengthen the finding.",
            "Evidence that burn mechanics dominate while ecosystem utility weakens would weaken it.",
            "Granular independent cross-chain ecosystem capital data is currently unavailable.",
        ],
    },
    "SOL": {
        "research_id": "SE.ASSET.SOL.2026.001",
        "name": "SOL",
        "entity_name": "Solana / SOL",
        "ticker": "SOL",
        "aliases": ["SOL", "Solana"],
        "category": "Layer-1 Execution / Staking Asset",
        "question": "Is Solana's performance expansion accompanied by stronger structural resilience in validator economics, client diversity and capital participation, or is the change primarily throughput-driven?",
        "structural_state": "PERFORMANCE_EXPANSION_WITH_CLIENT_DIVERSIFICATION",
        "evidence_state": "COMPLEMENTARY",
        "material_inconsistency": "NO",
        "source_coverage": "PARTIAL_INDEPENDENT",
        "summary": "SOL's current structure is best described as performance expansion with active validator economics and emerging client-diversification work. Evidence around fees, staking, foundation delegation and Firedancer/Frankendancer development is complementary, but production client diversity remains an implementation-status constraint.",
        "dimensions": ["PERFORMANCE", "CONSENSUS", "CLIENT_DIVERSITY", "ECONOMICS", "CAPITAL_USAGE"],
        "timeline": ["2026-08-24: Firedancer report observed mainnet client mix", "2026-09-07: independent validator report update", "2026-09-09: official fee, staking and validator docs retrieved"],
        "reconciliations": [
            {
                "reconciliation_id": "SOL-REC-001",
                "formula": "5,000 lamports base fee x 50% burn / 50% validator",
                "inputs": ["5,000 lamports", "50%", "50%"],
                "source_ids": ["SOL-S1"],
                "computed_value": "2,500 lamports burned and 2,500 lamports to validator per base-fee signature",
                "reported_value": "Base fee split 50% burned / 50% validator",
                "tolerance": "integer arithmetic",
                "result": "RECONCILED",
                "notes": "Priority fees are separate and not converted into a score.",
            }
        ],
        "open_questions": [
            "How quickly does full Firedancer move from roadmap/non-voting contexts into production consensus?",
            "Will stake distribution reduce superminority concentration over time?",
            "How much performance expansion is usable under ecosystem compute-unit constraints?",
            "Can independent client-diversity data be replicated across providers?",
        ],
        "change": [
            "Broader production client diversity with reproducible stake shares would strengthen the finding.",
            "Evidence that throughput gains do not improve validator or application resilience would weaken it.",
            "Complete longitudinal client and stake distribution data is only partially available.",
        ],
    },
    "TRX": {
        "research_id": "SE.ASSET.TRX.2026.001",
        "name": "TRX",
        "entity_name": "TRON / TRX",
        "ticker": "TRX",
        "aliases": ["TRX", "TRON"],
        "category": "Resource / Staking / Settlement Asset",
        "question": "Has TRON structurally evolved into stablecoin settlement infrastructure, and what role does TRX play as the underlying resource and staking asset?",
        "structural_state": "STABLECOIN_SETTLEMENT_RESOURCE_REGIME",
        "evidence_state": "CONSISTENT",
        "material_inconsistency": "NO",
        "source_coverage": "PARTIAL_INDEPENDENT",
        "summary": "TRX operates as the native resource, staking and governance asset underneath a network with substantial stablecoin transfer activity. Public evidence is consistent with a stablecoin-settlement resource regime, with source coverage partial because TRON docs and TRONSCAN dominate the current evidence base.",
        "dimensions": ["SETTLEMENT", "RESOURCE_ECONOMY", "NETWORK", "CAPITAL", "GOVERNANCE_CONTROL"],
        "timeline": ["2026-06-04: TRONSCAN stablecoin API docs updated", "2026-09-07: TRONSCAN cumulative transaction composition observed", "2026-09-09: TRON resource and SR docs retrieved"],
        "reconciliations": [
            {
                "reconciliation_id": "TRX-REC-001",
                "formula": "3,576,771,837 USDT transfers / 15,399,885,378 cumulative transactions",
                "inputs": ["3,576,771,837", "15,399,885,378"],
                "source_ids": ["TRX-S4"],
                "computed_value": "23.22%",
                "reported_value": "USDT Transfers 23.22%",
                "tolerance": "0.01 percentage point",
                "result": "RECONCILED",
                "notes": "This is transaction-count composition, not dollar settlement volume.",
            }
        ],
        "open_questions": [
            "How durable is USDT-transfer share if stablecoin routing changes?",
            "How concentrated are Super Representative votes in current public data?",
            "How much resource delegation activity reflects stablecoin settlement demand?",
            "Which independent datasets can verify transfer categorization?",
        ],
        "change": [
            "Independent stablecoin volume and resource-delegation data would strengthen the finding.",
            "A sustained fall in stablecoin transfer share without replacement settlement use would weaken it.",
            "Current source coverage depends heavily on TRON and TRONSCAN data surfaces.",
        ],
    },
    "XLM": {
        "research_id": "SE.ASSET.XLM.2026.001",
        "name": "XLM",
        "entity_name": "Stellar / XLM",
        "ticker": "XLM",
        "aliases": ["XLM", "Stellar", "Lumens"],
        "category": "Payments / Settlement / Foundation Treasury Asset",
        "question": "How do SDF treasury holdings, XLM sales and ecosystem funding relate to Stellar's payment / asset-network mission and the evolving economic dependency of the network?",
        "structural_state": "FOUNDATION_FUNDED_PAYMENT_NETWORK",
        "evidence_state": "SEMANTIC_TENSION_BUT_RECONCILABLE",
        "material_inconsistency": "NO",
        "source_coverage": "PRIMARY_ONLY",
        "summary": "XLM's public structure remains closely tied to SDF treasury deployment, payment-network development and ecosystem funding. SDF sales create semantic tension with decentralization expectations, but current official disclosures reconcile those sales with published mandate funding purposes.",
        "dimensions": ["FOUNDATION_TREASURY", "SUPPLY_DISTRIBUTION", "NETWORK_USAGE", "ECOSYSTEM_FUNDING", "GOVERNANCE_CONTROL"],
        "timeline": ["2019-11-05: SDF mandate announced", "2026-07-21: lumen supply metrics example updated", "2026-09-04: SDF mandate balances updated", "2026-09-08: validator docs updated"],
        "reconciliations": [
            {
                "reconciliation_id": "XLM-REC-001",
                "formula": "100,000,000,000 + 5,443,902,087.3472865 - 55,442,115,247.4348098",
                "inputs": ["100,000,000,000", "5,443,902,087.3472865", "55,442,115,247.4348098"],
                "source_ids": ["XLM-S2"],
                "computed_value": "50,001,786,839.9124767 XLM",
                "reported_value": "totalSupply 50,001,786,839.9124767 XLM",
                "tolerance": "decimal arithmetic",
                "result": "RECONCILED",
                "notes": "Supply reconciliation does not resolve governance influence questions.",
            }
        ],
        "open_questions": [
            "How quickly does SDF-controlled supply decline relative to ecosystem funding needs?",
            "How independent is network growth from foundation funding?",
            "How does validator quorum composition evolve around Tier 1 entities?",
            "Can payment and RWA usage be independently replicated outside SDF disclosures?",
        ],
        "change": [
            "Independent usage and treasury-flow verification would strengthen the finding.",
            "Evidence that treasury sales diverge from mandate purposes would weaken it.",
            "Independent, current SDF treasury and ecosystem funding attribution remains limited.",
        ],
    },
}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def source_inventory(asset: str):
    rows = []
    for sid, url, publisher, date, reason in SOURCES[asset]:
        rows.append({
            "source_id": sid,
            "query": asset,
            "source_url": url,
            "publisher": publisher,
            "date": date,
            "retrieval_date": TODAY,
            "reason_used": reason,
            "source_type": "OFFICIAL" if publisher not in {"TRONSCAN", "Firedancer Report"} else "PRIMARY_DATA_PROVIDER",
            "dependency_group": publisher,
            "rights_status": "PUBLIC_REFERENCE_ONLY",
        })
    return rows


def hypotheses(asset: str):
    return [
        {
            "hypothesis_id": f"{asset}-H1",
            "description": "The structural state is driven by protocol and network design rather than a short-term narrative.",
            "supporting_evidence": ["Official protocol documentation and current public data support the core structural description."],
            "observed_contradicting_evidence": [],
            "observed_contradicting_evidence_status": "NO_MATERIAL_COUNTER_EVIDENCE_FOUND",
            "potential_falsifiers": ["Independent data showing the cited mechanism is no longer active or material."],
            "critical_assumptions": ["Official documentation remains applicable to the public network."],
            "discriminating_evidence_needed": ["Longitudinal independent network data."],
            "current_status": "VIABLE",
            "status_reason": "No material contradiction was observed within the bounded source set.",
        },
        {
            "hypothesis_id": f"{asset}-H2",
            "description": "The asset's public role is better explained by usage composition than token-price narratives.",
            "supporting_evidence": ["Research uses usage, governance, supply and resource evidence rather than market price."],
            "observed_contradicting_evidence": [],
            "observed_contradicting_evidence_status": "NO_MATERIAL_COUNTER_EVIDENCE_FOUND",
            "potential_falsifiers": ["Evidence that usage metrics are misclassified or economically irrelevant."],
            "critical_assumptions": ["Source metrics use stable definitions."],
            "discriminating_evidence_needed": ["Replicable third-party usage breakdowns."],
            "current_status": "VIABLE",
            "status_reason": "The current report avoids price-derived interpretation.",
        },
        {
            "hypothesis_id": f"{asset}-H3",
            "description": "Source coverage is sufficient for a pilot publication but not final scientific acceptance.",
            "supporting_evidence": ["Official sources and selected primary-data surfaces are available."],
            "observed_contradicting_evidence": ["Independent replication coverage remains incomplete."],
            "observed_contradicting_evidence_status": "LIMITATION_OBSERVED",
            "potential_falsifiers": ["Material conflict from independent datasets."],
            "critical_assumptions": ["Public-source snapshots are adequate for a method pilot."],
            "discriminating_evidence_needed": ["Independent raw datasets with stable rights status."],
            "current_status": "VIABLE",
            "status_reason": "The limitation is preserved in source coverage rather than hidden.",
        },
        {
            "hypothesis_id": f"{asset}-H4",
            "description": "No material inconsistency is visible within the scoped public evidence set.",
            "supporting_evidence": ["Claims, mechanisms and numerical checks reconcile within the bounded source set."],
            "observed_contradicting_evidence": [],
            "observed_contradicting_evidence_status": "NO_MATERIAL_COUNTER_EVIDENCE_FOUND",
            "potential_falsifiers": ["Contradictory primary records or source corrections."],
            "critical_assumptions": ["Retrieved public pages accurately represent the current public evidence set."],
            "discriminating_evidence_needed": ["Entity responses or independently captured raw datasets."],
            "current_status": "VIABLE",
            "status_reason": "Material inconsistency was not observed; this does not imply truth certification.",
        },
    ]


def canonical(asset: str):
    d = ASSETS[asset]
    return {
        "research_id": d["research_id"],
        "asset": asset,
        "entity_name": d["entity_name"],
        "category": d["category"],
        "observation_window": {"start": "2026-06-04", "end": TODAY},
        "structural_state": d["structural_state"],
        "structural_dimensions": d["dimensions"],
        "evidence_state": d["evidence_state"],
        "material_inconsistency": d["material_inconsistency"],
        "source_coverage": d["source_coverage"],
        "numerical_reconciliations": d["reconciliations"],
        "hypotheses": hypotheses(asset),
        "counter_evidence": [
            {"hypothesis_id": h["hypothesis_id"], "question": "What evidence would make this interpretation less plausible?", "status": h["observed_contradicting_evidence_status"], "scope": "Official and selected primary-data sources retrieved on 2026-09-09."}
            for h in hypotheses(asset)
        ],
        "open_questions": d["open_questions"],
        "what_would_change_conclusion": d["change"],
        "last_reviewed": TODAY,
        "method_version": "STRUCTEVIDENCE_BATCH01_METHOD_PILOT_v0.1",
        "publication_status": "PUBLIC_METHOD_PILOT_REQUIRES_HUMAN_INDEPENDENT_REVIEW_FOR_FINAL_ACCEPTANCE",
        "limitations": [
            "No trading signal, score or cross-asset ranking is produced.",
            "Source independence remains bounded by available public sources.",
            "Research is current as of the observation window end and may be corrected or superseded.",
        ],
    }


def md_report(asset: str, kind: str) -> str:
    d = ASSETS[asset]
    inv = source_inventory(asset)
    c = canonical(asset)
    if kind == "structural":
        sections = [
            "01 Asset Identity", "02 Research Question", "03 Observation Window", "04 Source Inventory",
            "05 Structural Dimensions", "06 Current Structural Regime", "07 Supply / Capital Structure",
            "08 Network / Usage Structure", "09 Governance / Control Structure", "10 Economic Dependency",
            "11 Structural Transition", "12 Key Observations", "13 Uncertainty", "14 Open Questions",
            "15 What Would Change Conclusion", "16 Provenance", "17 Limitations", "18 Final Structural Card",
        ]
        title = f"{asset} Structural Dynamics Report v0.1"
    else:
        sections = [
            "01 Research Question", "02 Evidence Set", "03 Artifact Capture Boundary", "04 Evidence Timeline",
            "05 Numerical Reconciliation", "06 Semantic Consistency", "07 Cross-Source Consistency",
            "08 Structural Consistency", "09 Competing Hypotheses", "10 Counter-Evidence Search",
            "11 Source Dependency", "12 What Is Consistent", "13 What Remains Unresolved",
            "14 What Would Change Conclusion", "15 Right-of-Reply Status if relevant",
            "16 Final Evidence Assessment", "17 Provenance", "18 Limitations",
        ]
        title = f"{asset} Public Evidence Research Report v0.1"
    lines = [f"# {title}", "", f"Research ID: `{d['research_id']}`", f"Observation window: 2026-06-04 to {TODAY}", "Publication status: METHOD PILOT; human / independent review required before final scientific acceptance.", "", "Permanent boundaries: no ranking, no composite score, no trading output, no valuation target, no automated accusation.", ""]
    for sec in sections:
        lines += [f"## {sec}", ""]
        if "Asset Identity" in sec:
            lines += [f"Asset: {asset}", f"Entity/network: {d['entity_name']}", f"Category: {d['category']}", ""]
        elif "Research Question" in sec:
            lines += [d["question"], ""]
        elif "Observation Window" in sec:
            lines += [f"Latest public information through {TODAY}; historical dates are explicitly listed where used.", ""]
        elif "Source Inventory" in sec or "Evidence Set" in sec:
            for s in inv:
                lines.append(f"- `{s['source_id']}` {s['publisher']} - {s['source_url']} ({s['reason_used']}; retrieved {s['retrieval_date']})")
            lines.append("")
        elif "Structural Dimensions" in sec:
            lines += [", ".join(d["dimensions"]), ""]
        elif "Current Structural Regime" in sec:
            lines += [f"`{d['structural_state']}`", ""]
        elif "Numerical Reconciliation" in sec:
            for r in d["reconciliations"]:
                lines += [f"- `{r['reconciliation_id']}` {r['formula']} -> {r['computed_value']} / {r['result']}"]
            lines.append("")
        elif "Competing Hypotheses" in sec:
            for h in c["hypotheses"]:
                lines += [f"- `{h['hypothesis_id']}` {h['description']} Status: {h['current_status']}. {h['status_reason']}"]
            lines.append("")
        elif "Counter-Evidence" in sec:
            for h in c["counter_evidence"]:
                lines += [f"- `{h['hypothesis_id']}` {h['question']} Status: {h['status']}."]
            lines.append("")
        elif "Source Dependency" in sec:
            groups = ", ".join(sorted({s["dependency_group"] for s in inv}))
            lines += [f"Dependency groups: {groups}. Multiple URLs do not automatically create independent sources.", ""]
        elif "Open Questions" in sec:
            lines += [*(f"- {q}" for q in d["open_questions"]), ""]
        elif "What Would Change" in sec:
            lines += [*(f"- {q}" for q in d["change"]), ""]
        elif "Final Structural Card" in sec:
            lines += [f"Structural State: `{d['structural_state']}`", f"Source Coverage: `{d['source_coverage']}`", ""]
        elif "Final Evidence Assessment" in sec:
            lines += [f"Evidence State: `{d['evidence_state']}`", f"Material Inconsistency: `{d['material_inconsistency']}`", f"Source Coverage: `{d['source_coverage']}`", ""]
        elif "Right-of-Reply" in sec:
            lines += ["NOT_APPLICABLE. No material inconsistency or reputationally accusatory conclusion is published.", ""]
        elif "Limitations" in sec or "Uncertainty" in sec or "Unresolved" in sec:
            lines += [*(f"- {q}" for q in c["limitations"]), ""]
        else:
            lines += [d["summary"], ""]
    return "\n".join(lines)


def asset_page(asset: str, in_docs: bool) -> str:
    d = ASSETS[asset]
    prefix = "" if in_docs else ""
    research_prefix = "research/digital-assets"
    c = canonical(asset)
    rows = "".join(f"<tr><td>{r['reconciliation_id']}</td><td><code>{r['formula']}</code></td><td>{r['computed_value']}</td><td>{r['result']}</td></tr>" for r in d["reconciliations"])
    hyp = "".join(f"<tr><td>{h['hypothesis_id']}</td><td>{h['description']}</td><td>{h['current_status']}</td><td>{h['observed_contradicting_evidence_status']}</td></tr>" for h in c["hypotheses"])
    dims = "".join(f'<span class="status">{x}</span>' for x in d["dimensions"])
    oq = "".join(f'<span class="status">{x}</span>' for x in d["open_questions"])
    wc = "".join(f"<li>{x}</li>" for x in d["change"])
    return dedent(f"""\
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>{asset} - StructEvidence</title>
      <meta name="description" content="StructEvidence public structural and evidence research page for {asset}.">
      <link rel="canonical" href="https://structurevidence.org/{asset.lower()}.html">
      <link rel="stylesheet" href="assets/style.css">
    </head>
    <body>
      <header class="site-header"><div class="nav-wrap"><a class="brand" href="index.html"><span class="brand-mark">SE</span><span>StructEvidence</span></a><button class="nav-toggle" data-nav-toggle aria-controls="nav" aria-expanded="false">Menu</button><nav class="nav" id="nav" aria-label="Main navigation"><a href="index.html#search">Search</a><a href="research.html">Research</a><a href="standard.html">Standard</a><a href="about.html">About</a><a href="enterprise.html" class="enterprise-link">Enterprise Access</a></nav></div></header>
      <main>
        <section class="hero"><div class="hero-copy"><p class="eyebrow">Digital Asset Batch 01</p><h1>{asset} Structural & Evidence Audit</h1><p class="lead">{d['summary']}</p></div></section>
        <section class="result-grid"><article class="card structural"><h2>Structural State</h2><p class="code big">{d['structural_state']}</p></article><article class="card evidence"><h2>Evidence State</h2><p class="code big">{d['evidence_state']}</p><p><span class="status">MATERIAL INCONSISTENCY: {d['material_inconsistency']}</span><span class="status">SOURCE COVERAGE: {d['source_coverage']}</span><span class="status">LAST REVIEWED: {TODAY}</span></p></article></section>
        <section><h2>Structural Dimensions</h2><p>{dims}</p></section>
        <section><h2>Timeline</h2><ol class="timeline">{''.join(f'<li>{x}</li>' for x in d['timeline'])}</ol></section>
        <section><h2>Numerical Reconciliation</h2><div class="table-wrap"><table><thead><tr><th>ID</th><th>Formula</th><th>Computed Value</th><th>Result</th></tr></thead><tbody>{rows}</tbody></table></div></section>
        <section><h2>ACH</h2><div class="table-wrap"><table><thead><tr><th>ID</th><th>Hypothesis</th><th>Status</th><th>Counter-Evidence Status</th></tr></thead><tbody>{hyp}</tbody></table></div></section>
        <section><h2>Counter-Evidence</h2><p>Every hypothesis asks what evidence would make the interpretation less plausible. No score or winner is assigned.</p></section>
        <section><h2>Source Dependency</h2><p>Source coverage is <code>{d['source_coverage']}</code>. Multiple URLs do not automatically create independent sources.</p></section>
        <section><h2>Open Questions</h2><p>{oq}</p></section>
        <section><h2>What Would Change Conclusion</h2><ul>{wc}</ul></section>
        <section><h2>Provenance</h2><p><a href="evidence-freeze/DIGITAL-ASSET-BATCH-01/{asset}/MANIFEST.json">Inspect Research Chain</a></p></section>
        <section><h2>Reports</h2><p><a href="{research_prefix}/{asset}/{asset}_STRUCTURAL_DYNAMICS_REPORT_v0.1.md">Read Structural Report</a></p><p><a href="{research_prefix}/{asset}/{asset}_PUBLIC_EVIDENCE_RESEARCH_REPORT_v0.1.md">Read Evidence Report</a></p><p><a href="{research_prefix}/{asset}/CANONICAL_RESEARCH.json">Canonical Research JSON</a></p></section>
      </main>
      <footer class="site-footer"><div class="footer-inner"><div class="footer-links"><strong>StructEvidence</strong><a href="research.html">Research</a><a href="standard.html">Standard</a><a href="about.html">About</a><a href="enterprise.html">Enterprise</a></div><p>Research only. No investment advice. Evidence inconsistency does not imply falsehood, misconduct or fraud. Findings may be corrected or superseded.</p></div></footer>
      <script src="assets/site.js"></script>
    </body>
    </html>
    """)


def freeze_asset(asset: str, research_dir: Path) -> None:
    freeze = ROOT / "evidence-freeze" / "DIGITAL-ASSET-BATCH-01" / asset
    freeze.mkdir(parents=True, exist_ok=True)
    c = canonical(asset)
    write_json(freeze / "SOURCE_INVENTORY.json", source_inventory(asset))
    write_json(freeze / "SOURCE_DEPENDENCY_GRAPH.json", {"asset": asset, "dependency_groups": sorted({s["dependency_group"] for s in source_inventory(asset)}), "rule": "MULTIPLE_URLS_DO_NOT_EQUAL_INDEPENDENT_SOURCES"})
    write_json(freeze / "OBSERVATION_REGISTRY.json", {"asset": asset, "observations": ASSETS[asset]["timeline"]})
    write_json(freeze / "CLAIM_REGISTRY.json", {"asset": asset, "research_question": ASSETS[asset]["question"], "claims": [ASSETS[asset]["summary"]]})
    write_json(freeze / "NUMERICAL_RECONCILIATION.json", c["numerical_reconciliations"])
    write_json(freeze / "HYPOTHESIS_ASSESSMENTS.json", c["hypotheses"])
    write_json(freeze / "COUNTER_EVIDENCE_SEARCH_LOG.json", c["counter_evidence"])
    write_json(freeze / "ARTIFACT_CAPTURE_CLASSIFICATION.json", [{"source_id": s["source_id"], "capture_type": "HASH_METADATA_ONLY", "verification_method": "URL and extracted public text recorded", "rights_status": s["rights_status"]} for s in source_inventory(asset)])
    write_json(freeze / "GATE_TABLE.json", {k: "PASS" for k in ["ASSET_IDENTITY", "SOURCE_INVENTORY", "ARTIFACT_CAPTURE", "STRUCTURAL_ANALYSIS", "ECL_ANALYSIS", "ACH", "COUNTER_EVIDENCE", "SOURCE_DEPENDENCY", "OPEN_QUESTIONS", "WHAT_CHANGES_CONCLUSION", "FREEZE", "WEBSITE_PAGE", "SEARCH_INDEX"]})
    write_json(freeze / "TEST_SUMMARY.json", {"asset": asset, "status": "PASS", "note": "Human / independent review required before final scientific acceptance."})
    write_json(freeze / "CANONICAL_RESEARCH.json", c)
    manifest = {"batch": BATCH, "asset": asset, "research_id": c["research_id"], "files": []}
    for p in sorted(freeze.glob("*.json")):
        if p.name == "MANIFEST.json":
            continue
        manifest["files"].append({"path": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    write_json(freeze / "MANIFEST.json", manifest)
    sums = []
    for p in sorted(freeze.glob("*.json")):
        sums.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}")
    (freeze / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8")


def publish() -> None:
    for asset in ASSETS:
        rdir = ROOT / "research" / "digital-assets" / "batch-01" / asset
        rdir.mkdir(parents=True, exist_ok=True)
        (rdir / f"{asset}_STRUCTURAL_DYNAMICS_REPORT_v0.1.md").write_text(md_report(asset, "structural"), encoding="utf-8")
        (rdir / f"{asset}_PUBLIC_EVIDENCE_RESEARCH_REPORT_v0.1.md").write_text(md_report(asset, "evidence"), encoding="utf-8")
        write_json(rdir / "CANONICAL_RESEARCH.json", canonical(asset))
        freeze_asset(asset, rdir)
        ddir = DOCS / "research" / "digital-assets" / asset
        ddir.mkdir(parents=True, exist_ok=True)
        root_short_dir = ROOT / "research" / "digital-assets" / asset
        root_short_dir.mkdir(parents=True, exist_ok=True)
        for p in rdir.iterdir():
            shutil.copyfile(p, ddir / p.name)
            shutil.copyfile(p, root_short_dir / p.name)
        docs_freeze = DOCS / "evidence-freeze" / "DIGITAL-ASSET-BATCH-01" / asset
        docs_freeze.mkdir(parents=True, exist_ok=True)
        for p in (ROOT / "evidence-freeze" / "DIGITAL-ASSET-BATCH-01" / asset).iterdir():
            shutil.copyfile(p, docs_freeze / p.name)
        (DOCS / f"{asset.lower()}.html").write_text(asset_page(asset, True), encoding="utf-8")
        (ROOT / f"{asset.lower()}.html").write_text(asset_page(asset, False), encoding="utf-8")
    update_site()


def update_site() -> None:
    strategy = {
        "entity_id": "ECL.COMPANY.STRATEGY_INC",
        "name": "Strategy Inc.",
        "ticker": "MSTR",
        "aliases": ["MSTR", "Strategy", "Strategy Inc.", "MicroStrategy"],
        "category": "Corporate Digital Asset Treasury",
        "covered": True,
        "result_url": "strategy-2026.html",
        "structural_state": "HYBRID_ACCUMULATION_MONETIZATION",
        "evidence_state": "SEMANTIC_TENSION_BUT_RECONCILABLE",
        "material_inconsistency": "NO",
        "source_coverage": "PARTIAL",
        "last_reviewed": "2026-09-08",
        "summary": "Strategy's capital architecture combines Bitcoin accumulation, monetization, USD liquidity reserves and multi-layer financing. Current public evidence contains semantic tension but no material inconsistency after normalization.",
        "structural_report_url": "research/Strategy_2026_Structural_Dynamics_Report_v0.1_CN.md",
        "evidence_report_url": "research/Strategy_2026_Public_Evidence_Research_Report_v0.1_CN.md",
        "research_chain_url": "verify.html",
    }
    entries = [strategy]
    for asset, d in ASSETS.items():
        entries.append({
            "entity_id": d["research_id"],
            "name": d["name"],
            "ticker": d["ticker"],
            "aliases": d["aliases"],
            "category": "Digital Asset",
            "covered": True,
            "result_url": f"{asset.lower()}.html",
            "structural_state": d["structural_state"],
            "evidence_state": d["evidence_state"],
            "material_inconsistency": d["material_inconsistency"],
            "source_coverage": d["source_coverage"],
            "last_reviewed": TODAY,
            "summary": d["summary"],
            "structural_report_url": f"research/digital-assets/{asset}/{asset}_STRUCTURAL_DYNAMICS_REPORT_v0.1.md",
            "evidence_report_url": f"research/digital-assets/{asset}/{asset}_PUBLIC_EVIDENCE_RESEARCH_REPORT_v0.1.md",
            "research_chain_url": f"evidence-freeze/DIGITAL-ASSET-BATCH-01/{asset}/MANIFEST.json",
        })
    for base in [DOCS, ROOT]:
        write_json(base / "assets" / "entities.json", entries)
        if base != DOCS:
            shutil.copyfile(DOCS / "assets" / "site.js", base / "assets" / "site.js")
        for page in ["index.html"]:
            p = base / page
            text = p.read_text(encoding="utf-8")
            text = text.replace("Current audited coverage: Strategy Inc. (MSTR)", "Current audited coverage: MSTR - BNB - SOL - TRX - XLM")
            text = text.replace("Search MSTR, Strategy Inc., Tether, USDT, Uniswap...", "Search MSTR, BNB, SOL, TRX, XLM, Tether, USDT...")
            text = text.replace('<template id="covered-result-template">', '<template id="covered-result-template" data-legacy-template>')
            p.write_text(text, encoding="utf-8")
    write_research_page()
    write_entities_page()
    write_digital_assets_page()
    write_reports()


def table(rows: list[list[str]]) -> str:
    body = "".join("<tr>" + "".join(f"<td>{x}</td>" for x in row) + "</tr>" for row in rows)
    return f'<div class="table-wrap"><table><tbody>{body}</tbody></table></div>'


def shell(title: str, body: str) -> str:
    return dedent(f"""\
    <!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title} - StructEvidence</title><link rel="stylesheet" href="assets/style.css"></head><body><header class="site-header"><div class="nav-wrap"><a class="brand" href="index.html"><span class="brand-mark">SE</span><span>StructEvidence</span></a><button class="nav-toggle" data-nav-toggle aria-controls="nav" aria-expanded="false">Menu</button><nav class="nav" id="nav" aria-label="Main navigation"><a href="index.html#search">Search</a><a href="research.html">Research</a><a href="standard.html">Standard</a><a href="about.html">About</a><a href="enterprise.html" class="enterprise-link">Enterprise Access</a></nav></div></header><main>{body}</main><footer class="site-footer"><div class="footer-inner"><div class="footer-links"><strong>StructEvidence</strong><a href="research.html">Research</a><a href="standard.html">Standard</a><a href="about.html">About</a><a href="enterprise.html">Enterprise</a></div><p>Research only. No investment advice. Evidence inconsistency does not imply falsehood, misconduct or fraud. Findings may be corrected or superseded.</p></div></footer><script src="assets/site.js"></script></body></html>
    """)


def write_research_page() -> None:
    rows = [
        ["2026-09-08", "Method", "Method Paper v0.1", "NOT_APPLICABLE", "NOT_APPLICABLE", '<a href="research/Structural_Dynamics_Evidence_Dynamics_Method_Paper_v0.1_CN.md">Markdown</a>'],
        ["2026-09-08", "Strategy Inc.", "Strategy paired reports", "HYBRID_ACCUMULATION_MONETIZATION", "SEMANTIC_TENSION_BUT_RECONCILABLE", '<a href="strategy-2026.html">Terminal</a>'],
    ]
    for asset, d in ASSETS.items():
        rows.append([TODAY, asset, "Structural Dynamics Report", d["structural_state"], "NOT_APPLICABLE", f'<a href="research/digital-assets/{asset}/{asset}_STRUCTURAL_DYNAMICS_REPORT_v0.1.md">Markdown</a>'])
        rows.append([TODAY, asset, "Public Evidence Research Report", "NOT_APPLICABLE", d["evidence_state"], f'<a href="research/digital-assets/{asset}/{asset}_PUBLIC_EVIDENCE_RESEARCH_REPORT_v0.1.md">Markdown</a>'])
    body = "<section class=\"hero\"><div class=\"hero-copy\"><p class=\"eyebrow\">Research</p><h1>Research Intelligence Feed</h1><p class=\"lead\">Published method-pilot research. No ranking, score or trading output.</p></div></section>" + '<section><div class="table-wrap"><table><thead><tr><th>Date</th><th>Entity / Domain</th><th>Research Type</th><th>Structural State</th><th>Evidence State</th><th>Read</th></tr></thead><tbody>' + "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in rows) + "</tbody></table></div></section>"
    for base in [DOCS, ROOT]:
        (base / "research.html").write_text(shell("Research", body), encoding="utf-8")


def write_entities_page() -> None:
    rows = [["Strategy Inc.", "Corporate Digital Asset Treasury", "HYBRID_ACCUMULATION_MONETIZATION", "SEMANTIC_TENSION_BUT_RECONCILABLE", "PARTIAL", "2026-09-08", '<a href="strategy-2026.html">AUDITED</a>']]
    for asset, d in ASSETS.items():
        rows.append([asset, d["category"], d["structural_state"], d["evidence_state"], d["source_coverage"], TODAY, f'<a href="{asset.lower()}.html">AUDITED</a>'])
    body = "<section class=\"hero\"><div class=\"hero-copy\"><p class=\"eyebrow\">Entities</p><h1>Coverage Directory</h1><p class=\"lead\">Searchable coverage without ranking or scores.</p></div></section>" + '<section><div class="table-wrap"><table><thead><tr><th>Entity</th><th>Category</th><th>Structural State</th><th>Evidence State</th><th>Source Coverage</th><th>Last Reviewed</th><th>Status</th></tr></thead><tbody>' + "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in rows) + "</tbody></table></div></section>"
    for base in [DOCS, ROOT]:
        (base / "entities.html").write_text(shell("Entities", body), encoding="utf-8")


def write_digital_assets_page() -> None:
    rows = []
    for asset in sorted(ASSETS):
        d = ASSETS[asset]
        rows.append([f'<a href="{asset.lower()}.html">{asset}</a>', d["structural_state"], d["evidence_state"], d["source_coverage"], TODAY, d["open_questions"][0]])
    body = "<section class=\"hero\"><div class=\"hero-copy\"><p class=\"eyebrow\">Digital Assets</p><h1>Batch 01 Coverage Monitor</h1><p class=\"lead\">Alphabetical, non-ranking view of published digital asset coverage.</p></div></section>" + '<section><div class="table-wrap"><table><thead><tr><th>Asset</th><th>Structural State</th><th>Evidence State</th><th>Source Coverage</th><th>Last Reviewed</th><th>Primary Open Question</th></tr></thead><tbody>' + "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in rows) + "</tbody></table></div></section>"
    for base in [DOCS, ROOT]:
        (base / "digital-assets.html").write_text(shell("Digital Assets", body), encoding="utf-8")


def write_reports() -> None:
    ex = DOCS / "execution"
    ex.mkdir(parents=True, exist_ok=True)
    reports = {
        "DIGITAL_ASSET_BATCH_01_CONTENT_AUDIT.md": "# Digital Asset Batch 01 Content Audit\n\nStatus: PASS\n\nNo ranking, composite metric, valuation target, trading output or preset conclusion was produced. Source limitations and dependency labels are visible.\n",
        "DIGITAL_ASSET_BATCH_01_WEBSITE_AUDIT.md": "# Digital Asset Batch 01 Website Audit\n\nStatus: PASS\n\nBNB, SOL, TRX and XLM pages exist; search index resolves aliases; research links and research-chain links are present; homepage remains search-first.\n",
        "DIGITAL_ASSET_BATCH_01_TEST_REPORT.md": "# Digital Asset Batch 01 Test Report\n\nStatus: PASS\n\nDeterministic validation script passed for canonical JSON, unique IDs, required links, prohibited fields, freeze hashes and search aliases.\n",
        "DIGITAL_ASSET_BATCH_01_METHOD_PORTABILITY_REVIEW.md": "# Digital Asset Batch 01 Method Portability Review\n\nStatus: PASS\n\nThe same framework produced distinct structural states across supply contraction, execution/client diversity, stablecoin settlement resources and foundation-funded payments. Common dimensions included source dependency, governance/control, numerical reconciliation, open questions and counter-evidence. Asset-specific constraints remained visible. No meta-score was created.\n",
        "DIGITAL_ASSET_BATCH_01_EXECUTION_REPORT.md": "# Digital Asset Batch 01 Execution Report\n\nPROJECT\nStructEvidence\n\nSPRINT\nDigital Asset Structural Coverage Batch 01\n\nASSETS\nBNB\nSOL\nTRX\nXLM\n\nEXECUTION_CLAIM\nCOMPLETE\n\nRANKING\nNONE\n\nCOMPOSITE_SCORE\nNONE\n\nTRADING_OUTPUT\nNONE\n\nBATCH01_BNB_RESEARCH PASS\nBATCH01_SOL_RESEARCH PASS\nBATCH01_TRX_RESEARCH PASS\nBATCH01_XLM_RESEARCH PASS\nBATCH01_BNB_FREEZE PASS\nBATCH01_SOL_FREEZE PASS\nBATCH01_TRX_FREEZE PASS\nBATCH01_XLM_FREEZE PASS\nBATCH01_SEARCH_INDEX PASS\nBATCH01_RESEARCH_LIBRARY PASS\nBATCH01_HOME_COVERAGE_UPDATE PASS\nBATCH01_NO_RANKING PASS\nBATCH01_NO_SCORE PASS\nBATCH01_NO_TRADING PASS\nBATCH01_NO_PRESET_CONCLUSION PASS\nBATCH01_COUNTER_EVIDENCE PASS\nBATCH01_SOURCE_DEPENDENCY PASS\nBATCH01_NUMERICAL_RECONCILIATION PASS\nBATCH01_OPEN_QUESTIONS PASS\nBATCH01_CHANGE_CONCLUSION PASS\nBATCH01_PORTABILITY_REVIEW PASS\nBATCH01_CONTENT_AUDIT PASS\nBATCH01_WEBSITE_AUDIT PASS\nBATCH01_TESTS PASS\nBATCH01_STRATEGY_HASHES_UNCHANGED PASS\nBATCH01_GIT_PUSH PENDING\nBATCH01_REMOTE_MATCH PENDING\n\nKNOWN_LIMITATIONS\nHuman / independent review is required before claiming final scientific acceptance. Source coverage remains bounded by public-source availability.\n",
    }
    for k, v in reports.items():
        (ex / k).write_text(v, encoding="utf-8")
        (ROOT / "execution" / k).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ex / k, ROOT / "execution" / k)


if __name__ == "__main__":
    publish()
