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
    active = !paused && !preference.matches && !document.hidden;
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
  document.addEventListener?.('visibilitychange', sync);
  sync();

  // Observe content below the initial viewport. Nothing is hidden in CSS or
  // left waiting for JavaScript; each reveal ends at the original layout.
  const cards='.home-launch-card,.blog-card,.guide-card,.tool-card,.chain-card,.home-everyday-tool,.clear-tool-card,.clear-about-grid article,.protein-food-card,.search-start-tile,.pick-card,.answer-box,.evidence-card,.meal-idea';
  const targets=document.querySelectorAll('main h2');
  if ('IntersectionObserver' in window) {
    const observer=new IntersectionObserver(entries=>{
      entries.forEach(entry=>{
        if(!entry.isIntersecting)return;
        observer.unobserve(entry.target);
        const target=entry.target;
        if(!active||target.closest('form,[aria-live],#meal-quiz,details:not([open])'))return;
        // A fast scroll should never make already-passed content animate.
        if(entry.boundingClientRect && entry.boundingClientRect.bottom<=0)return;
        // Keep every word readable throughout. Only section headings move;
        // paragraphs and entire card grids no longer repaint on each scroll.
        play(target,[{translate:'0 5px',opacity:1},{translate:'0 0',opacity:1}],
          {duration:160,easing:'ease-out'});
      });
    },{threshold:.08,rootMargin:'0px 0px -24px 0px'});
    targets.forEach(target=>{
      if(target.getBoundingClientRect().top>=innerHeight && !target.parentElement.closest(cards))observer.observe(target);
    });
  }

  // Delegation also reaches quiz and comparison buttons rendered after startup.
  document.addEventListener?.('pointerdown', event => {
    const button=event.target.closest('.btn,.quiz-continue,.meal-save,[data-compare-pick]');
    if(!button||!active)return;
    button.classList.add('tide-ripple-host');
    const box=button.getBoundingClientRect(),ripple=document.createElement('span');
    ripple.className='tide-ripple';ripple.setAttribute('aria-hidden','true');
    ripple.style.left=event.clientX-box.left+'px';ripple.style.top=event.clientY-box.top+'px';
    const size=Math.hypot(box.width,box.height)*2;ripple.style.width=size+'px';ripple.style.height=size+'px';button.append(ripple);
    play(ripple,[{scale:'0',opacity:.18},{scale:'1',opacity:0}],{duration:380,easing:'ease-out'});
    setTimeout(()=>ripple.remove(),450);
  });
  document.addEventListener?.('pointerover',event=>{
    if(!fine.matches||!active)return;
    const icon=event.target.closest('.page-emblem,.learning-icon,.option-icon,.how-step-number');
    if(icon&&!icon.contains(event.relatedTarget))play(icon,[{rotate:'0deg'},{rotate:'-7deg',offset:.35},{rotate:'4deg',offset:.65},{rotate:'0deg'}],{duration:360,easing:'ease-out'});
  });
  document.addEventListener?.('toggle',event=>{
    const panel=event.target;
    if(panel.tagName!=='DETAILS'||!panel.open||!panel.closest('main,footer')||panel.closest('#meal-quiz'))return;
    Array.from(panel.children).filter(child=>child.tagName!=='SUMMARY').forEach(child=>play(child,[{opacity:.75,translate:'0 4px'},{opacity:1,translate:'0 0'}],{duration:180,easing:'ease-out'}));
  },true);
})();
