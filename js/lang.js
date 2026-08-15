/* Language switcher behaviour.
 *
 * Only some pages are available in Spanish and French. TRANSLATED lists, per
 * locale, the page filenames that actually exist under /es/ and /fr/, so the
 * switcher can link to the real translation of the current page instead of
 * dropping every visitor on the localized homepage.
 *
 * Where a translation does not exist the locale is shown as unavailable rather
 * than silently navigating somewhere unrelated, and the chosen language is
 * remembered so later visits to a page that *is* translated open in it.
 */
(function () {
  "use strict";

  var TRANSLATED = {
    es: ["index.html"],
    fr: ["index.html"]
  };

  var STORE = "gm-lang";
  var LABEL = {
    en: { name: "English", none: "This page is not available in English yet" },
    es: { name: "Espanol", none: "Esta pagina aun no esta disponible en espanol" },
    fr: { name: "Francais", none: "Cette page n'est pas encore disponible en francais" }
  };

  function readPref() {
    try { return localStorage.getItem(STORE); } catch (e) { return null; }
  }
  function writePref(v) {
    try { localStorage.setItem(STORE, v); } catch (e) { /* private mode */ }
  }

  // Where are we, and in which language?
  var path = location.pathname.replace(/\/$/, "/index.html");
  var parts = path.split("/").filter(Boolean);
  var last = parts[parts.length - 1] || "index.html";
  var maybeLocale = parts.length > 1 ? parts[parts.length - 2] : "";
  var current = (maybeLocale === "es" || maybeLocale === "fr") ? maybeLocale : "en";
  var page = last.indexOf(".html") === -1 ? "index.html" : last;
  var root = current === "en" ? "" : "../";

  function hasTranslation(loc, name) {
    return loc === "en" || (TRANSLATED[loc] || []).indexOf(name) !== -1;
  }

  function urlFor(loc, name) {
    if (loc === "en") return root + name;
    return root + loc + "/" + name;
  }

  var box = document.querySelector(".lang-switch");
  if (box) {
    var links = box.querySelectorAll("a");
    Array.prototype.forEach.call(links, function (a) {
      var loc = (a.textContent || "").trim().toLowerCase();
      if (loc !== "en" && loc !== "es" && loc !== "fr") return;

      if (loc === current) {
        a.setAttribute("aria-current", "page");
        a.removeAttribute("href");
        a.classList.remove("unavailable");
        a.title = LABEL[loc].name;
        return;
      }

      a.removeAttribute("aria-current");

      if (hasTranslation(loc, page)) {
        // Same page, other language.
        a.href = urlFor(loc, page);
        a.classList.remove("unavailable");
        a.title = LABEL[loc].name;
        a.removeAttribute("aria-disabled");
        a.addEventListener("click", function () { writePref(loc); });
      } else {
        // No translation of this page: say so instead of navigating away.
        a.removeAttribute("href");
        a.classList.add("unavailable");
        a.setAttribute("aria-disabled", "true");
        a.title = LABEL[loc].none;
      }
    });
  }

  if (current !== "en") writePref(current);

  // Keep the remembered language when the visitor heads back to the homepage.
  var pref = readPref();
  if (pref && pref !== "en" && hasTranslation(pref, "index.html")) {
    var homeSelector = 'a[href="' + root + 'index.html"], a[href="index.html"], a[href="../index.html"]';
    Array.prototype.forEach.call(document.querySelectorAll(homeSelector), function (a) {
      if (a.closest(".lang-switch")) return;
      a.href = urlFor(pref, "index.html");
    });
  }
})();
