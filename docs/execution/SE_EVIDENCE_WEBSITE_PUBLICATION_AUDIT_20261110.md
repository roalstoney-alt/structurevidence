# StructEvidence Evidence-to-Website Publication Audit — 2026-11-10

Project: `SE-E2W-RELEASE-20261110`
Baseline main: `4a57c5fb5cb2aef682058c0902d83c727f5610f1`
Baseline production: GitHub Pages deployment `7667743321`, SHA `4a57c5fb5cb2aef682058c0902d83c727f5610f1`
Mode: `APPEND_ONLY / MINIMAL_WEBSITE_PROJECTION`

## Scope and method

The audit covered all 57 GitHub pull requests reported as merged at the time of the audit and all ten deduplicated case/research chains present in the repository or case discovery surface. Records were deduplicated by stable case ID, evidence event ID and source lineage. Technical maintenance PRs were inspected but were not treated as new cases.

- Case/evidence/research-related merged PRs: `#1, #3, #4, #5, #21, #22, #24, #25, #27, #28, #31, #33, #34, #35, #38, #39, #40, #41, #42, #43, #46, #47, #48, #49, #50, #51, #52, #53, #57, #58, #59, #60, #65, #67, #68, #74, #75, #88`.
- Technical, presentation, operations, governance or infrastructure PRs with no separate case-page obligation: `#2, #6, #7, #8, #9, #10, #11, #12, #13, #14, #16, #17, #18, #19, #20, #30, #45, #54, #79`.

The public release gate applied to each record was:

`MERGED_TO_MAIN → SOURCE_PROVENANCE → CLAIM_BOUNDARY → EVIDENCE_LINEAGE → HISTORY_IMMUTABILITY → PUBLIC_DISCLOSURE → PUBLIC_PROJECTION_ACCURACY → SITE_INTEGRATION`

Independent third-party verification was not required to publish an attributable public claim. Source role and unverified conditions were required to remain explicit.

## Record audit

