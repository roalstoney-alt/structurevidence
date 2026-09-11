from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from commercial.reporting.pdf.authorization import authorize_pdf_build, authorize_pdf_delivery  # noqa: E402
from commercial.reporting.pdf.bundle import build_bundle, content_hash  # noqa: E402
from commercial.reporting.pdf.manifest import write_delivery_manifest, write_json, write_public_verify_record  # noqa: E402
from commercial.reporting.pdf.preflight import preflight_pdf  # noqa: E402
from commercial.reporting.pdf.renderer import RENDERER_VERSION, render_pdf, required_sections  # noqa: E402


def report_state(bundle: dict) -> dict:
    auth_snapshot = {"gdr_authorization": bundle["gdr_snapshot"]["authorization"], "gdr_authorization_id": bundle["gdr_snapshot"]["authorization_id"], "freshness_state": bundle["freshness_snapshot"]["release_freshness"], "evaluation_as_of": bundle["evaluation_as_of"]}
    return {"freshness_state": bundle["freshness_snapshot"]["release_freshness"], "gdr_authorization": bundle["gdr_snapshot"]["authorization"], "authorization_snapshot_hash": content_hash(auth_snapshot)}


def write_product_manifest() -> None:
    schema_hash = content_hash(json.loads((ROOT / "commercial/reporting/schema/paid_report_bundle.schema.json").read_text(encoding="utf-8")))
    config_hash = content_hash(json.loads((ROOT / "commercial/reporting/config/pdf_product.json").read_text(encoding="utf-8")))
    write_json(ROOT / "commercial/reporting/PDF_PRODUCT_MANIFEST.json", {"product_version": "STRUCTEVIDENCE_PAID_PDF_v0.1", "renderer_version": RENDERER_VERSION, "schema_hash": schema_hash, "config_hash": config_hash, "required_sections": required_sections(), "private_storage_required": True, "delivery_gate_version": "PAID_PDF_DELIVERY_GATE_v0.1"})


def build(args) -> dict:
    write_product_manifest()
    bundle = build_bundle(args.subject, args.as_of, args.fixture)
    order = {"order_id": args.order_id, "payment_status": "PAYMENT_CONFIRMED" if args.payment_confirmed else "PENDING", "draft_requested": args.draft}
    build_auth = authorize_pdf_build(order, report_state(bundle))
    if build_auth == "BLOCK":
        return {"status": "PDF_BUILD_BLOCKED", "build_authorization": build_auth, "report_state": report_state(bundle)}
    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT / output
    render_pdf(bundle, output, draft=args.draft)
    qa = preflight_pdf(output, draft_expected=args.draft)
    delivery_status = "DRAFT_NOT_FOR_DELIVERY" if args.draft else "FULFILLMENT_READY"
    manifest = write_delivery_manifest(output, bundle, qa, order, delivery_status)
    delivery_auth = authorize_pdf_delivery(order, manifest, report_state(bundle))
    verify = write_public_verify_record(bundle, manifest)
    result = {"status": "PDF_BUILD_PASS" if qa.get("pass") else "PDF_QA_FAIL", "build_authorization": build_auth, "delivery_authorization": delivery_auth, "pdf_path": str(output), "manifest_path": str(output.parent / "PAID_PDF_DELIVERY_MANIFEST.json"), "verify_path": str(ROOT / "verify" / "reports" / f"{bundle['artifact_id']}.json"), "qa": qa, "manifest": manifest, "verify": verify}
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", default="BNB")
    parser.add_argument("--fixture", default=None)
    parser.add_argument("--output", default="private/paid-reports/test/report.pdf")
    parser.add_argument("--as-of", default="2026-09-11T00:00:00Z")
    parser.add_argument("--order-id", default="ORDER-TEST-PAID-PDF")
    parser.add_argument("--payment-confirmed", action="store_true")
    parser.add_argument("--draft", action="store_true")
    args = parser.parse_args()
    result = build(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["status"] in {"PDF_BUILD_PASS", "PDF_BUILD_BLOCKED"} else 1)


if __name__ == "__main__":
    main()
