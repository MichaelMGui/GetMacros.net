"""Reconcile evidence after running the browser suites; never equate capture with review."""
from pathlib import Path
import csv,json,re,statistics
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/redesign'
# Screenshots actually viewed during this task, including corrective rechecks.
review={
 'index.html':['light 390','light 1440','dark 1440','home state light 1440','navigation state light 390'],
 '404.html':['dark 1440','light 390'],
 'about.html':['light 390','dark 1440'],
 'articles.html':['light 1440','dark 390'],
 'blog.html':['light 390','light 1440'],
 'budget-meal-builder.html':['dark 390 after illustration fix','light 1440'],
 'calculators.html':['light 390','light 1440','calculated results dark 390 after hierarchy fix'],
 'carbohydrate-label-portion-tool.html':['dark 390'],
 'chipotle-healthy-meals-macros.html':['dark 1280','dark 1440 after form layout fix'],
 'contact.html':['light 1440','dark 390'],
 'healthy-fast-food.html':['light 390'],
 'high-protein-foods-list.html':['light 1440'],
 'how-to-read-a-nutrition-label.html':['light 1280'],
 'nutrition-label-comparison-tool.html':['light 390 after comparison grid fix'],
 'privacy.html':['dark 1440','light 390'],
 'protein-value-calculator.html':['dark 1440 after numeric layout fix'],
 'recipe-macro-scaler.html':['light 1440 after numeric layout fix'],
 'restaurant-meal-guides.html':['dark 1440 after name/count layout fix'],
 'restaurant-meal-finder.html':['light 1440 initial quiz','light 390 filtered results','dark 1440 no-match state'],
 'search.html':['dark 390','light 1440'],
 'serving-size-vs-portion-size.html':['dark 390 after header height fix'],
 'sources.html':['dark 390','dark 1440'],
 'sodium-label-comparison-tool.html':['dark 390 calculated output'],
 'sweat-rate-calculator.html':['dark 390 calculated output'],
 'weight-goal-timeline-calculator.html':['light 1440'],
}
(OUT/'visual-review.json').write_text(json.dumps({'date':'2026-09-23','method':'Human visual interpretation of rendered screenshots through image tools; dimensions/themes below are actual reviewed representatives. Other routes were captured and automatically checked, not manually inspected.','pages':review},indent=2),encoding='utf-8')
checks=json.loads((OUT/'render-checks.json').read_text(encoding='utf-8'))
assert checks['checks']==740 and not checks['failures']
with (OUT/'coverage.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
for r in rows:
 if r['template']=='development artifact':continue
 file=r['route'].lstrip('/') or 'index.html'
 r['visual_status']='Visually inspected: '+ '; '.join(review[file]) if file in review else 'Automated render checked; shared family reviewed; this individual page not manually inspected'
 r['copy_status']='Authored corpus reviewed; useful sourced language retained; see copy-review.md'
 r['SEO_status']='Metadata/canonical/sitemap/internal-link checks passed; intent mapped; no current ranking data'
 r['responsive_status']='Passed 320/390/768/1024/1440 in light and dark; see render-checks.json'
 r['interaction_status']='Shared keyboard/navigation/theme tested; route runtime and labels checked'
 if r['template'] in ['finder','calculator','calculator-hub','search','contact','meal-ideas','home']:
  r['interaction_status']+='; relevant functional journey exercised'
 if r['template']=='restaurant':r['interaction_status']+='; shared chain finder exercised on Chipotle, all chain data/source labels validated'
 r['verification_performed']='10 route renders; H1, overflow, header clipping, images, controls, runtime; 3876-link site audit; '+('visual review logged' if file in review else 'no individual visual-review claim')
 r['remaining_issues']='Production/CDN and real-device assistive-technology checks not performed; no new verification of all nutrition sources'
with (OUT/'coverage.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
legacy=[]
for p in sorted(ROOT.glob('*.html')):
 s=p.read_text(encoding='utf-8');styles=re.findall(r'<link[^>]+href="(css/[^"?]+)',s)
 row=dict(route='/'+p.name,styles=styles,inline_styles=len(re.findall(r'<style\b',s)),old_sprites=len(re.findall(r'<symbol\b',s)))
 assert styles==['css/publication.css'] and row['inline_styles']==0 and row['old_sprites']==0,row
 legacy.append(row)
(OUT/'legacy-audit.json').write_text(json.dumps({'pages':legacy,'removed_stylesheets':34,'policy':'One active replacement stylesheet; inactive historical generators and development previews are preserved but excluded from publication. No data/application script deleted.'},indent=2),encoding='utf-8')
before=json.loads((OUT/'performance-before.json').read_text(encoding='utf-8'))['results'];after=json.loads((OUT/'performance-after.json').read_text(encoding='utf-8'))['results'];performance=[]
for page in ['index.html','calculators.html','restaurant-meal-finder.html']:
 a=[r for r in before if r['page']==page];b=[r for r in after if r['page']==page]
 performance.append(dict(page=page,before_lcp_ms=statistics.median(r['lcp'] for r in a),after_lcp_ms=statistics.median(r['lcp'] for r in b),before_resource_bytes=statistics.median(r['bytes'] for r in a),after_resource_bytes=statistics.median(r['bytes'] for r in b),after_max_cls=max(r['cls'] for r in b),after_max_long_task_blocking_ms=max(r['longTasks'] for r in b)))
(OUT/'performance-summary.json').write_text(json.dumps({'scope':'Three cold local lab runs per page; 390px Edge, 4x CPU, 100ms, 1.6Mbps; not field data or INP. See report.md.', 'medians':performance},indent=2),encoding='utf-8')
print('Reconciled',len(rows),'scope entries;',len(review),'visually reviewed representative pages; 73 legacy audits.')
print(json.dumps(performance,indent=2))
