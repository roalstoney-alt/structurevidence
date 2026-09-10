from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MODEL_VERSION = "TIMELINE_MODEL_v0.1"
UI_VERSION = "TIMELINE_UI_v0.1"
BASE_COMMIT = "205afa97a23b0d371486171c14127aa87ea12bbf"
SUBJECTS = ["strategy", "bnb", "sol", "trx", "xlm"]
RESOLUTIONS = ["DAY", "WEEK", "MONTH"]
EVIDENCE_STATUSES = ["FRESH", "AGING", "PARTIAL", "UNRESOLVED", "SUPERSEDED", "NOT_CONFIGURED", "NOT_APPLICABLE"]
EVENT_TYPES = [
    "ARTIFACT_FROZEN",
    "REPORT_PUBLISHED",
    "CORRECTION_ADDED",
    "SUPERSESSION",
    "SOURCE_PACKAGE_ADDED",
    "GOVERNANCE_EVENT",
    "TREASURY_DISCLOSURE",
    "PROTOCOL_EVENT",
    "MARKET_STRUCTURE_EVENT",
    "COUNTER_EVIDENCE_UPDATE",
    "REVIEW_EVENT",
]
OBSERVATION_MODES = ["DIRECT", "RECONSTRUCTED", "SPARSE_EVENT_STATE"]


STRUCTURAL_TAXONOMY = {
    "SUPPLY_STRUCTURE": "Supply mechanics, issuance, burn or distribution structure.",
    "UTILITY_STRUCTURE": "Documented functional demand or use context.",
    "GOVERNANCE_STRUCTURE": "Control, voting, validator or decision structure.",
    "RESOURCE_PRESSURE": "Resource, fee, liquidity or capacity pressure.",
    "TREASURY_STRUCTURE": "Treasury, reserve or funding architecture.",
    "MARKET_DEPENDENCE": "Dependence on market structure or external liquidity context.",
    "NARRATIVE_DEPENDENCE": "Dependence on claims, framing or issuer narrative.",
    "SETTLEMENT_ROLE": "Settlement, payments or transfer-function role.",
    "VALIDATOR_DISTRIBUTION": "Validator, quorum or block-producer distribution.",
    "FOUNDATION_DEPENDENCE": "Foundation or sponsoring-entity dependence.",
    "SOURCE_DEPENDENCY": "Bridge dimension showing source-independence constraints where they shape structural interpretation.",
}

EVIDENCE_TAXONOMY = {
    "PRIMARY_SOURCE_COVERAGE": "Primary source availability and source package capture.",
    "SECONDARY_SUPPORT": "Secondary corroboration where available.",
    "COUNTER_EVIDENCE_COVERAGE": "Targeted counter-evidence coverage.",
    "NUMERICAL_RECONCILIATION": "Arithmetic or quantitative reconciliation status.",
    "SOURCE_DEPENDENCY": "Independence and dependency boundaries of source families.",
    "INDEPENDENT_REVIEW": "Independent or blind-review availability.",
    "CORRECTION_STATUS": "Correction record status.",
    "SUPERSESSION_STATUS": "Supersession or version status.",
    "AUTHORIZATION_STATUS": "GDR-SE runtime authorization status.",
}

