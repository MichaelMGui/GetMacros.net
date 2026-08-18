(function () {
  "use strict";
  var input = document.getElementById("article-library-search");
  var sections = Array.prototype.slice.call(document.querySelectorAll(".library-section"));
  if (!input || !sections.length) return;
  var status = document.getElementById("library-search-status");

  sections.forEach(function (section) {
    var cards = Array.prototype.slice.call(section.querySelectorAll(".card"));
    section.dataset.expanded = "false";
    if (cards.length > 6) {
      var button = document.createElement("button");
      button.type = "button";
      button.className = "section-more";
      button.textContent = "Show all " + cards.length + " articles";
      button.addEventListener("click", function () {
        var expanded = section.dataset.expanded === "true";
        section.dataset.expanded = String(!expanded);
        apply("");
        button.textContent = expanded ? "Show all " + cards.length + " articles" : "Show fewer";
        if (expanded) section.scrollIntoView({ behavior: "smooth", block: "start" });
      });
      section.querySelector(".container").appendChild(button);
    }
  });

  function apply(raw) {
    var query = raw.trim().toLowerCase();
    var total = 0;
    sections.forEach(function (section) {
      var cards = Array.prototype.slice.call(section.querySelectorAll(".card"));
      var sectionMatches = 0;
      cards.forEach(function (card, index) {
        var matches = !query || card.textContent.toLowerCase().indexOf(query) !== -1;
        var withinLimit = section.dataset.expanded === "true" || index < 6;
        var show = query ? matches : withinLimit;
        card.classList.toggle("is-library-hidden", !show);
        if (matches) sectionMatches += 1;
      });
      total += sectionMatches;
      section.classList.toggle("is-no-results", query && sectionMatches === 0);
      var button = section.querySelector(".section-more");
      if (button) button.hidden = !!query;
    });
    if (status) {
      status.textContent = query ? (total ? total + " matching articles" : "No articles match that search. Try a broader word.") : "Showing the first six articles in each topic.";
      status.classList.toggle("library-empty", !!query && total === 0);
    }
  }
  input.addEventListener("input", function () { apply(input.value); });
  apply("");
})();
