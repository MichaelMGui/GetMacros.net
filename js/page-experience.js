/* A small, keyboard-accessible shortcut on long pages. */
(() => {
  const button=document.createElement('button');
  button.type='button';button.className='back-to-top';button.hidden=false;
  button.setAttribute('aria-label','Back to the top');
  button.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m5 12 7-7 7 7M12 5v15"/></svg><span>Top</span>';
  const footer=document.querySelector('footer .footer-bottom') || document.querySelector('footer');
  if(footer)footer.append(button);
  button.addEventListener('click',()=>{
    const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches||document.documentElement.classList.contains('tide-motion-off');
    window.scrollTo({top:0,behavior:reduced?'auto':'smooth'});
    const target=document.querySelector('main h1');
    if(target){target.tabIndex=-1;target.focus({preventScroll:true});}
  });

  // Navigation uses the browser's immediate paint and back/forward cache.
  // Do not fade an entire page or keep an outgoing screenshot on screen.
  document.documentElement.classList.remove('page-leaving');
  addEventListener('pageshow',event=>{if(event.persisted)document.documentElement.classList.remove('page-leaving');});
})();
