/* Catch ordinary words broken into fragments by narrow nested layouts. */
const fs = require('node:fs');
const {chromium} = require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets} = require('./browser-fixture.cjs');
(async () => {
  const browser = await chromium.launch({channel:'msedge'});
  const issues = [];
  try {
    await Promise.all([320,768,1440].map(async width => {
      const page = await browser.newPage({viewport:{width,height:950},reducedMotion:'reduce'});
      await localAssets(page);
      for (const file of fs.readdirSync('.').filter(f => f.endsWith('.html'))) {
        await page.goto('http://127.0.0.1:4174/'+file);
        const broken = await page.evaluate(() => {
          const found = [], walker = document.createTreeWalker(document.querySelector('main'),NodeFilter.SHOW_TEXT);
          while (walker.nextNode()) {
            const node = walker.currentNode;
            if (node.parentElement.closest('script,style,svg,.sr-only,.visually-hidden') || !node.parentElement.getClientRects().length) continue;
            for (const match of node.textContent.matchAll(/\b[A-Za-z]{5,20}\b/g)) {
              const range = document.createRange();
              range.setStart(node,match.index); range.setEnd(node,match.index+match[0].length);
              const rects = [...range.getClientRects()].filter(r => r.width>0 && r.height>0);
              if (rects.length>1 && rects.some(r => Math.abs(r.top-rects[0].top)>3)) found.push({word:match[0],text:node.textContent.trim().slice(0,80)});
            }
          }
          return found;
        });
        if (broken.length) issues.push({file,width,broken});
      }
      await page.close(); console.log('Word wrapping checked:',width);
    }));
    fs.writeFileSync('design/word-wrap-audit.json',JSON.stringify(issues,null,2));
    console.log(JSON.stringify(issues));
    if (issues.length) process.exitCode=1;
  } finally { await browser.close(); }
})().catch(e => {console.error(e);process.exitCode=1;});
