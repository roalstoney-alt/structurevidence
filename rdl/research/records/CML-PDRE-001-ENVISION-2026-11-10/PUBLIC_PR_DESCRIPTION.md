# CML-PDRE-001: admit Envision operator-reported live deployment evidence

## Scope

This change adds one `PUBLIC_EVIDENCE_CHAIN` record for Envision's public Galaxy AI Data Center announcement. It contains source identity and retrieval metadata, hashes of bounded source extractions, one evidence event, one claim record, one evidence-state transition, one daily case-watch observation, integrity receipts, and replay tests.

No customer contacts, inquiries, quotations, contracts, negotiations, credentials, internal acquisition scoring, production deployment, or social publication are included.

## Evidence boundary

- `SOURCE_ROLE=OPERATOR_AUTHORED`
- `CLAIM_STATUS=OPERATOR_REPORTED_LIVE_DEPLOYMENT`
- `INDEPENDENT_ACCEPTANCE=UNKNOWN`
- `MEASURED_IT_LOAD=UNKNOWN`
- `ECONOMIC_BENEFITS=UNKNOWN`

The record establishes what Envision publicly reported. It does not independently prove commissioning acceptance, installed IT load, protection performance, long-duration operation, industry adoption, or economic benefit. The reported August 2026 campus opening remains separate from the unknown SST/800VDC commissioning date. Planned 3GW capacity is not treated as commissioned load.

## Sources

- Original Envision-authored distribution: https://www.prnewswire.com/news-releases/envision-achieves-worlds-first-commercial-deployment-of-integrated-800v-dc-sst-based-power-system-in-large-scale-ai-data-center-302926109.html
- Envision-byline industry update: https://www.energy-storage.news/industry-updates/envision-achieves-worlds-first-commercial-deployment-of-integrated-800v-dc-sst-based-power-system-in-large-scale-ai-data-centre/

## Verification

- Envision append tests: PASS
- Case-watch schema and controls: PASS
- Existing EVP and case-watch regressions: PASS
- History Guard: PASS
- SHA-256 manifest: PASS
- Same-source replay: `DUPLICATE_NOOP`
- New regression count: 0

Six failures reproduced identically on the locked `origin/main` baseline remain documented as pre-existing observations; this change does not modify those tests or affected historical files.

## Release control

Prepared for public GitHub review only. Push, PR creation, merge, deployment, procurement, outreach, and social publication require their separately authorized gates.
