# Phase 2.5H Test Report

`STATUS = COMPLETE`

Targeted suite: `scripts/test_rdl_phase2_5h_allocation_freeze.py`.

The suite verifies six preserved candidates and decisions, human-decision counts, recommendation preservation, Candidate 001 L0 rescope, Candidate 005 four-part decomposition, exactly one Candidate 002 authorization, no research execution, L0-only RDL actions, authorization boundaries, RDL schema/hash integrity, historical immutability, and absence of new opaque scores.

## Results

- Phase 2.5H allocation freeze: `15/15 PASS`
- Phase 2.5 allocation: `17/17 PASS`
- Phase 1 RDL: `24/24 PASS`
- Phase 2 RDL: `16/16 PASS`
- CML transition regression: `10/10 PASS`
- CML regression harness: `6/6 PASS`
- CML core, observation, final audit, pilot initialization, and EVP ingestion: `72/72 PASS`
- RDL freshness checks: `4/4 PASS`
- Full repository discovery: `211 RUN; 208 PASS; 3 KNOWN FAILURES; 0 NEW FAILURES`

The three known failures remain confined to the pre-existing Opportunity Validation Phase A, Phase B, and Phase B-R1 baseline-integrity assumptions. No test or historical record was modified to mask them.
