#!/usr/bin/env python3
"""Consistency tests for the CML v1.1 final audit outputs."""
import json
import unittest

import validate_cml_v11_final as final


class CMLV11FinalAuditTests(unittest.TestCase):
    def test_all_25_independent_gates_pass(self):
        result=final.evaluate()
        self.assertEqual(result["summary"],{"PASS":25,"FAIL":0,"NOT_EVALUATED":0})
        self.assertEqual(result["old_record_mutation_count"],0)
        self.assertEqual(len({row["gate_id"] for row in result["results"]}),25)

    def test_frozen_gate_artifact_matches_live_evaluation(self):
        frozen=json.loads((final.ROOT/"technical-risk/cml-v1.1/validation/CML_V1_1_GATE_RESULTS.json").read_text())
        live=final.evaluate()
        self.assertEqual(frozen["summary"],live["summary"])
        self.assertEqual([row["gate_id"] for row in frozen["results"]],[row["gate_id"] for row in live["results"]])
        self.assertTrue(all(row["status"]=="PASS" for row in frozen["results"]))

    def test_report_contains_required_acceptance_fields(self):
        text=(final.ROOT/"docs/execution/CML_V1_1_METHOD_TRANSITION_REPORT.md").read_text()
        for field in ["ENTRY_SHA","ACTIVE_METHOD","HISTORICAL_BRANCH_STATUS","OLD_RECORD_MUTATION_COUNT","KNOWN_LIMITATIONS","UNRESOLVED_ITEMS","METHOD_ACCEPTANCE","NEXT_AUTHORIZED_PHASE"]:
            self.assertIn(field,text)
        self.assertIn("CML_V1_1_ACCEPTED",text)
        self.assertIn("PDRE_DISCOVERY_PILOT",text)


if __name__=="__main__": unittest.main()
