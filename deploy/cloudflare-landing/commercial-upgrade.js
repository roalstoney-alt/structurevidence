import { COMMERCIAL_CSS, COMMERCIAL_PAGES, page } from "./commercial-ui.js";
import { renderDecisionBoundaryHome, withCommercialHomepageSeo } from "./decision-boundary.js";

const field = (id, label, input, helper = "", wide = false) => `<label class="field${wide ? " wide" : ""}" for="${id}"><span>${label}</span>${input}${helper ? `<small>${helper}</small>` : ""}</label>`;
export const INTAKE_COPY = Object.freeze({
  en: Object.freeze({
    consent: "I understand that this submission remains customer-private, does not authorize research, and will not be published without separate written authorization.",
    turnstileHelp: "Human verification is required before anything is recorded. If it cannot load, no request is submitted; use the email fallback or try again later.",
    verificationRequired: "Complete human verification before submitting.",
    verificationUnavailable: "Human verification is unavailable. Nothing was recorded; use the email fallback or try again later.",
    recording: "Recording request…",
    reviewFields: "Please review the submitted fields.",
    conflict: "This idempotency key was already used for different request content. Nothing new was recorded; please submit again.",
    requestTooLarge: "The request is too large. Nothing was recorded; reduce the submitted content and try again.",
    verificationFailed: "Human verification failed. Nothing was recorded; complete a new verification and try again.",
    serviceUnavailable: "The secure request service is unavailable. Nothing was recorded.",
    emailFallback: "Use email fallback",
    requestReceived: "Request received",
    status: "Status",
    privacy: "Privacy",
    researchAuthorization: "Research authorization",
    successDetail: "A human will review whether the question is bounded enough to scope. You will receive either a written scope or a request to narrow it. No research starts from this form.",
    returnHome: "Return to StructEvidence →"
  }),
  "zh-CN": Object.freeze({
    consent: "我理解：本次提交内容将保持为客户私有信息；本次提交不授权开展研究；未经另行书面授权，提交内容不会公开发布。",
    turnstileHelp: "在记录任何内容之前，必须完成人机验证。如果无法加载验证，本次请求不会提交；请改用电子邮件备用方式或稍后重试。",
    verificationRequired: "请在提交前完成人机验证。",
    verificationUnavailable: "人机验证当前不可用。未记录任何内容；请改用电子邮件备用方式或稍后重试。",
    recording: "正在记录请求……",
    reviewFields: "请检查所提交的字段。",
    conflict: "此幂等键已用于不同的请求内容。未新增任何记录；请重新提交。",
    requestTooLarge: "请求内容过大。未记录任何内容；请减少提交内容后重试。",
    verificationFailed: "人机验证失败。未记录任何内容；请重新完成人机验证后再试。",
    serviceUnavailable: "安全请求服务当前不可用。未记录任何内容。",
    emailFallback: "改用电子邮件备用方式",
    requestReceived: "已收到请求",
    status: "状态",
    privacy: "隐私",
    researchAuthorization: "研究授权",
    successDetail: "人工将审核该问题是否足够明确，可进入范围界定。您将收到书面范围说明或缩小问题范围的请求。本表单不会启动任何研究。",
    returnHome: "返回 StructEvidence →"
  }),
  es: Object.freeze({
    consent: "Entiendo que este envío permanecerá privado para el cliente, no autoriza la realización de ninguna investigación y no se publicará sin una autorización escrita independiente.",
    turnstileHelp: "Se requiere la verificación humana antes de registrar cualquier dato. Si no puede cargarse, no se envía ninguna solicitud; use la alternativa por correo electrónico o vuelva a intentarlo más tarde.",
    verificationRequired: "Complete la verificación humana antes de enviar la solicitud.",
    verificationUnavailable: "La verificación humana no está disponible. No se registró ningún dato; use la alternativa por correo electrónico o vuelva a intentarlo más tarde.",
    recording: "Registrando la solicitud…",
    reviewFields: "Revise los campos enviados.",
    conflict: "Esta clave de idempotencia ya se utilizó con un contenido de solicitud diferente. No se registró nada nuevo; vuelva a enviar la solicitud.",
    requestTooLarge: "La solicitud es demasiado grande. No se registró ningún dato; reduzca el contenido y vuelva a intentarlo.",
    verificationFailed: "La verificación humana falló. No se registró ningún dato; complete una nueva verificación y vuelva a intentarlo.",
    serviceUnavailable: "El servicio seguro de solicitudes no está disponible. No se registró ningún dato.",
    emailFallback: "Usar la alternativa por correo electrónico",
    requestReceived: "Solicitud recibida",
    status: "Estado",
    privacy: "Privacidad",
    researchAuthorization: "Autorización de investigación",
    successDetail: "Una persona revisará si la pregunta está suficientemente delimitada para definir el alcance. Recibirá un alcance por escrito o una solicitud para acotar la pregunta. Este formulario no inicia ninguna investigación.",
    returnHome: "Volver a StructEvidence →"
  })
});
const acknowledgement = (id) => `<label class="consent wide" for="${id}"><input id="${id}" name="consent_accepted" type="checkbox" required><span data-intake-copy="consent">${INTAKE_COPY.en.consent}</span></label>`;
const turnstileChallenge = `<div class="turnstile-boundary wide"><div class="cf-turnstile" data-sitekey="__TURNSTILE_SITE_KEY__" data-action="public-intake" data-response-field-name="cf-turnstile-response"></div><p data-intake-copy="turnstileHelp">${INTAKE_COPY.en.turnstileHelp}</p></div><script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>`;
const successBoundary = `<aside class="boundary-card"><p class="kicker">Research boundary</p><h2>Submission starts human review.</h2><p>It does not authorize research, publish customer information, or create a finding.</p><ol><li>We test whether the question is bounded.</li><li>We match existing evidence first.</li><li>You receive a written scope or a request to narrow the question.</li><li>Research begins only after separate written authorization.</li></ol><div class="outcomes"><span>SUPPORTED</span><span>CONTRADICTED</span><span>NOT ESTABLISHED</span><span>UNKNOWN</span><span>VERIFICATION REQUIRED</span></div></aside>`;
const cycleBoundary = `<p class="scope-note"><strong>Evidence cut-off:</strong> each engagement is delivered against an explicit cut-off timestamp on the delivery date. No free revision rounds are included. Evidence published after that timestamp requires a separately purchased collection cycle. When a subsequent cycle is purchased, qualifying new evidence is incorporated and any superseded state is corrected as part of that cycle.</p>`;

