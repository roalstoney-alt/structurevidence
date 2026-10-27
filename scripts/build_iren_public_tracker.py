#!/usr/bin/env python3
"""Build the public-safe IREN tracker page and JSON projection.

The source registry, tracker dataset, and append-only event ledger are the
authoritative inputs. This builder does not fetch sources or publish anything.
"""

from __future__ import annotations

import hashlib
import html
import json
import shutil
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "cases" / "iren-ai-cloud-transition"


def load(name: str) -> dict:
    return json.loads((CASE / name).read_text(encoding="utf-8"))


def canonical_sha256(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate(tracker: dict, registry: dict, ledger: dict) -> None:
    source_ids = {source["source_id"] for source in registry["sources"]}
    event_ids = {event["event_id"] for event in ledger["events"]}
    row_ids: set[str] = set()
    for row in tracker["rows"]:
        assert row["row_id"] not in row_ids, f"duplicate row_id: {row['row_id']}"
        row_ids.add(row["row_id"])
        assert row["section"] in {"SUPPORTED_AS_ATTRIBUTED", "NOT_ESTABLISHED"}
        assert row["source_ids"], f"missing sources: {row['row_id']}"
        assert set(row["source_ids"]) <= source_ids, f"unknown source: {row['row_id']}"
        assert row["last_event_id"] in event_ids, f"unknown event: {row['row_id']}"
        assert row["pinpoint_locators"], f"missing pinpoint locator: {row['row_id']}"
        assert row["reading_check"] in tracker["reading_check_policy"]["result_vocabulary"]
        if row["state"] == "NOT_ESTABLISHED":
            assert row["plain_language"].startswith("Not shown in the sources reviewed")
        parsed = urlparse(row["challenge_url"])
        assert parsed.scheme == "https" and parsed.netloc == "structevidence.com"
        assert parsed.path == "/verify/"
        query = parse_qs(parsed.query)
        assert set(query) == {"case_id", "claim_id"}
        assert query["case_id"] == [tracker["case_id"]]
        assert query["claim_id"] == [row["row_id"]]
        assert row["next_check"].strip()
    allowed_release_states = {
        ("PENDING_HUMAN_REVIEW", "READY_FOR_HUMAN_PUBLICATION_REVIEW"),
        ("OWNER_AUTHORIZED_PUBLICATION", "PUBLICATION_AUTHORIZED_FOR_EXACT_SHA"),
    }
    assert (tracker["reviewer_status"], tracker["publication_status"]) in allowed_release_states
    if tracker["reviewer_status"] == "OWNER_AUTHORIZED_PUBLICATION":
        assert tracker.get("approval_record")
        assert (CASE / tracker["approval_record"]).is_file()
    assert ledger["append_only"] is True
    assert tracker["current_page_revision"] == ledger["events"][-1]["event_id"]


def humanize_code(value: str) -> str:
    labels = {
        "CAPTURED": "Captured",
        "RETRIEVAL_INCOMPLETE_HTTP_403": "Retrieval incomplete (HTTP 403)",
        "METADATA_VERIFIED_BODY_RETRIEVAL_INCOMPLETE_HTTP_403": "Metadata verified; body retrieval incomplete (HTTP 403)",
        "CONFIRMED_ON_ISSUER_INVESTOR_NEWS_INDEX": "Confirmed on issuer news index",
        "TARGET_NOT_COMPLETION": "Target only — not completion",
        "OPEN": "Open",
        "AGREED_WITH_SOURCE_NATIVE_WORDING_AND_BOUNDARY": "Agreed with source-native wording and boundary",
        "AGREED_WITH_BOUNDED_ABSENCE_STATE": "Agreed with bounded absence state",
    }
    return labels.get(value, value.replace("_", " ").lower())


def source_projection(source: dict) -> dict:
    allowed = {
        "source_id", "publisher", "title", "url", "accession", "publication_date",
        "source_type", "dependency_class", "assurance", "liability", "access_state",
        "capture_utc", "sha256", "review_state",
    }
    return {key: source[key] for key in source if key in allowed}


def render_source_links(source_ids: list[str], sources: dict[str, dict]) -> str:
    links = []
    for source_id in source_ids:
        source = sources[source_id]
        suffix = f" · {html.escape(source['accession'])}" if source.get("accession") else ""
        links.append(
            f'<a href="{html.escape(source["url"])}" rel="noopener noreferrer">'
            f'{html.escape(source_id)}</a>{suffix}'
        )
    return " · ".join(links)


def render_row(row: dict, sources: dict[str, dict], reading_policy: dict) -> str:
    state_class = "supported" if row["state"] == "SUPPORTED_AS_ATTRIBUTED" else "not-established"
    hashes = []
    for source_id in row["source_ids"]:
        digest = sources[source_id].get("sha256")
        hashes.append(f"{source_id}: {digest[:12]}…" if digest else f"{source_id}: capture incomplete")
    source_classes = []
    for source_id in row["source_ids"]:
        source = sources[source_id]
        source_class = f"{humanize_code(source['assurance'])} / {humanize_code(source['liability'])}"
        if source_class not in source_classes:
            source_classes.append(source_class)
    assurance = (
        "N/A — bounded absence claim. Reviewed sources: " + " · ".join(source_classes)
        if row["state"] == "NOT_ESTABLISHED"
        else " · ".join(source_classes)
    )
    locators = "<br>".join(html.escape(locator) for locator in row["pinpoint_locators"])
    plain_language = (
        f'\n        <p class="plain-absence"><strong>Plain language:</strong> {html.escape(row["plain_language"])}</p>'
        if row.get("plain_language") else ""
    )
    return f"""
      <article class="tracker-row" id="{html.escape(row['row_id'])}" data-row-id="{html.escape(row['row_id'])}">
        <div class="row-head"><code>{html.escape(row['row_id'])}</code><span class="state {state_class}">{html.escape(row['state'].replace('_', ' '))}</span></div>
        <h3>{html.escape(row['claim'])}</h3>
        <p class="boundary"><strong>Boundary:</strong> {html.escape(row['boundary'])}</p>{plain_language}
        <dl class="row-meta row-core">
          <div><dt>Sources</dt><dd>{render_source_links(row['source_ids'], sources)}</dd></div>
          <div><dt>Pinpoint</dt><dd>{locators}</dd></div>
          <div><dt>Next check</dt><dd>{html.escape(row['next_check'])}</dd></div>
        </dl>
        <details class="row-audit"><summary>Verify this row</summary><dl class="row-meta">
          <div><dt>Claim assurance</dt><dd>{html.escape(assurance)}</dd></div>
          <div><dt>Capture</dt><dd>{html.escape(' · '.join(hashes))}</dd></div>
          <div><dt>Check method</dt><dd>{html.escape(humanize_code(reading_policy['method']))}</dd></div>
          <div><dt>Reading checked</dt><dd>{html.escape(humanize_code(row['reading_check']))} · {html.escape(reading_policy['checked_at_utc'])}</dd></div>
        </dl><p>{html.escape(reading_policy['independence_boundary'])}</p></details>
        <a class="challenge-link" href="{html.escape(row['challenge_url'])}">Challenge {html.escape(row['row_id'])}</a>
      </article>"""


def build() -> None:
    tracker = load("tracker-v0.1.json")
    registry = load("source-registry-v0.1.json")
    ledger = load(tracker.get("event_ledger", "events-v0.1.json"))
    validate(tracker, registry, ledger)

    sources = {source["source_id"]: source for source in registry["sources"]}
    public_sources = [source_projection(source) for source in registry["sources"]]
    snapshot = {
        "schema_version": "SE-IREN-PUBLIC-SNAPSHOT-v0.1",
        "case_id": tracker["case_id"],
        "current_state": "SUPPORTED_AS_ATTRIBUTED_WITH_OPEN_BOUNDARIES",
        "tracker_data_version": tracker["tracker_data_version"],
        "evidence_cutoff": tracker["evidence_cutoff"],
        "last_source_check_utc": tracker["last_source_check_utc"],
        "next_source_check": tracker["next_source_check"],
        "reviewer_status": tracker["reviewer_status"],
        "reviewed_by": tracker.get("reviewed_by"),
        "reviewed_at_utc": tracker.get("reviewed_at_utc"),
        "publication_status": tracker["publication_status"],
        "approval_record": tracker.get("approval_record"),
        "approved_candidate_head_sha": tracker.get("approved_candidate_head_sha"),
        "notices": tracker["notices"],
        "rows": tracker["rows"],
        "watch_items": tracker["watch_items"],
        "sources": public_sources,
        "events": ledger["events"],
        "history": [event["event_id"] for event in ledger["events"]],
        "commercial_boundary": tracker["commercial_boundary"],
        "current_page_revision": tracker["current_page_revision"],
        "editorial_update_authorization": tracker.get("editorial_update_authorization"),
        "editorial_updated_at_utc": tracker.get("editorial_updated_at_utc"),
        "reading_check_policy": tracker["reading_check_policy"],
        "computed_metrics": tracker["computed_metrics"],
        "context_notes": tracker["context_notes"],
    }
    snapshot["content_digest"] = "sha256:" + canonical_sha256(snapshot)
    (CASE / "index.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    supported = "".join(
        render_row(row, sources, tracker["reading_check_policy"])
        for row in tracker["rows"] if row["section"] == "SUPPORTED_AS_ATTRIBUTED"
    )
    not_established = "".join(
        render_row(row, sources, tracker["reading_check_policy"])
        for row in tracker["rows"] if row["section"] == "NOT_ESTABLISHED"
    )
    watch = "".join(
        f"<tr><td><code>{html.escape(item['watch_id'])}</code></td><td>{html.escape(item['item'])}</td>"
        f"<td>{html.escape(item['date_or_window'])}</td><td>{html.escape(humanize_code(item['status']))}</td>"
        f"<td>{html.escape(item['what_to_check'])}</td></tr>" for item in tracker["watch_items"]
    )
    events = "".join(
        f"<li id=\"{html.escape(event['event_id'])}\"><div><code>{html.escape(event['event_id'])}</code> "
        f"<strong>{html.escape(event['event_type'].replace('_', ' '))}</strong></div>"
        f"<p>{html.escape(event['reason'])}</p><small>{html.escape(event['recorded_at_utc'])} · "
        f"{html.escape(event['event_digest'])}</small></li>" for event in ledger["events"]
    )
    provenance = "".join(
        f"<tr><td><a href=\"{html.escape(source['url'])}\">{html.escape(source['source_id'])}</a></td>"
        f"<td>{html.escape(source['title'])}</td><td>{html.escape(humanize_code(source['dependency_class']))}</td>"
        f"<td>{html.escape(humanize_code(source['liability']))}</td><td><span title=\"Raw JSON: {html.escape(source['access_state'])}\">{html.escape(humanize_code(source['access_state']))}</span></td>"
        f"<td><code>{html.escape(source['sha256'][:16] + '…' if source.get('sha256') else 'not captured')}</code></td></tr>"
        for source in registry["sources"]
    )
    context_notes = "".join(
        f'<article class="context-note"><p class="eyebrow">{html.escape(note["context_id"])}</p>'
        f'<h3>{html.escape(note["title"])}</h3><p>{html.escape(note["statement"])}</p>'
        f'<p class="boundary"><strong>Pinpoint:</strong> {html.escape(note["locator"])}</p>'
        f'<p class="boundary"><strong>Boundary:</strong> {html.escape(note["boundary"])}</p>'
        f'<p><strong>Sources:</strong> {render_source_links(note["source_ids"], sources)}</p></article>'
        for note in tracker["context_notes"]
    )
    metric = tracker["computed_metrics"][0]
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": tracker["title"],
        "description": "Evidence-bounded public tracker separating issuer-attributed disclosures from facts not established in the reviewed source set.",
        "dateModified": tracker["evidence_cutoff"],
        "url": "https://structurevidence.org/cases/iren-ai-cloud-transition/",
        "creator": {"@type": "Organization", "name": "StructEvidence", "url": "https://structurevidence.org/"},
    }, ensure_ascii=False, separators=(",", ":"))

    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>IREN AI Cloud Evidence Tracker | StructEvidence</title>
  <meta name="description" content="Evidence-bounded IREN AI Cloud transition tracker with source provenance, attributed claims, open unknowns, dated checks, and append-only change history.">
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <link rel="canonical" href="https://structurevidence.org/cases/iren-ai-cloud-transition/">
  <meta property="og:title" content="IREN AI Cloud Evidence Tracker">
  <meta property="og:description" content="Issuer-attributed disclosures kept separate from delivery, recognized revenue, cash collection, and economic-return unknowns.">
  <meta property="og:type" content="article">
  <meta property="og:url" content="https://structurevidence.org/cases/iren-ai-cloud-transition/">
  <script type="application/ld+json">{jsonld}</script>
  <link rel="stylesheet" href="/assets/product.css?v=20261001-gravity">
  <link rel="alternate" type="application/atom+xml" title="StructEvidence material-change feed" href="/feed.xml">
  <link rel="stylesheet" href="/assets/iren-tracker.css?v=20261028-verify-your-verify">
