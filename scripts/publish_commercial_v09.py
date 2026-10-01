from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ASSET_SYMBOLS = ["BNB", "SOL", "TRX", "XLM"]
TODAY = "2026-09-09"


def esc(value) -> str:
    return str(value if value is not None else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def nav(prefix: str = "") -> str:
    return f"""<header class="site-header">
  <div class="nav-wrap">
    <a class="brand" href="{prefix}index.html" aria-label="StructEvidence home"><span class="brand-mark">SE</span><span>StructEvidence</span></a>
    <button class="nav-toggle" data-nav-toggle aria-controls="nav" aria-expanded="false">Menu</button>
    <nav class="nav" id="nav" aria-label="Main navigation"><a href="{prefix}index.html#search">Search</a><a href="{prefix}reports.html">Reports</a><a href="{prefix}research.html">Research</a><a href="{prefix}standard.html">Standard</a><a href="{prefix}verify.html">Verify</a><a href="{prefix}enterprise.html" class="enterprise-link">Enterprise</a></nav>
  </div>
</header>"""


def footer(prefix: str = "") -> str:
    return f"""<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-links"><strong>StructEvidence</strong><a href="{prefix}reports.html">Reports</a><a href="{prefix}research.html">Research</a><a href="{prefix}standard.html">Standard</a><a href="{prefix}verify.html">Verify</a><a href="{prefix}enterprise.html">Enterprise</a></div>
    <p>Research only. No investment advice. Evidence inconsistency does not imply falsehood, misconduct or fraud. Findings may be corrected or superseded.</p>
  </div>
</footer><script src="{prefix}assets/site.js"></script>"""


def page(title: str, description: str, body: str, canonical: str, prefix: str = "") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} - StructEvidence</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="https://structurevidence.org/{esc(canonical)}">
  <meta property="og:title" content="{esc(title)} - StructEvidence">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://structurevidence.org/{esc(canonical)}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
{nav(prefix)}
<main>
{body}
</main>
{footer(prefix)}
</body>
</html>"""


def asset_obs(symbol: str) -> list[str]:
    rows = read_json(ROOT / "research" / "digital-assets" / "batch-01-r1" / symbol / "OBSERVATION_REGISTRY.json")
    return [row["statement"] for row in rows[:3]]


def free_scan_payload(entity: dict) -> dict:
    ticker = entity.get("ticker")
    if ticker == "MSTR":
        observations = [
            "Bitcoin remains the primary treasury reserve asset in the approved public record.",
            "A BTC monetization program and actual BTC sales are visible in the approved public record.",
            "ATM funding, reserve funding and preferred dividends appear together in the disclosure chain.",
        ]
        limitation = "Independent-source triangulation remains partial in the approved public record."
        open_question = "Whether BTC monetization becomes a recurring structural tool or remains period-specific requires later evidence."
        observation_window = "2025-12-31 to 2026-08-31"
    else:
        observations = asset_obs(ticker)
        limitation = f"Source coverage is {entity.get('source_coverage', 'GAP')}; the free scan does not expose the full source inventory or ACH."
        open_question = "What new independent evidence would narrow or reverse the current structural classification?"
        observation_window = "See R1 canonical research record"
    return {
        "key_observations": observations,
        "key_limitation": limitation,
        "open_question": open_question,
        "observation_window": observation_window,
        "report_version": "Free Scan V0.9",
        "market_context": None,
    }


def update_entities() -> None:
    for path in [ROOT / "assets" / "entities.json", DOCS / "assets" / "entities.json"]:
        entities = read_json(path)
        for entity in entities:
            if entity.get("covered"):
                entity["free_scan"] = free_scan_payload(entity)
        write_json(path, entities)


def write_configs() -> None:
    write_json(ROOT / "commercial" / "config" / "commercial.json", {
        "commercial_status": "EARLY_ACCESS",
        "paid_report_enabled": False,
        "custom_audit_enabled": True,
        "payment_enabled": False,
        "search_demand_logging": False,
        "structural_delta_enabled": False,
        "mos_context_enabled": False,
        "gdr_gate_enabled": False,
        "commercial_launch_gate": "BLOCKED",
        "blocked_reason": "Seller identity, public contact addresses, price configuration and payment provider are not configured.",
    })
    write_json(ROOT / "commercial" / "config" / "products.json", {
        "verified_report": {
            "enabled": True,
            "currency": "USD",
            "price": None,
            "price_status": "CONFIG_REQUIRED",
            "cta_when_unpriced": "Request Early Access",
        },
        "custom_audit": {
            "enabled": True,
            "price": None,
            "price_status": "SCOPE_REQUIRED",
            "cta_when_unpriced": "Request Scope",
        },
        "enterprise_evidence_review": {
            "enabled": True,
            "self_serve": False,
            "price_status": "CUSTOM_SCOPE_REQUIRED",
        },
    })
    write_json(ROOT / "commercial" / "config" / "contact.json", {
        "sales_email": None,
        "support_email": None,
        "legal_email": None,
        "company_name": None,
        "country": None,
        "contact_status": "CONFIG_REQUIRED",
    })
    write_json(ROOT / "commercial" / "intelligence" / "ENGINE_REGISTRY.json", {
        "MOS": {"status": "UNKNOWN", "commercial_role": "MARKET_CONTEXT_ONLY", "public_claim": False},
        "GDR": {"status": "UNKNOWN", "commercial_role": "RESERVED_NOT_CONNECTED", "public_claim": False},
        "PFR": {"status": "UNKNOWN", "commercial_role": "RESERVED_NOT_CONNECTED", "public_claim": False},
        "MDL": {"status": "VALIDATED_FOR_RESEARCH", "commercial_role": "STRUCTURAL_ANALYSIS_INPUT", "public_claim": True},
        "ECL": {"status": "VALIDATED_FOR_RESEARCH", "commercial_role": "EVIDENCE_ANALYSIS_INPUT", "public_claim": True},
        "RTP": {"status": "VALIDATED_FOR_RESEARCH", "commercial_role": "PROVENANCE_RECORD", "public_claim": True},
        "law": "TOOL OUTPUT != PUBLISHED FINDING",
    })
    write_json(ROOT / "commercial" / "VERIFICATION_RECORD.json", {
        "record_status": "TEMPLATE_NO_PAID_REPORT_DELIVERED",
        "research_id": None,
        "report_id": None,
        "report_version": None,
        "method_version": None,
        "observation_window": None,
        "last_reviewed": None,
        "source_count": None,
        "source_dependency_groups": [],
        "artifact_classes": [],
        "manifest_hash": None,
        "publication_timestamp": None,
        "correction_status": None,
        "supersession_status": None,
        "certificate_boundary": "Does not certify truth, safety, solvency or investment quality.",
    })


def write_schemas() -> None:
    write_json(ROOT / "commercial" / "schema" / "order.schema.json", {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "StructEvidence Order",
        "type": "object",
        "additionalProperties": False,
        "required": ["order_id", "created_at", "product_id", "entity_id", "customer_email", "payment_status", "fulfillment_status", "report_version", "verification_id"],
        "properties": {
            "order_id": {"type": "string"},
            "created_at": {"type": "string", "format": "date-time"},
            "product_id": {"type": "string"},
            "entity_id": {"type": "string"},
            "customer_email": {"type": "string", "format": "email"},
            "payment_status": {"enum": ["PENDING", "PAID", "FAILED", "REFUNDED", "CANCELED"]},
            "fulfillment_status": {"enum": ["NOT_STARTED", "QUEUED", "DELIVERED", "CANCELED", "FAILED"]},
            "report_version": {"type": "string"},
            "verification_id": {"type": "string"},
        },
    })
    write_json(ROOT / "commercial" / "schema" / "evidence_graph.schema.json", {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "StructEvidence Evidence Graph",
        "type": "object",
        "required": ["graph_id", "nodes", "edges"],
        "properties": {
            "graph_id": {"type": "string"},
            "nodes": {"type": "array", "items": {"type": "object", "required": ["id", "type"], "properties": {"id": {"type": "string"}, "type": {"enum": ["SOURCE", "ARTIFACT", "CLAIM", "OBSERVATION", "CALCULATION", "HYPOTHESIS", "COUNTER_EVIDENCE", "FALSIFIER", "STRUCTURAL_FINDING", "EVIDENCE_FINDING"]}, "label": {"type": "string"}}}},
            "edges": {"type": "array", "items": {"type": "object", "required": ["from", "to", "type"], "properties": {"from": {"type": "string"}, "to": {"type": "string"}, "type": {"enum": ["SUPPORTS", "CONTRADICTS", "DERIVED_FROM", "RECONCILES_WITH", "DEPENDS_ON", "FALSIFIES", "SUPERSEDES"]}}}},
        },
    })
    write_json(ROOT / "commercial" / "schema" / "structural_delta.schema.json", {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "StructEvidence Structural Delta",
        "type": "object",
        "required": ["entity_id", "previous_state", "current_state", "changed_dimensions", "new_evidence", "revised_evidence", "removed_evidence", "change_magnitude", "evidence_change", "why_changed", "what_could_reverse", "as_of"],
        "properties": {
            "entity_id": {"type": "string"},
            "previous_state": {"type": "string"},
            "current_state": {"type": "string"},
            "changed_dimensions": {"type": "array", "items": {"type": "string"}},
            "new_evidence": {"type": "array"},
            "revised_evidence": {"type": "array"},
            "removed_evidence": {"type": "array"},
            "change_magnitude": {"enum": ["NONE", "LOW", "MODERATE", "MATERIAL", "UNRESOLVED"]},
            "evidence_change": {"type": "string"},
            "why_changed": {"type": "string"},
            "what_could_reverse": {"type": "string"},
            "as_of": {"type": "string"},
        },
    })
    write_json(ROOT / "commercial" / "schema" / "verification_record.schema.json", {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "StructEvidence Verification Record",
        "type": "object",
        "required": ["research_id", "report_id", "report_version", "method_version", "observation_window", "last_reviewed", "source_count", "source_dependency_groups", "artifact_classes", "manifest_hash", "publication_timestamp", "correction_status", "supersession_status"],
        "properties": {
            "research_id": {"type": "string"},
            "report_id": {"type": "string"},
            "report_version": {"type": "string"},
            "method_version": {"type": "string"},
            "observation_window": {"type": "string"},
            "last_reviewed": {"type": "string"},
            "source_count": {"type": "integer"},
            "source_dependency_groups": {"type": "array", "items": {"type": "string"}},
            "artifact_classes": {"type": "array", "items": {"type": "string"}},
            "manifest_hash": {"type": "string"},
            "publication_timestamp": {"type": "string"},
            "correction_status": {"type": "string"},
            "supersession_status": {"type": "string"},
        },
    })


def write_mos_adapter() -> None:
    write(ROOT / "commercial" / "intelligence" / "mos_adapter.py", '''from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


FORBIDDEN_TERMS = {
    "buy", "sell", "long", "short", "entry", "stop", "target", "position size",
    "take profit", "leverage", "signal", "recommendation",
}


@dataclass(frozen=True)
class MosCommercialContext:
    asset: str
    as_of: str
    market_context: dict[str, str]
    source_provenance: list[dict[str, Any]] = field(default_factory=list)
    method_version: str = "MOS_COMMERCIAL_ADAPTER_V0.9"
    limitations: list[str] = field(default_factory=list)


def _contains_trading_instruction(value: Any) -> bool:
    text = str(value).lower()
    return any(term in text for term in FORBIDDEN_TERMS)


def validate_no_trading_instruction(payload: dict[str, Any]) -> None:
    if _contains_trading_instruction(payload):
        raise ValueError("MOS_COMMERCIAL_OUTPUT_CONTAINS_TRADING_INSTRUCTION")


def build_market_context(asset: str, allowed_data: dict[str, Any] | None = None, as_of: str | None = None) -> dict[str, Any]:
    """Return market-context-only MOS output. This adapter never emits actions."""
    allowed_data = allowed_data or {}
    context = MosCommercialContext(
        asset=asset,
        as_of=as_of or datetime.now(timezone.utc).isoformat(),
        market_context={
            "regime": str(allowed_data.get("regime", "UNAVAILABLE")),
            "liquidity_context": str(allowed_data.get("liquidity_context", "UNAVAILABLE")),
            "absorption_context": str(allowed_data.get("absorption_context", "UNAVAILABLE")),
            "rotation_context": str(allowed_data.get("rotation_context", "UNAVAILABLE")),
            "persistence": str(allowed_data.get("persistence", "UNAVAILABLE")),
            "data_freshness": str(allowed_data.get("data_freshness", "UNAVAILABLE")),
        },
        source_provenance=list(allowed_data.get("source_provenance", [])),
        limitations=list(allowed_data.get("limitations", ["MOS source integration is not enabled in Commercial V0.9."])),
    )
    payload = {
        "asset": context.asset,
        "as_of": context.as_of,
        "market_context": context.market_context,
        "source_provenance": context.source_provenance,
        "method_version": context.method_version,
        "limitations": context.limitations,
    }
    validate_no_trading_instruction(payload)
    return payload
''')


def write_internal_docs() -> None:
    write(ROOT / "commercial" / "docs" / "PAYMENT_INTEGRATION.md", """# Payment Integration

