#!/usr/bin/env python3
import fitz

from monitoring_test_common import ROOT, pass_message, read_json, require, sha256


def main() -> None:
    path = ROOT / "reports/DEMO_BNB_MONITORING_SNAPSHOT_v1.0.pdf"
    require(path.is_file(), "demo snapshot PDF missing")
    with fitz.open(path) as doc:
        require(doc.page_count == 8, "unexpected PDF page count")
        text = "\n".join(page.get_text() for page in doc)
    for required in ["DEMO_MONITORING_SNAPSHOT", "NOT A LIVE PAID REPORT", "NOT_MEASURED", "COMMERCIAL_DELIVERY", "BLOCK", "SNAPSHOT SHA-256"]:
        require(required in text, f"PDF boundary missing: {required}")
    record = read_json("verify/reports/DEMO_BNB_MONITORING_SNAPSHOT_v1.0.json")
    require(record["commercial_delivery"] is False and record["sha256"] == sha256(path), "PDF verification metadata mismatch")
    require((ROOT / "docs/reports" / path.name).read_bytes() == path.read_bytes(), "public PDF copies diverged")
    pass_message("MONITORING_SNAPSHOT_PDF_TESTS")


if __name__ == "__main__": main()
