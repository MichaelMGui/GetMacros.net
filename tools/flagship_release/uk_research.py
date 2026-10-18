"""Document every named UK candidate and emit integration metadata, not shells."""
from pathlib import Path
import collections,csv,json
import uk_integration as api

ROOT=Path(__file__).resolve().parents[2];DOC=ROOT/'docs/flagship-release-2026-10-18/uk'
DATE='2026-10-18'

META={
 'Nando’s':('https://www.nandos.co.uk/food/menu/','Chicken, regular and large sides, kids’ portions, drinks and Gatwick breakfast. Keep local recipes and optional spices separate.','Current official UK menu includes named dishes and explicit Northern Ireland/Gatwick restrictions.'),
 'LEON':('https://leon.co/menu/','Breakfast until 11am, all-day boxes, salads and named drinks. Compare the published recipe and portion, rather than a generic bowl.','Official UK menu explicitly separates breakfast, all-day, drinks and children’s menus.'),
 'Wagamama':('https://www.wagamama.com/menu','October 7 UK menu recipes, kids’ portions and separate gluten-free menu builds. Extras remain separate.','Official current menu is explicitly named October 7, 2026 UK main website.'),
 'Wendy’s':('https://www.wendys.com/en-gb/','UK burgers, chicken, breakfast, wraps, salads and sides from the March 25 guide. Salad rows include toppings and dressing.','Official UK site and UK nutrition guide identify local menu recipes and breakfast.'),
 'Five Guys':('https://www.fiveguys.co.uk/menu/','Named burgers, fries and shake components. Heathrow-only breakfast stays clearly restricted.','Official UK menu and October 13 linked guide distinguish UK locations and Heathrow breakfast.'),
 'Pepe’s':('https://www.pepes.co.uk/nutrition-allergens-uk','UK grilled and fried dishes, sides and sauce portions. Optional flavour quantities are separate from the base item.','Official source explicitly labels the UK separately from Ireland.'),
 'Starbucks':('https://www.starbucks.co.uk/nutrition-allergens','UK Autumn 2026 food and drinks, with the exact size and milk recipe. Optional cold foam and syrup portions are separate.','Official UK page links current Autumn beverage and food editions.'),
 'Chick-fil-A':('https://www.chick-fil-a.co.uk/locations/','UK sandwich, nugget, side, sauce and drink portions. Serving totals are calculated from the local per-100g sheet.','Official UK directory lists Hamilton, Liverpool, Kingston, Leeds, Templepatrick and Lisburn South.'),
 'Zizzi':('https://www.zizzi.co.uk/menus','UK Autumn 2026 pizzas, pasta, sides, desserts and drinks. Whole pizza servings and ingredient extras stay distinct.','Official menu links a UK guide separately from its Republic of Ireland/Belfast guide.'),
 'ASK Italian':('https://www.askitalian.co.uk/menus','Autumn 2026 core dishes and portions, with per-100g reference values kept separate.','Official UK menu links the current September 10 Autumn guide.'),
 'PizzaExpress':('https://www.pizzaexpress.com/allergens-and-nutritionals','England, Wales and Scotland source recipes. Classic, Romana and Large Classic pizzas differ; breakfast is airport-specific.','Official source separates England/Wales/Scotland, Northern Ireland and three local London editions.'),
 'Tortilla':('https://www.tortilla.co.uk/menu/nutrition-and-allergens','Ingredient allocations for each medium, large and breakfast format. A rice or filling entry is a component, not a complete burrito.','Official UK menu links the September 17 guide and local nutrition calculator.'),
 'Tim Hortons':('https://timhortons.co.uk/menu','October 8 local guide with breakfast, sandwiches, doughnuts and exact drink sizes. Dips stay separate.','Official UK menu links the current UK & Ireland-labelled source; no Republic of Ireland presence inferred.'),
 'Wasabi':('https://www.wasabi.uk.com/menus/','September 17 local guide: sushi, named hot food and portions. Serving calories and calculated macros retain their different source bases.','Official UK menus link Version 34 nutrition information released September 17.'),
 'Caffè Nero':('https://www.caffenero.com/uk/menu','Named milk and size options, breakfast, panini, snacks and drinks. Explicit Northern Ireland recipes stay separate.','Official UK category pages publish named products, with separate Northern Ireland recipes identified.'),
 'Chipotle':('https://www.chipotle.co.uk/nutrition-calculator','UK ingredient portions for building an order. These are not complete bowls, burritos or U.S. recipe substitutions.','The official local nutrition-calculator URL returns a UK per-serving ingredient PDF.'),
 'Chopstix':('https://chopstixnoodles.co.uk/menu/','Named base, topping, side and Mini Stix allocations. Build a box from its actual components and sizes.','All 33 product pages linked by the captured official UK menu were examined.'),
}

