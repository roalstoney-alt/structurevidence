import { page } from "./commercial-ui.js";

export const OPEN_EVIDENCE_GAP_PROTOCOL = Object.freeze({
  protocol: "OPEN EVIDENCE GAP PROTOCOL v0.1",
  phase: "PHASE 1 — EXTERNAL CHALLENGE ACTIVATION",
  launched_at: "2026-10-05",
  phase_duration_days: 30,
  target_invitations: 30,
  acknowledgement_target: "<24 hours",
  initial_review_target: "<72 hours",
  login_required: false,
  public_file_upload: false,
  no_bounty: true,
  no_leaderboard: true,
  no_contributor_score: true,
  no_auto_state_change: true,
  rate_limit: "5 submissions per IP-derived key per rolling 10 minutes",
  attribution_disclaimer: "Public attribution means evidence contribution only. It does not imply endorsement of StructEvidence's final conclusion."
});

export const GAP_EFFECTS = Object.freeze(["SUPPORT", "CONTRADICT", "NARROW_SCOPE", "CORRECT_ATTRIBUTION"]);
export const ATTRIBUTION_OPTIONS = Object.freeze(["NAMED", "ORGANIZATION_ONLY", "ANONYMOUS"]);
export const GAP_SUBMISSION_STATES = Object.freeze([
  "SUBMITTED", "SCREENED", "IN_SCOPE", "OUT_OF_SCOPE", "QUALIFYING", "NON_QUALIFYING",
  "NEEDS_CLARIFICATION", "ACCEPTED", "REJECTED", "STATE_CHANGED", "NO_STATE_CHANGE", "SCOPE_CLARIFIED"
]);

