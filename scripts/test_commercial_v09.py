from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


EXPECTED_STRATEGY_HASHES = {
    "docs/research/Strategy_2026_Public_Evidence_Research_Report_v0.1_CN.md": "81f9c8810b7cabd86426f6fc115f62ee20cc953494259a878c7a4a1f5c044fc0",
    "docs/research/Strategy_2026_Structural_Dynamics_Report_v0.1_CN.md": "75dfb5cd4eab564bf4c3989662ede851ceac16a6ed34c85587366760566697f7",
    "docs/research/Structural_Dynamics_Evidence_Dynamics_Method_Paper_v0.1_CN.md": "fe7c8f696cf14c3f5b3b470bc21d116c304b78d7bf60f949f043bfd335b4da8b",
    "docs/research/PUBLICATION_PACKAGE_MANIFEST.json": "272036c9da4075b44241cbb9473798d7b9ce5cb098b81bdbd98d6acdc26a4554",
}

REQUIRED_PAGES = [
    "index.html",
    "reports.html",
    "sample-report.html",
    "enterprise.html",
    "customize.html",
    "terms.html",
    "privacy.html",
    "terms-of-sale.html",
    "refund-policy.html",
    "research-scope.html",
]

FORBIDDEN_TRADING_COPY = [
    "buy signal",
    "sell signal",
    "price target",
    "position size",
    "investment recommendation",
    "universal score",
    "ranking table",
]


def fail(message: str) -> None:
    raise SystemExit(f"COMMERCIAL_V09_TEST_FAIL: {message}")


def read_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def check_pages() -> None:
    for rel in REQUIRED_PAGES:
        root_page = ROOT / rel
        docs_page = ROOT / "docs" / rel
        if not root_page.exists():
            fail(f"missing root page {rel}")
        if not docs_page.exists():
            fail(f"missing docs mirror {rel}")
        if root_page.read_text(encoding="utf-8") != docs_page.read_text(encoding="utf-8"):
            fail(f"root/docs page mismatch {rel}")
    homepage = (ROOT / "index.html").read_text(encoding="utf-8")
    required = [
        "Monitor structural change.",
        'action="monitor.html"',
        "BNB structural and evidence state",
        "Executive insight",
        "How the observed structure changed",
        "Export PDF",
        "reports.html",
        "Monitoring is not prediction",
    ]
    for phrase in required:
        if phrase not in homepage:
            fail(f"homepage missing {phrase}")
    for forbidden in ["coverage-index", "REFINEMENT_TABLE.html", "verify-r1.html", "SOL is featured as the conflict demonstration case"]:
        if forbidden in homepage:
            fail(f"homepage still exposes research-dashboard copy/link {forbidden}")
    if "PAYMENT_ENABLED: true" in homepage:
        fail("homepage implies enabled payment")


def check_entities_free_scan() -> None:
    entities = read_json("assets/entities.json")
    covered = [entity for entity in entities if entity.get("covered")]
    if {entity["ticker"] for entity in covered} != {"MSTR", "BNB", "SOL", "TRX", "XLM"}:
        fail("covered entities are not exactly MSTR, BNB, SOL, TRX, XLM")
    for entity in covered:
        scan = entity.get("free_scan") or {}
        if len(scan.get("key_observations") or []) != 3:
            fail(f"free scan needs exactly 3 observations for {entity['ticker']}")
        for field in ["key_limitation", "open_question", "observation_window", "report_version"]:
            if not scan.get(field):
                fail(f"free scan missing {field} for {entity['ticker']}")
        if scan.get("market_context") is not None:
            context = scan["market_context"]
            if not context.get("as_of") or not context.get("source_boundary"):
                fail(f"market context missing timestamp/source boundary for {entity['ticker']}")


def check_configs_and_schemas() -> None:
    commercial = read_json("commercial/config/commercial.json")
    products = read_json("commercial/config/products.json")
    contact = read_json("commercial/config/contact.json")
    if commercial["commercial_status"] != "EARLY_ACCESS" or commercial["payment_enabled"] is not False:
        fail("commercial status/payment gate incorrect")
    allowed_launch_gates = {
        "BLOCKED",
        "SINGAPORE_PAID_PILOT_READY_CONFIGURATION_PENDING",
    }
    if commercial["commercial_launch_gate"] not in allowed_launch_gates:
        fail("missing blocked launch gate")
    if products["verified_report"]["price"] is not None or products["verified_report"]["price_status"] != "CONFIG_REQUIRED":
        fail("verified report price must remain unconfigured")
    if products["custom_audit"]["price_status"] != "SCOPE_REQUIRED":
        fail("custom audit must require scope")
    allowed_contact_statuses = {
        "CONFIG_REQUIRED",
        "SINGAPORE_ENTITY_SELECTED_LEGAL_NAME_AND_CONTACT_REQUIRED",
    }
    if contact["contact_status"] not in allowed_contact_statuses:
        fail("contact config must remain explicit config-required")
    if not all(contact.get(field) is None for field in ["company_name", "legal_email", "sales_email", "support_email"]):
        fail("contact config must not invent seller identity before activation")
    for rel in [
        "commercial/schema/order.schema.json",
        "commercial/schema/evidence_graph.schema.json",
        "commercial/schema/structural_delta.schema.json",
        "commercial/schema/verification_record.schema.json",
        "commercial/VERIFICATION_RECORD.json",
    ]:
        read_json(rel)
    if read_json("commercial/VERIFICATION_RECORD.json")["record_status"] != "TEMPLATE_NO_PAID_REPORT_DELIVERED":
        fail("verification record template must not imply paid delivery")