</head>
<body class="product-site iren-tracker"><a class="skip-link" href="#main">Skip to content</a>
<header class="product-header"><nav class="product-nav" aria-label="Primary navigation"><a class="product-brand" href="/"><span>SE</span><strong>StructEvidence</strong></a><button class="product-nav-toggle" type="button" aria-expanded="false" aria-controls="product-links" data-product-nav-toggle>Menu</button><div class="product-links" id="product-links"><a aria-current="page" href="/cases/">Evidence Cases</a><a href="/gaps/">Open Evidence Gaps</a><a href="https://structevidence.com/verify/?case_id=SE-IREN-AI-CLOUD-001">Verify a Claim</a><a href="https://structevidence.com/decision-pack/?case_id=SE-IREN-AI-CLOUD-001">Decision Pack</a><a href="/method.html">Method</a></div></nav></header>
<main class="product-main" id="main"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">StructEvidence</a><span>›</span><a href="/cases/">Cases</a><span>›</span><span aria-current="page">IREN AI Cloud transition</span></nav>
  <section class="page-hero case-hero tracker-hero" aria-labelledby="case-title">
    <p class="eyebrow">Public research tracker · {html.escape(tracker['case_id'])} · {html.escape(tracker['tracker_data_version'])}</p>
    <h1 id="case-title">IREN Limited: AI Cloud transition, without collapsing the evidence chain.</h1>
    <p class="lead">Which milestones are supported by dated issuer disclosures—and where do contract value, delivery, customer acceptance, ARR, recognized revenue, cash collection, and economic returns remain distinct?</p>
    <div class="quick-read" aria-labelledby="quick-read-title"><div class="quick-read-copy"><p class="eyebrow">30-second read</p><h2 id="quick-read-title">A contract, an acceptance statement, revenue, and cash are four different observations.</h2><p>The sources support a $9.7bn headline Microsoft contract value, an IREN-authored statement that Horizon 1 was accepted, and $128.8m of FY26 AI Cloud revenue across IREN’s customer base. They do not establish that the headline value became recognized revenue or that it was collected in cash.</p></div><div class="evidence-ladder" aria-label="Evidence ladder from contract to cash"><div><span>1 · Contract</span><strong>$9.7bn headline</strong><small>Issuer disclosure · supported as attributed</small></div><i aria-hidden="true">→</i><div><span>2 · Acceptance</span><strong>Horizon 1</strong><small>Issuer-reported · no Microsoft-authored record captured</small></div><i aria-hidden="true">→</i><div><span>3 · Revenue</span><strong>$128.8m FY26</strong><small>AI Cloud total · not attributed to Microsoft</small></div><i aria-hidden="true">→</i><div class="ladder-open"><span>4 · Cash</span><strong>Not established</strong><small>Full $9.7bn collection not shown</small></div></div><p class="ladder-boundary">This visual explains the evidence separation. The formal D0–D4 rubric remains proposed and is not applied to rows until its definitions and adoption are separately approved.</p></div>
    <div class="review-hold review-authorized" role="status"><strong>Publication authorization:</strong> The initial release was owner-authorized; this editorial and provenance update was requested by the authenticated task owner and recorded in IREN-EV-005. Separate financial, legal, privacy, and row-level reviewer identities are not claimed.</div>
    <details class="case-audit"><summary>Technical record and review boundary</summary><dl class="case-facts">
      <div><dt>Evidence cutoff</dt><dd>{html.escape(tracker['evidence_cutoff'])}</dd></div>
      <div><dt>Last source check</dt><dd>{html.escape(tracker['last_source_check_utc'])}</dd></div>
      <div><dt>Next source check</dt><dd>{html.escape(tracker['next_source_check'])}</dd></div>
      <div><dt>Rubric</dt><dd>{html.escape(tracker['rubric_version'])}</dd></div>
      <div><dt>Page revision</dt><dd>{html.escape(tracker['current_page_revision'])}</dd></div>
      <div><dt>Data digest</dt><dd><code>{html.escape(snapshot['content_digest'])}</code></dd></div>
    </dl></details>
    <p class="notice">Not a recommendation, forecast, rating, certification, or securities analysis. Issuer assertions remain speaker-attributed. SEC hosting is not independent confirmation.</p>
    <div class="actions"><a class="button" href="#supported">Inspect evidence rows</a><a class="button secondary" href="/feed.xml">Subscribe to changes</a><a class="button secondary" href="index.json">Machine-readable snapshot</a></div>
  </section>

  <section class="tracker-principle" aria-label="Method statement"><p><strong>We can be wrong. We must remain auditable.</strong></p><p>Every row now shows a pinpoint locator and a documented second reading. A capture hash shows bytes stayed fixed; the reading check tests whether the row matches those bytes and its stated boundary.</p></section>

  <section class="product-section tracker-summary" aria-labelledby="calculation-title"><div class="calculation-card"><p class="eyebrow">StructEvidence calculation · {html.escape(metric['metric_id'])}</p><h2 id="calculation-title">{html.escape(metric['value'])} of FY26 revenue was AI Cloud Services.</h2><p class="formula">{html.escape(metric['formula'])} = {html.escape(metric['value'])}</p><p>{html.escape(metric['boundary'])}</p><p><strong>Pinpoint:</strong> {html.escape(metric['locator'])} · {render_source_links(metric['source_ids'], sources)}</p></div><aside class="subscription-card"><p class="eyebrow">Follow the evidence</p><h2>Free change alerts, paid decision work.</h2><p><strong>Free:</strong> this page, JSON, source registry, append-only history, and the public Atom change feed.</p><p><strong>Decision Pack:</strong> a scoped, dated evidence package. The current standard fee is USD 4,999, subject to written scope; one evidence cycle and no included revision rounds.</p><div class="actions"><a class="button" href="/feed.xml">Subscribe via Atom</a><a class="button secondary" href="/changes/">View changes</a><a class="button secondary" href="https://structevidence.com/pricing/">Current pricing</a></div></aside></section>

  <section class="product-section tracker-block" id="supported" aria-labelledby="supported-title"><div class="section-head"><div><p class="eyebrow">Block 1</p><h2 id="supported-title">Supported as attributed</h2></div><p>These rows are supportable only in the source-native, issuer-attributed wording shown. They are not independent customer confirmation.</p></div><div class="tracker-grid">{supported}</div></section>

  <section class="product-section tracker-block" id="not-established" aria-labelledby="not-established-title"><div class="section-head"><div><p class="eyebrow">Block 2</p><h2 id="not-established-title">Not established in the reviewed source set</h2></div><p>“Not established” is a bounded research state, never a claim of non-existence. Every row carries its next observable check.</p></div><div class="tracker-grid">{not_established}</div></section>

  <section class="product-section tracker-block" id="context-notes" aria-labelledby="context-title"><div class="section-head"><div><p class="eyebrow">Verified context</p><h2 id="context-title">Relevant disclosures that do not change the core ladder.</h2></div><p>These notes are source-bounded context, not new row-state promotions.</p></div><div class="context-grid">{context_notes}</div></section>

  <section class="product-section tracker-block" id="watch" aria-labelledby="watch-title"><div class="section-head"><div><p class="eyebrow">Block 3</p><h2 id="watch-title">What would change this / dated watch items</h2></div><p>A scheduled check does not predict an outcome. Silence does not prove no change.</p></div><div class="table-scroll" tabindex="0" aria-label="Dated IREN watch items"><table class="watch-table"><thead><tr><th>ID</th><th>Item</th><th>Date or window</th><th>Current state</th><th>What to check</th></tr></thead><tbody>{watch}</tbody></table></div></section>

  <section class="product-section tracker-block" id="change-log" aria-labelledby="change-log-title"><div class="section-head"><div><p class="eyebrow">Block 4</p><h2 id="change-log-title">Append-only change log</h2></div><p>Event digests chain to the prior event. Corrections must append a supersession; earlier records remain addressable.</p></div><ol class="event-log">{events}</ol><div class="actions"><a class="button secondary" href="{html.escape(tracker.get('event_ledger', 'events-v0.1.json'))}">Open current event ledger</a><a class="button secondary" href="events-v0.1.json">Open original candidate ledger</a></div></section>

  <section class="product-section" id="provenance" aria-labelledby="provenance-title"><div class="section-head"><div><p class="eyebrow">Source provenance</p><h2 id="provenance-title">Source access, dependency, and capture state</h2></div><p>SEC-hosted exhibits remain issuer-authored. I-S01, I-S06, and I-S07 now point to captured SEC exhibits rather than blocked investor-site pages. Any remaining HTTP 403 is a retrieval limitation, never evidence of absence.</p></div><div class="table-scroll" tabindex="0" aria-label="IREN source registry"><table class="watch-table source-table"><thead><tr><th>ID</th><th>Document</th><th>Dependency</th><th>Liability</th><th>Access</th><th>SHA-256</th></tr></thead><tbody>{provenance}</tbody></table></div><div class="actions"><a class="button secondary" href="source-registry-v0.1.json">Open raw source registry</a></div><p class="notice">Plain-language labels appear here; raw codes remain in the JSON. Assurance, liability, and D0–D4 are experimental disclosure attributes. D0–D4 is not adopted or applied to rows in this release. Cash collection and customer-authored confirmation remain distinct.</p></section>

  <section class="product-section research-policies" id="policies" aria-labelledby="policies-title"><div class="section-head"><div><p class="eyebrow">Research policies</p><h2 id="policies-title">Selection, conflicts, and corrections.</h2></div><p>Only claims supported by the public case record are made here.</p></div><div class="policy-grid"><article><h3>Selection</h3><p>Cases are selected for public-interest and evidence-boundary usefulness. Coverage is not an endorsement, recommendation, rating, or a claim of completeness.</p></article><article><h3>Conflicts and payment</h3><p>No issuer-sponsored scope or issuer payment is recorded for this case. The public record contains no team securities-position attestation, so this page does not claim that positions are absent; any material conflict identified later must be disclosed.</p></article><article><h3>Corrections</h3><p>Material corrections and superseding evidence append a new event and preserve the prior record. Challenges enter human review and never update a public state automatically.</p></article><article><h3>Professional review</h3><p>No counsel-review attestation is claimed for the disclaimer or this research page. Readers should obtain qualified legal, accounting, tax, technical, or investment advice before acting.</p></article></div><p><a href="/research-scope.html">Research scope →</a> · <a href="/about.html">Authorship and conflict boundary →</a> · <a href="/changes/">Correction record →</a></p></section>

  <section class="product-section" id="challenge" aria-labelledby="challenge-title"><div class="proof-card"><div class="proof-main"><p class="eyebrow">Human review boundary</p><h2 id="challenge-title">A challenge never changes a public state automatically.</h2><p>Only fixed public identifiers are sent to the existing private intake. Do not put evidence text, identity, thesis, or non-public context in the URL. Customer content remains private; submission does not authorize research or public release.</p><div class="actions"><a class="button" href="https://structevidence.com/verify/?case_id=SE-IREN-AI-CLOUD-001">Challenge or verify a claim</a><a class="button secondary" href="https://structevidence.com/decision-pack/?case_id=SE-IREN-AI-CLOUD-001">Request a Decision Pack</a></div></div><aside class="proof-aside"><p class="field-label">Do not equate</p><p>CONTRACTED ARR ≠ OPERATING ARR</p><p>ARR ≠ GAAP REVENUE</p><p>REVENUE ≠ CASH COLLECTION</p><p>ISSUER ACCEPTANCE CLAIM ≠ CUSTOMER-AUTHORED PROOF</p></aside></div></section>

  <section class="product-section related-context" aria-labelledby="related-title"><h2 id="related-title">Related evidence context stays separate</h2><p>IREN named Figure AI among recent signings in its FY26 Results release and among its customer base in the July 20, 2026 release. That issuer-attributed mention does not identify scope or performance and does not corroborate the separate <a href="https://github.com/roalstoney-alt/se-dual-case-public/blob/main/SE-PHYSICAL-AI-001.md" rel="noopener noreferrer">Figure AI × BMW provisional research ↗</a>.</p></section>
