# SE-DUAL-SITE-UPGRADE-002 — Phase D Pre-implementation Inventory

Status: DEVELOPMENT ONLY. NO MERGE OR PRODUCTION DEPLOY.

- Baseline main: `f267f9dbe506cb30f95a2f21543b72b4fc31c388`
- Inventory date: `2026-10-25`
- Commercial host: `https://structevidence.com`
- Research host: `https://structurevidence.org`

This inventory was completed before the Phase D commercial positioning edits. It records the implementation and live read-only observations used to classify product availability. No Cloudflare, D1, DNS, GitHub Pages, or production data was changed.

## Deployment and source architecture

| Surface | Observed implementation | Read-only production observation | Boundary |
| --- | --- | --- | --- |
| `structevidence.com` | Cloudflare Worker `structevidence-commercial`; source in `deploy/cloudflare-landing/` | `/`, `/capabilities.json`, and `/gaps/OEG-CML-001/` returned HTTP 200 with `server: cloudflare` on 2026-10-25 | Commercial pages, public gap UI/API, private intake, protected admin |
| `www.structevidence.com` | Worker redirect in `worker.js` | Code returns HTTP 308 to apex while retaining path/query | No duplicate commercial origin |
| `structurevidence.org` | Repository static research surface | Source Dependency View and Decision Conditions returned HTTP 200 with `server: GitHub.com` on 2026-10-25 | Canonical public evidence and exports remain on `.org` |

The commercial Worker does not proxy or rewrite `.org` artifacts. Phase D uses direct HTTPS links to canonical public pages and machine-readable exports. The commercial browser code makes no cross-origin evidence fetch.

Wrangler 4.136.2 was available locally. A read-only `wrangler deployments list` could not authenticate because this non-interactive session had no `CLOUDFLARE_API_TOKEN`; no temporary account or write operation was attempted. The deployed Worker identity is corroborated by the live Cloudflare response and repository route/binding configuration, but a Cloudflare deployment version ID is therefore not asserted.

## Worker routes and bindings

The Worker source is `deploy/cloudflare-landing/worker.js`; production configuration is `deploy/cloudflare-landing/wrangler.jsonc`.

- Public HTML: `/`, `/en/`, `/zh-cn/`, `/es/`, `/verify/`, `/context/`, `/decision-pack/`, `/pricing/`, `/deliverables/`, `/about/`, `/privacy/`, `/terms/`, `/gaps/`, `/gaps/changes/`, `/gaps/:gap_id/`.
- Public machine-readable routes: `/capabilities.json`, gap GET APIs.
- Public writes: `POST /api/requests` and gap challenge POST, each bounded by validation, origin policy, rate limiting, and human review.
- Protected routes: `/admin/requests` and `/api/admin/*`, guarded by Cloudflare Access issuer/audience/email policy and fail-closed behavior.
- D1 binding: `CUSTOMER_CASES_DB`, database name `structurevidence-customer-cases`, configured database ID `aee10591-536a-47af-8ee0-957551ba2360`.
- Rate-limit binding: `PUBLIC_INTAKE_RATE_LIMITER`.
- Configured public origins: commercial apex plus the `.org` research origins; no wildcard CORS.

## D1 and privacy boundary

Migration `0001_customer_intake.sql` defines customers, requests, and append-only request events. A public submission starts as:

- request status `SUBMITTED`;
- privacy `CUSTOMER_PRIVATE`;
- research authorization `NOT_AUTHORIZED`;
- no automatic owner, research, finding, publication, or public case update.

The public response exposes an external request ID only. Admin access is separate and protected. The migration has no upload/file table, and request events reject update and delete. Gap challenges use separate append-only history and never change evidence state without human review. Phase D neither changes these schemas nor exposes D1/customer fields in HTML, sitemap, public JSON, or `.org` links.

## Published prices and intake

The following prices existed at baseline and are frozen for Phase D:

| Service | Published price |
| --- | ---: |
| Claim Verification | USD 199 |
| Decision Context Review | USD 1,999 |
| Decision Pack | USD 4,999 |
| Rush handling | USD 399 additional, subject to capacity and written acceptance |

