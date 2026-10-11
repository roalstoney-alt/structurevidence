# SE-CEPE-001 baseline and boundaries

WORKFLOW = `SE-CEPE-001 v0.1`

STATUS = `HUMAN_REVIEW_REQUIRED`

ISOLATED_BRANCH = `codex/se-cepe-001-continuous-v01`

BASELINE_SHA = `51ec09ab0003b3efca5b085d599f0473927a447e`

BASELINE_SOURCE_BRANCH = `codex/se-ai-data-001-buyer-validated-pilot`

REPOSITORY = `roalstoney-alt/structurevidence`

PILOT_TIMEZONE = `Asia/Singapore (UTC+08)`

T0 = `2026-10-11T21:54:22+08:00`

PILOT_END = `2026-11-10T21:54:22+08:00`

ACTIVATION_EVIDENCE = `Existing Codex heartbeat updated ACTIVE; controlled run SE-CEPE-CTRL-20261011-002 wrote 8/8 observations and one run/cost/change report.`

## Immutable inputs verified at Stage 0

| Input | SHA-256 | Result |
|---|---|---|
| `ops/growth/SE_AI_DATA_001/SE_TEMPORAL_EVAL_SAMPLE/tasks.jsonl` | `2db1e1a6cbfe8d9032bfb1059cd81734b715c7b23ed9e43c400845ce066d19fc` | PASS |
| `ops/growth/SE_AI_DATA_001/SE_TEMPORAL_EVAL_SAMPLE/gold.jsonl` | `972b8f259a149df998b6d3c7dcb04512ab25a27335c87634db14a459927166cf` | PASS |
| `ops/growth/SE_AI_DATA_001/SE_TEMPORAL_EVAL_SAMPLE/source_manifest.json` | `7ff2f3770f58485548a65d47b49829570b6a6145bcefb44a5b244b3d69a79515` | PASS |
| Eight claim JSON records named by the manifest | manifest hashes | PASS |

The task registry points to exactly `SE-TECP-001` through `SE-TECP-008`. The
original Gold labels are two `SUPPORTED` and six `NOT_ESTABLISHED`; they are
read-only. A current observation may append a new evidence event, but it may
not rewrite a historical Gold, claim JSON, snapshot or cutoff.

## Protected trust boundaries

- `OUTREACH_AUTHORIZED = false`
- `PUBLICATION_AUTHORIZED = false`
- `PRODUCTION_DEPLOY_AUTHORIZED = false`
- `PAID_RESEARCH_AUTHORIZED = false`
- `HISTORICAL_REWRITE_AUTHORIZED = false`
- The raw eight-task package remains `NEEDS_OWNER_CONFIRMATION` for external
  redistribution.
- The Irkutsk records remain public-source projections only. No private case
  material, personal data or unpublished evidence may enter these artifacts.
- `structurevidence.org` remains the research surface and
  `structevidence.com` remains the commercial surface.
- The frozen value proposition remains verbatim: **Verify Your Verify — Lower
  the cost of knowing what you can trust.**

## Preserved programme states

- `GTM005_STATUS = HOLD`. The v0.2 study at commit
  `722389af54e48177bb2aebee4c173a507a5b5617` confirmed no buyer problem,
  qualified opportunity or paid intent.
- `GTM002_V04_STATUS = STOP_AND_RETAIN_RESULT`. The v0.4 fulfillment study is
  retained at commit `a31dd66fb3a55a8d056bcd1731738067eb02adbb`.
- `TRUST_BOUNDARY_30D_001_CHANGED = NO`. Its positioning lock and campaign
  state are separate and must not be edited or scheduled by this workflow.

## Deployment and cost boundary

This branch makes no site, API, Worker, database or production change. No paid
source or API is authorized. Unmeasured human time and agent/tool cost remain
`UNKNOWN`; they must never be recorded as zero merely because billing data is
unavailable.

## Observation scope

The local runner performs bounded public-source availability and retrieval-hash
checks. This is not a semantic conclusion engine. A retrieval error is an
operational exception, never a no-change result. Material interpretation,
publication, product changes and any new evaluation version all retain a human
gate.
