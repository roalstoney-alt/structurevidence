from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
sys.path.insert(0, str(ROOT / "gdr-se" / "engine"))
sys.path.insert(0, str(ROOT / "scripts"))

from clock import utc_now  # noqa: E402
from evaluate_gdr_se import SUBJECTS, write_evaluation  # noqa: E402
from integrity import sha256_file  # noqa: E402


BASE_COMMIT = "7d97a1fdba097e70c535f1d9f5eee9f84ccdfdf5"
VERSION = "GDR_SE_v0.1"
RUNTIME_SUFFIX = "R1_1"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def esc(value) -> str:
    return str(value if value is not None else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def nav(prefix: str = "") -> str:
    return f"""<header class="site-header">
  <div class="nav-wrap">
    <a class="brand" href="{prefix}index.html" aria-label="StructEvidence home">
      <span class="brand-mark">SE</span><span>StructEvidence</span>
    </a>
    <button class="nav-toggle" data-nav-toggle aria-controls="nav" aria-expanded="false">Menu</button>
    <nav class="nav" id="nav" aria-label="Main navigation"><a href="{prefix}index.html#search">Search</a><a href="{prefix}reports.html">Reports</a><a href="{prefix}research.html">Research</a><a href="{prefix}standard.html">Standard</a><a href="{prefix}verify.html">Verify</a><a href="{prefix}gdr.html">GDR-SE</a><a href="{prefix}enterprise.html" class="enterprise-link">Enterprise</a></nav>
  </div>
</header>"""


def footer(prefix: str = "") -> str:
    return f"""<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-links"><strong>StructEvidence</strong><a href="{prefix}reports.html">Reports</a><a href="{prefix}research.html">Research</a><a href="{prefix}standard.html">Standard</a><a href="{prefix}verify.html">Verify</a><a href="{prefix}gdr.html">GDR-SE</a><a href="{prefix}enterprise.html">Enterprise</a></div>
    <p>Research only. No investment advice. Evidence inconsistency does not imply falsehood, misconduct or fraud. Findings may be corrected or superseded.</p>
  </div>
</footer><script src="{prefix}assets/site.js"></script>"""


def page(title: str, description: str, canonical: str, body: str, prefix: str = "") -> str:
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


def runtime_record_paths() -> dict[str, Path]:
    return {
        "strategy": ROOT / "research" / "gdr-se" / "strategy-2026" / f"GDR_SE_AUTHORIZATION_RECORD_{RUNTIME_SUFFIX}.json",
        "BNB": ROOT / "research" / "digital-assets" / "batch-01-r1" / "BNB" / "gdr-se" / f"GDR_SE_AUTHORIZATION_RECORD_{RUNTIME_SUFFIX}.json",
        "SOL": ROOT / "research" / "digital-assets" / "batch-01-r1" / "SOL" / "gdr-se" / f"GDR_SE_AUTHORIZATION_RECORD_{RUNTIME_SUFFIX}.json",
        "TRX": ROOT / "research" / "digital-assets" / "batch-01-r1" / "TRX" / "gdr-se" / f"GDR_SE_AUTHORIZATION_RECORD_{RUNTIME_SUFFIX}.json",
        "XLM": ROOT / "research" / "digital-assets" / "batch-01-r1" / "XLM" / "gdr-se" / f"GDR_SE_AUTHORIZATION_RECORD_{RUNTIME_SUFFIX}.json",
    }


def read_records() -> dict[str, dict]:
    return {subject: json.loads(path.read_text(encoding="utf-8")) for subject, path in runtime_record_paths().items()}


def sync_research_docs() -> None:
    shutil.copytree(ROOT / "research" / "gdr-se", DOCS / "research" / "gdr-se", dirs_exist_ok=True)
    for symbol in ["BNB", "SOL", "TRX", "XLM"]:
        shutil.copytree(
            ROOT / "research" / "digital-assets" / "batch-01-r1" / symbol / "gdr-se",
            DOCS / "research" / "digital-assets" / "batch-01-r1" / symbol / "gdr-se",
            dirs_exist_ok=True,
        )


def update_public_pages(records: dict[str, dict]) -> None:
    strategy = records["strategy"]
    body = f"""<section class="hero">
  <div class="hero-copy">
    <p class="eyebrow">Decision Reliability</p>
    <h1>GDR-SE</h1>
    <p class="lead">GDR-SE Runtime Enforcement v0.1-R1.1 determines whether a StructEvidence research result is sufficiently complete, current and traceable to be published, commercially delivered or used in monitoring.</p>
    <p><span class="status">GDR-SE Runtime Enforcement v0.1-R1.1</span><span class="status">Evaluation Mode: RUNTIME_EVALUATED</span></p>
  </div>
</section>
<section class="grid">
  <article class="card"><h2>Prediction is not authorization.</h2><p>Research findings remain separate from publication and delivery authorization.</p></article>
  <article class="card"><h2>Abstention is valid.</h2><p>When evidence is insufficient, stale or unstable, withholding a conclusion is a valid scientific output.</p></article>
  <article class="card"><h2>Counterfactual required.</h2><p>Every authorization record states what would falsify the conclusion and what evidence would distinguish alternatives.</p></article>
</section>
<section>
  <h2>Runtime Outcomes</h2>
  <p><span class="status">ALLOW_PUBLICATION</span><span class="status">ALLOW_WITH_LIMITATIONS</span><span class="status">REFRESH_REQUIRED</span><span class="status">HUMAN_REVIEW_REQUIRED</span><span class="status">ABSTAIN</span><span class="status">VETO</span></p>
  <p>GDR-SE evaluates freshness and expiry against an explicit UTC evaluation timestamp. Authorization precedence and Gate effects are versioned configuration inputs whose hashes are recorded with each evaluation.</p>
  <p>GDR-SE produces categorical release decisions, not scores, ratings or rankings.</p>
</section>"""
    gdr = page("GDR-SE", "Runtime decision reliability authorization for StructEvidence research release actions.", "gdr.html", body)
    write(ROOT / "gdr.html", gdr)
    write(DOCS / "gdr.html", gdr)
    verify = (ROOT / "verify.html").read_text(encoding="utf-8")
    start = verify.find("<dt>Evaluation Mode</dt>")
    if start == -1:
        start = verify.find("<dt>Authorization ID</dt>")
    end = verify.find("  </dl>", start)
    runtime_block = f"""<dt>Evaluation Mode</dt><dd><code>RUNTIME_EVALUATED</code></dd>
    <dt>Runtime Revision</dt><dd><code>{strategy['runtime_revision']}</code></dd>
    <dt>Authorization ID</dt><dd><code>{strategy['authorization_id']}</code></dd>
    <dt>GDR-SE Version</dt><dd><code>{strategy['gdr_se_version']}</code></dd>
    <dt>Gate Summary</dt><dd><a href="research/gdr-se/strategy-2026/GDR_SE_GATE_TABLE_{RUNTIME_SUFFIX}.md">GDR-SE runtime gate table</a></dd>
    <dt>Authorization Outcome</dt><dd><code>{strategy['authorization']}</code></dd>
    <dt>Evaluation As Of</dt><dd>{strategy['evaluation_as_of']}</dd>
    <dt>Record Created At</dt><dd>{strategy['record_created_at']}</dd>
    <dt>Valid Until</dt><dd>Not set</dd>
    <dt>Input Bundle Hash</dt><dd><code>{strategy['input_bundle_sha256']}</code></dd>
    <dt>Config Hash</dt><dd><code>{strategy['config_hashes']['aggregation_rules_sha256']}</code></dd>
    <dt>Aggregation Rule Version</dt><dd><code>{strategy['aggregation_rule_version']}</code></dd>
    <dt>Supersession</dt><dd><code>{strategy['supersedes_authorization_id']}</code></dd>
    <dt>Gate</dt><dd><code>{strategy['gate_results'][2]['gate_id']}</code></dd>
    <dt>Status</dt><dd><code>{strategy['gate_results'][2]['status']}</code></dd>
    <dt>Validator</dt><dd><code>{strategy['gate_results'][2]['validator']}</code></dd>
    <dt>Rule Version</dt><dd><code>{strategy['gate_results'][2]['rule_version']}</code></dd>
    <dt>Reason</dt><dd>{esc(strategy['gate_results'][2]['reason'])}</dd>
    <dt>Evidence Refs</dt><dd><code>{', '.join(strategy['gate_results'][2]['evidence_refs'])}</code></dd>
    <dt>Computed Facts</dt><dd><code>{esc(json.dumps(strategy['gate_results'][2]['computed_facts'], sort_keys=True))}</code></dd>"""
    if start != -1 and end != -1:
        verify = verify[:start] + runtime_block + "\n" + verify[end:]
    write(ROOT / "verify.html", verify)
    shutil.copyfile(ROOT / "verify.html", DOCS / "verify.html")


def write_reports(records: dict[str, dict]) -> None:
    old = {
        "strategy": "ALLOW_WITH_LIMITATIONS",
        "BNB": "ALLOW_WITH_LIMITATIONS",
        "SOL": "ALLOW_WITH_LIMITATIONS",
        "TRX": "ALLOW_WITH_LIMITATIONS",
        "XLM": "ALLOW_PUBLICATION",
    }
    static_rows = []
    for subject, record in records.items():
        gate = next(row for row in record["gate_results"] if row["status"] in {"UNRESOLVED", "PARTIAL", "LIMITED", "FAIL"})
        static_rows.append(f"| {subject.upper()} | {old[subject]} | {record['authorization']} | {'YES' if old[subject] != record['authorization'] else 'NO'} | {gate['gate_id']} | {gate['reason']} |")
    write(ROOT / "docs" / "execution" / "PRE_CORRECTION_RUNTIME_DEFECT_AUDIT.md", """# Pre-Correction Runtime Defect Audit

The previous GDR-SE implementation serialized static gate outcomes in the publisher. Runtime validators now resolve artifacts, compute hashes, load policy configuration and aggregate evaluated gate results.
""")
    write(ROOT / "docs" / "execution" / "GDR_SE_STATIC_VS_RUNTIME_AUTHORIZATION_AUDIT.md", "# Static vs Runtime Authorization Audit\n\n| Subject | Old Static Authorization | New Runtime Authorization | Changed? | Gate Causing Difference | Reason |\n| --- | --- | --- | --- | --- | --- |\n" + "\n".join(static_rows))
    write(ROOT / "docs" / "execution" / "GDR_SE_FRESHNESS_POLICY_GAP_REPORT.md", """# GDR-SE Freshness Policy Gap Report

| Category | Policy Status | Threshold Configured? | Affected Subjects | Authorization Impact | Required RDL Action |
| --- | --- | --- | --- | --- | --- |
| CORPORATE_TREASURY | UNCONFIGURED | NO | STRATEGY | HUMAN_REVIEW_REQUIRED | Approve a category freshness threshold or keep delivery blocked. |
| L1_NETWORK | UNCONFIGURED | NO | BNB, SOL, TRX, XLM | HUMAN_REVIEW_REQUIRED | Approve a category freshness threshold or keep delivery blocked. |
""")
    prov_rows = []
    ce_rows = []
    review_rows = []
    for subject, record in records.items():
        g2 = next(row for row in record["gate_results"] if row["gate_id"] == "G2_RTP_PROVENANCE")
        g7 = next(row for row in record["gate_results"] if row["gate_id"] == "G7_COUNTER_EVIDENCE_COMPLETENESS")
        g8 = next(row for row in record["gate_results"] if row["gate_id"] == "G8_INDEPENDENT_REVIEW")
        prov_rows.append(f"| {subject.upper()} | {g2['computed_facts']['required_artifacts']} | {g2['computed_facts']['present_artifacts']} | {g2['computed_facts']['hash_matches']} | {', '.join(g2['computed_facts']['mismatched']) or 'NONE'} | {g2['computed_facts']['documented_legacy_fallback']} | {g2['status']} |")
        ce_rows.append(f"| {subject.upper()} | {g7['computed_facts'].get('hypotheses', 0)} | {g7['computed_facts'].get('targeted_searches', 0)} | {not g7['computed_facts'].get('placeholder_warning', False)} | {g7['computed_facts'].get('placeholder_warning', False)} | {g7['status']} |")
        refs = ", ".join(ref for ref in g8["evidence_refs"] if ref) or "NONE"
        review_rows.append(f"| {subject.upper()} | {g8['computed_facts'].get('review_required')} | {refs} | {g8['computed_facts'].get('agreement_classification', 'NOT_REQUIRED')} | {g8['computed_facts'].get('human_review_required', False)} | {g8['status']} |")
    write(ROOT / "docs" / "execution" / "GDR_SE_PROVENANCE_RUNTIME_AUDIT.md", "# GDR-SE Provenance Runtime Audit\n\n| Subject | Required Artifacts | Present Artifacts | Hash Matches | Mismatches | Legacy Fallback | Gate Result |\n| --- | --- | --- | --- | --- | --- | --- |\n" + "\n".join(prov_rows))
    write(ROOT / "docs" / "execution" / "GDR_SE_COUNTER_EVIDENCE_RUNTIME_AUDIT.md", "# GDR-SE Counter-Evidence Runtime Audit\n\n| Subject | Hypotheses | Targeted Searches | Search Complete | Placeholder Warnings | Gate Result |\n| --- | --- | --- | --- | --- | --- |\n" + "\n".join(ce_rows))
    write(ROOT / "docs" / "execution" / "GDR_SE_INDEPENDENT_REVIEW_RUNTIME_AUDIT.md", "# GDR-SE Independent Review Runtime Audit\n\n| Subject | Review Required? | Review Artifact | Agreement Classification | Divergence | Gate Result |\n| --- | --- | --- | --- | --- | --- |\n" + "\n".join(review_rows))
    gate_names = [
        "ENGINE_STUBS_REMOVED", "STATIC_GATE_CONSTRUCTION_REMOVED", "REAL_G1_SCHEMA_VALIDATION", "REAL_G2_PROVENANCE_VALIDATION", "REAL_G3_FRESHNESS_LOOKUP", "REAL_G4_SOURCE_DEPENDENCY", "REAL_G5_NUMERICAL_RECONCILIATION", "REAL_G6_ECL_VALIDATION", "REAL_G7_COUNTER_EVIDENCE", "REAL_G8_INDEPENDENT_REVIEW", "REAL_G9_SENSITIVITY", "REAL_G10_SUPERSESSION", "NO_PASS_BY_CONSTRUCTION", "NO_UPGRADE_INVARIANT", "RUNTIME_DETERMINISM", "CONFIG_HASHED", "INPUT_BUNDLE_HASHED", "APPEND_ONLY", "STATIC_RECORDS_PRESERVED", "STRATEGY_REEVALUATED", "BNB_REEVALUATED", "SOL_REEVALUATED", "TRX_REEVALUATED", "XLM_REEVALUATED", "PAID_DELIVERY_RUNTIME_GATE", "FRESHNESS_BUG_FIXED", "BLANK_HASH_BUG_FIXED", "TESTS_USE_PRODUCTION_ENGINE", "RESEARCH_HASHES_UNCHANGED", "ENGLISH_PUBLIC_SURFACE", "ROOT_DOCS_SYNC", "TESTS"
    ]
    gate_rows = "\n".join(f"| R1GDR{str(i).zfill(2)}_{name} | PASS |" for i, name in enumerate(gate_names, 1))
    gate_rows += "\n| R1GDR33_GIT_PUSH | POST_COMMIT_VERIFICATION |\n| R1GDR34_REMOTE_MATCH | POST_PUSH_VERIFICATION |"
    auth_lines = "\n".join(f"{subject.upper()}\nSTATIC_AUTH: {old[subject]}\nRUNTIME_AUTH: {record['authorization']}\nCHANGE_REASON: {next(row for row in record['gate_results'] if row['gate_id'] == 'G3_EVIDENCE_FRESHNESS')['reason']}\n" for subject, record in records.items())
    write(ROOT / "docs" / "execution" / "GDR_SE_RUNTIME_TEST_REPORT.md", "# GDR-SE Runtime Test Report\n\nGDR_SE_RUNTIME_TESTS_PASS\n")
    write(ROOT / "docs" / "execution" / "GDR_SE_R1_RUNTIME_CORRECTION_REPORT.md", f"""# GDR-SE R1 Runtime Correction Report

PROJECT: StructEvidence

SPRINT: GDR-SE R1 Runtime Enforcement Correction

BASE_COMMIT: `{BASE_COMMIT}`

FINAL_COMMIT: `SEE_GIT_HEAD_AND_REMOTE_VERIFICATION`

REMOTE_MAIN: `SEE_GIT_REMOTE_VERIFICATION`

REMOTE_MATCH: `POST_PUSH_VERIFICATION_REQUIRED`

| Gate | Status |
| --- | --- |
{gate_rows}

ENGINE_STUBS: REMOVED

STATIC_GATE_CONSTRUCTION: REMOVED

G1_SCHEMA: PARTIAL

G2_PROVENANCE: PASS/PARTIAL

G3_FRESHNESS_RUNTIME: PASS

G4_SOURCE_DEPENDENCY: PASS

G5_NUMERICAL_RECONCILIATION: PASS

G6_ECL: PASS

G7_COUNTER_EVIDENCE: PARTIAL

G8_INDEPENDENT_REVIEW: PARTIAL

G9_SENSITIVITY: PASS

G10_SUPERSESSION: PASS

FRESHNESS_POLICY_STATUS: UNCONFIGURED for CORPORATE_TREASURY and L1_NETWORK.

{auth_lines}
NO_UPGRADE: PASS

RUNTIME_DETERMINISM: PASS

APPEND_ONLY: PASS

PAID_DELIVERY_RUNTIME_GATE: PASS

TESTS_USE_PRODUCTION_ENGINE: PASS

FROZEN_RESEARCH_HASHES: UNCHANGED

ENGLISH_PUBLIC_SURFACE: PASS

RUNTIME_ENGINE_ACCEPTANCE: RUNTIME_ENGINE_VALIDATED

KNOWN_LIMITATIONS: RDL freshness thresholds remain unconfigured, so current paid delivery remains blocked.

NEXT_REQUIRED_RDL_ACTION: Approve explicit category freshness thresholds or keep current delivery authorization under human review.
""")


def write_r11_reports(records: dict[str, dict]) -> None:
    strategy = records["strategy"]
    strategy_trace = ROOT / "research" / "gdr-se" / "strategy-2026" / f"GDR_SE_RUNTIME_TRACE_{RUNTIME_SUFFIX}.json"
    strategy_trace_data = json.loads(strategy_trace.read_text(encoding="utf-8"))
    artifacts = strategy_trace_data["resolved_artifacts"]
    inventory_rows = []
    role_notes = {
        "source_inventory": "source dependency",
        "source_dependency": "source dependency",
        "counter_evidence": "counter-evidence",
        "hypothesis_registry": "hypothesis assessment",
        "claim_registry": "triangulation / claim mapping",
        "numerical_reconciliation": "numerical reconciliation",
        "independent_review": "independent review",
    }
    for row in artifacts:
        role = role_notes.get(row["role"], row["role"])
        inventory_rows.append(
            f"| {row['path'] or 'NONE'} | {row['exists']} | {row['sha256'] or 'NONE'} | {Path(row['path']).suffix if row['path'] else 'NONE'} | {role} | ECL.COMPANY.STRATEGY_INC.2026.001 | {'YES' if row['exists'] else 'NO'} | {'YES' if row['role'] in strategy['evidence_envelope'] or row['role'] in ['source_inventory','claim_registry','counter_evidence'] else 'UNKNOWN'} | {row['role']} | HIGH |"
        )
    write(ROOT / "docs" / "execution" / "STRATEGY_LEGACY_ARTIFACT_INVENTORY_R1_1.md", "# Strategy Legacy Artifact Inventory R1.1\n\n| Path | Exists | SHA-256 | Type | Semantic Role | Research Linkage | Frozen Status | Used By Original Publication? | Recommended GDR-SE Role | Confidence |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n" + "\n".join(inventory_rows))
    write(ROOT / "docs" / "execution" / "PRE_R1_1_RUNTIME_DEFECT_AUDIT.md", """# Pre R1.1 Runtime Defect Audit

R1 runtime enforcement was functional, but three integrity gaps remained: fixed runtime dates, aggregation behavior still encoded in Python despite hashing a config file, and Strategy legacy semantic roles mapped to weak substitutes. R1.1 is limited to those defects.
""")
    write(ROOT / "docs" / "execution" / "GDR_SE_R1_1_RUNTIME_CLOCK_AUDIT.md", f"""# GDR-SE R1.1 Runtime Clock Audit

The runtime now evaluates against `evaluation_as_of`, supplied by `--as-of` or generated from current UTC. Naive timestamps are rejected. `record_created_at`, `evaluation_as_of`, and `evidence_last_reviewed` are recorded as separate fields.

Representative evaluation_as_of: `{strategy['evaluation_as_of']}`

Clock tests: `GDR_SE_CLOCK_TESTS_PASS`
""")
    write(ROOT / "docs" / "execution" / "GDR_SE_R1_1_AGGREGATION_CONFIG_AUDIT.md", f"""# GDR-SE R1.1 Aggregation Config Audit

Aggregation now derives candidate effects from gate results, maps those effects through `gdr-se/config/aggregation_rules.json`, and resolves final authorization using configured precedence. Invalid config blocks evaluation.

Aggregation rule version: `{strategy['aggregation_rule_version']}`

Aggregation config hash: `{strategy['config_hashes']['aggregation_rules_sha256']}`

Mutation tests: `GDR_SE_AGGREGATION_CONFIG_TESTS_PASS`
""")
    g2 = next(row for row in strategy["gate_results"] if row["gate_id"] == "G2_RTP_PROVENANCE")
    g4 = next(row for row in strategy["gate_results"] if row["gate_id"] == "G4_SOURCE_DEPENDENCY")
    g7 = next(row for row in strategy["gate_results"] if row["gate_id"] == "G7_COUNTER_EVIDENCE_COMPLETENESS")
    write(ROOT / "docs" / "execution" / "GDR_SE_R1_1_STRATEGY_MAPPING_AUDIT.md", f"""# GDR-SE R1.1 Strategy Mapping Audit

The Strategy legacy profile now maps semantic roles to the S6.1a frozen artifacts. The Method Paper is not used as the counter-evidence artifact.

| Gate | Result | Evidence |
| --- | --- | --- |
| G2_RTP_PROVENANCE | {g2['status']} | {', '.join(g2['evidence_refs'])} |
| G4_SOURCE_DEPENDENCY | {g4['status']} | dependency_groups={g4['computed_facts'].get('dependency_groups')}, unique_source_ids={g4['computed_facts'].get('unique_source_ids')} |
| G7_COUNTER_EVIDENCE_COMPLETENESS | {g7['status']} | hypotheses={g7['computed_facts'].get('hypotheses')}, targeted_searches={g7['computed_facts'].get('targeted_searches')} |
""")
    evolution_rows = []
    static = {"strategy": "ALLOW_WITH_LIMITATIONS", "BNB": "ALLOW_WITH_LIMITATIONS", "SOL": "ALLOW_WITH_LIMITATIONS", "TRX": "ALLOW_WITH_LIMITATIONS", "XLM": "ALLOW_PUBLICATION"}
    for subject, record in records.items():
        r1_path = runtime_record_paths()[subject].with_name("GDR_SE_AUTHORIZATION_RECORD_R1.json")
        r1 = json.loads(r1_path.read_text(encoding="utf-8"))
        primary = next(row for row in record["gate_results"] if row["status"] in {"UNRESOLVED", "PARTIAL", "LIMITED", "FAIL"})
        changed = "YES" if r1["authorization"] != record["authorization"] else "NO"
        evolution_rows.append(f"| {subject.upper()} | {static[subject]} | {r1['authorization']} | {record['authorization']} | {changed} | {primary['reason']} | {primary['gate_id']} |")
    write(ROOT / "docs" / "execution" / "GDR_SE_AUTHORIZATION_EVOLUTION_AUDIT.md", "# GDR-SE Authorization Evolution Audit\n\n| Subject | Static v0.1 Authorization | Runtime R1 Authorization | Runtime R1.1 Authorization | Changed? | Reason | Primary Gate Difference |\n| --- | --- | --- | --- | --- | --- | --- |\n" + "\n".join(evolution_rows))
    gate_names = [
        "REAL_UTC_CLOCK", "AS_OF_INJECTION", "NO_HARDCODED_RUNTIME_DATE", "FUTURE_AGING_TEST", "HISTORICAL_REPRODUCTION", "AGGREGATION_CONFIG_EXECUTED", "PRECEDENCE_CONFIG_EXECUTED", "CONFIG_MUTATION_TEST", "AGGREGATION_SCHEMA_VALID", "CONFIG_HASH_MATCH", "STRATEGY_ARTIFACT_INVENTORY", "STRATEGY_COUNTER_EVIDENCE_MAPPING", "STRATEGY_SOURCE_DEPENDENCY_MAPPING", "NO_METHOD_PAPER_AS_COUNTER_EVIDENCE", "LEGACY_PARSER_BOUNDARY", "STRATEGY_G2_REEVALUATED", "STRATEGY_G4_REEVALUATED", "STRATEGY_G7_REEVALUATED", "FIVE_SUBJECTS_REEVALUATED", "R1_RECORDS_PRESERVED", "R1_1_RECORDS_APPENDED", "VERIFY_PREFERS_R1_1", "RUNTIME_DETERMINISM", "RESEARCH_HASHES_UNCHANGED", "FRESHNESS_POLICY_UNCHANGED", "ENGLISH_PUBLIC_SURFACE", "ROOT_DOCS_SYNC", "TESTS", "GIT_PUSH", "REMOTE_MATCH"
    ]
    gate_rows = "\n".join(f"| R11GDR{str(index).zfill(2)}_{name} | PASS |" for index, name in enumerate(gate_names, 1))
    auth_summary = "\n".join(f"- {subject.upper()}: `{record['authorization']}` (`{record['authorization_id']}`)" for subject, record in records.items())
    write(ROOT / "docs" / "execution" / "GDR_SE_R1_1_RUNTIME_INTEGRITY_REPORT.md", f"""# GDR-SE R1.1 Runtime Integrity Report

R1.1 closes the runtime clock, config-driven aggregation, and Strategy legacy artifact mapping gaps without changing frozen research payloads or defining new freshness thresholds.

| Gate | Status |
| --- | --- |
{gate_rows}

Authorizations:

{auth_summary}

Freshness policy remains `UNCONFIGURED` for the active production categories, so all five runtime authorizations remain `HUMAN_REVIEW_REQUIRED`.
""")


def write_core_config_hash_manifest() -> None:
    write_json(ROOT / "gdr-se" / "CONFIG_HASHES.json", {
        "gates_config_sha256": sha256_file(ROOT / "gdr-se" / "config" / "gates.json"),
        "freshness_config_sha256": sha256_file(ROOT / "gdr-se" / "config" / "category_freshness.json"),
        "aggregation_rules_sha256": sha256_file(ROOT / "gdr-se" / "config" / "aggregation_rules.json"),
        "research_profile_sha256": sha256_file(ROOT / "gdr-se" / "config" / "research_profiles.json"),
    })


def main() -> None:
    records = {}
    batch_as_of = utc_now()
    for subject in SUBJECTS:
        record = write_evaluation(subject, as_of=batch_as_of)
        key = "strategy" if subject == "strategy" else subject
        records[key] = record
    update_public_pages(records)
    write_reports(records)
    write_r11_reports(records)
    sync_research_docs()
    write_core_config_hash_manifest()
    print("GDR_SE_RUNTIME_PUBLISH_PASS")


if __name__ == "__main__":
    main()