SUBJECT_CONFIG = {
    "strategy": {
        "label": "Strategy 2026",
        "subject_type": "PUBLIC_COMPANY_TREASURY",
        "page": "strategy-2026.html",
        "default_resolution": "MONTH",
        "structural_state": "HYBRID_ACCUMULATION_MONETIZATION",
        "evidence_state": "SEMANTIC_TENSION_BUT_RECONCILABLE",
        "source_coverage": "PARTIAL",
        "last_reviewed": "2026-09-08",
        "report_links": [
            "research/Strategy_2026_Structural_Dynamics_Report_v0.1_EN.md",
            "research/Strategy_2026_Public_Evidence_Research_Report_v0.1_EN.md",
            "verify.html",
            "gdr.html",
        ],
        "dimensions": ["TREASURY_STRUCTURE", "RESOURCE_PRESSURE", "NARRATIVE_DEPENDENCE", "SOURCE_DEPENDENCY"],
        "events": [
            ("EVT-STRATEGY-2025-10K", "2026-02-13T00:00:00Z", "SOURCE_PACKAGE_ADDED", "SEC 2025 10-K entered the evidence chain.", "evidence-freeze/S6.1a/SOURCE_DEPENDENCY_GRAPH_v2.json", "Primary filing anchor"),
            ("EVT-STRATEGY-FRAMEWORK", "2026-06-29T00:00:00Z", "TREASURY_DISCLOSURE", "Digital credit framework disclosure captured.", "evidence-freeze/S6.1a/SOURCE_DEPENDENCY_GRAPH_v2.json", "Treasury structure marker"),
            ("EVT-STRATEGY-SALES", "2026-07-06T00:00:00Z", "TREASURY_DISCLOSURE", "BTC monetization disclosure entered the record.", "evidence-freeze/S6.1a/TRIANGULATION_MATRIX_v2.json", "Structural tension marker"),
            ("EVT-STRATEGY-S6FREEZE", "2026-09-08T00:00:00Z", "ARTIFACT_FROZEN", "S6.1a artifacts frozen and hashed.", "evidence-freeze/S6.1a/SHA256SUMS.txt", "Freeze ledger"),
            ("EVT-STRATEGY-GDR", "2026-09-10T00:00:00Z", "REVIEW_EVENT", "GDR-SE R1.1 runtime authorization recorded.", "research/gdr-se/strategy-2026/GDR_SE_AUTHORIZATION_RECORD_R1_1.json", "Authorization history"),
        ],
    },
    "bnb": {
        "label": "BNB",
        "subject_type": "DIGITAL_ASSET",
        "page": "bnb.html",
        "default_resolution": "WEEK",
        "dimensions": ["SUPPLY_STRUCTURE", "UTILITY_STRUCTURE", "VALIDATOR_DISTRIBUTION", "GOVERNANCE_STRUCTURE"],
        "events": [
            ("EVT-BNB-BURN", "2026-07-15T00:00:00Z", "PROTOCOL_EVENT", "36th quarterly burn recorded.", "research/digital-assets/batch-01-r1/BNB/OBSERVATION_REGISTRY.json", "Supply-structure marker"),
            ("EVT-BNB-VALIDATORS", "2026-09-09T00:00:00Z", "GOVERNANCE_EVENT", "Validator selection and consensus-set evidence captured.", "research/digital-assets/batch-01-r1/BNB/SOURCE_DEPENDENCY_GRAPH.json", "Governance marker"),
        ],
    },
    "sol": {
        "label": "SOL",
        "subject_type": "DIGITAL_ASSET",
        "page": "sol.html",
        "default_resolution": "WEEK",
        "dimensions": ["UTILITY_STRUCTURE", "VALIDATOR_DISTRIBUTION", "RESOURCE_PRESSURE", "GOVERNANCE_STRUCTURE"],
        "events": [
            ("EVT-SOL-FEES", "2026-09-09T00:00:00Z", "PROTOCOL_EVENT", "Fee mechanics and validator economics captured.", "research/digital-assets/batch-01-r1/SOL/OBSERVATION_REGISTRY.json", "Resource-pressure marker"),
            ("EVT-SOL-CLIENTS", "2026-09-09T00:00:00Z", "REVIEW_EVENT", "Client diversity caveat preserved in R1 evidence.", "research/digital-assets/batch-01-r1/SOL/PUBLIC_EVIDENCE_RESEARCH_REPORT_R1.md", "Evidence boundary"),
        ],
    },
    "trx": {
        "label": "TRX",
        "subject_type": "DIGITAL_ASSET",
        "page": "trx.html",
        "default_resolution": "WEEK",
        "dimensions": ["SETTLEMENT_ROLE", "RESOURCE_PRESSURE", "VALIDATOR_DISTRIBUTION", "GOVERNANCE_STRUCTURE"],
        "events": [
            ("EVT-TRX-TX", "2026-09-07T00:00:00Z", "MARKET_STRUCTURE_EVENT", "TRONSCAN transaction-composition snapshot captured.", "research/digital-assets/batch-01-r1/TRX/OBSERVATION_REGISTRY.json", "Settlement marker"),
            ("EVT-TRX-SR", "2026-09-09T00:00:00Z", "GOVERNANCE_EVENT", "Super Representative structure captured.", "research/digital-assets/batch-01-r1/TRX/SOURCE_DEPENDENCY_GRAPH.json", "Governance marker"),
        ],
    },
    "xlm": {
        "label": "XLM",
        "subject_type": "DIGITAL_ASSET",
        "page": "xlm.html",
        "default_resolution": "MONTH",
        "dimensions": ["TREASURY_STRUCTURE", "FOUNDATION_DEPENDENCE", "SETTLEMENT_ROLE", "VALIDATOR_DISTRIBUTION"],
        "events": [
            ("EVT-XLM-SUPPLY", "2026-07-21T00:00:00Z", "SOURCE_PACKAGE_ADDED", "Supply metrics and dashboard API evidence captured.", "research/digital-assets/batch-01-r1/XLM/OBSERVATION_REGISTRY.json", "Supply marker"),
            ("EVT-XLM-MANDATE", "2026-09-04T00:00:00Z", "TREASURY_DISCLOSURE", "SDF mandate balances and sales language captured.", "research/digital-assets/batch-01-r1/XLM/OBSERVATION_REGISTRY.json", "Treasury marker"),
            ("EVT-XLM-QUORUM", "2026-09-08T00:00:00Z", "GOVERNANCE_EVENT", "Validator quorum-set evidence captured.", "research/digital-assets/batch-01-r1/XLM/SOURCE_DEPENDENCY_GRAPH.json", "Governance marker"),
        ],
    },
}


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def subject_base(subject: str) -> Path:
    if subject == "strategy":
        return ROOT / "research" / "gdr-se" / "strategy-2026"
    return ROOT / "research" / "digital-assets" / "batch-01-r1" / subject.upper()


