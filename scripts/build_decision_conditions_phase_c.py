#!/usr/bin/env python3
"""Build Phase C JSON, Markdown and HTML Decision Conditions exports."""

from __future__ import annotations

import hashlib
import html
import json
import shutil
from pathlib import Path

from decision_conditions_v01 import build_package


ROOT = Path(__file__).resolve().parents[1]
INPUTS = {
    "source_dependency_view": Path("cases/800vdc/source-dependency-v0.1.json"),
    "source_review_matrix": Path("cases/800vdc/source-dependency-review-matrix-v0.1.json"),
    "source_registry": Path("protocol/source-dependency/registry-v0.1.json"),
    "qualification_rules": Path("protocol/source-dependency/qualification-rules-v0.2.json"),
}
JSON_PATH = Path("cases/800vdc/decision-conditions-v0.1.json")
MD_PATH = Path("cases/800vdc/decision-conditions-v0.1.md")
HTML_PATH = Path("cases/800vdc/decision-conditions/index.html")
MIRRORS = {
    JSON_PATH: Path("docs/cases/800vdc/decision-conditions-v0.1.json"),
    MD_PATH: Path("docs/cases/800vdc/decision-conditions-v0.1.md"),
    HTML_PATH: Path("docs/cases/800vdc/decision-conditions/index.html"),
    Path("assets/decision-conditions.css"): Path("docs/assets/decision-conditions.css"),
    Path("assets/decision-conditions.js"): Path("docs/assets/decision-conditions.js"),
    Path("protocol/decision-conditions/schema-v0.1.json"): Path("docs/protocol/decision-conditions/schema-v0.1.json"),
    Path("protocol/decision-conditions/README.md"): Path("docs/protocol/decision-conditions/README.md"),
    Path("decision-conditions-sitemap.xml"): Path("docs/decision-conditions-sitemap.xml"),
}


def sha(path: Path) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def citation(condition: dict, snapshot: str) -> str:
    rule = condition["source_evidence_rule"]
    result = condition["source_evidence_result"]
    time = condition["time_boundary"]
    unknown = " | ".join(condition["preserved_uncertainty"]["unknown"])
    return (
        f"StructEvidence Decision Condition {condition['decision_condition_id']} | "
        f"Case {condition['case_id']} | Gap {condition['gap_id']} | Claim {condition['claim_id']} | "
        f"Evidence result: {result['qualification_outcome']} within {condition['scope']['bounded_sample']} | "
        f"Closure rule: {rule['exact_closure_test']} | Evidence cutoff: {time['evidence_cutoff']} | "
        f"Last source check: {time['last_source_check_at']} | Reviewed: {time['reviewed_at']} | "
        f"UNKNOWN: {unknown} | CHINDATA_E3_E4=UNRESOLVED | SECOND_REAL_HUMAN_REVIEW=UNSUPPORTED | "
        f"Client action=UNSPECIFIED; source qualification does not select PROCEED/HOLD/EXIT | "
        f"Snapshot SHA-256: {snapshot} | JSON: {condition['stable_urls']['json']} | "
        f"Markdown: {condition['stable_urls']['markdown']} | HTML: {condition['stable_urls']['html']} | "
        f"Not a decision recommendation."
    )


