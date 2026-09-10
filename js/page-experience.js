/* A small, keyboard-accessible shortcut on long pages. */
(() => {
  const button=document.createElement('button');
  button.type='button';button.className='back-to-top';button.hidden=true;
  button.setAttribute('aria-label','Back to the top');
  button.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m5 12 7-7 7 7M12 5v15"/></svg><span>Top</span>';
  document.body.append(button);
  let queued=false;
  function update(){queued=false;button.hidden=scrollY<innerHeight*.8 || document.body.classList.contains('nav-open');}
  addEventListener('scroll',()=>{if(!queued){queued=true;requestAnimationFrame(update);}},{passive:true});
  button.addEventListener('click',()=>{
    const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches||document.documentElement.classList.contains('tide-motion-off');
    window.scrollTo({top:0,behavior:reduced?'auto':'smooth'});
    const target=document.querySelector('main h1');
    if(target){target.tabIndex=-1;target.focus({preventScroll:true});}
  });
  update();

  // Native transitions never postpone navigation. Older browsers receive one
  // short arrival fade at DOM readiness, rather than waiting for ads/images.
  const nativePages='onpagereveal' in window && 'onpageswap' in window;
  const motionAllowed=()=>!matchMedia('(prefers-reduced-motion: reduce)').matches&&!document.documentElement.classList.contains('tide-motion-off');
  function arrive(){
    document.documentElement.classList.remove('page-leaving');
    const main=document.querySelector('main');
    // A slow script must never fade content the reader has already been using.
    const firstPaint=performance.getEntriesByName('first-contentful-paint')[0];
    if(performance.now()>500 || (firstPaint && performance.now()-firstPaint.startTime>100))return;
    if(!nativePages&&motionAllowed()&&main?.animate)main.animate([{opacity:.7},{opacity:1}],{duration:240,easing:'cubic-bezier(.16,1,.3,1)'});
  }
  arrive();
  addEventListener('pageshow',event=>{if(event.persisted)document.documentElement.classList.remove('page-leaving');});
})();
