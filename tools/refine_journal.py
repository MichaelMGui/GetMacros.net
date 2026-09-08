"""Publish the five revised journal articles at their established URLs."""
from pathlib import Path
import re, json, html, math
ROOT=Path(__file__).resolve().parents[1]
ADDITIONS={
'best-fast-food-restaurants-for-your-goals.html': '''<h2>A fair comparison starts with the same job</h2><p>Compare a snack with a snack and a main meal with a main meal. A side of grilled chicken may have an excellent protein-to-calorie ratio, but that does not make it a complete replacement for a bowl with rice, beans and vegetables. Decide what you need the order to do before comparing its numbers.</p><ol><li><strong>Set the occasion:</strong> a quick snack, a regular lunch or a larger post-training meal.</li><li><strong>Keep the whole order:</strong> count the drink, dressing, sauce and sides you intend to eat.</li><li><strong>Compare two priorities:</strong> for example, protein and calories. Keep fiber and sodium visible as trade-offs.</li><li><strong>Check the exact build:</strong> double meat, a different bread or a sauce swap changes the comparison.</li></ol><p>For a concrete example, Chipotle publishes 46 g protein and 14 g fiber for its High Protein–High Fiber Bowl. Its chicken protein cup has 32 g protein, but is a side rather than the same kind of meal. These are different tools for different appetites. <a href="https://www.chipotle.com/high-protein-meals">Check Chipotle’s named builds and current availability.</a></p><p>The restaurant sections below are starting points drawn from tracked orders, not a test of every menu item or a claim that one chain is healthier overall. Use the <a href="restaurant-meal-finder.html">meal finder</a> to compare the restaurants you can actually reach.</p>''',
'how-much-protein-can-your-body-absorb.html': '''<h2>Turn the evidence into a normal day</h2><p>Suppose you have independently chosen a daily target of 120 g. Three meals containing 40 g each and four meals containing 30 g each both add to 120 g. This is an arithmetic example, not a recommended target for everyone. Neither pattern requires treating a larger dinner as wasted protein.</p><p>Start by checking where your current meals leave gaps. Moving some protein from a very large dinner to a low-protein breakfast may make the day easier to organize. Adding a shake solely because a clock says it is time can be unnecessary if your meals already meet your needs.</p><p>The <a href="https://pubmed.ncbi.nlm.nih.gov/38118410/">2023 post-exercise study</a> measured a response over hours; it did not prove that a 100 g meal is the best everyday strategy for long-term muscle growth. The <a href="https://pubmed.ncbi.nlm.nih.gov/29497353/">per-meal review</a> is useful for understanding distribution, but should not be read as a digestive limit.</p><p>For your next restaurant order, check the meal’s protein against your day as a whole. A larger protein serving is a food-planning choice, not a problem that needs a timer.</p>''',
'are-diet-drinks-bad-for-you.html': '''<h2>Three questions to ask about your own drink</h2><dl><dt><strong>What would I drink instead?</strong></dt><dd>Swapping regular soda for a no-calorie version reduces the sugar and energy in that drink. Replacing water with diet soda does not provide the same benefit. A <a href="https://pubmed.ncbi.nlm.nih.gov/35285920/">meta-analysis of randomized beverage trials</a> found modest benefits when low- or no-calorie drinks replaced sugary drinks in the studied adults; it is not evidence that adding diet drinks improves everyone’s health.</dd><dt><strong>Which ingredient matters to me?</strong></dt><dd>Read the actual label rather than assuming all diet drinks are the same. Sweeteners, caffeine and serving sizes differ. The <a href="https://www.fda.gov/food/food-additives-petitions/aspartame-and-other-sweeteners-food">FDA identifies phenylketonuria as a specific reason to avoid or restrict aspartame</a>.</dd><dt><strong>Am I treating a substitution as a guarantee?</strong></dt><dd>A drink swap is one choice within an eating pattern. The <a href="https://www.who.int/publications/i/item/9789240073616">WHO guideline</a> addresses long-term weight-control policy and is separate from an individual sweetener’s toxicological safety limit.</dd></dl><p>A practical experiment is to change the drink you actually want to replace, then notice whether the choice is enjoyable and sustainable. There is no need to add diet drinks if you already prefer water.</p>''',
'does-creatine-cause-hair-loss.html': '''<h2>What would change the conclusion?</h2><p>A stronger case for harm would need a reproducible difference in hair outcomes, not just a change in a blood hormone or a before-and-after photo without a comparison group. A stronger case for long-term reassurance would need larger studies lasting longer, including people beyond the young resistance-trained men studied so far.</p><p>The <a href="https://pubmed.ncbi.nlm.nih.gov/40265319/">2025 randomized trial</a> provides more direct evidence than the older hormone-only study because it measured hair. Its lack of a significant group difference should be read as a result within that study’s limits, not a guarantee of zero possible risk under every circumstance.</p><p>If you notice a change, write down when it began and any simultaneous changes in illness, stress, medication, eating or training. That history is more useful for a clinician than assuming either that creatine must be responsible or that it cannot be. You can also choose not to use an optional supplement while seeking advice.</p>''',
'calories-vs-macros-what-matters-more.html': '''<h2>Why two plans with the same calories can feel different</h2><p>Consider two hypothetical 2,000-calorie plans. Plan A has 100 g protein, 250 g carbohydrate and about 67 g fat. Plan B has 150 g protein, 200 g carbohydrate and about 67 g fat. Using 4 calories per gram of protein and carbohydrate and 9 per gram of fat, each comes to approximately 2,000 calories; the small difference is rounding.</p><p>Moving 50 g from carbohydrate to protein keeps the arithmetic similar but changes the foods and portions needed. This does not prove that Plan B is better. The useful question is whether either plan suits the person’s protein needs, activity, food preferences and health context.</p><p>You do not need to optimize every number at once. If you are struggling to follow a plan, first identify the actual problem: hunger, inconvenient meals, an unrealistic target, training fatigue or inaccurate portions. A more complicated macro ratio is not automatically the solution.</p><p>The <a href="https://www.niddk.nih.gov/health-information/weight-management/body-weight-planner">NIDDK Body Weight Planner</a> explains why energy needs change over time. Revisit estimates as circumstances change, and use a repeatable eating pattern rather than treating a calculator result as permanent.</p>'''
}
for name,addition in ADDITIONS.items():
 p=ROOT/name;s=p.read_text(encoding='utf-8')
 s=re.sub(r'<!--journal-revision:start-->.*?<!--journal-revision:end-->','',s,flags=re.S)
 # Keep the direct answer first, and insert the practical material before the sources.
 marker=re.search(r'<h2(?: id="[^"]+")?>(?:Sources and (?:limitations|scope)|Method and limitations)</h2>',s)
 if marker:s=s[:marker.start()]+'<!--journal-revision:start-->'+addition+'<!--journal-revision:end-->'+s[marker.start():]
 else:raise ValueError('Missing source section: '+name)
 if name=='best-fast-food-restaurants-for-your-goals.html':
  s=s.replace('<h2>Best for ','<h2>A useful option for ')
 s=s.replace('Reviewed September 1, 2026','Updated September 8, 2026')
 s=s.replace('<h2>Bottom line</h2>','<h2>What to take away</h2>')
 def schema(m):
  data=json.loads(m.group(1))
  if data.get('@type') in ['Article','BlogPosting']:data['dateModified']='2026-09-08'
  return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False)+'</script>'
 s=re.sub(r'<script type="application/ld\+json">(.*?)</script>',schema,s,flags=re.S)
 # A compact in-page contents disclosure makes long articles navigable on phones.
 s=re.sub(r'<!--journal-contents:start-->.*?<!--journal-contents:end-->','',s,flags=re.S)
 headings=[]
 def heading(m):
  title=re.sub('<[^>]+>','',m.group(1));slug='read-'+re.sub('[^a-z0-9]+','-',html.unescape(title).lower()).strip('-')
  headings.append((slug,title));return '<h2 id="'+slug+'">'+m.group(1)+'</h2>'
 s=re.sub(r'<h2(?: id="read-[^"]+")?>(.*?)</h2>',heading,s,flags=re.S)
 contents='<!--journal-contents:start--><details class="journal-contents"><summary>In this article</summary><nav aria-label="Article sections">'+''.join('<a href="#'+slug+'">'+title+'</a>' for slug,title in headings if title!='The short answer')+'</nav></details><!--journal-contents:end-->'
 s=re.sub(r'(<p class="blog-meta">.*?</p>)',lambda m:m.group(0)+contents,s,count=1,flags=re.S)
 body=re.search(r'<article class="article-container">(.*?)</article>',s,re.S)
 if body:
  words=len(re.sub('<[^>]+>',' ',body.group(1)).split());s=re.sub(r'\d+ minute read',str(math.ceil(words/220))+' minute read',s)
 s=re.sub(r'https://getmacros.net/images/(journal-[a-z-]+)\.svg',r'https://getmacros.net/images/\1.png',s)
 p.write_text(s,encoding='utf-8')
# Keep the hub's reading times consistent with the articles it links to.
hub=ROOT/'blog.html';text=hub.read_text(encoding='utf-8')
def card(match):
 block=match.group(0)
 for name in ADDITIONS:
  if 'href="'+name+'"' in block:
   article=(ROOT/name).read_text(encoding='utf-8');minutes=re.search(r'(\d+) minute read',article).group(1)
   block=re.sub(r'\d+ min read',minutes+' min read',block)
 return block
text=re.sub(r'<a class="blog-card.*?</a>',card,text,flags=re.S)
text=re.sub(r'https://getmacros.net/images/(journal-[a-z-]+)\.svg',r'https://getmacros.net/images/\1.png',text)
hub.write_text(text,encoding='utf-8')
sitemap=ROOT/'sitemap.xml';text=sitemap.read_text(encoding='utf-8')
for name in ADDITIONS:
 text=re.sub(r'(<loc>https://getmacros.net/'+re.escape(name)+r'</loc><lastmod>)[^<]+',r'\g<1>2026-09-08',text)
sitemap.write_text(text,encoding='utf-8')
print('Revised five journal articles with practical examples, source links and article navigation.')
