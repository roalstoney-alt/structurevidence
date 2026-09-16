#!/usr/bin/env python3
"""Read-only positive and adversarial tests of Wave 1 evidence boundaries."""
import copy
import unittest
from unittest.mock import patch

import jsonschema
import validate_cml_ov_phase_b as ov


class PhaseBTests(unittest.TestCase):
    def setUp(self):
        self.c = copy.deepcopy(ov.context('OV-03'))

    def rejects(self, gate):
        with self.assertRaises((ValueError, KeyError, jsonschema.ValidationError)):
            gate(self.c)

    def test_positive_packages_and_substantive_gaps(self):
        for target in ov.TARGETS:
            result = ov.evaluate(ov.context(target))
            self.assertEqual(result['summary'], {'PASS': 13, 'FAIL': 0, 'NOT_EVALUATED': 3}, result)
            self.assertEqual([r['validator'] for r in result['results'] if r['status'] == 'NOT_EVALUATED'],
                             ['current_solution', 'improvement_hypothesis', 'tool_bottleneck_mapping'])

    def test_stock_cannot_establish_usage(self):
        claim = self.c['package']['usage']['claims'][0]
        claim.update(evidence_basis='DISTRIBUTOR_LISTING', current_usage_asserted=True)
        self.c['package']['usage']['signal'] = 'CURRENT_USAGE_DIRECT'
        self.rejects(ov.current_usage)

    def test_eol_cannot_establish_customer_pain(self):
        self.c = ov.context('OV-01')
        self.c['package']['solution']['claims'][0]['customer_pain'] = 'DIRECT_PUBLIC_STATEMENT'
        self.rejects(ov.source_provenance)

    def test_price_cannot_establish_efficiency(self):
        self.c['package']['solution']['efficiency_conclusion'] = 'INEFFICIENT'
        self.rejects(ov.current_solution)

    def test_unit_price_cannot_establish_total_savings(self):
        self.c['package']['tmc']['total'] = -100
        self.rejects(ov.tmc_discipline)

    def test_unit_price_cannot_establish_migration_delta(self):
        self.c['package']['tmc']['variables'][0].update(state='PUBLIC_SIGNAL', value=90.32, unit='GBP', source_refs=['O3-S01'])
        self.rejects(ov.tmc_discipline)

    def test_mirrors_are_not_independent(self):
        self.c = ov.context('OV-01')
        self.c['package']['sources']['sources'][1]['independence_group'] = 'INDEPENDENT_DISTRIBUTOR'
        self.rejects(ov.source_independence)

    def test_missing_counter_evidence(self):
        self.c['package']['counter_evidence']['claims'] = []
        self.rejects(ov.counter_evidence)

    def test_unsupported_tool_benefit(self):
        h = self.c['package']['hypotheses']['hypotheses'][0]
        h.update(status='CONDITIONAL_RESEARCH_HYPOTHESIS', testable=True, bottleneck_claim_refs=['O3-C05'])
        self.rejects(ov.improvement_hypothesis)
        h['tool_source_refs'] = []
        self.rejects(ov.tool_bottleneck_mapping)

    def test_unsupported_adoption(self):
        p = self.c['package']['solution']['paths'][0]
        p.update(evidence_class='OBSERVED_CURRENT_SOLUTION', organization='Unverified customer', adoption_verified=True)
        self.rejects(ov.current_solution)

    def test_unverified_drop_in(self):
        claim = self.c['package']['usage']['claims'][0]
        claim['statement'] = 'The proposed assembly is a drop-in replacement.'
        self.rejects(ov.no_unverified_qualification)
        claim.update(statement='Headline characteristics match.', topic='FULLY_COMPATIBLE')
        self.rejects(ov.no_unverified_qualification)

    def test_private_data(self):
        for key in ov.load('technical-risk/config/public_private_boundary.json')['private']:
            with self.subTest(key=key):
                self.c['package']['assessment'][key] = 'private value'
                self.rejects(ov.private_boundary)
                del self.c['package']['assessment'][key]

    def test_paid_delivery_promotion(self):
        self.c['package']['assessment']['paid_delivery'] = 'ALLOW'
        self.rejects(ov.private_boundary)

    def test_public_release_promotion(self):
        self.c['package']['assessment']['public_release'] = 'ALLOW'
        self.rejects(ov.private_boundary)

    def test_snipe_solution_approval(self):
        self.c['package']['assessment']['solution_development'] = 'SNIPE_SOLUTION_APPROVED'
        self.rejects(ov.no_unverified_qualification)

    def test_phase_a_mutation(self):
        with patch.object(ov, 'frozen_changes', return_value=['technical-risk/records/example/OV-01.v0.1.json']):
            self.rejects(ov.baseline_integrity)

    def test_false_suboptimal_and_phase_c_promotion(self):
        a = self.c['package']['assessment']
        a['desk_opportunity_signal'] = 'PUBLIC_EVIDENCE_SUBOPTIMAL_SIGNAL'
        self.rejects(ov.desk_signal_discipline)
        a.update(desk_opportunity_signal='PUBLIC_EVIDENCE_UNRESOLVED_SIGNAL', decision='PROCEED_TO_PHASE_C')
        self.rejects(ov.desk_signal_discipline)

    def test_outreach_not_authorized(self):
        self.c['package']['human_targets']['targets'][0]['outreach_sent'] = True
        self.rejects(ov.human_validation_boundary)

    def test_no_invented_duration(self):
        self.c['package']['ttq']['variables'][0]['value'] = 7
        self.rejects(ov.ttq_discipline)

    def test_missing_schema_fields(self):
        del self.c['package']['sources']['sources'][0]['issuer']
        self.rejects(ov.source_provenance)

    def test_host_and_knowledge_time(self):
        source = self.c['package']['sources']['sources'][0]
        source['host'] = 'unrelated.example'
        self.rejects(ov.source_provenance)
        source['host'] = 'www.amphenolrf.com'
        source['known_at'] = '2099-01-01T00:00:00Z'
        self.rejects(ov.source_provenance)

    def test_successor_tampering(self):
        self.c['record']['core']['record_hash'] = '0' * 64
        self.rejects(ov.successor_hash_integrity)

    def test_historical_application_without_current_bridge(self):
        claim = self.c['package']['usage']['claims'][0]
        claim.update(claim_type='DIRECT_PUBLIC_EVIDENCE', evidence_basis='APPLICATION_DOCUMENT', current_usage_asserted=True)
        self.c['package']['sources']['sources'][0]['publication_date'] = '2000-01-01'
        self.c['package']['usage']['signal'] = 'CURRENT_USAGE_DIRECT'
        self.rejects(ov.current_usage)

    def test_market_signal_cannot_be_relabelled_as_bottleneck(self):
        claim = next(v for v in self.c['package']['inefficiency']['claims'] if v['claim_id'] == 'O3-C06')
        claim['topic'] = 'OBSERVED_BOTTLENECK'
        self.c['package']['hypotheses']['hypotheses'][0].update(status='CONDITIONAL_RESEARCH_HYPOTHESIS', testable=True, bottleneck_claim_refs=['O3-C06'])
        self.rejects(ov.improvement_hypothesis)
        self.c['package']['assessment']['desk_opportunity_signal'] = 'PUBLIC_EVIDENCE_SUBOPTIMAL_SIGNAL'
        self.rejects(ov.desk_signal_discipline)

    def test_bridge_requires_current_interval_and_application_source(self):
        claim = self.c['package']['usage']['claims'][0]
        claim.update(claim_type='DIRECT_PUBLIC_EVIDENCE', evidence_basis='APPLICATION_DOCUMENT', current_usage_asserted=True,
                     current_bridge={'source_refs':['O3-S01'], 'valid_from':'2000-01-01', 'valid_through':'2001-01-01', 'rationale':'Historical service window'})
        self.c['package']['usage']['signal'] = 'CURRENT_USAGE_DIRECT'
        self.rejects(ov.current_usage)
        claim['current_bridge']['valid_through'] = '2099-01-01'
        self.rejects(ov.current_usage)  # Current catalog is not an application document.

    def test_unarchived_source_cannot_claim_hash(self):
        self.c['package']['sources']['sources'][0]['artifact_path'] = 'missing.pdf'
        self.rejects(ov.source_provenance)


if __name__ == '__main__':
    unittest.main()
