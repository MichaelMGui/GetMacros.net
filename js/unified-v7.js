/* GetMacros Unified v7 interactions.
 * Navigation and motion are progressive enhancement: no content, result, or
 * control depends on this file becoming available.
 */
(function () {
  "use strict";

  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var mobile = window.matchMedia && window.matchMedia("(max-width: 900px)");
  var finePointer = window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  function headerState() {
    var header = document.querySelector(".site-header");
    if (!header) return;
    var queued = false;
    function paint() {
      var settled = (window.scrollY || 0) > 18;
      header.classList.toggle("is-scrolled", settled);
      document.body.classList.toggle("is-scrolled", settled);
      queued = false;
    }
    window.addEventListener("scroll", function () {
      if (queued) return;
      queued = true;
      requestAnimationFrame(paint);
    }, { passive: true });
    paint();
  }

  function readingProgress() {
    var content = document.querySelector(".article-container,.focused-guide-body");
    var header = document.querySelector(".full-nav");
    if (!content || !header || content.textContent.trim().split(/\s+/).length < 700) return;
    var track = document.createElement("div");
    var fill = document.createElement("span");
    track.className = "reading-progress";
    track.setAttribute("aria-hidden", "true");
    track.appendChild(fill);
    header.appendChild(track);
    var queued = false;
    function paint() {
      var rect = content.getBoundingClientRect();
      var start = window.scrollY + rect.top - window.innerHeight * .28;
      var end = start + content.offsetHeight - window.innerHeight * .52;
      var amount = end <= start ? 0 : Math.max(0, Math.min(1, (window.scrollY - start) / (end - start)));
      track.style.setProperty("--read-progress", amount.toFixed(4));
      queued = false;
    }
    window.addEventListener("scroll", function () {
      if (queued) return;
      queued = true;
      requestAnimationFrame(paint);
    }, { passive: true });
    window.addEventListener("resize", paint, { passive: true });
    paint();
  }

  function theme() {
    var buttons = document.querySelectorAll("[data-theme-toggle]");
    if (!buttons.length) return;
    var stored = "";
    try { stored = localStorage.getItem("gm-theme") || ""; } catch (error) {}
    var initial = document.documentElement.getAttribute("data-theme") || stored || "light";
    function apply(mode, remember) {
      document.documentElement.setAttribute("data-theme", mode);
      if (remember) {
        try { localStorage.setItem("gm-theme", mode); } catch (error) {}
      }
      var dark = mode === "dark";
      buttons.forEach(function (button) {
        button.setAttribute("aria-pressed", String(dark));
        button.setAttribute("aria-label", dark ? "Switch to light theme" : "Switch to dark theme");
        // The moon and sun are both in the markup; CSS reveals the one that
        // matches the current theme, so nothing here touches .theme-icon.
        var label = button.querySelector(".theme-label");
        if (label) label.textContent = dark ? "Light" : "Dark";
      });
      var meta = document.querySelector('meta[name="theme-color"]');
      if (meta) meta.setAttribute("content", dark ? "#0a3a26" : "#f4f7f2");
    }
    apply(initial === "dark" ? "dark" : "light", false);
    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        apply(document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark", true);
      });
    });
  }

  function navigation() {
    var nav = document.querySelector(".full-nav");
    if (!nav) return;
    var toggle = nav.querySelector(".nav-toggle");
    var links = nav.querySelector(".full-nav-links");
    var groups = Array.prototype.slice.call(nav.querySelectorAll(".nav-group"));
    if (!links) return;

    function closeGroups(except) {
      groups.forEach(function (group) {
        if (group === except) return;
        group.classList.remove("is-open");
        var trigger = group.querySelector(".nav-group-trigger");
        if (trigger) trigger.setAttribute("aria-expanded", "false");
      });
    }
    // The menu deliberately does not lock body scroll.
    //
    // `.nav-open{overflow:hidden}` reset the page to the top, because a body
    // that is still scrolled stops being scrollable -- the "I have to scroll
    // back up" problem. Pinning the body with position:fixed fixed that but
    // moved the drawer out of the viewport, since it is anchored inside a
    // sticky header.
    //
    // Leaving scroll alone is simpler and correct: the header is sticky, so
    // the drawer opens under it wherever you are, and closing the menu cannot
    // lose your place because nothing ever moved.
    function setNav(open) {
      document.body.classList.toggle("nav-open", open);
      if (toggle) {
        toggle.setAttribute("aria-expanded", String(open));
        var label = toggle.querySelector(".sr-only");
        if (label) label.textContent = open ? "Close site menu" : "Open site menu";
      }
      if (!open) closeGroups();
    }
    if (toggle) {
      toggle.addEventListener("click", function () {
        setNav(!document.body.classList.contains("nav-open"));
      });
    }
    groups.forEach(function (group) {
      var trigger = group.querySelector(".nav-group-trigger");
      if (!trigger) return;
      trigger.addEventListener("click", function () {
        var open = !group.classList.contains("is-open");
        closeGroups(group);
        group.classList.toggle("is-open", open);
        trigger.setAttribute("aria-expanded", String(open));
      });
    });
    document.addEventListener("click", function (event) {
      if (!nav.contains(event.target)) setNav(false);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key !== "Escape") return;
      var wasOpen = document.body.classList.contains("nav-open");
      setNav(false);
      if (wasOpen && toggle) {
        try { toggle.focus({ preventScroll: true }); }
        catch (error) { toggle.focus(); }
      }
    });
    links.addEventListener("click", function (event) {
      if (mobile.matches && event.target.closest("a")) setNav(false);
    });
    if (mobile.addEventListener) mobile.addEventListener("change", function () { setNav(false); });

    var current = (location.pathname.split("/").pop() || "index.html").toLowerCase();
    links.querySelectorAll("a[href]").forEach(function (link) {
      var target = (link.getAttribute("href") || "").split("#")[0].split("?")[0].split("/").pop().toLowerCase();
      var active = target === current;
      if (active) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
      if (active) {
        var parent = link.closest(".nav-group");
        if (parent) parent.classList.add("is-current");
      }
    });
  }

  function accessibility() {
    document.querySelectorAll(".table-wrap,.table-scroll").forEach(function (wrap) {
      if (!wrap.hasAttribute("tabindex")) wrap.tabIndex = 0;
      if (!wrap.hasAttribute("role")) wrap.setAttribute("role", "region");
      if (!wrap.hasAttribute("aria-label")) wrap.setAttribute("aria-label", "Scrollable nutrition table");
    });
    document.querySelectorAll("main img:not([width])").forEach(function (image) {
      image.setAttribute("decoding", "async");
    });
  }

  function reveals() {
    document.querySelectorAll(".studio-reveal").forEach(function (item) {
      item.classList.add("is-visible");
    });
    if (reduced || !("IntersectionObserver" in window)) return;
    var selector = [
      "main > section:not(:first-of-type) .section-head",
      "main > section:not(:first-of-type) > .container > h2",
      ".guide-card", ".blog-card", ".tool-card", ".goal-card", ".chain-card",
      ".result-card", ".explore-card", ".pick-card", ".ranking-card",
      ".food-gallery > *", ".content-grid > *", ".two-col > *"
    ].join(",");
    var items = [];
    document.querySelectorAll(selector).forEach(function (item) {
      if (item.closest("#meal-quiz,#macro-meals,[aria-live]")) return;
      if (items.indexOf(item) !== -1) return;
      item.classList.add("u-reveal");
      item.style.setProperty("--u-delay", (items.length % 3) * 45 + "ms");
      items.push(item);
    });
    if (!items.length) return;
    document.documentElement.classList.add("u-reveal-ready");
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    }, { threshold: .06, rootMargin: "0px 0px -6%" });
    items.forEach(function (item) {
      var rect = item.getBoundingClientRect();
      if (rect.top < window.innerHeight * .94) item.classList.add("is-visible");
      else observer.observe(item);
    });
    window.setTimeout(function () {
      items.forEach(function (item) { item.classList.add("is-visible"); });
    }, 1800);
  }

  function titleReveals() {
    document.querySelectorAll("[data-reveal-title]").forEach(function (heading) {
      // Do not rebuild headings after the page has laid out. Per-word wrapper
      // spans can change a line break by a few pixels; on a refresh farther
      // down the page that becomes a visible vertical jump. The heading stays
      // untouched and any motion is paint-only, so its height never changes.
      requestAnimationFrame(function () { heading.classList.add("is-title-visible"); });
    });
  }

  function pointerLight() {
    if (reduced || !finePointer) return;
    var cards = document.querySelectorAll(".guide-card,.blog-card,.tool-card,.goal-card,.chain-card,.result-card,.explore-card,.pick-card,.meal-card,[data-spotlight]");
    cards.forEach(function (card) {
      card.classList.add("u-pointer-card");
      var frame = 0;
      card.addEventListener("pointermove", function (event) {
        if (frame) return;
        frame = requestAnimationFrame(function () {
          var rect = card.getBoundingClientRect();
          card.style.setProperty("--u-x", ((event.clientX - rect.left) / rect.width * 100).toFixed(1) + "%");
          card.style.setProperty("--u-y", ((event.clientY - rect.top) / rect.height * 100).toFixed(1) + "%");
          frame = 0;
        });
      }, { passive: true });
    });
  }

  function compactRankings() {
    document.querySelectorAll(".ranking-card .ranking-list").forEach(function (list) {
      var rows = Array.prototype.slice.call(list.children);
      if (rows.length <= 5 || list.dataset.compactReady) return;
      list.dataset.compactReady = "true";
      rows.slice(5, 8).forEach(function (row) { row.classList.add("ranking-extra"); });
      rows.slice(8).forEach(function (row) { row.classList.add("ranking-overflow"); });
      var button = document.createElement("button");
      button.type = "button";
      button.className = "ranking-more";
      button.setAttribute("aria-expanded", "false");
      button.textContent = "See 3 more";
      button.addEventListener("click", function () {
        var open = list.classList.toggle("show-all");
        button.setAttribute("aria-expanded", String(open));
        button.textContent = open ? "Show top 5" : "See " + Math.min(3, rows.length - 5) + " more";
      });
      list.insertAdjacentElement("afterend", button);
    });
  }

  function start() {
    try { theme(); } catch (error) {}
    try { headerState(); } catch (error) {}
    try { readingProgress(); } catch (error) {}
    try { navigation(); } catch (error) {}
    try { accessibility(); } catch (error) {}
    try { compactRankings(); } catch (error) {}
    try { titleReveals(); } catch (error) {}
    try { reveals(); } catch (error) {}
    try { pointerLight(); } catch (error) {}
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
}());
