#!/usr/bin/env python3
"""Build public-safe growth-pilot exports without publishing or outreach."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "cases" / "iren-ai-cloud-transition"
GROWTH = ROOT / "growth" / "external-challenge"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_digest(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build(run_date: str) -> dict:
    date.fromisoformat(run_date)
    tracker = load(CASE / "tracker-v0.1.json")
    registry = load(CASE / "source-registry-v0.1.json")
    ledger = load(CASE / tracker["event_ledger"])
    sources = {source["source_id"]: source for source in registry["sources"]}

    incomplete = sorted(
        source_id for source_id, source in sources.items()
        if "INCOMPLETE" in source["access_state"]
    )
    status = "RETRIEVAL_INCOMPLETE" if incomplete else "NO_QUALIFYING_CHANGE"
    reason = (
        "No qualifying state-changing event is recorded after the current page revision; "
        f"source retrieval remains incomplete for {', '.join(incomplete)}."
        if incomplete else
        "No qualifying state-changing event is recorded after the current page revision."
    )

    claims = []
    for row in tracker["rows"]:
        row_sources = [sources[source_id] for source_id in row["source_ids"]]
        claims.append({
            "claim_id": row["row_id"],
            "public_claim": row["claim"],
            "speaker_attribution": (
                "IREN Limited — issuer-authored disclosure"
                if row["state"] == "SUPPORTED_AS_ATTRIBUTED"
                else "StructEvidence — bounded state derived from the reviewed source set"
            ),
            "evidence_state": row["state"],
            "evidence_boundary": row["boundary"],
            "source_references": row["source_ids"],
            "availability": [f"{source['source_id']}:{source['access_state']}" for source in row_sources],
            "evidence_cutoff": tracker["evidence_cutoff"],
            "capture_hashes": {source["source_id"]: source.get("sha256") for source in row_sources},
            "changed_conditions": [],
            "review_status": row["reading_check"],
            "what_would_change_it": row["next_check"],
        })

    export = {
        "schema_version": "SE-EXTERNAL-CHALLENGE-EVIDENCE-EXPORT-v0.1",
        "export_id": f"SE-IREN-EXPORT-{run_date.replace('-', '')}",
        "case_id": tracker["case_id"],
        "generated_for_date": run_date,
        "evidence_cutoff": tracker["evidence_cutoff"],
        "tracker_version": tracker["tracker_data_version"],
        "source_check_utc": tracker["last_source_check_utc"],
        "status": status,
        "status_reason": reason,
        "qualifying_change_count": 0,
        "changed_conditions": [],
        "claims": claims,
        "review_status": tracker["reviewer_status"],
        "publication_status": "DO_NOT_PUBLISH_UNTIL_HUMAN_REVIEW",
    }
    export["content_sha256"] = canonical_digest(export)
    out_dir = GROWTH / "evidence-exports"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{run_date}.json").write_text(
        json.dumps(export, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    selected = {"IREN-R003", "IREN-R004", "IREN-R009"}
    cards = []
    for row in tracker["rows"]:
        if row["row_id"] not in selected:
            continue
        first_source = sources[row["source_ids"][0]]
        cards.append({
            "card_id": f"SE-CARD-{row['row_id']}",
            "claim_id": row["row_id"],
            "public_claim": row["claim"],
            "evidence_boundary": row["boundary"],
            "what_remains_unknown": row.get("plain_language", "The boundary remains unresolved in the reviewed source set."),
            "what_would_change_it": row["next_check"],
            "source_url": first_source["url"],
            "source_ids": row["source_ids"],
            "cutoff": tracker["evidence_cutoff"],
            "version": tracker["tracker_data_version"],
            "identity": "StructEvidence · Verify Your Verify",
            "state": row["state"],
            "publication_status": "DO_NOT_PUBLISH",
        })
    visuals = GROWTH / "visuals"
    visuals.mkdir(parents=True, exist_ok=True)
    (visuals / "card-data.json").write_text(
        json.dumps({"schema_version": "SE-SOCIAL-CARD-DATA-v0.1", "cards": cards}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return export


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat())
    args = parser.parse_args()
    result = build(args.date)
    print(f"{result['export_id']} {result['status']} claims={len(result['claims'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
