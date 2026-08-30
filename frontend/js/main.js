// Main entry point — renders dynamic content (programs, packs) from the
// FastAPI backend, wires checkout → auth → checkout flow, and wires the
// contact form.
(function () {
  "use strict";

  const api = window.CREST_API;
  const auth = window.CREST_AUTH;
  const i18n = window.CREST_I18N;
  const ui = window.CREST_UI;

  // Map program slugs → translation keys so we keep one source of truth
  // for category labels in the i18n bundle.
  const PROGRAM_KEYS = {
    "built-different": {
      title: "programs.built.title",
      desc: "programs.built.desc",
      tag: "programs.tagStrength",
    },
    "peak-condition": {
      title: "programs.peak.title",
      desc: "programs.peak.desc",
      tag: "programs.tagConditioning",
    },
    "move-free": {
      title: "programs.move.title",
      desc: "programs.move.desc",
      tag: "programs.tagMobility",
    },
    "fuel-forward": {
      title: "programs.fuel.title",
      desc: "programs.fuel.desc",
      tag: "programs.tagNutrition",
    },
  };

  // ---------- Render: programs ----------
  function renderPrograms(programs) {
    const grid = document.getElementById("programs-grid");
    if (!grid) return;
    grid.innerHTML = "";
    programs.forEach((program) => {
      const keys = PROGRAM_KEYS[program.slug] || {};
      const title = i18n.t(keys.title || "") || program.title;
      const desc = i18n.t(keys.desc || "") || program.description;
      const tag = i18n.t(keys.tag || "") || program.category;
      const card = document.createElement("article");
      card.className = "program-card";
      card.innerHTML = `
        <div class="image">
          <img src="${escapeAttr(program.image_url)}" alt="${escapeAttr(title)}" loading="lazy" />
          <span class="tag">${escapeHtml(tag)}</span>
        </div>
        <div class="body">
          <h3>${escapeHtml(title)}</h3>
          <p>${escapeHtml(desc)}</p>
          <div class="row">
            <span class="chip"><span class="chip-dot"></span>${escapeHtml(program.category)}</span>
            <button class="btn btn-outline" data-checkout="program" data-item-id="${escapeAttr(program.id)}" data-item-title="${escapeAttr(title)}">
              ${escapeHtml(i18n.t("programs.select"))}
              <span aria-hidden="true">↗</span>
            </button>
          </div>
        </div>
      `;
      grid.appendChild(card);
    });
    wireCheckoutButtons(grid);
  }

  // ---------- Render: packs ----------
  function renderPacks(packs) {
    const grid = document.getElementById("packs-grid");
    if (!grid) return;
    grid.innerHTML = "";
    packs.forEach((pack) => {
      const featured = pack.is_featured;
      const card = document.createElement("article");
      card.className = "pack-card" + (featured ? " featured" : "");
      const features = (pack.features || [])
        .map((f) => `<li>${escapeHtml(f)}</li>`)
        .join("");
      card.innerHTML = `
        ${featured ? `<div class="badge">${escapeHtml(i18n.t("packs.popular"))} ✳</div>` : ""}
        <div class="head">
          <div>
            <span class="chip"><span class="chip-dot"></span>${escapeHtml(pack.name)}</span>
            <h3 style="margin-top:.75rem">${escapeHtml(pack.name)}</h3>
          </div>
          <div class="price">
            <strong>$${Number(pack.price).toFixed(0)}</strong>
            <small>${escapeHtml(i18n.t("packs.month"))}</small>
          </div>
        </div>
        <p class="desc">${escapeHtml(pack.description)}</p>
        <ul>${features}</ul>
        <button class="btn ${featured ? "btn-primary" : "btn-outline"}" data-checkout="pack" data-item-id="${escapeAttr(pack.id)}" data-item-title="${escapeAttr(pack.name)}">
          ${escapeHtml(i18n.t("packs.choose"))} ${escapeHtml(pack.name)}
          <span aria-hidden="true">↗</span>
        </button>
      `;
      grid.appendChild(card);
    });
    wireCheckoutButtons(grid);
  }

  // ---------- Wire checkout buttons (programs + packs) ----------
  function wireCheckoutButtons(scope) {
    (scope || document).querySelectorAll("[data-checkout]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const itemType = btn.dataset.checkout;
        const itemId = btn.dataset.itemId;
        const itemTitle = btn.dataset.itemTitle || "";
        if (!auth.isAuthenticated()) {
          try {
            sessionStorage.setItem(
              window.CREST_CONFIG.PENDING_CHECKOUT_KEY,
              JSON.stringify({ item_type: itemType, item_id: itemId, item_title: itemTitle })
            );
          } catch (_) { /* ignore */ }
          ui.showToast(i18n.t("toast.loginRequired"));
          window.CREST_UI.setModal(true);
          // Make sure the auth modal opens to the "login" view.
          switchAuthTab("login");
          return;
        }
        proceedToCheckout({ item_type: itemType, item_id: itemId, item_title: itemTitle });
      });
    });
  }

  async function proceedToCheckout(payload) {
    ui.showToast(i18n.t("toast.checkout"));
    try {
      const session = await api.createCheckout(payload);
      // In production this would redirect to the payment provider. We surface
      // the checkout id so the user sees the live API integration.
      ui.showToast(`✓ ${payload.item_title || session.item_title} — #${session.checkout_id.slice(0, 8)}`);
    } catch (err) {
      ui.showToast(err.message || i18n.t("auth.err.generic"), { error: true });
    }
  }

  // ---------- Auth modal: tabs + form submit ----------
  let currentAuthTab = "login";
  function switchAuthTab(tab) {
    currentAuthTab = tab;
    const tabs = document.querySelectorAll("[data-auth-tab]");
    tabs.forEach((t) => t.setAttribute("aria-selected", String(t.dataset.authTab === tab)));
    const loginFields = document.querySelectorAll("[data-auth-field='login']");
    const registerFields = document.querySelectorAll("[data-auth-field='register']");
    loginFields.forEach((f) => (f.style.display = tab === "login" ? "" : "none"));
    registerFields.forEach((f) => (f.style.display = tab === "register" ? "" : "none"));
    const err = document.querySelector(".auth-err");
    if (err) err.textContent = "";
  }

  async function submitAuth(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const errEl = form.querySelector(".auth-err");
    if (errEl) errEl.textContent = "";
    const data = new FormData(form);
    const payload = Object.fromEntries(data.entries());
    try {
      if (currentAuthTab === "register") {
        if (!payload.full_name || !payload.email || !payload.password) {
          throw new Error(i18n.t("auth.err.generic"));
        }
        await auth.register({
          email: payload.email,
          full_name: payload.full_name,
          password: payload.password,
          preferred_language: i18n.getLang(),
        });
      } else {
        if (!payload.email || !payload.password) {
          throw new Error(i18n.t("auth.err.generic"));
        }
        await auth.login(payload.email, payload.password);
      }
      window.CREST_UI.setModal(false);
      ui.showToast(i18n.t("toast.welcome"));
      // Resume pending checkout if any.
      try {
        const raw = sessionStorage.getItem(window.CREST_CONFIG.PENDING_CHECKOUT_KEY);
        if (raw) {
          sessionStorage.removeItem(window.CREST_CONFIG.PENDING_CHECKOUT_KEY);
          await proceedToCheckout(JSON.parse(raw));
        }
      } catch (_) { /* ignore */ }
    } catch (err) {
      if (errEl) errEl.textContent = err.message || i18n.t("auth.err.generic");
    }
  }

  function bindAuthModal() {
    document.querySelectorAll("[data-auth-tab]").forEach((t) => {
      t.addEventListener("click", () => switchAuthTab(t.dataset.authTab));
    });
    const form = document.querySelector("[data-auth-form]");
    if (form) form.addEventListener("submit", submitAuth);
  }

  // ---------- Language switcher ----------
  function bindLanguage() {
    const btn = document.querySelector("[data-language-toggle]");
    if (!btn) return;
    btn.addEventListener("click", async () => {
      const next = i18n.getLang() === "ar" ? "en" : "ar";
      await i18n.setLang(next);
      btn.textContent = next === "ar" ? "EN" : "AR";
      btn.setAttribute("aria-label", next === "ar" ? "Switch to English" : "التبديل إلى العربية");
    });
    btn.textContent = i18n.getLang() === "ar" ? "EN" : "AR";
  }

  // ---------- Logout button ----------
  function bindLogout() {
    document.addEventListener("click", (e) => {
      const target = e.target.closest("[data-logout]");
      if (!target) return;
      e.preventDefault();
      auth.logout();
    });
    auth.onLogout(() => {
      ui.showToast(i18n.t("toast.welcome"));
    });
  }

  // ---------- Contact form ----------
  function bindContact() {
    const form = document.querySelector("[data-contact-form]");
    if (!form) return;
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const status = form.querySelector(".contact-status");
      if (status) status.textContent = "";
      const data = new FormData(form);
      try {
        await api.submitContact({
          name: String(data.get("name") || "").trim(),
          email: String(data.get("email") || "").trim(),
          subject: String(data.get("subject") || "").trim(),
          message: String(data.get("message") || "").trim(),
          language: i18n.getLang(),
        });
        form.reset();
        ui.showToast(i18n.t("toast.contactReceived"));
      } catch (err) {
        if (status) status.textContent = err.message || i18n.t("auth.err.generic");
      }
    });
  }

  // ---------- Helpers ----------
  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }
  function escapeAttr(value) {
    return escapeHtml(value);
  }

  // ---------- Boot ----------
  async function loadData() {
    try {
      const [programs, packs] = await Promise.all([
        api.listPrograms(),
        api.listPacks(),
      ]);
      renderPrograms(programs);
      renderPacks(packs);
    } catch (err) {
      ui.showToast(err.message || "Failed to load catalog", { error: true });
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    bindAuthModal();
    bindLanguage();
    bindLogout();
    bindContact();
    // Wait one tick for i18n to populate, then load data.
    setTimeout(loadData, 0);
  });
})();
