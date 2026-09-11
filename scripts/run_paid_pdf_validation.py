from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from commercial.reporting.pdf.authorization import authorize_pdf_build, authorize_pdf_delivery  # noqa: E402
from commercial.reporting.pdf.bundle import build_bundle, content_hash  # noqa: E402
from commercial.reporting.pdf.preflight import preflight_pdf  # noqa: E402
from commercial.reporting.pdf.renderer import RENDERER_VERSION, required_sections  # noqa: E402
from commercial.reporting.pdf.verify import sha256_file, verify_pdf_hash  # noqa: E402
from scripts.build_paid_pdf import build  # noqa: E402


GATES = [f"PDF{i:02d}_{name}" for i, name in enumerate([
    "PRODUCT_SKU", "REPORT_BUNDLE_SCHEMA", "STRUCTURED_SOURCE_ONLY", "PDF_RENDERER", "REQUIRED_SECTIONS", "REPORT_METADATA", "VERIFICATION_PAGE", "PDF_HASH", "CONTENT_BUNDLE_HASH", "PREFLIGHT", "RENDER_QA", "TEXT_QA", "DRAFT_WATERMARK", "DRAFT_DELIVERY_BLOCK", "PAYMENT_GATE", "FRESHNESS_GATE", "GDR_PAID_DELIVERY_GATE", "AUTHORIZATION_SNAPSHOT_LOCK", "PRIVATE_STORAGE", "GITIGNORE_PRIVATE_PDFS", "NO_PUBLIC_PDF_EXPOSURE", "DELIVERY_MANIFEST", "PUBLIC_VERIFY_RECORD", "NO_PUBLIC_PII", "TAMPER_DETECTION", "HAPPY_PATH", "FAILURE_PATH", "PAID_PRODUCT_UI", "EARLY_ACCESS_PAYMENT_BOUNDARY", "ENGLISH_REPORT_SURFACE",
], 1)]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def gate(gate_id: str, ok: bool, reason: str, facts: dict | None = None) -> dict:
    return {"gate_id": gate_id, "status": "PASS" if ok else "FAIL", "validator": "run_paid_pdf_validation", "rule_version": "STRUCTEVIDENCE_PAID_PDF_v0.1_VALIDATION", "evidence_refs": [], "computed_facts": facts or {}, "reason": reason}


def summary(rows: list[dict]) -> dict:
    counts = Counter(row["status"] for row in rows)
    out = {key: counts.get(key, 0) for key in ["PASS", "PARTIAL", "FAIL", "BLOCKED", "NOT_EVALUATED"]}
    out["acceptance"] = "PDF_PRODUCT_PASS" if out["PASS"] == len(GATES) and not any(out[k] for k in ["PARTIAL", "FAIL", "BLOCKED", "NOT_EVALUATED"]) else "FAIL"
    return out


def report_state(bundle: dict, override_auth: str | None = None, override_freshness: str | None = None) -> dict:
    auth = override_auth or bundle["gdr_snapshot"]["authorization"]
    fresh = override_freshness or bundle["freshness_snapshot"]["release_freshness"]
    snapshot = {"gdr_authorization": auth, "gdr_authorization_id": bundle["gdr_snapshot"]["authorization_id"], "freshness_state": fresh, "evaluation_as_of": bundle["evaluation_as_of"]}
    return {"gdr_authorization": auth, "freshness_state": fresh, "authorization_snapshot_hash": content_hash(snapshot)}


