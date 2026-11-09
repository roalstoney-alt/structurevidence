#!/usr/bin/env python3
"""Regression tests for the append-only Envision evidence-chain update."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD_DIR = ROOT / "rdl/research/records/CML-PDRE-001-ENVISION-2026-11-10"
DAILY_PATH = ROOT / "data/case-watch/daily/2026/11/2026-11-10.jsonl"

HISTORICAL_HASHES = {
    "rdl/research/records/CML-PDRE-001-L1-FIELD-DEPLOYMENT-2026-09-20/field-deployment-evidence.json": "2f94a1925a4f6ec19fedf5d6c1d78c4edeba15380ecc2319d3d3ef2d067ba427",
    "rdl/research/records/CML-PDRE-001-L1-FIELD-DEPLOYMENT-2026-09-20/human-review-freeze.json": "78a518cfb87ed008a0a391b2f65ca6625f454f3dcc9e965c7db08fcc480235f6",
    "rdl/research/records/CML-PDRE-001-L1-FIELD-DEPLOYMENT-2026-09-20/research-capital-observation.json": "db83fa5d677c287068d44045533ea316cd32ca2bc4c6a41708bb8729b5562bd9",
    "rdl/research/records/CML-PDRE-001-L1-FIELD-DEPLOYMENT-2026-09-20/research-record.json": "435f7ebb2634c48d6abed4a2a5a0b3fd8403d55817e320076ecca6a88e4acbe8",
    "rdl/research/records/CML-PDRE-001-L1-FIELD-DEPLOYMENT-2026-09-20/source-classification.json": "5eaf29bf79d4e71e1745af75e278866a84426f5a08fa385f46bf965a3dc573be",
    "cases/800vdc/evidence.json": "ce37b5b9b6d3d365e2fe7cd0267d583d6a1aaa9f458154be561fe22354da4a94",
    "cases/800vdc/state_history.json": "ef9e0e715da67e5aab3833c43957ca6be695228028f00db7fec16087510113d1",
    "technical-risk/cml-v1.1/pdre/CML-PDRE-001/CASE.json": "8a91f9886d1c7791f59cf85404c905f1f6d67df91a96cff6121f57b9019d0cdb",
    "technical-risk/cml-v1.1/pdre/CML-PDRE-001/README.md": "39dd795ccf0e27c2327e70ff2c4c36a6dee6f7f697e88aea323adee4fb32bb05",
    "technical-risk/cml-v1.1/pdre/CML-PDRE-001/dependency-transfer.json": "00ff6526ed61d9d6d5c359d836548f3465519c5b91f602ae83c37d9e4c756cc6",
    "technical-risk/cml-v1.1/pdre/CML-PDRE-001/evidence-index.jsonl": "ce71d6e8f554703ccd1d99dbcb67eadb72a99e8d055949f97584023bf107f282",
    "technical-risk/cml-v1.1/pdre/CML-PDRE-001/pdre-record.json": "a4b86464b0ec9bd09fa7fe54a93c1fe2912fcc255a77d48f527e984d006b4fe8",
    "technical-risk/cml-v1.1/pdre/CML-PDRE-001/publication-control.json": "1e4d4f3684c09f8759ee128adecb602491e9ec78054db47a2c69693e45cb5e5b",
    "technical-risk/cml-v1.1/pdre/CML-PDRE-001/state-history.jsonl": "d8b1591fbfb5898f998bf4553a533d30b6650d5567193c9b48d5e640904b5629",
    "technical-risk/cml-v1.1/pdre/CML-PDRE-001/timeline.jsonl": "4d5535cd4e619d0ac71ba0590beaa0cc392e1883e278e28423d00b3384318c16",
    "data/ops/se/SCHEDULE_OWNERSHIP.json": "bdced838ae1612ee8739637f4fa6b2df4c6c13f31985b82334fe2158b0070188",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def event_identity(event, primary_source_url: str) -> str:
    identity = {
        "case_id": event["case_id"],
        "claim_type": event["claim_type"],
        "site": event["site"],
        "location": event["location"],
        "canonical_primary_source_url": primary_source_url,
    }
    return "sha256:" + hashlib.sha256(canonical_bytes(identity)).hexdigest()


def replay(existing, candidate):
    if any(row["event_id"] == candidate["event_id"] or row["deduplication_key"] == candidate["deduplication_key"] for row in existing):
        return list(existing), "DUPLICATE_NOOP"
    return [*existing, candidate], "APPENDED"


def validate_snapshot_record(record):
    if record["snapshot_status"] == "SOURCE_SNAPSHOT_UNAVAILABLE":
        if record.get("content_sha256") is not None:
            raise AssertionError("unavailable source cannot carry a fabricated content hash")
        return
    path = ROOT / record["snapshot_path"]
    if not path.is_file():
        raise AssertionError("captured snapshot path is missing")
    if sha256(path) != record["content_sha256"]:
        raise AssertionError("stored snapshot hash mismatch")


class EnvisionAppendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load_json(RECORD_DIR / "source-acquisition-manifest.json")
        cls.event = load_json(RECORD_DIR / "evidence-event.json")
        cls.claim = load_jsonl(RECORD_DIR / "claim-ledger.jsonl")[0]
        cls.transition = load_jsonl(RECORD_DIR / "state-transition.jsonl")[0]
        cls.replay_policy = load_json(RECORD_DIR / "replay-policy.json")
        cls.daily = load_jsonl(DAILY_PATH)[0]

    def test_source_snapshots_are_exactly_hash_bound(self):
        for source in self.manifest["sources"]:
            validate_snapshot_record(source)

    def test_original_announcement_and_requested_page_are_both_present(self):
        by_id = {row["source_id"]: row for row in self.manifest["sources"]}
        self.assertEqual(by_id["CML-PDRE-001-SRC-ENVISION-PRN-20261102"]["published_at"], "2026-11-02T07:42:00Z")
        self.assertEqual(by_id["CML-PDRE-001-SRC-ENVISION-ESN-20261104"]["published_at"], "2026-11-04")
        self.assertTrue(all(row["source_role"] == "OPERATOR_AUTHORED" for row in by_id.values()))

    def test_evidence_event_preserves_required_boundaries(self):
        self.assertEqual(self.event["claim_status"], "OPERATOR_REPORTED_LIVE_DEPLOYMENT")
        self.assertEqual(self.event["technology"], "10kV AC / SST / 800VDC")
        self.assertEqual(self.event["operating_load"], "AI_COMPUTING_LOAD_OPERATOR_REPORTED")
        for key in ("independent_acceptance", "installed_IT_load_MW", "protection_test_results", "long_duration_operation", "measured_CAPEX_OPEX"):
            self.assertEqual(self.event[key], "UNKNOWN")
        self.assertEqual(self.event["evidence_admission"], "ACCEPTED_AS_TRACEABLE_OPERATOR_STATEMENT")

    def test_campus_opening_is_not_used_as_commissioning_date(self):
        self.assertEqual(self.event["campus_opening"], "2026-08")
        self.assertEqual(self.event["sst_800vdc_commissioning_date"], "UNKNOWN")
        self.assertEqual(self.event["planned_capacity"], "3GW_PLANNED_NOT_COMMISSIONED_LOAD")

    def test_claim_resolves_from_event_and_preserves_independent_boundary(self):
        self.assertIn(self.event["event_id"], self.claim["evidence_refs"])
        self.assertEqual(self.claim["EVIDENCE_CLASS"], "ISSUER_REPORTED_FIELD_OPERATION")
        self.assertEqual(self.claim["SOURCE_DEPENDENCY"], "OPERATOR_AUTHORED")
        self.assertEqual(self.claim["INDEPENDENT_VALIDATION"], "NOT_ESTABLISHED")

    def test_claim_resolves_to_state_transition(self):
        self.assertEqual(self.transition["new_evidence_event_id"], self.event["event_id"])
        self.assertEqual(self.transition["claim_ref"], self.claim["claim_id"])
        self.assertEqual(self.transition["new_evidence_accepted"], "YES")
        self.assertEqual(self.transition["operator_reported_live_deployment"], "RECORDED")
        self.assertFalse(self.transition["canonical_readiness_changed"])
        self.assertFalse(self.transition["public_state_mutated"])

    def test_economics_and_long_term_operation_remain_unknown(self):
        unchanged = self.transition["explicit_unchanged_uncertainties"]
        self.assertEqual(unchanged["independent_long_term_operation"], "UNKNOWN")
        self.assertEqual(unchanged["economic_benefits"], "UNKNOWN")

    def test_deduplication_key_uses_canonical_identity(self):
        primary = self.replay_policy["canonical_primary_source_url"]
        self.assertEqual(event_identity(self.event, primary), self.event["deduplication_key"])
        self.assertEqual(self.event["deduplication_key"], self.replay_policy["expected_deduplication_key"])

    def test_same_source_replay_is_idempotent(self):
        once, first_result = replay([], self.event)
        twice, second_result = replay(once, self.event)
        self.assertEqual(first_result, "APPENDED")
        self.assertEqual(second_result, "DUPLICATE_NOOP")
        self.assertEqual(len(twice), 1)

    def test_missing_source_bytes_cannot_create_a_hash(self):
        unavailable = {"snapshot_status": "SOURCE_SNAPSHOT_UNAVAILABLE", "content_sha256": "0" * 64}
        with self.assertRaisesRegex(AssertionError, "fabricated content hash"):
            validate_snapshot_record(unavailable)

    def test_chindata_and_canonical_history_are_byte_identical(self):
        for relative, expected in HISTORICAL_HASHES.items():
            self.assertEqual(sha256(ROOT / relative), expected, relative)
        self.assertEqual(self.transition["previous_state_ref_sha256"], HISTORICAL_HASHES[self.transition["previous_state_ref"]])

    def test_daily_delta_uses_existing_pipeline_without_public_mutation(self):
        self.assertEqual(self.daily["case_id"], "CML-PDRE-001")
        self.assertEqual(self.daily["deployment_status"], "NAMED_SITE_LIVE_DEPLOYMENT_OPERATOR_REPORTED")
        self.assertEqual(self.daily["next_observable"], "COMMISSIONING / PROTECTION / MEASURED_LOAD / OPERATING_DATA")
        self.assertTrue(self.daily["weekly_review_required"])
        self.assertFalse(self.daily["public_state_mutated"])

    def test_existing_architecture_hash_chain_limitation_is_explicit(self):
        self.assertEqual(self.transition["hash_chain_status"], "NOT_SUPPORTED_BY_EXISTING_CML_CASE_ARCHITECTURE")
        self.assertEqual(self.replay_policy["previous_event_hash_linkage"], "NOT_SUPPORTED_BY_EXISTING_CML_CASE_ARCHITECTURE")


if __name__ == "__main__":
    unittest.main()
