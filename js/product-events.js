/* Provider-free product events. Never attach inputs, search text or identifiers. */
(function(){'use strict';const allowed=new Set(['finder_started','quiz_completed','filters_applied','meal_opened','comparison_used','calculator_completed','article_to_finder','share_action']);
window.GetMacrosEvents={emit(name){if(!allowed.has(name))return;document.dispatchEvent(new CustomEvent('getmacros:product-event',{detail:{name,version:1}}));}};
document.addEventListener('click',e=>{const a=e.target.closest('a');if(!a)return;if(a.closest('.meal-row'))GetMacrosEvents.emit('meal_opened');else if(document.querySelector('.article-container')&&a.getAttribute('href')?.startsWith('restaurant-meal-finder.html'))GetMacrosEvents.emit('article_to_finder');});
document.addEventListener('getmacros:calculator-completed',()=>GetMacrosEvents.emit('calculator_completed'));
})();
