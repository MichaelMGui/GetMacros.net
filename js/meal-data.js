/* Restaurant meal database for the finder and the chain guides.
 *
 * Values are approximate standard builds taken from published chain nutrition
 * information. They move with recipe changes, regional menus and how the item
 * is actually assembled, so every surface that shows them also tells the reader
 * to confirm against the chain's own current figures.
 *
 * null means "not published in a form we would stand behind" rather than zero.
 * Keeping it null is deliberate: the finder can filter it out rather than
 * quietly treating an unknown as a good score.
 *
 * Tags
 *   protein    at least ~25 g protein
 *   light      roughly 400 kcal or under
 *   energy     roughly 600 kcal or over, for higher-calorie / bulking days
 *   fibre      at least ~5 g fibre
 *   lowsodium  roughly 600 mg sodium or under
 *   balanced   a reasonable spread rather than one standout number
 *   vegetarian no meat or fish
 *   plant      no animal products in the standard build
 *   gluten     no gluten-containing ingredient in the standard build
 *   breakfast  served as a breakfast item
 */
window.GM_MEALS = [
/* ---- Chipotle ---- */
{chain:'Chipotle',name:'High-Protein Bowl',cal:540,p:46,c:44,na:null,f:14,t:['balanced','protein','fibre','gluten'],size:'medium',url:'chipotle-healthy-meals-macros.html',why:'Chicken, black beans, fajita vegetables and salsa. A genuinely filling bowl with real fibre.'},
{chain:'Chipotle',name:'High-Protein Salad',cal:470,p:36,c:22,na:null,f:10,t:['protein','fibre','gluten','light'],size:'medium',url:'chipotle-healthy-meals-macros.html',why:'Same protein base over greens instead of rice. Vinaigrette is most of the remaining calories.'},
{chain:'Chipotle',name:'Chicken Burrito Bowl with rice and beans',cal:700,p:45,c:74,na:null,f:13,t:['energy','protein','fibre','gluten'],size:'large',url:'chipotle-healthy-meals-macros.html',why:'The standard bowl most people order. A solid higher-calorie option around training.'},
{chain:'Chipotle',name:'Sofritas Bowl',cal:620,p:23,c:76,na:null,f:15,t:['vegetarian','plant','fibre','energy','gluten'],size:'large',url:'chipotle-healthy-meals-macros.html',why:'Braised tofu with rice and beans. One of the better plant-based fast-food options for fibre.'},
{chain:'Chipotle',name:'Veggie Bowl with guacamole',cal:640,p:15,c:78,na:null,f:16,t:['vegetarian','plant','fibre','energy','gluten'],size:'large',url:'chipotle-healthy-meals-macros.html',why:'Guacamole counts as your fat source here. High fibre, lower protein than it looks.'},
{chain:'Chipotle',name:'Steak Salad, no rice',cal:405,p:32,c:18,na:null,f:9,t:['protein','light','fibre','gluten'],size:'medium',url:'chipotle-healthy-meals-macros.html',why:'A lighter build that still clears 30 g protein.'},

/* ---- Sweetgreen ---- */
{chain:'Sweetgreen',name:'Chicken Pesto Parm',cal:525,p:35,c:44,na:null,f:null,t:['protein','balanced'],size:'medium',url:'sweetgreen-healthy-meals-macros.html',why:'Chicken and quinoa with a pesto base. Protein-forward without being enormous.'},
{chain:'Sweetgreen',name:'Harvest Bowl',cal:740,p:32,c:78,na:null,f:null,t:['energy','protein','balanced'],size:'large',url:'sweetgreen-healthy-meals-macros.html',why:'Chicken, rice, sweet potato, apple, goat cheese and almonds. Substantial and genuinely filling.'},
{chain:'Sweetgreen',name:'Shroomami',cal:635,p:18,c:64,na:null,f:null,t:['vegetarian','plant','balanced','energy'],size:'large',url:'sweetgreen-healthy-meals-macros.html',why:'Tofu, mushrooms, warm grains and vegetables. The most satisfying plant bowl on the menu.'},
{chain:'Sweetgreen',name:'Super Green Goddess',cal:465,p:12,c:38,na:null,f:null,t:['vegetarian','light'],size:'medium',url:'sweetgreen-healthy-meals-macros.html',why:'Vegetables and chickpeas. Light, but add a protein if it is your main meal.'},
{chain:'Sweetgreen',name:'Guacamole Greens with chicken',cal:600,p:31,c:32,na:null,f:null,t:['protein','balanced','gluten','energy'],size:'medium',url:'sweetgreen-healthy-meals-macros.html',why:'Avocado does the heavy lifting on fat and satiety here.'},

/* ---- CAVA ---- */
{chain:'CAVA',name:'Greek Salad bowl',cal:580,p:null,c:null,na:null,f:null,t:['balanced','gluten'],size:'large',url:'cava-healthy-meals-macros.html',why:'Chicken, greens, vegetables and dips in a standard build.'},
{chain:'CAVA',name:'Falafel Crunch bowl',cal:860,p:null,c:null,na:null,f:null,t:['vegetarian','plant','fibre','energy'],size:'large',url:'cava-healthy-meals-macros.html',why:'Falafel, lentils and vegetables. A high-calorie plant option for bigger days.'},
{chain:'CAVA',name:'Grilled chicken over greens, light dressing',cal:420,p:38,c:18,na:null,f:6,t:['protein','light','gluten','fibre'],size:'medium',url:'cava-healthy-meals-macros.html',why:'Build it yourself: greens, grilled chicken, vegetables, dressing on the side.'},
{chain:'CAVA',name:'Harissa Avocado bowl',cal:730,p:28,c:66,na:null,f:12,t:['energy','fibre','balanced'],size:'large',url:'cava-healthy-meals-macros.html',why:'Warm grains, avocado and spiced protein. Good when the day has been long.'},

/* ---- Chick-fil-A ---- */
{chain:'Chick-fil-A',name:'Grilled Nuggets, 8 count',cal:130,p:25,c:1,na:440,f:0,t:['protein','light','gluten','lowsodium'],size:'small',url:'chick-fil-a-healthy-meals-macros.html',why:'One of the highest protein-per-calorie items in fast food. Rarely a whole meal on its own.'},
{chain:'Chick-fil-A',name:'Grilled Nuggets, 12 count',cal:200,p:38,c:2,na:660,f:0,t:['protein','light','gluten'],size:'medium',url:'chick-fil-a-healthy-meals-macros.html',why:'The larger count turns it into a proper protein-led meal.'},
{chain:'Chick-fil-A',name:'Grilled Chicken Sandwich',cal:390,p:28,c:44,na:770,f:3,t:['protein','light','balanced'],size:'medium',url:'chick-fil-a-healthy-meals-macros.html',why:'A multigrain bun and grilled fillet. The reliable everyday order.'},
{chain:'Chick-fil-A',name:'Market Salad with Grilled Nuggets',cal:570,p:32,c:46,na:1080,f:6,t:['protein','fibre','balanced'],size:'large',url:'chick-fil-a-healthy-meals-macros.html',why:'Fruit, nuts and greens. The dressing decides how big this really is.'},
{chain:'Chick-fil-A',name:'Egg White Grill',cal:290,p:26,c:30,na:820,f:1,t:['protein','light','breakfast'],size:'medium',url:'chick-fil-a-healthy-meals-macros.html',why:'A rare fast-food breakfast that clears 25 g protein under 300 calories.'},
{chain:'Chick-fil-A',name:'Kale Crunch Side',cal:170,p:3,c:9,na:250,f:2,t:['vegetarian','light','lowsodium','gluten'],size:'small',url:'chick-fil-a-healthy-meals-macros.html',why:'A vegetable side that is not fries. Pair with grilled nuggets.'},

/* ---- Subway ---- */
{chain:'Subway',name:'6-inch Veggie Delite',cal:320,p:17,c:44,na:600,f:4,t:['vegetarian','light','lowsodium'],size:'medium',url:'subway-healthy-meals-macros.html',why:'The lightest standard build. Cheese and sauces change it quickly.'},
{chain:'Subway',name:'6-inch Oven Roasted Turkey',cal:280,p:19,c:41,na:760,f:4,t:['protein','light'],size:'medium',url:'subway-healthy-meals-macros.html',why:'A dependable lean order. Ask for extra vegetables at no real calorie cost.'},
{chain:'Subway',name:'6-inch Rotisserie Chicken',cal:320,p:29,c:41,na:640,f:4,t:['protein','light'],size:'medium',url:'subway-healthy-meals-macros.html',why:'Better protein than the turkey for a similar calorie total.'},
{chain:'Subway',name:'Footlong Rotisserie Chicken',cal:640,p:58,c:82,na:1280,f:8,t:['protein','energy','fibre'],size:'large',url:'subway-healthy-meals-macros.html',why:'A genuine high-calorie, high-protein option. Sodium is the trade-off.'},
{chain:'Subway',name:'Grilled Chicken Salad',cal:220,p:27,c:12,na:610,f:5,t:['protein','light','fibre','gluten'],size:'small',url:'subway-healthy-meals-macros.html',why:'Very high protein per calorie. Dressing is the variable.'},

/* ---- Panera ---- */
{chain:'Panera',name:'Mediterranean Chicken Greens with Grains, half',cal:330,p:17,c:32,na:660,f:4,t:['light','balanced'],size:'small',url:'panera-healthy-meals-macros.html',why:'Half portions are the underused trick on this menu.'},
{chain:'Panera',name:'Mediterranean Greens with Grains, whole',cal:540,p:11,c:58,na:820,f:7,t:['vegetarian','fibre','balanced'],size:'large',url:'panera-healthy-meals-macros.html',why:'A meat-free grain salad with genuinely useful fibre.'},
{chain:'Panera',name:'Ten Vegetable Soup, cup',cal:80,p:3,c:15,na:590,f:4,t:['vegetarian','plant','light','lowsodium'],size:'small',url:'panera-healthy-meals-macros.html',why:'A very light starter that adds volume without much energy.'},
{chain:'Panera',name:'Chicken Caesar Salad, whole',cal:470,p:34,c:16,na:930,f:4,t:['protein','balanced'],size:'medium',url:'panera-healthy-meals-macros.html',why:'Protein-led. The dressing and croutons carry most of the calories.'},
{chain:'Panera',name:'Turkey Chili, bowl',cal:340,p:26,c:38,na:1140,f:11,t:['protein','fibre','balanced'],size:'medium',url:'panera-healthy-meals-macros.html',why:'One of the highest-fibre hot options on any chain menu.'},

/* ---- Starbucks ---- */
{chain:'Starbucks',name:'Eggs & Cheddar Protein Box',cal:460,p:22,c:36,na:450,f:5,t:['vegetarian','balanced','breakfast','fibre','lowsodium'],size:'medium',url:'starbucks-healthy-food-meals-macros.html',why:'Portable mix of protein, fruit and carbohydrate. Good travel food.'},
{chain:'Starbucks',name:'Spinach, Feta & Egg White Wrap',cal:290,p:20,c:34,na:840,f:3,t:['vegetarian','light','breakfast'],size:'medium',url:'starbucks-healthy-food-meals-macros.html',why:'The standard lighter breakfast order.'},
{chain:'Starbucks',name:'Turkey Bacon & Egg White Sandwich',cal:230,p:17,c:28,na:550,f:3,t:['protein','light','breakfast','lowsodium'],size:'small',url:'starbucks-healthy-food-meals-macros.html',why:'Lowest-calorie hot breakfast that still brings real protein.'},
{chain:'Starbucks',name:'Rolled & Steel-Cut Oatmeal',cal:160,p:5,c:28,na:125,f:4,t:['vegetarian','plant','light','lowsodium','breakfast'],size:'small',url:'starbucks-healthy-food-meals-macros.html',why:'Plain base; the toppings are where the calories arrive.'},
{chain:'Starbucks',name:'Chicken & Quinoa Protein Bowl',cal:420,p:27,c:42,na:680,f:6,t:['protein','balanced','fibre'],size:'medium',url:'starbucks-healthy-food-meals-macros.html',why:'A full meal rather than a snack, with fibre from the grains.'},

/* ---- McDonald's ---- */
{chain:'McDonald’s',name:'Hamburger',cal:250,p:12,c:31,na:510,f:1,t:['light','lowsodium'],size:'small',url:'mcdonalds-healthy-meals-macros.html',why:'A known, small standard portion. Useful as a calibration point.'},
{chain:'McDonald’s',name:'Egg McMuffin',cal:310,p:17,c:30,na:770,f:2,t:['light','breakfast'],size:'medium',url:'mcdonalds-healthy-meals-macros.html',why:'Compact breakfast with egg and Canadian bacon.'},
{chain:'McDonald’s',name:'McChicken',cal:400,p:14,c:39,na:560,f:2,t:['light','lowsodium'],size:'medium',url:'mcdonalds-healthy-meals-macros.html',why:'Moderate everywhere. Not a protein play.'},
{chain:'McDonald’s',name:'Quarter Pounder with Cheese',cal:520,p:30,c:42,na:1140,f:2,t:['protein','energy'],size:'large',url:'mcdonalds-healthy-meals-macros.html',why:'Genuinely high protein for the menu. Sodium is the cost.'},
{chain:'McDonald’s',name:'Double Cheeseburger',cal:450,p:25,c:34,na:1050,f:2,t:['protein'],size:'medium',url:'mcdonalds-healthy-meals-macros.html',why:'More protein per calorie than most items here.'},
{chain:'McDonald’s',name:'Apple Slices',cal:15,p:0,c:4,na:0,f:0,t:['vegetarian','plant','light','lowsodium','gluten'],size:'small',url:'mcdonalds-healthy-meals-macros.html',why:'A swap for fries that costs almost nothing.'},

/* ---- Wendy's ---- */
{chain:'Wendy’s',name:'Grilled Chicken Sandwich',cal:370,p:34,c:38,na:800,f:2,t:['protein','light','balanced'],size:'medium',url:'wendys-healthy-meals-macros.html',why:'One of the better protein-to-calorie sandwiches in the category.'},
{chain:'Wendy’s',name:'Grilled Chicken Wrap',cal:280,p:21,c:26,na:760,f:1,t:['protein','light'],size:'small',url:'wendys-healthy-meals-macros.html',why:'A smaller order that still brings 20 g protein.'},
{chain:'Wendy’s',name:'Apple Pecan Salad, half',cal:340,p:19,c:26,na:570,f:3,t:['balanced','light','lowsodium'],size:'small',url:'wendys-healthy-meals-macros.html',why:'Half sizes make the salads workable as a light meal.'},
{chain:'Wendy’s',name:'Chili, small',cal:240,p:17,c:23,na:810,f:6,t:['protein','fibre','light'],size:'small',url:'wendys-healthy-meals-macros.html',why:'Cheap, filling, high fibre. An underrated fast-food order.'},
{chain:'Wendy’s',name:'Dave’s Single',cal:590,p:30,c:39,na:1120,f:2,t:['protein','energy'],size:'large',url:'wendys-healthy-meals-macros.html',why:'A higher-calorie option that still carries 30 g protein.'},

/* ---- Taco Bell ---- */
{chain:'Taco Bell',name:'Chicken Soft Taco',cal:170,p:12,c:17,na:470,f:2,t:['light','lowsodium'],size:'small',url:'taco-bell-healthy-meals-macros.html',why:'Small, cheap, easy to combine into whatever size meal you want.'},
{chain:'Taco Bell',name:'Power Menu Bowl with chicken',cal:470,p:26,c:50,na:1200,f:8,t:['protein','fibre','balanced'],size:'medium',url:'taco-bell-healthy-meals-macros.html',why:'Rice, beans, chicken and vegetables. The most complete build on the menu.'},
{chain:'Taco Bell',name:'Veggie Power Menu Bowl',cal:430,p:12,c:56,na:1010,f:11,t:['vegetarian','fibre','balanced'],size:'medium',url:'taco-bell-healthy-meals-macros.html',why:'Very high fibre from the beans. Add extra beans for more protein.'},
{chain:'Taco Bell',name:'Black Bean Burrito',cal:420,p:13,c:64,na:1000,f:11,t:['vegetarian','plant','fibre','energy'],size:'medium',url:'taco-bell-healthy-meals-macros.html',why:'One of the cheapest high-fibre plant-based fast-food items anywhere.'},
{chain:'Taco Bell',name:'Chicken Burrito Supreme',cal:390,p:19,c:50,na:1090,f:7,t:['balanced','fibre'],size:'medium',url:'taco-bell-healthy-meals-macros.html',why:'A middle-of-the-road order with decent fibre.'},

/* ---- Panda Express ---- */
{chain:'Panda Express',name:'Grilled Teriyaki Chicken',cal:275,p:33,c:14,na:470,f:0,t:['protein','light','lowsodium'],size:'medium',url:'panda-express-healthy-meals-macros.html',why:'High protein before the side. Sauce and side are counted separately.'},
{chain:'Panda Express',name:'Super Greens side',cal:90,p:6,c:10,na:260,f:5,t:['vegetarian','plant','fibre','light','lowsodium','gluten'],size:'small',url:'panda-express-healthy-meals-macros.html',why:'Swap this for chow mein and the meal changes shape entirely.'},
{chain:'Panda Express',name:'String Bean Chicken Breast',cal:190,p:14,c:13,na:590,f:4,t:['protein','light','lowsodium'],size:'small',url:'panda-express-healthy-meals-macros.html',why:'A lighter entrée with vegetables built in.'},
{chain:'Panda Express',name:'Teriyaki Chicken with Super Greens',cal:365,p:39,c:24,na:730,f:5,t:['protein','fibre','balanced','light'],size:'medium',url:'panda-express-healthy-meals-macros.html',why:'The best-value protein plate here once you skip the fried rice.'},
{chain:'Panda Express',name:'Broccoli Beef with brown rice',cal:570,p:19,c:87,na:1140,f:8,t:['energy','fibre','balanced'],size:'large',url:'panda-express-healthy-meals-macros.html',why:'A higher-carbohydrate plate that suits a training day.'},

/* ---- KFC ---- */
{chain:'KFC',name:'Original Recipe Drumstick',cal:130,p:12,c:4,na:430,f:0,t:['light','lowsodium'],size:'small',url:'kfc-healthy-meals-macros.html',why:'A small portion you can build a plate around.'},
{chain:'KFC',name:'Original Recipe Breast',cal:390,p:39,c:11,na:1190,f:1,t:['protein'],size:'medium',url:'kfc-healthy-meals-macros.html',why:'Very high protein, with sodium that deserves attention.'},
{chain:'KFC',name:'Kentucky Grilled Chicken Breast',cal:210,p:38,c:0,na:710,f:0,t:['protein','light','gluten'],size:'medium',url:'kfc-healthy-meals-macros.html',why:'Grilled rather than fried: nearly the same protein for half the calories.'},
{chain:'KFC',name:'Green Beans',cal:25,p:1,c:5,na:260,f:2,t:['vegetarian','plant','light','lowsodium','gluten'],size:'small',url:'kfc-healthy-meals-macros.html',why:'The lightest side on the board by a wide margin.'},
{chain:'KFC',name:'Grilled Breast with green beans and corn',cal:345,p:41,c:34,na:1040,f:5,t:['protein','fibre','balanced'],size:'medium',url:'kfc-healthy-meals-macros.html',why:'A complete plate built from the lighter half of the menu.'},

/* ---- Popeyes ---- */
{chain:'Popeyes',name:'3 Blackened Tenders',cal:170,p:26,c:2,na:550,f:0,t:['protein','light','gluten','lowsodium'],size:'small',url:'popeyes-healthy-meals-macros.html',why:'Blackened rather than battered. Excellent protein per calorie.'},
{chain:'Popeyes',name:'5 Blackened Tenders',cal:280,p:43,c:3,na:920,f:0,t:['protein','light','gluten'],size:'medium',url:'popeyes-healthy-meals-macros.html',why:'A serious protein portion for under 300 calories.'},
{chain:'Popeyes',name:'Red Beans & Rice, regular',cal:230,p:6,c:31,na:680,f:5,t:['vegetarian','fibre'],size:'small',url:'popeyes-healthy-meals-macros.html',why:'A side with real fibre. Not vegan in the standard recipe.'},
{chain:'Popeyes',name:'Blackened Tenders with green beans',cal:230,p:28,c:10,na:850,f:3,t:['protein','light','balanced'],size:'medium',url:'popeyes-healthy-meals-macros.html',why:'Complete, light and protein-led.'},

/* ---- Jersey Mike's ---- */
{chain:'Jersey Mike’s',name:'Turkey Sub in a Tub',cal:280,p:28,c:12,na:1220,f:4,t:['protein','light','gluten'],size:'medium',url:'jersey-mikes-healthy-subs-macros.html',why:'"In a tub" swaps the bread for greens. Big protein, low calories, high sodium.'},
{chain:'Jersey Mike’s',name:'Mini Turkey Sub',cal:390,p:26,c:48,na:1180,f:3,t:['protein','light'],size:'small',url:'jersey-mikes-healthy-subs-macros.html',why:'Portion control built into the menu.'},
{chain:'Jersey Mike’s',name:'Regular Chicken Caesar Wrap',cal:640,p:39,c:52,na:1560,f:4,t:['protein','energy'],size:'large',url:'jersey-mikes-healthy-subs-macros.html',why:'A high-calorie, high-protein option for bigger days.'},
{chain:'Jersey Mike’s',name:'Veggie Sub, regular',cal:520,p:20,c:64,na:1090,f:5,t:['vegetarian','fibre','energy'],size:'large',url:'jersey-mikes-healthy-subs-macros.html',why:'Cheese-forward rather than vegetable-forward; ask for extra vegetables.'},

/* ---- Dunkin' ---- */
{chain:'Dunkin’',name:'Egg & Cheese Wake-Up Wrap',cal:180,p:7,c:14,na:470,f:0,t:['vegetarian','light','breakfast','lowsodium'],size:'small',url:'dunkin-healthy-breakfast-macros.html',why:'Small enough to pair with something else.'},
{chain:'Dunkin’',name:'Egg & Cheese English Muffin',cal:340,p:14,c:36,na:650,f:1,t:['vegetarian','light','breakfast'],size:'medium',url:'dunkin-healthy-breakfast-macros.html',why:'A more substantial meat-free breakfast sandwich.'},
{chain:'Dunkin’',name:'Turkey Sausage Wake-Up Wrap',cal:230,p:12,c:14,na:600,f:0,t:['light','breakfast','lowsodium'],size:'small',url:'dunkin-healthy-breakfast-macros.html',why:'Better protein than the plain egg version for 50 more calories.'},
{chain:'Dunkin’',name:'Sourdough Breakfast Sandwich',cal:490,p:24,c:42,na:1180,f:2,t:['protein','breakfast','energy'],size:'large',url:'dunkin-healthy-breakfast-macros.html',why:'The largest breakfast option here, and the only one clearing 20 g protein.'}
];
