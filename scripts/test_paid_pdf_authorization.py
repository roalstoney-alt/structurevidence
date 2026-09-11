from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from commercial.reporting.pdf.authorization import authorize_pdf_build, authorize_pdf_delivery, paid_report_preflight  # noqa: E402


def fail(message: str) -> None:
    raise SystemExit(f"PAID_PDF_AUTH_TEST_FAIL: {message}")


def main() -> None:
    ready = {"freshness_state": "CURRENT", "gdr_authorization": "ALLOW_PAID_DELIVERY", "authorization_snapshot_hash": "abc"}
    blocked = {"freshness_state": "EVENT_INVALIDATED", "gdr_authorization": "HUMAN_REVIEW_REQUIRED", "authorization_snapshot_hash": "abc"}
    if paid_report_preflight("CURRENT", "ALLOW_PAID_DELIVERY") != "REPORT_AVAILABLE":
        fail("preflight available path failed")
    if paid_report_preflight("EVENT_INVALIDATED", "HUMAN_REVIEW_REQUIRED") != "HUMAN_REVIEW_REQUIRED":
        fail("preflight human review path failed")
    if authorize_pdf_build({"payment_status": "PENDING"}, ready) != "BLOCK":
        fail("final build allowed without payment")
    if authorize_pdf_build({"payment_status": "PAYMENT_CONFIRMED"}, blocked) != "BLOCK":
        fail("final build allowed with stale/ineligible report")
    manifest = {"delivery_status": "DRAFT_NOT_FOR_DELIVERY", "qa_pass": True, "pdf_sha256": "x", "authorization_snapshot_hash": "abc"}
    if authorize_pdf_delivery({"payment_status": "PAYMENT_CONFIRMED"}, manifest, ready) != "BLOCK":
        fail("draft delivery was allowed")
    manifest["delivery_status"] = "FULFILLMENT_READY"
    if authorize_pdf_delivery({"payment_status": "PENDING"}, manifest, ready) != "BLOCK":
        fail("delivery allowed without payment")
    if authorize_pdf_delivery({"payment_status": "PAYMENT_CONFIRMED"}, manifest, blocked) != "BLOCK":
        fail("delivery allowed without paid GDR/freshness")
    if authorize_pdf_delivery({"payment_status": "PAYMENT_CONFIRMED"}, manifest, ready) != "ALLOW_DELIVERY":
        fail("happy path delivery did not pass")
    print("PAID_PDF_AUTH_TESTS_PASS")


if __name__ == "__main__":
    main()
