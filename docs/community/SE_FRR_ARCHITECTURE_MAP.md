# SE-FRR-001 Architecture Map

Audit date: 2026-09-25  
Baseline SHA: `2356c9327ba5b40995435eca952edd706fd944fc`

## Current system

```text
Public research artifacts (JSON/Markdown/HTML)
        |
        +-- Evidence Core envelope
        +-- CML technical-risk records
        +-- RDL research/freshness records
        +-- Timeline + Monitoring snapshots/transitions
        +-- GDR-SE release authorization
        |
        v
structurevidence.org / static public research surface

structevidence.com
        |
        v
Cloudflare Worker: structevidence-commercial
        |
        +-- static commercial pages
        +-- POST /api/requests
        +-- /admin/requests/*
        +-- /api/admin/requests/*
        |
        +-- Cloudflare Access (admin identity)
        +-- D1 CUSTOMER_CASES_DB (private requests/events)
        +-- public intake rate limiter
```

The public evidence plane and private customer plane are intentionally separate. That boundary should be retained for FRR.

## Existing canonical layers

| Layer | Current implementation | Relevance to FRR |
|---|---|---|
| Evidence identity/provenance | `evidence/core/schema/evidence_core_record.schema.json` | Reuse IDs, subject IDs, source/artifact refs, dual clocks, verification, correction, supersession, policy and hashes. |
| Technical state | `technical-risk/cml-v1.1/` | Reuse dependency, alternative path, migration readiness, counter-evidence, unknowns and revision history. |
| Research trail | `rdl/research/` | Reuse research levels, checked/used/rejected sources, new/counter/duplicate evidence, before/after states, unknown resolution, authorization and telemetry. |
| Freshness | `rdl/freshness/` | Reuse explicit freshness policy, event invalidation and fail-safe unconfigured states. |
| State transitions | `monitoring/schema/state_transition.schema.json` | Reuse prior/current state linkage, effective/known time, basis and source refs. |
| Information events | `monitoring/schema/information_event.schema.json` | Reuse event time, knowledge time, source/artifact hashes, correction and supersession. |
| Snapshots | `monitoring/schema/monitoring_snapshot.schema.json` | Reuse subject snapshots, prior snapshot ID, evidence dynamics, hashes and version fields. |
| Release authorization | `gdr-se/` | Reuse fail-closed gates and human/review authorization boundary. |
| Public/paid packaging | `commercial/` | Reuse evidence graphs, structural deltas, verification records, order and paid-delivery authorization schemas. |
| Request intake | `deploy/cloudflare-landing/` | Extend rather than replace the existing D1 request/event model and Worker API. |
| Authentication | Cloudflare Access JWT validation in `worker.js` | Reuse for admin/reviewer routes; add role/entitlement design separately. |
| Deployment | `deploy/cloudflare-landing/wrangler.jsonc` | Reuse Worker, D1, rate limiter, custom domains and observability. |
| Public cases | `cases/800vdc/`, `cases/sodium-ion-bess/` | Candidate public-case seeds; do not claim completeness without mapping. |
| Technical records | Four directories under `technical-risk/records/` | Candidate initial subjects for Amphenol, Murata and NXP. |
| GDR records | Five directories under `gdr-se/records/` | Reusable gated records for Strategy, BNB, SOL, TRX and XLM where scope permits. |
| Test infrastructure | 269 Python tests plus 14 Worker tests | Extend with FRR append-only state, evidence, change and outcome invariants. |

## Reusable components count

Phase 0 counts 16 reusable component groups:

1. Evidence Core envelope
2. CML PDRE/state records
3. RDL research records
4. RDL freshness engine/configuration
5. Timeline atomic observations and event ledgers
6. Monitoring information events
7. Monitoring state transitions
8. Monitoring snapshots and provenance indexes
9. GDR-SE release/paid-delivery gates
10. Commercial evidence/verification schemas
11. D1 customer/request/request-event model
12. Append-only D1 event triggers
13. Cloudflare Access admin authentication
14. Public intake validation/rate limiting
15. Existing public and technical-risk case corpus
16. Python and Worker regression-test infrastructure

## Recommended FRR integration boundary

```text
Discord bot / website clients
            |
            v
Existing Cloudflare Worker API
            |
            +-- public read model: Subjects, States, Changes, Evidence
            +-- private write model: Requests, Challenges, Outcomes
            +-- admin review: Evidence review, State creation, Change creation
            |
            +-- D1 operational indexes and private workflow data
            +-- immutable/hash-bound file artifacts for publishable research records
            |
            v
Evidence Core + CML/RDL + Monitoring + GDR-SE
```

The Worker should expose the coherent FRR API while existing domain models remain authoritative for their own semantics. An adapter/mapping layer is safer than copying or silently rewriting existing CML/RDL history.

## Current API and authentication patterns

Public:

- `POST /api/requests`
- browser CORS restricted to configured origins
- non-browser requests without `Origin` supported
- IP-keyed rate limiting

Administrator:

- `GET /api/admin/requests`
- `GET /api/admin/requests/{id}`
- `PATCH /api/admin/requests/{id}`
- `POST /api/admin/requests/{id}/events`
- separate Cloudflare Access audiences for UI and API
- explicit administrator email allowlist

There are no current FRR read endpoints for states, histories, changes or evidence, and no challenge/outcome endpoints.

## Production topology and branches

- Git deployment source: `main`; remote tracking branch: `origin/main`.
- At audit time the local and remote branch tips match.
- `structevidence-commercial` serves custom domains `structevidence.com` and `www.structevidence.com`.
- D1 database binding: `structurevidence-customer-cases`.
- Public content and private customer records must remain separated.
- No deployment was performed during Phase 0.