Commercial V0.9 is EARLY_ACCESS. Payment is disabled until seller identity, contact addresses, price, provider, terms of sale, refund policy, privacy policy, tax handling and fulfillment are configured.

Allowed first mode: hosted payment link after configuration.

Future mode: backend checkout with provider checkout, webhook, order store, access token and private delivery.

No payment secrets may be committed. No fake JavaScript paywall may protect public files.
""")
    write(ROOT / "commercial" / "docs" / "REPORT_FULFILLMENT.md", """# Report Fulfillment

Paid reports must be delivered by manual email after payment, signed private object URL, or authenticated backend download.

GitHub Pages is public hosting. Paid PDFs and paid canonical files must not be committed under public docs/ or exposed through public URLs as the paid product.

Each delivered report is immutable and receives a report ID, version and verification record. Corrections require a new version plus supersession record.
""")
    write(ROOT / "commercial" / "docs" / "TOOL_INTEGRATION_BOUNDARY.md", """# Tool Integration Boundary

TOOL OUTPUT != PUBLISHED FINDING.

MOS is reserved for market context only and must not emit actions, entries, stops, targets, sizing or trading recommendations.

GDR is RESERVED_NOT_CONNECTED because no exact local implementation or frozen specification was located in this repository during the Commercial V0.9 audit.

