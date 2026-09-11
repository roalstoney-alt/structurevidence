from __future__ import annotations


ORDER_STATES = [
    "ORDER_CREATED",
    "PRECHECK_RUNNING",
    "REPORT_AVAILABLE",
    "AWAITING_PAYMENT",
    "PAYMENT_CONFIRMED",
    "FINAL_REVIEW_RUNNING",
    "FULFILLMENT_BLOCKED",
    "PDF_BUILDING",
    "PDF_QA",
    "FULFILLMENT_READY",
    "DELIVERED",
    "REFUND_REVIEW",
    "CANCELLED",
]


def paid_report_preflight(freshness_state: str, gdr_authorization: str) -> str:
    if freshness_state == "CURRENT" and gdr_authorization == "ALLOW_PAID_DELIVERY":
        return "REPORT_AVAILABLE"
    if freshness_state in {"REFRESH_REQUIRED", "AGING"}:
        return "REFRESH_REQUIRED"
    if freshness_state in {"EVENT_INVALIDATED", "UNDER_REVIEW", "INSUFFICIENT_DATA", "POLICY_NOT_CONFIGURED"}:
        return "HUMAN_REVIEW_REQUIRED"
    return "NOT_AVAILABLE"


def authorize_pdf_build(order: dict, report_state: dict) -> str:
    if order.get("draft_requested"):
        return "ALLOW_DRAFT_BUILD"
    if order.get("payment_status") == "PAYMENT_CONFIRMED" and report_state.get("freshness_state") == "CURRENT" and report_state.get("gdr_authorization") == "ALLOW_PAID_DELIVERY":
        return "ALLOW_FINAL_BUILD"
    return "BLOCK"


def authorize_pdf_delivery(order: dict, manifest: dict, report_state: dict) -> str:
    if manifest.get("delivery_status") == "DRAFT_NOT_FOR_DELIVERY":
        return "BLOCK"
    if order.get("payment_status") != "PAYMENT_CONFIRMED":
        return "BLOCK"
    if report_state.get("freshness_state") != "CURRENT":
        return "BLOCK"
    if report_state.get("gdr_authorization") != "ALLOW_PAID_DELIVERY":
        return "BLOCK"
    if not manifest.get("qa_pass") or not manifest.get("pdf_sha256"):
        return "BLOCK"
    if manifest.get("authorization_snapshot_hash") != report_state.get("authorization_snapshot_hash"):
        return "BLOCK"
    return "ALLOW_DELIVERY"
