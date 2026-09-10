from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "gdr-se" / "engine"
sys.path.insert(0, str(ENGINE))

from counterfactual import build_counterfactual  # noqa: E402
from clock import normalize_as_of  # noqa: E402
from evaluator import RUNTIME_REVISION, VERSION, evaluate  # noqa: E402
from integrity import canonical_sha256  # noqa: E402
from resolver import resolve  # noqa: E402


SUBJECTS = ["strategy", "BNB", "SOL", "TRX", "XLM"]
RUNTIME_SUFFIX = "R1_1"


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def authorization_id(evaluation) -> str:
    return f"GDR-SE-AUTH-{evaluation.context.subject}-{evaluation.input_bundle_sha256[:16]}-R1.1"


def previous_runtime_authorization_id(evaluation) -> str | None:
    previous = evaluation.context.output_dir / "GDR_SE_AUTHORIZATION_RECORD_R1.json"
    if previous.exists():
        return json.loads(previous.read_text(encoding="utf-8")).get("authorization_id")
    return evaluation.context.static_authorization_id


def record_for(evaluation) -> dict:
    return {
        "authorization_id": authorization_id(evaluation),
        "research_id": evaluation.context.research_id,
        "report_id": evaluation.context.report_id,
        "report_version": evaluation.context.report_version,
        "gdr_se_version": VERSION,
        "evaluation_mode": "RUNTIME_EVALUATED",
        "runtime_revision": RUNTIME_REVISION,
        "evaluation_id": evaluation.evaluation_id,
        "profile": evaluation.context.profile,
        "authorization": evaluation.authorization,
        "public_status": evaluation.public_status,
        "gate_results": evaluation.gate_results,
        "limitations": sorted({lim for row in evaluation.gate_results for lim in row["limitations"]}),
        "counterfactual": build_counterfactual(evaluation.context),
        "evaluation_as_of": evaluation.evaluation_as_of,
        "record_created_at": evaluation.record_created_at,
        "evidence_last_reviewed": evaluation.context.last_reviewed,
        "created_at": evaluation.record_created_at,
        "valid_until": None,
        "supersedes_authorization_id": previous_runtime_authorization_id(evaluation),
        "input_bundle_sha256": evaluation.input_bundle_sha256,
        "config_hashes": evaluation.config_hashes,
        "aggregation_rule_version": evaluation.aggregation_rule_version,
        "evidence_envelope": evaluation.evidence_envelope,
        "research_status": evaluation.context.research_status,
        "structural_state_reference": evaluation.context.structural_state,
        "evidence_state_reference": evaluation.context.evidence_state,
    }


def overlay_for(evaluation, record: dict) -> dict:
    return {
        "research_id": evaluation.context.research_id,
        "original_canonical_sha256": evaluation.evidence_envelope["canonical_research_sha256"],
        "gdr_se_version": VERSION,
        "evaluation_mode": "RUNTIME_EVALUATED",
        "runtime_revision": RUNTIME_REVISION,
        "authorization_id": record["authorization_id"],
        "authorization": evaluation.authorization,
        "input_bundle_sha256": evaluation.input_bundle_sha256,
        "gate_summary": [{"gate_id": row["gate_id"], "status": row["status"], "validator": row["validator"]} for row in evaluation.gate_results],
        "evaluation_as_of": evaluation.evaluation_as_of,
        "record_created_at": evaluation.record_created_at,
    }


def trace_for(evaluation, record: dict) -> dict:
    return {
        "evaluation_id": evaluation.evaluation_id,
        "research_id": evaluation.context.research_id,
        "profile": evaluation.context.profile,
        "resolved_artifacts": evaluation.artifact_metadata,
        "artifact_hashes": {row["role"]: row["sha256"] for row in evaluation.artifact_metadata},
        "config_hashes": evaluation.config_hashes,
        "gate_results": evaluation.gate_results,
        "aggregation_rule_version": evaluation.aggregation_rule_version,
        "final_authorization": evaluation.authorization,
        "authorization_id": record["authorization_id"],
        "input_bundle_sha256": evaluation.input_bundle_sha256,
        "evaluation_as_of": evaluation.evaluation_as_of,
        "record_created_at": evaluation.record_created_at,
    }


