// Authentication state + UI wiring for the login/register modal.
// Exposes CREST_AUTH.{user, login, register, logout, isAuthenticated}
(function () {
  "use strict";

  const cfg = window.CREST_CONFIG;
  const api = window.CREST_API;
  let user = null;

  function loadStoredUser() {
    try {
      const raw = localStorage.getItem(cfg.USER_STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (_) { return null; }
  }

  function persistUser(u) {
    try {
      if (u) localStorage.setItem(cfg.USER_STORAGE_KEY, JSON.stringify(u));
      else localStorage.removeItem(cfg.USER_STORAGE_KEY);
    } catch (_) { /* ignore */ }
  }

  function isAuthenticated() { return Boolean(api.getStoredToken() && user); }

  function getUser() { return user; }

  async function refreshMe() {
    if (!api.getStoredToken()) { user = null; persistUser(null); return null; }
    try {
      const me = await api.me();
      user = me;
      persistUser(me);
      return me;
    } catch (err) {
      user = null;
      persistUser(null);
      return null;
    }
  }

  async function login(email, password) {
    const tokens = await api.login({ email, password });
    api.setStoredTokens(tokens.access_token, tokens.refresh_token);
    await refreshMe();
    return user;
  }

  async function register(payload) {
    const tokens = await api.register(payload);
    api.setStoredTokens(tokens.access_token, tokens.refresh_token);
    await refreshMe();
    return user;
  }

  async function logout() {
    try { await api.logout(); } catch (_) { /* ignore */ }
    api.clearStoredTokens();
    user = null;
    persistUser(null);
    document.dispatchEvent(new CustomEvent("auth:logout", { detail: { reason: "user" } }));
  }

  function onLogout(handler) {
    document.addEventListener("auth:logout", (e) => handler(e.detail));
  }

  function init() {
    user = loadStoredUser();
    // Best-effort refresh; ignore failures.
    refreshMe();
  }

  document.addEventListener("DOMContentLoaded", init);

  window.CREST_AUTH = {
    getUser, isAuthenticated, login, register, logout, refreshMe, onLogout,
  };
})();