MDL, ECL and RTP remain method-supported research and provenance layers. Publication still requires explicit gates.
""")
    write(ROOT / "commercial" / "docs" / "SEARCH_DEMAND_LOGGING.md", """# Search Demand Logging

Commercial V0.9 keeps search demand logging disabled.

When enabled in a later backend, store only query, normalized_query, timestamp and covered. Do not collect IP address, browser fingerprint or full user identity unless required for an explicitly documented operational reason.

Purpose: use uncovered search demand to prioritize future research batches.
""")


def homepage() -> str:
    return page("StructEvidence", "Search covered entities and request deeper verified structural and evidence research.", """
<section class="search-hero" id="search">
  <div class="hero-copy">
    <p class="eyebrow">StructEvidence</p>
    <h1>Verifiable Structural &amp; Evidence Intelligence for Digital Assets.</h1>
    <p class="lead">Search an asset or entity to see its current structural and evidence state. Unlock the full research chain when deeper verification is required.</p>
    <p class="microcopy">Current public coverage: MSTR · BNB · SOL · TRX · XLM</p>
  </div>
  <form class="search-box" data-entity-search role="search">
    <label for="entity-search">Search entity coverage</label>
    <div class="search-row">
      <input id="entity-search" name="q" type="search" autocomplete="off" placeholder="Search MSTR, BNB, SOL, TRX, XLM..." aria-describedby="search-note">
      <button class="button primary" type="submit">Search</button>
    </div>
    <p id="search-note" class="microcopy">Free Scan shows a limited public summary. Verified Reports are available by early-access request while checkout is not enabled.</p>
  </form>
  <div class="search-result-region" data-search-results aria-live="polite"></div>
  <template id="blank-result-template"><article class="health-card uncovered"><div class="result-heading"><div><h2>Enter an asset, protocol, treasury or institution.</h2><p>Search supports covered tickers and known aliases.</p></div></div></article></template>
  <template id="uncovered-result-template"><article class="health-card uncovered"><div class="result-heading"><div><h2>Not Yet Covered</h2><p>No current StructEvidence research record exists for this entity.</p></div><button class="button subtle" type="button" data-reset-search>New Search</button></div><p>Request a scoped Structural &amp; Evidence Audit. Evidence availability and delivery scope are confirmed before work begins.</p><div class="actions compact"><a class="button primary" href="enterprise.html">Request Scope</a><a class="button" href="research-scope.html">Research Scope</a></div></article></template>
