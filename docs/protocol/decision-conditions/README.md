# Decision Conditions v0.1

This public protocol projects an already-reviewed evidence ledger into a citable condition. It does not create evidence, decide whether a claim is true, or select a client action.

The v0.1 package is deterministic. `record_sha256` seals each condition without its own hash field; `snapshot_sha256` seals the full package without its own hash field. Any evidence update must create a new version with `previous_snapshot_sha256` pointing to the frozen prior export.

`source_evidence_rule` answers only whether the cited source rows satisfy the declared rule. `client_action_condition` remains client-owned and `UNSPECIFIED` unless a client separately records it outside this public illustrative export.
