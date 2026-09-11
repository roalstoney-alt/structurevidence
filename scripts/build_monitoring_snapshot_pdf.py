#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from monitoring.reporting.renderer import render_cover, render_monitoring_snapshot
from monitoring.runtime.hash import file_hash


def main() -> int:
    snapshot = ROOT / "monitoring/subjects/bnb/MONITORING_SNAPSHOT.json"
    canonical = ROOT / "output/pdf/DEMO_BNB_MONITORING_SNAPSHOT_v1.0.pdf"
    public_pdf = ROOT / "reports/DEMO_BNB_MONITORING_SNAPSHOT_v1.0.pdf"
    cover = ROOT / "reports/demo-bnb-monitoring-snapshot-cover.png"
    render_monitoring_snapshot(snapshot, canonical)
    public_pdf.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(canonical, public_pdf)
    render_cover(public_pdf, cover)
    snapshot_data = json.loads(snapshot.read_text(encoding="utf-8"))
    record = {
        "artifact_id": "SE-DEMO-BNB-MONITORING-SNAPSHOT-v1.0",
        "artifact_type": "DEMO_MONITORING_SNAPSHOT",
        "commercial_delivery": False,
        "public_safe": True,
        "label": "NOT A LIVE PAID REPORT",
        "path": "reports/DEMO_BNB_MONITORING_SNAPSHOT_v1.0.pdf",
        "sha256": file_hash(public_pdf),
        "snapshot_id": snapshot_data["snapshot_id"],
        "snapshot_sha256": snapshot_data["snapshot_sha256"],
        "generated_from": "monitoring/subjects/bnb/MONITORING_SNAPSHOT.json",
    }
    record_path = ROOT / "verify/reports/DEMO_BNB_MONITORING_SNAPSHOT_v1.0.json"
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