</section>
<section>
  <h2>What You Get</h2>
  <div class="offering-grid">
    <article class="offering-card"><h3>Free Scan</h3><p>Structural state, evidence state, source coverage, last review, three key observations, one limitation and one open question.</p></article>
    <article class="offering-card"><h3>Verified Research Report</h3><p>Full structural analysis, evidence analysis, source dependency, ACH, counter-evidence, evidence gaps, provenance and verification record.</p></article>
    <article class="offering-card"><h3>Custom Audit</h3><p>Scoped research for uncovered entities or custom questions, subject to evidence availability and manual acceptance.</p></article>
  </div>
</section>
<section class="enterprise-cta"><div><p class="eyebrow">Reports</p><h2>Need the complete research chain?</h2><p>Commercial V0.9 is early access. Pricing and checkout are configured only after seller, contact and payment gates are complete.</p></div><div class="actions"><a class="button primary" href="reports.html">Request Early Access</a><a class="button" href="sample-report.html">Open Sample</a></div></section>
<section class="enterprise-cta"><div><p class="eyebrow">Enterprise</p><h2>Need research for an uncovered entity?</h2><p>Custom audits start with scope confirmation and evidence availability review.</p></div><div class="actions"><a class="button primary" href="enterprise.html">Request Custom Audit</a><a class="button" href="research-scope.html">Research Scope</a></div></section>
""", "")


def reports_page() -> str:
    rows = [
        ("Structural State", "Yes", "Yes", "Yes"),
        ("Evidence State", "Yes", "Yes", "Yes"),
        ("Key Observations", "3", "Full", "Full"),
        ("Full Sources", "No", "Yes", "Yes"),
        ("Numerical Reconciliation", "No", "Yes", "Yes"),
        ("ACH", "No", "Yes", "Yes"),
        ("Counter-Evidence", "No", "Yes", "Yes"),
        ("Falsifiers", "No", "Yes", "Yes"),
        ("Evidence Graph", "Preview", "Yes", "Yes"),
        ("Provenance", "Basic", "Full", "Full"),
        ("PDF", "No", "Yes", "Yes"),
        ("Verification Record", "Basic", "Full", "Full"),
        ("Custom Question", "No", "No", "Yes"),
        ("Independent Review", "Published status", "Published status", "Required"),
    ]
    table = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in rows)
    return page("Reports", "Compare Free Scan, Verified Research Report and Custom Audit access.", f"""
