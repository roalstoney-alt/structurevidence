# Customer Intake Infrastructure — Phase B Test Report

Date: 2026-09-23

## Results

- Worker unit/API tests: **6/6 passed**.
- Infrastructure guard tests: **3/3 passed**.
- Existing Paid-Readiness UI regression tests: **7/7 passed**.
- Targeted CML v1.1 + frozen L1 + UI + intake guards: **21/21 passed**.
- Wrangler production bundle dry-run: **PASS**.
- D1 migration against the Wrangler local database: **PASS**, 12 statements executed.
- Local Worker + D1 integration: Verify submission **201**, Context submission **201**.
- Local persistence query: both requests are `SUBMITTED`, `CUSTOMER_PRIVATE`, `NOT_AUTHORIZED`, owner null, with a `REQUEST_SUBMITTED` event by `CUSTOMER`.
- Local unauthenticated admin request: **blocked** because Cloudflare Access values are not configured.

## Covered assertions

- Persistent record creation and unique `SE-REQ-*` identifiers.
- Required defaults cannot be overridden by public input.
- Request and submission event are written in a single D1 batch.
- Invalid email/request shapes are rejected.
- Admin list and detail operations.
- Owner, status, and authorization changes append events.
- Admin-only fields are not accepted from customers.
- Event table has database-level update/delete rejection triggers.
- Verify and Context forms target the API and retain a clearly marked email fallback only for service unavailability.
- File table/upload is absent.
- Homepage and 800V case are byte-identical to `HEAD`.
- No CML, RDL, public evidence, timeline, or research artifact changed.

## Not testable before infrastructure configuration

- Real Cloudflare Access login and production JWT validation against the final team domain/AUD.
- Remote D1 migration and production persistence.
- Cloudflare WAF/rate-limiting behavior.
- Production routing and end-to-end delivery.

These remain behind the human infrastructure gate and were not represented as passing.
