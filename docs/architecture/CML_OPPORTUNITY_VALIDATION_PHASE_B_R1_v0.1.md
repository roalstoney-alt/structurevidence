# CML Opportunity Validation — Phase B-R1 v0.1

Policy version: `CML_OV_v0.1_PHASE_B_R1`. Authorized scope: targeted application and workflow discovery for OV-01 and OV-03 only. Baseline: accepted Wave 1 commit `b0459b2b945c78ae650a7e0a6db5b8f206857a46`.

## Purpose and boundary

B-R1 addresses the independent Wave 1 review finding that deeper work should target current applications and observed workflows. It does not repeat the full Phase B search and does not authorize OV-02, OV-04, outreach, samples, quotations, replacement design, qualification, Snipe Solution, public release or paid delivery.

OV-01 receives exactly one exact-MPN current-application pass and one exact-MPN current-solution/workflow pass. Broad catalog and distributor searches are outside B-R1. OV-03 uses the 40 GHz cable-assembly workflow as its research unit: production tests, qualification measurements, calibration/de-embedding, automation, pass/fail reporting and result retention. Exact-MPN catalog availability is inherited from Wave 1 and is not the focus of R1.

## Record and package model

Wave 1 `v0.2` records and packages remain unchanged. B-R1 creates `v0.3` successors with directional predecessor ID, hash and path; a new research event; the B-R1 terminal assessment; and hashes for the discovery package and limitations file. New evidence lives in each target's `phase-b-r1/` directory. The gate report is derived and excluded from the record hash to avoid a hash cycle.

The B-R1 package schema closes the new structures and restricts terminal outcomes to:

- `PUBLIC_BOTTLENECK_FOUND`
- `PUBLIC_EVIDENCE_CEILING`
- `NO_PLAUSIBLE_CURRENT_APPLICATION`
- `INSUFFICIENT_AFTER_TARGETED_RESEARCH`

`PUBLIC_EVIDENCE_CEILING` means the authorized public search found relevant evidence but the facts required for a material conclusion remain private or organization-specific. It cannot set customer pain or a bottleneck. It must name the inaccessible variables. A no-application outcome requires direct public negation rather than a bounded search with no result. A public-bottleneck outcome requires a source fact tied to an observed customer workflow; tool capability, supplier process descriptions and engineering judgment are insufficient.

## Evidence interpretation

Source claims distinguish manufacturer production statements, tool-vendor workflows, technical articles and commercial guidance. Issuer and host remain separate. Source/claim references are reciprocal. Dates represent the public document date where known and the B-R1 registration/retrieval clock otherwise. No remote source was archived locally, so successor hashes bind the research records rather than the changing remote content.

For OV-01, a manufacturer notice addressed to affected customers does not identify a current application, and offered EOL paths do not establish adoption. Generic commercial EOL guidance is a possible workflow map, not an observed workflow.

For OV-03, public production tests and automated VNA workflows establish method availability. They do not establish the target organization's baseline, a manual bottleneck, incremental benefit or customer pain. Relevant private variables include test coverage, acceptance limits, calibration cadence, fixture reuse, operator time, queue time, volume, yield, retest, failure analysis and cost.

## Validation and stop condition

`scripts/validate_cml_ov_phase_b_r1.py` evaluates accepted-baseline integrity, schema/provenance, targeted scope, terminal-outcome discipline, bottleneck discipline, prohibited-action boundaries, target isolation and successor hashes. `--write-results` writes only the two new derived gate files. `scripts/test_cml_ov_phase_b_r1.py` tests both valid packages and adversarial promotions.

Automated PASS establishes record discipline, not empirical truth. Independent review must inspect whether the cited public material supports the prose and whether the ceiling is being used as a limit rather than a positive opportunity signal. Execution stops after independent review of OV-01 and OV-03. B-R1 changes remain uncommitted until separately accepted.
