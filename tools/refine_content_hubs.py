"""Final, repeatable layouts for the learning and restaurant directories."""
import html
import re

PAGES = {'articles.html', 'blog.html', 'healthy-fast-food.html',
         'restaurant-meal-guides.html', 'nutrition-label-comparison-tool.html'}

GROUPS = [
    ('macros-and-goals', 'Start with the basics', 'learn', [
        ('what-are-macros', 'Understand protein, carbs and fats.'),
        ('how-many-calories-should-i-eat-a-day', 'Find a starting point for your daily calories.'),
        ('protein', 'Why your body needs protein and where to find it.'),
        ('carbs', 'How carbs fuel your day.'),
        ('fats', 'What fats do and how they fit into meals.'),
        ('how-much-protein-per-day', 'Work out a daily protein target.')]),
    ('weight-goals', 'Calories and weight goals', 'tools', [
        ('what-is-a-calorie-deficit', 'Understand the idea behind eating for weight loss.'),
        ('how-to-calculate-maintenance-calories', 'Estimate how much you need to maintain your weight.'),
        ('how-to-calculate-macros-by-hand', 'Follow a worked example, step by step.'),
        ('macros-for-weight-loss', 'Set calorie and macro targets for weight loss.'),
        ('macros-for-muscle-gain', 'Plan your macros to support muscle gain.'),
        ('cutting-bulking-maintenance-explained', 'What these terms mean for your food choices.'),
        ('body-recomposition-explained', 'Understand losing fat while building muscle.'),
        ('can-you-build-muscle-in-a-calorie-deficit', 'Who may be able to do both, and what helps.'),
        ('when-to-recalculate-calories-and-macros', 'Know when your targets need an update.')]),
    ('labels-and-recipes', 'Food labels and nutrients', 'labels', [
        ('how-to-read-a-nutrition-label', 'Know what to look for on the package.'),
        ('serving-size-vs-portion-size', 'Compare the label with the amount you actually eat.'),
        ('how-to-calculate-recipe-nutrition', 'Add up a recipe and divide it into portions.'),
        ('how-much-fiber-per-day', 'Your daily fiber target and foods that can help.'),
        ('how-much-sodium-per-day', 'Understand sodium amounts in everyday foods.')]),
    ('eating-out', 'Everyday meals', 'meal', [
        ('how-to-eat-out-without-wrecking-your-goal', 'Choose a restaurant meal that works for you.'),
        ('high-protein-foods-list', 'Compare protein in 25 everyday foods.'),
        ('how-to-build-a-balanced-meal-with-macros', 'Put together a meal, then adjust the portions.'),
        ('how-to-hit-protein-goal-on-budget', 'Make your protein budget go further.')]),
    ('training-and-routine', 'Training and your routine', 'timeline', [
        ('what-to-eat-before-a-workout', 'Pick a meal or snack for the time you have.'),
        ('what-to-eat-after-a-workout', 'Put together a practical meal after training.'),
        ('calories-on-rest-days', 'Decide whether to change your intake on rest days.'),
        ('why-did-i-gain-weight-overnight', 'Understand day-to-day changes on the scale.')])
]


def hero(title, description, drawing, actions=''):
    return ('<section class="hub-hero"><div class="container hub-hero-inner"><div>'
            f'<h1 data-reveal-title>{title}</h1><p>{description}</p>{actions}</div>'
            f'<div class="hub-art" aria-hidden="true">{drawing}</div></div></section>')


