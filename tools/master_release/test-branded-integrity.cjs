/* Every published grocery/reference row is inspected; no sampling of integrity. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto'),F=require('../../js/food-core.js');
const counts={},ids=new Set();let records=0,missing=0,formulations=new Set();
for(const source of ['usda','retailer-ca','cnf','off']){
 const dir='data/branded-foods/'+source,manifest=JSON.parse(fs.readFileSync(dir+'/manifest.json','utf8'));let count=0,markets={};
 for(const shard of manifest.recordShards){for(const row of JSON.parse(fs.readFileSync(dir+'/records/'+shard+'.json','utf8'))){
  count++;records++;assert(!ids.has(row.id),'duplicate global ID '+row.id);ids.add(row.id);assert.equal(crypto.createHash('sha256').update(row.id).digest('hex').slice(0,manifest.recordShardPrefix||2),shard);assert(row.name&&row.sourceId&&row.version&&row.sourceUrl.startsWith('https://'));assert(['g','serving'].includes(row.basis.unit));assert(row.basis.amount>0);assert.equal(Object.keys(row.nutrients).length,30);markets[row.market]=(markets[row.market]||0)+1;
  for(const field of F.fields){const n=row.nutrients[field];assert(n===null||F.known(n),row.id+' invalid '+field);if(n===null)missing++;else assert(row.provenance[field],row.id+' absent nutrient provenance '+field);}
  for(const p of row.portions)assert(p.id&&p.label&&F.known(p.grams)&&p.grams>0);const measure=row.basis.unit==='serving'?'serving':row.portions[0]?.id||'g';const snap=F.snapshot(row,1,measure);try{F.validateSnapshot(snap);}catch(error){throw Error(row.id+' '+row.name.length+' chars '+row.portions.length+' portions: '+error.message);}
  if(row.type==='branded'){assert(['US','CA','MX','GB','IE','AU','NZ','JP'].includes(row.market));assert(row.brand&&row.formulation);const key=[row.barcodeNormalized||row.id,row.market,row.formulation].join('|');assert(!formulations.has(key),'duplicate product identity/version '+key);formulations.add(key);}
  if(source==='usda'){assert.equal(row.sourceChecked,null);assert.equal(row.status,'manufacturer-label-imported');if(row.sourceServing.unit==='ml'){assert.equal(row.basis.unit,'serving');assert.equal(row.portions.length,0);assert.throws(()=>F.scale(row,100,'g'));}}
  if(source==='off'){assert.equal(row.sourceChecked,null);assert.equal(row.status,'community-label-imported');assert.equal(row.license,'ODbL-1.0');assert(row.attribution&&row.licenseUrl);assert.equal(snap.license,row.license);if(row.sourceServing.unit==='ml'){assert.equal(row.basis.unit,'serving');assert.throws(()=>F.scale(row,100,'g'));}}
  if(source==='cnf'){assert.equal(row.market,'CA-reference');assert.equal(row.type,'reference');assert.equal(row.basis.amount,100);assert.equal(row.basis.unit,'g');assert.equal(row.barcode,null);}
 }}
 assert.equal(count,manifest.profileCount);assert.deepEqual(markets,manifest.markets);counts[source]=count;
 // Every token/barcode posting has a valid catalog ordinal; no dangling query references.
 for(const prefix of manifest.tokenPrefixes)for(const ordinals of Object.values(JSON.parse(fs.readFileSync(dir+'/tokens/'+prefix+'.json','utf8'))))for(const i of ordinals)assert(Number.isInteger(i)&&i>=0&&i<count);
 for(const prefix of manifest.barcodePrefixes)for(const [code,ordinals] of Object.entries(JSON.parse(fs.readFileSync(dir+'/barcodes/'+prefix+'.json','utf8')))){assert(/^\d{14}$/.test(code));for(const i of ordinals)assert(Number.isInteger(i)&&i>=0&&i<count);}
}
assert.equal(counts.usda,36862);assert.equal(counts['retailer-ca'],4);assert.equal(counts.cnf,5993);assert.equal(JSON.parse(fs.readFileSync('data/food-library/manifest.json')).profileCount,13578);
assert(counts.off>0);const report={pass:true,recordsInspected:records,bySource:counts,unknownNutrientFieldsPreserved:missing,originalUsdaReferenceCount:13578};fs.writeFileSync('docs/master-completion-2026-10-13/branded-integrity.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
