# Observation bulletin publication gate

Development authorized 2026-11-26. Production merge/deployment remains HUMAN_GATE_REQUIRED.

This is a separate public projection, not a case-state mutation or material-change feed.
The existing daily task may propose append-only candidate records; it must not create a new timer,
auto-approve, merge, deploy, or publish social posts.

Only owner-reviewed, privacy-safe summaries enter observations/feed.json with publication_status APPROVED.
Required fields: observation_id, case_id, observed_on, type (OBSERVATION/OPEN_GAP/HUMAN_REVIEW_PENDING),
summary, boundary, case_url, event_on (original date or null), source_urls, knowledge_cutoff,
approval_reference, approved_at, content_sha256. Approval and content hash must be checked before merge.
Use immutable observation IDs and add later handling events rather than rewriting prior observations.

Every approved item must also be rendered as static HTML in observations/index.html for no-JS access,
search indexing and citation. Do not remove historical items when rotating the current selection.
Daily incomplete checks must say REVIEW_INCOMPLETE, not NO_NEW_EVIDENCE or NO_STATE_CHANGE.
Private intake/Admin access problems are internal observability limits, not public scientific gaps.
No customer identity, private intent, private files, sensitive Irkutsk details or medical advice may appear.

IREN: attributed issuer disclosures may be recorded without Microsoft reverse confirmation;
underlying fact acceptance remains HOLD_PENDING_REVIEW. Do not equate disclosure with independent verification.

Initial feed deliberately contains no approved items. Review exact candidate text separately.
Root and docs mirrors must match before deployment. Production body verification is separate from GitHub checks.
