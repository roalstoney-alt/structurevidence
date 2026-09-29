# Agent Discovery API Subdomain Routing v0.1

Status: active

Entry baseline: `e7d712ae65242bf1d833f1f44b115516185e180d`

Routing implementation commit: `3b918cd`

## Final architecture

- Public research and static evidence: `https://structurevidence.org` on GitHub Pages.
- Runtime resolution: `https://api.structurevidence.org/resolve` on the existing `structurevidence-public-claim-resolver` Cloudflare Worker.
- Commercial action: `https://structevidence.com` on the existing commercial Worker.

The API hostname uses Cloudflare's supported Worker custom-domain binding. This is deliberate: it creates an origin-free, proxied API hostname without moving the apex behind Cloudflare or inventing an origin dependency. The Worker owns the API hostname but returns JSON only for `/resolve`; other paths return 404.

## DNS and deployment record

Preflight public DNS:

- Apex A: GitHub Pages addresses `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, and `185.199.111.153`.
- `www`: `roalstoney-alt.github.io`.
- `api`: absent.
- MX, apex TXT, and `_dmarc` TXT: no public records returned.

Post-deployment public DNS:

- Apex and `www`: unchanged.
- `api`: Cloudflare anycast addresses `104.21.4.14` and `172.67.223.242`; HTTPS valid.
- MX, apex TXT, and `_dmarc` TXT: unchanged, with no public records returned.

Worker deployment:

- Worker: `structurevidence-public-claim-resolver`
- Custom domain: `api.structurevidence.org`
- Deployment version: `137ba032-46b0-4c9c-9ba2-1984cf458305`
- Deployment/acceptance time: 2026-09-29 UTC

## Runtime boundary

`GET /resolve` is public and read-only. `OPTIONS /resolve` supports CORS preflight. Responses use `application/json; charset=utf-8`, `Access-Control-Allow-Origin: *`, and `Cache-Control: no-store`. POST, PUT, PATCH, and DELETE return 405. `/api/resolve` and administrative paths return 404.

The resolver has no database binding, external search, LLM call, research authorization, customer request creation, email action, or state mutation.

## Acceptance

- GitHub Pages static regression: PASS.
- API DNS, Cloudflare edge, TLS, and Worker route: PASS.
- 800VDC deployment boundary: PASS.
- 800VDC adoption boundary: PASS.
- Sodium-ion commissioning boundary: PASS.
- Sodium-ion economic boundary: PASS.
- NSCLC trial-population boundary: PASS.
- Personal medical boundary: PASS.
- NO_MATCH behavior: PASS.
- Discovery manifest three-plane URLs: PASS.
- Commercial capabilities and human-authorization boundary: PASS.
- Root/docs parity: PASS.
- Claim files changed: 0.
- Public case primitives, CML history, and RDL history changed: 0.
- GitHub Pages CNAME files changed: 0.
- Email DNS changed: NO.

Validation commands:

```sh
python3 scripts/build_agent_discovery.py --check
python3 scripts/test_agent_discovery.py
python3 scripts/test_agent_api_subdomain_routing.py
node --test deploy/cloudflare-evidence-resolver/test/*.test.js
node --test deploy/cloudflare-landing/test/*.test.js
```
