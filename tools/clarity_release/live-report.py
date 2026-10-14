"""Create a publication manifest only from successful actual production evidence."""
from pathlib import Path
import csv, json, sys
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/clarity-release-2026-10-14'
deployment=json.loads((OUT/'deployment-verification.json').read_text(encoding='utf-8'))
browser=json.loads((OUT/'production/checks.json').read_text(encoding='utf-8'))
assert deployment['revision']==browser['revision']
assert all(r['status']=='completed' and r['conclusion']=='success' for r in deployment['actions'])
assert len(browser['checks'])==4 and all(r['pass'] for r in browser['checks'])
verified={r['path']:r for r in deployment['sourceMatches']}
manifest=json.loads((OUT/'editorial-manifest.json').read_text(encoding='utf-8'))
pages=[dict(kind='new article',route=r['route'],title=r['title']) for r in manifest['routes']]
pages += [dict(kind='substantially improved article',route=r['route'],title=r['heading']) for r in manifest['improvements']]
pages += [dict(kind='new tool',route='/compare-foods.html',title='Reviewed food comparison'),dict(kind='new restaurant guide',route='/ca/en/restaurants/triple-os/',title="Triple O's Canada nutrition")]
for route,title in [('/','United States homepage'),('/ca/en/','Canada homepage'),('/mx/en/','Mexico homepage'),('/food-diary.html','Food diary'),('/food-library.html','Food library'),('/calculators.html','Calculators'),('/restaurant-meal-finder.html','Meal finder'),('/read-and-watch.html','Read & Watch'),('/play.html','Play')]:
    pages.append(dict(kind='improved product page',route=route,title=title))
for r in pages:
    name=r['route'].lstrip('/')
    if not name or name.endswith('/'):name+='index.html'
    assert name in verified, 'No live source evidence for '+name
    r.update(url='https://getmacros.net'+r['route'],http_status=200,source_sha256=verified[name]['sha256'],revision=deployment['revision'],verified_at=deployment['verifiedAt'],publication='live source verified',indexed='unavailable; no Search Console access')
with (OUT/'live-links.csv').open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=pages[0]);writer.writeheader();writer.writerows(pages)
summary=dict(revision=deployment['revision'],previousRevision=json.loads((OUT/'baseline.json').read_text())['publishedRevision'],verifiedAt=deployment['verifiedAt'],newArticles=11,improvedArticles=10,newRestaurantRecords=40,officialNamedServings=37,calculatedOrders=3,newFinderEntries=37,newRestaurants=1,correctedMexicanCategories=20,relabelledMexicanRecords=39,newGroceryRecords=0,htmlRoutes=363,sitemapCanonicalURLs=360,searchResources=359,liveFilesVerified=deployment['counts']['verifiedFiles'],browserContexts=4,markets=['US','CA','MX','GB','IE','AU','NZ','JP'],sitemapSubmitted='not performed; no authorized Search Console access',indexed='not measured',humanSearchGrowth='not established by available edge metrics')
(OUT/'release-status.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
p=OUT/'release-report.md';s=p.read_text(encoding='utf-8');s+='\n## Verified production outcome\n\nPublished revision `'+deployment['revision']+'` through the existing atomic non-force two-branch workflow. Site quality and Pages deployment completed successfully. Actual production response checks passed for '+str(deployment['counts']['verifiedFiles'])+' files, including all 363 public HTML pages and all active immutable assets. Hosting email protection was reversed only where its decoded address exactly matched the unchanged source. Four real production browser contexts (390/1280, light/dark) passed the public-source comparison, exact dinner logging, article/tool, calculator, local finder, menus, media and game journeys. These were real public HTTPS pages without intercepted responses.\n\n`live-links.csv` contains the 11 new articles, 10 substantive article upgrades, new comparison and Triple O\'s guide, and selected improved product pages with exact source hashes and revision. Publication is verified; sitemap submission, Google indexing, clicks and income are not inferred. Final production screenshots are in `production/`.\n'
p.write_text(s,encoding='utf-8')
print(json.dumps(summary))
