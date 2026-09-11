(() => {
  const form = document.querySelector("[data-verify-form]");
  const result = document.querySelector("[data-verify-result]");
  if (!form || !result) return;
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g,(char)=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[char]);
  let records = [];
  function lookup(query) {
    const normalized = query.trim().toLowerCase();
    const record = records.find((row) => [row.snapshot_id,row.subject_id,row.snapshot_sha256,row.source_bundle_hash].some((value) => String(value).toLowerCase() === normalized));
    if (!record) { result.innerHTML = `<div class="verify-panel missing"><strong>NO MATCH</strong><p>No public monitoring record matches this exact identifier.</p></div>`; return; }
    result.innerHTML = `<div class="verify-panel"><div><span>RESULT</span><strong>HASH_METADATA_MATCH</strong></div><dl><dt>Snapshot ID</dt><dd>${esc(record.snapshot_id)}</dd><dt>Subject</dt><dd>${esc(record.subject_id)}</dd><dt>Snapshot As-Of</dt><dd>${esc(record.snapshot_as_of)}</dd><dt>Snapshot SHA-256</dt><dd><code>${esc(record.snapshot_sha256)}</code></dd><dt>Source Bundle SHA-256</dt><dd><code>${esc(record.source_bundle_hash)}</code></dd><dt>Artifact</dt><dd><a href="${esc(record.artifact_path)}">Open JSON</a></dd><dt>Workspace</dt><dd><a href="${esc(record.workspace_path)}">Open monitor</a></dd></dl><p>Boundary: hash verification establishes artifact identity, not truth.</p></div>`;
  }
  form.addEventListener("submit",(event)=>{event.preventDefault();lookup(form.elements.q.value);});
  fetch("monitoring/PUBLIC_MONITORING_INDEX.json").then((response)=>response.json()).then((index)=>{records=index.records||[];lookup(form.elements.q.value);}).catch(()=>{result.innerHTML='<div class="verify-panel missing"><strong>INDEX UNAVAILABLE</strong></div>';});
})();