def render_markdown(package: dict) -> str:
    lines = [
        "# 800VDC Decision Conditions · v0.1",
        "",
        f"Snapshot SHA-256: `{package['snapshot_sha256']}`",
        "",
        "> Public illustrative export. StructEvidence reports time-bounded evidence conditions; it does not select a client action or recommend a decision.",
        "",
    ]
    for item in package["conditions"]:
        rule = item["source_evidence_rule"]
        result = item["source_evidence_result"]
        lines += [
            f"## {item['decision_condition_id']}", "",
            f"- Case / Gap / Claim: `{item['case_id']}` / `{item['gap_id']}` / `{item['claim_id']}`",
            f"- Illustrative decision type: `{item['decision_type']}` (`{item['decision_context_status']}`)",
            f"- Question: {item['scope']['question']}",
            f"- Current evidence state: `{item['current_evidence_state']['case_state']}` as of `{item['current_evidence_state']['case_state_as_of']}`; export state change: `false`",
            f"- Evidence result: `{result['qualification_outcome']}`; qualifying evidence present: `{str(result['qualifying_evidence_present']).lower()}`",
            f"- Rule: `{rule['qualification_rule_id']}` under `{rule['rubric_version']}`; minimum `{rule['minimum_evidence_level']}`",
            f"- Exact closure test: {rule['exact_closure_test']}",
            f"- Cutoff / last check / review: `{item['time_boundary']['evidence_cutoff']}` / `{item['time_boundary']['last_source_check_at']}` / `{item['time_boundary']['reviewed_at']}`",
            f"- Sample boundary: {item['scope']['bounded_sample']}",
            "- Preserved uncertainty: `UNKNOWN`; `CHINDATA_E3_E4=UNRESOLVED`; `SECOND_REAL_HUMAN_REVIEW=UNSUPPORTED`.",
            "- Client action: `UNSPECIFIED`. Trigger, review date, fallback and exposure threshold are all `UNSPECIFIED` and client-owned.",
            f"- Record SHA-256: `{item['record_sha256']}`", "",
            "### Source rows", "",
            "| Source row | Level | Dependency | Access | Qualification | Source |", "|---|---|---|---|---|---|",
        ]
        for source in result["qualifying_evidence"] + result["nonqualifying_evidence"]:
            title = source["title"].replace("|", "\\|")
            lines.append(f"| `{source['source_row_id']}` | `{source['evidence_level']}` | `{source['dependency_class']}` | `{source['source_access_status']}` | `{source['qualification_status']}` | [{title}]({source['url']}) |")
        lines += ["", "### Copyable complete citation", "", citation(item, package["snapshot_sha256"]), ""]
    return "\n".join(lines).rstrip() + "\n"


