/* Shared browse metadata points to real source profiles, without copying nutrition. */
const fs=require('node:fs'),assert=require('node:assert/strict'),vm=require('node:vm'),crypto=require('node:crypto');
const F=require('../../js/food-core.js'),html=fs.readFileSync('food-diary.html','utf8');
const url=html.match(/data-diary-catalogue="([^"]+)"/)[1],catalogue=JSON.parse(fs.readFileSync('.'+url,'utf8'));
const index=new Map(JSON.parse(fs.readFileSync('data/food-library/index.json','utf8')).map(r=>[r.id,r]));
assert.equal(catalogue.schemaVersion,1);assert.equal(catalogue.groups.length,12);assert(catalogue.foodCount>=9000);assert.equal(catalogue.foodCount,catalogue.groups.reduce((sum,g)=>sum+g.foods.length,0));
assert.equal(crypto.createHash('sha256').update(fs.readFileSync('.'+url)).digest('hex').slice(0,12),url.match(/-([a-f0-9]{12})\.json$/)[1]);
const ids=new Set(),names=new Set(),shards=new Map();
for(const group of catalogue.groups){assert(group.foods.length>=100);for(const row of group.foods){
 assert(!ids.has(row.id));ids.add(row.id);assert(!names.has(row.name.toLowerCase()));names.add(row.name.toLowerCase());
 const original=index.get(row.id);assert(original);assert.equal(row.name,original.name);assert.equal(row.type,original.type);assert.equal(row.shard,original.shard);
 assert.deepEqual(Object.keys(row).sort(),['id','name','shard','type']);assert(['foundation','legacy','prepared'].includes(row.type));
 if(!shards.has(row.shard))shards.set(row.shard,JSON.parse(fs.readFileSync('data/food-library/records/'+row.shard+'.json')));
 const source=shards.get(row.shard).find(r=>r.id===row.id);assert(source);assert.equal(source.name,row.name);assert.equal(source.basis.unit,'g');assert.equal(source.basis.amount,100);
}}
const requests=[],context={GetMacrosFood:F,Map,Promise,fetch:async url=>{requests.push(url);return {ok:true,json:async()=>JSON.parse(fs.readFileSync('.'+url,'utf8'))}}};context.window=context;
vm.runInNewContext(fs.readFileSync('js/food-library.js','utf8'),context);
(async()=>{
 const food=catalogue.groups[0].foods[0],record=await context.GetMacrosLibrary.reference(food.id,food.shard);
 assert.deepEqual(requests,['/data/food-library/records/'+food.shard+'.json']);
 const expected=shards.get(food.shard).find(r=>r.id===food.id);assert.equal(record.nutrients.cal,expected.nutrients.cal);
 const snapshot=F.snapshot(record,37,'g');assert.equal(snapshot.nutrients.p,record.nutrients.p===null?null:record.nutrients.p*.37);assert.equal(F.validateSnapshot(snapshot),snapshot);
 await context.GetMacrosLibrary.reference(food.id,food.shard);assert.equal(requests.length,1);
 await assert.rejects(()=>context.GetMacrosLibrary.reference('fdc:0',food.shard),/unavailable/);
 await assert.rejects(()=>context.GetMacrosLibrary.reference(food.id,'../'),/unavailable/);
 await assert.rejects(()=>context.GetMacrosLibrary.reference('order:US:test',food.shard),/unavailable/);
 assert.equal(F.sum([{cal:null}]).cal.value,null);assert.equal(F.sum([{cal:0}]).cal.value,0);
 assert.equal(F.sum([{cal:25},{cal:null}]).cal.value,null);assert.equal(F.sum([{cal:25},{cal:null}]).cal.subtotal,25);
 assert(fs.readFileSync('sw.js','utf8').includes(url),'Browse catalogue is part of the matching offline shell');
 console.log('PASS: '+catalogue.foodCount+' source-backed browse choices; 12 groups; source identity, portions, nulls, bounded loading and offline catalogue.');
})().catch(e=>{console.error(e);process.exitCode=1});
