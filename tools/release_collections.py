"""Audited source facts and individually edited meal resources for the release.

This tool writes integration JSON only. It never mutates central meal records or
public HTML. Tables are reproduced from those records, with source facts kept
separate from GetMacros arithmetic. Run after the root integrator applies patches.
"""
from pathlib import Path
import json, re, hashlib, html, statistics
from urllib.parse import urlencode
from build_meal_finder import parse_meals

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/release-2026-10-03'
DATE = '2026-10-03'
CHIP = 'https://www.chipotle.com/content/dam/chipotle/menu/nutrition/US-Nutrition-Facts-Paper-Menu-3-2025.pdf'
CHIP_MENU = 'https://newsroom.chipotle.com/2025-12-18-CHIPOTLE-UNVEILS-ITS-FIRST-EVER-HIGH-PROTEIN-MENU-FEATURING-A-NEW-SNACK-READY-HIGH-PROTEIN-CUP'
PANDA = 'https://www.pandaexpress.com/nutritioninformation'
PANERA = 'https://www.panerabread.com/content/dam/panerabread/documents/c8-26-nutrition-guide.pdf'
CAVA = 'https://assets.ctfassets.net/kugm9fp9ib18/3rkBCBV2gIGMu78AnqigQk/26f1d223147700d1c266d358b3678d3b/CAVA-Reg-GID-0425-Nutri_Allerg.pdf'
POPEYES = 'https://plk-use1-prod.sites.rbictg.com/nutrition/PLK_Nutrition.pdf'
SWEET = 'https://www.sweetgreen.com/nutrition'
CFA = 'https://www.chick-fil-a.com/menu/'
KEYS = ('cal','p','c','f','na','fat')

# Values follow cal, protein g, carbohydrate g, fiber g, sodium mg, total fat g.
# These are transcribed numerical facts, not redistributed source-document media.
CHIP_INGREDIENTS = {
 'chicken': (180,32,0,0,310,7), 'steak':(150,21,1,1,330,6),
 'sofritas':(150,8,9,3,560,10), 'white rice':(210,4,40,1,350,4),
 'brown rice':(210,4,36,2,190,6), 'black beans':(130,8,22,7,210,1.5),
 'pinto beans':(130,8,21,8,210,1.5),'fajita vegetables':(20,1,5,1,150,0),
 'corn salsa':(80,3,16,3,330,1.5),'tomato salsa':(25,0,4,1,550,0),
 'romaine':(5,0,1,1,0,0),'supergreens':(15,1,3,2,15,0),
 'guacamole':(230,2,8,6,370,22),'cheese':(110,6,1,0,190,8),
 'sour cream':(110,2,2,0,30,9),'vinaigrette':(220,1,18,1,850,16),
 'burrito tortilla':(320,8,50,3,600,9),
}
CHIP_PORTIONS = {'chicken':'4 oz','steak':'4 oz','sofritas':'4 oz','white rice':'4 oz',
 'brown rice':'4 oz','black beans':'4 oz','pinto beans':'4 oz','fajita vegetables':'2 oz',
 'corn salsa':'4 oz','tomato salsa':'4 oz','romaine':'1 oz','supergreens':'3 oz',
 'guacamole':'4 oz','cheese':'1 oz','sour cream':'2 oz','vinaigrette':'2 fl oz','burrito tortilla':'1 tortilla'}
PANDA_INGREDIENTS = {
 'grilled teriyaki chicken':(280,38,13,0,610,9),
 'super greens base':(180,8,17,8,660,9),
 'super greens entree':(45,3,5,3,130,2),
 'string bean chicken':(210,15,15,3,600,10),
 'broccoli beef':(190,17,14,2,600,7),
 'white rice':(570,11,129,0,0,0), 'fried rice':(610,15,109,3,810,13),
 'chow mein':(520,14,89,5,1040,12), 'orange chicken':(560,19,63,1,1000,25),
 'teriyaki sauce':(70,0,16,0,380,0),
}
PANDA_PORTIONS = {'grilled teriyaki chicken':'6.1 oz','super greens base':'10 oz',
 'super greens entree':'3.5 oz','string bean chicken':'5.6 oz','broccoli beef':'6.3 oz',
 'white rice':'12 oz','fried rice':'12 oz','chow mein':'12 oz','orange chicken':'6.2 oz',
 'teriyaki sauce':'1.8 oz'}

def values(t): return dict(zip(KEYS,t))
def summed(components, facts):
    return {k:sum(facts[name][i]*amount for name,amount in components) for i,k in enumerate(KEYS)}

