# SE-DUAL-SITE-UPGRADE-002 / PHASE B — Codex Execution Handoff
Status: AUTHORIZED FOR DEVELOPMENT ONLY; NO PRODUCTION DEPLOYMENT.
Baseline main: f89f5dbba30c3f504833418d643786680d5769ca
PR #48: merged.
Branch: codex/se-002-source-dependency-view-phase-b

## Objective
Implement first grounded 800VDC Source Dependency View on structurevidence.org, using actual existing source packets, OEG-CML-001 / OEG-CML-002 acceptance rules, immutable source registry and explicit review cutoffs. Maintain existing site mirrors, source IDs, case statuses and deployment boundaries.

## Before editing
Inspect original case source packet, gap records, public URL templates, data provenance/capture references, protected hashes, and scripts/source_dependency_v01.py. Compare frozen acceptance standards with newly introduced qualification rules. If mismatch, record discrepancy and stop affected classification; do not silently reinterpret evidence or auto-update case state.

## Work
1. Enumerate candidate records and assign immutable source_row_ids with URLs, captures/hashes or honest reference-only limitations.
2. Record author/originator, publication host, economic relationship evidence, original lineage; do not infer INDEPENDENT from missing relationship disclosures. UNKNOWN if unverifiable.
3. Separately score evidence content E0–E5; verify facets from actual records. Gate using gap-specific criteria, never E5 blanket requirement. Document reasons for every result.
4. Support two independent reviewer records only if actual second review occurred; otherwise mark pending and do not claim double-review.
5. Append additions and supersession events; historical snapshots, IDs, statuses and raw evidence remain unchanged.
6. Render a reader-facing Who is actually saying this? view, listing source, originator, class, evidence level, qualification reason, source link, search scope, cutoff, last checked, rubric version, missing/access restricted references, and challenge route only if operational and human-gated.
7. Computed metrics must return count and included source-row IDs; count evidence lineages rather than URL hosts. Describe zeros as zero in the declared scope.
8. Mirror root/docs pages as required; preserve EN/zh-CN/es locales, canonicals, hreflang, sitemap and existing claim/Gaps navigation.
9. Keep commercial .com files, D1, private customer data, prices and contracts unchanged in Phase B.

## Test gate
- 0 protected originals changed; new only append-only.
- independent provenance and acceptance-rule case checks with counterexamples: derived-copy counts, issuer E4 may qualify, independent E2 does not prove field deployment, inaccessible unknown, source-lineage cycles, conflicting reviewers and version supersessions.
- Run focused and full baseline-differential tests; report legacy failures separately; NEW_REGRESSION_COUNT=0.
- No unreviewed status promotion, no invented counts or outcome metrics, no public external writes.
- Include responsive page, accessibility, internal link, multilingual and security checks.

## Deliverable
Open a DRAFT PR-B for human review, including grounded evidence ledger, status of every source, test results and drift hashes, HEAD and BASELINE SHAs, user-visible screenshots if available, plus precise remaining unknowns and blockers.
Do not merge PR-B and DO NOT DEPLOY production until an explicit separate human approval.
