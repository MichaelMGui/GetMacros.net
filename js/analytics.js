/* Public-content measurement, release 2026-10-23.2. Never reads food logs or form values. */
(() => {
  'use strict';
  if (window.__getMacrosAnalyticsLoaded) return;
  window.__getMacrosAnalyticsLoaded = true;
  const id = 'G-MWXSWP6ZGY';
  const key = 'gm-analytics-consent-v1';
  const disable = 'ga-disable-' + id;
  let started = false;
  let settings = { choice: 'unknown', excluded: false };
  try {
    const stored = JSON.parse(localStorage.getItem(key));
    if (stored && ['granted', 'denied'].includes(stored.choice)) {
      settings = { choice: stored.choice, excluded: stored.excluded === true };
    }
  } catch (_) { /* Unavailable storage never implies permission. */ }

  const publicPage = document.body.dataset.analyticsPage === 'public';
  const production = location.hostname === 'getmacros.net';
  // Search/filter URLs and fragments can contain private or user-entered text.
  // Measure only the clean published URL, rather than trying to guess its contents.
  const cleanURL = !location.search && !location.hash;
  const automated = navigator.webdriver === true;
  const privacySignal = navigator.globalPrivacyControl === true;
  const eligible = publicPage && production && cleanURL && !automated && !privacySignal;
  const banner = document.querySelector('[data-analytics-notice]');
  const dialog = document.querySelector('#analytics-preferences');
  const status = document.querySelector('[data-analytics-status]');
  const exclusion = document.querySelector('[data-analytics-exclude]');
  const error = document.querySelector('[data-analytics-error]');

  function clearCookies() {
    for (const cookie of document.cookie.split(';')) {
      const name = cookie.split('=')[0].trim();
      if (!/^_ga(?:_|$)/.test(name)) continue;
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
    const gtag = function () { window.dataLayer.push(arguments); };
    // Basic consent: this function and the remote loader run only AFTER opt-in.
    gtag('consent', 'default', {
      analytics_storage: 'denied', ad_storage: 'denied',
      ad_user_data: 'denied', ad_personalization: 'denied'
    });
    gtag('consent', 'update', { analytics_storage: 'granted' });
    gtag('js', new Date());
    const canonical = document.querySelector('link[rel="canonical"]');
    const url = new URL(canonical ? canonical.href : location.pathname, location.origin);
    const page = 'https://getmacros.net' + url.pathname;
    let referrer = '';
    try { referrer = new URL(document.referrer).origin + '/'; } catch (_) {}
    const title = document.querySelector('meta[property="og:title"]');
    const safe = {
      page_location: page, page_referrer: referrer, page_title: title ? title.content : document.title,
      allow_google_signals: false, allow_ad_personalization_signals: false
    };
    gtag('set', safe);
    gtag('config', id, Object.assign({}, safe, {
      send_page_view: false, cookie_expires: 7776000, cookie_flags: 'SameSite=Lax;Secure'
    }));
    gtag('event', 'page_view', Object.assign({ send_to: id }, safe));
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + id;
    script.referrerPolicy = 'no-referrer';
    script.dataset.getmacrosAnalytics = '';
    document.head.append(script);
  }

  function refresh() {
    if (banner) banner.hidden = settings.choice !== 'unknown' || !eligible || settings.excluded;
    if (exclusion) exclusion.checked = settings.excluded;
    if (status) status.textContent = settings.excluded ? 'This browser is excluded.' :
      settings.choice === 'granted' ? 'Analytics allowed on public pages.' : 'Analytics is off.';
  }

  function choose(choice, excluded = settings.excluded) {
    const next = { choice, excluded };
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
    const stop = started && (choice !== 'granted' || excluded);
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
    button.addEventListener('click', () => choose(button.dataset.analyticsChoice, exclusion ? exclusion.checked : settings.excluded));
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
    settings = next && ['granted', 'denied'].includes(next.choice) ?
      { choice: next.choice, excluded: next.excluded === true } : { choice: 'unknown', excluded: false };
    if (started && (settings.choice !== 'granted' || settings.excluded)) {
      window[disable] = true; clearCookies(); location.reload();
    } else { refresh(); start(); }
  });
  refresh();
  start();
})();
