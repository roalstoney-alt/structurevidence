from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise SystemExit(f"PAID_PDF_SECURITY_TEST_FAIL: {message}")


def main() -> None:
    tracked_like = [path for base in ["docs", "verify", "."] for path in (ROOT / base).glob("**/*.pdf") if "private" not in path.parts]
    if tracked_like:
        fail(f"public PDF exposure found: {tracked_like}")
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
    if "private/" not in ignored or "*.pdf" not in ignored:
        fail("private PDF storage is not ignored")
    for path in (ROOT / "verify" / "reports").glob("*.json"):
        record = json.loads(path.read_text(encoding="utf-8"))
        if any(key in record for key in ["customer_name", "customer_email", "payment_amount", "wallet_address", "order_notes", "delivery_address"]):
            fail(f"public verify PII field found in {path}")
    print("PAID_PDF_SECURITY_TESTS_PASS")


if __name__ == "__main__":
    main()
