/* GetMacros Atelier v5 interactions.
 * Progressive enhancement only: navigation, section maps, icon upgrades and
 * subtle pointer depth. Core content and tools remain usable without it.
 */
(function () {
  "use strict";

  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var mobile = window.matchMedia && window.matchMedia("(max-width: 760px)");

  function navigation() {
    var nav = document.querySelector(".full-nav");
    var links = nav && nav.querySelector(".full-nav-links");
    if (!nav || !links) return;

    var toggle = nav.querySelector(".nav-toggle");
    var groups = Array.prototype.slice.call(nav.querySelectorAll(".nav-group"));

    function closeGroups(except) {
      groups.forEach(function (group) {
        if (group === except) return;
        group.classList.remove("is-open");
        var button = group.querySelector(".nav-group-trigger");
        if (button) button.setAttribute("aria-expanded", "false");
      });
    }

    function closeNav() {
      document.body.classList.remove("nav-open");
      if (toggle) toggle.setAttribute("aria-expanded", "false");
      closeGroups();
    }

    if (toggle) {
      toggle.addEventListener("click", function () {
        var opening = !document.body.classList.contains("nav-open");
        document.body.classList.toggle("nav-open", opening);
        toggle.setAttribute("aria-expanded", String(opening));
        if (!opening) closeGroups();
      });
    }

    groups.forEach(function (group) {
      var button = group.querySelector(".nav-group-trigger");
      if (!button) return;
      button.addEventListener("click", function () {
        var opening = !group.classList.contains("is-open");
        closeGroups(group);
        group.classList.toggle("is-open", opening);
        button.setAttribute("aria-expanded", String(opening));
      });
    });

    document.addEventListener("click", function (event) {
      if (!nav.contains(event.target)) closeNav();
    });
    document.addEventListener("keydown", function (event) {
      if (event.key !== "Escape") return;
      closeNav();
      if (toggle && mobile.matches) toggle.focus();
    });
    links.addEventListener("click", function (event) {
      if (mobile.matches && event.target.closest("a")) closeNav();
    });
    if (mobile.addEventListener) mobile.addEventListener("change", closeNav);
  }

  function activeNavigation() {
    var file = (window.location.pathname.split("/").pop() || "index.html").toLowerCase();
    document.querySelectorAll(".full-nav-links a[href]").forEach(function (link) {
      var href = link.getAttribute("href").toLowerCase();
      if (href === file) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
    var groups = document.querySelectorAll(".nav-group");
    groups.forEach(function (group) {
      var current = Array.prototype.some.call(group.querySelectorAll("a[href]"), function (link) {
        return link.getAttribute("href").toLowerCase() === file;
      });
      group.classList.toggle("is-current", current);
    });
  }

  function sectionMap() {
    if (!document.body.classList.contains("article-page")) return;
    if (document.body.classList.contains("restaurant-guide") || document.body.classList.contains("calculators-v2")) return;
    var main = document.querySelector("main");
    if (!main || main.querySelector(".section-map")) return;

    var headings = Array.prototype.filter.call(main.querySelectorAll("h2"), function (heading) {
      return heading.textContent.trim().length > 4 && !heading.closest("footer,.related-links,.source-box");
    }).slice(0, 6);
    if (headings.length < 4) return;

    var map = document.createElement("nav");
    map.className = "section-map";
    map.setAttribute("aria-label", "On this page");
    var inner = document.createElement("div");
    inner.className = "section-map-inner";
    var label = document.createElement("strong");
    label.textContent = "On this page";
    inner.appendChild(label);

    headings.forEach(function (heading, index) {
      if (!heading.id) heading.id = "section-" + (index + 1);
      var link = document.createElement("a");
      link.href = "#" + heading.id;
      link.textContent = heading.textContent.trim().replace(/\s+/g, " ");
      inner.appendChild(link);
    });
    map.appendChild(inner);

    var hero = main.querySelector("section[class*='hero']");
    if (hero) hero.insertAdjacentElement("afterend", map);
    else main.insertBefore(map, main.firstChild);
  }

  function upgradeToolIcons() {
    var files = {
      "recipe-macro-scaler.html": "icon-carbs",
      "nutrition-label-comparison-tool.html": "icon-document",
      "protein-value-calculator.html": "icon-protein",
      "budget-meal-builder.html": "icon-rice-bowl",
      "sodium-label-comparison-tool.html": "icon-water",
      "carbohydrate-label-portion-tool.html": "icon-carbs",
      "weight-goal-timeline-calculator.html": "icon-target",
      "sweat-rate-calculator.html": "icon-water",
      "calculators.html": "icon-calculator"
    };
    document.querySelectorAll("a.tool-card[href]").forEach(function (card) {
      var file = (card.getAttribute("href") || "").split("#")[0].split("/").pop();
      var icon = files[file];
      var badge = card.querySelector(":scope > span:first-child");
      if (!icon || !badge || badge.querySelector("svg")) return;
      badge.innerHTML = '<svg aria-hidden="true"><use href="icon-sprite.svg#' + icon + '"></use></svg>';
    });
  }

  function tableAccessibility() {
    document.querySelectorAll(".table-wrap,.table-scroll").forEach(function (wrap) {
      if (!wrap.hasAttribute("tabindex")) wrap.tabIndex = 0;
      if (!wrap.hasAttribute("role")) wrap.setAttribute("role", "region");
      if (!wrap.hasAttribute("aria-label")) wrap.setAttribute("aria-label", "Scrollable comparison table");
    });
  }

  function heroDepth() {
    if (reduced || !window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;
    var hero = document.querySelector("main section[class*='hero']");
    if (!hero) return;
    var frame = 0;
    hero.addEventListener("pointermove", function (event) {
      if (frame) return;
      frame = requestAnimationFrame(function () {
        var rect = hero.getBoundingClientRect();
        hero.style.setProperty("--hero-x", ((event.clientX - rect.left) / rect.width * 100).toFixed(1) + "%");
        hero.style.setProperty("--hero-y", ((event.clientY - rect.top) / rect.height * 100).toFixed(1) + "%");
        frame = 0;
      });
    }, { passive: true });
  }

  function start() {
    try { navigation(); } catch (error) {}
    try { activeNavigation(); } catch (error) {}
    try { sectionMap(); } catch (error) {}
    try { upgradeToolIcons(); } catch (error) {}
    try { tableAccessibility(); } catch (error) {}
    try { heroDepth(); } catch (error) {}
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
}());
