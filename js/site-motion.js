(function () {
  "use strict";
  var ticking = false;

  function updateHeader() {
    document.body.classList.toggle("is-scrolled", (window.scrollY || 0) > 12);
    ticking = false;
  }
  window.addEventListener("scroll", function () {
    if (!ticking) {
      ticking = true;
      window.requestAnimationFrame(updateHeader);
    }
  }, { passive: true });
  updateHeader();

  var mobileNav = document.querySelector(".full-nav-links");
  if (mobileNav && window.matchMedia && window.matchMedia("(max-width: 620px)").matches) {
    mobileNav.scrollLeft = 0;
  }

  /* Full-site reveal, progress, liquid and card behaviour lives in polish.js.
     This tiny companion only gives the sticky navigation a settled state. */
}());