const verifyBody = `<section class="page-hero"><p class="kicker">Verify a Claim</p><h1>Test one critical claim before you commit.</h1><p class="lead">Define the claim, the decision it affects, and the evidence you already have. Existing evidence is matched first. New work is proposed only if a bounded unknown can change the decision.</p><p class="scope-note">Customer submission does not automatically authorize research.</p></section><section><div class="section-head"><p class="kicker">Use case</p><h2>One statement blocking one decision.</h2></div><div class="detail-grid"><article><h3>Good fit</h3><ul><li>Real field-deployment claims</li><li>Supplier or production-readiness claims</li><li>Component substitution or qualification claims</li></ul></article><article><h3>Evidence Verification Record</h3><ul><li>CLAIM and DECISION_AFFECTED</li><li>CURRENT_STATE and source boundary</li><li>EVIDENCE and COUNTER_EVIDENCE</li></ul></article><article><h3>What remains visible</h3><ul><li>WHAT_CHANGED / WHAT_DID_NOT_CHANGE</li><li>REMAINING_UNKNOWNS</li><li>Minimum next verification</li></ul></article></div><p class="scope-note"><strong>Not suitable for:</strong> guaranteed outcomes, legal assurance, investment recommendations, anonymous accusations, or unrestricted investigation. If company-specific context is required, we will say so before paid work begins.</p>${cycleBoundary}</section><section class="form-layout"><form data-request-form data-request-type="VERIFY"><h2>Submit one claim for human review</h2><p class="form-intro wide">This is a review request, not authorization to begin research.</p>${field("v-email", "Email *", '<input id="v-email" name="email" type="email" autocomplete="email" required>', "We do not require a corporate email domain.")}${field("v-name", "Name *", '<input id="v-name" name="contact_name" autocomplete="name" required>')}${field("v-company", "Organization or project *", '<input id="v-company" name="company" autocomplete="organization" required>')}${field("v-object", "Technical object", '<input id="v-object" name="technical_object">', "Product, system, component, supplier path, or application.")}${field("v-claim", "The claim *", '<textarea id="v-claim" name="claim_or_question" required></textarea>', "Write one bounded statement.", true)}${field("v-decision", "Decision this claim affects *", '<textarea id="v-decision" name="decision" required></textarea>', "What commitment depends on treating the claim as established?", true)}${field("v-belief", "Current belief", '<textarea id="v-belief" name="current_belief"></textarea>', "Your current view may be supported, contradicted, or remain unresolved.", true)}${field("v-evidence", "Evidence and known counter-evidence", '<textarea id="v-evidence" name="existing_evidence"></textarea>', "Provide links or document names only. Do not paste secrets.", true)}${field("v-timing", "Decision timing *", '<select id="v-timing" name="decision_timing" required><option value="">Select</option><option>Informational</option><option>This quarter</option><option>Blocking a live commitment</option></select>')}${field("v-deadline", "Decision deadline", '<input id="v-deadline" name="decision_deadline" type="date">')}${acknowledgement("v-private")}${turnstileChallenge}<button class="button" type="submit">Submit for human review</button><div class="form-status" data-form-status role="status" aria-live="polite"></div></form>${successBoundary}</section>`;

