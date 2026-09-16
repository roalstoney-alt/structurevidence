# CML Opportunity Validation — Phase B Wave 1 v0.1

Policy: `CML_OV_v0.1_PHASE_B`. Scope: OV-01 and OV-03 only. This implements the user-authorized Wave 1 of `SE-CML-OV-001-PHASE-B`; continuation, outreach, solution development, publication and paid delivery remain unauthorized.

## Baseline and record model

The entry baseline is `ad3206fff3c8d8375b1c9e087df44bd9c7336927` on main. The untracked Phase A completion report was moved outside the repository before confirming a clean worktree and HEAD = origin/main. All files tracked at that commit remain frozen, including all four Phase A records, schemas, manifests, audit artifacts, CML history, policies, adapter and public pages.

Each Wave 1 successor is `OV-xx.v0.2.json`, bound to its predecessor ID, record hash and file hash. The copied Phase A analytical layers retain their historical initialization values; they are not the new empirical assessment. New findings are in `phase_b_assessment` and the eleven bound artifacts in the adjacent `phase-b/` directory. A separate Phase B record schema preserves the common Evidence Core envelope and validates the new payload. The package schema validates source, claim, solution, counter-evidence, hypothesis, variable and assessment structures.

Research-event clocks describe this desk-review event, not a replacement lifecycle event. Existing lifecycle dates and qualification states are unchanged. Shared source references include predecessor lineage; the new source register contains new research sources only. Hashes use the existing canonical digest convention. The input hash binds the source register and payload; the record hash binds the core without its hash and the payload. Eleven package file hashes are bound, excluding the self record and derived gate report to avoid a cycle.

No Phase B entries are added to the frozen Phase A index, manifest or CML version history. New lineage is carried by the successor records and this review. No Phase B files are copied into the public `docs/technical-risk` mirror or registered in its UI. Existing mirrors remain unchanged. The older whole-root mirror invariant is not claimed for these intentionally internal additions; changing that shared validator would require a separate architecture decision. Do not publish these files through a future blanket mirroring operation.

## Evidence rules

Issuer and host are distinct. Same-issuer sources and distributor mirrors do not supply independent corroboration of demand. Independent evidence-family labels are derived from issuer groups and artifact families, not counted as proof of an opportunity.

Source registration records conservative known/retrieved timestamps after review, rather than exact network request times. Undated material retains null publication dates. No source files were locally archived; source artifact hashes remain null. Artifact hashes protect the research package, not the remote content. Remote pages can change, and revalidation is required before later use.

Each substantive claim carries its type, scope, evidence basis, references and limitations. Stock and catalog relevance do not establish installed use. Supplier prices do not establish customer costs. A manufacturer's offered process does not establish customer adoption. A tool capability or measurement requirement does not establish inefficient work.

Direct current-use or observed current-solution claims require a source-linked `current_bridge` with an explicit validity interval covering the research date and a rationale. Eligible evidence must be opened application, service, public BOM, procurement or process-study material. A publication date alone is insufficient. The validity interval must be supported by the source; it is not an inferred expiry date or a universal freshness rule. No present Wave 1 claim asserts such a bridge. Human review must assess the source's actual meaning and the claimed interval.

Accepted bottleneck hypotheses and suboptimal signals additionally require direct application evidence through this bridge, not a relabelled market signal. This conservative Wave 1 implementation can under-admit useful indirect leads; those remain research leads pending review. Neither structured validation nor a text-pattern check can establish semantic truth or detect every unsupported prose claim.

TMC and TTQ list all required variables without invented costs, durations or totals. Future contact records contain public forwarding channels only. They neither identify verified customer demand nor authorize sending a message.

## Gates and tests

Run `python3 scripts/validate_cml_ov_phase_b.py` read-only. Use `--write-results` only to regenerate the two new `12_PHASE_B_GATE.json` files. Run `python3 scripts/test_cml_ov_phase_b.py` for positive and adversarial checks. Phase A validators/tests remain read-only.

Each target independently evaluates the workflow's sixteen gates. PASS means the stated structural/evidence discipline holds, not that the opportunity is real. NOT_EVALUATED explicitly exposes missing observed solutions, accepted hypotheses or tool-benefit mappings. FAIL requires correction or a reported limitation before reuse. Gate snapshots include validator hash and successor hash. Independent review also inspects source meaning and inference quality; it is not replaced by automated gates.

Stop after Wave 1 independent review. `CONTINUE_DESK_RESEARCH` is an analytical recommendation, not authorization for another wave or outreach. `PUBLIC_RELEASE = BLOCK` and `PAID_DELIVERY = BLOCK` remain unconditional for this package.
