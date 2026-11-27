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
  const subject = form.dataset.subject || "StructEvidence scope request";
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

document.querySelectorAll("[data-copy-citation]").forEach((button) => {
  button.addEventListener("click", async () => {
    const status = button.parentElement.querySelector("[data-citation-status]");
    try {
      await navigator.clipboard.writeText(button.dataset.citation);
      status.textContent = " Citation copied.";
    } catch {
      status.textContent = " Clipboard unavailable; copy the citation text above.";
    }
  });
});

const activitySummary = document.querySelector("[data-activity-summary]");
if (activitySummary) {
  const status = document.querySelector("[data-activity-status]");
  fetch(activitySummary.dataset.source, { cache: "no-cache" })
    .then((response) => response.ok ? response.json() : Promise.reject(new Error("change feed unavailable")))
    .then((feed) => {
      // All recorded totals: do not manufacture a current window from an old generated_at.
      const validDate = value => typeof value === "string" && /^\d{4}-\d{2}-\d{2}$/.test(value) &&
        Number.isFinite(Date.parse(value)) && new Date(value).toISOString().slice(0, 10) === value;
      if (!Array.isArray(feed.changes) || !validDate(feed.generated_at)) throw new Error("invalid feed");
      const seen = new Set();
      const recent = feed.changes;
      const today = new Date().toISOString().slice(0, 10);
      recent.forEach(item => {
        if (!item || typeof item.id !== "string" || !item.id || seen.has(item.id) ||
            typeof item.case_id !== "string" || !item.case_id || !validDate(item.date) || item.date > today ||
            !["STATE_CHANGE", "VERIFIED_EVENT"].includes(item.type) ||
            !Number.isSafeInteger(item.qualifying_evidence_added) || item.qualifying_evidence_added < 0 ||
            !Number.isSafeInteger(item.unknowns_resolved) || item.unknowns_resolved < 0 ||
            typeof item.state_changed !== "boolean") throw new Error("invalid change record");
        seen.add(item.id);
      });
      const values = {
        cases: new Set(recent.map((item) => item.case_id)).size,
        evidence: recent.reduce((sum, item) => sum + (item.qualifying_evidence_added || 0), 0),
        unknowns: recent.reduce((sum, item) => sum + (item.unknowns_resolved || 0), 0),
        states: recent.filter((item) => item.state_changed).length,
      };
      Object.entries(values).forEach(([key, value]) => {
        activitySummary.querySelector(`[data-activity="${key}"]`).textContent = String(value);
      });
      const dates = recent.map(item => item.date).sort();
      const range = dates.length ? `${dates[0]} to ${dates[dates.length - 1]}` : "no dated entries";
      activitySummary.dataset.coverage = "INCOMPLETE";
      if (status) status.textContent = `INCOMPLETE COVERAGE · ${recent.length} recorded entries · Event dates: ${range}. Feed generation metadata: ${feed.generated_at}. These are historical recorded totals, not current operational metrics or a complete case audit.`;
      if (dates.length && dates[dates.length - 1] > feed.generated_at && status)
        status.textContent += " Metadata predates the latest entry; freshness cannot be established.";
    })
    .catch(() => {
      activitySummary.querySelectorAll("[data-activity]").forEach((node) => { node.textContent = "Unavailable"; });
      if (status) status.textContent = "SOURCE_UNAVAILABLE · Public change data could not be loaded or validated. Counts are unknown, not zero.";
    });
}
