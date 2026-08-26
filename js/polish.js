/* Visual behaviour that CSS alone cannot express.
 *
 * Three rules hold throughout:
 *   - nothing here changes layout, so none of it can cost CLS;
 *   - everything degrades to the plain page if the API is missing or throws;
 *   - everything is skipped entirely under prefers-reduced-motion.
 */
(function () {
  "use strict";

  var reduced = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- Scroll reveal --------------------------------------------------
   * The .js-reveal class is what makes the items start hidden, and it is
   * added only once we know we can reveal them again. Without it the page
   * renders normally, so a browser lacking IntersectionObserver never shows
   * a blank column. */
  function reveal() {
    if (reduced || !("IntersectionObserver" in window)) return;
    // Static content only. Regions a script rewrites at run time -- search
    // results, the meal finder's output -- are excluded: their nodes are
    // replaced after this runs, so a node marked here can be swapped for one
    // that never gets observed, and the replacement inherits the hidden state
    // from CSS without ever being told to reveal.
    var targets = document.querySelectorAll(
      "main section > .container > *, main .goal-grid > *," +
      "main .tool-grid > *, main .guide-grid > *, main .chain-grid > *," +
      "main .pick-grid > *, main .explore-grid > *");
    if (!targets.length) return;

    var seen = 0;
    Array.prototype.forEach.call(targets, function (el) {
      // Leave the first screenful alone: animating what is already visible
      // makes the page look like it loaded broken.
      var r = el.getBoundingClientRect();
      if (r.top < window.innerHeight * 0.9) return;
      // A zero-height box never crosses the intersection threshold, so it
      // would stay hidden forever. Containers filled in later by script --
      // search results, for one -- are empty at this point and must be
      // left alone.
      if (r.height < 4) return;
      // Anything inside a live region is off limits for the same reason.
      if (el.closest("#results, #meal-quiz, #macro-meals, #search-results, [aria-live]")) return;
      if (el.id === "results" || el.id === "search-results") return;
      el.classList.add("reveal-item");
      seen++;
    });
    if (!seen) return;
    document.documentElement.classList.add("js-reveal");

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add("is-in");
        io.unobserve(e.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });

    document.querySelectorAll(".reveal-item").forEach(function (el) { io.observe(el); });

    // Safety net. Reveals everything still hidden after three seconds,
    // unconditionally: content invisible because an animation never fired is
    // a far worse outcome than an element that appears without its
    // transition. An earlier version only revealed items already in the
    // viewport, which left five blocks on the search page hidden for good.
    setTimeout(function () {
      document.querySelectorAll(".reveal-item:not(.is-in)").forEach(function (el) {
        el.classList.add("is-in");
      });
    }, 1200);
  }

  /* ---- Reading progress ---------------------------------------------- */
  function progress() {
    if (reduced) return;
    var article = document.querySelector("main");
    if (!article) return;
    var bar = document.createElement("div");
    bar.className = "read-progress";
    bar.setAttribute("aria-hidden", "true");
    document.body.appendChild(bar);

    var ticking = false;
    function update() {
      // scrollHeight is read fresh each frame: the reveal animation and any
      // late-loading content change document height after load, and caching
      // it left the bar stuck at 62% at the bottom of a long page.
      var doc = document.documentElement;
      var h = Math.max(doc.scrollHeight, document.body.scrollHeight) - window.innerHeight;
      var y = window.scrollY || doc.scrollTop || 0;
      var pct = h > 4 ? Math.min(Math.max(y / h, 0), 1) : 0;
      bar.style.transform = "scaleX(" + pct.toFixed(4) + ")";
      ticking = false;
    }
    window.addEventListener("scroll", function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener("resize", update, { passive: true });
    update();
  }

  /* ---- Pointer-following card sheen ----------------------------------
   * Writes two custom properties the CSS gradient reads. Throttled to one
   * write per frame so a fast pointer cannot flood the main thread. */
  function sheen() {
    if (reduced || !window.matchMedia("(hover: hover)").matches) return;
    var pending = null;
    document.addEventListener("pointermove", function (e) {
      var card = e.target.closest &&
        e.target.closest(".meal-card,.goal-card,.tool-card,.guide-card,.pick-card,.explore-card");
      if (!card) return;
      if (pending) return;
      pending = requestAnimationFrame(function () {
        var r = card.getBoundingClientRect();
        card.style.setProperty("--mx", ((e.clientX - r.left) / r.width * 100) + "%");
        card.style.setProperty("--my", ((e.clientY - r.top) / r.height * 100) + "%");
        pending = null;
      });
    }, { passive: true });
  }

  /* ---- Counting numbers ----------------------------------------------
   * Only runs on elements holding a plain number, and always ends on the
   * exact original text so a rounding difference cannot alter what is shown. */
  function countUp() {
    if (reduced || !("IntersectionObserver" in window)) return;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        io.unobserve(el);
        var final = el.textContent.trim();
        var m = final.match(/^([\d,]+)(.*)$/);
        if (!m) return;
        var target = parseInt(m[1].replace(/,/g, ""), 10);
        if (!isFinite(target) || target < 10) return;
        var suffix = m[2], start = performance.now(), dur = 850;
        function frame(now) {
          var t = Math.min((now - start) / dur, 1);
          var eased = 1 - Math.pow(1 - t, 3);
          if (t < 1) {
            el.textContent = Math.round(target * eased).toLocaleString() + suffix;
            requestAnimationFrame(frame);
          } else {
            el.textContent = final;   // restore the exact original string
          }
        }
        requestAnimationFrame(frame);
      });
    }, { threshold: 0.4 });
    document.querySelectorAll(".mm-num b, .stats-ribbon b, .proof-strip strong")
      .forEach(function (el) { io.observe(el); });
  }

  function start() {
    try { reveal(); } catch (e) { document.documentElement.classList.remove("js-reveal"); }
    try { progress(); } catch (e) {}
    try { sheen(); } catch (e) {}
    try { countUp(); } catch (e) {}
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
