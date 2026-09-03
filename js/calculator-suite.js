(function () {
  "use strict";

  var pages = {
    "calculators.html": "calculator",
    "recipe-macro-scaler.html": "recipe",
    "nutrition-label-comparison-tool.html": "compare",
    "protein-value-calculator.html": "value",
    "budget-meal-builder.html": "basket",
    "sodium-label-comparison-tool.html": "sodium",
    "carbohydrate-label-portion-tool.html": "carbs",
    "weight-goal-timeline-calculator.html": "target",
    "sweat-rate-calculator.html": "water"
  };

  var file = (location.pathname.split("/").pop() || "index.html").toLowerCase();
  var icon = pages[file];
  if (!icon) return;

  document.body.classList.add("calculator-suite", "calculator-suite--" + icon);

  var icons = {
    calculator: '<rect x="5" y="3" width="14" height="18" rx="3"/><path d="M8 7h8M8 11h2m4 0h2m-8 4h2m4 0h2m-8 3h8"/>',
    recipe: '<path d="M6 5h12l-1 16H7L6 5Z"/><path d="M4 5h16M9 2v3m6-3v3M9 9h6m-6 4h6m-6 4h4"/>',
    compare: '<rect x="3" y="5" width="7" height="14" rx="2"/><rect x="14" y="5" width="7" height="14" rx="2"/><path d="M6 9h1m10 0h1M6 13h1m10 0h1M10 12h4"/>',
    value: '<path d="M4 6h10l6 6-8 8-8-8V6Z"/><circle cx="9" cy="10" r="1.5"/><path d="M13 9v6m2-5.2c-.6-.5-2-.5-2 .4 0 1.3 2.8.7 2.8 2.2 0 1.1-1.8 1.4-2.8.6"/>',
    basket: '<path d="M4 10h16l-2 10H6L4 10Z"/><path d="m8 10 4-7 4 7M8 14v2m4-2v2m4-2v2"/>',
    sodium: '<path d="M12 2S6 10 6 15a6 6 0 0 0 12 0c0-5-6-13-6-13Z"/><path d="M9 15a3 3 0 0 0 3 3m-1-7h2m-1-1v2"/>',
    carbs: '<path d="M12 22V4M8 6c2 0 4 2 4 4-2 0-4-2-4-4Zm8 4c-2 0-4 2-4 4 2 0 4-2 4-4ZM8 14c2 0 4 2 4 4-2 0-4-2-4-4Z"/>',
    target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/><path d="m15 9 5-5m-3 0h3v3"/>',
    water: '<path d="M12 2S6 10 6 15a6 6 0 0 0 12 0c0-5-6-13-6-13Z"/><path d="M9 15a3 3 0 0 0 3 3"/>'
  };

  function heroContainer() {
    var hero = document.querySelector("main > .hero, main > .tool-hero, main > .calc-hub-hero");
    if (hero) return hero.querySelector(":scope > .container") || hero;
    return document.querySelector("main > .article-container:has(> form)");
  }

  function addHeroMark() {
    if (file === "calculators.html") return;
    var host = heroContainer();
    if (!host || host.querySelector(":scope > .suite-hero-mark")) return;
    var mark = document.createElement("div");
    mark.className = "suite-hero-mark";
    mark.setAttribute("aria-hidden", "true");
    mark.innerHTML = '<svg viewBox="0 0 24 24">' + icons[icon] + "</svg>";
    // Keep the icon with the heading, not in a floating oversized hero column.
    var heading = host.querySelector("h1");
    if (heading) heading.insertAdjacentElement("beforebegin", mark);
    else host.prepend(mark);
  }

  function decorateForms() {
    document.querySelectorAll("main form").forEach(function (form) {
      if (form.closest(".site-header, .modern-footer")) return;
      form.classList.add("calculator-form");
      form.querySelectorAll("label").forEach(function (label) {
        if (label.querySelector("input, select, textarea")) label.classList.add("calculator-field");
      });
      form.querySelectorAll("button").forEach(function (button) {
        button.classList.add("calculator-button");
      });
      form.querySelectorAll('input[type="number"][min="0.01"][step="0.25"]').forEach(function (input) {
        /* A 0.01 minimum makes ordinary quarter-serving values such as 1 and
           1.5 fail native step validation. Anchor the step at 0.25 instead. */
        input.min = "0.25";
      });
    });
  }

  function decorateOutputs() {
    var selector = [
      "#out", "#result", "#wg-results", "#macro-results", "#protein-calc-results",
      "#fat-results", "#carb-calc-results", ".builder > .output", ".results"
    ].join(",");
    document.querySelectorAll(selector).forEach(function (output) {
      output.classList.add("calculator-output");
      var observer = new MutationObserver(function () {
        if (output.hidden) return;
        output.classList.remove("is-fresh");
        window.requestAnimationFrame(function () { output.classList.add("is-fresh"); });
      });
      observer.observe(output, { childList: true, subtree: true, attributes: true, attributeFilter: ["hidden"] });
    });
  }

  function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, function (character) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[character];
    });
  }

  function enhanceLegacyCalculators() {
    var form = document.getElementById("tool");
    var output = document.getElementById("out");
    if (!form || !output) return;

    if (file === "sodium-label-comparison-tool.html") {
      form.addEventListener("submit", function (event) {
        event.preventDefault();
        var a = Number(document.getElementById("am").value) * Number(document.getElementById("as").value);
        var b = Number(document.getElementById("bm").value) * Number(document.getElementById("bs").value);
        var aName = escapeHTML(document.getElementById("an").value || "Product A");
        var bName = escapeHTML(document.getElementById("bn").value || "Product B");
        var verdict = a === b ? "They are equal for these portions." : (a < b ? aName : bName) + " has less sodium for the entered portion.";
        output.innerHTML = '<p class="result-kicker">Your entered portions</p><h2>Portion comparison</h2>' +
          '<div class="calc-metric-grid"><article class="calc-metric"><span>' + aName + '</span><strong>' + Math.round(a) + ' mg</strong><small>' + Math.round(a / 2300 * 100) + '% of the general Daily Value</small><i style="--metric:' + Math.min(100, a / 2300 * 100) + '%"></i></article>' +
          '<article class="calc-metric"><span>' + bName + '</span><strong>' + Math.round(b) + ' mg</strong><small>' + Math.round(b / 2300 * 100) + '% of the general Daily Value</small><i style="--metric:' + Math.min(100, b / 2300 * 100) + '%"></i></article></div>' +
          '<p class="calc-verdict">' + verdict + '</p><p class="calc-result-note">The Daily Value is a label reference, not individualized medical advice.</p>';
        output.hidden = false;
      });
    }

    if (file === "carbohydrate-label-portion-tool.html") {
      form.addEventListener("submit", function (event) {
        event.preventDefault();
        var servings = Number(document.getElementById("s").value);
        var carbs = Number(document.getElementById("c").value || 0) * servings;
        var fiber = Number(document.getElementById("f").value || 0) * servings;
        var sugar = Number(document.getElementById("a").value || 0) * servings;
        output.innerHTML = '<p class="result-kicker">Your entered portion</p><h2>Label totals</h2><div class="calc-metric-grid calc-metric-grid--three">' +
          '<article class="calc-metric"><span>Total carbohydrate</span><strong>' + carbs.toFixed(1) + ' g</strong></article>' +
          '<article class="calc-metric"><span>Fiber</span><strong>' + fiber.toFixed(1) + ' g</strong></article>' +
          '<article class="calc-metric"><span>Added sugar</span><strong>' + sugar.toFixed(1) + ' g</strong></article></div>' +
          '<p class="calc-result-note">These are label calculations, not an insulin dose or a judgment about the food.</p>';
        output.hidden = false;
      });
    }

    form.addEventListener("reset", function () {
      output.hidden = true;
      output.innerHTML = "";
    });
  }

  function addPointerLight() {
    if (!window.matchMedia || !window.matchMedia("(pointer:fine)").matches) return;
    document.querySelectorAll("form.calculator-form, .toolbox, .builder").forEach(function (card) {
      card.addEventListener("pointermove", function (event) {
        var box = card.getBoundingClientRect();
        card.style.setProperty("--pointer-x", ((event.clientX - box.left) / box.width * 100).toFixed(1) + "%");
        card.style.setProperty("--pointer-y", ((event.clientY - box.top) / box.height * 100).toFixed(1) + "%");
      }, { passive: true });
    });
  }

  function addReveal() {
    var items = document.querySelectorAll("form.calculator-form, .toolbox, .builder, .tool-group, .expanded > .container");
    if (!items.length) return;
    if (!window.IntersectionObserver || (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches)) {
      items.forEach(function (item) { item.classList.add("calc-reveal", "is-visible"); });
      return;
    }
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    }, { threshold: .08, rootMargin: "0px 0px -6% 0px" });
    items.forEach(function (item) {
      item.classList.add("calc-reveal");
      // Anything already on screen is shown at once rather than waiting for a
      // callback that has nothing to report.
      if (item.getBoundingClientRect().top < window.innerHeight * 0.94) {
        item.classList.add("is-visible");
      } else {
        observer.observe(item);
      }
    });
    // Unconditional safety net. .calc-reveal sets opacity to 0, and until this
    // was here the only thing that ever put it back was the observer: if it
    // missed an element -- a slow device, a scroll that outran the callback, a
    // browser that batches differently -- the whole calculator stayed
    // invisible with no way to recover. A reveal is decoration; the tool
    // underneath it is not optional. js/unified-v7.js has had this fallback
    // all along, which is why its sections never went missing.
    window.setTimeout(function () {
      items.forEach(function (item) { item.classList.add("is-visible"); });
    }, 1500);
  }

  addHeroMark();
  decorateForms();
  decorateOutputs();
  enhanceLegacyCalculators();
  // Inputs must never fade out or move after load. Motion is reserved for
  // explicit interactions and fresh results, not the working surface.
}());
