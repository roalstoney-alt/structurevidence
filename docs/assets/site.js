const mobileQuery = window.matchMedia("(max-width: 760px)");

function syncNavState() {
  document.querySelectorAll("[data-nav-toggle]").forEach((button) => {
    const nav = document.getElementById(button.getAttribute("aria-controls"));
    if (!nav) return;
    if (mobileQuery.matches) {
      nav.hidden = button.getAttribute("aria-expanded") !== "true";
    } else {
      nav.hidden = false;
      button.setAttribute("aria-expanded", "false");
    }
  });
}

document.querySelectorAll("[data-nav-toggle]").forEach((button) => {
  button.addEventListener("click", () => {
    const nav = document.getElementById(button.getAttribute("aria-controls"));
    if (!nav) return;
    const expanded = button.getAttribute("aria-expanded") === "true";
    button.setAttribute("aria-expanded", String(!expanded));
    nav.hidden = expanded;
  });
});

mobileQuery.addEventListener("change", syncNavState);
syncNavState();

let coveredAliases = new Set(["mstr", "strategy", "strategy inc.", "microstrategy"]);
let coveredEntities = [];

function wireReset(region) {
  const reset = region.querySelector("[data-reset-search]");
  if (reset) {
    reset.addEventListener("click", () => {
      const input = document.getElementById("entity-search");
      if (input) {
        input.value = "";
        input.focus();
      }
      region.replaceChildren();
      const url = new URL(window.location.href);
      url.searchParams.delete("q");
      history.replaceState({}, "", `${url.pathname}${url.hash || "#search"}`);
    });
  }
}

function renderTemplate(region, id) {
  const template = document.getElementById(id);
  if (!template || !region) return;
  region.replaceChildren(template.content.cloneNode(true));
  wireReset(region);
}

function escapeText(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[char]);
}

function renderCoveredEntity(region, entity) {
  const structuralState = escapeText(entity.structural_state || "INSUFFICIENT_DATA");
  const evidenceState = escapeText(entity.evidence_state || "INSUFFICIENT_DATA");
  const inconsistency = escapeText(entity.material_inconsistency || "UNRESOLVED");
  const coverage = escapeText(entity.source_coverage || "UNRESOLVED");
  const reviewed = escapeText(entity.last_reviewed || "UNRESOLVED");
  region.innerHTML = `
    <article class="health-card">
      <div class="result-topline"><span>Structural & Evidence Health Card</span><span>HEALTH CARD != HEALTH SCORE</span></div>
      <div class="result-heading"><div><h2>${escapeText(entity.name)}</h2><p>${escapeText(entity.ticker || entity.name)} / ${escapeText(entity.category)}</p></div><button class="button subtle" type="button" data-reset-search>New Search</button></div>
      <div class="health-fields">
        <div><span>STRUCTURAL STATE</span><strong><code>${structuralState}</code></strong></div>
        <div><span>EVIDENCE STATE</span><strong><code>${evidenceState}</code></strong></div>
        <div><span>MATERIAL INCONSISTENCY</span><strong class="${inconsistency === "NO" ? "ok" : ""}">${inconsistency}</strong></div>
        <div><span>SOURCE COVERAGE</span><strong class="${coverage.includes("PARTIAL") ? "partial" : ""}">${coverage}</strong></div>
        <div><span>LAST REVIEWED</span><strong>${reviewed}</strong></div>
        <div><span>RESEARCH STATUS</span><strong>${escapeText(entity.research_status || "METHOD PILOT")}</strong></div>
      </div>
      <p>${escapeText(entity.summary)}</p>
      <div class="actions compact"><a class="button primary" href="${escapeText(entity.result_url)}">View Full Audit</a><a class="button" href="${escapeText(entity.structural_report_url || "research.html")}">Read Structural Report</a><a class="button" href="${escapeText(entity.evidence_report_url || "research.html")}">Read Evidence Report</a><a class="button" href="${escapeText(entity.research_chain_url || "verify.html")}">Inspect Research Chain</a></div>
    </article>
  `;
  wireReset(region);
}

function runSearch(query, updateUrl = true) {
  const region = document.querySelector("[data-search-results]");
  const normalized = query.trim().toLowerCase();
  if (!normalized) {
    renderTemplate(region, "blank-result-template");
  } else {
    const entity = coveredEntities.find((item) => {
      const aliases = [item.name, item.ticker, ...(item.aliases || [])].map((value) => String(value || "").trim().toLowerCase());
      return item.covered && aliases.includes(normalized);
    });
    if (entity || coveredAliases.has(normalized)) {
      renderCoveredEntity(region, entity || coveredEntities[0]);
    } else {
      renderTemplate(region, "uncovered-result-template");
    }
  }
  if (updateUrl) {
    const url = new URL(window.location.href);
    if (query.trim()) {
      url.searchParams.set("q", query.trim());
    } else {
      url.searchParams.delete("q");
    }
    url.hash = "search";
    history.replaceState({}, "", url);
  }
}

document.querySelectorAll("[data-entity-search]").forEach((form) => {
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const input = form.querySelector("input[name='q']");
    runSearch(input ? input.value : "");
  });
});

const initialSearch = new URLSearchParams(window.location.search).get("q");

fetch("assets/entities.json")
  .then((response) => (response.ok ? response.json() : []))
  .then((entities) => {
    coveredEntities = entities.filter((entity) => entity.covered);
    const aliases = entities
      .filter((entity) => entity.covered)
      .flatMap((entity) => [entity.name, entity.ticker, ...(entity.aliases || [])])
      .map((value) => String(value).trim().toLowerCase());
    if (aliases.length) coveredAliases = new Set(aliases);
  })
  .finally(() => {
    if (initialSearch !== null) {
      const input = document.getElementById("entity-search");
      if (input) input.value = initialSearch;
      runSearch(initialSearch, false);
    }
  });
