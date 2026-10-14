/* Optional scoped enhancement: never needed to read media or operate games. */
(()=>{'use strict';const calm=()=>document.documentElement.dataset.motion==='calm'||matchMedia('(prefers-reduced-motion: reduce)').matches;
document.addEventListener('getmacros:game-completed',e=>{const scope=e.target.closest('.play-workspace');if(!scope)return;window.GetMacrosCharacters?.enhance(scope);if(!calm())window.GetMacrosCharacters?.respond('complete',scope);});
})();
