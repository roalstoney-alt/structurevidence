from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_paid_pdf import build  # noqa: E402


def fail(message: str) -> None:
    raise SystemExit(f"PAID_PDF_TEST_FAIL: {message}")


def main() -> None:
    args = argparse.Namespace(subject="BNB", fixture="paid_report_happy_path", output="private/paid-reports/test/report.pdf", as_of="2026-09-11T00:00:00Z", order_id="ORDER-TEST-PAID-PDF", payment_confirmed=True, draft=False)
    result = build(args)
    if result["status"] != "PDF_BUILD_PASS" or not result["qa"]["pass"]:
        fail("happy path PDF did not pass QA")
    verify = json.loads(Path(result["verify_path"]).read_text(encoding="utf-8"))
    if verify["pdf_sha256"] != result["manifest"]["pdf_sha256"]:
        fail("public verify hash does not match manifest")
    if any(key in verify for key in ["customer_name", "customer_email", "payment_amount", "wallet_address", "order_notes"]):
        fail("public verify record contains prohibited PII/payment fields")
    print("PAID_PDF_TESTS_PASS")


if __name__ == "__main__":
    main()
