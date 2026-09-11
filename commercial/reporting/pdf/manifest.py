from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import fitz

from .bundle import content_hash
from .verify import sha256_file


ROOT = Path(__file__).resolve().parents[3]


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_delivery_manifest(pdf_path: Path, bundle: dict, qa: dict, order: dict, delivery_status: str, delivery_method: str = "MANUAL_EMAIL_ATTACHMENT") -> dict:
    doc = fitz.open(pdf_path)
    page_count = doc.page_count
    doc.close()
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    auth_snapshot = {"gdr_authorization": bundle["gdr_snapshot"]["authorization"], "gdr_authorization_id": bundle["gdr_snapshot"]["authorization_id"], "freshness_state": bundle["freshness_snapshot"]["release_freshness"], "evaluation_as_of": bundle["evaluation_as_of"]}
    manifest = {
        "order_id": order["order_id"],
        "report_id": bundle["report_id"],
        "artifact_id": bundle["artifact_id"],
        "pdf_sha256": sha256_file(pdf_path),
        "report_content_bundle_sha256": bundle["report_content_bundle_sha256"],
        "authorization_snapshot_hash": content_hash(auth_snapshot),
        "page_count": page_count,
        "file_size": pdf_path.stat().st_size,
        "generated_at": generated_at,
        "evaluation_as_of": bundle["evaluation_as_of"],
        "gdr_authorization_id": bundle["gdr_snapshot"]["authorization_id"],
        "freshness_record_path": bundle["verification"].get("verify_path", "").replace("verify/reports", "research/freshness"),
        "delivery_status": delivery_status,
        "delivery_method": delivery_method,
        "delivered_at": generated_at if delivery_status == "DELIVERED" else None,
        "qa_pass": bool(qa.get("pass")),
    }
    path = pdf_path.parent / "PAID_PDF_DELIVERY_MANIFEST.json"
    write_json(path, manifest)
    try:
        os.chmod(pdf_path, 0o600)
        os.chmod(path, 0o600)
    except OSError:
        pass
    return manifest


def public_verify_record(bundle: dict, manifest: dict) -> dict:
    return {
        "artifact_id": bundle["artifact_id"],
        "report_id": bundle["report_id"],
        "research_id": bundle["research_id"],
        "report_version": bundle["report_version"],
        "pdf_sha256": manifest["pdf_sha256"],
        "generated_at": manifest["generated_at"],
        "evaluation_as_of": bundle["evaluation_as_of"],
        "freshness_policy_version": bundle["freshness_snapshot"]["policy_version"],
        "gdr_authorization_id": bundle["gdr_snapshot"]["authorization_id"],
        "correction_status": bundle["verification"].get("correction_status"),
        "supersession_status": bundle["verification"].get("supersession_status"),
    }


def write_public_verify_record(bundle: dict, manifest: dict) -> dict:
    record = public_verify_record(bundle, manifest)
    for base in [ROOT / "verify" / "reports", ROOT / "docs" / "verify" / "reports"]:
        write_json(base / f"{bundle['artifact_id']}.json", record)
    return record