OTHER={
 'McDonald’s':('https://www.mcdonalds.com/gb/en-gb/menu.html','https://www.mcdonalds.com/gb/en-gb/product/big-mac.html','official-source-access-incomplete','UK menu and current allergen booklet confirmed. Full macros load through a dynamic service; browser product request was access-denied. No UK macros imported from another country.'),
 'Burger King':('https://www.burgerking.co.uk/responsiblebusiness','https://www.burgerking.co.uk/menu','dynamic-adapter-pending','Official UK responsible-business page describes local menus/nutrition. Captured app is a small dynamic shell; current nutrition report/serving mapping not yet captured and reviewed.'),
 'Popeyes':('https://popeyesuk.com/','https://allergensandnutritions.popeyesuk.com/nutritional-information-table','dynamic-adapter-pending','Official UK source points to a public nutrition platform. Captured request returned an empty array; category/recipe rendering still needs a reviewed adapter. This is incomplete implementation, not proof that nutrition is unavailable.'),
 'Domino’s':('https://corporate.dominos.co.uk/about-us/our-food/allergens-and-nutrition','https://corporate.dominos.co.uk/Media/Default/Corporate%20Responsibility/Food/IngredientsPizzasandToppings.pdf','official-source-access-blocked','Current corporate UK & Ireland nutrition page and linked pizza source found. Direct page and PDF captures returned HTTP403. No U.S. or other-market substitutions imported.'),
 'Pizza Hut':('https://customercare.pizzahut.co.uk/hc/en-gb/articles/36834760768657-Where-can-I-find-nutritional-and-allergen-information-for-a-Pizza-Hut-Restaurant','https://www.pizzahut.co.uk/restaurants/food/nutritional-information/','official-source-access-blocked','Official UK help links local restaurant nutrition; direct destination capture returned HTTP403. Historical June2024 delivery PDF is not relabelled current restaurant nutrition.'),
 'Papa Johns':('https://www.papajohns.co.uk/','https://www.papajohns.co.uk/allergens-and-nutrition','official-local-source-redirect','Official UK menu and nutrition guide are visible through current search. Local page and PDF fetches redirected to the U.S. international site and returned HTML. Not imported as a British menu.'),
 'Shake Shack':('https://www.shakeshack.co.uk/faqs/','https://www.shakeshack.co.uk/menu/allergen-information/','calories-only-and-access-gap','Official current UK FAQ/menu confirms local operation and calorie/allergen resources. Direct current guide capture returned HTTP403. An older 2022 calorie-only PDF is not a current complete-macro menu.'),
 'Taco Bell':('https://www.tacobell.co.uk/locations/','https://www.tacobell.co.uk/nutrition-information/','provider-adapter-and-permission-review-pending','Official UK menu/nutrition page links an external Nutritionix premium provider. Current local serving data and permitted integration still require review; U.S. values are not used.'),
 'Wingstop':('https://www.wingstop.co.uk/','https://www.wingstop.co.uk/content/wingstop-uk-allergen-info-v2.pdf','external-provider-adapter-pending','Official UK location page and guide found. The guide redirects readers to an Andithas location-specific nutrition interface. No unchecked third-party figures imported.'),
 'Jollibee':('https://www.jollibee.uk/faqs','https://www.jollibee.uk/nutritional-info','calories-only-historical-guide','Official FAQ names current UK locations. Current nutrition page links an allergy list and March2023 calorie chart, not a full local macro table. No U.S. nutrition substitution.'),
 'Pret A Manger':('https://www.pret.com/en-GB/allergenguide','https://www.pret.co.uk/en-GB/our-menu','product-adapter-pending','Official page distinguishes England/Scotland/Wales from Ireland/Northern Ireland. Menu categories captured; product-level nutrition extraction and regional serving review remain unfinished.'),
 'Costa Coffee':('https://www.costa.co.uk/sustainability/nutrition','https://www.costa.co.uk/docs/store-allergen-guide.pdf','official-guide-response-incomplete','Official UK nutrition page links store guide. Direct PDF request returned a 940-byte HTML response rather than a PDF. Old October2025–January2026 guide is not declared current.'),
 'itsu':('https://www.itsu.com/menu/','https://www.itsu.com/faq/','product-adapter-pending','Official restaurant menu and nutrition FAQ captured. Menu carries product data in Nuxt serialization; a reviewed per-portion adapter and region check are still required. No third-party menu copied.'),
 'German Doner Kebab':('https://germandonerkebab.com/menu','https://germandonerkebab.com/gb/menu','geographic-source-selection-incomplete','Official menu explicitly states GDK UK. Direct generic homepage redirected to Canada. A UK-specific local-source capture and nutrient-serving review remain unfinished; Canadian values are not substituted.'),
 'Slim Chickens':('https://www.slimchickens.co.uk/locations','https://www.slimchickens.co.uk/','uk-provider-adapter-pending','Official UK location/menu site captured. Its UK menu differs from the detailed U.S. nutrition site; no U.S. macros imported. Local dietary/nutrition interface still needs reviewed extraction.'),
 'Wenzel’s':('https://www.wenzels.co.uk/menu/','https://www.wenzels.co.uk/wp-content/uploads/2026/06/Wenzels_Allergen_Sheet_June_2026.pdf','image-table-extraction-pending','Current official menu and June19 Version07 guide captured. Nutrition page8 is an embedded image; text extraction cannot verify its rows. Reviewed OCR/manual table extraction remains unfinished.'),
}

