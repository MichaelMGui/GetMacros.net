"""Apply a coherent visual family to every page without changing its content."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
ICONS={
 'meal':'<circle cx="12" cy="12" r="8"/><path d="M3 3v6m-2-6v4c0 3 4 3 4 0V3M3 9v12M22 3v18m0-18c-4 3-4 8 0 8"/>',
 'tools':'<rect x="5" y="2" width="14" height="20" rx="3"/><path d="M8 6h8M8 11h2m4 0h2m-8 4h2m4 0h2m-8 4h2m4 0h2"/>',
 'learn':'<path d="M12 6C8 3 4 3 2 4v15c3-1 6-1 10 2 4-3 7-3 10-2V4c-2-1-6-1-10 2Zm0 0v15"/>',
 'site':'<path d="M12 3 3 7v6c0 5 9 9 9 9s9-4 9-9V7l-9-4Z"/><path d="m8 12 3 3 5-6"/>',
 'search':'<circle cx="10" cy="10" r="7"/><path d="m15 15 6 6"/>',
 'contact':'<rect x="2" y="4" width="20" height="16" rx="3"/><path d="m3 6 9 7 9-7"/>'}
def run():
 for p in ROOT.glob('*.html'):
  s=p.read_text(encoding='utf-8');body=re.search(r'<body[^>]*>',s)[0]
  family='tools' if 'tools-page' in body else 'meal' if any(k in body for k in ['restaurant-page','order-match-page','home-studio','flagship-page']) or p.name=='restaurant-meal-guides.html' else 'contact' if p.name=='contact.html' else 'search' if p.name=='search.html' else 'site' if p.name in ['about.html','privacy.html','terms.html','sources.html','accessibility.html','corrections.html','editorial-policy.html','404.html'] else 'learn'
  s=re.sub(r' data-design-family="[^"]+"','',s);s=s.replace('<body','<body data-design-family="'+family+'"',1)
  # Existing food illustrations, logos and calculator artwork already identify those pages.
  if family in ['learn','site','contact','search'] and 'class="page-emblem"' not in s and 'blog-hero-grid' not in s and p.name!='articles.html':
   s=re.sub(r'(<h1\b[^>]*>)', '<span class="page-emblem" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'+ICONS[family]+'</svg></span>\\1',s,count=1)
  if 'restaurant-page' in body and 'class="restaurant-emblem"' not in s:
   logo=p.name.split('-healthy-')[0]
   if (ROOT/'images/restaurant-logos'/f'{logo}.png').exists():
    s=re.sub(r'(<h1\b[^>]*>)','<span class="restaurant-emblem" aria-hidden="true"><img src="images/restaurant-logos/'+logo+'.png" width="48" height="48" alt=""></span>\\1',s,count=1)
  p.write_text(s,encoding='utf-8')
if __name__=='__main__':run()
