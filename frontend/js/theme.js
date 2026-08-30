// Theme switching (dark / light). Auto-detects OS preference on first load,
// then honors the user override. Syncs the DOM label and dispatches a
// change event so the i18n module can refresh the toggle text.
(function () {
  "use strict";

  const cfg = window.CREST_CONFIG;
  const STORAGE_KEY = cfg.THEME_STORAGE_KEY;

  function getStored() {
    try { return localStorage.getItem(STORAGE_KEY); } catch (_) { return null; }
  }
  function setStored(value) {
    try { localStorage.setItem(STORAGE_KEY, value); } catch (_) { /* ignore */ }
  }

  function apply(theme) {
    const html = document.documentElement;
    if (theme === "light") {
      html.classList.add("light");
    } else {
      html.classList.remove("light");
    }
    document.querySelectorAll("[data-theme-label]").forEach((el) => {
      el.textContent = theme === "light" ? "Light" : "Dark";
    });
    document.querySelectorAll("[data-theme-icon]").forEach((el) => {
      el.textContent = theme === "light" ? "☼" : "☾";
    });
  }

  function detect() {
    const stored = getStored();
    if (stored === "light" || stored === "dark") return stored;
    return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  }

  function toggle() {
    const next = document.documentElement.classList.contains("light") ? "dark" : "light";
    setStored(next);
    apply(next);
    document.dispatchEvent(new CustomEvent("theme:change", { detail: { theme: next } }));
  }

  document.addEventListener("DOMContentLoaded", () => {
    apply(detect());
    document.querySelectorAll("[data-theme-toggle]").forEach((btn) => {
      btn.addEventListener("click", toggle);
    });
    // React to OS theme changes only when the user has no override.
    window.matchMedia("(prefers-color-scheme: light)").addEventListener("change", (e) => {
      if (!getStored()) apply(e.matches ? "light" : "dark");
    });
  });

  window.CREST_THEME = { toggle, apply };
})();