def check_mos_gdr_boundaries() -> None:
    registry = read_json("commercial/intelligence/ENGINE_REGISTRY.json")
    if registry["GDR"]["commercial_role"] != "RESERVED_NOT_CONNECTED":
        fail("GDR must remain reserved when local spec is absent")
    adapter_path = ROOT / "commercial" / "intelligence" / "mos_adapter.py"
    spec = importlib.util.spec_from_file_location("mos_adapter", adapter_path)
    if spec is None or spec.loader is None:
        fail("cannot import MOS adapter")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    payload = module.build_market_context("SOL", {"regime": "UNAVAILABLE"})
    if "market_context" not in payload or "asset" not in payload:
        fail("MOS adapter payload shape invalid")
    try:
        module.build_market_context("SOL", {"regime": "buy now"})
    except ValueError as exc:
        if str(exc) != "MOS_COMMERCIAL_OUTPUT_CONTAINS_TRADING_INSTRUCTION":
            fail("MOS adapter raised wrong trading gate")
    else:
        fail("MOS adapter allowed trading instruction")
    if not (ROOT / "commercial" / "docs" / "SEARCH_DEMAND_LOGGING.md").exists():
        fail("missing search demand logging design")


def check_paid_boundary_and_copy() -> None:
    public_text = "\n".join((ROOT / rel).read_text(encoding="utf-8") for rel in REQUIRED_PAGES)
    lowered = public_text.lower()
    for forbidden in FORBIDDEN_TRADING_COPY:
        if forbidden in lowered:
            fail(f"forbidden public copy remains: {forbidden}")
    customize = (ROOT / "customize.html").read_text(encoding="utf-8")
    for product in ["Verified Research Report", "Custom Structural Audit", "Enterprise Evidence Review"]:
        if product not in customize:
            fail(f"customize page missing product: {product}")
    for boundary in ["Configuration pending", "Scoped quote", "Custom scope required", "No checkout is active."]:
        if boundary not in customize:
            fail(f"customize page missing commercial boundary: {boundary}")
    for rel in ["reports.html", "sample-report.html", "enterprise.html", "customize.html"]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        if "$" in text:
            fail(f"fake price appears in {rel}")
    for path in (ROOT / "docs").rglob("*"):
        if path.is_file() and path.suffix.lower() == ".pdf" and "sample" not in path.name.lower():
            if path.name != "DEMO_BNB_MONITORING_SNAPSHOT_v1.0.pdf":
                fail(f"paid pdf-like file exposed in public docs: {path}")
            record = read_json("verify/reports/DEMO_BNB_MONITORING_SNAPSHOT_v1.0.json")
            if record.get("commercial_delivery") is not False or record.get("label") != "NOT A LIVE PAID REPORT":
                fail("public monitoring demo lacks noncommercial boundary")


def check_hashes_unchanged() -> None:
    for rel, expected in EXPECTED_STRATEGY_HASHES.items():
        if sha256(rel) != expected:
            fail(f"Strategy hash changed: {rel}")
    changed = []
    for rel in [
        "research/digital-assets/batch-01",
        "evidence-freeze/DIGITAL-ASSET-BATCH-01",
        "evidence-freeze/DIGITAL-ASSET-BATCH-01-R1",
        "docs/evidence-freeze/DIGITAL-ASSET-BATCH-01",
        "docs/evidence-freeze/DIGITAL-ASSET-BATCH-01-R1",
    ]:
        if not (ROOT / rel).exists():
            fail(f"missing research path {rel}")
    if changed:
        fail(f"unexpected research changes: {changed}")


def main() -> None:
    check_pages()
    check_entities_free_scan()
    check_configs_and_schemas()
    check_mos_gdr_boundaries()
    check_paid_boundary_and_copy()
    check_hashes_unchanged()
    print("COMMERCIAL_V09_TESTS_PASS")


if __name__ == "__main__":
    main()
