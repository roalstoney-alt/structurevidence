# L1 CML-PDRE-001 Field Deployment Verification

`RESEARCH_ID = L1-CML-PDRE-001-FIELD-DEPLOYMENT-VERIFY`

`STATUS = CLOSED_AND_FROZEN`

`ENTRY_SHA = 356e5baf38363af69ad22841523cae8e5f76734b`

## Result

`RESULT = QUALIFYING_FIELD_DEPLOYMENT_EVIDENCE_FOUND`

`STOP_REASON = QUALIFYING_RECORD_FOUND`

The bounded L1 search found a dated operator publication stating that an SST-based intelligent DC power system entered commercial operation at Chindata's Sangyuan Cloud Computing Campus near Beijing. The source describes a 10kV utility-AC-to-800VDC architecture and reports entry into commercial operation after 34 performance and safety validation tests.

Human CML review accepted this as `ARCHITECTURE_FIELD_DEPLOYED_SINGLE_DEPLOYMENT_EVIDENCE`. It does not establish industry-wide deployment, full PDRE validation, or R5 in the canonical case; the canonical transition remains `CML_TRANSITION_PENDING_EXISTING_GOVERNANCE`.

Source: [Chindata operator publication](https://www.chindatagroup.com/media/news/533.html), published 2026-07-02.

## Boundary and timing

- `EVENT_TIME = 2026-07-02`
- `KNOWLEDGE_TIME = 2026-09-20T10:46:47Z`
- `DECISION_BEFORE = R5_FIELD_DEPLOYED_NOT_ESTABLISHED`
- `HUMAN_CML_REVIEW = ACCEPT`
- `DECISION_AFTER = R5_ARCHITECTURE_FIELD_DEPLOYMENT_EVIDENCE_ACCEPTED_SINGLE_INSTANCE`
- `CANONICAL_CML_STATE_CHANGED = NO`
- `PDRE_FULL_VALIDATION = NO`
- `SEARCH_QUERIES = 4/8`
- `DEEP_SOURCE_REVIEWS = 1/5`
- `SOURCES_CHECKED = 9`
- `SOURCES_USED = 1`
- `SOURCES_REJECTED = 8`
- `DUPLICATES = 0`

Rejected apparent deployment claims are preserved in the source-classification artifact with explicit reasons including planned deployment, lab-only demonstration, product announcement, and absence of operational evidence.

## Cost observation

- `CREDIT_BALANCE_BEFORE = 384`
- `CREDIT_BALANCE_AFTER = 347`
- `ACCOUNT_CREDIT_DELTA = 37`
- `MEASUREMENT_STATUS = OBSERVED`
- `MEASUREMENT_SOURCE = HUMAN_CHATGPT_USAGE_SCREENSHOTS`
- `ATTRIBUTION_CONFIDENCE = HIGH`
- `TOKEN_USAGE = UNKNOWN`

The credit delta is an observed account-level balance change across the isolated L1 execution window. It is not claimed as billing-ledger-level exact attribution and is not converted to USD.

No L2, L3, Candidate 001, Candidate 005, or Phase 3 activity was performed.

## Validation

- `L1_TARGETED_TESTS = 11/11 PASS`
- `HUMAN_REVIEW_FREEZE_TESTS = 9/9 PASS`
- `RDL_SCHEMA_VALIDATION = PASS`
- `CML_V11_TRANSITION = 10/10 PASS`
- `CML_REGRESSION_HARNESS = 6/6 PASS`
- `FULL_TEST_RESULTS = 231 RUN; 228 PASS`
- `KNOWN_FAILURES = 3`
- `NEW_FAILURES = 0`
- `OLD_RECORD_MUTATION_COUNT = 0`
- `COMMIT = NOT_PERFORMED`