</main>
<footer class="product-footer"><div class="product-wrap"><div class="footer-grid"><strong>StructEvidence</strong><a href="/cases/">Evidence cases</a><a href="/changes/">Recorded changes</a><a href="/feed.xml">Subscribe</a><a href="#policies">Policies</a><a href="/method.html">Method</a><a href="/privacy.html">Privacy</a><span>Owner-authorized public research projection.</span></div><div class="research-disclaimer" role="note" aria-label="Research disclaimer"><strong>Research disclaimer.</strong> This website presents time-bounded public-source research for inspection and challenge. It is not investment, legal, accounting, tax, technical-certification, or other professional advice; it is not a recommendation, rating, forecast, or assurance of future performance. Issuer-authored statements remain attributed claims, missing evidence is not proof of non-existence, and readers should verify primary sources and obtain qualified advice before acting. No counsel-review attestation is claimed.</div></div></footer><script src="/assets/product.js"></script></body></html>
"""
    (CASE / "index.html").write_text(page, encoding="utf-8")
    docs_case = ROOT / "docs" / "cases" / "iren-ai-cloud-transition"
    docs_case.mkdir(parents=True, exist_ok=True)
    for source in CASE.iterdir():
        if source.is_file():
            shutil.copy2(source, docs_case / source.name)
    shutil.copy2(ROOT / "assets" / "iren-tracker.css", ROOT / "docs" / "assets" / "iren-tracker.css")


if __name__ == "__main__":
    build()
