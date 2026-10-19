/* Explicit research command; never invoked by a public request or build. */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../..');
const out = path.join(root, 'docs/ultimate-release-2026-10-19/editorial/sources');
fs.mkdirSync(out, {recursive: true});
const rows = JSON.parse(fs.readFileSync(path.join(root, 'js/order-registry.json'), 'utf8')).records;
const chains = [['CA','Tim Hortons'],['CA','Harvey’s'],['GB','Greggs'],['GB','KFC'],['GB','Subway'],['GB','Wagamama'],['GB','Wasabi'],['GB','PizzaExpress'],['GB','Tortilla'],['GB','Caffè Nero'],['GB','Five Guys'],['GB','Chopstix'],['GB','Starbucks'],['GB','LEON'],['US','Burger King']];
const results = [];
async function main() {
for (const [market, chain] of chains) {
  const first = rows.find(r => r.market === market && r.chain === chain);
  if (!first) throw Error(`Missing ${market} ${chain}`);
  const url = first.source;
  const key = `${market}-${first.restaurantId}`;
  try {
    const response = await fetch(url, {headers: {'User-Agent': 'GetMacros editorial source review; public official nutrition source'}, signal: AbortSignal.timeout(45000)});
    const body = Buffer.from(await response.arrayBuffer());
    const contentType = response.headers.get('content-type') || '';
    const ext = contentType.includes('pdf') ? '.pdf' : '.html';
    const file = key + ext;
    const sha256 = crypto.createHash('sha256').update(body).digest('hex');
    if (response.ok) fs.writeFileSync(path.join(out, file), body);
    results.push({market,chain,url,finalUrl:response.url,status:response.status,contentType,bytes:body.length,sha256,file:response.ok?file:null,retrievedAt:new Date().toISOString(),previousSourceHash:first.sourceHash||null,sameAsPreviousCapture:first.sourceHash?sha256===first.sourceHash:null});
  } catch (error) { results.push({market,chain,url,status:null,error:error.message,retrievedAt:new Date().toISOString()}); }
  fs.writeFileSync(path.join(out, 'source-checks.json'), JSON.stringify(results,null,2)+'\n');
  process.stdout.write(`${market} ${chain}: ${results.at(-1).status || results.at(-1).error}\n`);
}
}
main().catch(error => { process.stderr.write(error.stack + '\n'); process.exitCode = 1; });
