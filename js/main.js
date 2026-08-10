// Shared site behavior: mobile nav toggle.
// (Photo fallback logic lives in img-fallback.js, loaded in <head>.)
(function () {
  var toggle = document.querySelector(".nav-toggle");
  var links = document.querySelector(".nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      links.classList.toggle("open");
    });
  }
})();
