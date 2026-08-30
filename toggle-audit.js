const { chromium } = require('playwright');
const fs = require('fs');
const pages = fs.readdirSync('/home/user/GetMacros.net').filter(f=>f.endsWith('.html')&&f!=='404.html').sort();
function lum(c){const [r,g,b]=c.map(v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)});return .2126*r+.7152*g+.0722*b;}
function ratio(a,b){const l1=lum(a),l2=lum(b);return (Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05);}
const MEASURE = () => {
  const out=[];
  const toRGB=s=>{const m=s.match(/\d+/g);return m?m.slice(0,3).map(Number):null;};
  function stops(img){const o=[];const re=/rgba?\(([^)]+)\)/g;let m;
    while((m=re.exec(img))){const a=m[1].split(',').map(parseFloat);if(a.length<4||a[3]>0.55)o.push(a.slice(0,3));}return o;}
  function bgsOf(el){let n=el;while(n&&n!==document.documentElement){const s=getComputedStyle(n);
    if(s.backgroundImage&&s.backgroundImage!=='none'){
      const lin=(s.backgroundImage.match(/(?:repeating-)?linear-gradient\([^;]*?\)(?=,\s*(?:repeating-)?(?:linear|radial|conic)-gradient|$)/g)||[]);
      const st=lin.length?stops(lin.join(' ')):[]; if(st.length)return st;}
    const m=s.backgroundColor.match(/rgba?\(([^)]+)\)/);
    if(m){const a=m[1].split(',').map(parseFloat);if(a.length<4||a[3]>0.5)return [a.slice(0,3)];}
    n=n.parentElement;}
    const bs=getComputedStyle(document.body).backgroundColor.match(/\d+/g);
    return [bs?bs.slice(0,3).map(Number):[255,255,255]];}
  const sel=el=>el.tagName.toLowerCase()+(typeof el.className==='string'&&el.className?'.'+el.className.trim().split(/\s+/)[0]:'');
  for (const el of document.querySelectorAll('body *')) {
    const s=getComputedStyle(el);
    if(s.display==='none'||s.visibility==='hidden'||+s.opacity===0)continue;
    if(el.closest('.sr-only,.visually-hidden'))continue;
    if(![...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim().length>2))continue;
    const fg=toRGB(s.color); if(!fg)continue;
    out.push({fg,bgs:bgsOf(el),size:parseFloat(s.fontSize),bold:+s.fontWeight>=700,sel:sel(el)});
  }
  return out;
};
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const bucket={};
  const add=(k,page)=>{(bucket[k]=bucket[k]||new Set()).add(page);};
  for (const start of ['light','dark']) {
    for (const f of pages) {
      const p = await b.newPage({ viewport: { width: 390, height: 844 } });
      await p.addInitScript(t=>{try{localStorage.setItem('gm-theme',t);}catch(e){}}, start);
      await p.goto('http://localhost:8899/'+f,{waitUntil:'load'}); await p.waitForTimeout(200);
      await p.evaluate(()=>document.querySelectorAll('details').forEach(d=>d.open=true));
      // Toggle the theme the way a person does: click the button.
      const t = await p.$('[data-theme-toggle]');
      if (!t) { await p.close(); continue; }
      await t.click(); await p.waitForTimeout(320);
      const after = await p.evaluate(MEASURE);
      const now = await p.evaluate(()=>document.documentElement.getAttribute('data-theme'));
      for (const c of after) {
        if (!c.bgs||!c.bgs.length) continue;
        let worst=c.bgs[0],cr=Infinity;
        for (const bg of c.bgs){const v=ratio(c.fg,bg); if(v<cr){cr=v;worst=bg;}}
        const large=c.size>=24||(c.size>=18.66&&c.bold);
        if (cr < (large?3:4.5))
          add(`[${start}->${now}] ${cr.toFixed(2)}:1 ${c.sel} rgb(${c.fg}) on rgb(${worst})`, f);
      }
      await p.close();
    }
  }
  const rows=Object.entries(bucket).map(([k,v])=>[k,v.size,[...v][0]]).sort((a,b)=>b[1]-a[1]);
  console.log('AFTER TOGGLING THE THEME AT RUNTIME:', rows.length, 'distinct');
  rows.slice(0,25).forEach(([k,n,eg])=>console.log(`  ${String(n).padStart(3)}x  ${k}   e.g. ${eg}`));
  if (rows.length>25) console.log('  ...', rows.length-25, 'more');
  await b.close();
})();