Each purchase covers one dated evidence cycle. No checkout, ROI, savings estimate, recurring subscription, or automatic renewal existed at baseline. `/verify/`, `/context/`, and `/decision-pack/` submit to the same-origin `/api/requests` flow and require human scope and separate authorization before research.

## Languages and SEO

- Commercial languages: English (`/` and `/en/`), Simplified Chinese (`/zh-cn/`), and Spanish (`/es/`).
- Locale price manifests contain identical numeric prices.
- Baseline home canonical was `https://structevidence.com/`; localized canonical generation existed but reciprocal home `hreflang` and a Worker sitemap route were absent in the inspected source.
- Phase D may add reciprocal homepage `hreflang`, deterministic commercial sitemap, and robots routes. These must contain `.com` commercial canonicals only and must not mirror `.org` evidence.
- Existing self-hosted CSS/JS and Content Security Policy prohibit external script dependencies. No external conversion/tracking script was found; the same-origin intake conversion path is preserved.

## Canonical `.org` evidence used by Phase D

| Artifact | Canonical URL | Baseline SHA-256 |
| --- | --- | --- |
| 800VDC case | `https://structurevidence.org/cases/800vdc/` | Not modified by Phase D |
| Source Dependency View | `https://structurevidence.org/cases/800vdc/source-dependency/` | `e42b94dcbce09900c9b79bc2374bf09b53ace2d1b9e897a50fb544715272ba38` |
| Source Dependency JSON | `https://structurevidence.org/cases/800vdc/source-dependency-v0.1.json` | `9038817ab15e1202ea5ae8ca374f515f5381b6480fce22f2ff137d3267cd7705` |
| Decision Conditions page | `https://structurevidence.org/cases/800vdc/decision-conditions/` | `a50ab5f0985decd60aab105b90365ea3c10f4c0e5195d8c779c544649fd4d581` |
| Decision Conditions JSON | `https://structurevidence.org/cases/800vdc/decision-conditions-v0.1.json` | `c451662988a44c9907c906e6e245b1ee64e5c204fc5dca7b4d06c26f4b49f040` |
| Decision Conditions Markdown | `https://structurevidence.org/cases/800vdc/decision-conditions-v0.1.md` | `bafe2695ee79f6cc0a9b5ed033546d1a36a84071d7a447f9ffed247eb6fe9fea` |

Public evidence cut-off: `2026-10-22T14:02:00Z`. Decision Conditions snapshot SHA-256: `1aa90c414d4eee5f98adc1a35adcad304543eb30bfd57946fd7a998a37a1dea1`.

The bounded public packet contains nine reviewed URLs and seven source lineages. It does not establish independent field validation or a second independently controlled operating instance. `CHINDATA_E3_E4=UNRESOLVED`, `SECOND_REAL_HUMAN_REVIEW=UNSUPPORTED`, and all client action fields remain `UNSPECIFIED`. These are time-bounded review results, not authoritative truth or customer actions.

## Availability classification used in Phase D

| Capability | Status | Evidence for classification |
| --- | --- | --- |
| Public evidence and read APIs | `LIVE` | Public `.org` artifacts and `.com` gap GET routes return HTTP 200 |
| Private intake and request history | `LIVE` | Existing Worker POST, D1 binding, privacy defaults, append-only event tests |
| Scoped private Decision Record | `AVAILABLE_WITH_HUMAN_SCOPE` | Existing manual service/intake terms require written scope, contract, and authorization; no self-service product |
| Private managed gap register | `AVAILABLE_WITH_HUMAN_SCOPE` | Can be part of accepted human work; public gap registry exists, but no private self-service register |
| Evidence notifications | `PROPOSED_NOT_LIVE` | No delivery or subscription implementation found |
| Recurring subscriptions | `PROPOSED_NOT_LIVE` | No billing/renewal/subscription implementation found |
| Customer Decision Boundary API | `PROPOSED_NOT_LIVE` | Public read endpoints exist; no client-private decision or autonomous research API exists |

This classification does not claim production deployment of Phase D. It describes the real pre-existing service boundary that the proposed homepage must communicate.
