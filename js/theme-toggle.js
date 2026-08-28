/* Light/dark toggle.
 *
 * The site follows the operating system by default. This only exists for the
 * override, so it writes data-theme on <html> and remembers the choice.
 *
 * The initial value is applied by a small inline script in <head> rather than
 * here: waiting for a deferred script means a dark-mode visitor sees a white
 * page flash first.
 */
(function () {
  "use strict";
  var KEY = "gm-theme";

  function current() {
    var set = document.documentElement.getAttribute("data-theme");
    if (set) return set;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark" : "light";
  }

  function apply(mode) {
    document.documentElement.setAttribute("data-theme", mode);
    try { localStorage.setItem(KEY, mode); } catch (e) {}
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", mode === "dark" ? "#0d1613" : "#1b6b4a");
    document.querySelectorAll("[data-theme-toggle]").forEach(function (b) {
      b.setAttribute("aria-pressed", String(mode === "dark"));
      b.setAttribute("aria-label", mode === "dark" ? "Switch to light theme" : "Switch to dark theme");
      b.querySelector(".theme-icon").textContent = mode === "dark" ? "☀" : "☾";
    });
  }

  function mount() {
    // Mount inside the nav row, not on the header element itself: appending
    // to .site-header dropped the button below the bar, where it sat on top
    // of the in-page section map.
    var nav = document.querySelector(
      ".full-nav .nav-actions, .full-nav, .modern-header .container," +
      ".site-header .container, .site-header nav");
    if (!nav || document.querySelector("[data-theme-toggle]")) return;
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "theme-toggle";
    btn.setAttribute("data-theme-toggle", "");
    btn.innerHTML = '<span class="theme-icon" aria-hidden="true">☾</span>';
    btn.addEventListener("click", function () {
      apply(current() === "dark" ? "light" : "dark");
    });
    nav.appendChild(btn);
    apply(current());
  }

  // Follow the system while the visitor has expressed no preference.
  if (window.matchMedia) {
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function (e) {
      var stored = null;
      try { stored = localStorage.getItem(KEY); } catch (err) {}
      if (!stored) apply(e.matches ? "dark" : "light");
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else { mount(); }
})();
