// Shared site behavior: keyboard skip link, resilient mobile navigation,
// current-page state, and small progressive-enhancement helpers.
(function () {
  "use strict";

  var main = document.querySelector("main");
  if (main) {
    if (!main.id) main.id = "main-content";
    if (!document.querySelector(".skip-link")) {
      var skip = document.createElement("a");
      skip.className = "skip-link";
      skip.href = "#" + main.id;
      skip.textContent = "Skip to main content";
      document.body.insertBefore(skip, document.body.firstChild);
    }
  }

  var toggle = document.querySelector(".nav-toggle");
  var links = document.querySelector(".nav-links");
  if (toggle && links) {
    if (!links.id) links.id = "site-navigation";
    toggle.setAttribute("aria-controls", links.id);
    toggle.setAttribute("aria-expanded", "false");

    function setOpen(open) {
      links.classList.toggle("open", open);
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    }

    toggle.addEventListener("click", function () {
      setOpen(!links.classList.contains("open"));
    });

    links.addEventListener("click", function (event) {
      if (event.target.closest("a")) setOpen(false);
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && links.classList.contains("open")) {
        setOpen(false);
        toggle.focus();
      }
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 1050) setOpen(false);
    }, { passive: true });
  }

  // Mark the current local navigation item when a hand-written page omitted it.
  var currentPath = location.pathname.replace(/\/$/, "/index.html").split("/").pop() || "index.html";
  document.querySelectorAll(".nav-links a[href]").forEach(function (link) {
    var target = link.getAttribute("href").split("#")[0].split("?")[0];
    if (target === currentPath && !link.hasAttribute("aria-current")) {
      link.setAttribute("aria-current", "page");
    }
  });

  // External sources open in the same tab by default, but disclose their
  // destination to assistive technology when visible text does not.
  document.querySelectorAll('main a[href^="http"]').forEach(function (link) {
    if (!link.getAttribute("aria-label") && !link.textContent.trim()) {
      link.setAttribute("aria-label", "Open external source");
    }
  });
})();