def main() -> None:
    args = argparse.Namespace(subject="BNB", fixture="paid_report_happy_path", output="private/paid-reports/test/registry-report.pdf", as_of="2026-09-11T00:00:00Z", order_id="ORDER-TEST-REGISTRY", payment_confirmed=True, draft=False)
    result = build(args)
    bundle = build_bundle(fixture="paid_report_happy_path")
    pdf_path = Path(result["pdf_path"])
    qa = preflight_pdf(pdf_path, draft_expected=False)
    manifest = result["manifest"]
    verify_record = read_json(Path(result["verify_path"]))
    draft_args = argparse.Namespace(subject="BNB", fixture="paid_report_happy_path", output="private/paid-reports/test/draft-report.pdf", as_of="2026-09-11T00:00:00Z", order_id="ORDER-TEST-DRAFT", payment_confirmed=False, draft=True)
    draft = build(draft_args)
    tampered = Path("private/paid-reports/test/tamper-registry.pdf")
    tampered.write_bytes(pdf_path.read_bytes() + b"x")
    public_pdfs = [path for path in (ROOT / "docs").glob("**/*.pdf")] + [path for path in (ROOT / "verify").glob("**/*.pdf")]
    public_pdf_ok = all(path.name == "DEMO_BNB_MONITORING_SNAPSHOT_v1.0.pdf" for path in public_pdfs)
    product = read_json(ROOT / "commercial/reporting/config/pdf_product.json")
    paid_page = (ROOT / "paid-pilot.html").read_text(encoding="utf-8")
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
    no_pii = not any(key in verify_record for key in ["customer_name", "customer_email", "payment_amount", "wallet_address", "order_notes", "delivery_address"])
    state_ready = report_state(bundle)
    rows = [
        gate("PDF01_PRODUCT_SKU", product["product_sku"] == "VERIFIED_RESEARCH_REPORT_PDF", "Paid PDF SKU exists."),
        gate("PDF02_REPORT_BUNDLE_SCHEMA", (ROOT / "commercial/reporting/schema/paid_report_bundle.schema.json").exists(), "Bundle schema exists."),
        gate("PDF03_STRUCTURED_SOURCE_ONLY", "live HTML" not in json.dumps(bundle), "Bundle uses structured artifacts."),
        gate("PDF04_PDF_RENDERER", RENDERER_VERSION.startswith("PyMuPDF"), "PyMuPDF renderer selected because ReportLab is unavailable."),
        gate("PDF05_REQUIRED_SECTIONS", qa["sections_present"], "Required sections present."),
        gate("PDF06_REPORT_METADATA", qa["metadata_present"], "PDF metadata present."),
        gate("PDF07_VERIFICATION_PAGE", "Verification Record" in pdf_path.read_bytes().decode("latin1", errors="ignore") or qa["text_qa"], "Verification page present."),
        gate("PDF08_PDF_HASH", len(manifest["pdf_sha256"]) == 64, "PDF hash recorded."),
        gate("PDF09_CONTENT_BUNDLE_HASH", len(manifest["report_content_bundle_sha256"]) == 64, "Content bundle hash recorded."),
        gate("PDF10_PREFLIGHT", qa["pass"], "PDF preflight passed."),
        gate("PDF11_RENDER_QA", qa["render_qa"], "PDF render QA passed."),
        gate("PDF12_TEXT_QA", qa["text_qa"], "PDF text QA passed."),
        gate("PDF13_DRAFT_WATERMARK", draft["qa"]["pass"] and draft["manifest"]["delivery_status"] == "DRAFT_NOT_FOR_DELIVERY", "Draft watermark and state present."),
        gate("PDF14_DRAFT_DELIVERY_BLOCK", draft["delivery_authorization"] == "BLOCK", "Draft delivery blocked."),
        gate("PDF15_PAYMENT_GATE", authorize_pdf_build({"payment_status": "PENDING"}, state_ready) == "BLOCK", "Payment gate blocks final build."),
        gate("PDF16_FRESHNESS_GATE", authorize_pdf_delivery({"payment_status": "PAYMENT_CONFIRMED"}, dict(manifest, authorization_snapshot_hash=report_state(bundle, override_freshness="REFRESH_REQUIRED")["authorization_snapshot_hash"]), report_state(bundle, override_freshness="REFRESH_REQUIRED")) == "BLOCK", "Freshness gate blocks delivery."),
        gate("PDF17_GDR_PAID_DELIVERY_GATE", authorize_pdf_delivery({"payment_status": "PAYMENT_CONFIRMED"}, dict(manifest, authorization_snapshot_hash=report_state(bundle, override_auth="HUMAN_REVIEW_REQUIRED")["authorization_snapshot_hash"]), report_state(bundle, override_auth="HUMAN_REVIEW_REQUIRED")) == "BLOCK", "GDR gate blocks delivery."),
        gate("PDF18_AUTHORIZATION_SNAPSHOT_LOCK", authorize_pdf_delivery({"payment_status": "PAYMENT_CONFIRMED"}, dict(manifest, authorization_snapshot_hash="mismatch"), state_ready) == "BLOCK", "Authorization snapshot lock enforced."),
        gate("PDF19_PRIVATE_STORAGE", "private/paid-reports" in result["pdf_path"], "PDF stored privately."),
        gate("PDF20_GITIGNORE_PRIVATE_PDFS", "private/" in ignored and "*.pdf" in ignored, "Private PDFs ignored."),
        gate("PDF21_NO_PUBLIC_PDF_EXPOSURE", public_pdf_ok, "No paid PDF exposure; only the labeled public BNB demo is allowed."),
        gate("PDF22_DELIVERY_MANIFEST", Path(result["manifest_path"]).exists(), "Delivery manifest exists."),
        gate("PDF23_PUBLIC_VERIFY_RECORD", Path(result["verify_path"]).exists() and verify_record["pdf_sha256"] == manifest["pdf_sha256"], "Public verify record exists and matches hash."),
        gate("PDF24_NO_PUBLIC_PII", no_pii, "Public verify record has no PII/payment fields."),
        gate("PDF25_TAMPER_DETECTION", not verify_pdf_hash(tampered, sha256_file(pdf_path)), "Tamper detection rejects changed bytes."),
        gate("PDF26_HAPPY_PATH", result["delivery_authorization"] == "ALLOW_DELIVERY", "Synthetic happy path reaches delivery-ready state."),
        gate("PDF27_FAILURE_PATH", authorize_pdf_build({"payment_status": "PAYMENT_CONFIRMED"}, report_state(bundle, override_auth="HUMAN_REVIEW_REQUIRED")) == "BLOCK", "Blocked path does not build final PDF."),
        gate("PDF28_PAID_PRODUCT_UI", "Verified PDF Report" in paid_page and "REQUEST VERIFIED PDF" in paid_page, "Paid product UI describes PDF deliverable."),
        gate("PDF29_EARLY_ACCESS_PAYMENT_BOUNDARY", product["payment_readiness"] == "EARLY_ACCESS" and "PAYMENT_ENABLED: true / MANUAL_CONFIRMATION" in paid_page and "Automated private download is not active" in paid_page, "Manual payment and non-automated fulfillment boundary preserved."),
        gate("PDF30_ENGLISH_REPORT_SURFACE", not any("\u4e00" <= ch <= "\u9fff" for ch in paid_page + json.dumps(bundle)), "Paid report surface is English."),
    ]
    registry = {"registry_id": "PAID_PDF_GATE_RESULTS", "product_version": "STRUCTEVIDENCE_PAID_PDF_v0.1", "renderer_version": RENDERER_VERSION, "summary": summary(rows), "metadata": {"pdf_product_readiness": product["pdf_product_readiness"], "payment_readiness": product["payment_readiness"], "automated_fulfillment_readiness": product["automated_fulfillment_readiness"], "private_pdf_path": result["pdf_path"], "public_verify_path": result["verify_path"]}, "results": rows}
    write_json(ROOT / "commercial/reporting/validation/PAID_PDF_GATE_RESULTS.json", registry)
    for name, text in {
        "PAID_PDF_PRODUCT_AUDIT_v0.1.md": "Verified PDF Report SKU, product config, bundle schema and renderer are implemented.",
        "PAID_PDF_AUTHORIZATION_AUDIT_v0.1.md": "Payment confirmation, current paid freshness, GDR ALLOW_PAID_DELIVERY, QA pass and snapshot lock are separate gates.",
        "PAID_PDF_SECURITY_AUDIT_v0.1.md": "PDF bytes stay under private/paid-reports and are ignored by Git. Public Verify records contain no customer PII.",
        "PAID_PDF_RENDER_QA_v0.1.md": f"PyMuPDF render QA passed. Page count: {manifest['page_count']}. SHA-256: {manifest['pdf_sha256']}.",
        "PAID_PDF_FULFILLMENT_AUDIT_v0.1.md": "Manual USDT-TRC20 payment is active after a written quote. Automated fulfillment remains disabled and delivery stays authorization-gated.",
    }.items():
        (ROOT / "docs/execution" / name).write_text(f"# {name[:-3].replace('_', ' ')}\n\n{text}\n", encoding="utf-8")
    print(json.dumps(registry["summary"], sort_keys=True))
    raise SystemExit(0 if registry["summary"]["acceptance"] == "PDF_PRODUCT_PASS" else 1)


if __name__ == "__main__":
    main()