const contextBody = `<section class="page-hero"><p class="kicker">Decision Context</p><h1>Start with your decision.</h1><p class="lead">Describe the decision boundary, current dependency, alternative path, and timing. Customer context remains separate from public research.</p></section><section><div class="section-head"><p class="kicker">Scope</p><h2>Map the evidence around a real decision.</h2></div><div class="detail-grid"><article><h3>Decision frame</h3><p>The commitment, intended use, deadline, and constraints.</p></article><article><h3>Gap map</h3><p>Dependency transfer, qualification gaps, and customer-specific unknowns.</p></article><article><h3>Minimum next evidence</h3><p>The smallest evidence capable of changing the decision.</p></article></div>${cycleBoundary}</section><section class="form-layout"><form data-request-form data-request-type="CONTEXT"><h2>Submit decision context</h2><p class="form-intro wide">Send the minimum context needed for human scoping. Do not send a full data room.</p>${field("c-email", "Email *", '<input id="c-email" name="email" type="email" autocomplete="email" required>')}${field("c-name", "Name *", '<input id="c-name" name="contact_name" autocomplete="name" required>')}${field("c-company", "Organization or project *", '<input id="c-company" name="company" autocomplete="organization" required>')}${field("c-object", "Product, system, or application", '<input id="c-object" name="technical_object">')}${field("c-decision", "Decision boundary *", '<textarea id="c-decision" name="decision" required></textarea>', "What must be decided, and what would count as defensible?", true)}${field("c-current", "Current dependency *", '<textarea id="c-current" name="current_dependency" required></textarea>', "Current architecture, supplier, component, or path.", true)}${field("c-alternative", "Alternative path", '<textarea id="c-alternative" name="alternative_considered"></textarea>', "What is being considered instead?", true)}${field("c-change", "What would change the decision?", '<textarea id="c-change" name="what_would_change"></textarea>', "Name the smallest evidence that would move you.", true)}${field("c-timing", "Decision timing *", '<select id="c-timing" name="decision_timing" required><option value="">Select</option><option>Exploratory</option><option>This quarter</option><option>Commitment pending</option></select>')}${field("c-deadline", "Decision deadline", '<input id="c-deadline" name="decision_deadline" type="date">')}${field("c-output", "Requested output", '<input id="c-output" name="requested_output">')}${acknowledgement("c-private")}${turnstileChallenge}<button class="button" type="submit">Submit for human review</button><div class="form-status" data-form-status role="status" aria-live="polite"></div></form>${successBoundary}</section>`;

