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
  const coverage = escapeText(entity.source_coverage || "UNRESOLVED");
  const reviewed = escapeText(entity.last_reviewed || "UNRESOLVED");
  const freeScan = entity.free_scan || {};
  const observations = (freeScan.key_observations || []).slice(0, 3);
  const observationItems = observations.map((item) => `<li>${escapeText(item)}</li>`).join("");
  const observationWindow = escapeText(freeScan.observation_window || "See public research record");
  const reportVersion = escapeText(freeScan.report_version || "Free Scan V0.9");
  const marketContext = freeScan.market_context;
  const marketContextBlock = marketContext ? `<div><span>MARKET CONTEXT</span><strong>${escapeText(marketContext.regime || "UNAVAILABLE")}</strong></div>` : "";
  region.innerHTML = `
    <article class="health-card">
      <div class="result-topline"><span>Free Scan</span><span>NOT A SCORE OR RANKING</span></div>
      <div class="result-heading"><div><h2>${escapeText(entity.name)}</h2><p>${escapeText(entity.ticker || entity.name)} / ${escapeText(entity.category)}</p></div><button class="button subtle" type="button" data-reset-search>New Search</button></div>
      <div class="health-fields">
        <div><span>STRUCTURAL STATE</span><strong><code>${structuralState}</code></strong></div>
        <div><span>EVIDENCE STATE</span><strong><code>${evidenceState}</code></strong></div>
        <div><span>SOURCE COVERAGE</span><strong class="${coverage.includes("PARTIAL") ? "partial" : ""}">${coverage}</strong></div>
        <div><span>LAST REVIEWED</span><strong>${reviewed}</strong></div>
        <div><span>RESEARCH STATUS</span><strong>${escapeText(entity.research_status || "METHOD PILOT")}</strong></div>
        <div><span>OBSERVATION WINDOW</span><strong>${observationWindow}</strong></div>
        <div><span>REPORT VERSION</span><strong>${reportVersion}</strong></div>
        ${marketContextBlock}
      </div>
      <h3>Key Observations</h3>
      <ul>${observationItems}</ul>
      <h3>Key Limitation</h3>
      <p>${escapeText(freeScan.key_limitation || "GAP")}</p>
      <h3>Open Question</h3>
      <p>${escapeText(freeScan.open_question || "GAP")}</p>
      <div class="actions compact"><a class="button primary" href="reports.html">Request Early Access</a><a class="button" href="${escapeText(entity.result_url)}">View Public Detail</a><a class="button" href="${escapeText(entity.research_chain_url || "verify.html")}">Verify Public Record</a></div>
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

const statusLabels = {
  FRESH: "Fresh display update",
  AGING: "Aging display update",
  PARTIAL: "Partial evidence",
  UNRESOLVED: "Unresolved review",
  SUPERSEDED: "Superseded",
  NOT_CONFIGURED: "Not configured",
  NOT_APPLICABLE: "Not applicable",
};

function timelinePath(prefix, subject, kind) {
  return `${prefix || ""}timeline/subjects/${subject}_${kind}_timeline.json`;
}

function eventPath(prefix, subject) {
  return `${prefix || ""}timeline/subjects/${subject}_event_ledger.json`;
}

function rowsForResolution(rows, resolution) {
  return rows.filter((row) => row.resolution === resolution);
}

function renderTimelinePanel(panel, data, resolution) {
  const structural = data.structural;
  const evidence = data.evidence;
  const ledger = data.ledger;
  const ribbon = rowsForResolution(structural.phase_ribbon, resolution);
  const dimensionHtml = structural.dimensions.map((dimension) => {
    const rows = rowsForResolution(dimension.series, resolution);
    const blocks = rows.map((row) => `<span class="wave-point ${escapeText(row.band).toLowerCase()}" tabindex="0" title="${escapeText(row.notes.join(" "))}" aria-label="${escapeText(dimension.label)} ${escapeText(row.band)} from ${escapeText(row.t_start)} to ${escapeText(row.t_end)}">${escapeText(row.band)}</span>`).join("");
    return `<div class="timeline-track"><div><strong>${escapeText(dimension.label)}</strong><span>${escapeText(dimension.taxonomy_note)}</span></div><div class="wave-row">${blocks}</div></div>`;
  }).join("");
  const heatRows = evidence.evidence_families.map((family) => {
    const cells = rowsForResolution(family.series, resolution).map((row) => `<span class="heat-cell ${escapeText(row.status).toLowerCase()}" tabindex="0" title="${escapeText(row.notes.join(" "))}" aria-label="${escapeText(family.label)} ${escapeText(row.status)}">${escapeText(row.status.replaceAll("_", " "))}</span>`).join("");
    return `<div class="timeline-track"><div><strong>${escapeText(family.label)}</strong><span>${escapeText(family.taxonomy_note)}</span></div><div class="timeline-heatmap">${cells}</div></div>`;
  }).join("");
  const events = ledger.events.map((event) => `<li><time>${escapeText(event.timestamp.slice(0, 10))}</time><strong>${escapeText(event.event_type.replaceAll("_", " "))}</strong><span>${escapeText(event.label)}</span><a href="${escapeText(event.refs[0])}">Source</a></li>`).join("");
  const ribbonHtml = ribbon.map((row) => `<span class="phase-segment" tabindex="0" title="${escapeText(row.notes.join(" "))}" aria-label="${escapeText(row.phase)} ${escapeText(row.t_start)} to ${escapeText(row.t_end)}"><strong>${escapeText(row.phase)}</strong><small>${escapeText(row.observation_mode.replaceAll("_", " "))}</small></span>`).join("");
  const legend = Object.entries(statusLabels).map(([key, label]) => `<span><i class="${key.toLowerCase()}"></i>${escapeText(label)}</span>`).join("");
  panel.innerHTML = `
    <div class="timeline-meta"><span>${escapeText(structural.model_version)}</span><span>${escapeText(resolution)}</span><span>${escapeText(structural.construction_method)}</span><span>${escapeText(evidence.display_boundary)}</span></div>
    <div class="timeline-legend" aria-label="Timeline legend">${legend}</div>
    <div class="timeline-block"><h3>Structural Phase Ribbon</h3><div class="phase-ribbon">${ribbonHtml}</div></div>
    <div class="timeline-block"><h3>Structural Dimension Waveforms</h3>${dimensionHtml}</div>
    <div class="timeline-block"><h3>Evidence Dynamics / Freshness Heatmap</h3>${heatRows}</div>
    <div class="timeline-block"><h3>Event / Freeze Ledger</h3><ol class="timeline-events">${events}</ol></div>
    <details class="timeline-fallback"><summary>Table fallback</summary><table><thead><tr><th>Layer</th><th>Name</th><th>Status</th><th>Mode</th></tr></thead><tbody>${structural.dimensions.map((dimension) => `<tr><td>Structural</td><td>${escapeText(dimension.label)}</td><td>${escapeText(structural.current_structural_state)}</td><td>${escapeText(structural.construction_method)}</td></tr>`).join("")}${evidence.evidence_families.map((family) => `<tr><td>Evidence</td><td>${escapeText(family.label)}</td><td>${escapeText(rowsForResolution(family.series, resolution)[0]?.status || "NOT_APPLICABLE")}</td><td>${escapeText(rowsForResolution(family.series, resolution)[0]?.observation_mode || "RECONSTRUCTED")}</td></tr>`).join("")}</tbody></table></details>
  `;
}

document.querySelectorAll("[data-timeline-subject]").forEach((section) => {
  const subject = section.getAttribute("data-timeline-subject");
  const prefix = section.getAttribute("data-timeline-prefix") || "";
  const renderRegion = section.querySelector("[data-timeline-render]");
  Promise.all([
    fetch(timelinePath(prefix, subject, "structural")).then((response) => response.json()),
    fetch(timelinePath(prefix, subject, "evidence")).then((response) => response.json()),
    fetch(eventPath(prefix, subject)).then((response) => response.json()),
  ]).then(([structural, evidence, ledger]) => {
    const data = { structural, evidence, ledger };
    let active = structural.default_resolution || "WEEK";
    section.querySelectorAll("[data-resolution]").forEach((button) => {
      const resolution = button.getAttribute("data-resolution");
      button.setAttribute("role", "tab");
      button.setAttribute("aria-selected", String(resolution === active));
      button.addEventListener("click", () => {
        active = resolution;
        section.querySelectorAll("[data-resolution]").forEach((item) => item.setAttribute("aria-selected", String(item === button)));
        renderTimelinePanel(renderRegion, data, active);
      });
    });
    renderTimelinePanel(renderRegion, data, active);
  }).catch(() => {
    if (renderRegion) renderRegion.innerHTML = '<p class="microcopy">Timeline data is unavailable for this static view.</p>';
  });
});
