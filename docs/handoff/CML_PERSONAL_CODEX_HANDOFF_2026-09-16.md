# StructEvidence Technical Risk / CML — Personal Codex handoff

Date: 2026-09-16. This document is self-contained continuation context for a Personal ChatGPT/Codex workspace with zero access to the prior Business conversation. Repository files are the evidence authority.

This change is HANDOFF ONLY: no Opportunity Validation implementation, new research, scientific finding changes or product features. The next-session authorization below is not work performed by this handoff.

## 1. Repository state

| Field | Pre-handoff snapshot |
| --- | --- |
| Repository | `roalstoney-alt/structurevidence` |
| Origin | `git@github.com:roalstoney-alt/structurevidence.git` |
| Current branch | `main` |
| Current HEAD / PRE_HANDOFF_SHA | `ecf81585fa5f495dfa0a31ddccfcef351d182801` |
| origin/main SHA | `ecf81585fa5f495dfa0a31ddccfcef351d182801` |
| Live remote main (verified with git ls-remote) | `ecf81585fa5f495dfa0a31ddccfcef351d182801` |
| Worktree status before handoff | Clean; main aligned with origin/main |
| Latest implementation SHA | `088012605a7b731ce2b868c87eef8c9af986a94a` — Harden CML v0.1 audit closure |
| Latest audit-closure SHA | `ecf81585fa5f495dfa0a31ddccfcef351d182801` — Close CML v0.1 audit hardening |

The implementation SHA is corroborated by the final audit report, manifest build_commit and version history. The handoff commit is a successor to this snapshot, not a new implementation version. Resolve its SHA after commit with `git log -1 --format=%H -- docs/handoff/CML_PERSONAL_CODEX_HANDOFF_2026-09-16.md`; do not insert a self-referential commit hash into this document.

## 2. Frozen current state

```text
CML_PROTOCOL = CML_v0.1
METHOD_PILOT = ACCEPTED
TECHNICAL_RISK_ARCHITECTURE = FROZEN
SITE_INTEGRATION = CML_SITE_INTEGRATION_v0.1a
AUDIT_POLICY = CML_AUDIT_v0.1a
CML01-CML40 = independently evaluated
RDL_FRESHNESS_INTEGRATION = PASS
GDR_CML_RELEASE_SEMANTICS = PASS
DATA_DICTIONARY = COMPLETE / SCHEMA_DERIVED
VERSION_HISTORY = APPEND_ONLY / CURRENT
```

The frozen audit has 40 distinct validators, 40 PASS, zero FAIL and zero NOT_EVALUATED; the dictionary covers 108 authoritative paths. These are the accepted historical release results, not a claim that time-dependent evidence was refreshed by this handoff. Public release remains `METHOD_PILOT_ALLOW_WITH_LIMITATIONS`; method acceptance does not qualify a replacement or authorize paid decision delivery.

## 3. Important architecture

```text
ONE EVIDENCE CORE
+
SHARED STORAGE / RECORD SYSTEM
+
DOMAIN-SPECIFIC TECHNICAL RISK MODULE

structevidence.com = external discovery / acquisition
structurevidence.org = primary research / application environment
```

Technical Risk / CML is one StructEvidence evidence domain, not a separate product or database. Reuse the common envelope, canonical file-backed records, provenance, dual clocks, corrections, directional supersession, RDL freshness, GDR release governance, Verify and hash-bound manifests. Technical identities, lifecycle, compatibility and qualification live in the domain payload. Keep intentional root/docs mirrors consistent in future implementation work.

Pipeline: `Identity -> Event -> Dependency -> Evidence -> Alternative -> Verification -> Decision`.

Architecture references: `docs/architecture/CML_STRUCTEVIDENCE_INTEGRATION_ASSESSMENT_v0.1.md`, `docs/architecture/CML_UNIFIED_SITE_ARCHITECTURE_v0.1a.md`, and `technical-risk/CML_SITE_ARCHITECTURE_v0.1a.json`.

## 4. Frozen laws

