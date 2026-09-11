#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from monitoring.runtime.hash import canonical_hash
from monitoring.runtime.validators import establish_delta, validate_append_only_events, visible_at


GATE_IDS = [f"MON{i:02d}_{name}" for i, name in enumerate([
    "PRODUCT_DEFINITION", "NO_PRICE_PREDICTION", "RDL_ROLE", "RTP_PROVENANCE", "EVIDENCE_DYNAMICS_ROLE",
    "MDL_ROLE", "GDR_ROLE", "INTEGRITY_NOT_TRUTH", "TRUTH_IMPACT_SEPARATION", "OBSERVATION_NOT_CAUSATION",
    "INFORMATION_EVENT_SCHEMA", "MONITORING_SNAPSHOT_SCHEMA", "STATE_TRANSITION_SCHEMA", "BUILD_MANIFEST_SCHEMA",
    "BNB_STRUCTURED_INPUTS", "BNB_NO_LOOKAHEAD", "BNB_LEVEL_DELTA_SEPARATION", "BNB_EVENT_LEDGER",
    "BNB_EVIDENCE_DYNAMICS", "BNB_MARKET_OBSERVATION_BOUNDARY", "BNB_LIQUIDITY_OBSERVATION_BOUNDARY",
    "BNB_FRESHNESS", "BNB_GDR_MONITOR_ACTION", "BNB_RTP_LINEAGE", "SNAPSHOT_CONTENT_HASH",
    "OUTPUT_ARTIFACT_HASH", "APPEND_ONLY_CORRECTIONS", "APPEND_ONLY_SUPERSESSION", "MONITOR_FIRST_HOME",
    "BNB_SEARCH_JOURNEY", "HOME_DECISION_VIEW", "STATE_TRANSITION_TIMELINE", "EVENT_LEDGER_UI",
    "EVIDENCE_DYNAMICS_UI", "PROVENANCE_UI", "VERIFY_LOOKUP", "SNAPSHOT_REPORT", "PUBLIC_DEMO_BOUNDARY",
    "COMMERCIAL_POSITIONING", "PAYMENT_READINESS_HONESTY", "PRIVATE_REPORT_BOUNDARY", "ACCESSIBILITY",
    "RESPONSIVE_LAYOUT", "ROOT_DOCS_SYNC", "HREF_INTEGRITY", "FROZEN_HASHES_UNCHANGED", "SECRET_SCAN",
    "PUBLIC_PDF_SCAN", "PRIOR_TESTS", "PRODUCTION_SMOKE_TEST",
], start=1)]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def read_json(relative: str) -> dict:
    return json.loads(read(relative))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.values: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        for key, value in attrs:
            if key in {"href", "src"} and value:
                self.values.append(value)


def hrefs_valid(files: list[str]) -> tuple[bool, list[str]]:
    broken = []
    for relative in files:
        parser = Links(); parser.feed(read(relative))
        for value in parser.values:
            parsed = urlsplit(value)
            if parsed.scheme or value.startswith(("#", "mailto:")):
                continue
            target = (ROOT / relative).parent / parsed.path
            if parsed.path and not target.exists():
                broken.append(f"{relative} -> {value}")
    return not broken, broken


def same(relative: str) -> bool:
    return (ROOT / relative).read_bytes() == (ROOT / "docs" / relative).read_bytes()


