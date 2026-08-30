// UI plumbing: drawer, modal, toast, smooth scroll, header shadow on scroll.
(function () {
  "use strict";

  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

  // ---------- Drawer ----------
  function setDrawer(open) {
    const drawer = $(".drawer");
    const backdrop = $(".drawer-backdrop");
    if (!drawer) return;
    drawer.classList.toggle("open", open);
    backdrop.classList.toggle("open", open);
    drawer.setAttribute("aria-hidden", String(!open));
    document.body.style.overflow = open ? "hidden" : "";
    const opener = $("[data-menu-open]");
    if (opener) opener.setAttribute("aria-expanded", String(open));
  }

  // ---------- Modal ----------
  function setModal(open) {
    const modal = $(".modal");
    const backdrop = $(".modal-backdrop");
    if (!modal) return;
    modal.classList.toggle("open", open);
    backdrop.classList.toggle("open", open);
    modal.setAttribute("aria-hidden", String(!open));
    document.body.style.overflow = open ? "hidden" : "";
    if (open) {
      const focusable = modal.querySelector("input, button, [tabindex]");
      if (focusable) focusable.focus({ preventScroll: true });
    }
  }

  // ---------- Toast ----------
  let toastTimer;
  function showToast(message, opts = {}) {
    const toast = $(".toast");
    if (!toast) return;
    toast.textContent = message;
    toast.classList.toggle("err", Boolean(opts.error));
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("show"), opts.duration || 3200);
  }

  // ---------- Scroll shadow ----------
  function onScroll() {
    const header = $(".site-header");
    if (!header) return;
    header.classList.toggle("scrolled", window.scrollY > 8);
  }

  // ---------- Smooth-scroll for in-page links ----------
  function bindSmoothScroll() {
    $$('a[href^="#"]').forEach((a) => {
      a.addEventListener("click", (e) => {
        const id = a.getAttribute("href");
        if (!id || id === "#") return;
        const target = document.querySelector(id);
        if (!target) return;
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
        history.replaceState(null, "", id);
      });
    });
  }

  // ---------- Header navigation links highlight on scroll ----------
  function bindNavHighlight() {
    const links = $$(".nav-link");
    const sections = links
      .map((link) => {
        const id = link.getAttribute("href");
        if (!id || !id.startsWith("#")) return null;
        const el = document.querySelector(id);
        return el ? { link, el } : null;
      })
      .filter(Boolean);
    if (!sections.length) return;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const match = sections.find((s) => s.el === entry.target);
            if (match) links.forEach((l) => l.removeAttribute("aria-current"));
            if (match) match.link.setAttribute("aria-current", "true");
          }
        });
      },
      { rootMargin: "-45% 0px -45% 0px", threshold: 0 }
    );
    sections.forEach((s) => observer.observe(s.el));
  }

  // ---------- Wire static triggers ----------
  function bindStatic() {
    $$("[data-menu-open]").forEach((el) => el.addEventListener("click", () => setDrawer(true)));
    $$("[data-menu-close]").forEach((el) => el.addEventListener("click", () => setDrawer(false)));
    $$("[data-modal-open]").forEach((el) => el.addEventListener("click", () => setModal(true)));
    $$("[data-modal-close]").forEach((el) => el.addEventListener("click", () => setModal(false)));
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        setDrawer(false);
        setModal(false);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.documentElement.classList.remove("preload");
    bindStatic();
    bindSmoothScroll();
    bindNavHighlight();
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  });

  window.CREST_UI = { setDrawer, setModal, showToast };
})();
