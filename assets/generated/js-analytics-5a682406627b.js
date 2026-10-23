/* Consented public-page visits and safe destination clicks. No food/form values. */
(() => {
  'use strict';
  if (window.__getMacrosAnalyticsLoaded) return;
  window.__getMacrosAnalyticsLoaded = true;
  const id = 'G-MWXSWP6ZGY';
  const key = 'gm-analytics-consent-v1';
  const disable = 'ga-disable-' + id;
  let started = false;
  let loaded = false;
  let blocked = false;
  let send;
  let settings = { choice: 'unknown', excluded: false, diagnostic: false };
  try {
    const stored = JSON.parse(localStorage.getItem(key));
    if (stored && ['granted', 'denied'].includes(stored.choice)) {
      settings = { choice: stored.choice, excluded: stored.excluded === true, diagnostic: stored.diagnostic === true };
    }
  } catch (_) { /* Unavailable storage never implies permission. */ }

  const publicPage = document.body.dataset.analyticsPage === 'public';
  const production = location.hostname === 'getmacros.net';
  // Parameters and fragments are never sent. A normal market or campaign link
  // must not lose its entire visit simply because the address contains one.
  const automated = navigator.webdriver === true;
  const privacySignal = navigator.globalPrivacyControl === true;
  const eligible = publicPage && production && !automated && !privacySignal;
  const banner = document.querySelector('[data-analytics-notice]');
  const dialog = document.querySelector('#analytics-preferences');
  const status = document.querySelector('[data-analytics-status]');
  const exclusion = document.querySelector('[data-analytics-exclude]');
  const diagnostic = document.querySelector('[data-analytics-diagnostic]');
  const error = document.querySelector('[data-analytics-error]');

  function clearCookies() {
    for (const cookie of document.cookie.split(';')) {
      const name = cookie.split('=')[0].trim();
      if (!/^(?:_ga(?:_|$)|gm_qa_ga(?:_|$))/.test(name)) continue;
      for (const domain of ['', ';domain=getmacros.net', ';domain=.getmacros.net']) {
        document.cookie = name + '=; Max-Age=0; path=/' + domain + '; SameSite=Lax; Secure';
      }
    }
  }

  function start() {
    if (started || !eligible || settings.choice !== 'granted' || settings.excluded) return;
    started = true;
    window[disable] = false;
    window.dataLayer = window.dataLayer || [];
    const gtag = window.gtag = function () { window.dataLayer.push(arguments); };
    // The tag does not exist before permission. Initialize it with the actual
    // affirmative analytics choice, while keeping every advertising purpose off.
    gtag('consent', 'default', {
      analytics_storage: 'granted', ad_storage: 'denied',
      ad_user_data: 'denied', ad_personalization: 'denied'
    });
    gtag('js', new Date());
    const canonical = document.querySelector('link[rel="canonical"]');
    const url = new URL(canonical ? canonical.href : location.pathname, location.origin);
    const page = 'https://getmacros.net' + url.pathname;
    let referrer = '';
    try { referrer = new URL(document.referrer).origin + '/'; } catch (_) {}
    const title = document.querySelector('meta[property="og:title"]');
    const safe = {
      page_location: page, page_referrer: referrer,
      page_title: (settings.diagnostic ? '[Diagnostic] ' : '') + (title ? title.content : document.title),
      gm_traffic_class: settings.diagnostic ? 'diagnostic' : 'standard',
      allow_google_signals: false, allow_ad_personalization_signals: false
    };
    const testing = settings.diagnostic ? { debug_mode: true, traffic_type: 'internal', cookie_prefix: 'gm_qa' } : {};
    gtag('set', safe);
    gtag('config', id, Object.assign({}, safe, testing, {
      send_page_view: false, cookie_expires: 7776000, cookie_flags: 'SameSite=Lax;Secure'
    }));
    send = (name, details = {}) => {
      if (settings.choice !== 'granted' || settings.excluded || window[disable]) return;
      gtag('event', name, Object.assign({ send_to: id }, safe,
        settings.diagnostic ? { debug_mode: true, traffic_type: 'internal' } : {}, details));
    };
    send('page_view');
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + id;
    script.referrerPolicy = 'no-referrer';
    script.dataset.getmacrosAnalytics = '';
    script.onload = () => { loaded = true; refresh(); };
    script.onerror = () => { blocked = true; refresh(); };
    document.head.append(script);
  }

  function refresh() {
    if (banner) banner.hidden = settings.choice !== 'unknown' || !eligible || settings.excluded;
    if (exclusion) exclusion.checked = settings.excluded;
    if (diagnostic) diagnostic.checked = settings.diagnostic;
    if (status) status.textContent = settings.excluded ? 'This browser is excluded.' :
      !publicPage ? 'Analytics is off on this private tool.' :
      !production ? 'Analytics is off on previews.' :
      automated ? 'Automated browsers are excluded.' :
      privacySignal ? 'Your browser privacy signal keeps analytics off.' :
      settings.choice !== 'granted' ? 'Analytics is off.' :
      blocked ? 'Your browser blocked the analytics tag.' :
      !loaded ? 'Analytics allowed. Connecting to Google…' :
      settings.diagnostic ? 'Tag loaded. This browser is labeled Diagnostic, not audience traffic.' :
      'Analytics tag loaded for public-page visits.';
  }

  function choose(choice, excluded = settings.excluded, diagnosticMode = settings.diagnostic) {
    const next = { choice, excluded, diagnostic: diagnosticMode };
    try {
      localStorage.setItem(key, JSON.stringify(next));
      if (localStorage.getItem(key) !== JSON.stringify(next)) throw new Error('Storage unavailable');
    } catch (_) {
      if (error) error.textContent = 'Your browser could not save this choice. Analytics stays off.';
      window[disable] = true;
      if (started) { clearCookies(); location.reload(); }
      else if (dialog && !dialog.open) dialog.showModal();
      return;
    }
    const stop = started && (choice !== 'granted' || excluded || diagnosticMode !== settings.diagnostic);
    settings = next;
    refresh();
    if (stop) {
      // Do not send a consent-denied ping. Stop, clear this site's GA cookies,
      // then unload the previously permitted tag and its listeners.
      window[disable] = true;
      clearCookies();
      location.reload();
      return;
    }
    if (choice === 'denied' || excluded) { window[disable] = true; clearCookies(); }
    start();
    if (dialog && dialog.open) dialog.close();
  }

  document.querySelectorAll('[data-analytics-choice]').forEach(button => {
    button.addEventListener('click', () => choose(button.dataset.analyticsChoice,
      exclusion ? exclusion.checked : settings.excluded, diagnostic ? diagnostic.checked : settings.diagnostic));
  });
  document.querySelectorAll('[data-analytics-preferences]').forEach(button => {
    button.addEventListener('click', () => { refresh(); if (dialog) dialog.showModal(); });
  });
  if (dialog) {
    dialog.querySelector('[data-analytics-close]').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => {
      const rect = dialog.getBoundingClientRect();
      if (event.target === dialog && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) dialog.close();
    });
  }
  // Revoking in another tab also stops this document's previously loaded tag.
  window.addEventListener('storage', event => {
    if (event.key !== key) return;
    let next;
    try { next = JSON.parse(event.newValue); } catch (_) {}
    const previousDiagnostic = settings.diagnostic;
    settings = next && ['granted', 'denied'].includes(next.choice) ?
      { choice: next.choice, excluded: next.excluded === true, diagnostic: next.diagnostic === true } : { choice: 'unknown', excluded: false, diagnostic: false };
    if (started && (settings.choice !== 'granted' || settings.excluded || settings.diagnostic !== previousDiagnostic)) {
      window[disable] = true; clearCookies(); location.reload();
    } else { refresh(); start(); }
  });
  document.addEventListener('click', event => {
    if (!send || !event.isTrusted || event.button !== 0) return;
    const link = event.target.closest('a[href]');
    if (!link) return;
    let target;
    try { target = new URL(link.href, location.origin); } catch (_) { return; }
    if (!['https:', 'http:'].includes(target.protocol)) return;
    const external = target.origin !== location.origin;
    if (!external && target.pathname === location.pathname) return;
    // Enum destinations only: never forward a link's text, query, hash or
    // selected food/restaurant/health preference from the destination URL.
    const destination = external ? 'external' :
      /find-a-meal|restaurant-meal-finder/.test(target.pathname) ? 'finder' :
      /calculators|calculator|recipe-macro-scaler|comparison-tool|portion-tool/.test(target.pathname) ? 'calculator' :
      /food-diary/.test(target.pathname) ? 'diary' :
      /food-library|food-shelf/.test(target.pathname) ? 'food_library' :
      /compare-|complete-order|drink-comparison/.test(target.pathname) ? 'comparison' :
      /play/.test(target.pathname) ? 'play' :
      /restaurants\/|restaurant-meal-guides|world-restaurant/.test(target.pathname) ? 'restaurants' :
      target.pathname === '/' || /^\/[a-z]{2}\/en\/$/.test(target.pathname) ? 'home' : 'content';
    const area = link.closest('header') ? 'header' : link.closest('footer') ? 'footer' : 'content';
    send(external ? 'outbound_click' : 'navigation_click', { destination, link_area: area });
  });
  refresh();
  start();
})();