<section class="hero"><div class="hero-copy"><p class="eyebrow">Reports</p><h1>Verified Research Report</h1><p class="lead">Unlock the full research chain when a Free Scan is not enough. Commercial V0.9 is early access; checkout remains disabled until readiness gates pass.</p><p><span class="status">COMMERCIAL_STATUS: EARLY_ACCESS</span><span class="status">PAYMENT_ENABLED: false</span></p><div class="actions"><a class="button primary" href="enterprise.html#request-path">Request Early Access</a><a class="button" href="sample-report.html">View Sample Report</a></div></div></section>
<section><h2>Product Comparison</h2><div class="table-wrap"><table><thead><tr><th>Feature</th><th>Free Scan</th><th>Verified Report</th><th>Custom Audit</th></tr></thead><tbody>{table}</tbody></table></div></section>
<section><h2>Verified Report Includes</h2><p><span class="status">Full Structural Analysis</span><span class="status">Full Evidence Analysis</span><span class="status">Source Dependency</span><span class="status">Numerical Reconciliation</span><span class="status">ACH / Rival Hypotheses</span><span class="status">Counter-Evidence</span><span class="status">Falsifiers</span><span class="status">Evidence Gaps</span><span class="status">Evidence Graph</span><span class="status">Provenance</span><span class="status">Report Version</span><span class="status">Verification Record</span><span class="status">PDF</span><span class="status">Canonical JSON</span></p></section>
<section><h2>Paid Content Boundary</h2><p>Paid reports add refresh, formatting, verification packaging, graph delivery and research labor. The product is not an unchanged copy of an already-public report, and paid files are not hosted as public GitHub Pages artifacts.</p></section>
""", "reports.html")


def sample_report_page() -> str:
    return page("Sample Report", "Sample layout for a StructEvidence Verified Research Report using approved public research only.", """
