"""Presence is independent of whether GetMacros has usable local nutrition."""
from pathlib import Path
from collections import Counter
import json,re
ROOT=Path(__file__).resolve().parents[2]
DATE='2026-10-12'
def slug(s):return re.sub('[^a-z0-9]+','-',s.lower()).strip('-')
def main():
 old=json.loads((ROOT/'js/order-registry.json').read_text(encoding='utf-8'))['records']
 new=json.loads((ROOT/'tools/master_release/restaurant_records.json').read_text(encoding='utf-8'))['records']
 # Stable id merging allows this research step to be rerun after integration.
 records=list({r.get('id') or '|'.join([r['market'],r['chain'],r['name'],r.get('serving','')]):r for r in old+new}.values())
 rows={}
 for r in records:
  key=r['market']+'|'+slug(r['chain'])
  if key not in rows:rows[key]={'id':key,'country':r['market'],'restaurantBrand':r['chain'],'restaurantId':slug(r['chain']),'localOperatingEntity':None,'officialCountryWebsite':r.get('sourceParent') or r['source'],'presence':{'status':'confirmed','evidenceUrl':r.get('sourceParent') or r['source'],'evidenceType':'official explicitly market-scoped menu or nutrition table','observation':'Local-market serving definitions appear in the cited official source. This is not an audit of every branch.','checkedAt':r.get('retrievedAt') or r.get('checked')},'localMenuSource':r.get('sourceParent') or r['source'],'nutritionSources':[],'lastCheckedDate':r.get('retrievedAt') or r.get('checked'),'coverageStatus':'published-selection','nutritionAvailable':True,'finderSupported':False,'trackedRecords':0,'completeMacroRecords':0,'finderRecords':0,'calculatedOrders':0,'caloriesOnlyRecords':0,'sourceRetrievalIsVerification':False,'limitations':'Tracked source selection, not a complete live menu or local-stock guarantee.'}
  row=rows[key];row['trackedRecords']+=1
  full=all(r.get(k) is not None for k in ['cal','p','c','fat'])
  row['completeMacroRecords']+=int(full)
  row['finderRecords']+=int(full and r.get('category') not in ['component','sauce'])
  row['calculatedOrders']+=int(r.get('verificationStatus')=='calculated-from-official-components')
  row['caloriesOnlyRecords']+=int(r.get('cal') is not None and all(r.get(k) is None for k in ['p','c','fat']))
  if r['source'] not in row['nutritionSources']:row['nutritionSources'].append(r['source'])
  row['finderSupported']=row['finderRecords']>0
  if row['caloriesOnlyRecords']==row['trackedRecords']:row['coverageStatus']='calories-only'

 # Evidence was read in current official pages/search results, October 12.
 # Presence does not imply national availability or complete nutrition access.
 ca=[
 ('McDonald’s','https://www.mcdonalds.com/ca/en-ca.html','https://www.mcdonalds.com/ca/en-ca/full-menu.html','https://www.mcdonalds.com/ca/en-ca/about-our-food/nutrition-calculator.html','Official Canadian menu explicitly limits nutrition to Canadian restaurants. Current calculator API/browser blocked access (403); historical PDFs are not substituted.','McDonald’s Restaurants of Canada Limited'),
 ('Burger King','https://www.burgerking.ca/','https://www.burgerking.ca/menu/','https://www.burgerking.ca/','Official Canadian site offers local store selection. Dynamic local nutrition has not been captured or validated.',None),
 ('Chipotle','https://locations.chipotle.ca/','https://www.chipotle.ca/','https://www.chipotle.ca/nutrition-calculator','Official Canadian directory lists Alberta, British Columbia and Ontario. Canadian component source and current customizations still require review; U.S. bowls are not substituted.',None),
 ('Subway','https://www.subway.com/en-ca/menunutrition/nutrition?MenuCategoryId=684&ProductId=8753','https://www.subway.com/en-ca/','https://media.subway.com/dam/urn:aaid:aem:c0ee4b37-9376-42de-b2d6-2a3ffaadecb1/original/as/CAN_Nutrition_ENG_6_11_26.pdf','June 2026 Canadian edition; source recipes, not all customizations.',None),
 ('Domino’s','https://pizza.dominos.ca/','https://www.dominos.ca/','https://www.dominos.ca/assets/build/market/CA/_en/pdf/Canadian-Nutrition-Guide-Final-Secure.pdf','Official directory lists Canadian stores. August 2025 guide supports selected small hand-tossed components and calculated builds; other sizes are outside this import.',None),
 ('Pizza Nova','https://pizzanova.com/nutrition','https://pizzanova.com/','https://pizzanova.com/nutrition','Official site returned a Toronto Ontario store and current nutrition UI. Explicit in-store slice calories only; macros are unavailable. Signature calorie denominator is not assumed.','Pizza Nova Take Out Ltd.'),
 ('Tim Hortons','https://locations.timhortons.ca/en/locations-list/on','https://www.timhortons.ca/','https://www.timhortons.ca/nutrition-and-allergens','Canadian official location directory. Previously reviewed July 2026 source selections remain; presence check does not refresh their nutrition review date.',None),
 ('A&W Canada','https://www.web.aw.ca/en/locations','https://web.aw.ca/','https://web.aw.ca/en/our-menu','Official Canadian location page. Separate Canadian operating identity; never equated to U.S. A&W.','A&W Food Services of Canada Inc.'),
 ('Harvey’s','https://www.harveys.ca/en/faq.html','https://www.harveys.ca/en/','https://www.harveys.ca/en/nutrition.html','Official FAQ confirms Canadian operating locations. Selected standard products and separate sauces; no assumption that all provinces have branches.',None),
 ('Wendy’s','https://locations.wendys.com/canada','https://order.wendys.com/ca/en/national/menu','https://order.wendys.com/ca/en/national/menu','Official Canada location directory. Dynamic Canadian nutrition requires item-level source review; no U.S. substitution.',None),
 ('KFC','https://www.kfc.ca/','https://www.kfc.ca/','https://www.kfc.ca/nutrition-allergen','Current Canadian menu and nutrition landing page. Browser capture failed with HTTP2 error; older Canadian PDFs are not silently treated as current.',None),
 ('Popeyes','https://www.popeyeschicken.ca/store-locator?callbackUrl=%2Fmenu','https://www.popeyeschicken.ca/menu/','https://www.popeyeschicken.ca/','Official locator displays Brampton and Mississauga addresses. Canadian nutrition has not been verified for this release.',None),
 ('Pizza Pizza','https://www.pizzapizza.ca/restaurant-locator/ontario/toronto/','https://www.pizzapizza.ca/','https://www.pizzapizza.ca/about-us/nutrition/small-pizza/','Official Toronto location and small-pizza table. Blank products and conflicting saturated-fat entries remain incomplete.',None),
 ('Starbucks','https://stories.starbucks.ca/customer-experience/','https://www.starbucks.ca/','https://www.starbucks.ca/menu','Official Canada publication describes Canadian coffeehouses and current products. Exact Canadian drink builds and milk/customization values remain unverified.',None),
 ('Dairy Queen','https://www.dairyqueen.com/en-ca/locations/','https://www.dairyqueen.com/en-ca/','https://www.dairyqueen.com/en-ca/menu/','Official locator lists Canadian provinces. Separate local product/size nutrient review required.','Dairy Queen Canada, Inc.'),
 ('Taco Bell','https://locations.tacobell.ca/en/index.html','https://www.tacobell.ca/','https://www.tacobell.ca/','Official location directory lists Canadian provinces and Toronto stores. Canada-specific nutrition not yet ingested.',None),
 ('Five Guys','https://restaurants.fiveguys.ca/','https://www.fiveguys.ca/','https://www.fiveguys.ca/menu/','Official directory explicitly lists restaurants in Canada. Older Canadian ingredient guide located; current edition not validated.',None),
 ('Mary Brown’s','https://marybrowns.com/','https://marybrowns.com/menu/','https://marybrowns.com/wp-content/uploads/Mary-Browns-Allergen-and-Nutritionals-July-2026.pdf','Official menu links July 2026 download. Selected clear single servings only; contradictory and ambiguous rows withheld.','Mary Brown’s Inc.'),
 ('Mucho Burrito','https://locations.muchoburrito.com/en-ca','https://muchoburrito.com/menu/','https://muchoburrito.com/nutrition/','Official locator shows Alberta and Saskatchewan branches. Nutrition calculator located but selected ingredient values not verified.',None),
 ('Quesada','https://quesada.ca/mexican-restaurant/','https://quesada.ca/','https://quesada.ca/','Official locator lists Alberta locations and nutrition link. A 2025 ingredient guide is not a substitute for complete numeric nutrition.',None),
 ('Osmow’s','https://locations.osmows.com/ca','https://osmows.com/','https://osmows.com/','Official Canada location directory. Historical source tables have unresolved portion/edition issues; current local nutrition pending.',None),
 ('Pita Pit','https://pitapit.ca/find-a-restaurant/','https://pitapit.ca/','https://pitapit.ca/','Official Canadian address list. Current Canadian standard recipe and nutrient tables pending.',None),
 ('Booster Juice','https://boosterjuice.com/en-ca/pages/our-story','https://boosterjuice.com/en-ca/','https://cdn.shopify.com/s/files/1/0673/9371/6482/files/2026-09-NutritionGuide-ENG.pdf?v=1788534813','Canadian site’s actual footer links September 2026 nutrition edition. Selected regular/snack drinks; volume is not treated as mass.',None),
 ('New York Fries','https://www.newyorkfries.com/locations-new','https://www.newyorkfries.com/','https://www.newyorkfries.com/','Official locator distinguishes Canadian from overseas stores. Canadian nutrition not verified; U.S. site values are not substituted.',None),
 ('Freshii','https://freshii.com/enjoy-freshii-for-longer/','https://freshii.com/','https://freshii.com/wp-content/uploads/2024/03/NA-Guide-EN_compressed.pdf','Official site lists Canadian addresses. North America PDF located but regional recipe equivalence/current edition not verified.',None)
 ]
 for brand,presence,website,nutrition,note,entity in ca:
  key='CA|'+slug(brand);row=rows.get(key)
  if row is None:
   row={'id':key,'country':'CA','restaurantBrand':brand,'restaurantId':slug(brand),'nutritionAvailable':True,'finderSupported':False,'trackedRecords':0,'completeMacroRecords':0,'finderRecords':0,'calculatedOrders':0,'caloriesOnlyRecords':0,'nutritionSources':[nutrition],'coverageStatus':'local-nutrition-review-pending','sourceRetrievalIsVerification':False};rows[key]=row
  row.update({'localOperatingEntity':entity,'officialCountryWebsite':website,'localMenuSource':website,'presence':{'status':'confirmed','evidenceUrl':presence,'evidenceType':'current official local operating page/location directory','observation':note,'checkedAt':DATE},'lastCheckedDate':DATE,'limitations':note})
  # A generic homepage alone is not evidence of complete published nutrients.
  if not row['trackedRecords']:row['nutritionAvailable']=brand in ['McDonald’s','Chipotle','Wendy’s','KFC','Mucho Burrito','Quesada','Five Guys','Freshii'];row['nutritionSourceStatus']='located-not-verified' if row['nutritionAvailable'] else 'not-yet-verified'
  else:row['nutritionSourceStatus']='reviewed-selection'
 payload={'schemaVersion':1,'checkedAt':DATE,'scope':'Published menu coverage plus researched Canadian operating presence; no assumption of national branch availability.','statusMeaning':{'presence':'Official evidence that the chain operates locally.','nutritionAvailable':'A country-specific nutrition resource was located, not a claim that it was fully verified.','finderSupported':'At least one locally sourced record with complete calories, protein, carbs and fat supports browsing.','calories-only':'Exact documented calories may be logged, but macro-constrained matching is unavailable.'},'relationships':sorted(rows.values(),key=lambda r:(r['country'],r['restaurantBrand']))}
 (ROOT/'tools/master_release/restaurant_presence.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Presence relationships:',len(rows),'Canada:',sum(r['country']=='CA' for r in rows.values()))
if __name__=='__main__':main()
