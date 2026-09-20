# Phase 2.5 Test Report

`STATUS = COMPLETE_WITH_BASELINE_REMOTE_SYNC_LIMITATION`

Targeted tests: `scripts/test_rdl_phase2_5_allocation.py`.

The suite covers baseline/tag and human-exception integrity, candidate freeze and source hash, exact card count, L0-only actions, external-research prohibition, pending authorization, no L1 execution, evidence-reference resolution, cost-unknown preservation, scope/recommendation rules, no opaque scores, RDL validation and hashes, historical immutability, and exclusion of unrelated paths from inputs.

## Results

| Suite | Result |
| --- | --- |
| Phase 2.5 targeted allocation | 17/17 PASS |
| CML transition | 9/10 PASS; one pre-existing baseline remote-sync gate failed |
| CML core | 15/15 PASS |
| CML regression harness | 5/6 PASS; one pre-existing baseline remote-sync gate failed |
| CML observation and final audit | 19/19 PASS |
| CML-PDRE-001 pilot | 22/22 PASS |
| Phase 1 RDL | 24/24 PASS |
| Phase 2 RDL | 16/16 PASS |
| RDL freshness suites | 4/4 PASS |
| Full repository discovery | 196 run; 191 PASS; 3 failures and 2 errors |

The full-discovery exceptions are exactly:

- three previously documented Opportunity Validation historical failures;
- two entry-baseline remote-sync failures because local `HEAD` is the accepted `c690e2a…` baseline while unpushed `origin/main` remains `667708f…`.

The two remote-sync gates existed at Phase 2.5 entry and conflict with neither the revised Phase 2.5 baseline rule nor the annotated tag. Phase 2.5 did not push, mutate `origin/main`, or weaken those tests.

`KNOWN_FAILURES = 3`

`BASELINE_REMOTE_SYNC_FAILURES = 2`

`NEW_FAILURES = 0`
