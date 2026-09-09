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

function renderTemplate(region, id) {
  const template = document.getElementById(id);
  if (!template || !region) return;
  region.replaceChildren(template.content.cloneNode(true));
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

function runSearch(query, updateUrl = true) {
  const region = document.querySelector("[data-search-results]");
  const normalized = query.trim().toLowerCase();
  if (!normalized) {
    renderTemplate(region, "blank-result-template");
  } else if (coveredAliases.has(normalized)) {
    renderTemplate(region, "covered-result-template");
  } else {
    renderTemplate(region, "uncovered-result-template");
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
    const aliases = entities
      .filter((entity) => entity.covered)
      .flatMap((entity) => [entity.name, ...(entity.aliases || [])])
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