const decisionBody = `<section class="page-hero"><p class="kicker">Decision Pack</p><h1>Turn evidence into an action path.</h1><p class="lead">A decision-relevant package of known evidence, counter-evidence, unknowns, transferred dependencies, qualification gaps, and bounded action options. No forced answer.</p><a class="text-link" href="https://structurevidence.org/reports/STRUCTUREEVIDENCE_800VDC_DECISION_PACK_SAMPLE_v1.0.pdf">Download the 800V DC sample pack →</a></section><section><div class="section-head"><p class="kicker">Decision Evidence Pack</p><h2>Knowns, gaps, and actions stay separate.</h2></div><div class="detail-grid"><article><h3>Evidence state</h3><ul><li>DECISION_AFFECTED</li><li>EVIDENCE_ESTABLISHED</li><li>COUNTER_EVIDENCE</li></ul></article><article><h3>Decision gaps</h3><ul><li>OPEN_GAPS</li><li>DEPENDENCY_TRANSFER</li><li>QUALIFICATION_GAPS</li></ul></article><article><h3>Action options</h3><ul><li>Bounded next steps</li><li>Evidence conditions</li><li>Stop and escalation conditions</li></ul></article></div><p class="scope-note">Use Verify a Claim when one assertion is the blocker. Use a Decision Pack when the decision depends on several evidence states, dependencies, qualifications, and timing constraints at once.</p>${cycleBoundary}</section><section class="form-layout"><form data-request-form data-request-type="CONTEXT"><input type="hidden" name="requested_output" value="DECISION_PACK"><h2>Request a Decision Pack scope</h2><p class="form-intro wide">Describe the decision, not a full data room. We will identify the minimum required evidence.</p>${field("d-email", "Email *", '<input id="d-email" name="email" type="email" autocomplete="email" required>')}${field("d-name", "Name *", '<input id="d-name" name="contact_name" autocomplete="name" required>')}${field("d-company", "Organization or project *", '<input id="d-company" name="company" autocomplete="organization" required>')}${field("d-object", "Product, system, or application", '<input id="d-object" name="technical_object">')}${field("d-decision", "Decision boundary *", '<textarea id="d-decision" name="decision" required></textarea>', "What must be decided, and what would count as defensible?", true)}${field("d-current", "Current dependency *", '<textarea id="d-current" name="current_dependency" required></textarea>', "Current architecture, supplier, component, or path.", true)}${field("d-alternative", "Alternative path", '<textarea id="d-alternative" name="alternative_considered"></textarea>', "What is being considered instead?", true)}${field("d-change", "What would change the decision? *", '<textarea id="d-change" name="what_would_change" required></textarea>', "The smallest evidence capable of moving the decision.", true)}${field("d-timing", "Decision timing *", '<select id="d-timing" name="decision_timing" required><option value="">Select</option><option>Exploratory</option><option>This quarter</option><option>Commitment pending</option></select>')}${field("d-deadline", "Decision deadline", '<input id="d-deadline" name="decision_deadline" type="date">')}${acknowledgement("d-private")}${turnstileChallenge}<button class="button" type="submit">Request written scope</button><div class="form-status" data-form-status role="status" aria-live="polite"></div></form>${successBoundary}</section>`;

const deliverablesBody = `<section class="page-hero"><p class="kicker">Deliverables</p><h1>Inspect the work before you buy it.</h1><p class="lead">Every engagement names its evidence boundary, cut-off timestamp, output, unresolved questions, and next verification step.</p></section><section><div class="section-head"><p class="kicker">Public samples</p><h2>Three ways to inspect the evidence system.</h2></div><div class="detail-grid"><article><h3>800V DC Decision Pack sample</h3><p>A five-page, customer-neutral example showing the decision frame, evidence register, gap map, and bounded actions.</p><a class="text-link" href="https://structurevidence.org/reports/STRUCTUREEVIDENCE_800VDC_DECISION_PACK_SAMPLE_v1.0.pdf">Download PDF →</a></article><article><h3>BNB monitoring snapshot</h3><p>A frozen structural and evidence-state monitoring delivery.</p><a class="text-link" href="https://structurevidence.org/reports/DEMO_BNB_MONITORING_SNAPSHOT_v1.0.pdf">Download PDF →</a></article><article><h3>800V DC live evidence case</h3><p>The underlying public evidence chain, including accepted evidence and preserved unknowns.</p><a class="text-link" href="https://structurevidence.org/cases/800vdc/">Open live case →</a></article></div>${cycleBoundary}</section><section><div class="section-head"><p class="kicker">Artifact structure</p><h2>Decision-relevant, traceable, bounded.</h2></div><div class="detail-grid"><article><h3>Evidence Verification Record</h3><p>Claim, decision affected, evidence, counter-evidence, state, unknowns, and minimum next verification.</p></article><article><h3>Migration / Qualification Gap Map</h3><p>Current dependency, alternative path, transferred dependencies, qualification gaps, and resolving evidence.</p></article><article><h3>Decision Evidence Pack</h3><p>Established evidence, open gaps, dependency transfer, qualification boundaries, and action options.</p></article></div></section>`;

