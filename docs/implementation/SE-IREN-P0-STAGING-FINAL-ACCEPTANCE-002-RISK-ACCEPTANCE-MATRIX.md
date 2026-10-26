# SE-IREN-P0-STAGING-FINAL-ACCEPTANCE-002 · Risk acceptance matrix

Date: 2026-10-27 (Asia/Shanghai)

This matrix records technical acceptance evidence for owner review. It does not authorize production deployment, merge, production POST, charging, outreach, social publication, or a public Pilot. Risk acceptance authority remains with the owner.

Evidence classes are deliberately non-interchangeable:

- `REAL_PROVIDER_OBSERVED`: directly observed through Cloudflare Access or Turnstile staging infrastructure.
- `DETERMINISTIC_FAULT_INJECTION`: a controlled response or transport failure injected into the production Worker code path during automated testing.
- `REMOTE_D1_OBSERVED`: a read or fail-closed mutation attempt against the isolated staging D1.
- `PRODUCTION_READ_ONLY_OBSERVED`: a read-only inventory check; no production mutation occurred.

| ID | Boundary | Evidence class | Observation | Fail-closed result | Residual risk / disposition |
|---|---|---|---|---|---|
| RA-01 | Access authorized admin list | REAL_PROVIDER_OBSERVED | Authenticated navigation reached `/api/admin/requests`; HTTP 200 JSON contained `SE-REQ-E56EABAB6D574DC3BC7C` | Target matched D1 privacy and authorization fields | PASS for owner production review; JWT, OTP, and identity were neither extracted nor persisted |
| RA-02 | Turnstile valid challenge | REAL_PROVIDER_OBSERVED | Two independent staging browser challenges produced HTTP 201 | Each successful request retained private, unauthorized defaults | PASS |
| RA-03 | Turnstile invalid token | REAL_PROVIDER_OBSERVED | Staging Siteverify returned HTTP 400 `Human verification failed` | No D1 write | PASS |
| RA-04 | Missing token | DETERMINISTIC_FAULT_INJECTION | Required-token validation returned HTTP 400 | No D1 write | PASS; this is application validation, not a provider observation |
| RA-05 | Expired token | DETERMINISTIC_FAULT_INJECTION | Injected verifier rejection returned HTTP 400 | No D1 write | PASS for code-path coverage; not claimed as a real-provider expiry event |
| RA-06 | Replayed token | DETERMINISTIC_FAULT_INJECTION | First injected single-use token returned 201; second use under a different request scope returned 400 | One logical write only | PASS for code-path coverage; not claimed as a real-provider replay event |
| RA-07 | Wrong hostname | DETERMINISTIC_FAULT_INJECTION | Successful Siteverify payload with an unapproved hostname returned HTTP 400 | No D1 write | PASS |
| RA-08 | Wrong action | DETERMINISTIC_FAULT_INJECTION | Successful Siteverify payload with the wrong action returned HTTP 400 | No D1 write | PASS |
| RA-09 | Provider error | DETERMINISTIC_FAULT_INJECTION | Injected provider transport failure returned HTTP 503 | No D1 write | PASS |
| RA-10 | Provider timeout | DETERMINISTIC_FAULT_INJECTION | Injected abort at the bounded timeout returned HTTP 503 | No D1 write | PASS |
| RA-11 | Consent and request privacy | REMOTE_D1_OBSERVED | Target has one consent receipt at `SE-CUSTOMER-PRIVACY-v1`; request is `CUSTOMER_PRIVATE`, `NOT_AUTHORIZED`, owner unset | No implicit research or publication authorization | PASS |
| RA-12 | Idempotency | REMOTE_D1_OBSERVED | Target has one active hashed idempotency record and one logical request/event/consent relationship | Replay does not duplicate history | PASS |
| RA-13 | Append-only history | REMOTE_D1_OBSERVED | Four UPDATE/DELETE triggers are present; no-op UPDATE attempts against the target event and consent receipt were rejected by D1 | History remained unchanged | PASS |
| RA-14 | Production isolation | PRODUCTION_READ_ONLY_OBSERVED | Production deployment history still ends at 2026-10-08; migration `0003` remains pending | Production Worker and D1 were not mutated; production POST count is zero | PASS |

## Decision

The two previously blocked technical gates are closed for the limited purpose of owner production review:

1. `ACCESS_AUTHORIZED_ADMIN_READ = PASS`
2. `LAYERED_TURNSTILE_ACCEPTANCE = PASS`

`READY_FOR_OWNER_PRODUCTION_REVIEW = YES` does not mean production-ready or deployment-authorized. Owner review must still decide deployment sequencing, production migration authorization, production Access/Turnstile configuration, human privacy/legal review, and rollback/monitoring readiness.
