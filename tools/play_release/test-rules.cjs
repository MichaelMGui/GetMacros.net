const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const R=require('../../js/play-rules.js'),catalogue=require('./catalogue.json');
const s={window:{}};vm.createContext(s);for(const f of ['meal-data','meal-provenance'])vm.runInContext(fs.readFileSync('js/'+f+'.js','utf8'),s);
const records=s.window.GM_MEALS.filter(x=>x.verificationStatus==='source inspected').map(x=>({...x,ingredients:(x.components||[]).map(c=>c.item),portion:x.serving}));
let count=0;
for(const [id]of catalogue)for(let seed=1;seed<=40;seed++){
 const g=R.create(id,seed,records);assert(!g.blocked,`${id}: ${g.blocked}`);assert.deepEqual(g,R.create(id,seed,records),'deterministic '+id);
 const initial=R.clone(g);R.act(g,{type:'check'});assert(!g.done,`${id} incorrectly completed before input`);
 let solved=R.clone(initial);for(const action of initial.solution){R.act(solved,action);assert(!solved.error,`${id} seed ${seed}: ${solved.error} at ${JSON.stringify(action)}`);}
 assert(solved.done,`${id} seed ${seed} does not complete`);const complete=R.clone(solved);R.act(solved,{type:'pick',index:0});assert.deepEqual(solved,complete,'completed state changed');
 let paused=R.clone(initial);paused.paused=true;const copy=R.clone(paused);R.act(paused,initial.solution[0]);assert.deepEqual(paused,copy,'paused state changed');count++;
}
assert.equal(catalogue.length,56);assert.equal(new Set(catalogue.map(x=>x[0])).size,56);
let g=R.create('pantry-pack',1,records);R.act(g,{type:'place',index:15});assert(g.error&&!g.done);R.act(g,{type:'place',index:0});R.act(g,{type:'piece',index:1});R.act(g,{type:'place',index:0});assert(g.error,'overlap accepted');
g=R.create('ingredient-anagrams',1,records);R.act(g,{type:'pick',index:0});R.act(g,{type:'pick',index:0});assert.equal(g.selected.length,1,'letter reused');
g=R.create('macro-grid',1,records);g.cells[0]='';g.cells[4]='';g.cells[8]='';R.act(g,{type:'check'});assert(!g.done,'blank value interpreted as zero');
g=R.create('garden-glide',1,records);const start=g.pos;R.act(g,{type:'move',index:24});assert.equal(g.pos,start,'teleport allowed');
console.log(`PASS: ${count} deterministic solvable games across 56 rules; invalid inputs, empty values, overlap, repeated tiles, completion and pause guards.`);
