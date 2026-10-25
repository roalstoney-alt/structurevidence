# Decision Boundary Pilot protocol v0.1

This protocol measures review work without converting an evidence boundary into a customer recommendation. It does not change evidence, case state, source qualification, pricing, or any public Decision Condition.

## Append-only ledger

Every event has an increasing `sequence`, the SHA-256 of the prior event, and its own canonical SHA-256. Corrections append `SUPERSEDED` plus a replacement event. They never delete or rewrite the earlier event. Exact replays are idempotent; conflicting reuse of an `event_id` is rejected.

Supported event types are `BASELINE_FROZEN`, `REVIEW_STARTED`, `EVIDENCE_ADDED`, `EVIDENCE_REJECTED`, `CHALLENGE_RECEIVED`, `RULE_CHECKED`, `STOP_POINT_EMITTED`, `CLIENT_DECISION_RECORDED`, `OUTCOME_OBSERVED`, and `SUPERSEDED`.

`CLIENT_DECISION_RECORDED` is permitted only for a real independently authorized pilot and only when the decision is client supplied. `OUTCOME_OBSERVED` requires an independently observed, scope-permitted outcome. Neither event exists in the public fixture.

## Authorization and privacy

Until written opt-in and independent human scope approval exist, the only allowed mode is `PUBLIC_ILLUSTRATION_NOT_CUSTOMER_PILOT` with `PUBLIC_TEST_FIXTURE_ONLY` data. Real customer data belongs in private storage and must never be emitted by the public fixture/report builder. D1 identifiers, names, organizations, contact fields, private owners and internal case identifiers are forbidden in public records.

Enrollment, outreach, billing, retention changes, production writes and deployment each require separate authorization. This repository protocol grants none of them.

## Measurement boundary

The fixed work-unit vocabulary records researcher minutes, reviewer-touch minutes, source-acquisition cost in minor currency units, review rounds, new qualifying sources, clarifications, challenges, Decision Condition citations, and append-only revisions/supersessions.

The deterministic fixture includes synthetic baseline arithmetic to test aggregation. Its public comparison remains `INSUFFICIENT_DATA`: no fixture value is an observed customer result, causal estimate, saving, avoided-loss estimate, or ROI claim. A real comparison would require an actual comparable baseline and after-measurement, client authorization, permitted outcome observation, and separate causal analysis.