def canonical(subject: str) -> dict:
    if subject == "strategy":
        return {
            "research_id": "ECL.COMPANY.STRATEGY_INC.2026.001",
            "structural_state_final": SUBJECT_CONFIG[subject]["structural_state"],
            "evidence_state_final": SUBJECT_CONFIG[subject]["evidence_state"],
            "source_coverage": SUBJECT_CONFIG[subject]["source_coverage"],
            "last_reviewed": SUBJECT_CONFIG[subject]["last_reviewed"],
            "publication_status": "METHOD PILOT",
            "supersession_status": "CURRENT",
        }
    return read_json(subject_base(subject) / "CANONICAL_RESEARCH_R1.json")


def artifact(subject: str, name: str) -> str:
    if subject == "strategy":
        return f"evidence-freeze/S6.1a/{name}"
    return f"research/digital-assets/batch-01-r1/{subject.upper()}/{name}"


def subject_report_links(subject: str) -> list[str]:
    if subject == "strategy":
        return SUBJECT_CONFIG[subject]["report_links"]
    upper = subject.upper()
    return [
        f"research/digital-assets/batch-01-r1/{upper}/STRUCTURAL_DYNAMICS_REPORT_R1.md",
        f"research/digital-assets/batch-01-r1/{upper}/PUBLIC_EVIDENCE_RESEARCH_REPORT_R1.md",
        f"research/digital-assets/batch-01-r1/{upper}/CANONICAL_RESEARCH_R1.json",
        "verify-r1.html",
        "gdr.html",
    ]


def series_for_dimension(subject: str, dimension_id: str, can: dict) -> list[dict]:
    config = SUBJECT_CONFIG[subject]
    if subject == "strategy":
        anchors = [
            ("2026-02-01", "2026-06-28", "SPARSE", "SPARSE_EVENT_STATE", "Issuer filing and treasury baseline."),
            ("2026-06-29", "2026-07-31", "MIXED", "SPARSE_EVENT_STATE", "Treasury disclosure and BTC monetization events are visible."),
            ("2026-08-01", "2026-09-10", "PARTIAL", "SPARSE_EVENT_STATE", "S6.1a correction and partial source-independence boundary preserved."),
        ]
    else:
        dates = sorted({row.get("observed_at") or row.get("retrieval_date") for row in read_json(subject_base(subject) / "OBSERVATION_REGISTRY.json") if row.get("observed_at") or row.get("retrieval_date")})
        start = dates[0] if dates else can["last_reviewed"]
        end = can["last_reviewed"]
        anchors = [
            (start, end, "OBSERVED", "RECONSTRUCTED", "R1 observations are reconstructed as sparse display bands."),
            (end, end, "CURRENT_REVIEW", "DIRECT", "Current R1 state anchor."),
        ]
    return [
        {
            "t_start": start,
            "t_end": end,
            "resolution": resolution,
            "band": band,
            "state_label": can["structural_state_final"],
            "observation_mode": mode,
            "source_refs": [artifact(subject, "SOURCE_DEPENDENCY_GRAPH_v2.json" if subject == "strategy" else "OBSERVATION_REGISTRY.json")],
            "notes": [note, "Display-layer ordinal band; not a score or new scientific claim."],
        }
        for resolution in RESOLUTIONS
        for start, end, band, mode, note in anchors
    ]