export const OPEN_EVIDENCE_GAPS = Object.freeze([
  {
    gap_id: "OEG-CML-001",
    case_id: "CML-PDRE-001",
    case_title: "800V DC Data Center Power Architecture",
    case_url: "https://structurevidence.org/cases/800vdc/",
    claim_id: "CML-PDRE-001.INDEPENDENT_VALIDATION",
    claim_text: "Independent third-party validation of the reported 800VDC / SST deployment is established.",
    current_state: "NOT_ESTABLISHED",
    current_scope: "One operator-reported deployment at one named campus; no independent performance validation is established.",
    evidence_cutoff: "2026-09-20T10:46:47Z",
    what_is_established: ["One named operator reported commercial operation of a materially relevant 10kV AC to SST to 800VDC architecture."],
    what_is_not_established: ["Independent verification of operating conditions, performance, availability, efficiency, or safety at the named site."],
    what_would_change_this: "An independently attributable operating or test record tied to the named site, with observation period, conditions, method, and responsible organization.",
    acceptable_source_examples: ["Independent engineering test report", "Operator record with attributable methodology", "Third-party commissioning or performance record"],
    non_qualifying_examples: ["Vendor marketing copy", "Unattributed screenshots", "A second retelling of the operator's original announcement"],
    last_reviewed: "2026-10-05",
    challenge_url: "https://structevidence.com/gaps/OEG-CML-001/"
  },
  {
    gap_id: "OEG-CML-002",
    case_id: "CML-PDRE-001",
    case_title: "800V DC Data Center Power Architecture",
    case_url: "https://structurevidence.org/cases/800vdc/",
    claim_id: "CML-PDRE-001.MULTI_ENTITY_REPLICATION",
    claim_text: "The 800VDC / SST architecture has been replicated by multiple independent entities.",
    current_state: "NOT_ESTABLISHED",
    current_scope: "The public record supports a single operator-reported instance, not replication across independent operators or sites.",
    evidence_cutoff: "2026-09-20T10:46:47Z",
    what_is_established: ["A single named operator reported one materially relevant field deployment."],
    what_is_not_established: ["A second independently attributable deployment", "Multi-operator replication", "Repeat procurement or industry adoption"],
    what_would_change_this: "A public record for another attributable operator or independently controlled site showing a materially comparable deployed architecture and operating status.",
    acceptable_source_examples: ["Named operator commissioning record", "Regulatory or grid-connection record", "Independent case study identifying operator, site, architecture, and date"],
    non_qualifying_examples: ["Multiple articles about the same site", "Planned projects without commissioning", "Vendor pipeline totals without named deployments"],
    last_reviewed: "2026-10-05",
    challenge_url: "https://structevidence.com/gaps/OEG-CML-002/"
  },
  {
    gap_id: "OEG-BESS-001",
    case_id: "SE-BESS-SODIUM-001",
    case_title: "Sodium-Ion BESS Commercialization",
    case_url: "https://structurevidence.org/cases/sodium-ion-bess/",
    claim_id: "SE-BESS-SODIUM-001.NAMED_COMMISSIONED_SITE",
    claim_text: "A named customer sodium-ion stationary BESS site has been commissioned.",
    current_state: "NOT_ESTABLISHED",
    current_scope: "Stationary sodium-ion BESS only; vehicle, starter-battery, and solid-state battery claims are excluded.",
    evidence_cutoff: "2026-09-24",
    what_is_established: ["A stationary sodium-ion BESS product launch", "A public supply cooperation agreement", "Future delivery milestones stated by manufacturers"],
    what_is_not_established: ["Completed customer delivery", "Named-site commissioning or grid connection", "Customer acceptance"],
    what_would_change_this: "A public, attributable record identifying the customer or operator, site, sodium-ion stationary system, commissioning or grid-connection date, and operational status.",
    acceptable_source_examples: ["Customer acceptance record", "Named-site commissioning notice", "Grid-connection or regulator record tied to the system"],
    non_qualifying_examples: ["Product launch", "Framework agreement", "Future delivery target", "Unnamed pilot or showcase"],
    last_reviewed: "2026-10-05",
    challenge_url: "https://structevidence.com/gaps/OEG-BESS-001/"
  },
  {
    gap_id: "OEG-BESS-002",
    case_id: "SE-BESS-SODIUM-001",
    case_title: "Sodium-Ion BESS Commercialization",
    case_url: "https://structurevidence.org/cases/sodium-ion-bess/",
    claim_id: "SE-BESS-SODIUM-001.INDEPENDENT_FIELD_PERFORMANCE",
    claim_text: "Independent field-performance evidence for sodium-ion stationary BESS is established.",
    current_state: "NOT_ESTABLISHED",
    current_scope: "Public evidence reviewed for stationary sodium-ion BESS; manufacturer-attributed product claims are not independent field-performance evidence.",
    evidence_cutoff: "2026-09-24",
    what_is_established: ["The product was publicly launched and showcased", "Manufacturer-attributed performance and field-validation language exists"],
    what_is_not_established: ["Independent field measurements", "Attributable operating duration and conditions", "Independent safety or performance validation"],
    what_would_change_this: "A third-party or operator-controlled dataset tied to a named stationary sodium-ion BESS, with dates, operating conditions, measurement method, and accountable publisher.",
    acceptable_source_examples: ["Independent test report", "Operator telemetry summary with methodology", "Regulator or research-institute field evaluation"],
    non_qualifying_examples: ["Manufacturer datasheet", "Laboratory cell result without field linkage", "Unattributed performance chart"],
    last_reviewed: "2026-10-05",
    challenge_url: "https://structevidence.com/gaps/OEG-BESS-002/"
  },
  {
    gap_id: "OEG-ONC-001",
    case_id: "SE-ONC-NSQNSCLC-CN-001",
    case_title: "China Non-Squamous NSCLC Evidence Pathway",
    case_url: "https://structurevidence.org/cases/nsq-nsclc-china/",
    claim_id: "SE-ONC-NSQNSCLC-CN-001.HOSPITAL_AGGREGATE_OUTCOME_DATA",
    claim_text: "A hospital-specific aggregate outcome dataset has been acquired for this public NSCLC case.",
    current_state: "NOT_ESTABLISHED",
    current_scope: "China non-squamous NSCLC; the detailed index cohort is EGFR-mutated locally advanced or metastatic disease after EGFR-TKI progression.",
    evidence_cutoff: "2026-09-28",
    what_is_established: ["Public regulatory, randomized-trial, guideline, surgical-cohort, ECMO-context, and transplant-consensus sources were identified within their stated scopes."],
    what_is_not_established: ["An authorized hospital-specific aggregate dataset for the index cohort", "Hospital-level exposure, follow-up, survival, adverse-event, or patient-feedback outcomes for this case"],
    what_would_change_this: "A lawful public aggregate dataset or citable public analysis with a defined hospital population, cohort criteria, treatment exposure, outcome definitions, follow-up, censoring, and permitted reuse boundary.",
    acceptable_source_examples: ["Peer-reviewed hospital aggregate study", "Public registry analysis with cohort and censoring definitions", "Authorized de-identified aggregate report with reuse terms"],
    non_qualifying_examples: ["Patient-identifiable data", "Anecdotes", "Hospital marketing claims", "Aggregate numbers without cohort or outcome definitions"],
    last_reviewed: "2026-10-05",
    challenge_url: "https://structevidence.com/gaps/OEG-ONC-001/"
  },
  {
    gap_id: "OEG-ONC-002",
    case_id: "SE-ONC-NSQNSCLC-CN-001",
    case_title: "China Non-Squamous NSCLC Evidence Pathway",
    case_url: "https://structurevidence.org/cases/nsq-nsclc-china/",
    claim_id: "SE-ONC-NSQNSCLC-CN-001.PATIENT_SPECIFIC_SUCCESS_PROBABILITY",
    claim_text: "A patient-specific treatment success probability is established by this public NSCLC case.",
    current_state: "NOT_ESTABLISHED",
    current_scope: "The public case separates population evidence from individual prognosis and does not hold patient-level clinical data.",
    evidence_cutoff: "2026-09-28",
    what_is_established: ["Population-level trial and clinical-context evidence exists for defined cohorts", "Population estimates do not directly establish an individual's outcome"],
    what_is_not_established: ["A patient-specific probability", "An individualized treatment ranking", "Clinical applicability to an unidentified individual"],
    what_would_change_this: "Only clinically governed analysis using complete, lawful individual data and a validated model appropriate to that exact population could address an individual estimate; a public challenge may correct or narrow this boundary but cannot create medical advice.",
    acceptable_source_examples: ["External validation of a relevant prognostic model", "Clinical guideline defining model applicability", "Methodological evidence that materially narrows the population-to-individual boundary"],
    non_qualifying_examples: ["Applying a trial median to one person", "Testimonials", "Unvalidated online calculators", "Treatment advice or identifiable patient records"],
    last_reviewed: "2026-10-05",
    challenge_url: "https://structevidence.com/gaps/OEG-ONC-002/"
  }
]);

