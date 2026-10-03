const fs=require('fs');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('./browser-fixture.cjs');
const out='docs/cozy-redesign-2026-10-03/final';
(async()=>{const b=await chromium.launch({channel:'msedge'});for(const [theme,appearance,width] of [['light','fresh',390],['light','fresh',1440],['dark','harvest',390],['dark','harvest',1440]]){
process.env.GM_TEST_THEME=theme;const p=await b.newPage({viewport:{width,height:1000},reducedMotion:'reduce'});await localAssets(p);await p.addInitScript(a=>localStorage.setItem('gm-appearance',a),appearance);
const shot=async name=>{await p.evaluate(()=>document.fonts.ready);await p.screenshot({path:`${out}/${name}-${theme}-${appearance}-${width}.png`});};
await p.goto('https://127.0.0.1:4187/index.html');await p.locator('#meal-quiz[data-ready=true]').waitFor();await shot('home-viewport');await p.locator('[data-launch-guide]').click();await shot('quiz');await p.keyboard.press('Escape');
if(width<901)await p.locator('.nav-toggle').click();await p.locator('.nav-group-trigger').nth(1).click();await shot('navigation');await p.keyboard.press('Escape');
await p.goto('https://127.0.0.1:4187/restaurant-meal-finder.html');await p.locator('#meal-quiz[data-ready=true]').waitFor();await shot('results-viewport');await p.screenshot({path:`${out}/results-full-${theme}-${appearance}-${width}.png`,fullPage:true});await p.close();}delete process.env.GM_TEST_THEME;await b.close();console.log('Captured current homepage, quiz, navigation and results in both themes at mobile and desktop widths.');})().catch(e=>{console.error(e);process.exitCode=1;});
