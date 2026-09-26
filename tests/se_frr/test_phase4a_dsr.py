import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("phase4a_dsr", ROOT / "apps/demand-signal-radar/dsr.py")
dsr = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(dsr)

SUBJECTS = [{"subject_id": "SE-SUBJ-000001", "canonical_name": "NXP RF Power", "aliases": ["MRF101AN"], "tags": ["RF power"], "current_state": {"state_id": "SE-ST-20260925-000001", "state_code": "MIGRATION_PRESSURE_DETECTED"}}]
RAW = {"platform": "GITHUB", "source_url": "https://github.com/example/project/issues/42", "observed_at": "2026-09-26T10:00:00Z", "author_public_id": "42", "author_public_name": "public-engineer", "organization_public_name": None, "text": "We cannot source MRF101AN after EOL and need an alternative. Has anyone tested a replacement in production?", "contact_route": "PUBLIC_REPLY"}

class Phase4ADsrTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.store = dsr.RadarStore(Path(self.temp.name) / "dsr.sqlite3")
    def tearDown(self): self.temp.cleanup()
    def test_signal_schema_and_score(self):
        signal = dsr.classify(RAW, SUBJECTS)
        schema = json.loads((ROOT / "schemas/se-frr/demand-signal.schema.json").read_text())
        jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(signal)
        self.assertEqual(signal["real_decision_score"], 10)
        self.assertEqual(signal["score_class"], "HIGH_VALUE")
        self.assertEqual(signal["mapped_subject_id"], "SE-SUBJ-000001")
    def test_private_or_unexpected_fields_rejected(self):
        for field in ["private_email", "phone", "address", "family_information"]:
            with self.assertRaises(ValueError): dsr.classify({**RAW, field: "private"}, SUBJECTS)
    def test_https_source_required(self):
        with self.assertRaises(ValueError): dsr.classify({**RAW, "source_url": "http://private.invalid"}, SUBJECTS)
    def test_dedupe_url_and_semantic_problem(self):
        signal = dsr.classify(RAW, SUBJECTS)
        self.assertFalse(self.store.ingest(signal)[1]); self.assertTrue(self.store.ingest(signal)[1])
        repeated = dsr.classify({**RAW, "source_url": "https://github.com/example/project/issues/43"}, SUBJECTS)
        self.assertTrue(self.store.ingest(repeated)[1])
    def test_qualified_queue_and_candidate_card(self):
        self.store.ingest(dsr.classify(RAW, SUBJECTS)); queue = self.store.queue()
        self.assertEqual(len(queue), 1); self.assertEqual(queue[0]["recommended_human_action"], "PUBLIC_REPLY")
        self.assertIn("timestamped evidence chain", queue[0]["draft_public_reply"])
    def test_review_approves_but_never_contacts(self):
        signal, _ = self.store.ingest(dsr.classify(RAW, SUBJECTS))
        reviewed = self.store.review(signal["signal_id"], "APPROVE_PUBLIC_REPLY", "human-owner")
        self.assertEqual(reviewed["contact_status"], "APPROVED_FOR_CONTACT")
        events = [row[0] for row in self.store.db.execute("SELECT event_type FROM contact_events")]
        self.assertIn("HUMAN_CONTACT_APPROVED", events); self.assertNotIn("HUMAN_CONTACT_SENT", events)
    def test_unmapped_high_value_preserved(self):
        signal = dsr.classify({**RAW, "source_url": "https://github.com/example/project/issues/44", "text": "We cannot source ABCD-9999 after EOL and need alternative. Has anyone tested replacement in production?"}, [])
        self.assertEqual(signal["score_class"], "HIGH_VALUE"); self.assertIsNone(signal["mapped_subject_id"])
    def test_daily_output(self):
        self.store.ingest(dsr.classify(RAW, SUBJECTS)); report = self.store.daily("2026-09-26")
        self.assertEqual(report["high_value_signals"], 1); self.assertEqual(report["human_review_required"], 1)
    def test_paid_chain_is_preparation_only(self):
        scope = self.store.prepare_scope("SE-REQ-20260926-000001", "Bounded evidence chain", "199", "USD")
        self.assertEqual(scope["provider_adapter"], "DISABLED"); self.assertEqual(scope["payment_status"], "NOT_REQUESTED")
    def test_source_policy_capabilities(self):
        caps = dsr.source_capabilities(); self.assertEqual(caps["GITHUB"], "AUTO_PUBLIC_API"); self.assertEqual(caps["REDDIT"], "MANUAL_SEARCH_REQUIRED")

if __name__ == "__main__": unittest.main()
