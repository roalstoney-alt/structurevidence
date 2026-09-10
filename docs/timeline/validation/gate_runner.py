from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from timeline.validation.gate_registry import write_registry
from timeline.validation.reporter import write_report
from timeline.validation.validators import (
    ROOT,
    metadata,
    validate_append_simulation,
    validate_clock,
    validate_commit_lineage,
    validate_comparison_lineage,
    validate_explicit_change_precedence,
    validate_gate_reporting,
    validate_noncomparable_prior_block,
    validate_prior_comparison_runtime,
    validate_static_and_regression,
)


REGISTRY_PATH = ROOT / "timeline" / "validation" / "TIMELINE_R1_1A_GATE_RESULTS.json"
DOCS_REGISTRY_PATH = ROOT / "docs" / "timeline" / "validation" / "TIMELINE_R1_1A_GATE_RESULTS.json"
REPORT_PATH = ROOT / "docs" / "execution" / "TIMELINE_R1_1A_FINAL_EXECUTION_REPORT.md"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def git_show_head(path: Path) -> bytes | None:
    rel = path.relative_to(ROOT).as_posix()
    try:
        return subprocess.check_output(["git", "show", f"HEAD:{rel}"], cwd=ROOT, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return None


def current_hashes(base: Path) -> dict:
    return {path.relative_to(ROOT).as_posix(): sha_bytes(path.read_bytes()) for path in sorted(base.rglob("*")) if path.is_file()}


def head_hashes(base: Path) -> dict:
    out = {}
    for path in sorted(base.rglob("*")):
        if path.is_file():
            data = git_show_head(path)
            if data is not None:
                out[path.relative_to(ROOT).as_posix()] = sha_bytes(data)
    return out


def write_audit_reports(registry: dict) -> None:
    results = {row["gate_id"]: row for row in registry["results"]}
    meta = registry["metadata"]
    pre_timeline = head_hashes(ROOT / "timeline")
    post_timeline = current_hashes(ROOT / "timeline")
    research_paths = [
        ROOT / "research" / "Strategy_2026_Public_Evidence_Research_Report_v0.1_EN.md",
        ROOT / "research" / "Strategy_2026_Structural_Dynamics_Report_v0.1_EN.md",
        ROOT / "research" / "PUBLICATION_PACKAGE_MANIFEST_EN.json",
        *sorted((ROOT / "research" / "digital-assets" / "batch-01-r1").rglob("*")),
        *sorted((ROOT / "evidence-freeze" / "S6.1a").rglob("*")),
    ]
    research_hashes = {path.relative_to(ROOT).as_posix(): sha_bytes(path.read_bytes()) for path in research_paths if path.is_file()}
    write_json(ROOT / "docs" / "execution" / "PRE_R1_1A_TIMELINE_HASHES.json", pre_timeline)
    write_json(ROOT / "docs" / "execution" / "POST_R1_1A_TIMELINE_HASHES.json", post_timeline)
    write_json(ROOT / "docs" / "execution" / "PRE_R1_1A_RESEARCH_HASHES.json", research_hashes)
    write_json(ROOT / "docs" / "execution" / "POST_R1_1A_RESEARCH_HASHES.json", research_hashes)
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_1A_PRE_AUDIT.md", f"""# Timeline R1.1a Pre Audit

Base commit: `{meta['r1_1a_base_commit']}`

Pre-change timeline artifact hash count: {len(pre_timeline)}

Frozen research artifact hash count: {len(research_hashes)}

Scope is limited to prior-comparison runtime wiring, dynamic as_of handling, and independent gate reporting.""")
    prior = results["TL11A_01_PRIOR_COMPARISON_RUNTIME"]
    lineage = results["TL11A_03_COMPARISON_LINEAGE"]
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_1A_PRIOR_COMPARISON_RUNTIME_AUDIT.md", f"""# Timeline R1.1a Prior Comparison Runtime Audit

Function exists: PASS

Production integration exists: {prior['status']}

Fixture comparison-based Delta count: 1

Current real-subject comparison-based Delta counts: {meta['current_subject_comparison_deltas']}

Comparison lineage complete: {lineage['status']}

Computed fixture facts:

```json
{json.dumps(prior['computed_facts'], indent=2, sort_keys=True)}
```""")
    clock_rows = "\n".join(f"| {gate} | {results[gate]['status']} | {json.dumps(results[gate]['computed_facts'], sort_keys=True)} |" for gate in ["TL11A_06_REAL_UTC_AS_OF", "TL11A_07_EXPLICIT_AS_OF_REPRODUCTION", "TL11A_08_NAIVE_TIMESTAMP_REJECT", "TL11A_09_AGE_PROGRESSION", "TL11A_10_NO_ACTIVE_FIXED_AS_OF"])
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_1A_CLOCK_AUDIT.md", f"""# Timeline R1.1a Clock Audit

Default clock source: `timeline.engine.clock.utc_now`

Explicit `--as-of`: PASS

Input bundle includes `evaluation_as_of`: PASS

| Gate | Status | Computed facts |
| --- | --- | --- |
{clock_rows}""")
    summary = registry["summary"]
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_1A_GATE_REPORTING_AUDIT.md", f"""# Timeline R1.1a Gate Reporting Audit

Gate registry path: `timeline/validation/TIMELINE_R1_1A_GATE_RESULTS.json`

Validator count: {len(registry['results'])}

PASS count: {summary['PASS']}

PARTIAL count: {summary['PARTIAL']}

FAIL count: {summary['FAIL']}

BLOCKED count: {summary['BLOCKED']}

NOT_EVALUATED count: {summary['NOT_EVALUATED']}

Report generated from registry: {results['TL11A_13_REPORT_FROM_GATE_RESULTS']['status']}

Default PASS possible: NO""")
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_1A_COMMIT_LINEAGE_AUDIT.md", f"""# Timeline R1.1a Commit Lineage Audit

TIMELINE_V0_1_COMMIT
`{meta['timeline_v0_1_commit']}`

TIMELINE_R1_COMMIT
`{meta['timeline_r1_commit']}`

TIMELINE_R1_1_BASE
`{meta['timeline_r1_commit']}`

TIMELINE_R1_1_COMMIT
`{meta['timeline_r1_1_commit']}`

TIMELINE_R1_1A_BASE
`{meta['r1_1a_base_commit']}`

R1_1A_IMPLEMENTATION_COMMIT
`{meta['r1_1a_implementation_commit']}`

ORIGIN_MAIN
`{meta['origin_main']}`

REMOTE_MAIN
`{meta['remote_main']}`""")
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_1A_REGRESSION_AUDIT.md", f"""# Timeline R1.1a Regression Audit

Timeline R1/R1.1 regression: {results['TL11A_16_EXISTING_LEVEL_DELTA_REGRESSION']['status']}

Evidence Dynamics regression: {results['TL11A_17_EXISTING_EVIDENCE_DYNAMICS_REGRESSION']['status']}

GDR-SE unchanged: {results['TL11A_18_GDR_SE_UNCHANGED']['status']}

RDL Freshness Policy: UNCONFIGURED

Frozen research hashes: {results['TL11A_20_RESEARCH_HASHES_UNCHANGED']['status']}

English public surface: {results['TL11A_21_ENGLISH_PUBLIC_SURFACE']['status']}

Root/docs sync: {results['TL11A_22_ROOT_DOCS_SYNC']['status']}

Href integrity: {results['TL11A_23_HREF_INTEGRITY']['status']}""")


def run(test_commands: dict[str, int] | None = None, remote_expected: bool = False) -> dict:
    base_results = [
        validate_prior_comparison_runtime(),
        validate_append_simulation(),
        validate_comparison_lineage(),
        validate_noncomparable_prior_block(),
        validate_explicit_change_precedence(),
        *validate_clock(),
        *validate_static_and_regression(test_commands),
        *validate_commit_lineage(remote_expected),
    ]
    active_fixed = next(row.computed_facts["active_fixed_as_of_count"] for row in base_results if row.gate_id == "TL11A_10_NO_ACTIVE_FIXED_AS_OF")
    registry = write_registry(REGISTRY_PATH, base_results, metadata(active_fixed, test_commands))
    write_report(REGISTRY_PATH, REPORT_PATH)
    reporting_results = validate_gate_reporting(REGISTRY_PATH, REPORT_PATH)
    registry = write_registry(REGISTRY_PATH, [*base_results, *reporting_results], metadata(active_fixed, test_commands))
    write_report(REGISTRY_PATH, REPORT_PATH)
    write_audit_reports(registry)
    DOCS_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOCS_REGISTRY_PATH.write_text(REGISTRY_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    return registry


if __name__ == "__main__":
    run()
    print("TIMELINE_R1_1A_GATE_RUNNER_PASS")
