# SE-CML-OV-001 — Phase A architecture

Phase 0.5 / CML Opportunity Validation v0.1. This implementation initializes architecture only. Implementation Phase A is distinct from analytical layer A (Problem Persistence). No empirical Opportunity Validation has been performed. The authorization is section 7 of `docs/handoff/CML_PERSONAL_CODEX_HANDOFF_2026-09-16.md`; its continuation scope supersedes the historical SNIPE development wording without changing that report.

## Evidence Core and storage

One Evidence Core, shared file-backed record store, Technical Risk domain, existing RDL and GDR. Each new record uses the unchanged `evidence/core/schema/evidence_core_record.schema.json` envelope, `domain = TECHNICAL_RISK`, `protocol = CML`, and the original subject ID. OV fields live in the `opportunity_validation` domain payload. New records are stored below each existing `technical-risk/records/<slug>/opportunity-validation/` directory. The OV index is a typed index into this store, not a second evidence database. No source registry, provenance engine, freshness engine or Verify service is duplicated.

`technical-risk/opportunity-validation/schema/record.schema.json` is the normative Phase A schema. It is kept outside the frozen CML schema set, so the historical manifest and 108-path dictionary remain valid. The schema uses closed objects and requires all three layers. A schema-valid worked template is in `templates/phase-a-record.json`; it is OV-01 as an example, not a fifth record. Copying it alone does not initialize another record: identity, baseline, clocks, hashes, index and manifest must all reconcile.

## Exact initialization mapping

| OV | Existing subject | Scope | Preserved lifecycle |
| --- | --- | --- | --- |
| OV-01 | Amphenol 10081811-101-07LF | Exact part | EOL_ANNOUNCED |
| OV-02 | Murata MYMGM5R012ELA5RND | Exact suffix | NRND |
| OV-03 | Amphenol RF 095-725-134-006 | Exact assembly | ACTIVE |
| OV-04 | NXP Radio Power 2026 | Family event | LAST_TIME_BUY_OPEN |

OV-04 preserves the existing family subject ID. It does not promote `RADIO-POWER-2026-FAMILY` into an orderable MPN or assert interchangeability among MRF101AN, MW6S010GNR1 and MMRF1009HR5. Later application assessment requires exact selected devices. OV-03 remains an active benchmark, not a lifecycle crisis.

## Three analytical layers

Each assessment cell has `state = NOT_ASSESSED`, `value = null`, `evidence_refs = []`. Null is unknown, never zero, false, no pain or no opportunity. An empty evidence list means no OV assessment evidence has been supplied, not that the baseline has no technical evidence.

| Payload path | Required questions represented |
| --- | --- |
| `problem_persistence` | Does the original problem persist? Is there active customer pain? Which application is affected? Has it been handled internally? |
| `current_solution_audit` | Current handling, technical performance, solution efficiency, constraints, operating cost and switching barriers |
| `solution_improvement_potential` | Modern design, verification and manufacturing potential; measurable improvement; metric, unit, baseline, target, scope, method, acceptance criteria and net benefit |
| `solution_improvement_potential.cost_assessment` | Unit cost, engineering/redesign, tooling, verification, qualification, certification, manufacturing transition, downtime, supply/logistics, lifetime operation, total migration cost and comparison horizon |

These 34 cells are placeholders, not proposed designs, suppliers, metrics or test plans. Existing technical verification requirements are referenced separately as historical requirements, not executed tests. Existing unknowns, counter-evidence and limitations remain accessible through the immutable baseline reference. Original source facts and recommendations stay in the original record; they are not relabeled as OV findings.

The six continuation laws apply independently: public technical risk is not active customer pain; existing solution is not efficient solution; technically working is not economically optimal; internal resolution is not no opportunity; alternative exists is not alternative qualified; lower unit price is not lower total migration cost. In particular, unresolved lifecycle evidence cannot establish pain, and internal resolution cannot automatically reject an opportunity. No score or replacement probability is introduced.

## Vocabulary and future transitions

