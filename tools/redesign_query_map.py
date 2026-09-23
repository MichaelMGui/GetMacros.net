"""Repository-derived intent map. Not keyword-volume or ranking data."""
import csv,json,re
from pathlib import Path
from redesign_inventory import ROOT,OUT,plain
corpus=json.loads((OUT/'copy-corpus.json').read_text(encoding='utf-8'))
rows=[]
for p in corpus:
 text=(ROOT/p['route'][1:]).read_text(encoding='utf-8')
 questions='; '.join(b['text'] for b in p['blocks'] if b['tag']=='h2')
 lead=next((b['text'] for b in p['blocks'] if b['tag']=='p' and not b['text'].startswith(('By ','Published '))),p['h1'])
 family=p['template'];action='Use the meal finder: /restaurant-meal-finder.html'
 if family=='restaurant':value='Specific tracked U.S. orders, included ingredients, nutrition table and official chain sources'
 elif family in ('calculator','calculator-hub'):value='Working numeric inputs, units, validation, results and method notes'
 elif family=='finder':value='83 tracked orders; actual nutrient limits; explicit missing data; side-by-side comparison'
 elif family=='article':value='Source-linked explanation: '+lead;action='Follow the relevant tool, reference or related guide linked in the article'
 elif family in ('trust','legal'):value='Publisher-specific methods, commitments or operational disclosures';action='Contact GetMacros: /contact.html'
 elif family=='error':value='Recovery navigation for an unavailable address';action='Find a meal or search'
 else:value=lead
 query={'home':'healthy fast food meal finder','finder':'find high protein fast food meals','journal':'nutrition questions and restaurant comparisons','search':'On-site search; not a keyword landing page','error':'No search target'}.get(family,p['h1'])
 rows.append({'route':p['route'],'primary_query_or_topic':query,'primary_intent':p['h1'],'supporting_questions':questions,'unique_value':value,'next_action':action,'indexability':'noindex' if re.search(r'<meta[^>]+content="[^"]*noindex',text) else 'indexable','evidence':'Repository content; qualitative research in seo-research.md; no volume estimate'})
alias=dict(next(r for r in rows if r['route']=='/index.html'));alias['route']='/';rows.insert(0,alias)
with (OUT/'query-to-page.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print('Mapped',len(rows),'routes to their existing purpose, supporting questions and next action.')
