// Raster derivatives of the original repository-owned SVG, not third-party artwork.
const fs=require('node:fs');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{const b=await chromium.launch({channel:'msedge'});try{
const p=await b.newPage({deviceScaleFactor:1});const svg=fs.readFileSync('images/botanical-mark.svg','utf8');
for(const [size,file] of [[192,'images/icon-192.png'],[512,'images/icon-512.png'],[180,'apple-touch-icon.png']]){
await p.setViewportSize({width:size,height:size});await p.setContent(`<style>html,body{margin:0}svg{width:100vw;height:100vh}</style>${svg}`);await p.screenshot({path:file});}
await p.setViewportSize({width:1200,height:630});await p.setContent(`<style>body{margin:0;background:#fffefb;color:#152d24;font:26px Arial;padding:72px}svg{width:66px;height:66px;vertical-align:middle;margin-right:18px}h1{font:bold 82px/1.05 Arial;margin:60px 0 30px;letter-spacing:-4px;max-width:900px}p{color:#276443;font-size:28px}.rule{height:6px;background:#bed780;width:100px}</style><div>${svg}<b>GetMacros.</b></div><h1>Fast food.<br>Your macros.</h1><div class="rule"></div><p>Find fast-food meals by calories and protein.</p>`);await p.screenshot({path:'images/og-default.png'});
}finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