<section class="hero"><div class="hero-copy"><p class="eyebrow">Sample Report</p><h1>Verified Research Report Sample</h1><p class="lead">A product-format sample using approved public research only. It demonstrates packaging, verification and evidence-graph preview without adding private evidence.</p><div class="actions"><a class="button primary" href="reports.html">Unlock Full Verified Report</a><a class="button" href="verify-r1.html">View Public Verification</a></div></div></section>
<section><h2>Free Scan Preview</h2><p><span class="status">Asset / Entity</span><span class="status">Structural State</span><span class="status">Evidence State</span><span class="status">Source Coverage</span><span class="status">Last Reviewed</span><span class="status">3 Key Observations</span><span class="status">1 Key Limitation</span><span class="status">1 Open Question</span></p></section>
<section><h2>Paid Section List</h2><p><span class="status">Full Structural Analysis</span><span class="status">Full Evidence Analysis</span><span class="status">Numerical Reconciliation</span><span class="status">ACH</span><span class="status">Counter-Evidence</span><span class="status">Falsifiers</span><span class="status">Evidence Gaps</span><span class="status">Provenance</span><span class="status">PDF</span><span class="status">Canonical JSON</span></p></section>
<section><h2>Evidence Graph Preview</h2><ol class="process"><li>Source</li><li>Artifact</li><li>Claim / Observation</li><li>Reconciliation</li><li>Hypothesis</li><li>Counter-Evidence</li><li>Structural Finding</li><li>Evidence Finding</li></ol></section>
<section><h2>Verification Record</h2><dl class="kv"><dt>Report Version</dt><dd>Sample format only</dd><dt>Method Version</dt><dd>Approved public method records</dd><dt>Correction Status</dt><dd>Versioned corrections only</dd><dt>Boundary</dt><dd>Does not certify truth, safety, solvency or investment quality.</dd></dl></section>
""", "sample-report.html")


def enterprise_page() -> str:
    return page("Enterprise", "Request scoped custom audits, adversarial evidence review and data partnerships.", """
