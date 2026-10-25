# SE-DUAL-SITE-UPGRADE-002 / Phase E — Decision Boundary Pilot
Status: DEVELOPMENT AUTHORIZED; no PR merge, Cloudflare publish, GitHub Pages changes or production writes authorized.
Baseline main: 95219314309e01af6bf4042831b2bf4ba18fbc02
Previous: PR #51 squash merged; no intentional production deployment.

## Product hypothesis
A dated evidence boundary, source lineage and citable decision conditions can reduce a client's cost of discovering what may safely be treated as supported, unknown or out of scope. This is an unproven hypothesis, not a demonstrated ROI claim.

## First requirement — deploy trigger audit
Check GitHub repo Settings > Pages publishing source (branch/root/docs versus Actions), Pages deployment history for merged SHA, the actual public .org HTTP content/commit if inspectable, and any push-to-main workflow that may publish. The presence of CNAME files and HTTP 200 is NOT proof of auto deploy or exact deployed commit. If GitHub Pages source/version inaccessible report UNVERIFIED, with observed evidence. Do not change Pages settings or publish. Cloudflare Worker .com requires separate authorization and version/smoke test before production.

## Pilot design
- Select one actually authorized customer/decision only after written opt-in and human scope approval; until then use clearly labeled PUBLIC_ILLUSTRATION_NOT_CUSTOMER_PILOT.
- Record freeze T0: decision question, owner (private), decision event and deadline (client-specified), scoped source list, qualifying rules, evidence cutoff, last reviewed, unknowns, competing hypotheses, hash/version.
- Record measured work units: researcher minutes, source acquisition costs, reviewer touch time, rounds, net new qualifying sources, clarifications, challenge submissions, decision-condition citations, revisions/supersessions.
- Record outcome only when independently observed and permitted for the scope. Do not turn customer decision into our recommendation.
- Show before/after cost or speed only with actual baseline and comparable measurements; otherwise INSUFFICIENT_DATA. Do not claim avoided loss.
- Separate public sample from private client data; do not emit D1 or internal case identities on .org.

## Engineering deliverables
1. Versioned Pilot Protocol and schema with append-only events: BASELINE_FROZEN, REVIEW_STARTED, EVIDENCE_ADDED, EVIDENCE_REJECTED, CHALLENGE_RECEIVED, RULE_CHECKED, STOP_POINT_EMITTED, CLIENT_DECISION_RECORDED (client supplied only), OUTCOME_OBSERVED, SUPERSEDED.
2. Deterministic local demo using synthetic data with clear TEST_FIXTURE_ONLY flag. Never turn fixtures into customer evidence.
3. Human-approvable consent, privacy, scope, retention and no-outreach boundaries.
4. Machine and human-readable report that distinguishes observed telemetry, missing data, causal limitations and costs.
5. Optional safe links from commercial staging to .org static cases; do not presume subscription, automatic notification or private API live.
6. Tests: source baseline drift zero, append-only, idempotency, missing data, access control and privacy, unsupported reviewer truthfulness, cross-locale compatibility, case status preserved, no false ROI, new regression count zero.

## Approval gates
PR-E Draft only; no automatic merge; no production deploy; no new billing, research outreach or client enrollment without separate approval.
Return code HEAD SHA, files, tests, source hash drift, exact Pages deployment trigger evidence, pilot observations vs test fixtures, blockers and next human gate.
