const fs=require('node:fs');
const files=fs.readdirSync('.').filter(f=>f.endsWith('.html'));
const counts=[];
for(const file of files){
 const source=fs.readFileSync(file,'utf8');
 const main=source.split('<main')[1]?.split('</main>')[0]||'';
 const classes=[...new Set([...main.matchAll(/class="([^"]+)"/g)].flatMap(m=>m[1].split(' ')))];
 const styles=[...source.matchAll(/<link[^>]+href="([^"?]+\.css)/g)].map(m=>m[1]);
 counts.push({file,words:main.replace(/<[^>]+>/g,' ').split(/\s+/).length,cssBytes:styles.reduce((a,f)=>a+(fs.existsSync(f)?fs.statSync(f).size:0),0),classes});
}
if(process.argv.includes('--classes')) for(const x of counts.filter(x=>['recipe-macro-scaler.html','nutrition-label-comparison-tool.html','blog.html','articles.html','healthy-fast-food.html','restaurant-meal-guides.html','chipotle-healthy-meals-macros.html','how-to-read-a-nutrition-label.html','contact.html','restaurant-meal-finder.html'].includes(x.file)))console.log(x.file,x.classes.join(' '));
else console.log(JSON.stringify(counts.map(({classes,...x})=>x),null,2));
