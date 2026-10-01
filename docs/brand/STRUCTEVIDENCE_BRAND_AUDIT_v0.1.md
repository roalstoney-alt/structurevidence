# StructEvidence Brand Audit v0.1

Audit date: 2026-10-01
Target public brand: `StructEvidence`
Protected research domain: `structurevidence.org`
Protected commercial domain: `structevidence.com`

## Method

The tracked repository was searched case-sensitively and case-insensitively for the three legacy display forms:

- `Structure` + `Evidence`
- `STRUCTURE` + `EVIDENCE`
- `Structure` + space + `Evidence`

Tracked paths were searched separately so filename and machine-identifier exceptions are not hidden by a content-only search. Generated public HTML and current page/export generators were audited after running `python3 scripts/export_public_records.py`.

## Result

| Classification | Count | Result |
| --- | ---: | --- |
| A. `PUBLIC_DISPLAY_NAME` | 0 | PASS |
| B. `HISTORICAL_RECORD` | 70 | Allowed; frozen/versioned records are not rewritten |
| C. `DOMAIN_OR_PATH` | 2 | Allowed; references preserve the existing PDF URL and filename |
| D. `FILENAME_OR_MACHINE_IDENTIFIER` | 8 content references + 3 tracked filenames | Allowed; identifiers are not renamed |
| E. `COMMENT_OR_INTERNAL_NOTE` | 1 | Allowed; validator module description only |

`PUBLIC_DISPLAY_NAME_LEGACY_COUNT = 0`

`ALLOWED_LEGACY_IDENTIFIER_COUNT = 84` (81 tracked-content occurrences plus 3 tracked filenames)

## Remaining tracked-content occurrences

Every remaining content occurrence is listed below. Line numbers refer to this audited revision.

