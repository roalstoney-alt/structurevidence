# Cost and runtime record

Measured locally on 2026-10-29 in the isolated implementation worktree. Timings use `/usr/bin/time -p`; they are observations, not service-level guarantees.

| Step | Real time | Result |
|---|---:|---|
| Build daily public-safe evidence export | 0.08 s | `RETRIEVAL_INCOMPLETE`; 11 claims |
| Rebuild IREN tracker + docs mirror | 0.12 s | completed |
| Render six X/LinkedIn cards through Playwright + local Chrome | 8.85 s | 6 assets; `DO_NOT_PUBLISH` |
| Desktop/mobile/DDR local browser QA | 12.17 s | PASS; 0 console errors |
| Growth-pilot + existing IREN regression tests | 0.42 s | 29 passed |

Incremental paid-service cost recorded for this implementation: **USD 0.00**. No new hosted service, scheduled automation, Worker deployment, D1 migration, social post, production POST, or outbound message was created. Local CPU/storage use is not priced here.