def refine_hubs(text, name, art):
    if name not in PAGES:
        return text
    text = re.sub(r'(<body[^>]*class=")([^"]*)',
        lambda m: m[1] + m[2] + (' hub-finish' if 'hub-finish' not in m[2] else ''), text, count=1)
    main = text.split('<main id="main-content">', 1)[1].split('</main>', 1)[0]
    breadcrumb = re.search(r'<nav class="breadcrumb".*?</nav>', main, re.S)
    crumb = breadcrumb[0] if breadcrumb else ''
    if name == 'articles.html':
        titles = dict(re.findall(r'<a class="guide-card" href="([^"]+)">\s*<h3>(.*?)</h3>', main, re.S))
        expected = {slug+'.html' for _, _, _, links in GROUPS for slug, _ in links}
        assert set(titles) == expected, ('Unassigned basics guide', set(titles) ^ expected)
        intro = hero('Nutrition basics', 'Find a clear answer to your food and nutrition questions.', art('learn'))
        jumps = '<nav class="container hub-topics" aria-label="Nutrition topics">' + ''.join(
            f'<a href="#{key}">{label}</a>' for key, label in [
                ('macros-and-goals','The basics'), ('weight-goals','Weight goals'),
                ('labels-and-recipes','Food labels'), ('eating-out','Everyday meals'),
                ('training-and-routine','Training')]) + '</nav>'
        sections = []
        for key, label, kind, links in GROUPS:
            cards = ''.join(f'<a class="guide-card" href="{slug}.html"><h3>{titles[slug+".html"]}</h3>'
                            f'<p>{html.escape(desc)}</p></a>' for slug, desc in links)
            sections.append(f'<section class="guide-group data-section hub-topic" id="{key}"><div class="container">'
                f'<div class="section-head"><span class="learning-icon" aria-hidden="true">{art(kind)}</span>'
                f'<h2>{label}</h2></div><div class="guide-grid">{cards}</div></div></section>')
        main = crumb + intro + jumps + ''.join(sections)
    elif name == 'blog.html':
        cards = re.findall(r'<a class="blog-card guide-card".*?</a>', main, re.S)
        assert len(cards) == 5
        cards = [re.sub(r'(<div class="blog-meta">\s*<span>.*?</span>)\s*<span>.*?</span>', r'\1', card, flags=re.S) for card in cards]
        main = crumb + hero('GetMacros Blog', 'Food questions, research and practical takeaways.', art('learn'))
        main += '<section id="latest" class="hub-blog-list"><div class="container"><div class="blog-grid">'+''.join(cards)+'</div></div></section>'
        main += '<section class="hub-next container"><div><h2>New to nutrition?</h2><p>Start with calories, macros and food labels.</p></div><a class="btn action-link" href="articles.html">Explore nutrition basics</a></section>'
    elif name == 'restaurant-meal-guides.html':
        cards = re.findall(r'<a class="chain-card".*?</a>', main, re.S)
        assert len(cards) == 15
        updated = []
        for card in cards:
            url = re.search(r'href="([^"]+)"', card)[1]
            slug = url.split('-healthy-')[0]
            card = re.sub(r'<img\b[^>]*>', '', card)
            card = card.replace('>', f'><img class="directory-logo" src="images/restaurant-marks/{slug}.svg?v=palm1" alt="" width="48" height="48" loading="lazy">', 1)
            updated.append(card)
        main = crumb + hero('Restaurant meal guides', 'Pick a restaurant. See menu options, macros and simple ordering tips.', art('meal'))
        main += '<section class="hub-directory"><div class="container"><div class="chain-grid">'+''.join(updated)+'</div></div></section>'
        main += '<section class="hub-next container"><div><h2>Not sure where to eat?</h2><p>Find meals from different restaurants for your goals.</p></div><a class="btn btn-primary" href="restaurant-meal-finder.html">Find my meal</a></section>'
        main += ('<section class="hub-notes container"><details><summary>About the nutrition numbers</summary>'
                 '<p>We use the restaurants’ published nutrition information for the named U.S. menu items. '
                 'Portions, locations and customizations can change the numbers. Missing values appear as a dash.</p>'
                 '<p>Check the restaurant’s current menu and allergen information before ordering.</p>'
                 '<a class="btn action-link" href="sources.html">See nutrition sources</a></details></section>')
    elif name == 'healthy-fast-food.html':
        rankings = re.search(r'<section id="rankings".*?</section>', main, re.S)[0]
        rankings = rankings.replace('Compare meals by your goal', 'Compare by your goal').replace(
            'Compare standard menu items. Portions and customizations can change the numbers.',
            'Open a list to compare menu options. Portions and swaps can change the numbers.')
        cards = re.findall(r'<a class="chain-card".*?</a>', main, re.S)
        # On repeat builds, the directory remains in this disclosure.
        assert len(cards) == 15
        actions = '<div class="focus-actions"><a class="btn btn-primary" href="restaurant-meal-finder.html">Find my meal</a><a class="btn action-link" href="restaurant-meal-guides.html">Browse restaurants</a></div>'
        main = crumb + hero('Healthy fast food', 'Compare 83 menu options for more protein, fewer calories or a bigger meal.', art('meal'), actions)
        main += rankings
        main += '<section class="hub-notes container"><details class="hub-restaurant-list"><summary>Browse all 15 restaurants</summary><div class="chain-grid">'+''.join(cards)+'</div></details></section>'
        main += ('<section class="hub-notes container"><details><summary>How to use these lists</summary>'
                 '<p>These are comparisons of specific menu options, not an overall health score. '
                 'Consider the full order and the nutrients that matter to you.</p>'
                 '<p>We use standard U.S. menu items. Missing nutrition values stay blank. '
                 'Dietary labels do not guarantee allergy safety; check with the restaurant.</p>'
                 '<a class="btn action-link" href="sources.html">See nutrition sources</a></details></section>')
    else:
        # Keep the working form and result IDs intact; simplify the supporting explanation.
        main = re.sub(r'<section class="(?:tool-hero|hub-hero)[^"]*">.*?</section>',
            hero('Compare two food labels', 'Enter two labels. Compare the portions you eat or the same amount of each food.', art('labels')), main, count=1, flags=re.S)
        main = re.sub(r'<section class="simple-tool-help clarity-help">.*?</section>', '', main, flags=re.S)
        example = ('<!-- practical-example:start --><section class="practical-example hub-comparison-example" aria-labelledby="example-title"><div class="container">'
                   '<h2 id="example-title">Same food amount. Fairer comparison.</h2>'
                   '<p class="example-intro">The example cereals have different serving sizes. Here’s why that matters.</p>'
                   '<div class="example-grid"><article><h3>By serving</h3><strong>160 vs. 210 calories</strong>'
                   '<p>You’re comparing 40 g of Cereal A with 55 g of Cereal B.</p></article>'
                   '<article><h3>By equal weight</h3><strong>400 vs. 382 calories</strong>'
                   '<p>At 100 g each, Cereal B has fewer calories.</p></article></div>'
                   '<details><summary>Which comparison should I choose?</summary>'
                   '<p><strong>Per serving:</strong> compare the label portions. <strong>Per 100 g:</strong> compare equal weights. '
                   '<strong>Per 100 calories:</strong> compare nutrients for the same calories.</p>'
                   '<p>Use the numbers that matter to your meal. There isn’t one overall winner.</p>'
                   '<a class="btn action-link" href="how-to-read-a-nutrition-label.html">How to read a food label</a>'
                   '</details></div></section><!-- practical-example:end -->')
        main = re.sub(r'<!-- practical-example:start -->.*?<!-- practical-example:end -->', example, main, flags=re.S)
    main = re.sub(r'<div class="ad-auto-anchor"[^>]*>\s*</div>', '', main)
    return text.split('<main id="main-content">', 1)[0] + '<main id="main-content">' + main + '<div class="ad-auto-anchor" aria-hidden="true"></div></main>' + text.split('</main>', 1)[1]
