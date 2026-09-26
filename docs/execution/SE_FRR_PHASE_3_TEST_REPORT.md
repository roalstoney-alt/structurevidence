# SE-FRR-001 Phase 3 Test Report

Date: 2026-09-26

## Results

| Suite | Result |
|---|---:|
| Historical Python baseline | 255/258 pass; two failures and one error exactly match the three frozen exceptions |
| Phase 1 protocol | 26/26 pass |
| Phase 2 Python materializer/contract | 8/8 pass |
| Phase 2 API behavior | 23/23 pass (included in Worker total) |
| Phase 3 product/security | 13/13 pass |
| Worker total | 49/49 pass |
| Unified SE-FRR validation | PASS; 15 objects, zero schema/reference/hash/chain/privacy errors |
| State-chain verification | PASS; two States, one valid chain |
| OpenAPI operation parity | PASS; 21 operations, 13 public, 8 protected |
| Wrangler deploy dry-run | PASS; 183.50 KiB, no deployment |

The frozen historical exceptions remain:

1. Phase A history entry `ValueError`.
2. Phase B `OV-B01_BASELINE_INTEGRITY`: 12 pass, 1 fail, 3 not evaluated.
3. Phase B-R1 `OV-R101_ACCEPTED_WAVE1_BASELINE`: 7 pass, 1 fail.

The full historical suite was rerun after the implementation commit so dirty-worktree detection could not mask a regression. No fourth failure remained.

## Phase 3 coverage

Tests cover route rendering, State metadata, State history links, semantic fields, temporal UI markers, evidence categories, Request/Challenge copy and routing, Access-protected Outcome, 404/method failure, empty production projection, privacy-safe telemetry, founding configuration, noindex/no-store, sitemap/robots exclusion, responsive CSS, and bounded share metadata.

Browser-client syntax is compiled with `new Function(PRODUCT_APP_JS)` before the Worker suite. Local preview HTTP returned 200 for `/states` and a valid `SE_API_v1` Subject response.