| Case ID | Related PR numbers | Latest controlling merge/content SHA | Evidence completeness | Current website URL | Previous publication status | Release-gate result | Publication decision | Final website URL | HTTP verification | Remaining unknowns or blockers |
|---|---|---|---|---|---|---|---|---|---|---|
| `CML-PDRE-001` | #5, #21, #22, #31, #38, #39, #40, #48, #49, #50, #51, #52, #88, #89 | `64bab7e87d51b1a96134a1a0cd74c0f6b1b5e554` | Complete Envision event, claim, state transition, provenance and hashes; earlier Vantage route existed but was omitted from the append-only event ledger | `https://structurevidence.org/cases/800vdc/` | `PUBLISHED_STALE` | PASS for Envision; PASS for bounded Vantage ledger reconciliation | Protected v0.1 case page preserved byte-for-byte; Envision event route published and both missing events appended to the event ledger | `https://structurevidence.org/cases/800vdc/events/envision-galaxy-800vdc-2026/` | HTTP 200 and deployed-byte hash match | Independent acceptance, commissioned IT MW, protection testing, long-term operation and measured economics remain `UNKNOWN`; planned 3GW is not commissioned load |
| `SE-BESS-SODIUM-001` | #1, #4, #5, #40, #43 | `fcfb499778d2fcc6b4d604e8786bd74d692d8e55` | Public state, evidence, counter-evidence, unknowns and decision memory present | `https://structurevidence.org/cases/sodium-ion-bess/` | `PUBLISHED_VERIFIED` | PASS | No substantive change; do not republish | Same | Baseline 200 | Named commissioned site and independent field performance remain not established |
| `SE-ONC-NSQNSCLC-CN-001` | #3, #4, #5, #33, #40, #43 | `62acc0e4a6773bcf6014eb759b362978cf5efe6a` | Public research preview, bounded claims, stop point and publication control present | `https://structurevidence.org/cases/nsq-nsclc-china/` | `PUBLISHED_VERIFIED` | PASS | No substantive change | Same | Baseline 200 | No patient-specific probability or individualized treatment conclusion |
| `SE-IRK-LAB-001` | #21, #22, #24, #25, #27, #33, #34, #35, #40, #43 | `d435fe84144f13391a2a66fca8d0f1fe01c861d6` | Public sources, state history, corrections and ECDC event preserved | `https://structurevidence.org/cases/irkutsk-lab-worker-death/` | `PUBLISHED_VERIFIED` | PASS | No substantive change | Same | Baseline 200 | Cause, pathogen link, laboratory accident and final risk assessment remain unresolved |
| `SE-IREN-AI-CLOUD-001` | #53, #54, #57, #58, #59, #60, #65 | `ea1dff9e53725e49d64d595d362b3baa63fe7047` | Public tracker, claim rows, sources, events, approval and DDR entry present | `https://structurevidence.org/cases/iren-ai-cloud-transition/` | `PUBLISHED_VERIFIED` | PASS | No substantive change | Same | Baseline 200 | Contracted, operating, recognized and collected states remain distinct |
| `SE-BINANCE-SECURITY-001` | #67, #68, #74, #75 | `1581abdf764f04517e909cece09ecc4d0d8eea05` | Time-bounded public record, claims, sources, on-chain observations and transitions present | `https://structurevidence.org/cases/binance-security-2026/` | `PUBLISHED_VERIFIED` | PASS | No substantive change | Same | Baseline 200 | Six open claims and independent verification boundaries remain visible |
| `SE-PHYSICAL-AI-001` | #41, #42, #68 | `440b3ae7e2ff2ad1b28577b401cce55d67ed0a09` | External provisional study is explicitly separated from the six on-site trackers | External GitHub research URL linked from `/cases/` | `PUBLISHED_VERIFIED` | PASS as an external provisional link | No substantive change | Same external URL | Baseline link present | Not industrial certification; external repository remains the canonical record |
| `SE-OPEN-CIV-001` | No merged PR number identified; direct content commit | `84e945b4e0c702228bec52d7fd095f7a5f1b7663` | Public theoretical inquiry with explicit hypothesis limits | `https://structurevidence.org/cases/civilization-under-irreversible-time/` | `PUBLISHED_VERIFIED` | PASS as open research, not an evidence tracker | No substantive change | Same | Baseline 200 | Hypotheses remain not established |
| `SE-EKN-001` | #28 | `5a3bd2883af40969c5ca63c0581d15afdc7b30b4` | Frozen decision audit and limitations present | `https://structurevidence.org/cases/ekn-necessity/` | `PUBLISHED_VERIFIED` | PASS as a frozen decision audit | No substantive change | Same | Baseline 200 | `HOLD_NEEDS_EVIDENCE`; platform deployment is not implied |
| `RDL-DOD-BEAM-001` | No merged PR number identified; direct content commits | `7ffcb7319ca7f0137f5698fa812d4de19023e8f9` | Narrative page exists, but no complete machine-readable source registry, claim ledger and state lineage equivalent to current public-case gates | `https://structurevidence.org/cases/beam/` | `INCOMPLETE_CHAIN` | BLOCKED | Preserve existing page; do not promote or add discovery links in this release | Same existing route | Baseline route checked separately | Formal evidence lineage and publication-control gate remain incomplete |

## Counts before release

- Merged PRs audited: **57**
- Deduplicated evidence/case/research records audited: **10**
- `PUBLISHED_VERIFIED`: **8**
- `PUBLISHED_STALE`: **1**
- `MERGED_NOT_PUBLISHED`: **0**
- `INCOMPLETE_CHAIN`: **1**
- `INTERNAL_ONLY`: **0**
- New release candidates passing every gate: **1** (`CML-PDRE-001` Envision projection)
- Blocked records: **1** (`RDL-DOD-BEAM-001` formal chain incomplete)
- Newly published pages planned: **1**

## Envision publication boundary