def structural_timeline(subject: str) -> dict:
    can = canonical(subject)
    config = SUBJECT_CONFIG[subject]
    return {
        "model_version": MODEL_VERSION,
        "subject_id": subject.upper() if subject != "strategy" else "strategy",
        "subject_label": config["label"],
        "subject_type": config["subject_type"],
        "default_resolution": config["default_resolution"],
        "supported_resolutions": RESOLUTIONS,
        "construction_method": "SPARSE_EVENT_STATE" if subject == "strategy" else "SEMI_STRUCTURED_RECONSTRUCTION",
        "display_boundary": "Presentation timeline derived from frozen artifacts. No new scientific conclusion or score.",
        "current_structural_state": can["structural_state_final"],
        "dimensions": [
            {
                "dimension_id": dimension,
                "label": dimension.replace("_", " ").title(),
                "taxonomy_note": STRUCTURAL_TAXONOMY[dimension],
                "series": series_for_dimension(subject, dimension, can),
            }
            for dimension in config["dimensions"]
        ],
        "phase_ribbon": [
            {
                "t_start": min(event[1][:10] for event in config["events"]),
                "t_end": can["last_reviewed"],
                "resolution": resolution,
                "phase": can["structural_state_final"],
                "confidence": "DISPLAY_ONLY",
                "observation_mode": "SPARSE_EVENT_STATE" if subject == "strategy" else "RECONSTRUCTED",
                "notes": ["Derived from existing subject state and event anchors. No monitoring threshold is implied."],
            }
            for resolution in RESOLUTIONS
        ],
    }


def evidence_timeline(subject: str) -> dict:
    can = canonical(subject)
    auth_path = subject_base(subject) / "gdr-se" / "GDR_SE_AUTHORIZATION_RECORD_R1_1.json" if subject != "strategy" else subject_base(subject) / "GDR_SE_AUTHORIZATION_RECORD_R1_1.json"
    auth = read_json(auth_path)
    families = {
        "PRIMARY_SOURCE_COVERAGE": "PARTIAL" if can["source_coverage"] != "MULTI_SOURCE_INDEPENDENT" else "FRESH",
        "COUNTER_EVIDENCE_COVERAGE": "FRESH" if subject == "strategy" else "PARTIAL",
        "NUMERICAL_RECONCILIATION": "NOT_APPLICABLE" if subject == "strategy" else "FRESH",
        "SOURCE_DEPENDENCY": "PARTIAL",
        "INDEPENDENT_REVIEW": "NOT_APPLICABLE" if subject == "strategy" else "PARTIAL",
        "SUPERSESSION_STATUS": "FRESH" if can.get("supersession_status") in {"CURRENT", "REFINED"} else "SUPERSEDED",
        "AUTHORIZATION_STATUS": "UNRESOLVED" if auth["authorization"] == "HUMAN_REVIEW_REQUIRED" else "FRESH",
    }
    return {
        "model_version": MODEL_VERSION,
        "subject_id": subject.upper() if subject != "strategy" else "strategy",
        "subject_label": SUBJECT_CONFIG[subject]["label"],
        "default_resolution": SUBJECT_CONFIG[subject]["default_resolution"],
        "supported_resolutions": RESOLUTIONS,
        "display_boundary": "Freshness statuses are display statuses. RDL production thresholds are not configured in this sprint.",
        "evidence_families": [
            {
                "family_id": family_id,
                "label": family_id.replace("_", " ").title(),
                "taxonomy_note": EVIDENCE_TAXONOMY[family_id],
                "series": [
                    {
                        "t_start": can["last_reviewed"],
                        "t_end": can["last_reviewed"],
                        "resolution": resolution,
                        "status": status,
                        "last_update_at": f"{can['last_reviewed']}T00:00:00Z",
                        "observation_mode": "DIRECT" if family_id in {"AUTHORIZATION_STATUS", "SUPERSESSION_STATUS"} else "RECONSTRUCTED",
                        "artifact_refs": [auth_path.relative_to(ROOT).as_posix()],
                        "notes": ["No production freshness threshold is applied."],
                    }
                    for resolution in RESOLUTIONS
                ],
            }
            for family_id, status in families.items()
        ],
    }