| File | Lines | Count | Classification | Reason |
| --- | --- | ---: | --- | --- |
| `.gitignore` | 16, 19, 22 | 3 | D | Preserve the published PDF filename |
| `cases/800vdc/stop-v0.1.html` | 2, 3, 5 | 3 | B | Frozen v0.1 citation surface; protected by historical-integrity tests |
| `cases/nsq-nsclc-china/stop-v0.1.html` | 2, 3, 5 | 3 | B | Frozen v0.1 citation surface; protected by historical-integrity tests |
| `cases/sodium-ion-bess/stop-v0.1.html` | 2, 3, 5 | 3 | B | Frozen v0.1 citation surface; protected by historical-integrity tests |
| `cases/sodium-ion-bess/decision-memory-v0.1.json` | 369, 430 | 2 | B | Frozen decision-memory v0.1 record |
| `deploy/cloudflare-landing/commercial-upgrade.js` | 12, 14 | 2 | C | Existing public PDF URL/path only |
| `deploy/cloudflare-landing/test/commercial-upgrade.test.js` | 36 | 1 | D | Assertion for the unchanged PDF filename |
| `docs/cases/800vdc/stop-v0.1.html` | 2, 3, 5 | 3 | B | Frozen v0.1 citation mirror |
| `docs/cases/nsq-nsclc-china/stop-v0.1.html` | 2, 3, 5 | 3 | B | Frozen v0.1 citation mirror |
| `docs/cases/sodium-ion-bess/stop-v0.1.html` | 2, 3, 5 | 3 | B | Frozen v0.1 citation mirror |
| `docs/cases/sodium-ion-bess/decision-memory-v0.1.json` | 369, 430 | 2 | B | Frozen decision-memory v0.1 mirror |
| `docs/product/COMMERCIAL_DOMAIN_SPLIT_V2_EXECUTION_REPORT.md` | 1 | 1 | B | Historical execution-report title |
| `evidence/decision-memory/schema/decision-memory-record.schema.json` | 4 | 1 | B | Frozen v0.1 canonical schema title |
| `research-snapshot/v0.1/README.md` | 1, 3 | 2 | B | Frozen v0.1 research snapshot |
| `research-snapshot/v0.1/method-contract.json` | 2 | 1 | B | Frozen v0.1 method snapshot |
| `research-snapshot/v0.1/protocol/state-normalization/schema-v0.1.json` | 4 | 1 | B | Frozen v0.1 schema snapshot |
| `research/STRUCTEVIDENCE_METHOD_PAPER_AND_REPLICATION_KIT_v0.1/README.md` | 25, 31 | 2 | B | Versioned method-paper package |
| `research/STRUCTEVIDENCE_METHOD_PAPER_AND_REPLICATION_KIT_v0.1/paper/ABSTRACTS_AND_KEYWORDS.md` | 9, 13, 17, 21 | 4 | B | Published paper title and abstract text |
| `research/STRUCTEVIDENCE_METHOD_PAPER_AND_REPLICATION_KIT_v0.1/paper/STRUCTEVIDENCE_METHOD_PAPER_EN_v0.1.md` | 6, 42, 54, 66, 70, 74, 78, 82, 94, 137, 480, 546, 553 | 13 | B | Published English paper; title/content frozen with DOI record |
| `research/STRUCTEVIDENCE_METHOD_PAPER_AND_REPLICATION_KIT_v0.1/paper/STRUCTEVIDENCE_METHOD_PAPER_ZH_v0.1.md` | 6, 35, 54, 60, 374, 425 | 6 | B | Published Chinese paper; title/content frozen with DOI record |
| `research/STRUCTEVIDENCE_METHOD_PAPER_AND_REPLICATION_KIT_v0.1/publication/MEDIUM_DRAFT_EN.md` | 9, 11 | 2 | B | Historical publication draft |
| `research/STRUCTEVIDENCE_METHOD_PAPER_AND_REPLICATION_KIT_v0.1/publication/PUBLIC_LAUNCH_NOTE.md` | 1, 3, 32 | 3 | B | Historical v0.1 launch record |
| `research/STRUCTEVIDENCE_METHOD_PAPER_AND_REPLICATION_KIT_v0.1/publication/ZHIHU_DRAFT_ZH.md` | 13, 160 | 2 | B | Historical publication draft |
| `research/STRUCTEVIDENCE_METHOD_PAPER_AND_REPLICATION_KIT_v0.1/release/CODEX_PUBLICATION_WORKFLOW.md` | 66 | 1 | B | Historical release commit message |
| `research/STRUCTEVIDENCE_METHOD_PAPER_AND_REPLICATION_KIT_v0.1/release/LICENSE_RECOMMENDATION.md` | 17, 22 | 2 | B | Versioned release/legal recommendation |
| `research/STRUCTEVIDENCE_METHOD_PAPER_AND_REPLICATION_KIT_v0.1/replication/CHALLENGE_SUBMISSION_TEMPLATE.md` | 1 | 1 | B | Versioned v0.1 replication-kit artifact |
| `research/STRUCTEVIDENCE_METHOD_PAPER_AND_REPLICATION_KIT_v0.1/replication/REPLICATION_AND_CHALLENGE_PROTOCOL_v0.1.md` | 5, 17 | 2 | B | Versioned v0.1 replication protocol |
| `research/STRUCTEVIDENCE_METHOD_PAPER_AND_REPLICATION_KIT_v0.1/spec/METHOD_CONTRACT_PUBLIC_v0.1.md` | 1, 7 | 2 | B | Versioned v0.1 public method contract |
| `research/STRUCTEVIDENCE_METHOD_PAPER_AND_REPLICATION_KIT_v0.1/spec/QUESTION_TO_EVIDENCE_PROTOCOL_SPEC_v0.1.md` | 4, 186 | 2 | B | Versioned compatibility baseline/specification |
| `scripts/build_800vdc_decision_pack_sample.py` | 23 | 1 | D | Output filename is an existing public machine identifier |
| `scripts/validate_case_watch.py` | 2 | 1 | E | Internal validator module description; does not emit public content |
| This audit's protected-filename list | three entries below | 3 | D | Documentation references to the unchanged public PDF filename |

## Remaining tracked filenames

These paths remain unchanged because renaming them would break existing URLs and external references:

- `docs/reports/STRUCTUREEVIDENCE_800VDC_DECISION_PACK_SAMPLE_v1.0.pdf`
- `output/pdf/STRUCTUREEVIDENCE_800VDC_DECISION_PACK_SAMPLE_v1.0.pdf`
- `reports/STRUCTUREEVIDENCE_800VDC_DECISION_PACK_SAMPLE_v1.0.pdf`

## Acceptance

Current public HTML, metadata, JSON-LD, schemas, locale text, active presentation JavaScript, and active generators emit `StructEvidence`. The remaining legacy strings are confined to immutable historical records and protected paths/machine identifiers. Domains, canonical URLs, DOI records, IDs, evidence states, and conclusions remain unchanged.
