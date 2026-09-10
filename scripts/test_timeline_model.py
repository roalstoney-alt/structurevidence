from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUBJECTS = ["strategy", "bnb", "sol", "trx", "xlm"]
RESOLUTIONS = {"DAY", "WEEK", "MONTH"}
EVIDENCE_STATUSES = {"FRESH", "AGING", "PARTIAL", "UNRESOLVED", "SUPERSEDED", "NOT_CONFIGURED", "NOT_APPLICABLE"}
EVENT_TYPES = {"ARTIFACT_FROZEN", "REPORT_PUBLISHED", "CORRECTION_ADDED", "SUPERSESSION", "SOURCE_PACKAGE_ADDED", "GOVERNANCE_EVENT", "TREASURY_DISCLOSURE", "PROTOCOL_EVENT", "MARKET_STRUCTURE_EVENT", "COUNTER_EVIDENCE_UPDATE", "REVIEW_EVENT"}
MODES = {"DIRECT", "RECONSTRUCTED", "SPARSE_EVENT_STATE"}


def fail(message: str) -> None:
    raise SystemExit(f"TIMELINE_MODEL_TEST_FAIL: {message}")


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest() -> str:
    h = hashlib.sha256()
    for path in sorted((ROOT / "timeline").rglob("*.json")):
        h.update(path.relative_to(ROOT).as_posix().encode())
        h.update(path.read_bytes())
    return h.hexdigest()


def main() -> None:
    for subject in SUBJECTS:
        structural = read(ROOT / "timeline" / "subjects" / f"{subject}_structural_timeline.json")
        evidence = read(ROOT / "timeline" / "subjects" / f"{subject}_evidence_timeline.json")
        events = read(ROOT / "timeline" / "subjects" / f"{subject}_event_ledger.json")
        if set(structural["supported_resolutions"]) != RESOLUTIONS or set(evidence["supported_resolutions"]) != RESOLUTIONS:
            fail(f"missing resolutions for {subject}")
        if not structural["dimensions"] or not structural["phase_ribbon"]:
            fail(f"missing structural model for {subject}")
        if subject == "strategy" and structural["construction_method"] != "SPARSE_EVENT_STATE":
            fail("Strategy must remain sparse event-state")
        for dim in structural["dimensions"]:
            for row in dim["series"]:
                if "value" in row:
                    fail(f"numeric false precision in {subject}")
                if row["resolution"] not in RESOLUTIONS or row["observation_mode"] not in MODES:
                    fail(f"invalid structural row for {subject}")
        for family in evidence["evidence_families"]:
            for row in family["series"]:
                if row["status"] not in EVIDENCE_STATUSES or row["observation_mode"] not in MODES:
                    fail(f"invalid evidence row for {subject}")
        if not events["events"]:
            fail(f"missing events for {subject}")
        for event in events["events"]:
            if event["event_type"] not in EVENT_TYPES or not event["refs"]:
                fail(f"invalid event for {subject}")
    before = digest()
    subprocess.run([sys.executable, "-B", "scripts/build_timeline_model.py"], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    after = digest()
    if before != after:
        fail("timeline generation is not deterministic")
    print("TIMELINE_MODEL_TESTS_PASS")


if __name__ == "__main__":
    main()
