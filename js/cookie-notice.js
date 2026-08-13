(function () {
  var KEY = 'gm-cookie-ack';
  if (localStorage.getItem(KEY)) return;

  function init() {
    var bar = document.createElement('div');
    bar.id = 'cookie-notice';
    bar.setAttribute('role', 'region');
    bar.setAttribute('aria-label', 'Cookie notice');
    bar.innerHTML =
      '<div class="cookie-notice-inner">' +
        '<p>This site uses cookies from ad partners (Google AdSense, Adsterra) to show ads and, where permitted, personalize them. See our <a href="/privacy.html">Privacy policy</a>.</p>' +
        '<div class="cookie-notice-actions">' +
          '<button type="button" class="btn btn-primary cookie-notice-ok">Got it</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(bar);
    requestAnimationFrame(function () { bar.classList.add('show'); });

    bar.querySelector('.cookie-notice-ok').addEventListener('click', function () {
      localStorage.setItem(KEY, '1');
      bar.classList.remove('show');
      setTimeout(function () { bar.remove(); }, 250);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