```text
PUBLIC TECHNICAL RISK != ACTIVE CUSTOMER PAIN
EXISTING SOLUTION != EFFICIENT SOLUTION
TECHNICALLY WORKING != ECONOMICALLY OPTIMAL
INTERNAL RESOLUTION != NO OPPORTUNITY
ALTERNATIVE EXISTS != ALTERNATIVE IS QUALIFIED
LOWER UNIT PRICE != LOWER TOTAL MIGRATION COST
```

CML does not only search for unresolved problems. CML searches for problems that have not yet been solved efficiently. These continuation laws do not establish that any pilot has customer pain, an inefficient solution or a commercially viable improvement.

Preserve the existing evidence and release laws:

- Exact manufacturer and full part number/suffix govern identity; family similarity does not establish interchangeability.
- Manufacturer primary evidence governs lifecycle; distributor labels cannot override it. Preserve conflicting evidence visibly.
- Lifecycle state, replacement availability, source dependency and qualification state are separate dimensions. NRND is not EOL; an active benchmark must not be turned into a lifecycle crisis.
- Paper screening, OEM alternatives and connector-level ratings do not establish a qualified drop-in or complete-assembly performance. Qualification requires evidence for a defined application and test scope.
- Distinguish source facts, interpretation and decision recommendations; keep unknowns, limitations and counter-evidence explicit. Do not invent numeric risk scores or replacement probabilities.
- Preserve effective/event time and known/knowledge time, event-domain scoping, correction and supersession direction. Frozen LEVEL, DELTA and NO OBSERVATION semantics and existing scientific findings remain unchanged.
- Use canonical RDL states with reason and rule type; no global component-age threshold. Unsupported cadence remains `POLICY_NOT_CONFIGURED`.
- GDR remains the release/paid-delivery veto layer: invalidation, material correction, supersession, private context, absent primary sources/counter-evidence and unverified drop-in claims must not bypass release controls.
- Private BOM, pricing, inventory, drawings, application limits, NDA material and lab raw data never enter Public Verify. A public technical record is not a private customer assessment.
- Preserve canonical record hashes, artifact lineage, append-only history, and frozen Timeline and digital-asset evidence. No parallel evidence database or provenance system.

## 5. Existing pilots — unchanged baseline

OV labels below are the user-authorized mapping for future initialization, not evidence that Opportunity Validation records already exist. States and hashes are copied from the existing `11_PUBLIC_RECORD.json` files at the pre-handoff SHA, with manifest corroboration. Do not alter existing findings or infer present customer pain, solution efficiency or opportunity qualification from these states.

All four are public-evidence pilots with `client_scope = NOT_PROVIDED`, `PUBLIC_EVIDENCE_ONLY_NO_CLIENT_BOM`, and `REVIEWED_WITH_LIMITATIONS`. No client BOM, pricing, inventory, drawings, application limits, laboratory raw data or qualification approval is included. A paper candidate is never a qualified replacement.

### OV-01 / existing CML record — Amphenol 10081811-101-07LF

- Record: `SE.CML.RECORD.AMPHENOL.10081811-101-07LF.v0.1`.
- Source directory: `technical-risk/records/amphenol-10081811-101-07lf/`.
- Current lifecycle state: `EOL_ANNOUNCED`.
- Current qualification state: `LAB_VERIFICATION_REQUIRED`.
- OEM replacement state: `OEM_REPLACEMENT_NOT_LISTED`.
- Freshness: `CURRENT_WITH_LIMITATIONS`; `CONFLICTING_PRIMARY_LIFECYCLE_EFFECTIVE_DATE`.
- Current canonical record hash: `e665909621d08fe0c1049a1a09775d69e101856ed3b9305c500f887e8c2af51f`.

Material unknowns (existing record):

- An OEM-approved replacement is not established by the reviewed evidence.
- Exact footprint, mating and plating equivalence for any third-party candidate is not established.
- A second Amphenol EOL listing with a different effective date requires manufacturer clarification.

Current evidence limitations / counter-evidence: A later public Amphenol EOL list appears to include the same MPN under PCN 26043 with a different effective date. This may be an overlapping notice or later schedule and must be reconciled with Amphenol before procurement action. The common public-evidence limitations above apply to this record.

