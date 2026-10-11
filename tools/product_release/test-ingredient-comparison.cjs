const assert=require('node:assert/strict'),C=require('../../js/ingredient-compare-core.js');
const left=['Onions','Cucumbers','Lettuce','Bread (variety not specified)'],right=['processed cheddar cheese','lettuce','tomato','cucumber','carrot','mayonnaise on wheat bread'];
const before=JSON.stringify({left,right}),result=C.compare(left,right);
assert.deepEqual(result.matching,[{left:'Cucumbers',right:'cucumber'},{left:'Lettuce',right:'lettuce'}]);assert.deepEqual(result.onlyLeft,['Onions','Bread (variety not specified)']);assert.equal(JSON.stringify({left,right}),before);
for(const [a,b] of [['Chicken Breast','Chicken Strips'],['Cos Lettuce','Iceberg Lettuce'],['Wheat bread','Bread (variety not specified)'],['Mayonnaise','Mayonnaise on wheat bread']])assert.equal(C.compare([a],[b]).matching.length,0);
assert.deepEqual(C.compare([],[]),{matching:[],onlyLeft:[],onlyRight:[]});assert.equal(C.compare(['Tomatoes'],['tomato']).matching.length,1);
console.log('PASS: source-label plurals, original labels retained, no preparation/bread/sauce equivalence inferred, immutable inputs.');
