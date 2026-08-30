// Small fetch wrapper. Centralizes:
// - JSON parsing
// - Authorization header injection
// - Surface FastAPI error envelopes as structured exceptions
// - 401 handling (clear token + emit "auth:logout")
(function () {
  "use strict";

  const cfg = window.CREST_CONFIG;

  function getStoredToken() {
    try {
      return localStorage.getItem(cfg.TOKEN_STORAGE_KEY);
    } catch (_) {
      return null;
    }
  }

  function getStoredRefresh() {
    try {
      return localStorage.getItem(cfg.REFRESH_STORAGE_KEY);
    } catch (_) {
      return null;
    }
  }

  function setStoredTokens(access, refresh) {
    try {
      if (access) localStorage.setItem(cfg.TOKEN_STORAGE_KEY, access);
      if (refresh) localStorage.setItem(cfg.REFRESH_STORAGE_KEY, refresh);
    } catch (_) { /* ignore */ }
  }

  function clearStoredTokens() {
    try {
      localStorage.removeItem(cfg.TOKEN_STORAGE_KEY);
      localStorage.removeItem(cfg.REFRESH_STORAGE_KEY);
      localStorage.removeItem(cfg.USER_STORAGE_KEY);
    } catch (_) { /* ignore */ }
  }

  class ApiError extends Error {
    constructor(message, status, payload) {
      super(message);
      this.name = "ApiError";
      this.status = status;
      this.payload = payload;
    }
  }

  async function request(path, options = {}) {
    const opts = Object.assign(
      {
        method: "GET",
        credentials: cfg.COOKIE_AUTH ? "include" : "same-origin",
        headers: { Accept: "application/json" },
      },
      options
    );

    if (opts.body && !(opts.body instanceof FormData) && typeof opts.body !== "string") {
      opts.body = JSON.stringify(opts.body);
      opts.headers["Content-Type"] = "application/json";
    }

    const token = getStoredToken();
    if (token && !opts.skipAuth) {
      opts.headers["Authorization"] = `Bearer ${token}`;
    }

    const url = path.startsWith("http") ? path : `${cfg.API_BASE_URL}${path}`;
    let response;
    try {
      response = await fetch(url, opts);
    } catch (networkErr) {
      throw new ApiError("Network error — please try again.", 0, null);
    }

    let payload = null;
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      try { payload = await response.json(); } catch (_) { payload = null; }
    }

    if (!response.ok) {
      const message =
        (payload && (payload.error || payload.detail)) ||
        response.statusText ||
        "Request failed.";
      if (response.status === 401 && !opts.skipAuth) {
        clearStoredTokens();
        window.dispatchEvent(new CustomEvent("auth:logout", { detail: { reason: "expired" } }));
      }
      throw new ApiError(message, response.status, payload);
    }

    return payload;
  }

  const api = {
    ApiError,
    getStoredToken,
    getStoredRefresh,
    setStoredTokens,
    clearStoredTokens,
    request,

    // ---- auth ----
    register(payload) {
      return request("/auth/register", { method: "POST", body: payload });
    },
    login(payload) {
      return request("/auth/login", { method: "POST", body: payload });
    },
    refresh() {
      const refreshToken = getStoredRefresh();
      return request("/auth/refresh", {
        method: "POST",
        body: { refresh_token: refreshToken },
        skipAuth: true,
      });
    },
    logout() {
      return request("/auth/logout", { method: "POST" }).catch(() => null);
    },
    me() {
      return request("/auth/me");
    },

    // ---- catalog ----
    listPrograms() { return request("/programs"); },
    listPacks() { return request("/packs"); },

    // ---- checkout ----
    createCheckout(payload) {
      return request("/checkout", { method: "POST", body: payload });
    },

    // ---- contact ----
    submitContact(payload) {
      return request("/contact", { method: "POST", body: payload });
    },
  };

  window.CREST_API = api;
})();