Existing factual context (unchanged):

- SOURCE_FACT: PCN 26 027 lists four affected BERGSTIK part numbers, including the exact MPN.
- SOURCE_FACT: Last-time buy is 2026-09-15; effective change is 2027-03-15; last shipment is 2027-09-15.
- SOURCE_FACT: The available-alternatives field is blank in the reviewed notice.

Preserve the original lifecycle label and dated context; this handoff does not recompute lifecycle or qualify any alternative.

### OV-02 — Murata MYMGM5R012ELA5RND

- Record: `SE.CML.RECORD.MURATA.MYMGM5R012ELA5RND.v0.1`.
- Source directory: `technical-risk/records/murata-mymgm5r012ela5rnd/`.
- Current lifecycle state: `NRND`.
- Current qualification state: `LAB_VERIFICATION_REQUIRED`.
- OEM replacement state: `OEM_REPLACEMENT_UNRESOLVED`.
- Freshness: `POLICY_NOT_CONFIGURED`; `EXACT_LIFECYCLE_EFFECTIVE_DATE_UNRESOLVED`.
- Current canonical record hash: `f18e8d0dd74abd6874d4325af895197e07bb10d331f2e18167891f28a6b3f9dd`.

Material unknowns (existing record):

- An exact OEM successor for this suffix is not established in the reviewed snapshot.
- Customer output setpoint, transient limits, EMI class and thermal environment are unknown.
- No bench comparison or customer qualification evidence is present.

Current evidence limitations / counter-evidence: The base series remains documented and only a specific suffix is visibly marked NRND. This may reduce immediate operational impact if the customer uses another orderable suffix; BOM identity must be exact. The common public-evidence limitations above apply to this record.

Existing factual context (unchanged):

- SOURCE_FACT: MYMGM5R012ELA5RND is marked NRND in the manufacturer datasheet.
- SOURCE_FACT: The series is a 12 A non-isolated DC-DC converter with 7.5-15 V input and a 10.5 x 9.0 x 5.0 mm package class.
- SOURCE_FACT: Murata maintains a separate discontinued/NRND index and a DC-DC cross-reference surface.

Preserve the original lifecycle label and dated context; this handoff does not recompute lifecycle or qualify any alternative.

### OV-03 — Amphenol RF 095-725-134-006

- Record: `SE.CML.RECORD.AMPHENOL-RF.095-725-134-006.v0.1`.
- Source directory: `technical-risk/records/amphenol-rf-095-725-134-006/`.
- Current lifecycle state: `ACTIVE`.
- Current qualification state: `LAB_VERIFICATION_REQUIRED`.
- OEM replacement state: `OEM_REPLACEMENT_UNRESOLVED`.
- Freshness: `POLICY_NOT_CONFIGURED`; `ACTIVE_BENCHMARK_HAS_NO_EMPIRICAL_CADENCE`.
- Current canonical record hash: `0616350e28fe26de50acc10877a7adf07ac1b033d6403c742dc6e011110e8b57`.

Material unknowns (existing record):

- No independent VNA trace, per-unit insertion-loss limit or return-loss acceptance curve is present.
- Power handling, phase stability and flex-life limits are not established in reviewed evidence.
- No alternate supplier assembly has been qualified against this benchmark.

Current evidence limitations / counter-evidence: The item is an active off-the-shelf assembly, so substitution may not be operationally necessary. The pilot tests whether CML can structure qualification evidence without inventing a lifecycle crisis. The common public-evidence limitations above apply to this record.

Existing factual context (unchanged):

- SOURCE_FACT: The exact assembly is listed Active, 6.00 in (153 mm), 50 ohm, and 40 GHz maximum.
- SOURCE_FACT: Interfaces are 2.92 mm straight plug to SMPM straight plug on 0.085-inch conformable cable.
- SOURCE_FACT: The family cutsheet states DC-40 GHz interface ranges and warns specifications may vary by exact part number.

Preserve the original lifecycle label and dated context; this handoff does not recompute lifecycle or qualify any alternative.

### OV-04 — NXP Radio Power family

