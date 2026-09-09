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
})();
