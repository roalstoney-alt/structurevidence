# IREN Funnel Contract Verification

Observed on 2026-10-29. These checks were read-only GET requests; no production POST was made.

| Surface | URL contract | Result |
|---|---|---|
| Public tracker | `https://structurevidence.org/cases/iren-ai-cloud-transition/` | HTTP 200 |
| Row challenge | `https://structevidence.com/verify/?case_id=SE-IREN-AI-CLOUD-001&claim_id=IREN-R003` | HTTP 200; fixed public identifiers only |
| Decision Pack | `https://structevidence.com/decision-pack/?case=SE-IREN-AI-CLOUD-001` | HTTP 200; existing compatible case parameter |

The `.org` page sends no evidence text, person identity, private thesis, unpublished evidence, or token in the URL. The existing private intake contract remains unchanged. Customer content remains `CUSTOMER_PRIVATE` and `NOT_AUTHORIZED` for research/publication unless separately authorized.

`PRODUCTION_POSTS=0`

`WORKER_CHANGES=0`

`D1_MIGRATIONS=0`
