#!/usr/bin/env python3
"""Build the two Phase B-R1 successor records from reviewed local artifacts."""
import copy
import hashlib
import json
from pathlib import Path

from test_cml_v01 import ROOT, digest

VERSION = "CML_OV_v0.1_PHASE_B_R1"
NOW = "2026-09-16T22:35:07+08:00"
TARGETS = {
    "OV-01": "amphenol-10081811-101-07lf",
    "OV-03": "amphenol-rf-095-725-134-006",
}
ARTIFACTS = ["01_TARGETED_DISCOVERY.json", "03_LIMITATIONS.md"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    for target, slug in TARGETS.items():
        base = ROOT / "technical-risk/records" / slug / "opportunity-validation"
        predecessor_path = base / f"{target}.v0.2.json"
        predecessor = json.loads(predecessor_path.read_text())
        package_dir = base / "phase-b-r1"
        discovery = json.loads((package_dir / ARTIFACTS[0]).read_text())
        payload = copy.deepcopy(predecessor["opportunity_validation"])
        core = copy.deepcopy(predecessor["core"])
        artifact_hashes = {name: sha(package_dir / name) for name in ARTIFACTS}
        payload.update(
            version=VERSION,
            phase="PHASE_B_R1",
            assessment_version=VERSION,
            predecessor_record_id=predecessor["core"]["record_id"],
            predecessor_record_hash=predecessor["core"]["record_hash"],
            predecessor_path=predecessor_path.relative_to(ROOT).as_posix(),
            research_event={
                "event_domain": "RESEARCH_EVENT",
                "event_type": "TARGETED_APPLICATION_AND_WORKFLOW_DISCOVERY",
                "effective_at": NOW,
                "known_at": NOW,
                "created_at": NOW,
                "source_refs": [s["source_id"] for s in discovery["sources"]],
            },
            phase_b_r1_assessment=discovery["assessment"],
            artifact_hashes=artifact_hashes,
        )
        payload["governance"] = copy.deepcopy(payload["governance"])
        payload["governance"]["reason"] = "PHASE_B_R1_INTERNAL_RESEARCH_ONLY"
        core.pop("record_hash")
        new_source_ids = [s["source_id"] for s in discovery["sources"]]
        predecessor_ref = predecessor_path.relative_to(ROOT).as_posix() + ":" + sha(predecessor_path)
        artifact_refs = [
            (package_dir / name).relative_to(ROOT).as_posix() + ":" + artifact_hashes[name]
            for name in sorted(ARTIFACTS)
        ]
        core.update(
            record_id=f"SE.CML.OV.{target}.v0.3",
            effective_at=NOW,
            known_at=NOW,
            created_at=NOW,
            updated_at=NOW,
            verification_status="TARGETED_PUBLIC_RESEARCH_REVIEWED_WITH_LIMITATIONS",
            policy_version=VERSION,
            source_refs=sorted(set(core["source_refs"]) | set(new_source_ids)),
            artifact_refs=core["artifact_refs"] + [predecessor_ref] + artifact_refs,
        )
        core["input_hash"] = digest({"sources": discovery["sources"], "payload": payload})
        core["record_hash"] = digest({"core": core, "payload": payload})
        output = {"core": core, "opportunity_validation": payload}
        (base / f"{target}.v0.3.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