def source_patch():
    patches=[]
    def add(chain,name,nums,source,serving,source_date=None,kind='published',components=None,notes=''):
        nums=values(nums) if isinstance(nums,tuple) else nums
        patches.append({'recordKey':chain+'||'+name,'values':nums,'source':source,
          'sourceURLs':[source], 'market':'U.S.','serving':serving,'retrievalDate':DATE,
          'sourceDate':source_date,'verificationStatus':'source inspected',
          'nutrientProvenance':{k:{'method':kind,'source':source,'retrieved':DATE} for k in nums},
          'components':components or [],'notes':notes})
    for name,nums,portion in [
      ('Chicken Pesto Parm',(510,38,30,6,1560,24),'1 standard bowl, 420 g, including dressing'),
      ('Harvest Bowl',(760,40,60,10,1265,42),'1 standard bowl, 425 g, including dressing'),
      ('Shroomami',(665,20,51,11,1250,45),'1 standard bowl, 457 g, including dressing'),
      ('Super Green Goddess',(465,12,36,13,1230,32),'1 standard salad, 347 g, including dressing'),
      ('Guacamole Greens',(555,29,35,12,1560,32),'1 standard salad, 635 g, including dressing')]:
        add('Sweetgreen',name,nums,SWEET,portion)
    for name,nums,portion in [
      ('Green Goddess Cobb Salad with Chicken, half',(290,20,15,4,990,17),'1/2 standard salad, dressing included; extra side excluded'),
      ('Greek Salad, whole',(630,8,17,5,1400,59),'1 whole standard salad, dressing included; extra side excluded'),
      ('Homestyle Chicken Noodle Soup, cup',(120,10,14,0,1050,3),'1 cup, without bread or another side'),
      ('Caesar with Chicken Salad, whole',(670,35,27,4,2620,47),'1 whole standard salad, dressing included; extra side excluded'),
      ('Hearty Fireside Chili, bowl',(410,19,49,9,1730,15),'1 bowl, without bread bowl or another side')]:
        add('Panera',name,nums,PANERA,portion,'2026-09-02')
    for name,nums in [
      ('Greek Salad bowl',(585,37,19,8,1830,40)),('Falafel Crunch bowl',(860,24,88,18,2230,56)),
      ('Chicken + Rice bowl',(710,40,43,7,1830,42)),('Harissa Avocado bowl',(840,42,63,12,2030,50))]:
        add('CAVA',name,nums,CAVA,'1 standard curated bowl, including its standard dips, toppings and dressing',
          notes='Existing official April-2025-named document inspected; no printed publication date established. Current live menu linkage could not be verified. Do not claim this is a new menu edition.')
    for name,nums,portion in [
      ('Grilled Nuggets, 8 count',(130,25,1,0,440,3),'8 grilled nuggets, without dipping sauce'),
      ('Grilled Chicken Sandwich',(390,28,45,3,765,11),'1 standard sandwich; source formulation includes listed sauce ingredients; extra packets, sides and drinks excluded'),
      ('Egg White Grill',(300,27,29,1,990,8),'1 standard breakfast sandwich'),
      ('Kale Crunch Side',(170,4,13,4,250,12),'1 standard side with vinaigrette and almonds'),
      ('Grilled Chicken Club Sandwich',(520,37,45,3,1055,22),'1 standard sandwich; extra sides and drinks excluded'),
      ('Chick-fil-A Cool Wrap',(660,43,32,14,1420,45),'1 standard wrap with suggested Avocado Lime Ranch dressing')]:
        slug={'Grilled Nuggets, 8 count':'entrees/grilled-nuggets','Grilled Chicken Sandwich':'entrees/grilled-chicken-sandwich',
          'Egg White Grill':'breakfast/egg-white-grill','Kale Crunch Side':'sides/kale-crunch-side',
          'Grilled Chicken Club Sandwich':'entrees/chick-fil-a-grilled-chicken-club-sandwich',
          'Chick-fil-A Cool Wrap':'entrees/chick-fil-a-cool-wrap'}[name]
        add('Chick-fil-A',name,nums,CFA+slug,portion)
    add('Chick-fil-A','Grilled Nuggets, 12 count',{'cal':200,'p':38,'c':2,'fat':4.5},
       CFA+'entrees/12-ct-grilled-nuggets','12 grilled nuggets, without dipping sauce',
       notes='Dedicated item page displays four nutrients. Prior fiber and sodium were not reverified in this inspection; retain their prior provenance dates.')
    for name,nums,portion in [('3 Blackened Tenders',(170,28,2,1,860,6),'3 tenders'),
      ('5 Blackened Tenders',(280,47,4,1,1430,9),'5 tenders'),
      ('Red Beans & Rice, regular',(260,7,29,6,580,16),'1 regular side')]:
        add('Popeyes',name,nums,POPEYES,portion+', biscuit, sauce and drink excluded','2026-09')
    add('Popeyes','3 Blackened Tenders with regular red beans and rice',(430,35,31,7,1440,22),
        POPEYES,'3 blackened tenders plus 1 regular red beans and rice; biscuit, sauce and drink excluded',
        '2026-09','calculated',[{'item':'3 Blackened Tenders','count':1},{'item':'Red Beans & Rice, regular','count':1}])
    for name,component,portion in [('Grilled Teriyaki Chicken','grilled teriyaki chicken','6.1 oz chicken entree'),
      ('Super Greens side','super greens base','10 oz full Super Greens base'),
      ('String Bean Chicken Breast','string bean chicken','5.6 oz entree')]:
        add('Panda Express',name,PANDA_INGREDIENTS[component],PANDA,portion)
    for name,components in [
      ('Grilled Teriyaki Chicken with Super Greens',[('grilled teriyaki chicken',1),('super greens base',1)]),
      ('Broccoli Beef with white steamed rice',[('broccoli beef',1),('white rice',1)]),
      ('Bigger Plate: fried rice + 3 grilled teriyaki chicken entrées',[('fried rice',1),('grilled teriyaki chicken',3)]),
      ('Bigger Plate: chow mein + grilled teriyaki + orange chicken + string bean chicken',
          [('chow mein',1),('grilled teriyaki chicken',1),('orange chicken',1),('string bean chicken',1)])]:
        detail=[{'item':n,'count':a,'serving':PANDA_PORTIONS[n],'values':values(PANDA_INGREDIENTS[n])} for n,a in components]
        add('Panda Express',name,summed(components,PANDA_INGREDIENTS),PANDA,
           ' + '.join(f'{a:g} × {PANDA_PORTIONS[n]} {n}' for n,a in components),
           kind='calculated',components=detail,notes='Sum of full source-table portions, not half-sides or Cub Meal portions; extra sauce packets and drinks excluded.')
    for name,product,nums,portion in [
      ('Turkey Bacon, Cheddar & Egg White Sandwich',368,(260,17,30,2,600,9),'1 sandwich, 142 g'),
      ('Spinach, Feta & Egg White Wrap',371,(290,20,34,3,840,8),'1 wrap, 159 g'),
      ('Egg White & Roasted Red Pepper Egg Bites',2122117,(170,12,11,0,470,8),'1 serving of two bites, 130 g')]:
        add('Starbucks',name,nums,f'https://www.starbucks.com/menu/product/{product}/single/nutrition',portion,
           notes='Official nutrition-page text returned in search result inspection. Direct page retrieval produced an empty script shell; this distinction is recorded, not claimed as a fresh rendered-site inspection.')
        patches[-1]['verificationStatus']='official indexed nutrition text inspected; live rendering inaccessible'
    for name,components in [
      ('Chicken Bowl with white rice and black beans',[('chicken',1),('white rice',1),('black beans',1),('fajita vegetables',1),('corn salsa',1),('tomato salsa',1),('romaine',1)]),
      ('Sofritas Bowl with brown rice and black beans',[('sofritas',1),('brown rice',1),('black beans',1),('fajita vegetables',1),('corn salsa',1),('tomato salsa',1),('romaine',1)]),
      ('Veggie Bowl with brown rice, black beans and guacamole',[('brown rice',1),('black beans',1),('fajita vegetables',1),('tomato salsa',1),('guacamole',1),('romaine',1)]),
      ('Steak Salad with black beans, no rice',[('steak',1),('supergreens',1),('black beans',1),('fajita vegetables',1),('tomato salsa',1),('romaine',1)]),
      ('High Protein-High Fiber Bowl',[('chicken',1),('brown rice',.5),('black beans',1),('fajita vegetables',1),('corn salsa',1),('tomato salsa',1),('romaine',1)]),
      ('High Protein-Low Calorie Salad',[('chicken',1),('supergreens',1),('fajita vegetables',1),('tomato salsa',1),('guacamole',1)])]:
        nums=summed(components,CHIP_INGREDIENTS)
        published = {'High Protein-High Fiber Bowl':{'cal':540,'p':46,'f':14},
          'High Protein-Low Calorie Salad':{'cal':470,'p':36,'f':10}}.get(name,{})
        nums.update(published)
        detail=[{'item':n,'count':a,'serving':CHIP_PORTIONS[n],'values':values(CHIP_INGREDIENTS[n])} for n,a in components]
        add('Chipotle',name,nums,CHIP,'Listed ingredient build: '+', '.join(f'{a:g} × {CHIP_PORTIONS[n]} {n}' for n,a in components),
           '2024-10 (ingredient PDF printed edition)','calculated',detail,
           'Component sums use rounded published portions. High Protein Menu calories, protein and fiber retain restaurant-published totals; other nutrients are ingredient sums. A half rice portion is an explicit GetMacros assumption, not a freshly measured restaurant scoop.')
        if published:
            patches[-1]['sourceURLs'].append(CHIP_MENU)
            for k in published: patches[-1]['nutrientProvenance'][k]={'method':'published','source':CHIP_MENU,'retrieved':DATE,'sourceDate':'2025-12-18'}
    payload={'retrievalDate':DATE,'market':'U.S.','records':patches,'ingredients':{
       'Chipotle':{'source':CHIP,'sourceDate':'2024-10 (printed edition)','values':{n:{'serving':CHIP_PORTIONS[n],**values(v)} for n,v in CHIP_INGREDIENTS.items()}},
       'Panda Express':{'source':PANDA,'sourceDate':None,'values':{n:{'serving':PANDA_PORTIONS[n],**values(v)} for n,v in PANDA_INGREDIENTS.items()}}},
       'unverifiedCombinations':['Chick-fil-A||Grilled Club, medium waffle fries and 12 grilled nuggets','Chick-fil-A||30 grilled nuggets, medium waffle fries and large fruit cup'],
       'sourceLimitations':['Starbucks live nutrition pages were not rendered: official indexed source text inspected.',
          'CAVA existing official document accessible; its current menu linkage and printed publication date remain unresolved.',
          'Neither accessible source nor attribution alone establishes a right to redistribute complete documents or datasets. No source documents, branded images or bulk dataset downloads are published by this tool.']}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'data-audited-patches.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    return payload

def esc(text): return html.escape(str(text), quote=True)
def fmt(value):
    if value is None: return 'Not available'
    return f'{value:,g}'

