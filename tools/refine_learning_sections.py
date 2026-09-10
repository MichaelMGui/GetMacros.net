"""Give the basics library and blog distinct article lists and navigation labels."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
def decorate_basics(s):
 s=re.sub(r'(<body[^>]*class=")([^"]*)',lambda m:m[1]+m[2]+(' basics-page' if 'basics-page' not in m[2] else ''),s,count=1)
 icons=['<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/>','<path d="M4 3v7c0 3 5 3 5 0V3M6.5 3v18M18 3v18M18 3c-5 3-5 9 0 9"/>','<path d="M12 3s7 8 7 12a7 7 0 0 1-14 0c0-4 7-12 7-12Z"/>','<path d="M19 4C9 4 5 9 6 15c1 5 9 6 11-1 1-3 2-7 2-10ZM5 21l9-12"/>','<path d="M7 5v14M17 5v14M4 9h3m10 0h3M4 15h3m10 0h3M9 8v8m6-8v8"/>','<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 8h6M9 12h6M9 16h4"/>']
 if 'class="learning-icon"' not in s:
  count=[0]
  def section(m):
   i=count[0];count[0]+=1
   icon='<span class="learning-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'+icons[i%len(icons)]+'</svg></span>'
   return m[0].replace('<h2>',icon+'<h2>',1)
  s=re.sub(r'<section class="guide-group data-section"[^>]*><div class="container"><div class="section-head"><h2>',section,s)
 s=re.sub(r'<nav class="guide-start".*?</nav>','<nav class="guide-start" aria-label="Choose a topic"><a href="#macros-and-goals">Calories &amp; macros</a><a href="#eating-out">Eating out</a><a href="#labels-and-recipes">Labels &amp; recipes</a></nav>',s,flags=re.S)
 return s

def run():
 for p in ROOT.glob('*.html'):
  s=p.read_text(encoding='utf-8')
  s=s.replace('<strong>Nutrition Guides</strong><small>Clear, practical explainers</small>','<strong>Nutrition basics</strong><small>Calories, macros and food labels</small>')
  s=s.replace('<strong>GetMacros Blog</strong><small>New evidence and ideas</small>','<strong>GetMacros Blog</strong><small>Research and common questions</small>')
  s=s.replace('href="articles.html">Nutrition guides</a>','href="articles.html">Nutrition basics</a>')
  if p.name=='articles.html':
   s=re.sub(r'<section class="guide-group data-section"><div class="container"><div class="section-head"><h2>Featured guides</h2>.*?</section>','',s,flags=re.S)
   s=s.replace('Nutrition Guides','Nutrition basics').replace('Nutrition guides for everyday questions','Nutrition basics, made simple')
   s=s.replace('Clear, sourced guides about calories, protein, food labels, training and eating out. Start with the question you need answered.','Learn how to set your macros, read food labels and plan everyday meals. Choose a topic to get started.')
   s=decorate_basics(s)
  if p.name=='blog.html':
   s=s.replace('Practical answers about fast food, protein and everyday nutrition.','A closer look at protein myths, diet drinks, creatine and restaurant choices—what the evidence says and what it means for you.')
   s=s.replace('Read the latest','Explore the articles').replace('Browse all guides','Learn the basics')
   s=s.replace('Looking for a specific nutrition answer? <a href="articles.html">Browse all nutrition guides</a>.','New to calories and macros? <a href="articles.html">Start with nutrition basics</a>.')
  p.write_text(s,encoding='utf-8')
 # The hubs must have separate editorial lists, not the same cards under new headings.
 guides=(ROOT/'articles.html').read_text(encoding='utf-8').split('<main',1)[1].split('</main>',1)[0]
 blog=(ROOT/'blog.html').read_text(encoding='utf-8').split('<main',1)[1].split('</main>',1)[0]
 guide_links=set(re.findall(r'<a class="guide-card" href="([^"]+)"',guides))
 blog_links=set(re.findall(r'<a class="blog-card guide-card" href="([^"]+)"',blog))
 assert len(blog_links)==5 and len(guide_links)>20
 assert not guide_links & blog_links, 'Basics library repeats blog articles'
if __name__=='__main__':run()
