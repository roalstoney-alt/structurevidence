from __future__ import annotations

import json
from copy import deepcopy
import subprocess
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker, RefResolver


ROOT = Path(__file__).resolve().parents[1]
CASES = ["800vdc", "sodium-ion-bess"]


class PublicRecordExportTest(unittest.TestCase):
    def test_export_is_deterministic(self):
        result = subprocess.run([sys.executable, "scripts/check_public_record_drift.py"], cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PUBLIC_RECORD_DRIFT = PASS", result.stdout)

    def test_case_json_schema(self):
        schema = json.loads((ROOT / "schemas/case.schema.json").read_text())
        store = {
            "https://structurevidence.org/schemas/evidence.schema.json": json.loads((ROOT / "schemas/evidence.schema.json").read_text()),
            "https://structurevidence.org/schemas/state.schema.json": json.loads((ROOT / "schemas/state.schema.json").read_text()),
        }
        resolver = RefResolver.from_schema(schema, store=store)
        validator = Draft202012Validator(schema, resolver=resolver, format_checker=FormatChecker())
        for slug in CASES:
            record = json.loads((ROOT / f"cases/{slug}/index.json").read_text())
            self.assertEqual(list(validator.iter_errors(record)), [], slug)

    def test_public_evidence_has_parent_and_atomic_route(self):
        for slug in CASES:
            record = json.loads((ROOT / f"cases/{slug}/index.json").read_text())
            for evidence in record["evidence"]:
                route = ROOT / "e" / evidence["evidence_id"]
                atomic = json.loads((route / "index.json").read_text())
                self.assertEqual(atomic["parent_case"], record["case_id"])
                self.assertTrue((route / "index.html").is_file())

    def test_event_summary_schema_rejects_malformed_provenance(self):
        schema = json.loads((ROOT / "schemas/case.schema.json").read_text())
        validator = Draft202012Validator(schema["properties"]["events"], format_checker=FormatChecker())
        events = json.loads((ROOT / "cases/800vdc/index.json").read_text())["events"]
        self.assertEqual(list(validator.iter_errors(events)), [])
        for field, value in [("state_changed", "false"), ("published_at", "2026-99-99"),
                             ("retrieved_at", None), ("url", "not-a-url"),
                             ("classifications", []), ("unexpected", True)]:
            with self.subTest(field=field):
                malformed = deepcopy(events)
                malformed[0][field] = value
                self.assertTrue(list(validator.iter_errors(malformed)))
        for field in events[0]:
            with self.subTest(missing=field):
                malformed = deepcopy(events)
                del malformed[0][field]
                self.assertTrue(list(validator.iter_errors(malformed)))
        self.assertFalse(schema["additionalProperties"])


if __name__ == "__main__":
    unittest.main()
