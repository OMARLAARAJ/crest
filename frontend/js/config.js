// Frontend runtime configuration. Override these by editing before deploy or
// by serving the frontend behind a reverse proxy that rewrites /api.
window.CREST_CONFIG = Object.assign(
  {
    API_BASE_URL: "http://localhost:8000/api/v1",
    COOKIE_AUTH: true,
    TOKEN_STORAGE_KEY: "crest.token",
    REFRESH_STORAGE_KEY: "crest.refresh",
    USER_STORAGE_KEY: "crest.user",
    PENDING_CHECKOUT_KEY: "crest.pending",
    THEME_STORAGE_KEY: "crest.theme",
    LANG_STORAGE_KEY: "crest.lang",
  },
  window.CREST_CONFIG || {}
);
