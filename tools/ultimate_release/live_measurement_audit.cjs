/* Passive public-HTML inspection, not an account, traffic or browser-network audit. */
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'../..'),out=path.join(root,'docs/ultimate-release-2026-10-19');
const routes=['/','/food-diary.html','/calculators.html','/articles.html','/privacy.html','/ca/en/'];
(async()=>{
 const checks=[];
 for(const route of routes){
  const response=await fetch('https://getmacros.net'+route,{signal:AbortSignal.timeout(30000)});
  const html=await response.text();
  const scripts=Array.from(html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script\s*>/gi)).map(m=>({src:m[1].match(/\bsrc=["']([^"']+)/i)?.[1]||null,text:m[2]}));
  const external=scripts.filter(s=>s.src&&/^(?:https?:)?\/\//.test(s.src)).map(s=>s.src.split('?')[0]);
  checks.push({route,status:response.status,finalURL:response.url,ga4OrGTM:scripts.some(s=>/googletagmanager|google-analytics|\bgtag\s*\(/.test((s.src||'')+' '+s.text)),
   productionAdLoader:scripts.some(s=>/pagead2\.googlesyndication|adsbygoogle\.js|scripts\.mediavine|scripts\.journeymv/.test((s.src||'')+' '+s.text)),
   cloudflareWebAnalyticsBeacon:scripts.some(s=>/static\.cloudflareinsights\.com/.test(s.src||'')),
   cloudflareSecurityAppendix:scripts.some(s=>/__CF\$cv\$params|cdn-cgi\/challenge-platform/.test(s.text)),externalScriptURLs:external,
   robotsMeta:html.match(/<meta\b[^>]*name=["']robots["'][^>]*content=["']([^"']+)/i)?.[1]||null});
 }
 const report={checkedAt:new Date().toISOString(),scope:'Public production HTTP HTML only. No login, analytics account or visitor data. No script execution or browser network trace.',checks,
  interpretation:'An absent HTML beacon does not prove Cloudflare dashboard analytics are disabled. Edge analytics and browser analytics are separate. Actual provider account and browser-network evidence remain necessary.'};
 fs.mkdirSync(out,{recursive:true});fs.writeFileSync(path.join(out,'live-measurement-audit.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));
})().catch(e=>{console.error(e.message);process.exitCode=1;});
