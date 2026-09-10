from __future__ import annotations


def fulfillment_ready(payment_status: str, research_authorization: str) -> bool:
    return payment_status == "CONFIRMED" and research_authorization == "ALLOW_PAID_DELIVERY"


def evaluate_paid_delivery_authorization(publication_authorization: str, freshness_resolved: bool, report_current: bool, seller_config_valid: bool, product_configured: bool, secure_fulfillment_available: bool) -> str:
    if (
        publication_authorization in {"ALLOW_PUBLICATION", "ALLOW_WITH_LIMITATIONS"}
        and freshness_resolved
        and report_current
        and seller_config_valid
        and product_configured
        and secure_fulfillment_available
    ):
        return "ALLOW_PAID_DELIVERY"
    return "BLOCKED"


def evaluate_publication_authorization(runtime_authorization: str) -> str:
    return runtime_authorization
