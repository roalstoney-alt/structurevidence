# Paid-Readiness UI Audit

## CURRENT_INFORMATION_ARCHITECTURE

The repository publishes a static site from mirrored root and `docs/` trees. Before this upgrade the homepage prioritized the BNB structural monitor, with separate structural-intelligence, technical-risk, report, method, verification, contact, payment, and policy pages. Technical-risk records live below `/technical-risk/`; research and method artifacts remain directly addressable.

The paid-readiness layer adds five primary product surfaces without deleting existing routes: `/`, `/cases/800vdc/`, `/verify/`, `/decision-pack/`, and `/context/`. Method and research remain available below the primary customer journey.

## REUSABLE_COMPONENTS

- Existing static header/footer, responsive CSS, semantic HTML, manual contact path, and canonical-URL convention.
- New shared product assets: `assets/product.css` and `assets/product.js`.
- Shared component patterns: evidence-state badge, evidence record, unknown-gap card, decision transition, research boundary, counter-evidence card, dependency path/transfer map, deliverable preview, paid-work boundary, and customer-context form.

## CURRENT_PRODUCT_GAPS

Before the upgrade the homepage led with digital-asset monitoring, primary navigation exposed internal/product-domain labels, no flagship 800V product case existed, the difference between public evidence and paid work was not explicit, deliverable structures were not previewed, and company context could not be collected in a decision-first form.

## CURRENT_DATA_SOURCES

- Canonical CML case and PDRE records under `technical-risk/cml-v1.1/pdre/CML-PDRE-001/`.
- Frozen L1 verification under `rdl/research/records/CML-PDRE-001-L1-FIELD-DEPLOYMENT-2026-09-20/`.
- Phase-2 dependency and qualification mappings under `rdl/research/records/CML-PDRE-001-PHASE-2/`.
- Evidence Core schema under `evidence/core/schema/`.

No external research was performed for this upgrade.

## CURRENT_FORM_CAPABILITY

The site has no server-side form or upload endpoint. Existing service contact is email/WhatsApp. The new forms use native required-field validation and prepare an email for user review. File uploads are intentionally not rendered; users are told to exchange documents only after scope and privacy boundaries are agreed.

## CURRENT_DEPLOYMENT_BOUNDARY

The public site is a static GitHub Pages-style tree with a Cloudflare landing proxy configuration under `deploy/cloudflare-landing/`. Root and `docs/` are mirrored. This implementation does not change backend architecture, add analytics vendors, implement payment, or deploy automatically.
