#!/usr/bin/env python3
"""Generates the SEO article pages for GetMacros.net.

Run from anywhere: python3 tools/generate_articles.py
Regenerates every file listed in ARTICLES into the site root, using the
same header/nav/footer markup and css/js as the hand-written pages.
To add another article, add an entry to ARTICLES and re-run.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(ROOT, "icon-sprite.svg")) as _f:
    ICON_SPRITE = _f.read().strip()

def nav_html(current="articles"):
    def cur(name):
        return ' aria-current="page"' if name == current else ""

    return f'''<header class="site-header">
  <nav class="nav">
    <a href="index.html" class="nav-brand"><svg class="logo-mark" aria-hidden="true"><use href="#logo-mark"/></svg>Get<span>Macros</span>.net</a>
    <button class="nav-toggle" aria-label="Toggle menu">☰</button>
    <ul class="nav-links">
      <li><a href="index.html">Home</a></li>
      <li><a href="protein.html">Protein</a></li>
      <li><a href="fats.html">Fat</a></li>
      <li><a href="carbs.html">Carbs</a></li>
      <li><a href="calculators.html">Calculators</a></li>
      <li><a href="articles.html"{cur("articles")}>Articles</a></li>
      <li><a href="glossary.html"{cur("glossary")}>Glossary</a></li>
      <li><a href="quiz.html"{cur("quiz")}>Quiz</a></li>
      <li><a href="sources.html">Sources</a></li>
    </ul>
  </nav>
</header>'''


NAV = nav_html("articles")

FOOTER = '''<footer class="site-footer">
  <div class="container">
    <div>
      <h4>GetMacros.net</h4>
      <p class="disclaimer">Educational content only — not medical advice. See <a href="sources.html">Sources</a> for citations.</p>
    </div>
    <div>
      <h4>Learn</h4>
      <ul>
        <li><a href="protein.html">Protein</a></li>
        <li><a href="fats.html">Fat</a></li>
        <li><a href="carbs.html">Carbohydrates</a></li>
        <li><a href="articles.html">All articles</a></li>
        <li><a href="glossary.html">Glossary</a></li>
      </ul>
    </div>
    <div>
      <h4>Tools</h4>
      <ul>
        <li><a href="calculators.html">Macro calculator</a></li>
        <li><a href="quiz.html">Quizzes &amp; games</a></li>
        <li><a href="sources.html">Sources &amp; citations</a></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">© 2026 GetMacros.net</div>
</footer>'''

# --- Ads (Google AdSense) -------------------------------------------------
# TODO: replace with your real AdSense values once your account is approved:
#   1. ADSENSE_CLIENT -> your Publisher ID from adsense.google.com (ca-pub-...)
#   2. The data-ad-slot value below -> an ad unit ID from your AdSense dashboard
#      (the same responsive display unit can be reused on every page).
# Until both are real, AdSense simply won't render anything in this slot --
# nothing breaks, the site just shows no ad.
ADSENSE_CLIENT = "ca-pub-XXXXXXXXXXXXXXXX"

ADSENSE_LOADER = (
    f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" '
    'crossorigin="anonymous"></script>'
)

AD_SLOT = f'''  <section class="tight ad-slot">
    <div class="container">
      <p class="ad-label">Advertisement</p>
      <ins class="adsbygoogle"
           style="display:block"
           data-ad-client="{ADSENSE_CLIENT}"
           data-ad-slot="0000000000"
           data-ad-format="auto"
           data-full-width-responsive="true"></ins>
      <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
    </div>
  </section>
'''

HERO_STYLE = {
    "protein": "background: linear-gradient(rgba(90,20,15,.72),rgba(90,20,15,.82))",
    "fat": "background: linear-gradient(rgba(110,75,10,.72),rgba(110,75,10,.82))",
    "carbs": "background: linear-gradient(rgba(10,60,35,.72),rgba(10,60,35,.82))",
    "general": "background:var(--color-primary-dark); color:#fff;",
}


def page(slug, title, meta, category, eyebrow, h1, intro, body, related):
    hero_class = "hero page-hero" if category != "general" else "page-hero"
    related_links = " &middot; ".join(
        f'<a href="{href}">{label}</a>' for href, label in related
    )
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://pagead2.googlesyndication.com https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.googletagservices.com; style-src 'self' 'unsafe-inline' https://*.googlesyndication.com; img-src 'self' data: https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.gstatic.com; font-src 'self'; connect-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; frame-src https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>{title} | GetMacros.net</title>
<meta name="description" content="{meta}">
<link rel="canonical" href="https://getmacros.net/{slug}.html">
<link rel="stylesheet" href="css/style.css">
<script src="js/img-fallback.js"></script>
{ADSENSE_LOADER}
</head>
<body>
{ICON_SPRITE}
{NAV}

<main>
  <section class="{hero_class}" style="{HERO_STYLE[category]}">
    <div class="container">
      <p class="eyebrow">{eyebrow}</p>
      <h1>{h1}</h1>
      <p>{intro}</p>
    </div>
  </section>

{body}

  <section class="tight">
    <div class="container">
      <p class="section-intro"><strong>Keep reading:</strong> {related_links}</p>
    </div>
  </section>
</main>

{AD_SLOT}
{FOOTER}

<script src="js/main.js"></script>
<script src="js/reveal.js"></script>
</body>
</html>
'''


def sec(inner, bg=None, tight=False):
    cls = "tight" if tight else ""
    style = f' style="background:{bg}"' if bg else ""
    cls_attr = f' class="{cls}"' if cls else ""
    return f'  <section{cls_attr}{style}>\n    <div class="container">\n{inner}\n    </div>\n  </section>\n'


ARTICLES = []


def add(slug, title, meta, category, eyebrow, h1, intro, body, related):
    ARTICLES.append(dict(slug=slug, title=title, meta=meta, category=category,
                          eyebrow=eyebrow, h1=h1, intro=intro, body=body, related=related))


# ---------------------------------------------------------------- PROTEIN --

add(
    "how-much-protein-per-day",
    "How Much Protein Do You Need Per Day?",
    "How much protein you actually need per day for baseline health, general fitness, and muscle building, based on RDA and sports nutrition research.",
    "protein", "Protein Guide", "How much protein do you need per day?",
    "The right number depends heavily on your activity level and goals — the government minimum and the amount that supports muscle building are very different numbers.",
    sec('''      <h2>The short answer</h2>
      <table class="data-table">
        <tr><th>Who you are</th><th>Grams per kg body weight</th><th>Example at 70kg (154lb)</th></tr>
        <tr><td>Sedentary adult (RDA minimum)</td><td>0.8 g/kg</td><td>56 g/day</td></tr>
        <tr><td>Generally active</td><td>1.2–1.6 g/kg</td><td>84–112 g/day</td></tr>
        <tr><td>Building muscle / in a calorie deficit</td><td>1.6–2.2 g/kg</td><td>112–154 g/day</td></tr>
      </table>
      <p>The 0.8 g/kg figure is the Recommended Dietary Allowance — the minimum intake shown to prevent deficiency in a mostly sedentary adult. It is not an optimal target if you exercise regularly.<sup class="ref"><a href="sources.html#p3">[1]</a></sup> The International Society of Sports Nutrition instead recommends 1.4–2.0 g/kg/day for people who train, to maximize muscle protein balance.<sup class="ref"><a href="sources.html#p2">[2]</a></sup></p>''') +
    sec('''      <h2>Why the RDA understates most people's needs</h2>
      <p>The RDA was calculated to answer one question: what's the minimum amount that keeps a sedentary person from becoming deficient? It wasn't designed to answer "what's optimal for building or preserving muscle," which is a different question entirely. Resistance training increases the rate at which your body breaks down and rebuilds muscle protein, so more raw material (amino acids) is needed to support that turnover.</p>
      <div class="panel">
        <h3>Rule of thumb</h3>
        <p>If you strength train several times a week, aim for roughly <strong>0.7–1.0 grams of protein per pound of body weight</strong> (about 1.6–2.2 g/kg). Above that range, additional protein generally doesn't add extra muscle-building benefit.</p>
      </div>''', bg="var(--color-protein-bg)", tight=True) +
    sec('''      <p>Want an exact number instead of a range? Our calculator factors in your weight, activity level, and goal automatically.</p>
      <p><a href="calculators.html" class="btn btn-primary">Calculate my protein target →</a></p>'''),
    [("protein.html", "What protein actually does"), ("protein-for-muscle-growth.html", "Protein for muscle growth"), ("high-protein-foods-list.html", "High-protein foods list")]
)

add(
    "protein-for-muscle-growth",
    "Protein for Muscle Growth: How Much, When, and Why",
    "How dietary protein drives muscle protein synthesis after training, how much you need, and whether meal timing actually matters.",
    "protein", "Protein Guide", "Protein for muscle growth: how much, when, and why",
    "Muscle isn't built in the gym — it's built afterward, from amino acids, and only if enough of them are available.",
    sec('''      <h2>The mechanism: muscle protein synthesis</h2>
      <p>Resistance training damages muscle fibers at a microscopic level and triggers <strong>muscle protein synthesis (MPS)</strong> — the process your body uses to repair and build new muscle tissue. Both exercise and protein intake independently stimulate MPS, and the two together are more powerful than either alone. After a resistance training session, MPS can stay elevated for up to 48 hours as your body remodels the trained muscle.<sup class="ref"><a href="sources.html#p2">[1]</a></sup> Without enough dietary protein available during that window, the repair process is incomplete.</p>''') +
    sec('''      <h2>How much, and how often</h2>
      <ul class="checklist">
        <li><strong>Daily total: 1.6–2.2 g/kg body weight</strong> for most people actively training for muscle growth</li>
        <li><strong>Per-meal target: roughly 0.4 g/kg</strong>, spread across 3–4 meals — this appears to maximize MPS response better than getting most of your protein in one large meal</li>
        <li><strong>Consistency matters more than precision</strong> — hitting your daily total most days beats hitting an exact number occasionally</li>
      </ul>''') +
    sec('''      <div class="panel warn">
        <h3>Does the "anabolic window" matter?</h3>
        <p>The idea that you must eat protein within 30–60 minutes of training to avoid "missing the window" is largely overstated. Total daily protein intake and consistent spacing across the day matter far more than precise post-workout timing for most people. See our <a href="protein-timing.html">full breakdown of protein timing research</a>.</p>
      </div>'''),
    [("protein-timing.html", "Does protein timing matter?"), ("how-much-protein-per-day.html", "How much protein per day"), ("macros-for-muscle-gain.html", "Macros for building muscle")]
)

add(
    "protein-deficiency-symptoms",
    "10 Warning Signs You're Not Eating Enough Protein",
    "The early warning signs of low protein intake, from slow wound healing to hair thinning, and when they signal a real deficiency.",
    "protein", "Protein Guide", "10 warning signs you're not eating enough protein",
    "Severe protein deficiency (kwashiorkor) is rare in well-fed populations — but eating below your personal needs is common, and it shows up in ways people rarely connect back to diet.",
    sec('''      <ul class="checklist">
        <li><strong>Constant fatigue</strong> — protein is needed to make the enzymes and transport proteins involved in energy metabolism</li>
        <li><strong>Slow-healing cuts and bruises</strong> — tissue repair depends directly on amino acid availability</li>
        <li><strong>Thinning hair or hair loss</strong> — hair is largely made of a protein called keratin</li>
        <li><strong>Brittle, ridged, or slow-growing nails</strong> — same underlying cause as hair changes</li>
        <li><strong>Getting sick often</strong> — antibodies are proteins; low intake can blunt immune response</li>
        <li><strong>Unexplained swelling (edema)</strong>, especially in the belly or legs — a hallmark of severe deficiency, caused by low blood protein levels affecting fluid balance<sup class="ref"><a href="sources.html#p4">[1]</a></sup></li>
        <li><strong>Losing muscle despite training</strong> — without enough amino acids, your body can't fully repair and build muscle tissue</li>
        <li><strong>Constant hunger, especially cravings</strong> — protein is the most satiating macronutrient; low intake often shows up as never feeling full</li>
        <li><strong>Mood changes or brain fog</strong> — several neurotransmitters are synthesized from amino acids</li>
        <li><strong>Skin changes</strong> — dryness, rashes, or slow-fading marks</li>
      </ul>''') +
    sec('''      <p>Most of these signs have other possible causes too, so they're not a diagnosis on their own — but if several apply and your diet is genuinely low in protein sources, it's worth checking your actual intake against your target.</p>
      <p><a href="calculators.html" class="btn btn-primary">Check your protein target →</a></p>''', bg="var(--color-protein-bg)", tight=True),
    [("protein.html", "What protein actually does"), ("high-protein-foods-list.html", "High-protein foods list"), ("how-much-protein-per-day.html", "How much protein you need")]
)

add(
    "high-protein-foods-list",
    "25 High-Protein Foods and How Much Protein They Contain",
    "A reference list of high-protein animal and plant foods with approximate grams of protein per 100g, for building meals around your target.",
    "protein", "Protein Guide", "25 high-protein foods and how much protein they contain",
    "Approximate protein content per 100 grams unless noted — actual values vary by cut, brand, and preparation.",
    sec('''      <h2>Animal sources</h2>
      <table class="data-table">
        <tr><th>Food</th><th>Protein (per 100g)</th></tr>
        <tr><td>Chicken breast, cooked</td><td>~31 g</td></tr>
        <tr><td>Turkey breast, cooked</td><td>~29 g</td></tr>
        <tr><td>Tuna, canned</td><td>~30 g</td></tr>
        <tr><td>Lean beef, cooked</td><td>~26 g</td></tr>
        <tr><td>Salmon, cooked</td><td>~25 g</td></tr>
        <tr><td>Shrimp, cooked</td><td>~24 g</td></tr>
        <tr><td>Pork loin, cooked</td><td>~26 g</td></tr>
        <tr><td>Cottage cheese</td><td>~11 g</td></tr>
        <tr><td>Greek yogurt, plain</td><td>~10 g</td></tr>
        <tr><td>Eggs (whole)</td><td>~13 g (~6g per large egg)</td></tr>
        <tr><td>Milk</td><td>~3.4 g</td></tr>
        <tr><td>Whey protein powder</td><td>~75–85 g (per 100g powder)</td></tr>
      </table>''') +
    sec('''      <h2>Plant sources</h2>
      <table class="data-table">
        <tr><th>Food</th><th>Protein (per 100g, cooked unless noted)</th></tr>
        <tr><td>Tempeh</td><td>~19 g</td></tr>
        <tr><td>Edamame</td><td>~11 g</td></tr>
        <tr><td>Lentils</td><td>~9 g</td></tr>
        <tr><td>Black beans</td><td>~9 g</td></tr>
        <tr><td>Chickpeas</td><td>~9 g</td></tr>
        <tr><td>Tofu, firm</td><td>~8 g</td></tr>
        <tr><td>Quinoa</td><td>~4.5 g</td></tr>
        <tr><td>Peanut butter</td><td>~25 g</td></tr>
        <tr><td>Almonds</td><td>~21 g</td></tr>
        <tr><td>Pumpkin seeds</td><td>~19 g</td></tr>
        <tr><td>Chia seeds</td><td>~17 g</td></tr>
        <tr><td>Hemp seeds</td><td>~31 g</td></tr>
        <tr><td>Oats, dry</td><td>~13 g</td></tr>
      </table>
      <p class="section-intro">See <a href="sources.html#p5">MyPlate's Protein Foods Group</a> for the full USDA reference list.</p>'''),
    [("protein.html", "What protein actually does"), ("plant-based-protein-sources.html", "Best plant-based protein sources"), ("complete-vs-incomplete-protein.html", "Complete vs. incomplete protein")]
)

add(
    "complete-vs-incomplete-protein",
    "Complete vs. Incomplete Protein: What Actually Matters",
    "The real difference between complete and incomplete protein sources, why 'protein combining' at every meal is a myth, and what actually matters for muscle and health.",
    "protein", "Protein Guide", "Complete vs. incomplete protein: what actually matters",
    "Your body needs 9 essential amino acids from food. \"Complete\" and \"incomplete\" just describe whether a single food supplies all 9 in meaningful amounts.",
    sec('''      <h2>What makes a protein "complete"</h2>
      <p>Of the 20 amino acids that make up protein, 9 are essential — your body can't synthesize them, so they must come from food. A <strong>complete protein</strong> supplies all 9 essential amino acids in reasonably sufficient amounts. Nearly all animal proteins (meat, fish, eggs, dairy) are complete. Among plant foods, soy, quinoa, and buckwheat are complete proteins too — the exception rather than the rule.</p>
      <p>An <strong>incomplete protein</strong> is low in one or more essential amino acids. Most individual plant proteins — beans, rice, nuts, most grains — fall into this category.</p>''') +
    sec('''      <h2>The "protein combining" myth</h2>
      <p>You may have heard you need to eat complementary plant proteins (like rice and beans) <em>at the same meal</em> to get a complete amino acid profile. This isn't accurate — your body maintains a pool of amino acids and can combine what you eat across an entire day, not just a single meal. As long as your overall diet includes a reasonable variety of protein sources, hitting your total daily protein target matters far more than pairing specific foods together.<sup class="ref"><a href="sources.html#p1">[1]</a></sup></p>
      <div class="panel">
        <h3>Practical takeaway</h3>
        <p>Eat a variety of protein sources across the day (which most omnivore and vegetarian diets do naturally), hit your total gram target, and don't stress about combining specific foods at specific meals.</p>
      </div>''', bg="var(--color-protein-bg)", tight=True),
    [("plant-based-protein-sources.html", "Best plant-based protein sources"), ("high-protein-foods-list.html", "High-protein foods list"), ("protein.html", "What protein actually does")]
)

add(
    "plant-based-protein-sources",
    "Best Plant-Based Protein Sources for Vegans and Vegetarians",
    "The most protein-dense plant foods for vegans and vegetarians, with approximate grams per serving and tips for hitting your daily target.",
    "protein", "Protein Guide", "Best plant-based protein sources for vegans and vegetarians",
    "Getting enough protein on a plant-based diet is straightforward once you know which foods to build meals around.",
    sec('''      <table class="data-table">
        <tr><th>Food</th><th>Protein per typical serving</th></tr>
        <tr><td>Tofu (½ cup, ~124g)</td><td>~10 g</td></tr>
        <tr><td>Tempeh (½ cup, ~83g)</td><td>~16 g</td></tr>
        <tr><td>Edamame (1 cup)</td><td>~17 g</td></tr>
        <tr><td>Lentils (1 cup cooked)</td><td>~18 g</td></tr>
        <tr><td>Black beans (1 cup cooked)</td><td>~15 g</td></tr>
        <tr><td>Chickpeas (1 cup cooked)</td><td>~15 g</td></tr>
        <tr><td>Seitan (100g)</td><td>~25 g</td></tr>
        <tr><td>Quinoa (1 cup cooked)</td><td>~8 g</td></tr>
        <tr><td>Peanut butter (2 tbsp)</td><td>~7 g</td></tr>
        <tr><td>Hemp seeds (3 tbsp)</td><td>~10 g</td></tr>
        <tr><td>Pea protein powder (1 scoop)</td><td>~20–25 g</td></tr>
      </table>''') +
    sec('''      <h2>Tips for hitting your target on a plant-based diet</h2>
      <ul class="checklist">
        <li><strong>Build meals around a protein-dense staple</strong> — tofu, tempeh, seitan, or legumes — rather than treating protein as an afterthought</li>
        <li><strong>Use variety, not one "hero" food</strong> — different plant proteins have different amino acid strengths</li>
        <li><strong>Don't fear plant protein powders</strong> — pea, soy, or blended plant proteins are an easy way to close a gap without much food volume</li>
        <li><strong>Track for a week</strong> if you're unsure — plant-based eaters often underestimate their protein intake until they actually log it</li>
      </ul>''', bg="var(--color-protein-bg)", tight=True),
    [("complete-vs-incomplete-protein.html", "Complete vs. incomplete protein"), ("high-protein-foods-list.html", "Full high-protein foods list"), ("calculators.html", "Calculate your protein target")]
)

add(
    "protein-timing",
    "Does Protein Timing Really Matter? What the Research Shows",
    "Whether the post-workout 'anabolic window' is real, how often you should eat protein, and what the sports nutrition research actually supports.",
    "protein", "Protein Guide", "Does protein timing really matter?",
    "For years, lifters were told to chug a shake within 30 minutes of finishing a workout or lose their gains. The research tells a more relaxed story.",
    sec('''      <h2>The "anabolic window" is wider than you think</h2>
      <p>Muscle protein synthesis stays elevated for up to 48 hours after resistance training, not 30 minutes.<sup class="ref"><a href="sources.html#p2">[1]</a></sup> That means the practical "window" to get protein in after a workout is measured in hours, not minutes — eating a normal meal within a few hours of training is more than adequate for the vast majority of people.</p>''') +
    sec('''      <h2>What actually seems to matter</h2>
      <ul class="checklist">
        <li><strong>Total daily protein</strong> is the single biggest driver of muscle protein synthesis over time — timing is a second-order effect at best</li>
        <li><strong>Distribution across the day</strong> — spreading protein across 3–4 meals (roughly 0.4 g/kg per meal) appears to modestly outperform getting most of it in one sitting</li>
        <li><strong>Not training fasted for extended periods</strong> without eventually eating matters more than exact pre/post-workout timing</li>
      </ul>
      <div class="panel">
        <h3>Bottom line</h3>
        <p>If a post-workout shake fits your routine, keep doing it — it's convenient. But don't stress if you eat your post-workout meal an hour or two later; the science doesn't support a strict cutoff.</p>
      </div>'''),
    [("protein-for-muscle-growth.html", "Protein for muscle growth"), ("how-much-protein-per-day.html", "How much protein per day"), ("protein.html", "What protein actually does")]
)

# -------------------------------------------------------------------- FAT --

add(
    "how-much-fat-per-day",
    "How Much Fat Should You Eat Per Day? (20–35% Explained)",
    "The recommended daily fat intake range (20-35% of calories), what it looks like in grams at different calorie levels, and why the range exists.",
    "fat", "Fat Guide", "How much fat should you eat per day?",
    "The Acceptable Macronutrient Distribution Range for fat is 20-35% of total calories for adults — here's what that looks like in real grams.",
    sec('''      <table class="data-table">
        <tr><th>Daily calories</th><th>20% (lower bound)</th><th>27.5% (typical)</th><th>35% (upper bound)</th></tr>
        <tr><td>1,800</td><td>40 g</td><td>55 g</td><td>70 g</td></tr>
        <tr><td>2,200</td><td>49 g</td><td>67 g</td><td>86 g</td></tr>
        <tr><td>2,600</td><td>58 g</td><td>79 g</td><td>101 g</td></tr>
        <tr><td>3,000</td><td>67 g</td><td>92 g</td><td>117 g</td></tr>
      </table>
      <p>This range comes from the Dietary Reference Intakes' Acceptable Macronutrient Distribution Range (AMDR) for fat.<sup class="ref"><a href="sources.html#f4">[1]</a></sup> Below 20%, it becomes difficult to get enough essential fatty acids and to properly absorb vitamins A, D, E, and K, which require dietary fat. Consistently well above 35% usually means protein or carbohydrate intake is being squeezed out.</p>''') +
    sec('''      <p>Enter your own calorie target for an exact gram range, or use the full macro calculator for a complete breakdown.</p>
      <p><a href="calculators.html#fat-calculator" class="btn btn-primary">Calculate my fat range →</a></p>''', bg="var(--color-fat-bg)", tight=True),
    [("fats.html", "What fat actually does"), ("low-fat-diet-risks.html", "Risks of very low-fat diets"), ("healthy-high-fat-foods.html", "Healthy high-fat foods")]
)

add(
    "saturated-vs-unsaturated-fat",
    "Saturated vs. Unsaturated Fat: What's Actually the Difference",
    "The chemical difference between saturated and unsaturated fat, how each affects health, and which foods contain them.",
    "fat", "Fat Guide", "Saturated vs. unsaturated fat: what's actually the difference",
    "Not all fat behaves the same way in your body — the difference comes down to a detail in the fat molecule's chemical structure.",
    sec('''      <h2>The chemistry, briefly</h2>
      <p>Fat molecules are chains of carbon atoms. In <strong>saturated fat</strong>, every carbon is bonded to as many hydrogen atoms as possible — no double bonds — which makes the molecule straight and lets it pack tightly (this is why saturated fats like butter are solid at room temperature). <strong>Unsaturated fats</strong> have one or more double bonds, which kinks the chain and keeps it liquid at room temperature — like olive oil.</p>''') +
    sec('''      <h2>Health associations and food sources</h2>
      <div class="two-col">
        <div class="panel">
          <h3>Saturated fat</h3>
          <p>Found in butter, fatty cuts of meat, cheese, and coconut oil. Research reviewed by Harvard's Nutrition Source associates replacing saturated fat with unsaturated fat with improved blood cholesterol profiles.<sup class="ref"><a href="sources.html#f2">[1]</a></sup> Most guidelines suggest keeping saturated fat intake moderate rather than eliminating it.</p>
        </div>
        <div class="panel">
          <h3>Unsaturated fat</h3>
          <p>Found in olive oil, avocado, nuts, seeds, and fatty fish. Includes both monounsaturated fats (olive oil, avocado) and polyunsaturated fats (fish, walnuts, sunflower oil) — the latter includes the essential omega-3 and omega-6 fatty acids.</p>
        </div>
      </div>''') +
    sec('''      <p>There's a third category worth knowing: industrially-produced trans fat, which behaves differently from both and is best minimized. <a href="trans-fat-explained.html">Read what trans fat is and why it was banned</a>.</p>''', bg="var(--color-fat-bg)", tight=True),
    [("healthy-high-fat-foods.html", "Healthy high-fat foods"), ("trans-fat-explained.html", "What is trans fat?"), ("fats.html", "What fat actually does")]
)

add(
    "omega-3-vs-omega-6",
    "Omega-3 vs Omega-6 Fatty Acids: Why Balance Matters",
    "The difference between omega-3 and omega-6 essential fatty acids, why most modern diets are skewed, and how to add more omega-3 sources.",
    "fat", "Fat Guide", "Omega-3 vs omega-6: why balance matters",
    "Both are essential fatty acids your body can't make on its own — but most modern diets get far more omega-6 than omega-3.",
    sec('''      <h2>Both are essential, but the ratio has shifted</h2>
      <p>Omega-3 and omega-6 fatty acids are both classified as essential — your body cannot synthesize them, so they must come from food.<sup class="ref"><a href="sources.html#f3">[1]</a></sup> Omega-6 is abundant in vegetable oils (corn, soybean, sunflower) widely used in processed food, while omega-3 is concentrated in fewer everyday foods — fatty fish, walnuts, flaxseed, and chia seeds. As a result, the typical modern diet supplies far more omega-6 than omega-3, a shift from the more balanced ratio humans evolved eating.</p>''') +
    sec('''      <h2>Practical ways to add more omega-3</h2>
      <ul class="checklist">
        <li><strong>Fatty fish</strong> (salmon, mackerel, sardines) 1–2 times per week</li>
        <li><strong>Walnuts</strong> as a snack or salad topping</li>
        <li><strong>Ground flaxseed or chia seeds</strong> stirred into oatmeal or yogurt</li>
        <li><strong>Algae-based omega-3 supplements</strong> for those who don't eat fish</li>
      </ul>
      <p>You don't need to eliminate omega-6 — it's essential too — just make a deliberate effort to add more omega-3-rich foods rather than relying entirely on whatever oil happens to be in packaged food.</p>''', bg="var(--color-fat-bg)", tight=True),
    [("healthy-high-fat-foods.html", "Healthy high-fat foods"), ("fats.html", "What fat actually does"), ("saturated-vs-unsaturated-fat.html", "Saturated vs. unsaturated fat")]
)

add(
    "low-fat-diet-risks",
    "The Hidden Risks of Very Low-Fat Diets",
    "What can go wrong when fat intake drops too low for too long — hormone production, vitamin absorption, and diet adherence.",
    "fat", "Fat Guide", "The hidden risks of very low-fat diets",
    "Cutting fat too aggressively doesn't just make food taste worse — it can quietly undercut hormone production and vitamin absorption.",
    sec('''      <ul class="checklist">
        <li><strong>Reduced hormone production</strong> — steroid hormones like testosterone and estrogen are synthesized from cholesterol, and a meta-analysis of intervention studies found men on low-fat diets (~20% of calories) had measurably lower testosterone than men on higher-fat diets (~40%).<sup class="ref"><a href="sources.html#f6">[1]</a></sup></li>
        <li><strong>Poor absorption of vitamins A, D, E, and K</strong> — these fat-soluble vitamins require dietary fat to be absorbed, regardless of how much you're eating in your food.<sup class="ref"><a href="sources.html#f5">[2]</a></sup></li>
        <li><strong>Essential fatty acid shortfalls</strong> — omega-3 and omega-6 fats can't be made by your body and must come from food<sup class="ref"><a href="sources.html#f3">[3]</a></sup></li>
        <li><strong>Menstrual irregularities</strong> — very low fat and low overall energy intake are linked with disrupted cycles</li>
        <li><strong>Poor diet adherence</strong> — fat slows digestion and increases satiety; very low-fat diets are often harder to stick to long-term</li>
      </ul>''', bg="var(--color-fat-bg)", tight=True) +
    sec('''      <p>The fix isn't complicated: stay within the recommended 20–35% of calories from fat rather than pushing dramatically lower.</p>
      <p><a href="how-much-fat-per-day.html" class="btn btn-primary">See recommended fat intake by calorie level →</a></p>'''),
    [("fats.html", "What fat actually does"), ("how-much-fat-per-day.html", "How much fat per day"), ("healthy-high-fat-foods.html", "Healthy high-fat foods")]
)

add(
    "healthy-high-fat-foods",
    "15 Healthy High-Fat Foods to Add to Your Diet",
    "A list of nutrient-dense high-fat foods — avocado, olive oil, fatty fish, nuts, and more — with approximate fat content per serving.",
    "fat", "Fat Guide", "15 healthy high-fat foods to add to your diet",
    "High-fat doesn't mean unhealthy — these foods pack fat alongside real nutritional value.",
    sec('''      <table class="data-table">
        <tr><th>Food</th><th>Fat per serving</th><th>Notes</th></tr>
        <tr><td>Avocado (½ medium)</td><td>~15 g</td><td>Mostly monounsaturated</td></tr>
        <tr><td>Olive oil (1 tbsp)</td><td>~14 g</td><td>Mostly monounsaturated</td></tr>
        <tr><td>Salmon (100g)</td><td>~13 g</td><td>Rich in omega-3</td></tr>
        <tr><td>Mackerel (100g)</td><td>~14 g</td><td>Rich in omega-3</td></tr>
        <tr><td>Walnuts (28g)</td><td>~18 g</td><td>Plant omega-3 source</td></tr>
        <tr><td>Almonds (28g)</td><td>~14 g</td><td>Also high in vitamin E</td></tr>
        <tr><td>Chia seeds (28g)</td><td>~9 g</td><td>Plus fiber &amp; omega-3</td></tr>
        <tr><td>Flaxseed, ground (2 tbsp)</td><td>~8 g</td><td>Plant omega-3 source</td></tr>
        <tr><td>Eggs (1 large)</td><td>~5 g</td><td>Also a complete protein</td></tr>
        <tr><td>Dark chocolate, 70%+ (28g)</td><td>~12 g</td><td>In moderation</td></tr>
        <tr><td>Cheese (28g)</td><td>~9 g</td><td>Mostly saturated</td></tr>
        <tr><td>Peanut butter (2 tbsp)</td><td>~16 g</td><td>Also a protein source</td></tr>
        <tr><td>Sardines (100g)</td><td>~11 g</td><td>Rich in omega-3</td></tr>
        <tr><td>Coconut oil (1 tbsp)</td><td>~14 g</td><td>Mostly saturated — use in moderation</td></tr>
        <tr><td>Pumpkin seeds (28g)</td><td>~13 g</td><td>Also high in protein</td></tr>
      </table>'''),
    [("fats.html", "What fat actually does"), ("saturated-vs-unsaturated-fat.html", "Saturated vs. unsaturated fat"), ("omega-3-vs-omega-6.html", "Omega-3 vs omega-6")]
)

add(
    "trans-fat-explained",
    "What Is Trans Fat, and Why Was It Banned?",
    "What trans fat is, how partially hydrogenated oils are made, and why regulators moved to eliminate them from the food supply.",
    "fat", "Fat Guide", "What is trans fat, and why was it banned?",
    "Unlike saturated and unsaturated fat, trans fat isn't really a natural dietary staple — most of it came from a manufacturing shortcut.",
    sec('''      <h2>Where trans fat came from</h2>
      <p>Most artificial trans fat is created through <strong>partial hydrogenation</strong> — pumping hydrogen into liquid vegetable oil to make it more solid and shelf-stable, historically used in margarine, shortening, and baked goods. The process changes the fat's molecular shape in a way that behaves differently in the body than naturally occurring fats.</p>''') +
    sec('''      <h2>Why regulators acted</h2>
      <p>Research linking artificial trans fat to negative changes in cholesterol (raising LDL while lowering HDL) led U.S. regulators to determine that partially hydrogenated oils were no longer "generally recognized as safe" as a food additive, with final compliance for removing them from the food supply completed in 2018. Many other countries have taken similar regulatory action.</p>
      <div class="panel">
        <h3>Where trans fat still shows up</h3>
        <p>Since the ban targeted partially hydrogenated oils specifically, trace amounts of trans fat can still occur naturally in small quantities in some dairy and meat products, and in some imported or shelf-stable packaged foods. Checking labels for "partially hydrogenated oil" in the ingredients list is still a reasonable habit.</p>
      </div>''', bg="var(--color-fat-bg)", tight=True),
    [("saturated-vs-unsaturated-fat.html", "Saturated vs. unsaturated fat"), ("fats.html", "What fat actually does"), ("healthy-high-fat-foods.html", "Healthy high-fat foods")]
)

# ------------------------------------------------------------------ CARBS --

add(
    "how-many-carbs-per-day",
    "How Many Carbs Should You Eat Per Day?",
    "The recommended daily carbohydrate range (45-65% of calories), what it looks like in grams, and when lower or higher intakes make sense.",
    "carbs", "Carbohydrate Guide", "How many carbs should you eat per day?",
    "The Acceptable Macronutrient Distribution Range for carbohydrates is 45-65% of total calories for most adults.",
    sec('''      <table class="data-table">
        <tr><th>Daily calories</th><th>45% (lower bound)</th><th>55% (typical)</th><th>65% (upper bound)</th></tr>
        <tr><td>1,800</td><td>203 g</td><td>248 g</td><td>293 g</td></tr>
        <tr><td>2,200</td><td>248 g</td><td>303 g</td><td>358 g</td></tr>
        <tr><td>2,600</td><td>293 g</td><td>358 g</td><td>423 g</td></tr>
        <tr><td>3,000</td><td>338 g</td><td>413 g</td><td>488 g</td></tr>
      </table>
      <p>This range is the Acceptable Macronutrient Distribution Range (AMDR) for carbohydrates.<sup class="ref"><a href="sources.html#c4">[1]</a></sup> Endurance athletes with heavy training volumes often sit at the higher end (or above it) to keep glycogen stores full,<sup class="ref"><a href="sources.html#c2">[2]</a></sup> while some people deliberately use lower-carb approaches for specific medical or performance goals — see our breakdown of <a href="low-carb-diet-effects.html">what actually happens on a low-carb diet</a>.</p>''') +
    sec('''      <p><a href="calculators.html" class="btn btn-primary">Get your personalized carb target →</a></p>''', bg="var(--color-carbs-bg)", tight=True),
    [("carbs.html", "What carbohydrates actually do"), ("what-is-glycogen.html", "What is glycogen?"), ("low-carb-diet-effects.html", "What happens on a low-carb diet")]
)

add(
    "what-is-glycogen",
    "What Is Glycogen? How Your Body Stores Carbs for Energy",
    "How glycogen works as your body's short-term carbohydrate storage in muscle and liver, and how much you can actually store.",
    "carbs", "Carbohydrate Guide", "What is glycogen?",
    "Every gram of carbohydrate you eat and don't use immediately gets bundled into glycogen — your body's rechargeable energy battery.",
    sec('''      <h2>How it works</h2>
      <p>After digestion, carbohydrates become glucose in your bloodstream. Glucose not needed right away is linked together into a branched storage molecule called <strong>glycogen</strong> and stored mainly in two places: your <strong>muscles</strong> (used locally by that muscle during activity) and your <strong>liver</strong> (which can release glucose back into the bloodstream to keep blood sugar stable, including fueling your brain between meals).</p>
      <p>Combined muscle and liver glycogen typically stores somewhere in the range of 400–500 grams of carbohydrate in an average adult, though this varies with body size, muscle mass, and training status.</p>''') +
    sec('''      <h2>Depletion and refilling</h2>
      <p>During prolonged or intense exercise, glycogen stores gradually empty, which is a major contributor to fatigue and declining performance late in a workout or endurance event.<sup class="ref"><a href="sources.html#c2">[1]</a></sup> Refilling glycogen happens through eating carbohydrates — athletes with heavy training schedules sometimes deliberately "carb load" before long events to maximize stores. See our <a href="carb-loading-for-athletes.html">carb loading guide</a> for the details.</p>''', bg="var(--color-carbs-bg)", tight=True),
    [("carbs.html", "What carbohydrates actually do"), ("carb-loading-for-athletes.html", "Carb loading for athletes"), ("how-many-carbs-per-day.html", "How many carbs per day")]
)

add(
    "low-carb-diet-effects",
    "What Happens to Your Body on a Low-Carb Diet",
    "The physiological changes that happen when carbohydrate intake drops sharply, including glycogen depletion, ketosis, and 'keto flu' symptoms.",
    "carbs", "Carbohydrate Guide", "What happens to your body on a low-carb diet",
    "Cutting carbs sharply forces your body to switch fuel sources — and that transition comes with a predictable set of effects.",
    sec('''      <h2>The adaptation period</h2>
      <p>When carbohydrate intake drops sharply, glycogen stores empty out within a few days, and your body increasingly relies on fat (producing ketones) and protein (via a process called gluconeogenesis) for fuel. This transition period is sometimes called "keto flu" and can include fatigue, headaches, irritability, and brain fog as your body adapts.<sup class="ref"><a href="sources.html#c6">[1]</a></sup></p>''') +
    sec('''      <h2>Effects to know about</h2>
      <ul class="checklist">
        <li><strong>Reduced high-intensity exercise performance</strong> — glycogen is the primary fuel for fast, powerful efforts, so low-carb intake can blunt performance in that specific type of activity</li>
        <li><strong>Increased muscle protein breakdown risk</strong> — with glycogen low, the body relies more on amino acids for energy, which can work against muscle-building goals unless protein intake is raised to compensate</li>
        <li><strong>Reduced fiber intake</strong> — cutting carbs often means cutting fiber-rich foods (whole grains, fruit, legumes) too, unless you deliberately replace that fiber elsewhere</li>
        <li><strong>Initial water weight loss</strong> — glycogen is stored with water, so early weight loss on a low-carb diet is partly water, not fat</li>
      </ul>''', bg="var(--color-carbs-bg)", tight=True) +
    sec('''      <p>None of this means low-carb diets don't work for some people and some goals — it just means the early effects are largely predictable physiology, not a sign something is wrong. Anyone on blood-sugar-lowering medication should talk to a doctor before cutting carbs significantly.</p>'''),
    [("what-is-glycogen.html", "What is glycogen?"), ("carbs.html", "What carbohydrates actually do"), ("simple-vs-complex-carbs.html", "Simple vs. complex carbs")]
)

add(
    "simple-vs-complex-carbs",
    "Simple vs. Complex Carbohydrates Explained",
    "The structural difference between simple and complex carbohydrates, how each affects blood sugar and digestion, and food examples of both.",
    "carbs", "Carbohydrate Guide", "Simple vs. complex carbohydrates explained",
    "The difference comes down to molecular size — and it affects how fast a carbohydrate hits your bloodstream.",
    sec('''      <h2>The structural difference</h2>
      <div class="two-col">
        <div class="panel">
          <h3>Simple carbohydrates</h3>
          <p>One or two sugar units (mono- or disaccharides) — table sugar, honey, fruit juice, candy. Digested and absorbed quickly, causing a faster rise in blood sugar.</p>
        </div>
        <div class="panel">
          <h3>Complex carbohydrates</h3>
          <p>Long chains of sugar units (polysaccharides) — whole grains, legumes, starchy vegetables. Take longer to digest, generally producing a slower, more moderate blood sugar response, especially when they retain their natural fiber.</p>
        </div>
      </div>''') +
    sec('''      <p>This isn't a strict "good vs. bad" split — whole fruit is technically a simple-carb source but comes packaged with fiber, water, and micronutrients that slow its digestion and add nutritional value. Highly processed simple carbs (soda, candy, refined white bread) are the ones most worth limiting, not simple carbs as a category. In general, building most of your carbohydrate intake around complex, minimally processed sources — and pairing carbs with protein, fat, or fiber — supports more stable blood sugar and better satiety.<sup class="ref"><a href="sources.html#c1">[1]</a></sup></p>
      <p>Curious how this connects to blood sugar response specifically? Read our <a href="glycemic-index-explained.html">explainer on the glycemic index</a>.</p>''', bg="var(--color-carbs-bg)", tight=True),
    [("glycemic-index-explained.html", "What is the glycemic index?"), ("carbs.html", "What carbohydrates actually do"), ("fiber-benefits.html", "Why fiber matters")]
)

add(
    "carb-loading-for-athletes",
    "Carb Loading: How Athletes Maximize Glycogen Stores",
    "How carb loading works, the modern protocol most athletes actually use, and who genuinely benefits from it.",
    "carbs", "Carbohydrate Guide", "Carb loading: how athletes maximize glycogen stores",
    "Carb loading isn't just eating a huge plate of pasta the night before a race — done properly, it's a deliberate glycogen-maximizing strategy.",
    sec('''      <h2>The idea behind it</h2>
      <p>Since depleted glycogen is a major driver of fatigue during prolonged exercise,<sup class="ref"><a href="sources.html#c2">[1]</a></sup> endurance athletes sometimes deliberately increase carbohydrate intake in the days before a long event to maximize how much glycogen their muscles and liver can store going in. The modern approach typically involves raising carbohydrate intake to roughly 8–12 g/kg body weight per day for 1–3 days beforehand, while also reducing training volume so the body isn't burning through the extra carbs as fast as they're consumed.</p>''') +
    sec('''      <h2>Who actually benefits</h2>
      <ul class="checklist">
        <li><strong>Endurance events lasting 90+ minutes</strong> — marathons, long cycling events, triathlons — where glycogen depletion is a realistic limiter</li>
        <li><strong>Not necessary for shorter workouts</strong> — a normal daily diet already provides enough glycogen for training sessions under about an hour</li>
        <li><strong>Not a weight-loss strategy</strong> — the extra stored glycogen comes with extra stored water, which shows up as temporary weight gain on the scale, not fat</li>
      </ul>''', bg="var(--color-carbs-bg)", tight=True),
    [("what-is-glycogen.html", "What is glycogen?"), ("how-many-carbs-per-day.html", "How many carbs per day"), ("carbs.html", "What carbohydrates actually do")]
)

add(
    "fiber-benefits",
    "Why Fiber Matters: Benefits of a High-Fiber Diet",
    "The health benefits of dietary fiber, the difference between soluble and insoluble fiber, and how much you actually need per day.",
    "carbs", "Carbohydrate Guide", "Why fiber matters: benefits of a high-fiber diet",
    "Fiber is a carbohydrate your body can't fully digest — and that's exactly what makes it useful.",
    sec('''      <h2>Soluble vs. insoluble fiber</h2>
      <div class="two-col">
        <div class="panel">
          <h3>Soluble fiber</h3>
          <p>Dissolves in water and forms a gel-like substance in digestion. Found in oats, beans, apples, and citrus fruit. Associated with improved cholesterol and more stable blood sugar.</p>
        </div>
        <div class="panel">
          <h3>Insoluble fiber</h3>
          <p>Doesn't dissolve, and adds bulk that helps move food through the digestive tract. Found in whole wheat, nuts, and vegetable skins. Associated with regularity and digestive health.</p>
        </div>
      </div>''') +
    sec('''      <h2>Why it matters</h2>
      <ul class="checklist">
        <li><strong>Digestive regularity</strong> — adds bulk to stool and supports normal bowel function</li>
        <li><strong>Cholesterol and blood sugar</strong> — soluble fiber in particular is linked to improved cholesterol levels and more gradual blood sugar rises</li>
        <li><strong>Satiety</strong> — high-fiber foods tend to be more filling per calorie, which can support weight management</li>
        <li><strong>Gut microbiome health</strong> — fiber feeds beneficial gut bacteria</li>
      </ul>
      <p>Most adults need roughly <strong>25 grams/day (women) to 38 grams/day (men)</strong> under age 50 — and most people fall short of that target.<sup class="ref"><a href="sources.html#c5">[1]</a></sup></p>''', bg="var(--color-carbs-bg)", tight=True),
    [("carbs.html", "What carbohydrates actually do"), ("simple-vs-complex-carbs.html", "Simple vs. complex carbs"), ("how-many-carbs-per-day.html", "How many carbs per day")]
)

add(
    "glycemic-index-explained",
    "What Is the Glycemic Index and Does It Matter?",
    "How the glycemic index measures a food's effect on blood sugar, what raises or lowers it, and how to use it practically.",
    "carbs", "Carbohydrate Guide", "What is the glycemic index, and does it matter?",
    "The glycemic index (GI) ranks how quickly a carbohydrate-containing food raises blood sugar compared to pure glucose.",
    sec('''      <h2>How it works</h2>
      <p>Foods are scored on a 0–100 scale: high-GI foods (white bread, white rice, most sugary drinks) cause a fast, sharp rise in blood sugar, while low-GI foods (most legumes, oats, non-starchy vegetables) produce a slower, more gradual rise.<sup class="ref"><a href="sources.html#c1">[1]</a></sup> Several factors affect a food's GI beyond the carb itself: fiber content, how processed or ripe it is, and what it's eaten alongside.</p>''') +
    sec('''      <h2>The practical takeaway</h2>
      <ul class="checklist">
        <li><strong>Pairing carbs with protein, fat, or fiber</strong> lowers the effective glycemic response of a meal, even if an individual ingredient has a high GI on its own</li>
        <li><strong>GI isn't the whole picture</strong> — glycemic load (which factors in portion size) and overall diet quality matter at least as much as a single food's GI ranking</li>
        <li><strong>It's most useful as a general pattern</strong> — favoring minimally processed, fiber-rich carb sources most of the time — rather than a strict food-by-food rulebook</li>
      </ul>''', bg="var(--color-carbs-bg)", tight=True),
    [("simple-vs-complex-carbs.html", "Simple vs. complex carbs"), ("carbs.html", "What carbohydrates actually do"), ("fiber-benefits.html", "Why fiber matters")]
)

add(
    "micronutrients-vs-macronutrients",
    "Micronutrients vs. Macronutrients: What's the Difference",
    "The difference between macronutrients (protein, fat, carbs) and micronutrients (vitamins, minerals), and why hitting your macros doesn't guarantee good nutrition.",
    "general", "Nutrition Basics", "Micronutrients vs. macronutrients: what's the difference",
    "Macros give you energy and building blocks. Micros keep the machinery running — and you need both.",
    sec('''      <h2>Two different jobs</h2>
      <p><strong>Macronutrients</strong> — protein, fat, and carbohydrates — are needed in large amounts and supply calories (energy). <strong>Micronutrients</strong> — vitamins and minerals like vitamin D, iron, calcium, and potassium — are needed in much smaller amounts and don't supply calories, but are essential for things like immune function, bone health, oxygen transport, and hundreds of enzyme reactions.</p>''') +
    sec('''      <div class="panel warn">
        <h3>Why "hitting your macros" isn't the whole story</h3>
        <p>It's entirely possible to hit a protein/fat/carb target using foods with almost no micronutrient value — and it's equally possible to hit the same targets with foods that are also rich in vitamins, minerals, and fiber. The macro number is the same either way, but the health outcome isn't. That's why food quality still matters even once your macros are dialed in.</p>
      </div>''', bg="var(--color-carbs-bg)", tight=True),
    [("carbs.html", "What carbohydrates actually do"), ("fiber-benefits.html", "Why fiber matters"), ("iifym-flexible-dieting.html", "IIFYM: does flexible dieting work?")]
)

add(
    "how-to-read-a-nutrition-label",
    "How to Read a Nutrition Label (Macros Edition)",
    "How to quickly find protein, fat, and carbohydrate info on a nutrition label, and the common mistakes people make reading serving sizes.",
    "general", "Nutrition Basics", "How to read a nutrition label (macros edition)",
    "The label has everything you need to track macros — if you know where to look and what the serving size actually means.",
    sec('''      <h2>Where to look</h2>
      <ul class="checklist">
        <li><strong>Serving size first</strong> — every number on the label is per serving, not per package. A bag that "looks like one serving" is often 2–3</li>
        <li><strong>Total Carbohydrate</strong> includes fiber and sugar — the "Dietary Fiber" sub-line is already counted inside the total, not extra</li>
        <li><strong>Total Fat</strong> includes the saturated and trans fat sub-lines, same logic — they're a breakdown, not additional grams</li>
        <li><strong>Protein</strong> is usually the simplest line, listed directly in grams per serving</li>
      </ul>''') +
    sec('''      <div class="panel">
        <h3>Common mistake</h3>
        <p>Multiplying by the wrong number of servings is the single biggest source of tracking error. Before logging a food, check how many servings you're actually eating and multiply every number on the label accordingly — not just the calories.</p>
      </div>''', bg="var(--color-fat-bg)", tight=True),
    [("high-protein-foods-list.html", "High-protein foods list"), ("calculators.html", "Macro calculator"), ("macros-for-weight-loss.html", "Macros for fat loss")]
)

add(
    "vegan-macros-guide",
    "Vegan Macros: Hitting Your Targets Without Meat or Dairy",
    "A practical guide to hitting protein, fat, and carb targets on a fully plant-based diet.",
    "general", "Nutrition Basics", "Vegan macros: hitting your targets without meat or dairy",
    "Every macro target on this site is achievable on a vegan diet — it just takes knowing which plant foods to lean on.",
    sec('''      <div class="two-col">
        <div class="panel">
          <h3>Protein</h3>
          <p>Lean on tofu, tempeh, seitan, legumes, and a plant protein powder to hit the higher end of your protein range without huge food volume. See our <a href="plant-based-protein-sources.html">full plant-based protein list</a>.</p>
        </div>
        <div class="panel">
          <h3>Fat</h3>
          <p>Olive oil, avocado, nuts, seeds, and nut butters cover fat easily — pay attention to getting enough omega-3 specifically, since fish is off the table (walnuts, flax, chia, or an algae-based supplement).</p>
        </div>
      </div>''', bg="var(--color-protein-bg)", tight=True) +
    sec('''      <p>Carbs are usually the easiest target to hit on a vegan diet — whole grains, fruit, and legumes cover it naturally, and often add useful fiber alongside. The main planning challenge is protein density per calorie, since most whole plant proteins carry more carbs alongside them than animal protein does — which is a feature, not a bug, as long as it fits your total macro plan.</p>'''),
    [("plant-based-protein-sources.html", "Plant-based protein sources"), ("complete-vs-incomplete-protein.html", "Complete vs. incomplete protein"), ("calculators.html", "Calculate your macros")]
)

add(
    "intermittent-fasting-and-macros",
    "Intermittent Fasting and Macros: Does Timing Matter?",
    "How intermittent fasting interacts with your macro targets, and whether meal timing itself changes results independent of what you eat.",
    "general", "Nutrition Basics", "Intermittent fasting and macros: does timing matter?",
    "Fasting changes when you eat. It doesn't change the math of what you eat — your daily macro totals still do the heavy lifting.",
    sec('''      <p>Intermittent fasting (commonly a 16:8 or similar eating-window schedule) restricts <em>when</em> you eat, not what your protein, fat, and carb totals add up to across the day. For most outcomes — fat loss, muscle maintenance — total daily macros and calories appear to matter far more than the specific hours they're eaten in.</p>''') +
    sec('''      <ul class="checklist">
        <li><strong>Fewer, larger meals</strong> — fasting naturally compresses eating into fewer meals, so each one needs to carry more protein to still hit your daily distribution target</li>
        <li><strong>Practical benefit for some people</strong> — a shorter eating window can make calorie counting simpler and curb late-night snacking, independent of any special metabolic effect</li>
        <li><strong>Not automatically better for muscle building</strong> — spreading protein across more meals may have a slight edge for muscle protein synthesis, so heavy fasting windows are a tradeoff to be aware of for that specific goal</li>
      </ul>''', bg="var(--color-carbs-bg)", tight=True),
    [("protein-timing.html", "Does protein timing matter?"), ("calculators.html", "Calculate your macros"), ("macros-for-muscle-gain.html", "Macros for building muscle")]
)

add(
    "cutting-bulking-maintenance-explained",
    "Cutting vs. Bulking vs. Maintenance: Which Phase Are You In?",
    "What the terms cutting, bulking, and maintenance actually mean in terms of calories and macros, and how to tell which one you should be doing.",
    "general", "Nutrition Basics", "Cutting vs. bulking vs. maintenance: which phase are you in?",
    "Three phases, three different calorie targets — and each one calls for a different macro emphasis.",
    sec('''      <table class="data-table">
        <tr><th>Phase</th><th>Calories</th><th>Main macro priority</th></tr>
        <tr><td>Cutting</td><td>Deficit (~15–25% below TDEE)</td><td>Protein up (~1.8 g/kg) to protect muscle</td></tr>
        <tr><td>Maintenance</td><td>At TDEE</td><td>Standard ranges across all three</td></tr>
        <tr><td>Bulking</td><td>Surplus (~10–15% above TDEE)</td><td>Adequate carbs for training performance</td></tr>
      </table>
      <p>None of these are permanent — most people cycle between phases over months or years depending on their current goal, body composition, and how their training is going.</p>''') +
    sec('''      <p><a href="macros-for-weight-loss.html">Read the full cutting macro breakdown</a> or <a href="macros-for-muscle-gain.html">the full bulking macro breakdown</a>.</p>''', bg="var(--color-fat-bg)", tight=True),
    [("macros-for-weight-loss.html", "Macros for fat loss"), ("macros-for-muscle-gain.html", "Macros for building muscle"), ("tdee-vs-bmr.html", "BMR vs. TDEE")]
)

add(
    "protein-powder-101",
    "Protein Powder 101: Whey, Casein, and Plant Blends Explained",
    "The practical differences between whey, casein, and plant-based protein powders, and how to choose between them.",
    "protein", "Protein Guide", "Protein powder 101: whey, casein, and plant blends",
    "Protein powder is just a convenient, concentrated food — the type mostly affects digestion speed and dietary fit, not whether it \"works.\"",
    sec('''      <div class="two-col">
        <div class="panel">
          <h3>Whey protein</h3>
          <p>A complete, fast-digesting milk-derived protein. The most researched protein supplement and a convenient way to hit a daily protein target, especially post-workout. Not suitable for those avoiding dairy.</p>
        </div>
        <div class="panel">
          <h3>Casein protein</h3>
          <p>Also milk-derived, but digests much more slowly, releasing amino acids gradually. Often used before bed for a slow overnight supply, though total daily intake still matters more than this specific timing choice.</p>
        </div>
      </div>''', bg="var(--color-protein-bg)", tight=True) +
    sec('''      <h2>Plant-based blends</h2>
      <p>Usually a mix of pea, rice, and/or hemp protein, combined specifically because blending sources compensates for any single plant protein's weaker amino acids — a practical example of variety solving what one plant protein alone doesn't.<sup class="ref"><a href="sources.html#p1">[1]</a></sup> A good plant blend performs comparably to whey for most practical purposes.</p>
      <p>Bottom line: pick whichever type fits your diet and stomach best — the protein content is what matters most, not the source.</p>'''),
    [("complete-vs-incomplete-protein.html", "Complete vs. incomplete protein"), ("plant-based-protein-sources.html", "Plant-based protein sources"), ("protein-timing.html", "Does protein timing matter?")]
)

add(
    "sugar-vs-starch",
    "Sugar vs. Starch: Are All Carbs Created Equal?",
    "The difference between sugar and starch as types of carbohydrate, how your body processes each, and what it means for your diet.",
    "carbs", "Carbohydrate Guide", "Sugar vs. starch: are all carbs created equal?",
    "Both break down to glucose eventually — but the path they take there is very different.",
    sec('''      <p><strong>Sugars</strong> are simple carbohydrates — one or two linked sugar units — found naturally in fruit and dairy, or added to food as table sugar, syrup, or honey. They're absorbed quickly. <strong>Starches</strong> are long chains of glucose units (a complex carbohydrate) found in grains, potatoes, and legumes, and take longer to break down during digestion, generally producing a more gradual rise in blood sugar.</p>''') +
    sec('''      <div class="panel warn">
        <h3>The nuance</h3>
        <p>Naturally occurring sugar in whole fruit comes packaged with fiber and water that slow its absorption, unlike the same amount of sugar in a soda. And highly refined starches (white bread, white rice) can behave more like sugar in terms of blood sugar response than a whole-grain starch would. The <strong>form</strong> of the carbohydrate — whole and fiber-intact vs. refined — often matters as much as whether it's technically a "sugar" or a "starch."</p>
      </div>'''),
    [("simple-vs-complex-carbs.html", "Simple vs. complex carbs"), ("glycemic-index-explained.html", "What is the glycemic index?"), ("fiber-benefits.html", "Why fiber matters")]
)

add(
    "ketogenic-diet-explained",
    "The Ketogenic Diet Explained: Macros, Benefits, and Risks",
    "How the ketogenic diet's macro split works, what ketosis actually is, and who should be cautious about trying it.",
    "carbs", "Carbohydrate Guide", "The ketogenic diet explained: macros, benefits, and risks",
    "Keto isn't just \"low carb\" — it's a specific macro ratio designed to push your body into a distinct metabolic state.",
    sec('''      <h2>The macro split</h2>
      <p>A standard ketogenic diet typically targets roughly <strong>70–80% of calories from fat, 15–25% from protein, and only about 5–10% from carbohydrate</strong> — often under 50g of carbs per day. That's dramatically below the standard 45–65% AMDR for carbs.<sup class="ref"><a href="sources.html#c4">[1]</a></sup> At that level, glycogen stores empty out and the body shifts to producing ketones from fat as its primary fuel source — the metabolic state called ketosis.</p>''') +
    sec('''      <h2>What to know before trying it</h2>
      <ul class="checklist">
        <li><strong>The adaptation period</strong> can include fatigue, headaches, and irritability ("keto flu") as the body shifts fuel sources — see our <a href="low-carb-diet-effects.html">full breakdown of low-carb diet effects</a></li>
        <li><strong>High-intensity performance can suffer</strong>, since glycogen is the preferred fuel for fast, powerful efforts</li>
        <li><strong>Not automatically appropriate for everyone</strong> — anyone on blood-sugar-lowering or blood-pressure medication should talk to a doctor before attempting it, since the diet can significantly affect both</li>
      </ul>''', bg="var(--color-carbs-bg)", tight=True),
    [("low-carb-diet-effects.html", "What happens on a low-carb diet"), ("what-is-glycogen.html", "What is glycogen?"), ("how-many-carbs-per-day.html", "How many carbs per day")]
)

add(
    "high-protein-breakfast-ideas",
    "High-Protein Breakfast Ideas That Actually Fill You Up",
    "Practical high-protein breakfast combinations and roughly how much protein each provides.",
    "protein", "Protein Guide", "High-protein breakfast ideas that actually fill you up",
    "Breakfast is the meal most people under-eat protein at — small swaps close the gap fast.",
    sec('''      <table class="data-table">
        <tr><th>Breakfast</th><th>Approx. protein</th></tr>
        <tr><td>3 eggs + 1 cup cottage cheese</td><td>~40 g</td></tr>
        <tr><td>Greek yogurt (1 cup) + handful of almonds</td><td>~25 g</td></tr>
        <tr><td>Protein smoothie (1 scoop powder + milk + fruit)</td><td>~30 g</td></tr>
        <tr><td>Oats made with milk + scoop of protein powder</td><td>~30 g</td></tr>
        <tr><td>Tofu scramble (200g) + vegetables</td><td>~16 g</td></tr>
        <tr><td>2 eggs + 2 turkey sausage links + toast</td><td>~28 g</td></tr>
      </table>
      <p>A simple pattern: pick one protein-dense anchor (eggs, Greek yogurt, cottage cheese, tofu, or a protein powder) and build the rest of the meal around it, rather than treating protein as an afterthought.</p>'''),
    [("high-protein-foods-list.html", "Full high-protein foods list"), ("how-much-protein-per-day.html", "How much protein per day"), ("protein-timing.html", "Does protein timing matter?")]
)

add(
    "meal-frequency-and-metabolism",
    "Does Meal Frequency Matter for Macros and Metabolism?",
    "Whether eating more or fewer meals per day changes metabolism or macro results, according to the research.",
    "general", "Nutrition Basics", "Does meal frequency matter for macros and metabolism?",
    "Three meals, six meals, one meal — does the number actually change anything, or just how you get to the same daily total?",
    sec('''      <p>The idea that eating more frequently "stokes your metabolism" isn't well supported — total daily calories and macros appear to matter far more than how many meals they're split across. Digesting food does burn a small number of calories (the thermic effect of food), but that's roughly proportional to total food eaten, not the number of separate meals.</p>''') +
    sec('''      <div class="panel">
        <h3>Where meal frequency does matter</h3>
        <p>Practical factors, not metabolic ones: more frequent smaller meals may help some people manage hunger and adherence, while fewer larger meals may suit others' schedules and appetite better. For muscle building specifically, spreading protein across 3–4 meals (rather than one large dose) appears to modestly support muscle protein synthesis better.<sup class="ref"><a href="sources.html#p2">[1]</a></sup> Pick the pattern you can sustain — it's a bigger lever than the theoretical metabolic difference.</p>
      </div>''', bg="var(--color-protein-bg)", tight=True),
    [("protein-timing.html", "Does protein timing matter?"), ("intermittent-fasting-and-macros.html", "Intermittent fasting and macros"), ("calculators.html", "Calculate your macros")]
)

add(
    "body-recomposition-explained",
    "Body Recomposition: Building Muscle and Losing Fat at Once",
    "What body recomposition means, who it actually works for, and how to set macros for it.",
    "general", "Nutrition Basics", "Body recomposition: building muscle and losing fat at once",
    "Losing fat and building muscle simultaneously is possible — but it's slower than doing either one at a time, and works best for specific people.",
    sec('''      <h2>Who it works best for</h2>
      <ul class="checklist">
        <li><strong>Beginners to resistance training</strong> — new lifters can often build muscle and lose fat at the same time, a rare window that shrinks with training experience</li>
        <li><strong>People returning after a break</strong> — "muscle memory" allows relatively fast muscle regain even in a calorie deficit</li>
        <li><strong>People with more body fat to lose</strong> — extra stored energy (fat) can help offset the calorie cost of building new muscle</li>
      </ul>''') +
    sec('''      <h2>Setting macros for recomposition</h2>
      <p>Calories are typically set at or very close to maintenance (TDEE), rather than a clear deficit or surplus. Protein is kept high — similar to a cutting phase, around 1.8–2.2 g/kg — since it's doing double duty: supporting muscle growth and protecting existing muscle. Progress is usually slower and harder to see on the scale than a dedicated cut or bulk, so tracking measurements or photos matters more than the number on the scale.</p>''', bg="var(--color-carbs-bg)", tight=True),
    [("macros-for-muscle-gain.html", "Macros for building muscle"), ("macros-for-weight-loss.html", "Macros for fat loss"), ("cutting-bulking-maintenance-explained.html", "Cutting vs. bulking vs. maintenance")]
)

add(
    "alcohol-and-macros",
    "Alcohol and Macros: How Drinking Fits Into Your Targets",
    "How alcohol interacts with your calorie and macro targets, since it doesn't cleanly fit into protein, fat, or carbs.",
    "general", "Nutrition Basics", "Alcohol and macros: how drinking fits into your targets",
    "Alcohol supplies calories — about 7 per gram, between fat and carbs — but it isn't a macronutrient, which makes it easy to under-account for.",
    sec('''      <p>Alcohol provides roughly <strong>7 calories per gram</strong>, more than protein or carbs (4) and just under fat (9), but it isn't classified as a macronutrient because it isn't required for any bodily function. Those calories still count toward your daily total even though they don't show up on a "protein/fat/carb" macro split — a standard drink can easily add 100–200 calories that are easy to forget when tracking.</p>''') +
    sec('''      <div class="panel warn">
        <h3>Practical approach</h3>
        <p>Most people who track macros simply subtract alcohol calories from their remaining daily calorie budget for the day (often treated as "extra fat calories" for simplicity, since it's not far off gram-for-gram). It's also worth knowing that alcohol can temporarily reduce fat burning while it's being processed, and mixed drinks often carry substantial hidden carbs from sugary mixers.</p>
      </div>''', bg="var(--color-fat-bg)", tight=True),
    [("calculators.html", "Calculate your macros"), ("macros-for-weight-loss.html", "Macros for fat loss")]
)

add(
    "cholesterol-explained",
    "Cholesterol Explained: Dietary vs. Blood Cholesterol",
    "The difference between the cholesterol you eat and the cholesterol measured in your blood, and why they aren't the same thing.",
    "fat", "Fat Guide", "Cholesterol explained: dietary vs. blood cholesterol",
    "Eating cholesterol and having high blood cholesterol are related, but not in the direct one-to-one way many people assume.",
    sec('''      <p><strong>Dietary cholesterol</strong> is the cholesterol found in food — eggs, shellfish, organ meats. <strong>Blood cholesterol</strong> is what's measured in a lipid panel (LDL, HDL, triglycerides) and is influenced by many factors, with your liver producing most of your body's cholesterol regardless of diet. For most people, dietary cholesterol has a smaller effect on blood cholesterol than saturated and trans fat intake does.<sup class="ref"><a href="sources.html#f2">[1]</a></sup></p>''') +
    sec('''      <div class="panel">
        <h3>Why this matters for fat intake</h3>
        <p>Cholesterol is also the raw material your body uses to build steroid hormones like testosterone and estrogen — one more reason very low-fat diets can backfire on hormone production. See our piece on <a href="low-fat-diet-risks.html">the hidden risks of very low-fat diets</a> for the full picture.</p>
      </div>''', bg="var(--color-fat-bg)", tight=True),
    [("saturated-vs-unsaturated-fat.html", "Saturated vs. unsaturated fat"), ("low-fat-diet-risks.html", "Risks of very low-fat diets"), ("fats.html", "What fat actually does")]
)

add(
    "water-weight-vs-fat-loss",
    "Water Weight vs. Fat Loss: Why the Scale Lies",
    "Why the scale can jump or drop several pounds overnight that have nothing to do with actual fat loss or gain, and what's really going on.",
    "general", "Nutrition Basics", "Water weight vs. fat loss: why the scale lies",
    "A pound of fat doesn't appear or disappear overnight — but a pound of water absolutely can.",
    sec('''      <ul class="checklist">
        <li><strong>Carbohydrate changes</strong> — every gram of stored glycogen holds roughly 3 grams of water alongside it, so cutting carbs sharply can drop several pounds of water weight in days, and eating more carbs can add it right back<sup class="ref"><a href="sources.html#c2">[1]</a></sup></li>
        <li><strong>Sodium intake</strong> — a high-sodium meal can cause temporary water retention that shows up on the scale the next morning</li>
        <li><strong>Hormonal fluctuations</strong> — water retention around the menstrual cycle is common and normal</li>
        <li><strong>Hard training sessions</strong> — muscles can hold extra water temporarily during recovery and repair</li>
      </ul>''', bg="var(--color-carbs-bg)", tight=True) +
    sec('''      <p>None of this means the scale is useless — it just means single-day readings are noisy. A weekly average, taken under similar conditions (same time of day, similar hydration), is a far more reliable signal of actual fat loss or gain than any individual day's number.</p>'''),
    [("what-is-glycogen.html", "What is glycogen?"), ("macros-for-weight-loss.html", "Macros for fat loss"), ("low-carb-diet-effects.html", "What happens on a low-carb diet")]
)

add(
    "macros-for-endurance-vs-strength-athletes",
    "Macros for Endurance Athletes vs. Strength Athletes",
    "How macro priorities differ between endurance athletes and strength athletes, and why one-size-fits-all macro advice doesn't work for both.",
    "general", "Nutrition Basics", "Macros for endurance athletes vs. strength athletes",
    "A marathoner and a powerlifter both train hard — but their fuel needs point in different directions.",
    sec('''      <div class="two-col">
        <div class="panel">
          <h3>Endurance athletes</h3>
          <p>Carbohydrate needs are often at or above the top of the standard AMDR range — sometimes 8–12 g/kg on heavy training days — since glycogen availability directly limits performance in long events.<sup class="ref"><a href="sources.html#c2">[1]</a></sup> Protein needs are still elevated versus sedentary baselines, but generally lower than a strength athlete's, around 1.2–1.6 g/kg.</p>
        </div>
        <div class="panel">
          <h3>Strength &amp; physique athletes</h3>
          <p>Protein needs sit at the higher end, 1.6–2.2 g/kg, to support muscle repair and growth from resistance training.<sup class="ref"><a href="sources.html#p2">[2]</a></sup> Carbohydrate needs are typically more moderate than an endurance athlete's, since training sessions are shorter and less glycogen-depleting overall.</p>
        </div>
      </div>''', bg="var(--color-carbs-bg)", tight=True) +
    sec('''      <p>Fat generally stays in the standard 20–35% range for both groups. The takeaway: your sport's energy demands should shape your macro split, not a single generic ratio applied to everyone.</p>'''),
    [("how-many-carbs-per-day.html", "How many carbs per day"), ("how-much-protein-per-day.html", "How much protein per day"), ("carb-loading-for-athletes.html", "Carb loading for athletes")]
)

# --------------------------------------------------------------- GENERAL --

add(
    "tdee-vs-bmr",
    "BMR vs. TDEE: What's the Difference and Why It Matters",
    "The difference between Basal Metabolic Rate (BMR) and Total Daily Energy Expenditure (TDEE), and how the Mifflin-St Jeor equation estimates both.",
    "general", "Calculator Guide", "BMR vs. TDEE: what's the difference?",
    "These two numbers are the foundation of every calorie and macro target on this site — here's what each one actually measures.",
    sec('''      <h2>BMR: energy at complete rest</h2>
      <p>Basal Metabolic Rate is the number of calories your body burns just to stay alive — breathing, circulating blood, maintaining body temperature — if you did nothing but lie still for 24 hours. Our calculator estimates it using the <strong>Mifflin-St Jeor equation</strong>, a widely used, research-validated formula:<sup class="ref"><a href="sources.html#cal1">[1]</a></sup></p>
      <div class="panel">
        <p><strong>Men:</strong> BMR = 10 × weight(kg) + 6.25 × height(cm) − 5 × age + 5<br>
        <strong>Women:</strong> BMR = 10 × weight(kg) + 6.25 × height(cm) − 5 × age − 161</p>
      </div>''') +
    sec('''      <h2>TDEE: your real daily number</h2>
      <p>Total Daily Energy Expenditure adds everything else on top of BMR: digesting food, daily movement, and exercise. It's estimated by multiplying BMR by an activity multiplier, ranging from about 1.2 (sedentary) to 1.9 (very high activity, physical job plus training).<sup class="ref"><a href="sources.html#cal2">[2]</a></sup> TDEE — not BMR — is the number that represents "maintenance calories," and it's the starting point for setting a deficit (fat loss) or surplus (muscle gain) goal.</p>
      <p><a href="calculators.html" class="btn btn-primary">Calculate my BMR and TDEE →</a></p>''', bg="var(--color-fat-bg)", tight=True),
    [("calculators.html", "Full macro calculator"), ("macros-for-weight-loss.html", "Macros for fat loss"), ("macros-for-muscle-gain.html", "Macros for building muscle")]
)

add(
    "macros-for-weight-loss",
    "How to Set Your Macros for Fat Loss",
    "A practical framework for setting protein, fat, and carb targets during a fat-loss phase, including why protein should go up, not down.",
    "general", "Calculator Guide", "How to set your macros for fat loss",
    "Fat loss ultimately requires a calorie deficit — but how you fill that deficit changes whether you lose fat, or lose muscle along with it.",
    sec('''      <ul class="checklist">
        <li><strong>Set a moderate deficit</strong> — roughly 15–25% below your TDEE (maintenance calories) is sustainable for most people; more aggressive cuts are harder to stick to and increase muscle loss risk</li>
        <li><strong>Raise protein, don't cut it</strong> — aim for the higher end of the normal range, around 1.8 g/kg body weight, to help preserve muscle while in a deficit<sup class="ref"><a href="sources.html#p2">[1]</a></sup></li>
        <li><strong>Keep fat at least at the AMDR floor</strong> — don't drop below roughly 20% of calories, to protect hormone production and vitamin absorption</li>
        <li><strong>Let carbs fill the rest</strong> — after protein and fat are set, remaining calories go to carbohydrates, which support training performance and daily energy</li>
      </ul>''', bg="var(--color-carbs-bg)", tight=True) +
    sec('''      <p>Our calculator applies exactly this logic automatically when you select "Lose fat" as your goal — it raises your protein target and sets a moderate deficit for you.</p>
      <p><a href="calculators.html" class="btn btn-primary">Set my fat-loss macros →</a></p>'''),
    [("calculators.html", "Full macro calculator"), ("how-much-protein-per-day.html", "How much protein per day"), ("tdee-vs-bmr.html", "BMR vs. TDEE")]
)

add(
    "macros-for-muscle-gain",
    "How to Set Your Macros for Building Muscle (Bulking)",
    "A practical framework for setting protein, fat, and carb targets to build muscle while minimizing unnecessary fat gain.",
    "general", "Calculator Guide", "How to set your macros for building muscle",
    "Building muscle requires a calorie surplus and enough protein — but 'more is better' isn't the right mindset for either one.",
    sec('''      <ul class="checklist">
        <li><strong>Use a modest surplus</strong> — a large calorie surplus doesn't build muscle faster, it mostly adds fat faster. A moderate surplus of roughly 10–15% above TDEE is a reasonable starting point.</li>
        <li><strong>Protein: 1.6–2.2 g/kg</strong> — this range supports maximal muscle protein synthesis; going higher generally doesn't add extra benefit<sup class="ref"><a href="sources.html#p2">[1]</a></sup></li>
        <li><strong>Don't skimp on carbs</strong> — adequate carbohydrate intake keeps glycogen stores full, which directly supports training performance and recovery<sup class="ref"><a href="sources.html#c2">[2]</a></sup></li>
        <li><strong>Keep fat in the normal range</strong> — 20–35% of calories supports hormone production, which matters for muscle building<sup class="ref"><a href="sources.html#f6">[3]</a></sup></li>
        <li><strong>Track your rate of gain</strong> — if the scale is climbing quickly, the surplus is probably larger than it needs to be</li>
      </ul>''', bg="var(--color-protein-bg)", tight=True) +
    sec('''      <p>Selecting "Build muscle" in our calculator applies a modest surplus and a higher protein target automatically.</p>
      <p><a href="calculators.html" class="btn btn-primary">Set my muscle-building macros →</a></p>'''),
    [("calculators.html", "Full macro calculator"), ("protein-for-muscle-growth.html", "Protein for muscle growth"), ("what-is-glycogen.html", "What is glycogen?")]
)

add(
    "iifym-flexible-dieting",
    "IIFYM: What Is Flexible Dieting and Does It Work?",
    "What 'If It Fits Your Macros' (IIFYM) means, its real pros and cons, and a practical middle-ground approach.",
    "general", "Calculator Guide", "IIFYM: what is flexible dieting, and does it work?",
    "\"If It Fits Your Macros\" (IIFYM) is the idea that as long as you hit your protein, fat, and carb targets, the specific foods you eat them from don't matter.",
    sec('''      <h2>The case for it</h2>
      <p>IIFYM's biggest strength is adherence: no foods are strictly off-limits, which makes it easier for many people to sustain over the long term compared to highly restrictive diets. If your macro targets are set appropriately for your goal, hitting them consistently — regardless of exact food choices — genuinely does drive most of the physical outcome (fat loss, muscle gain, maintenance).</p>''') +
    sec('''      <h2>Where it falls short</h2>
      <ul class="checklist">
        <li><strong>Micronutrients aren't tracked</strong> — hitting your macros with candy and processed food technically "fits," but won't supply the vitamins, minerals, and fiber whole foods provide</li>
        <li><strong>Fiber and satiety often suffer</strong> — highly processed foods tend to be less filling per calorie, which can make the diet harder to sustain, not easier</li>
        <li><strong>It's a framework, not a food-quality guarantee</strong> — the macros can be "right" while the diet is still nutritionally poor</li>
      </ul>
      <div class="panel">
        <h3>A practical middle ground</h3>
        <p>Build the majority of your diet — most nutrition coaches suggest roughly 80–90% — from whole, minimally processed foods that naturally hit your macro and fiber targets, and use the remaining room flexibly for foods you enjoy. You get the adherence benefits of flexibility without giving up nutritional quality.</p>
      </div>''', bg="var(--color-fat-bg)", tight=True),
    [("calculators.html", "Full macro calculator"), ("macros-for-weight-loss.html", "Macros for fat loss"), ("macros-for-muscle-gain.html", "Macros for building muscle")]
)


CATEGORY_LABEL = {
    "protein": "Protein",
    "fat": "Fat",
    "carbs": "Carbohydrates",
    "general": "Calculators &amp; Planning",
}
CATEGORY_PILL = {"protein": "protein", "fat": "fat", "carbs": "carbs", "general": "carbs"}


def build_hub():
    by_cat = {}
    for a in ARTICLES:
        by_cat.setdefault(a["category"], []).append(a)

    sections = ""
    order = ["protein", "fat", "carbs", "general"]
    bg = {"protein": "var(--color-protein-bg)", "fat": "var(--color-fat-bg)", "carbs": "var(--color-carbs-bg)", "general": None}
    for cat in order:
        items = by_cat.get(cat, [])
        if not items:
            continue
        badge_class = CATEGORY_PILL[cat] if cat != "general" else "neutral"
        badge_icon = {"protein": "icon-protein", "fat": "icon-fat", "carbs": "icon-carbs", "general": "icon-article"}[cat]
        cards = "\n".join(
            f'        <a href="{a["slug"]}.html" class="card {CATEGORY_PILL[cat]}"><span class="icon-badge {badge_class}"><svg class="icon" aria-hidden="true"><use href="#{badge_icon}"/></svg></span><h3>{a["h1"]}</h3><p>{a["meta"]}</p></a>'
            for a in items
        )
        style = f' style="background:{bg[cat]}"' if bg[cat] else ""
        sections += f'''  <section{style}>
    <div class="container">
      <h2><span class="pill {CATEGORY_PILL[cat]}">{CATEGORY_LABEL[cat]}</span></h2>
      <div class="card-grid">
{cards}
      </div>
    </div>
  </section>
'''

    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://pagead2.googlesyndication.com https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.googletagservices.com; style-src 'self' 'unsafe-inline' https://*.googlesyndication.com; img-src 'self' data: https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.gstatic.com; font-src 'self'; connect-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; frame-src https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>Articles | GetMacros.net</title>
<meta name="description" content="Every GetMacros.net article in one place — protein, fat, and carbohydrate guides, food lists, and calculator explainers.">
<link rel="canonical" href="https://getmacros.net/articles.html">
<link rel="stylesheet" href="css/style.css">
<script src="js/img-fallback.js"></script>
{ADSENSE_LOADER}
</head>
<body>
{ICON_SPRITE}
{NAV}

<main>
  <section class="page-hero" style="background:var(--color-primary-dark); color:#fff;">
    <div class="container">
      <p class="eyebrow">Library</p>
      <h1>All articles</h1>
      <p>Every guide on GetMacros.net, organized by topic. Start with the core pages if you're new — <a href="protein.html" style="color:#fff;text-decoration:underline;">Protein</a>, <a href="fats.html" style="color:#fff;text-decoration:underline;">Fat</a>, <a href="carbs.html" style="color:#fff;text-decoration:underline;">Carbohydrates</a> — or dive into a specific question below.</p>
    </div>
  </section>

{sections}
</main>

{AD_SLOT}
{FOOTER}

<script src="js/main.js"></script>
<script src="js/reveal.js"></script>
</body>
</html>
'''
    path = os.path.join(ROOT, "articles.html")
    with open(path, "w") as f:
        f.write(html)
    print("wrote", path)


CORE_PAGES = [
    ("", "1.0"),  # homepage
    ("protein.html", "0.9"),
    ("fats.html", "0.9"),
    ("carbs.html", "0.9"),
    ("calculators.html", "0.9"),
    ("articles.html", "0.8"),
    ("sources.html", "0.5"),
]


def build_sitemap():
    domain = "https://getmacros.net"
    urls = [f"{domain}/{p}" for p, _ in CORE_PAGES]
    priorities = {p: pr for p, pr in CORE_PAGES}
    entries = []
    for path, priority in CORE_PAGES:
        entries.append(f"  <url>\n    <loc>{domain}/{path}</loc>\n    <priority>{priority}</priority>\n  </url>")
    for a in ARTICLES:
        entries.append(f'  <url>\n    <loc>{domain}/{a["slug"]}.html</loc>\n    <priority>0.7</priority>\n  </url>')
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(entries) + "\n</urlset>\n"
    with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
        f.write(xml)
    print("wrote", os.path.join(ROOT, "sitemap.xml"), f"({len(CORE_PAGES) + len(ARTICLES)} urls)")

    robots = "User-agent: *\nAllow: /\nSitemap: https://getmacros.net/sitemap.xml\n"
    with open(os.path.join(ROOT, "robots.txt"), "w") as f:
        f.write(robots)
    print("wrote", os.path.join(ROOT, "robots.txt"))


# --------------------------------------------------------- FOR STUDENTS --

add(
    "nitrogen-balance-explained",
    "Nitrogen Balance Explained: Why It Matters for Muscle",
    "What nitrogen balance measures, how it relates to protein intake, and why it's used to assess whether the body is gaining or losing muscle.",
    "protein", "For Students", "Nitrogen balance explained",
    "Protein is roughly 16% nitrogen by weight, which makes nitrogen a convenient marker for tracking whether your body is building or breaking down protein tissue overall.",
    sec('''      <h2>What it measures</h2>
      <p>Nitrogen balance compares nitrogen intake (from dietary protein) to nitrogen losses (mainly through urine, with smaller amounts through skin and feces). The result falls into one of three states:</p>
      <ul class="checklist">
        <li><strong>Positive balance</strong> — intake exceeds losses; the body is building more protein tissue than it's breaking down (growth, pregnancy, muscle building, recovery from illness)</li>
        <li><strong>Negative balance</strong> — losses exceed intake; the body is breaking down more protein than it's replacing (inadequate protein intake, illness, severe calorie restriction)</li>
        <li><strong>Equilibrium</strong> — intake matches losses; typical for a healthy, weight-stable adult eating adequate protein</li>
      </ul>''') +
    sec('''      <p>For athletes and people building muscle, staying in positive or neutral nitrogen balance by eating enough protein is a practical way to support muscle protein synthesis and avoid unwanted muscle breakdown, especially during a calorie deficit.<sup class="ref"><a href="sources.html#p2">[1]</a></sup> Research labs measure nitrogen balance directly, but for practical purposes, hitting your daily protein target is the everyday equivalent.</p>''', bg="var(--color-protein-bg)", tight=True),
    [("protein.html", "What protein actually does"), ("how-much-protein-per-day.html", "How much protein per day"), ("catabolism-vs-anabolism.html", "Catabolism vs. anabolism")]
)

add(
    "catabolism-vs-anabolism",
    "Catabolism vs. Anabolism: The Basics of Metabolism",
    "The difference between catabolic and anabolic processes, and how they relate to muscle building, fat loss, and everyday metabolism.",
    "general", "For Students", "Catabolism vs. anabolism: the basics of metabolism",
    "Your metabolism runs on two opposing processes happening simultaneously, all day, every day.",
    sec('''      <div class="two-col">
        <div class="panel">
          <h3>Catabolism</h3>
          <p>Breaking larger molecules into smaller ones, releasing energy in the process. Digesting food, breaking down glycogen into glucose, and breaking down muscle protein into amino acids for fuel are all catabolic.</p>
        </div>
        <div class="panel">
          <h3>Anabolism</h3>
          <p>Building larger molecules from smaller ones, using energy in the process. Building muscle protein from amino acids and storing glucose as glycogen are both anabolic.</p>
        </div>
      </div>''') +
    sec('''      <p>Both are happening constantly — the practical question for body composition is which one dominates over time. A calorie surplus with resistance training and adequate protein tends to favor net anabolism (muscle building); a calorie deficit tends to favor net catabolism (fat and, without enough protein and training stimulus, muscle breakdown). "Anabolic" and "catabolic" aren't good or bad on their own — they're just the two directions metabolism can run.</p>'''),
    [("body-recomposition-explained.html", "Body recomposition explained"), ("nitrogen-balance-explained.html", "Nitrogen balance explained"), ("what-is-glycogen.html", "What is glycogen?")]
)

add(
    "how-to-calculate-macros-by-hand",
    "How to Calculate Your Macros by Hand (Step-by-Step)",
    "A step-by-step walkthrough of the exact math behind a macro calculator — useful for nutrition students who need to show their work.",
    "general", "For Students", "How to calculate your macros by hand",
    "Same math our calculator runs automatically — worked out step by step, in case you need to show your work.",
    sec('''      <h2>Step 1: Estimate BMR (Mifflin-St Jeor)</h2>
      <div class="panel">
        <p><strong>Men:</strong> BMR = 10 × weight(kg) + 6.25 × height(cm) − 5 × age + 5<br>
        <strong>Women:</strong> BMR = 10 × weight(kg) + 6.25 × height(cm) − 5 × age − 161</p>
      </div>
      <h2>Step 2: Multiply by activity to get TDEE</h2>
      <p>Multiply BMR by a Physical Activity Level factor: 1.2 (sedentary) up to 1.9 (very active).<sup class="ref"><a href="sources.html#cal2">[1]</a></sup></p>
      <h2>Step 3: Adjust for goal</h2>
      <p>Multiply TDEE by ~0.8 for a fat-loss deficit, 1.0 to maintain, or ~1.1-1.15 for a muscle-building surplus.</p>''') +
    sec('''      <h2>Step 4: Set protein (grams), then convert to calories</h2>
      <p>Multiply body weight (kg) by a target g/kg (commonly 1.6-2.2 for active individuals), then multiply grams by 4 to get protein calories.</p>
      <h2>Step 5: Set fat (% of total calories), then convert to grams</h2>
      <p>Multiply total calories by a fat percentage (20-35%) to get fat calories, then divide by 9 to get grams.</p>
      <h2>Step 6: Remainder goes to carbs</h2>
      <p>Subtract protein and fat calories from total calories, then divide the remainder by 4 to get carb grams.</p>
      <p><a href="calculators.html" class="btn btn-primary">Skip the math — use the calculator →</a></p>''', bg="var(--color-carbs-bg)", tight=True),
    [("tdee-vs-bmr.html", "BMR vs. TDEE"), ("calculators.html", "Full macro calculator"), ("how-much-protein-per-day.html", "How much protein per day")]
)

add(
    "rda-vs-dri-vs-amdr",
    "RDA vs. DRI vs. AMDR: What's the Difference?",
    "A plain-language breakdown of the nutrition reference terms students mix up most often: RDA, DRI, and AMDR.",
    "general", "For Students", "RDA vs. DRI vs. AMDR: what's the difference?",
    "These three acronyms show up constantly in nutrition coursework and are easy to confuse — here's how they actually relate to each other.",
    sec('''      <table class="data-table">
        <tr><th>Term</th><th>What it is</th></tr>
        <tr><td>DRI (Dietary Reference Intakes)</td><td>The umbrella term for the whole set of nutrient reference values published by the U.S. National Academies — RDA and AMDR are both types of DRI.</td></tr>
        <tr><td>RDA (Recommended Dietary Allowance)</td><td>A specific daily intake target (usually for vitamins, minerals, and protein) sufficient to meet the needs of nearly all healthy people in a group.</td></tr>
        <tr><td>AMDR (Acceptable Macronutrient Distribution Range)</td><td>A percentage-of-calories range (not a single number) for protein, fat, and carbohydrate associated with reduced chronic disease risk while meeting nutrient needs.</td></tr>
      </table>
      <p>In short: DRI is the category, RDA is a single-number target used mainly for micronutrients and protein, and AMDR is a range used specifically for the three macronutrients.<sup class="ref"><a href="sources.html#p3">[1]</a></sup></p>'''),
    [("how-much-protein-per-day.html", "How much protein per day"), ("how-many-carbs-per-day.html", "How many carbs per day"), ("glossary.html", "Full glossary")]
)

add(
    "nutrient-density-explained",
    "Nutrient Density Explained: Getting More From Your Calories",
    "What nutrient density means, why it matters even when your macros are on target, and how to eat more nutrient-dense meals.",
    "general", "For Students", "Nutrient density explained",
    "Two foods with identical calories and macros can deliver very different amounts of actual nutrition.",
    sec('''      <p><strong>Nutrient density</strong> describes how much nutritional value (vitamins, minerals, fiber, protein quality) a food provides relative to its calorie content. A food can be "energy dense" (lots of calories) without being nutrient dense, or vice versa — steamed broccoli and a candy bar can have wildly different nutrient density despite both containing carbohydrate calories.</p>''') +
    sec('''      <div class="panel">
        <h3>Why it matters even if your macros are perfect</h3>
        <p>Hitting a protein/fat/carb target doesn't guarantee adequate vitamin, mineral, or fiber intake — that's the core limitation of pure macro tracking discussed in our <a href="iifym-flexible-dieting.html">IIFYM article</a>. Prioritizing nutrient-dense foods (vegetables, fruit, lean proteins, whole grains, legumes) within your calorie and macro targets is how you get both numbers right and genuinely well-nourished.</p>
      </div>''', bg="var(--color-carbs-bg)", tight=True),
    [("micronutrients-vs-macronutrients.html", "Micronutrients vs. macronutrients"), ("iifym-flexible-dieting.html", "IIFYM explained"), ("fiber-benefits.html", "Why fiber matters")]
)

add(
    "muscle-fiber-types-and-nutrition",
    "Muscle Fiber Types and Nutrition: Fast-Twitch vs. Slow-Twitch",
    "How fast-twitch and slow-twitch muscle fibers differ in fuel use, and what that means for carbohydrate and protein needs by sport.",
    "carbs", "For Students", "Muscle fiber types and nutrition",
    "Not all muscle fibers burn fuel the same way — and that has real implications for how different athletes should eat.",
    sec('''      <div class="two-col">
        <div class="panel">
          <h3>Slow-twitch (Type I)</h3>
          <p>Fatigue-resistant fibers that rely heavily on oxygen and fat oxidation for fuel, well-suited to prolonged, lower-intensity effort like distance running.</p>
        </div>
        <div class="panel">
          <h3>Fast-twitch (Type II)</h3>
          <p>Fibers built for short, powerful efforts that rely heavily on stored glycogen and produce force quickly, but fatigue faster — used in sprinting and heavy lifting.</p>
        </div>
      </div>''', bg="var(--color-carbs-bg)", tight=True) +
    sec('''      <p>This split helps explain why endurance athletes (more reliant on sustained aerobic, fat- and glycogen-fueled effort) often need very high carbohydrate intakes to keep glycogen topped up,<sup class="ref"><a href="sources.html#c2">[1]</a></sup> while strength and power athletes (more reliant on fast-twitch, glycogen-dependent bursts) tend to prioritize protein for muscle repair alongside adequate — but not necessarily extreme — carbohydrate intake. See our full breakdown in <a href="macros-for-endurance-vs-strength-athletes.html">macros for endurance vs. strength athletes</a>.</p>'''),
    [("macros-for-endurance-vs-strength-athletes.html", "Macros for endurance vs. strength athletes"), ("what-is-glycogen.html", "What is glycogen?"), ("carb-loading-for-athletes.html", "Carb loading for athletes")]
)

add(
    "how-digestion-works",
    "How Digestion Works: From Bite to Absorption",
    "A step-by-step overview of how protein, fat, and carbohydrates are broken down and absorbed during digestion.",
    "general", "For Students", "How digestion works: from bite to absorption",
    "Every macronutrient takes a different path through digestion before it can actually be used by your body.",
    sec('''      <table class="data-table">
        <tr><th>Stage</th><th>What happens</th></tr>
        <tr><td>Mouth</td><td>Chewing and salivary enzymes begin breaking down starches</td></tr>
        <tr><td>Stomach</td><td>Acid and enzymes (like pepsin) begin breaking proteins into smaller peptides</td></tr>
        <tr><td>Small intestine</td><td>The main site of digestion and absorption: pancreatic enzymes finish breaking down protein into amino acids, fat into fatty acids (with help from bile), and carbs into simple sugars — all absorbed into the bloodstream here</td></tr>
        <tr><td>Large intestine</td><td>Water is absorbed, and fiber that wasn't digested is fermented by gut bacteria</td></tr>
      </table>''') +
    sec('''      <p>The speed of this process varies by macronutrient and food: simple sugars are absorbed fastest, protein and fiber-rich complex carbs take longer, and fat slows digestion of everything eaten alongside it — one reason meals with a mix of macronutrients tend to produce a more gradual, sustained energy release than any single macronutrient eaten alone.</p>'''),
    [("simple-vs-complex-carbs.html", "Simple vs. complex carbs"), ("fiber-benefits.html", "Why fiber matters"), ("glycemic-index-explained.html", "What is the glycemic index?")]
)

add(
    "protein-quality-scores-pdcaas-diaas",
    "Protein Quality Scores: PDCAAS and DIAAS Explained",
    "What PDCAAS and DIAAS scores measure, how they're calculated, and why they matter for comparing protein sources.",
    "protein", "For Students", "Protein quality scores: PDCAAS and DIAAS explained",
    "Not all protein sources are scored equally — these two methods are how nutrition science formally measures protein quality.",
    sec('''      <p><strong>PDCAAS</strong> (Protein Digestibility-Corrected Amino Acid Score) and its successor <strong>DIAAS</strong> (Digestible Indispensable Amino Acid Score) are methods for scoring how well a protein source meets essential amino acid needs, adjusted for how digestible it actually is. Both compare a food's essential amino acid profile against a reference pattern of human requirements.</p>''') +
    sec('''      <ul class="checklist">
        <li><strong>Whey, egg, and milk protein</strong> score at or near the maximum on both scales — highly digestible, complete amino acid profiles</li>
        <li><strong>Soy protein</strong> scores well, among the highest of common plant proteins</li>
        <li><strong>Most other plant proteins</strong> (wheat, rice, beans individually) score lower, usually due to being relatively low in one or more essential amino acids — which is why <a href="plant-based-protein-sources.html">combining varied plant protein sources</a> across the day matters more on a plant-based diet</li>
      </ul>
      <p>DIAAS is generally considered the more accurate, updated method, but PDCAAS still appears widely in food labeling and older research.</p>''', bg="var(--color-protein-bg)", tight=True),
    [("complete-vs-incomplete-protein.html", "Complete vs. incomplete protein"), ("plant-based-protein-sources.html", "Plant-based protein sources"), ("protein-powder-101.html", "Protein powder 101")]
)

add(
    "common-nutrition-myths-debunked",
    "Common Nutrition Myths Debunked",
    "A quick fact-check of persistent nutrition myths about carbs at night, eating frequency, detoxing, and more.",
    "general", "For Students", "Common nutrition myths, debunked",
    "A handful of nutrition claims keep resurfacing despite not holding up — here's what the evidence actually says.",
    sec('''      <ul class="checklist">
        <li><strong>"Carbs after 6pm turn to fat"</strong> — total daily intake matters far more than the clock; there's no special metabolic penalty for carbohydrates eaten in the evening for most people</li>
        <li><strong>"Eating more meals speeds up your metabolism"</strong> — meal frequency has minimal independent effect on metabolic rate; see our <a href="meal-frequency-and-metabolism.html">full breakdown</a></li>
        <li><strong>"You need to detox your body with juice cleanses"</strong> — the liver and kidneys already handle this continuously in a healthy person; no food or supplement "detoxes" you faster</li>
        <li><strong>"Fat makes you fat"</strong> — dietary fat and body fat are not the same thing; excess calories from any macronutrient, not fat specifically, drive fat gain</li>
        <li><strong>"Natural sugar and added sugar are metabolically different"</strong> — glucose and fructose are processed the same way regardless of source, though whole foods bring fiber and nutrients that pure added sugar doesn't</li>
        <li><strong>"You must eat protein immediately post-workout or lose gains"</strong> — the real window is much wider than assumed; see <a href="protein-timing.html">does protein timing matter?</a></li>
      </ul>''', bg="var(--color-fat-bg)", tight=True),
    [("meal-frequency-and-metabolism.html", "Does meal frequency matter?"), ("protein-timing.html", "Does protein timing matter?"), ("sugar-vs-starch.html", "Sugar vs. starch")]
)

add(
    "how-to-read-a-nutrition-study",
    "How to Read a Nutrition Study: A Student's Guide",
    "A practical guide for nutrition students on evaluating study design, sample size, and funding when reading nutrition research.",
    "general", "For Students", "How to read a nutrition study",
    "Nutrition headlines rarely tell you what the underlying study actually measured — here's what to check before trusting a claim.",
    sec('''      <ul class="checklist">
        <li><strong>Study design</strong> — a randomized controlled trial is stronger evidence than an observational study, which is stronger than a case report; headlines rarely specify which one you're reading about</li>
        <li><strong>Sample size and duration</strong> — a 12-person, 2-week study can't tell you much about long-term outcomes in the general population</li>
        <li><strong>Human vs. animal/cell studies</strong> — a striking result in mice doesn't automatically translate to humans</li>
        <li><strong>Association vs. causation</strong> — observational studies can show two things are correlated without proving one causes the other</li>
        <li><strong>Funding and conflicts of interest</strong> — industry-funded research isn't automatically wrong, but it's worth checking who paid for it</li>
        <li><strong>Has it been replicated?</strong> — a single study is a data point, not a verdict; look for whether other research supports the same conclusion</li>
      </ul>''', bg="var(--color-carbs-bg)", tight=True) +
    sec('''      <p>This is exactly why every claim on this site links back to its original source on the <a href="sources.html">Sources page</a> — so you can evaluate the underlying research yourself rather than taking a summary on faith.</p>'''),
    [("sources.html", "Sources & citations"), ("common-nutrition-myths-debunked.html", "Common nutrition myths debunked")]
)

add(
    "units-and-conversions-cheat-sheet",
    "Units and Conversions Cheat Sheet for Nutrition Students",
    "A quick-reference conversion sheet for calories, kilojoules, grams, ounces, and macronutrient calorie values.",
    "general", "For Students", "Units and conversions cheat sheet",
    "The conversions that come up constantly in nutrition coursework and macro tracking, in one place.",
    sec('''      <table class="data-table">
        <tr><th>Conversion</th><th>Value</th></tr>
        <tr><td>1 gram protein</td><td>4 calories</td></tr>
        <tr><td>1 gram carbohydrate</td><td>4 calories</td></tr>
        <tr><td>1 gram fat</td><td>9 calories</td></tr>
        <tr><td>1 gram alcohol</td><td>~7 calories</td></tr>
        <tr><td>1 kilocalorie (kcal / Calorie)</td><td>4.184 kilojoules (kJ)</td></tr>
        <tr><td>1 kilogram</td><td>2.2046 pounds</td></tr>
        <tr><td>1 pound</td><td>16 ounces / 0.4536 kg</td></tr>
        <tr><td>1 ounce</td><td>~28.35 grams</td></tr>
        <tr><td>1 inch</td><td>2.54 centimeters</td></tr>
      </table>
      <p>Bookmark this page — it comes in handy for homework, lab calculations, and double-checking food labels against research reported in different units.</p>'''),
    [("how-to-calculate-macros-by-hand.html", "How to calculate macros by hand"), ("calculators.html", "Macro calculator"), ("glossary.html", "Full glossary")]
)

add(
    "thermic-effect-of-food-explained",
    "The Thermic Effect of Food Explained",
    "What the thermic effect of food (TEF) is, why protein has the highest TEF of the three macronutrients, and how much it actually affects calorie burn.",
    "protein", "For Students", "The thermic effect of food explained",
    "Digesting food isn't free — it costs your body calories, and that cost depends on what you're eating.",
    sec('''      <p>The <strong>Thermic Effect of Food (TEF)</strong>, also called diet-induced thermogenesis, is the energy your body spends digesting, absorbing, and metabolizing what you eat. It's a real (if modest) component of total daily energy expenditure, and it varies significantly by macronutrient:</p>
      <table class="data-table">
        <tr><th>Macronutrient</th><th>Approximate TEF</th></tr>
        <tr><td>Protein</td><td>20-30% of its calories</td></tr>
        <tr><td>Carbohydrate</td><td>5-10% of its calories</td></tr>
        <tr><td>Fat</td><td>0-3% of its calories</td></tr>
      </table>''') +
    sec('''      <p>In practice, this means a higher-protein diet burns modestly more calories through digestion alone than an equal-calorie lower-protein diet — one small piece of why higher protein intakes are often recommended during a fat-loss phase, alongside protein's larger effects on satiety and muscle preservation.<sup class="ref"><a href="sources.html#cal2">[1]</a></sup> TEF is a real effect, but it's a modest slice of total daily expenditure — not a substitute for an appropriate overall calorie target.</p>''', bg="var(--color-protein-bg)", tight=True),
    [("tdee-vs-bmr.html", "BMR vs. TDEE"), ("macros-for-weight-loss.html", "Macros for fat loss"), ("how-much-protein-per-day.html", "How much protein per day")]
)


def main():
    for a in ARTICLES:
        html = page(a["slug"], a["title"], a["meta"], a["category"],
                    a["eyebrow"], a["h1"], a["intro"], a["body"], a["related"])
        path = os.path.join(ROOT, f'{a["slug"]}.html')
        with open(path, "w") as f:
            f.write(html)
        print("wrote", path)
    print(f"\n{len(ARTICLES)} articles generated.")
    build_hub()
    build_sitemap()
    return ARTICLES


if __name__ == "__main__":
    main()
