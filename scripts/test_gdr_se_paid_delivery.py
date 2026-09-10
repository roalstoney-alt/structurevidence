from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "commercial" / "intelligence"))

from gdr_se_runtime import evaluate_paid_delivery_authorization, fulfillment_ready  # noqa: E402


def fail(message: str) -> None:
    raise SystemExit(f"GDR_SE_PAID_DELIVERY_TEST_FAIL: {message}")


def main() -> None:
    cases = [
        ("CONFIRMED", "ALLOW_PAID_DELIVERY", True),
        ("PENDING", "ALLOW_PAID_DELIVERY", False),
        ("CONFIRMED", "ALLOW_PUBLICATION", False),
        ("CONFIRMED", "ALLOW_WITH_LIMITATIONS", False),
        ("CONFIRMED", "HUMAN_REVIEW_REQUIRED", False),
        ("CONFIRMED", "REFRESH_REQUIRED", False),
        ("CONFIRMED", "ABSTAIN", False),
        ("CONFIRMED", "VETO", False),
    ]
    for payment, auth, expected in cases:
        if fulfillment_ready(payment, auth) is not expected:
            fail(f"fulfillment_ready failed for {payment}+{auth}")
    if evaluate_paid_delivery_authorization("ALLOW_PUBLICATION", False, True, True, True, True) != "BLOCKED":
        fail("unresolved freshness allowed paid delivery")
    if evaluate_paid_delivery_authorization("ALLOW_PUBLICATION", True, True, True, True, True) != "ALLOW_PAID_DELIVERY":
        fail("complete paid-delivery authorization did not pass")
    print("GDR_SE_PAID_DELIVERY_TESTS_PASS")


if __name__ == "__main__":
    main()
