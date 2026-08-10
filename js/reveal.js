// Scroll-reveal: fades/slides sections and cards into view. Applied
// automatically to structural elements already present on every page —
// no per-page markup needed. Respects prefers-reduced-motion via CSS
// (the .reveal rules themselves are gated in style.css).
(function () {
  if (!("IntersectionObserver" in window)) return;
  var targets = document.querySelectorAll("main > section, .card, .food-gallery figure");
  if (!targets.length) return;

  targets.forEach(function (el, i) {
    el.classList.add("reveal");
    el.style.transitionDelay = (i % 6) * 60 + "ms";
  });

  var obs = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          obs.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
  );
  targets.forEach(function (el) {
    obs.observe(el);
  });
})();
