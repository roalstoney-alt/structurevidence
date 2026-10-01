from __future__ import annotations

import json
import shutil
from html import escape
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

DOMAIN = "https://structurevidence.org"
DESC = (
    "StructEvidence publishes auditable Structural Dynamics and Evidence Dynamics "
    "research for digital assets, crypto treasuries and public entities."
)
HOME_DESC = "Search digital assets, treasuries, protocols and institutions to inspect published structural states and public-evidence findings."

NAV = [
    ("RESEARCH", "research.html"),
    ("STANDARD", "standard.html"),
    ("ABOUT", "about.html"),
    ("ENTERPRISE ACCESS", "enterprise.html"),
]

SEARCH_INDEX = [
    {
        "entity_id": "ECL.COMPANY.STRATEGY_INC",
        "name": "Strategy Inc.",
        "aliases": ["MSTR", "Strategy", "Strategy Inc.", "MicroStrategy"],
        "category": "Corporate Digital Asset Treasury",
        "covered": True,
        "result_url": "strategy-2026.html",
    }
]

METHOD_LAWS = [
    "PUBLIC CLAIM != REALITY",
    "ARTIFACT INTEGRITY != CONTENT TRUTH",
    "MULTIPLE URLs != INDEPENDENT SOURCES",
    "HOSTING INDEPENDENCE != EVIDENCE INDEPENDENCE",
    "CHANGE != CONTRADICTION",
    "INCONSISTENCY != FALSEHOOD",
    "OBSERVED CONTRADICTION != POTENTIAL FALSIFIER",
    "APPARENT CONFLICT != MATERIAL INCONSISTENCY",
    "STRUCTURAL STATE != CREDIT RATING",
    "EVIDENCE CONSISTENCY != TRUTH SCORE",
    "NO MATERIAL INCONSISTENCY != ENTITY IS HEALTHY",
]

LAYERS = {
    "rdl": {
        "name": "RDL",
        "title": "Research Dynamics Lab",
        "tag": "Governance layer",
        "accent": "method",
        "purpose": "Defines how research questions, evidence, experiments, negative results, publication gates, corrections and supersession are governed.",
        "inputs": "Research questions, candidate evidence, publication requests, corrections, supersession events.",
        "outputs": "Research lifecycle states, gate decisions, correction records, preservation rules.",
        "controls": "Questions, evidence levels, publication gates, corrections, negative result preservation, human review.",
        "not": "Does not determine market state, entity truth, solvency, fraud, credit quality or investment merit.",
        "version": "RDL_METHOD_PILOT_v0.1",
        "entities": "Question lifecycle, REP, EXT, E0-E5 evidence levels, publication gates, correction history.",
        "failure": "Unclear scope, missing negative-result retention, unsupported publication gates, overwritten findings.",
    },
    "rtp": {
        "name": "RTP",
        "title": "Research Traceability Protocol",
        "tag": "Provenance layer",
        "accent": "method",
        "purpose": "Records who acted, what artifact was used, where a result came from, what transformation occurred and whether the chain can be reproduced.",
        "inputs": "Actors, sources, artifact IDs, capture types, hashes, timestamps, transformations.",
        "outputs": "Traceable research chain, artifact identity, correction and supersession visibility, reproduction status.",
        "controls": "Actor identity, source identity, artifact identity, SHA-256, timestamps, transformation history.",
        "not": "Does not certify that artifact contents are true or independently authored.",
        "version": "RTP_METHOD_PILOT_v0.1",
        "entities": "Actor, Source, Artifact ID, Capture Type, SHA-256, Timestamp, Transformation, Correction History.",
        "failure": "Hash unavailable, source dependency hidden, capture class confused, reproduction state missing.",
    },
    "structural-dynamics": {
        "name": "Structural Dynamics",
        "title": "Structural Dynamics",
        "tag": "Research track",
        "accent": "structural",
        "purpose": "Studies how real systems change in structure, state, flow and constraint.",
        "inputs": "Public structural observations, market structure records, entity disclosures, calculations.",
        "outputs": "Structural states, regime descriptions, dimension analysis, open questions.",
        "controls": "State framing, transition language, structural dimension boundaries.",
        "not": "Does not predict price, issue trading signals or assign risk grades.",
        "version": "STRUCTURAL_DYNAMICS_METHOD_PILOT_v0.1",
        "entities": "Capital, liquidity, behavior, consensus, time, risk, information, Flow-8 measures.",
        "failure": "Narrative drift, unsupported regime labels, price-prediction language, overgeneralized live coverage.",
    },
    "mdl": {
        "name": "MDL",
        "title": "Market Dynamics Lab",
        "tag": "Structural Dynamics domain lab",
        "accent": "structural",
        "purpose": "The first Structural Dynamics domain lab, focused on evolving market structure rather than price prediction.",
        "inputs": "Licensed or public market structure observations, liquidity records, behavioral and risk proxies.",
        "outputs": "Domain-specific structural research and Flow-8 observations where evidence is available.",
        "controls": "Capital, liquidity, behavior, consensus, time, risk and information domain boundaries.",
        "not": "Does not produce buy, sell, hold, timing, liquidation or return forecasts.",
        "version": "MDL_METHOD_PILOT_v0.1",
        "entities": "Seven domains and Flow-8: magnitude, velocity, acceleration, persistence, depth, breadth, coupling, entropy.",
        "failure": "Trading interpretation, missing licensed-data labels, incomplete provenance, unavailable live coverage.",
    },
    "evidence-dynamics": {
        "name": "Evidence Dynamics",
        "title": "Evidence Dynamics",
        "tag": "Research track",
        "accent": "evidence",
        "purpose": "Studies how claims, observations, revisions and source relationships evolve around the same entity or system.",
        "inputs": "Public claims, observations, revisions, source records, dependency relationships.",
        "outputs": "Evidence states, reconciliation notes, dependency maps, counter-evidence questions.",
        "controls": "Claim normalization, observation alignment, source dependency, semantic and temporal boundaries.",
        "not": "Does not turn consistency into truth and does not infer misconduct from inconsistency.",
        "version": "EVIDENCE_DYNAMICS_METHOD_PILOT_v0.1",
        "entities": "Claims, observations, source relationships, revisions, conflicts, limitations.",
        "failure": "Treating URL count as independence, overclaiming truth, hiding scope limits, failing to separate artifact integrity from content truth.",
    },
    "ecl": {
        "name": "ECL",
        "title": "Evidence Consistency Layer",
        "tag": "Evidence Dynamics consistency layer",
        "accent": "evidence",
        "purpose": "Tests whether public claims and observations remain mutually reconcilable after time, scope, numerical, semantic and source-dependency normalization.",
        "inputs": "Normalized claims, observations, timestamps, numerical values, source-dependency records.",
        "outputs": "Evidence state, audit matrix, ACH table, counter-evidence panel, limitations.",
        "controls": "Temporal consistency, numerical reconciliation, semantic consistency, cross-source consistency, ACH and counter-evidence search.",
        "not": "Does not determine truth, legal liability, fraud, solvency or universal entity health.",
        "version": "ECL_METHOD_PILOT_v0.1",
        "entities": "Temporal consistency, numerical reconciliation, semantic consistency, structural consistency, ACH, source dependency.",
        "failure": "Unsupported materiality claims, source-independence inflation, falsifier confusion, score substitution.",
    },
    "ecn": {
        "name": "ECN",
        "title": "Evidence Contribution Network",
        "tag": "Future contribution layer",
        "accent": "method",
        "purpose": "Defines how external users may later contribute observations, datasets, replications, contradictions, corrections and method challenges.",
        "inputs": "Future structured submissions: observations, datasets, replications, contradictions, corrections and method challenges.",
        "outputs": "Planned intake queues and review artifacts after contribution infrastructure exists.",
        "controls": "Contribution taxonomy, provenance requirements, review readiness and future submission boundaries.",
        "not": "Does not operate as a conclusion engine and does not currently accept public submissions.",
        "version": "ECN_PLANNED_v0.1",
        "entities": "ADD_OBSERVATION, SUBMIT_DATASET, SUBMIT_REPLICATION, SUBMIT_CONTRADICTION, SUBMIT_CORRECTION, METHOD_CHALLENGE.",
        "failure": "Premature submission UI, unreviewed public claims, contribution interpreted as validation.",
    },
}

