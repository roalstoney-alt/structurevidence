# SE-LISTED-PROJECT-TRACKER-IREN-001 — Engineering and Evidence Pilot v0.1
Status: APPROVED TO PREPARE IN DRAFT ONLY. No public publication, outreach, billing, automatic alerts, trading or customer enrollment authorized.
Baseline main SHA: 305bbef43f2ccdef9d025ac802dfca6b6ad6a8df
Case: SE-NEW-BUSINESS-001 — IREN Limited's AI Cloud transition. Preserve its existing frozen internal/public histories and case IDs; append corrections, never rewrite.

## Why this pilot
Test whether exposing a listed company's significant *project commitments* as time-bounded, challengeable evidence conditions attracts qualified dialogue and creates reusable institutional Decision Boundary records. NOT stock research ratings, trade signals, a subscription launch or measured cost-savings claim.

Core message: From one person's conviction to an institutional, auditable commitment. Avoid anti-founder or hindsight criticism. Track situations, not audiences: what is committed while which assumptions remain unresolved? Client-specific thresholds/actions never guessed.
Frozen brand: “Verify Your Verify — Lower the cost of knowing what you can trust.”; “We can be wrong. We must remain auditable.”; every state shows how it was checked.

## Inputs and truth boundary
The user-provided 'f2fwithcc1026.txt' and 'StructEvidence Tracker Pilot IREN Limited.md' are PROPOSALS, not qualifying source evidence. Do not claim file paths in assistant sandbox are accessible to Codex. If these files are absent from the worktree, implement the detailed contract below and report external-reference gaps; do not fabricate content.
Initial authoritative leads to retrieve and snapshot with source-specific digest, retrieval timestamp and SEC accession number:
- https://www.iren.com/investors/sec-filings (index; includes Oct 13 2026 proxy/ARS items)
- FY26 SEC 10-K: https://www.sec.gov/Archives/edgar/data/1878848/000187884826000052/iren-20260630.htm
- FY26 results SEC exhibit: https://www.sec.gov/Archives/edgar/data/1878848/000187884826000051/irenreportsfy26results.htm
- August 13 2026 8-K and July 20 2026 8-K; fetch by verified accession and record exhibits' filed-vs-furnished treatment; do not infer from document name.
Record inaccessible sources as ACCESS_RESTRICTED/RETRIEVAL_FAILED, never 'does not exist'. Source timestamps, observation date and publication date separately. Check newer SEC filings and issuer investor calendar as of actual capture date, do not assume Aug releases are newest.
Claims to VERIFY before publication: FY26 revenue 707.0m / AI Cloud 128.8m / reported loss 702.6m; impairment 638.8m; Microsoft ~9.7bn five-year contract; Horizon 1 accepted *as issuer reported*; Horizons 2-4 targets vs contractual grace; $4bn contracted vs $1bn operating ARR definitions; NVIDIA investment right vs funds received; $3.6bn GPU financing; historic FY24 Poolside figures. Each unverified stays NOT_REVERIFIED.
Preserve important distinction: contract value != recognized revenue != cash collected; target != delivered capacity; issuer's 'customer acceptance' statement != customer-authored confirmation; options/right to invest != investment completed. Any disputed July vs August ARR wording gets an append-only DEFINITION_DRIFT event, not silent reconciliation.

## Financial-source rubric extension (parallel axes, not E0–E5 replacement)
Introduce additive, versioned metadata:
- source_origin: ISSUER_AUTHORED/DERIVED/PARTIALLY_DEPENDENT/INDEPENDENT/UNKNOWN;
- document_kind and liability_regime: FILED/FURNISHED/UNFILED/UNDETERMINED (validated per SEC filing and exhibit); never assume audit applies to whole 10-K;
- assurance: AUDITED_FINANCIAL_STATEMENT/REVIEWED_INTERIM/UNAUDITED_DISCLOSURE/PROMOTIONAL/NOT_APPLICABLE/UNKNOWN with statement and scope;
- disclosure_stage D0=TARGET_OR_FORECAST, D1=ANNOUNCED_OR_SIGNED_CONTRACT, D2=ISSUER_REPORTED_DELIVERY_OR_ACCEPTANCE, D3=RECOGNIZED_REVENUE_IN_FINANCIALS, D4a=CASH_COLLECTED, D4b=CUSTOMER_AUTHORED_CONFIRMATION.
**IMPORTANT** D4a and D4b are different dimensions; do not put them above one another or imply D3->D4 is an inevitable ladder. Do not automatically infer D3 from D1, nor D4b from D2.
Test legal treatment of 'furnished' disclosures against actual cover/exhibit text; flag UNKNOWN rather than using guesses. Schema remains proposal until review.

