(function () {
  var A = window.ADSTERRA;
  if (!A) return;

  function renderFrame(container, unit) {
    var iframe = document.createElement('iframe');
    iframe.title = 'Advertisement';
    iframe.loading = 'lazy';
    iframe.style.border = '0';
    iframe.style.width = unit.width + 'px';
    iframe.style.height = unit.height + 'px';
    iframe.src = 'ad-frame.html?key=' + encodeURIComponent(unit.key) + '&w=' + unit.width + '&h=' + unit.height;
    container.appendChild(iframe);
  }

  function makeSlot(unit, opts) {
    opts = opts || {};
    var section = document.createElement(opts.tag || 'div');
    section.className = 'ad-slot' + (opts.extraClass ? ' ' + opts.extraClass : '');
    var inner = document.createElement('div');
    inner.className = 'container';
    var label = document.createElement('p');
    label.className = 'ad-label';
    label.textContent = 'Advertisement';
    inner.appendChild(label);
    var frameWrap = document.createElement('div');
    renderFrame(frameWrap, unit);
    inner.appendChild(frameWrap);
    section.appendChild(inner);
    return section;
  }

  function isMobile() {
    return window.matchMedia('(max-width: 600px)').matches;
  }

  function injectTopBanner() {
    var main = document.querySelector('main');
    if (!main) return;
    var unit = isMobile() ? A.banner320x50 : A.banner728x90;
    var slot = makeSlot(unit, { tag: 'section', extraClass: 'tight' });
    main.parentNode.insertBefore(slot, main);
  }

  function injectInContentBanner() {
    var main = document.querySelector('main');
    if (!main) return;
    var headings = main.querySelectorAll('h2');
    if (headings.length < 2) return;
    var target = headings[1];
    var section = target.closest('section') || target.parentNode;
    var slot = makeSlot(A.banner300x250, { tag: 'section', extraClass: 'tight' });
    section.parentNode.insertBefore(slot, section.nextSibling);
  }

  function injectPreFooterBanner() {
    var footer = document.querySelector('.site-footer');
    if (!footer) return;
    var slot = makeSlot(A.banner468x60, { tag: 'section', extraClass: 'tight' });
    footer.parentNode.insertBefore(slot, footer);
  }

  function injectCornerRail() {
    if (isMobile()) return;
    if (sessionStorage.getItem('gm-corner-ad-dismissed')) return;
    var wrap = document.createElement('div');
    wrap.className = 'ad-corner-rail';
    var closeBtn = document.createElement('button');
    closeBtn.setAttribute('aria-label', 'Close ad');
    closeBtn.textContent = '✕';
    closeBtn.className = 'ad-corner-close';
    closeBtn.addEventListener('click', function () {
      wrap.remove();
      sessionStorage.setItem('gm-corner-ad-dismissed', '1');
    });
    var label = document.createElement('p');
    label.className = 'ad-label';
    label.textContent = 'Advertisement';
    var frameWrap = document.createElement('div');
    renderFrame(frameWrap, A.banner160x300);
    wrap.appendChild(closeBtn);
    wrap.appendChild(label);
    wrap.appendChild(frameWrap);
    document.body.appendChild(wrap);
  }

  function injectSideRail() {
    if (window.innerWidth < 1500) return;
    var wrap = document.createElement('div');
    wrap.className = 'ad-side-rail';
    var frameWrap = document.createElement('div');
    renderFrame(frameWrap, A.banner160x600);
    wrap.appendChild(frameWrap);
    document.body.appendChild(wrap);
  }

  function init() {
    injectTopBanner();
    injectInContentBanner();
    injectPreFooterBanner();
    injectCornerRail();
    injectSideRail();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