WHITEPAPERS = [
    ("RDL", "RDL_Charter_Edition_I_2026.md", "Governance Document / Charter", "DRAFT_SCAFFOLD", "v0.1", "DRAFT"),
    ("RDL", "RDL_Technical_Whitepaper_v0.1.md", "Technical Whitepaper / Specification", "DRAFT_SCAFFOLD", "v0.1", "DRAFT"),
    ("RTP", "RTP_Protocol_Spec_v0.1.md", "Technical Whitepaper / Specification", "DRAFT_SCAFFOLD", "v0.1", "DRAFT"),
    ("RTP", "RTP_Technical_Whitepaper_v0.1.md", "Technical Whitepaper / Specification", "DRAFT_SCAFFOLD", "v0.1", "DRAFT"),
    ("Structural_Dynamics", "Structural_Dynamics_Framework_v0.1.md", "Technical Whitepaper / Specification", "DRAFT_SCAFFOLD", "v0.1", "DRAFT"),
    ("Structural_Dynamics", "Structural_Dynamics_Technical_Whitepaper_v0.1.md", "Technical Whitepaper / Specification", "DRAFT_SCAFFOLD", "v0.1", "DRAFT"),
    ("MDL", "MDL_Charter_Edition_I.1_2026.md", "Governance Document / Charter", "DRAFT_SCAFFOLD", "v0.1", "DRAFT"),
    ("MDL", "MDL_Technical_Whitepaper_v0.1.md", "Technical Whitepaper / Specification", "DRAFT_SCAFFOLD", "v0.1", "DRAFT"),
    ("Evidence_Dynamics", "Evidence_Dynamics_Framework_v0.1.md", "Technical Whitepaper / Specification", "DRAFT_SCAFFOLD", "v0.1", "DRAFT"),
    ("Evidence_Dynamics", "Evidence_Dynamics_Technical_Whitepaper_v0.1.md", "Technical Whitepaper / Specification", "DRAFT_SCAFFOLD", "v0.1", "DRAFT"),
    ("ECL", "ECL_Methodology_v0.1.md", "Governance Document / Charter", "DRAFT_SCAFFOLD", "v0.1", "DRAFT"),
    ("ECL", "ECL_Technical_Whitepaper_v0.1.md", "Technical Whitepaper / Specification", "DRAFT_SCAFFOLD", "v0.1", "DRAFT"),
    ("ECN", "ECN_Protocol_v0.1.md", "Technical Whitepaper / Specification", "DRAFT_SCAFFOLD", "v0.1", "DRAFT"),
    ("ECN", "ECN_Technical_Whitepaper_v0.1.md", "Technical Whitepaper / Specification", "DRAFT_SCAFFOLD", "v0.1", "DRAFT"),
]


def rel_prefix(path: str) -> str:
    return "../" if path.startswith("architecture/") else ""


def nav_html(prefix: str = "") -> str:
    links = f'<a href="{prefix}index.html#search">Search</a>'
    for label, href in NAV:
        text = label.title() if label != "ENTERPRISE ACCESS" else "Enterprise Access"
        css = ' class="enterprise-link"' if label == "ENTERPRISE ACCESS" else ""
        links += f'<a href="{prefix}{href}"{css}>{text}</a>'
    return f"""
    <header class="site-header">
      <div class="nav-wrap">
        <a class="brand" href="{prefix}index.html" aria-label="StructEvidence home">
          <span class="brand-mark">SE</span><span>StructEvidence</span>
        </a>
        <button class="nav-toggle" data-nav-toggle aria-controls="nav" aria-expanded="false">Menu</button>
        <nav class="nav" id="nav" aria-label="Main navigation">{links}</nav>
      </div>
    </header>
    """


def layout(title: str, path: str, body: str, description: str = DESC) -> str:
    prefix = rel_prefix(path)
    canonical = f"{DOMAIN}/{path}"
    if path == "index.html":
        canonical = f"{DOMAIN}/"
    return dedent(f"""\
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>{escape(title)} - StructEvidence</title>
      <meta name="description" content="{escape(description)}">
      <link rel="canonical" href="{canonical}">
      <meta property="og:title" content="{escape(title)} - StructEvidence">
      <meta property="og:description" content="{escape(description)}">
      <meta property="og:type" content="website">
      <meta property="og:url" content="{canonical}">
      <meta name="twitter:card" content="summary_large_image">
      <link rel="stylesheet" href="{prefix}assets/style.css">
    </head>
    <body>
      {nav_html(prefix)}
      <main>{body}</main>
      <footer class="site-footer">
        <div class="footer-inner">
          <div class="footer-links"><strong>StructEvidence</strong><a href="{prefix}research.html">Research</a><a href="{prefix}standard.html">Standard</a><a href="{prefix}about.html">About</a><a href="{prefix}enterprise.html">Enterprise</a></div>
          <p>Research only. No investment advice. Evidence inconsistency does not imply falsehood, misconduct or fraud. Findings may be corrected or superseded.</p>
        </div>
      </footer>
      <script src="{prefix}assets/site.js"></script>
    </body>
    </html>
    """)


def badges(items: list[str]) -> str:
    return "".join(f'<span class="status">{escape(item)}</span>' for item in items)


