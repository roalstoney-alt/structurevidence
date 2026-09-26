from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from materialize_se_proposal import materialize  # noqa: E402
from se_frr_protocol import PROTOCOL_VERSION, ProtocolError  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load(kind, object_id):
    return json.loads((FIXTURES / kind / f"{object_id}.json").read_text(encoding="utf-8"))


def provenance(at):
    return {"repository": "StructEvidence materializer test", "commit_sha": None, "source_object": "SYNTHETIC_TEST_FIXTURE", "created_by": "materializer test", "method_version": PROTOCOL_VERSION, "recorded_at": at, "supersedes": None, "superseded_by": None}


def proposal():
    previous = load("states", "SE-ST-20260925-000002")
    evidence_id, state_id, change_id = "SE-EV-20260927-000006", "SE-ST-20260927-000003", "SE-CHG-20260927-000002"
    evidence = {
        "schema_version": "SE_EVIDENCE_v0.1", "evidence_id": evidence_id, "subject_id": previous["subject_id"],
        "published_at": "2026-09-26T08:00:00Z", "observed_at": "2026-09-27T08:00:00Z", "recorded_at": "2026-09-27T09:00:00Z", "effective_at": None,
        "source": {"name": "Synthetic later source", "url": None, "type": "SYNTHETIC", "publisher": None, "snapshot_ref": "SYNTHETIC_TEST_FIXTURE", "retrieved_at": "2026-09-27T08:00:00Z"},
        "raw_reference": "synthetic://phase2/evidence-6", "normalized_claim": "A later synthetic observation exists.", "evidence_type": "SYNTHETIC_PROTOCOL_EVIDENCE",
        "review": {"status": "ACCEPTED", "reason": "Synthetic controlled-gateway test.", "reviewed_at": "2026-09-27T09:00:00Z", "reviewed_by": "materializer test"},
        "counter_to": [], "research_class": "SYNTHETIC_TEST_ONLY", "visibility": "PUBLIC", "content_hash": "0" * 64, "provenance": provenance("2026-09-27T09:00:00Z"),
    }
    state = copy.deepcopy(previous)
    state.update({"state_id": state_id, "observed_at": "2026-09-27T08:30:00Z", "recorded_at": "2026-09-27T09:30:00Z", "previous_state_id": previous["state_id"], "previous_state_hash": previous["state_hash"], "accepted_evidence_ids": [*previous["accepted_evidence_ids"], evidence_id], "state_changed": True, "change_event_id": change_id, "state_hash": "0" * 64, "chain_hash": "0" * 64, "provenance": provenance("2026-09-27T09:30:00Z")})
    change = {
        "schema_version": "SE_CHANGE_v0.1", "change_id": change_id, "subject_id": previous["subject_id"], "previous_state_id": previous["state_id"], "previous_state_hash": previous["state_hash"], "new_state_id": state_id, "new_state_hash": "0" * 64,
        "detected_at": "2026-09-27T08:30:00Z", "recorded_at": "2026-09-27T09:30:00Z", "trigger_evidence_ids": [evidence_id], "unknowns_resolved": [], "unknowns_added": [], "counter_evidence_added": [], "counter_evidence_removed": [], "change_summary": "A later synthetic observation was accepted without rewriting history.", "materiality": "MINOR", "visibility": "PUBLIC", "change_hash": "0" * 64, "provenance": provenance("2026-09-27T09:30:00Z"),
    }
    return {
        "schema_version": "SE_STATE_CHANGE_PROPOSAL_v0.1", "proposal_id": "SE-PROP-20260927-000001", "subject_id": previous["subject_id"], "created_at": "2026-09-27T10:00:00Z", "created_by": "materializer test",
        "proposed_evidence_ids": [evidence_id], "proposed_evidence": [evidence], "previous_state_id": previous["state_id"], "previous_state_hash": previous["state_hash"], "proposed_state": state, "proposed_change_event": change,
        "validation_status": "VALIDATED", "chain_verification_status": "REPOSITORY_VERIFICATION_REQUIRED", "review_status": "APPROVED", "materialization_status": "NOT_MATERIALIZED", "commit_sha": None, "status": "APPROVED",
    }


class MaterializerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        (self.repo / "data" / "se-frr").mkdir(parents=True)
        for directory in FIXTURES.iterdir():
            if directory.is_dir():
                shutil.copytree(directory, self.repo / "data" / "se-frr" / directory.name)
        subprocess.run(["git", "init"], cwd=self.repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.name", "SE Test"], cwd=self.repo, check=True)
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-m", "fixture baseline"], cwd=self.repo, check=True, capture_output=True)
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(proposal(), handle)
        handle.close()
        self.proposal_path = Path(handle.name)

    def tearDown(self):
        self.proposal_path.unlink(missing_ok=True)
        self.tmp.cleanup()

    def test_dry_run_verifies_without_writing(self):
        result = materialize(self.proposal_path, self.repo, dry_run=True)
        self.assertEqual(result["chain_verification"], "PASS")
        self.assertFalse((self.repo / "data/se-frr/states/SE-ST-20260927-000003.json").exists())

    def test_materialization_appends_and_preserves_old_state(self):
        old_path = self.repo / "data/se-frr/states/SE-ST-20260925-000002.json"
        before = old_path.read_bytes()
        result = materialize(self.proposal_path, self.repo)
        self.assertEqual(result["state_id"], "SE-ST-20260927-000003")
        self.assertEqual(old_path.read_bytes(), before)
        self.assertTrue((self.repo / "data/se-frr/changes/SE-CHG-20260927-000002.json").exists())

    def test_existing_destination_is_never_overwritten(self):
        materialize(self.proposal_path, self.repo)
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-m", "materialized"], cwd=self.repo, check=True, capture_output=True)
        with self.assertRaisesRegex(ProtocolError, "destination already exists"):
            materialize(self.proposal_path, self.repo)

    def test_unverified_tail_is_rejected(self):
        value = proposal()
        value["previous_state_hash"] = "f" * 64
        self.proposal_path.write_text(json.dumps(value), encoding="utf-8")
        with self.assertRaisesRegex(ProtocolError, "verified canonical tail"):
            materialize(self.proposal_path, self.repo, dry_run=True)

    def test_dirty_worktree_is_rejected(self):
        (self.repo / "dirty.txt").write_text("dirty", encoding="utf-8")
        with self.assertRaisesRegex(ProtocolError, "clean worktree required"):
            materialize(self.proposal_path, self.repo, dry_run=True)


if __name__ == "__main__":
    unittest.main()