`STATUS_VOCABULARY.json` defines the implemented vocabulary. Record state is `INITIALIZED_UNASSESSED`; assessment and opportunity qualification are `NOT_ASSESSED`; client scope is `NOT_PROVIDED`. Phase A schemas deliberately cannot represent a positive/negative empirical finding or a qualified opportunity. Later work needs explicit authorization and a versioned schema/policy extension, evidence for a defined application, counter-evidence, review of current handling, and a measurable comparison including total migration and qualification costs. Technical qualification remains a separate CML dimension. No automatic state promotion is available.

## Provenance, clocks and history

The baseline is pinned to handoff commit `19be538447a90672491768d818fa07e3dd3dd377`, its canonical record hash and release-manifest byte hash. Validators check all 12 baseline files against that commit and the original release artifact commitments. Manufacturer identity, exact suffix, lifecycle, qualification, replacement state, freshness, material unknowns and conflicting evidence are preserved.

OV initialization is a `RESEARCH_EVENT`. Its core effective/known/created/updated clocks describe the initialization and equal the manifest initialization timestamp. The baseline subject-event effective and known clocks remain separately preserved; initialization never redates a manufacturer event. Existing source references and artifact lineage are reused, with byte-bound references to the baseline record and release manifest.

Canonical hashing follows CML's existing ASCII JSON, sorted keys and compact separators. `input_hash = SHA256({sources: baseline, payload: opportunity_validation})`; `record_hash = SHA256({core: core_without_record_hash, payload: opportunity_validation})`. `PHASE_A_MANIFEST.json` commits to record, schema, vocabulary, template and index file bytes, excludes itself, and is explicitly initialization integrity only. It is not a release manifest. Repository history commits validator code and documentation; the initialization manifest does not claim to commit those files.

Existing CML version history receives one appended entry and its docs mirror. Future corrections or supersession require a successor record/version with directional predecessor references and retained prior artifacts; do not edit this initialized version to imply it was assessed earlier. The original CML record is a baseline, not a superseded predecessor. Frozen Timeline, LEVEL, DELTA and NO OBSERVATION semantics are untouched.

## RDL, GDR and private boundary

Baseline freshness is historical context, not newly refreshed evidence. OV assessment freshness is independently `POLICY_NOT_CONFIGURED`, reason `OV_ASSESSMENT_CADENCE_NOT_CONFIGURED`, rule `UNCONFIGURED`; there is no component-age threshold. The validator invokes the existing GDR CML adapter for the baseline and adds a Phase A veto. Both OV public release and paid delivery remain `BLOCK`, even if a baseline public method pilot is allowed with limitations. Solution development is `NOT_AUTHORIZED`. Successful architecture validation is not commercial authorization.

These are public-safe repository artifacts only. They are not registered in Public Verify or the public record index, and no UI, deployment or paid flow is added. Intentional root/docs mirrors contain identical public-safe initialization data. The closed schema and recursive configured private-key checks reject client BOM, pricing, inventory, drawings, limits, NDA, raw lab data and other reserved fields. Actual future private context needs an authorized private storage/review workflow; it must never be entered into these artifacts or mirrors. Structured checks cannot classify arbitrary secrets hidden in prose; Phase A therefore accepts only exact baseline prose and null assessment values. Baseline GDR hard blocks remain in force; no alternate release grant exists.

## Executable gates and validation

Run `python3 scripts/validate_cml_ov_phase_a.py` for read-only computed results; no historical audit outputs are rewritten. Seven distinct per-record validators cover schema, immutable baseline, shared envelope/clocks, canonical hashes, unassessed cells, private boundary and release/freshness governance. The package validator checks exact mappings, complete manifest coverage, mirrors, a valid worked template and append-only history. A malformed record fails closed.

Run `python3 scripts/test_cml_ov_phase_a.py` for positive and adversarial cases: fabricated pain/efficiency/improvement, unit-cost shortcuts, private fields, numeric scores, baseline drift, identity and clock drift, correction/supersession, release/freshness promotion, missing layers and extra qualification claims. Existing frozen gate functions may be invoked read-only except historical CML01 and CML35; never run the writing `test_cml_v01.py` entry point to regenerate the accepted historical release.

Stop after Phase A. Customer pain, current handling, solution efficiency, application constraints, measurable improvement, cost/benefit and qualification remain unresolved. No external research, outreach, samples, lab commission, replacement design or supplier selection is included.
