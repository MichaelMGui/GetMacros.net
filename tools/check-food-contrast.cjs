// Semantic token pairs only; not an audit of every rendered pixel or WCAG certification.
const fs=require('node:fs'),assert=require('node:assert/strict');
const css=fs.readFileSync('tools/food-design.css','utf8');
const vars=s=>Object.fromEntries([...s.matchAll(/--([\w-]+):(#\w{6})/g)].map(m=>[m[1],m[2]]));
const day=vars(css.match(/:root\{([^}]+)/)[1]),night={...day,...vars(css.match(/html\[data-theme=dark\]\{([^}]+)/)[1])};
function luminance(hex){return hex.slice(1).match(/../g).map(v=>parseInt(v,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((n,v,i)=>n+v*[.2126,.7152,.0722][i],0);}
function contrast(a,b){const x=luminance(a),y=luminance(b);return(Math.max(x,y)+.05)/(Math.min(x,y)+.05);}
const report=[];
for(const [theme,t]of Object.entries({light:day,dark:night})){
 for(const background of ['bg','surface','soft'])for(const foreground of ['ink','muted','green','error','warning']){const ratio=contrast(t[foreground],t[background]);report.push({theme,foreground,background,ratio:Number(ratio.toFixed(2)),minimum:4.5});assert.ok(ratio>=4.5,`${theme} ${foreground}/${background}: ${ratio}`);}
 for(const [foreground,background,minimum]of [['on-green','green',4.5],['ink','highlight',4.5],['error','error-bg',4.5],['control-border','surface',3],['control-border','bg',3],['focus','bg',3],['focus','surface',3]]){const ratio=contrast(t[foreground],t[background]);report.push({theme,foreground,background,ratio:Number(ratio.toFixed(2)),minimum});assert.ok(ratio>=minimum,`${theme} ${foreground}/${background}: ${ratio}`);}
}
fs.writeFileSync('docs/food-reset-2026-10-03/contrast-tokens.json',JSON.stringify(report,null,2));console.log('PASS 44 semantic text/action/focus/control token pairs in both themes.');