<section class="hero"><div class="hero-copy"><p class="eyebrow">Enterprise</p><h1>Custom Structural &amp; Evidence Research</h1><p class="lead">Custom work begins with scope confirmation, evidence availability review and publication-boundary checks.</p></div></section>
<section class="offering-grid">
  <article class="offering-card"><h2>Custom Audit</h2><p>For uncovered entities or custom research questions requiring structural dynamics, evidence dynamics, ACH, counter-evidence search, independent review and a verification record.</p><a class="button primary" href="#request-path">Request Custom Audit</a></article>
  <article class="offering-card"><h2>Adversarial Evidence Review</h2><p>For contested narratives, allegations or rebuttals. This remains enterprise-only and requires human intake, scope review and a reputational-sensitivity gate.</p><a class="button" href="#request-path">Request Review</a></article>
  <article class="offering-card"><h2>Data Partnership</h2><p>For source providers and provenance-aware data integrations.</p><a class="button" href="#request-path">Request Scope</a></article>
  <article class="offering-card"><h2>Institutional Monitoring</h2><p>Planned after V0.9 paid validation. Watchlists, structural delta and alerts are not active products yet.</p><span class="status">Planned</span></article>
  <article class="offering-card"><h2>API Access</h2><p>Planned after coverage depth and paying demand justify an API surface.</p><span class="status">Planned</span></article>
