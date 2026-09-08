// Raster social previews are supported more widely than SVG Open Graph images.
const path=require('node:path');
const sharp=require(process.env.SHARP_MODULE||'C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root=path.resolve(__dirname,'..');
Promise.all(['restaurant-comparison','protein-absorption','diet-drinks','creatine-hair','calories-vs-macros'].map(async slug=>{
 const base=path.join(root,'images','journal-'+slug);
 await sharp(base+'.svg').resize(1200,630,{fit:'cover'}).png().toFile(base+'.png');
})).catch(e=>{console.error(e);process.exitCode=1});
