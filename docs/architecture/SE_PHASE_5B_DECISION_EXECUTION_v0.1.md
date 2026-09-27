# Phase 5B Decision Execution Plane v0.1

Phase 5B adds a public Decision Inventory to the 800V structural-event projection and a separate protected execution plane for paid gap verification.

## Boundary

The public route exposes recorded states, counts, reason text, the evidence cutoff, and a non-aggressive verification path. Customer claims, decision context, jurisdiction, system boundary, quotes, payment references, RDL bindings, research, and deliveries remain `CUSTOMER_PRIVATE`.

## State and authorization

Every transition is explicit, actor-attributed, reason-attributed, and append-only. Research cannot begin and an RDL run cannot be bound until payment is recorded as confirmed. A human override is recorded as an override and excluded from ordinary unit-economics metrics.

The canary does not run deep research. Preflight assesses feasibility from the existing inventory and uses zero discovery queries. G1/G2/G3 enforce maximum query, source, deep-review, paid-data, and specialist boundaries. A quote retains `UNKNOWN` whenever a monetary component or configured target margin is unknown.

## Determination and proof

One determination object renders both the JSON delivery and human-readable output. It binds the evidence cutoff, canonical record hash, evidence references, counter-evidence, unknowns, limitations, and a P1 snapshot-chain proof. P2/IPFS remains inactive. An `UNKNOWN` determination is a valid delivery; a favorable result is never promised.

## Additional canaries

- Context Fit validates scope architecture only and never emits BUY or ADOPT advice.
- Watch cycles allow 30 or 90 days and require a material candidate before deep research.
- Provider registration is an abstraction, not a marketplace. With zero completed tasks, provider performance is `UNKNOWN`.
- Temporal rates are derived only from dated events; state-transition rate and composite velocity remain `UNKNOWN` when not observed.
- Discovery questions require review and cannot auto-publish or perform outbound acquisition.

## Exit state

With no real paid request, the phase reports `READY_AWAITING_REAL_PROBLEM`. Real unit economics remain `UNKNOWN`.
