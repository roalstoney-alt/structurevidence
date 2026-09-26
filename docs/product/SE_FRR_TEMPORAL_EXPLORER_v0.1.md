# SE-FRR Temporal Explorer v0.1

The explorer calls:

```text
GET /api/v1/subjects/{subject_id}/state?as_of={RFC3339 boundary}
```

The API selects only a State whose `observed_at` and `recorded_at` are both at or before the boundary. The client separately labels evidence with later `observed_at` as excluded, even when `published_at` is earlier than the selected boundary.

The historical result is visibly distinct from the current State. A missing State at the boundary remains an explicit `STATE_NOT_FOUND_AT_BOUNDARY` condition. No current record is used as a fallback.

State comparison is semantic rather than a generic JSON diff. It reports State code, accepted Evidence added, counter Evidence added, unknowns resolved/added, and Branch changes.
