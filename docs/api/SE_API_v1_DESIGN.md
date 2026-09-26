# StructEvidence API v1 Design

`SE_API_v1` has three deliberately separate planes.

The public read plane serves only an injected sanitized projection. The production default is empty; Phase 1 synthetic fixtures are injected only by local tests. Public representations omit repository paths, private provenance, raw references, and customer-plane data. Thirteen GET operations expose capabilities, Subjects, current/historical State, Changes, Evidence, and Branches.

The customer input plane stores Request, Challenge, and Outcome submissions in protected D1 tables. Input fields are allowlisted, payloads are capped at 65,536 bytes, configured origins are enforced, prepared statements are used, and `Idempotency-Key` prevents duplicates. Customer objects are `CUSTOMER_PRIVATE`; public handlers never query or merge those tables. Challenge creates `CHALLENGE_SUBMITTED`, and Outcome creates `OUTCOME_REPORTED`; neither path can write canonical State.

The control plane stores proposals behind Cloudflare Access. API validation and human approval do not materialize history. Repository creation is delegated to `materialize_se_proposal.py`, which requires a clean tree and performs schema, reference, temporal, hash, tail, chain, and no-overwrite checks. `--dry-run` performs all checks without writes. An explicit `--commit` is required to create the Git commit after successful materialization.

This is not CRUD. There are no PUT, PATCH, or DELETE State endpoints and no direct canonical-write HTTP endpoint.

Public read CORS is intentionally broad because responses are sanitized and public. Submission and control endpoints never use wildcard CORS. Rate classes are `PUBLIC_READ`, `PUBLIC_SUBMISSION`, and `ADMIN_CONTROL`; Phase 2 reuses the existing limiter binding for harmful public submissions and leaves low-friction public reads cacheable.