- Record: `SE.CML.RECORD.NXP.RADIO-POWER-2026.v0.1`.
- Source directory: `technical-risk/records/nxp-radio-power-2026/`.
- Current lifecycle state: `LAST_TIME_BUY_OPEN`.
- Current qualification state: `LAB_VERIFICATION_REQUIRED`.
- OEM replacement state: `OEM_REPLACEMENT_NOT_LISTED`.
- Freshness: `CURRENT_WITH_LIMITATIONS`; `MANUFACTURER_INTERFACE_STATUS_CONFLICT`.
- Current canonical record hash: `fad0d50b97e54a61c22078da35b79f63bb8de8e0bed1a0cc38d398977ac409aa`.

Material unknowns (existing record):

- No reviewed evidence establishes a board drop-in successor for any selected device.
- Application-specific matching networks, thermal margins and stability criteria are unknown.
- The MRF101AN overview has shown an inconsistent Active label while package/quality and the discontinuance notice indicate EOL.

Current evidence limitations / counter-evidence: Some NXP overview surfaces have retained an Active label for MRF101AN. The later dated discontinuance notice and package status are treated as stronger lifecycle evidence, while the conflict remains visible. The common public-evidence limitations above apply to this record.

Existing factual context (unchanged):

- SOURCE_FACT: NXP's final notice states the Radio Power product line is being ramped down.
- SOURCE_FACT: MRF101AN, MW6S010GNR1 and MMRF1009HR5 are listed with no replacement and a 2026-09-30 LTB.
- SOURCE_FACT: MRF101AN is a 50 V wideband 1.8-250 MHz device; MW6S010GNR1 is a 28 V 450-1500 MHz 10 W class device; MMRF1009HR5 is a 50 V 960-1215 MHz 500 W pulse device.

Preserve the original lifecycle label and dated context; this handoff does not recompute lifecycle or qualify any alternative.

## 6. Next authorized phase

```text
NEXT_PHASE = SE-CML-OV-001
NAME = CML Opportunity Validation v0.1
POSITION = Phase 0.5
```

Purpose: Do not only determine whether the original problem is unresolved. Determine whether the existing technical solution is inefficient and whether modern design, verification and manufacturing tools can produce a measurable improvement. Efficiency and improvement remain hypotheses until supported by evidence, including total migration and qualification costs.

The intended analysis has three layers:

A. **Problem Persistence** — whether the original problem persists and what evidence supports that conclusion.
B. **Current Solution Audit** — how the problem is currently handled and what remains unknown about efficiency and constraints.
C. **Solution Improvement Potential** — whether a measurable improvement is plausible and how it could later be verified.

This user authorization supersedes the older report's `NEXT_PHASE_AUTHORIZED = CML SNIPE SOLUTION DEVELOPMENT` for continuation scope only. Preserve that historical report unchanged. It does not authorize immediate solution development.

## 7. Next task boundary

The next Personal Codex session should execute **ONLY Phase A first**: the architecture and initialization step for SE-CML-OV-001. “Phase A” here is the implementation boundary; it is not permission to conduct empirical research for analytical layer A above.

Authorized next-session outputs:

- Opportunity Validation architecture within the existing Evidence Core and Technical Risk domain.
- Schemas, status vocabulary, record templates and gates.
- Validation tests for the new architecture and its boundaries.
- Initialize OV-01 through OV-04 using the mapping and immutable baseline references above; preserve unresolved fields as unknown/unassessed rather than fabricate conclusions.

Do not perform broad external research, contact companies, contact engineers, buy samples, commission lab testing, build replacement designs or select suppliers. Do not add unrelated product features or modify frozen findings. This handoff itself implements none of these outputs. Stop after Phase A and report artifacts, tests and remaining unknowns before further phases.

## 8. Required first action in Personal Codex

Before changing anything, run in the repository:

```sh
git status
git rev-parse HEAD
git rev-parse origin/main
```

Then read, in order:

