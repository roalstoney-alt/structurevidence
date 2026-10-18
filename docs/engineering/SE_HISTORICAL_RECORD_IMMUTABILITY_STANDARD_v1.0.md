# SE Engineering Standard: Historical Record Immutability & Cross-Branch Evidence Reconciliation

**Standard ID:** `SE-ENG-HISTORY-001`  
**Version:** `1.0`  
**Effective:** 2026-10-18 (prospective controls; no retroactive rewriting)  
**Status:** `ACTIVE_ENGINEERING_STANDARD`  
**Applies to:** StructEvidence repository, Codex/agents, human operators, research reviews, claim/evidence events, decision memory, X candidate preparation, website releases and multi-branch contributions.

> **Historical records are immutable. New knowledge is appended, reconciled, and linked—not substituted.**

## 1. Rationale and scope

Git preserves file revisions, but does not prevent an older branch from replacing a more recent accepted observation or reusing a logical review identifier for a different review. The 2026-10-17 `SE-800V-REVIEW-20261017-01` collision between an already-published daily review and an unmerged Sungrow candidate is the motivating counterexample. This standard creates an explicit **logical evidence identity and provenance gate** beyond ordinary Git mergeability. The observed collision is not proof that the published review was wrong.

The canonical evidence history is append-only. Immutable facts, corrections, accepted states, and administrative projections are different classes of record. No automated executor may translate a newer retrieval or deployment time into an earlier source's publication/event date.

## 2. Record classes and permitted operations

| Class | Examples | Permitted actions |
|---|---|---|
| `IMMUTABLE_SOURCE` | Saved bounded snapshots, evidence/event records, source/search provenance | Create; later corrections **append a separate record** with lineage references. Never edit, delete, rename or replace original bytes. |
| `IMMUTABLE_REVIEW` | Versioned case reviews, run ledgers, daily report receipts, X candidates | Append new records; link to earlier review IDs and content hashes. Never overwrite earlier observations or reuse ID for materially different scope. |
| `FROZEN_DECISION` | Accepted state snapshots, human-reviewed decision records, EKN frozen v1.0 | Keep byte-identical; any reopening is a distinct authorized decision artifact, not a rewrite. |
| `REGENERABLE_PROJECTION` | `cases/index.html`, mirrored docs indexes, public review-status JSON, sitemap, event-list indexes, current-view pages | Rebuild from canonical source records with reproducible input commits and traceable IDs. Projection changes do **not** imply changed historical state. |
| `CODE_OR_SCHEMA` | Validators, rendering and workflow code | Editable with regression and impact checks; must not silently transform canonical historical bytes. |

Exact protected path patterns and the PR differential enforcement are implemented by `scripts/guard_history_immutability.py`; this table defines semantics beyond the current test coverage.

## 3. Stable identity and collision prevention

Every new substantive review has a unique `review_id` representing **one** bounded observation. `case_id`, `reviewed_at`, `search_boundary`, `sources_checked`, result, and reviewed record content establish its identity. A mirrored copy or a reference to the **same** observation may reuse its ID; a distinct search, source boundary, clock or conclusion **must** use a new ID.

On discovering an ID collision, STOP. Do not choose the newer branch solely because its Git commit is newer. Record both commit/blob hashes, file paths, retrieval and review times, source scopes and divergent fields, then append a reconciliation artifact with `conflicting_record_id`, `original_record_ref`, `candidate_record_ref`, `resolution`, `reviewer` and `reviewed_at`. The original bytes remain intact. A correction or superseding conclusion carries a **new identifier** plus `corrects`/`supersedes`/`derived_from` links and an explicit new human gate whenever the accepted stop would change.

The same rule applies to `event_id`, `candidate_id`, `run_id`, decision IDs and snapshot IDs: one identity, one logical event. Replayed identical content is idempotent; incompatible payloads are conflicts.

## 4. Branch integration protocol

1. Read the **latest main** commit and freeze its SHA before assessing a stale branch; inspect open/merged PRs and prior publication receipts. Never infer accepted facts from an unmerged PR.
2. Compare candidate records by `(identity, original path, byte SHA256, scope, clock, accepted state)` against current main, not merely against the original fork point.
3. For a diverged branch, create a **new integration branch from latest main** and selectively import nonconflicting new artifacts. Preserve the old PR and its exact SHA as provenance; do not blindly rebase or `checkout --theirs` over canonical history.
4. Add uniquely named supplemental review/correction and reconciliation records. Do not replace a previously published daily report or X candidate, even if later research is better.
5. Rebuild only derived indexes, root/docs mirrors and sitemaps. Verify protected-content digests, ID uniqueness, root/docs parity, and state cutoffs. No publication count may increase solely from an alias/mirror.
6. Review any accepted-state transition and any material public correction separately with `HUMAN_GATE_REQUIRED`.
7. Obtain GitHub checks/reviews, merge using normal branch policy and verify live body marker plus source hash. A successful Pages build alone is not a website verification receipt.
8. Store a release receipt with `BASE_SHA`, `HEAD_SHA`, `MERGE_SHA`, affected identities, content hashes, original-record-change count, production check, open gates and rollback information.

## 5. Time and evidence-state rules

Record distinct clocks: `published_at` (source publication), `event_at` (underlying event), `retrieved_at`/`first_observed_at` (first observation), `reviewed_at` (actual bounded check), `evidence_state_as_of` (accepted knowledge cutoff), and `deployed_at` (delivery). A newly discovered old publication is **not** a new event, independent verification or proof of a stop change. `NOT_FOUND_WITHIN_SCOPE` is not non-existence; a source-originator announcement is not independent issuer verification.

X candidates remain human-reviewed and website-first; an unpublished event has no permission to assert the public page is live. The daily candidate fallback may link only already verified pages, but **must not overwrite** the day's previous candidate; use a supplemental ID/record and preserve both. All automated X writes remain disabled unless separately authorized.

## 6. Change-control gate and existing debt

Pull requests that modify/delete/rename protected existing records **FAIL** the history guard. New records with a reused logical ID but divergent identity metadata also **FAIL**. Adding new records is permitted. CI is conservative; review all failures instead of suppressing tests. Historical collisions or already failing tests are logged as baseline debt, not silently renamed or excused. The PR guard does **not** validate the complete truth of every source and is not a substitute for human review; valid-looking malicious data, file-path classes not yet covered and semantic mismatch beyond selected identity fields remain residual risks.

When the gate is too narrow, update the guard **prospectively** through a reviewed PR; never weaken it as an incidental workaround for a blocked evidence merge. Exceptions for legally necessary redaction/erasure, secrets exposure or other higher legal obligations require separate human-controlled procedures with minimal public disclosure; do not publish confidential material to maintain append-only history.

## 7. Mandatory acceptance record

```text
SE_HISTORY_STANDARD = SE-ENG-HISTORY-001/v1.0
BASELINE_SHA = <frozen main>
REVIEW_ID_COLLISIONS_NEW = 0
IMMUTABLE_RECORD_MUTATIONS = 0
ORIGINAL_RECORDS_CHANGED = 0
NEW_RECORDS_APPENDED = <count>
RECONCILIATION_LINKS = <paths or NONE>
ACCEPTED_STOP_CHANGED = NO | HUMAN_APPROVED_RECORD
ROOT_DOCS_PARITY = PASS
PR_DIFF_HISTORY_GUARD = PASS
X_POST_SENT = 0 unless separately authorized
DEPLOYED_AND_VERIFIED = <observed result>
```

**Explicit non-goals:** This standard does not approve PR #26, change the 800V/Sodium/Irkutsk accepted stops, reopen EKN, launch new research, or authorize X publication.