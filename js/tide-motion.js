/* Progressive enhancement: content is always visible before motion starts. */
(() => {
  'use strict';
  const root = document.documentElement;
  const preference = matchMedia('(prefers-reduced-motion: reduce)');
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  let paused = false;
  try { paused = localStorage.getItem('gm-motion') === 'paused'; } catch (_) {}
  let active = false;
  const running = new Set();
  const play = (element, frames, options) => {
    if (!active || !element.animate) return;
    const animation = element.animate(frames, options);
    running.add(animation);
    animation.finished.catch(() => {}).finally(() => running.delete(animation));
  };
  const control = document.createElement('button');
  control.type = 'button';
  control.className = 'tide-motion-toggle';
  const sync = () => {
    active = !paused && !preference.matches;
    root.classList.toggle('tide-motion-on', active);
    root.classList.toggle('tide-motion-off', !active);
    control.textContent = preference.matches ? 'Motion reduced by device' : paused ? 'Enable motion' : 'Pause motion';
    control.disabled = preference.matches;
    control.setAttribute('aria-pressed', String(paused || preference.matches));
    if (!active) { running.forEach(a => a.cancel()); running.clear(); }
  };
  control.addEventListener('click', () => {
    paused = !paused;
    try { localStorage.setItem('gm-motion', paused ? 'paused' : 'enabled'); } catch (_) {}
    sync();
  });
  (document.querySelector('footer .container') || document.querySelector('footer'))?.append(control);
  preference.addEventListener('change', sync);
  sync();

  // A quiet colour wash tracks progress without moving the document itself.
  let washQueued = false;
  const updateWash = () => {
    washQueued = false;
    if (!active) return;
    const length = Math.max(1, root.scrollHeight - innerHeight);
    const progress = Math.min(1, Math.max(0, scrollY / length));
    root.style.setProperty('--tide-wash-x', (12 + progress * 76).toFixed(1) + '%');
    root.style.setProperty('--tide-wash-y', (18 + progress * 54).toFixed(1) + '%');
    root.style.setProperty('--tide-progress', progress.toFixed(4));
  };
  addEventListener('scroll', () => {
    if (active && !washQueued) { washQueued = true; requestAnimationFrame(updateWash); }
  }, {passive:true});
  addEventListener('resize', updateWash, {passive:true});

  const hero = document.querySelector('.home-intro,.article-hero,.page-hero,.blog-hero,.focus-hero,.calc-hub-hero,.match-intro,.search-hero,.tool-hero');
  if (hero) {
    hero.classList.add('tide-motion-scene');
    const liquid = document.createElement('div');
    liquid.className = 'tide-liquid'; liquid.setAttribute('aria-hidden', 'true');
    liquid.innerHTML = '<i></i><i></i><i></i>';
    hero.prepend(liquid);
    let queued = false;
    const drift = () => {
      queued = false;
      if (!active) return;
      const box = hero.getBoundingClientRect();
      if (box.bottom < 0 || box.top > innerHeight) return;
      liquid.style.setProperty('--tide-drift', Math.min(65, Math.max(-65, -box.top * .13)) + 'px');
    };
    addEventListener('scroll', () => {
      if (active && !queued) { queued = true; requestAnimationFrame(drift); }
    }, { passive: true });
  }

  // One-time entrances, only after intersection; observer failure cannot hide text.
  const targets = document.querySelectorAll('main h1,main h2,.home-launch-card,.blog-card,.guide-card,.tool-card,.chain-card,.home-everyday-tool');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      let sequence = 0;
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        if (entry.target.closest('form,[aria-live],#meal-quiz')) return;
        const heading = /^H[12]$/.test(entry.target.tagName);
        play(entry.target, heading ? [
          { translate: '0 28px', opacity: .65 },
          { translate: '0 -2px', opacity: 1, offset: .78 },
          { translate: '0 0', opacity: 1 }
        ] : [
          { translate: '0 30px', rotate: '0.6deg', filter: 'blur(2px)' },
          { translate: '0 -3px', rotate: '-0.12deg', filter: 'blur(0)', offset: .76 },
          { translate: '0 0', rotate: '0deg', filter: 'blur(0)' }
        ], { duration: heading ? 950 : 780, delay: Math.min(sequence++ * 65, 195), easing: 'cubic-bezier(.2,.75,.2,1)' });
      });
    }, { threshold: .12 });
    targets.forEach(target => observer.observe(target));
  }

  document.querySelectorAll('.btn,.home-launch-card').forEach(button => {
    button.classList.add('tide-ripple-host');
    button.addEventListener('pointerdown', event => {
      if (!active) return;
      const box = button.getBoundingClientRect();
      const ripple = document.createElement('span');
      ripple.className = 'tide-ripple'; ripple.setAttribute('aria-hidden', 'true');
      ripple.style.left = event.clientX - box.left + 'px';
      ripple.style.top = event.clientY - box.top + 'px';
      button.append(ripple);
      const size = Math.hypot(box.width, box.height) * 2;
      play(ripple, [{ width: '0px', height: '0px', opacity: .3 }, { width: size + 'px', height: size + 'px', opacity: 0 }], { duration: 650, easing: 'ease-out' });
      setTimeout(() => ripple.remove(), 700);
    });
    button.addEventListener('pointerenter', () => {
      if (!fine.matches) return;
      play(button, [{ scale: '1' }, { scale: '1.025', offset: .55 }, { scale: '1' }], { duration: 480, easing: 'ease-out' });
    });
  });
})();
