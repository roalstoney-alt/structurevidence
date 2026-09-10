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
from evaluator import CREATED_AT, VERSION, evaluate  # noqa: E402
from integrity import canonical_sha256  # noqa: E402
from resolver import resolve  # noqa: E402


SUBJECTS = ["strategy", "BNB", "SOL", "TRX", "XLM"]


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def authorization_id(evaluation) -> str:
    return f"GDR-SE-AUTH-{evaluation.context.subject}-{evaluation.input_bundle_sha256[:16]}-R1"


def record_for(evaluation) -> dict:
    return {
        "authorization_id": authorization_id(evaluation),
        "research_id": evaluation.context.research_id,
        "report_id": evaluation.context.report_id,
        "report_version": evaluation.context.report_version,
        "gdr_se_version": VERSION,
        "evaluation_mode": "RUNTIME_EVALUATED",
        "evaluation_id": evaluation.evaluation_id,
        "profile": evaluation.context.profile,
        "authorization": evaluation.authorization,
        "public_status": evaluation.public_status,
        "gate_results": evaluation.gate_results,
        "limitations": sorted({lim for row in evaluation.gate_results for lim in row["limitations"]}),
        "counterfactual": build_counterfactual(evaluation.context),
        "created_at": CREATED_AT,
        "valid_until": None,
        "supersedes_authorization_id": evaluation.context.static_authorization_id,
        "input_bundle_sha256": evaluation.input_bundle_sha256,
        "config_hashes": evaluation.config_hashes,
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
        "authorization_id": record["authorization_id"],
        "authorization": evaluation.authorization,
        "input_bundle_sha256": evaluation.input_bundle_sha256,
        "gate_summary": [{"gate_id": row["gate_id"], "status": row["status"], "validator": row["validator"]} for row in evaluation.gate_results],
        "created_at": CREATED_AT,
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
        "aggregation_rule_version": "GDR_SE_AGGREGATION_v0.1-R1",
        "final_authorization": evaluation.authorization,
        "authorization_id": record["authorization_id"],
        "input_bundle_sha256": evaluation.input_bundle_sha256,
        "created_at": CREATED_AT,
    }


def gate_table(evaluation) -> str:
    rows = "\n".join(
        f"| {row['gate_id']} | {row['status']} | {row['severity']} | {row['validator']} | {row['rule_version']} | {row['reason']} |"
        for row in evaluation.gate_results
    )
    return f"""# GDR-SE Runtime Gate Table R1

| Gate | Status | Severity | Validator | Rule Version | Reason |
| --- | --- | --- | --- | --- | --- |
{rows}

Authorization: `{evaluation.authorization}`

Input Bundle SHA-256: `{evaluation.input_bundle_sha256}`
"""


def append_history(record: dict) -> None:
    history_dir = ROOT / "gdr-se" / "records" / record["research_id"].replace("/", "_").replace(":", "_")
    history_dir.mkdir(parents=True, exist_ok=True)
    history = history_dir / "authorization_history.jsonl"
    existing = history.read_text(encoding="utf-8").splitlines() if history.exists() else []
    line = json.dumps(record, sort_keys=True)
    if line not in existing:
        with history.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")


def write_evaluation(subject: str) -> dict:
    evaluation = evaluate(resolve(subject, ROOT), ROOT)
    record = record_for(evaluation)
    out = evaluation.context.output_dir
    write_json(out / "GDR_SE_AUTHORIZATION_RECORD_R1.json", record)
    write_json(out / "GDR_SE_OVERLAY_R1.json", overlay_for(evaluation, record))
    write_json(out / "GDR_SE_RUNTIME_TRACE.json", trace_for(evaluation, record))
    write_text(out / "GDR_SE_GATE_TABLE_R1.md", gate_table(evaluation))
    append_history(record)
    return record


def dry_run(subject: str) -> dict:
    evaluation = evaluate(resolve(subject, ROOT), ROOT)
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
    args = parser.parse_args(argv)
    subjects = SUBJECTS if args.all else [args.subject]
    if not subjects or subjects == [None]:
        parser.error("--subject or --all is required")
    records = []
    for subject in subjects:
        record = write_evaluation(subject) if args.write else dry_run(subject)
        records.append(record)
        print(f"{subject}: {record['authorization']} {record['authorization_id']}")
    if args.write:
        sync_docs()
    digest = canonical_sha256([{k: r[k] for k in ["authorization_id", "authorization", "input_bundle_sha256"]} for r in records])
    print(f"GDR_SE_RUNTIME_EVALUATION_HASH {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
