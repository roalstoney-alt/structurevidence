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
