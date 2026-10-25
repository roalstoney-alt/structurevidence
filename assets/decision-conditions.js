(() => {
  "use strict";
  document.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-copy-decision-conditions]");
    if (!button) return;
    const source = document.getElementById(button.dataset.copySource || "");
    const card = button.closest("[data-decision-condition]");
    const status = card && card.querySelector("[data-copy-status]");
    if (!source) {
      if (status) status.textContent = "Citation unavailable.";
      return;
    }
    try {
      if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error("clipboard unavailable");
      await navigator.clipboard.writeText(source.value);
      if (status) status.textContent = "Complete decision conditions copied.";
    } catch (_error) {
      source.focus();
      source.select();
      if (status) status.textContent = "Select and copy the highlighted citation.";
    }
  });
})();
