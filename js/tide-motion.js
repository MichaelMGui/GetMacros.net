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

  // One observer, compositor-only movement, no per-frame layout measurements.
  // The page is readable before JS loads and when a fast swipe outruns effects.
  const cards='.home-launch-card,.home-reading-card,.home-everyday-tool,.guide-card,.blog-card,.tool-card,.clear-tool-card,.clear-about-grid article,.protein-food-card,.search-start-tile,.pick-card,.answer-box,.evidence-card,.meal-idea';
  if ('IntersectionObserver' in window) {
    const initialized=new WeakSet();
    const observer=new IntersectionObserver(entries=>{
      entries.forEach(entry=>{
        const target=entry.target,rect=entry.boundingClientRect;
        const first=!initialized.has(target);initialized.add(target);
        if(first&&rect.top<innerHeight){observer.unobserve(target);return;}
        if(!entry.isIntersecting)return;
        observer.unobserve(target);
        if(!active||rect.bottom<=0||running.size>=4||target.closest('form,[aria-live],#meal-quiz,details:not([open])'))return;
        play(target,[{opacity:.72,translate:'0 6px'},{opacity:1,translate:'0 0'}],
          {duration:220,easing:'cubic-bezier(.2,.7,.3,1)'});
      });
    },{threshold:0,rootMargin:'0px 0px 64px 0px'});
    document.querySelectorAll('main h2,'+cards).forEach(target=>{
      if(!target.parentElement.closest(cards))observer.observe(target);
    });
  }

  // Delegation also reaches quiz and comparison buttons rendered after startup.
  function ripple(event) {
    const button=event.target.closest('.btn,.quiz-continue,.meal-save,[data-compare-pick]');
    if(!button||!active)return;
    button.classList.add('tide-ripple-host');
    const box=button.getBoundingClientRect(),ripple=document.createElement('span');
    ripple.className='tide-ripple';ripple.setAttribute('aria-hidden','true');
    ripple.style.left=event.clientX-box.left+'px';ripple.style.top=event.clientY-box.top+'px';
    const size=Math.hypot(box.width,box.height)*2;ripple.style.width=size+'px';ripple.style.height=size+'px';button.append(ripple);
    play(ripple,[{scale:'0',opacity:.18},{scale:'1',opacity:0}],{duration:380,easing:'ease-out'});
    setTimeout(()=>ripple.remove(),450);
  }
  let touchStart;
  document.addEventListener?.('pointerdown',event=>{
    if(event.pointerType==='mouse'){if(fine.matches)ripple(event);return;}
    touchStart={id:event.pointerId,x:event.clientX,y:event.clientY,target:event.target};
  },{passive:true});
  document.addEventListener?.('pointerup',event=>{
    if(touchStart&&event.pointerId===touchStart.id&&event.target===touchStart.target&&Math.hypot(event.clientX-touchStart.x,event.clientY-touchStart.y)<10)ripple(event);
    touchStart=null;
  },{passive:true});
  document.addEventListener?.('pointermove',event=>{
    if(touchStart&&event.pointerId===touchStart.id&&Math.hypot(event.clientX-touchStart.x,event.clientY-touchStart.y)>=10)touchStart=null;
  },{passive:true});
  document.addEventListener?.('pointercancel',()=>{touchStart=null;},{passive:true});
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
