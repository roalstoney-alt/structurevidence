#!/usr/bin/env python3
"""Targeted tests for the post-commit CML v1.1 regression harness."""
from __future__ import annotations

import json
import unittest

import cml_v11_regression as regression
import validate_cml_v11_core as core


class CMLV11RegressionHarnessTests(unittest.TestCase):
    def test_current_head_descends_from_accepted_v11_2_without_breaking_v11_1(self):
        head = regression.git("rev-parse", "HEAD").strip()

        self.assertTrue(
            regression.is_ancestor(
                regression.V11_2_ACCEPTED_SHA,
                head,
            )
        )

        self.assertEqual(
            regression.validate_v11_1_milestone()["milestone"],
            regression.V11_1_SHA
        )

        self.assertEqual(
            regression.historical_mutations(),
            []
        )

    def test_current_head_passes_v11_2_milestone_regression(self):
        result = regression.validate_v11_2_milestone()
        self.assertEqual(result["accepted"], regression.V11_2_ACCEPTED_SHA)
        self.assertGreater(result["frozen_core_files"], 0)
        self.assertEqual(core.preservation_regression()["old_record_mutation_count"], 0)

    def test_future_files_are_not_historical_or_frozen_core(self):
        future = "technical-risk/cml-v1.1/schema/trigger-event.schema.json"
        self.assertNotIn(future, regression.historical_protected_paths())
        self.assertNotIn(future, regression.frozen_v11_2_paths())

    def test_changed_historical_file_would_be_detected_without_mutation(self):
        path = regression.historical_protected_paths()[0]
        mutations = regression.compare_content(
            [path], lambda _: b"accepted historical bytes", lambda _: b"changed bytes"
        )
        self.assertEqual(mutations, [path])

    def test_changed_frozen_v11_2_schema_would_be_detected_without_mutation(self):
        path = next(path for path in regression.frozen_v11_2_paths() if "/schema/" in path)
        mutations = regression.compare_content(
            [path], lambda _: b"accepted schema bytes", lambda _: b"changed schema bytes"
        )
        self.assertEqual(mutations, [path])

    def test_future_history_append_is_allowed_but_rewrite_is_rejected(self):
        current = (regression.ROOT / regression.HISTORY_PATH).read_text(encoding="utf-8").splitlines()
        future = current + [json.dumps({"change_type": "FUTURE_APPEND_ONLY_TEST", "method_version": "CML_v1.1"})]
        result = regression.validate_version_history_lines(future)
        self.assertEqual(result["current_lines"], len(current) + 1)
        rewritten = list(current)
        rewritten[0] = json.dumps({"rewritten": True})
        with self.assertRaises(ValueError):
            regression.validate_version_history_lines(rewritten)


if __name__ == "__main__":
    unittest.main()
