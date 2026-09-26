# SE API v1 Temporal Query Semantics

`GET /api/v1/subjects/{subject_id}/state?as_of=<RFC3339 timestamp>` reconstructs the latest canonical State for which both:

1. `observed_at <= as_of`; and
2. `recorded_at <= as_of`.

Ordering is by `recorded_at`, then stable `state_id`. If no State meets both boundaries, the API returns `404 STATE_NOT_FOUND_AT_BOUNDARY`.

`published_at` never determines historical visibility. A source published at T1, queried at T2, and first observed by StructEvidence at T3 is invisible at T2 when T1 < T2 < T3. A future `effective_at` likewise does not move knowledge backward. This prevents retrospective leakage while preserving the distinct publication, observation, recording, and effective clocks frozen in the temporal protocol.

Without `as_of`, the endpoint returns the latest recorded State and labels it `CURRENT_RECORDED_STATE_NOT_PREDICTION_RECOMMENDATION_OR_GUARANTEE`.
