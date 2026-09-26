# SE-FRR Telemetry v0.1

The product emits only the following event names: `STATE_LIST_VIEW`, `STATE_VIEW`, `CHANGE_VIEW`, `EVIDENCE_OPEN`, `HISTORY_VIEW`, `AS_OF_QUERY`, `BRANCH_VIEW`, `REQUEST_START`, `REQUEST_SUBMIT`, `CHALLENGE_START`, `CHALLENGE_SUBMIT`, and `FOUNDING_WAITLIST_SUBMIT`.

Allowed dimensions are route and public object identifiers (`subject_id`, `state_id`, `change_id`). The endpoint rejects unexpected fields. Evidence text, customer questions, decision context, names, email addresses, source URLs, and form values are never telemetry payloads.

These events make the requested future rates derivable without optimizing them in Phase 3. Worker logs are operational telemetry only; customer submissions remain in the protected customer plane.
