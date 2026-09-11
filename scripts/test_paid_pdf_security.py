from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise SystemExit(f"PAID_PDF_SECURITY_TEST_FAIL: {message}")


def main() -> None:
    tracked_like = [path for base in ["docs", "verify", "."] for path in (ROOT / base).glob("**/*.pdf") if "private" not in path.parts]
    allowed_demo_names = {"DEMO_BNB_MONITORING_SNAPSHOT_v1.0.pdf"}
    unexpected = [path for path in tracked_like if path.name not in allowed_demo_names]
    if unexpected:
        fail(f"public paid or unlabeled PDF exposure found: {unexpected}")
    for path in tracked_like:
        data = path.read_bytes()
        if b"DEMO_MONITORING_SNAPSHOT" not in data and b"NOT A LIVE PAID REPORT" not in data:
            # Compressed streams may hide labels, so the public verification record is authoritative.
            record_path = ROOT / "verify/reports/DEMO_BNB_MONITORING_SNAPSHOT_v1.0.json"
            record = json.loads(record_path.read_text(encoding="utf-8")) if record_path.is_file() else {}
            if record.get("commercial_delivery") is not False or record.get("label") != "NOT A LIVE PAID REPORT":
                fail(f"public demo boundary is missing for {path}")
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