1. `docs/handoff/CML_PERSONAL_CODEX_HANDOFF_2026-09-16.md`
2. `docs/execution/CML_V0_1_FINAL_AUDIT_HARDENING_REPORT.md`
3. `technical-risk/CML_VERSION_HISTORY.jsonl`
4. `technical-risk/TECHNICAL_RISK_MANIFEST.json`
5. `technical-risk/CML_GATE_RESULTS.json`
6. `docs/architecture/CML_TECHNICAL_RISK_DATA_DICTIONARY_v0.1.md`
7. `technical-risk/schema/` (all schema files)
8. `gdr-se/engine/domain_adapters/cml.py`

Also read the four baseline record directories, their release manifests, applicable repository instructions, and the architecture references above before designing extensions. Reconcile any newer commits or dirty worktree with this snapshot; do not reset or overwrite user changes. A fresh checkout will include the handoff commit, so HEAD is expected to differ from PRE_HANDOFF_SHA.

## 9. Handoff integrity and finalization

Checks performed locally without regenerating frozen outputs:

- Six focused scripts PASS: `scripts/test_cml_gate_registry.py`, `scripts/test_cml_freshness_vocabulary.py`, `scripts/test_cml_gdr_adapter.py`, `scripts/test_cml_dictionary_drift.py`, `scripts/test_cml_version_history.py`, `scripts/test_cml_site_metadata.py`.
- Read-only invocation of the existing gate functions: all 38 non-release-snapshot validators PASS, including schemas, canonical record/release artifact hashes, 93 frozen Timeline file hashes checked by the current validator, and complete intentional root/docs mirrors.
- The historical closure report states 98 protected Timeline files; the current read-only validator reports 93 protected files, all matching. Preserve both artifacts unchanged; this count discrepancy is recorded, not silently reconciled.
- Historical CML01 requires HEAD to equal the manifest implementation SHA and fails at the later audit-closure HEAD. Historical CML35 compares remote to that same implementation SHA and is intentionally not replayed against current remote. Current clean branch/HEAD/remote alignment is checked separately. Neither limitation changes the accepted historical 40/40 audit.
- Do not run the writing entry point of `scripts/test_cml_v01.py` merely to refresh handoff results: it rewrites four frozen gate-result artifacts. Do not supply a historical SHA as if it were the current remote.
- Verify handoff hashes/states against source records, required paths, whitespace, and that the commit changes only this handoff file. Commit message: `Add Personal Codex CML handoff`. Push to `origin/main`, then verify live remote SHA and clean worktree.

No research, production deployment, record updates or scientific changes are part of this handoff. The final session report carries the actual handoff commit and post-push remote SHA.

## 10. Personal Codex start prompt

```text
Continue roalstoney-alt/structurevidence, project StructEvidence Technical Risk / CML. Assume ZERO access to the prior Business ChatGPT/Codex conversation. Before changing anything, run git status, git rev-parse HEAD, and git rev-parse origin/main. Then read docs/handoff/CML_PERSONAL_CODEX_HANDOFF_2026-09-16.md and every required source listed in its section 8. Reconcile current Git state with its baseline without overwriting user changes.

Execute ONLY Phase A of SE-CML-OV-001, CML Opportunity Validation v0.1 (Phase 0.5): create architecture, schemas, status vocabulary, record templates, gates and validation tests; initialize OV-01 through OV-04 from the handoff's exact existing-record mapping. This is architecture/initialization, not new empirical research. Model Problem Persistence, Current Solution Audit and Solution Improvement Potential while keeping unsupported assessments unknown. Preserve the shared Evidence Core, frozen CML findings, baseline record hashes, public/private boundary, RDL/GDR controls and append-only history.

CML seeks problems not yet solved efficiently: public technical risk is not proof of customer pain; an existing or working solution is not proof of efficiency; internal resolution does not rule out opportunity; alternatives are not automatically qualified; lower unit price is not lower total migration cost. Do not conduct broad external research, contact companies or engineers, buy samples, commission lab testing, build replacement designs or select suppliers. Do not add unrelated features. The handoff's Phase A authorization supersedes the older SNIPE Solution Development next-step wording. Run appropriate integrity tests, report changed artifacts and remaining unknowns, and stop after Phase A.
```
