// Must load in <head> (not deferred) so this function exists before any
// <img onerror="imgFallback(this)"> in the body can possibly fail to load.
function imgFallback(img) {
  if (img.dataset.fallenBack) return;
  img.dataset.fallenBack = "1";
  var icon = img.getAttribute("data-icon") || "📷";
  var label = img.alt || "Photo coming soon";
  var wrap = document.createElement("div");
  wrap.className = "photo-fallback";
  wrap.setAttribute("role", "img");
  wrap.setAttribute("aria-label", label);
  wrap.innerHTML =
    '<span class="ph-icon" aria-hidden="true">' + icon + "</span>" +
    '<span class="ph-label">' + label + "</span>" +
    '<span class="ph-note">Photo pending &mdash; see images/README.md</span>';
  img.replaceWith(wrap);
}
