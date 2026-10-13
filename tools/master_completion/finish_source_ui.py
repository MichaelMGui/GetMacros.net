"""Small, checked source edits; do not migrate private diary storage."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def replace(path,old,new):
    p=ROOT/path;s=p.read_text(encoding="utf-8")
    if new in s:return
    if old not in s:raise ValueError("Expected source anchor absent: "+path+" "+old[:80])
    p.write_text(s.replace(old,new,1),encoding="utf-8")

replace("js/food-core.js","sourceOrigin:record.sourceOrigin||null,sourceRelease:",
    "sourceOrigin:record.sourceOrigin||null,license:record.license||null,licenseUrl:record.licenseUrl||null,attribution:record.attribution||null,sourceRelease:")
replace("js/food-core.js","sourceOrigin:s.sourceOrigin,sourceRelease:",
    "sourceOrigin:s.sourceOrigin,license:s.license,licenseUrl:s.licenseUrl,attribution:s.attribution,sourceRelease:")
replace("js/food-core.js","  for(const values of [s.nutrients,s.sourceNutrients])",
    "  for(const key of ['license','attribution'])if(s[key]!=null&&(typeof s[key]!=='string'||s[key].length>1000))bad();\n  if(s.licenseUrl!=null&&!(typeof s.licenseUrl==='string'&&s.licenseUrl.length<2000&&/^https:\\/\\//.test(s.licenseUrl)))bad();\n  for(const values of [s.nutrients,s.sourceNutrients])")
replace("js/food-app.js","form.querySelector('[data-review-flags]').textContent=(record.flags||[]).join(' ');",
    "const flags=form.querySelector('[data-review-flags]');flags.textContent=(record.flags||[]).join(' ');if(record.attribution&&!flags.textContent.includes(record.attribution))flags.append(el('span',' '+record.attribution));if(record.licenseUrl?.startsWith('https://')){const license=el('a',' '+(record.license||'Source license'));license.href=record.licenseUrl;flags.append(license);}")
replace("js/food-app.js","const linked=new URLSearchParams(location.search).get('food');",
    "const publicParams=new URLSearchParams(location.search);if(!diary){const brand=publicParams.get('brand');if(brand&&brand.length<=100){query.value=brand;root.querySelector('[data-food-type]').value='branded';syncSource();search().catch(error);}}const linked=publicParams.get('food');")
replace("js/food-app.js",r"retailer-ca:costco:\d+)|cnf:\d+|order:",
    r"retailer-ca:costco:\d+|off:\d{8,14}:[A-Z]{2})|cnf:\d+|order:")
replace("js/food-portion-compare.js","for(const line of lines(attribution,91))",
    "const extra=items.some(s=>s.sourceId?.startsWith('off-'))?' Contains information from Open Food Facts — ODbL 1.0. https://openfoodfacts.org/ · https://opendatacommons.org/licenses/odbl/1-0/':'';\nfor(const line of lines(attribution+extra,91))")
replace("tools/site_scope.py","    routes.add('how-to-log-food-portions.html')",
    "    routes.add('how-to-log-food-portions.html')\n    routes.add('grocery-food-coverage.html')")
replace("tools/run_food_build.py","files.insert(files.index('refresh_release_search'),'build_master_diary')",
    "files.insert(files.index('refresh_release_search'),'build_master_completion')\nfiles.insert(files.index('refresh_release_search'),'build_master_diary')")
replace("tools/build_site.sh","python3 tools/build_master_diary.py",
    "python3 tools/build_master_completion.py\npython3 tools/build_master_diary.py")
replace("tools/build_master_diary.py",'<a class="text-action" href="/food-library-sources.html">Sources &amp; coverage →</a>',
    '<a class="text-action" href="/grocery-food-coverage.html">Browse brands →</a><a class="text-action" href="/food-library-sources.html">Sources &amp; coverage →</a>')
replace("tools/release_collections.py",
    "Existing official April-2025-named document inspected; no printed publication date established. Current live menu linkage could not be verified. Do not claim this is a new menu edition.",
    "Values come from an official document whose filename refers to April 2025. The document supplies no publication date; its connection to today's menu is unconfirmed.")
replace("tools/growth_release/review-source.py",
    "Sauce inclusion is unresolved: the product page ingredient list includes Honey Roasted BBQ ingredients, while its prose says the sandwich pairs with that sauce. Do not label this 390 kcal row as sauce-free or subtract a packet.",
    "The source lists Honey Roasted BBQ ingredients but also describes the sandwich as paired with that sauce. Whether the published 390 kcal includes it is unclear; a sauce-free total is unavailable.")
p=ROOT/"tools/growth_release/menu-records.json"
s=p.read_text(encoding="utf-8")
old="Sauce inclusion is unresolved: the product page ingredient list includes Honey Roasted BBQ ingredients, while its prose says the sandwich pairs with that sauce. Do not label this 390 kcal row as sauce-free or subtract a packet."
if old in s:
    p.write_text(s.replace(old,"The source lists Honey Roasted BBQ ingredients but also describes the sandwich as paired with that sauce. Whether the published 390 kcal includes it is unclear; a sauce-free total is unavailable."),encoding="utf-8")
print("Source licenses persist in reviewed snapshots; public brand links use bounded packaged searches.")
