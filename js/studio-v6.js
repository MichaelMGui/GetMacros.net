/* GetMacros Studio v6 progressive enhancement. */
(function () {
  "use strict";

  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var finePointer = window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  function floatingHeader() {
    var header = document.querySelector(".site-header");
    if (!header) return;
    var scheduled = false;
    function paint() {
      header.classList.toggle("is-scrolled", window.scrollY > 24);
      scheduled = false;
    }
    window.addEventListener("scroll", function () {
      if (scheduled) return;
      scheduled = true;
      requestAnimationFrame(paint);
    }, { passive: true });
    paint();
  }

  function titleReveals() {
    if (reduced) return;
    document.querySelectorAll("[data-reveal-title]").forEach(function (heading) {
      if (heading.dataset.revealReady) return;
      var words = heading.textContent.trim().split(/\s+/);
      heading.textContent = "";
      words.forEach(function (word, index) {
        var outer = document.createElement("span");
        var inner = document.createElement("span");
        outer.className = "gm6-title-word";
        outer.style.setProperty("--word-index", index);
        inner.textContent = word;
        outer.appendChild(inner);
        heading.appendChild(outer);
        if (index < words.length - 1) heading.appendChild(document.createTextNode(" "));
      });
      heading.dataset.revealReady = "true";
      requestAnimationFrame(function () { heading.classList.add("is-title-visible"); });
    });
  }

  function scrollReveals() {
    var items = Array.prototype.slice.call(document.querySelectorAll(".studio-reveal"));
    if (!items.length) return;
    if (reduced || !("IntersectionObserver" in window)) {
      items.forEach(function (item) { item.classList.add("is-visible"); });
      return;
    }
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    }, { threshold: .08, rootMargin: "0px 0px -7%" });
    items.forEach(function (item, index) {
      item.style.setProperty("--reveal-delay", (index % 4) * 55 + "ms");
      observer.observe(item);
    });
  }

  function spotlight() {
    if (reduced || !finePointer) return;
    document.querySelectorAll("[data-spotlight]").forEach(function (surface) {
      var frame = 0;
      surface.addEventListener("pointermove", function (event) {
        if (frame) return;
        frame = requestAnimationFrame(function () {
          var rect = surface.getBoundingClientRect();
          var x = (event.clientX - rect.left) / rect.width;
          var y = (event.clientY - rect.top) / rect.height;
          surface.style.setProperty("--spot-x", (x * 100).toFixed(1) + "%");
          surface.style.setProperty("--spot-y", (y * 100).toFixed(1) + "%");
          if (surface.classList.contains("gm6-decision-panel")) {
            surface.style.setProperty("--tilt-x", ((x - .5) * 4).toFixed(2) + "deg");
            surface.style.setProperty("--tilt-y", ((.5 - y) * 3).toFixed(2) + "deg");
          }
          frame = 0;
        });
      }, { passive: true });
      surface.addEventListener("pointerleave", function () {
        surface.style.removeProperty("--tilt-x");
        surface.style.removeProperty("--tilt-y");
      });
    });
  }

  function goalStory() {
    var visual = document.querySelector(".gm6-story-visual");
    var steps = Array.prototype.slice.call(document.querySelectorAll(".gm6-story-step"));
    if (!visual || !steps.length) return;
    var title = visual.querySelector("[data-story-title]");
    var copy = visual.querySelector("[data-story-copy]");
    var number = visual.querySelector("[data-story-number]");
    function activate(step) {
      steps.forEach(function (item) { item.classList.toggle("is-active", item === step); });
      if (title) title.textContent = step.dataset.title;
      if (copy) copy.textContent = step.dataset.copy;
      if (number) number.textContent = step.dataset.number;
      visual.style.setProperty("--story-width", step.dataset.width || "70%");
    }
    activate(steps[0]);
    if (reduced || !("IntersectionObserver" in window)) return;
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) activate(entry.target);
      });
    }, { rootMargin: "-35% 0px -45%", threshold: 0 });
    steps.forEach(function (step) { observer.observe(step); });
  }

  function readingProgress() {
    if (!document.body.classList.contains("article-page")) return;
    var progress = document.createElement("div");
    progress.className = "reading-progress";
    progress.setAttribute("aria-hidden", "true");
    document.body.appendChild(progress);
    var scheduled = false;
    function paint() {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      progress.style.setProperty("--reading", (max > 0 ? Math.min(100, window.scrollY / max * 100) : 0).toFixed(1) + "%");
      scheduled = false;
    }
    window.addEventListener("scroll", function () {
      if (scheduled) return;
      scheduled = true;
      requestAnimationFrame(paint);
    }, { passive: true });
    paint();
  }

  function tagExistingSections() {
    document.querySelectorAll("main > section:not(:first-child) .section-head, main > section:not(:first-child) > .container > h2").forEach(function (item) {
      item.classList.add("studio-reveal");
    });
    document.querySelectorAll(".goal-card,.tool-card,.guide-card,.blog-card,.ranking-card,.pick-card,.meal-card").forEach(function (item, index) {
      if (index < 24) item.classList.add("studio-reveal");
    });
  }

  function start() {
    try { floatingHeader(); } catch (error) {}
    try { tagExistingSections(); } catch (error) {}
    try { titleReveals(); } catch (error) {}
    try { scrollReveals(); } catch (error) {}
    try { spotlight(); } catch (error) {}
    try { goalStory(); } catch (error) {}
    try { readingProgress(); } catch (error) {}
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
}());
