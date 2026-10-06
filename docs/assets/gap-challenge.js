const value = (form, name) => String(new FormData(form).get(name) || "").trim() || null;

for (const form of document.querySelectorAll("[data-gap-challenge-form]")) {
  const preference = form.querySelector('[name="attribution_preference"]');
  const named = form.querySelector("[data-named-field]");
  const organization = form.querySelector("[data-organization-field]");
  const status = form.querySelector("[data-gap-form-status]");
  const button = form.querySelector('button[type="submit"]');

  const syncAttributionFields = () => {
    const selected = preference.value;
    named.hidden = selected !== "NAMED";
    organization.hidden = !["NAMED", "ORGANIZATION_ONLY"].includes(selected);
    named.querySelector("input").required = selected === "NAMED";
    organization.querySelector("input").required = selected === "ORGANIZATION_ONLY";
  };

  preference.addEventListener("change", syncAttributionFields);
  syncAttributionFields();

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    status.textContent = "Recording challenge…";
    button.disabled = true;

    try {
      const response = await fetch(form.action, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          gap_id: form.dataset.gapId,
          evidence_reference: value(form, "evidence_reference"),
          effect: value(form, "effect"),
          attribution_preference: value(form, "attribution_preference"),
          attribution_name: value(form, "attribution_name"),
          organization_name: value(form, "organization_name"),
          contact_email: value(form, "contact_email"),
          note: value(form, "note")
        })
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) {
        status.textContent = result.error || "Challenge could not be recorded.";
        return;
      }
      form.reset();
      syncAttributionFields();
      status.textContent = `Challenge ${result.challenge_id} recorded. State: ${result.state}. No evidence state changed.`;
    } catch {
      status.textContent = "The challenge service is unavailable. Nothing was recorded.";
    } finally {
      button.disabled = false;
    }
  });
}
