# SE-FRR-001 Baseline Failure Classification

Date: 2026-09-25  
Audited baseline: `2356c9327ba5b40995435eca952edd706fd944fc`  
Clean branch: `feat/se-frr-001`

## Classification totals

The Phase 0 dirty run and Phase 0.5 clean comparison identified 17 distinct failing test outcomes requiring classification.

| Class | Count | Final disposition |
|---|---:|---|
| A — Dirty-worktree contamination | 1 | Eliminated by the clean worktree; no code change. |
| B — Stale frozen expectation | 5 | Two PDRE expectations remediated with an explicit container-evolution record; three Opportunity Validation current-HEAD assumptions retained and formally accepted as historical-runner limitations. |
| C — Actual baseline integrity regression | 11 | Root cause was two protected files. Formally superseded with a narrow hash-bound record; no unexplained mutation remains. |
| D — Tooling/environment test failure | 0 | Environment issues were resolved or recorded as non-failing technical debt. |

## Class A — Dirty-worktree contamination

### `A-001`

- Failure: `test_rdl_phase2_5_allocation.Phase25AllocationTests.test_q_no_tracked_historical_mutation`
- Dirty-only cause: uncommitted `deploy/cloudflare-landing/worker.js` and `deploy/cloudflare-landing/test/intake.test.js`.
- Clean result: the Worker paths disappeared from the failure.
- Introducing commit: not applicable; the changes were uncommitted in the preserved original checkout.
- Canonical state: audited Git baseline `2356c9327ba5b40995435eca952edd706fd944fc`.
- Formal disposition: `NO_CODE_CHANGE`; isolate SE-FRR in the clean worktree.

## Class B — Stale frozen expectations

### `B-001` — Phase A history cardinality

- Failure: `test_cml_ov_phase_a.PhaseATests.test_four_initializations_and_package`.
- Baseline reference SHA: `19be538447a90672491768d818fa07e3dd3dd377`.
- Current SHA at triage: `2356c9327ba5b40995435eca952edd706fd944fc`.
- First divergent commit: `b0459b2b945c78ae650a7e0a6db5b8f206857a46` (`Add CML Opportunity Validation Wave 1 evidence`).
- Changed input: append-only `technical-risk/CML_VERSION_HISTORY.jsonl` gained later valid entries.
- Declared decision record: `technical-risk/cml-v1.1/METHOD_TRANSITION.json` and `docs/execution/CML_V1_1_METHOD_TRANSITION_REPORT.md` preserve Phase A as a historical branch and explicitly document milestone-era current-HEAD assumptions.
- Cause: the historical runner requires exactly one post-baseline history entry instead of accepting later append-only history.
- Canonical state: later history entries are valid and append-only; the Phase A artifacts remain hash-bound.
- Formal disposition: `INTENTIONAL_HISTORICAL_TEST_FAILURE`; do not rewrite the frozen Phase A validator.

### `B-002` — Phase B whole-repository baseline assumption

- Failure: `test_cml_ov_phase_b.PhaseBTests.test_positive_packages_and_substantive_gaps` at `OV-B01_BASELINE_INTEGRITY`.
- Baseline reference SHA: `ad3206fff3c8d8375b1c9e087df44bd9c7336927`.
- Current SHA at triage: `2356c9327ba5b40995435eca952edd706fd944fc`.
- First divergent commit: `b0459b2b945c78ae650a7e0a6db5b8f206857a46` (`Add CML Opportunity Validation Wave 1 evidence`).
- Changed files: the validator treats every tracked file added or changed after the Phase A baseline as a violation, including its own authorized Wave 1 successor artifacts and all later repository development.
- Declared decision record: `docs/architecture/CML_OPPORTUNITY_VALIDATION_PHASE_B_WAVE1_v0.1.md`, `docs/execution/CML_OV_PHASE_B_WAVE1_REVIEW.md`, and the later CML v1.1 method-transition records.
- Cause: milestone-era `git diff BASE..HEAD` assumption, not artifact corruption.
- Canonical state: Wave 1 and later method versions are tracked successors; historical preservation is checked by hash/base-snapshot comparison.
- Formal disposition: `INTENTIONAL_HISTORICAL_TEST_FAILURE`; do not bulk-reset the historical validator.

### `B-003` — Phase B-R1 whole-repository baseline assumption

- Failure: `test_cml_ov_phase_b_r1.PhaseBR1Tests.test_positive_targets` at `OV-R101_ACCEPTED_WAVE1_BASELINE`.
- Baseline reference SHA: `b0459b2b945c78ae650a7e0a6db5b8f206857a46`.
- Current SHA at triage: `2356c9327ba5b40995435eca952edd706fd944fc`.
- First divergent commit: `f2cb555aa773b788bd5268276d4adf054a1b5b25` (`Add CML Opportunity Validation Phase B-R1`).
- Changed files: the validator rejects every tracked change after Wave 1, including its own Phase B-R1 artifacts and later CML v1.1 work.
- Declared decision record: `docs/architecture/CML_OPPORTUNITY_VALIDATION_PHASE_B_R1_v0.1.md`, `docs/execution/CML_OV_PHASE_B_R1_REVIEW.md`, and the CML v1.1 method-transition records.
- Cause: milestone-era whole-repository current-HEAD assumption.
- Canonical state: B-R1 is preserved as a historical method branch; later additions are valid successors.
- Formal disposition: `INTENTIONAL_HISTORICAL_TEST_FAILURE`; do not modify the frozen validator merely to turn it green.

