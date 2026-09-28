# Public evidence change and submission protocol

This page is an editorial operating note for `/changes/`, the three v0.1 stop-point projections, and `/cases/submit-evidence/`. It does not alter the underlying canonical research states.

## Fixed starting records

- CML-PDRE-001: one human-reviewed attributable field deployment, knowledge time 2026-09-20T10:46:47Z, frozen 2026-09-20T11:12:14Z; publication control 2026-09-23. Canonical migration readiness was not changed.
- SE-BESS-SODIUM-001: public state v0.1 and Decision Memory, knowledge cutoff 2026-09-24. Named commissioned customer site NOT_ESTABLISHED, not disproved or absent everywhere.
- SE-ONC-NSQNSCLC-CN-001: public research preview v0.1, knowledge cutoff 2026-09-28, clinical interpretation review PENDING, hospital outcome dataset NOT_ACQUIRED, patient-specific forecast stopped.

Each `stop-v0.1.html` is an immutable **derived public summary**. The case page may point to the latest approved version in the future, but this version's claim, scope, dates, state, supports, does-not-support, and source references must not be silently changed. If a factual error is found, preserve a correction note and publish a new version. Do not mark a derived summary as a complete 5C1 canonical projection without the required source fields, verification gate, stable version, and review.

## New evidence cycle

1. Receive public URL or stable document identifier privately through the case-specific email template. Do not publish sender details or raw messages automatically. The mailto action opens a user's email client; there is no website receipt ID or server-side submission.
2. Human reviewer records case ID, atomic claim, source identity, event time, publication time, knowledge time, access status, dependence, and search scope. A source behind a paywall or access restriction remains classified as such; do not present it as reviewed content.
3. Check whether the source qualifies for the exact statement. Preserve non-qualifying sources and reasons, and counter-evidence. `NOT_FOUND_WITHIN_SCOPE` requires a documented, completed bounded search. Non-response and failed search never prove nonexistence.
4. Human acceptance gate decides whether a state transition, correction, or no-change review is warranted. The submission itself authorizes no new research or direct inquiry. Separate written authorization is required for a direct source inquiry or any paid data collection.
5. Append a dated entry to `/changes/` with `WHAT_CHANGED`, `WHAT_DID_NOT_CHANGE`, source/provenance link, event and knowledge times, prior/current state, review decision, and next minimum evidence. Do not rewrite a previous entry. Update the case and create `stop-v0.2.html` (or later) only after source and publication review.
6. Mirror all public files under root and `docs/`, including sitemap entries, and verify both render the same version. Do not place customer-specific details, private submissions, or patient records in public artifacts.

## Publication checks

- Every copyable stop point shows claim, scope, cutoff, state, support and non-support together. Missing fields block copy.
- 800V single-instance evidence does not become industry adoption or a canonical readiness change.
- BESS `NOT_ESTABLISHED` does not become `NOT_FOUND_WITHIN_SCOPE` or a proof of absence.
- Medical trial-group estimates never become a patient-specific probability or a cross-modality ranking. The submission form rejects patient records by instruction and acknowledgement, but human moderation must still screen incoming mail.
- A newly accepted source appends a new version and change entry. Existing v0.1 records remain accessible.
