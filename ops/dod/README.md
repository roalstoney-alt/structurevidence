# SE-DOD-001 — Decision Opportunity Discovery

This workspace implements the controlled first execution defined by
`STRUCTEVIDENCE_DECISION_OPPORTUNITY_DISCOVERY_CODEX_WORKFLOW_v0.1.md`.

Snapshot date: 2026-10-08 (Asia/Shanghai)
Protocol level: v0.1.2
Run type: `CALIBRATION`

Operating boundaries:

- The radar covers only the four frozen verticals A–D.
- Five events per vertical validate the workflow only. This is not market coverage and cannot support tier relaxation or a conclusion about market demand.
- The records describe public evidence boundaries, not everything an organization may know privately.
- A gap qualifies for opportunity selection only when resolving it could materially change a real decision. A missing public fact alone is insufficient.
- An evidence gap is not a company failure and is not an investment recommendation. Internal or private evidence may exist outside the reviewed boundary.
- Owner resolution distinguishes named accountable people, accountable roles, company routes, and unresolved ownership. A corporate route is not proof of decision responsibility.
- A missing fact qualifies only if the evidence should reasonably exist at the current decision point. Future outcomes are classified `FUTURE_OBSERVABLE` and cannot support first-contact outreach.
- Every first-wave send requires a fresh Q0 check immediately before human authorization. Material new evidence produces `REOPEN` and prohibits send.
- Route validity and route purpose fit are separate gates. Only `DIRECT` and `ROUTABLE` routes are first-wave eligible, and routable messages must address the receiving function honestly.
- No outreach has been sent. A send recommendation still requires an immediate Q0 recheck and explicit human recipient/channel authorization.
- No guessed email address is eligible for the send queue.

`MATERIAL_DECISION_EVIDENCE_GAPS.csv` applies the material-impact test to the claim inventory. `TEMPORAL_OBSERVABILITY.csv` applies Q2B to the first wave. `FRESHNESS_RECHECKS.csv` records point-in-time Q0 evidence and state transitions. `OPPORTUNITIES.csv` is the patched qualification and owner-resolution ledger. `PRE_SEND_GATES.csv` records the twelve required gates for the five first-wave opportunities.
