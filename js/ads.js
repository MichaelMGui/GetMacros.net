/* AdSense-ready ad bootstrap.
 *
 * Intentionally does not inject third-party banners, iframes, sticky rails,
 * pop-ups, or corner units. Google ads must remain clearly associated with
 * substantial publisher content and must not interfere with navigation.
 *
 * Existing .adsbygoogle units in page templates activate only after the real
 * publisher and slot IDs replace their placeholders.
 */
(function () {
  'use strict';

  function hasRealId(value) {
    return Boolean(value && !/X{4,}|0{6,}/.test(value));
  }

  function initAdSenseUnits() {
    var units = document.querySelectorAll('ins.adsbygoogle');
    units.forEach(function (unit) {
      var client = unit.getAttribute('data-ad-client') || '';
      var slot = unit.getAttribute('data-ad-slot') || '';
      var wrapper = unit.closest('.ad-slot');

      if (!hasRealId(client) || !hasRealId(slot)) {
        if (wrapper) wrapper.hidden = true;
        return;
      }

      try {
        (window.adsbygoogle = window.adsbygoogle || []).push({});
      } catch (error) {
        if (wrapper) wrapper.hidden = true;
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAdSenseUnits);
  } else {
    initAdSenseUnits();
  }
})();
