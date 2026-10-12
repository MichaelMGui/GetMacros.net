"""Late master-release guide generation. Root owns registry/markets integration.

Call build(page) with the shared site renderer after the global-product module.
Only six substantive Canadian guides and a new presence asset are written here.
"""
from pathlib import Path
from html import escape
from urllib.parse import quote
import json
ROOT=Path(__file__).resolve().parents[1]
DATE='2026-10-12'
def e(x):return escape(str(x),quote=True)
def load():return json.loads((ROOT/'tools/master_release/restaurant_records.json').read_text(encoding='utf-8'))
def action(href,text,primary=False):return '<a class="'+('btn btn-primary' if primary else 'text-action')+'" href="'+e(href)+'">'+e(text)+' →</a>'
def values(r,fields=('cal','p','c','fat','f','na')):return ''.join('<td>'+('Unknown' if r.get(k) is None else f'{r[k]:g}')+'</td>' for k in fields)
def table(rows,caption,calorie_only=False):
 fields=('cal',) if calorie_only else ('cal','p','c','fat','f','na')
 headings=['Calories (kcal)'] if calorie_only else ['kcal','Protein (g)','Carbs (g)','Fat (g)','Fibre (g)','Sodium (mg)']
 return '<div class="table-wrap" tabindex="0" role="region" aria-label="Canadian serving '+('calories; other macros unavailable' if calorie_only else 'nutrition')+'"><table'+(' class="calorie-only-table"' if calorie_only else '')+'><caption>'+e(caption)+'</caption><thead><tr><th scope="col">Item / portion</th>'+''.join('<th scope="col">'+x+'</th>' for x in headings)+'</tr></thead><tbody>'+''.join('<tr><th scope="row">'+e(r['name'])+'<small>'+e(r['serving'])+'</small></th>'+values(r,fields)+'</tr>' for r in rows)+'</tbody></table></div>'
def section(title,body):return '<section><h2>'+e(title)+'</h2>'+body+'</section>'
def select(rows,text):return next(r for r in rows if r['name']==text)
def sources(rows,notes):
 source=rows[0]['source'];edition=rows[0]['sourceDate'] or 'not supplied'
 return section('Sources and limits','<p>Source edition: '+e(edition)+'. Table layout and selected rows reviewed October 12, 2026. Retrieval does not mean recipes were independently tested.</p><details class="food-product-details"><summary>Read the source and serving notes</summary><p>'+e(notes)+'</p>'+action(source,'Official nutrition source')+'<p>GetMacros is independent of the restaurant. Local availability, prepared portions and later menu changes can differ. No allergen guarantee is made.</p>'+action('/food-library-sources.html','How source values are recorded')+'</details>')
