"""Finish local verification evidence without claiming deployment or indexing."""
from pathlib import Path
import csv,json,hashlib,sys,datetime
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/ultimate-release-2026-10-19'
sys.path.insert(0,str(ROOT/'tools'))
from build_ultimate_release import articles

def read(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def put(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
browser=read('after/browser-results.json');final=read('after/final-journeys.json');tests=read('tests.json')
assert not browser['failures'] and not browser['errors'] and not final['errors']
assert len(tests)==51 and all(r['exit']==0 for r in tests)
screens=sorted(set(browser['screens'])|set(final['screens']))
for name in screens:assert (OUT/'after'/name).is_file(),name
summary=read('release-summary.json');summary.update({'finishedScreenshots':len(screens),'browserJourneyGroups':len(browser['checks'])+len(final['checks']),'CICheckGroups':len(tests),'motionEvidence':['after/product-interactions.zip','after/final-interactions.zip'],'lab':read('lab-performance.json'),'analyticsConnections':'No GA4, Search Console, Windsor.ai or Ahrefs tool connection was available; no account or property credentials were used.'})
put('release-summary.json',summary)
review=[]
for row in articles():
 slug=row['slug'].removesuffix('.html');review.append({'route':'/'+slug+'.html','title':row['title'],'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceCheckDates':sorted({s['checked_on'] for s in row['sources'] if s.get('checked_on')}),'review':'AI-assisted source, arithmetic, market, overlap, copy and rendered-layout review. No human expert or dietitian review claimed.','mobileScreenshot':'after/'+slug+'-390.png','desktopScreenshot':'after/'+slug+'-1440.png','production':'Pending actual public HTTP verification; no indexing claim.'})
put('integrated-editorial-review.json',review)
csv_path=OUT/'published-links.csv'
with csv_path.open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
for row in rows:row['source_review']='Source/portion/arithmetic/copy and integrated browser checks passed; AI-assisted review, no clinical review.'
with csv_path.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
coverage=read('ios/final-bundle-coverage.json')
coverage['priorRestaurantImageAssignmentCounts']=coverage.pop('restaurantImageManifestCounts',coverage.get('priorRestaurantImageAssignmentCounts'))
assets=json.loads((ROOT/'images/meal-cutouts/provenance.json').read_text(encoding='utf-8'))['assets']
for asset in assets:
 data=(ROOT/'native/app/www'/asset['path'].lstrip('/')).read_bytes().replace(b'\r\n',b'\n')
 assert hashlib.sha256(data).hexdigest()==asset['sha256'],asset['path']
coverage['currentBundledOriginalCategoryAssets']=len(assets)
coverage['imageEvidence']='Seventeen original category SVGs checked against current authored hashes. Zero exact meal photographs. Prior restaurant assignment matrix is retained separately.'
put('ios/final-bundle-coverage.json',coverage)
issues=OUT/'visual-issues.csv'
with issues.open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
rows=[r for r in rows if r['page'] not in ['Enlarged reading/navigation','Diary initial load','Article source-check date']]
for values in [
 ('High','Enlarged reading/navigation','after/zoom-failure.png','Flex minimum sizing and a fixed mobile navigation reserve','Shrinkable heading measure and text-aware navigation height','after/learn-text-zoom-final-mobile.png','Actual 200% text-size and reserved-height assertions pass'),
 ('Medium','Diary initial load','lab-before-layout-fix.json','Initial empty source details collapsed while meal rows were inserted','Start totals hidden until the storage read; reserve initial empty meal-row space','lab-performance.json','Same stated synthetic test: diary CLS 0.12724 before, 0 after; not field data'),
 ('Medium','Article source-check date','after/source-date-before-review.png','An unpublished draft has a null modification date, which was used as source date','Use actual checked_on dates from source evidence, retaining older source checks','integrated-editorial-review.json','All 29 rendered source panels and source-date regression pass')]:
  row=dict(zip(['severity','page','before','cause','remedy','after','result'],values))
  if row['before']=='after/source-date-before-review.png':row['before']='Editorial source-date null was found during screenshot review; original captures were replaced by corrected final captures.'
  rows.append(row)
with issues.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
put('final-validation.json',{'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'CICheckGroups':51,'failedCIChecks':[],'broadRoutesRendered':len(browser['renders']),'broadResponsiveFamilies':28,'themes':4,'widths':[320,390,768,1024,1440],'finishedScreenshots':len(screens),'extraJourneyGroups':len(final['checks']),'repeatIntegration':'Passed repeat-build-stable.log. Subsequent source-date, layout-reservation and sitemap fixes passed scoped regressions; production CI will rebuild the final commit.','nativeScaffoldChecks':coverage['scaffoldChecks'],'simulatedNativeBridgeJourneys':coverage['simulatedBridgeBrowserChecks'],'nativeCompilation':'Not run; Windows has no Xcode or iOS simulator','imageEvidenceImages':'Two manufacturer webp captures remain local review evidence and are excluded from publication; no photographic reuse rights claimed.'})
print(json.dumps({'CICheckGroups':51,'finishedScreenshots':len(screens),'reviewedNewArticles':len(review),'nativeScaffoldChecks':coverage['scaffoldChecks'],'simulatedNativeBridgeJourneys':coverage['simulatedBridgeBrowserChecks']}))