export const STATIC_GAP_CHANGE_LOG = Object.freeze(OPEN_EVIDENCE_GAPS.map((gap, index) => ({
  change_id: `OEG-CHANGE-${String(index + 1).padStart(3, "0")}`,
  gap_id: gap.gap_id,
  challenge_id: null,
  change_type: "GAP_OPENED",
  summary: "Initial open evidence gap published under Open Evidence Gap Protocol v0.1.",
  attribution: "StructEvidence",
  previous_state: null,
  new_state: gap.current_state,
  changed_at: "2026-10-05",
  append_only: true
})));

export function findGap(gapId) {
  return OPEN_EVIDENCE_GAPS.find((gap) => gap.gap_id === gapId) || null;
}

const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[character]);
const renderList = (items) => `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
const protocolBoundary = `<aside class="gap-boundary"><h2>Challenge boundary</h2><ul><li>No bounty, leaderboard, or contributor score.</li><li>No login and no public file upload in Phase 1.</li><li>Every submission receives human screening; it never changes a state automatically.</li><li>${escapeHtml(OPEN_EVIDENCE_GAP_PROTOCOL.attribution_disclaimer)}</li></ul></aside>`;
const withGapScript = (html, canonicalPath) => html
  .replace("https://structevidence.com/gaps/", `https://structevidence.com${canonicalPath}`)
  .replace("</body>", '<script src="/assets/gaps.js" defer></script></body>');

export function renderGapIndex() {
  const cards = OPEN_EVIDENCE_GAPS.map((gap) => `<article class="gap-card"><p class="kicker">${escapeHtml(gap.gap_id)} · ${escapeHtml(gap.current_state)}</p><h3><a href="/gaps/${escapeHtml(gap.gap_id)}/">${escapeHtml(gap.claim_text)}</a></h3><p>${escapeHtml(gap.case_title)}</p><dl><div><dt>Evidence cut-off</dt><dd>${escapeHtml(gap.evidence_cutoff)}</dd></div><div><dt>Claim</dt><dd>${escapeHtml(gap.claim_id)}</dd></div></dl><a class="text-link" href="/gaps/${escapeHtml(gap.gap_id)}/">Inspect and challenge →</a></article>`).join("");
  const body = `<section class="page-hero"><p class="kicker">VORTEX Activation · Phase 1</p><h1>Open Evidence Gaps</h1><p class="lead">Six bounded stop points across the three existing public cases. Submit a public URL or document reference that could support, contradict, narrow, or correct one gap.</p><div class="actions"><a class="button" href="#open-gaps">Inspect six gaps</a><a class="button secondary" href="/gaps/changes/">Public change log</a></div></section><section id="open-gaps"><div class="section-head"><div><p class="kicker">2 gaps per existing case</p><h2>What evidence could change the public record?</h2></div><p>Submission is not acceptance. Evidence is screened against the stated scope and source requirements.</p></div><div class="gap-grid">${cards}</div></section>${protocolBoundary}`;
  return withGapScript(page("Open Evidence Gaps", "Six public, machine-readable evidence gaps across the three existing StructEvidence cases.", body, "gaps"), "/gaps/");
}

