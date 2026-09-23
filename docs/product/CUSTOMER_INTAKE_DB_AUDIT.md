# Customer Intake + Case Database Audit

Date: 2026-09-23
Entry SHA: `3f78f740aad224fa991a09a13046906846bbe571`

## Current behavior

- `/verify/` uses `assets/product.js` to convert the submitted form into a `mailto:` URL. No request is persisted.
- `/context/` uses the same `mailto:` behavior. No request is persisted.
- No request database, migration system, server-side intake handler, or admin request queue exists.
- The public site is published from a static root/`docs/` mirror through GitHub Pages.
- `deploy/cloudflare-landing/worker.js` only proxies requests to `structurevidence.org`; its Wrangler configuration has no D1, KV, Durable Object, or other persistent binding.
- Existing “Enterprise Access”/“Login” wording routes to manual contact. It is not an authentication mechanism.

## Existing runtime boundary

The existing Cloudflare Worker runtime could technically be extended with persistent storage, but no storage binding is configured in the current deployment. The primary public origin remains static GitHub Pages. Adding D1 would therefore be a new deployment capability, schema migration, binding, and operational boundary rather than reuse of an existing request database.

## Authentication audit

No reusable administrator authentication or authorization mechanism was found:

- no OAuth/OIDC integration;
- no Cloudflare Access identity assertion validation;
- no signed session or JWT validation;
- no authenticated admin middleware;
- no administrator role/allowlist configuration.

Publishing `/api/admin/requests` or `/admin/requests/` without this control would expose customer-private submissions. A shared secret embedded in browser JavaScript, an obscured URL, or a client-only password is not acceptable protection.

## Stop decision

`AUTH_REQUIRED`

The upgrade specification explicitly requires work to stop rather than invent insecure admin protection. Therefore this run does not:

- replace the two `mailto:` flows;
- create public or admin API routes;
- create a production database;
- implement file uploads;
- modify homepage positioning or the 800V case;
- write customer data into CML, RDL, evidence, timeline, or publication-control records;
- deploy anything.

## Minimum prerequisite for resumption

Human approval must select and configure an administrator identity boundary. A compatible minimal target would be Cloudflare Access in front of `/admin/*` and `/api/admin/*`, with the Worker validating the Access JWT and enforcing an explicit administrator allowlist. D1 could then be introduced as the persistent store with migrations and separate customer-private tables.