### `B-004` and `B-005` — PDRE container evolution

- Failures: `test_expected_container_files_exist` and `test_no_url_or_external_source_was_added` in `test_cml_pdre_001_init`.
- Old expectation: the initialization container had seven files and no URLs.
- Current repository state: `publication-control.json` is an eighth, later lifecycle artifact with an approved public URL.
- Introducing commit: `8e82a910211fb19bb1dd3daca95764c76150bdef` (`chore(cml): add 800V public projection approval record`).
- Artifact hash: `1e4d4f3684c09f8759ee128adecb602491e9ec78054db47a2c69693e45cb5e5b`.
- Rationale: the artifact is an explicit human publication-control decision; it states that full PDRE validation is false and that historical research/evidence was not mutated.
- Decision: `FORMALLY_SUPERSEDE_CONTAINER_EXPECTATION` in `technical-risk/cml-v1.1/history/PDRE_001_CONTAINER_EVOLUTION.json`.
- Test disposition: preserve the no-URL/no-external-source invariant for the seven initialization files and separately validate the later publication-control boundary.

## Class C — Actual baseline integrity regression

Eleven tests independently surfaced the same two-file mutation:

- `test_cml_v11_regression_harness.test_current_head_passes_v11_2_milestone_regression`
- `test_cml_v11_final.test_all_25_independent_gates_pass`
- `test_cml_v11_final.test_frozen_gate_artifact_matches_live_evaluation`
- `test_cml_v11_regression_harness.test_current_head_descends_from_accepted_v11_2_without_breaking_v11_1`
- `test_cml_v11_transition.test_current_historical_files_are_preserved`
- `test_rdl_l1_field_deployment.test_k_historical_preservation`
- `test_rdl_l1_human_review_freeze.test_i_old_record_mutation_count_is_zero`
- `test_rdl_phase2_5_allocation.test_q_no_tracked_historical_mutation`
- `test_rdl_phase2_5h_allocation_freeze.test_o_historical_cml_rtp_ecn_gdr_are_unchanged`
- `test_rdl_phase2_cml_pdre_001.test_g_tracked_historical_scopes_are_unchanged`
- `test_rdl_research_record.test_existing_cml_historical_files_remain_unchanged`

### `scripts/publish_cml_v01.py`

- Frozen baseline SHA: `a1bb8e442316c48acb0af2aca0c8c269b00340af`.
- Frozen hash: `e04e710c68a3d56a6d294cbffa64f28c4e08a2c901dc3d528558ad943669d55a`.
- Current accepted hash: `7a6d473ef4c1bbff64ed277065b008ff3d59453c73cd34292bdaac871609813c`.
- First divergent commit: `a0baa74cd28175470ae35782c21548878e558a47`.
- Later modifying commits: `007d784f09d014c3c795ffd784baef67bf0acad7`, `a59b5b65d7ef2c8ec799004dda46fdfc509bec19`.
- Change: brand/contact/commercial copy; no scientific result or research state change.

### `technical-risk/request-analysis/index.html`

- Frozen baseline SHA: `a1bb8e442316c48acb0af2aca0c8c269b00340af`.
- Frozen hash: `efb42167281cde9c156e97b34e3978c1b4f156b25ef970805bfcdaaa04f99ffd`.
- Current accepted hash: `3045ffdf674dcab7ad7cd8f55a593ed1d48d92d4b6facd537ef822e2a4c05059`.
- First divergent commit: `a0baa74cd28175470ae35782c21548878e558a47`.
- Later modifying commit: `007d784f09d014c3c795ffd784baef67bf0acad7`.
- Change: public contact identity; later commercial and customer-intake tests require the successor state.

Restoring the old bytes was tested and rejected because it caused accepted commercial-domain, customer-intake, and contact-consistency guards to fail. The final disposition is `FORMALLY_SUPERSEDE_BASELINE`, recorded in `technical-risk/cml-v1.1/history/HISTORICAL_FILE_SUPERSESSIONS.json`. The preservation helper now permits only the two named successor files when their baseline hashes, successor hashes, and introducing-commit ancestry all match. All other historical files remain byte-frozen.

## Class D — Tooling and environment

No application test failure remains classified as environmental.

- Missing system `node`: resolved by using the Codex bundled Node.js runtime.
- Missing clean-worktree dependencies: resolved from the lockfile; no package version was changed.
- Wrangler debug-log permission: resolved by setting `WRANGLER_LOG_PATH=/tmp/se-frr-wrangler.log`; dry-run passed and no deployment occurred.
- `jsonschema.RefResolver` deprecation: recorded as `TECH_DEBT_SE_001`; non-blocking and not remediated in Phase 0.5.
- Shell `.zprofile` references missing `/opt/homebrew/bin/brew`: warning only; commands and tests execute.

## Final classification gate

`UNKNOWN_BASELINE_REGRESSIONS = 0`

Every failing baseline outcome has a cause, introducing commit or dirty-worktree source, canonical-state decision, and formal disposition.
