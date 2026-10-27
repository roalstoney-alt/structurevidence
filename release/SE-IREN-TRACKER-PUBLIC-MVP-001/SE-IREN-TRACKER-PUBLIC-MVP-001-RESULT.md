# SE-IREN-TRACKER-PUBLIC-MVP-001 result

Result: `READY_FOR_HUMAN_PUBLICATION_REVIEW`.

The bounded release candidate is implemented in `codex/se-iren-tracker-public-mvp-001`. It contains an English public tracker route, public-safe JSON, a source registry, schema, append-only digest-chained event ledger, row-specific fixed-ID challenge links, root/docs mirrors, tests, screenshots, a human review sheet, and a draft editorial digest. Case-index and sitemap wiring are deliberately deferred because the existing history guard freezes those projection files and publication approval has not been given.

No publication, merge, production POST, Worker/D1 change, social output, or pilot start occurred.

## Evidence result

- Evidence cutoff: `2026-10-22`.
- Last source check: `2026-10-27T19:38:39Z`.
- Next scheduled check: `2026-11-05`, confirmed on the official IREN investor-news index.
- Captured and SHA-256 hashed official sources: 8.
- Retrieval incomplete or metadata-only: 4.
- Supported-as-attributed rows: 6.
- Not-established rows: 5.
- Human reviewer: unassigned; all rows `PENDING`.

The candidate corrects a material draft-classification risk: the reviewed 8-K releases/exhibits for the Microsoft agreement, Horizon 1, FY26 results, and July ARR update are explicitly treated as `furnished_not_filed`, not generically filed. D0–D4 remains proposed, unapproved, and unapplied.

## Verification result

The IREN adversarial suite passed 15/15 and the relevant repository history/SEO regressions passed 10/10. Local link integrity found 0 missing references. Desktop and mobile-breakpoint previews rendered successfully. Existing `.com` Verify and Decision Pack routes returned HTTP 200 through read-only HEAD requests. No POST was sent.

Full repository discovery passed 31/42. Its 11 failures come from a stale PR26 baseline manifest against eight untouched protected files, the pre-existing case-index projection hash, and two assertions exposing the pre-existing root/docs case-index mirror mismatch. No failed path is changed by this branch, so the new-regression count is zero; the stale manifest and mirror mismatch are still reported as release blockers rather than hidden or rewritten.

## Human gate

Publication is blocked until a legitimate reviewer signs every row and the owner approves the exact candidate source SHA, page/data digests, row list, cutoff, preview, and intended public URL. Any later content change invalidates that approval.

```text
PROJECT=SE-IREN-TRACKER-PUBLIC-MVP-001
FREEZE_MANIFEST_SHA256=TO_BE_RECORDED_AFTER_SHA256SUMS
FEATURE_BRANCH=codex/se-iren-tracker-public-mvp-001
HEAD_SHA=TO_BE_RECORDED_AFTER_FREEZE_COMMIT
TRACKER_DATA_VERSION=v0.1-rc1
EVIDENCE_CUTOFF=2026-10-22
LAST_SOURCE_CHECK=2026-10-27T19:38:39Z
NEXT_SOURCE_CHECK=2026-11-05
PRIMARY_SOURCES_VERIFIED=8
RETRIEVAL_INCOMPLETE=4
REVIEWER_STATUS=PENDING_HUMAN_REVIEW
FOUR_BLOCKS=PASS
ROW_PROVENANCE=PASS
ROW_CHALLENGE=PASS
APPEND_ONLY_HISTORY=PASS
EN_PUBLIC_ROUTE_PREVIEW=LOCAL_ONLY:http://127.0.0.1:8766/cases/iren-ai-cloud-transition/
ORG_CASE_INDEX=FAIL
SITEMAP_CANONICAL=FAIL
COM_READONLY_CTA=PASS
HISTORICAL_RECORD_DRIFT=PASS
TESTS=25/25_TARGETED; FULL_DISCOVERY=31/42_WITH_11_PREEXISTING; NEW_REGRESSION_COUNT=0
DRAFT_PR_URL=TO_BE_OPENED
OWNER_PUBLICATION_APPROVAL=NOT_GIVEN
ORG_PUBLISHED=NO
COM_WORKER_DEPLOY=NO
PRODUCTION_POST_COUNT_ADDED=0
SOCIAL_POST_SENT=0
PUBLIC_PILOT_STARTED=NO
BLOCKERS=HUMAN_ROW_REVIEW,COUNSEL_OR_ACCOUNTABLE_REVIEW,EXACT_SHA_OWNER_APPROVAL,FOUR_RETRIEVAL_LIMITATIONS,STALE_PR26_BASELINE_MANIFEST,PREEXISTING_CASE_INDEX_MIRROR_MISMATCH
```
