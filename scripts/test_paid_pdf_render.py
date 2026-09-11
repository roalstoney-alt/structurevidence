from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from commercial.reporting.pdf.preflight import preflight_pdf  # noqa: E402
from commercial.reporting.pdf.verify import sha256_file, verify_pdf_hash  # noqa: E402
from scripts.build_paid_pdf import build  # noqa: E402


def fail(message: str) -> None:
    raise SystemExit(f"PAID_PDF_RENDER_TEST_FAIL: {message}")


def main() -> None:
    args = argparse.Namespace(subject="BNB", fixture="paid_report_happy_path", output="private/paid-reports/test/render-report.pdf", as_of="2026-09-11T00:00:00Z", order_id="ORDER-TEST-PAID-PDF-RENDER", payment_confirmed=True, draft=False)
    result = build(args)
    pdf_path = Path(result["pdf_path"])
    qa = preflight_pdf(pdf_path, draft_expected=False)
    if not qa["pass"]:
        fail(f"PDF QA failed: {qa}")
    tampered = pdf_path.with_name("tampered.pdf")
    shutil.copyfile(pdf_path, tampered)
    data = bytearray(tampered.read_bytes())
    data[-20] = (data[-20] + 1) % 255
    tampered.write_bytes(data)
    if verify_pdf_hash(tampered, sha256_file(pdf_path)):
        fail("tamper detection did not reject changed PDF")
    print("PAID_PDF_RENDER_TESTS_PASS")


if __name__ == "__main__":
    main()
