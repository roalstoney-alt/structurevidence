# SE-CEPE-001 run audit notes

## `SE-CEPE-CTRL-20261011-001`

DISPOSITION = `INVALIDATED_FOR_ACTIVATION_EVIDENCE`

The first uncommitted controlled run is retained for append-only audit. It
identified an AP HTTP 403 and correctly recorded that task observation as
`SOURCE_UNAVAILABLE`, but the run summary incorrectly counted that status as a
completed check. Its supplied `started_at` was also 48 seconds later than the
local `finished_at`, so it is not valid evidence of T0.

The runner was corrected to:

1. count `SOURCE_UNAVAILABLE` as an operational exception;
2. try only the task's already-registered fallback sources, in order;
3. retain each attempted URL and result; and
4. preserve this original run rather than silently rewriting it.

The next controlled run, if internally consistent and logged, is the only run
eligible to establish T0 and scheduler verification.

## `SE-CEPE-20261012T090153Z`

DISPOSITION = `ACCEPTED_BOUNDED_NO_CHANGE_RUN`

The scheduled runner completed checks for all eight registered tasks. Every
task retained `NO_MATERIAL_CHANGE` within the documented primary-source
availability and retrieval-hash scope; this is not a semantic conclusion that
nothing changed outside that scope. `MATERIAL_EVENT_COUNT = 0` and no content
draft was created.

For `SE-TECP-007`, AP and TASS returned HTTP 403. The runner preserved both
failed attempts as `SOURCE_UNAVAILABLE`, then used the already-registered WHO
fallback successfully. The bounded task check therefore completed; the failed
attempts were not erased or represented as successful retrievals.

Post-run verification passed:

- `scripts/test_se_cepe_001.py`: 12/12
- `scripts/test_se_ai_data_001.py`: 7/7
- `scripts/test_se_ai_data_001_observation_v02.py`: 10/10
- `scripts/test_case_watch.py`: 5/5
- `scripts/test_irkutsk_publication.py`: PASS
- `scripts/test_irkutsk_alias_repair.py`: PASS

Frozen Gold, claim hashes, protected snapshots, publication/outreach kill
switches, `GTM005 = HOLD`, `GTM002 v0.4 = STOP_AND_RETAIN_RESULT`, and the
Trust Boundary campaign inputs remain unchanged.

## `SE-CEPE-20261013T090308Z`

DISPOSITION = `HUMAN_REVIEW_REQUIRED_AFTER_POSTCHECK`

The scheduled runner completed 8/8 availability checks and wrote its original
append-only records. A required post-run comparison then found changed WHO page
hashes for `SE-TECP-007` and `SE-TECP-008` relative to the prior successful
run. WHO response headers reported `Last-Modified` values on 2026-10-12 after
the prior observation. Immediate repeat retrievals reproduced both new hashes.

The runner-generated `NO_MATERIAL_CHANGE` records and automatic report are
retained as history, but they are not accepted as the final disposition for
those two tasks. The supplemental run
`SE-CEPE-20261013T090308Z-POSTCHECK` appends two
`INTERPRETATION_REVIEW_REQUIRED` observations and a human-review report.

No frozen Gold, claim, case state or historical cutoff was changed. Existing X
and Zhihu drafts remain unsent and are held pending the semantic review.

Post-run verification passed:

- `scripts/test_se_cepe_001.py`: 12/12
- `scripts/test_se_ai_data_001.py`: 7/7
- `scripts/test_se_ai_data_001_observation_v02.py`: 10/10
- `scripts/test_case_watch.py`: 5/5
- `scripts/test_irkutsk_publication.py`: PASS
- `scripts/test_irkutsk_alias_repair.py`: PASS

## `SE-CEPE-20261014T090033Z`

DISPOSITION = `ACCEPTED_WITH_EXISTING_HUMAN_REVIEW_OPEN`

The scheduled runner completed 8/8 availability checks with no operational
failures. Its postcheck found another source-byte and `Last-Modified` change
for `SE-TECP-007`. Bounded review of the current WHO page found no new
claim-bearing statement beyond the evidence already queued on 2026-10-13.
Because the exact previous response body was not archived, the supplemental
record remains `INTERPRETATION_REVIEW_REQUIRED`; it does not make a new state
recommendation or close the existing human review.

Post-run verification passed:

- `scripts/test_se_cepe_001.py`: 12/12
- `scripts/test_se_ai_data_001.py`: 7/7
- `scripts/test_se_ai_data_001_observation_v02.py`: 10/10
- `scripts/test_case_watch.py`: 5/5
- `scripts/test_irkutsk_publication.py`: PASS
- `scripts/test_irkutsk_alias_repair.py`: PASS

Frozen Gold, claim hashes, source manifests, protected snapshots, publication
and outreach gates, GTM holds, and Trust Boundary inputs remain unchanged.
