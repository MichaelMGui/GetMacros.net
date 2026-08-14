// Shared site behavior: keyboard skip link, resilient mobile navigation,
// current-page state, and small progressive-enhancement helpers.
(function () {
  "use strict";

  // Give every original template the same identity and navigation as the
  // modern homepage and restaurant experience.
  var oldHeader = document.querySelector(".site-header:not(.modern-header)");
  if (oldHeader) {
    var unifiedStyle = document.createElement("style");
    unifiedStyle.textContent = ".modern-header{background:rgba(247,248,243,.96);border-bottom:1px solid #dce4dd}.full-nav{max-width:1320px;min-height:76px;margin:auto;padding:0 20px;display:flex;align-items:center;gap:24px}.modern-brand{display:flex;align-items:center;gap:10px;color:#10231b;text-decoration:none;font:800 1.08rem system-ui}.brand-mark{width:34px;height:34px;border-radius:11px;background:#10231b;color:#dfff69;display:grid;place-items:center}.brand-dot{color:#4b9e69}.full-nav-links{display:flex;align-items:center;gap:19px;margin-left:auto}.full-nav-links a{color:#10231b;text-decoration:none;font:700 .79rem system-ui;white-space:nowrap}.nav-action{background:#10231b;color:#fff!important;text-decoration:none;padding:11px 18px;border-radius:999px;font:750 .82rem system-ui;white-space:nowrap}.modern-footer{padding:55px max(24px,calc((100% - 1192px)/2));display:grid;grid-template-columns:2fr repeat(3,1fr);gap:45px;background:#0f241b;color:#fff}.modern-footer>div{display:flex;flex-direction:column;gap:9px}.modern-footer p,.modern-footer a{color:#aebfb6;font:.82rem system-ui;text-decoration:none}.modern-footer small{grid-column:1/-1;padding-top:25px;border-top:1px solid #31483d;color:#84988d}@media(max-width:980px){.full-nav{flex-wrap:wrap;padding-top:10px}.full-nav-links{order:3;width:100%;overflow:auto;padding-bottom:11px}.full-nav .nav-action{margin-left:auto}}@media(max-width:650px){.full-nav-links{gap:8px 15px;flex-wrap:wrap}.full-nav-links a{font-size:.69rem}.full-nav .nav-action{display:none}.modern-footer{grid-template-columns:1fr 1fr;padding:40px 20px}.modern-footer>div:first-child{grid-column:1/-1}}";
    document.head.appendChild(unifiedStyle);
    oldHeader.classList.add("modern-header");
    oldHeader.innerHTML = '<nav class="full-nav" aria-label="Main navigation"><a class="modern-brand" href="index.html" aria-label="GetMacros.net home"><span class="brand-mark" aria-hidden="true">G</span><span>GetMacros<span class="brand-dot">.</span></span></a><div class="full-nav-links"><a href="index.html">Home</a><a href="articles.html">Articles</a><a href="calculators.html">Calculators</a><a href="quiz.html">Quizzes &amp; Games</a><a href="healthy-fast-food.html">Healthy Fast Food</a><a href="search.html">Search</a><a href="contact.html">Contact</a></div><a class="nav-action" href="restaurant-meal-finder.html">Find my meal</a></nav>';
  }

  var oldFooter = document.querySelector(".site-footer:not(.modern-footer)");
  if (oldFooter) {
    oldFooter.className = "modern-footer";
    oldFooter.innerHTML = '<div><a class="modern-brand footer-brand" href="index.html"><span class="brand-mark" aria-hidden="true">G</span><span>GetMacros<span class="brand-dot">.</span></span></a><p>Clear nutrition tools for real decisions. Independent, evidence-led and judgment-free.</p></div><div><strong>Explore</strong><a href="healthy-fast-food.html">Healthy fast food</a><a href="calculators.html">Calculators</a><a href="articles.html">Articles</a><a href="quiz.html">Quizzes &amp; games</a></div><div><strong>Standards</strong><a href="editorial-policy.html">Editorial policy</a><a href="sources.html">Sources</a><a href="corrections.html">Corrections</a></div><div><strong>Company</strong><a href="about.html">About</a><a href="privacy.html">Privacy</a><a href="contact.html">Contact</a></div><small>© 2026 GetMacros.net · Educational information, not individualized medical advice.</small>';
  }

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

  // Keep search reachable from every page, including older hand-written templates.
  if (links && !links.querySelector('a[href$="search.html"]')) {
    var searchItem = document.createElement("li");
    var searchLink = document.createElement("a");
    searchLink.href = "/search.html";
    searchLink.textContent = "Search";
    searchItem.appendChild(searchLink);
    var contactItem = links.querySelector(".nav-cta");
    links.insertBefore(searchItem, contactItem ? contactItem.closest("li") : null);
  }
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