const pricingBody = `<section class="page-hero"><p class="kicker">Pricing</p><h1>Standard fees with a written scope.</h1><p class="lead">Choose the smallest engagement capable of answering the decision.</p></section><section><div class="price-grid"><article><p class="kicker">01 · Claim Verification</p><strong>USD 199</strong><h3>One narrow claim</h3><ul><li>Evidence Verification Record</li><li>Explicit state and unknowns</li><li>One evidence cut-off timestamp</li></ul><a class="button small" href="/verify/">Submit a claim</a></article><article><p class="kicker">02 · Decision Context Review</p><strong>USD 1,999</strong><h3>One company decision</h3><ul><li>Decision and evidence map</li><li>Dependency and qualification gaps</li><li>One evidence cut-off timestamp</li></ul><a class="button small" href="/context/">Submit context</a></article><article><p class="kicker">03 · Decision Pack</p><strong>USD 4,999</strong><h3>Structured decision package</h3><ul><li>Evidence, gaps, and dependencies</li><li>Bounded action options</li><li>One evidence cut-off timestamp</li></ul><a class="button small" href="/decision-pack/">Request a pack</a></article></div></section><section><div class="section-head"><p class="kicker">Service-cycle boundary</p><h2>Each fee purchases one dated evidence cycle.</h2></div><div class="detail-grid"><article><h3>No included revision rounds</h3><p>Each service is a frozen, traceable delivery as of its stated cut-off timestamp. Clarification of an error is not a new evidence search.</p></article><article><h3>Future evidence</h3><p>Evidence published after the cut-off is outside the purchased cycle and requires a separately paid collection cycle.</p></article><article><h3>Next cycle correction</h3><p>When a later cycle is purchased, qualifying new evidence is incorporated and any superseded evidence state is corrected automatically within that new delivery.</p></article></div><p class="scope-note">Rush handling costs USD 399 per request in addition to the selected tier, subject to capacity and written acceptance. Contracts, formal quotations, and invoices are available.</p></section><section><div class="section-head"><p class="kicker">Cancellation and refund</p><h2>Research capacity is reserved when work begins.</h2></div><p>After research begins, fees are generally non-refundable because research capacity and computational or third-party costs are consumed. Exceptions include duplicate payment, failure to deliver the agreed scope, material service error, written exceptions, and rights required by applicable law.</p><a class="text-link" href="/terms/">Read the commercial terms →</a></section>`;

const termsBody = `<section class="page-hero"><p class="kicker">Terms</p><h1>Commercial service boundary.</h1><p class="lead">MATRIX ASIA PACIFIC LIMITED provides manually scoped StructEvidence research services. Submission is not an engagement or research authorization.</p></section><section><div class="detail-grid"><article><h3>Written scope</h3><p>The accepted contract or scope controls the question, exclusions, responsible researcher, output, cut-off timestamp, quote, invoice, and customer-data boundary.</p></article><article><h3>Evidence state</h3><p>Payment does not determine a finding. Results may remain NOT ESTABLISHED, UNKNOWN, or VERIFICATION REQUIRED.</p></article><article><h3>Customer responsibility</h3><p>Customers remain responsible for engineering, legal, financial, safety, procurement, and qualification decisions.</p></article></div></section><section><div class="section-head"><p class="kicker">Evidence-cycle terms</p><h2>Dated delivery, no included revision rounds.</h2></div><p>Each engagement covers evidence available and accepted up to the explicit cut-off timestamp stated for that delivery. Evidence appearing later is outside the completed scope and requires a new paid collection cycle.</p><p>When a subsequent service cycle is purchased, qualifying new evidence is incorporated and any prior state that has become superseded is corrected in that cycle. This does not constitute continuous monitoring or a free revision obligation.</p></section><section><div class="section-head"><p class="kicker">Cancellation, refund, and rush</p><h2>Agreed before work begins.</h2></div><p>After research begins, fees are generally non-refundable because research capacity and computational or third-party costs are consumed. Rush handling costs USD 399 per request and does not bypass evidence, privacy, or authorization controls.</p></section><section class="final"><h2>Questions about an engagement?</h2><a class="button" href="mailto:support@structevidence.com">Contact support</a></section>`;


