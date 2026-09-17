# CML v1.1 Method Transition Report

ENTRY_SHA = `833fa342a34c3910a4ef415dd88b15888baf87bb`  
ACTIVE_METHOD = `CML_v1.1`  
HISTORICAL_BRANCH_STATUS = `PRESERVED; C0 DEPRECATED_AS_PRIMARY_RESEARCH_GATE ONLY`

## Milestone status

V11_1_STATUS = `PASS`  
V11_2_STATUS = `PASS`  
V11_3_STATUS = `PASS`  
REGRESSION_HARNESS_STATUS = `PASS; POST-COMMIT SAFE`

## Audit scope

FILES_AUDITED = `43 implementation and preservation inputs`  
SCHEMAS_AUDITED = `9`  
VOCABULARIES_AUDITED = `9`  
TEMPLATES_AUDITED = `9`  
VALIDATORS_AUDITED = `3 CML v1.1 validators`

OLD_RECORD_MUTATION_COUNT = `0`

The audit covered the method transition and registry, historical freeze policy, append-only version history, all CML v1.1 schemas/vocabularies/templates, Evidence Core references, validators, adversarial suites, commercial-boundary policy and architecture statement. Derived gate results and this report are excluded from the implementation-input count.

## Gate results

| Gate | Result |
|---|---|
| CML11-01 METHOD_TRANSITION | PASS |
| CML11-02 HISTORY_PRESERVED | PASS |
| CML11-03 NO_OLD_RECORD_MUTATION | PASS |
| CML11-04 PDRE_SCHEMA | PASS |
| CML11-05 DEPENDENCY_SCHEMA | PASS |
| CML11-06 CONSTRAINT_VOCABULARY | PASS |
| CML11-07 MIGRATION_READINESS | PASS |
| CML11-08 ADOPTION_FRICTION | PASS |
| CML11-09 READINESS_FRICTION_SEPARATION | PASS |
| CML11-10 STRUCTURAL_EXPOSURE | PASS |
| CML11-11 BENEFICIARY_MAP | PASS |
| CML11-12 EXPOSURE_BENEFICIARY_SEPARATION | PASS |
| CML11-13 TRIGGER_SCHEMA | PASS |
| CML11-14 REAL_WORLD_RESPONSE | PASS |
| CML11-15 MIGRATION_LAG | PASS |
| CML11-16 EVIDENCE_PRIORITY | PASS |
| CML11-17 PUBLIC_RESEARCH_OBJECT | PASS |
| CML11-18 REVISION_APPEND_ONLY | PASS |
| CML11-19 FAILURE_PRESERVATION | PASS |
| CML11-20 NON_ACCUSATORY_LANGUAGE | PASS |
| CML11-21 PUBLIC_PAID_BOUNDARY | PASS |
| CML11-22 BENEFICIARY_COMMERCIAL_PATH | PASS |
| CML11-23 NO_MANAGEMENT_INPUT_DEPENDENCY | PASS |
| CML11-24 NO_OPAQUE_SCORE | PASS |
| CML11-25 EVIDENCE_CORE_REUSE | PASS |

GATE_RESULTS = `25 PASS; 0 FAIL; 0 NOT_EVALUATED`

## Regression results

- V11-1 transition/history suite: 10/10 PASS.
- V11-2 semantic/adversarial suite: 15/15 PASS.
- Post-commit regression harness: 6/6 PASS.
- V11-3 observation/commercial-boundary suite: 16/16 PASS.
- Final audit consistency suite: PASS.
- Historical CML v0.1 frozen gate snapshot: 40/40 PASS; four mirrors byte-identical.
- Opportunity Validation, Phase B, Phase B-R1 and Phase C0: frozen artifact byte-preservation PASS across the historical protected-file set.
- Historical protected files: 174 checked; zero mutations.
- V11-2 frozen core artifacts: 11 checked; zero mutations.

## Known limitations

KNOWN_LIMITATIONS = `METHOD-LEVEL ACCEPTANCE ONLY; NO POPULATED PDRE HAS BEEN VALIDATED`

- No real PDRE candidate or empirical technology study has been executed; method acceptance is not validation of any market or technical hypothesis.
- No universal FAST/NORMAL/LATE migration-lag thresholds are configured. Records remain `POLICY_NOT_CONFIGURED` or `UNKNOWN` unless a separately authorized domain policy exists.
- Public PDRE source pointers and hashes are structurally required; byte-level comparison with a populated source PDRE occurs during record ingestion, not in an empty template audit.
- The shared Evidence Core remains deliberately domain-neutral; CML-specific semantic enforcement resides in the CML validators.
- The legacy CML v0.1 monolithic runner writes derived gate files and assumes its original release commit. Final preservation therefore verifies its frozen 40-gate snapshot and byte-identical mirrors instead of regenerating historical outputs.
- Historical Opportunity Validation runners also contain milestone-era current-HEAD assumptions. They remain frozen as method history; current preservation is established through base-snapshot byte comparison rather than modifying those historical validators.

## Unresolved items

UNRESOLVED_ITEMS = `FIRST PDRE PILOT, POPULATED CROSS-RECORD VERIFICATION, AND PRE-PUBLICATION HUMAN REVIEW`

- Select and authorize a first PDRE discovery pilot.
- Populate a public-evidence candidate record and exercise cross-record source-pointer verification with actual frozen inputs.
- Perform independent human review of the first populated PDRE before publication.

METHOD_ACCEPTANCE = `CML_V1_1_ACCEPTED`  
NEXT_AUTHORIZED_PHASE = `PDRE_DISCOVERY_PILOT`