def gate_table(evaluation) -> str:
    rows = "\n".join(
        f"| {row['gate_id']} | {row['status']} | {row['severity']} | {row['validator']} | {row['rule_version']} | {row['reason']} |"
        for row in evaluation.gate_results
    )
    return f"""# GDR-SE Runtime Gate Table R1.1

| Gate | Status | Severity | Validator | Rule Version | Reason |
| --- | --- | --- | --- | --- | --- |
{rows}

Authorization: `{evaluation.authorization}`

Evaluation As Of: `{evaluation.evaluation_as_of}`

Input Bundle SHA-256: `{evaluation.input_bundle_sha256}`
"""


def append_history(record: dict) -> None:
    history_dir = ROOT / "gdr-se" / "records" / record["research_id"].replace("/", "_").replace(":", "_")
    history_dir.mkdir(parents=True, exist_ok=True)
    history = history_dir / "authorization_history.jsonl"
    existing = history.read_text(encoding="utf-8").splitlines() if history.exists() else []
    existing_ids = {json.loads(line).get("authorization_id") for line in existing if line.strip()}
    line = json.dumps(record, sort_keys=True)
    if record["authorization_id"] not in existing_ids:
        with history.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")


def write_evaluation(subject: str, as_of=None) -> dict:
    evaluation = evaluate(resolve(subject, ROOT), ROOT, as_of=as_of)
    record = record_for(evaluation)
    out = evaluation.context.output_dir
    write_json(out / f"GDR_SE_AUTHORIZATION_RECORD_{RUNTIME_SUFFIX}.json", record)
    write_json(out / f"GDR_SE_OVERLAY_{RUNTIME_SUFFIX}.json", overlay_for(evaluation, record))
    write_json(out / f"GDR_SE_RUNTIME_TRACE_{RUNTIME_SUFFIX}.json", trace_for(evaluation, record))
    write_text(out / f"GDR_SE_GATE_TABLE_{RUNTIME_SUFFIX}.md", gate_table(evaluation))
    append_history(record)
    return record


def dry_run(subject: str, as_of=None) -> dict:
    evaluation = evaluate(resolve(subject, ROOT), ROOT, as_of=as_of)
    return record_for(evaluation)


def sync_docs() -> None:
    shutil.copyfile(ROOT / "gdr.html", ROOT / "docs" / "gdr.html")
    shutil.copyfile(ROOT / "verify.html", ROOT / "docs" / "verify.html")
    shutil.copytree(ROOT / "research" / "gdr-se", ROOT / "docs" / "research" / "gdr-se", dirs_exist_ok=True)
    for symbol in ["BNB", "SOL", "TRX", "XLM"]:
        shutil.copytree(
            ROOT / "research" / "digital-assets" / "batch-01-r1" / symbol / "gdr-se",
            ROOT / "docs" / "research" / "digital-assets" / "batch-01-r1" / symbol / "gdr-se",
            dirs_exist_ok=True,
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", choices=SUBJECTS)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--as-of", help="Timezone-aware UTC evaluation timestamp, for example YYYY-MM-DDTHH:MM:SSZ")
    args = parser.parse_args(argv)
    try:
        as_of = normalize_as_of(args.as_of) if args.as_of else None
    except ValueError as exc:
        parser.error(str(exc))
    subjects = SUBJECTS if args.all else [args.subject]
    if not subjects or subjects == [None]:
        parser.error("--subject or --all is required")
    records = []
    for subject in subjects:
        record = write_evaluation(subject, as_of=as_of) if args.write else dry_run(subject, as_of=as_of)
        records.append(record)
        print(f"{subject}: {record['authorization']} {record['authorization_id']}")
    if args.write:
        sync_docs()
    digest = canonical_sha256([{k: r[k] for k in ["authorization_id", "authorization", "input_bundle_sha256"]} for r in records])
    print(f"GDR_SE_RUNTIME_EVALUATION_HASH {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
