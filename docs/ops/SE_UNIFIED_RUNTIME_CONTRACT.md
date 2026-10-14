# StructEvidence unified runtime contract

Version: `SE-UNIFIED-SCHEDULE-X-v1.0`
Effective prospectively from: 2026-10-14

## Single trigger

StructEvidence has one verified logical production trigger: the already-existing
local Codex heartbeat `structevidence-trust-boundary-30d`, repurposed for 22:00
daily in `Asia/Singapore`. The specified platform-hosted task
`6aba2674e6448191867d0890ad2cc1ed` was not addressable from the Codex app and is
therefore treated as an unverified read-only surface, not a second firing
executor. The fallback follows the workflow's rule for a platform task that
cannot invoke local/cloud code. The trigger starts the bounded run at 22:00; the
report is delivered after completion and carries its real delivery time.
Repository `workflow_dispatch` jobs are manually invoked executors and are not
clocks.

The orchestrator does not schedule itself. CML and LoveTimeline remain separate
projects and are read only from this workflow. The second StructEvidence
heartbeat is paused; no new schedule was created.

## State and evidence discipline

Configured, attempted, delivered and verified are separate states. Every stage
uses one of `PASS`, `PARTIAL`, `BLOCKED`, `MISSED`, `NOT_DUE`, `HOLD`, or
`UNVERIFIED`. `NO_NEW_EVIDENCE` is a research outcome, not proof that a job ran.
Unrun review periods remain `NOT_YET_REVIEWED`. Evidence-state cutoffs and
material-change dates advance only after accepted qualifying evidence and any
required human gate.

Each daily run has a deterministic ID and an expiring lease. JSON artifacts are
written atomically. Run files and X receipts are append-only: replay returns the
same completed run, and a conflicting replacement fails. X idempotency is keyed
by account, date, and canonical content hash. Because X create-post does not
provide a native idempotency key, the adapter reconciles provider history before
publishing and after an ambiguous transport outcome. It never blindly resends.

## Case workflow

The daily bundle covers `CML-PDRE-001`, `SE-BESS-SODIUM-001`, and
`SE-IRK-LAB-001`. Sunday also covers the three-case synthesis and folded
`SE-ONC-NSQNSCLC-CN-001`; Monday includes the private-wall
`SE-IRK-SOCSM-001` check. Review inputs must include a real review ID, retrieval
time, boundary, sources, old/new accepted state, and explicit evidence counts.
Irkutsk direct and indirect work shares one maximum budget of four search groups
and eight webpage-open attempts and stores a dependency graph to prevent
syndicated reposts becoming false corroboration.

## X publication

The supported direct adapter uses the official X API v2 with an OAuth 2 user
access token supplied at runtime as `X_USER_ACCESS_TOKEN`. It verifies
`/2/users/me` resolves exactly to `@structevidence`, reads recent account posts,
checks duplication, sends at most one candidate, and reads the new post back.
Tokens are never logged or persisted. A write response without a matching
readback is `POST_ACCEPTED_VERIFICATION_PENDING`; an ambiguous transport result
is `PUBLISH_OUTCOME_UNKNOWN` until provider reconciliation succeeds.

Ordinary accepted method or existing-state posts may be `AUTO_PUBLISH`.
Accepted case-state transitions, meaningful medical conclusions, substantive
corrections, or sensitive material are `HUMAN_GATE_REQUIRED`. External outreach
is `HOLD`.

## Observability and failure delivery

Stages emit `SCHEDULED`, `STARTED`, `SEARCH_COMPLETED`, `ARTIFACT_CREATED`,
`WRITE_ATTEMPTED`, `DELIVERED`, and `VERIFIED` with timestamps and proof.
Reports are rendered on failure. A run cannot independently prove its own
absence, so missing-run detection remains
`MISSING_RUN_DETECTION_NOT_INDEPENDENT` until an already-authorized external
health surface is verified. No additional StructEvidence timer may be created
to repair that gap.

## Historical note

The older three-case weekly and separate Irkutsk schedule descriptions remain
historical records of the prior arrangement. They do not authorize parallel
production timers after this contract takes effect.
