# CML v0.1 Pre-Audit

| Check | Result |
| --- | --- |
| REPO_HEAD | `0abab7f1246f70445d018478542a6dc0f7b5ab05` |
| REMOTE_MAIN | `0abab7f1246f70445d018478542a6dc0f7b5ab05` |
| WORKTREE_CLEAN | YES at entry |
| PRODUCTION_DOMAIN | `structevidence.com` via Cloudflare Worker; canonical source site `structurevidence.org` |
| RDL_FRESHNESS_POLICY_VERSION | `RDL_FRESHNESS_v0.1a` |
| RDL_ENGINE_VERSION | `RDL_FRESHNESS_ENGINE_v0.1a` |
| EVENT_SCOPE_STATUS | PASS / event domain + target + as-of matching implemented |
| SUPERSESSION_STATUS | PASS / directional predecessor-successor relation implemented |
| GDR_G3_STATUS | PASS / runtime freshness lookup uses v0.1a |
| PAYMENT_READINESS | MANUAL_USDT_SETTLEMENT_ACTIVE / quote gated |
| PAID_PDF_READINESS | PDF product PASS; fulfillment MANUAL_ONLY |

`CML_IMPLEMENTATION = PERMITTED_WITH_LIMITATIONS`

The domain may be published as a Method Pilot and request-only service. It may not claim automated fulfillment, universal qualification or configured freshness where CML family cadence is unresolved.
