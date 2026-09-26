# SE API v1 Security Boundary

Public GET endpoints read only the sanitized projection and intentionally allow public-read CORS. Immutable State, Change, and Evidence responses bind ETag to their canonical hash and support `If-None-Match`/304.

Customer submissions require JSON, a configured allowed origin when Origin is present, field allowlists, the existing rate limiter, and D1. Request, Challenge, and Outcome bodies are private and are not included in public response models, logs, or projections. Status lookup and all proposal operations require the existing Cloudflare Access issuer, audience, JWT, and administrator email allowlist checks.

Request IDs are included in versioned error envelopes. Logging may identify method, route, status, duration, subject ID, and object ID, but must not log authorization tokens, Access JWTs, customer identity, decision context, or Outcome text. Unexpected fields, malformed JSON, oversized bodies, wrong origins, wrong audiences, traversal-shaped identifiers, and missing authorization fail closed.

D1 migration `0002_se_api_v1.sql` creates dedicated private tables, a scoped idempotency registry, and the proposal store. Request, Challenge, and Outcome rows have UPDATE and DELETE denial triggers. Proposal updates represent workflow status; they do not grant canonical-write authority.

No production deployment, credential change, live D1 read, or external integration is part of Phase 2.
