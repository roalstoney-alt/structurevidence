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

  if (requestedSubject && requestedSubject.trim().toLowerCase() !== "bnb") {
    workspace.innerHTML = `<section class="monitor-error"><p class="monitor-kicker">Coverage boundary</p><h1>${esc(requestedSubject.toUpperCase())} monitoring is not available</h1><p>Monitoring v1.0 currently exposes a generated workspace for BNB only. No BNB state has been substituted for this request.</p><p><a class="monitor-command" href="monitor.html?subject=bnb">Open BNB workspace</a> <a class="monitor-command secondary" href="index.html#asset-states">View archive coverage</a></p></section>`;
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

  function render(snapshot) {
    renderExecutive(snapshot);
    document.querySelector("[data-monitor-boundary]").textContent = snapshot.monitoring_boundary;
    document.querySelector("[data-snapshot-strip]").innerHTML = [["SUBJECT",snapshot.subject_id],["SNAPSHOT AS-OF",snapshot.snapshot_as_of],["KNOWN-AT CUTOFF",snapshot.known_at_cutoff],["FRESHNESS",snapshot.freshness_snapshot.release_state],["GDR",snapshot.gdr_snapshot.authorization],["SNAPSHOT HASH",shortHash(snapshot.snapshot_sha256)]].map(([label,value]) => `<div><span>${esc(label)}</span><strong>${esc(value)}</strong></div>`).join("");
    document.querySelector("[data-state-grid]").innerHTML = [
      stateCard("Structural Level",snapshot.structural_level.overall_state,`${snapshot.structural_level.dimensions.length} observed dimensions`,"structural"),
      stateCard("Structural Delta",snapshot.structural_delta.overall_state,"Level and Delta remain separate","delta"),
      stateCard("Evidence State",snapshot.evidence_dynamics.overall_state,snapshot.evidence_dynamics.ecl_consistency,"evidence"),
      stateCard("Market Dynamics",snapshot.market_dynamics.state,"Flow-8 unavailable without measured inputs","missing"),
      stateCard("Liquidity Observation",snapshot.liquidity_observations.every((row) => row.state === "NOT_MEASURED") ? "NOT_MEASURED" : "PARTIAL","No frozen microstructure series","missing")
    ].join("");
    const levels = Object.fromEntries(snapshot.structural_level.dimensions.map((row) => [row.dimension_id,row]));
    document.querySelector("[data-transition-table] tbody").innerHTML = snapshot.structural_delta.dimensions.map((row) => { const level = levels[row.dimension_id] || {}; return `<tr><td><strong>${esc(row.dimension_id)}</strong></td><td>${esc(level.state || "NOT_OBSERVED")}</td><td>${esc(dateOnly(level.effective_at))}</td><td>${esc(row.state)}</td><td>${esc(row.basis)}</td><td>${esc(row.comparability_state)}</td></tr>`; }).join("");
    window.monitorEvents = snapshot.recent_events; renderEvents("ALL");
    const filter = document.querySelector("[data-event-filter]"); filter.addEventListener("change", () => renderEvents(filter.value));
    const evidence = snapshot.evidence_dynamics;
    document.querySelector("[data-evidence-summary]").innerHTML = [["CLAIMS",evidence.claim_count],["SOURCES",evidence.source_count],["DEPENDENCY GROUPS",evidence.dependency_group_count],["SOURCE COVERAGE",evidence.source_coverage],["ECL CONSISTENCY",evidence.ecl_consistency]].map(([label,value]) => `<div><span>${esc(label)}</span><strong>${esc(value)}</strong></div>`).join("");
    document.querySelector("[data-evidence-table] tbody").innerHTML = evidence.events.map((row) => `<tr><td>${esc(row.family_id)}</td><td>${esc(row.state_after)}</td><td>${esc(dateOnly(row.known_at))}</td><td>${esc(row.observation_mode)}</td><td>${sourceLink(row.artifact_refs?.[0])}</td></tr>`).join("");
    document.querySelector("[data-market-reason]").textContent = snapshot.market_dynamics.reason;
    document.querySelector("[data-market-table] tbody").innerHTML = snapshot.liquidity_observations.map((row) => `<tr><td>${esc(row.metric)}</td><td><strong class="state-muted">${esc(row.state)}</strong></td><td>${esc(row.observation_window || "NONE")}</td><td>${row.source_refs.length ? esc(row.source_refs.length) : "NO INPUT ARTIFACT"}</td></tr>`).join("");
    document.querySelector("[data-gdr-id]").textContent = snapshot.gdr_snapshot.authorization_id;
    document.querySelector("[data-gdr-table] tbody").innerHTML = Object.entries(snapshot.gdr_snapshot.actions).map(([action,outcome]) => `<tr><td><strong>${esc(action)}</strong></td><td>${esc(outcome)}</td><td>${action === "COMMERCIAL_DELIVERY" ? "Requires exact paid-delivery authorization" : "Versioned monitor adapter v1.0"}</td></tr>`).join("");
    document.querySelector("[data-provenance-list]").innerHTML = snapshot.rtp_provenance_refs.map((row) => `<details><summary><span>${esc(row.role)}</span><strong>${esc(row.path.split("/").pop())}</strong></summary><dl><dt>Path</dt><dd>${esc(row.path)}</dd><dt>SHA-256</dt><dd><code>${esc(row.sha256)}</code></dd><dt>Boundary</dt><dd>Hash match proves artifact identity, not content truth.</dd></dl></details>`).join("");
  }

  fetch("monitoring/subjects/bnb/MONITORING_SNAPSHOT.json").then((response) => { if (!response.ok) throw new Error("snapshot unavailable"); return response.json(); }).then(render).catch((error) => { workspace.innerHTML = `<section class="monitor-error"><h1>Monitoring snapshot unavailable</h1><p>${esc(error.message)}</p></section>`; });
})();