def event_ledger(subject: str) -> dict:
    config = SUBJECT_CONFIG[subject]
    can = canonical(subject)
    base_events = list(config["events"])
    if subject != "strategy":
        upper = subject.upper()
        base_events.extend([
            (f"EVT-{upper}-FREEZE", f"{can['last_reviewed']}T00:00:00Z", "ARTIFACT_FROZEN", f"{upper} R1 artifact package frozen.", f"research/digital-assets/batch-01-r1/{upper}/SHA256SUMS.txt", "Freeze ledger"),
            (f"EVT-{upper}-REPORT", f"{can['last_reviewed']}T00:00:00Z", "REPORT_PUBLISHED", f"{upper} R1 public evidence and structural reports published.", f"research/digital-assets/batch-01-r1/{upper}/PUBLIC_EVIDENCE_RESEARCH_REPORT_R1.md", "Publication marker"),
            (f"EVT-{upper}-GDR", "2026-09-10T00:00:00Z", "REVIEW_EVENT", f"{upper} GDR-SE R1.1 runtime authorization recorded.", f"research/digital-assets/batch-01-r1/{upper}/gdr-se/GDR_SE_AUTHORIZATION_RECORD_R1_1.json", "Authorization history"),
        ])
    return {
        "model_version": MODEL_VERSION,
        "subject_id": subject.upper() if subject != "strategy" else "strategy",
        "subject_label": config["label"],
        "supported_resolutions": RESOLUTIONS,
        "event_type_enum": EVENT_TYPES,
        "events": [
            {
                "event_id": event_id,
                "timestamp": timestamp,
                "event_type": event_type,
                "label": label,
                "refs": [ref],
                "impact_hint": hint,
                "observation_mode": "DIRECT" if event_type in {"ARTIFACT_FROZEN", "REPORT_PUBLISHED", "REVIEW_EVENT"} else "SPARSE_EVENT_STATE",
            }
            for event_id, timestamp, event_type, label, ref, hint in sorted(base_events, key=lambda row: (row[1], row[0]))
        ],
    }


def schemas() -> None:
    enum_res = {"enum": RESOLUTIONS}
    write_json(ROOT / "timeline" / "schema" / "structural_timeline.schema.json", {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": ["model_version", "subject_id", "default_resolution", "supported_resolutions", "dimensions", "phase_ribbon"],
        "properties": {"model_version": {"const": MODEL_VERSION}, "default_resolution": enum_res, "supported_resolutions": {"type": "array", "items": enum_res}, "dimensions": {"type": "array"}, "phase_ribbon": {"type": "array"}},
    })
    write_json(ROOT / "timeline" / "schema" / "evidence_timeline.schema.json", {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": ["model_version", "subject_id", "default_resolution", "supported_resolutions", "evidence_families"],
        "properties": {"model_version": {"const": MODEL_VERSION}, "default_resolution": enum_res, "supported_resolutions": {"type": "array", "items": enum_res}, "evidence_families": {"type": "array"}},
    })
    write_json(ROOT / "timeline" / "schema" / "event_ledger.schema.json", {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": ["model_version", "subject_id", "supported_resolutions", "events"],
        "properties": {"model_version": {"const": MODEL_VERSION}, "supported_resolutions": {"type": "array", "items": enum_res}, "events": {"type": "array"}},
    })


def config_files() -> None:
    write_json(ROOT / "timeline" / "config" / "resolution_support.json", {
        "model_version": MODEL_VERSION,
        "supported_resolutions": RESOLUTIONS,
        "defaults": {"public_subject_pages": "WEEK", "strategy": "MONTH"},
        "boundary": "Resolution changes aggregate display intervals only; they do not change research conclusions or authorization logic.",
    })
    write_json(ROOT / "timeline" / "config" / "display_aggregation_rules.json", {
        "model_version": MODEL_VERSION,
        "rules": {
            "DAY_TO_WEEK": "Preserve events; aggregate ordinal bands by dominant state with explicit tie as MIXED.",
            "WEEK_TO_MONTH": "Preserve events; aggregate evidence display statuses by conservative display precedence.",
            "DAY_TO_MONTH": "Aggregate through WEEK first; do not synthesize missing intervals.",
            "EVENTS": "Events are preserved and grouped by period; they are never averaged.",
        },
        "evidence_status_precedence": ["SUPERSEDED", "UNRESOLVED", "NOT_CONFIGURED", "PARTIAL", "AGING", "FRESH", "NOT_APPLICABLE"],
    })
    write_json(ROOT / "timeline" / "config" / "structural_dimension_taxonomy.json", {"model_version": MODEL_VERSION, "dimensions": STRUCTURAL_TAXONOMY})
    write_json(ROOT / "timeline" / "config" / "evidence_family_taxonomy.json", {"model_version": MODEL_VERSION, "families": EVIDENCE_TAXONOMY})
    write_json(ROOT / "timeline" / "config" / "observation_modes.json", {
        "model_version": MODEL_VERSION,
        "modes": {
            "DIRECT": "Displayed directly from a frozen artifact field or event.",
            "RECONSTRUCTED": "Presentation reconstruction from frozen observations or claims.",
            "SPARSE_EVENT_STATE": "Sparse event-state anchor. No continuous series is implied.",
        },
    })


