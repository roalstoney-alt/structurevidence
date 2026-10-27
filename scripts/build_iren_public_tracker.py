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


def render_row(row: dict, sources: dict[str, dict], reviewer_status: str) -> str:
    state_class = "supported" if row["state"] == "SUPPORTED_AS_ATTRIBUTED" else "not-established"
    hashes = []
    for source_id in row["source_ids"]:
        digest = sources[source_id].get("sha256")
        hashes.append(f"{source_id}: {digest[:12]}…" if digest else f"{source_id}: capture incomplete")
    return f"""
      <article class="tracker-row" id="{html.escape(row['row_id'])}" data-row-id="{html.escape(row['row_id'])}">
        <div class="row-head"><code>{html.escape(row['row_id'])}</code><span class="state {state_class}">{html.escape(row['state'].replace('_', ' '))}</span></div>
        <h3>{html.escape(row['claim'])}</h3>
        <p class="boundary"><strong>Boundary:</strong> {html.escape(row['boundary'])}</p>
        <dl class="row-meta">
          <div><dt>Sources</dt><dd>{render_source_links(row['source_ids'], sources)}</dd></div>
          <div><dt>Assurance / liability</dt><dd>{html.escape(row['assurance'])} / {html.escape(row['liability'])}</dd></div>
          <div><dt>Capture</dt><dd>{html.escape(' · '.join(hashes))}</dd></div>
          <div><dt>Revision</dt><dd>{html.escape(row['last_event_id'])} · {html.escape(reviewer_status.replace('_', ' '))}</dd></div>
          <div><dt>Next check</dt><dd>{html.escape(row['next_check'])}</dd></div>
        </dl>
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
    }
    snapshot["content_digest"] = "sha256:" + canonical_sha256(snapshot)
    (CASE / "index.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    supported = "".join(
        render_row(row, sources, tracker["reviewer_status"])
        for row in tracker["rows"] if row["section"] == "SUPPORTED_AS_ATTRIBUTED"
    )
    not_established = "".join(
        render_row(row, sources, tracker["reviewer_status"])
        for row in tracker["rows"] if row["section"] == "NOT_ESTABLISHED"
    )
    watch = "".join(
        f"<tr><td><code>{html.escape(item['watch_id'])}</code></td><td>{html.escape(item['item'])}</td>"
        f"<td>{html.escape(item['date_or_window'])}</td><td>{html.escape(item['status'])}</td>"
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
        f"<td>{html.escape(source['title'])}</td><td>{html.escape(source['dependency_class'])}</td>"
        f"<td>{html.escape(source['liability'])}</td><td>{html.escape(source['access_state'])}</td>"
        f"<td><code>{html.escape(source['sha256'][:16] + '…' if source.get('sha256') else 'not captured')}</code></td></tr>"
        for source in registry["sources"]
    )
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
  <link rel="stylesheet" href="/assets/iren-tracker.css?v=20261028-publication">
</head>
<body class="product-site iren-tracker"><a class="skip-link" href="#main">Skip to content</a>
<header class="product-header"><nav class="product-nav" aria-label="Primary navigation"><a class="product-brand" href="/"><span>SE</span><strong>StructEvidence</strong></a><button class="product-nav-toggle" type="button" aria-expanded="false" aria-controls="product-links" data-product-nav-toggle>Menu</button><div class="product-links" id="product-links"><a aria-current="page" href="/cases/">Evidence Cases</a><a href="/gaps/">Open Evidence Gaps</a><a href="https://structevidence.com/verify/?case_id=SE-IREN-AI-CLOUD-001">Verify a Claim</a><a href="https://structevidence.com/decision-pack/?case_id=SE-IREN-AI-CLOUD-001">Decision Pack</a><a href="/method.html">Method</a></div></nav></header>
<main class="product-main" id="main"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">StructEvidence</a><span>›</span><a href="/cases/">Cases</a><span>›</span><span aria-current="page">IREN AI Cloud transition</span></nav>
  <section class="page-hero case-hero tracker-hero" aria-labelledby="case-title">
    <p class="eyebrow">Public research tracker · {html.escape(tracker['case_id'])} · {html.escape(tracker['tracker_data_version'])}</p>
    <h1 id="case-title">IREN Limited: AI Cloud transition, without collapsing the evidence chain.</h1>
    <p class="lead">Which milestones are supported by dated issuer disclosures—and where do contract value, delivery, customer acceptance, ARR, recognized revenue, cash collection, and economic returns remain distinct?</p>
    <div class="review-hold review-authorized" role="status"><strong>Publication authorization:</strong> The authenticated task owner approved the exact reviewed candidate for public release. Separate financial, legal, privacy, and row-level reviewer identities are not claimed by the public authorization record.</div>
    <dl class="case-facts">
      <div><dt>Evidence cutoff</dt><dd>{html.escape(tracker['evidence_cutoff'])}</dd></div>
      <div><dt>Last source check</dt><dd>{html.escape(tracker['last_source_check_utc'])}</dd></div>
      <div><dt>Next source check</dt><dd>{html.escape(tracker['next_source_check'])}</dd></div>
      <div><dt>Rubric</dt><dd>{html.escape(tracker['rubric_version'])}</dd></div>
      <div><dt>Human review</dt><dd>{html.escape(tracker['reviewer_status'])}</dd></div>
      <div><dt>Data digest</dt><dd><code>{html.escape(snapshot['content_digest'])}</code></dd></div>
    </dl>
    <p class="notice">Not a recommendation, forecast, rating, certification, or securities analysis. Issuer assertions remain speaker-attributed. SEC hosting is not independent confirmation.</p>
    <div class="actions"><a class="button" href="#supported">Inspect evidence rows</a><a class="button secondary" href="index.json">Machine-readable snapshot</a><a class="button secondary" href="source-registry-v0.1.json">Source registry</a></div>
  </section>

  <section class="tracker-principle" aria-label="Method statement"><p><strong>We can be wrong. We must remain auditable.</strong></p><p>Every state shows how it was checked. Verify Your Verify — Lower the cost of knowing what you can trust.</p></section>

  <section class="product-section tracker-block" id="supported" aria-labelledby="supported-title"><div class="section-head"><div><p class="eyebrow">Block 1</p><h2 id="supported-title">Supported as attributed</h2></div><p>These rows are supportable only in the source-native, issuer-attributed wording shown. They are not independent customer confirmation.</p></div><div class="tracker-grid">{supported}</div></section>

  <section class="product-section tracker-block" id="not-established" aria-labelledby="not-established-title"><div class="section-head"><div><p class="eyebrow">Block 2</p><h2 id="not-established-title">Not established in the reviewed source set</h2></div><p>“Not established” is a bounded research state, never a claim of non-existence. Every row carries its next observable check.</p></div><div class="tracker-grid">{not_established}</div></section>

  <section class="product-section tracker-block" id="watch" aria-labelledby="watch-title"><div class="section-head"><div><p class="eyebrow">Block 3</p><h2 id="watch-title">What would change this / dated watch items</h2></div><p>A scheduled check does not predict an outcome. Silence does not prove no change.</p></div><div class="table-scroll" tabindex="0" aria-label="Dated IREN watch items"><table class="watch-table"><thead><tr><th>ID</th><th>Item</th><th>Date or window</th><th>Current state</th><th>What to check</th></tr></thead><tbody>{watch}</tbody></table></div></section>

  <section class="product-section tracker-block" id="change-log" aria-labelledby="change-log-title"><div class="section-head"><div><p class="eyebrow">Block 4</p><h2 id="change-log-title">Append-only change log</h2></div><p>Event digests chain to the prior event. Corrections must append a supersession; earlier records remain addressable.</p></div><ol class="event-log">{events}</ol><div class="actions"><a class="button secondary" href="{html.escape(tracker.get('event_ledger', 'events-v0.1.json'))}">Open current event ledger</a><a class="button secondary" href="events-v0.1.json">Open original candidate ledger</a></div></section>

  <section class="product-section" id="provenance" aria-labelledby="provenance-title"><div class="section-head"><div><p class="eyebrow">Source provenance</p><h2 id="provenance-title">Source access, dependency, and capture state</h2></div><p>SEC-hosted exhibits remain issuer-authored. HTTP 403 is recorded as a retrieval limitation and is never evidence of absence. No private source bytes are included.</p></div><div class="table-scroll" tabindex="0" aria-label="IREN source registry"><table class="watch-table source-table"><thead><tr><th>ID</th><th>Document</th><th>Dependency</th><th>Liability</th><th>Access</th><th>SHA-256</th></tr></thead><tbody>{provenance}</tbody></table></div><p class="notice">Assurance, liability, and D0–D4 are proposed experimental disclosure attributes. D0–D4 is not adopted or applied to rows in this public release. Cash collection and customer-authored confirmation remain distinct.</p></section>

  <section class="product-section" id="challenge" aria-labelledby="challenge-title"><div class="proof-card"><div class="proof-main"><p class="eyebrow">Human review boundary</p><h2 id="challenge-title">A challenge never changes a public state automatically.</h2><p>Only fixed public identifiers are sent to the existing private intake. Do not put evidence text, identity, thesis, or non-public context in the URL. Customer content remains private; submission does not authorize research or public release.</p><div class="actions"><a class="button" href="https://structevidence.com/verify/?case_id=SE-IREN-AI-CLOUD-001">Challenge or verify a claim</a><a class="button secondary" href="https://structevidence.com/decision-pack/?case_id=SE-IREN-AI-CLOUD-001">Request a Decision Pack</a></div></div><aside class="proof-aside"><p class="field-label">Do not equate</p><p>CONTRACTED ARR ≠ OPERATING ARR</p><p>ARR ≠ GAAP REVENUE</p><p>REVENUE ≠ CASH COLLECTION</p><p>ISSUER ACCEPTANCE CLAIM ≠ CUSTOMER-AUTHORED PROOF</p></aside></div></section>

  <section class="product-section related-context" aria-labelledby="related-title"><h2 id="related-title">Related evidence context stays separate</h2><p><a href="https://github.com/roalstoney-alt/se-dual-case-public/blob/main/SE-PHYSICAL-AI-001.md" rel="noopener noreferrer">Figure AI × BMW provisional research ↗</a> is a separate issuer/dependent evidence study. It does not corroborate IREN delivery, customer acceptance, revenue, or cash collection.</p></section>
</main>
<footer class="product-footer"><div class="product-wrap"><div class="footer-grid"><strong>StructEvidence</strong><a href="/cases/">Evidence cases</a><a href="/changes/">Recorded changes</a><a href="/method.html">Method</a><a href="/privacy.html">Privacy</a><span>Owner-authorized public research projection.</span></div><div class="research-disclaimer" role="note" aria-label="Research disclaimer"><strong>Research disclaimer.</strong> This website presents time-bounded public-source research for inspection and challenge. It is not investment, legal, accounting, tax, technical-certification, or other professional advice; it is not a recommendation, rating, forecast, or assurance of future performance. Issuer-authored statements remain attributed claims, missing evidence is not proof of non-existence, and readers should verify primary sources and obtain qualified advice before acting.</div></div></footer><script src="/assets/product.js"></script></body></html>
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
