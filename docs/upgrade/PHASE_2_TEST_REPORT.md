# Phase 2 Test Report

`STATUS = COMPLETE`

Targeted Phase 2 tests: `scripts/test_rdl_phase2_cml_pdre_001.py`.

Required checks cover L0-only actions, evidence-reference resolution, no parallel evidence store, unknown preservation, counter-evidence preservation, event/knowledge-time separation, historical immutability, RDL record validation, hash integrity, transparent reuse arithmetic, and prohibition of opaque scores.

## Results

| Suite | Result |
| --- | --- |
| Phase 2 targeted tests | 16/16 PASS |
| CML v1.1 / pilot baseline | 72/72 PASS |
| Phase 1 RDL tests | 24/24 PASS |
| RDL freshness suites | 4/4 PASS |
| Full repository discovery | 179 run; 176 PASS; exactly 3 known pre-existing failures |

The three known failures are the previously documented Opportunity Validation Phase A history-shape error, Phase B frozen-baseline failure, and Phase B-R1 accepted-baseline failure. They remain `PRE_EXISTING / OUT_OF_SCOPE` and were not modified, rebaselined, or marked as passing.

`NEW_FAILURES = 0`
