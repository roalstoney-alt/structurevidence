# SE Open Challenge — public research challenge area v0.1
Status: PROPOSED FOR PHASE B; no production launch authorized.
Purpose: Invite falsifiable, attributable challenges from peers and specialist readers without allowing any submitter to purchase, automatically influence or overwrite an evidence state.

## Surface
Place a **Challenge the evidence** entry in the research section of structurevidence.org, with contextual “Challenge this row” links in the 800VDC Source Dependency View and gap/case pages. Keep commercial .com separate. Do not hide challenges merely because they disagree with SE.

## Submission types
1. SOURCE_DEPENDENCY: challenge authorship, independence, derivative lineage or relationship classification.
2. EVIDENCE_LEVEL: challenge E0–E5 classification or missing conditions.
3. QUALIFICATION_RULE: challenge specific gap acceptance or identity test.
4. MISSING_COUNTEREVIDENCE: provide an alternative or contradictory source.
5. TEMPORAL_ERROR: claim an event/cutoff/supersession error.
6. OTHER_REPRODUCIBLE_METHOD_ERROR.

## Minimal schema
challenge_id, target_type, target_id, case_id, gap_id (nullable), specific_contested_statement, proposed_correction, rationale, supporting_urls, source_capture_optional, submitted_at, method_version, status, moderator_event_ids, parent_challenge_id, public_privacy_consent. Require stable target links and URL provenance; evidence absence remains UNKNOWN, not false. Do not require public real-name disclosure; optional pseudonym, expertise statement explicitly UNVERIFIED. Disallow credentials, private patient/child data, contracts, personal contacts and file uploads by default. Rate-limit; anti-spam and moderation; consent notice; contact verification optional private, never display emails.

## Lifecycle
SUBMITTED_PRIVATE -> TRIAGED -> (PUBLIC_ACCEPTED | NEEDS_CLARIFICATION | REJECTED_WITH_REASON) -> UNDER_REVIEW -> (CONFIRMED | NOT_ESTABLISHED | INCORRECT | OUT_OF_SCOPE) -> CLOSED. Each event append-only with timestamp, reason and version. Public moderation rejection statistics can be published only with complete denominators and defined scope. No auto-promotion of evidence or case state. Distinguish submitted critique from independently verified evidence.

## UI
Public index: challenged issue, target stable ID, date, submitted claim, cited URLs, review state, decision memo, appended amendments. Show disagreements and limitations. Clearly label unreviewed user submissions and confidential/redacted content. Cases link to the review; changed classification points at predecessor row and challenge. Accessible keyboard/mobile and EN / zh-CN / ES where existing locale policy requires.

## Gates
Before opening external endpoint: security/privacy review, bounded schema, input escaping, URL restrictions, rate limit, bot resistance, retention/deletion policy, anti-abuse moderation workflow, no arbitrary public HTML execution, production smoke; human authorization required. If no secure backend is ready, ship only a clearly marked nonfunctional proposal or existing approved intake link, not a fake working submit button.

## Acceptance
Tests for row/gap reference integrity, duplicate challenges, idempotency, invalid URLs, injection, rate limits, pending claims mistakenly shown as established, private-field leaks, moderation permissions, append-only revisions, evidence hashes and preserved baseline. Separate engineering readiness from second-review availability. Open PR for human review; do not auto-merge or deploy.
