from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gdr-se" / "engine"))
sys.path.insert(0, str(ROOT / "commercial" / "intelligence"))

from aggregation import aggregate  # noqa: E402
from gdr_se_runtime import fulfillment_ready  # noqa: E402

VERSION = "GDR_SE_v0.1"
SUBJECTS = {
    "strategy": ROOT / "research" / "gdr-se" / "strategy-2026",
    "bnb": ROOT / "research" / "digital-assets" / "batch-01-r1" / "BNB" / "gdr-se",
    "sol": ROOT / "research" / "digital-assets" / "batch-01-r1" / "SOL" / "gdr-se",
    "trx": ROOT / "research" / "digital-assets" / "batch-01-r1" / "TRX" / "gdr-se",
    "xlm": ROOT / "research" / "digital-assets" / "batch-01-r1" / "XLM" / "gdr-se",
}
EXPECTED_RESEARCH_HASHES = {
    "research/Strategy_2026_Public_Evidence_Research_Report_v0.1_EN.md": "416af04d120a0ee87046dee426ae0404c0fb3ca47cbe7f83e4d986ced3179e68",
    "research/Strategy_2026_Structural_Dynamics_Report_v0.1_EN.md": "e84a97409e69bcfcfa901d1f5281ec88802ae0e44eb91af6eaca14906a63edf9",
    "research/PUBLICATION_PACKAGE_MANIFEST_EN.json": "1769ec5adebc32ff3e3ecfd9cc1ea527ef30e025b7e559539266c331c147669a",
}
FORBIDDEN_GDR_SE_TERMS = [
    "AUTHORIZE_PROBE",
    "AUTHORIZE_NORMAL",
    "MANAGE_ONLY",
    "ENTRY",
    "STOP_LOSS",
    "TAKE_PROFIT",
    "POSITION_SIZE",
]
FORBIDDEN_SCORE_TERMS = ["GDR score", "health score", "decision score", "A/B/C rating", "stars"]


def fail(message: str) -> None:
    raise SystemExit(f"GDR_SE_TEST_FAIL: {message}")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def check_records() -> None:
    ids = set()
    for subject, path in SUBJECTS.items():
        record = read_json(path / "GDR_SE_AUTHORIZATION_RECORD_R1_1.json")
        overlay = read_json(path / "GDR_SE_OVERLAY_R1_1.json")
        if record["gdr_se_version"] != VERSION or overlay["gdr_se_version"] != VERSION:
            fail(f"wrong version for {subject}")
        if record["evaluation_mode"] != "RUNTIME_EVALUATED":
            fail(f"missing runtime evaluation mode for {subject}")
        if record.get("runtime_revision") != "R1.1" or overlay.get("runtime_revision") != "R1.1":
            fail(f"missing R1.1 runtime revision for {subject}")
        if record["authorization_id"] in ids:
            fail("duplicate authorization id")
        ids.add(record["authorization_id"])
        if record["authorization"] not in {"ALLOW_PUBLICATION", "ALLOW_WITH_LIMITATIONS", "REFRESH_REQUIRED", "HUMAN_REVIEW_REQUIRED", "ABSTAIN", "VETO"}:
            fail(f"invalid authorization for {subject}")
        if len(record["gate_results"]) != 10:
            fail(f"missing ten gates for {subject}")
        if not record["counterfactual"].get("falsifiers") or not record["counterfactual"].get("discriminating_evidence"):
            fail(f"missing counterfactual for {subject}")
        if overlay["authorization"] != record["authorization"]:
            fail(f"overlay mismatch for {subject}")
        lowered_record = json.dumps(record).lower()
        for forbidden in ["0-100 score", "health score", "decision score", "a/b/c rating", "stars"]:
            if forbidden in lowered_record:
                fail(f"forbidden scoring language in record {subject}: {forbidden}")
        history = ROOT / "gdr-se" / "records" / record["research_id"].replace("/", "_").replace(":", "_") / "authorization_history.jsonl"
        lines = history.read_text(encoding="utf-8").splitlines()
        if not any(json.loads(line)["authorization_id"] == record["authorization_id"] for line in lines):
            fail(f"append-only history missing {subject}")