def resources(patch):
    """Edited resources with reproducible rows, not a restaurant-keyword matrix."""
    meals=parse_meals((ROOT/'js/meal-data.js').read_text(encoding='utf-8'))
    central={m['chain']+'||'+m['name']:m for m in meals}
    audited={p['recordKey']:{**central[p['recordKey']],**p['values'],**{
        'recordKey':p['recordKey'],'serving':p['serving'],'sourceURLs':p['sourceURLs'],
        'notes':p['notes'],'provenance':p['nutrientProvenance']}} for p in patch['records']}
    # The 12-count page did not expose fresh fiber/sodium. Keep those unknown in
    # this release research pool, even though the central finder has older values.
    audited['Chick-fil-A||Grilled Nuggets, 12 count']['f']=None
    audited['Chick-fil-A||Grilled Nuggets, 12 count']['na']=None
    pool=list(audited.values())
    def choose(*keys): return [audited[k] for k in keys]
    def find(predicate,order=None):
        rows=[m for m in pool if predicate(m)]
        return sorted(rows,key=order) if order else rows
    def table(rows,cols=('cal','p','c','fat','f','na'),density=False):
        labels={'cal':'Calories','p':'Protein (g)','c':'Carbs (g)','fat':'Fat (g)','f':'Fiber (g)','na':'Sodium (mg)'}
        headers='<th scope="col">Order and portion</th>'+''.join('<th scope="col">'+labels[k]+'</th>' for k in cols)
        if density: headers+='<th scope="col">Protein per 100 calories (g)</th>'
        body=''
        for m in rows:
            body+='<tr><th scope="row">'+esc(m['chain'])+' · '+esc(m['name'])+'<p class="table-portion">'+esc(m['serving'])+'</p></th>'
            body+=''.join('<td>'+fmt(m.get(k))+'</td>' for k in cols)
            if density: body+='<td>'+f'{m["p"] / m["cal"] * 100:.1f}'+'</td>'
            body+='</tr>'
        columns='<colgroup><col class="restaurant-order-column order-column">'+('<col class="restaurant-nutrient-column nutrient-column">'*(len(cols)+(1 if density else 0)))+'</colgroup>'
        return '<div class="table-wrap" tabindex="0" role="region" aria-label="Nutrition comparison; scroll horizontally on a small screen"><table class="comparison-table restaurant-comparison-table restaurant-comparison-table-cols-'+str(1+len(cols)+(1 if density else 0))+'">'+columns+'<thead><tr>'+headers+'</tr></thead><tbody>'+body+'</tbody></table></div>'
    def ingredient_table(chain,names):
        facts=patch['ingredients'][chain]
        rows=[{'chain':chain,'name':n.title(),'serving':facts['values'][n]['serving'],**facts['values'][n]} for n in names]
        return table(rows),rows
    pages=[]
    def add(slug,title,desc,h1,intent,utility,criteria,rows,body,sources=None,related=None,category='Restaurant comparisons'):
        urls=list(dict.fromkeys(sources or [url for m in rows for url in m.get('sourceURLs',[])]))
        used=[m['recordKey'] for m in rows if 'recordKey' in m]
        facts=[{'recordKey':m.get('recordKey'), 'label':m['chain']+' · '+m['name'],
                'serving':m['serving'],'values':{k:m.get(k) for k in KEYS},
                'nutrientProvenance':m.get('provenance',{})} for m in rows]
        claims=[{'claim':'The displayed nutrition for '+f['label']+' applies to '+f['serving']+'.',
                 'kind':'restaurant-published or explicitly calculated nutrition',
                 'recordKey':f['recordKey'],'values':f['values'],'sources':urls} for f in facts]
        source_names={SWEET:'Sweetgreen nutrition table',PANERA:'Panera U.S. nutrition guide',CAVA:'CAVA official nutrition document',
                      PANDA:'Panda Express nutrition table',CHIP:'Chipotle U.S. ingredient table',CHIP_MENU:'Chipotle High Protein Menu announcement',POPEYES:'Popeyes U.S. nutrition guide'}
        sources_html='<h2>Sources and date boundaries</h2><ul>'+''.join('<li><a href="'+esc(u)+'">'+esc(source_names.get(u,'Official restaurant item nutrition'))+'</a></li>' for u in urls)+'</ul>'
        note='These are selected U.S. portions, not a complete menu survey. Extra drinks, sides and sauce packets are excluded unless named. Published portions can differ from the food actually served.'
        if any(m['chain']=='Chipotle' for m in rows) or CHIP in urls:
            note+=' Chipotle ingredient sums use its October 2024 printed U.S. table, inspected October 3, 2026; retrieval does not make that an October 2026 menu edition.'
        if any(m['chain']=='CAVA' for m in rows):
            note+=' The CAVA figures come from the accessible official April-2025-named document. Its printed date and current menu linkage could not be established.'
        if any(m['chain']=='Starbucks' for m in rows):
            note+=' Starbucks values were inspected in indexed text from its official nutrition pages; direct retrieval returned a script shell rather than a rendered nutrition table.'
        if any(m['chain']=='Panera' for m in rows): note+=' Panera’s inspected guide is effective September 2, 2026.'
        if any(m['chain']=='Popeyes' for m in rows): note+=' The inspected Popeyes PDF is labeled September 2026.'
        sources_html+='<p>'+note+'</p>'
        related=related or [{'url':'restaurant-meal-finder.html','label':'Find and compare tracked meals'}, {'url':'restaurant-meal-guides.html','label':'Restaurant nutrition guides'}]
        pages.append({'slug':slug,'title':title,'description':desc,'h1':h1,'category':category,
          'intent':intent,'originalUtility':utility,'criteria':criteria,'recordKeys':used,
          'body':body+sources_html,'sourceURLs':urls,'claims':claims,'tableFacts':facts,
          'related':related,'publicationDate':DATE,'sourceStatus':'See explicit source edition and access notes; no claim of universal menu freshness.',
          'researchStatus':'Qualitative search-intent inspection; no search-volume or ranking estimates.'})
    def finder(label,**kwargs): return '<p><a href="restaurant-meal-finder.html?'+esc(urlencode(kwargs))+'">'+esc(label)+'</a>. The live finder covers more tracked orders than this source-audited shortlist.</p>'

    rows=find(lambda m:m['p']>=20,lambda m:-m['p']/m['cal'])[:12]
    add('protein-density-fast-food.html','Fast-food protein per 100 calories: a portion-aware comparison',
        'Compare protein density and total protein in selected fast-food orders. See why chicken portions and complete bowls answer different questions.',
        'How much protein do you get per 100 calories?',
        'Compare protein efficiency while retaining actual order sizes.',
        'Reproducible density ranking beside total protein, serving definitions and sodium; explains the small-portion trap.',
        'Among 41 source-inspected records, at least 20 g protein; twelve highest unrounded protein/calorie ratios. Not a complete-menu ranking.',rows,
        '<p>Chick-fil-A’s eight grilled nuggets provide 25 g protein in 130 calories: <strong>19.2 g protein per 100 calories</strong>. That is a concentrated protein portion. It is not automatically a complete lunch, and the ratio does not tell you how filling your whole order will be.</p>'
        '<h2>Compare density and the amount you will actually eat</h2><p>We divide the published protein by calories and multiply by 100. The table includes the twelve highest ratios among source-inspected GetMacros records with at least 20 g protein. Ranking uses the unrounded ratio; the displayed ratio is rounded to one decimal place.</p>'+table(rows,('cal','p','na'),True)+
        '<h2>A bigger number is only one part of the decision</h2><p>Popeyes’ five blackened tenders supply 47 g protein, more than the eight nuggets’ 25 g, while their ratio is lower. If you want a specific amount of protein, compare the total first. If you have a calorie limit as well, the ratio can help you compare two orders that already fit.</p><p>A side, biscuit, dressing or sauce can change the finished order’s ratio. Calculate it from the finished totals rather than averaging individual item ratios. A 130-calorie chicken portion should not be described as nutritionally equivalent to a bowl with beans and vegetables merely because it ranks higher here.</p>'
        '<h2>Use a second constraint</h2><p>Sodium is shown because a protein ranking alone can conceal a relevant difference. Fiber, carbohydrate and fat also matter to the question you are asking. This reference identifies a numerical relationship; it does not name a healthiest restaurant or prescribe your protein intake.</p>'+finder('Set a protein minimum',minProtein=25,sort='protein'),category='Nutrition data')

    rows=find(lambda m:m['p']>=25 and m['cal']<500,lambda m:(m['cal'],-m['p']))
    add('high-protein-fast-food-under-500-calories.html','High-protein fast food under 500 calories: exact orders and portions',
        'Selected orders with at least 25 g protein and fewer than 500 calories, with servings, sodium, fiber and excluded extras kept visible.',
        'Fast-food orders under 500 calories with at least 25 g protein',
        'Find an order meeting two explicit nutrition limits.',
        'Finite source-audited dual-threshold shortlist separating protein portions, breakfast and assembled meals.',
        'Protein >=25 g and calories <500; source-inspected record pool, sorted by calories.',rows,
        '<p>There are several ways to reach 25 g protein below 500 calories in the orders we checked. Some are chicken portions; others are sandwiches, salads or a chicken-and-side combination. <strong>The portion and included items matter as much as the two numbers.</strong></p>'
        '<h2>The source-inspected shortlist</h2><p>“High protein” means at least 25 g for this collection, matching the finder’s protein preference threshold. “Under 500” is strictly below 500. This is an editorial filter, not a regulated nutrition claim, medical target or full survey of every fast-food menu.</p>'+table(rows,('cal','p','f','na'))+
        '<h2>Which rows describe a meal?</h2><p>The nuggets and blackened tenders are chicken-only portions. The Grilled Chicken Sandwich includes its standard formulation but no fries or drink. Chick-fil-A’s Egg White Grill is a breakfast sandwich. Popeyes’ tenders-and-red-beans combination includes the named regular side; Panda’s combination includes the full Super Greens base listed below.</p><p>The Chipotle Steak Salad is a defined GetMacros ingredient build, not a claim that every steak salad at the counter has those totals. The High Protein-Low Calorie Salad retains restaurant-published calories, protein and fiber; its carbohydrate and sodium values are component sums.</p>'
        '<h2>Make the limit fit your actual order</h2><p>If you add a drink, biscuit, sauce packet or another side, this shortlist no longer describes your complete order. Check the appropriate restaurant source and add the supported values. If 500 calories is not your own meal target, change the limit rather than treating this collection as a recommendation for everyone.</p>'+finder('Browse meals with a 499-calorie limit and 25 g protein minimum',maxCal=499,minProtein=25),category='Meal collections')

    rows=find(lambda m:500<=m['cal']<=700 and m['p']>=20 and m['meal']=='main',lambda m:m['cal'])
    add('fast-food-meals-500-to-700-calories.html','Fast-food orders from 500 to 700 calories: compare what is included',
        'Compare tracked bowls, salads, a wrap and a sandwich within a 500–700-calorie range, with protein, fiber and serving details.',
        'Compare fast-food orders in the 500–700-calorie range',
        'Compare substantial main-order formats within a chosen calorie band.',
        'Inclusive calorie-band comparison with minimum protein and format-specific composition notes.',
        'Main records, 500–700 calories inclusive, protein >=20 g; source-inspected pool.',rows,
        '<p>A 500–700-calorie range can include very different orders: a grilled chicken club, a grain bowl, a salad or a dressed wrap. This comparison keeps their protein and fiber beside calories so the format does not decide for you.</p>'
        '<h2>Orders in this band</h2><p>These are source-inspected main-order records with at least 20 g protein. The range is a browsing choice, not a universal lunch requirement. Standard dressings are included where the source says so; extra sides and drinks are not.</p>'+table(rows,('cal','p','c','f','na'))+
        '<h2>The same calorie range can mean different ingredients</h2><p>Sweetgreen’s Chicken Pesto Parm is 510 calories with 38 g protein and 6 g fiber. Its Shroomami bowl is 665 calories with 20 g protein and 11 g fiber. Those differences come from their complete recipes, not simply “salad versus bowl.” Both appear here because the criteria are numerical.</p><p>Chick-fil-A’s Cool Wrap includes the suggested Avocado Lime Ranch dressing in the inspected figure. Removing that dressing without a separately supported calculation would make the comparison less reliable. Likewise, Chipotle’s 650-calorie chicken bowl describes the exact seven-ingredient build, not an unlimited choice of toppings.</p>'
        '<h2>Refine the shortlist in one direction</h2><p>If protein is your main constraint, sort by protein. If you want beans or vegetables to contribute fiber, compare that column as well. A whole salad may exceed another order’s sodium even if its name sounds lighter; Panera’s whole Caesar with Chicken illustrates why the source numbers should remain visible.</p>'+finder('Browse with a 700-calorie maximum and 20 g protein minimum',maxCal=700,minProtein=20)+
        '<p>The finder link sets an upper limit, not the lower edge of this static collection. Check each result’s calories if you want to stay above 500.</p>',category='Meal collections')

    rows=find(lambda m:m['meal']=='breakfast',lambda m:-m['p'])
    add('fast-food-breakfast-protein-comparison.html','Fast-food breakfast protein: four exact food portions compared',
        'Compare Chick-fil-A and Starbucks breakfast food by protein, calories, carbohydrate and sodium. Drinks and breakfast extras are excluded.',
        'Compare protein in four tracked fast-food breakfasts',
        'Choose between named breakfast foods without invented prices or extra-drink assumptions.',
        'Four sourced breakfast foods with total protein and density plus a concrete egg-bites versus sandwich calculation.',
        'All breakfast records within the source-inspected release pool; no coffee, hash browns or extra spreads.',rows,
        '<p>Among these four breakfast foods, Chick-fil-A’s Egg White Grill supplies the most protein: <strong>27 g in 300 calories</strong>. Starbucks’ egg-white bites have fewer calories, but their two-bite serving supplies 12 g protein. “Egg white” in the name does not make the portions equivalent.</p>'
        '<h2>Compare one listed food serving</h2><p>The Starbucks bites are one serving of two bites, not one individual bite. Each sandwich or wrap is one standard item. No drink, hash browns or added spread is counted in this table.</p>'+table(rows,('cal','p','c','na'),True)+
        '<h2>What changes between the wrap and sandwich?</h2><p>The Starbucks Spinach, Feta &amp; Egg White Wrap has 20 g protein and 290 calories. Its Turkey Bacon, Cheddar &amp; Egg White Sandwich has 17 g protein and 260 calories. The wrap adds 3 g protein and 30 calories in this comparison, along with 240 mg more sodium. The choice depends on which difference matters to you.</p><p>The Egg White Grill and spinach wrap are close in calories, at 300 and 290, but differ by 7 g protein and 150 mg sodium. These are complete named food items, so that comparison is more useful than comparing their egg ingredients alone.</p>'
        '<h2>Keep the source and local menu in view</h2><p>Breakfast hours and available items can differ by location. The Starbucks figures were returned from indexed official nutrition text; the live page could not be rendered during this check. Confirm the local item before relying on availability. For a coffee or side, use the exact size and preparation listed by the restaurant.</p>'+finder('Browse tracked breakfast foods',meal='breakfast'),category='Restaurant comparisons')

    rows=find(lambda m:m['p']>=25 and m['na'] is not None,lambda m:m['na'])
    add('fast-food-protein-and-sodium.html','High-protein fast food and sodium: compare both numbers',
        'A source-audited comparison of fast-food orders with at least 25 g protein, sorted by sodium and retaining exact servings.',
        'More protein does not always mean less sodium',
        'Compare sodium among protein-containing orders, rather than rank on protein alone.',
        'Paired-constraint analysis with a protein-only portion contrast and an assembled-order contrast.',
        'Protein >=25 g and sodium directly inspected or reproducibly calculated; sorted by sodium.',rows,
        '<p>Chick-fil-A’s eight grilled nuggets provide 25 g protein with 440 mg sodium. Popeyes’ five blackened tenders provide 47 g protein with 1,430 mg sodium. Both meet this page’s protein cutoff, but the portions and sodium totals are quite different.</p>'
        '<h2>Keep protein and sodium on the same row</h2><p>This table contains source-inspected portions with at least 25 g protein and an inspected sodium value. We excluded the twelve-count nuggets from this sodium analysis because their current item page exposed calories, protein, carbohydrate and fat, but did not expose a fresh sodium value in our inspection.</p>'+table(rows,('cal','p','na'))+
        '<h2>Adding a side changes the comparison</h2><p>Panda’s teriyaki chicken entree is 610 mg sodium. Adding its full 10 oz Super Greens base produces a calculated total of 1,270 mg. The greens add 8 g fiber and 8 g protein as well. A useful comparison keeps all of those changes, rather than claiming the combination is lower sodium because it includes vegetables.</p><p>Popeyes’ three tenders with regular red beans and rice contain a calculated 1,440 mg sodium, very close to the five tenders’ 1,430 mg. They are still different orders: 35 g versus 47 g protein, and 7 g versus 1 g fiber.</p>'
        '<h2>Choose your own sodium ceiling</h2><p>This is an order comparison, not advice for a medical sodium restriction. The FDA’s <a href="https://www.fda.gov/food/nutrition-education-resources-materials/sodium-your-diet">sodium guide</a> explains how daily labeling reference values work. A daily reference is not automatically a target for each meal. In the finder, a sodium ceiling excludes records above your chosen amount or without a known sodium value.</p>'+finder('Compare orders with 25 g protein and at most 1,000 mg sodium',minProtein=25,maxSodium=1000),sources=list(dict.fromkeys([u for m in rows for u in m['sourceURLs']]+['https://www.fda.gov/food/nutrition-education-resources-materials/sodium-your-diet'])),category='Nutrition data')

    rows=find(lambda m:m['p']>=20 and m['f'] is not None and m['f']>=7,lambda m:(-m['f'],-m['p']))
    add('fast-food-fiber-and-protein.html','Fast-food fiber and protein: compare beans, bowls and wraps',
        'Selected fast-food orders with at least 20 g protein and 7 g fiber. Compare calories, sodium and the exact included portions.',
        'Fast-food orders that combine fiber and protein',
        'Find an order that meets two nutrients rather than maximize one.',
        'Dual-nutrient collection with ingredient calculations explaining beans and the limits of cross-chain swaps.',
        'Protein >=20 g and fiber >=7 g, with both values source-inspected; sorted by fiber then protein.',rows,
        '<p>Beans, vegetables and some wraps can change a protein-focused order’s fiber total. In the checked records, several bowls and salads contain at least 20 g protein and 7 g fiber. The calories and sodium still vary widely.</p>'
        '<h2>Both nutrients, one defined portion</h2><p>The cutoffs here are collection rules, not a universal meal prescription. We use the fiber published for the exact order or a declared ingredient sum. Unknown fiber does not count as zero and cannot qualify.</p>'+table(rows,('cal','p','f','na'))+
        '<h2>Beans can contribute to both totals</h2><p>Chipotle’s published 4 oz black-bean portion contains 8 g protein and 7 g fiber. Its 4 oz pinto-bean portion contains 8 g protein and 8 g fiber. These ingredients explain part of the bowls’ totals, but a finished bowl also includes its rice, protein, toppings and serving choices.</p><p>The Sofritas bowl in this comparison has 24 g protein and 18 g fiber. The listed chicken bowl has 48 g protein and 14 g fiber. They are different builds with different rice choices; this is not a controlled chicken-for-sofritas substitution. Use the separate ingredient figures for that narrower question.</p>'
        '<h2>Look beyond the largest fiber number</h2><p>CAVA’s Falafel Crunch bowl contains 18 g fiber and 24 g protein in the inspected document, alongside 860 calories and 2,230 mg sodium. The Chick-fil-A wrap has 14 g fiber with its named dressing included. Fiber alone does not establish that every version of either order fits your preferences.</p>'+finder('Set a protein and fiber minimum',minProtein=20,minFiber=7),category='Meal collections')

    veg_keys=['Chipotle||Sofritas Bowl with brown rice and black beans','Chipotle||Veggie Bowl with brown rice, black beans and guacamole',
              'Sweetgreen||Shroomami','Sweetgreen||Super Green Goddess','CAVA||Falafel Crunch bowl','Panera||Greek Salad, whole',
              'Starbucks||Spinach, Feta & Egg White Wrap','Starbucks||Egg White & Roasted Red Pepper Egg Bites']
    rows=sorted(choose(*veg_keys),key=lambda m:-m['p'])
    add('vegetarian-fast-food-protein-comparison.html','Vegetarian fast-food protein: compare eight tracked orders',
        'Compare protein, calories and fiber in tracked meat-free bowls, salads and breakfast foods, with ingredient and source limitations.',
        'Compare protein in tracked meat-free orders',
        'Understand protein differences among existing vegetarian ingredient classifications.',
        'Explicit candidate-order list distinguishes egg/dairy foods from plant-based builds without allergy-safety claims.',
        'Eight source-inspected records with existing editorial vegetarian/plant ingredient classifications. Not newly certified dietary or allergen claims.',rows,
        '<p>A meat-free order can be a sofritas bowl, a vegetable salad or an egg-and-cheese breakfast. Their protein totals differ. In these eight tracked orders, the Sofritas Bowl and Falafel Crunch bowl each contain 24 g protein; the whole Panera Greek Salad contains 8 g.</p>'
        '<h2>Compare the named builds</h2><p>This is a comparison of orders already marked meat-free in GetMacros’ ingredient notes. Nutrition was inspected separately from dietary classification. The numbers do not certify a recipe as vegan, allergy-safe or free from shared-equipment contact.</p>'+table(rows,('cal','p','f','na'))+
        '<h2>Vegetarian is not the same as plant-based</h2><p>The Starbucks wrap and egg bites contain egg and dairy, while Panera’s Greek Salad includes dairy. They are not substitutes for a no-animal-ingredients preference. The Chipotle Sofritas and Veggie rows describe specific rice, bean and vegetable builds with no cheese or sour cream counted; adding either changes that description and the totals.</p><p>The Veggie Bowl includes guacamole, while the Sofritas Bowl includes sofritas and corn salsa. Their equal 620-calorie totals do not mean the recipes are the same: the Sofritas build has 9 g more protein. Do not attribute that difference entirely to one ingredient without checking every component.</p>'
        '<h2>Check the finished order</h2><p>Use the restaurant’s current ingredient and allergen information before ordering for a dietary restriction. Dressings, toppings and local recipe changes matter. GetMacros’ preference filter is a useful starting point for discovery; it is not an assurance from the restaurant.</p>'+finder('Browse the existing meat-free preference',diet='vegetarian'),category='Meal collections')

    rows=choose('Chick-fil-A||Grilled Nuggets, 8 count','Chick-fil-A||Grilled Nuggets, 12 count',
                'Popeyes||3 Blackened Tenders','Popeyes||5 Blackened Tenders','Panda Express||Grilled Teriyaki Chicken')
    add('grilled-and-blackened-chicken-comparison.html','Grilled and blackened fast-food chicken: compare protein portions',
        'Compare exact nugget, tender and teriyaki-chicken portions by protein, calories, fat and sodium without treating them as complete lunches.',
        'Compare grilled and blackened chicken portions',
        'Choose a stand-alone protein portion using total amount and density.',
        'Count versus ounce portions and directly derived per-calorie efficiency, with incomplete sodium explicitly retained.',
        'Five named stand-alone chicken portions from three chains; no bun, rice, greens, biscuit or dipping sauce.',rows,
        '<p>Nuggets, tenders and a teriyaki entree are different serving definitions. The clearest comparison keeps the exact count or weight visible. These are <strong>protein portions</strong>, not five complete lunches.</p>'
        '<h2>Count and weight stay beside the numbers</h2>'+table(rows,('cal','p','fat','na'),True)+
        '<h2>What can you infer from the portion?</h2><p>Eight Chick-fil-A grilled nuggets contain 25 g protein, while twelve contain 38 g. The twelve-count serving is one and a half times the item count, but rounded nutrition values do not have to scale perfectly. Use the restaurant’s separate portion entry when it is available.</p><p>Popeyes’ five blackened tenders contain 47 g protein, compared with 28 g in three. They are blackened, not labeled grilled. Panda’s 6.1 oz teriyaki chicken is a source-defined weight and cannot be turned into an equivalent nugget count.</p>'
        '<h2>Do not forget the rest of the order</h2><p>The Panda figure excludes an extra 1.8 oz teriyaki sauce portion: that separately listed sauce contributes 70 calories and 380 mg sodium. A dipping sauce, bun or side changes another chain’s totals too. Compare the complete order once you have decided what goes with the chicken.</p><p>The twelve-count nuggets’ sodium appears as unavailable here because that nutrient was not exposed in the newly inspected dedicated item page. We have not inferred it from the eight-count serving or presented an older value as freshly checked.</p>'+finder('Compare tracked chicken-containing orders',minProtein=25,sort='protein'),category='Restaurant comparisons')

    tab,rows=ingredient_table('Panda Express',['grilled teriyaki chicken','string bean chicken','orange chicken'])
    add('panda-express-chicken-entree-comparison.html','Panda Express chicken entrees: teriyaki, string bean and orange',
        'Compare source-defined Panda Express chicken portions and see what changes when the same full rice base is added to each.',
        'Compare three Panda Express chicken entrees',
        'Choose among three specific chicken preparations while holding the side constant in worked calculations.',
        'Official entree portion table plus equal-base arithmetic; separates portion totals from recipe claims.',
        'Official full entree portions: teriyaki 6.1 oz, string bean 5.6 oz, orange 6.2 oz. Equal-base example adds one 12 oz white rice portion.',rows,
        '<p>In the inspected U.S. table, Grilled Teriyaki Chicken has 38 g protein and 280 calories, String Bean Chicken has 15 g and 210 calories, and Orange Chicken has 19 g and 560 calories. These are the restaurant’s three different full entree portions.</p>'
        '<h2>Read the entree before adding a base</h2>'+tab+
        '<h2>Hold the rice portion constant</h2><p>Panda’s full 12 oz white-rice base contributes 570 calories, 11 g protein and 129 g carbohydrate. Adding that same source portion to each entree gives these calculated orders:</p><ul><li>Teriyaki chicken plus white rice: <strong>850 calories and 49 g protein</strong>.</li><li>String bean chicken plus white rice: <strong>780 calories and 26 g protein</strong>.</li><li>Orange chicken plus white rice: <strong>1,130 calories and 30 g protein</strong>.</li></ul><p>These are GetMacros sums, not three separately published combo totals. They assume full source-table portions with no other entree, sauce packet or drink. A half-side order is a different calculation.</p>'
        '<h2>A lower-calorie entree is not always the highest-protein one</h2><p>String Bean Chicken has the fewest calories of these three portions, but Teriyaki Chicken has more than twice its protein. Orange Chicken has a different carbohydrate and fat profile as well. The table lets you choose the constraint rather than relying on the word “chicken.”</p><p>For the base decision, <a href="panda-express-base-nutrition-comparison.html">compare rice, chow mein and Super Greens portions</a>. Panda’s separate teriyaki sauce entry is 70 calories per 1.8 oz; it is not silently included in these extra-sauce-free calculations.</p>',sources=[PANDA],related=[{'url':'panda-express-base-nutrition-comparison.html','label':'Compare Panda bases'},{'url':'panda-express-healthy-meals-macros.html','label':'Tracked Panda orders'}])

    bowl_keys=['Chipotle||High Protein-High Fiber Bowl','Chipotle||Chicken Bowl with white rice and black beans',
               'Chipotle||Sofritas Bowl with brown rice and black beans','Chipotle||Veggie Bowl with brown rice, black beans and guacamole',
               'CAVA||Greek Salad bowl','CAVA||Falafel Crunch bowl','CAVA||Chicken + Rice bowl','CAVA||Harissa Avocado bowl',
               'Sweetgreen||Chicken Pesto Parm','Sweetgreen||Harvest Bowl','Sweetgreen||Shroomami']
    rows=sorted(choose(*bowl_keys),key=lambda m:m['cal'])
    add('restaurant-bowl-nutrition-comparison.html','Restaurant bowl nutrition: compare complete listed builds',
        'Compare selected Chipotle, CAVA and Sweetgreen bowls with exact build descriptions, protein, fiber, sodium and source-date boundaries.',
        'A bowl is a format, not a nutrition target',
        'Compare named grain and vegetable bowl builds across three supported chains.',
        'Source-audited cross-chain bowl range with explicit complete-build boundaries; no interchangeable base assumptions.',
        'Eleven explicit bowl-format builds at Chipotle, CAVA and Sweetgreen from the release-audited pool; complete named builds, sorted by calories.',rows,
        '<p>The bowls in this table range from Chipotle’s 540-calorie High Protein-High Fiber Bowl to CAVA’s 860-calorie Falafel Crunch bowl. They contain different proteins, bases, toppings and dressings. The word “bowl” does not make their servings comparable by itself.</p>'
        '<h2>Compare the whole named build</h2><p>This is a selected comparison of tracked bowl-format orders, not every bowl offered at each chain. It includes three standard Sweetgreen bowls, four defined Chipotle builds and four named CAVA recipes. Ingredient sums are labeled in the source notes.</p>'+table(rows,('cal','p','c','f','na'))+
        '<h2>Equal calories can conceal different recipes</h2><p>The two 620-calorie Chipotle builds here contain 24 g and 15 g protein. The Sofritas version has corn salsa and sofritas; the Veggie version has guacamole. Both have 18 g fiber in the published-component sums. Their totals do not describe an identical base with only the protein swapped.</p><p>The CAVA Chicken + Rice bowl is 710 calories and 40 g protein in the accessible official document. Sweetgreen’s Harvest Bowl is 760 calories and 40 g protein. Equal protein is useful to know, but it does not establish equal portions or an otherwise identical lunch.</p>'
        '<h2>Start with the recipe you want</h2><p>Choose the named build first, then check the limits that matter to you. Dressings and dips are part of these totals when they are part of the standard recipe. For a customized bowl, use each supported component and its serving amount; do not assume another restaurant’s rice, hummus or chicken has the same nutrition.</p>'+finder('Compare tracked bowls and other main orders',meal='main'),category='Meal collections')

    rows=find(lambda m:m['na'] is not None and m['na']<1000,lambda m:m['na'])
    add('fast-food-under-1000mg-sodium.html','Fast-food portions under 1,000 mg sodium: a sourced shortlist',
        'Selected U.S. portions below 1,000 mg sodium, including sides and main items. Exact servings and excluded extras remain visible.',
        'Tracked fast-food portions below 1,000 mg sodium',
        'Find source-inspected candidates below an explicit order-level sodium ceiling.',
        'Strict sodium cutoff with sides/main-item separation and a zero-sodium rice counterexample.',
        'Known inspected sodium <1,000 mg; includes sides, breakfast and main items, sorted by sodium. Not a regulated low-sodium claim.',rows,
        '<p>The portions below contain fewer than 1,000 mg sodium in the inspected source or explicit component calculation. Some are sides, some are breakfast foods and some are main items. This is a numerical shortlist; it is <strong>not a list of foods certified “low sodium.”</strong></p>'
        '<h2>See what the sodium figure includes</h2>'+table(rows,('cal','p','f','na'))+
        '<h2>A side is not the same as a finished meal</h2><p>Chick-fil-A’s Kale Crunch Side contains 250 mg sodium, while its Grilled Chicken Sandwich contains 765 mg. Adding the two creates a calculated 1,015 mg order, so the combination would not qualify for this page even though both individual items do.</p><p>Panda’s Broccoli Beef with a full white-rice base has a calculated 600 mg sodium because the source lists 600 mg for the beef and 0 mg for that rice portion. Its 760 calories and 28 g protein still need to be considered. An item with less sodium is not automatically a smaller order.</p>'
        '<h2>A strict boundary needs exact numbers</h2><p>Panera’s half Green Goddess Cobb is 990 mg sodium and appears here. Its cup of Homestyle Chicken Noodle Soup is 1,050 mg and does not. Those are source portion totals; an unlisted substitution or added bread would need its own supported value.</p><p>If you have a sodium limit set by a clinician, use that individual guidance and ask the restaurant about the actual preparation. These U.S. source records cannot establish the sodium of a local customized order.</p>'+finder('Browse with a 999 mg sodium maximum',maxSodium=999),category='Meal collections')

    rows=choose('Chick-fil-A||Grilled Nuggets, 8 count','Popeyes||3 Blackened Tenders','Popeyes||5 Blackened Tenders')
    add('chick-fil-a-vs-popeyes-chicken.html','Chick-fil-A grilled nuggets vs Popeyes blackened tenders',
        'Compare three exact chicken portions by protein, calories, fat and sodium, then see a defined side-added calculation without invented swaps.',
        'Grilled nuggets or blackened tenders?',
        'Compare two chains’ distinct chicken-only portions and an explicit side decision.',
        'Specific cross-chain count comparison with total sodium/protein tradeoff and one supported complete-order example.',
        'Eight grilled nuggets versus three or five blackened tenders; no extrapolated equal-weight portions.',rows,
        '<p>Eight Chick-fil-A grilled nuggets have 130 calories and 25 g protein. Three Popeyes blackened tenders have 170 calories and 28 g protein. That is a 40-calorie and 3 g protein difference between the named portions—not between equal weights of chicken.</p>'
        '<h2>Keep the item count visible</h2>'+table(rows,('cal','p','fat','na'))+
        '<h2>Sodium changes more than protein in the smaller portions</h2><p>The eight nuggets have 440 mg sodium; the three tenders have 860 mg. The tenders provide 3 g more protein alongside 420 mg more sodium. Five tenders increase protein to 47 g and sodium to 1,430 mg. A protein-only ranking would leave out a meaningful part of that choice.</p><p>Neither the eight-count nuggets nor the tender portions include a side, drink, biscuit or dipping sauce in these figures. The restaurants use different item shapes and preparations, so we have not invented an equal-weight serving.</p>'
        '<h2>One supported way to build out the order</h2><p>Popeyes’ regular Red Beans &amp; Rice adds 260 calories, 7 g protein, 6 g fiber and 580 mg sodium. With three tenders, the calculated order is 430 calories, 35 g protein, 7 g fiber and 1,440 mg sodium. It is an explicit two-item sum, not a claim about every combo sold at the counter.</p><p>To compare a different finished order, include its exact side and sauce amounts. <a href="chick-fil-a-healthy-meals-macros.html">Review the Chick-fil-A records</a> or <a href="popeyes-healthy-meals-macros.html">review the Popeyes records</a>, then compare the named items in the finder.</p>')

    rows=choose('Chipotle||Chicken Bowl with white rice and black beans','CAVA||Chicken + Rice bowl','CAVA||Greek Salad bowl')
    add('chipotle-vs-cava-chicken-bowls.html','Chipotle vs CAVA chicken bowls: compare defined orders',
        'A defined Chipotle chicken bowl and two published CAVA bowls compared by calories, protein, carbs, fiber and sodium.',
        'Compare a Chipotle chicken bowl with CAVA’s named bowls',
        'Compare actual tracked chicken orders rather than declare a universally healthier chain.',
        'Cross-chain complete-build comparison with precise Chipotle component inventory and CAVA source-edition limit.',
        'One seven-component GetMacros Chipotle build versus two restaurant-published CAVA curated bowl totals; no custom substitutions.',rows,
        '<p>The listed Chipotle chicken bowl contains 650 calculated calories and 48 g protein. CAVA’s Chicken + Rice bowl is 710 calories and 40 g protein in the inspected official document. The 60-calorie and 8 g protein differences belong to these exact builds.</p>'
        '<h2>Three defined orders, not two whole menus</h2>'+table(rows,('cal','p','c','f','na'))+
        '<h2>What is in the Chipotle calculation?</h2><p>The build uses one published portion each of chicken, white rice, black beans, fajita vegetables, corn salsa, tomato salsa and romaine. It contains no cheese, sour cream, guacamole, tortilla or vinaigrette. Adding one of those would create a different comparison.</p><p>CAVA’s figures describe its complete named recipes, including their standard dips, toppings and dressing. We have not replaced those components with Chipotle ingredient values or assumed that a scoop weighs the same at both chains.</p>'
        '<h2>Calorie and sodium comparisons point in different directions</h2><p>The calculated Chipotle build has 1,900 mg sodium, compared with 1,830 mg for CAVA’s Chicken + Rice bowl. The calorie-lower build is not the sodium-lower build. CAVA’s Greek Salad bowl is 585 calories and 37 g protein, so changing the recipe within a chain can matter as much as changing restaurants.</p><p>CAVA’s available document is older than this page’s publication date; its current menu linkage could not be established. Verify the local menu and source before treating these as interchangeable live ordering quotes.</p>'+finder('Compare tracked Chipotle and CAVA orders',minProtein=25),related=[{'url':'chipotle-healthy-meals-macros.html','label':'Chipotle tracked builds'},{'url':'cava-healthy-meals-macros.html','label':'CAVA tracked bowls'}])

    rows=choose('Sweetgreen||Guacamole Greens','Panera||Caesar with Chicken Salad, whole')
    add('sweetgreen-vs-panera-chicken-salads.html','Sweetgreen vs Panera chicken salads: two whole orders compared',
        'Compare whole Guacamole Greens and Caesar with Chicken salads by calories, protein, fat, fiber and sodium, including their standard dressing.',
        'Compare two whole chicken salads',
        'Choose between two fully named salads with dressing included and no half-versus-whole mismatch.',
        'Whole-order cross-chain table with quantified protein/sodium/fiber differences and truthful dressing boundaries.',
        'Sweetgreen Guacamole Greens standard 635 g order versus Panera whole Caesar with Chicken, standard dressing included.',rows,
        '<p>Sweetgreen’s Guacamole Greens is 555 calories with 29 g protein. Panera’s whole Caesar with Chicken is 670 calories with 35 g protein. Panera’s portion has 6 g more protein, but those two values do not tell the whole story.</p>'
        '<h2>Compare whole orders with dressing</h2>'+table(rows)+
        '<h2>What else changes?</h2><p>The Panera salad has 2,620 mg sodium compared with Sweetgreen’s 1,560 mg: a difference of 1,060 mg for the named orders. Sweetgreen’s salad contains 12 g fiber versus 4 g, while Panera’s has 47 g fat versus 32 g. The recipes differ in multiple ingredients; we have not attributed every difference to the dressing or chicken.</p><p>The Sweetgreen source gives a 635 g standard serving. Panera identifies a whole salad. Those labels are retained rather than implying equal weights. Neither row includes an extra side, bakery item or drink.</p>'
        '<h2>Why the half salad is not substituted here</h2><p>Panera’s half Green Goddess Cobb with Chicken is a useful separate option, but replacing a whole Caesar with a half Cobb would change both the recipe and the serving size. This comparison answers the narrower question of two whole named salads.</p><p>If you want dressing on the side or a different topping, ask for the supported nutrition of that specific change. A standard-total table cannot verify an improvised subtraction. <a href="sweetgreen-healthy-meals-macros.html">See the tracked Sweetgreen orders</a> and <a href="panera-healthy-meals-macros.html">the tracked Panera portions</a>.</p>')

    tab,rows=ingredient_table('Panda Express',['super greens base','white rice','fried rice','chow mein','super greens entree'])
    add('panda-express-base-nutrition-comparison.html','Panda Express bases: rice, chow mein and Super Greens portions',
        'Compare full Panda Express bases by calories, carbs, fiber and sodium, with the 10 oz Super Greens base separated from the 3.5 oz entree entry.',
        'Compare Panda Express bases using the right serving',
        'Resolve base-versus-entree Super Greens portion confusion and compare full bases.',
        'Five official serving rows plus reproducible full-base differences; explicitly avoids half-side substitution.',
        'Official full bases: Super Greens 10 oz; rice/chow mein 12 oz; separate 3.5 oz Super Greens entree shown only to distinguish source entries.',rows,
        '<p>The inspected Panda Express table lists <strong>Super Greens twice</strong>: a 10 oz base with 180 calories and a 3.5 oz entree entry with 45 calories. Using the smaller entry for a full base would describe the wrong portion.</p>'
        '<h2>Full bases, plus the separate entree entry</h2>'+tab+
        '<h2>What changes when the base changes?</h2><p>A full Super Greens base is 390 calories below the full white-rice base, but it also contains 112 g less carbohydrate and 660 mg more sodium. White rice is listed with 0 mg sodium; that does not mean an entree served with it has zero sodium.</p><p>Fried rice contains 610 calories compared with white rice’s 570, alongside 810 mg sodium rather than 0 mg. Chow mein has 520 calories and 1,040 mg sodium. If sodium is your main constraint, sorting only by calories would miss that difference.</p>'
        '<h2>Half-and-half needs another calculation</h2><p>This table shows full source-defined portions. It does not assert that a half-side scoop is exactly half the weight served in practice. For an explicit arithmetic model, half of two published full portions can be added, but that remains an assumption until the restaurant supplies the actual serving basis.</p><p>For a complete order, add the exact entree portion to the chosen base. <a href="panda-express-chicken-entree-comparison.html">Compare three chicken entrees with the same rice base</a>. Extra sauce packets and drinks are additional items.</p>',sources=[PANDA],related=[{'url':'panda-express-chicken-entree-comparison.html','label':'Compare chicken entrees'},{'url':'panda-express-healthy-meals-macros.html','label':'Tracked Panda orders'}])

    tab,rows=ingredient_table('Chipotle',['white rice','brown rice','black beans','pinto beans'])
    add('chipotle-rice-beans-nutrition.html','Chipotle rice and beans: compare exact portions and combined totals',
        'Compare Chipotle’s published 4 oz rice and bean portions, including fiber, protein and sodium. See two explicit rice-and-bean sums.',
        'Compare Chipotle rice and bean portions',
        'Understand rice-versus-bean and white-versus-brown numerical differences within one chain.',
        'Equal official 4 oz portion comparison plus two complete component sums, without nutrition equivalence claims.',
        'Four official 4 oz ingredient portions; two separately calculated rice-plus-bean examples.',rows,
        '<p>In Chipotle’s printed U.S. ingredient table, both white and brown rice are 210 calories per 4 oz. Black and pinto beans are 130 calories per 4 oz. Equal rice calories do not mean every nutrient matches.</p>'
        '<h2>Use the same published portion</h2>'+tab+
        '<h2>Two rice-and-bean combinations</h2><p>One white-rice portion plus one black-bean portion totals <strong>340 calories, 12 g protein, 62 g carbohydrate, 8 g fiber and 560 mg sodium</strong>. One brown-rice portion plus one black-bean portion totals <strong>340 calories, 12 g protein, 58 g carbohydrate, 9 g fiber and 400 mg sodium</strong>.</p><p>These are ingredient sums. Neither includes chicken, sofritas, salsa, vegetables, cheese or guacamole. Adding one of those means it is no longer a rice-and-beans-only total.</p>'
        '<h2>Beans are not just another rice serving</h2><p>Both bean portions have 8 g protein, compared with either rice’s 4 g. Pinto beans have 8 g fiber versus black beans’ 7 g in the printed figures. That one-gram difference comes from rounded published portions, not a guarantee about each scoop.</p><p>If you order light rice, write down the assumed portion. A GetMacros half-portion calculation is not a measured counter scoop. The ingredient PDF is printed October 2024, even though its URL contains 2025 and we inspected it during this release.</p><p><a href="chipotle-toppings-nutrition.html">Compare the toppings separately</a>, then use the exact build in the <a href="chipotle-healthy-meals-macros.html">Chipotle order guide</a>.</p>',sources=[CHIP],related=[{'url':'chipotle-toppings-nutrition.html','label':'Compare toppings'},{'url':'chipotle-healthy-meals-macros.html','label':'Tracked Chipotle builds'}])

    tab,rows=ingredient_table('Chipotle',['cheese','sour cream','guacamole','tomato salsa','corn salsa','vinaigrette','fajita vegetables'])
    add('chipotle-toppings-nutrition.html','Chipotle topping nutrition: compare serving sizes and added totals',
        'Compare cheese, sour cream, guacamole, salsas, vinaigrette and vegetables using their own published serving sizes, with worked addition totals.',
        'What do Chipotle toppings add to the order?',
        'Compare real topping portions and their additive effects without calling ingredients bad or zero-calorie.',
        'Different serving-unit reference plus two explicit additions; distinguishes tablespoon guesses from published portions.',
        'Seven published topping portions, with their different oz/fl oz units retained; sums are explicitly arithmetic.',rows,
        '<p>Chipotle’s cheese and sour cream are each 110 calories in the printed table, but cheese is a 1 oz serving and sour cream is 2 oz. Their protein and fat also differ. Compare the portion you plan to add, not just the ingredient name.</p>'
        '<h2>Each topping has its own serving</h2>'+tab+
        '<h2>Two additions you can reproduce</h2><p>One cheese portion plus one sour-cream portion adds <strong>220 calories, 8 g protein, 3 g carbohydrate, 17 g fat and 220 mg sodium</strong>. One guacamole portion plus one tomato-salsa portion adds <strong>255 calories, 2 g protein, 12 g carbohydrate, 22 g fat, 7 g fiber and 920 mg sodium</strong>.</p><p>Those are additions to an existing order, not complete bowl totals. Do not count a topping twice if it is already part of the named recipe you are comparing.</p>'
        '<h2>Small-looking extras can have different roles</h2><p>Tomato salsa is 25 calories per 4 oz but contains 550 mg sodium. Vinaigrette is 220 calories and 850 mg sodium per 2 fl oz. Fajita vegetables contribute 20 calories per 2 oz. None is called “free,” and calories alone do not establish an ingredient’s usefulness or taste.</p><p>For a light or extra portion, the restaurant needs to provide a supported amount, or your calculation must state its assumption. These values describe the printed portions; they do not verify every scoop or local substitution.</p><p><a href="chipotle-rice-beans-nutrition.html">Build the rice-and-bean base first</a> or compare the complete listed orders in the <a href="chipotle-healthy-meals-macros.html">Chipotle guide</a>.</p>',sources=[CHIP],related=[{'url':'chipotle-rice-beans-nutrition.html','label':'Rice and beans'},{'url':'chipotle-healthy-meals-macros.html','label':'Tracked Chipotle builds'}])

    # An original citable snapshot of THIS project, not a representative survey.
    all_chains=len(set(m['chain'] for m in meals)); audited_chains=len(set(m['chain'] for m in pool))
    full_audit=[m for m in pool if all(m.get(k) is not None for k in KEYS)]
    median_cal=statistics.median(m['cal'] for m in full_audit)
    median_p=statistics.median(m['p'] for m in full_audit)
    coverage='<div class="table-wrap" tabindex="0"><table class="comparison-table"><thead><tr><th scope="col">Measure</th><th scope="col">Release snapshot</th><th scope="col">What it describes</th></tr></thead><tbody>'
    for measure,count,meaning in [('Tracked records',len(meals),'Curated orders, sides and defined combinations; not unique menu items across all restaurants.'),
       ('Tracked restaurant names',all_chains,'Distinct chain labels in the central dataset.'),('Source-inspected records in this release',len(pool),'Records with at least some nutrient values inspected at official sources.'),
       ('Chains represented in the source inspection',audited_chains,'Inspection coverage, not a claim about every source or store.'),
       ('Records with all six nutrients inspected or reproducibly calculated',len(full_audit),'Calories, protein, carbs, fat, fiber and sodium.'),
       ('Median calories in the six-nutrient inspection subset',fmt(median_cal),'Includes sides and large combinations; not a typical restaurant meal.'),
       ('Median protein in the six-nutrient inspection subset',fmt(median_p)+' g','A descriptive statistic of this finite inspected subset.')]:
        coverage+='<tr><th scope="row">'+measure+'</th><td>'+str(count)+'</td><td>'+meaning+'</td></tr>'
    coverage+='</tbody></table></div>'
    add('fast-food-nutrition-data-report.html','GetMacros nutrition data snapshot: coverage, calculations and source limits',
        'An original, reproducible snapshot of GetMacros’ tracked U.S. order dataset, source-inspection coverage, nutrient provenance and exact scope.',
        'The GetMacros restaurant-data snapshot',
        'Cite and understand the original project dataset scope and release-level inspection coverage.',
        'Reproducible coverage counts and descriptive medians, audited ingredient/calculated provenance and source access boundaries.',
        'All central records for coverage counts; source-inspected release subset for six-nutrient medians. No population inference.',pool,
        f'<p>At this release, GetMacros tracks <strong>{len(meals)} selected records across {all_chains} restaurant names</strong>. They include individual foods, sides and explicitly assembled orders. This report makes the size and source boundaries of that working dataset visible; it is not a ranking of the U.S. restaurant market.</p>'
        '<h2>What the snapshot covers</h2>'+coverage+
        '<h2>Published totals and calculated totals are different evidence</h2><p>A standard Sweetgreen bowl uses the restaurant’s published complete recipe total. A named Chipotle build can use sums of published ingredient portions. The High Protein Menu’s published calories, protein and fiber remain separate from GetMacros’ component calculations for other nutrients. Summing rounded component values can differ from a separately rounded complete-order figure.</p><p>Panda combinations use full entree and base portions from its table. In particular, the 10 oz Super Greens base and 3.5 oz entree entry are distinct records in that source. No missing fat value is inferred from a calorie equation.</p>'
        '<h2>Why these medians are not a typical lunch</h2><p>The inspected subset contains small sides, breakfast foods and large multi-entree combinations. It was selected by source accessibility and relevance to this release, not random sampling. The medians describe those records only. They cannot establish what Americans eat, the average menu item, the healthiest chain or the portion available at your local restaurant.</p>'
        '<h2>Dates and access are part of the record</h2><p>October 3, 2026 is the inspection and publication date. It is not the publication date of every source. Panera’s guide is effective September 2, 2026; Popeyes’ PDF is labeled September 2026; Chipotle’s ingredient PDF is printed October 2024. CAVA’s current document linkage could not be established. Starbucks nutrition was visible in indexed official text but not a rendered live table during this inspection.</p><p>The twelve-count nuggets were verified for four nutrients only. Two large Chick-fil-A combinations were not newly recalculated because their exact side portions were not reverified. These limitations remain recorded rather than being hidden behind a global “updated” label.</p>'
        '<h2>How to cite this analysis</h2><p>Cite “GetMacros restaurant-data snapshot, October 3, 2026,” this page’s URL and the exact statistic used. Name the subset and units. For a restaurant nutrient claim, cite the restaurant source as well; this report does not replace its serving definitions or local ordering information.</p><p><a href="sources.html#restaurant-method">Read the site’s calculation methodology</a> or <a href="sources.html">follow the restaurant source links</a>. No complete source documents, branded imagery or bulk restaurant-data export are republished here.</p>',category='Nutrition data')
    return pages, audited, central

