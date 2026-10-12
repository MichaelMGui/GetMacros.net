// Must load in <head> (not deferred) so this function exists before any
// <img onerror="imgFallback(this)"> in the body can possibly fail to load.
// Maps each page's data-icon emoji shorthand to a sprite icon symbol id
// (see icon-sprite.svg, injected once per page right after <body>).
var IMG_FALLBACK_ICON_MAP = {
  "🍗": "icon-protein", "🥚": "icon-protein", "🥣": "icon-protein",
  "🫘": "icon-protein", "🫀": "icon-protein",
  "🐟": "icon-fat", "🥑": "icon-fat", "🥜": "icon-fat", "🫒": "icon-fat",
  "🌱": "icon-carbs", "🌾": "icon-carbs", "🍎": "icon-carbs", "🍚": "icon-carbs", "🥗": "icon-carbs",
  "🧪": "icon-molecule"
};

function imgFallback(img) {
  if (img.dataset.fallenBack) return;
  img.dataset.fallenBack = "1";
  var raw = img.getAttribute("data-icon") || "";
  var iconId = IMG_FALLBACK_ICON_MAP[raw] || "icon-article";
  var label = img.alt || "Photo coming soon";
  var wrap = document.createElement("div");
  wrap.className = "photo-fallback";
  wrap.setAttribute("role", "img");
  wrap.setAttribute("aria-label", label);
  wrap.innerHTML =
    '<span class="ph-icon" aria-hidden="true"><svg class="icon"><use href="#' + iconId + '"/></svg></span>' +
    '<span class="ph-label">' + label + "</span>" +
    '<span class="ph-note">Photo pending &mdash; see images/README.md</span>';
  img.replaceWith(wrap);
}