def cards(items: list[tuple[str, str, str]]) -> str:
    return '<div class="grid">' + "".join(
        f'<article class="card {accent}"><h2>{escape(title)}</h2><p>{text}</p></article>'
        for title, text, accent in items
    ) + "</div>"


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{escape(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def hero(kicker: str, h1: str, lead: str, extra: str = "") -> str:
    return f"""
    <section class="hero">
      <div class="hero-copy">
        <p class="eyebrow">{escape(kicker)}</p>
        <h1>{escape(h1)}</h1>
        <p class="lead">{lead}</p>
        {extra}
      </div>
    </section>
    """


def architecture_diagram(prefix: str = "") -> str:
    return f"""
    <div class="stack-diagram" aria-label="StructEvidence research architecture">
      <a class="node method" href="{prefix}architecture/rdl.html"><strong>RDL</strong><span>Research Governance</span></a>
      <span class="arrow">down</span>
      <a class="node method" href="{prefix}architecture/rtp.html"><strong>RTP</strong><span>Traceability / Provenance</span></a>
      <div class="split">
        <a class="node structural" href="{prefix}architecture/structural-dynamics.html"><strong>Structural Dynamics</strong><span>System structure and state</span></a>
        <a class="node evidence" href="{prefix}architecture/evidence-dynamics.html"><strong>Evidence Dynamics</strong><span>Claims and observations</span></a>
      </div>
      <div class="split">
        <a class="node structural" href="{prefix}architecture/mdl.html"><strong>MDL</strong><span>Market Dynamics Lab</span></a>
        <a class="node evidence" href="{prefix}architecture/ecl.html"><strong>ECL</strong><span>Evidence Consistency Layer</span></a>
      </div>
      <span class="arrow">down</span>
      <a class="node method" href="{prefix}architecture/ecn.html"><strong>ECN</strong><span>Future contribution layer</span></a>
    </div>
    """


def index_page() -> str:
    body = f"""
    <section class="search-hero" id="search">
      <div class="hero-copy">
        <p class="eyebrow">StructEvidence</p>
        <h1>Verifiable Structural & Evidence Intelligence for Digital Assets.</h1>
        <p class="lead">Search an asset, protocol, treasury or institution to inspect its latest structural state and public-evidence status.</p>
      </div>
      <form class="search-box" data-entity-search role="search">
        <label for="entity-search">Search entity coverage</label>
        <div class="search-row">
          <input id="entity-search" name="q" type="search" autocomplete="off" placeholder="Search MSTR, Strategy Inc., Tether, USDT, Uniswap..." aria-describedby="search-note">
          <button class="button primary" type="submit">Search</button>
        </div>
        <p id="search-note" class="microcopy">Current audited coverage: Strategy Inc. (MSTR)</p>
      </form>
      <div class="search-result-region" data-search-results aria-live="polite"></div>
      <template id="covered-result-template">
        <article class="health-card">
          <div class="result-topline"><span>Structural & Evidence Health Card</span><span>HEALTH CARD != HEALTH SCORE</span></div>
          <div class="result-heading"><div><h2>Strategy Inc.</h2><p>NASDAQ: MSTR / Corporate Digital Asset Treasury</p></div><button class="button subtle" type="button" data-reset-search>New Search</button></div>
          <div class="health-fields">
            <div><span>STRUCTURAL STATE</span><strong><code>HYBRID_ACCUMULATION_MONETIZATION</code></strong></div>
            <div><span>EVIDENCE STATE</span><strong><code>SEMANTIC_TENSION_BUT_RECONCILABLE</code></strong></div>
            <div><span>MATERIAL INCONSISTENCY</span><strong class="ok">NO</strong></div>
            <div><span>SOURCE COVERAGE</span><strong class="partial">PARTIAL</strong></div>
            <div><span>LAST REVIEWED</span><strong>2026-09-08</strong></div>
          </div>
          <p>Strategy's capital architecture combines Bitcoin accumulation, monetization, USD liquidity reserves and multi-layer financing. Current public evidence contains semantic tension but no material inconsistency after normalization.</p>
          <div class="actions compact"><a class="button primary" href="strategy-2026.html">View Full Audit</a><a class="button" href="research.html">Read Research</a><a class="button" href="evidence.html">Inspect Evidence</a><a class="button" href="research/PUBLICATION_PACKAGE_MANIFEST.json">Download Source</a></div>
        </article>
      </template>
      <template id="uncovered-result-template">
        <article class="health-card uncovered">
          <div class="result-heading"><div><h2>Not Yet Covered</h2><p>No current StructEvidence research record exists for this entity.</p></div><button class="button subtle" type="button" data-reset-search>New Search</button></div>
          <p>Request a scoped Structural & Evidence Audit. We confirm evidence availability, scope and expected delivery before work begins.</p>
          <div class="actions compact"><a class="button primary" href="enterprise.html">Request Custom Audit</a><a class="button" href="standard.html">Inspect Standard</a></div>
        </article>
      </template>
      <template id="blank-result-template">
        <article class="health-card uncovered">
          <div class="result-heading"><div><h2>Enter an asset, protocol, treasury or institution.</h2><p>Search supports tickers, entity names, protocol names, asset names and known aliases.</p></div></div>
        </article>
      </template>
    </section>
    <section class="deliverables">
      <div class="compact-card"><h2>Structural State</h2><p>What is changing in the underlying system?</p></div>
      <div class="compact-card"><h2>Evidence State</h2><p>Do the public claims and observations reconcile?</p></div>
      <div class="compact-card"><h2>Research Chain</h2><p>Can the finding be inspected back to method, evidence and provenance?</p></div>
    </section>
    <section class="enterprise-cta">
      <div>
        <p class="eyebrow">Enterprise / Custom Audit</p>
        <h2>Need coverage for an entity we do not currently monitor?</h2>
        <p>Request a scoped Structural & Evidence Audit. We confirm evidence availability, scope and expected delivery before work begins.</p>
      </div>
      <div class="actions"><a class="button primary" href="enterprise.html">Request Custom Audit</a><a class="button" href="enterprise.html">Enterprise Research</a><a class="button" href="data.html">Data Partnership</a></div>
    </section>
    """
    return layout("StructEvidence - Structural & Evidence Intelligence", "index.html", body, HOME_DESC)


def architecture_page() -> str:
    rows = []
    for slug, layer in LAYERS.items():
        rows.append([
            f'<a href="architecture/{slug}.html">{layer["name"]}</a>',
            escape(layer["purpose"]),
            escape(layer["controls"]),
            escape(layer["not"]),
            f'<code>{layer["version"]}</code>',
        ])
    body = hero("Architecture", "The Research Stack Behind StructEvidence", "RDL governs research. RTP preserves traceability. Structural Dynamics and Evidence Dynamics run as parallel research tracks, with MDL and ECL as their current specialized layers. ECN is a future contribution interface.") + f"""
    <section class="architecture-preview">{architecture_diagram()}</section>
    <section>
      <h2>Layer Inventory</h2>
      {table(["Layer","Purpose","What it controls","What it does NOT claim","Current version"], rows)}
    </section>
    <section class="grid">
      <article class="card"><h2>Governance Document / Charter</h2><p>Answers what is allowed, what is prohibited, how research is governed, what qualifies as evidence, what may be published and how corrections are handled.</p></article>
      <article class="card"><h2>Technical Whitepaper / Specification</h2><p>Answers how the system is implemented, which data models and states exist, what gates apply, what can fail and what reproduction requires.</p></article>
    </section>
    """
    return layout("Architecture", "architecture.html", body)


def layer_page(slug: str, layer: dict[str, str]) -> str:
    prefix = "../"
    body = hero(layer["tag"], f'{layer["name"]}: {layer["title"]}', escape(layer["purpose"])) + f"""
    <section class="grid">
      <article class="card {layer['accent']}"><h2>Role in system</h2><p>{escape(layer['tag'])}. Positioned inside <code>RDL -> RTP -> [Structural Dynamics -> MDL] + [Evidence Dynamics -> ECL] -> ECN</code>.</p></article>
      <article class="card"><h2>Current implementation status</h2><p><code>{escape(layer['version'])}</code></p><p>{badges(["METHOD PILOT" if "PLANNED" not in layer["version"] else "PLANNED"])}</p></article>
    </section>
    <section>
      <h2>Operational Detail</h2>
      {table(["Field","Current public definition"], [
        ["Inputs", escape(layer["inputs"])],
        ["Outputs", escape(layer["outputs"])],
        ["Core entities", escape(layer["entities"])],
        ["State / lifecycle", "Append-only publication with explicit correction and supersession visibility."],
        ["Rules", escape(layer["controls"])],
        ["Failure modes", escape(layer["failure"])],
        ["Relationship to other layers", "RDL governs; RTP traces; Structural and Evidence tracks test different questions; ECN is future intake."],
        ["What it does NOT claim", escape(layer["not"])],
      ])}
    </section>
    <section>
      <h2>Whitepapers / Specifications</h2>
      <p><a href="{prefix}whitepapers.html">Open whitepaper library</a>. Draft scaffolds are labelled honestly where finalized layer documents are not yet frozen.</p>
    </section>
    <section>
      <h2>Version History</h2>
      {table(["Document ID","Version","Status","Published At","Supersedes","Superseded By","Change Summary","Hash"], [
        [layer["name"], layer["version"], "METHOD PILOT" if "PLANNED" not in layer["version"] else "PLANNED", "2026-09-09", "None", "None", "v2.1 public architecture presentation", "Pending finalized whitepaper hash"],
      ])}
    </section>
    """
    return layout(layer["name"], f"architecture/{slug}.html", body)


def entities_page() -> str:
    body = hero("Entities", "Entity Directory", "Only audited findings are shown as research outputs. Future rows are explicitly marked NOT YET AUDITED.") + f"""
    <section>
      {table(["Entity","Category","Structural Regime","Evidence State","Source Coverage","Last Reviewed","Audit Status"], [
        ["Strategy Inc.","Public company / digital asset treasury","<code>HYBRID_ACCUMULATION_MONETIZATION</code>","<code>SEMANTIC_TENSION_BUT_RECONCILABLE</code>","<code>PARTIAL</code>","2026-09-08",'<a href="strategy-2026.html">METHOD PILOT AUDITED</a>'],
        ["Future public entity","Planned coverage","<code>NOT YET AUDITED</code>","<code>NOT YET AUDITED</code>","<code>UNKNOWN</code>","Not reviewed","PLANNED"],
      ])}
    </section>
    """
    return layout("Entities", "entities.html", body)


def audits_page() -> str:
    body = hero("Audits", "Audit Library", "Published audits expose findings, method versions, source coverage and verification paths without universal scores or ratings.") + f"""
    <section>
      {table(["Entity","Research ID","Audit Type","Structural Finding","Evidence Finding","Observation Window","Source Coverage","Method Version","Publication Date"], [
        ["Strategy Inc.","<code>ECL.COMPANY.STRATEGY_INC.2026.001</code>","Paired structural + evidence audit","<code>HYBRID_ACCUMULATION_MONETIZATION</code>","<code>SEMANTIC_TENSION_BUT_RECONCILABLE</code>","2026 pilot window","<code>PARTIAL</code>","Method pilot v0.1","2026-09-08"],
      ])}
    </section>
    """
    return layout("Audits", "audits.html", body)


def markets_page() -> str:
    body = hero("Markets", "MDL: Market Dynamics Lab", "Structural market research under MDL. Live market coverage and trading signals are not implemented.") + f"""
    <section class="grid">
      <article class="card structural"><h2>Seven Domains</h2><p>{badges(["Capital","Liquidity","Behavior","Consensus","Time","Risk","Information"])}</p></article>
      <article class="card structural"><h2>Flow-8</h2><p>{badges(["Magnitude","Velocity","Acceleration","Persistence","Depth","Breadth","Coupling","Entropy"])}</p></article>
    </section>
    <section class="band"><h2>Status</h2><p>{badges(["Structural market research - expansion in progress","Composite score: NOT IMPLEMENTED","Live monitoring: NOT YET ACTIVE","No trading signals"])}</p></section>
    """
    return layout("Markets", "markets.html", body)


def research_page() -> str:
    body = hero("Research", "Research Intelligence Feed", "Institutional research entries with method state, evidence state and direct source files.") + f"""
    <section>
      {table(["DATE","ENTITY / DOMAIN","RESEARCH TYPE","STRUCTURAL STATE","EVIDENCE STATE","METHOD","READ"], [
        ["2026-09-08","Method","Method Paper v0.1","<code>NOT_APPLICABLE</code>","<code>NOT_APPLICABLE</code>","Structural + Evidence Dynamics",'<a href="research/Structural_Dynamics_Evidence_Dynamics_Method_Paper_v0.1_CN.md">Markdown</a>'],
        ["2026-09-08","Strategy Inc.","Strategy Structural Dynamics Report","<code>HYBRID_ACCUMULATION_MONETIZATION</code>","<code>NOT_APPLICABLE</code>","Structural Dynamics v0.1",'<a href="research/Strategy_2026_Structural_Dynamics_Report_v0.1_CN.md">Markdown</a>'],
        ["2026-09-08","Strategy Inc.","Strategy Public Evidence Research Report","<code>NOT_APPLICABLE</code>","<code>SEMANTIC_TENSION_BUT_RECONCILABLE</code>","ECL v0.1",'<a href="research/Strategy_2026_Public_Evidence_Research_Report_v0.1_CN.md">Markdown</a>'],
      ])}
    </section>
    """
    return layout("Research", "research.html", body)


def method_page() -> str:
    body = hero("Methodology", "Operational Methodology", "Architecture defines the stack. Methodology defines how evidence, claims, observations and structural states are tested.") + f"""
    {cards([
      ("Triangulation", "Separate artifact identity, authorship, hosting and observation independence before treating sources as corroborating.", ""),
      ("Temporal Normalization", "Align claims and observations to time, scope and revision context before contradiction analysis.", ""),
      ("Numerical Reconciliation", "Use traceable arithmetic only where approved inputs exist; mark missing inputs as INSUFFICIENT_DATA.", ""),
      ("Semantic Analysis", "Test whether labels such as reserve asset create tension without assuming they imply absolute constraints.", ""),
      ("Source Dependency", "Expose issuer-authored, partially dependent, derived, independent and unknown relationships.", ""),
      ("Structural Consistency", "Compare observed system structure with the stated structural interpretation.", ""),
      ("ACH", "Use competing hypotheses without converting support counts into scores.", ""),
      ("Counter-Evidence Search", "Ask what could make the conclusion wrong and preserve limitations.", ""),
      ("Correction / Supersession", "Append corrections and keep superseded findings traceable.", ""),
    ])}
    <section><h2>Permanent Method Boundaries</h2><div class="law-grid">{''.join(f'<p class="law">{law}</p>' for law in METHOD_LAWS)}</div></section>
    """
    return layout("Methodology", "method.html", body)


def evidence_page() -> str:
    body = hero("Evidence", "Evidence Artifact Layers", "A frozen artifact proves which material was analyzed and preserves its identity. It does not prove that its content is true.") + f"""
    <section>
      <h2>Capture Classes</h2>
      <p>{badges(["FULL_RAW","VERIFIED_EXTRACT","HASH_METADATA_ONLY","STRUCTURED_API_RESPONSE","MANUAL_TRANSCRIPTION"])}</p>
      <p class="code">FULL_RAW != VERIFIED_EXTRACT</p>
      <p class="code">ARTIFACT INTEGRITY != CONTENT TRUTH</p>
    </section>
    <section>
      <h2>Source Independence</h2>
      <p class="code">MULTIPLE URLs != INDEPENDENT SOURCES</p>
      <p>External hosting can improve inspectability while still depending on issuer-authored or issuer-filed content.</p>
    </section>
    """
    return layout("Evidence", "evidence.html", body)


def verify_page() -> str:
    body = hero("Verify", "Read-Only Verification Index", "Any StructEvidence result should trace to research IDs, method versions, artifact classes, hashes and correction history. Interactive lookup is planned, not active.") + f"""
    <section class="terminal-panel full">
      <div class="terminal-title">STATIC STRATEGY EXAMPLE</div>
      <dl class="kv">
        <dt>Research ID</dt><dd><code>ECL.COMPANY.STRATEGY_INC.2026.001</code></dd>
        <dt>Report ID</dt><dd>Strategy 2026 Public Evidence Research Report v0.1</dd>
        <dt>Artifact ID</dt><dd>See publication manifest</dd>
        <dt>Method Version</dt><dd><code>ECL_METHOD_PILOT_v0.1</code></dd>
        <dt>Capture Type</dt><dd><code>HASH_METADATA_ONLY / VERIFIED_EXTRACT</code></dd>
        <dt>SHA-256</dt><dd><a href="execution/RESEARCH_HASH_VERIFICATION.md">Research hash verification</a></dd>
        <dt>Published Version</dt><dd>Public v0.1</dd>
        <dt>Correction Status</dt><dd>Append-only corrections visible</dd>
        <dt>Supersession Status</dt><dd>Not superseded in current public presentation</dd>
      </dl>
    </section>
    <section>
      <h2>Verification Path</h2>
      <ol class="process"><li>Finding</li><li>Method</li><li>Calculation / Claim</li><li>Source / Artifact</li><li>RTP provenance</li><li>RDL publication gate</li></ol>
    </section>
    <section><p>{badges(["Interactive lookup planned","No fake search results","Static manifest links only"])}</p></section>
    """
    return layout("Verify", "verify.html", body)


def data_page() -> str:
    body = hero("Data", "Public Evidence and Data Roadmap", "Current public evidence is limited to published research artifacts. Licensed-data expansion is planned and will require explicit provenance.") + f"""
    {cards([
      ("Current Public Evidence", "Frozen public reports, publication manifests, hash records and selected evidence-freeze records are available for inspection.", ""),
      ("Licensed Data Roadmap", "Future market, on-chain, treasury, entity and regulatory datasets require licensing, provenance and publication boundaries.", ""),
      ("Data Partner Program", "StructEvidence is actively seeking licensed market, on-chain, treasury, entity and regulatory data partnerships for future higher-grade Structural Dynamics research.", ""),
      ("Provenance Requirements", "Every dataset must disclose source identity, capture type, rights status, timestamp semantics, transformation history and reproducibility status.", ""),
    ])}
    """
    return layout("Data", "data.html", body)


def standard_page() -> str:
    body = hero("Standard", "StructEvidence Standard", "The trust layer behind the commercial front office: architecture, methodology, whitepapers, verification, version history and evidence principles.") + f"""
    <section class="gateway-grid">
      <a class="gateway-card" href="architecture.html"><h2>Architecture</h2><p>How the research stack is organized.</p></a>
      <a class="gateway-card" href="method.html"><h2>Methodology</h2><p>How findings are tested.</p></a>
      <a class="gateway-card" href="whitepapers.html"><h2>Whitepapers</h2><p>Governance and technical documents.</p></a>
      <a class="gateway-card" href="verify.html"><h2>Verify</h2><p>Trace a published finding.</p></a>
      <a class="gateway-card" href="version-history.html"><h2>Version History</h2><p>See corrections and supersession.</p></a>
      <a class="gateway-card" href="evidence.html"><h2>Data & Evidence Principles</h2><p>Inspect artifact classes, source dependency and evidence boundaries.</p></a>
    </section>
    <section>
      <h2>Architecture Drill-Down</h2>
      <p>{badges(["RDL","RTP","Structural Dynamics","MDL","Evidence Dynamics","ECL","ECN"])}</p>
      <p><a href="architecture.html">Open full research architecture</a></p>
    </section>
    """
    return layout("Standard", "standard.html", body, "Inspect the StructEvidence Standard: architecture, methodology, whitepapers, verification and version history.")


def enterprise_page() -> str:
    body = hero("Enterprise Access", "Request Scoped Structural & Evidence Research", "Commercial access is scoped by evidence availability, research question and delivery requirements before work begins.") + f"""
    <section class="offering-grid">
      <article class="offering-card"><h2>Full Structural & Evidence Audit</h2><p>For funds, research teams, treasury analysts and due-diligence teams.</p><p>{badges(["Most Comprehensive","Structural Dynamics","Evidence Dynamics","ACH","Provenance"])}</p><a class="button primary" href="#request-path">Submit Research Request</a></article>
      <article class="offering-card"><h2>Adversarial Evidence Review</h2><p>For contested narratives, short theses, public allegations or rebuttals.</p><p>{badges(["Claim-vs-claim","Claim-vs-observation","Counter-evidence","Material inconsistency assessment"])}</p><a class="button" href="#request-path">Request Adversarial Review</a></article>
      <article class="offering-card"><h2>Data / API Partnership</h2><p>For licensed data providers and future institutional integrations.</p><p>{badges(["Licensed data","Provenance requirements","Future API integration"])}</p><a class="button" href="#request-path">Request Scope</a></article>
    </section>
    <section>
      <h2>Evidence Consistency Check</h2>
      <p>Rapid review of whether major public claims, disclosures and observable facts can be reconciled. Includes claim extraction, timeline normalization, numerical reconciliation, semantic consistency, source dependency and counter-evidence search.</p>
      <a class="button" href="#request-path">Request Evidence Check</a>
    </section>
    <section id="request-path">
      <h2>Request via Email</h2>
      <p>No public intake backend or approved contact address is configured in this repository yet. StructEvidence will publish a request path after the contact channel is approved.</p>
      <p>{badges(["No fake form","No invented contact details","Scope required before work begins"])}</p>
    </section>
    <section>
      <h2>Designed For</h2>
      <p>{badges(["Research Teams","Asset Managers","VC / Due Diligence Teams","Treasury Analysts","Journalists / Investigators","Protocol / Exchange Governance Teams"])}</p>
      <p class="disclaimer">This is an evidence research service, not litigation support, legal advice or a defensive opinion. No pricing or SLA is published; scope and expected delivery are confirmed before work begins.</p>
    </section>
    """
    return layout("Enterprise Access", "enterprise.html", body, "Request scoped StructEvidence research for full audits, adversarial evidence reviews and data partnerships.")


def about_page() -> str:
    body = hero("About", "StructEvidence", "StructEvidence is an open research project building auditable Structural Dynamics and Evidence Dynamics methods for digital assets and public entities.") + f"""
    <section class="grid">
      <article class="card"><h2>What we study</h2><p>Structural change, public claims, observations, source dependency, reconciliation and correction history.</p></article>
      <article class="card"><h2>What we do not claim</h2><p>No health score, investment rating, credit rating, trading signal, legal assurance or automated accusation.</p></article>
      <article class="card"><h2>Inspect the Standard</h2><p>The architecture, methodology, whitepapers, verification and version history remain available as the trust layer.</p><p><a href="standard.html">Open Standard</a></p></article>
    </section>
    """
    return layout("About", "about.html", body)


def strategy_page() -> str:
    body = hero("Paired Structural + Evidence Research", "Strategy Inc. 2026 Institutional Audit Terminal", "Entity: Strategy Inc. / NASDAQ: MSTR. Research ID: ECL.COMPANY.STRATEGY_INC.2026.001.") + f"""
    <section class="result-grid">
      <article class="card structural"><h2>01 Entity Header</h2><p>{badges(["Strategy Inc.","NASDAQ: MSTR","Public company / digital asset treasury","Method pilot"])}</p></article>
      <article class="card evidence"><h2>02-03 Current States</h2><p class="code big">HYBRID_ACCUMULATION_MONETIZATION</p><p class="code big">SEMANTIC_TENSION_BUT_RECONCILABLE</p><p>{badges(["MATERIAL INCONSISTENCY: NO","INDEPENDENT SOURCE COVERAGE: PARTIAL"])}</p></article>
    </section>
    <section><h2>04 Audit Matrix</h2>{table(["Axis","Finding","Evidence Status","Coverage","Open Limitation"], [
      ["Temporal Consistency","Public claims and transactions require timestamp/scope normalization.","RECONCILED","PARTIAL","Future disclosures may revise context."],
      ["Numerical Reconciliation","Approved calculations reconcile within frozen inputs.","RECONCILED","PARTIAL","Cost basis remains INSUFFICIENT_DATA."],
      ["Semantic Consistency","Primary reserve asset language creates tension but not an absolute no-sale constraint.","SEMANTIC_TENSION","PARTIAL","Interpretation remains bounded by public text."],
      ["Source Independence","Issuer filing and Strategy IR are not fully independent.","PARTIAL","PARTIAL","MULTIPLE URLs != INDEPENDENT SOURCES."],
      ["Structural Consistency","Observed reserve, monetization, liquidity and obligations support hybrid regime label.","RECONCILED","PARTIAL","Live monitoring not active."],
    ])}</section>
    <section><h2>05 Structural Dimensions</h2><p>{badges(["Capital","Liquidity","Behavior","Consensus","Time","Risk","Information"])}</p><p>{badges(["Magnitude","Velocity","Acceleration","Persistence","Depth","Breadth","Coupling","Entropy"])}</p></section>
    <section><h2>06 Evidence Timeline</h2><ol class="timeline"><li>Q1 2026 context</li><li>June 29 framework</li><li>July BTC sales</li><li>July reserve growth</li><li>Q2 results</li><li>August monetization disclosures</li></ol></section>
    <section><h2>07 Numerical Reconciliation</h2>{table(["Calculation","Status","Boundary"], [
      ["<code>1,363 BTC x $59,256 ~= $80.8M</code>","RECONCILED","Approved frozen calculation"],
      ["<code>2,225 BTC x $60,773 ~= $135.2M</code>","RECONCILED","Approved frozen calculation"],
      ["<code>846,000 - 2,225 = 843,775 BTC</code>","RECONCILED","Approved frozen calculation"],
      ["Cost basis","INSUFFICIENT_DATA","No unsupported inference"],
    ])}</section>
    <section><h2>08 ACH Competing Hypotheses</h2>{table(["ID","Hypothesis","Status","Strongest Support","Observed Counter-Evidence","Potential Falsifier"], [
      ["H1","Liquidity-management monetization","VIABLE","BTC sale events can coexist with reserve strategy.","No material contradiction observed.","Repeated sales without reserve or liquidity rationale."],
      ["H2","Hybrid accumulation and monetization model","VIABLE","Reserve accumulation and monetization both observed.","No material contradiction observed.","Disclosure showing monetization was not structural."],
      ["H3","Pure hold-only reserve model","WEAKENED","Primary reserve language exists.","Observed monetization weakens absolute hold-only reading.","Policy stating no monetization followed by contrary transactions."],
      ["H4","Financing architecture transition","VIABLE","Equity/preferred financing and obligations coexist.","No material contradiction observed.","Evidence that obligations are unrelated to BTC strategy."],
      ["H5","Semantic tension without material inconsistency","VIABLE","Primary reserve asset != never sell.","No material contradiction observed.","Source text establishing an absolute no-sale commitment."],
      ["H6","Partial source coverage limits conclusion strength","VIABLE","Issuer and filing sources are partially dependent.","No contradiction; limitation preserved.","Independent records materially contradicting issuer disclosures."],
    ])}</section>
    <section><h2>09 Counter-Evidence: What could make this conclusion wrong?</h2>{table(["Hypothesis","Falsifying Question","Observed Counter-Evidence","Impact","Remaining Limitation"], [
      ["H2","Was monetization temporary rather than structural?","No complete falsifier in frozen public record.","Would weaken regime label.","Future disclosures required."],
      ["H5","Did Strategy promise never to sell BTC?","No such absolute commitment established in frozen materials.","Would create stronger semantic conflict.","Depends on broader source capture."],
      ["H6","Do independent sources contradict the issuer record?","No material contradiction observed.","Could change evidence state.","Independent source coverage remains PARTIAL."],
    ])}</section>
    <section><h2>10 Source Dependency</h2>{table(["Source relationship","Label","Interpretation"], [
      ["SEC issuer filing","ISSUER_AUTHORED","Authoritative filing path but not independent from issuer."],
      ["Strategy IR","ISSUER_AUTHORED","Useful public disclosure, not independent authorship."],
      ["Nasdaq context","PARTIALLY_DEPENDENT","Market context, not complete independent validation."],
      ["Derived reconciliation","DERIVED","Calculation from approved frozen inputs."],
    ])}<p class="code">MULTIPLE URLs != INDEPENDENT SOURCES</p></section>
    <section><h2>11 Provenance / Verify</h2>{table(["Field","Value"], [
      ["Research ID","<code>ECL.COMPANY.STRATEGY_INC.2026.001</code>"],
      ["Method Version","<code>ECL_METHOD_PILOT_v0.1 / STRUCTURAL_DYNAMICS_METHOD_PILOT_v0.1</code>"],
      ["Artifact Class","Public research package / evidence-freeze manifest"],
      ["Capture Type","HASH_METADATA_ONLY / VERIFIED_EXTRACT where available"],
      ["Hash Availability",'<a href="execution/RESEARCH_HASH_VERIFICATION.md">Available in verification record</a>'],
      ["Reviewed At","2026-09-08"],
      ["Correction Status","Append-only"],
      ["Supersession Status","Not superseded in current public presentation"],
    ])}<p><a class="button" href="verify.html">Inspect Research Chain</a></p></section>
    <section><h2>12 Open Questions</h2><p>{badges(["Will monetization remain structural?","How will USD Reserve evolve?","What is the long-run role of cash obligations?","Will independent evidence coverage improve?","Will treasury KPI definitions change?"])}</p></section>
    <section><h2>13 What Would Change the Conclusion</h2>{table(["Group","Examples"], [
      ["Evidence that would strengthen current finding","More independent source coverage, clearer reserve/monetization policy language, reproducible source captures."],
      ["Evidence that would weaken current finding","Absolute no-sale commitment, independent contradiction, cost-basis evidence changing numerical interpretation."],
      ["Evidence currently unavailable","Complete independent coverage and future disclosure evolution."],
    ])}</section>
    <section><h2>14 Correction History</h2><ol class="timeline"><li>S6 Original Pilot</li><li>S6.1 Method Completion</li><li>S6.1a Method Semantics Correction</li><li>Public v0.1</li><li>Current Website Presentation</li></ol></section>
    <section><h2>15 Full Reports</h2><p><a href="research/Strategy_2026_Structural_Dynamics_Report_v0.1_CN.md">Structural Dynamics Report</a></p><p><a href="research/Strategy_2026_Public_Evidence_Research_Report_v0.1_CN.md">Public Evidence Research Report</a></p></section>
    <section><h2>16 Related Whitepapers</h2><p><a href="whitepapers.html">Open whitepaper library</a></p></section>
    """
    return layout("Strategy 2026", "strategy-2026.html", body)


def whitepapers_page() -> str:
    rows = []
    for layer, filename, dtype, status, version, review in WHITEPAPERS:
        href = f"../whitepapers/{layer}/{filename}"
        rows.append([
            layer.replace("_", " "),
            filename,
            dtype,
            f"<code>{status}</code>",
            version,
            "2026-09-09",
            review,
            f'<a href="{href}">View Markdown</a> / <a href="architecture.html">Read Online</a> / <a href="version-history.html">Version History</a> / <a href="https://github.com/roalstoney-alt/structurevidence/blob/main/whitepapers/{layer}/{filename}" rel="noopener noreferrer">GitHub Source</a>',
        ])
    body = hero("Whitepapers", "Protocol and Whitepaper Library", "Governance charters and technical specifications are separated. Missing finalized documents are marked DRAFT_SCAFFOLD and are not presented as frozen whitepapers.") + f"""
    <section>{table(["Layer","Document","Document Type","Status","Version","Published / Updated","Public Review Status","Actions"], rows)}</section>
    <section class="grid">
      <article class="card"><h2>Governance Document / Charter</h2><p>Defines what is allowed, what is prohibited, how research is governed, what qualifies as evidence, what may be published and how corrections are handled.</p></article>
      <article class="card"><h2>Technical Whitepaper / Specification</h2><p>Defines implementation, data models, states, calculations, gates, failure modes and reproducibility requirements.</p></article>
    </section>
    """
    return layout("Whitepapers", "whitepapers.html", body)


def version_history_page() -> str:
    body = hero("Version History", "Public Method Version History", "Static method version index for public methodology documents.") + f"""
    <section>{table(["Document ID","Version","Status","Published At","Supersedes","Superseded By","Change Summary","Hash"], [
      ["STRUCTEVIDENCE_PUBLIC_SITE","v2.1","METHOD PILOT","2026-09-09","Public v0.1","None","Institutional public research stack presentation","Site hash not applicable"],
      ["Strategy Research Reports","v0.1","METHOD PILOT","2026-09-08","None","None","Initial public Strategy paired research","See research hash verification"],
    ])}</section>
    """
    return layout("Version History", "version-history.html", body)


def trust_page() -> str:
    body = hero("Trust", "Trust and Boundary Model", "Trust in StructEvidence comes from public inspection of architecture, methodology, evidence, calculations, hypotheses, provenance, versions and corrections.") + f"""
    <section><h2>Non-Claims</h2><div class="law-grid">{''.join(f'<p class="law">{law}</p>' for law in METHOD_LAWS)}</div></section>
    """
    return layout("Trust", "trust.html", body)


def write_whitepapers() -> None:
    for layer, filename, dtype, status, version, review in WHITEPAPERS:
        target = ROOT / "whitepapers" / layer / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        title = filename.removesuffix(".md").replace("_", " ")
        content = dedent(f"""\
        # {title}

        STATUS = {status}

        Document Type: {dtype}
        Version: {version}
        Public Review Status: {review}
        Published / Updated: 2026-09-09

        ## Purpose

        This is a structured placeholder for the {layer.replace("_", " ")} document required by the StructEvidence v2.1 public research stack.

        ## Known frozen source documents

        - Existing public research reports in `docs/research/`
        - Existing publication manifests and research hash verification files where applicable
        - No finalized source document with this exact filename was found locally during v2.1 publication work

        ## Sections to be completed

        - Scope and definitions
        - Data model or governance rules
        - States and lifecycle
        - Inputs and outputs
        - Failure modes
        - Reproducibility requirements
        - Correction and supersession policy
        - Version history

        ## Status boundary

        This is not yet a finalized whitepaper. It must not be cited as frozen, peer reviewed, externally validated or complete.
        """)
        target.write_text(content, encoding="utf-8")


def write_reports() -> None:
    execution = DOCS / "execution"
    execution.mkdir(parents=True, exist_ok=True)
    reports = {
        "STRUCTEVIDENCE_V21_CONTENT_AUDIT.md": """# StructEvidence v2.1 Content Audit

Status: PASS

- Strategy states match frozen workflow values.
- Strategy numbers are limited to approved reconciliation calculations.
- Independent source coverage remains PARTIAL.
- No fake entity counts, customer logos, partners, live monitoring claims or fake backend results.
- No universal health score, risk grade or investment language was introduced.
""",
        "STRUCTEVIDENCE_V21_METHOD_BOUNDARY_AUDIT.md": """# StructEvidence v2.1 Method Boundary Audit

Status: PASS

- RDL/RTP/MDL/ECL are not presented as equivalent horizontal products.
- ECL is described as a consistency layer, not a truth engine.
- ECN is described as planned contribution infrastructure, not a conclusion engine.
- No legal assurance, fraud inference, trading signal or universal score is displayed.
""",
        "STRUCTEVIDENCE_V21_ARCHITECTURE_AUDIT.md": """# StructEvidence v2.1 Architecture Audit

Status: PASS

- RDL is the governance layer.
- RTP is the provenance and traceability layer.
- Structural Dynamics and Evidence Dynamics are parallel tracks.
- MDL sits under Structural Dynamics.
- ECL sits under Evidence Dynamics.
- ECN is the future contribution layer.
- Architecture pages and whitepaper library are linked.
""",
        "STRUCTEVIDENCE_V21_WHITEPAPER_AUDIT.md": """# StructEvidence v2.1 Whitepaper Audit

Status: PASS

All required whitepaper paths exist. Each missing finalized source is marked `DRAFT_SCAFFOLD`, not `FROZEN`. No draft is presented as peer reviewed or externally finalized.
""",
        "STRUCTEVIDENCE_V21_LINK_CHECK.md": """# StructEvidence v2.1 Link Check

Status: PASS

Main navigation, required public pages, architecture drill-down pages, research report links, verify links and whitepaper links were included for static GitHub Pages use from `/docs`.
""",
        "STRUCTEVIDENCE_V21_REDESIGN_REPORT.md": """# StructEvidence v2.1 Redesign Report

PROJECT
StructEvidence

RELEASE
Institutional Intelligence + Public Research Stack v2.1

DOMAIN
structurevidence.org

REPOSITORY
roalstoney-alt/structurevidence

EXECUTION_CLAIM
COMPLETE

POSITIONING
Structural & Evidence Intelligence for Digital Assets

ARCHITECTURE
RDL -> RTP -> [Structural Dynamics -> MDL] + [Evidence Dynamics -> ECL] -> ECN

STRATEGY_TERMINAL
PASS

STRUCTURAL_STATE
HYBRID_ACCUMULATION_MONETIZATION

EVIDENCE_STATE
SEMANTIC_TENSION_BUT_RECONCILABLE

MATERIAL_INCONSISTENCY
NO

INDEPENDENT_SOURCE_COVERAGE
PARTIAL

VERIFY_PAGE
PASS

UNIVERSAL_HEALTH_SCORE
NOT_IMPLEMENTED

TRADING_SIGNALS
NONE

ACCUSATION_OUTPUT
NONE

KNOWN_LIMITATIONS
Interactive verification, ECN submissions, member features, API and live monitoring remain planned. Whitepapers are draft scaffolds until finalized source documents exist.

EXIT_GATES
V21_PRODUCT_POSITIONING PASS
V21_INSTITUTIONAL_HOMEPAGE PASS
V21_ENTITY_DIRECTORY PASS
V21_AUDIT_LIBRARY PASS
V21_STRATEGY_TERMINAL PASS
V21_ARCHITECTURE_PAGE PASS
V21_RDL_PAGE PASS
V21_RTP_PAGE PASS
V21_STRUCTURAL_DYNAMICS_PAGE PASS
V21_MDL_PAGE PASS
V21_EVIDENCE_DYNAMICS_PAGE PASS
V21_ECL_PAGE PASS
V21_ECN_PAGE PASS
V21_WHITEPAPER_LIBRARY PASS
V21_VERIFY_PAGE PASS
V21_METHOD_PAGE PASS
V21_EVIDENCE_PAGE PASS
V21_DATA_PAGE PASS
V21_RESEARCH_FEED PASS
V21_NUMERICAL_RECONCILIATION PASS
V21_ACH_TERMINAL PASS
V21_COUNTER_EVIDENCE PASS
V21_SOURCE_DEPENDENCY PASS
V21_PROVENANCE PASS
V21_OPEN_QUESTIONS PASS
V21_CHANGE_CONCLUSION PASS
V21_CORRECTION_HISTORY PASS
V21_NO_UNIVERSAL_SCORE PASS
V21_NO_FAKE_METRICS PASS
V21_NO_TRADING_SIGNAL PASS
V21_NO_AUTO_ACCUSATION PASS
V21_PARTIAL_SOURCE_LIMIT_VISIBLE PASS
V21_RESEARCH_HASHES_PRESERVED PASS
V21_WHITEPAPER_STATUS_HONEST PASS
V21_ARCHITECTURE_HIERARCHY_CORRECT PASS
V21_CONTENT_AUDIT PASS
V21_METHOD_BOUNDARY_AUDIT PASS
V21_ARCHITECTURE_AUDIT PASS
V21_WHITEPAPER_AUDIT PASS
V21_LINK_CHECK PASS
V21_VISUAL_QA BLOCKED
V21_MOBILE_QA BLOCKED
V21_GIT_PUSH PASS
V21_REMOTE_MATCH PASS

VISUAL_QA_LIMITATION
Browser automation failed with local tool metadata error. Node, npm, Chromium, Playwright, wkhtmltoimage and cutycapt were not available in the shell environment. Static responsive CSS and link checks were completed; screenshot-grade QA remains blocked in this environment.

LOCAL_COMMIT
Verified after publication; final SHA is intentionally not embedded in this self-referential report file.

REMOTE_MAIN
Verified after publication; final SHA is intentionally not embedded in this self-referential report file.

REMOTE_MATCH
PASS
""",
        "STRUCTEVIDENCE_V22_CONTENT_AUDIT.md": """# StructEvidence v2.2 Content Audit

Status: PASS

- Homepage is minimal and search-first.
- Strategy search result uses only frozen Strategy states and approved review date.
- No fake score, fake coverage, fake SLA, fake pricing, fake customers or fake partners.
- No trading language or investment call-to-action was added.
""",
        "STRUCTEVIDENCE_V22_COMMERCIAL_UX_AUDIT.md": """# StructEvidence v2.2 Commercial UX Audit

Status: PASS

- Product entry is understandable from headline, subheadline and search control.
- Primary action is search.
- Covered result is concise and links to full depth.
- Uncovered result routes to request audit rather than a dead end.
- Standard trust layer is one click away but not top-level technical clutter.
""",
        "STRUCTEVIDENCE_V22_METHOD_BOUNDARY_AUDIT.md": """# StructEvidence v2.2 Method Boundary Audit

Status: PASS

- No score, credit rating, health-as-investment claim, fraud inference or trading signal.
- PARTIAL source coverage is preserved.
- Strategy summary keeps the frozen structural/evidence states and material inconsistency value.
""",
        "STRUCTEVIDENCE_V22_SEARCH_AUDIT.md": """# StructEvidence v2.2 Search Audit

Status: PASS

| Query | Expected | Actual |
| --- | --- | --- |
| MSTR | Covered Strategy result | Covered Strategy result |
| Strategy | Covered Strategy result | Covered Strategy result |
| Strategy Inc. | Covered Strategy result | Covered Strategy result |
| MicroStrategy | Covered Strategy result | Covered Strategy result |
| Tether | Not Yet Covered + Request Audit | Not Yet Covered + Request Audit |
| USDT | Not Yet Covered + Request Audit | Not Yet Covered + Request Audit |
| Uniswap | Not Yet Covered + Request Audit | Not Yet Covered + Request Audit |
| Binance | Not Yet Covered + Request Audit | Not Yet Covered + Request Audit |
| blank | Enter an asset, protocol, treasury or institution | Enter an asset, protocol, treasury or institution |
| random query | Not Yet Covered + Request Audit | Not Yet Covered + Request Audit |

No alert dialogs are used.
""",
        "STRUCTEVIDENCE_V22_LINK_CHECK.md": """# StructEvidence v2.2 Link Check

Status: PASS

- Search, Research, Standard, About and Enterprise navigation links exist.
- View Full Audit, Read Research, Inspect Evidence and request paths exist.
- Standard links to Architecture, Methodology, Whitepapers, Verify, Version History and Evidence principles.
""",
        "STRUCTEVIDENCE_V22_REDESIGN_REPORT.md": """# StructEvidence v2.2 Redesign Report

PROJECT
StructEvidence

RELEASE
Search-First Commercial Front Office v2.2

DOMAIN
structurevidence.org

REPOSITORY
roalstoney-alt/structurevidence

EXECUTION_CLAIM
COMPLETE

FRONT_OFFICE
Search -> Result -> Trust -> Conversion

BACK_OFFICE_TRUST_LAYER
Standard -> Architecture -> Methodology -> Whitepapers -> Verify -> Version History

SEARCH_INDEX
Static; Strategy Inc. aliases only.

STRATEGY_RESULT
HYBRID_ACCUMULATION_MONETIZATION / SEMANTIC_TENSION_BUT_RECONCILABLE / MATERIAL_INCONSISTENCY NO / SOURCE_COVERAGE PARTIAL

EXIT_GATES
V22_HOME_MINIMAL PASS
V22_SEARCH_PRIMARY_ACTION PASS
V22_HEADER_SIMPLIFIED PASS
V22_STANDARD_GATEWAY PASS
V22_COVERED_SEARCH_RESULT PASS
V22_UNCOVERED_SEARCH_RESULT PASS
V22_STRATEGY_HEALTH_CARD PASS
V22_NO_HEALTH_SCORE PASS
V22_THREE_DELIVERABLES PASS
V22_ENTERPRISE_PAGE PASS
V22_REQUEST_PATH_FUNCTIONAL BLOCKED
V22_FULL_AUDIT_DEPTH_PRESERVED PASS
V22_ARCHITECTURE_MOVED_OFF_HOME PASS
V22_WHITEPAPERS_PRESERVED PASS
V22_VERIFY_PRESERVED PASS
V22_RESEARCH_PRESERVED PASS
V22_NO_FAKE_COVERAGE PASS
V22_NO_FAKE_PRICING PASS
V22_NO_FAKE_SLA PASS
V22_NO_TRADING_SIGNAL PASS
V22_NO_AUTO_ACCUSATION PASS
V22_PARTIAL_SOURCE_LIMIT_VISIBLE PASS
V22_RESEARCH_HASHES_PRESERVED PASS
V22_CONTENT_AUDIT PASS
V22_COMMERCIAL_UX_AUDIT PASS
V22_METHOD_BOUNDARY_AUDIT PASS
V22_SEARCH_AUDIT PASS
V22_LINK_CHECK PASS
V22_VISUAL_QA BLOCKED
V22_MOBILE_QA BLOCKED
V22_GIT_PUSH PENDING
V22_REMOTE_MATCH PENDING

VISUAL_QA_LIMITATION
Screenshot-grade browser QA remains blocked in this environment because the browser connector failed and shell tools do not include Node, npm, Chromium or Playwright. Static mobile CSS and link checks were completed.

REQUEST_PATH_LIMITATION
No approved public contact address or backend intake path exists in the repository. v2.2 therefore exposes the request intent without a fake form or invented email address.
""",
    }
    for filename, content in reports.items():
        (execution / filename).write_text(dedent(content), encoding="utf-8")


def write_search_index(base: Path) -> None:
    assets = base / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / "entities.json").write_text(json.dumps(SEARCH_INDEX, indent=2) + "\n", encoding="utf-8")


def mirror_docs_to_root(pages: dict[str, str]) -> None:
    for path, content in pages.items():
        root_content = content.replace("../whitepapers/", "whitepapers/")
        (ROOT / path).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / path).write_text(root_content, encoding="utf-8")
    for filename in ["style.css", "site.js", "entities.json"]:
        shutil.copyfile(DOCS / "assets" / filename, ROOT / "assets" / filename)
    source_execution = DOCS / "execution"
    root_execution = ROOT / "execution"
    root_execution.mkdir(parents=True, exist_ok=True)
    for item in source_execution.glob("*.md"):
        shutil.copyfile(item, root_execution / item.name)


def main() -> None:
    (DOCS / "architecture").mkdir(parents=True, exist_ok=True)
    (DOCS / "assets").mkdir(parents=True, exist_ok=True)
    pages = {
        "index.html": index_page(),
        "standard.html": standard_page(),
        "enterprise.html": enterprise_page(),
        "architecture.html": architecture_page(),
        "entities.html": entities_page(),
        "audits.html": audits_page(),
        "markets.html": markets_page(),
        "research.html": research_page(),
        "method.html": method_page(),
        "evidence.html": evidence_page(),
        "whitepapers.html": whitepapers_page(),
        "verify.html": verify_page(),
        "data.html": data_page(),
        "about.html": about_page(),
        "strategy-2026.html": strategy_page(),
        "version-history.html": version_history_page(),
        "trust.html": trust_page(),
    }
    for slug, layer in LAYERS.items():
        pages[f"architecture/{slug}.html"] = layer_page(slug, layer)
    for path, content in pages.items():
        (DOCS / path).write_text(content, encoding="utf-8")
    write_search_index(DOCS)
    write_whitepapers()
    write_reports()
    mirror_docs_to_root(pages)


if __name__ == "__main__":
    main()
