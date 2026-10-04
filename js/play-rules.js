/* Original GetMacros puzzle rules. Shared primitives, distinct objectives.
   Numeric food labels below are explicitly fictional educational examples. */
(function(scope){'use strict';
const foods=['egg','strawberry','broccoli','avocado','potato','banana','carrot','tomato'];
const clone=x=>JSON.parse(JSON.stringify(x));
function rng(seed){let a=(Number(seed)||1)>>>0;return()=>{a+=0x6D2B79F5;let t=a;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return((t^t>>>14)>>>0)/4294967296;};}
function shuffle(a,r){a=a.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(r()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
function runs(a){let n=0,out=[];a.forEach(v=>{if(v)n++;else if(n){out.push(n);n=0;}});if(n)out.push(n);return out.length?out:[0];}
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function create(id,seed=1,records=[]){const r=rng(seed),n=2+Math.floor(r()*4),b=10+Math.floor(r()*6)*5;
 const g={id,seed,turns:0,done:false,error:'',feedback:'',score:0,kind:'number',inputs:[],selected:[],options:[],answer:null,solution:[],values:{},paused:false};
 const number=(prompt,fields,answers)=>{g.prompt=prompt;g.inputs=fields.map((label,i)=>({label,value:'',answer:answers[i]}));g.answer=answers;g.solution=answers.map((value,index)=>({type:'input',index,value})).concat({type:'check'});};
 const choose=(prompt,options,answer,multi=false)=>{g.kind=multi?'select':'choice';g.prompt=prompt;g.options=options;g.answer=answer;g.solution=answer.map(index=>({type:'pick',index})).concat({type:'check'});};
 const ordering=(prompt,options,answer)=>{g.kind='order';g.prompt=prompt;g.options=options;g.answer=answer;g.solution=answer.map(index=>({type:'pick',index})).concat({type:'check'});};
 const pairs=(prompt,left,right)=>{g.kind='pairs';g.prompt=prompt;g.left=left;g.options=shuffle(right.map((text,key)=>({text,key})),r);g.answer=left.map((_,i)=>g.options.findIndex(x=>x.key===i));g.solution=g.answer.map((index,row)=>({type:'pair',index,row})).concat({type:'check'});};
 const grid=(prompt,size,target)=>{g.kind='grid';g.prompt=prompt;g.size=size;g.cells=Array(size*size).fill(0);g.target=target;g.solution=target.map((v,index)=>v?{type:'cell',index}:null).filter(Boolean).concat({type:'check'});};
 const maze=(prompt,steps)=>{const rotate=i=>{let y=Math.floor(i/5),x=i%5;for(let k=0;k<seed%4;k++)[y,x]=[x,4-y];return y*5+x;};g.kind='maze';g.prompt=prompt;g.size=5;g.pos=rotate(0);g.walls=[6,7,11,16,18].map(rotate);g.goal=rotate(24);g.collected=[];g.path=[];g.steps=steps;g.required=(steps||[]).map(rotate);g.solution=[1,2,3,4,9,14,19,24].map(index=>({type:'move',index:rotate(index)}));};
 switch(id){
 case 'serving-size-detective':number(`${n} servings, ${b} g carbohydrate in each example serving. What is the total?`,['Carbohydrate (g)'],[n*b]);break;
 case 'label-matchmaker':pairs('Pair each portion with its example calorie panel.',[`${n} × 40 kcal`,`2 × ${b} kcal`,'Half of 80 kcal'],[`${n*40} kcal`,`${2*b} kcal`,'40 kcal']);break;
 case 'missing-number-kitchen':number(`An example recipe totals ${b*3+n} g protein. Two parts contain ${b} g each. What is the missing part?`,['Missing protein (g)'],[b+n]);break;
 case 'portion-balance':g.kind='balance';g.prompt=`Each left portion is ${n*10} g. Each right portion is 10 g. Match exactly ${n*20} g on both sides.`;g.weights=[n*10,10];g.counts=[0,0];g.goal=n*20;g.solution=[{type:'count',index:0,value:2},{type:'count',index:1,value:n*2},{type:'check'}];break;
 case 'claim-check':choose(`Example label: ${b} g protein per 100 g portion. Which statement follows?`,[`${b*2} g protein in 200 g`,'Guaranteed muscle gain','Safe for every allergy',`${b} g protein in every possible portion`],[0]);break;
 case 'rounding-room':number(`${b*10} is an ordinary nearest-ten rounded value. Give the inclusive lower and exclusive upper bounds. Halfway values round upward.`,['Lower bound (inclusive)','Upper bound (exclusive)'],[b*10-5,b*10+5]);break;
 case 'ingredient-order':{let w=shuffle([40,70,100,130],r);ordering('Example recipe: put the ingredient masses in descending order.',w.map((x,i)=>`${foods[i]} · ${x} g`),w.map((x,i)=>i).sort((a,b)=>w[b]-w[a]));break;}
 case 'build-a-plate':choose('Choose exactly one grain token, one vegetable token and one protein token.', ['Rice · grain','Carrot · vegetable','Beans · protein token','Bread · grain','Tomato · vegetable'],[0,1,2],true);g.rule='plate';break;
 case 'protein-target-puzzle':choose(`Fictional portions: reach exactly ${n*3+b} g with two different portions.`,[`${n*3} g`,`${b} g`,`${b+1} g`,`${n*3+2} g`],[0,1],true);g.rule='sum';g.amounts=[n*3,b,b+1,n*3+2];g.goal=n*3+b;break;
 case 'range-finder':choose(`Select ALL fictional orders between ${b*10} and ${b*10+100} kcal, inclusive.`,[b*10-1,b*10,b*10+50,b*10+100,b*10+101].map(x=>`${x} kcal`),[1,2,3],true);break;
 case 'fiber-trail':maze('Collect all three fictional 2 g fiber tokens, then reach the gate.',[2,9,19]);g.rule='collect';break;
 case 'sodium-sort':{let w=shuffle([80,150,230,310],r);ordering('Equal 100 g example servings: sort sodium from least to most.',w.map(x=>`${x} mg / 100 g`),w.map((x,i)=>i).sort((a,b)=>w[a]-w[b]));break;}
 case 'restaurant-order-builder':{let available=records.filter(x=>x.ingredients&&x.ingredients.length>1),meal=available[Math.floor(r()*available.length)];if(!meal){g.blocked='No suitable verified order data is available.';break;}g.meal=meal;g.kind='select';g.prompt=`Rebuild ${meal.chain} · ${meal.name}. Select every item listed in the source order.`;g.options=meal.ingredients.concat(['Untracked extra: mango','Untracked extra: toast']);g.answer=meal.ingredients.map((_,i)=>i);g.source=meal.source;g.solution=g.answer.map(index=>({type:'pick',index})).concat({type:'check'});break;}
 case 'trade-off-table':choose('Select all fictional orders with at least 25 g protein AND no more than 700 mg sodium.', ['28 g · 650 mg','25 g · 700 mg','32 g · 800 mg','20 g · 400 mg','27 g · 500 mg'],[0,1,4],true);break;
 case 'fruit-catch':g.kind='catch';g.prompt='Catch five requested fruits. Move your basket, then drop the fruit.';g.lane=2;g.round=0;g.targets=Array.from({length:5},()=>Math.floor(r()*5));g.options=['strawberry','banana','orange','apple','pear'];g.solution=g.targets.flatMap(index=>[{type:'lane',index},{type:'advance'}]);break;
 case 'garden-glide':maze('Reach the garden gate. Use arrows or choose a neighboring square.');break;
 case 'picnic-delivery':maze('Collect parcels 1, 2 and 3 in order, then reach the picnic table.',[2,9,19]);g.rule='ordered';break;
 case 'berry-bounce':g.kind='bounce';g.prompt='Predict the next bounce lane. Catch six returns to clear the berry targets.';g.lane=2;g.ball=1;g.direction=1;g.round=0;g.solution=[];{let p=1,d=1;for(let i=0;i<6;i++){if(p+d>4||p+d<0)d=-d;p+=d;g.solution.push({type:'lane',index:p},{type:'advance'});}}break;
 case 'kitchen-rhythm':g.kind='sequence';g.prompt='Study this four-beat pattern. Hide it, then tap its beats in order.';g.options=['Tap','Hold','Rest'];g.target=Array.from({length:4},()=>Math.floor(r()*3));g.revealed=true;g.solution=[{type:'study'},...g.target.map(index=>({type:'pick',index})),{type:'check'}];break;
 case 'orange-orbit':g.kind='orbit';g.prompt='Land on three marked platforms. Turn one step at a time, then choose Land.';g.pos=0;g.round=0;g.targets=shuffle([2,4,6],r);g.solution=[];{let p=0;g.targets.forEach(t=>{while(p!==t){p=(p+1)%8;g.solution.push({type:'advance'});}g.solution.push({type:'land'});});}break;
 case 'bean-balance':g.kind='stack';g.prompt='Place five beans. Keep the average lane between 1.5 and 2.5 after every placement.';g.options=['Lane 0','Lane 1','Lane 2','Lane 3','Lane 4'];g.solution=Array.from({length:5},()=>({type:'pick',index:2}));break;
 case 'pantry-pack':case 'tabletop-tangram':g.kind='pack';g.size=4;g.prompt=id==='pantry-pack'?'Pack all four pantry blocks into the 4 × 4 grid.':'Cover the diamond-shaped lunch silhouette with four L-shaped pieces.';g.shapes=id==='pantry-pack'?[[[0,0],[0,1],[1,0],[1,1]],[[0,0],[0,1],[1,0],[1,1]],[[0,0],[0,1],[1,0],[1,1]],[[0,0],[0,1],[1,0],[1,1]]]:[[[0,1],[1,0],[1,1]],[[0,0],[1,0],[1,1]],[[0,0],[0,1],[1,1]],[[0,0],[0,1],[1,0]]];g.target=id==='tabletop-tangram'?[0,1,1,0,1,1,1,1,1,1,1,1,0,1,1,0]:Array(16).fill(1);g.cells=Array(16).fill(-1);g.piece=0;g.rotation=0;g.solution=(id==='pantry-pack'?[0,2,8,10]:[0,2,8,10]).flatMap((index,piece)=>[{type:'piece',index:piece},{type:'place',index}]).concat({type:'check'});break;
 case 'recipe-path':maze('Visit preparation steps 1, 2 and 3 in order, then finish.',[1,4,14]);g.rule='ordered';break;
 case 'garden-pipes':g.kind='pipes';g.size=3;g.prompt='Rotate the marked elbows to join the water inlet to the flower.';g.path=[0,1,2,5,8];g.required=[1,1,2,0,0];g.cells=Array(9).fill(0);g.rotations=g.required.map(x=>(x+1+Math.floor(r()*3))%4);g.solution=[];g.rotations.forEach((x,i)=>{for(let k=0;k<(g.required[i]-x+4)%4;k++)g.solution.push({type:'rotate',index:i});});g.solution.push({type:'check'});break;
 case 'snack-slide':g.kind='slide';g.size=3;g.prompt='Arrange tiles 1–8, with the empty space last. Choose a tile beside the gap.';g.cells=[1,2,3,4,5,6,7,8,0];g.solution=[];{let empty=8,last=-1;for(let k=0;k<14;k++){const opts=neighbors(empty,3).filter(x=>x!==last),i=opts[Math.floor(r()*opts.length)];[g.cells[i],g.cells[empty]]=[g.cells[empty],g.cells[i]];g.solution.unshift({type:'slide',index:empty});last=empty;empty=i;}}break;
 case 'orchard-nonogram':{let t=[0,1,1,0,1,1,1,1,1,1,1,1,0,1,1,0];if(seed%2)t=t.map((_,i)=>t[(3-i%4)*4+Math.floor(i/4)]);grid('Fill the 4 × 4 orchard pattern from its clues. Mark empty cells with the Cross tool.',4,t);g.rows=Array.from({length:4},(_,i)=>runs(t.slice(i*4,i*4+4)));g.cols=Array.from({length:4},(_,i)=>runs(Array.from({length:4},(_,j)=>t[j*4+i])));break;}
 case 'lunchbox-logic':g.kind='assign';g.prompt='Place four items: egg immediately left of tomato; rice in the rightmost compartment; carrot left of egg.';g.options=['Egg','Tomato','Rice','Carrot'];g.answer=[3,0,1,2];g.solution=g.answer.map((index,row)=>({type:'pair',row,index})).concat({type:'check'});break;
 case 'ingredient-anagrams':{const word=['AVOCADO','BROCCOLI','STRAWBERRY','POTATO'][Math.floor(r()*4)];g.kind='order';g.prompt='Unscramble the ingredient name.';g.options=shuffle(word.split(''),r);g.answer=word;let used=[];g.solution=word.split('').map(c=>{let i=g.options.findIndex((x,j)=>x===c&&!used.includes(j));used.push(i);return{type:'pick',index:i};}).concat({type:'check'});break;}
 case 'food-crossword':g.kind='crossword';g.prompt='Two words cross at the marked shared letter.';g.words=seed%2?['PEAR','BEAN']:['LIME','RICE'];g.clues=seed%2?['Four-letter fruit; third letter A.','Four-letter legume; third letter A.']:['Four-letter citrus fruit; second letter I.','Four-letter grain; second letter I.'];g.cross=seed%2?2:1;number(g.prompt,g.clues,g.words);g.kind='crossword';break;
 case 'menu-word-hunt':g.kind='hunt';g.size=6;g.words=[['EGG','BEAN','RICE'],['PEA','LIME','OATS'],['HAM','PEAR','TOFU']][seed%3];g.prompt=`Find ${g.words.join(', ')}. Select the first and last letter of each word.`;g.cells=Array.from({length:36},()=>String.fromCharCode(65+Math.floor(r()*26)));g.wordpaths=[[0,1,2],[6,12,18,24],[8,15,22,29]];g.wordpaths.forEach((p,i)=>p.forEach((x,j)=>g.cells[x]=g.words[i][j]));g.found=[];g.solution=g.wordpaths.flatMap(p=>[{type:'cell',index:p[0]},{type:'cell',index:p.at(-1)}]);break;
 case 'kitchen-connections':g.kind='groups';g.prompt='Find two groups of four: measuring equipment and actions that cut.';g.options=shuffle(['Cup','Scale','Spoon','Measuring jug','Slice','Dice','Chop','Mince'],r);g.categories=['Cup','Scale','Spoon','Measuring jug'];g.found=[];g.solution=[g.categories,['Slice','Dice','Chop','Mince']].flatMap(a=>a.map(x=>({type:'pick',index:g.options.indexOf(x)})).concat({type:'check'}));break;
 case 'description-detective':pairs('Match the specific description to its ingredient.', ['Yellow fruit with a long curved peel','Green fruit with a large central pit','Red seeded fruit with a leafy cap'],['Banana','Avocado','Strawberry']);break;
 case 'nutrition-term-match':pairs('Match the nutrition-label term to its definition.', ['Serving size','Protein','Total carbohydrate'],['Reference amount used for the label’s listed values','The quantity of protein listed in grams','The quantity of total carbohydrate listed in grams']);break;
 case 'source-sleuth':{const nutrient=['fiber','protein','carbohydrate'][seed%3];choose(`Claim: “This example ${n*50} g portion contains ${b} g ${nutrient}.” Which excerpt supports it directly?`, [`Example table: ${n*50} g portion; ${nutrient} ${b} g.`,`A headline: ${nutrient} makes every meal better.`,`A table: 50 g portion; fat ${b} g.`,'A study headline about an unspecified population.'],[0]);break;}
 case 'market-memory':g.kind='memory';g.prompt='Match all four ingredient pairs. Reveal two, then continue after a mismatch.';g.options=shuffle(['egg','egg','potato','potato','tomato','tomato','banana','banana'],r);g.found=[];g.solution=[];['egg','potato','tomato','banana'].forEach(f=>g.options.forEach((v,index)=>{if(v===f)g.solution.push({type:'pick',index});}));break;
 case 'spot-the-swap':g.kind='spot';g.prompt='Select the three positions that changed from the first scene to the second.';g.left=shuffle(foods,r);g.options=g.left.slice();g.answer=shuffle([0,1,2,3,4,5,6,7],r).slice(0,3).sort((a,b)=>a-b);g.answer.forEach((i,j)=>g.options[i]=g.left[(i+1)%8]);g.solution=g.answer.map(index=>({type:'pick',index})).concat({type:'check'});break;
 case 'order-recall':g.kind='recall';g.prompt='Study these four ingredients, then hide them and repeat their order.';g.options=foods.slice(0,6);g.target=shuffle([0,1,2,3,4,5],r).slice(0,4);g.revealed=true;g.solution=[{type:'study'},...g.target.map(index=>({type:'pick',index})),{type:'check'}];break;
 case 'pantry-peek':g.kind='peek';g.prompt='Study the pantry. Then hide it and tell us how many potatoes it contained.';g.options=shuffle(['potato','egg','potato','tomato','banana','potato','egg','avocado'],r);g.revealed=true;g.inputs=[{label:'Potatoes',value:'',answer:3}];g.solution=[{type:'study'},{type:'input',index:0,value:3},{type:'check'}];break;
 case 'sequence-chef':g.kind='chef';g.prompt='Study, hide and repeat. The sequence grows from two to four ingredients.';g.options=foods.slice(0,4);g.target=shuffle([0,1,2,3],r);g.round=2;g.revealed=true;g.solution=[];for(let k=2;k<=4;k++)g.solution.push({type:'study'},...g.target.slice(0,k).map(index=>({type:'pick',index})),{type:'check'});break;
 case 'silhouette-supper':g.kind='silhouette';g.prompt='Which ingredient has this silhouette?';g.options=['pear','banana','egg','broccoli'];g.answer=[Math.floor(r()*4)];g.solution=[{type:'pick',index:g.answer[0]},{type:'check'}];break;
 case 'odd-ingredient-out':choose('Shape rule: all except one are modeled as a round circle. Select the long curved silhouette.', ['Tomato','Orange','Apple','Banana'],[3]);break;
 case 'plate-art':g.kind='art';g.prompt='Place three or more ingredient stamps on the plate. Choose a stamp, then a position. Save when you like it.';g.options=foods;g.cells=Array(9).fill(-1);g.piece=0;g.solution=[{type:'piece',index:0},{type:'place',index:1},{type:'piece',index:1},{type:'place',index:4},{type:'piece',index:2},{type:'place',index:7},{type:'save'}];break;
 case 'smoothie-studio':g.kind='mix';g.prompt='Make six scoops in a 1 : 2 : 3 ratio of berry, banana and avocado color tokens.';g.options=['Berry','Banana','Avocado'];g.counts=[0,0,0];g.target=[1,2,3];g.solution=[1,2,3].map((value,index)=>({type:'count',index,value})).concat({type:'check'});break;
 case 'sandwich-architect':ordering('Build from bottom to top: bread, tomato, egg, avocado, bread.', ['Bread base','Tomato','Egg','Avocado','Bread lid'],[0,1,2,3,4]);break;
 case 'mascot-maker':g.kind='mascot';g.prompt='Choose a food body, eyes and expression. Save your original character on this device.';g.options=foods;g.values={body:'egg',eyes:'calm',mouth:'smile'};g.solution=[{type:'custom',key:'body',value:'avocado'},{type:'custom',key:'eyes',value:'bright'},{type:'custom',key:'mouth',value:'grin'},{type:'save'}];break;
 case 'recipe-remix':pairs('Replace the missing example token with a token in the same stated recipe role.', ['Crunch token missing','Liquid token missing','Green color token missing'],['Carrot · crunch token','Water · liquid token','Broccoli · green color token']);break;
 case 'market-budget':choose('Fictional prices: buy exactly three different items for exactly 10 tokens.', ['Eggs · 2 tokens','Rice · 3 tokens','Tomato · 5 tokens','Pear · 6 tokens','Beans · 8 tokens'],[0,1,2],true);g.rule='budget';g.amounts=[2,3,5,6,8];g.goal=10;break;
 case 'picnic-planner':choose('Pack exactly three objects: at least 4 seats, at least 4 drinks; use no more than 8 space tokens.', ['Bench: 4 seats · 3 space','Drink jug: 4 drinks · 2 space','Blanket: 0 seats · 0 drinks · 3 space','Stool: 1 seat · 2 space','Cup: 1 drink · 2 space'],[0,1,2],true);g.rule='picnic';break;
 case 'menu-mystery':{const a=records.filter(x=>Number.isFinite(x.cal)&&Number.isFinite(x.p));if(a.length<4){g.blocked='Four verified meals are needed.';break;}g.meal=a[Math.floor(r()*a.length)];g.kind='mystery';g.options=shuffle([g.meal,...shuffle(a.filter(x=>x.name!==g.meal.name),r).slice(0,3)],r);g.answer=[g.options.indexOf(g.meal)];g.clues=[`${g.meal.cal} kcal per listed order`,`${g.meal.p} g protein per listed order`,g.meal.chain,g.meal.portion];g.clue=0;g.solution=[{type:'clue'},{type:'clue'},{type:'clue'},{type:'pick',index:g.answer[0]},{type:'check'}];break;}
 case 'macro-grid':{let a=Array.from({length:9},()=>1+Math.floor(r()*9));g.kind='numeric-grid';g.prompt='Fill the three blank example gram values. Check every row and column total.';g.size=3;g.answer=a;g.cells=a.map((x,i)=>i%4===0?'':x);g.rows=[0,1,2].map(i=>a.slice(i*3,i*3+3).reduce((t,x)=>t+x,0));g.cols=[0,1,2].map(i=>a[i]+a[i+3]+a[i+6]);g.solution=[0,4,8].map(index=>({type:'input',index,value:a[index]})).concat({type:'check'});break;}
 case 'portion-fractions':g.kind='fractions';g.prompt='Shade one half of both plates: one has 4 slices, the other 6.';g.cells=Array(10).fill(0);g.answer=[2,3];g.solution=[0,1,4,5,6].map(index=>({type:'cell',index})).concat({type:'check'});break;
 case 'restaurant-route':g.kind='route';g.prompt='Visit all four fictional stops and return home. Keep the route at 12 grid units or less.';g.options=['A (0, 0) · home','B (3, 0)','C (3, 3)','D (0, 3)'];g.coords=[[0,0],[3,0],[3,3],[0,3]];g.goal=12;g.solution=[0,1,2,3].map(index=>({type:'pick',index})).concat({type:'check'});break;
 case 'harvest-conveyor':g.kind='conveyor';g.prompt='Send four harvest items to their marked bins. The switch-to-bin map changes each turn.';g.round=0;g.routes=Array.from({length:4},()=>shuffle([0,1,2],r));g.targets=Array.from({length:4},()=>Math.floor(r()*3));g.options=['Left switch','Center switch','Right switch'];g.solution=g.targets.map((t,i)=>({type:'pick',index:g.routes[i].indexOf(t)}));break;
 case 'food-factory':{const order=shuffle([0,1,2],r);let target='ABC';order.forEach(i=>{if(i===0)target=target.split('').reverse().join('');if(i===1)target=target.slice(1)+target[0];if(i===2)target='X'+target;});ordering(`Transform ABC into ${target}. Arrange the three switches, each used once.`, ['Reverse','Move first to end','Add X at start'],order);g.rule='factory';g.target=target;break;}
 case 'recipe-dominoes':g.kind='domino';g.prompt='Join every ingredient-tag tile. Matching tags meet; flip a tile before placing if needed.';g.tiles=shuffle([['grain','crunch'],['crunch','green'],['green','fruit'],['fruit','grain']],r);g.options=g.tiles.map(a=>a.join(' → '));g.flipped=[];g.solution=['grain','crunch','green','fruit'].map(t=>({type:'pick',index:g.tiles.findIndex(a=>a[0]===t)})).concat({type:'check'});break;
 default:throw Error('Unknown game '+id);
 }
 if(id==='pantry-pack'&&seed%2){g.shapes=[[[0,0],[0,1],[0,2],[0,3]],[[0,0],[0,1],[0,2],[0,3]],[[0,0],[0,1],[1,0],[1,1]],[[0,0],[0,1],[1,0],[1,1]]];g.solution=[0,4,8,10].flatMap((index,piece)=>[{type:'piece',index:piece},{type:'place',index}]).concat({type:'check'});}
 return g;
}
function neighbors(i,n){return[i-n,i+n,i%n?i-1:-1,i%n<n-1?i+1:-1].filter(x=>x>=0&&x<n*n);}
function act(g,a){if(g.done||g.paused||g.blocked)return g;g.error='';g.feedback='';g.turns++;
 const fail=t=>{g.error=t;return g;},win=()=>{g.done=true;g.score=1;g.feedback='Complete. Nicely done!';return g;};
 if(a.type==='input'){if(g.kind==='numeric-grid')g.cells[a.index]=a.value;else g.inputs[a.index].value=a.value;return g;}
 if(a.type==='study'){g.revealed=!g.revealed;g.selected=[];return g;}
 if(a.type==='clear'){g.selected=[];if(g.kind==='pairs'||g.kind==='assign')g.values={};return g;}
 if(a.type==='custom'){g.values[a.key]=a.value;return g;}
 if(a.type==='clue'){g.clue=Math.min(g.clue+1,g.clues.length-1);return g;}
 if(a.type==='count'){g.counts[a.index]=Math.max(0,Math.min(30,Number(a.value)||0));return g;}
 if(a.type==='pair'){if(a.index===null)delete g.values[a.row];else g.values[a.row]=a.index;return g;}
 if(a.type==='lane'){g.lane=a.index;return g;}
 if(a.type==='piece'){g.piece=a.index;g.rotation=0;return g;}
 if(a.type==='rotate'&&g.kind==='pipes'){g.rotations[a.index]=(g.rotations[a.index]+1)%4;return g;}
 if(a.type==='rotate'&&g.kind==='pack'){g.rotation=(g.rotation+1)%4;return g;}
 if(a.type==='flip'){g.flipped[a.index]=!g.flipped[a.index];return g;}
 if(a.type==='cell'){
  if(g.kind==='hunt'){g.selected.push(a.index);if(g.selected.length===2){const[from,to]=g.selected;const idx=g.wordpaths.findIndex(p=>p[0]===from&&p.at(-1)===to);g.selected=[];if(idx<0)return fail('That start and end do not match a hidden word.');if(!g.found.includes(idx))g.found.push(idx);if(g.found.length===3)return win();}return g;}
  g.cells[a.index]=g.cells[a.index]===1?0:1;return g;
 }
 if(a.type==='place'){
  if(g.kind==='art'){g.cells[a.index]=g.piece;return g;}
  if(g.kind==='pack'){
   const shape=g.shapes[g.piece].map(([y,x])=>{for(let k=0;k<g.rotation;k++)[y,x]=[x,-y];return[y,x];});const minY=Math.min(...shape.map(x=>x[0])),minX=Math.min(...shape.map(x=>x[1]));const y=Math.floor(a.index/g.size),x=a.index%g.size;
   const cells=shape.map(([dy,dx])=>[y+dy-minY,x+dx-minX]);if(cells.some(([cy,cx])=>cy<0||cx<0||cy>=g.size||cx>=g.size))return fail('That piece would leave the grid.');if(cells.some(([cy,cx])=>!g.target[cy*g.size+cx]))return fail('Keep every piece inside the marked silhouette.');if(cells.some(([cy,cx])=>g.cells[cy*g.size+cx]!==-1&&g.cells[cy*g.size+cx]!==g.piece))return fail('Pieces cannot overlap.');g.cells=g.cells.map(v=>v===g.piece?-1:v);cells.forEach(([cy,cx])=>g.cells[cy*g.size+cx]=g.piece);return g;
  }
 }
 if(a.type==='move'){
  if(!neighbors(g.pos,g.size).includes(a.index)||g.walls.includes(a.index))return fail('Choose a neighboring open square.');g.pos=a.index;g.path.push(a.index);
  if(g.required.includes(a.index)&&!g.collected.includes(a.index)){if(g.rule==='ordered'&&g.required[g.collected.length]!==a.index)return fail('Visit the numbered steps in order.');g.collected.push(a.index);}
  if(g.pos===g.goal){if(g.collected.length===g.required.length)return win();return fail('Collect every marked stop before finishing.');}return g;
 }
 if(a.type==='slide'){const empty=g.cells.indexOf(0);if(!neighbors(empty,g.size).includes(a.index))return fail('Only a tile next to the gap can slide.');[g.cells[empty],g.cells[a.index]]=[g.cells[a.index],g.cells[empty]];if(same(g.cells,[1,2,3,4,5,6,7,8,0]))return win();return g;}
 if(a.type==='advance'){
  if(g.kind==='orbit'){g.pos=(g.pos+1)%8;return g;}
  if(g.kind==='catch'){if(g.lane!==g.targets[g.round])return fail('Move the basket beneath the requested fruit, then catch.');g.round++;return g.round===5?win():g;}
  if(g.kind==='bounce'){let d=g.direction;if(g.ball+d<0||g.ball+d>4)d=-d;const next=g.ball+d;if(next!==g.lane)return fail(`The berry will return in lane ${next+1}. Reposition the paddle.`);g.direction=d;g.ball=next;g.round++;return g.round===6?win():g;}
 }
 if(a.type==='land'){if(g.pos!==g.targets[g.round])return fail('Turn until the orange reaches the marked platform.');g.round++;return g.round===3?win():g;}
 if(a.type==='pick'){
  if(g.kind==='memory'){if(g.found.includes(a.index)||g.selected.includes(a.index))return g;if(g.selected.length===2)return fail('Choose Continue to turn the unmatched pair over.');g.selected.push(a.index);if(g.selected.length===2&&g.options[g.selected[0]]===g.options[g.selected[1]]){g.found.push(...g.selected);g.selected=[];if(g.found.length===8)return win();}return g;}
  if(g.kind==='stack'){g.selected.push(a.index);const avg=g.selected.reduce((t,x)=>t+x,0)/g.selected.length;if(avg<1.5||avg>2.5){g.selected.pop();return fail('That placement tips outside the support. Try another lane.');}return g.selected.length===5?win():g;}
  if(g.kind==='conveyor'){if(g.routes[g.round][a.index]!==g.targets[g.round])return fail('That switch leads to a different bin on this turn.');g.round++;return g.round===4?win():g;}
  if(['recall','sequence','chef'].includes(g.kind)){if(g.revealed)return fail('Hide the sequence before answering.');g.selected.push(a.index);return g;}
  if(['order','route','domino'].includes(g.kind)){if(g.selected.includes(a.index))return g;g.selected.push(a.index);return g;}
  if(['choice','silhouette','mystery'].includes(g.kind)){g.selected=[a.index];return g;}
  if(g.selected.includes(a.index))g.selected=g.selected.filter(x=>x!==a.index);else g.selected.push(a.index);return g;
 }
 if(a.type==='save'){if(g.kind==='art'&&g.cells.filter(x=>x>=0).length<3)return fail('Place at least three stamps before saving.');return win();}
 if(a.type==='check'){
  let ok=false;
  if(['number','crossword','peek'].includes(g.kind))ok=g.inputs.every(x=>String(x.value).trim()!==''&&(g.kind==='crossword'?String(x.value).trim().toUpperCase()===x.answer:Number(x.value)===x.answer));
  else if(g.kind==='balance')ok=g.counts.every((x,i)=>x*g.weights[i]===g.goal);
  else if(g.kind==='mix')ok=same(g.counts,g.target);
  else if(g.kind==='pairs'||g.kind==='assign')ok=g.answer.every((x,i)=>g.values[i]!==undefined&&(Number(g.values[i])===x||(g.kind==='pairs'&&g.options[Number(g.values[i])]?.text===g.options[x].text)))&&new Set(Object.values(g.values)).size===g.answer.length;
  else if(g.kind==='order'){
   if(typeof g.answer==='string')ok=g.selected.map(i=>g.options[i]).join('')===g.answer;
   else if(g.rule==='factory'){let x='ABC';g.selected.forEach(i=>{if(i===0)x=x.split('').reverse().join('');if(i===1)x=x.slice(1)+x[0];if(i===2)x='X'+x;});ok=g.selected.length===3&&x===g.target;}
   else ok=same(g.selected,g.answer);
  }
  else if(['choice','select','silhouette','mystery','spot'].includes(g.kind)){
   if(g.rule==='plate')ok=g.selected.length===3&&g.selected.filter(x=>[0,3].includes(x)).length===1&&g.selected.filter(x=>[1,4].includes(x)).length===1&&g.selected.includes(2);
   else if(g.rule==='sum'||g.rule==='budget')ok=g.selected.length===(g.rule==='sum'?2:3)&&g.selected.reduce((t,i)=>t+g.amounts[i],0)===g.goal;
   else if(g.rule==='picnic')ok=g.selected.length===3&&g.selected.includes(0)&&g.selected.includes(1)&&g.selected.reduce((t,i)=>t+[3,2,3,2,2][i],0)<=8;
   else ok=same(g.selected.slice().sort((a,b)=>a-b),g.answer.slice().sort((a,b)=>a-b));
  }
  else if(g.kind==='pipes')ok=g.rotations.every((x,i)=>[0,1,3].includes(i)?x%2===g.required[i]%2:x===g.required[i]);
  else if(g.kind==='grid'){const filled=g.cells.map(x=>Number(x===1));ok=g.rows.every((c,i)=>same(runs(filled.slice(i*g.size,i*g.size+g.size)),c))&&g.cols.every((c,i)=>same(runs(Array.from({length:g.size},(_,j)=>filled[j*g.size+i])),c));}
  else if(g.kind==='pack')ok=g.cells.every((x,i)=>g.target[i]?x!==-1:x===-1)&&new Set(g.cells.filter(x=>x>=0)).size===g.shapes.length;
  else if(g.kind==='numeric-grid')ok=g.cells.every((x,i)=>String(x).trim()!==''&&Number(x)===g.answer[i]);
  else if(g.kind==='fractions')ok=g.cells.slice(0,4).reduce((t,x)=>t+x,0)===2&&g.cells.slice(4).reduce((t,x)=>t+x,0)===3;
  else if(['recall','sequence','chef'].includes(g.kind)){ok=same(g.selected,g.target.slice(0,g.kind==='chef'?g.round:g.target.length));if(ok&&g.kind==='chef'&&g.round<4){g.round++;g.selected=[];g.revealed=true;g.feedback='Correct. The sequence now has one more ingredient.';return g;}}
  else if(g.kind==='groups'){const selected=g.selected.map(i=>g.options[i]);const first=selected.length===4&&selected.every(x=>g.categories.includes(x));const second=selected.length===4&&selected.every(x=>!g.categories.includes(x));if((first&&!g.found.includes(0))||(second&&!g.found.includes(1))){g.found.push(first?0:1);g.selected=[];if(g.found.length===2)return win();g.feedback='One connection found. Find the other group.';return g;}}
  else if(g.kind==='route'){let distance=0;for(let i=0;i<g.selected.length;i++){let a=g.coords[g.selected[i]],b=g.coords[g.selected[(i+1)%g.selected.length]];distance+=Math.abs(a[0]-b[0])+Math.abs(a[1]-b[1]);}g.distance=distance;ok=g.selected.length===4&&g.selected[0]===0&&distance<=g.goal;}
  else if(g.kind==='domino'){let tiles=g.selected.map(i=>g.flipped[i]?g.tiles[i].slice().reverse():g.tiles[i]);ok=tiles.length===g.tiles.length&&tiles.every((t,i)=>!i||tiles[i-1][1]===t[0]);}
  return ok?win():fail('Not quite. Check the stated rules and try again. Your choices are kept.');
 }
 return g;
}
const api={create,act,rng,shuffle,neighbors,runs,clone,foods};if(typeof module!=='undefined'&&module.exports)module.exports=api;scope.GetMacrosPlayRules=api;
})(typeof window!=='undefined'?window:globalThis);
