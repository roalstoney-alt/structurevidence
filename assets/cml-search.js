(() => {
  const form = document.querySelector("[data-cml-search]");
  const input = document.querySelector("#cml-query");
  const output = document.querySelector("[data-cml-results]");
  if (!form || !input || !output) return;

  let records = [];
  const normalize = (value) => value.trim().toLowerCase();
  const render = (query) => {
    const needle = normalize(query);
    const matches = records.filter((record) => [record.manufacturer, record.manufacturer_part_number, record.product_family, record.technical_item_type, ...(record.search_aliases || [])].some((value) => normalize(value).includes(needle)));
    if (!needle) {
      output.innerHTML = `<p class="search-empty">Enter an exact part number or manufacturer.</p>`;
      return;
    }
    if (!matches.length) {
      output.innerHTML = `<div class="search-empty"><h2>No structured assessment is currently available.</h2><p>Identity was not substituted with a similar part number.</p><a class="button" href="../request-analysis/?item=${encodeURIComponent(query.slice(0, 100))}">Request an analysis</a></div>`;
      return;
    }
    output.innerHTML = matches.map((record) => `<a class="search-result" href="${record.href}"><div><h2>${escapeHtml(record.manufacturer_part_number)}</h2><p>${escapeHtml(record.manufacturer)} / ${escapeHtml(record.product_family)}</p></div><span class="state ${record.lifecycle_state === "ACTIVE" ? "ok" : record.lifecycle_state.includes("EOL") ? "alert" : "review"}">${escapeHtml(record.lifecycle_state)}</span></a>`).join("");
  };
  const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"})[char]);
  fetch("../records/PUBLIC_RECORD_INDEX.json")
    .then((response) => { if (!response.ok) throw new Error("INDEX_UNAVAILABLE"); return response.json(); })
    .then((data) => { records = data.records || []; const initial = new URLSearchParams(location.search).get("q") || ""; input.value = initial; render(initial); })
    .catch(() => { output.innerHTML = `<p class="search-empty">The public record index is temporarily unavailable. <a href="../request-analysis/">Request an analysis</a>.</p>`; });
  form.addEventListener("submit", (event) => { event.preventDefault(); const query = input.value; const url = new URL(location.href); query ? url.searchParams.set("q", query) : url.searchParams.delete("q"); history.replaceState({}, "", url); render(query); });
})();
