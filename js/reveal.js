// Scroll-reveal: fades/slides sections and cards into view. Applied
// automatically to structural elements already present on every page —
// no per-page markup needed. Respects prefers-reduced-motion via CSS
// (the .reveal rules themselves are gated in style.css).
(function () {
  if (!("IntersectionObserver" in window)) return;
  var candidates = document.querySelectorAll("main > section, .card, .food-gallery figure");
  if (!candidates.length) return;

  // Elements much taller than the viewport (e.g. a glossary section holding
  // hundreds of terms) can never satisfy a percentage-of-target threshold —
  // a fixed number of visible pixels would need to exceed the viewport
  // itself. Skip the animation for those and just show them immediately;
  // only animate elements a normal scroll can plausibly bring fully (or
  // near-fully) into view.
  var maxRevealHeight = window.innerHeight * 2.5;
  var targets = [];
  candidates.forEach(function (el, i) {
    if (el.getBoundingClientRect().height > maxRevealHeight) return;
    el.classList.add("reveal");
    el.style.transitionDelay = (i % 6) * 60 + "ms";
    targets.push(el);
  });
  if (!targets.length) return;

  var obs = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          obs.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.01, rootMargin: "0px 0px -40px 0px" }
  );
  targets.forEach(function (el) {
    obs.observe(el);
  });
})();
