# SE-FRR-001 Phase 4A Test Report

Date: 2026-09-26

## Results

| Suite | Result |
|---|---:|
| Phase 4A DSR | 10/10 pass |
| Phase 4A Discord bot/server specification | 8/8 pass |
| Complete SE-FRR Python suite | 44/44 pass |
| Worker regression suite | 49/49 pass |
| JSON schema parse | PASS |
| Phase 4A SQLite migration application | PASS |
| Discord JavaScript syntax | PASS |
| Discord registration approval guard | PASS |
| Unified SE-FRR validation | PASS; 15 objects, zero schema/reference/hash/chain/privacy errors |
| State-chain verification | PASS; two States, one valid chain |
| OpenAPI operation parity | PASS; 21 operations, 13 public, 8 protected |
| Wrangler deployment dry run | PASS; 185.02 KiB, no deployment |
| Frozen historical Python baseline | 255/258 pass; exactly two failures and one error match the three frozen exceptions |

The frozen historical exceptions remain:

1. Phase A history entry `ValueError`.
2. Phase B `OV-B01_BASELINE_INTEGRITY`: 12 pass, 1 fail, 3 not evaluated.
3. Phase B-R1 `OV-R101_ACCEPTED_WAVE1_BASELINE`: 7 pass, 1 fail.

No fourth historical failure appeared. New unexplained failures: 0.

## Phase 4A coverage

Tests cover the exact DSR schema, scoring boundaries, State mapping, HTTPS-only sources, unexpected/private-field rejection, URL and semantic deduplication, qualified queues, candidate drafts, unmapped high-value preservation, daily reporting, disabled payments, public-source capability policy, command behavior, API-only State and Change reads, protected Request and Challenge redirects, mention suppression, invite-only configuration, member cap, least privilege, and the no-automatic-invite boundary.

The command registration program was also executed without the human approval flag and correctly failed closed before reading credentials or making a network request.