const localizeChrome = (html, locale) => {
  if (locale === "zh-CN") return html
    .replace('<html lang="en">','<html lang="zh-CN">')
    .replace('>Skip to content<','>跳到正文<')
    .replace('>Verify a Claim<','>验证判断<')
    .replace('>Decision Pack<','>决策证据包<')
    .replace('>Pricing<','>价格<')
    .replace('>Deliverables<','>交付物<')
    .replace('>About<','>关于<')
    .replace('>Research<','>公开研究<')
    .replace('Technical evidence for consequential decisions.','为关键决策提供可追溯技术证据。')
    .replace('Customer submissions remain separate from public research. No BOM, internal document, or company context is published without separate written authorization.','客户提交内容与公开研究严格分离。未经单独书面授权，不公开 BOM、内部文件或公司决策背景。')
    .replace('Research service only. Not investment advice, legal assurance, a credit rating, health score, or trading signal.','仅提供研究服务；不构成投资建议、法律保证、信用评级、健康评分或交易信号。')
    .replaceAll('href="/verify/"','href="/verify/?lang=zh-CN"')
    .replaceAll('href="/context/"','href="/context/?lang=zh-CN"')
    .replaceAll('href="/decision-pack/"','href="/decision-pack/?lang=zh-CN"');
  if (locale === "es") return html
    .replace('<html lang="en">','<html lang="es">')
    .replace('>Skip to content<','>Ir al contenido<')
    .replace('>Verify a Claim<','>Verificar afirmación<')
    .replace('>Decision Pack<','>Paquete de decisión<')
    .replace('>Pricing<','>Precios<')
    .replace('>Deliverables<','>Entregables<')
    .replace('>About<','>Acerca de<')
    .replace('>Research<','>Investigación pública<')
    .replace('Technical evidence for consequential decisions.','Evidencia técnica trazable para decisiones importantes.')
    .replace('Customer submissions remain separate from public research. No BOM, internal document, or company context is published without separate written authorization.','Los datos del cliente permanecen separados de la investigación pública. No se publica ningún BOM, documento interno o contexto empresarial sin autorización escrita independiente.')
    .replace('Research service only. Not investment advice, legal assurance, a credit rating, health score, or trading signal.','Servicio de investigación únicamente. No constituye asesoramiento de inversión, garantía legal, calificación crediticia ni señal de trading.')
    .replaceAll('href="/verify/"','href="/verify/?lang=es"')
    .replaceAll('href="/context/"','href="/context/?lang=es"')
    .replaceAll('href="/decision-pack/"','href="/decision-pack/?lang=es"');
  return html;
};

const englishCommercialPage = withCommercialHomepageSeo(page("Decision Boundary", "Inspect what is established, unknown, changed, and capable of changing a technical decision boundary.", renderDecisionBoundaryHome("en"), "home"), "/");
const englishCommercialAlias = withCommercialHomepageSeo(page("Decision Boundary", "Inspect what is established, unknown, changed, and capable of changing a technical decision boundary.", renderDecisionBoundaryHome("en"), "home"), "/en/");
const zhCommercialPage = withCommercialHomepageSeo(localizeChrome(page("决策边界", "检查技术决策中已建立、未知、已变化及可改变记录的条件。", renderDecisionBoundaryHome("zh-CN"), "zh-cn"), "zh-CN"), "/zh-cn/");
const esCommercialPage = withCommercialHomepageSeo(localizeChrome(page("Límite de decisión", "Inspecciona lo establecido, desconocido, cambiado y capaz de cambiar un límite de decisión técnico.", renderDecisionBoundaryHome("es"), "es"), "es"), "/es/");

export const COMMERCIAL_PAGES_V2 = {
  ...COMMERCIAL_PAGES,
  "/": englishCommercialPage,
  "/en/": englishCommercialAlias,
  "/zh-cn/": zhCommercialPage,
  "/es/": esCommercialPage,
  "/verify/": page("Verify a Claim", "Test one technical or industrial claim before you commit.", verifyBody, "verify"),
  "/context/": page("Start with Your Decision", "Submit company-specific decision context for human review.", contextBody, "context"),
  "/decision-pack/": page("Decision Pack", "Request a traceable package of evidence, gaps, and action options.", decisionBody, "decision-pack"),
  "/pricing/": page("Pricing", "Standard service fees and dated evidence-cycle boundaries.", pricingBody, "pricing"),
  "/deliverables/": page("Deliverables", "Inspect public StructEvidence deliverable samples and evidence-cycle boundaries.", deliverablesBody, "deliverables"),
  "/terms/": page("Terms", "StructEvidence commercial and evidence-cycle boundaries.", termsBody, "terms")
};