def check_no_upgrade_and_abstention() -> None:
    veto = aggregate([{"status": "FAIL", "severity": "HARD", "gate_id": "G1_SCHEMA_INTEGRITY", "reason": "", "computed_facts": {}}])
    if veto != "VETO":
        fail("hard fail must veto")
    gate_ids = [
        "G1_SCHEMA_INTEGRITY",
        "G2_RTP_PROVENANCE",
        "G3_EVIDENCE_FRESHNESS",
        "G4_SOURCE_DEPENDENCY",
        "G5_NUMERICAL_RECONCILIATION",
        "G6_ECL_CONSISTENCY",
        "G7_COUNTER_EVIDENCE_COMPLETENESS",
        "G8_INDEPENDENT_REVIEW",
        "G9_SENSITIVITY_RIGHT_OF_REPLY",
        "G10_EXPIRY_SUPERSESSION",
    ]
    abstain_gates = [{"gate_id": gate_id, "status": "PASS", "severity": "SOFT", "reason": "fixture", "computed_facts": {}} for gate_id in gate_ids]
    for row in abstain_gates:
        if row["gate_id"] == "G6_ECL_CONSISTENCY":
            row["status"] = "INSUFFICIENT_DATA"
    if aggregate(abstain_gates) != "ABSTAIN":
        fail("insufficient data must abstain")
    sol = read_json(SUBJECTS["sol"] / "GDR_SE_AUTHORIZATION_RECORD_R1_1.json")
    if sol["evidence_state_reference"] != "POTENTIAL_CONFLICT":
        fail("SOL evidence state fixture changed")
    if sol["authorization"] == "VETO":
        fail("SOL potential conflict was treated as material inconsistency veto")
    if "Potential conflict is not material inconsistency" not in json.dumps(sol):
        fail("SOL sensitivity explanation missing")


def check_public_surface() -> None:
    for rel in ["gdr.html", "docs/gdr.html", "architecture.html", "standard.html", "method.html", "verify.html"]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        for term in FORBIDDEN_GDR_SE_TERMS + FORBIDDEN_SCORE_TERMS:
            if term in text:
                fail(f"forbidden term {term} in {rel}")
        if any(ord(char) > 127 and "\u4e00" <= char <= "\u9fff" for char in text):
            fail(f"non-English public surface in {rel}")
    for rel in ["gdr.html", "architecture.html", "standard.html", "method.html", "verify.html", "whitepapers.html", "reports.html", "paid-pilot.html"]:
        if (ROOT / rel).read_text(encoding="utf-8") != (ROOT / "docs" / rel).read_text(encoding="utf-8"):
            fail(f"root/docs sync failed for {rel}")


def check_commercial_and_monitor() -> None:
    paid_schema = read_json(ROOT / "commercial" / "schema" / "paid_delivery_authorization.schema.json")
    monitor_schema = read_json(ROOT / "gdr-se" / "schema" / "monitor_authorization.schema.json")
    if paid_schema["properties"]["authorization"]["const"] != "ALLOW_PAID_DELIVERY":
        fail("paid delivery schema must require ALLOW_PAID_DELIVERY")
    if "VETO" not in monitor_schema["properties"]["authorization"]["enum"]:
        fail("monitor schema must include veto")
    if fulfillment_ready("CONFIRMED", "ALLOW_PUBLICATION"):
        fail("publication authorization must not trigger paid fulfillment")
    if fulfillment_ready("PENDING", "ALLOW_PAID_DELIVERY"):
        fail("pending payment must not trigger paid fulfillment")
    if not fulfillment_ready("CONFIRMED", "ALLOW_PAID_DELIVERY"):
        fail("confirmed payment plus paid authorization should trigger fulfillment readiness")


def check_hashes_and_terms() -> None:
    for rel, expected in EXPECTED_RESEARCH_HASHES.items():
        if sha(rel) != expected:
            fail(f"frozen research hash changed: {rel}")
    text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in (ROOT / "gdr-se").rglob("*") if path.is_file())
    for term in FORBIDDEN_GDR_SE_TERMS + ["BUY", "SELL"]:
        if term in text:
            fail(f"trading semantic leaked into gdr-se: {term}")
    if "86/100" in text:
        fail("numeric score leaked into gdr-se")


def main() -> None:
    check_records()
    check_no_upgrade_and_abstention()
    check_public_surface()
    check_commercial_and_monitor()
    check_hashes_and_terms()
    print("GDR_SE_TESTS_PASS")


if __name__ == "__main__":
    main()
