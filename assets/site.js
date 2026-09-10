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

const levelLabels = {
  CONTRACTIONARY: "Contractionary condition",
  MECHANISM_DEFINED: "Mechanism defined",
  FIXED_OR_RESTRICTED_SET: "Fixed or restricted set",
  MATERIAL_ROLE: "Material role",
  ESTABLISHED_ROLE: "Established role",
  HIGH_DEPENDENCE: "High dependence",
  MATERIAL_DEPENDENCE: "Material dependence",
  HYBRID_DEPENDENCE: "Hybrid dependence",
  MIXED_ROLE: "Mixed role",
  SOURCE_DEPENDENT: "Source dependent",
  INSUFFICIENT_DATA: "Insufficient data",
  NO_OBSERVATION: "No time-indexed observation",
  MIXED_LEVEL: "Mixed level",
};

const deltaLabels = {
  TOWARD_CONTRACTION: "Toward contraction",
  TOWARD_EXPANSION: "Toward expansion",
  TOWARD_CONCENTRATION: "Toward concentration",
  TOWARD_DISTRIBUTION: "Toward distribution",
  ROLE_STRENGTHENING: "Role strengthening",
  ROLE_WEAKENING: "Role weakening",
  STRUCTURAL_SHIFT: "Structural shift",
  MIXED_CHANGE: "Mixed change",
  UNCHANGED: "Unchanged",
  NOT_ESTABLISHED: "Not established",
  INSUFFICIENT_DATA: "Insufficient data",
};

const evidenceLabels = {
  NOT_OBSERVED: "Not observed",
  OBSERVED: "Observed",
  PARTIAL: "Partial",
  COMPLETE: "Complete",
  UNRESOLVED: "Unresolved",
  UNDER_REVIEW: "Under review",
  SUPERSEDED: "Superseded",
  NOT_APPLICABLE: "Not applicable",
  POLICY_NOT_CONFIGURED: "Policy not configured",
};

function timelinePath(prefix, subject, kind) {
  return `${prefix || ""}timeline/subjects/${subject}_${kind}_timeline.json`;
}

function eventPath(prefix, subject) {
  return `${prefix || ""}timeline/subjects/${subject}_event_ledger.json`;
}

function dataPath(prefix, path) {
  return `${prefix || ""}${path}`;
}

function periodLabel(bucket) {
  return bucket.period || bucket.date || bucket.week_start || bucket.month_start || bucket.bucket_start || "";
}

function bucketTitle(bucket) {
  const ids = bucket.observations || bucket.events || [];
  const refs = bucket.source_refs || bucket.lineage?.artifact_refs || [];
  return [`${periodLabel(bucket)} ${bucket.level_state || bucket.closing_level_state || bucket.closing_state || ""} ${bucket.delta_state || bucket.period_delta_state || ""}`, `${ids.length} linked record(s)`, refs[0] || ""].filter(Boolean).join(" | ");
}

function renderLegend(labels, className) {
  return Object.entries(labels).map(([key, label]) => `<span><i class="${className} ${key.toLowerCase()}"></i>${escapeText(key)} - ${escapeText(label)}</span>`).join("");
}

function bucketsByDimension(buckets) {
  return buckets.reduce((acc, bucket) => {
    (acc[bucket.dimension_id] ||= []).push(bucket);
    return acc;
  }, {});
}

function bucketsByFamily(buckets) {
  return buckets.reduce((acc, bucket) => {
    (acc[bucket.family_id] ||= []).push(bucket);
    return acc;
  }, {});
}