def render_html(package: dict) -> str:
    cards = []
    for item in package["conditions"]:
        rule = item["source_evidence_rule"]
        result = item["source_evidence_result"]
        cid = html.escape(item["decision_condition_id"])
        source_rows = "".join(
            f"<li><a href=\"{html.escape(source['url'], quote=True)}\">{html.escape(source['title'])}</a> "
            f"<code>{html.escape(source['source_row_id'])}</code> · {html.escape(source['evidence_level'])} · "
            f"{html.escape(source['dependency_class'])} · {html.escape(source['qualification_status'])}</li>"
            for source in result["qualifying_evidence"] + result["nonqualifying_evidence"]
        )
        copy_text = html.escape(citation(item, package["snapshot_sha256"]))
        cards.append(f'''<article class="dc-card" id="{cid}" data-decision-condition>
<p class="eyebrow">{html.escape(item['gap_id'])} · public illustrative condition</p><h2>{cid}</h2>
<dl class="dc-fields"><div><dt>Scoped question</dt><dd>{html.escape(item['scope']['question'])}</dd></div>
<div><dt>Source evidence result</dt><dd><strong>{html.escape(result['qualification_outcome'])}</strong><br>Zero applies only to the bounded sample; it is not proof of global absence.</dd></div>
<div><dt>Current evidence state</dt><dd><strong>{html.escape(item['current_evidence_state']['case_state'])}</strong><br>As of <code>{html.escape(item['current_evidence_state']['case_state_as_of'])}</code>; not authoritative truth.</dd></div>
<div><dt>Exact closure test</dt><dd>{html.escape(rule['exact_closure_test'])}</dd></div>
<div><dt>Time boundary</dt><dd>Cutoff <code>{html.escape(item['time_boundary']['evidence_cutoff'])}</code><br>Last source check <code>{html.escape(item['time_boundary']['last_source_check_at'])}</code><br>Reviewed <code>{html.escape(item['time_boundary']['reviewed_at'])}</code></dd></div>
<div><dt>Preserved uncertainty</dt><dd><code>UNKNOWN</code> · <code>CHINDATA_E3_E4=UNRESOLVED</code> · <code>SECOND_REAL_HUMAN_REVIEW=UNSUPPORTED</code></dd></div>
<div><dt>Client action condition</dt><dd><code>UNSPECIFIED</code>. StructEvidence does not select PROCEED, HOLD or EXIT.</dd></div></dl>
<details><summary>Review all source rows ({len(result['qualifying_evidence']) + len(result['nonqualifying_evidence'])})</summary><ul class="dc-sources">{source_rows}</ul></details>
<h3>Complete citation</h3><textarea class="dc-citation" id="copy-{cid}" readonly rows="11">{copy_text}</textarea>
<div class="dc-actions"><button type="button" class="button small" data-copy-decision-conditions data-copy-source="copy-{cid}">Copy decision conditions</button>
<a href="/cases/800vdc/decision-conditions-v0.1.json">JSON</a><a href="/cases/800vdc/decision-conditions-v0.1.md">Markdown</a><a href="{html.escape(item['stable_urls']['gap'], quote=True)}">Challenge rule or source</a>
<span role="status" aria-live="polite" data-copy-status></span></div>
<p class="dc-hash">Record SHA-256 <code>{html.escape(item['record_sha256'])}</code></p></article>''')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>800VDC Decision Conditions v0.1 | StructEvidence</title><meta name="description" content="Citable, deterministic evidence conditions for the two public 800VDC evidence gaps; client actions remain unspecified.">
<link rel="canonical" href="https://structurevidence.org/cases/800vdc/decision-conditions/"><link rel="alternate" type="application/json" href="https://structurevidence.org/cases/800vdc/decision-conditions-v0.1.json"><link rel="alternate" type="text/markdown" href="https://structurevidence.org/cases/800vdc/decision-conditions-v0.1.md">
<link rel="stylesheet" href="/assets/product.css"><link rel="stylesheet" href="/assets/decision-conditions.css"></head><body class="product-site"><a class="skip-link" href="#main">Skip to content</a>
<header class="product-header"><nav class="product-nav" aria-label="Primary navigation"><a class="product-brand" href="/"><span>SE</span><strong>StructEvidence</strong></a><div class="product-links"><a href="/cases/">Evidence Cases</a><a href="/gaps/">Open Evidence Gaps</a><a href="/method.html">Method</a></div></nav></header>
<main class="product-main" id="main"><section class="page-hero"><p class="eyebrow">SE-DUAL-SITE-UPGRADE-002 · Phase C · v0.1</p><h1>Citable Decision Conditions</h1><p class="lead">Two deterministic public exports derived from the existing 800VDC source ledger. Evidence qualification is separate from any client action.</p>
<p class="dc-boundary"><strong>Not a decision recommendation.</strong> No client adoption, exposure, trigger, fallback, purchase, investment or deployment decision is asserted.</p><p>Snapshot SHA-256 <code>{html.escape(package['snapshot_sha256'])}</code></p></section>
<section class="product-section" aria-label="Decision conditions">{''.join(cards)}</section></main>
<footer class="product-footer"><div class="product-wrap footer-grid"><strong>StructEvidence</strong><a href="/cases/800vdc/source-dependency/">Source Dependency View</a><span>Evidence evolves. Decisions remain accountable.</span></div></footer><script src="/assets/decision-conditions.js"></script></body></html>'''


def write_outputs() -> dict:
    provenance = {name: str(path) for name, path in INPUTS.items()}
    provenance.update({f"{name}_sha256": sha(path) for name, path in INPUTS.items()})
    package = build_package(load(INPUTS["source_dependency_view"]), load(INPUTS["source_review_matrix"]), load(INPUTS["source_registry"]), load(INPUTS["qualification_rules"]), provenance)
    outputs = {JSON_PATH: json.dumps(package, ensure_ascii=False, indent=2) + "\n", MD_PATH: render_markdown(package), HTML_PATH: render_html(package)}
    for path, content in outputs.items():
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    for source, mirror in MIRRORS.items():
        target = ROOT / mirror
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source, target)
    return package


if __name__ == "__main__":
    built = write_outputs()
    print(f"DECISION_CONDITIONS_CREATED = {len(built['conditions'])}")
    print(f"SNAPSHOT_SHA256 = {built['snapshot_sha256']}")
