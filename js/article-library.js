(function () {
  "use strict";
  var input = document.getElementById("article-library-search");
  var sections = Array.prototype.slice.call(document.querySelectorAll(".library-section, .guide-group"));
  if (!input || !sections.length) return;
  var status = document.getElementById("library-search-status");

  sections.forEach(function (section) {
    var cards = Array.prototype.slice.call(section.querySelectorAll(".card, .guide-card"));
    section.dataset.expanded = "false";
    if (cards.length > 4) {
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
      var cards = Array.prototype.slice.call(section.querySelectorAll(".card, .guide-card"));
      var sectionMatches = 0;
      cards.forEach(function (card, index) {
        var matches = !query || card.textContent.toLowerCase().indexOf(query) !== -1;
        var withinLimit = section.dataset.expanded === "true" || index < 4;
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
      status.textContent = query ? (total ? total + " matching guides" : "No guides match that search. Try a broader word.") : "Showing a curated selection from each topic.";
      status.classList.toggle("library-empty", !!query && total === 0);
    }
  }
  input.addEventListener("input", function () { apply(input.value); });
  apply("");
})();
