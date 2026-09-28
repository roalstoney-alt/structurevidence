document.querySelectorAll("[data-product-nav-toggle]").forEach((button) => {
  button.addEventListener("click", () => {
    const nav = document.getElementById(button.getAttribute("aria-controls"));
    const open = button.getAttribute("aria-expanded") === "true";
    button.setAttribute("aria-expanded", String(!open));
    nav.classList.toggle("open", !open);
  });
});

const params = new URLSearchParams(window.location.search);
document.querySelectorAll("[data-query-field]").forEach((field) => {
  const value = params.get(field.dataset.queryField);
  if (value) field.value = value;
});

const API_ENDPOINT = "https://structevidence.com/api/requests";

function payloadFor(form) {
  const data = new FormData(form);
  const value = (name) => String(data.get(name) || "").trim() || null;
  if (form.dataset.requestType === "VERIFY") return { request_type: "VERIFY", contact_name: value("contact_name"), email: value("email"), company: value("company_or_project"), decision: value("decision_affected"), claim_or_question: value("claim_or_question"), technical_object: value("technical_object"), decision_deadline: value("decision_deadline"), case_reference: value("case_reference"), requested_output: "EVIDENCE_VERIFICATION_RECORD", current_belief: value("current_belief"), existing_evidence: value("existing_evidence") };
  return { request_type: "CONTEXT", contact_name: value("contact_name"), email: value("email"), company: value("company_or_project"), decision: value("decision"), technical_object: value("product_system_application"), current_dependency: value("current_technology_or_dependency"), alternative_considered: value("alternative_considered"), decision_deadline: value("decision_deadline"), case_reference: value("case_reference"), requested_output: value("intent") };
}

function fallbackLink(form, payload, status) {
  const subject = form.dataset.subject || "StructureEvidence scope request";
  const fields = Object.entries(payload).filter(([, value]) => value).map(([key, value]) => `${key.replaceAll("_", " ").toUpperCase()}: ${value}`);
  const link = document.createElement("a");
  link.href = `mailto:support@structevidence.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(fields.join("\n\n"))}`;
  link.textContent = "Use email fallback";
  status.replaceChildren(document.createTextNode("The secure request service is unavailable. Nothing was recorded. "), link, document.createTextNode(" and clearly identify the message as a fallback submission."));
}

document.querySelectorAll("[data-scope-form]").forEach((form) => {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (window.location.hostname === "structurevidence.org" || window.location.hostname === "www.structurevidence.org") {
      window.location.href = form.dataset.requestType === "VERIFY" ? "https://structevidence.com/verify/" : "https://structevidence.com/context/";
      return;
    }
    if (!form.reportValidity()) return;
    const status = form.querySelector("[data-form-status]");
    const button = form.querySelector("button[type=submit]");
    const payload = payloadFor(form);
    status.textContent = "Recording request…";
    button.disabled = true;
    try {
      const response = await fetch(API_ENDPOINT, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(payload) });
      const result = await response.json().catch(() => ({}));
      if (!response.ok && response.status < 500) {
        status.textContent = result.error || "Please review the submitted fields.";
        return;
      }
      if (!response.ok) throw new Error(result.error || "Request service unavailable");
      const title = document.createElement("strong");
      title.textContent = "Request received.";
      status.replaceChildren(title, document.createElement("br"), document.createTextNode(`Request ID: ${result.request_id}`), document.createElement("br"), document.createTextNode("Status: SUBMITTED"), document.createElement("br"), document.createTextNode("Research authorization: NOT AUTHORIZED"), document.createElement("br"), document.createTextNode("Your request has been recorded for human review. Submission does not authorize research."));
      form.reset();
    } catch {
      fallbackLink(form, payload, status);
    } finally {
      button.disabled = false;
    }
  });
});


// Copy only a complete, bounded public citation. The card's visible fields remain the source.
document.querySelectorAll("[data-copy-stop]").forEach((button) => {
  button.addEventListener("click", async () => {
    const card = button.closest("[data-stop-point]");
    const keys = ["claim", "scope", "cutoff", "state", "supports", "limits", "next"];
    const values = Object.fromEntries(keys.map((key) => [key, card.querySelector('[data-stop-field="' + key + '"]')?.textContent.trim() || ""]));
    const version = card.dataset.version, url = card.dataset.stableUrl;
    const status = card.querySelector("[data-copy-status]");
    if (Object.values(values).some((value) => !value) || !version || !url) { status.textContent = "Citation is incomplete; copy blocked."; return; }
    const citation = ["Claim: " + values.claim, "Scope: " + values.scope, "Time boundary: " + values.cutoff, "State: " + values.state, "Supports: " + values.supports, "Does not support: " + values.limits, "Next minimum verification: " + values.next, "Version: " + version, "Stable URL: " + url].join("\n");
    try { await navigator.clipboard.writeText(citation); status.textContent = "Complete citation copied, including limits."; }
    catch { status.textContent = "Clipboard unavailable. Open the permanent citation page to copy its text."; }
  });
});
const publicEvidenceForm = document.querySelector("[data-public-evidence-form]");
if (publicEvidenceForm) {
  const caseField = publicEvidenceForm.querySelector("[data-evidence-case]");
  const selectedCase = params.get("case");
  if ([...caseField.options].some((option) => option.value === selectedCase)) caseField.value = selectedCase;
  const status = publicEvidenceForm.querySelector("[data-evidence-status]");
  const submissionText = () => {
    const data = new FormData(publicEvidenceForm);
    const value = (key) => String(data.get(key) || "").trim();
    return ["Case: " + value("case_reference"), "Statement: " + value("claim"), "Source role: " + value("source_role"), "Source access: " + value("source_access"), "Public source URL / identifier: " + value("source_reference"), "Why this may change the boundary: " + value("reason"), "I provided no personal medical records or confidential content."].join("\n\n");
  };
  publicEvidenceForm.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!publicEvidenceForm.reportValidity()) return;
    const subject = "Public evidence review | " + caseField.value;
    window.location.href = "mailto:support@structevidence.com?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(submissionText());
    status.textContent = "Email draft prepared. Nothing is received until you send it from your mail application.";
  });
  publicEvidenceForm.querySelector("[data-copy-submission]").addEventListener("click", async () => {
    if (!publicEvidenceForm.reportValidity()) return;
    try { await navigator.clipboard.writeText(submissionText()); status.textContent = "Submission text copied. Send it to support@structevidence.com with the case ID in the subject."; }
    catch { status.textContent = "Clipboard unavailable. Use the email submission button."; }
  });
}