export const COMMERCIAL_APP_JS_UPGRADE = `
const params = new URLSearchParams(location.search);
const CONSENT_VERSION = "SE-CUSTOMER-PRIVACY-v1";
const INTAKE_COPY = ${JSON.stringify(INTAKE_COPY)};
const requestedLocale = params.get("lang");
const intakeLocale = requestedLocale === "zh-CN" || requestedLocale === "zh-cn" ? "zh-CN" : requestedLocale === "es" ? "es" : "en";
const intakeCopy = INTAKE_COPY[intakeLocale];
for (const element of document.querySelectorAll("[data-intake-copy]")) {
  const key = element.dataset.intakeCopy;
  if (intakeCopy[key]) element.textContent = intakeCopy[key];
  element.lang = intakeLocale;
}
const output = document.querySelector('[name="requested_output"]');
if (output && params.get("intent")) output.value = params.get("intent");
const prefill = (name, key) => {
  const field = document.querySelector('[name="' + name + '"]'), value = params.get(key);
  if (field && value && !field.value) field.value = value;
};
prefill('claim_or_question','question');
prefill('existing_evidence','minimum_missing_evidence');
const clean = (value) => String(value || "").trim();
function payload(form) {
  const data = new FormData(form), get = (name) => clean(data.get(name)) || null;
  const timing = get("decision_timing"), change = get("what_would_change"), existing = get("existing_evidence"), belief = get("current_belief");
  return {
    request_type: form.dataset.requestType,
    contact_name: get("contact_name"), email: get("email"), company: get("company"),
    decision: get("decision"), claim_or_question: get("claim_or_question"), technical_object: get("technical_object"),
    current_dependency: get("current_dependency"), alternative_considered: get("alternative_considered"),
    decision_deadline: get("decision_deadline"), case_reference: get("case_reference"), requested_output: get("requested_output"),
    current_belief: [belief, timing && "Decision timing: " + timing].filter(Boolean).join("\\n\\n") || null,
    existing_evidence: [existing, change && "What would change the decision: " + change].filter(Boolean).join("\\n\\n") || null,
    consent_accepted: data.get("consent_accepted") === "on",
    consent_version: CONSENT_VERSION,
    turnstile_token: get("cf-turnstile-response")
  };
}
function resetChallenge(form) {
  if (window.turnstile) {
    const widget = form.querySelector(".cf-turnstile");
    try { window.turnstile.reset(widget); } catch { window.turnstile.reset(); }
  }
}
function showSuccess(status, id) {
  status.classList.add("confirmation-panel");
  status.lang = intakeLocale;
  const authorizationBoundary = intakeLocale === "en" ? '<dt>Research authorization</dt><dd>NOT_AUTHORIZED</dd>' : '<dt>' + intakeCopy.researchAuthorization + '</dt><dd>NOT_AUTHORIZED</dd>';
  status.innerHTML = '<p class="kicker">' + intakeCopy.requestReceived + '</p><h3>' + id + '</h3><dl><div><dt>' + intakeCopy.status + '</dt><dd>SUBMITTED</dd></div><div><dt>' + intakeCopy.privacy + '</dt><dd>CUSTOMER_PRIVATE</dd></div><div>' + authorizationBoundary + '</div></dl><p>' + intakeCopy.successDetail + '</p><a class="text-link" href="/">' + intakeCopy.returnHome + '</a>';
}
for (const form of document.querySelectorAll("[data-request-form]")) {
  const caseRef = params.get("case"), gap = params.get("gap");
  const protocolRef = [params.get('claim_id') && "Claim: " + params.get('claim_id'), params.get('match_class') && "Match: " + params.get('match_class'), params.get('rdl') && "RDL candidate: " + params.get('rdl')].filter(Boolean);
  if ((caseRef || protocolRef.length) && !form.querySelector('[name="case_reference"]')) {
    const hidden = document.createElement("input"); hidden.type = "hidden"; hidden.name = "case_reference";
    hidden.value = [caseRef + (gap ? " / " + gap : ""), ...protocolRef].filter(Boolean).join(" / "); form.append(hidden);
  }
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const status = form.querySelector("[data-form-status]"), button = form.querySelector('button[type="submit"]');
    status.lang = intakeLocale;
    const siteKey = form.querySelector(".cf-turnstile")?.dataset.sitekey;
    const body = payload(form);
    if (!siteKey || !body.turnstile_token) {
      status.textContent = siteKey ? intakeCopy.verificationRequired : intakeCopy.verificationUnavailable;
      return;
    }
    form.dataset.idempotencyKey ||= crypto.randomUUID().replaceAll("-", "");
    status.classList.remove("confirmation-panel"); status.textContent = intakeCopy.recording; button.disabled = true;
    try {
      const response = await fetch("/api/requests", { method: "POST", headers: { "content-type": "application/json", "idempotency-key": form.dataset.idempotencyKey }, body: JSON.stringify(body) });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) {
        if (response.status === 409) delete form.dataset.idempotencyKey;
        resetChallenge(form);
        if (response.status >= 500) throw new Error("unavailable");
        status.textContent = response.status === 409 ? intakeCopy.conflict : response.status === 413 ? intakeCopy.requestTooLarge : /Human verification/i.test(result.error || "") ? intakeCopy.verificationFailed : intakeCopy.reviewFields; return;
      }
      delete form.dataset.idempotencyKey; form.reset(); showSuccess(status, result.request_id);
    } catch {
      resetChallenge(form);
      const fallback = "mailto:support@structevidence.com?subject=" + encodeURIComponent("StructEvidence request fallback");
      status.innerHTML = intakeCopy.serviceUnavailable + ' <a href="' + fallback + '">' + intakeCopy.emailFallback + '</a>.';
    } finally { button.disabled = false; }
  });
}`;

