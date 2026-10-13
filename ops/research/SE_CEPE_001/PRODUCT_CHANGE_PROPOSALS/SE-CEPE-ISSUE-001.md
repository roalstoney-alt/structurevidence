# Proposed pilot-runner fix — SE-CEPE-ISSUE-001

STATUS = `HUMAN_REVIEW_REQUIRED`

The existing runner records availability and a retrieval hash but does not
compare that hash with the prior successful observation. On 2026-10-13 this
allowed two changed WHO page versions to receive an automatic
`NO_MATERIAL_CHANGE` label before the mandatory postcheck caught the deltas.

## Smallest proposed fix

For each task with an `AVAILABLE` result:

1. locate the latest earlier successful observation for the same task;
2. compare the prior and current `source_content_sha256` values;
3. retain `NO_MATERIAL_CHANGE` only when the hashes match;
4. emit `INTERPRETATION_REVIEW_REQUIRED` when they differ;
5. never infer a claim-state transition from a byte-level change;
6. retain failed attempts and existing fallback behavior.

No production, public case, frozen Gold or publication behavior changes. The
proposal is not implemented until the human gate is approved.

APPROVAL_GATE = `HUMAN_REVIEW_REQUIRED`
