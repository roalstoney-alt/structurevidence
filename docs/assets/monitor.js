(() => {
  const workspace = document.querySelector("[data-monitor-workspace]");
  if (!workspace) return;
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[char]);
  const shortHash = (value) => value ? `${value.slice(0, 12)}...${value.slice(-8)}` : "NOT_AVAILABLE";
  const dateOnly = (value) => value ? value.replace("T00:00:00Z", " UTC") : "NOT_ESTABLISHED";
  const sourceLink = (path) => path ? `<a href="${esc(path)}">${esc(path.split("/").pop())}</a>` : "NONE";
  const stateCard = (label, value, note, tone = "") => `<article class="state-cell ${tone}"><span>${esc(label)}</span><strong>${esc(value)}</strong><small>${esc(note)}</small></article>`;
  const requestedSubject = new URLSearchParams(window.location.search).get("subject");
  const dimensionLabels = {
    GOVERNANCE_STRUCTURE: "governance",
    SUPPLY_STRUCTURE: "supply",
    UTILITY_STRUCTURE: "utility",
    VALIDATOR_DISTRIBUTION: "validator distribution"
  };
  const displayLabels = {
    SUPPLY_STRUCTURE: "Supply",
    UTILITY_STRUCTURE: "Utility",
    GOVERNANCE_STRUCTURE: "Governance",
    VALIDATOR_DISTRIBUTION: "Validator distribution",
    CONTRACTIONARY: "Contractionary",
    ESTABLISHED_ROLE: "Established role",
    MIXED_ROLE: "Mixed role",
    MECHANISM_DEFINED: "Mechanism defined",
    FIXED_OR_RESTRICTED_SET: "Fixed / restricted set",
    TOWARD_CONTRACTION: "Toward contraction",
    NOT_ESTABLISHED: "Not established"
  };
  const displayLabel = (value) => displayLabels[value] || String(value || "Not observed").replaceAll("_", " ").toLowerCase();

  if (requestedSubject && requestedSubject.trim().toLowerCase() !== "bnb") {
    const subject = requestedSubject.trim().toUpperCase();
    workspace.innerHTML = `<section class="monitor-error"><p class="monitor-kicker">Coverage boundary</p><h1>${esc(subject)} monitoring is not available</h1><p>Monitoring v1.0 currently exposes a generated workspace for BNB only. No BNB state has been substituted for this request.</p><p><a class="monitor-command" href="customize.html?subject=${encodeURIComponent(subject)}">Ask Audit</a> <a class="monitor-command secondary" href="monitor.html?subject=bnb">Open BNB workspace</a></p><p>Custom research begins with evidence availability and scope review.</p></section>`;
    return;
  }

  function renderEvents(domain) {
    const events = (window.monitorEvents || []).filter((row) => domain === "ALL" || row.event_domain === domain);
    document.querySelector("[data-event-table] tbody").innerHTML = events.map((row) => `<tr><td>${esc(dateOnly(row.known_at))}</td><td><strong>${esc(row.event_id)}</strong><small>${esc(row.event_type)}</small></td><td>${esc(row.event_domain)}</td><td>${esc(row.epistemic_status)}</td><td><span class="state-muted">${esc(row.market_impact_status)}</span></td><td>${esc(row.causal_status)}</td><td>${sourceLink(row.artifact_ids[0])}</td></tr>`).join("") || `<tr><td colspan="7">No events match this domain.</td></tr>`;
  }

  function renderExecutive(snapshot) {
    const deltas = snapshot.structural_delta.dimensions;
    const established = deltas.filter((row) => row.state !== "NOT_ESTABLISHED");
    const open = deltas.filter((row) => row.state === "NOT_ESTABLISHED");
    const supply = established.find((row) => row.dimension_id === "SUPPLY_STRUCTURE");
    const impactOpen = snapshot.market_dynamics.state === "NOT_MEASURED";
    const openLabels = open.map((row) => dimensionLabels[row.dimension_id] || row.dimension_id.toLowerCase()).join(", ");
    const posture = snapshot.gdr_snapshot.authorization === "ALLOW_WITH_LIMITATIONS" ? "Monitor with limitations" : snapshot.gdr_snapshot.authorization.replaceAll("_", " ");
    const headline = supply
      ? "Supply contraction direction is established; market effect remains unresolved."
      : "No structural direction is established in the current snapshot.";
    const summary = supply
      ? `The model records an explicit supply-structure change toward contraction, effective ${dateOnly(supply.effective_at)}. No comparable prior establishes change in ${openLabels || "the remaining dimensions"}. ${impactOpen ? "Price, depth, spread, and liquidity response have not been measured." : "Measured market observations are available in the supporting record."}`
      : `Current structural Levels are observed, but the available history does not establish a comparable change direction. ${impactOpen ? "Market and liquidity response have not been measured." : "Measured market observations are available in the supporting record."}`;
    document.querySelector("[data-executive-asof]").textContent = `As of ${snapshot.snapshot_as_of.slice(0, 10)} UTC`;
    document.querySelector("[data-executive-posture]").textContent = posture;
    document.querySelector("[data-executive-headline]").textContent = headline;
    document.querySelector("[data-executive-summary]").textContent = summary;
    document.querySelector("[data-executive-facts]").innerHTML = [
      ["Established change", supply ? "Supply toward contraction" : "None"],
      ["Evidence basis", supply?.basis === "EXPLICIT_CHANGE_EVENT" ? "Explicit change event" : "No comparable prior"],
      ["Freshness", snapshot.freshness_snapshot.release_state]
    ].map(([label, value]) => `<div><dt>${esc(label)}</dt><dd>${esc(value)}</dd></div>`).join("");
    const flags = [
      {label: "Market confirmation", state: impactOpen ? "OPEN" : "OBSERVED", note: impactOpen ? "No frozen price, depth, spread, or liquidity series." : "Measured observations are linked below.", tone: impactOpen ? "open" : "clear"},
      {label: "Cross-dimension change", state: open.length ? "LIMITED" : "ESTABLISHED", note: open.length ? `${open.length} of ${deltas.length} structural dimensions lack a comparable prior.` : "All observed dimensions have a comparable prior.", tone: open.length ? "limited" : "clear"},
      {label: "Evidence coverage", state: snapshot.evidence_dynamics.source_coverage, note: snapshot.evidence_dynamics.ecl_consistency.replaceAll("_", " ").toLowerCase(), tone: snapshot.evidence_dynamics.source_coverage === "PARTIAL" ? "limited" : "clear"}
    ];
    document.querySelector("[data-risk-count]").textContent = `${flags.filter((flag) => flag.tone !== "clear").length} open`;
    document.querySelector("[data-risk-flags]").innerHTML = flags.map((flag) => `<div class="risk-row ${esc(flag.tone)}"><div><span>${esc(flag.label)}</span><strong>${esc(flag.state)}</strong></div><p>${esc(flag.note)}</p></div>`).join("");
  }

  function renderStructureTimeline(snapshot, dataset) {
    const chart = document.querySelector("[data-change-chart]");
    const detail = document.querySelector("[data-change-detail]");
    if (!chart || !detail) return;
    if (!dataset?.buckets) {
      chart.innerHTML = '<p class="change-unavailable">Structured timeline unavailable. The monitoring snapshot remains accessible below.</p>';
      return;
    }
    const active = dataset.buckets.filter((row) => Number(row.observation_count) > 0);
    const startMs = Math.min(...active.map((row) => Date.parse(row.date)));
    const endMs = Date.parse(snapshot.snapshot_as_of);
    const position = (date) => Math.max(2, Math.min(96, ((Date.parse(date) - startMs) / Math.max(1, endMs - startMs)) * 94 + 2));
    const dimensionOrder = ["SUPPLY_STRUCTURE", "UTILITY_STRUCTURE", "GOVERNANCE_STRUCTURE", "VALIDATOR_DISTRIBUTION"];
    const structuralHash = snapshot.rtp_provenance_refs.find((row) => row.role === "structural_day")?.sha256 || "";
    const rows = dimensionOrder.map((dimension) => {
      const observations = active.filter((row) => row.dimension_id === dimension).sort((a, b) => a.date.localeCompare(b.date));
      if (!observations.length) return "";
      const connectors = observations.slice(1).map((row, index) => {
        const left = position(observations[index].date);
        const right = position(row.date);
        return `<span class="change-connector" style="left:${left}%;width:${Math.max(0, right - left)}%" aria-hidden="true"></span>`;
      }).join("");
      const points = observations.map((row) => {
        const established = row.delta_state !== "NOT_ESTABLISHED";
        const payload = encodeURIComponent(JSON.stringify({dimension:displayLabel(row.dimension_id),date:row.date,level:displayLabel(row.level_state),delta:displayLabel(row.delta_state),basis:displayLabel(row.delta_basis),observations:row.level_observation_ids || [],sources:row.source_refs || [],hash:structuralHash}));
        return `<button class="change-point ${established ? "established" : "observed"} ${position(row.date) > 72 ? "align-right" : ""}" style="left:${position(row.date)}%" type="button" data-change-point="${payload}" aria-label="${esc(displayLabel(row.dimension_id))}, ${esc(row.date)}, ${esc(displayLabel(row.level_state))}"><span class="point-date">${esc(row.date.slice(5))}</span><i aria-hidden="true"></i><strong>${esc(displayLabel(row.level_state))}</strong>${established ? `<small>${esc(displayLabel(row.delta_state))}</small>` : ""}</button>`;
      }).join("");
      return `<div class="change-lane"><div class="lane-label"><strong>${esc(displayLabel(dimension))}</strong><span>${observations.reduce((sum, row) => sum + row.observation_count, 0)} observations</span></div><div class="lane-track">${connectors}${points}</div></div>`;
    }).join("");
    chart.innerHTML = `<div class="change-axis"><span>2026-07-15</span><span>2026-09-09</span><span>Snapshot<br>${esc(snapshot.snapshot_as_of.slice(0, 10))}</span></div>${rows}`;
    const showDetail = (button) => {
      const row = JSON.parse(decodeURIComponent(button.dataset.changePoint));
      chart.querySelectorAll("[data-change-point]").forEach((point) => point.setAttribute("aria-pressed", point === button ? "true" : "false"));
      detail.innerHTML = `<div><span>Selected observation</span><strong>${esc(row.dimension)} / ${esc(row.date)}</strong></div><dl><div><dt>Observed Level</dt><dd>${esc(row.level)}</dd></div><div><dt>Delta</dt><dd>${esc(row.delta)}</dd></div><div><dt>Basis</dt><dd>${esc(row.basis)}</dd></div><div><dt>Observation IDs</dt><dd>${row.observations.map(esc).join(", ")}</dd></div></dl><div class="change-lineage"><span>Structural-day SHA-256</span><code>${esc(row.hash)}</code><a href="timeline/subjects/bnb_structural_day.json">Open source artifact</a></div>`;
    };
    chart.querySelectorAll("[data-change-point]").forEach((button) => button.addEventListener("click", () => showDetail(button)));
    const defaultPoint = chart.querySelector("[data-change-point].established") || chart.querySelector("[data-change-point]");
    if (defaultPoint) showDetail(defaultPoint);
  }

  function render(snapshot, structuralDay) {
    renderExecutive(snapshot);
    renderStructureTimeline(snapshot, structuralDay);
    document.querySelector("[data-monitor-boundary]").textContent = snapshot.monitoring_boundary;
    document.querySelector("[data-snapshot-strip]").innerHTML = [["SUBJECT",snapshot.subject_id],["SNAPSHOT AS-OF",snapshot.snapshot_as_of],["KNOWN-AT CUTOFF",snapshot.known_at_cutoff],["FRESHNESS",snapshot.freshness_snapshot.release_state],["GDR",snapshot.gdr_snapshot.authorization],["SNAPSHOT HASH",shortHash(snapshot.snapshot_sha256)]].map(([label,value]) => `<div><span>${esc(label)}</span><strong>${esc(value)}</strong></div>`).join("");
    document.querySelector("[data-state-grid]").innerHTML = [
      stateCard("Structural Level",snapshot.structural_level.overall_state,`${snapshot.structural_level.dimensions.length} observed dimensions`,"structural"),
      stateCard("Structural Delta",snapshot.structural_delta.overall_state,"Level and Delta remain separate","delta"),
      stateCard("Evidence State",snapshot.evidence_dynamics.overall_state,snapshot.evidence_dynamics.ecl_consistency,"evidence")
    ].join("");
    const levels = Object.fromEntries(snapshot.structural_level.dimensions.map((row) => [row.dimension_id,row]));
    document.querySelector("[data-transition-table] tbody").innerHTML = snapshot.structural_delta.dimensions.map((row) => { const level = levels[row.dimension_id] || {}; return `<tr><td><strong>${esc(row.dimension_id)}</strong></td><td>${esc(level.state || "NOT_OBSERVED")}</td><td>${esc(dateOnly(level.effective_at))}</td><td>${esc(row.state)}</td><td>${esc(row.basis)}</td><td>${esc(row.comparability_state)}</td></tr>`; }).join("");
    window.monitorEvents = snapshot.recent_events; renderEvents("ALL");
    const filter = document.querySelector("[data-event-filter]"); filter.addEventListener("change", () => renderEvents(filter.value));
    const evidence = snapshot.evidence_dynamics;
    document.querySelector("[data-evidence-summary]").innerHTML = [["CLAIMS",evidence.claim_count],["SOURCES",evidence.source_count],["DEPENDENCY GROUPS",evidence.dependency_group_count],["SOURCE COVERAGE",evidence.source_coverage],["ECL CONSISTENCY",evidence.ecl_consistency]].map(([label,value]) => `<div><span>${esc(label)}</span><strong>${esc(value)}</strong></div>`).join("");
    document.querySelector("[data-evidence-table] tbody").innerHTML = evidence.events.map((row) => `<tr><td>${esc(row.family_id)}</td><td>${esc(row.state_after)}</td><td>${esc(dateOnly(row.known_at))}</td><td>${esc(row.observation_mode)}</td><td>${sourceLink(row.artifact_refs?.[0])}</td></tr>`).join("");
    document.querySelector("[data-market-reason]").textContent = snapshot.market_dynamics.reason;
    const marketPackOpen = snapshot.market_dynamics.state !== "NOT_MEASURED" || snapshot.liquidity_observations.some((row) => row.state !== "NOT_MEASURED");
    document.querySelector("[data-market-pack-state]").textContent = marketPackOpen ? "Coverage available" : "Not connected";
    document.querySelector("[data-market-table] tbody").innerHTML = snapshot.liquidity_observations.map((row) => `<tr><td>${esc(row.metric)}</td><td><strong class="state-muted">${esc(row.state)}</strong></td><td>${esc(row.observation_window || "NONE")}</td><td>${row.source_refs.length ? esc(row.source_refs.length) : "NO INPUT ARTIFACT"}</td></tr>`).join("");
    document.querySelector("[data-gdr-id]").textContent = snapshot.gdr_snapshot.authorization_id;
    document.querySelector("[data-gdr-table] tbody").innerHTML = Object.entries(snapshot.gdr_snapshot.actions).map(([action,outcome]) => `<tr><td><strong>${esc(action)}</strong></td><td>${esc(outcome)}</td><td>${action === "COMMERCIAL_DELIVERY" ? "Requires exact paid-delivery authorization" : "Versioned monitor adapter v1.0"}</td></tr>`).join("");
    document.querySelector("[data-provenance-list]").innerHTML = snapshot.rtp_provenance_refs.map((row) => `<details><summary><span>${esc(row.role)}</span><strong>${esc(row.path.split("/").pop())}</strong></summary><dl><dt>Path</dt><dd>${esc(row.path)}</dd><dt>SHA-256</dt><dd><code>${esc(row.sha256)}</code></dd><dt>Boundary</dt><dd>Hash match proves artifact identity, not content truth.</dd></dl></details>`).join("");
  }

  Promise.all([
    fetch("monitoring/subjects/bnb/MONITORING_SNAPSHOT.json").then((response) => { if (!response.ok) throw new Error("snapshot unavailable"); return response.json(); }),
    fetch("timeline/subjects/bnb_structural_day.json").then((response) => response.ok ? response.json() : null).catch(() => null)
  ]).then(([snapshot, structuralDay]) => render(snapshot, structuralDay)).catch((error) => { workspace.innerHTML = `<section class="monitor-error"><h1>Monitoring snapshot unavailable</h1><p>${esc(error.message)}</p></section>`; });
})();