export function renderGapDetail(gap) {
  const opening = STATIC_GAP_CHANGE_LOG.find((change) => change.gap_id === gap.gap_id);
  const body = `<section class="page-hero"><p class="kicker">${escapeHtml(gap.gap_id)} · ${escapeHtml(gap.current_state)}</p><h1>${escapeHtml(gap.claim_text)}</h1><p class="lead">${escapeHtml(gap.current_scope)}</p><div class="actions"><a class="button secondary" href="${escapeHtml(gap.case_url)}">Open source case</a><a class="button secondary" href="/api/gaps/${escapeHtml(gap.gap_id)}">Machine-readable JSON</a></div></section><section class="gap-detail"><dl class="gap-facts"><div><dt>Case</dt><dd>${escapeHtml(gap.case_id)} · ${escapeHtml(gap.case_title)}</dd></div><div><dt>Claim</dt><dd>${escapeHtml(gap.claim_id)}</dd></div><div><dt>Current state</dt><dd>${escapeHtml(gap.current_state)}</dd></div><div><dt>Evidence cut-off</dt><dd>${escapeHtml(gap.evidence_cutoff)}</dd></div><div><dt>Last reviewed</dt><dd>${escapeHtml(gap.last_reviewed)}</dd></div></dl><div class="gap-columns"><article><h2>What is established</h2>${renderList(gap.what_is_established)}</article><article><h2>What is not established</h2>${renderList(gap.what_is_not_established)}</article><article><h2>What would change this</h2><p>${escapeHtml(gap.what_would_change_this)}</p></article><article><h2>Qualifying boundary</h2><h3>Examples that may qualify</h3>${renderList(gap.acceptable_source_examples)}<h3>Examples that do not qualify</h3>${renderList(gap.non_qualifying_examples)}</article></div></section><section class="form-layout"><form data-gap-challenge-form data-gap-id="${escapeHtml(gap.gap_id)}"><h2>Challenge this gap</h2><input type="hidden" name="gap_id" value="${escapeHtml(gap.gap_id)}"><label class="field wide"><span>Public URL or document reference *</span><input name="evidence_reference" maxlength="2000" required><small>Phase 1 accepts references only. Do not submit files, private records, credentials, or personal health information.</small></label><label class="field"><span>Proposed effect *</span><select name="effect" required><option value="">Select</option>${GAP_EFFECTS.map((effect) => `<option>${effect}</option>`).join("")}</select></label><label class="field"><span>Attribution preference *</span><select name="attribution_preference" required><option value="">Select</option>${ATTRIBUTION_OPTIONS.map((option) => `<option>${option}</option>`).join("")}</select></label><label class="field" data-named-field hidden><span>Public contributor name *</span><input name="attribution_name" maxlength="200"></label><label class="field" data-organization-field hidden><span>Public organization name *</span><input name="organization_name" maxlength="300"></label><label class="field"><span>Contact email (optional, never public)</span><input name="contact_email" type="email" maxlength="254"></label><label class="field wide"><span>Optional note</span><textarea name="note" maxlength="4000"></textarea></label><button class="button" type="submit">Submit for human screening</button><div class="form-status" data-gap-form-status role="status" aria-live="polite"></div></form>${protocolBoundary}</section><section><div class="section-head"><div><p class="kicker">Append-only</p><h2>Public change log</h2></div><p>Accepted evidence may result in a state change, no state change, or scope clarification. Earlier entries remain visible.</p></div><ol class="gap-change-log" data-gap-change-log data-gap-id="${escapeHtml(gap.gap_id)}"><li data-change-id="${escapeHtml(opening.change_id)}"><strong>${escapeHtml(opening.changed_at)} · ${escapeHtml(opening.change_type)}</strong><p>${escapeHtml(opening.summary)}</p><small>${escapeHtml(opening.attribution)}</small></li></ol></section>`;
  return withGapScript(page(`${gap.gap_id} Open Evidence Gap`, gap.claim_text, body, "gaps"), `/gaps/${gap.gap_id}/`);
}

export function renderGapChangeLog() {
  const rows = STATIC_GAP_CHANGE_LOG.map((change) => `<li><strong>${escapeHtml(change.changed_at)} · ${escapeHtml(change.gap_id)} · ${escapeHtml(change.change_type)}</strong><p>${escapeHtml(change.summary)}</p><a href="/gaps/${escapeHtml(change.gap_id)}/">Open gap →</a></li>`).join("");
  const body = `<section class="page-hero"><p class="kicker">Open Evidence Gap Protocol v0.1</p><h1>Public change log</h1><p class="lead">Append-only records for gap openings and human-reviewed challenge outcomes. A submission alone never appears here and never changes a state.</p></section><section><ol class="gap-change-log">${rows}</ol></section>${protocolBoundary}`;
  return withGapScript(page("Open Evidence Gap Change Log", "Append-only public changes for StructEvidence open evidence gaps.", body, "gaps"), "/gaps/changes/");
}

