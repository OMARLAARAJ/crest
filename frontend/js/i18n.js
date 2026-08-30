// Internationalization: fetches locale JSON, applies DOM translations,
// swaps <html dir="..."> + <html lang="...">, persists preference.
(function () {
  "use strict";

  const SUPPORTED = ["en", "ar"];
  const DEFAULT_LANG = "en";
  const cfg = window.CREST_CONFIG;

  const cache = Object.create(null);
  let currentLang = DEFAULT_LANG;

  function detectInitialLang() {
    try {
      const stored = localStorage.getItem(cfg.LANG_STORAGE_KEY);
      if (stored && SUPPORTED.includes(stored)) return stored;
    } catch (_) { /* ignore */ }
    const navLang = (navigator.language || "").toLowerCase();
    if (navLang.startsWith("ar")) return "ar";
    return DEFAULT_LANG;
  }

  async function load(lang) {
    if (cache[lang]) return cache[lang];
    const res = await fetch(`locales/${lang}.json`, { credentials: "omit" });
    if (!res.ok) throw new Error(`Failed to load ${lang}.json`);
    const dict = await res.json();
    cache[lang] = dict;
    return dict;
  }

  function interpolate(template, vars) {
    if (!vars) return template;
    return template.replace(/\{(\w+)\}/g, (_, key) =>
      Object.prototype.hasOwnProperty.call(vars, key) ? String(vars[key]) : `{${key}}`
    );
  }

  function applyTranslations(root) {
    const scope = root || document;
    const dict = cache[currentLang] || {};
    scope.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      const value = dict[key];
      if (typeof value === "string") el.textContent = value;
    });
    scope.querySelectorAll("[data-i18n-html]").forEach((el) => {
      const key = el.getAttribute("data-i18n-html");
      const value = dict[key];
      if (typeof value === "string") el.textContent = value;
    });
    scope.querySelectorAll("[data-i18n-attr]").forEach((el) => {
      const spec = el.getAttribute("data-i18n-attr"); // "attr:key,attr:key"
      spec.split(",").forEach((part) => {
        const [attr, key] = part.split(":").map((s) => s.trim());
        if (!attr || !key) return;
        const value = dict[key];
        if (typeof value === "string") el.setAttribute(attr, value);
      });
    });
  }

  function applyDirAndLang() {
    const html = document.documentElement;
    html.lang = currentLang;
    html.dir = currentLang === "ar" ? "rtl" : "ltr";
  }

  function t(key, vars) {
    const dict = cache[currentLang] || {};
    const value = dict[key];
    if (typeof value !== "string") return key;
    return interpolate(value, vars);
  }

  async function setLang(lang, opts = {}) {
    if (!SUPPORTED.includes(lang)) lang = DEFAULT_LANG;
    currentLang = lang;
    try { localStorage.setItem(cfg.LANG_STORAGE_KEY, lang); } catch (_) { /* ignore */ }
    await load(lang);
    applyDirAndLang();
    applyTranslations(opts.scope || document);
    document.dispatchEvent(new CustomEvent("i18n:change", { detail: { lang } }));
    return lang;
  }

  function getLang() { return currentLang; }

  // Initialize
  document.addEventListener("DOMContentLoaded", async () => {
    currentLang = detectInitialLang();
    try {
      await load(currentLang);
    } catch (_) {
      currentLang = DEFAULT_LANG;
      await load(currentLang);
    }
    applyDirAndLang();
    applyTranslations(document);
  });

  window.CREST_I18N = { setLang, getLang, t, applyTranslations };
})();
