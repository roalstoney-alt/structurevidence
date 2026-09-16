#!/usr/bin/env python3
"""Positive and adversarial tests for Phase B-R1."""
import copy
import unittest
from unittest.mock import patch

import jsonschema
import validate_cml_ov_phase_b_r1 as r1


class PhaseBR1Tests(unittest.TestCase):
    def setUp(self):
        self.c = copy.deepcopy(r1.context("OV-03"))

    def rejects(self, validator):
        with self.assertRaises((ValueError, KeyError, jsonschema.ValidationError)):
            validator(self.c)

    def test_positive_targets(self):
        for target in r1.TARGETS:
            result = r1.evaluate(r1.context(target))
            self.assertEqual(result["summary"], {"PASS": 8, "FAIL": 0}, result)
            self.assertEqual(result["terminal_outcome"], "PUBLIC_EVIDENCE_CEILING")

    def test_ceiling_is_not_customer_pain(self):
        self.c["package"]["assessment"]["confirmed_customer_pain"] = True
        self.rejects(r1.terminal_outcome)
        self.rejects(r1.provenance)

    def test_ceiling_is_not_bottleneck(self):
        self.c["package"]["assessment"]["public_bottleneck"] = True
        self.rejects(r1.terminal_outcome)
        self.rejects(r1.bottleneck_discipline)

    def test_tool_capability_cannot_become_bottleneck(self):
        claim = self.c["package"]["claims"][2]
        claim["topic"] = "OBSERVED_PUBLIC_BOTTLENECK"
        self.c["package"]["assessment"].update(terminal_outcome="PUBLIC_BOTTLENECK_FOUND", public_bottleneck=True)
        self.rejects(r1.bottleneck_discipline)

    def test_no_application_requires_direct_negation(self):
        self.c["package"]["assessment"]["terminal_outcome"] = "NO_PLAUSIBLE_CURRENT_APPLICATION"
        self.rejects(r1.terminal_outcome)

    def test_ceiling_requires_explicit_unknowns(self):
        self.c["package"]["assessment"]["facts_requiring_nonpublic_validation"] = []
        self.rejects(r1.terminal_outcome)

    def test_ov01_scope_is_exactly_two_passes(self):
        self.c = copy.deepcopy(r1.context("OV-01"))
        self.c["package"]["passes"].append(copy.deepcopy(self.c["package"]["passes"][0]))
        self.rejects(r1.targeted_scope)

    def test_ov01_rejects_catalog_or_distributor_repeat(self):
        self.c = copy.deepcopy(r1.context("OV-01"))
        self.c["package"]["passes"][0]["queries"].append("broad distributor catalog search")
        self.rejects(r1.targeted_scope)

    def test_ov03_requires_production_calibration_and_verdict(self):
        self.c["package"]["passes"][2]["result"] = "Generic VNA information."
        self.rejects(r1.targeted_scope)

    def test_prohibited_actions_and_release(self):
        for key in ["contact_attempted", "samples_bought", "quotations_requested", "replacement_designed", "snipe_solution_authorized"]:
            with self.subTest(key=key):
                self.c["package"]["boundaries"][key] = True
                self.rejects(r1.boundary)
                self.c["package"]["boundaries"][key] = False
        self.c["package"]["boundaries"]["public_release"] = "ALLOW"
        self.rejects(r1.boundary)

    def test_source_host_and_claim_reciprocity(self):
        self.c["package"]["sources"][0]["host"] = "invalid.example"
        self.rejects(r1.provenance)
        self.c = copy.deepcopy(r1.context("OV-03"))
        self.c["package"]["sources"][0]["supports_claims"] = []
        self.rejects(r1.provenance)

    def test_wave1_mutation(self):
        with patch.object(r1.subprocess, "check_output", return_value="technical-risk/records/example/OV-01.v0.2.json\n"):
            self.rejects(r1.baseline_integrity)

    def test_successor_cannot_predate_accepted_wave1(self):
        self.c["record"]["core"]["known_at"] = "2026-09-16T13:00:00+08:00"
        self.rejects(r1.baseline_integrity)

    def test_new_record_structures_fail_closed(self):
        self.c["record"]["opportunity_validation"]["research_event"]["unexpected"] = True
        self.rejects(r1.provenance)
        del self.c["record"]["opportunity_validation"]["research_event"]["unexpected"]
        self.c["record"]["opportunity_validation"]["artifact_hashes"]["unexpected.txt"] = "0" * 64
        self.rejects(r1.provenance)

    def test_ov02_or_ov04_change(self):
        with patch("subprocess.check_output", return_value="?? technical-risk/records/nxp-radio-power-2026/phase-b-r1/\n"):
            self.rejects(r1.target_isolation)

    def test_successor_tampering(self):
        self.c["record"]["core"]["record_hash"] = "0" * 64
        self.rejects(r1.successor_integrity)

    def test_private_or_decision_field(self):
        self.c["package"]["assessment"]["opportunity_state"] = "CONFIRMED"
        self.rejects(r1.boundary)


if __name__ == "__main__":
    unittest.main()