function renderTimelinePanel(panel, data, resolution) {
  const structural = data.structural;
  const evidence = data.evidence;
  const ledger = data.ledger;
  const structuralBuckets = data.structuralBuckets.buckets || [];
  const evidenceBuckets = data.evidenceBuckets.buckets || [];
  const byDimension = bucketsByDimension(structuralBuckets);
  const byFamily = bucketsByFamily(evidenceBuckets);
  const dimensionHtml = structural.dimensions.map((dimension) => {
    const rows = byDimension[dimension.dimension_id] || [];
    const blocks = rows.map((row) => `<span class="wave-point level-${escapeText(row.level_state || row.closing_level_state).toLowerCase()} delta-${escapeText(row.delta_state || row.period_delta_state).toLowerCase()}" tabindex="0" title="${escapeText(bucketTitle(row))}" aria-label="${escapeText(dimension.label)} level ${escapeText(row.level_state || row.closing_level_state)} delta ${escapeText(row.delta_state || row.period_delta_state)} ${escapeText(periodLabel(row))}">${escapeText(periodLabel(row))}<strong>LEVEL ${escapeText(row.level_state || row.closing_level_state)}</strong><strong>DELTA ${escapeText(row.delta_state || row.period_delta_state)}</strong><small>${escapeText(String(row.observation_count))} obs / ${escapeText(row.delta_basis || "NOT_ESTABLISHED")}</small></span>`).join("");
    return `<div class="timeline-track ${escapeText(dimension.render_mode || "SPARSE_POINTS").toLowerCase()}"><div><strong>${escapeText(dimension.label)}</strong><span>${escapeText(dimension.render_mode)} / ${escapeText(String(dimension.observation_count))} observations</span></div><div class="wave-row">${blocks || '<span class="microcopy">No time-indexed observation available.</span>'}</div></div>`;
  }).join("");
  const heatRows = evidence.evidence_families.map((family) => {
    const cells = (byFamily[family.family_id] || []).map((row) => {
      const age = row.age_days ?? row.age_days_at_period_end;
      return `<span class="heat-cell ${escapeText(row.closing_state).toLowerCase()}" tabindex="0" title="${escapeText(bucketTitle(row))}" aria-label="${escapeText(family.label)} ${escapeText(row.closing_state)} ${escapeText(periodLabel(row))}">${escapeText(periodLabel(row))}<strong>${escapeText(row.closing_state)}</strong><small>${escapeText(String(row.events_count))} events${age === null || age === undefined ? "" : ` / ${escapeText(String(age))}d`}</small></span>`;
    }).join("");
    return `<div class="timeline-track"><div><strong>${escapeText(family.label)}</strong><span>${escapeText(family.taxonomy_note)}</span></div><div class="timeline-heatmap">${cells}</div></div>`;
  }).join("");
  const eventsByDomain = ledger.events.reduce((acc, event) => {
    (acc[event.event_domain] ||= []).push(event);
    return acc;
  }, {});
  const events = Object.entries(eventsByDomain).map(([domain, rows]) => `<div class="event-lane"><h4>${escapeText(domain.replaceAll("_", " "))}</h4><ol>${rows.map((event) => `<li><time>${escapeText((event.timestamp || "").slice(0, 10))}</time><strong>${escapeText(event.event_type.replaceAll("_", " "))}</strong><span>${escapeText(event.label)}</span><a href="${escapeText(event.refs[0])}">Source</a></li>`).join("")}</ol></div>`).join("");
  const ribbonHtml = (structural.phase_ribbon || []).map((row) => `<span class="phase-segment" tabindex="0" title="${escapeText((row.notes || []).join(" "))}" aria-label="${escapeText(row.phase)} ${escapeText(row.period)}"><strong>${escapeText(row.period)}</strong><small>${escapeText(row.phase_mode || row.phase)}</small></span>`).join("");
  const density = `${escapeText(String(structural.density?.atomic_observations || 0))} atomic observations / ${escapeText(String(structural.density?.active_days || 0))} active days / ${escapeText(String(evidence.density?.evidence_events || 0))} evidence events`;
  const structuralRows = structuralBuckets.map((row) => `<tr><td>${escapeText(periodLabel(row))}</td><td>${escapeText(row.dimension_id)}</td><td>${escapeText(row.level_state || row.closing_level_state)}</td><td>${escapeText(row.delta_state || row.period_delta_state)}</td><td>${escapeText((row.observations || []).join(", "))}</td><td>${escapeText((row.source_refs || []).join(", "))}</td><td>${escapeText(row.aggregation_rule)}</td></tr>`).join("");
  const evidenceRows = evidenceBuckets.map((row) => `<tr><td>${escapeText(periodLabel(row))}</td><td>${escapeText(row.family_id)}</td><td>${escapeText(row.opening_state)}</td><td>${escapeText(row.closing_state)}</td><td>${escapeText(String(row.events_count))}</td><td>${escapeText(row.latest_update_at || "")}</td><td>${escapeText(String(row.age_days ?? row.age_days_at_period_end ?? ""))}</td></tr>`).join("");
  panel.innerHTML = `
    <div class="timeline-meta"><span>${escapeText(structural.model_version)}</span><span>${escapeText(resolution)}</span><span>${escapeText(structural.construction_method)}</span><span>${density}</span><span>${escapeText(evidence.display_boundary)}</span></div>
    <div class="timeline-legend" aria-label="Level legend">${renderLegend(levelLabels, "level-key")}</div>
    <div class="timeline-legend" aria-label="Delta legend">${renderLegend(deltaLabels, "delta-key")}</div>
    <div class="timeline-block"><h3>Research / Phase Markers</h3><div class="phase-ribbon">${ribbonHtml}</div></div>
    <div class="timeline-block"><h3>Structural Dimension Trajectories</h3>${dimensionHtml}</div>
    <div class="timeline-block"><h3>Evidence Dynamics / Update Age</h3><div class="timeline-legend" aria-label="Evidence legend">${renderLegend(evidenceLabels, "evidence-key")}</div>${heatRows}</div>
    <div class="timeline-block"><h3>Event / Freeze Ledger</h3><div class="timeline-events">${events}</div></div>
    <details class="timeline-fallback"><summary>Structural table fallback</summary><table><thead><tr><th>Period</th><th>Dimension</th><th>Level</th><th>Delta</th><th>Observation IDs</th><th>Source refs</th><th>Aggregation</th></tr></thead><tbody>${structuralRows}</tbody></table></details>
    <details class="timeline-fallback"><summary>Evidence table fallback</summary><table><thead><tr><th>Period</th><th>Family</th><th>Opening</th><th>Closing</th><th>Events</th><th>Last update</th><th>Age days</th></tr></thead><tbody>${evidenceRows}</tbody></table></details>
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
    let active = structural.default_resolution || "WEEK";
    const loadResolution = (resolution) => Promise.all([
      fetch(dataPath(prefix, structural.datasets[resolution])).then((response) => response.json()),
      fetch(dataPath(prefix, evidence.datasets[resolution])).then((response) => response.json()),
    ]).then(([structuralBuckets, evidenceBuckets]) => {
      renderTimelinePanel(renderRegion, { structural, evidence, ledger, structuralBuckets, evidenceBuckets }, resolution);
    });
    section.querySelectorAll("[data-resolution]").forEach((button) => {
      const resolution = button.getAttribute("data-resolution");
      button.setAttribute("role", "tab");
      button.setAttribute("aria-selected", String(resolution === active));
      button.addEventListener("click", () => {
        active = resolution;
        section.querySelectorAll("[data-resolution]").forEach((item) => item.setAttribute("aria-selected", String(item === button)));
        loadResolution(active);
      });
    });
    loadResolution(active);
  }).catch(() => {
    if (renderRegion) renderRegion.innerHTML = '<p class="microcopy">Timeline data is unavailable for this static view.</p>';
  });
});