- Evidence classification: `PUBLIC_EVIDENCE_CHAIN`.
- Source role: `OPERATOR_AUTHORED`.
- Claim status: `OPERATOR_REPORTED_LIVE_DEPLOYMENT`.
- Named site: Galaxy AI Data Center, Ulanqab, China.
- Architecture: `10kV AC → SST → 800VDC`.
- Evidence event: `CML-PDRE-001-EV-ENVISION-20261108-001`.
- Claim: `ENVISION_GALAXY_800VDC_LIVE_DEPLOYMENT`.
- Evidence cutoff: `2026-11-09T21:54:45Z`.
- Independent acceptance, installed IT MW, protection tests, long-term operating data and measured economic benefits remain `UNKNOWN`.
- The announced 3GW capacity is planned capacity, not commissioned load.
- Complete third-party articles are not redistributed.

## Pre-release verification

- All ten existing public case/research routes returned HTTP 200 on 2026-11-10.
- The new event page, machine-readable projection and case-index link were exercised in a real local browser preview. The index link is generated from the event projection's explicit `case_index_visible` flag; deterministic regeneration preserves the prior review clock.
- The PR Newswire source and complete GitHub evidence-record links returned HTTP 200. The Energy-Storage.news URL returned HTTP 403 to a non-browser `curl` request but loaded successfully in the real browser; this retrieval behavior is not treated as evidence absence.
- Internal-link audit: zero broken links, zero orphan pages, zero cases without state and zero evidence pages without a parent.
- Release-specific tests: 7/7 PASS. Envision append/integrity tests: 15/15 PASS. Source-dependency tests: 21/21 PASS. History/SEO unit tests: 12/12 PASS. Case-watch validation groups: 9/9 PASS.
- `test_agent_discovery.py` reports two failures at both the exact production baseline and the release worktree (`test_f_claim_projection_determinism` and `test_t_u_v_existing_histories_and_snapshots_are_immutable`); they are preserved baseline observations, not new regressions.
- Public-disclosure scan found no credentials, tokens, private customer contacts, restricted business records or absolute local filesystem paths in the release set.

## Production architecture and rollback

Production is GitHub Pages from `main:/docs`. The baseline deployment ID is `7667743321`. The release changes only a new mirrored event projection, the existing case-index generator and its generated CML row, the append-only event ledger, sitemap entries, release tests and public audit receipts. The protected v0.1 case HTML and JSON remain byte-for-byte unchanged. The index addition links the new event, explicitly says the canonical state is unchanged and does not advance the prior review clock. The release does not modify Cloudflare Workers, D1, commercial workflows, schedules or the evidence-chain source records.

Rollback is a normal Git revert of the website release merge commit followed by the existing GitHub Pages deployment. No database or Worker rollback is required.

## Post-deployment verification

- Release PR: `#89`; merge SHA: `64bab7e87d51b1a96134a1a0cd74c0f6b1b5e554`.
- GitHub Pages deployment: `7668361028`; workflow run: `42716111884`; completed successfully at `2026-11-09T23:00:54Z`.
- The event HTML, machine projection, case index, event ledger, review-status projection and sitemap each returned HTTP 200 and matched the corresponding deployed `docs/` file byte-for-byte.
- A real production browser showed the required case ID, claim boundary, sources, timestamps, unknowns, state transition, GitHub record link and case-index entry.
- The protected CML v0.1 page retained SHA-256 `06c69bfdbca2ccb5bce25c487319d04ecd5067eea7ff54d2c9228f5f42222cfa`; the homepage retained SHA-256 `ec02fccc51782b481493d815133d89dd200a863af57ff2a038be9bd9dee76975`.
- Complete hashes and URL-level results are stored in `execution/SE_E2W_PRODUCTION_VERIFICATION_20261110.json`.

## Standard future workflow

`Evidence Acquired → Append-only Record → Claim Review → GitHub Merge → Website Projection Gate → Production Deployment → Live Verification`

Evidence merging must not automatically authorize website publication. Website projection must not modify the underlying evidence chain. No automatic publish-on-merge mechanism is introduced by this release.