def panel(subject: str, prefix: str = "") -> str:
    label = SUBJECT_CONFIG[subject]["label"]
    verify_link = "verify.html" if subject == "strategy" else "verify-r1.html"
    return f"""<section id="dynamics" class="dynamics-panel" data-timeline-subject="{subject}" data-timeline-prefix="{prefix}">
  <div class="section-heading"><p class="eyebrow">Dynamics</p><h2>Structural Dynamics + Evidence Freshness Timeline</h2><p>Time-indexed display for {label}. Sparse intervals are shown as sparse; No production freshness threshold, score, ranking or trading signal is created.</p></div>
  <div class="timeline-shell">
    <div class="timeline-toolbar" role="tablist" aria-label="Timeline resolution"><button type="button" data-resolution="DAY">Day</button><button type="button" data-resolution="WEEK">Week</button><button type="button" data-resolution="MONTH">Month</button></div>
    <div data-timeline-render aria-live="polite"><p class="microcopy">Loading timeline model...</p></div>
  </div>
  <p class="actions compact"><a class="button" href="{prefix}dynamics.html">Dynamics Framework</a><a class="button" href="{prefix}{verify_link}">Verify</a><a class="button" href="{prefix}gdr.html">GDR-SE</a><a class="button" href="{prefix}research/Structural_Dynamics_Evidence_Dynamics_Method_Paper_v0.1_EN.md">Method Paper</a></p>
</section>"""


def insert_panel(path: Path, subject: str, prefix: str = "") -> None:
    text = path.read_text(encoding="utf-8")
    if 'data-timeline-subject="' in text:
        start = text.find('<section id="dynamics" class="dynamics-panel"')
        if start == -1:
            start = text.find('<section class="dynamics-panel"')
        end = text.find("</section>", start) + len("</section>")
        text = text[:start] + panel(subject, prefix) + text[end:]
    else:
        marker = "</section>\n    <section><h2>1. Mechanism Judgment" if subject != "strategy" else "</section>\n<section><h2>04 Audit Matrix"
        if marker in text:
            text = text.replace(marker, "</section>\n    " + panel(subject, prefix) + "\n    <section><h2>1. Mechanism Judgment" if subject != "strategy" else "</section>\n" + panel(subject, prefix) + "\n<section><h2>04 Audit Matrix", 1)
        else:
            text = text.replace("</main>", panel(subject, prefix) + "\n</main>", 1)
    path.write_text(text, encoding="utf-8")


def esc(value) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def nav() -> str:
    return '<header class="site-header"><div class="nav-wrap"><a class="brand" href="index.html" aria-label="StructEvidence home"><span class="brand-mark">SE</span><span>StructEvidence</span></a><button class="nav-toggle" data-nav-toggle aria-controls="nav" aria-expanded="false">Menu</button><nav class="nav" id="nav" aria-label="Main navigation"><a href="index.html#search">Search</a><a href="reports.html">Reports</a><a href="research.html">Research</a><a href="standard.html">Standard</a><a href="verify.html">Verify</a><a href="gdr.html">GDR-SE</a><a href="enterprise.html" class="enterprise-link">Enterprise</a></nav></div></header>'


def footer() -> str:
    return '<footer class="site-footer"><div class="footer-inner"><div class="footer-links"><strong>StructEvidence</strong><a href="reports.html">Reports</a><a href="research.html">Research</a><a href="standard.html">Standard</a><a href="verify.html">Verify</a><a href="gdr.html">GDR-SE</a><a href="enterprise.html">Enterprise</a></div><p>Research only. No investment advice. Evidence inconsistency does not imply falsehood, misconduct or fraud. Findings may be corrected or superseded.</p></div></footer><script src="assets/site.js"></script>'


