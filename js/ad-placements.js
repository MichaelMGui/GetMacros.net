/* Disabled by default. An authorized provider adapter must return a DOM element.
 * No provider script or data request occurs until explicit granted consent.
 */
(function(){'use strict';let config={enabled:false,consent:'unknown',adapter:null,timeout:5000};let generation=0;
function collapse(host){host.replaceChildren();host.hidden=true;host.removeAttribute('data-ad-state');}
async function render(host,version){collapse(host);if(!config.enabled||config.consent!=='granted'||typeof config.adapter!=='function')return;
host.hidden=false;host.dataset.adState='loading';const label=document.createElement('p');label.textContent='Advertisement';label.className='ad-label';const space=document.createElement('div');space.className='ad-space';host.append(label,space);
let timer;try{const response=await Promise.race([config.adapter({placement:host.dataset.adPlacement}),new Promise(resolve=>timer=setTimeout(()=>resolve(null),config.timeout))]);if(version!==generation)return;if(!response||!(response instanceof HTMLElement)){collapse(host);return;}space.append(response);host.dataset.adState='filled';}catch{if(version===generation)collapse(host);}finally{clearTimeout(timer);}}
window.GetMacrosAdvertising={configure(next){config={...config,...next};generation++;document.querySelectorAll('[data-ad-placement]').forEach(h=>render(h,generation));},disable(){this.configure({enabled:false});}};
document.querySelectorAll('[data-ad-placement]').forEach(collapse);
})();
