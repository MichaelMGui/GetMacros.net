'use strict';
const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../..');
const directory = path.join(root, 'docs/global-product-release-2026-10-11/sources');
const sources = [
 ['foundation.zip','https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_foundation_food_json_2026-04-30.zip'],
 ['sr-legacy.zip','https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_json_2018-04.zip'],
 ['survey.zip','https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_survey_food_json_2024-10-31.zip'],
 ['greggs.pdf','https://a.storyblok.com/f/94904/x/7dd8489dab/nutritional-information.pdf'],
 ['gyg.pdf','https://www.guzmanygomez.com.au/wp-content/uploads/2026/03/260305_NUTRITION_ALLERGEN_GUIDE_420X297MM.pdf'],
 ['mcdonalds-japan.html','https://www.mcdonalds.co.jp/quality/allergy_Nutrition/nutrient/'],
 ['mcdonalds-mexico.html','https://www.mcdonalds.com.mx/menu/hamburguesas/mctocino'],
 ['subway-mexico.pdf','https://www.subway.com/v1v2/assets/es-mx/nutrition/documents/mexico-nutrition-112025-eng.pdf'],
 ['mcdonalds-india.pdf','https://mcdonaldsindia.com/pdf/2024/nutrition-information.pdf'],
 ['mcdonalds-singapore.html','https://www.mcdonalds.com.sg/nutrition-calculator'],
 ['subway-nz.pdf','https://www.subway.com/en-nz/-/media/New_Zealand/Documents/Nutritionals/NZ-Nutritional-Summary.pdf'],
 ['subway-uk.pdf','https://media.subway.com/dam/urn:aaid:aem:c9e92cc1-b7a5-493f-adcd-7acb0641eeba/original/as/UKIBuildsandIngredientsNutritionalInformationSeptember2.pdf']
];
async function main(){
 await fs.mkdir(directory,{recursive:true});
 const selected=process.argv.includes('--new')?sources.slice(-2):sources;
 const results=await Promise.allSettled(selected.map(async([name,url])=>{
  const target=path.join(directory,name);let buffer;
  try{buffer=await fs.readFile(target);}catch{
   const response=await fetch(url,{signal:AbortSignal.timeout(60000),headers:{'User-Agent':'GetMacros source-verification/1.0'}});
   if(!response.ok)throw Error(name+' HTTP '+response.status);
   buffer=Buffer.from(await response.arrayBuffer());
   if(buffer.length>30000000)throw Error(name+' exceeded expected source size');
   await fs.writeFile(target,buffer);
  }
  return {file:name,url,retrieved:'2026-10-11',bytes:buffer.length,sha256:crypto.createHash('sha256').update(buffer).digest('hex')};
 }));
 const latest=results.map((r,i)=>r.status==='fulfilled'?r.value:{file:selected[i][0],url:selected[i][1],error:String(r.reason)});
 let previous=[];try{previous=JSON.parse(await fs.readFile(path.join(directory,'retrieval.json'),'utf8'));}catch{}
 const report=[...previous.filter(r=>!selected.some(s=>s[0]===r.file)),...latest];
 await fs.writeFile(path.join(directory,'retrieval.json'),JSON.stringify(report,null,2));
 report.forEach(r=>console.log(JSON.stringify(r)));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