def guide_specs():
 records=load()['records'];specs=[]
 info={
 'Subway':('Subway Canada nutrition: subs, salads & breakfast','Compare Canadian 6-inch subs, Fresh Fit recipes, wraps, salads, power bowls and breakfast servings using Subway’s June 2026 table.','Choose the recipe as well as the filling. A Fresh Fit sub, Classics sub and wrap with the same protein do not have the same nutrition.'),
 'Domino’s':('Domino’s Canada pizza nutrition: exact small-slice builds','Calculate a small hand-tossed Canadian pizza slice from official crust, sauce, cheese and topping portions. See ingredients and serving limits.','Start with size and crust. This guide builds one-sixth of a small hand-tossed pizza from the Canadian component table.'),
 'Mary Brown’s':('Mary Brown’s Canada nutrition: chicken, sandwiches & sides','Compare source-defined Canadian chicken pieces, Big Mary sandwiches, small sides and exact-order totals from the July 2026 nutrition guide.','Choose the chicken pieces and sides separately. The totals here follow explicit single servings, not an unspecified bucket or combo.'),
 'Booster Juice':('Booster Juice Canada nutrition: smoothie sizes & protein','Compare regular and snack smoothies, protein, total sugars and serving volumes from Booster Juice’s September 2026 Canadian nutrition guide.','Check the drink and the size together. A snack serving is not always exactly half of a regular recipe’s published values.'),
 'Pizza Pizza':('Pizza Pizza Canada calories: small pizza per slice','Compare calories, protein and macros for one-sixth of a 10-inch small Canadian Pizza Pizza pizza. Missing and contradictory fields stay visible.','These values are for one-sixth of a 10-inch small pizza. A walk-in slice and a slice from another size need their own record.'),
 'Pizza Nova':('Pizza Nova Canada calories: in-store slice portions','Look up official Pizza Nova in-store slice calories, understand the serving difference from made-to-order pizzas, and see which macros are unavailable.','The official in-store listing gives calories for one slice. It does not supply the protein, carbs or fat needed for a complete macro comparison.')}
 for chain,(title,desc,intro) in info.items():
  rows=[r for r in records if r['chain']==chain];route=rows[0]['url'];body='<section class="food-app"><header class="food-app-head"><div><h1>'+e(title.split(':')[0])+'.</h1><p>'+e(intro)+'</p></div></header><nav class="food-actions" aria-label="Restaurant tools">'
  if chain!='Pizza Nova':body+=action('/ca/en/find-a-meal/?chain='+quote(chain),'Find an order',True)
  body+=action('/food-diary.html?market=CA','Log a serving')+action('/ca/en/restaurants/','Canadian restaurants')+'</nav>'
  if chain=='Subway':
   examples=[select(rows,x) for x in ['6" Classics Subs — Rotisserie-Style Chicken','6-inch Fresh Fit — Rotisserie-Style Chicken','Classics wrap — Rotisserie-Style Chicken']]
   body+=section('Same protein, different build',table(examples,'Canadian standard recipes; no extra sides or drinks.'))
   body+=section('Logging a footlong','<p>Subway defines a footlong as two 6-inch servings for the listed sub recipes. For the Fresh Fit Rotisserie-Style Chicken example, that gives 900 kcal and 60 g protein. A wrap, bowl or snackwich is not doubled under that rule.</p><p>Salad values include the named vegetables and exclude dressing unless noted. The breakfast groups include their source-listed bread or wrap, egg and cheese assumptions; confirm the exact menu name.</p>')
   body+='<details class="food-product-details"><summary>All '+str(len(rows))+' source recipes</summary>'+table(rows,'June 2026 Canadian selection. Source recipes, not every custom order.')+'</details>'
  elif chain=='Domino’s':
   builds=[r for r in rows if r['category']=='entree'];components=[r for r in rows if r['category']=='component']
   body+=section('Three exact slice builds',table(builds,'GetMacros calculations from rounded official component values.'))
   body+=section('Why the cheese amount changes','<p>The source has one cheese quantity for a cheese-only pizza and another for cheese alongside toppings. Using the cheese-only quantity for a pepperoni pizza would describe a different build.</p><p>For the listed cheese pizza: 120 kcal crust + 5 kcal pizza sauce + 70 kcal regular cheese = 195 kcal per slice. Six matching slices total 1,170 kcal. These are component sums, not a separately published complete-pizza test.</p>')
   body+=action('/ca/en/tools/complete-order/','Build your complete order')
   body+='<details class="food-product-details"><summary>Small hand-tossed components</summary>'+table(components,'Amounts for one-sixth of a small pizza; components are not complete meals.')+'</details>'
  elif chain=='Mary Brown’s':
   featured=[select(rows,x) for x in ['Big Mary','Spicy Big Mary','Side Breast','Thigh','Taters (Small)','Fries (Small)']]
   body+=section('Chicken, sandwiches and small sides',table(featured,'Listed single servings; sauces and drinks are separate.'))
   a=select(rows,'Big Mary');b=select(rows,'Taters (Small)');total={k:sum(r[k] for r in [a,b]) for k in ['cal','p','c','fat','f','na']};total.update({'name':'Big Mary + small Taters','serving':'1 sandwich, 249 g + 1 small Taters, 199 g; no drink'})
   body+=section('A complete-order example',table([total],'GetMacros sums the two listed Canadian servings.')+'<p>This order totals 1,066 kcal and 42.4 g protein before a drink or separate dipping sauce. Keep those extras separate rather than assigning a single number to every combo.</p>')
   body+=section('Why some large orders are absent','<p>The guide gives several large sides and buckets a multi-serving label without an unambiguous total-order denominator. We do not multiply those rows into an invented full bucket. A large-Taters fat value also exceeds its listed mass, and two spicy-tender sodium figures need clarification. These rows are withheld.</p>')
   body+='<details class="food-product-details"><summary>All reviewed single servings</summary>'+table(rows,'Source-defined single portions; ambiguous multi-serving entries excluded.')+'</details>'
  elif chain=='Booster Juice':
   featured=[select(rows,x) for x in ['Strawberry Sunshine (R)','Strawberry Sunshine (S)','Bananas-A-Whey (R)','Ripped Berry (R)','Strawberry Storm (R)',"Nuttin' Better (R)"]]
   body+=section('Size and protein at a glance',table(featured,'Regular (R), 710 mL; snack (S), 355 mL for these smoothies.'))
   body+=section('Total sugar is not added sugar','<p>The guide reports total sugar. It does not split naturally occurring sugar from added sugar, so neither a fruit recipe nor a sorbet-free description establishes a zero-added-sugar or zero-total-sugar value.</p><p>Volume is also not weight: 710 mL is not treated as 710 g. Custom milk, fruit or booster changes need their own published portion information.</p>')
   body+='<details class="food-product-details"><summary>All reviewed smoothies and Mixer recipes</summary>'+table(rows,'September 2026 standard recipes, pages 1–2. Other categories are outside this import.')+'</details>'
  elif chain=='Pizza Pizza':
   body+=section('Small-pizza slices',table(rows,'One slice = 1/6 of a 10-inch small pizza.'))
   body+=section('Two slices versus a whole pizza','<p>For Classic Cheese, one source slice is 180 kcal and 9 g protein. Two matching slices are 360 kcal and 18 g protein; six make a 1,080 kcal pizza with 54 g protein. This multiplication follows the explicit six-slice serving definition.</p>')
   body+=section('Source fields that need clarification','<p>Several saturated-fat cells in the English source are larger than the total-fat value. They remain unknown here; we do not guess a missing decimal. Blank new-product rows are excluded. The source supplies no gram weight for these slices.</p>')
  else:
   body+=section('In-store slice calories',table(rows,'One explicitly labelled in-store slice. Protein, carbs, fat, fibre and sodium are unavailable, not zero.',calorie_only=True))
   body+=section('Why an in-store slice is different','<p>For example, the in-store Cheese slice is listed at 570 kcal. The source also has a separate signature-pizza size table with slice counts, but the retrieved table does not explicitly state its calorie denominator. We do not treat that as an interchangeable slice or a full-pizza total.</p><p>If protein, carb or fat limits matter, this calorie-only listing cannot confirm a match. Choose a complete Canadian record elsewhere, or use the calorie entry while keeping the missing nutrients visible.</p>')
  body+=sources(rows,rows[0]['notes'])+'</section>'
  specs.append({'route':route,'title':title,'description':desc,'body':body,'kind':'restaurant','market':'CA','indexable':True})
 return specs
def build(page):
 presence=json.loads((ROOT/'tools/master_release/restaurant_presence.json').read_text(encoding='utf-8'))
 out=ROOT/'data/restaurant-presence.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(presence,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
 for s in guide_specs():page(**s)
 return guide_specs()
if __name__=='__main__':
 specs=guide_specs();out=ROOT/'docs/master-release-2026-10-12/restaurant-guide-specs.json';out.write_text(json.dumps([{k:v for k,v in s.items() if k!='body'} for s in specs],ensure_ascii=False,indent=2),encoding='utf-8');print('Prepared six substantive Canadian guide specifications; root renderer integration required.')
