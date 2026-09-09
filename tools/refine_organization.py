"""Remove redundant framing and keep the primary action clear after rebuilds."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
symbols={key:(viewbox,body) for key,viewbox,body in re.findall(r'<symbol id="([^"]+)" viewBox="([^"]+)">(.*?)</symbol>',(ROOT/'icon-sprite.svg').read_text(encoding='utf-8'),re.S)}
for p in ROOT.glob('*.html'):
    s=p.read_text(encoding='utf-8')
    s=s.replace('Healthy Order Match','Fast-food meal finder')
    s=s.replace('Recipe Macro Scaler','Adjust recipe portions').replace('Compare Labels','Compare two foods')
    s=s.replace('The GetMacros Journal','GetMacros Blog').replace('the GetMacros Journal','the GetMacros Blog').replace('>Journal<','>Blog<').replace('"name": "Journal"','"name": "Blog"')
    # Inline shared navigation icons so Safari does not depend on external-use loading.
    def inline_icon(m):
        if m.group(2) not in symbols:return m.group(0)
        viewbox,body=symbols[m.group(2)]
        return '<svg'+m.group(1)+' viewBox="'+viewbox+'">'+body+'</svg>'
    s=re.sub(r'<svg([^>]*)><use href="icon-sprite.svg(?:\?[^"#]*)?#([^"]+)"></use></svg>',inline_icon,s)
    # Generic one-card recommendations repeat existing contextual links/footer.
    s=re.sub(r'<section class="related-explore"[^>]*>.*?</section>','',s,flags=re.S)
    if p.name=='accessibility.html':
        s=s.replace('Interactive tools and games','Interactive tools').replace('calculators, quizzes, and games','calculators and meal finder')
    if p.name=='index.html':
        s=s.replace('Good food.<br><em>Your kind of fuel.</em>','Healthy fast-food meals.<br><em>Find your fit.</em>')
        s=s.replace('Find a meal you’ll love, understand what’s in it, and make the numbers work for you. Explore 15 restaurant chains in five easy questions.','Meals from 15 restaurant chains, matched to your appetite and goals.')
        s=s.replace('Match meals to cutting, bulking, protein and dietary needs.','Choose your goals. Get your shortlist.')
        s=s.replace('Put two foods on the same serving and calorie basis.','See calories and nutrients side by side.')
    if p.name=='articles.html':
        previews={
          'best-fast-food-restaurants-for-your-goals.html':('restaurant-comparison','Compare restaurant meals for your goal.'),
          'how-much-protein-can-your-body-absorb.html':('protein-absorption','What larger protein servings mean for muscle.'),
          'are-diet-drinks-bad-for-you.html':('diet-drinks','Sweeteners, safety and everyday drink choices.'),
          'does-creatine-cause-hair-loss.html':('creatine-hair','What the hair studies actually found.'),
          'calories-vs-macros-what-matters-more.html':('calories-vs-macros','Where to start with calories and nutrients.')
        }
        def guide_preview(m):
            block=m.group(0)
            if m.group(1) not in previews:return block
            image,description=previews[m.group(1)]
            block=re.sub(r'<p>.*?</p>','<p>'+description+'</p>',block,flags=re.S)
            if 'guide-preview' not in block:
                block=block.replace('<h3>','<img class="guide-preview" src="images/journal-'+image+'.svg" alt="" width="320" height="180" loading="lazy"><h3>',1)
            return block
        s=re.sub(r'<a class="guide-card" href="([^"]+)">.*?</a>',guide_preview,s,flags=re.S)
    if p.name=='calculators.html':
        s=s.replace('Food, recipe and label math','Food &amp; recipe tools').replace('Goals, training and eating out','More tools')
        s=s.replace('Calculate calories and macros for your goal','Calculate your daily macros')
        s=s.replace('Enter your age, height, weight, activity and goal to estimate daily calories, protein, carbs and fat. The calculation and its assumptions stay visible.','Estimate calories, protein, carbs and fat for your goal.')
        s=s.replace('Full macro calculator','Your details')
        s=s.replace('<p class="section-intro">Enter your details on the left. Your estimated daily calories and macros appear alongside them.</p>','')
        s=re.sub(r'(?m)^[ \t]+$','',s)
        s=re.sub(r'<p class="editorial-note" id="adult-scope">(.*?)</p>',r'<details class="calculator-scope" id="adult-scope"><summary>For adults 18+ · About this estimate</summary><p>\1</p></details>',s,flags=re.S)
        for old,new in {'Food, recipe and label math':'Food & recipe tools','Goals, training and eating out':'More tools','Recipe Calories and Macros Calculator':'Recipe portions','Compare Nutrition Labels Side by Side':'Compare food labels','Protein Cost per Gram Calculator':'Protein cost','Budget Meal Builder':'Meal ideas','Sodium per Portion Calculator':'Sodium per portion','Carbs per Portion Calculator':'Carbs per portion','Weight Goal Timeline Calculator':'Weight-goal timeline','Sweat Rate Calculator':'Sweat rate','Healthy Order Match':'Find a restaurant meal'}.items():
            # Shorten tool-directory labels, leaving page metadata descriptive.
            s=re.sub(r'(<div class="tool-links">)(.*?)(</div>)',lambda m:m.group(1)+m.group(2).replace(old,new)+m.group(3),s,flags=re.S)
    if p.name=='healthy-fast-food.html':
        s=re.sub(r'<section><div class="container"><div class="section-head"><p class="eyebrow">Combine goals.*?</section>','',s,flags=re.S)
        s=s.replace('Healthy fast food for cutting, bulking and high protein','Find your next restaurant meal')
        s=s.replace('Every chain page now exposes all tracked options, protein-per-calorie, goal-based picks, unique ordering advice, an official source and a real checked date.','Choose a restaurant to compare meals, nutrition and ordering tips.')
        s=s.replace('High protein and bulking can coexist. So can vegetarian and lower calorie. The finder ranks compatible records without pretending one meal is best for everyone.','Choose your priorities. You can combine goals in the meal finder.')
        s=s.replace('Every number below comes from the central dataset. Small sides are excluded from the substantial lower-calorie list.','Compare standard menu items. Portions and customizations can change the numbers.')
        # Put the restaurant directory before the detailed rankings.
        directory=re.search(r'<section><div class="container"><div class="section-head"><p class="eyebrow">Restaurant directory.*?</section>',s,re.S)
        if directory:
            block=directory.group(0);s=s.replace(block,'');s=s.replace('<section id="rankings"',block+'<section id="rankings"',1)
        def logo(m):
            block=m.group(0)
            if '<img' in block:return block
            slug=m.group(1).split('-healthy')[0]
            return block.replace('<span>','<img class="directory-logo" src="images/restaurant-logos/'+slug+'.png" alt="" width="48" height="48" loading="lazy"><span>',1)
        s=re.sub(r'<a class="chain-card" href="([^"]+)">.*?</a>',logo,s,flags=re.S)
        s=re.sub(r'<article class="ranking-card"><h3>(.*?)</h3>(.*?)</article>',r'<details class="ranking-card ranking-disclosure"><summary>\1</summary>\2</details>',s,flags=re.S)
    p.write_text(s,encoding='utf-8')
print('Simplified calculator framing, tool labels and restaurant discovery.')
