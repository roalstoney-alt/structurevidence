# Test Baseline

## Snapshot

- Commit: `667708fe624f78768d97480856c8e92725665ea5`
- `HEAD == origin/main`: yes
- Entry worktree: clean
- Python test files discovered under `scripts/`: 69
- Validator/validation runner files: 12

## Full discovery result

Command:

```text
python3 -B -m unittest discover -s scripts -p 'test_*.py'
```

Result:

```text
139 tests run
136 passed
2 failures
1 error
overall: FAIL
```

The failures existed at the audited committed snapshot; Phase 0 did not repair them.

## Failing baseline tests

| Test | Failure | Audit interpretation |
| --- | --- | --- |
| `test_cml_ov_phase_a.PhaseATests.test_four_initializations_and_package` | `ValueError: Phase A history entry` | Historical Phase A assumes a fixed history shape and is not future-append safe. |
| `test_cml_ov_phase_b.PhaseBTests.test_positive_packages_and_substantive_gaps` | `OV-B01_BASELINE_INTEGRITY` reports frozen tracked files changed | Milestone preservation logic compares later legitimate repository state against an earlier frozen assumption. |
| `test_cml_ov_phase_b_r1.PhaseBR1Tests.test_positive_targets` | `OV-R101_ACCEPTED_WAVE1_BASELINE` reports accepted baseline changed | The accepted Wave 1 test is not fully post-commit safe after later authorized method work. |

These are regression-harness defects or obsolete historical expectations, not evidence that Phase 0 changed historical files. The worktree was clean when the suite started.

## Focused current-method baseline

| Suite | Result |
| --- | --- |
| CML v1.1 transition | 10/10 PASS |
| CML v1.1 core | 15/15 PASS |
| CML v1.1 regression harness | 6/6 PASS |
| CML v1.1 observation | 16/16 PASS |
| CML v1.1 final audit | 3/3 PASS |
| CML-PDRE-001 initialization/lifecycle | 10/10 PASS |
| CML-PDRE-001 EVP-001 ingestion | 12/12 PASS |
| RDL freshness policy script | PASS |
| RDL freshness runtime script | PASS |
| RDL freshness validation script | PASS |
| RDL freshness/GDR integration script | PASS |

Current CML v1.1 plus pilot targeted tests total 72/72 passing.

## Warnings

`scripts/test_cml_v01.py` emits a deprecation warning for `jsonschema.RefResolver`. This is not a test failure but should be tracked as maintenance.

## Phase 1 coverage gaps

There are no tests for a canonical research record because no such schema/runtime exists. Phase 1 should add targeted tests for:

- Evidence Core reuse and hash integrity;
- L0/L1/L2/L3 authorization rules;
- required decision target and minimum missing evidence;
- before/after state preservation;
- `UNKNOWN` cost handling;
- append-only revisions and outcome links;
- duplicate/search-memory matching without false positives;
- failed/low-value research preservation;
- stop reasons and saturation observables;
- inventory/customer privacy separation;
- no opaque aggregate research-value score;
- historical CML/RDL/RTP/ECN preservation.

## Baseline gate

`CURRENT_CML_V1_1_AND_PILOT = PASS`

`RDL_FRESHNESS = PASS`

`FULL_REPOSITORY_DISCOVERY = FAIL_WITH_3_PRE_EXISTING_HISTORICAL_HARNESS_DEFECTS`