export const GAP_APP_JS = `const value=(form,name)=>String(new FormData(form).get(name)||'').trim()||null;for(const form of document.querySelectorAll('[data-gap-challenge-form]')){const preference=form.querySelector('[name="attribution_preference"]'),named=form.querySelector('[data-named-field]'),organization=form.querySelector('[data-organization-field]');const sync=()=>{const selected=preference.value;named.hidden=selected!=='NAMED';organization.hidden=!['NAMED','ORGANIZATION_ONLY'].includes(selected);named.querySelector('input').required=selected==='NAMED';organization.querySelector('input').required=selected==='ORGANIZATION_ONLY'};preference.addEventListener('change',sync);sync();form.addEventListener('submit',async event=>{event.preventDefault();if(!form.reportValidity())return;const status=form.querySelector('[data-gap-form-status]'),button=form.querySelector('button[type="submit"]'),gapId=form.dataset.gapId;status.textContent='Recording challenge…';button.disabled=true;try{const response=await fetch('/api/gaps/'+encodeURIComponent(gapId)+'/challenge',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({gap_id:gapId,evidence_reference:value(form,'evidence_reference'),effect:value(form,'effect'),note:value(form,'note'),attribution_preference:value(form,'attribution_preference'),attribution_name:value(form,'attribution_name'),organization_name:value(form,'organization_name'),contact_email:value(form,'contact_email')})}),result=await response.json().catch(()=>({}));if(!response.ok){status.textContent=result.error||'Challenge could not be recorded.';return}form.reset();sync();status.textContent='Challenge '+result.challenge_id+' recorded as SUBMITTED. Human acknowledgement target: '+result.acknowledgement_target+'. Initial review target: '+result.initial_review_target+'. No evidence state changed.'}catch{status.textContent='The challenge service is unavailable. Nothing was recorded.'}finally{button.disabled=false}})}for(const list of document.querySelectorAll('[data-gap-change-log]')){fetch('/api/gaps/'+encodeURIComponent(list.dataset.gapId)).then(response=>response.ok?response.json():null).then(result=>{if(!result)return;const known=new Set([...list.querySelectorAll('[data-change-id]')].map(item=>item.dataset.changeId));for(const change of result.change_log||[]){if(known.has(change.change_id))continue;const item=document.createElement('li');item.dataset.changeId=change.change_id;const heading=document.createElement('strong');heading.textContent=change.changed_at+' · '+change.change_type;const summary=document.createElement('p');summary.textContent=change.summary;const attribution=document.createElement('small');attribution.textContent=change.attribution;item.append(heading,summary,attribution);list.append(item)}}).catch(()=>{})}`;

export const GAP_CSS = `
.gap-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}.gap-card{background:var(--white);border:1px solid var(--line);border-top:5px solid var(--accent);padding:28px}.gap-card h3{font-size:1.2rem}.gap-card dl,.gap-facts{margin:22px 0;display:grid;gap:10px}.gap-card dl div,.gap-facts div{display:grid;grid-template-columns:150px 1fr;gap:14px;border-top:1px solid var(--line);padding-top:10px}.gap-card dt,.gap-facts dt{color:var(--muted);font-weight:700}.gap-card dd,.gap-facts dd{margin:0;overflow-wrap:anywhere}.gap-boundary{background:var(--soft);border:1px solid var(--line);border-left:5px solid var(--accent);padding:28px}.gap-boundary ul{padding-left:20px}.gap-columns{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}.gap-columns article{background:var(--white);border:1px solid var(--line);padding:28px}.gap-columns article p,.gap-columns article li{color:var(--muted)}.gap-change-log{list-style:none;padding:0;margin:0;border-top:1px solid var(--line)}.gap-change-log li{padding:22px 0;border-bottom:1px solid var(--line)}.gap-change-log p{margin:8px 0;color:var(--muted)}.gap-change-log small{font-weight:700}.field select{width:100%;border:1px solid #879693;background:#fff;padding:11px;font:inherit}.field[hidden]{display:none}@media(max-width:800px){.gap-grid,.gap-columns{grid-template-columns:1fr}.gap-card dl div,.gap-facts div{grid-template-columns:1fr;gap:3px}}
`;