## Tracker view — internal draft, NOT automatically published
Four main sections: SUPPORTED_AS_ATTRIBUTED / NOT_ESTABLISHED_WITHIN_SCOPE / WHAT_WOULD_CHANGE_IT / APPEND_ONLY_CHANGE_LOG.
Each row: stable claim_id, actual source ID/accession/url, period, as-of/cutoff, retrieval status, origin and derivative lineage, assurance/liability, exact claim language, qualifying evidence, contradictory evidence, missing condition, next check, reviewer identity/status, source hash, prior version. Clearly separate legal filed status from independence and evidentiary completeness.
Context box 'Same boundary, three readings': manufacturer/operator, financier/board, buyer/technical user. These are different *questions* to the same evidence, NOT recommendations or inferred client exposure. Add Company Bet Register schema: commitment (issuer reported), decision owner UNKNOWN unless sourced, amount and stage if explicitly disclosed, unmet conditions, evidence cutoff, client action UNSPECIFIED, review triggers; never pretend to know internal board intent.
Clickable challenges only via existing functional, approved gap route; otherwise NOT_LAUNCHED. No unmoderated submission endpoint.

## Independence/market neutrality safeguards
- Neutral, prepublished-style selection criteria drafted in advance: listed firm, bounded public project, material disclosed commitment, minimum two primary document types, time-bound milestones. This is a one-case exploratory pilot, not a random sample.
- Draft editorial/no-positions/conflicts policy: covered-securities employee/contractor trading restrictions only after legal/operational review; conflict disclosure, no issuer fee for favorable state or priority changes, paid & free same-time state publication, never ratings, targets or buy/sell directives. Do not falsely attest team is position-free now; mark DECLARATION_NOT_COLLECTED.
- Securities/commercial legal review for US and operator/reader jurisdictions BEFORE marketing paid investor-facing outputs, personalized alerts, or onboarding. Not legal approval by an LLM.
- Publication remains HUMAN_GATE. No X/LinkedIn autopost, SEC event push notification or website deploy in this PR.

## Cadence & 8-week experiment (not scheduled until activation)
Daily/weekday internal scan of issuer IR/SEC with scoped fair-access and bounded search provenance; one weekly editorial digest (even 'no qualifying change' must truthfully say checked scope/date) and exceptional event-delta draft on meaningful filing/state change. Alert drafts are human-reviewed, NOT live subscription alerts.
Pilot length: 8 weeks measured from separately authorized PUBLIC_PILOT_START, not branch creation or a synthetic run.
Pre-registered *proposed* minimum goals for owner approval:
- >=3 qualified, non-incentivized professional interactions over 8 weeks;
- >=2 externally submitted substantive evidence challenges/sources (count zero if none);
- median filing-to-internal-update <=3 calendar days for material primary filings with accessible originals;
- all accepted changes have append-only provenance and no unreviewed production releases.
If below first two thresholds at week 8, stop public promotion and record pilot as weak demand, not product failure. These thresholds are proposals pending owner approval, not frozen facts. Record denominator of eligible events and censored failures.
No invented subscribers/conversions, actual expenses, saved time, or avoided losses.

## Security and regression
Do not modify commercial prices, intake, D1, existing cases/URLs/DOIs/ledger or original source bytes. Protect all baselines. Append-only versions of new tracker and protocol. Root/docs mirrors only where needed; safe published paths if explicitly later authorized. Never publish private partner/source-bridge contents. Dedupe same origin across hosts, never equate SEC filing legal liability with independent verification.
Automated tests: date/cutoff leakage; post-hoc leakage; D0 target vs signed D1; issuer-reported D2 vs third-party; D3 recognized revenue vs cash; D4a vs D4b; 10-K audit scope; filed/furnished; duplicate coverage; inaccessible SEC; unknown next date; conflict declarations; no implied trading signal; immutable corrections; challenge moderation; locale and sitemap; public/nonpublic boundary; deterministic hashes; zero new regressions.
Output report: BASELINE_MAIN_SHA, HEAD_SHA, SOURCE_CAPTURE_STATUS, ACCESSION_LIST, ORIGINALS_CHANGED=0, CASE_STATE_CHANGED=NO, FINANCIAL_RUBRIC_STATUS, DRAFT_TRACKER_STATUS, PAGES_DEPLOY=NO, NEW_REGRESSION_COUNT, HUMAN_GATES.
Do not merge, deploy, publish, schedule automations, contact covered company or prospective investors, or accept payment without additional owner authorization.
