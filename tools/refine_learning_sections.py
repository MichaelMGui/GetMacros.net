"""Give the basics library and blog distinct article lists and navigation labels."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
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
