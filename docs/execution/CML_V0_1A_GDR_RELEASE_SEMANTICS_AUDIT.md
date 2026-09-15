# CML v0.1a GDR Release Semantics Audit

The shared GDR-SE CML adapter remains the only release veto layer. Public release now hard-blocks missing primary evidence, a failed private boundary, superseded records, event-invalidated freshness, material correction review, missing counter-evidence and unverified drop-in claims.

`POLICY_NOT_CONFIGURED` and `INSUFFICIENT_DATA` may be published only as `PUBLIC_TECHNICAL_RECORD` Method Pilot material with explicit limitations. They do not authorize paid decision delivery. All current CML Method Pilot records retain `paid_delivery = BLOCK`.

Negative fixtures cover event invalidation, review state, unconfigured policy, material correction, missing counter-evidence, critical unknowns, incomplete qualification, supersession, distributor-only lifecycle evidence, prohibited private fields and unsupported drop-in claims.
