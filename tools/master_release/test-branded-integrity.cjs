const sourceJSON=require('../source-json.cjs');
/* Every published grocery/reference row is inspected; no sampling of integrity. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto'),F=require('../../js/food-core.js');
const counts={},ids=new Set();let records=0,missing=0,formulations=new Set(),validUsdaRepeatedFormulations=0,usdaVersionGroups=0,usdaHistoricalRows=0;
const iso=value=>value===null||typeof value==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(value)&&Number.isFinite(Date.parse(value))&&new Date(value+'T12:00:00Z').toISOString().slice(0,10)===value;
for(const source of ['usda','retailer-ca','cnf','off']){
 const dir='data/branded-foods/'+source,manifest=sourceJSON.read(dir+'/manifest.json'),groups=new Map(),brandsByMarket={},seenOrdinals=new Set();let count=0,markets={};
 if(source==='usda'){assert.equal(manifest.profileCount,446810);assert.equal(manifest.jsonEncoding,'gzip');assert.equal(manifest.recordShardPrefix,3);assert.equal(manifest.brandCountsPrefix,'brands');assert.equal(manifest.brandCount,38412);}
 for(const shard of manifest.recordShards){if(manifest.jsonEncoding==='gzip')assert.equal(sourceJSON.resolve(dir+'/records/'+shard+'.json'),dir+'/records/'+shard+'.json.gz');for(const row of sourceJSON.read(dir+'/records/'+shard+'.json')){
  count++;records++;assert(!ids.has(row.id),'duplicate global ID '+row.id);ids.add(row.id);assert.equal(crypto.createHash('sha256').update(row.id).digest('hex').slice(0,manifest.recordShardPrefix||2),shard);assert(row.name&&row.sourceId&&row.version&&row.sourceUrl.startsWith('https://'));assert(['g','serving'].includes(row.basis.unit));assert(row.basis.amount>0);assert.equal(Object.keys(row.nutrients).length,30);markets[row.market]=(markets[row.market]||0)+1;
  for(const field of F.fields){const n=row.nutrients[field];assert(n===null||F.known(n),row.id+' invalid '+field);if(n===null)missing++;else assert(row.provenance[field],row.id+' absent nutrient provenance '+field);}
  for(const p of row.portions)assert(p.id&&p.label&&F.known(p.grams)&&p.grams>0);const measure=row.basis.unit==='serving'?'serving':row.portions[0]?.id||'g';const snap=F.snapshot(row,1,measure);try{F.validateSnapshot(snap);}catch(error){throw Error(row.id+' '+row.name.length+' chars '+row.portions.length+' portions: '+error.message);}
  assert(Number.isInteger(row.catalogOrdinal)&&row.catalogOrdinal>=0&&row.catalogOrdinal<manifest.profileCount);assert(!seenOrdinals.has(row.catalogOrdinal),'duplicate catalogue ordinal');seenOrdinals.add(row.catalogOrdinal);
  if(row.type==='branded'){
   assert(['US','CA','MX','GB','IE','AU','NZ','JP'].includes(row.market));assert(row.brand&&row.formulation);const key=[row.barcodeNormalized||row.id,row.market,row.formulation].join('|');
   if(formulations.has(key)){
    // Actual USDA source versions can retain an unchanged label. Every rank,
    // group count, publication date and distinct FDC ID is checked below.
    assert.equal(source,'usda','duplicate product identity/version '+key);assert(Number.isInteger(row.sourceVersionCount)&&row.sourceVersionCount>1,'duplicate label lacks actual version metadata');validUsdaRepeatedFormulations++;
   }
   formulations.add(key);
  }
  if(source==='usda'){
   assert.equal(row.sourceChecked,null);assert.equal(row.status,'manufacturer-label-imported');assert.equal(row.license,'CC0-1.0');assert(['US','NZ'].includes(row.market));
   assert(/^\d+$/.test(row.sourceRef));assert.equal(row.id,'branded:usda:'+row.sourceRef);assert.equal(row.sourceUrl,'https://fdc.nal.usda.gov/food-details/'+row.sourceRef+'/nutrients');
   for(const field of ['sourcePublished','sourceModified','labelDate','discontinuedDate'])assert(iso(row[field]),row.id+' invalid source date '+field);
   assert(Number.isInteger(row.sourceVersionRank)&&row.sourceVersionRank>=1);assert(Number.isInteger(row.sourceVersionCount)&&row.sourceVersionCount>=row.sourceVersionRank);
   assert.equal(row.sourceVersionRole,row.sourceVersionRank===1?'latest-in-bulk':'historical-in-bulk');
   assert.equal(row.versionGroup,'usda:'+crypto.createHash('sha256').update(JSON.stringify([row.market,row.barcodeNormalized||'fdc:'+row.sourceRef])).digest('hex').slice(0,16));
   let group=groups.get(row.versionGroup);if(!group){group={market:row.market,barcode:row.barcodeNormalized,count:row.sourceVersionCount,latest:row.latestSourceId,rows:[]};groups.set(row.versionGroup,group);}
   assert.equal(group.market,row.market);assert.equal(group.barcode,row.barcodeNormalized);assert.equal(group.count,row.sourceVersionCount);assert.equal(group.latest,row.latestSourceId);
   group.rows.push({id:row.id,published:row.sourcePublished||'',ref:Number(row.sourceRef),rank:row.sourceVersionRank});
   const brands=brandsByMarket[row.market]||(brandsByMarket[row.market]={});brands[row.brand]=(brands[row.brand]||0)+1;
   assert(Array.isArray(row.sourceHistory)&&row.sourceHistory.length);assert(row.sourceHistory.some(h=>h.sourceRef===row.sourceRef&&h.sourcePublished===row.sourcePublished&&h.availableInCatalogue===true));
   for(const history of row.sourceHistory){assert(/^\d+$/.test(history.sourceRef));assert(iso(history.sourcePublished));assert.equal(typeof history.availableInCatalogue,'boolean');assert(!Object.hasOwn(history,'nutrients'),'historical reference must not fabricate a nutrient body');}
   assert(F.known(row.sourceServing.amount)&&row.sourceServing.amount>0);assert.equal(({g:'g',ml:'ml',GRM:'g',MLT:'ml'})[row.sourceServing.rawUnit],row.sourceServing.unit);
   for(const field of F.fields){const raw=row.sourcePer100.nutrients[field],value=row.nutrients[field];if(raw===null){assert.equal(value,null);assert(!row.provenance[field]);}else{assert(F.known(raw));const expected=raw*(row.sourceServing.unit==='ml'?row.sourceServing.amount/100:1);assert(Math.abs(expected-value)<=Math.max(1,expected)*1e-12,row.id+' wrong source scaling '+field);}}
   if(row.sourceServing.unit==='ml'){assert.equal(row.basis.unit,'serving');assert.equal(row.basis.amount,1);assert.equal(row.portions.length,0);assert.throws(()=>F.scale(row,100,'g'));}
   else{assert.equal(row.basis.unit,'g');assert.equal(row.basis.amount,100);assert.equal(row.portions[0].grams,row.sourceServing.amount);}
  }
  if(source==='off'){assert.equal(row.sourceChecked,null);assert.equal(row.status,'community-label-imported');assert.equal(row.license,'ODbL-1.0');assert(row.attribution&&row.licenseUrl);assert.equal(snap.license,row.license);if(row.sourceServing.unit==='ml'){assert.equal(row.basis.unit,'serving');assert.throws(()=>F.scale(row,100,'g'));}}
  if(source==='cnf'){assert.equal(row.market,'CA-reference');assert.equal(row.type,'reference');assert.equal(row.basis.amount,100);assert.equal(row.basis.unit,'g');assert.equal(row.barcode,null);}
 }}
 assert.equal(count,manifest.profileCount);assert.deepEqual(markets,manifest.markets);counts[source]=count;
 if(source==='usda'){
  for(const group of groups.values()){
   assert.equal(group.rows.length,group.count,'source version count has missing or fabricated rows');group.rows.sort((a,b)=>b.published.localeCompare(a.published)||b.ref-a.ref);assert.equal(group.latest,group.rows[0].id);assert(ids.has(group.latest));group.rows.forEach((row,index)=>assert.equal(row.rank,index+1,'source versions must use publication chronology'));usdaHistoricalRows+=group.rows.length-1;
  }
  usdaVersionGroups=groups.size;const allBrands={};
  for(const [market,expected] of Object.entries(brandsByMarket)){const actual=sourceJSON.read(dir+'/'+manifest.brandCountsPrefix+'/'+market+'.json');assert.deepEqual(actual,expected);assert.equal(Object.values(actual).reduce((n,v)=>n+v,0),markets[market]);for(const [brand,n] of Object.entries(actual))allBrands[brand]=(allBrands[brand]||0)+n;}
  assert.equal(Object.keys(allBrands).length,manifest.brandCount);assert.equal(Object.values(allBrands).reduce((n,v)=>n+v,0),count);
 }
 // Every token/barcode posting has a valid catalog ordinal; no dangling query references.
 for(const prefix of manifest.tokenPrefixes)for(const ordinals of Object.values(sourceJSON.read(dir+'/tokens/'+prefix+'.json')))for(const i of ordinals)assert(Number.isInteger(i)&&i>=0&&i<count);
 for(const prefix of manifest.barcodePrefixes)for(const [code,ordinals] of Object.entries(sourceJSON.read(dir+'/barcodes/'+prefix+'.json'))){assert(/^\d{14}$/.test(code));for(const i of ordinals)assert(Number.isInteger(i)&&i>=0&&i<count);}
}
assert.equal(counts.usda,446810);assert.equal(counts['retailer-ca'],4);assert.equal(counts.cnf,5993);assert.equal(sourceJSON.read('data/food-library/manifest.json').profileCount,13578);
assert(counts.off>0);const report={pass:true,recordsInspected:records,bySource:counts,unknownNutrientFieldsPreserved:missing,originalUsdaReferenceCount:13578,usdaVersionGroups,usdaHistoricalRows,validUsdaRepeatedFormulations};fs.writeFileSync('docs/global-coverage-2026-10-17/usda/branded-integrity.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
