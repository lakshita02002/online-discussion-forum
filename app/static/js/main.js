"use strict";

(function initMobileNav() {
  const toggle = document.getElementById("navToggle");
  const links = document.getElementById("navLinks");
  if (!toggle || !links) return;

  toggle.addEventListener("click", () => {
    const isOpen = links.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(isOpen));
  });

  links
    .querySelectorAll("a")
    .forEach((link) =>
      link.addEventListener("click", () => links.classList.remove("open")),
    );
})();

(function initPasswordToggles() {
  document.querySelectorAll(".form__toggle-pw").forEach((btn) => {
    btn.addEventListener("click", () => {
      const wrap = btn.closest(".form__input-wrap");
      const input = wrap && wrap.querySelector("input");
      if (!input) return;

      const isText = input.type === "text";
      input.type = isText ? "password" : "text";
      btn.textContent = isText ? "👁" : "🙈";
      btn.setAttribute(
        "aria-label",
        isText ? "Show password" : "Hide password",
      );
    });
  });
})();

(function initFlashAutoDismiss() {
  document.querySelectorAll(".flash").forEach((flash) => {
    setTimeout(() => {
      flash.style.transition = "opacity 0.4s ease, max-height 0.4s ease";
      flash.style.opacity = "0";
      flash.style.maxHeight = "0";
      flash.style.overflow = "hidden";
      setTimeout(() => flash.remove(), 420);
    }, 5000);
  });
})();

(function initCharCounters() {
  document.querySelectorAll("textarea[maxlength]").forEach((textarea) => {
    const max = parseInt(textarea.getAttribute("maxlength"), 10);
    const counter = document.createElement("small");
    counter.className = "form__hint form__char-counter";
    counter.textContent = `0 / ${max}`;
    textarea.insertAdjacentElement("afterend", counter);

    textarea.addEventListener("input", () => {
      const len = textarea.value.length;
      counter.textContent = `${len} / ${max}`;
      counter.style.color =
        len > max * 0.9 ? "var(--clr-danger)" : "var(--clr-text-muted)";
    });
  });
})();

(function initDeleteConfirm() {
  // Handles forms using data-confirm; inline onsubmit= in templates covers the common case
  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (e) => {
      const msg = form.dataset.confirm || "Are you sure?";
      if (!window.confirm(msg)) e.preventDefault();
    });
  });
})();

(function initCommentHighlight() {
  const hash = window.location.hash;
  if (!hash.startsWith("#comment-")) return;
  const el = document.querySelector(hash);
  if (!el) return;
  el.style.boxShadow = "0 0 0 3px var(--clr-brand)";
  el.scrollIntoView({ behavior: "smooth", block: "center" });
  setTimeout(() => {
    el.style.boxShadow = "";
  }, 2500);
})();