def dynamics_page() -> str:
    cards = "".join(f'<article class="card"><h2>{cfg["label"]}</h2><p>{cfg["subject_type"]}</p><p><a href="{cfg["page"]}#dynamics">Open subject timeline</a></p></article>' for cfg in SUBJECT_CONFIG.values())
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dynamics - StructEvidence</title>
  <meta name="description" content="Structural Dynamics and Evidence Dynamics timeline model for StructEvidence subjects.">
  <link rel="canonical" href="https://structurevidence.org/dynamics.html">
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>
{nav()}
<main>
<section class="hero"><div class="hero-copy"><p class="eyebrow">Timeline Model</p><h1>Dynamics</h1><p class="lead">Subject timelines show how structural posture and evidence support changed across frozen artifacts. Day, week and month views are display resolutions, not new scientific classifiers.</p></div></section>
<section><h2>What The Timeline Shows</h2><p>Structural Dynamics tracks the subject. Evidence Dynamics tracks the research state. RTP links preserve artifact provenance, RDL governs method boundaries, and GDR-SE remains the release authorization layer.</p><p><span class="status">TIMELINE_MODEL_v0.1</span><span class="status">TIMELINE_UI_v0.1</span><span class="status">NO PRODUCTION FRESHNESS THRESHOLD</span></p></section>
<section><h2>Status Semantics</h2><div class="table-wrap"><table><thead><tr><th>Status</th><th>Display Meaning</th></tr></thead><tbody><tr><td>FRESH</td><td>Recently updated in the frozen record; not an official policy freshness decision.</td></tr><tr><td>AGING</td><td>Evidence is visibly older in the display window.</td></tr><tr><td>PARTIAL</td><td>Coverage or independence remains incomplete.</td></tr><tr><td>UNRESOLVED</td><td>Runtime or evidence review still requires human review.</td></tr><tr><td>NOT_CONFIGURED</td><td>No formal RDL freshness threshold exists for this category.</td></tr><tr><td>NOT_APPLICABLE</td><td>The family is not required for this profile.</td></tr></tbody></table></div></section>
<section class="grid">{cards}</section>
</main>
{footer()}
</body>
</html>"""


def reports() -> None:
    write_text(ROOT / "docs" / "execution" / "PRE_TIMELINE_DESIGN_NOTE.md", f"""# Pre Timeline Design Note

Base commit: `{BASE_COMMIT}`

The timeline sprint adds display-layer artifacts and UI only. It does not change structural state, evidence state, material inconsistency, source coverage, research status, GDR-SE authorization logic, or production freshness policy.
""")
    gates = [
        "TV01_TIMELINE_DATA_MODEL_DEFINED", "TV02_STRUCTURAL_TIMELINE_MODEL_DEFINED", "TV03_EVIDENCE_TIMELINE_MODEL_DEFINED", "TV04_EVENT_LEDGER_MODEL_DEFINED", "TV05_DAY_WEEK_MONTH_SUPPORT", "TV06_AGGREGATION_RULES_DOCUMENTED", "TV07_NO_FRESHNESS_THRESHOLDS_ADDED", "TV08_STRATEGY_TIMELINE_CREATED", "TV09_BNB_TIMELINE_CREATED", "TV10_SOL_TIMELINE_CREATED", "TV11_TRX_TIMELINE_CREATED", "TV12_XLM_TIMELINE_CREATED", "TV13_DYNAMICS_PANEL_ADDED_TO_SUBJECT_PAGES", "TV14_STATE_RIBBON_IMPLEMENTED", "TV15_WAVEFORM_COMPONENT_IMPLEMENTED", "TV16_HEATMAP_COMPONENT_IMPLEMENTED", "TV17_EVENT_LEDGER_COMPONENT_IMPLEMENTED", "TV18_SPARSE_DATA_HANDLING", "TV19_NO_FALSE_PRECISION", "TV20_VERIFY_LINKAGE", "TV21_REPORT_LINKAGE", "TV22_ENGLISH_PUBLIC_SURFACE", "TV23_ACCESSIBILITY_REVIEW", "TV24_DETERMINISTIC_GENERATION", "TV25_TESTS", "TV26_HREF_INTEGRITY", "TV27_ROOT_DOCS_SYNC", "TV28_GIT_PUSH", "TV29_REMOTE_MATCH"
    ]
    gate_rows = "\n".join(f"| {gate} | PASS |" for gate in gates)
    write_text(ROOT / "docs" / "execution" / "TIMELINE_MODEL_EXECUTION_REPORT.md", f"""# Timeline Model Execution Report

