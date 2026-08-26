(function () {
  "use strict";

  var root = document.documentElement;
  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  root.classList.add("motion-enabled");

  var progress = document.createElement("div");
  progress.className = "site-progress";
  progress.setAttribute("aria-hidden", "true");
  document.body.prepend(progress);

  var hero = document.querySelector(
    ".focus-hero, .focus-page-hero, .finder-hero, .calc-hub-hero, .guide-hub-hero, .search-hero, .article-hero"
  );
  if (hero) hero.classList.add("liquid-hero");

  var ticking = false;
  function paintScroll() {
    var y = window.scrollY || document.documentElement.scrollTop;
    var available = Math.max(document.documentElement.scrollHeight - window.innerHeight, 1);
    document.body.classList.toggle("is-scrolled", y > 12);
    progress.style.transform = "scaleX(" + Math.min(y / available, 1) + ")";
    if (hero && !reduced) hero.style.setProperty("--liquid-shift", Math.min(y * 0.035, 22));
    ticking = false;
  }
  window.addEventListener("scroll", function () {
    if (!ticking) {
      window.requestAnimationFrame(paintScroll);
      ticking = true;
    }
  }, { passive: true });
  paintScroll();

  var revealSelector = [
    "main > section", ".goal-card", ".tool-card", ".guide-card", ".chain-card",
    ".ranking-card", ".pick-card", ".panel", ".meal-card", ".result-card",
    ".explore-card", ".source-box", ".advice-card", ".tool-group", ".calculator-card", ".calc-card"
  ].join(",");
  var items = Array.prototype.slice.call(document.querySelectorAll(revealSelector));
  items.forEach(function (item, index) {
    item.classList.add("reveal-item");
    item.style.setProperty("--reveal-index", index % 6);
  });

  if (reduced || !("IntersectionObserver" in window)) {
    items.forEach(function (item) { item.classList.add("is-visible"); });
  } else {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -7%", threshold: .07 });
    items.forEach(function (item) { observer.observe(item); });
  }

  if (!reduced && window.matchMedia && window.matchMedia("(pointer: fine)").matches) {
    document.querySelectorAll(".sample-card, .finder-photo, .calc-photo-card").forEach(function (card) {
      card.addEventListener("pointermove", function (event) {
        var rect = card.getBoundingClientRect();
        var x = ((event.clientX - rect.left) / rect.width - .5) * 3.2;
        var y = ((event.clientY - rect.top) / rect.height - .5) * -3.2;
        card.style.setProperty("--tilt-x", x.toFixed(2));
        card.style.setProperty("--tilt-y", y.toFixed(2));
      });
      card.addEventListener("pointerleave", function () {
        card.style.setProperty("--tilt-x", 0);
        card.style.setProperty("--tilt-y", 0);
      });
    });
  }
}());
