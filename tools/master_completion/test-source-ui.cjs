/* Source attribution is preserved through arithmetic, favorites and private backups. */
const assert=require('node:assert/strict'),fs=require('node:fs'),F=require('../../js/food-core.js');
const manifest=JSON.parse(fs.readFileSync('data/branded-foods/retailer-ca/manifest.json','utf8'));
const actual=JSON.parse(fs.readFileSync('data/branded-foods/retailer-ca/records/'+manifest.recordShards[0]+'.json','utf8'));
const record=actual[0];
assert(record&&record.sourceUrl&&record.nutrients);
const metadata={license:'ODbL-1.0',licenseUrl:'https://opendatacommons.org/licenses/odbl/1-0/',attribution:'Contains information from Open Food Facts — ODbL 1.0'};
// Isolated metadata contract only; this does not relabel or publish a retailer record.
const licensed={...record,...metadata},snapshot=F.snapshot(licensed,1,'source-serving');
for(const [key,value]of Object.entries(metadata)){assert.equal(snapshot[key],value);assert.equal(F.fromSnapshot(snapshot)[key],value);}
const backup={schemaVersion:1,entries:[{id:'metadata-test',date:'2026-10-13',occasion:'Lunch',note:'',savedAt:'2026-10-13T12:00:00Z',snapshot}],recipes:[],favorites:[snapshot]};
assert.equal(F.validateExport(JSON.parse(JSON.stringify(backup))).entries[0].snapshot.attribution,metadata.attribution);
const old=F.snapshot(record,1,'source-serving');delete old.license;delete old.licenseUrl;delete old.attribution;assert.equal(F.validateSnapshot(old),old);
for(const change of [s=>s.licenseUrl='javascript:alert(1)',s=>s.attribution='x'.repeat(1001),s=>s.license={}]){const bad=structuredClone(snapshot);change(bad);assert.throws(()=>F.validateSnapshot(bad));}
const code=fs.readFileSync('js/food-app.js','utf8');assert(code.includes('if(!diary){const brand=publicParams.get(\'brand\')'));assert(code.includes('off:\\d{8,14}:[A-Z]{2}'));assert(code.includes('record.licenseUrl'));assert(!code.includes("history.pushState"));
const comparison=fs.readFileSync('js/food-portion-compare.js','utf8');assert(comparison.includes('Contains information from Open Food Facts'));assert(comparison.includes("sourceId?.startsWith('off-')"));assert(comparison.includes('recipeParts?.some(usesOff)'));
console.log('PASS source-license preservation, backward-compatible snapshots, private backup validation, public-only brand shortcuts and attributed share-card contracts');

const G=require('../../js/branded-foods.js');const a={id:'label-a',type:'branded',barcodeNormalized:'00012345678905',market:'CA',brand:'Example',name:'Plain yogurt',package:'500 g'},b={...a,id:'label-b',sourceId:'other-source'};const groups=G.group([a,b,{...a,id:'flavour',name:'Vanilla yogurt'},{...a,id:'country',market:'US'},{...a,id:'pack',package:'1 kg'}]);assert.equal(groups.length,4);assert.equal(groups[0].versions.length,1);assert.notEqual(groups[0].primary.id,groups[0].versions[0].id);
const nyf=JSON.parse(fs.readFileSync('tools/master_completion/restaurant_records.json')).records[0],converted=F.restaurant(nyf);assert.equal(converted.nutrients.potassium,nyf.additionalNutrients.potassium.value);assert.equal(converted.retrievedAt,nyf.retrievedAt);assert(converted.provenance.p);const badUnit={...nyf,additionalNutrients:{potassium:{value:999,unit:'g'}}};assert.equal(F.restaurant(badUnit).nutrients.potassium,null);console.log('PASS source-version grouping preserves distinct flavours, packages and markets; supported restaurant minerals retain exact units/provenance');