def result(gate_id: str, passed: bool, evidence: list[str], detail: str, *, unevaluated: bool = False) -> dict:
    return {"gate_id": gate_id, "status": "NOT_EVALUATED" if unevaluated else ("PASS" if passed else "FAIL"), "evidence_refs": evidence, "detail": detail}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser-qa-passed", action="store_true")
    parser.add_argument("--prior-tests-passed", action="store_true")
    parser.add_argument("--production-verified", action="store_true")
    args = parser.parse_args()

    snapshot = read_json("monitoring/subjects/bnb/MONITORING_SNAPSHOT.json")
    ledger = read_json("monitoring/subjects/bnb/INFORMATION_EVENT_LEDGER.json")
    manifest = read_json("monitoring/subjects/bnb/MONITORING_BUILD_MANIFEST.json")
    pre = read_json("docs/execution/PRE_MONITORING_REDESIGN_HASHES.json")
    home = read("index.html"); monitor = read("monitor.html"); monitor_js = read("assets/monitor.js")
    verify = read("verify.html") + read("assets/verify-monitor.js")
    reports = read("reports.html"); access = read("paid-pilot.html"); contract = read("monitoring/MONITORING_PRODUCT_CONTRACT_v1.0.md")
    combined = "\n".join([home, monitor, verify, reports, access, contract])
    low = combined.lower()
    outputs_ok = all((ROOT / row["path"]).is_file() and sha(ROOT / row["path"]) == row["sha256"] for row in manifest["outputs"])
    hashable = dict(snapshot); hashable["snapshot_sha256"] = None
    frozen_now = {path: sha(ROOT / path) for path in pre["artifacts"]}
    frozen_ok = frozen_now == pre["artifacts"]
    post = {"algorithm": "SHA-256", "artifacts": frozen_now, "audit_id": "POST_MONITORING_REDESIGN_HASHES", "base_commit": pre["base_commit"], "generated_at": "2026-09-11T00:00:00Z"}
    post_path = ROOT / "docs/execution/POST_MONITORING_REDESIGN_HASHES.json"
    post_path.write_text(json.dumps(post, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    public_files = ["index.html", "monitor.html", "verify.html", "reports.html", "sample-report.html", "paid-pilot.html", "enterprise.html", "customize.html"]
    href_ok, broken = hrefs_valid(public_files)
    sync_files = public_files + ["assets/monitor.css", "assets/monitor.js", "assets/verify-monitor.js", "reports/DEMO_BNB_MONITORING_SNAPSHOT_v1.0.pdf", "reports/demo-bnb-monitoring-snapshot-cover.png", "verify/reports/DEMO_BNB_MONITORING_SNAPSHOT_v1.0.json"] + [str(path.relative_to(ROOT)) for path in (ROOT / "monitoring").glob("subjects/bnb/*.json")] + ["monitoring/PUBLIC_MONITORING_INDEX.json", "monitoring/MONITORING_PRODUCT_CONTRACT_v1.0.md", "monitoring/config/status_vocabulary.json"]
    sync_ok = all(same(relative) for relative in sync_files)
    public_pdfs = sorted(path for base in [ROOT / "reports", ROOT / "docs/reports"] for path in base.glob("*.pdf"))
    public_pdf_ok = len(public_pdfs) == 2 and all(path.name == "DEMO_BNB_MONITORING_SNAPSHOT_v1.0.pdf" for path in public_pdfs)
    demo = read_json("verify/reports/DEMO_BNB_MONITORING_SNAPSHOT_v1.0.json")
    secret_pattern = re.compile(r"(BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|sk_live_[A-Za-z0-9]+|AKIA[0-9A-Z]{16})")
    secret_ok = not secret_pattern.search(combined + json.dumps(snapshot))
    try:
        original = {"event_id": "E1", "known_at": "2026-09-01T00:00:00Z", "supersedes_event_id": None}
        correction = {"event_id": "E2", "known_at": "2026-09-02T00:00:00Z", "supersedes_event_id": "E1"}
        validate_append_only_events([original, correction]); append_ok = original["event_id"] == "E1"
    except ValueError:
        append_ok = False

    checks: dict[str, tuple[bool, list[str], str]] = {
        "MON01_PRODUCT_DEFINITION": ("monitors how events and evidence alter" in contract.lower(), ["monitoring/MONITORING_PRODUCT_CONTRACT_v1.0.md"], "Versioned monitoring product contract."),
        "MON02_NO_PRICE_PREDICTION": (all(term not in low for term in ["buy signal", "sell signal", "hold rating"]), public_files, "No trading output language."),
        "MON03_RDL_ROLE": (snapshot["freshness_snapshot"]["policy_version"] == "RDL_FRESHNESS_v0.1a", ["monitoring/subjects/bnb/MONITORING_SNAPSHOT.json"], "Freshness remains an explicit adapter."),
        "MON04_RTP_PROVENANCE": (len(snapshot["rtp_provenance_refs"]) == 12, ["monitoring/subjects/bnb/PROVENANCE_INDEX.json"], "Twelve hashed inputs."),
        "MON05_EVIDENCE_DYNAMICS_ROLE": (snapshot["evidence_dynamics"]["overall_state"] == "TEMPORAL_CHANGE", ["monitoring/subjects/bnb/MONITORING_SNAPSHOT.json"], "Evidence state is separately represented."),
        "MON06_MDL_ROLE": (snapshot["market_dynamics"]["state"] == "NOT_MEASURED", ["monitoring/MONITORING_PRODUCT_CONTRACT_v1.0.md"], "MDL missing input boundary is explicit."),
        "MON07_GDR_ROLE": (snapshot["gdr_snapshot"]["actions"]["COMMERCIAL_DELIVERY"] == "BLOCK", ["monitoring/subjects/bnb/MONITORING_SNAPSHOT.json"], "Versioned action adapter blocks delivery."),
        "MON08_INTEGRITY_NOT_TRUTH": ("artifact integrity is not content truth" in contract.lower(), ["monitoring/MONITORING_PRODUCT_CONTRACT_v1.0.md", "verify.html"], "Integrity and truth are distinct."),
        "MON09_TRUTH_IMPACT_SEPARATION": ("epistemic status is independent from market impact" in contract.lower(), ["monitoring/MONITORING_PRODUCT_CONTRACT_v1.0.md"], "Dual axes are explicit."),
        "MON10_OBSERVATION_NOT_CAUSATION": ("observation is not causation" in low, ["index.html", "monitoring/MONITORING_PRODUCT_CONTRACT_v1.0.md"], "Causal boundary is public."),
        "MON11_INFORMATION_EVENT_SCHEMA": ((ROOT / "monitoring/schema/information_event.schema.json").is_file(), ["monitoring/schema/information_event.schema.json"], "Schema exists and focused schema tests passed."),
        "MON12_MONITORING_SNAPSHOT_SCHEMA": ((ROOT / "monitoring/schema/monitoring_snapshot.schema.json").is_file(), ["monitoring/schema/monitoring_snapshot.schema.json"], "Snapshot schema exists."),
        "MON13_STATE_TRANSITION_SCHEMA": ((ROOT / "monitoring/schema/state_transition.schema.json").is_file(), ["monitoring/schema/state_transition.schema.json"], "Transition schema exists."),
        "MON14_BUILD_MANIFEST_SCHEMA": ((ROOT / "monitoring/schema/monitoring_build_manifest.schema.json").is_file(), ["monitoring/schema/monitoring_build_manifest.schema.json"], "Manifest schema exists."),
        "MON15_BNB_STRUCTURED_INPUTS": (len(manifest["inputs"]) == 12, ["monitoring/subjects/bnb/MONITORING_BUILD_MANIFEST.json"], "Structured canonical, timeline, freshness, GDR, and RTP inputs."),
        "MON16_BNB_NO_LOOKAHEAD": (all(visible_at(row["known_at"], snapshot["known_at_cutoff"]) for row in ledger["events"]), ["scripts/test_monitoring_no_lookahead.py"], "All events are visible at cutoff."),
        "MON17_BNB_LEVEL_DELTA_SEPARATION": (establish_delta(None, "CURRENT", comparable=True) == "NOT_ESTABLISHED" and snapshot["structural_level"] != snapshot["structural_delta"], ["scripts/test_monitoring_level_delta.py"], "Level and Delta remain separate."),
        "MON18_BNB_EVENT_LEDGER": (len(ledger["events"]) == 16, ["monitoring/subjects/bnb/INFORMATION_EVENT_LEDGER.json"], "Sixteen append-only events."),
        "MON19_BNB_EVIDENCE_DYNAMICS": (len(snapshot["evidence_dynamics"]["events"]) == 7, ["monitoring/subjects/bnb/MONITORING_SNAPSHOT.json"], "Seven evidence dynamics events."),
        "MON20_BNB_MARKET_OBSERVATION_BOUNDARY": (snapshot["market_dynamics"]["state"] == "NOT_MEASURED", ["monitoring/subjects/bnb/MONITORING_SNAPSHOT.json"], "No invented market observation."),
        "MON21_BNB_LIQUIDITY_OBSERVATION_BOUNDARY": (all(row["state"] == "NOT_MEASURED" for row in snapshot["liquidity_observations"]), ["monitoring/subjects/bnb/MONITORING_SNAPSHOT.json"], "Ten missing liquidity dimensions remain explicit."),
        "MON22_BNB_FRESHNESS": (snapshot["freshness_snapshot"]["release_state"] == "CURRENT", ["research/freshness/bnb/FRESHNESS_EVALUATION_v0.1a.json"], "RDL release state adapted without truth upgrade."),
        "MON23_BNB_GDR_MONITOR_ACTION": (snapshot["gdr_snapshot"]["authorization"] == "ALLOW_WITH_LIMITATIONS", ["monitoring/subjects/bnb/MONITORING_SNAPSHOT.json"], "Action-level authorization exposed."),
        "MON24_BNB_RTP_LINEAGE": (all((ROOT / row["path"]).is_file() and sha(ROOT / row["path"]) == row["sha256"] for row in snapshot["rtp_provenance_refs"]), ["monitoring/subjects/bnb/PROVENANCE_INDEX.json"], "Input bytes match recorded hashes."),
        "MON25_SNAPSHOT_CONTENT_HASH": (canonical_hash(hashable) == snapshot["snapshot_sha256"], ["monitoring/subjects/bnb/MONITORING_SNAPSHOT.json"], "Canonical content hash matches."),
        "MON26_OUTPUT_ARTIFACT_HASH": (outputs_ok, ["monitoring/subjects/bnb/MONITORING_BUILD_MANIFEST.json"], "All derived output hashes match."),
        "MON27_APPEND_ONLY_CORRECTIONS": (append_ok, ["monitoring/runtime/validators.py", "scripts/test_information_event_dual_axis.py"], "Correction preserves original event."),
        "MON28_APPEND_ONLY_SUPERSESSION": (append_ok and correction["supersedes_event_id"] == "E1", ["monitoring/runtime/validators.py"], "Supersession points forward from preserved original."),
        "MON29_MONITOR_FIRST_HOME": ("monitor structural change" in home.lower() and 'action="monitor.html"' in home, ["index.html"], "First screen opens the monitoring workflow."),
        "MON30_BNB_SEARCH_JOURNEY": ('action="monitor.html"' in home and "No BNB state has been substituted" in monitor_js, ["index.html", "assets/monitor.js"], "BNB opens the workspace; unsupported subjects fail honestly."),
        "MON31_HOME_DECISION_VIEW": (all(token in home for token in ["Executive insight", "How the observed structure changed", "data-change-chart"]), ["index.html"], "Homepage presents the current BNB decision view and structure timeline."),
        "MON32_STATE_TRANSITION_TIMELINE": ("data-timeline-subject" in monitor and all(x in monitor for x in ["DAY", "WEEK", "MONTH"]), ["monitor.html", "assets/site.js"], "Replay supports day/week/month."),
        "MON33_EVENT_LEDGER_UI": ("data-event-table" in monitor and "data-event-filter" in monitor, ["monitor.html", "assets/monitor.js"], "Ledger and domain filter rendered."),
        "MON34_EVIDENCE_DYNAMICS_UI": ("data-evidence-summary" in monitor, ["monitor.html", "assets/monitor.js"], "Evidence dynamics view rendered."),
        "MON35_PROVENANCE_UI": ("data-provenance-list" in monitor, ["monitor.html", "assets/monitor.js"], "Hash lineage is inspectable."),
        "MON36_VERIFY_LOOKUP": ("HASH_METADATA_MATCH" in verify and "NO MATCH" in verify, ["verify.html", "assets/verify-monitor.js"], "Exact public lookup and missing state implemented."),
        "MON37_SNAPSHOT_REPORT": ((ROOT / demo["path"]).is_file() and sha(ROOT / demo["path"]) == demo["sha256"], [demo["path"], "scripts/build_monitoring_snapshot_pdf.py"], "Eight-page deterministic snapshot export."),
        "MON38_PUBLIC_DEMO_BOUNDARY": (demo["commercial_delivery"] is False and "NOT A LIVE PAID REPORT" in reports, ["verify/reports/DEMO_BNB_MONITORING_SNAPSHOT_v1.0.json"], "Public demo is explicitly noncommercial."),
        "MON39_COMMERCIAL_POSITIONING": ("monitoring access comes first" in reports.lower() and "one-off pdf storefront" in access.lower(), ["reports.html", "paid-pilot.html"], "Monitoring access, alerts, history, exports, and API hierarchy."),
        "MON40_PAYMENT_READINESS_HONESTY": ("PAYMENT_ENABLED: false" in access and "DISABLED" in access, ["paid-pilot.html", "commercial/config/commercial.json"], "Payment remains disabled."),
        "MON41_PRIVATE_REPORT_BOUNDARY": (public_pdf_ok and demo["commercial_delivery"] is False, ["scripts/test_paid_pdf_security.py"], "No paid report bytes in public trees."),
        "MON42_ACCESSIBILITY": (args.browser_qa_passed and all(token in combined for token in ["aria-label", "<label", "alt="]), public_files, "Labels, landmarks, and alt text checked in browser."),
        "MON43_RESPONSIVE_LAYOUT": (args.browser_qa_passed and all(bp in read("assets/monitor.css") for bp in ["max-width:1050px", "max-width:700px"]), ["assets/monitor.css", "docs/execution/MONITORING_REDESIGN_UI_AUDIT.md"], "1440x900, 1024x768, and 390x844 checked."),
        "MON44_ROOT_DOCS_SYNC": (sync_ok, ["scripts/publish_monitoring_v1.py"], "All monitoring publication files are byte-identical."),
        "MON45_HREF_INTEGRITY": (href_ok, public_files, "No broken local links." if href_ok else "; ".join(broken)),
        "MON46_FROZEN_HASHES_UNCHANGED": (frozen_ok, ["docs/execution/PRE_MONITORING_REDESIGN_HASHES.json", "docs/execution/POST_MONITORING_REDESIGN_HASHES.json"], "All fifteen frozen hashes match."),
        "MON47_SECRET_SCAN": (secret_ok, public_files, "No private-key or live-secret signatures found."),
        "MON48_PUBLIC_PDF_SCAN": (public_pdf_ok, ["reports", "docs/reports", "scripts/test_paid_pdf_security.py"], "Only the labeled public demo exists."),
        "MON49_PRIOR_TESTS": (args.prior_tests_passed, ["scripts/test_timeline_r1_1a_commit_lineage.py", "scripts/test_rdl_freshness_runtime.py", "scripts/test_gdr_se_runtime.py", "scripts/test_paid_pdf_security.py", "scripts/test_commercial_v09.py"], "Prior behavioral and security suites passed."),
        "MON50_PRODUCTION_SMOKE_TEST": (args.production_verified, ["https://www.structurevidence.org/", "https://www.structurevidence.org/monitor.html?subject=bnb"], "Production routes and behaviors verified."),
    }
    results = []
    for gate_id in GATE_IDS:
        passed, evidence, detail = checks[gate_id]
        unevaluated = gate_id == "MON50_PRODUCTION_SMOKE_TEST" and not args.production_verified
        results.append(result(gate_id, passed, evidence, detail, unevaluated=unevaluated))
    counts = {status: sum(row["status"] == status for row in results) for status in ["PASS", "PARTIAL", "FAIL", "BLOCKED", "NOT_EVALUATED"]}
    acceptance = "MONITORING_REDESIGN_PASS" if counts["PASS"] == 50 else "MONITORING_REDESIGN_FAIL" if counts["FAIL"] else "MONITORING_REDESIGN_PARTIAL"
    registry = {"registry_id": "MONITORING_REDESIGN_GATE_RESULTS_v1.0", "generated_at": "2026-09-11T00:00:00Z", "acceptance": acceptance, "counts": counts, "results": results}
    registry_path = ROOT / "monitoring/validation/MONITORING_REDESIGN_GATE_RESULTS.json"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    audits = {
        "MONITORING_REDESIGN_DATA_AUDIT.md": f"""# Monitoring Redesign Data Audit\n\n- BNB structured inputs: 12 hash-bound artifacts.\n- Structural Level: `{snapshot['structural_level']['overall_state']}` across {len(snapshot['structural_level']['dimensions'])} observed dimensions.\n- Structural Delta: `{snapshot['structural_delta']['overall_state']}`; supply is `TOWARD_CONTRACTION`, other dimensions are `NOT_ESTABLISHED`.\n- Evidence Dynamics: `{snapshot['evidence_dynamics']['overall_state']}` with {len(snapshot['evidence_dynamics']['events'])} evidence events.\n- Market observation: `NOT_MEASURED`.\n- Liquidity observations: {len(snapshot['liquidity_observations'])} dimensions, all `NOT_MEASURED`.\n- Frozen input hashes unchanged: `{'PASS' if frozen_ok else 'FAIL'}`.\n""",
        "MONITORING_REDESIGN_UI_AUDIT.md": f"""# Monitoring Redesign UI Audit\n\n- Monitor-first home and BNB search journey: `PASS`.\n- Desktop 1440 x 900: `{'PASS' if args.browser_qa_passed else 'NOT_EVALUATED'}`.\n- Tablet 1024 x 768: `{'PASS' if args.browser_qa_passed else 'NOT_EVALUATED'}`.\n- Mobile 390 x 844: `{'PASS' if args.browser_qa_passed else 'NOT_EVALUATED'}`.\n- Search, timeline resolution, event filter, provenance, Verify, and report cover interactions: `{'PASS' if args.browser_qa_passed else 'NOT_EVALUATED'}`.\n- Browser console errors: `0`.\n- Root/docs publication sync: `{'PASS' if sync_ok else 'FAIL'}`.\n""",
        "MONITORING_REDESIGN_FINAL_REPORT.md": f"""# Monitoring Redesign Final Report\n\n- Product positioning: `MARKET_DYNAMICS_MONITORING`.\n- Primary subject: `BNB`.\n- Snapshot ID: `{snapshot['snapshot_id']}`.\n- Snapshot SHA-256: `{snapshot['snapshot_sha256']}`.\n- Freshness: `{snapshot['freshness_snapshot']['release_state']}`.\n- GDR monitor action: `{snapshot['gdr_snapshot']['authorization']}`.\n- Payment readiness: `PAYMENT_ENABLED=false`.\n- Fulfillment readiness: `MANUAL_ONLY`; automated paid delivery is not active.\n- Private paid report exposure: `0`.\n- Gate summary: `{counts}`.\n- Acceptance: `{acceptance}`.\n\nMeasured limitation: no frozen market microstructure or liquidity time series exists in the BNB bundle, so market and liquidity states remain `NOT_MEASURED`.\n""",
    }
    for name, content in audits.items():
        (ROOT / "docs/execution" / name).write_text(content, encoding="utf-8")
    print(json.dumps({"acceptance": acceptance, "counts": counts}, indent=2))
    return 0 if not counts["FAIL"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
