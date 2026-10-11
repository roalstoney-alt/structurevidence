# SE-GTM-002 — Decision-Pressure Acquisition Pilot

Status: `HUMAN_REVIEW_REQUIRED`

Baseline: `b53abeedbf2926f90ef6acad59563132fddcc8fc`

Branch: `codex/se-gtm-002-decision-pressure-pilot`

This pilot is an additive customer-acquisition experiment. It does not replace
or amend `TRUST_BOUNDARY_30D_001`, CML, RDL, Claim Intake, Decision Pack,
historical Stop-Points, production websites, payment systems, authentication,
or public APIs.

## Scope

- Pipeline A: event-first direct opportunity discovery.
- Pipeline B: existing-customer-channel partner discovery.
- Use case A: industrial electronic-component EOL and alternative qualification.
- Use case B: technical RFQ compliance and supplier-evidence verification.

## Current boundary

The initial candidate set reuses four existing public CML research objects.
Those objects establish technical trigger evidence, but do not establish a
named affected customer, an active customer decision, a verified purpose-fit
contact route, confirmed demand, or willingness to pay.

Five organizations are recorded as potential channel partners because their
official material supports relevant customer-facing capabilities and official
contact routes. Partner fit remains a hypothesis; no organization has been
contacted.

## Append-only rule

Never overwrite a CDSP record to change a fact or outcome. Create a new version,
set `predecessor_record_id`, append a history event, and preserve the prior
file. Silence is not a response and a score cannot override a failed gate.

## Human gate

Email, contact forms, LinkedIn messages, other private outreach, payment
commitments, and external research spend require separate human approval for
the exact recipient, route, content, and cost.