def verify(pages,audited,central,require_applied=False):
    slugs=[p['slug'] for p in pages]
    assert len(pages)==18 and len(set(slugs))==18
    changes=[]
    provenance=__import__('meal_provenance').read(ROOT/'js/meal-provenance.js')
    for key,m in audited.items():
        for nutrient,proof in m['provenance'].items():
            if nutrient=='fat':
                if provenance[key].get('fat')!=m.get('fat'):changes.append({'recordKey':key,'nutrient':nutrient,'before':provenance[key].get('fat'),'audited':m.get('fat')})
                continue
            if central[key].get(nutrient)!=m.get(nutrient): changes.append({'recordKey':key,'nutrient':nutrient,'before':central[key].get(nutrient),'audited':m.get(nutrient)})
    for p in pages:
        assert p['sourceURLs'] and p['originalUtility'] and p['criteria']
        assert '<h1' not in p['body'] and '<main' not in p['body']
        assert p['body'].count('<table')==p['body'].count('</table>')
        assert p['body'].count('<h2>')>=4
        for key in p['recordKeys']: assert key in audited
        for link in re.findall(r'href="([^"]+)"',p['body']):
            link=html.unescape(link)
            if link.startswith(('https:','http:','#')): continue
            route=link.split('?')[0].split('#')[0]
            assert route in slugs or (ROOT/route).exists(), f'{p["slug"]}: broken link {route}'
        for fact in p['tableFacts']:
            if fact['recordKey']:
                assert all(fact['values'].get(k)==audited[fact['recordKey']].get(k) for k in KEYS)
    if require_applied: assert not changes, 'Central records need the audited patch: '+json.dumps(changes,ensure_ascii=False)
    return {'pages':len(pages),'uniqueSlugs':len(slugs),'tableFactRows':sum(len(p['tableFacts']) for p in pages),
       'sourceInspectedRecords':len(audited),'centralValuesPending':changes,'checks':['Unique page intents supplied for editorial review','Balanced tables and section headings','Internal body links resolve locally or within batch','Table rows match audited source values','No missing nutrient replaced by zero'],
       'notPerformed':['Visual/browser review of the final integrated pages','Live ordering/menu availability verification','Legal determination of numerical fact/database reuse in each jurisdiction']}