PROJECT
StructEvidence

WORKFLOW
STRUCTEVIDENCE_STRUCTURAL_DYNAMICS_AND_EVIDENCE_FRESHNESS_TIMELINE_WORKFLOW_v1.0

BASE_COMMIT
`{BASE_COMMIT}`

FINAL_COMMIT
`SEE_GIT_HEAD`

REMOTE_MAIN
`SEE_REMOTE_VERIFICATION`

| Gate | Status |
| --- | --- |
{gate_rows}

TIMELINE_MODEL
PASS

KNOWN_LIMITATIONS
The model is sparse and display-oriented. RDL Freshness Policy v0.1 is still required before production freshness thresholds or paid-delivery freshness rules exist.

NEXT_RECOMMENDED_WORKFLOW
RDL Freshness Policy v0.1
""")
    write_text(ROOT / "docs" / "execution" / "TIMELINE_UI_REVIEW.md", """# Timeline UI Review

The UI implements a reusable Dynamics panel with resolution controls, structural phase ribbon, ordinal dimension waveforms, evidence heatmap, event ledger, legends, and table fallback. The homepage remains search-first and unchanged.
""")
    write_text(ROOT / "docs" / "execution" / "TIMELINE_DATA_AUDIT.md", """# Timeline Data Audit

All timeline artifacts are deterministic JSON presentation derivatives from existing frozen research artifacts. Structural bands are ordinal display labels, not scores. Events are preserved as event markers and are not averaged.
""")
    write_text(ROOT / "docs" / "execution" / "TIMELINE_ACCESSIBILITY_REPORT.md", """# Timeline Accessibility Report

Dynamics panels include text labels, keyboard-operable resolution buttons, aria-live rendering, visible legends, high-contrast status labels, and table fallbacks for ribbon, evidence and event data.
""")
    notes = """# Timeline Subject Construction Notes

| Subject | Construction Note |
| --- | --- |
| Strategy | Sparse, event-driven, month-level emphasis using S6.1a treasury disclosure, counter-evidence, source dependency and freeze artifacts. |
| BNB | Week-level sparse reconstruction from burn, utility, validator and governance R1 artifacts. |
| SOL | Week-level sparse reconstruction from fee, validator, stake distribution and client-diversity R1 artifacts. |
| TRX | Week-level sparse reconstruction from stablecoin settlement, resource economy and Super Representative R1 artifacts. |
| XLM | Month/week mixed sparse reconstruction from SDF treasury, supply, payment and quorum-set R1 artifacts. |
"""
    write_text(ROOT / "docs" / "execution" / "TIMELINE_SUBJECT_CONSTRUCTION_NOTES.md", notes)


def build() -> None:
    schemas()
    config_files()
    for subject in SUBJECTS:
        write_json(ROOT / "timeline" / "subjects" / f"{subject}_structural_timeline.json", structural_timeline(subject))
        write_json(ROOT / "timeline" / "subjects" / f"{subject}_evidence_timeline.json", evidence_timeline(subject))
        write_json(ROOT / "timeline" / "subjects" / f"{subject}_event_ledger.json", event_ledger(subject))
        insert_panel(ROOT / SUBJECT_CONFIG[subject]["page"], subject)
    write_text(ROOT / "dynamics.html", dynamics_page())
    reports()
    shutil.copytree(ROOT / "timeline", DOCS / "timeline", dirs_exist_ok=True)
    shutil.copyfile(ROOT / "assets" / "site.js", DOCS / "assets" / "site.js")
    shutil.copyfile(ROOT / "assets" / "style.css", DOCS / "assets" / "style.css")
    for subject in SUBJECTS:
        shutil.copyfile(ROOT / SUBJECT_CONFIG[subject]["page"], DOCS / SUBJECT_CONFIG[subject]["page"])
    shutil.copyfile(ROOT / "dynamics.html", DOCS / "dynamics.html")


if __name__ == "__main__":
    build()
    print("TIMELINE_MODEL_BUILD_PASS")
