#!/usr/bin/env python3
from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

PUBLIC_FILES = [
    "index.html",
    "monitor.html",
    "verify.html",
    "reports.html",
    "sample-report.html",
    "paid-pilot.html",
    "enterprise.html",
    "customize.html",
    "checkout.html",
    "terms.html",
    "terms-of-sale.html",
    "privacy.html",
    "refund-policy.html",
    "sitemap.xml",
    "robots.txt",
    "assets/monitor.css",
    "assets/monitor.js",
    "assets/verify-monitor.js",
    "assets/tron-usdt-qr.jpg",
    "assets/favicon.svg",
    "reports/DEMO_BNB_MONITORING_SNAPSHOT_v1.0.pdf",
    "reports/demo-bnb-monitoring-snapshot-cover.png",
    "verify/reports/DEMO_BNB_MONITORING_SNAPSHOT_v1.0.json",
]

PUBLIC_MONITORING_FILES = [
    "monitoring/MONITORING_PRODUCT_CONTRACT_v1.0.md",
    "monitoring/PUBLIC_MONITORING_INDEX.json",
    "monitoring/config/status_vocabulary.json",
    "monitoring/subjects/bnb/INFORMATION_EVENT_LEDGER.json",
    "monitoring/subjects/bnb/MONITORING_BUILD_MANIFEST.json",
    "monitoring/subjects/bnb/MONITORING_SNAPSHOT.json",
    "monitoring/subjects/bnb/PROVENANCE_INDEX.json",
    "monitoring/subjects/bnb/STATE_TRANSITION_INDEX.json",
]


def copy_file(relative: str) -> None:
    source = ROOT / relative
    target = DOCS / relative
    if not source.is_file():
        raise FileNotFoundError(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def main() -> int:
    for relative in PUBLIC_FILES:
        copy_file(relative)
    target_monitoring = DOCS / "monitoring"
    if target_monitoring.exists():
        shutil.rmtree(target_monitoring)
    for relative in PUBLIC_MONITORING_FILES:
        copy_file(relative)
    print(f"Published monitoring v1.0 surface to {DOCS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