def build():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--require-applied',action='store_true')
    args=parser.parse_args()
    patch=source_patch()
    pages,audited,central=resources(patch)
    result=verify(pages,audited,central,args.require_applied)
    (ROOT/'tools/release_collections.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'data-resource-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'data-publication-manifest.json').write_text(json.dumps({'date':DATE,'market':'U.S.','datasetSHA256':hashlib.sha256((ROOT/'js/meal-data.js').read_bytes()).hexdigest(),
        'poolDefinition':'Release-inspected records; twelve-count nuggets fiber and sodium remain unavailable for this research subset.',
        'resources':[{k:p[k] for k in ('slug','intent','originalUtility','criteria','recordKeys','sourceURLs','claims','tableFacts')} for p in pages]},ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'data-query-map.json').write_text(json.dumps([{'route':p['slug'],'intent':p['intent'],'uniqueValue':p['originalUtility'],'nextAction':p['related'],
        'date':DATE,'locale':'Search locale not confirmed; source nutrition scope U.S.','measurement':'Qualitative opportunity, no volume/ranking metric'} for p in pages],ensure_ascii=False,indent=2),encoding='utf-8')
    calculations=[]
    def calculation(route,label,components,facts,expected):
        actual=summed(components,facts)
        assert actual==dict(zip(KEYS,expected)),(label,actual,expected)
        calculations.append({'route':route,'label':label,'method':'Sum of rounded official portion values; not a separately published combo total',
            'components':[{'item':name,'count':amount,'values':values(facts[name])} for name,amount in components], 'results':actual})
    for name,expected in [('grilled teriyaki chicken',(850,49,142,0,610,9)),('string bean chicken',(780,26,144,3,600,10)),('orange chicken',(1130,30,192,1,1000,25))]:
        calculation('panda-express-chicken-entree-comparison.html',name+' with full white-rice base',[(name,1),('white rice',1)],PANDA_INGREDIENTS,expected)
    calculation('chipotle-rice-beans-nutrition.html','white rice and black beans',[('white rice',1),('black beans',1)],CHIP_INGREDIENTS,(340,12,62,8,560,5.5))
    calculation('chipotle-rice-beans-nutrition.html','brown rice and black beans',[('brown rice',1),('black beans',1)],CHIP_INGREDIENTS,(340,12,58,9,400,7.5))
    calculation('chipotle-toppings-nutrition.html','cheese and sour cream',[('cheese',1),('sour cream',1)],CHIP_INGREDIENTS,(220,8,3,0,220,17))
    calculation('chipotle-toppings-nutrition.html','guacamole and tomato salsa',[('guacamole',1),('tomato salsa',1)],CHIP_INGREDIENTS,(255,2,12,7,920,22))
    assert audited['Chick-fil-A||Grilled Chicken Sandwich']['na']+audited['Chick-fil-A||Kale Crunch Side']['na']==1015
    assert audited['Panera||Caesar with Chicken Salad, whole']['na']-audited['Sweetgreen||Guacamole Greens']['na']==1060
    (OUT/'data-derived-calculations.json').write_text(json.dumps({'date':DATE,'calculations':calculations,
        'otherCheckedDifferences':['Grilled Chicken Sandwich plus Kale Crunch sodium =1015mg','Whole Caesar with Chicken minus Guacamole Greens sodium =1060mg'],
        'ratioMethod':'Protein g / calories ×100; rank before rounding, display one decimal'},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='centralValuesPending'},ensure_ascii=False))
    print(f'{len(result["centralValuesPending"])} central nutrient values still differ from audited release facts.')

if __name__=='__main__': build()