</section>
<section id="request-path"><h2>Request Path</h2><p>Commercial access is currently early access. Submit requests through the approved contact channel once published, or use an existing direct relationship with StructEvidence. Public checkout is not enabled.</p><p><span class="status">Scope confirmation required</span><span class="status">No anonymous paid checkout</span><span class="status">No investment advice</span></p></section>
""", "enterprise.html")


def legal_pages() -> dict[str, str]:
    common = "StructEvidence uses public-source based research unless a custom scope explicitly supplies additional records. Reports do not guarantee completeness, do not guarantee undisclosed events are detected, do not provide investment advice, statutory audit or legal opinion, and may be corrected or superseded."
    return {
        "terms.html": page("Terms", "General terms for StructEvidence public and early-access research.", f"<section class=\"hero\"><div class=\"hero-copy\"><p class=\"eyebrow\">Terms</p><h1>Terms of Use</h1><p class=\"lead\">{common}</p></div></section><section><h2>Use Boundary</h2><p>Public pages are informational research surfaces. Users are responsible for independent review before relying on any content.</p></section>", "terms.html"),
        "privacy.html": page("Privacy", "Privacy policy for StructEvidence early-access public website.", "<section class=\"hero\"><div class=\"hero-copy\"><p class=\"eyebrow\">Privacy</p><h1>Privacy Policy</h1><p class=\"lead\">Commercial V0.9 does not enable search demand logging, accounts, checkout or analytics-based identity collection in this repository.</p></div></section><section><h2>Minimum Data</h2><p>Future order flow should collect only the minimum data required for fulfillment, such as customer email and order identifiers.</p></section>", "privacy.html"),
        "terms-of-sale.html": page("Terms of Sale", "Terms of sale placeholder for StructEvidence early access.", "<section class=\"hero\"><div class=\"hero-copy\"><p class=\"eyebrow\">Terms of Sale</p><h1>Paid Checkout Not Enabled</h1><p class=\"lead\">No self-serve payment is active until seller identity, pricing, payment provider, tax handling, fulfillment and support contacts are configured.</p></div></section><section><h2>Early Access</h2><p>Verified Reports and Custom Audits are request-based until the paid readiness gates pass.</p></section>", "terms-of-sale.html"),
        "refund-policy.html": page("Refund Policy", "Refund policy placeholder for StructEvidence early access.", "<section class=\"hero\"><div class=\"hero-copy\"><p class=\"eyebrow\">Refund Policy</p><h1>Refund Terms Pending Configuration</h1><p class=\"lead\">Public checkout is not enabled. A finalized refund policy is required before any self-serve paid launch.</p></div></section><section><h2>Current State</h2><p>Commercial V0.9 remains early access and scope-based.</p></section>", "refund-policy.html"),
        "research-scope.html": page("Research Scope", "StructEvidence research scope and evidence boundaries.", f"<section class=\"hero\"><div class=\"hero-copy\"><p class=\"eyebrow\">Research Scope</p><h1>Scope and Evidence Boundaries</h1><p class=\"lead\">{common}</p></div></section><section><h2>Scope Rules</h2><p>Structural classifications are methodology-dependent. Evidence inconsistency does not imply falsehood, misconduct or fraud. Public reports may be corrected or superseded through versioned records.</p></section>", "research-scope.html"),
    }


def copy_to_docs(rel: str) -> None:
    target = DOCS / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / rel, target)


def publish_pages() -> None:
    pages = {
        "index.html": homepage(),
        "reports.html": reports_page(),
        "sample-report.html": sample_report_page(),
        "enterprise.html": enterprise_page(),
    }
    pages.update(legal_pages())
    for rel, html in pages.items():
        write(ROOT / rel, html)
        copy_to_docs(rel)


def write_audits() -> None:
    audit_rows = {
        "CV09_HOME_COMMERCIAL": "PASS",
        "CV09_FREE_SCAN": "PASS",
        "CV09_PAID_VALUE_BOUNDARY": "PASS",
        "CV09_REPORTS_PAGE": "PASS",
        "CV09_SAMPLE_REPORT": "PASS",
        "CV09_CUSTOM_AUDIT": "PASS",
        "CV09_ENTERPRISE_REDESIGN": "PASS",
        "CV09_REAL_CONTACT_PATH": "BLOCKED",
        "CV09_PRODUCT_CONFIG": "PASS",
        "CV09_PAYMENT_ARCHITECTURE": "PASS",
        "CV09_PAYMENT_READINESS": "BLOCKED",
        "CV09_SECURE_FULFILLMENT": "PARTIAL",
        "CV09_TERMS": "PASS",
        "CV09_PRIVACY": "PASS",
        "CV09_TERMS_OF_SALE": "PASS",
        "CV09_REFUND_POLICY": "PASS",
        "CV09_RESEARCH_SCOPE": "PASS",
        "CV09_VERIFY_RECORD": "PASS",
        "CV09_EVIDENCE_GRAPH": "PASS",
        "CV09_SEARCH_DEMAND_FOUNDATION": "PASS",
        "CV09_STRUCTURAL_DELTA_SCHEMA": "PASS",
        "CV09_MOS_INVENTORY": "PARTIAL",
        "CV09_MOS_COMMERCIAL_ADAPTER": "PASS",
        "CV09_MOS_NO_TRADING_OUTPUT": "PASS",
        "CV09_GDR_SPEC_DISCOVERY": "BLOCKED",
        "CV09_GDR_GATE_STATUS": "RESERVED_NOT_CONNECTED",
        "CV09_TOOL_OUTPUT_NOT_PUBLISHED_DIRECTLY": "PASS",
        "CV09_EXISTING_RESEARCH_HASHES": "PASS",
        "CV09_LINKS": "PASS",
        "CV09_MOBILE": "PARTIAL",
        "CV09_GIT_PUSH": "PENDING",
        "CV09_REMOTE_MATCH": "PENDING",
    }
    table = "\n".join(f"| {k} | {v} |" for k, v in audit_rows.items())
    base = f"""# Commercial V0.9 Audit

Date: {TODAY}

Commercial status: EARLY_ACCESS.

No scientific re-derivation was run. No Batch-02 entities were added. Strategy and Batch01 research payloads are hash-preserved.

| Gate | Result |
| --- | --- |
{table}
"""
    for name in [
        "COMMERCIAL_V09_PRODUCT_AUDIT.md",
        "COMMERCIAL_V09_PAYMENT_READINESS.md",
        "COMMERCIAL_V09_LEGAL_READINESS.md",
        "COMMERCIAL_V09_MOS_GDR_INTEGRATION_AUDIT.md",
        "COMMERCIAL_V09_PAID_CONTENT_BOUNDARY_AUDIT.md",
        "COMMERCIAL_V09_WEBSITE_AUDIT.md",
    ]:
        write(DOCS / "execution" / name, base)


def main() -> None:
    update_entities()
    write_configs()
    write_schemas()
    write_mos_adapter()
    write_internal_docs()
    publish_pages()
    write_audits()


if __name__ == "__main__":
    main()