BASE={
 'Greggs':('https://www.greggs.co.uk/menu','https://a.storyblok.com/f/94904/x/7dd8489dab/nutritional-information.pdf'),
 'KFC':('https://www.kfc.co.uk/nutrition-allergens','https://brand-uk.assets.kfc.co.uk/nutrition-allergens.pdf'),
 'Subway':('https://www.subway.com/en-gb/menunutrition/nutrition','https://www.subway.com/en-gb/menunutrition/nutrition'),
}

def main():
    rows=api.load_batch()['records'];existing=json.loads((ROOT/'js/order-registry.json').read_text(encoding='utf-8'))['records']
    by=collections.defaultdict(list)
    for row in rows:by[row['chain']].append(row)
    defs=[];matrix=[]
    for chain,items in by.items():
        official,description,presence=META[chain];rid=items[0]['restaurantId']
        limits='Reviewed source selection with explicit missing/ambiguous rows withheld. No full current-menu, every-branch, allergen-safety or exact-photo claim. '+description
        defs.append(dict(market='GB',chain=chain,restaurantId=rid,restaurantMarketId='GB|'+rid,slug=rid,
            route='/gb/en/restaurants/'+rid+'/',title=chain+' UK nutrition and menu portions',description=description,
            officialCountryWebsite=official,menuSource=official,presenceSource=official,presenceObservation=presence,
            sources=sorted({r['source'] for r in items}),records=len(items),finderRecords=sum(r['finderSupported'] for r in items),
            categoryCounts=dict(collections.Counter(r['category'] for r in items)),limitations=limits))
        matrix.append(dict(country='GB',restaurant=chain,presence='confirmed',presenceSource=official,
            menuSource=official,nutritionSource=' | '.join(sorted({r['source'] for r in items})),nutritionStatus='reviewed-source-selection',
            baselineRecords=0,newPortions=len(items),newSourceIdentities=len({r.get('productId',r['name'].split(' · ')[0]) for r in items}),
            categoryCoverage=' | '.join(sorted({r['sourceGroup'] for r in items})),exactPhotoAssetsAdded=0,imageRights='no restaurant image-reuse rights inferred',
            lastChecked=DATE,disposition='implemented-with-documented-gaps',remaining=limits))
    for chain,(official,nutri,status,gap) in OTHER.items():
        matrix.append(dict(country='GB',restaurant=chain,presence='confirmed-from-official-local-source',presenceSource=official,menuSource=official,
            nutritionSource=nutri,nutritionStatus=status,baselineRecords=0,newPortions=0,newSourceIdentities=0,categoryCoverage='Not imported',
            exactPhotoAssetsAdded=0,imageRights='not reviewed or acquired',lastChecked=DATE,disposition='not-implemented-specific-gap',remaining=gap))
    for chain,(official,nutri) in BASE.items():
        old=[r for r in existing if r.get('market')=='GB' and r['chain']==chain]
        matrix.append(dict(country='GB',restaurant=chain,presence='previously-confirmed-preserved',presenceSource=official,menuSource=official,nutritionSource=nutri,
            nutritionStatus='existing-reviewed-selection-preserved',baselineRecords=len(old),newPortions=0,newSourceIdentities=0,
            categoryCoverage='Existing named source categories preserved',exactPhotoAssetsAdded=0,imageRights='unchanged',lastChecked=DATE,
            disposition='preserved-not-reverified-whole-menu',remaining='Existing nutrition source editions preserved; this batch does not re-label their older verification date.'))
    matrix.sort(key=lambda r:r['restaurant'].lower())
    assert len(matrix)==36 and len({r['restaurant'] for r in matrix})==36
    (ROOT/'tools/flagship_release/uk_definitions.json').write_text(json.dumps(dict(schemaVersion=1,reviewedAt=DATE,restaurants=defs),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (DOC/'country-restaurant-matrix.json').write_text(json.dumps(dict(reviewedAt=DATE,scope='All35 named UK candidates plus Chick-fil-A from the global queue. Presence, source availability and implementation are different statuses.',relationships=matrix),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with (DOC/'country-restaurant-matrix.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(matrix[0]));w.writeheader();w.writerows(matrix)
    category_rows=[]
    for chain,items in by.items():
        for group in sorted({r['sourceGroup'] for r in items}):
            chosen=[r for r in items if r['sourceGroup']==group]
            category_rows.append(dict(market='GB',chain=chain,sourceCategory=group,stagedNamedPortions=len(chosen),macroComplete=len(chosen),
                sourceScope=' | '.join(sorted({str(r.get('sourceDate') or 'live; edition unavailable') for r in chosen})),
                status='reviewed selection; not whole-business menu completeness',remaining='See withheld.json and source-register.json for excluded/missing rows and source-specific limitations.'))
    with (DOC/'menu-category-completeness.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(category_rows[0]));w.writeheader();w.writerows(category_rows)
    (DOC/'menu-category-inventory.json').write_text(json.dumps(dict(reviewedAt=DATE,scope='Final reviewed source-category selections after audit; not a whole-live-menu completeness claim.',groups=category_rows),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    counts={d['chain']:dict(namedSourceIdentities=next(r['newSourceIdentities'] for r in matrix if r['restaurant']==d['chain']),namedPortions=d['records'],calculatedComposedOrders=0,categoryCounts=d['categoryCounts']) for d in defs}
    (DOC/'chain-counts.json').write_text(json.dumps(counts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(candidateDispositions=len(matrix),newChains=len(defs),preservedChains=len(BASE),unimplementedWithSpecificGaps=len(OTHER),newPortions=len(rows),categoryGroups=len(category_rows)),ensure_ascii=False))

if __name__=='__main__':main()
