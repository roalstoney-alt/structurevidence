# SE-FRR-001 Clean Baseline Test Report

Date: 2026-09-25  
Audited baseline SHA: `2356c9327ba5b40995435eca952edd706fd944fc`  
Branch: `feat/se-frr-001`  
Worktree: `/Users/roal/Documents/ChatGPT/structurevidence-se-frr`

## Dirty versus clean comparison

| Check | Preserved original checkout | Clean SE-FRR baseline before remediation |
|---|---:|---:|
| Python tests discovered | 269 | 256 |
| Python passed | 253 | 240 |
| Python failed | 14 | 14 |
| Python errors | 2 | 2 |
| Worker tests | 14/14 pass | 13/13 pass |
| Wrangler dry-run | Pass with sandbox log warning | Pass with explicit writable log path |

The 13 additional Python tests in the original checkout came from the untracked `scripts/test_cml_fde_v3.py` and were correctly excluded from the scoped clean branch. The additional Worker test came from the preserved uncommitted `/admin` work and was also correctly excluded.

The clean worktree removed the dirty Worker files from the RDL clean-tree failure. The remaining clean failures reproduced tracked baseline/history issues and were classified independently.

## Remediation performed

1. Created a narrow, hash-bound formal supersession for the two historically protected files whose later commercial/contact states are enforced by accepted tests.
2. Updated the preservation helper to validate that supersession record and reject any unrecorded path or hash.
3. Added an explicit PDRE container-evolution record for the human-authorized `publication-control.json` lifecycle artifact.
4. Updated the PDRE initialization test to preserve initialization invariants while validating the later publication control separately.
5. Left three historical Opportunity Validation runners unchanged because repository decision records explicitly identify their current-HEAD assumptions as milestone-era limitations.
6. Deferred `jsonschema.RefResolver` migration as `TECH_DEBT_SE_001`.

## Final Python result

Command:

```text
python3 -m unittest discover -s scripts -p 'test_*.py'
```

Expected classified result after committing Phase 0.5 artifacts:

```text
258 tests
255 pass
2 fail
1 error
```

The three non-passing tests are `B-001`, `B-002`, and `B-003`: frozen Opportunity Validation runners with known milestone-era current-HEAD assumptions. They have zero unexplained divergence and formal dispositions in `SE_FRR_BASELINE_FAILURE_CLASSIFICATION.md`.

## Worker result

```text
13 tests
13 pass
0 fail
```

The suite used the bundled Node.js runtime and dependencies restored from the committed lockfile.

## Wrangler result

```text
PASS — dry-run only; no deployment
Total Upload: 116.95 KiB / gzip: 29.84 KiB
```

Bindings resolved:

- `CUSTOMER_CASES_DB`
- `PUBLIC_INTAKE_RATE_LIMITER`
- `PUBLIC_ORIGINS`
- `TEAM_DOMAIN`

## Gate conclusion

- `WORKER_TESTS = PASS`
- `WRANGLER_DRY_RUN = PASS`
- `UNKNOWN_BASELINE_REGRESSIONS = 0`
- `PYTHON_TESTS = CLASSIFIED_HISTORICAL_EXCEPTIONS`

The three remaining historical test failures are accepted under the Phase 0.5 rule permitting intentional frozen-test failures only when each has a failure ID, cause, introducing commit, canonical state, and formal disposition.