export const COMMERCIAL_CSS_V2 = `${COMMERCIAL_CSS}\n.lang-switch{display:flex;gap:6px;align-items:center;margin-left:auto}.lang-switch a{padding:6px 8px;border:1px solid var(--line);text-decoration:none;font-size:.72rem;font-weight:800}.lang-switch a:hover{border-color:var(--accent)}@media(max-width:800px){.site-header{flex-wrap:wrap}.lang-switch{width:100%;justify-content:flex-end;margin-top:8px}}\n.field small,.form-intro{color:var(--muted);font-weight:500}.field select{width:100%;border:1px solid #879693;background:#fff;padding:11px;font:inherit}.consent{display:flex;gap:12px;align-items:flex-start;padding:16px;border:1px solid var(--line);background:var(--soft);font-weight:700}.consent input{margin-top:5px}.turnstile-boundary{padding:16px;border:1px solid var(--line)}.turnstile-boundary p{color:var(--muted);font-size:.82rem;margin:10px 0 0}.confirmation-panel{background:var(--soft);border:1px solid var(--accent);border-left:5px solid var(--accent);padding:24px}.confirmation-panel h3{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:1rem;overflow-wrap:anywhere}.confirmation-panel dl{display:grid;gap:8px}.confirmation-panel dl div{display:grid;grid-template-columns:180px 1fr;gap:12px}.confirmation-panel dt{color:var(--muted)}.confirmation-panel dd{margin:0;font-weight:800}.boundary-card ol{padding-left:20px;color:var(--muted)}.boundary-split,.decision-flow,.availability-grid{display:grid;gap:18px}.boundary-split{grid-template-columns:repeat(2,1fr)}.decision-flow{grid-template-columns:repeat(4,1fr)}.availability-grid{grid-template-columns:repeat(3,1fr)}.boundary-split article,.decision-flow article,.availability-grid article{background:var(--white);border:1px solid var(--line);padding:28px}.decision-flow article{border-top:5px solid var(--accent)}.boundary-split p,.decision-flow p,.availability-grid p{color:var(--muted)}.availability{display:inline-block;padding:7px 9px;margin-bottom:18px;border:1px solid var(--ink);font-size:.68rem;font-weight:900;letter-spacing:.06em;overflow-wrap:anywhere}.availability.live{background:var(--ink);color:#fff}.availability.available_with_human_scope{border-color:var(--accent);color:var(--accent)}.availability.proposed_not_live{border-style:dashed;color:var(--muted)}.snapshot-meta{display:grid;grid-template-columns:repeat(2,1fr);gap:0 24px;margin:32px 0;background:var(--soft);padding:22px}.snapshot-meta div{display:grid;grid-template-columns:150px 1fr;gap:12px;padding:10px 0;border-bottom:1px solid var(--line)}.snapshot-meta dt{font-weight:800}.snapshot-meta dd{margin:0;overflow-wrap:anywhere}.reference-links{display:flex;gap:18px;flex-wrap:wrap}.public-example code{font-size:.76rem}footer{grid-template-columns:.7fr 1.2fr 1.2fr .9fr}.footer-boundary p{margin:0 0 12px}@media(max-width:1000px){footer{grid-template-columns:1fr 1fr}.decision-flow,.availability-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:800px){footer,.boundary-split,.decision-flow,.availability-grid,.snapshot-meta{grid-template-columns:1fr}.confirmation-panel dl div,.snapshot-meta div{grid-template-columns:1fr;gap:2px}}`;
