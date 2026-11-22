#!/usr/bin/env python3
"""Build or apply a verified, append-only Anthropic publication overlay.

The event input must describe an already successful GitHub Pages deployment and
an observed live case. This tool never invents those facts. It leaves frozen
claim rows and the public source registry byte-identical, appends one event, and
projects current publication state into the mutable public presentation files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE_ID = "SE-AI-COMPUTE-OBLIGATIONS-001"
CASE_SLUG = "cases/anthropic-compute-obligations"
CANONICAL_URL = "https://structurevidence.org/cases/anthropic-compute-obligations/"
SOURCE_SHA256 = "0c3a6faad0e1bddc30b108054ec318a0ed5ea509b0ff1d6c8f16a8bdf234424b"
REVIEWED_HEAD = "f195d44e464e7c27c23d1a1eb5b9858687166dfc"
REQUIRED_OWNER_DECISION = "APPROVE_ATOMIC_PUBLICATION_ACTIVATION_AND_AUTO_DEPLOY"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def jsonl_bytes(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for row in rows) + "\n").encode()


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load(root: Path, relative: str) -> dict:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def parse_time(value: str, field: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{field} must be an observed RFC3339 UTC timestamp ending in Z")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} is not a valid RFC3339 timestamp") from exc


def validate_event(event: dict, *, allow_test_fixture: bool = False) -> None:
    required = {
        "schema_version", "case_id", "event_id", "event_type", "owner_decision",
        "owner_authorized_at", "candidate_head_sha", "merge_commit_sha",
        "publication_event_at", "pages_workflow_run_id", "pages_deployment_id",
        "pages_deployment_status_id", "pages_deployment_succeeded_at",
        "pages_source_branch", "pages_source_path", "pages_trigger",
        "deployment_environment", "deployment_status", "live_case_url",
        "live_case_http_status", "live_case_sha256", "live_index_sha256",
        "live_claims_sha256", "live_verified_at", "source_sha256",
        "owner_review_gate", "test_fixture",
    }
    missing = sorted(required - event.keys())
    if missing:
        raise ValueError(f"activation event missing fields: {missing}")
    if event["schema_version"] != "SE-AICO-PUBLICATION-ACTIVATION-EVENT-v0.2":
        raise ValueError("unexpected activation event schema")
    if event["case_id"] != CASE_ID or event["event_type"] != "PUBLICATION_ACTIVATION_VERIFIED":
        raise ValueError("event is not the verified activation for this case")
    if event["owner_decision"] != REQUIRED_OWNER_DECISION:
        raise ValueError("a separate exact merge+automatic-deploy owner decision is required")
    if event["test_fixture"] is True and not allow_test_fixture:
        raise ValueError("test fixtures cannot produce an actual activation overlay")
    if event["test_fixture"] not in (True, False):
        raise ValueError("test_fixture must be boolean")
    if not SHA_RE.fullmatch(event["candidate_head_sha"]) or not SHA_RE.fullmatch(event["merge_commit_sha"]):
        raise ValueError("candidate and merge commit SHAs must be exact 40-character Git SHAs")
    for field in ("live_case_sha256", "live_index_sha256", "live_claims_sha256", "source_sha256"):
        if not SHA256_RE.fullmatch(event[field]):
            raise ValueError(f"{field} must be SHA256")
    if event["source_sha256"] != SOURCE_SHA256:
        raise ValueError("reviewed SEC source digest changed")
    if event["pages_source_branch"] != "main" or event["pages_source_path"] != "/":
        raise ValueError("event does not match the verified Pages source")
    if event["pages_trigger"] != "PUSH_TO_MAIN_AUTOMATIC_PAGES_BUILD":
        raise ValueError("event does not match the verified automatic Pages trigger")
    if event["deployment_environment"] != "github-pages" or event["deployment_status"] != "success":
        raise ValueError("GitHub Pages deployment is not recorded as successful")
    if event["live_case_url"] != CANONICAL_URL or event["live_case_http_status"] != 200:
        raise ValueError("canonical case URL was not successfully observed")
    if event["owner_review_gate"] != "OWNER_REVIEW_OF_ATOMIC_PUBLICATION_ACTIVATION":
        raise ValueError("activation event references the wrong owner gate")
    for field in ("pages_workflow_run_id", "pages_deployment_id", "pages_deployment_status_id"):
        if not isinstance(event[field], int) or event[field] <= 0:
            raise ValueError(f"{field} must be an actual positive GitHub ID")
    authorized = parse_time(event["owner_authorized_at"], "owner_authorized_at")
    deployed = parse_time(event["pages_deployment_succeeded_at"], "pages_deployment_succeeded_at")
    published = parse_time(event["publication_event_at"], "publication_event_at")
    verified = parse_time(event["live_verified_at"], "live_verified_at")
    if published != deployed:
        raise ValueError("publication_event_at must equal the observed successful Pages deployment time")
    if not authorized <= deployed <= verified:
        raise ValueError("authorization, deployment and live verification times are out of order")


def verify_frozen_inputs(source_root: Path) -> dict[str, str]:
    claims = (source_root / CASE_SLUG / "claims-v0.2.jsonl").read_bytes()
    registry = (source_root / CASE_SLUG / "source-registry-public-v0.2.json").read_bytes()
    registry_json = json.loads(registry)
    if registry_json["sources"][0]["raw_sha256"] != SOURCE_SHA256:
        raise ValueError("source registry no longer carries the reviewed SEC digest")
    if len([line for line in claims.splitlines() if line]) != 15:
        raise ValueError("frozen claim row count changed")
    return {
        "claims_v0_2_sha256": digest_bytes(claims),
        "source_registry_sha256": digest_bytes(registry),
        "source_capture_sha256_carried_forward": SOURCE_SHA256,
    }


def replace_jsonld(html: str, event: dict) -> str:
    marker = '<script type="application/ld+json">'
    start = html.index(marker) + len(marker)
    end = html.index("</script>", start)
    metadata = json.loads(html[start:end])
    metadata["creativeWorkStatus"] = "PUBLISHED_VERIFIED"
    metadata["datePublished"] = event["publication_event_at"]
    metadata["dateModified"] = event["live_verified_at"]
    metadata["name"] = "Anthropic compute obligations — verified public release"
    for claim in metadata["hasPart"]:
        for prop in claim.get("additionalProperty", []):
            if prop.get("name") == "claim_record_published_at":
                prop["value"] = event["publication_event_at"]
    value = json.dumps(metadata, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    html = html[:start] + value + html[end:]
    status = (
        '<section class="publication-state" data-publication-state="PUBLISHED_VERIFIED">'
        '<h2>Publication state</h2><p>Verified live publication. '
        f'Activated at <time datetime="{event["publication_event_at"]}">{event["publication_event_at"]}</time>; '
        '<a href="publication-receipt-v0.2.json">append-only deployment receipt</a>. '
        'Evidence conclusions and issuer attribution are unchanged.</p></section>'
    )
    return html.replace("<main>", "<main>\n" + status, 1)


def build_overlay(source_root: Path, event: dict, *, allow_test_fixture: bool = False) -> dict[str, bytes]:
    validate_event(event, allow_test_fixture=allow_test_fixture)
    frozen = verify_frozen_inputs(source_root)
    publication_date = event["publication_event_at"][:10]

    index = load(source_root, f"{CASE_SLUG}/index.json")
    original_claims = json.loads(json.dumps(index["claims"]))
    index.update({
        "status": "PUBLICATION_ACTIVATED_AND_LIVE_VERIFIED",
        "deployment_state": "APPLIED_AND_LIVE_VERIFIED",
        "publication_authorized": True,
        "claim_record_published_at": event["publication_event_at"],
        "structevidence_publication_date": publication_date,
        "publication_event_at": event["publication_event_at"],
        "publication_current_state": "publication-current-state-v0.2.json",
        "publication_receipt": "publication-receipt-v0.2.json",
        "historical_prepublication_head_sha": REVIEWED_HEAD,
        "prepublication_claim_rows_rewritten": False,
    })
    if index["claims"] != original_claims:
        raise AssertionError("embedded evidence claims changed during publication projection")

    metadata = load(source_root, f"{CASE_SLUG}/structured-metadata-v0.2.json")
    metadata.update({
        "creativeWorkStatus": "PUBLISHED_VERIFIED",
        "datePublished": event["publication_event_at"],
        "dateModified": event["live_verified_at"],
        "name": "Anthropic compute obligations — verified public release",
    })

    existing_events_bytes = (source_root / CASE_SLUG / "events-v0.2.jsonl").read_bytes()
    existing_events = [json.loads(line) for line in existing_events_bytes.splitlines() if line]
    if any(row.get("event_id") == event["event_id"] for row in existing_events):
        raise ValueError("activation event_id already exists")
    appended_event = {
        "event_id": event["event_id"],
        "event_type": "PUBLICATION_ACTIVATION_VERIFIED",
        "event_at": event["publication_event_at"],
        "known_at": event["live_verified_at"],
        "recorded_at_utc": event["live_verified_at"],
        "state_before": "PREPUBLICATION_CANDIDATE_PUBLICATION_HOLD",
        "state_after": "PUBLISHED_AND_LIVE_VERIFIED",
        "publication_effect": "CURRENT_PUBLIC_STATE_ACTIVATED",
        "owner_decision": event["owner_decision"],
        "merge_commit_sha": event["merge_commit_sha"],
        "pages_workflow_run_id": event["pages_workflow_run_id"],
        "pages_deployment_id": event["pages_deployment_id"],
        "live_case_sha256": event["live_case_sha256"],
        "source_sha256": SOURCE_SHA256,
        "historical_rows_rewritten": False,
    }
    events = existing_events + [appended_event]

    current_state = {
        "schema_version": "SE-AICO-PUBLICATION-CURRENT-STATE-v0.2",
        "case_id": CASE_ID,
        "status": "PUBLISHED_AND_LIVE_VERIFIED",
        "publication_event_at": event["publication_event_at"],
        "live_verified_at": event["live_verified_at"],
        "event_id": event["event_id"],
        "owner_decision": event["owner_decision"],
        "owner_review_gate": event["owner_review_gate"],
        "candidate_head_sha": event["candidate_head_sha"],
        "merge_commit_sha": event["merge_commit_sha"],
        "pages": {
            "source_branch": "main",
            "source_path": "/",
            "trigger": "PUSH_TO_MAIN_AUTOMATIC_PAGES_BUILD",
            "workflow_run_id": event["pages_workflow_run_id"],
            "deployment_id": event["pages_deployment_id"],
            "deployment_status_id": event["pages_deployment_status_id"],
            "deployment_succeeded_at": event["pages_deployment_succeeded_at"],
        },
        "live": {
            "url": CANONICAL_URL,
            "http_status": 200,
            "case_sha256": event["live_case_sha256"],
            "index_sha256": event["live_index_sha256"],
            "claims_sha256": event["live_claims_sha256"],
        },
        "evidence_state_changed": False,
        "historical_prepublication_head_sha": REVIEWED_HEAD,
        "historical_prepublication_rows_rewritten": False,
        "source_sha256": SOURCE_SHA256,
    }
    receipt = {
        "schema_version": "SE-AICO-PUBLICATION-RECEIPT-v0.2",
        "case_id": CASE_ID,
        "status": "ACTUAL_DEPLOYMENT_AND_LIVE_URL_VERIFIED",
        "receipt_id": event["event_id"] + "-RECEIPT",
        "publication_event_at": event["publication_event_at"],
        "live_verified_at": event["live_verified_at"],
        "activated_commit_sha": event["merge_commit_sha"],
        "candidate_head_sha": event["candidate_head_sha"],
        "deployment_environment": "github-pages",
        "pages_workflow_run_id": event["pages_workflow_run_id"],
        "pages_deployment_id": event["pages_deployment_id"],
        "pages_deployment_status_id": event["pages_deployment_status_id"],
        "live_case_url": CANONICAL_URL,
        "live_case_http_status": 200,
        "live_case_sha256": event["live_case_sha256"],
        "live_index_sha256": event["live_index_sha256"],
        "live_claims_sha256": event["live_claims_sha256"],
        "source_sha256": SOURCE_SHA256,
        "append_only": True,
        "prepublication_history_rewritten": False,
        "frozen_input_hashes": frozen,
    }

    discovery = load(source_root, ".well-known/structurevidence.json")
    claims_index = load(source_root, "claims/index.json")
    for document, key in ((discovery, "versioned_case_adapters"), (claims_index, "versioned_adapters")):
        adapter = next(row for row in document[key] if row["case_id"] == CASE_ID)
        adapter["structevidence_date_published"] = event["publication_event_at"]
        adapter["publication_current_state"] = CANONICAL_URL + "publication-current-state-v0.2.json"
        adapter["publication_receipt"] = CANONICAL_URL + "publication-receipt-v0.2.json"

    review = load(source_root, "cases/review-status.json")
    row = next(item for item in review["cases"] if item["case_id"] == CASE_ID)
    row.update({
        "last_reviewed_at": event["owner_authorized_at"],
        "review_result": "PUBLICATION_ACTIVATION_APPROVED",
        "latest_review_id": event["event_id"],
        "latest_review_file": f"{CASE_SLUG}/publication-receipt-v0.2.json",
        "period": {
            "id": "OWNER_REVIEW_OF_ATOMIC_PUBLICATION_ACTIVATION",
            "start": event["owner_authorized_at"][:10],
            "end": event["owner_authorized_at"][:10],
            "status": "PUBLICATION_ACTIVATION_APPROVED",
            "scope": "Exact commit deployment and canonical live URL verified; evidence conclusions unchanged.",
        },
        "period_review_id": event["event_id"],
    })

    case_index_html = (source_root / "cases/index.html").read_text(encoding="utf-8")
    old = '<strong>Pending review · OWNER_REVIEW_OF_EXACT_MINIMAL_PR_DIFF</strong><br><small>No completed review recorded for this period.</small>'
    new = (
        f'<time datetime="{event["owner_authorized_at"]}">{event["owner_authorized_at"][:10]}</time><br>'
        '<strong>PUBLICATION ACTIVATION APPROVED</strong><br><small>'
        'OWNER_REVIEW_OF_ATOMIC_PUBLICATION_ACTIVATION · Exact commit deployment and canonical live URL verified; '
        'evidence conclusions unchanged.</small><br>'
        '<a href="/cases/anthropic-compute-obligations/publication-receipt-v0.2.json">Review record</a>'
    )
    if old not in case_index_html:
        raise ValueError("obsolete pending-review label was not found exactly once")
    case_index_html = case_index_html.replace(old, new, 1)

    case_html = replace_jsonld((source_root / CASE_SLUG / "index.html").read_text(encoding="utf-8"), event)
    relative = {
        f"{CASE_SLUG}/index.json": json_bytes(index),
        f"{CASE_SLUG}/structured-metadata-v0.2.json": json_bytes(metadata),
        f"{CASE_SLUG}/events-v0.2.jsonl": jsonl_bytes(events),
        f"{CASE_SLUG}/publication-current-state-v0.2.json": json_bytes(current_state),
        f"{CASE_SLUG}/publication-receipt-v0.2.json": json_bytes(receipt),
        f"{CASE_SLUG}/index.html": case_html.encode(),
        ".well-known/structurevidence.json": json_bytes(discovery),
        "claims/index.json": json_bytes(claims_index),
        "cases/review-status.json": json_bytes(review),
        "cases/index.html": case_index_html.encode(),
    }
    overlay = dict(relative)
    for path, value in relative.items():
        overlay["docs/" + path] = value
    return overlay


def write_overlay(output_dir: Path, overlay: dict[str, bytes], event: dict) -> None:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("output directory must be empty")
    output_dir.mkdir(parents=True, exist_ok=True)
    for relative, value in overlay.items():
        path = output_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value)
    manifest = {
        "schema_version": "SE-AICO-ACTIVATION-OVERLAY-MANIFEST-v0.2",
        "case_id": CASE_ID,
        "event_id": event["event_id"],
        "candidate_head_sha": event["candidate_head_sha"],
        "test_fixture": event["test_fixture"],
        "files": [
            {"path": path, "sha256": digest_bytes(value), "bytes": len(value)}
            for path, value in sorted(overlay.items())
        ],
    }
    (output_dir / "activation-manifest-v0.2.json").write_bytes(json_bytes(manifest))


def apply_overlay(target: Path, output_dir: Path, event: dict) -> None:
    if event["test_fixture"]:
        raise ValueError("test fixture overlays cannot be applied")
    current = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=target, text=True).strip()
    if current != event["candidate_head_sha"]:
        raise ValueError(f"target HEAD {current} does not match authorized candidate {event['candidate_head_sha']}")
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=target, text=True).strip():
        raise ValueError("target worktree is not clean")
    manifest = json.loads((output_dir / "activation-manifest-v0.2.json").read_text())
    with tempfile.TemporaryDirectory(dir=target) as temporary:
        stage = Path(temporary)
        for item in manifest["files"]:
            source = output_dir / item["path"]
            if digest_bytes(source.read_bytes()) != item["sha256"]:
                raise ValueError(f"overlay hash mismatch: {item['path']}")
            destination = stage / item["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        for item in manifest["files"]:
            destination = target / item["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(stage / item["path"], destination)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--allow-test-fixture", action="store_true")
    parser.add_argument("--apply-to", type=Path)
    args = parser.parse_args()
    event = json.loads(args.event.read_text(encoding="utf-8"))
    overlay = build_overlay(args.source_root, event, allow_test_fixture=args.allow_test_fixture)
    write_overlay(args.output_dir, overlay, event)
    if args.apply_to:
        apply_overlay(args.apply_to, args.output_dir, event)
    print(f"PASS: wrote {len(overlay)} verified activation projection files; applied={bool(args.apply_to)}")


if __name__ == "__main__":
    main()
