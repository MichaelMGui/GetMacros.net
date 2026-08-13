#!/usr/bin/env python3
"""Generates the SEO article pages for GetMacros.net.

Run from anywhere: python3 tools/generate_articles.py
Regenerates every file listed in ARTICLES into the site root, using the
same header/nav/footer markup and css/js as the hand-written pages.
To add another article, add an entry to ARTICLES and re-run.
"""
import json
import os
from html import escape as esc_html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(ROOT, "icon-sprite.svg")) as _f:
    ICON_SPRITE = _f.read().strip()


SITE = "https://getmacros.net"
AUTHOR_NAME = "The GetMacros.net editorial team"
# Every page on the site was written and published during this build window.
# dateModified tracks the most recent sitewide content pass.
DATE_PUBLISHED = "2026-08-10"
DATE_MODIFIED = "2026-08-13"
# Bumped whenever css/js changes, so browsers fetch the new file instead of
# pairing fresh HTML with a stale cached stylesheet.
ASSET_VERSION = "20260814c"

# Social share cards, one per content category (1200x630).
OG_IMAGE = {
    "protein": "og-protein.png",
    "fat": "og-fat.png",
    "carbs": "og-carbs.png",
    "diets": "og-diets.png",
    "athletes": "og-athletes.png",
    "science": "og-science.png",
    "general": "og-default.png",
}


def og_image_url(category="general"):
    return f"{SITE}/images/{OG_IMAGE.get(category, 'og-default.png')}"


def seo_meta(title, description, url, og_type="article", category="general"):
    t = esc_html(f"{title} | GetMacros.net")
    d = esc_html(description)
    img = og_image_url(category)
    return f'''<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="GetMacros.net">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="en_US">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="GetMacros.net — nutrition explained with cited research">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{img}">'''


def article_jsonld(title, description, url, kind="Article", category="general"):
    data = {
        "@context": "https://schema.org",
        "@type": kind,
        "headline": title,
        "description": description,
        "url": url,
        "image": og_image_url(category),
        "datePublished": DATE_PUBLISHED,
        "dateModified": DATE_MODIFIED,
        "inLanguage": "en",
        "author": {"@type": "Organization", "name": AUTHOR_NAME, "url": f"{SITE}/about.html"},
        "publisher": {
            "@type": "Organization",
            "name": "GetMacros.net",
            "url": f"{SITE}/",
            "logo": {"@type": "ImageObject", "url": f"{SITE}/images/og-default.png"},
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
    }
    return '<script type="application/ld+json">' + json.dumps(data).replace("</", "<\\/") + "</script>"


def breadcrumb_jsonld(title, url, hub_name="Articles", hub_url="https://getmacros.net/articles.html"):
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://getmacros.net/"},
            {"@type": "ListItem", "position": 2, "name": hub_name, "item": hub_url},
            {"@type": "ListItem", "position": 3, "name": title, "item": url},
        ],
    }
    return '<script type="application/ld+json">' + json.dumps(data).replace("</", "<\\/") + "</script>"


def webpage_jsonld(title, description, url):
    data = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "url": url,
        "inLanguage": "en",
        "description": description,
        "isPartOf": {"@type": "WebSite", "name": "GetMacros.net", "url": f"{SITE}/"},
    }
    return '<script type="application/ld+json">' + json.dumps(data).replace("</", "<\\/") + "</script>"


def hub_jsonld():
    """CollectionPage + ItemList for the articles hub, so search engines see the
    full index of articles rather than guessing at the page's purpose."""
    data = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "All Nutrition Articles",
        "url": f"{SITE}/articles.html",
        "inLanguage": "en",
        "isPartOf": {"@type": "WebSite", "name": "GetMacros.net", "url": f"{SITE}/"},
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(ARTICLES),
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": a["h1"],
                 "url": f'{SITE}/{a["slug"]}.html'}
                for i, a in enumerate(ARTICLES)
            ],
        },
    }
    return '<script type="application/ld+json">' + json.dumps(data).replace("</", "<\\/") + "</script>"


def faq_jsonld(qa_pairs):
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in qa_pairs
        ],
    }
    return '<script type="application/ld+json">' + json.dumps(data).replace("</", "<\\/") + "</script>"


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
      <li><a href="diets-explained.html"{cur("diets")}>Diets</a></li>
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
    <div>
      <h4>Company</h4>
      <ul>
        <li><a href="about.html">About</a></li>
        <li><a href="contact.html">Contact</a></li>
        <li><a href="privacy.html">Privacy policy</a></li>
        <li><a href="terms.html">Terms of use</a></li>
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
    "athletes": "background: linear-gradient(rgba(10,60,68,.78),rgba(15,90,100,.82))",
    "diets": "background: linear-gradient(rgba(60,35,90,.8),rgba(80,50,110,.82))",
    "science": "background: linear-gradient(rgba(18,40,86,.82),rgba(30,62,124,.84))",
    "general": "background:var(--color-primary-dark); color:#fff;",
}


def page(slug, title, meta, category, eyebrow, h1, intro, body, related, extra_head=""):
    hero_class = "hero page-hero" if category != "general" else "page-hero"
    related_links = " &middot; ".join(
        f'<a href="{href}">{label}</a>' for href, label in related
    )
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<script>if(self!==top){{try{{top.location=self.location;}}catch(e){{document.documentElement.style.display="none";}}}}</script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://pagead2.googlesyndication.com https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.googletagservices.com; style-src 'self' 'unsafe-inline' https://*.googlesyndication.com; img-src 'self' data: https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.gstatic.com; font-src 'self'; connect-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; frame-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; frame-ancestors 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#1b6b4a">
<link rel="preconnect" href="https://pagead2.googlesyndication.com">
<link rel="preconnect" href="https://www.highperformanceformat.com">
<title>{title} | GetMacros.net</title>
<meta name="description" content="{meta}">
<meta name="author" content="{AUTHOR_NAME}">
<link rel="canonical" href="https://getmacros.net/{slug}.html">
{seo_meta(title, meta, f"https://getmacros.net/{slug}.html", category=category)}
{article_jsonld(title, meta, f"https://getmacros.net/{slug}.html", category=category)}
{breadcrumb_jsonld(title, f"https://getmacros.net/{slug}.html")}
{extra_head}
<link rel="stylesheet" href="css/style.css?v={ASSET_VERSION}">
<script src="js/img-fallback.js?v={ASSET_VERSION}"></script>
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

  <nav class="breadcrumb" aria-label="Breadcrumb">
    <div class="container">
      <a href="index.html">Home</a> <span aria-hidden="true">›</span>
      <a href="articles.html">Articles</a> <span aria-hidden="true">›</span>
      <span aria-current="page">{h1}</span>
    </div>
  </nav>

{body}

  <section class="tight">
    <div class="container">
      <p class="section-intro"><strong>Keep reading:</strong> {related_links}</p>
    </div>
  </section>
</main>

{AD_SLOT}
{FOOTER}

<script src="js/main.js?v={ASSET_VERSION}"></script>
<script src="js/reveal.js?v={ASSET_VERSION}"></script>
<script src="js/ads-config.js?v={ASSET_VERSION}"></script>
<script src="js/ads.js?v={ASSET_VERSION}"></script>
</body>
</html>
'''


def sec(inner, bg=None, tight=False):
    cls = "tight" if tight else ""
    style = f' style="background:{bg}"' if bg else ""
    cls_attr = f' class="{cls}"' if cls else ""
    return f'  <section{cls_attr}{style}>\n    <div class="container">\n{inner}\n    </div>\n  </section>\n'


ARTICLES = []


def faq_section(qa_pairs):
    """Renders the FAQ visibly. Google only honours FAQPage markup when the same
    questions and answers appear on the page, so the two always ship together."""
    items = "\n".join(
        '        <details class="faq-item">\n'
        '          <summary>' + q + '</summary>\n'
        '          <p>' + a + '</p>\n'
        '        </details>'
        for q, a in qa_pairs
    )
    return ('      <h2>Frequently asked questions</h2>\n'
            '      <div class="faq-list">\n' + items + '\n      </div>')


def add(slug, title, meta, category, eyebrow, h1, intro, body, related, extra_head="", faq=None):
    if faq:
        body = body + sec(faq_section(faq), tight=True)
        extra_head = extra_head + faq_jsonld(faq)
    ARTICLES.append(dict(slug=slug, title=title, meta=meta, category=category,
                          eyebrow=eyebrow, h1=h1, intro=intro, body=body, related=related, extra_head=extra_head))


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
    "Protein for Muscle Growth: How Much and When",
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
    "10 Signs You're Not Eating Enough Protein",
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
    "25 High-Protein Foods (With Protein Per 100g)",
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
    "Complete vs. Incomplete Protein",
    "What complete and incomplete proteins are, which foods fall where, and why protein combining at every meal matters far less than people think.",
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
    "Best Plant-Based Protein Sources",
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
    "Does Protein Timing Actually Matter?",
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
    "How Much Fat Should You Eat Per Day?",
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
    "Saturated vs. Unsaturated Fat: The Difference",
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
    "Omega-3 vs Omega-6: Why the Balance Matters",
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
    "What Is Glycogen? How Your Body Stores Carbs",
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
    "Carb Loading for Athletes: How It Works",
    "How carb loading works, the modern protocol most athletes actually use, and who benefits from it.",
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
    "Why Fiber Matters: High-Fiber Diet Benefits",
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
    "Micronutrients vs. Macronutrients",
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
    "Vegan Macros: How to Hit Your Targets",
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
    "Intermittent Fasting and Your Macros",
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
    "Cutting vs. Bulking vs. Maintenance",
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
    "Protein Powder 101: Whey, Casein &amp; Plant",
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
    "Keto Diet Explained: Macros, Benefits &amp; Risks",
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
    "High-Protein Breakfast Ideas That Fill You Up",
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
    "Does Meal Frequency Affect Metabolism?",
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
    "Body Recomposition: Build Muscle, Lose Fat",
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
    "Alcohol and Macros: How Drinking Fits In",
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
    "Cholesterol: Dietary vs. Blood Explained",
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
    "Macros: Endurance vs. Strength Athletes",
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
    "BMR vs. TDEE: What's the Difference?",
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
    "How to Set Your Macros for Muscle Gain",
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
    "IIFYM: What Is Flexible Dieting?",
    "What 'If It Fits Your Macros' (IIFYM) means, its real pros and cons, and a practical middle-ground approach.",
    "general", "Calculator Guide", "IIFYM: what is flexible dieting, and does it work?",
    "\"If It Fits Your Macros\" (IIFYM) is the idea that as long as you hit your protein, fat, and carb targets, the specific foods you eat them from don't matter.",
    sec('''      <h2>The case for it</h2>
      <p>IIFYM's biggest strength is adherence: no foods are strictly off-limits, which makes it easier for many people to sustain over the long term compared to highly restrictive diets. If your macro targets are set appropriately for your goal, hitting them consistently — regardless of exact food choices — drives most of the physical outcome (fat loss, muscle gain, maintenance).</p>''') +
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
    "athletes": "Athletes &amp; Sports Nutrition",
    "diets": "Diets",
    "science": "Nutrition Science &amp; Physiology",
    "general": "Calculators &amp; Planning",
}
CATEGORY_PILL = {"protein": "protein", "fat": "fat", "carbs": "carbs", "athletes": "athletes", "diets": "diets", "science": "science", "general": "carbs"}


def build_hub():
    by_cat = {}
    for a in ARTICLES:
        by_cat.setdefault(a["category"], []).append(a)

    sections = ""
    order = ["protein", "fat", "carbs", "diets", "athletes", "science", "general"]
    bg = {"protein": "var(--color-protein-bg)", "fat": "var(--color-fat-bg)", "carbs": "var(--color-carbs-bg)", "athletes": "var(--color-pop2-bg)", "diets": "var(--color-pop3-bg)", "science": "var(--color-pop4-bg)", "general": None}
    for cat in order:
        items = by_cat.get(cat, [])
        if not items:
            continue
        badge_class = CATEGORY_PILL[cat] if cat != "general" else "neutral"
        badge_icon = {"protein": "icon-protein", "fat": "icon-fat", "carbs": "icon-carbs", "athletes": "icon-medal", "diets": "icon-leaf", "science": "icon-book", "general": "icon-article"}[cat]
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
<script>if(self!==top){{try{{top.location=self.location;}}catch(e){{document.documentElement.style.display="none";}}}}</script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://pagead2.googlesyndication.com https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.googletagservices.com; style-src 'self' 'unsafe-inline' https://*.googlesyndication.com; img-src 'self' data: https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.gstatic.com; font-src 'self'; connect-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; frame-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; frame-ancestors 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#1b6b4a">
<link rel="preconnect" href="https://pagead2.googlesyndication.com">
<link rel="preconnect" href="https://www.highperformanceformat.com">
<title>All Nutrition Articles | GetMacros.net</title>
<meta name="description" content="Every GetMacros.net article in one place — protein, fat, and carbohydrate guides, diet breakdowns, food lists, and calculator explainers.">
<meta name="author" content="{AUTHOR_NAME}">
<link rel="canonical" href="https://getmacros.net/articles.html">
{seo_meta("All Nutrition Articles", "Every GetMacros.net article in one place — protein, fat, and carbohydrate guides, diet breakdowns, food lists, and calculator explainers.", "https://getmacros.net/articles.html", og_type="website")}
{hub_jsonld()}
<link rel="stylesheet" href="css/style.css?v={ASSET_VERSION}">
<script src="js/img-fallback.js?v={ASSET_VERSION}"></script>
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

<script src="js/main.js?v={ASSET_VERSION}"></script>
<script src="js/reveal.js?v={ASSET_VERSION}"></script>
<script src="js/ads-config.js?v={ASSET_VERSION}"></script>
<script src="js/ads.js?v={ASSET_VERSION}"></script>
</body>
</html>
'''
    path = os.path.join(ROOT, "articles.html")
    with open(path, "w") as f:
        f.write(html)
    print("wrote", path)


def about_jsonld(url):
    data = {
        "@context": "https://schema.org",
        "@type": "AboutPage",
        "url": url,
        "inLanguage": "en",
        "mainEntity": {
            "@type": "Organization",
            "name": "GetMacros.net",
            "url": f"{SITE}/",
            "logo": {"@type": "ImageObject", "url": f"{SITE}/images/og-default.png"},
            "description": "A free nutrition education resource explaining protein, fat, and "
                           "carbohydrates with citations to primary research.",
        },
    }
    return '<script type="application/ld+json">' + json.dumps(data).replace("</", "<\\/") + "</script>"


def build_about():
    title = "About GetMacros.net"
    meta = "What GetMacros.net is, who it's built for, and the editorial and sourcing standards behind every article, calculator, and citation on the site."
    url = "https://getmacros.net/about.html"
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<script>if(self!==top){{try{{top.location=self.location;}}catch(e){{document.documentElement.style.display="none";}}}}</script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://pagead2.googlesyndication.com https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.googletagservices.com; style-src 'self' 'unsafe-inline' https://*.googlesyndication.com; img-src 'self' data: https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.gstatic.com; font-src 'self'; connect-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; frame-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; frame-ancestors 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#1b6b4a">
<link rel="preconnect" href="https://pagead2.googlesyndication.com">
<link rel="preconnect" href="https://www.highperformanceformat.com">
<title>{title}</title>
<meta name="description" content="{meta}">
<meta name="author" content="{AUTHOR_NAME}">
<link rel="canonical" href="{url}">
{seo_meta(title, meta, url, og_type="website")}
{about_jsonld(url)}
<link rel="stylesheet" href="css/style.css?v={ASSET_VERSION}">
<script src="js/img-fallback.js?v={ASSET_VERSION}"></script>
{ADSENSE_LOADER}
</head>
<body>
{ICON_SPRITE}
{NAV}

<main>
  <section class="page-hero" style="background:var(--color-primary-dark); color:#fff;">
    <div class="container">
      <p class="eyebrow"><svg class="icon" aria-hidden="true"><use href="#icon-graduation"/></svg> About</p>
      <h1>About GetMacros.net</h1>
      <p>A reference site built for nutrition students and anyone who wants the real biology behind protein, fat, and carbohydrates — not the diet-culture version.</p>
    </div>
  </section>

  <section>
    <div class="container">
      <h2>What this site is</h2>
      <p>GetMacros.net explains what protein, fat, and carbohydrates actually do in the body, how much of each you need, and what happens when you don't get enough — backed by calculators, a glossary, quizzes, and games for anyone studying or applying sports and nutrition science.</p>
    </div>
  </section>

  <section style="background:var(--color-carbs-bg)">
    <div class="container">
      <h2>How articles are sourced</h2>
      <p>Every factual claim on this site is cited to a peer-reviewed study, a government or academic health agency (Harvard T.H. Chan School of Public Health, the National Academies, NIH, Mayo Clinic, Cleveland Clinic), or — for athlete and team nutrition stories specifically — established news reporting. Every citation used across the site is listed with a direct link on the <a href="sources.html">Sources &amp; citations page</a>, so any claim can be checked against its original source.</p>
      <p>Calculators use published, research-validated formulas (the Mifflin-St Jeor equation for BMR, Dietary Reference Intake activity multipliers for TDEE) rather than proprietary or unverifiable estimates — also documented on the Sources page.</p>
    </div>
  </section>

  <section>
    <div class="container">
      <h2>What this site is not</h2>
      <p>This is educational content, not medical advice. Nothing here should replace guidance from a doctor or registered dietitian, especially if you have a medical condition or are making a major change to your diet.</p>
    </div>
  </section>

  <section style="background:var(--color-protein-bg)">
    <div class="container">
      <h2>Questions or corrections</h2>
      <p>If you find a claim that looks wrong or a citation that's out of date, the fastest way to verify it yourself is the <a href="sources.html">Sources page</a> — every reference links directly to its original source. To report it directly, see our <a href="contact.html">Contact page</a>.</p>
    </div>
  </section>
</main>

{AD_SLOT}
{FOOTER}

<script src="js/main.js?v={ASSET_VERSION}"></script>
<script src="js/reveal.js?v={ASSET_VERSION}"></script>
<script src="js/ads-config.js?v={ASSET_VERSION}"></script>
<script src="js/ads.js?v={ASSET_VERSION}"></script>
</body>
</html>
'''
    path = os.path.join(ROOT, "about.html")
    with open(path, "w") as f:
        f.write(html)
    print("wrote", path)


def build_privacy():
    title = "Privacy Policy"
    meta = "GetMacros.net's privacy policy — what data is and isn't collected, how localStorage is used for quizzes and games, and how third-party ad networks use cookies."
    url = "https://getmacros.net/privacy.html"
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<script>if(self!==top){{try{{top.location=self.location;}}catch(e){{document.documentElement.style.display="none";}}}}</script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://pagead2.googlesyndication.com https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.googletagservices.com; style-src 'self' 'unsafe-inline' https://*.googlesyndication.com; img-src 'self' data: https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.gstatic.com; font-src 'self'; connect-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; frame-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; frame-ancestors 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#1b6b4a">
<link rel="preconnect" href="https://pagead2.googlesyndication.com">
<link rel="preconnect" href="https://www.highperformanceformat.com">
<title>{title} | GetMacros.net</title>
<meta name="description" content="{meta}">
<meta name="author" content="{AUTHOR_NAME}">
<link rel="canonical" href="{url}">
{seo_meta(title, meta, url, og_type="website")}
{webpage_jsonld(title, meta, url)}
<link rel="stylesheet" href="css/style.css?v={ASSET_VERSION}">
<script src="js/img-fallback.js?v={ASSET_VERSION}"></script>
{ADSENSE_LOADER}
</head>
<body>
{ICON_SPRITE}
{NAV}

<main>
  <section class="page-hero" style="background:var(--color-primary-dark); color:#fff;">
    <div class="container">
      <p class="eyebrow"><svg class="icon" aria-hidden="true"><use href="#icon-shield"/></svg> Privacy</p>
      <h1>Privacy policy</h1>
      <p>Last updated August 2026. This page explains what data GetMacros.net does and doesn't collect.</p>
    </div>
  </section>

  <section>
    <div class="container">
      <h2>What we don't collect</h2>
      <p>GetMacros.net has no user accounts, no sign-up forms, and no server-side database. We don't collect names, emails, or any personal information you type in, because there's nowhere on the site that asks you to.</p>
    </div>
  </section>

  <section style="background:var(--color-carbs-bg)">
    <div class="container">
      <h2>What's stored in your browser</h2>
      <p>The calculators, quizzes, and games use your browser's <code>localStorage</code> to remember things like your quiz high scores and whether you've dismissed a corner ad — entirely on your device. This data is never sent to us; we have no way to see it, and clearing your browser data removes it completely.</p>
    </div>
  </section>

  <section>
    <div class="container">
      <h2>Hosting and basic logs</h2>
      <p>This site is hosted on GitHub Pages, behind Cloudflare. Like virtually any website, the hosting provider's servers log standard technical information (IP address, browser type, pages requested) for security and performance purposes — we don't have access to personally identify visitors from this.</p>
    </div>
  </section>

  <section style="background:var(--color-fat-bg)">
    <div class="container">
      <h2>Advertising</h2>
      <p>This site displays ads served by Google AdSense and Adsterra. These networks may use cookies and similar technologies to serve ads based on your visits to this and other sites. We don't control what these networks collect — see <a href="https://policies.google.com/technologies/ads" target="_blank" rel="noopener">Google's advertising policy</a> for how Google's ad products work, including how to opt out of personalized advertising via <a href="https://myadcenter.google.com" target="_blank" rel="noopener">Google Ad Settings</a>.</p>
    </div>
  </section>

  <section>
    <div class="container">
      <h2>Children's privacy</h2>
      <p>This site is not directed at children under 13 and we do not knowingly collect any information from them.</p>
    </div>
  </section>

  <section style="background:var(--color-protein-bg)">
    <div class="container">
      <h2>Changes to this policy</h2>
      <p>If this policy changes, the update will be reflected on this page with a new "last updated" date above.</p>
    </div>
  </section>
</main>

{AD_SLOT}
{FOOTER}

<script src="js/main.js?v={ASSET_VERSION}"></script>
<script src="js/reveal.js?v={ASSET_VERSION}"></script>
<script src="js/ads-config.js?v={ASSET_VERSION}"></script>
<script src="js/ads.js?v={ASSET_VERSION}"></script>
</body>
</html>
'''
    path = os.path.join(ROOT, "privacy.html")
    with open(path, "w") as f:
        f.write(html)
    print("wrote", path)


def contact_jsonld(url):
    data = {
        "@context": "https://schema.org",
        "@type": "ContactPage",
        "url": url,
        "inLanguage": "en",
        "mainEntity": {
            "@type": "Organization",
            "name": "GetMacros.net",
            "url": f"{SITE}/",
            "email": "getmacros.net@outlook.com",
        },
    }
    return '<script type="application/ld+json">' + json.dumps(data).replace("</", "<\\/") + "</script>"


def build_contact():
    title = "Contact GetMacros.net"
    meta = "How to reach GetMacros.net with corrections, content questions, or advertising inquiries."
    url = "https://getmacros.net/contact.html"
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<script>if(self!==top){{try{{top.location=self.location;}}catch(e){{document.documentElement.style.display="none";}}}}</script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://pagead2.googlesyndication.com https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.googletagservices.com; style-src 'self' 'unsafe-inline' https://*.googlesyndication.com; img-src 'self' data: https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.gstatic.com; font-src 'self'; connect-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; frame-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; frame-ancestors 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#1b6b4a">
<link rel="preconnect" href="https://pagead2.googlesyndication.com">
<link rel="preconnect" href="https://www.highperformanceformat.com">
<title>{title} | GetMacros.net</title>
<meta name="description" content="{meta}">
<meta name="author" content="{AUTHOR_NAME}">
<link rel="canonical" href="{url}">
{seo_meta(title, meta, url, og_type="website")}
{contact_jsonld(url)}
<link rel="stylesheet" href="css/style.css?v={ASSET_VERSION}">
<script src="js/img-fallback.js?v={ASSET_VERSION}"></script>
{ADSENSE_LOADER}
</head>
<body>
{ICON_SPRITE}
{NAV}

<main>
  <section class="page-hero" style="background:var(--color-primary-dark); color:#fff;">
    <div class="container">
      <p class="eyebrow"><svg class="icon" aria-hidden="true"><use href="#icon-mail"/></svg> Contact</p>
      <h1>Contact GetMacros.net</h1>
      <p>Spotted an error, have a source to suggest, or a business inquiry? Here's how to reach us.</p>
    </div>
  </section>

  <section>
    <div class="container">
      <h2>Email</h2>
      <p>The fastest way to reach us for anything — corrections, questions about a citation, content suggestions, or advertising and partnership inquiries.</p>
      <p><a class="btn btn-primary" href="mailto:getmacros.net@outlook.com">getmacros.net@outlook.com</a></p>
      <p class="hint">This is a small, independently run reference site — we read every message but can't guarantee a response time.</p>
    </div>
  </section>

  <section style="background:var(--color-carbs-bg)">
    <div class="container">
      <h2>Found an error?</h2>
      <p>If a number, claim, or citation looks wrong, email us the article URL and what looks off. We'd rather fix it than leave it — every factual claim on this site is meant to trace back to a real source on the <a href="sources.html">Sources page</a>, and we take it seriously when that breaks down.</p>
    </div>
  </section>

  <section>
    <div class="container">
      <h2>What we can't help with</h2>
      <p>This site is educational, not a medical or dietetics practice — we can't answer personal health questions or give individualized advice. For that, see a doctor or registered dietitian. See our <a href="about.html">About page</a> for more on what the site is and isn't.</p>
    </div>
  </section>
</main>

{AD_SLOT}
{FOOTER}

<script src="js/main.js?v={ASSET_VERSION}"></script>
<script src="js/reveal.js?v={ASSET_VERSION}"></script>
<script src="js/ads-config.js?v={ASSET_VERSION}"></script>
<script src="js/ads.js?v={ASSET_VERSION}"></script>
</body>
</html>
'''
    path = os.path.join(ROOT, "contact.html")
    with open(path, "w") as f:
        f.write(html)
    print("wrote", path)


def build_terms():
    title = "Terms of Use"
    meta = "The terms governing use of GetMacros.net — educational content only, not medical advice, third-party ads, and intellectual property."
    url = "https://getmacros.net/terms.html"
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<script>if(self!==top){{try{{top.location=self.location;}}catch(e){{document.documentElement.style.display="none";}}}}</script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://pagead2.googlesyndication.com https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.googletagservices.com; style-src 'self' 'unsafe-inline' https://*.googlesyndication.com; img-src 'self' data: https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.gstatic.com; font-src 'self'; connect-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; frame-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; frame-ancestors 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#1b6b4a">
<link rel="preconnect" href="https://pagead2.googlesyndication.com">
<link rel="preconnect" href="https://www.highperformanceformat.com">
<title>{title} | GetMacros.net</title>
<meta name="description" content="{meta}">
<meta name="author" content="{AUTHOR_NAME}">
<link rel="canonical" href="{url}">
{seo_meta(title, meta, url, og_type="website")}
{webpage_jsonld(title, meta, url)}
<link rel="stylesheet" href="css/style.css?v={ASSET_VERSION}">
<script src="js/img-fallback.js?v={ASSET_VERSION}"></script>
{ADSENSE_LOADER}
</head>
<body>
{ICON_SPRITE}
{NAV}

<main>
  <section class="page-hero" style="background:var(--color-primary-dark); color:#fff;">
    <div class="container">
      <p class="eyebrow"><svg class="icon" aria-hidden="true"><use href="#icon-document"/></svg> Terms</p>
      <h1>Terms of use</h1>
      <p>Last updated August 2026. Plain-language terms for using GetMacros.net.</p>
    </div>
  </section>

  <section>
    <div class="container">
      <h2>Acceptance of these terms</h2>
      <p>By using GetMacros.net, you agree to these terms. If you don't agree with them, the only enforceable request we can make is that you stop using the site.</p>
    </div>
  </section>

  <section style="background:var(--color-carbs-bg)">
    <div class="container">
      <h2>Educational content, not advice</h2>
      <p>Everything on this site — articles, calculators, quizzes, glossary — is for general education, not personalized medical, dietetic, or health advice. Calculator results are estimates based on published formulas, not a prescription. Talk to a doctor or registered dietitian before making significant changes to your diet, especially if you have a medical condition.</p>
    </div>
  </section>

  <section>
    <div class="container">
      <h2>Intellectual property</h2>
      <p>The text, design, and original graphics on this site are owned by GetMacros.net unless otherwise credited. You're welcome to link to any page. Please don't republish or scrape substantial portions of the content elsewhere without permission — email us at <a href="mailto:getmacros.net@outlook.com">getmacros.net@outlook.com</a> if you'd like to use something. Cited facts and figures themselves aren't ours to own — see the <a href="sources.html">Sources page</a> for the original research behind them.</p>
    </div>
  </section>

  <section style="background:var(--color-fat-bg)">
    <div class="container">
      <h2>Third-party links and advertising</h2>
      <p>This site displays ads from Google AdSense and Adsterra, and links out to external sources for citations. We don't control the content, availability, or practices of external sites and aren't responsible for them. See our <a href="privacy.html">Privacy policy</a> for how advertising cookies work.</p>
    </div>
  </section>

  <section>
    <div class="container">
      <h2>No warranty</h2>
      <p>This site is provided "as is." We work to keep facts accurate and citations current, but we don't guarantee the content is complete, error-free, or suitable for any particular purpose. Use of any information here is at your own discretion.</p>
    </div>
  </section>

  <section style="background:var(--color-protein-bg)">
    <div class="container">
      <h2>Changes to these terms</h2>
      <p>If these terms change, the update will be reflected on this page with a new "last updated" date above. Continued use of the site after a change means you accept the updated terms.</p>
    </div>
  </section>
</main>

{AD_SLOT}
{FOOTER}

<script src="js/main.js?v={ASSET_VERSION}"></script>
<script src="js/reveal.js?v={ASSET_VERSION}"></script>
<script src="js/ads-config.js?v={ASSET_VERSION}"></script>
<script src="js/ads.js?v={ASSET_VERSION}"></script>
</body>
</html>
'''
    path = os.path.join(ROOT, "terms.html")
    with open(path, "w") as f:
        f.write(html)
    print("wrote", path)


def build_404():
    title = "Page Not Found"
    meta = "The page you're looking for doesn't exist. Find protein, fat, and carbohydrate guides, calculators, quizzes, and the full glossary on GetMacros.net."
    url = "https://getmacros.net/404.html"
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<script>if(self!==top){{try{{top.location=self.location;}}catch(e){{document.documentElement.style.display="none";}}}}</script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://pagead2.googlesyndication.com https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.googletagservices.com; style-src 'self' 'unsafe-inline' https://*.googlesyndication.com; img-src 'self' data: https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.gstatic.com; font-src 'self'; connect-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; frame-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; frame-ancestors 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#1b6b4a">
<link rel="preconnect" href="https://pagead2.googlesyndication.com">
<link rel="preconnect" href="https://www.highperformanceformat.com">
<meta name="robots" content="noindex, follow">
<title>{title} | GetMacros.net</title>
<meta name="description" content="{meta}">
{seo_meta(title, meta, url, og_type="website")}
<link rel="stylesheet" href="css/style.css?v={ASSET_VERSION}">
<script src="js/img-fallback.js?v={ASSET_VERSION}"></script>
{ADSENSE_LOADER}
</head>
<body>
{ICON_SPRITE}
{NAV}

<main>
  <section class="page-hero" style="background:var(--color-primary-dark); color:#fff; text-align:center;">
    <div class="container">
      <p class="eyebrow"><svg class="icon" aria-hidden="true"><use href="#icon-search"/></svg> 404</p>
      <h1>We couldn't find that page</h1>
      <p>The link might be broken, or the page may have moved. Here's where you probably wanted to go:</p>
    </div>
  </section>

  <section>
    <div class="container">
      <div class="card-grid">
        <a href="index.html" class="card"><span class="icon-badge neutral"><svg class="icon" aria-hidden="true"><use href="#icon-molecule"/></svg></span><h3>Home</h3><p>The three macronutrients, explained properly.</p></a>
        <a href="calculators.html" class="card"><span class="icon-badge neutral"><svg class="icon" aria-hidden="true"><use href="#icon-calculator"/></svg></span><h3>Calculators</h3><p>Get your personal protein, fat, and carb targets.</p></a>
        <a href="articles.html" class="card"><span class="icon-badge neutral"><svg class="icon" aria-hidden="true"><use href="#icon-article"/></svg></span><h3>All articles</h3><p>Every guide on the site, organized by topic.</p></a>
        <a href="quiz.html" class="card"><span class="icon-badge neutral"><svg class="icon" aria-hidden="true"><use href="#icon-quiz"/></svg></span><h3>Quiz &amp; games</h3><p>Test what you know, or learn hands-on.</p></a>
        <a href="glossary.html" class="card"><span class="icon-badge neutral"><svg class="icon" aria-hidden="true"><use href="#icon-book"/></svg></span><h3>Glossary</h3><p>Every nutrition term, from A to Z.</p></a>
        <a href="sources.html" class="card"><span class="icon-badge neutral"><svg class="icon" aria-hidden="true"><use href="#icon-search"/></svg></span><h3>Sources</h3><p>Every citation used across the site.</p></a>
      </div>
    </div>
  </section>
</main>

{AD_SLOT}
{FOOTER}

<script src="js/main.js?v={ASSET_VERSION}"></script>
<script src="js/reveal.js?v={ASSET_VERSION}"></script>
<script src="js/ads-config.js?v={ASSET_VERSION}"></script>
<script src="js/ads.js?v={ASSET_VERSION}"></script>
</body>
</html>
'''
    path = os.path.join(ROOT, "404.html")
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
    ("about.html", "0.4"),
    ("contact.html", "0.3"),
    ("privacy.html", "0.2"),
    ("terms.html", "0.2"),
    ("es/", "0.6"),
    ("fr/", "0.6"),
]


SITEMAP_LASTMOD = "2026-08-12"


def build_sitemap():
    domain = "https://getmacros.net"
    urls = [f"{domain}/{p}" for p, _ in CORE_PAGES]
    priorities = {p: pr for p, pr in CORE_PAGES}
    entries = []
    for path, priority in CORE_PAGES:
        entries.append(f"  <url>\n    <loc>{domain}/{path}</loc>\n    <lastmod>{SITEMAP_LASTMOD}</lastmod>\n    <priority>{priority}</priority>\n  </url>")
    for a in ARTICLES:
        entries.append(f'  <url>\n    <loc>{domain}/{a["slug"]}.html</loc>\n    <lastmod>{SITEMAP_LASTMOD}</lastmod>\n    <priority>0.7</priority>\n  </url>')
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
    "Nitrogen Balance: Why It Matters for Muscle",
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
    "Catabolism vs. Anabolism: Metabolism Basics",
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
    "How to Calculate Your Macros by Hand",
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
    "Nutrient Density: More Nutrition Per Calorie",
    "What nutrient density means, why it matters even when your macros are on target, and how to eat more nutrient-dense meals.",
    "general", "For Students", "Nutrient density explained",
    "Two foods with identical calories and macros can deliver very different amounts of actual nutrition.",
    sec('''      <p><strong>Nutrient density</strong> describes how much nutritional value (vitamins, minerals, fiber, protein quality) a food provides relative to its calorie content. A food can be "energy dense" (lots of calories) without being nutrient dense, or vice versa — steamed broccoli and a candy bar can have wildly different nutrient density despite both containing carbohydrate calories.</p>''') +
    sec('''      <div class="panel">
        <h3>Why it matters even if your macros are perfect</h3>
        <p>Hitting a protein/fat/carb target doesn't guarantee adequate vitamin, mineral, or fiber intake — that's the core limitation of pure macro tracking discussed in our <a href="iifym-flexible-dieting.html">IIFYM article</a>. Prioritizing nutrient-dense foods (vegetables, fruit, lean proteins, whole grains, legumes) within your calorie and macro targets is how you get both numbers right and stay well-nourished.</p>
      </div>''', bg="var(--color-carbs-bg)", tight=True),
    [("micronutrients-vs-macronutrients.html", "Micronutrients vs. macronutrients"), ("iifym-flexible-dieting.html", "IIFYM explained"), ("fiber-benefits.html", "Why fiber matters")]
)

add(
    "muscle-fiber-types-and-nutrition",
    "Muscle Fiber Types: Fast- vs. Slow-Twitch",
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
    sec('''      <p>This split explains a lot about how the two groups eat. Endurance athletes rely on sustained aerobic effort fueled by fat and glycogen, so they often need very high carbohydrate intakes to keep glycogen topped up.<sup class="ref"><a href="sources.html#c2">[1]</a></sup> Strength and power athletes rely more on fast-twitch, glycogen-dependent bursts, so they tend to prioritize protein for muscle repair alongside adequate — but not extreme — carbohydrate. See our full breakdown in <a href="macros-for-endurance-vs-strength-athletes.html">macros for endurance vs. strength athletes</a>.</p>'''),
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
    sec('''      <p>How fast this happens depends on the food. Simple sugars are absorbed fastest, protein and fiber-rich complex carbs take longer, and fat slows the digestion of everything eaten alongside it. That's one reason a mixed meal gives a more gradual, sustained energy release than any single macronutrient eaten on its own.</p>'''),
    [("simple-vs-complex-carbs.html", "Simple vs. complex carbs"), ("fiber-benefits.html", "Why fiber matters"), ("glycemic-index-explained.html", "What is the glycemic index?")]
)

add(
    "protein-quality-scores-pdcaas-diaas",
    "Protein Quality: PDCAAS and DIAAS Explained",
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
    "How to Read a Nutrition Study",
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
    "Nutrition Units &amp; Conversions Cheat Sheet",
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


# ----------------------------------------------------------------- ATHLETES --

add(
    "world-cup-2026-team-nutrition",
    "What World Cup 2026 Teams Are Actually Eating",
    "How World Cup squads fuel for match day — carbohydrate loading, hydration, recovery protein, and what amateur players can realistically borrow.",
    "athletes", "Athletes &amp; Sports", "What World Cup 2026 teams are actually eating",
    "For elite national teams, food isn't an afterthought during a tournament — it's logistics, planned months ahead, with a chef and a shipping manifest.",
    sec('''      <h2>Norway's 1,000kg of imported food</h2>
      <p>Norway's men's national team transported more than 1,000 kilograms of food from Norway to their training base for the 2026 World Cup, including hundreds of kilos of Atlantic salmon and white fish, over 100kg of brunost (traditional Norwegian brown cheese), and roughly 6,000 oranges. Aaron Espeland, who has cooked for the national team for 35 years, traveled with a full culinary staff to prepare every meal.<sup class="ref"><a href="sources.html#ath1">[1]</a></sup></p>''') +
    sec('''      <h2>Argentina's 500kg of beef and the post-win asado</h2>
      <p>Argentina brought nearly 500kg of beef from home for the same tournament, prepared by longtime team chef Diego Iacovone. The squad's traditional asado (barbecue) is treated as part of team identity — reserved as a reward the coaching staff allows the players to step outside their strict routine and enjoy after important wins.<sup class="ref"><a href="sources.html#ath2">[2]</a></sup></p>''') +
    sec('''      <h2>Why do this at all?</h2>
      <p>It isn't about comfort food or homesickness. Both teams describe it as a performance decision: a World Cup is a high-stress, condensed schedule where a single case of food-related illness or gut discomfort can end a player's tournament. Sudden changes in diet can disrupt digestion, sleep, and concentration — all things that affect performance directly — so elite squads try to eliminate that variable entirely by controlling every ingredient down to where it was sourced.<sup class="ref"><a href="sources.html#ath2">[2]</a></sup> It's the same principle sports dietitians give any athlete: never try something new on game day.</p>''', bg="var(--color-pop2-bg)", tight=True),
    [("famous-athlete-diets-fact-checked.html", "6 famous athlete diets, fact-checked"), ("macros-for-endurance-vs-strength-athletes.html", "Macros for endurance vs. strength athletes"), ("calculators.html", "Macro calculator")]
)

add(
    "famous-athlete-diets-fact-checked",
    "6 Famous Athlete Diets, Fact-Checked",
    "What elite athletes actually eat, which viral diet claims hold up to scrutiny, and what the research says about copying their approach.",
    "athletes", "Athletes &amp; Sports", "6 famous athlete diets, fact-checked",
    "Elite athletes' diets get turned into internet legend fast. Here's what's actually documented, sourced back to the original reporting.",
    sec('''      <h2>Lionel Messi: cutting sugar and refined flour</h2>
      <p>Since 2014, Messi has worked with Italian sports physician Giuliano Poser, who had him cut refined sugar, limit refined flour and certain dairy, and build meals around water, extra-virgin olive oil, whole grains, fish, vegetables, fruit, nuts, and seeds. Messi reportedly lost about 3.5kg and had fewer digestion-related issues after the change.<sup class="ref"><a href="sources.html#ath3">[3]</a></sup></p>
      <h2>Cristiano Ronaldo: six small meals a day</h2>
      <p>Ronaldo eats roughly six small meals every 2-4 hours built around lean protein (chicken, sea bass, swordfish, tuna), fruit, vegetables, whole grains, and consistent hydration, while avoiding refined sugar, dairy, and processed food. The stated goal is steady energy and blood sugar rather than large infrequent meals.<sup class="ref"><a href="sources.html#ath4">[4]</a></sup></p>''') +
    sec('''      <h2>Michael Phelps: the 12,000-calorie diet that wasn't</h2>
      <p>The famous claim that Phelps ate 12,000 calories a day is false — it came from a reporter's back-of-envelope math on a casually described meal plan. Phelps has said in his own autobiography the real number was closer to 8,000-10,000 calories on his heaviest training days, still enormous, but roughly 25% less than the myth.<sup class="ref"><a href="sources.html#ath5">[5]</a></sup></p>
      <h2>Usain Bolt: 1,000 chicken nuggets in Beijing</h2>
      <p>This one is true. At the 2008 Beijing Olympics, Bolt ate almost nothing but McDonald's chicken nuggets — about 100 a day for 10 days — after a local meal upset his stomach and he decided not to risk anything unfamiliar before his races. He still broke three world records that Games. By the time he returned to Beijing in 2015, food options had improved and he didn't need to repeat it.<sup class="ref"><a href="sources.html#ath6">[6]</a></sup></p>''', bg="var(--color-fat-bg)", tight=True) +
    sec('''      <h2>Novak Djokovic: gluten-free and plant-based</h2>
      <p>Djokovic went gluten-free in 2010 after a Serbian nutritionist diagnosed a gluten sensitivity, and later moved to a fully plant-based diet built around vegetables, fruit, nuts, seeds, and legumes. He credits the change with his run of Grand Slam success, though the specific health claims (like curing his allergies) are self-reported and haven't been independently verified.<sup class="ref"><a href="sources.html#ath7">[7]</a></sup> See our <a href="do-elimination-diets-improve-performance.html">deep dive on elimination diets and performance</a> for what controlled research actually finds.</p>
      <h2>Simone Biles: no strict tracking</h2>
      <p>Biles deliberately avoids rigid meal tracking, calling it a risk factor for disordered eating given how much time she spends in the gym. She eats intuitively — oatmeal or eggs for breakfast, anything from pizza to salmon for lunch, fish with vegetables and rice for dinner, and a protein shake post-workout.<sup class="ref"><a href="sources.html#ath8">[8]</a></sup></p>''') +
    sec('''      <p>The pattern across all six: what works is highly individual, and a diet succeeding alongside an elite athlete doesn't prove the diet caused the success — genetics, training volume, and years of development matter enormously too. Use these as examples of different valid approaches, not templates to copy exactly.</p>
      <p><a href="calculators.html" class="btn btn-primary">Find your own numbers instead →</a></p>''', tight=True),
    [("world-cup-2026-team-nutrition.html", "What World Cup 2026 teams are actually eating"), ("do-elimination-diets-improve-performance.html", "Do elimination diets improve performance?"), ("protein-timing.html", "Does protein timing matter?")]
)

add(
    "do-elimination-diets-improve-performance",
    "Do Elimination Diets Improve Performance?",
    "What controlled research finds when non-celiac athletes go gluten-free or try other elimination diets for performance — and why some still swear by the results.",
    "athletes", "Athletes &amp; Sports", "Do elimination diets actually improve performance?",
    "High-profile athletes like Novak Djokovic have made gluten-free and elimination diets look like a performance secret. Controlled research tells a more boring story.",
    sec('''      <h2>What the research actually shows</h2>
      <p>In athletes without celiac disease or a diagnosed gluten sensitivity, controlled trials have found that a short-term gluten-free diet produces no measurable change in performance, gastrointestinal symptoms, or inflammatory markers compared to a normal mixed diet.<sup class="ref"><a href="sources.html#ath9">[9]</a></sup> That holds despite gluten-free eating being popular among endurance athletes specifically for perceived performance and gut-comfort benefits.</p>''') +
    sec('''      <h2>So why do some athletes swear by it?</h2>
      <p>There are simpler explanations that don't require gluten itself to be the culprit. Cutting gluten usually means cutting processed food, refined sugar, and low-fiber packaged carbs at the same time — the same changes behind most "clean eating" results. Placebo effects on perceived performance are also well documented. And non-celiac sensitivity is real in a minority of people, even without full celiac disease.</p>''', bg="var(--color-pop2-bg)", tight=True) +
    sec('''      <h2>The actual risk</h2>
      <p>Going gluten-free (or removing any other whole food group) without medical guidance can crowd out fiber, B vitamins, and iron that are otherwise easy to get from whole grains and fortified foods — see our <a href="fiber-benefits.html">fiber benefits guide</a> and <a href="micronutrients-vs-macronutrients.html">micronutrients vs. macronutrients</a> for what's actually at stake. If you suspect a real gluten or food sensitivity, that's worth testing for directly rather than guessing with a self-imposed elimination diet.</p>'''),
    [("famous-athlete-diets-fact-checked.html", "6 famous athlete diets, fact-checked"), ("fiber-benefits.html", "Fiber benefits"), ("common-nutrition-myths-debunked.html", "Common nutrition myths debunked")]
)

# --------------------------------------------------------- GENERAL / ADVANCED --

add(
    "creatine-explained",
    "Creatine: What It Does &amp; Who Needs It",
    "What creatine monohydrate actually does in the body, what the safety research says, and the simple, effective way to take it based on the ISSN position stand.",
    "general", "For Students", "Creatine explained: what it does and who needs it",
    "Creatine is one of the most researched supplements in sports nutrition, and also one of the most misunderstood.",
    sec('''      <h2>What creatine actually does</h2>
      <p>Creatine increases the amount of phosphocreatine stored in muscle, which your body uses to rapidly regenerate ATP — the direct energy source for short, high-intensity effort like sprinting or a heavy lift. More available phosphocreatine means slightly more capacity for that kind of effort, which over weeks of training translates into more total work done and more muscle and strength gained. The International Society of Sports Nutrition calls it the most effective legal ergogenic supplement currently available for increasing high-intensity exercise capacity and lean body mass.<sup class="ref"><a href="sources.html#ath11">[11]</a></sup></p>''') +
    sec('''      <h2>Is it safe?</h2>
      <p>Yes, for healthy people. Studies covering doses up to 30g/day for as long as 5 years report it as safe and well-tolerated, and it does not appear to harm kidney function in people with normal kidneys — the "creatine damages your kidneys" claim is a myth that keeps circulating despite the position-stand evidence. Some studies even found creatine use associated with less muscle cramping and fewer injuries during training, not more.<sup class="ref"><a href="sources.html#ath11">[11]</a></sup></p>''', bg="var(--color-fat-bg)", tight=True) +
    sec('''      <h2>How much to take</h2>
      <table class="data-table">
        <tr><th>Approach</th><th>Dose</th><th>Time to full saturation</th></tr>
        <tr><td>Maintenance only</td><td>3-5g/day</td><td>~3-4 weeks</td></tr>
        <tr><td>Loading phase (optional)</td><td>20g/day (split into 4 doses) for 5-7 days, then 3-5g/day</td><td>~1 week</td></tr>
      </table>
      <p>Timing relative to your workout doesn't meaningfully matter — see our piece on the <a href="post-workout-anabolic-window.html">post-workout anabolic window</a> for why timing windows in general are smaller than supplement marketing suggests. Consistency day to day is what actually saturates your muscle stores.</p>'''),
    [("post-workout-anabolic-window.html", "The post-workout anabolic window"), ("protein-timing.html", "Does protein timing matter?"), ("how-much-protein-per-day.html", "How much protein do you need per day?")]
)

add(
    "carb-cycling-explained",
    "Carb Cycling Explained",
    "What carb cycling actually is, how the high-day/low-day approach works, and what the (limited) research says about whether it beats a steady daily carb intake.",
    "carbs", "For Students", "Carb cycling explained",
    "Carb cycling has a devoted following in bodybuilding circles. The evidence for it is a lot thinner than the hype.",
    sec('''      <h2>What carb cycling is</h2>
      <p>Carb cycling means deliberately alternating your daily carbohydrate intake — typically higher carbs on hard training days, to fuel the session and refill muscle glycogen, and lower carbs on rest days, when your body needs less immediate fuel. The rest of your macros and total weekly calories usually stay roughly consistent; only the carb-to-fat ratio shifts day to day.<sup class="ref"><a href="sources.html#ath13">[13]</a></sup></p>''') +
    sec('''      <h2>What the evidence actually shows</h2>
      <p>Most of the research behind carb manipulation was done on endurance athletes managing glycogen for long events, not on bodybuilders or general lifters trying to lose fat and keep muscle. For that more common goal, the evidence for carb cycling specifically — beyond just hitting an appropriate weekly average — is thin, and there are very few controlled trials on it at all.<sup class="ref"><a href="sources.html#ath13">[13]</a></sup> Your body cares far more about your total calorie and macro intake over days and weeks than about which specific day each gram of carbohydrate landed on.</p>''', bg="var(--color-carbs-bg)", tight=True) +
    sec('''      <p>If you like the structure of eating more around your hardest training days, there's nothing wrong with it — just don't expect it to outperform a steady, well-calculated daily target. <a href="calculators.html#carb-calculator" class="btn btn-primary">Calculate your daily carb target →</a></p>'''),
    [("how-many-carbs-per-day.html", "How many carbs do you need per day?"), ("what-is-glycogen.html", "What is glycogen?"), ("iifym-flexible-dieting.html", "IIFYM / flexible dieting")]
)

add(
    "post-workout-anabolic-window",
    "Is the Post-Workout Anabolic Window Real?",
    "What the research actually says about the 30-minute post-workout anabolic window — and why total daily protein intake matters far more than exact timing.",
    "general", "For Students", "The post-workout anabolic window: myth or real?",
    "\"You have to get protein in within 30 minutes or you lose your gains\" is one of the most repeated claims in the gym. It's mostly wrong.",
    sec('''      <h2>The 30-minute myth</h2>
      <p>The classic \"anabolic window\" theory claimed there's a narrow 30-60 minute period after training where nutrient timing matters enormously for muscle growth. A meta-analysis of 23 randomized trials on the topic found that studies claiming a timing benefit had a hidden confound: the group told to eat protein right after training was also eating about 25% more total protein per day than the control group. Once total daily protein intake was statistically matched between groups, the timing effect on muscle growth and strength disappeared entirely.<sup class="ref"><a href="sources.html#ath10">[10]</a></sup></p>''') +
    sec('''      <h2>What actually matters</h2>
      <p>The anabolic effect of a normal mixed meal lasts several hours, not minutes — so if you ate a meal with protein 2-4 hours before training, your muscles are still actively using those amino acids well into your post-workout period, and there's no urgent countdown clock once you finish. What actually predicts results is your total protein intake across the whole day, spread reasonably across meals.<sup class="ref"><a href="sources.html#ath10">[10]</a></sup></p>''', bg="var(--color-protein-bg)", tight=True) +
    sec('''      <p>Eating protein soon after training is still a perfectly good habit — it's just not the make-or-break window it's often marketed as. See our page on <a href="protein-timing.html">protein timing</a> for the fuller picture, or hit your daily number directly.</p>
      <p><a href="calculators.html#protein-calculator" class="btn btn-primary">Calculate my protein target →</a></p>''', tight=True),
    [("protein-timing.html", "Does protein timing matter?"), ("creatine-explained.html", "Creatine explained"), ("muscle-fiber-types-and-nutrition.html", "Muscle fiber types and nutrition")]
)

add(
    "sports-drinks-vs-water",
    "Sports Drinks vs. Water: Which Do You Need?",
    "When plain water is enough during exercise and when a carbohydrate-electrolyte sports drink actually helps, based on ACSM hydration guidance.",
    "carbs", "For Students", "Sports drinks vs. water: when you actually need electrolytes",
    "Sports drink marketing implies you need electrolytes for any workout. For most people, most of the time, that's not true.",
    sec('''      <h2>When water is enough</h2>
      <p>For moderate exercise under about an hour, plain water is sufficient for the vast majority of people — you simply haven't sweated out enough sodium or burned through enough glycogen for a carbohydrate-electrolyte drink to meaningfully help, according to American College of Sports Medicine hydration guidance.<sup class="ref"><a href="sources.html#ath12">[12]</a></sup></p>''') +
    sec('''      <h2>When you actually need electrolytes</h2>
      <p>Past about 60-90 minutes of continuous exercise, ACSM guidance recommends 30-60g of carbohydrate per hour to maintain performance, delivered via a 6-8% carbohydrate-electrolyte drink taken in small amounts every 10-20 minutes. Sodium becomes especially important once exercise stretches past 2-3 hours or involves heavy sweating in heat, since sodium helps your body actually absorb and retain the fluid you're drinking rather than just passing through.<sup class="ref"><a href="sources.html#ath12">[12]</a></sup></p>''', bg="var(--color-carbs-bg)", tight=True) +
    sec('''      <table class="data-table">
        <tr><th>Situation</th><th>What to drink</th></tr>
        <tr><td>Under 60 minutes, moderate effort</td><td>Plain water</td></tr>
        <tr><td>60-90+ minutes, or heavy sweat/heat</td><td>Carb-electrolyte sports drink, small sips every 10-20 min</td></tr>
        <tr><td>2-3+ hours (endurance events)</td><td>Higher-sodium endurance drink</td></tr>
      </table>'''),
    [("how-many-carbs-per-day.html", "How many carbs do you need per day?"), ("carb-loading-for-athletes.html", "Carb loading for athletes"), ("water-weight-vs-fat-loss.html", "Water weight vs. fat loss")]
)


# --------------------------------------------------------- MORE SEO PAGES --

add(
    "net-carbs-vs-total-carbs",
    "Net Carbs vs. Total Carbs",
    "What \"net carbs\" actually means, how to calculate it, and why the number on a low-carb product's label can be misleading.",
    "carbs", "For Students", "Net carbs vs. total carbs: what's the difference?",
    "\"Net carbs\" shows up on every keto-marketed food label. It isn't an official nutrition term, and calculating it wrong can throw off your whole day.",
    sec('''      <h2>What "net carbs" means</h2>
      <p>Net carbs is calculated as total carbohydrate minus fiber (and sometimes minus sugar alcohols), based on the idea that fiber isn't digested and absorbed the way other carbs are, so it shouldn't count toward the carb total that affects blood sugar.<sup class="ref"><a href="sources.html#c5">[1]</a></sup> For example, a food with 20g total carbs and 8g fiber would be marketed as "12g net carbs."</p>''') +
    sec('''      <h2>Why it's not perfectly standardized</h2>
      <p>Unlike "Calories" or "grams of protein," net carbs is not an FDA-regulated term with one fixed formula — different brands calculate it differently, and some sugar alcohols (like maltitol) are only partially unabsorbed, so subtracting them in full can understate the real carb impact.<sup class="ref"><a href="sources.html#c1">[2]</a></sup> If you're tracking macros for a medical reason (like diabetes) rather than general dieting, total carbohydrate — not the marketing number — is what your calculations should be based on.</p>''', bg="var(--color-carbs-bg)", tight=True) +
    sec('''      <p>For everyday macro tracking, total carbs is simpler and more consistent. Use net carbs only as a rough guide on packaged low-carb products, not as your primary tracking number.</p>
      <p><a href="calculators.html#carb-calculator" class="btn btn-primary">Calculate your daily carb target →</a></p>'''),
    [("fiber-benefits.html", "Fiber benefits"), ("ketogenic-diet-explained.html", "The ketogenic diet explained"), ("how-to-read-a-nutrition-label.html", "How to read a nutrition label")]
)

add(
    "protein-intake-for-women",
    "How Much Protein Do Women Actually Need?",
    "Protein targets for women specifically — why the same g/kg guidance applies regardless of sex, and where the numbers actually differ in practice.",
    "protein", "For Students", "How much protein do women actually need?",
    "Protein recommendations are given per kilogram of body weight, not by sex — but average body weight differences mean the absolute gram targets often look different for women in practice.",
    sec('''      <h2>The RDA and training targets are the same formula</h2>
      <p>The protein RDA of 0.8 g/kg and the higher 1.4-2.0 g/kg range for people who train apply the same way regardless of sex — there's no separate "women's protein RDA" in the research.<sup class="ref"><a href="sources.html#p2">[1]</a></sup> What differs is that average body weight is lower for women than men, so the same per-kilogram target produces a lower absolute gram number — that's a body-weight effect, not a different requirement.</p>''') +
    sec('''      <h2>Where it matters in practice</h2>
      <p>Two things are worth knowing specifically: pregnancy and breastfeeding meaningfully raise protein needs above baseline, and women in a calorie deficit trying to preserve muscle benefit from the same higher end of the 1.6-2.2 g/kg range recommended for anyone dieting while training.<sup class="ref"><a href="sources.html#p3">[2]</a></sup> Neither of those is about sex directly — they're about a higher physiological demand, the same way a larger training volume raises requirements for anyone.</p>''', bg="var(--color-protein-bg)", tight=True) +
    sec('''      <p>Rather than using a generic "women's" number, calculate your own target from your actual body weight and goal.</p>
      <p><a href="calculators.html#protein-calculator" class="btn btn-primary">Calculate my protein target →</a></p>'''),
    [("how-much-protein-per-day.html", "How much protein do you need per day?"), ("macros-for-weight-loss.html", "Macros for fat loss"), ("high-protein-foods-list.html", "High-protein foods list")]
)

add(
    "does-eating-fat-make-you-fat",
    "Does Eating Fat Make You Fat?",
    "Why dietary fat and body fat are not the same thing, and what actually determines weight gain — with the research on total calories vs. fat specifically.",
    "fat", "For Students", "Does eating fat make you fat?",
    "It's an intuitive-sounding idea: eat fat, gain fat. The actual mechanism of weight gain doesn't work that way.",
    sec('''      <h2>Weight gain is a calorie story, not a macronutrient story</h2>
      <p>Body fat is gained when you consistently eat more total calories than you burn — regardless of whether those extra calories came from fat, carbs, protein, or alcohol.<sup class="ref"><a href="sources.html#f1">[1]</a></sup> Fat does have more calories per gram (9 versus 4 for protein and carbs), which makes it easier to overeat calorically without noticing, but that's a calorie-density issue, not evidence that fat itself is uniquely fattening.</p>''') +
    sec('''      <h2>Where the confusion comes from</h2>
      <p>The low-fat diet trend of the 1980s-90s conflated "dietary fat" with "body fat" partly because of the shared word, and partly because fat is calorie-dense and satiating in ways that made it an easy target. Research since then has found that low-fat and low-carb diets produce similar weight loss when calories and protein are matched — the macronutrient split matters far less than total intake for weight change specifically.<sup class="ref"><a href="sources.html#cal2">[2]</a></sup></p>''', bg="var(--color-fat-bg)", tight=True) +
    sec('''      <p>Fat is not the enemy — it's essential for hormone production and vitamin absorption. What determines weight change is your total calorie balance. <a href="calculators.html" class="btn btn-primary">Calculate my calorie and macro targets →</a></p>'''),
    [("fats.html", "What fat actually does"), ("low-fat-diet-risks.html", "Risks of very low-fat diets"), ("macros-for-weight-loss.html", "Macros for fat loss")]
)

add(
    "keto-flu-explained",
    "Keto Flu: Why It Happens and How to Fix It",
    "What causes \"keto flu\" symptoms in the first days of a ketogenic diet, why electrolytes are the main culprit, and how to actually fix it.",
    "carbs", "For Students", "Keto flu explained: why it happens and how to fix it",
    "The fatigue, headaches, and brain fog some people get starting keto aren't really about ketones — they're mostly about sodium and water.",
    sec('''      <h2>What causes it</h2>
      <p>Cutting carbs sharply depletes glycogen, and each gram of stored glycogen is bound to roughly 3 grams of water — so in the first few days of a very low-carb diet, you lose a real amount of water weight fast. That water carries sodium and potassium out with it, and low-carb eating also naturally cuts many of the foods (fruit, grains, legumes) that are typical sources of potassium and magnesium.<sup class="ref"><a href="sources.html#gen2">[1]</a></sup> The resulting electrolyte drop is what produces the classic fatigue, headache, irritability, and brain fog cluster often called "keto flu," usually appearing 2-7 days in.<sup class="ref"><a href="sources.html#gen2">[1]</a></sup></p>''') +
    sec('''      <h2>How to actually fix it</h2>
      <p>Deliberately replacing sodium (bouillon, broth, or adding salt to food), and getting enough potassium and magnesium (leafy greens, avocado, nuts — all carb-light), resolves most symptoms within 24-48 hours. Staying well-hydrated matters too, since the water loss itself is part of the mechanism.<sup class="ref"><a href="sources.html#gen2">[1]</a></sup> If symptoms persist past a week or two, that's a signal to reassess whether a very low-carb approach is the right fit for you rather than pushing through indefinitely.</p>''', bg="var(--color-carbs-bg)", tight=True),
    [("ketogenic-diet-explained.html", "The ketogenic diet explained"), ("water-weight-vs-fat-loss.html", "Water weight vs. fat loss"), ("sports-drinks-vs-water.html", "Sports drinks vs. water")]
)

add(
    "omega-3-foods-list",
    "15 Foods High in Omega-3 Fatty Acids",
    "A list of real food sources of omega-3 fatty acids, from fatty fish to plant-based ALA sources, with approximate amounts per serving.",
    "fat", "For Students", "15 foods high in omega-3 fatty acids",
    "Omega-3s are essential — your body can't make them — so getting enough depends entirely on what's on your plate.",
    sec('''      <h2>Marine sources (EPA + DHA)</h2>
      <table class="data-table">
        <tr><th>Food</th><th>Approx. omega-3 per serving</th></tr>
        <tr><td>Salmon (100g)</td><td>~2.2g</td></tr>
        <tr><td>Mackerel (100g)</td><td>~2.5g</td></tr>
        <tr><td>Sardines (100g)</td><td>~1.5g</td></tr>
        <tr><td>Anchovies (100g)</td><td>~1.4g</td></tr>
        <tr><td>Trout (100g)</td><td>~1.0g</td></tr>
        <tr><td>Oysters (100g)</td><td>~0.7g</td></tr>
      </table>
      <p>Marine sources provide EPA and DHA directly — the two omega-3 forms most directly used by the body, particularly for reducing inflammation and supporting brain and cardiovascular health.<sup class="ref"><a href="sources.html#f3">[1]</a></sup></p>''') +
    sec('''      <h2>Plant sources (ALA)</h2>
      <table class="data-table">
        <tr><th>Food</th><th>Approx. omega-3 per serving</th></tr>
        <tr><td>Flaxseed, ground (1 tbsp)</td><td>~2.4g</td></tr>
        <tr><td>Chia seeds (1 tbsp)</td><td>~2.5g</td></tr>
        <tr><td>Walnuts (30g)</td><td>~2.6g</td></tr>
        <tr><td>Hemp seeds (1 tbsp)</td><td>~1.0g</td></tr>
        <tr><td>Edamame (1 cup)</td><td>~1.0g</td></tr>
        <tr><td>Brussels sprouts (1 cup)</td><td>~0.2g</td></tr>
      </table>
      <p>Plant sources provide ALA, a precursor the body can convert to EPA and DHA — but only inefficiently (often under 10%), which is why relying on plant sources alone generally means eating considerably more of them, or using an algae-based EPA/DHA supplement.<sup class="ref"><a href="sources.html#f3">[1]</a></sup></p>''', bg="var(--color-fat-bg)", tight=True),
    [("omega-3-vs-omega-6.html", "Omega-3 vs. omega-6"), ("healthy-high-fat-foods.html", "Healthy high-fat foods"), ("vegan-macros-guide.html", "Vegan macros guide")]
)

add(
    "how-much-water-should-you-drink-per-day",
    "How Much Water Should You Drink Per Day?",
    "Real daily water intake guidance from the National Academies, why \"8 glasses a day\" is a rough rule of thumb rather than a hard number, and how activity changes it.",
    "general", "For Students", "How much water should you actually drink per day?",
    "\"Drink 8 glasses a day\" isn't wrong exactly — it's just not based on your actual body, activity level, or climate.",
    sec('''      <h2>The actual guideline</h2>
      <p>The U.S. National Academies' adequate intake for total water (from all beverages and food combined) is about 3.7 liters/day (~15.5 cups) for men and 2.7 liters/day (~11.5 cups) for women in a temperate climate. Roughly 20% of that typically comes from food, so beverage intake alone is somewhat lower than those totals.<sup class="ref"><a href="sources.html#gen1">[1]</a></sup></p>''') +
    sec('''      <h2>What changes the number</h2>
      <p>Exercise, hot or humid climates, higher body size, pregnancy/breastfeeding, and high-sodium diets all raise fluid needs above the baseline. Thirst is a reasonably reliable guide for most healthy people day-to-day; pale yellow urine is a simple practical check for adequate hydration.<sup class="ref"><a href="sources.html#gen1">[1]</a></sup> For guidance specific to exercise duration and electrolyte needs during a workout, see our dedicated breakdown.</p>''', bg="var(--color-carbs-bg)", tight=True),
    [("sports-drinks-vs-water.html", "Sports drinks vs. water"), ("water-weight-vs-fat-loss.html", "Water weight vs. fat loss"), ("tdee-vs-bmr.html", "BMR vs. TDEE")]
)

add(
    "macros-for-vegetarians",
    "Macros for Vegetarians: Hit Your Targets",
    "How to hit protein, fat, and carb targets on a vegetarian diet — complete protein combining, common gaps, and the best vegetarian protein sources.",
    "general", "For Students", "Macros for vegetarians: hitting your targets without meat",
    "Vegetarian (unlike vegan) diets still include eggs and dairy, which makes hitting protein targets considerably more straightforward — but it still takes some planning.",
    sec('''      <h2>Complete protein is easier than you'd think</h2>
      <p>Eggs, Greek yogurt, cottage cheese, and milk are all complete proteins supplying all 9 essential amino acids, the same as meat.<sup class="ref"><a href="sources.html#p1">[1]</a></sup> Combined with plant sources like lentils, quinoa, tofu, and tempeh, hitting a full protein target on a vegetarian diet is very achievable without needing to carefully combine plant proteins the way a fully vegan diet often requires.</p>''') +
    sec('''      <h2>Common gaps to watch</h2>
      <p>The main risk on a vegetarian diet isn't protein quantity — it's under-eating protein-dense foods relative to overall calories, since vegetables and grains are less calorie- and protein-dense than meat. Iron (non-heme iron from plants absorbs less efficiently than heme iron from meat) and vitamin B12 (found almost exclusively in animal products, though eggs and dairy cover this for vegetarians) are worth being deliberate about.<sup class="ref"><a href="sources.html#p2">[2]</a></sup></p>''', bg="var(--color-protein-bg)", tight=True) +
    sec('''      <p><a href="calculators.html#protein-calculator" class="btn btn-primary">Calculate your protein target →</a></p>'''),
    [("vegan-macros-guide.html", "Vegan macros guide"), ("plant-based-protein-sources.html", "Plant-based protein sources"), ("complete-vs-incomplete-protein.html", "Complete vs. incomplete protein")]
)

add(
    "high-fiber-foods-list",
    "15 High-Fiber Foods to Add to Your Diet",
    "A list of real high-fiber foods — legumes, whole grains, fruit, and vegetables — with approximate fiber content per serving, to help you hit your daily target.",
    "carbs", "For Students", "15 high-fiber foods to add to your diet",
    "Most adults fall well short of the recommended daily fiber intake. Here's what actually moves the number.",
    sec('''      <h2>Legumes and grains</h2>
      <table class="data-table">
        <tr><th>Food</th><th>Approx. fiber per serving</th></tr>
        <tr><td>Lentils, cooked (1 cup)</td><td>~15.6g</td></tr>
        <tr><td>Black beans, cooked (1 cup)</td><td>~15g</td></tr>
        <tr><td>Chickpeas, cooked (1 cup)</td><td>~12.5g</td></tr>
        <tr><td>Oats, dry (1 cup)</td><td>~8.2g</td></tr>
        <tr><td>Quinoa, cooked (1 cup)</td><td>~5.2g</td></tr>
        <tr><td>Whole wheat bread (2 slices)</td><td>~3.8g</td></tr>
      </table>''') +
    sec('''      <h2>Fruits and vegetables</h2>
      <table class="data-table">
        <tr><th>Food</th><th>Approx. fiber per serving</th></tr>
        <tr><td>Raspberries (1 cup)</td><td>~8g</td></tr>
        <tr><td>Avocado (1 whole)</td><td>~10g</td></tr>
        <tr><td>Pear, with skin (1 medium)</td><td>~5.5g</td></tr>
        <tr><td>Broccoli, cooked (1 cup)</td><td>~5.1g</td></tr>
        <tr><td>Apple, with skin (1 medium)</td><td>~4.4g</td></tr>
        <tr><td>Brussels sprouts, cooked (1 cup)</td><td>~4g</td></tr>
      </table>
      <p>Most adults need roughly 25g/day (women) to 38g/day (men) under age 50, and most people fall short of that target.<sup class="ref"><a href="sources.html#c5">[1]</a></sup> Increase fiber gradually and drink enough water alongside it — a fast jump in fiber intake without enough fluid commonly causes bloating and digestive discomfort.</p>''', bg="var(--color-carbs-bg)", tight=True),
    [("fiber-benefits.html", "Fiber benefits"), ("net-carbs-vs-total-carbs.html", "Net carbs vs. total carbs"), ("simple-vs-complex-carbs.html", "Simple vs. complex carbs")]
)


# ------------------------------------------------------------------ DIETS --

_DIETS_FAQ = [
    ("What is an animal-based diet?", "An animal-based diet emphasizes meat, organs, fish, eggs, and dairy, with limited plant foods — typically fruit, honey, and some low-toxin vegetables. It's more flexible than carnivore but far more restrictive than a standard omnivorous diet."),
    ("What is a plant-based diet?", "Plant-based means the majority of calories come from plant foods, but unlike vegan, it doesn't necessarily exclude all animal products entirely — it's a spectrum, not a strict rule."),
    ("What is a vegan diet?", "A vegan diet excludes all animal products, including meat, dairy, eggs, and honey, relying entirely on plant foods for every nutrient, including protein."),
    ("What is the paleo diet?", "The paleo diet is based on foods presumed available to Paleolithic humans — meat, fish, fruit, vegetables, nuts, and seeds — while excluding grains, legumes, dairy, and refined sugar."),
    ("What is the carnivore diet?", "The carnivore diet consists exclusively of animal products — meat, fish, eggs, and sometimes dairy — excluding all plant foods, including fruits and vegetables."),
    ("What is a vegetarian diet?", "A vegetarian diet excludes meat, poultry, and fish, but typically still includes eggs and dairy, making it easier to hit protein targets than a fully vegan diet."),
    ("What is a pescatarian diet?", "A pescatarian diet excludes meat and poultry but includes fish and seafood, along with eggs, dairy, and plant foods — often described as vegetarian plus fish."),
    ("What is the keto diet?", "The ketogenic diet keeps carbs very low (usually under 50g/day) and fat very high (roughly 70-80% of calories) to shift the body into ketosis, burning fat and ketones for fuel instead of glucose."),
    ("What is the Mediterranean diet?", "The Mediterranean diet emphasizes vegetables, fruit, whole grains, legumes, olive oil, and fish, with red meat and processed food kept minimal — it has one of the strongest research bases of any named diet, including the landmark PREDIMED cardiovascular trial."),
]

_DIET_COMPARE_DATA = [
    {"id": "animal", "name": "Animal-based", "p": 35, "f": 55, "c": 10, "macros": "High protein, high fat, low-moderate carb", "includes": "Meat, organs, fish, eggs, dairy, some fruit &amp; honey", "excludes": "Most plants, grains, refined sugar", "evidence": "Newer trend, not clinically established"},
    {"id": "plant", "name": "Plant-based", "p": 15, "f": 25, "c": 60, "macros": "Varies — typically higher carb, moderate protein", "includes": "Vegetables, fruit, grains, legumes; may include some animal foods", "excludes": "Nothing strictly — it's a spectrum, not a hard rule", "evidence": "Broadly supported for heart health"},
    {"id": "vegan", "name": "Vegan", "p": 15, "f": 25, "c": 60, "macros": "Moderate protein (needs combining), higher carb", "includes": "All plant foods", "excludes": "All animal products: meat, dairy, eggs, honey", "evidence": "Well-studied; plan B12 and iron"},
    {"id": "paleo", "name": "Paleo", "p": 27, "f": 43, "c": 30, "macros": "High protein (19-35%), moderate fat (28-58%), low-moderate carb (22-40%)", "includes": "Meat, fish, fruit, vegetables, nuts, seeds", "excludes": "Grains, legumes, dairy, refined sugar", "evidence": "Short-term gains mostly from cutting processed food"},
    {"id": "carnivore", "name": "Carnivore", "p": 40, "f": 60, "c": 0, "macros": "Very high protein &amp; fat, ~0% carb", "includes": "Meat, fish, eggs, sometimes dairy", "excludes": "All plant foods", "evidence": "Real long-term deficiency risk (vitamin C, magnesium, calcium)"},
    {"id": "vegetarian", "name": "Vegetarian", "p": 20, "f": 30, "c": 50, "macros": "Moderate-high protein, moderate fat, moderate-high carb", "includes": "Vegetables, fruit, grains, legumes, eggs, dairy", "excludes": "Meat, poultry, fish", "evidence": "Well-studied; easier protein than vegan"},
    {"id": "pescatarian", "name": "Pescatarian", "p": 30, "f": 35, "c": 35, "macros": "High protein, moderate omega-3-rich fat, moderate carb", "includes": "Fish, seafood, eggs, dairy, plant foods", "excludes": "Meat, poultry", "evidence": "Strong cardiovascular evidence"},
    {"id": "keto", "name": "Keto", "p": 20, "f": 75, "c": 5, "macros": "Moderate protein, very high fat (70-80%), very low carb (&lt;50g/day)", "includes": "Meat, fish, eggs, high-fat dairy, low-carb vegetables, oils", "excludes": "Grains, sugar, most fruit, starchy vegetables", "evidence": "Effective short-term; long-term data limited"},
    {"id": "mediterranean", "name": "Mediterranean", "p": 18, "f": 37, "c": 45, "macros": "Moderate protein, moderate-high unsaturated fat, moderate carb", "includes": "Vegetables, fruit, whole grains, legumes, olive oil, fish", "excludes": "Little red meat, minimal processed food", "evidence": "Strongest evidence base (PREDIMED trial)"},
]

_DIET_COMPARE_TOOL = '''      <h2>Compare any two diets</h2>
      <p class="section-intro">Pick two diets below and see exactly how they differ — macros, what's included, what's excluded, and how strong the evidence is.</p>
      <div class="diet-picker-row">
        <div class="diet-picker" id="diet-picker-a">
          <span class="diet-picker-label">First diet</span>
          <button type="button" class="diet-picker-btn" id="diet-picker-a-btn" aria-haspopup="listbox" aria-expanded="false">
            <span class="diet-picker-current"></span>
            <svg class="chev" width="12" height="8" viewBox="0 0 12 8" fill="none"><path d="M1 1l5 5 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
          <div class="diet-picker-menu" id="diet-picker-a-menu" role="listbox"></div>
        </div>
        <button type="button" class="diet-swap-btn" id="diet-swap-btn" aria-label="Swap diets" title="Swap">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M7 4l-4 4 4 4M3 8h13M17 12l4 4-4 4M21 16H8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>
        <div class="diet-picker" id="diet-picker-b">
          <span class="diet-picker-label">Second diet</span>
          <button type="button" class="diet-picker-btn" id="diet-picker-b-btn" aria-haspopup="listbox" aria-expanded="false">
            <span class="diet-picker-current"></span>
            <svg class="chev" width="12" height="8" viewBox="0 0 12 8" fill="none"><path d="M1 1l5 5 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
          <div class="diet-picker-menu" id="diet-picker-b-menu" role="listbox"></div>
        </div>
      </div>
      <div id="diet-compare-chart"></div>
      <div id="diet-compare-table"></div>
      <script>
      (function () {
        var DIETS = ''' + json.dumps(_DIET_COMPARE_DATA) + ''';
        var chart = document.getElementById("diet-compare-chart");
        var out = document.getElementById("diet-compare-table");
        var state = { a: "vegan", b: "keto" };

        function dietById(id) { return DIETS.filter(function (d) { return d.id === id; })[0]; }
        function dominant(d) {
          if (d.p >= d.f && d.p >= d.c) return "protein";
          if (d.f >= d.p && d.f >= d.c) return "fat";
          return "carbs";
        }

        function closeAll() {
          document.querySelectorAll(".diet-picker-menu.open").forEach(function (m) { m.classList.remove("open"); });
          document.querySelectorAll(".diet-picker-btn.open").forEach(function (b) { b.classList.remove("open"); b.setAttribute("aria-expanded", "false"); });
        }
        document.addEventListener("click", closeAll);
        document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeAll(); });

        function buildPicker(key) {
          var btn = document.getElementById("diet-picker-" + key + "-btn");
          var menu = document.getElementById("diet-picker-" + key + "-menu");
          DIETS.forEach(function (d) {
            var opt = document.createElement("div");
            opt.className = "diet-picker-option";
            opt.setAttribute("role", "option");
            opt.dataset.id = d.id;
            opt.innerHTML = '<i class="dot ' + dominant(d) + '"></i><span>' + d.name + '</span><span class="check">\\u2713</span>';
            opt.addEventListener("click", function (e) {
              e.stopPropagation();
              state[key] = d.id;
              closeAll();
              render();
            });
            menu.appendChild(opt);
          });
          btn.addEventListener("click", function (e) {
            e.stopPropagation();
            var isOpen = menu.classList.contains("open");
            closeAll();
            if (!isOpen) {
              menu.classList.add("open");
              btn.classList.add("open");
              btn.setAttribute("aria-expanded", "true");
            }
          });
        }
        buildPicker("a");
        buildPicker("b");

        document.getElementById("diet-swap-btn").addEventListener("click", function (e) {
          e.stopPropagation();
          var tmp = state.a; state.a = state.b; state.b = tmp;
          render();
        });

        function chartCard(d) {
          return '<div class="diet-chart-card">' +
            '<h3>' + d.name + '</h3>' +
            '<div class="diet-chart-bar">' +
              '<span class="seg protein" style="width:' + d.p + '%" title="Protein ' + d.p + '%"></span>' +
              '<span class="seg fat" style="width:' + d.f + '%" title="Fat ' + d.f + '%"></span>' +
              '<span class="seg carbs" style="width:' + d.c + '%" title="Carbs ' + d.c + '%"></span>' +
            '</div>' +
            '<div class="diet-chart-legend">' +
              '<span><i class="dot protein"></i>Protein ' + d.p + '%</span>' +
              '<span><i class="dot fat"></i>Fat ' + d.f + '%</span>' +
              '<span><i class="dot carbs"></i>Carbs ' + d.c + '%</span>' +
            '</div></div>';
        }

        function render() {
          var a = dietById(state.a), b = dietById(state.b);
          document.querySelector("#diet-picker-a-btn .diet-picker-current").textContent = a.name;
          document.querySelector("#diet-picker-b-btn .diet-picker-current").textContent = b.name;
          document.querySelectorAll("#diet-picker-a-menu .diet-picker-option").forEach(function (o) { o.classList.toggle("selected", o.dataset.id === state.a); });
          document.querySelectorAll("#diet-picker-b-menu .diet-picker-option").forEach(function (o) { o.classList.toggle("selected", o.dataset.id === state.b); });
          chart.innerHTML = '<div class="diet-chart">' + chartCard(a) + chartCard(b) + '</div>';
          var rows = [["Typically includes", "includes"], ["Typically excludes", "excludes"], ["Evidence strength", "evidence"]];
          var html = '<div class="diet-info-card"><div class="diet-info-head"><span></span><span>' +
            a.name + '</span><span>' + b.name + '</span></div>';
          rows.forEach(function (r) {
            html += '<div class="diet-info-row"><span class="diet-info-key">' + r[0] + '</span><span>' + a[r[1]] + '</span><span>' + b[r[1]] + '</span></div>';
          });
          html += "</div>";
          out.innerHTML = html;
        }
        render();
      })();
      </script>'''

add(
    "diets-explained",
    "Diets Explained &amp; Compared Side by Side",
    "Compare animal-based, plant-based, vegan, paleo, carnivore, vegetarian, pescatarian, keto, and Mediterranean diets side by side on macros and evidence.",
    "diets", "Diets", "Diets",
    "Every diet you've heard of is really just a different rule about which foods are in or out. Pick any two below to compare them, or read the full breakdown of each.",
    sec(_DIET_COMPARE_TOOL, bg="var(--color-pop3-bg)", tight=True) +
    sec('''      <h2>Animal-based</h2>
      <p>An animal-based diet centers on meat, organs, fish, eggs, and dairy, while still allowing a limited amount of plant food — typically fruit, honey, and squash, chosen for being relatively low in the plant compounds ("antinutrients") some animal-based proponents try to avoid. It's meaningfully more flexible than carnivore, since it doesn't ban fruit outright, but far more restrictive than a standard diet. It's a newer, less clinically studied eating pattern than the others on this list, so treat specific health claims about it with more caution.</p>
      <h2>Plant-based</h2>
      <p>"Plant-based" describes a spectrum rather than one strict rule: the majority of calories come from plants, but it doesn't necessarily mean zero animal products the way vegan does. Someone eating plant-based might still have eggs or fish occasionally — the emphasis is on proportion, not a hard exclusion list.</p>
      <h2>Vegan</h2>
      <p>Vegan excludes all animal products — meat, dairy, eggs, and honey — with 100% of nutrients, including all essential amino acids, coming from plant sources.<sup class="ref"><a href="sources.html#p1">[1]</a></sup> Because no single common plant food supplies complete protein the way meat, eggs, or dairy do, vegan diets require more deliberate food combining. See our full <a href="vegan-macros-guide.html">vegan macros guide</a>.</p>''') +
    sec('''      <h2>Paleo</h2>
      <p>The paleo diet is built around foods presumed available to Paleolithic humans — lean meat, fish, fruit, vegetables, nuts, and seeds — while excluding grains, legumes, dairy, refined sugar, and processed food. It's typically high protein (19-35% of calories), moderate fat (28-58%), and relatively low carb (22-40%).<sup class="ref"><a href="sources.html#gen3">[2]</a></sup> See our full <a href="paleo-diet-explained.html">paleo diet guide</a>.</p>
      <h2>Carnivore</h2>
      <p>Carnivore is the strictest pattern here: animal products only — meat, fish, eggs, sometimes dairy — with zero plant foods, including fruits and vegetables. Cutting out entire food groups removes fiber and several plant-derived compounds linked to lower chronic disease risk, and clinicians caution that long-term nutrient deficiencies (vitamin C, magnesium, calcium) are a real risk without careful planning.<sup class="ref"><a href="sources.html#gen4">[3]</a></sup> See our full <a href="carnivore-diet-explained.html">carnivore diet guide</a>.</p>''', bg="var(--color-pop3-bg)", tight=True) +
    sec('''      <h2>Keto</h2>
      <p>The ketogenic diet keeps carbs very low — usually under 50g/day, roughly 5-10% of calories — and fat very high (70-80%), with moderate protein, to push the body into ketosis and rely on fat and ketones for fuel instead of glucose. See our full <a href="ketogenic-diet-explained.html">keto diet guide</a>. Common early side effects ("keto flu") come from rapid sodium and water loss, not the ketones themselves — see our <a href="keto-flu-explained.html">keto flu explainer</a>.</p>
      <h2>Mediterranean</h2>
      <p>The Mediterranean diet emphasizes vegetables, fruit, whole grains, legumes, and olive oil as the principal fat, with fish regularly and red meat rarely. It has one of the strongest research bases of any named diet — the landmark PREDIMED trial found roughly 30% fewer major cardiovascular events in people following it.<sup class="ref"><a href="sources.html#gen6">[4]</a></sup> See our full <a href="mediterranean-diet-explained.html">Mediterranean diet guide</a>.</p>''') +
    sec('''      <h2>Vegetarian</h2>
      <p>Vegetarian excludes meat, poultry, and fish but usually keeps eggs and dairy, which makes hitting protein targets considerably more straightforward than fully vegan, since eggs and dairy are already complete proteins. See our full <a href="macros-for-vegetarians.html">vegetarian macros guide</a>.</p>
      <h2>Pescatarian</h2>
      <p>Pescatarian excludes meat and poultry but includes fish and seafood alongside eggs, dairy, and plant foods — essentially vegetarian plus fish. Research associates regular seafood intake with meaningfully lower cardiovascular risk, largely via omega-3 fatty acids.<sup class="ref"><a href="sources.html#gen5">[5]</a></sup> See our full <a href="pescatarian-diet-explained.html">pescatarian diet guide</a>.</p>''', bg="var(--color-pop3-bg)", tight=True) +
    sec('''      <h2>Which one is "best"?</h2>
      <p>None of these is universally optimal — each is a different set of food-group restrictions, and the research consistently points to total calories, protein adequacy, and diet quality (whole foods vs. processed) mattering more for most health outcomes than which specific pattern you follow. The right one is the one that hits your protein target, fits your life, and you can sustain.</p>
      <p><a href="calculators.html" class="btn btn-primary">Calculate your macros on any diet →</a></p>'''),
    [("mediterranean-diet-explained.html", "The Mediterranean diet explained"), ("ketogenic-diet-explained.html", "The ketogenic diet explained"), ("vegan-macros-guide.html", "Vegan macros guide")],
    extra_head=faq_jsonld(_DIETS_FAQ),
)

add(
    "paleo-diet-explained",
    "Paleo Diet Explained: Food List &amp; Macros",
    "What the paleo diet includes and excludes, its typical macronutrient split, and what the research actually says about its health claims.",
    "diets", "Diets", "The paleo diet explained",
    "Paleo is built on a simple pitch: eat like humans did before agriculture. The actual food list and evidence are more nuanced than that pitch suggests.",
    sec('''      <h2>What's in and what's out</h2>
      <p>Paleo includes lean meat (especially grass-fed or wild game), fish, fruit, vegetables, nuts, and seeds — foods that could plausibly be hunted or gathered. It excludes grains, legumes, dairy, refined sugar, and most processed food. Macronutrient-wise, it typically runs high protein (19-35% of calories), moderate fat (28-58%), and relatively low carbohydrate (22-40%) compared to a standard diet.<sup class="ref"><a href="sources.html#gen3">[1]</a></sup></p>''') +
    sec('''      <h2>What the evidence actually shows</h2>
      <p>Paleo does tend to produce weight loss and better blood markers in short-term studies. But that's largely because it cuts refined sugar and ultra-processed food — changes that help on almost any eating pattern, not something unique to eating "like a caveman." There's a trade-off too: excluding whole grains and legumes removes well-established sources of fiber and micronutrients, so a poorly planned paleo diet can fall short there.<sup class="ref"><a href="sources.html#c5">[2]</a></sup></p>''', bg="var(--color-pop3-bg)", tight=True) +
    sec('''      <p><a href="calculators.html" class="btn btn-primary">Calculate your macros on paleo →</a></p>'''),
    [("diets-explained.html", "Diets explained: every major pattern"), ("carnivore-diet-explained.html", "The carnivore diet explained"), ("net-carbs-vs-total-carbs.html", "Net carbs vs. total carbs")]
)

add(
    "carnivore-diet-explained",
    "Carnivore Diet Explained: Risks &amp; Reality",
    "What the carnivore diet actually restricts, why some people report short-term benefits, and the nutrient-deficiency risks clinicians flag with long-term use.",
    "diets", "Diets", "The carnivore diet explained",
    "Carnivore is the strictest common elimination diet — animal products only, nothing else. That simplicity is also its biggest risk.",
    sec('''      <h2>What it is</h2>
      <p>Carnivore means animal products exclusively — meat, fish, eggs, and sometimes dairy — with zero plant foods of any kind, including fruits, vegetables, grains, and legumes. Some short-term reports describe improved energy or digestive symptoms, plausibly from cutting processed food and added sugar entirely, similar to other elimination diets.</p>''') +
    sec('''      <h2>The real risks</h2>
      <p>Removing every plant food removes fiber, carotenoids, and polyphenols entirely — compounds linked to lower risk of chronic disease. Clinicians report deficiencies in vitamin C, magnesium, calcium, and thiamin among long-term carnivore dieters, and caution the diet should be avoided by anyone with high blood pressure, high cholesterol, or cardiovascular disease.<sup class="ref"><a href="sources.html#gen4">[1]</a></sup> Short-term experimentation is one thing; long-term adherence without medical supervision carries real, documented risk.</p>''', bg="var(--color-pop3-bg)", tight=True),
    [("diets-explained.html", "Diets explained: every major pattern"), ("do-elimination-diets-improve-performance.html", "Do elimination diets improve performance?"), ("animal-based-diet-explained.html", "The animal-based diet explained")]
)

add(
    "animal-based-diet-explained",
    "Animal-Based Diet Explained",
    "What an animal-based diet actually allows compared to strict carnivore, and why the distinction matters if you're considering either.",
    "diets", "Diets", "The animal-based diet explained",
    "Animal-based and carnivore get used interchangeably online. They're not the same diet.",
    sec('''      <h2>How it differs from carnivore</h2>
      <p>An animal-based diet centers on meat, organs, fish, eggs, and dairy — but unlike strict carnivore, it allows a limited amount of plant food, typically fruit, honey, and squash, chosen for being relatively low in plant compounds some proponents try to minimize. It's low-carb but not necessarily ketogenic, since fruit and honey add meaningful carbohydrate on top of the animal-product base.</p>''') +
    sec('''      <h2>Where the evidence stands</h2>
      <p>This is a newer, less clinically studied pattern than paleo, vegan, or vegetarian, and much of its popularity traces to individual influencers and anecdotal reports rather than controlled research. The same general caution that applies to carnivore applies here in a milder form: cutting most plant foods reduces fiber and phytonutrient intake, so if you try it, doing so with some awareness of what you're giving up is worth it.<sup class="ref"><a href="sources.html#gen4">[1]</a></sup></p>''', bg="var(--color-pop3-bg)", tight=True),
    [("diets-explained.html", "Diets explained: every major pattern"), ("carnivore-diet-explained.html", "The carnivore diet explained"), ("paleo-diet-explained.html", "The paleo diet explained")]
)

add(
    "pescatarian-diet-explained",
    "Pescatarian Diet: Benefits &amp; Macros",
    "What a pescatarian diet includes, the cardiovascular research behind it, and how to structure protein, fat, and carbs on it.",
    "diets", "Diets", "The pescatarian diet explained",
    "Pescatarian is often described as \"vegetarian plus fish\" — and that one addition changes the nutrition picture meaningfully.",
    sec('''      <h2>What it includes</h2>
      <p>Pescatarian excludes meat and poultry but keeps fish and seafood, alongside eggs, dairy, vegetables, fruit, grains, legumes, nuts, and seeds. That combination makes it one of the easier restrictive diets to hit both protein and omega-3 targets on, since fatty fish delivers complete protein and EPA/DHA in one food.<sup class="ref"><a href="sources.html#gen5">[1]</a></sup></p>''') +
    sec('''      <h2>The cardiovascular research</h2>
      <p>Regular seafood intake is linked to meaningfully lower cardiovascular risk — one widely cited analysis found roughly a 36% lower risk of death from heart disease associated with eating about 8 ounces of seafood per week, largely attributed to omega-3 fatty acids.<sup class="ref"><a href="sources.html#gen5">[1]</a></sup> Avoiding red and processed meat specifically (rather than all animal products) is also associated with lower rates of certain cancers and type 2 diabetes.</p>''', bg="var(--color-pop3-bg)", tight=True) +
    sec('''      <p><a href="calculators.html" class="btn btn-primary">Calculate your macros on pescatarian →</a></p>'''),
    [("diets-explained.html", "Diets explained: every major pattern"), ("omega-3-foods-list.html", "15 foods high in omega-3"), ("macros-for-vegetarians.html", "Macros for vegetarians")]
)

add(
    "plant-based-vs-vegan-diet",
    "Plant-Based vs. Vegan: The Real Difference",
    "Plant-based and vegan get used as synonyms constantly. They're not the same thing — here's the real distinction and why it matters for tracking macros.",
    "diets", "Diets", "Plant-based vs. vegan: what's actually the difference?",
    "\"Plant-based\" and \"vegan\" show up interchangeably in headlines, but they describe different rules — one is a strict exclusion list, the other is a loose emphasis.",
    sec('''      <h2>The actual difference</h2>
      <p>Vegan is a hard rule: zero animal products, full stop — no meat, dairy, eggs, or honey, in any amount, for any reason.<sup class="ref"><a href="sources.html#p1">[1]</a></sup> Plant-based is a spectrum: the majority of the diet is plant foods, but it doesn't necessarily mean zero animal products — someone eating "plant-based" might still have occasional eggs, fish, or dairy. Every vegan diet is plant-based; not every plant-based diet is vegan.</p>''') +
    sec('''      <h2>Why the distinction matters for macros</h2>
      <p>If you're tracking macros, this distinction changes your protein strategy considerably. A plant-based diet that still includes eggs or dairy has easy access to complete protein; a strict vegan diet needs deliberate combining of plant proteins (legumes, grains, soy) across the day to cover all 9 essential amino acids reliably.<sup class="ref"><a href="sources.html#p1">[1]</a></sup> Know which one you're actually doing before you plan your protein sources.</p>''', bg="var(--color-pop3-bg)", tight=True) +
    sec('''      <p><a href="calculators.html#protein-calculator" class="btn btn-primary">Calculate your protein target →</a></p>'''),
    [("vegan-macros-guide.html", "Vegan macros guide"), ("diets-explained.html", "Diets explained: every major pattern"), ("plant-based-protein-sources.html", "Plant-based protein sources")]
)

# ------------------------------------------------------------- MORE PAGES --

add(
    "cheat-days-do-they-help-or-hurt",
    "Cheat Days: Do They Help or Hurt?",
    "What a cheat day does to your metabolism and progress, whether it helps adherence, and how it compares to more moderate approaches like flexible dieting.",
    "general", "For Students", "Cheat days: do they actually help or hurt?",
    "One high-calorie day a week isn't going to undo your progress — but it's also not the metabolism-boosting hack it's sometimes marketed as.",
    sec('''      <h2>What a cheat day actually does</h2>
      <p>A single high-calorie day causes a small, temporary bump in metabolic rate and can refill glycogen stores (with some accompanying water weight), but it does not meaningfully "reset" a slowed metabolism the way it's sometimes marketed — metabolic adaptation to dieting is a gradual process that one day doesn't reverse.<sup class="ref"><a href="sources.html#cal2">[1]</a></sup> The main practical effect of a cheat day is psychological: for some people, having a planned release valve improves adherence to the rest of the week.</p>''') +
    sec('''      <h2>Cheat day vs. flexible dieting</h2>
      <p>The risk with a dedicated "cheat day" is that it can turn into a large enough calorie surplus to offset several days of a deficit, especially if it isn't planned with any structure. A more moderate alternative many people find easier to sustain is flexible dieting (IIFYM) — working treats into your regular daily targets in moderate amounts, rather than saving everything for one unrestricted day.<sup class="ref"><a href="sources.html#cal2">[1]</a></sup></p>''', bg="var(--color-carbs-bg)", tight=True),
    [("iifym-flexible-dieting.html", "IIFYM explained"), ("macros-for-weight-loss.html", "Macros for fat loss"), ("cutting-bulking-maintenance-explained.html", "Cutting, bulking, and maintenance"),]
)

add(
    "sugar-addiction-is-it-real",
    "Is Sugar Addiction Real? What Research Shows",
    "Whether sugar is addictive in the same sense as drugs, what brain-reward research actually finds, and why cravings feel so strong anyway.",
    "carbs", "For Students", "Is sugar addiction real?",
    "\"Sugar is as addictive as cocaine\" is one of the most repeated claims in diet culture. The actual research is a lot more measured.",
    sec('''      <h2>What the research actually shows</h2>
      <p>Sugar does activate the brain's dopamine reward pathway, the same general system involved in drug addiction — but most of the striking findings behind the "sugar is addictive" claim come from animal studies using intermittent access to large amounts of sugar, a very different setup from normal human eating.<sup class="ref"><a href="sources.html#c3">[1]</a></sup> In humans, sugar doesn't reliably produce the tolerance, withdrawal, and compulsive use pattern that defines addiction in the clinical sense — most researchers describe strong sugar cravings as closer to a learned, highly palatable-food-driven habit than a true substance addiction.</p>''') +
    sec('''      <h2>Why cravings still feel so strong</h2>
      <p>Highly processed foods that combine sugar, fat, and salt are engineered to be intensely palatable, and irregular eating patterns (skipping meals, chronic dieting) amplify cravings by leaving you under-fueled. Neither of those requires an "addiction" framework to explain — consistent meals with adequate protein and fiber, and not treating any food as fully off-limits, reliably reduces the intensity of cravings for most people.</p>''', bg="var(--color-carbs-bg)", tight=True),
    [("common-nutrition-myths-debunked.html", "Common nutrition myths debunked"), ("sugar-vs-starch.html", "Sugar vs. starch"), ("iifym-flexible-dieting.html", "IIFYM explained")]
)

add(
    "best-time-to-eat-carbs",
    "Is There a Best Time to Eat Carbs?",
    "Whether eating carbs at a specific time of day (morning, evening, around workouts) actually matters for fat loss or performance.",
    "carbs", "For Students", "Is there a best time to eat carbs?",
    "\"Don't eat carbs after 6pm\" is one of the most persistent diet rules with almost nothing behind it.",
    sec('''      <h2>What actually matters: total intake, not timing</h2>
      <p>For fat loss and general health, total daily carbohydrate and calorie intake predicts outcomes far more reliably than what time of day you eat them. Studies comparing carb-heavy-morning vs. carb-heavy-evening eating patterns with matched total calories generally find no meaningful difference in weight or fat loss.<sup class="ref"><a href="sources.html#cal2">[1]</a></sup></p>''') +
    sec('''      <h2>Where timing has a real, smaller effect</h2>
      <p>The one place timing has a genuine, evidence-backed role is around exercise: eating carbs before and after a hard training session supports performance and glycogen replenishment more directly than eating the same carbs at a random time of day.<sup class="ref"><a href="sources.html#c2">[2]</a></sup> That's a performance optimization, though — not a fat-loss requirement.</p>''', bg="var(--color-carbs-bg)", tight=True),
    [("carb-loading-for-athletes.html", "Carb loading for athletes"), ("post-workout-anabolic-window.html", "The post-workout anabolic window"), ("meal-frequency-and-metabolism.html", "Meal frequency and metabolism")]
)

add(
    "are-protein-bars-actually-healthy",
    "Are Protein Bars Actually Healthy?",
    "What's really in most protein bars, how to read the label past the marketing, and when a protein bar is a good choice.",
    "protein", "For Students", "Are protein bars actually healthy?",
    "A protein bar can be a solid convenience food or barely-better-than-candy — the front-of-package marketing won't tell you which.",
    sec('''      <h2>What to actually check on the label</h2>
      <p>Skip the front-of-package claims and check three numbers on the back. <strong>Protein per calorie</strong> — protein should make up a real share of the total, not a few grams padded out with sugar and fat. <strong>Added sugar</strong> — many bars carry 15-20g, more than a candy bar. <strong>Fiber and sugar alcohols</strong> — useful in moderation, but a common cause of digestive discomfort in large amounts.<sup class="ref"><a href="sources.html#cal2">[1]</a></sup></p>''') +
    sec('''      <h2>When a protein bar is a good choice</h2>
      <p>A protein bar is a legitimately good option when whole food isn't practical — traveling, between meetings, post-workout when you need something quickly. It's a worse choice as a routine meal replacement, since whole foods generally deliver more fiber, micronutrients, and satiety per calorie than a processed bar.</p>''', bg="var(--color-protein-bg)", tight=True) +
    sec('''      <p><a href="high-protein-foods-list.html" class="btn btn-primary">See whole-food high-protein options →</a></p>'''),
    [("high-protein-foods-list.html", "High-protein foods list"), ("protein-powder-101.html", "Protein powder 101"), ("how-to-read-a-nutrition-label.html", "How to read a nutrition label")]
)

add(
    "bulking-without-gaining-fat",
    "How to Bulk Without Gaining Excess Fat",
    "How to run a calorie surplus for muscle gain while minimizing fat gain — surplus size, protein intake, and how to know when to stop.",
    "general", "For Students", "How to bulk without gaining excess fat",
    "Building muscle requires a calorie surplus — but a bigger surplus doesn't build muscle faster, it just adds more fat along the way.",
    sec('''      <h2>Keep the surplus small</h2>
      <p>Muscle growth has a biological ceiling on how fast it can happen (a large surplus can't force it faster), so a modest surplus of roughly 10-20% above maintenance calories is generally recommended over an aggressive one — it supports muscle growth while minimizing the fat gained alongside it.<sup class="ref"><a href="sources.html#cal2">[1]</a></sup> A larger surplus mostly just means more of the weight gained ends up being fat rather than muscle.</p>''') +
    sec('''      <h2>Protein and monitoring matter more than the exact number</h2>
      <p>Keeping protein in the 1.6-2.2 g/kg range supports muscle gain specifically (rather than just generic weight gain), and tracking your rate of weight gain — aiming for roughly 0.25-0.5% of body weight per week — lets you adjust the surplus up or down before it drifts into excess fat gain.<sup class="ref"><a href="sources.html#p2">[2]</a></sup></p>''', bg="var(--color-protein-bg)", tight=True) +
    sec('''      <p><a href="calculators.html" class="btn btn-primary">Calculate your bulking calories and macros →</a></p>'''),
    [("macros-for-muscle-gain.html", "Macros for muscle gain"), ("cutting-bulking-maintenance-explained.html", "Cutting, bulking, and maintenance"), ("body-recomposition-explained.html", "Body recomposition explained")]
)

add(
    "portion-sizes-without-a-scale",
    "Estimate Portion Sizes Without a Scale",
    "Practical hand-based and household-object portion estimation methods for when you can't or don't want to weigh your food.",
    "general", "For Students", "How to estimate portion sizes without a food scale",
    "A food scale is the most accurate way to track macros — but it's not the only way, and it's not required to eat consistently.",
    sec('''      <h2>Hand-based estimates</h2>
      <table class="data-table">
        <tr><th>Food type</th><th>Rough portion</th></tr>
        <tr><td>Protein (meat, fish, tofu)</td><td>Palm-sized, palm-thick</td></tr>
        <tr><td>Carbs (rice, pasta, potato)</td><td>Cupped hand</td></tr>
        <tr><td>Fat (oils, nut butter, cheese)</td><td>Thumb-sized</td></tr>
        <tr><td>Vegetables</td><td>Fist-sized or more</td></tr>
      </table>
      <p>Hand-based portions scale naturally with body size (bigger hands tend to belong to people with higher calorie needs), which is part of why they work reasonably well as a rough guide without a scale.</p>''') +
    sec('''      <h2>How accurate this actually is</h2>
      <p>Hand and household-object estimates are noticeably less precise than a food scale — expect meaningful day-to-day variance rather than gram-level accuracy. That's a fair trade-off for many people: it's far more sustainable long-term than weighing every meal, and "roughly consistent" beats "perfectly accurate for two weeks, then abandoned."<sup class="ref"><a href="sources.html#cal2">[1]</a></sup></p>''', bg="var(--color-carbs-bg)", tight=True),
    [("how-to-calculate-macros-by-hand.html", "How to calculate macros by hand"), ("iifym-flexible-dieting.html", "IIFYM explained"), ("units-and-conversions-cheat-sheet.html", "Units and conversions cheat sheet")]
)


# ------------------------------------------------------- MORE DIETS + PAGES --

add(
    "mediterranean-diet-explained",
    "Mediterranean Diet Explained: The Evidence",
    "What the Mediterranean diet includes, why it's one of the most rigorously studied eating patterns, and what the landmark PREDIMED trial found.",
    "diets", "Diets", "The Mediterranean diet explained",
    "Unlike most diet trends, the Mediterranean diet has decades of high-quality research behind it — including one of nutrition science's most cited randomized trials.",
    sec('''      <h2>What it actually includes</h2>
      <p>The Mediterranean diet centers on vegetables, fruit, whole grains, legumes, nuts, and olive oil as the principal fat, with fish and seafood regularly, poultry and dairy in moderation, red meat rarely, and optional moderate wine. It's less a strict macro ratio than a pattern of food choices — higher total fat than a typical low-fat diet, but overwhelmingly unsaturated fat from olive oil, nuts, and fish rather than saturated fat.<sup class="ref"><a href="sources.html#gen6">[1]</a></sup></p>''') +
    sec('''      <h2>The evidence behind it</h2>
      <p>The landmark PREDIMED trial randomly assigned thousands of people at high cardiovascular risk to a Mediterranean diet (enriched with either extra-virgin olive oil or nuts) versus a low-fat control diet, and found roughly a 30% lower rate of major cardiovascular events — heart attack, stroke, cardiovascular death — in the Mediterranean diet groups.<sup class="ref"><a href="sources.html#gen6">[1]</a></sup> That's a considerably stronger evidence base than most named diets have, which is part of why it's consistently recommended by major health organizations rather than treated as a trend.</p>''', bg="var(--color-pop3-bg)", tight=True) +
    sec('''      <p><a href="calculators.html" class="btn btn-primary">Calculate your macros on any diet →</a></p>'''),
    [("diets-explained.html", "Diets explained: every major pattern"), ("dash-diet-explained.html", "The DASH diet explained"), ("healthy-high-fat-foods.html", "Healthy high-fat foods")]
)

add(
    "dash-diet-explained",
    "DASH Diet Explained: Lower Blood Pressure",
    "What the DASH diet is, how it differs from Mediterranean, and the sodium and potassium targets behind why it works for blood pressure.",
    "diets", "Diets", "The DASH diet explained",
    "DASH stands for Dietary Approaches to Stop Hypertension — and unlike most diets, it was designed and tested specifically for that one outcome.",
    sec('''      <h2>What it includes</h2>
      <p>DASH emphasizes vegetables, fruit, whole grains, low-fat dairy, and lean protein, while limiting sodium, red meat, added sugar, and saturated fat. It supplies a balanced macronutrient mix — complex carbohydrates from whole grains and legumes, lean protein, and modest fat — developed and clinically tested by the National Heart, Lung, and Blood Institute specifically to lower blood pressure.<sup class="ref"><a href="sources.html#gen7">[1]</a></sup></p>''') +
    sec('''      <h2>How it differs from Mediterranean</h2>
      <p>DASH and Mediterranean overlap heavily — both emphasize whole foods, vegetables, and limiting red meat — but DASH is more explicitly sodium-restricted and dairy-inclusive, built around clinical blood pressure trials, while Mediterranean is built around cardiovascular outcomes more broadly and includes more olive oil and moderate wine. Both are considered strong, evidence-backed patterns rather than restrictive trends.<sup class="ref"><a href="sources.html#gen7">[1]</a></sup></p>''', bg="var(--color-pop3-bg)", tight=True),
    [("mediterranean-diet-explained.html", "The Mediterranean diet explained"), ("sodium-how-much-do-you-need.html", "Sodium: how much do you actually need?"), ("diets-explained.html", "Diets explained: every major pattern")]
)

add(
    "intuitive-eating-explained",
    "Intuitive Eating Explained",
    "What intuitive eating actually means as a structured approach, how it differs from just \"not tracking,\" and who it tends to work well for.",
    "general", "For Students", "Intuitive eating explained: is it right for you?",
    "Intuitive eating gets dismissed as \"no rules\" — it's actually a structured framework, and it's not the right fit for every goal.",
    sec('''      <h2>What it actually is</h2>
      <p>Intuitive eating is a framework built around recognizing internal hunger and fullness cues, rejecting a strict "good food/bad food" mentality, and decoupling eating from external rules like meal timing windows or macro targets. It's a defined approach with real structure, not simply "eat whatever, whenever" — as we noted in our <a href="famous-athlete-diets-fact-checked.html">athlete diets piece</a>, Simone Biles has spoken about using this approach deliberately rather than as an absence of a plan.</p>''') +
    sec('''      <h2>Who it tends to work well for</h2>
      <p>It tends to suit people with a history of restrictive dieting or disordered eating patterns, where rigid tracking itself becomes a source of stress, and people whose goal is general health maintenance rather than a specific body-composition target. It's a harder fit for anyone with a precise physique or performance goal (a physique competition prep, a specific strength-to-weight target), where hitting numeric macro targets consistently really does matter more than it does for general health.</p>''', bg="var(--color-protein-bg)", tight=True),
    [("famous-athlete-diets-fact-checked.html", "6 famous athlete diets, fact-checked"), ("iifym-flexible-dieting.html", "IIFYM explained"), ("portion-sizes-without-a-scale.html", "Estimating portions without a scale")]
)

add(
    "electrolytes-explained",
    "Electrolytes: Sodium, Potassium &amp; Magnesium",
    "What electrolytes actually do in the body, the sodium, potassium, and magnesium targets from the American Heart Association, and when you actually need more.",
    "general", "For Students", "Electrolytes explained: sodium, potassium, and magnesium",
    "\"Electrolytes\" gets used as sports-drink marketing shorthand — the actual minerals involved have specific, individual jobs and targets.",
    sec('''      <h2>What each one actually does</h2>
      <p>Sodium regulates fluid balance and blood volume; potassium supports muscle contraction (including your heart) and helps counteract sodium's effect on blood pressure; magnesium is involved in hundreds of enzymatic reactions including energy production and muscle function. Americans on average get far more sodium than recommended and far less potassium and magnesium than recommended — the opposite imbalance of what most electrolyte marketing implies.<sup class="ref"><a href="sources.html#gen9">[2]</a></sup></p>''') +
    sec('''      <h2>The actual daily targets</h2>
      <table class="data-table">
        <tr><th>Electrolyte</th><th>AHA recommendation</th></tr>
        <tr><td>Sodium</td><td>Under 2,300mg/day (ideally under 1,500mg for most adults)</td></tr>
        <tr><td>Potassium</td><td>~4,700mg/day (varies by DRI: 3,400mg men / 2,600mg women)</td></tr>
        <tr><td>Magnesium</td><td>400-420mg (men) / 310-320mg (women)</td></tr>
      </table>
      <p>For most people eating a varied diet, these targets are best met through food — fruits, vegetables, legumes, and dairy — rather than supplements, since most people are already over on sodium and under on the other two.<sup class="ref"><a href="sources.html#gen9">[2]</a></sup></p>''', bg="var(--color-carbs-bg)", tight=True),
    [("sodium-how-much-do-you-need.html", "Sodium: how much do you actually need?"), ("sports-drinks-vs-water.html", "Sports drinks vs. water"), ("dash-diet-explained.html", "The DASH diet explained")]
)

add(
    "sodium-how-much-do-you-need",
    "Sodium: How Much Do You Actually Need?",
    "The real American Heart Association sodium targets, why most people eat far more than recommended, and where most dietary sodium actually comes from.",
    "general", "For Students", "Sodium: how much do you actually need?",
    "Most sodium in the average diet isn't coming from the salt shaker — which is exactly why cutting back is harder than it sounds.",
    sec('''      <h2>The actual target</h2>
      <p>The American Heart Association recommends no more than 2,300mg of sodium per day for most adults, with an ideal limit closer to 1,500mg — yet average intake in the U.S. runs over 3,100mg/day, more than double the ideal target.<sup class="ref"><a href="sources.html#gen8">[1]</a></sup></p>''') +
    sec('''      <h2>Where it actually comes from</h2>
      <p>The majority of dietary sodium comes from processed and restaurant food — bread, deli meat, canned soup, sauces, and packaged snacks — not the salt added at the table. That's why simply not adding extra salt to home-cooked meals often makes a much smaller dent than people expect; reading labels on packaged and restaurant food matters more for most people's actual sodium intake.<sup class="ref"><a href="sources.html#gen8">[1]</a></sup></p>''', bg="var(--color-carbs-bg)", tight=True) +
    sec('''      <p><a href="how-to-read-a-nutrition-label.html" class="btn btn-primary">Learn to read a nutrition label →</a></p>'''),
    [("electrolytes-explained.html", "Electrolytes explained"), ("dash-diet-explained.html", "The DASH diet explained"), ("how-to-read-a-nutrition-label.html", "How to read a nutrition label")]
)

add(
    "added-sugar-vs-natural-sugar",
    "Added Sugar vs. Natural Sugar",
    "Whether added sugar and naturally occurring sugar (like the sugar in fruit) actually behave differently in the body, and why food matrix matters.",
    "carbs", "For Students", "Added sugar vs. natural sugar: does the difference matter?",
    "Chemically, table sugar in a can of soda and the sugar in an apple are extremely similar. Nutritionally, they're not treated the same — for good reason.",
    sec('''      <h2>The actual difference</h2>
      <p>Added sugar (in soda, candy, baked goods) and naturally occurring sugar (in fruit, dairy) can be chemically near-identical — but whole fruit delivers that sugar packaged with fiber, water, and micronutrients that slow digestion and absorption, producing a gentler blood sugar response than the same amount of sugar consumed on its own.<sup class="ref"><a href="sources.html#c1">[1]</a></sup> This is often called the "food matrix" effect — the surrounding food structure changes how a nutrient is absorbed, not just what the nutrient itself is.</p>''') +
    sec('''      <h2>Why nutrition labels separate them</h2>
      <p>U.S. nutrition labels now list "Added Sugars" separately from total sugar. That's because added sugar is the component most directly linked to excess calorie intake and health risk in observational research. Someone eating an orange isn't at meaningful risk of "too much sugar" the way someone drinking several sodas a day is — even though both contain sugar.<sup class="ref"><a href="sources.html#c1">[1]</a></sup></p>''', bg="var(--color-carbs-bg)", tight=True),
    [("sugar-vs-starch.html", "Sugar vs. starch"), ("sugar-addiction-is-it-real.html", "Is sugar addiction real?"), ("how-to-read-a-nutrition-label.html", "How to read a nutrition label")]
)

add(
    "best-breakfast-for-muscle-gain",
    "What's the Best Breakfast for Muscle Gain?",
    "What actually matters in a muscle-building breakfast — protein content and total daily intake — versus what's mostly marketing.",
    "protein", "For Students", "What's the best breakfast for muscle gain?",
    "There's no magic breakfast that builds muscle by itself — but a poorly built one can make hitting your daily protein target considerably harder.",
    sec('''      <h2>What actually matters</h2>
      <p>A good muscle-building breakfast does one main thing: it puts a real dent in your daily protein target. Aim for roughly 25-40g — eggs, Greek yogurt, cottage cheese, or a protein shake. Starting there makes the rest of the day far easier than opening with a protein-light meal like cereal or a plain bagel.<sup class="ref"><a href="sources.html#p2">[1]</a></sup> There's no special muscle-building property to eating specifically in the morning — it's the same principle as any other meal, just easier to underweight if breakfast defaults to mostly carbs.</p>''') +
    sec('''      <h2>A simple template</h2>
      <table class="data-table">
        <tr><th>Component</th><th>Example</th></tr>
        <tr><td>Protein (25-40g)</td><td>3-4 eggs, Greek yogurt, or a protein shake</td></tr>
        <tr><td>Carbs</td><td>Oats, whole grain toast, or fruit</td></tr>
        <tr><td>Fat</td><td>Avocado, nut butter, or the fat naturally in eggs/yogurt</td></tr>
      </table>'''),
    [("high-protein-breakfast-ideas.html", "High-protein breakfast ideas"), ("macros-for-muscle-gain.html", "Macros for muscle gain"), ("bulking-without-gaining-fat.html", "Bulking without gaining excess fat")]
)

add(
    "eating-late-at-night-weight-gain",
    "Does Eating Late at Night Cause Weight Gain?",
    "Whether eating close to bedtime actually causes weight gain independent of total calories, and what the research on meal timing actually shows.",
    "general", "For Students", "Does eating late at night cause weight gain?",
    "\"Don't eat after 8pm\" is repeated constantly. The mechanism behind it is weaker than the rule itself suggests.",
    sec('''      <h2>What the research actually shows</h2>
      <p>When total daily calories are matched, eating later in the day hasn't been shown to independently cause more fat gain than eating the same food earlier — your body doesn't store calories differently after a specific clock time.<sup class="ref"><a href="sources.html#cal2">[1]</a></sup> The real association between late-night eating and weight gain is more indirect: late-night eating is often additional, unplanned eating on top of a day's normal intake (mindless snacking while watching TV), rather than a like-for-like swap.</p>''') +
    sec('''      <h2>Where timing has smaller, real effects</h2>
      <p>Eating very close to bedtime can affect sleep or digestive comfort for some people. And in observational studies, irregular late-night eating patterns do track with worse overall diet quality. Neither of those, though, means late calories are stored differently. Total daily intake is still what predicts weight change.<sup class="ref"><a href="sources.html#cal2">[1]</a></sup></p>''', bg="var(--color-carbs-bg)", tight=True),
    [("meal-frequency-and-metabolism.html", "Meal frequency and metabolism"), ("best-time-to-eat-carbs.html", "Is there a best time to eat carbs?"), ("intermittent-fasting-and-macros.html", "Intermittent fasting and macros")]
)


# --------------------------------------------------------- FINAL BATCH --

add(
    "bcaas-explained",
    "BCAAs Explained: Are They Worth Taking?",
    "What branched-chain amino acids actually do, why isolated BCAA supplements underperform whole protein, and when they might still make sense.",
    "protein", "For Students", "BCAAs explained: are they actually worth taking?",
    "BCAA supplements were huge before people realized whole protein already contains them — and does more.",
    sec('''      <h2>What they actually do</h2>
      <p>BCAAs (leucine, isoleucine, valine) can trigger the molecular signaling that starts muscle protein synthesis, mainly through leucine. But signaling alone isn't enough — building new muscle protein needs a full supply of all 9 essential amino acids as raw material, not just the three BCAAs.<sup class="ref"><a href="sources.html#gen12">[1]</a></sup></p>''') +
    sec('''      <h2>Why whole protein still wins</h2>
      <p>In direct comparisons, 5.6g of isolated BCAAs after resistance training produced roughly half the muscle protein synthesis response of an equivalent dose of complete protein — because the BCAA-only dose runs out of the other essential amino acids needed to keep building. Interestingly, "topping up" a suboptimal whey dose with extra leucine can match a full whey dose's effect, but that's a leucine-boosting strategy, not evidence for BCAAs as a standalone product.<sup class="ref"><a href="sources.html#gen12">[1]</a></sup></p>''', bg="var(--color-protein-bg)", tight=True) +
    sec('''      <p>If you're already hitting your daily protein target from whole food or a complete protein powder, isolated BCAAs add little. They may have a narrow use case for people training fasted or restricting calories heavily, but for most people, the money is better spent on more complete protein.</p>
      <p><a href="protein-powder-101.html" class="btn btn-primary">Read protein powder 101 →</a></p>'''),
    [("protein-powder-101.html", "Protein powder 101"), ("whey-vs-casein-protein.html", "Whey vs. casein protein"), ("how-much-protein-per-day.html", "How much protein do you need per day?")]
)

add(
    "whey-vs-casein-protein",
    "Whey vs. Casein: Which Protein Is Better?",
    "How whey and casein protein actually differ in digestion speed and amino acid profile, and when each one makes more practical sense.",
    "protein", "For Students", "Whey vs. casein protein: what's the real difference?",
    "Both are complete milk proteins — the real difference is digestion speed, not quality.",
    sec('''      <h2>The actual difference</h2>
      <p>Whey and casein are both complete proteins derived from milk, supplying all 9 essential amino acids. The practical difference is digestion speed: whey is absorbed quickly, producing a fast spike in blood amino acids, while casein forms a gel in the stomach and releases amino acids slowly over several hours.<sup class="ref"><a href="sources.html#p2">[1]</a></sup></p>''') +
    sec('''      <h2>When each makes more sense</h2>
      <p>Whey's fast absorption fits post-workout or any time you want protein quickly. Casein's slow release fits before a long gap without food — before bed being the most common use case, to keep amino acids available overnight. Neither is inherently superior for muscle building; given our earlier point on the <a href="post-workout-anabolic-window.html">post-workout anabolic window</a>, total daily protein intake matters far more than which type you use when.</p>''', bg="var(--color-protein-bg)", tight=True),
    [("bcaas-explained.html", "BCAAs explained"), ("protein-powder-101.html", "Protein powder 101"), ("protein-timing.html", "Does protein timing matter?")]
)

add(
    "fasted-cardio-fat-loss",
    "Does Fasted Cardio Actually Burn More Fat?",
    "What controlled research finds when comparing fasted vs. fed cardio for fat loss, and why acute fat-burning differences don't translate to better long-term results.",
    "general", "For Students", "Does fasted cardio actually burn more fat?",
    "Fasted cardio does burn a higher percentage of fat during the session itself. That doesn't mean it burns more fat overall.",
    sec('''      <h2>What happens during the session</h2>
      <p>Exercising in a fasted state does shift your body toward burning a higher proportion of fat for fuel during that session — one study found fat oxidation increased by roughly 73% during fasted cycling compared to the same session fed.</p>''') +
    sec('''      <h2>Why it doesn't add up to more fat loss</h2>
      <p>Despite that acute difference, controlled trials comparing fasted and fed cardio with matched total calories and protein find no significant difference in fat loss over time — in one 4-week trial, both groups lost the same amount of body fat.<sup class="ref"><a href="sources.html#gen11">[1]</a></sup> The body appears to compensate over the full day: burning more fat in one session doesn't change your total calorie balance, which is what actually determines fat loss over weeks.</p>''', bg="var(--color-fat-bg)", tight=True) +
    sec('''      <p>Fasted cardio is a fine choice if it fits your schedule or preference — it's just not a fat-loss advantage on its own.</p>'''),
    [("intermittent-fasting-and-macros.html", "Intermittent fasting and macros"), ("macros-for-weight-loss.html", "Macros for fat loss"), ("meal-frequency-and-metabolism.html", "Meal frequency and metabolism")]
)

add(
    "egg-yolks-cholesterol-myth",
    "Are Egg Yolks Bad for Your Cholesterol?",
    "What Harvard's long-term research actually found about egg consumption and heart disease risk, and why dietary cholesterol matters less than saturated fat.",
    "fat", "For Students", "Are egg yolks bad for your cholesterol?",
    "Eggs spent decades as a cholesterol villain. Large long-term studies tell a more forgiving story for most people.",
    sec('''      <h2>What the research actually found</h2>
      <p>Large, long-term Harvard cohort studies found no significant overall association between egg consumption and risk of coronary heart disease or stroke in the general population, with up to about 7 eggs per week considered compatible with a healthy diet for most people.<sup class="ref"><a href="sources.html#gen10">[1]</a></sup></p>''') +
    sec('''      <h2>Why dietary cholesterol matters less than expected</h2>
      <p>Most blood cholesterol is produced by your liver, and the liver is stimulated to make more cholesterol primarily by dietary saturated and trans fat — not the cholesterol in food itself. Eggs are relatively low in saturated fat and contain no trans fat, which is a large part of why egg intake doesn't move blood cholesterol as much as it was long assumed to. One notable exception: some research links higher egg intake with increased cardiovascular risk specifically in men with diabetes, so individual risk factors still matter.<sup class="ref"><a href="sources.html#gen10">[1]</a></sup></p>''', bg="var(--color-fat-bg)", tight=True),
    [("cholesterol-explained.html", "Cholesterol explained"), ("saturated-vs-unsaturated-fat.html", "Saturated vs. unsaturated fat"), ("high-protein-breakfast-ideas.html", "High-protein breakfast ideas")]
)

add(
    "metabolic-damage-is-it-real",
    "Is \"Metabolic Damage\" From Dieting Real?",
    "What actually happens to metabolism during prolonged dieting, whether it can be permanently \"damaged,\" and what the research on adaptive thermogenesis shows.",
    "general", "For Students", "Is \"metabolic damage\" from dieting real?",
    "\"My metabolism is broken from dieting\" is common online. The real phenomenon behind it is real, but far less permanent than the phrase implies.",
    sec('''      <h2>What actually happens</h2>
      <p>Extended dieting does reduce metabolic rate below what body weight alone would predict — a real, measured phenomenon called adaptive thermogenesis, partly from losing body mass (which burns calories) and partly from hormonal and neurological adaptations that increase energy efficiency during a prolonged deficit.<sup class="ref"><a href="sources.html#cal2">[1]</a></sup></p>''') +
    sec('''      <h2>Why "damaged" is the wrong word</h2>
      <p>This adaptation is a normal, reversible survival response, not permanent damage to your metabolism — most of the drop recovers over weeks to months once calorie intake returns to maintenance, especially alongside resistance training to rebuild any lost muscle. What actually helps: reverse dieting (raising calories gradually rather than all at once) and prioritizing protein and strength training through and after a diet phase to preserve muscle mass, which is the biggest driver of metabolic rate you actually control.</p>''', bg="var(--color-carbs-bg)", tight=True),
    [("tdee-vs-bmr.html", "BMR vs. TDEE"), ("cutting-bulking-maintenance-explained.html", "Cutting, bulking, and maintenance"), ("macros-for-weight-loss.html", "Macros for fat loss")]
)

add(
    "refeed-days-explained",
    "Refeed Days: Do They Actually Help?",
    "What a refeed day actually does physiologically during a calorie deficit, and how it differs from an unplanned cheat day.",
    "general", "For Students", "Refeed days explained: do they actually help a diet?",
    "A refeed day is a deliberate, planned tool — not just a nicer name for a cheat day.",
    sec('''      <h2>What a refeed actually does</h2>
      <p>A refeed day means deliberately raising calories — usually via carbohydrate — back up to roughly maintenance for a day or two during an extended deficit. This partially restores depleted glycogen stores, can modestly and temporarily support hormones affected by sustained dieting (like leptin), and gives a mental break from restriction.<sup class="ref"><a href="sources.html#cal2">[1]</a></sup></p>''') +
    sec('''      <h2>How it differs from a cheat day</h2>
      <p>Unlike an unplanned <a href="cheat-days-do-they-help-or-hurt.html">cheat day</a>, a refeed is calculated — raising calories to a specific target (often via carbs specifically, keeping protein and fat closer to normal) rather than eating without a plan. It's most useful for people in a long, aggressive deficit (physique competitors, extended cuts) rather than someone in a short, moderate deficit, where the physiological benefit is smaller relative to the risk of it turning into an unplanned surplus.</p>''', bg="var(--color-carbs-bg)", tight=True),
    [("cheat-days-do-they-help-or-hurt.html", "Cheat days: do they help or hurt?"), ("metabolic-damage-is-it-real.html", "Is metabolic damage real?"), ("macros-for-weight-loss.html", "Macros for fat loss")]
)

add(
    "zone-diet-explained",
    "The Zone Diet Explained: The 40/30/30 Approach",
    "What the Zone diet's fixed 40/30/30 macro split actually means, where it came from, and what the evidence says about a fixed ratio approach.",
    "diets", "Diets", "The Zone diet explained: the 40/30/30 approach",
    "The Zone diet popularized something novel for its time: a fixed macro percentage instead of a food list.",
    sec('''      <h2>What it actually is</h2>
      <p>The Zone diet targets a fixed 40% of calories from carbohydrate, 30% from protein, and 30% from fat at every meal, developed in the 1990s around the idea of controlling insulin response and inflammation through consistent macro ratios rather than a food-inclusion/exclusion list the way paleo or keto work.</p>''') +
    sec('''      <h2>What the evidence says</h2>
      <p>The specific 40/30/30 ratio itself hasn't been shown to be uniquely superior to other reasonable macro splits for fat loss or health when calories and protein are held constant — its real contribution was popularizing macro-percentage thinking rather than a magic ratio.<sup class="ref"><a href="sources.html#cal2">[1]</a></sup> A moderate-carb, higher-protein split like this is a perfectly reasonable target — it's just not meaningfully better than a well-calculated target based on your own numbers.</p>''', bg="var(--color-pop3-bg)", tight=True) +
    sec('''      <p><a href="calculators.html" class="btn btn-primary">Calculate your own macro split →</a></p>'''),
    [("diets-explained.html", "Diets explained: every major pattern"), ("iifym-flexible-dieting.html", "IIFYM explained"), ("how-to-calculate-macros-by-hand.html", "How to calculate macros by hand")]
)

add(
    "body-types-somatotypes-macros",
    "Do Body Types Determine Your Macros?",
    "Where the ectomorph/mesomorph/endomorph body type system actually came from, why it isn't a validated way to set macros, and what actually should drive your targets.",
    "general", "For Students", "Do body types actually determine your macros?",
    "\"Ectomorph,\" \"mesomorph,\" and \"endomorph\" get treated as science-backed categories for setting macros. The original research behind them was never about diet at all.",
    sec('''      <h2>Where the idea actually came from</h2>
      <p>The somatotype system was developed in the 1940s by psychologist William Sheldon, who used it to try to correlate body shape with personality and temperament — a theory that has since been discredited as pseudoscience. It was never a validated framework for nutrition or exercise prescription; fitness culture adopted the three body-type labels decades later and retrofitted diet advice onto them.</p>''') +
    sec('''      <h2>What actually should set your macros</h2>
      <p>Your protein, fat, and carb targets should come from your actual body weight, activity level, and goal — not a body-shape label. Someone who identifies as an "ectomorph" and someone who identifies as an "endomorph" at the same weight, activity level, and goal need essentially the same macro targets; individual differences in metabolism and training response are real, but they're not reliably predicted by a 1940s personality typology.<sup class="ref"><a href="sources.html#cal2">[1]</a></sup></p>''', bg="var(--color-carbs-bg)", tight=True) +
    sec('''      <p><a href="calculators.html" class="btn btn-primary">Calculate your macros from your actual numbers →</a></p>'''),
    [("how-to-calculate-macros-by-hand.html", "How to calculate macros by hand"), ("common-nutrition-myths-debunked.html", "Common nutrition myths debunked"), ("macros-for-muscle-gain.html", "Macros for muscle gain")]
)


# ------------------------------------- MICRONUTRIENTS & SUPPLEMENTS BATCH --

add(
    "vitamin-d-explained",
    "Vitamin D: How Much You Need and Why",
    "What vitamin D does, how much you need per day, why deficiency is so common, and which foods and sources actually raise your levels.",
    "general", "Micronutrients", "Vitamin D: how much you need and why",
    "Vitamin D behaves more like a hormone than a typical vitamin, and it's one of the few nutrients most people genuinely struggle to get enough of.",
    sec('''      <h2>What it does</h2>
      <p>Vitamin D's best-known job is helping your gut absorb calcium — without enough of it, you can eat plenty of calcium and still absorb only a fraction of it. It also supports bone mineralization, normal muscle function, and immune signalling. Severe, prolonged deficiency causes rickets in children and osteomalacia (soft bones) in adults.<sup class="ref"><a href="sources.html#mic1">[1]</a></sup></p>
      <h2>How much you need</h2>
      <table class="data-table">
        <tr><th>Group</th><th>RDA</th><th>Upper limit</th></tr>
        <tr><td>Adults 19–70</td><td>600 IU (15 mcg)</td><td>4,000 IU (100 mcg)</td></tr>
        <tr><td>Adults 71+</td><td>800 IU (20 mcg)</td><td>4,000 IU (100 mcg)</td></tr>
      </table>
      <p>These are the U.S. Dietary Reference Intake values, set assuming minimal sun exposure.<sup class="ref"><a href="sources.html#mic1">[1]</a></sup></p>''') +
    sec('''      <h2>Why deficiency is common</h2>
      <p>Very few foods naturally contain meaningful vitamin D. The reliable ones are fatty fish (salmon, mackerel, sardines), cod liver oil, egg yolks in smaller amounts, and fortified foods — most notably milk and some cereals and plant milks. Your skin also makes vitamin D from UVB sunlight, but that production drops sharply with higher latitude, winter months, darker skin pigmentation, sunscreen use, and time spent indoors.<sup class="ref"><a href="sources.html#mic1">[1]</a></sup></p>
      <div class="panel">
        <h3>Worth knowing</h3>
        <p>Vitamin D is fat-soluble, so it's stored in body tissue rather than flushed out daily. That's exactly why the upper limit matters — unlike water-soluble vitamins, it's genuinely possible to take too much over time.</p>
      </div>''', bg="var(--color-fat-bg)", tight=True) +
    sec('''      <p>Because it's fat-soluble, vitamin D is absorbed better when eaten alongside a meal containing some fat. See our guide to <a href="fat-soluble-vitamins-explained.html">fat-soluble vitamins</a> for the full picture.</p>'''),
    [("fat-soluble-vitamins-explained.html", "Fat-soluble vitamins explained"), ("calcium-and-bone-health.html", "Calcium and bone health"), ("healthy-high-fat-foods.html", "Healthy high-fat foods")]
)

add(
    "iron-deficiency-and-athletes",
    "Iron Deficiency in Athletes: Signs and Fixes",
    "Why endurance athletes and menstruating women are at higher risk of low iron, what the symptoms look like, and how heme and non-heme iron differ.",
    "athletes", "Sports Nutrition", "Iron deficiency in athletes: signs and fixes",
    "Iron deficiency is the most common nutrient deficiency worldwide, and athletes — especially female endurance athletes — sit squarely in the highest-risk group.",
    sec('''      <h2>Why iron matters for performance</h2>
      <p>Iron is the core of hemoglobin, the protein that carries oxygen in your blood, and of myoglobin, which stores oxygen in muscle. Low iron means less oxygen delivered per heartbeat, which shows up directly as fatigue, breathlessness, and a drop in endurance capacity long before it becomes clinical anemia.<sup class="ref"><a href="sources.html#mic2">[1]</a></sup></p>
      <h2>How much you need</h2>
      <table class="data-table">
        <tr><th>Group</th><th>RDA</th></tr>
        <tr><td>Men 19+</td><td>8 mg/day</td></tr>
        <tr><td>Women 19–50</td><td>18 mg/day</td></tr>
        <tr><td>Women 51+</td><td>8 mg/day</td></tr>
        <tr><td>Pregnancy</td><td>27 mg/day</td></tr>
      </table>
      <p>Menstruation is the main reason the requirement for women aged 19–50 is more than double that of men.<sup class="ref"><a href="sources.html#mic2">[1]</a></sup></p>''') +
    sec('''      <h2>Heme vs. non-heme iron</h2>
      <p>Iron comes in two forms, and they are not absorbed equally:</p>
      <ul class="checklist">
        <li><strong>Heme iron</strong> — found in meat, poultry, and fish. Absorbed far more efficiently and less affected by other things in the meal.</li>
        <li><strong>Non-heme iron</strong> — found in plants, eggs, and fortified foods. Absorbed less efficiently, and inhibited by tea, coffee, and phytates in whole grains and legumes.</li>
      </ul>
      <p>Vitamin C markedly improves non-heme absorption, which is why pairing plant iron sources with citrus, peppers, or tomatoes is a useful habit — and why <a href="vegan-macros-guide.html">vegan</a> and <a href="macros-for-vegetarians.html">vegetarian</a> athletes need to plan iron more deliberately.<sup class="ref"><a href="sources.html#mic2">[1]</a></sup></p>''', bg="var(--color-pop2-bg)", tight=True) +
    sec('''      <div class="panel warn">
        <h3>Don't self-supplement blindly</h3>
        <p>Iron is one of the few nutrients where excess is genuinely harmful, and the symptoms of low iron overlap with plenty of other causes. Low iron should be confirmed with a blood test (ferritin plus a full blood count) before supplementing, not guessed at.</p>
      </div>'''),
    [("plant-based-protein-sources.html", "Plant-based protein sources"), ("macros-for-endurance-vs-strength-athletes.html", "Endurance vs. strength macros"), ("protein-intake-for-women.html", "Protein intake for women")]
)

add(
    "magnesium-explained",
    "Magnesium: What It Does and Where to Get It",
    "What magnesium does in the body, how much you need per day, the best food sources, and whether supplementing actually helps most people.",
    "general", "Micronutrients", "Magnesium: what it does and where to get it",
    "Magnesium is involved in hundreds of enzyme reactions, and intakes below the recommended amount are common — but that's not the same as deficiency.",
    sec('''      <h2>What it does</h2>
      <p>Magnesium acts as a cofactor in more than 300 enzyme systems, including those governing protein synthesis, muscle and nerve function, blood glucose control, and blood pressure regulation. It's also required for the production and use of ATP, your cells' immediate energy currency.<sup class="ref"><a href="sources.html#mic3">[1]</a></sup></p>
      <h2>How much you need</h2>
      <table class="data-table">
        <tr><th>Group</th><th>RDA</th></tr>
        <tr><td>Men 19–30</td><td>400 mg/day</td></tr>
        <tr><td>Men 31+</td><td>420 mg/day</td></tr>
        <tr><td>Women 19–30</td><td>310 mg/day</td></tr>
        <tr><td>Women 31+</td><td>320 mg/day</td></tr>
      </table>''') +
    sec('''      <h2>Where to get it</h2>
      <p>Magnesium is concentrated in plant foods built around chlorophyll and in seeds: pumpkin seeds, chia seeds, almonds, cashews, spinach, black beans, edamame, peanut butter, and whole grains are all strong sources. Refining grains strips most of the magnesium out, which is a large part of why intakes fall short on heavily processed diets.<sup class="ref"><a href="sources.html#mic3">[1]</a></sup></p>
      <div class="panel">
        <h3>Low intake vs. real deficiency</h3>
        <p>Many people eat less than the RDA, but genuine symptomatic magnesium deficiency is uncommon in otherwise healthy people, because the kidneys limit how much is excreted when intake is low. Persistently low intake is still worth correcting — ideally through food first.<sup class="ref"><a href="sources.html#mic3">[1]</a></sup></p>
      </div>''', bg="var(--color-carbs-bg)", tight=True),
    [("electrolytes-explained.html", "Electrolytes explained"), ("high-fiber-foods-list.html", "High-fiber foods list"), ("micronutrients-vs-macronutrients.html", "Micronutrients vs. macronutrients")]
)

add(
    "vitamin-b12-and-vegan-diets",
    "Vitamin B12 on a Vegan Diet: What to Know",
    "Why vitamin B12 is the one nutrient vegans genuinely cannot get from unfortified plant foods, and how to cover it reliably.",
    "diets", "Diets", "Vitamin B12 on a vegan diet: what to know",
    "Most nutrition debates have two reasonable sides. B12 on a fully plant-based diet isn't one of them — this one has a clear answer.",
    sec('''      <h2>Why B12 is different</h2>
      <p>Vitamin B12 is required to make red blood cells, synthesize DNA, and maintain the myelin sheath around nerves. Deficiency causes megaloblastic anemia and, if prolonged, nerve damage that can become permanent.<sup class="ref"><a href="sources.html#mic4">[1]</a></sup></p>
      <p>The catch is where it comes from. B12 is produced by bacteria, not by plants or animals — animals accumulate it through their own gut bacteria and their food. That means no unfortified plant food is a reliable B12 source. Not spirulina, not nutritional yeast unless it's explicitly fortified, not fermented soy.<sup class="ref"><a href="sources.html#mic4">[1]</a></sup></p>
      <h2>How much you need</h2>
      <p>The adult RDA is <strong>2.4 mcg/day</strong>, rising to 2.6 mcg in pregnancy and 2.8 mcg while breastfeeding.<sup class="ref"><a href="sources.html#mic4">[1]</a></sup></p>''') +
    sec('''      <h2>How vegans should cover it</h2>
      <ul class="checklist">
        <li><strong>Fortified foods</strong> — many plant milks, breakfast cereals, and nutritional yeast products are fortified. Check the label; fortification is not universal.</li>
        <li><strong>A B12 supplement</strong> — the simplest and most reliable route, and widely recommended for anyone eating fully plant-based.</li>
        <li><strong>Don't rely on stores</strong> — the liver can hold years' worth of B12, which is exactly why deficiency creeps up slowly and is often missed until symptoms appear.</li>
      </ul>
      <p>Vegetarians who eat dairy and eggs are in a much easier position, since both contain B12 — see our <a href="macros-for-vegetarians.html">vegetarian macros guide</a>.</p>''', bg="var(--color-pop3-bg)", tight=True),
    [("vegan-macros-guide.html", "Vegan macros guide"), ("plant-based-vs-vegan-diet.html", "Plant-based vs. vegan"), ("plant-based-protein-sources.html", "Plant-based protein sources")]
)

add(
    "calcium-and-bone-health",
    "Calcium and Bone Health: How Much You Need",
    "How much calcium you need at each age, the best dietary sources, and why calcium without vitamin D and resistance training does less than you'd think.",
    "general", "Micronutrients", "Calcium and bone health: how much you need",
    "Bone isn't inert scaffolding — it's living tissue that's constantly broken down and rebuilt, and calcium is the raw material for the rebuilding half.",
    sec('''      <h2>How much you need</h2>
      <table class="data-table">
        <tr><th>Group</th><th>RDA</th></tr>
        <tr><td>Adults 19–50</td><td>1,000 mg/day</td></tr>
        <tr><td>Women 51–70</td><td>1,200 mg/day</td></tr>
        <tr><td>Adults 71+</td><td>1,200 mg/day</td></tr>
      </table>
      <p>Requirements rise later in life because absorption efficiency falls and, after menopause, bone loss accelerates.<sup class="ref"><a href="sources.html#mic5">[1]</a></sup></p>
      <h2>Where to get it</h2>
      <p>Dairy is the most concentrated common source, but it's far from the only one: canned sardines and salmon (with the bones), tofu set with calcium salts, fortified plant milks, kale, bok choy, and broccoli all contribute meaningfully. Spinach contains calcium but binds much of it in oxalates, making it poorly absorbed — a good example of why the number on a label isn't the whole story.<sup class="ref"><a href="sources.html#mic5">[1]</a></sup></p>''') +
    sec('''      <div class="panel">
        <h3>Calcium doesn't work alone</h3>
        <p>Absorbing calcium depends on adequate <a href="vitamin-d-explained.html">vitamin D</a>, and the signal that tells your body to deposit calcium into bone is mechanical loading — resistance training and weight-bearing activity. Calcium intake alone, without those two, is the least effective version of a bone-health strategy.<sup class="ref"><a href="sources.html#mic1">[2]</a></sup></p>
      </div>''', bg="var(--color-carbs-bg)", tight=True),
    [("vitamin-d-explained.html", "Vitamin D explained"), ("micronutrients-vs-macronutrients.html", "Micronutrients vs. macronutrients"), ("protein-intake-for-women.html", "Protein intake for women")]
)

add(
    "fat-soluble-vitamins-explained",
    "Fat-Soluble Vitamins: A, D, E and K",
    "How vitamins A, D, E, and K differ from water-soluble vitamins, why they need dietary fat to absorb, and why upper limits matter more for them.",
    "fat", "Fat Guide", "Fat-soluble vitamins: A, D, E and K",
    "Four vitamins dissolve in fat rather than water — and that single property changes how you absorb them, how you store them, and how easy they are to overdo.",
    sec('''      <h2>The four, and what they do</h2>
      <table class="data-table">
        <tr><th>Vitamin</th><th>Main roles</th><th>Good sources</th></tr>
        <tr><td>A</td><td>Vision, immune function, cell growth</td><td>Liver, eggs, dairy; beta-carotene in orange and dark green vegetables</td></tr>
        <tr><td>D</td><td>Calcium absorption, bone and muscle function</td><td>Fatty fish, fortified milk, sunlight exposure</td></tr>
        <tr><td>E</td><td>Antioxidant protecting cell membranes</td><td>Nuts, seeds, vegetable oils</td></tr>
        <tr><td>K</td><td>Blood clotting, bone metabolism</td><td>Leafy greens, some fermented foods</td></tr>
      </table>''') +
    sec('''      <h2>Why "fat-soluble" actually matters</h2>
      <p>Two practical consequences follow from dissolving in fat rather than water:</p>
      <ul class="checklist">
        <li><strong>You need dietary fat to absorb them.</strong> Eating a carrot with no fat at all means absorbing much less of its beta-carotene. This is one of the concrete downsides of very low-fat diets.<sup class="ref"><a href="sources.html#mic6">[1]</a></sup></li>
        <li><strong>Excess is stored, not excreted.</strong> Water-soluble vitamins are largely flushed out in urine when you overshoot. Fat-soluble ones accumulate in the liver and fat tissue, so high-dose supplementation — particularly vitamin A — can build to toxic levels over time.<sup class="ref"><a href="sources.html#mic6">[1]</a></sup></li>
      </ul>
      <div class="panel warn">
        <h3>Preformed vitamin A vs. beta-carotene</h3>
        <p>These aren't interchangeable in terms of risk. Preformed vitamin A (retinol, from animal foods and supplements) can reach toxic levels. Beta-carotene from plants is converted as needed and doesn't carry the same toxicity risk.<sup class="ref"><a href="sources.html#mic6">[1]</a></sup></p>
      </div>''', bg="var(--color-fat-bg)", tight=True),
    [("vitamin-d-explained.html", "Vitamin D explained"), ("low-fat-diet-risks.html", "Risks of very low-fat diets"), ("healthy-high-fat-foods.html", "Healthy high-fat foods")]
)

add(
    "caffeine-and-athletic-performance",
    "Caffeine and Athletic Performance: The Evidence",
    "How much caffeine actually improves performance, when to take it, who responds least, and where the evidence is strongest.",
    "athletes", "Sports Nutrition", "Caffeine and athletic performance: the evidence",
    "Caffeine is one of the very few supplements with genuinely strong, consistent evidence behind it — and one of the easiest to get wrong by overdoing.",
    sec('''      <h2>How much, and when</h2>
      <p>The International Society of Sports Nutrition's position stand concludes that caffeine improves performance across endurance, high-intensity, and strength-based activities at doses of roughly <strong>3–6 mg per kg of body weight</strong>, taken about 60 minutes before exercise. For a 70 kg athlete that's around 210–420 mg — roughly two to four cups of coffee.<sup class="ref"><a href="sources.html#mic7">[1]</a></sup></p>
      <p>Higher doses (9 mg/kg and above) do not reliably improve performance further, and markedly increase side effects: jitteriness, elevated heart rate, GI upset, and disrupted sleep.<sup class="ref"><a href="sources.html#mic7">[1]</a></sup></p>''') +
    sec('''      <h2>What it actually does</h2>
      <p>The main mechanism isn't extra energy — caffeine has no calories. It blocks adenosine receptors in the brain, which reduces your perception of effort and fatigue, so a given workload feels easier. That's why the effect shows up most clearly in endurance events and in sustained high-intensity work.<sup class="ref"><a href="sources.html#mic7">[1]</a></sup></p>
      <div class="panel">
        <h3>Individual response varies a lot</h3>
        <p>Genetic differences in caffeine metabolism, plus habitual intake, mean the same dose affects people very differently. Response is worth testing in training rather than on competition day.<sup class="ref"><a href="sources.html#mic7">[1]</a></sup></p>
      </div>
      <p>Caffeine's effect on sleep is the most common way athletes undermine themselves with it — and sleep loss degrades recovery and performance more than the caffeine helped.</p>''', bg="var(--color-pop2-bg)", tight=True),
    [("creatine-explained.html", "Creatine explained"), ("sports-drinks-vs-water.html", "Sports drinks vs. water"), ("carb-loading-for-athletes.html", "Carb loading for athletes")]
)

add(
    "collagen-supplements-explained",
    "Do Collagen Supplements Actually Work?",
    "What collagen supplements are, what happens to them during digestion, and how strong the evidence really is for skin and joint claims.",
    "protein", "Protein Guide", "Do collagen supplements actually work?",
    "Collagen is the most abundant protein in your body. Whether swallowing more of it does what the marketing promises is a separate question.",
    sec('''      <h2>What happens when you eat it</h2>
      <p>Collagen supplements are usually hydrolyzed collagen — collagen broken into shorter peptides. Like any protein, it's digested into amino acids and short peptides before absorption. Your body does not route ingested collagen preferentially to your skin or joints; those amino acids enter the same general pool every other protein feeds.</p>
      <p>Collagen is also an incomplete protein: it's very low in tryptophan and not well balanced in essential amino acids, which makes it a poor choice as a primary protein source compared to <a href="whey-vs-casein-protein.html">whey or casein</a>.<sup class="ref"><a href="sources.html#p1">[1]</a></sup></p>''') +
    sec('''      <h2>What the evidence supports</h2>
      <ul class="checklist">
        <li><strong>Joint discomfort</strong> — some trials report modest improvements in activity-related joint pain, though study sizes are small and industry funding is common.<sup class="ref"><a href="sources.html#mic12">[2]</a></sup></li>
        <li><strong>Skin elasticity</strong> — several trials report small improvements, again mostly small and often manufacturer-funded.</li>
        <li><strong>Muscle building</strong> — not supported. For muscle protein synthesis, a complete protein with adequate leucine outperforms collagen clearly.<sup class="ref"><a href="sources.html#p2">[3]</a></sup></li>
      </ul>
      <div class="panel warn">
        <h3>The honest summary</h3>
        <p>Collagen is not useless, but it's nowhere near as well-supported as creatine or caffeine. If your total protein intake is already adequate, collagen is a low-priority addition — and if it isn't adequate, a complete protein source is the better fix.</p>
      </div>''', bg="var(--color-protein-bg)", tight=True),
    [("protein-powder-101.html", "Protein powder 101"), ("creatine-explained.html", "Creatine explained"), ("complete-vs-incomplete-protein.html", "Complete vs. incomplete protein")]
)

add(
    "soy-and-testosterone",
    "Does Soy Lower Testosterone? What Research Says",
    "Where the soy and testosterone myth came from, what meta-analyses of clinical trials actually found, and what soy does offer nutritionally.",
    "protein", "Protein Guide", "Does soy lower testosterone?",
    "Few nutrition claims have been tested as directly as this one — and few myths have survived the results as stubbornly.",
    sec('''      <h2>Where the claim came from</h2>
      <p>Soy contains isoflavones, plant compounds classed as phytoestrogens because they can bind weakly to estrogen receptors. The reasoning went: estrogen-like compound in, testosterone down. A handful of widely-shared case reports involving extreme intakes added fuel.</p>
      <h2>What the research found</h2>
      <p>An expanded meta-analysis pooling clinical studies in men found that neither soy protein nor isoflavone intake significantly altered testosterone, free testosterone, or estradiol levels.<sup class="ref"><a href="sources.html#mic9">[1]</a></sup> Phytoestrogens bind estrogen receptors far more weakly than human estrogen does, and the binding is selective — the effect simply isn't equivalent.</p>''') +
    sec('''      <h2>What soy actually offers</h2>
      <ul class="checklist">
        <li><strong>A complete protein</strong> — soy is one of the few plant foods supplying all nine essential amino acids in useful amounts, which is why it scores well on <a href="protein-quality-scores-pdcaas-diaas.html">PDCAAS and DIAAS</a>.<sup class="ref"><a href="sources.html#p1">[2]</a></sup></li>
        <li><strong>Useful for plant-based diets</strong> — tofu, tempeh, edamame, and soy milk are among the most efficient protein sources available to <a href="vegan-macros-guide.html">vegans</a>.</li>
        <li><strong>Calcium, when set with calcium salts</strong> — check the label on tofu; it varies by brand.</li>
      </ul>
      <p>As with any food, the sensible caveat is dose and variety: soy as one protein source among several is well-supported. Extremely high intakes of any single food are a different question, and one nobody has strong data on.</p>''', bg="var(--color-protein-bg)", tight=True),
    [("plant-based-protein-sources.html", "Plant-based protein sources"), ("common-nutrition-myths-debunked.html", "Common nutrition myths"), ("complete-vs-incomplete-protein.html", "Complete vs. incomplete protein")]
)

add(
    "protein-before-bed",
    "Protein Before Bed: Does It Help Muscle Growth?",
    "What happens to muscle protein synthesis overnight, what pre-sleep protein research found, and whether it matters if your daily total is already met.",
    "protein", "Protein Guide", "Protein before bed: does it help muscle growth?",
    "You spend roughly a third of your life in an overnight fast. That window turns out to be more interesting than it sounds.",
    sec('''      <h2>The overnight problem</h2>
      <p>Muscle protein synthesis needs amino acids available in the bloodstream. During a normal 7–9 hour sleep, no protein is coming in, so rates of synthesis decline over the course of the night while breakdown continues. The question researchers asked was simple: does adding protein right before sleep change that?</p>
      <h2>What the research found</h2>
      <p>In a controlled trial, participants who consumed roughly 40 g of casein protein before sleep after an evening resistance training session showed improved whole-body protein balance and higher overnight muscle protein synthesis rates than those given a placebo.<sup class="ref"><a href="sources.html#mic10">[1]</a></sup> Casein is the usual choice because it digests slowly, releasing amino acids gradually across several hours.</p>''') +
    sec('''      <h2>How much this actually matters</h2>
      <p>The effect is real but should be kept in proportion. Pre-sleep protein is best understood as <em>a convenient way to hit your daily total and spread intake evenly</em>, not a separate magic window. If you're already eating 1.6–2.2 g/kg spread across the day, adding a night-time serving on top adds much less than the headline suggests.<sup class="ref"><a href="sources.html#p2">[2]</a></sup></p>
      <div class="panel">
        <h3>Practical version</h3>
        <p>If you struggle to reach your protein target, moving a serving to before bed is a useful place to put it. Good options: cottage cheese, Greek yogurt, milk, or a casein shake — all slow-digesting. See <a href="whey-vs-casein-protein.html">whey vs. casein</a> for the difference.</p>
      </div>''', bg="var(--color-protein-bg)", tight=True),
    [("whey-vs-casein-protein.html", "Whey vs. casein protein"), ("protein-timing.html", "Does protein timing matter?"), ("protein-for-muscle-growth.html", "Protein for muscle growth")]
)

add(
    "seed-oils-explained",
    "Are Seed Oils Bad for You? The Evidence",
    "What seed oils are, why linoleic acid became controversial, and what controlled trials and major reviews actually conclude about replacing saturated fat.",
    "fat", "Fat Guide", "Are seed oils bad for you?",
    "Few foods have swung from health-recommended to internet-villain as fast as seed oils. The underlying evidence has moved much less than the discourse.",
    sec('''      <h2>What they are</h2>
      <p>"Seed oils" usually refers to soybean, canola (rapeseed), sunflower, safflower, corn, cottonseed, grapeseed, and rice bran oil. What they share is being high in polyunsaturated fat, particularly the omega-6 fatty acid <strong>linoleic acid</strong>.</p>
      <h2>The argument against them</h2>
      <p>The common claim runs: omega-6 fats are pro-inflammatory, modern diets contain far more omega-6 than our ancestors ate, therefore seed oils drive chronic disease. The <a href="omega-3-vs-omega-6.html">omega-6 to omega-3 ratio</a> has genuinely shifted in modern diets — that part is accurate.</p>''') +
    sec('''      <h2>What the evidence actually shows</h2>
      <p>The American Heart Association's presidential advisory reviewed the randomized controlled trials and pooled analyses and concluded that <strong>replacing saturated fat with polyunsaturated vegetable oil lowers cardiovascular disease risk</strong> — by about 30% in the pooled trial data, an effect comparable to statin treatment.<sup class="ref"><a href="sources.html#mic11">[1]</a></sup></p>
      <p>The proposed inflammation mechanism has also not held up well: controlled feeding trials increasing linoleic acid intake have generally not shown corresponding increases in inflammatory markers in humans.<sup class="ref"><a href="sources.html#mic11">[1]</a></sup></p>
      <div class="panel">
        <h3>The reasonable middle</h3>
        <p>A fair reading is that seed oils are not the problem — but the foods they most often arrive in might be. Most seed oil in a typical diet comes packaged inside fried and ultra-processed food, and that association is easy to mistake for causation by the oil itself. Getting more <a href="omega-3-foods-list.html">omega-3</a> is better supported than fearing omega-6.</p>
      </div>''', bg="var(--color-fat-bg)", tight=True),
    [("omega-3-vs-omega-6.html", "Omega-3 vs omega-6"), ("saturated-vs-unsaturated-fat.html", "Saturated vs. unsaturated fat"), ("common-nutrition-myths-debunked.html", "Common nutrition myths")]
)

add(
    "artificial-sweeteners-explained",
    "Artificial Sweeteners: What the Evidence Says",
    "How non-sugar sweeteners work, what the WHO's 2023 guideline concluded about using them for weight control, and how to read the evidence sensibly.",
    "carbs", "Carbohydrate Guide", "Artificial sweeteners: what the evidence says",
    "Sweeteners let you have the taste of sugar without the calories. Whether that translates into better health outcomes is a more complicated story.",
    sec('''      <h2>What they are</h2>
      <p>Non-sugar sweeteners include aspartame, sucralose, saccharin, acesulfame-K, stevia, and monk fruit extract. They're intensely sweet — often hundreds of times sweeter than sucrose — so the quantity used contributes negligible calories and, in most cases, no meaningful effect on blood glucose. That makes them useful in principle for people managing <a href="glycemic-index-explained.html">blood sugar</a> or total calories.</p>''') +
    sec('''      <h2>What the WHO concluded</h2>
      <p>In 2023 the World Health Organization issued a conditional recommendation <strong>against using non-sugar sweeteners as a means of achieving weight control or reducing the risk of noncommunicable diseases</strong>. The reasoning: while short-term trials show modest weight reduction, longer-term observational data did not show sustained benefit, and suggested possible associations with type 2 diabetes and cardiovascular disease.<sup class="ref"><a href="sources.html#mic8">[1]</a></sup></p>
      <div class="panel warn">
        <h3>Read that carefully</h3>
        <p>The WHO explicitly labelled this a <em>conditional</em> recommendation based on low-certainty evidence, and noted the observational associations may reflect reverse causation — people already at higher risk are more likely to switch to sweeteners in the first place. It is not a finding that sweeteners are toxic, and it is not a safety warning about approved intake levels.<sup class="ref"><a href="sources.html#mic8">[1]</a></sup></p>
      </div>
      <p>The practical takeaway most researchers converge on: swapping sugary drinks for sweetened ones is likely an improvement over doing nothing, but neither is as good as shifting toward water and whole foods.</p>''', bg="var(--color-carbs-bg)", tight=True),
    [("added-sugar-vs-natural-sugar.html", "Added vs. natural sugar"), ("sugar-addiction-is-it-real.html", "Is sugar addiction real?"), ("net-carbs-vs-total-carbs.html", "Net carbs vs. total carbs")]
)

add(
    "fiber-and-gut-microbiome",
    "Fiber and Your Gut Microbiome Explained",
    "How gut bacteria ferment dietary fiber into short-chain fatty acids, why that matters for health, and which foods feed your microbiome best.",
    "carbs", "Carbohydrate Guide", "Fiber and your gut microbiome",
    "You don't digest fiber. The trillions of bacteria in your large intestine do — and what they produce from it is the interesting part.",
    sec('''      <h2>What fermentation actually produces</h2>
      <p>Fiber passes through the small intestine largely intact. In the colon, gut bacteria ferment the soluble, fermentable fraction of it and produce <strong>short-chain fatty acids</strong> — mainly acetate, propionate, and butyrate. Butyrate is the preferred fuel of the cells lining your colon, which is a striking arrangement: you feed the bacteria, and the bacteria feed your gut lining.<sup class="ref"><a href="sources.html#mic13">[1]</a></sup></p>
      <h2>Soluble vs. insoluble</h2>
      <table class="data-table">
        <tr><th>Type</th><th>What it does</th><th>Found in</th></tr>
        <tr><td>Soluble</td><td>Forms a gel, feeds gut bacteria, slows glucose absorption, binds cholesterol</td><td>Oats, barley, beans, apples, citrus, psyllium</td></tr>
        <tr><td>Insoluble</td><td>Adds bulk, speeds transit through the gut</td><td>Wheat bran, whole grains, nuts, vegetable skins</td></tr>
      </table>''') +
    sec('''      <h2>Feeding a diverse microbiome</h2>
      <p>The single most consistent finding in this area is that <strong>plant diversity matters more than any one "superfood."</strong> Different bacterial species ferment different fibers, so a diet drawing on a wide range of plants supports a wider range of species than a diet built on one high-fiber food.</p>
      <ul class="checklist">
        <li>Legumes — beans, lentils, chickpeas</li>
        <li>Whole grains — oats, barley, rye</li>
        <li>A varied mix of vegetables, fruit, nuts, and seeds</li>
        <li>Fermented foods, which add live bacteria alongside the fiber that feeds them</li>
      </ul>
      <div class="panel">
        <h3>Increase it gradually</h3>
        <p>Jumping from a low-fiber diet to a very high-fiber one in a few days reliably produces gas and bloating while your microbiome adjusts. Increase over a few weeks and raise water intake alongside it.</p>
      </div>''', bg="var(--color-carbs-bg)", tight=True),
    [("fiber-benefits.html", "Why fiber matters"), ("high-fiber-foods-list.html", "High-fiber foods list"), ("how-digestion-works.html", "How digestion works")]
)

add(
    "how-to-track-your-macros",
    "How to Track Your Macros: A Beginner's Guide",
    "A practical walkthrough of tracking macros — setting targets, weighing versus estimating, handling recipes and eating out, and when to stop tracking.",
    "general", "Practical Guides", "How to track your macros: a beginner's guide",
    "Tracking is a measurement tool, not a lifestyle. Used well it teaches you what's in your food; used badly it becomes an anxiety generator.",
    sec('''      <h2>Step 1: set your targets</h2>
      <p>Start with total calories based on your <a href="tdee-vs-bmr.html">TDEE</a> and goal, then set protein first (1.6–2.2 g/kg if you train), fat next (at minimum 20% of calories to support hormone production and <a href="fat-soluble-vitamins-explained.html">fat-soluble vitamin absorption</a>), and let carbohydrate fill the remainder.<sup class="ref"><a href="sources.html#p2">[1]</a></sup> Our <a href="calculators.html">macro calculator</a> does this arithmetic for you, or you can <a href="how-to-calculate-macros-by-hand.html">work it out by hand</a>.</p>
      <h2>Step 2: weigh, at first</h2>
      <p>For the first two or three weeks, weigh food in grams rather than using cups or eyeballing. Not forever — the point is calibration. Most people substantially underestimate portions of calorie-dense foods (oil, nut butter, cheese, rice) and overestimate protein portions. Once you've seen what 150 g of chicken actually looks like, you can <a href="portion-sizes-without-a-scale.html">estimate without a scale</a> reasonably well.</p>''') +
    sec('''      <h2>Step 3: handle the awkward cases</h2>
      <ul class="checklist">
        <li><strong>Recipes</strong> — log the raw ingredients once, save the recipe, then log portions of it. Weigh the finished dish so you can divide it accurately.</li>
        <li><strong>Eating out</strong> — pick the closest reasonable database match and move on. Precision here is impossible, and chasing it is the fastest route to giving up.</li>
        <li><strong>Cooked vs. raw</strong> — weights differ substantially as food loses or absorbs water. Pick one convention and stay consistent.</li>
        <li><strong>Alcohol</strong> — contributes 7 kcal/g and fits no macro category cleanly. See <a href="alcohol-and-macros.html">alcohol and macros</a>.</li>
      </ul>''', bg="var(--color-pop2-bg)", tight=True) +
    sec('''      <h2>Step 4: know when to stop</h2>
      <p>Tracking has done its job when you can look at a plate and estimate its macros within a reasonable margin. Many people track for a few months, then move to tracking only protein, or only occasionally to recalibrate. If tracking starts driving anxiety around food, that's a signal to stop and consider a less rigid approach such as <a href="intuitive-eating-explained.html">intuitive eating</a> — a tool that makes eating worse isn't working.</p>
      <p><a href="calculators.html" class="btn btn-primary">Set your macro targets →</a></p>'''),
    [("calculators.html", "Macro calculator"), ("how-to-calculate-macros-by-hand.html", "Calculate macros by hand"), ("iifym-flexible-dieting.html", "IIFYM and flexible dieting")]
)

# ------------------------------------------ HEALTH & PRACTICAL BATCH ------

add(
    "protein-and-kidney-health",
    "Does High Protein Damage Your Kidneys?",
    "Where the high-protein kidney myth came from, what controlled trials show in healthy people, and who genuinely does need to limit protein.",
    "protein", "Protein Guide", "Does high protein damage your kidneys?",
    "This is probably the most repeated concern about high-protein diets — and one where the evidence for healthy people is much clearer than the rumour suggests.",
    sec('''      <h2>Where the concern came from</h2>
      <p>Protein metabolism produces nitrogen waste, which the kidneys filter out. In people who <em>already</em> have chronic kidney disease, reducing protein intake can slow the decline in kidney function. That clinical finding — real and well-established in kidney patients — got generalized into a warning for everyone.<sup class="ref"><a href="sources.html#p3">[1]</a></sup></p>
      <h2>What happens in healthy kidneys</h2>
      <p>Higher protein intake does increase glomerular filtration rate, the rate at which kidneys filter blood. But that's a normal functional adaptation to a higher workload, not damage — in the same way that muscles adapt to heavier training. Controlled trials in healthy adults consuming high-protein diets have not shown deterioration in kidney function.<sup class="ref"><a href="sources.html#p2">[2]</a></sup></p>''') +
    sec('''      <div class="panel warn">
        <h3>Who should actually limit protein</h3>
        <p>People with diagnosed chronic kidney disease, reduced kidney function, or a single kidney should follow protein targets set by their doctor or renal dietitian — not general fitness guidance. The point isn't that protein is harmless for everyone; it's that healthy kidneys and impaired kidneys are different situations.</p>
      </div>
      <p>If you have any reason to suspect reduced kidney function, that's a blood test question, not an internet question.</p>''', bg="var(--color-protein-bg)", tight=True),
    [("how-much-protein-per-day.html", "How much protein per day"), ("common-nutrition-myths-debunked.html", "Common nutrition myths"), ("protein-for-muscle-growth.html", "Protein for muscle growth")],
    faq=[
        ("Does high protein damage healthy kidneys?", "In people with healthy kidneys, controlled trials have not shown that high protein intake causes kidney damage. The increase in filtration rate seen on higher-protein diets is a normal functional adaptation rather than injury."),
        ("Who does need to limit protein?", "People with diagnosed chronic kidney disease or reduced kidney function should follow protein targets set by their doctor or renal dietitian, since lowering protein can slow the decline in kidney function in that group."),
        ("How much protein is too much?", "For healthy adults there is no well-established intake at which protein becomes harmful. Most benefit plateaus around 1.6-2.2 g/kg of body weight per day for people who train, so higher intakes mainly displace other nutrients rather than adding benefit."),
    ],
)

add(
    "how-to-build-a-balanced-meal",
    "How to Build a Balanced Meal (Simple Method)",
    "A practical plate framework for putting together meals that hit protein, fiber, and calorie targets without weighing every ingredient.",
    "general", "Practical Guides", "How to build a balanced meal",
    "You don't need a spreadsheet to eat well. You need a repeatable structure you can apply to whatever's in the fridge.",
    sec('''      <h2>The four-part plate</h2>
      <ul class="checklist">
        <li><strong>Protein first (a palm-sized portion, 25-40g)</strong> — meat, fish, eggs, dairy, tofu, tempeh, or legumes. Building the plate around protein is the single highest-leverage habit, because it's the macro people most often fall short on.<sup class="ref"><a href="sources.html#p2">[1]</a></sup></li>
        <li><strong>Vegetables (half the plate)</strong> — volume, fiber, and micronutrients for very few calories. This is what makes a meal filling without making it calorie-dense.</li>
        <li><strong>A carbohydrate source (a cupped-hand portion)</strong> — rice, potatoes, pasta, bread, oats. Scale this up on training days and down on rest days if you're managing calories.</li>
        <li><strong>A fat source (a thumb-sized portion)</strong> — olive oil, nuts, avocado, cheese. Small by volume, but the most calorie-dense part of the plate, so this is where portions drift most easily.</li>
      </ul>''') +
    sec('''      <h2>Why this works without tracking</h2>
      <p>Hand-based portions scale with body size automatically — bigger people have bigger hands and generally need more food. It's imprecise, but the error is small compared to the error most people make when eyeballing with no framework at all. See <a href="portion-sizes-without-a-scale.html">estimating portions without a scale</a> for the full method.</p>
      <div class="panel">
        <h3>The adjustment dial</h3>
        <p>If you're losing weight too fast, add carbs. Too slow, reduce the fat portion first (it's the densest). Hungry between meals, add protein and vegetables rather than snacks. One variable at a time.</p>
      </div>''', bg="var(--color-carbs-bg)", tight=True),
    [("portion-sizes-without-a-scale.html", "Portion sizes without a scale"), ("how-to-track-your-macros.html", "How to track your macros"), ("nutrient-density-explained.html", "Nutrient density explained")],
    faq=[
        ("How much protein should be on each plate?", "A palm-sized portion, roughly 25-40g of protein, works for most people. Spreading protein across three or four meals this way supports muscle protein synthesis better than getting most of your protein in one large meal."),
        ("Do I need to weigh food to eat balanced meals?", "No. Hand-based portions scale with body size and are accurate enough for most goals. Weighing food for two or three weeks is useful for calibration, after which visual estimates become reliable."),
        ("Should carbs change on rest days?", "Optionally. Some people scale carbohydrate up on training days and down on rest days to match energy demand, but total weekly intake matters more than daily distribution for most goals."),
    ],
)

add(
    "sleep-and-nutrition",
    "How Sleep Affects Appetite and Body Composition",
    "What short sleep does to hunger hormones, cravings, and muscle retention while dieting, and why sleep is a nutrition variable.",
    "general", "Practical Guides", "How sleep affects appetite and body composition",
    "You can do everything right with food and still stall — because sleep quietly moves several of the levers you're trying to control.",
    sec('''      <h2>What short sleep does to appetite</h2>
      <p>Sleep restriction shifts the hormones governing hunger: ghrelin (which stimulates appetite) tends to rise and leptin (which signals fullness) tends to fall. The practical result is that under-slept people report more hunger and stronger cravings for calorie-dense, high-carbohydrate food — while their actual energy needs haven't changed.</p>
      <h2>What it does to body composition</h2>
      <p>The more striking finding concerns <em>what</em> you lose while dieting. In controlled calorie-restriction studies, participants sleeping around 5.5 hours lost a substantially greater proportion of their weight as lean mass rather than fat, compared with the same deficit at around 8.5 hours. Same calories, worse outcome.</p>''') +
    sec('''      <h2>Treating sleep as a nutrition variable</h2>
      <ul class="checklist">
        <li><strong>Caffeine timing</strong> — caffeine has a half-life of roughly 5-6 hours, so an afternoon coffee is still meaningfully active at bedtime. See <a href="caffeine-and-athletic-performance.html">caffeine and performance</a>.</li>
        <li><strong>Alcohol</strong> — it shortens time to sleep onset but degrades sleep quality, particularly REM. See <a href="alcohol-and-macros.html">alcohol and macros</a>.</li>
        <li><strong>Very large late meals</strong> — can cause discomfort and disrupt sleep for some people, though total intake still drives weight change more than timing does.</li>
        <li><strong>Protein before bed</strong> — a slow-digesting protein source is a reasonable way to use the overnight window. See <a href="protein-before-bed.html">protein before bed</a>.</li>
      </ul>''', bg="var(--color-pop2-bg)", tight=True),
    [("protein-before-bed.html", "Protein before bed"), ("eating-late-at-night-weight-gain.html", "Eating late at night"), ("body-recomposition-explained.html", "Body recomposition")],
    faq=[
        ("Does poor sleep make you hungrier?", "Yes. Sleep restriction tends to raise ghrelin, which stimulates appetite, and lower leptin, which signals fullness. Under-slept people typically report more hunger and stronger cravings for calorie-dense foods."),
        ("Can bad sleep stop fat loss?", "It does not stop fat loss, but it changes its composition. In controlled studies at the same calorie deficit, people sleeping around 5.5 hours lost a greater share of weight as lean mass than those sleeping around 8.5 hours."),
        ("How late can I drink coffee?", "Caffeine has a half-life of roughly 5-6 hours, so a mid-afternoon coffee is still meaningfully active at bedtime for many people. Shifting caffeine earlier is one of the simplest sleep improvements available."),
    ],
)

add(
    "food-labels-serving-size-traps",
    "Nutrition Label Traps: Serving Sizes Explained",
    "How serving sizes, rounding rules, and per-100g versus per-serving figures make packaged food look better than it is.",
    "general", "Practical Guides", "Nutrition label traps: serving sizes explained",
    "The numbers on a label are accurate. What they're attached to is where the room for interpretation lives.",
    sec('''      <h2>Trap 1: the serving is not the package</h2>
      <p>A bottle of soda or a bag of chips frequently contains two or three servings. All the figures on the panel — calories, sugar, sodium — describe one of them. Nothing is false, but reading the panel without checking "servings per container" understates what you actually consumed by a factor of two or three.</p>
      <h2>Trap 2: rounding to zero</h2>
      <p>Labelling rules allow amounts below a threshold to be declared as zero. A product with a small amount of trans fat per serving can legally be listed as "0g trans fat" — and if the serving is small enough, several servings still add up. Checking the ingredients list for "partially hydrogenated oil" is more reliable than trusting the zero.<sup class="ref"><a href="sources.html#f4">[1]</a></sup></p>''') +
    sec('''      <h2>Trap 3: per 100g vs per serving</h2>
      <p>Comparing two products is only meaningful on the same basis. Per-100g figures are the fair comparison between brands; per-serving figures tell you what you'll actually eat. Manufacturers may choose flattering serving sizes, so use per-100g to compare and per-serving to plan.</p>
      <div class="panel">
        <h3>Fast label check</h3>
        <p>Servings per container → calories per serving → protein → added sugar → ingredients list. The ingredients list is ordered by weight, so if sugar (under any of its many names) appears in the first three, the product is largely sugar regardless of front-of-pack claims. See <a href="how-to-read-a-nutrition-label.html">how to read a nutrition label</a>.</p>
      </div>''', bg="var(--color-fat-bg)", tight=True),
    [("how-to-read-a-nutrition-label.html", "How to read a nutrition label"), ("added-sugar-vs-natural-sugar.html", "Added vs. natural sugar"), ("trans-fat-explained.html", "Trans fat explained")],
    faq=[
        ("Why do labels show more than one serving?", "Serving sizes are standardized reference amounts, not a recommendation of how much to eat. A package often contains two or three servings, so the panel figures must be multiplied by servings per container to describe the whole package."),
        ("Can a product labelled 0g trans fat contain trans fat?", "Yes. Labelling rules permit amounts below a threshold to be rounded to zero per serving. Checking the ingredients list for partially hydrogenated oil is a more reliable indicator than the declared figure."),
        ("Should I compare foods per serving or per 100g?", "Use per-100g figures to compare brands fairly, since serving sizes differ between products, and per-serving figures to plan what you will actually eat."),
    ],
)

add(
    "meal-prep-for-macros",
    "Meal Prep for Macros: A Practical System",
    "How to batch-cook around macro targets, which foods hold up over several days, and how to keep prepped meals from getting boring.",
    "general", "Practical Guides", "Meal prep for macros: a practical system",
    "Most diets fail on a Tuesday evening when there's nothing ready and everything is easy to order. Prep is insurance against that moment.",
    sec('''      <h2>Prep components, not complete meals</h2>
      <p>Cooking five identical portions of one dish is the fastest route to abandoning meal prep. Preparing <em>components</em> — a protein, a starch, a vegetable, a sauce — lets you assemble different combinations from the same batch cook, which keeps variety high for the same effort.</p>
      <ul class="checklist">
        <li><strong>Proteins that reheat well</strong> — chicken thighs, beef mince, lentils, baked tofu, hard-boiled eggs. Chicken breast dries out; thighs are more forgiving.</li>
        <li><strong>Starches that hold</strong> — rice, potatoes, pasta, quinoa. Cooled and reheated starches also form some resistant starch, which acts more like fiber.</li>
        <li><strong>Vegetables that survive</strong> — roasted root vegetables, peppers, broccoli. Leafy greens are best added fresh at serving.</li>
        <li><strong>Sauces</strong> — the cheapest way to make the same components taste like different meals.</li>
      </ul>''') +
    sec('''      <h2>Weigh once, at the batch level</h2>
      <p>Weigh ingredients raw as you cook, note the total, then divide the finished batch into equal portions. That gives you accurate per-portion macros without weighing anything at mealtime — the practical version of <a href="how-to-track-your-macros.html">macro tracking</a>.</p>
      <div class="panel warn">
        <h3>Food safety, briefly</h3>
        <p>Cool cooked food quickly and refrigerate within about two hours. Most prepped meals keep three to four days refrigerated; freeze anything beyond that. Reheat to steaming hot rather than just warm.</p>
      </div>''', bg="var(--color-carbs-bg)", tight=True),
    [("how-to-track-your-macros.html", "How to track your macros"), ("how-to-build-a-balanced-meal.html", "Build a balanced meal"), ("high-protein-foods-list.html", "High-protein foods list")],
    faq=[
        ("How long do prepped meals last?", "Most cooked meals keep three to four days refrigerated. Cool them quickly and refrigerate within about two hours of cooking, and freeze anything you will not eat within that window."),
        ("How do I get accurate macros from a batch cook?", "Weigh the ingredients raw as you cook and record the totals, then divide the finished batch into equal portions. Each portion carries a known share of the total, so no mealtime weighing is needed."),
        ("How do I stop meal prep getting boring?", "Prepare components rather than complete meals. A batch of protein, starch, vegetables, and two or three sauces can be assembled into several different-tasting meals from one cooking session."),
    ],
)

add(
    "ultra-processed-foods-explained",
    "Ultra-Processed Foods: What the Evidence Shows",
    "What ultra-processed actually means under the NOVA classification, what the controlled feeding research found, and why the category is debated.",
    "general", "Practical Guides", "Ultra-processed foods: what the evidence shows",
    "\"Processed\" covers everything from bagged spinach to a frozen pizza, which is exactly why the term causes so much confusion.",
    sec('''      <h2>What the term actually means</h2>
      <p>The NOVA system sorts food by degree of processing rather than by nutrient content. Group 1 is unprocessed or minimally processed food; Group 2 is culinary ingredients like oil and salt; Group 3 is processed food such as bread and cheese; Group 4 is <strong>ultra-processed</strong> — industrial formulations typically containing ingredients not used in home cooking, such as protein isolates, emulsifiers, and modified starches.</p>
      <h2>The key experiment</h2>
      <p>A tightly controlled inpatient trial fed participants either ultra-processed or minimally processed diets matched for calories, sugar, fat, fiber, and sodium, and let them eat as much as they wanted. On the ultra-processed diet people ate roughly 500 more calories per day and gained weight; on the minimally processed diet they lost it. Because the diets were nutrient-matched, something about the processing itself — not just the nutrient profile — was driving intake.<sup class="ref"><a href="sources.html#upf1">[1]</a></sup></p>''') +
    sec('''      <h2>The honest caveats</h2>
      <ul class="checklist">
        <li><strong>The category is broad.</strong> Wholegrain bread, flavoured yogurt, and a candy bar can all land in Group 4, which limits how useful a blanket warning is.</li>
        <li><strong>Mechanism isn't settled.</strong> Energy density, softer texture and faster eating rate, and lower satiety per calorie are all plausible contributors.</li>
        <li><strong>Cost and access matter.</strong> Ultra-processed food is often cheaper, shelf-stable, and requires no cooking, so "just avoid it" is not equally actionable for everyone.</li>
      </ul>
      <p>A more workable framing than avoidance: build meals around whole foods where you can, and treat a high share of ultra-processed food as something to shift gradually rather than eliminate overnight.</p>''', bg="var(--color-pop3-bg)", tight=True),
    [("nutrient-density-explained.html", "Nutrient density explained"), ("how-to-read-a-nutrition-label.html", "How to read a nutrition label"), ("added-sugar-vs-natural-sugar.html", "Added vs. natural sugar")],
    faq=[
        ("What counts as ultra-processed food?", "Under the NOVA classification, ultra-processed foods are industrial formulations that typically include ingredients not used in home cooking, such as protein isolates, emulsifiers, and modified starches. Soft drinks, packaged snacks, and many ready meals fall in this group."),
        ("Do ultra-processed foods cause weight gain?", "A controlled inpatient trial matching diets for calories, sugar, fat, fiber, and sodium found people ate around 500 more calories per day on the ultra-processed diet and gained weight, suggesting processing itself influences intake beyond nutrient content."),
        ("Are all processed foods bad?", "No. Processing covers a wide range, from bagged salad and canned beans to industrially formulated snacks. Many processed foods such as wholegrain bread, yogurt, and frozen vegetables are nutritionally useful."),
    ],
)

add(
    "hydration-and-performance",
    "Dehydration and Performance: What Matters",
    "How much fluid loss actually impairs performance, how to estimate your sweat rate, and why drinking to thirst works for most people.",
    "athletes", "Sports Nutrition", "Dehydration and performance: what matters",
    "Hydration advice swings between \"you're chronically dehydrated\" and \"just drink to thirst.\" The research supports something closer to the second, with conditions.",
    sec('''      <h2>Where performance actually declines</h2>
      <p>Meaningful decrements in endurance performance generally appear once fluid loss exceeds roughly <strong>2% of body mass</strong> — about 1.5 kg for a 75 kg athlete. Below that threshold, effects on performance are small and inconsistent. Above it, and particularly in heat, cardiovascular strain rises and performance falls measurably.<sup class="ref"><a href="sources.html#ath3">[1]</a></sup></p>
      <h2>Estimating your sweat rate</h2>
      <p>Weigh yourself before and after an hour of training, in minimal clothing, accounting for any fluid consumed. The difference approximates your hourly sweat loss. Rates vary enormously between individuals and conditions — from under 0.5 L/hour to over 2 L/hour — which is exactly why blanket fluid recommendations fit almost nobody well.</p>''') +
    sec('''      <h2>What to drink, and when</h2>
      <ul class="checklist">
        <li><strong>Under 60 minutes</strong> — water is sufficient for the overwhelming majority of sessions. See <a href="sports-drinks-vs-water.html">sports drinks vs. water</a>.</li>
        <li><strong>Over 60-90 minutes, or heavy sweating in heat</strong> — a drink containing sodium and carbohydrate becomes useful for both fluid retention and fuel.</li>
        <li><strong>Drinking to thirst</strong> — for most recreational athletes this self-regulates adequately without any calculation.</li>
      </ul>
      <div class="panel warn">
        <h3>Overdrinking is a real risk too</h3>
        <p>Drinking far beyond sweat losses during long events can dilute blood sodium, causing exercise-associated hyponatremia — a genuinely dangerous condition. More fluid is not automatically better; matching intake roughly to losses is.<sup class="ref"><a href="sources.html#ath3">[1]</a></sup></p>
      </div>''', bg="var(--color-pop2-bg)", tight=True),
    [("sports-drinks-vs-water.html", "Sports drinks vs. water"), ("electrolytes-explained.html", "Electrolytes explained"), ("how-much-water-should-you-drink-per-day.html", "How much water per day")],
    faq=[
        ("At what point does dehydration hurt performance?", "Endurance performance generally declines once fluid loss exceeds roughly 2% of body mass, which is about 1.5 kg for a 75 kg athlete. Below that level, effects are small and inconsistent."),
        ("How do I work out my sweat rate?", "Weigh yourself before and after an hour of training in minimal clothing, adjusting for any fluid you drank. The weight difference approximates your hourly sweat loss."),
        ("Can you drink too much water during exercise?", "Yes. Drinking well beyond sweat losses during prolonged events can dilute blood sodium and cause exercise-associated hyponatremia, which is dangerous. Matching intake roughly to losses is safer than maximising intake."),
    ],
)

add(
    "vitamin-c-and-immunity",
    "Vitamin C and Immunity: What It Really Does",
    "How much vitamin C you need, whether supplements shorten colds, and why the megadose claims outran the evidence.",
    "general", "Micronutrients", "Vitamin C and immunity: what it really does",
    "Vitamin C is the nutrient most associated with immunity in the public mind, and the gap between that reputation and the trial data is instructive.",
    sec('''      <h2>What it does</h2>
      <p>Vitamin C is required to synthesize collagen, which is why severe deficiency causes scurvy — poor wound healing, bleeding gums, and connective tissue breakdown. It also functions as an antioxidant and supports several immune cell functions, and it markedly improves absorption of non-heme iron from plant foods.<sup class="ref"><a href="sources.html#mic14">[1]</a></sup></p>
      <h2>How much you need</h2>
      <table class="data-table">
        <tr><th>Group</th><th>RDA</th><th>Upper limit</th></tr>
        <tr><td>Men 19+</td><td>90 mg/day</td><td>2,000 mg/day</td></tr>
        <tr><td>Women 19+</td><td>75 mg/day</td><td>2,000 mg/day</td></tr>
        <tr><td>Smokers</td><td>+35 mg/day</td><td>2,000 mg/day</td></tr>
      </table>
      <p>A single medium orange supplies roughly 70 mg; a cup of raw red pepper supplies more than a day's requirement.<sup class="ref"><a href="sources.html#mic14">[1]</a></sup></p>''') +
    sec('''      <h2>Does it prevent colds?</h2>
      <p>Regular supplementation does not appear to reduce the likelihood of catching a cold in the general population. It has been associated with a modest reduction in cold <em>duration</em>, and the picture differs for people under heavy physical stress such as marathon runners, where supplementation has shown a larger effect on incidence.<sup class="ref"><a href="sources.html#mic14">[1]</a></sup></p>
      <div class="panel">
        <h3>Why megadoses do little</h3>
        <p>Absorption efficiency falls sharply as intake rises, and the excess — being water-soluble — is excreted. Beyond roughly 400 mg/day, plasma levels plateau regardless of how much more you take.<sup class="ref"><a href="sources.html#mic14">[1]</a></sup></p>
      </div>''', bg="var(--color-carbs-bg)", tight=True),
    [("iron-deficiency-and-athletes.html", "Iron deficiency in athletes"), ("micronutrients-vs-macronutrients.html", "Micronutrients vs. macronutrients"), ("vitamin-d-explained.html", "Vitamin D explained")],
    faq=[
        ("Does vitamin C prevent colds?", "Regular vitamin C supplementation does not appear to reduce how often people in the general population catch colds, though it has been linked to a modest reduction in duration. People under heavy physical stress, such as marathon runners, show larger effects."),
        ("How much vitamin C do I need per day?", "The RDA is 90 mg per day for adult men and 75 mg for adult women, with an additional 35 mg for smokers. The tolerable upper limit is 2,000 mg per day."),
        ("Do high-dose vitamin C supplements work better?", "Not meaningfully. Absorption efficiency falls as intake rises and the excess is excreted in urine, so plasma levels plateau beyond roughly 400 mg per day."),
    ],
)

add(
    "zinc-explained",
    "Zinc: Immune Function, Sources and Limits",
    "What zinc does for immune function and protein synthesis, how much you need, and why plant-based diets need more of it.",
    "general", "Micronutrients", "Zinc: immune function, sources and limits",
    "Zinc turns up in hundreds of enzymes and is one of the minerals most affected by what kind of diet you eat.",
    sec('''      <h2>What it does</h2>
      <p>Zinc is a component of hundreds of enzymes and is required for protein synthesis, DNA synthesis, wound healing, normal growth, and immune cell development. Deficiency impairs immune function and slows wound healing, and severe deficiency stunts growth in children.<sup class="ref"><a href="sources.html#mic15">[1]</a></sup></p>
      <h2>How much you need</h2>
      <table class="data-table">
        <tr><th>Group</th><th>RDA</th><th>Upper limit</th></tr>
        <tr><td>Men 19+</td><td>11 mg/day</td><td>40 mg/day</td></tr>
        <tr><td>Women 19+</td><td>8 mg/day</td><td>40 mg/day</td></tr>
      </table>''') +
    sec('''      <h2>Why plant-based diets need more</h2>
      <p>Oysters are by far the richest source, followed by red meat, poultry, beans, nuts, and whole grains. But phytates in legumes and whole grains bind zinc and reduce its absorption, so the Institute of Medicine notes that vegetarians may require as much as <strong>50% more</strong> zinc than the RDA.<sup class="ref"><a href="sources.html#mic15">[1]</a></sup> Soaking, sprouting, and leavening bread all reduce phytate content and improve absorption.</p>
      <div class="panel warn">
        <h3>The upper limit matters here</h3>
        <p>Chronic high-dose zinc supplementation interferes with copper absorption and can cause copper deficiency. The 40 mg/day upper limit is not a formality — lozenges and supplements can push past it easily if taken continuously.<sup class="ref"><a href="sources.html#mic15">[1]</a></sup></p>
      </div>''', bg="var(--color-protein-bg)", tight=True),
    [("vegan-macros-guide.html", "Vegan macros guide"), ("iron-deficiency-and-athletes.html", "Iron deficiency in athletes"), ("plant-based-protein-sources.html", "Plant-based protein sources")],
    faq=[
        ("How much zinc do I need daily?", "The RDA is 11 mg per day for adult men and 8 mg for adult women, with a tolerable upper limit of 40 mg per day for adults."),
        ("Do vegetarians need more zinc?", "Yes. Phytates in legumes and whole grains bind zinc and reduce absorption, and vegetarians may require up to 50% more zinc than the RDA. Soaking, sprouting, and leavening reduce phytate content."),
        ("Can you take too much zinc?", "Yes. Chronic intakes above the 40 mg per day upper limit interfere with copper absorption and can cause copper deficiency, so continuous high-dose supplementation should be avoided."),
    ],
)

add(
    "protein-for-older-adults",
    "Protein for Older Adults: Preventing Muscle Loss",
    "Why protein needs rise with age, what anabolic resistance means, and how much protein helps preserve muscle after 50.",
    "protein", "Protein Guide", "Protein for older adults: preventing muscle loss",
    "The RDA was set from nitrogen balance studies in younger adults. For older adults, the evidence increasingly says it's too low.",
    sec('''      <h2>Sarcopenia and anabolic resistance</h2>
      <p>Adults progressively lose muscle mass and strength from around the fourth decade onward — a process called <strong>sarcopenia</strong>. Part of the cause is <em>anabolic resistance</em>: ageing muscle responds less strongly to a given dose of protein than younger muscle does. The same 20g of protein that maximally stimulates muscle protein synthesis in a 25-year-old produces a blunted response in a 70-year-old.<sup class="ref"><a href="sources.html#p2">[1]</a></sup></p>
      <h2>What that means for intake</h2>
      <p>Because the response is blunted, the practical answer is a larger dose per meal rather than the same amount spread thinner. Research groups working on healthy ageing commonly recommend intakes above the 0.8 g/kg RDA — often in the region of <strong>1.0-1.2 g/kg/day</strong> for healthy older adults, and higher still with illness or during rehabilitation.<sup class="ref"><a href="sources.html#p3">[2]</a></sup></p>''') +
    sec('''      <h2>Protein alone isn't enough</h2>
      <p>The strongest signal for muscle retention is mechanical: resistance training. Protein supplies the raw material, but without a stimulus telling the body to build, the material is largely redirected. Combining resistance training with adequate protein is far more effective for preserving muscle than either alone.<sup class="ref"><a href="sources.html#p2">[1]</a></sup></p>
      <div class="panel">
        <h3>Practical targets</h3>
        <p>Aim for a meaningful protein serving (roughly 25-40g) at each main meal rather than one protein-heavy dinner. Appetite often declines with age, so protein-dense choices — dairy, eggs, fish, meat, legumes — matter more when total food volume is lower.</p>
      </div>''', bg="var(--color-protein-bg)", tight=True),
    [("how-much-protein-per-day.html", "How much protein per day"), ("protein-for-muscle-growth.html", "Protein for muscle growth"), ("catabolism-vs-anabolism.html", "Catabolism vs. anabolism")],
    faq=[
        ("Do older adults need more protein?", "The evidence increasingly supports intakes above the 0.8 g/kg RDA for healthy older adults, often around 1.0-1.2 g/kg per day, because ageing muscle responds less strongly to a given dose of protein."),
        ("What is anabolic resistance?", "Anabolic resistance describes the blunted muscle protein synthesis response to protein intake that develops with age. A protein dose that maximally stimulates synthesis in a young adult produces a smaller response in an older adult."),
        ("Is protein enough to prevent muscle loss?", "No. Resistance training provides the mechanical signal that drives muscle retention, and protein supplies the raw material. Combining the two is substantially more effective than either alone."),
    ],
)

# ------------------------------- NUTRITION SCIENCE & PHYSIOLOGY (REVISION) --

add(
    "glycolysis-explained",
    "Glycolysis Explained: Steps, ATP Yield, Control",
    "A revision walkthrough of glycolysis — the investment and payoff phases, net ATP and NADH yield, regulation, and what happens to pyruvate.",
    "science", "Metabolism", "Glycolysis explained: steps, ATP yield and control",
    "Glycolysis is the entry point for carbohydrate metabolism and one of the most reliably examined pathways in any biochemistry course.",
    sec('''      <h2>The overview equation</h2>
      <p>Glycolysis splits one 6-carbon glucose molecule into two 3-carbon pyruvate molecules in the cytosol. It requires no oxygen, which is why it functions in both aerobic and anaerobic conditions.</p>
      <div class="panel">
        <h3>Net reaction</h3>
        <p>Glucose + 2 NAD<sup>+</sup> + 2 ADP + 2 P<sub>i</sub> → 2 pyruvate + 2 NADH + 2 H<sup>+</sup> + <strong>2 ATP</strong> + 2 H<sub>2</sub>O</p>
      </div>
      <h2>Two phases</h2>
      <p>The pathway divides cleanly into an energy <em>investment</em> phase and an energy <em>payoff</em> phase — a distinction worth memorizing, because it explains why the gross and net ATP figures differ.</p>
      <table class="data-table">
        <tr><th>Phase</th><th>Steps</th><th>ATP</th><th>Key point</th></tr>
        <tr><td>Investment</td><td>1–5</td><td>−2 ATP</td><td>Glucose is phosphorylated twice, then split into two 3-carbon molecules</td></tr>
        <tr><td>Payoff</td><td>6–10</td><td>+4 ATP, +2 NADH</td><td>Everything happens twice, once per 3-carbon molecule</td></tr>
      </table>
      <p>Gross yield is 4 ATP; net yield is <strong>2 ATP</strong> because two were spent up front.</p>''') +
    sec('''      <h2>The three regulated steps</h2>
      <p>Exam questions frequently target regulation. Three steps are effectively irreversible and therefore serve as control points:</p>
      <ul class="checklist">
        <li><strong>Hexokinase</strong> (step 1) — traps glucose in the cell as glucose-6-phosphate; inhibited by its own product.</li>
        <li><strong>Phosphofructokinase-1 (PFK-1)</strong> (step 3) — the <em>rate-limiting</em> step and the main control point. Inhibited by ATP and citrate (signals of energy abundance), activated by AMP and fructose-2,6-bisphosphate (signals of energy demand).</li>
        <li><strong>Pyruvate kinase</strong> (step 10) — the final ATP-generating step, inhibited by ATP.</li>
      </ul>
      <div class="panel warn">
        <h3>Common exam trap</h3>
        <p>If asked for the rate-limiting enzyme of glycolysis, the answer is <strong>PFK-1</strong>, not hexokinase. Hexokinase is the first step, which is not the same thing.</p>
      </div>''', bg="var(--color-pop4-bg)", tight=True) +
    sec('''      <h2>What happens to pyruvate</h2>
      <ul class="checklist">
        <li><strong>With oxygen</strong> — pyruvate enters the mitochondrion, is converted to acetyl-CoA, and feeds the <a href="krebs-cycle-explained.html">Krebs cycle</a>.</li>
        <li><strong>Without sufficient oxygen</strong> — pyruvate is reduced to lactate, regenerating the NAD<sup>+</sup> that glycolysis needs to keep running. This is why glycolysis can continue briefly during intense exercise.</li>
      </ul>
      <p>That NAD<sup>+</sup> regeneration is the entire point of lactate production — a detail often missed when lactate is framed simply as a "waste product." See <a href="energy-systems-explained.html">the three energy systems</a> for how this plays out during exercise.</p>'''),
    [("krebs-cycle-explained.html", "The Krebs cycle explained"), ("energy-systems-explained.html", "The three energy systems"), ("what-is-glycogen.html", "What is glycogen?")],
    faq=[
        ("What is the net ATP yield of glycolysis?", "Glycolysis produces a gross yield of 4 ATP but consumes 2 ATP in the investment phase, giving a net yield of 2 ATP per glucose molecule, along with 2 NADH and 2 pyruvate."),
        ("What is the rate-limiting enzyme of glycolysis?", "Phosphofructokinase-1 (PFK-1) is the rate-limiting enzyme. It is inhibited by ATP and citrate, and activated by AMP and fructose-2,6-bisphosphate."),
        ("Does glycolysis require oxygen?", "No. Glycolysis occurs in the cytosol and does not require oxygen, which is why it functions under both aerobic and anaerobic conditions. Oxygen availability determines what happens to pyruvate afterwards."),
    ],
)

add(
    "krebs-cycle-explained",
    "Krebs Cycle Explained: Steps and ATP Yield",
    "A revision guide to the citric acid cycle — the eight steps, per-turn yields of NADH, FADH2 and GTP, regulation, and where it sits in respiration.",
    "science", "Metabolism", "The Krebs cycle explained",
    "Also called the citric acid cycle or TCA cycle, this is the metabolic hub where carbohydrate, fat, and protein breakdown all converge.",
    sec('''      <h2>Where it happens and what enters</h2>
      <p>The cycle runs in the <strong>mitochondrial matrix</strong>. Its input is acetyl-CoA — a 2-carbon unit produced from pyruvate (via pyruvate dehydrogenase), from fatty acids (via <a href="beta-oxidation-explained.html">beta-oxidation</a>), and from certain amino acids.</p>
      <div class="panel">
        <h3>Yield per turn</h3>
        <p><strong>3 NADH · 1 FADH<sub>2</sub> · 1 GTP (or ATP) · 2 CO<sub>2</sub></strong></p>
        <p>One glucose produces two acetyl-CoA, so it drives <em>two</em> turns: 6 NADH, 2 FADH<sub>2</sub>, 2 GTP.</p>
      </div>
      <h2>The cycle in brief</h2>
      <table class="data-table">
        <tr><th>Step</th><th>Conversion</th><th>Produces</th></tr>
        <tr><td>1</td><td>Acetyl-CoA + oxaloacetate → citrate</td><td>—</td></tr>
        <tr><td>2</td><td>Citrate → isocitrate</td><td>—</td></tr>
        <tr><td>3</td><td>Isocitrate → α-ketoglutarate</td><td>NADH, CO<sub>2</sub></td></tr>
        <tr><td>4</td><td>α-ketoglutarate → succinyl-CoA</td><td>NADH, CO<sub>2</sub></td></tr>
        <tr><td>5</td><td>Succinyl-CoA → succinate</td><td>GTP</td></tr>
        <tr><td>6</td><td>Succinate → fumarate</td><td>FADH<sub>2</sub></td></tr>
        <tr><td>7</td><td>Fumarate → malate</td><td>—</td></tr>
        <tr><td>8</td><td>Malate → oxaloacetate</td><td>NADH</td></tr>
      </table>''') +
    sec('''      <h2>What the cycle is actually for</h2>
      <p>A frequent misconception is that the Krebs cycle "makes ATP." It makes very little directly — just one GTP per turn. Its real function is to <strong>strip electrons</strong> from fuel molecules and load them onto the carriers NADH and FADH<sub>2</sub>, which then deliver them to the <a href="electron-transport-chain-explained.html">electron transport chain</a>, where the great majority of ATP is actually generated.</p>
      <h2>Regulation</h2>
      <ul class="checklist">
        <li><strong>Citrate synthase</strong> — inhibited by ATP, NADH, and succinyl-CoA</li>
        <li><strong>Isocitrate dehydrogenase</strong> — the main control point; activated by ADP, inhibited by ATP and NADH</li>
        <li><strong>α-ketoglutarate dehydrogenase</strong> — inhibited by its products and by NADH</li>
      </ul>
      <p>The pattern is consistent across all three: high energy charge slows the cycle, low energy charge accelerates it.</p>''', bg="var(--color-pop4-bg)", tight=True),
    [("glycolysis-explained.html", "Glycolysis explained"), ("electron-transport-chain-explained.html", "The electron transport chain"), ("beta-oxidation-explained.html", "Beta-oxidation explained")],
    faq=[
        ("What does one turn of the Krebs cycle produce?", "One turn produces 3 NADH, 1 FADH2, 1 GTP (or ATP), and 2 CO2. Because each glucose molecule yields two acetyl-CoA, one glucose drives two turns of the cycle."),
        ("Where does the Krebs cycle take place?", "In the mitochondrial matrix. This is distinct from glycolysis, which occurs in the cytosol, and from the electron transport chain, which is embedded in the inner mitochondrial membrane."),
        ("Why does the Krebs cycle make so little ATP directly?", "Its purpose is to strip electrons from fuel molecules onto NADH and FADH2 rather than to make ATP itself. Those carriers then feed the electron transport chain, where most ATP is generated."),
    ],
)

add(
    "electron-transport-chain-explained",
    "Electron Transport Chain and ATP Synthase",
    "How the electron transport chain and chemiosmosis generate most of your ATP — complexes I-IV, the proton gradient, and total aerobic yield.",
    "science", "Metabolism", "The electron transport chain explained",
    "This is where the overwhelming majority of ATP is produced, and where the NADH and FADH2 from earlier pathways finally get spent.",
    sec('''      <h2>Location and components</h2>
      <p>The chain sits in the <strong>inner mitochondrial membrane</strong>, arranged in four complexes plus ATP synthase.</p>
      <table class="data-table">
        <tr><th>Complex</th><th>Role</th><th>Pumps H<sup>+</sup>?</th></tr>
        <tr><td>I (NADH dehydrogenase)</td><td>Accepts electrons from NADH</td><td>Yes</td></tr>
        <tr><td>II (succinate dehydrogenase)</td><td>Accepts electrons from FADH<sub>2</sub></td><td><strong>No</strong></td></tr>
        <tr><td>III (cytochrome bc<sub>1</sub>)</td><td>Passes electrons to cytochrome c</td><td>Yes</td></tr>
        <tr><td>IV (cytochrome c oxidase)</td><td>Transfers electrons to O<sub>2</sub>, forming water</td><td>Yes</td></tr>
      </table>
      <p>Because FADH<sub>2</sub> enters at complex II and bypasses complex I, it drives fewer protons across the membrane — which is exactly why it yields less ATP than NADH (roughly 1.5 vs 2.5).</p>''') +
    sec('''      <h2>Chemiosmosis</h2>
      <p>As electrons move down the chain, complexes I, III, and IV pump protons from the matrix into the intermembrane space. This builds an electrochemical gradient — the <strong>proton-motive force</strong>. Protons then flow back into the matrix through <strong>ATP synthase</strong>, and that flow drives the rotation that phosphorylates ADP into ATP. Peter Mitchell's chemiosmotic theory describing this won the 1978 Nobel Prize in Chemistry.</p>
      <div class="panel warn">
        <h3>Why oxygen matters</h3>
        <p>Oxygen is the <em>final electron acceptor</em> at complex IV. Without it, electrons back up, the carriers stay reduced, NAD<sup>+</sup> is not regenerated, and the Krebs cycle halts. This is the precise reason aerobic respiration requires oxygen — not because oxygen is consumed to "burn" fuel directly.</p>
      </div>''', bg="var(--color-pop4-bg)", tight=True) +
    sec('''      <h2>Total aerobic yield</h2>
      <table class="data-table">
        <tr><th>Stage</th><th>Direct ATP</th><th>Carriers</th></tr>
        <tr><td>Glycolysis</td><td>2</td><td>2 NADH</td></tr>
        <tr><td>Pyruvate → acetyl-CoA</td><td>0</td><td>2 NADH</td></tr>
        <tr><td>Krebs cycle (×2)</td><td>2</td><td>6 NADH, 2 FADH<sub>2</sub></td></tr>
      </table>
      <p>Using the modern estimates of ~2.5 ATP per NADH and ~1.5 per FADH<sub>2</sub>, one glucose yields roughly <strong>30–32 ATP</strong>. Older textbooks state 36–38; the figure was revised downward once the cost of transporting cytosolic NADH into the mitochondrion was accounted for. If an exam expects the older number, it will usually say so.</p>'''),
    [("krebs-cycle-explained.html", "The Krebs cycle explained"), ("glycolysis-explained.html", "Glycolysis explained"), ("atp-explained.html", "What is ATP?")],
    faq=[
        ("How much ATP does one glucose molecule produce?", "Modern estimates give roughly 30-32 ATP per glucose, using about 2.5 ATP per NADH and 1.5 per FADH2. Older textbooks cite 36-38, a figure revised downward once the cost of shuttling cytosolic NADH into the mitochondrion was included."),
        ("Why does FADH2 yield less ATP than NADH?", "FADH2 donates its electrons at complex II, bypassing complex I. Because one fewer proton-pumping complex is involved, it contributes less to the proton gradient and therefore drives less ATP synthesis."),
        ("What is the role of oxygen in the electron transport chain?", "Oxygen is the final electron acceptor at complex IV, where it combines with electrons and protons to form water. Without it, electrons back up, NAD+ is not regenerated, and the Krebs cycle stops."),
    ],
)

add(
    "atp-explained",
    "What Is ATP? Structure, Hydrolysis and Function",
    "Why ATP is the cell's energy currency — its structure, why hydrolysis releases usable energy, and how quickly it is recycled.",
    "science", "Metabolism", "What is ATP?",
    "Every energy-requiring process in your body ultimately draws on the same molecule, and your body recycles roughly its own body weight of it each day.",
    sec('''      <h2>Structure</h2>
      <p>Adenosine triphosphate has three components: the nitrogenous base <strong>adenine</strong>, the 5-carbon sugar <strong>ribose</strong>, and a chain of <strong>three phosphate groups</strong>. Adenine plus ribose together form adenosine; adding the phosphates gives AMP, ADP, and ATP respectively.</p>
      <h2>Why hydrolysis releases energy</h2>
      <p>The three phosphate groups each carry negative charge and are held close together, so they repel one another — the molecule is under electrostatic strain. Breaking the terminal phosphate bond relieves that strain, and the products (ADP and inorganic phosphate) are more stable and better solvated than the reactant.</p>
      <div class="panel warn">
        <h3>The "high-energy bond" misconception</h3>
        <p>ATP's terminal bonds are often called "high-energy bonds," which misleads students into thinking the bond itself stores energy. Breaking any bond <em>requires</em> energy. The net energy release comes from the products being substantially more stable than the reactants — not from the bond containing energy.</p>
      </div>''') +
    sec('''      <h2>How it is regenerated</h2>
      <p>ATP is not a storage molecule — cells hold only a few seconds' worth. It is continuously regenerated from ADP by three routes:</p>
      <ul class="checklist">
        <li><strong>Substrate-level phosphorylation</strong> — direct transfer of a phosphate group from a substrate, as in <a href="glycolysis-explained.html">glycolysis</a> and the Krebs cycle. Fast, small yield.</li>
        <li><strong>Oxidative phosphorylation</strong> — via the <a href="electron-transport-chain-explained.html">electron transport chain</a> and ATP synthase. Slower, by far the largest yield.</li>
        <li><strong>The phosphocreatine system</strong> — creatine phosphate donates a phosphate to ADP for immediate resynthesis during very short, intense effort. See <a href="creatine-explained.html">creatine explained</a>.</li>
      </ul>
      <p>How these three are prioritized during exercise is covered in <a href="energy-systems-explained.html">the three energy systems</a>.</p>''', bg="var(--color-pop4-bg)", tight=True),
    [("energy-systems-explained.html", "The three energy systems"), ("electron-transport-chain-explained.html", "The electron transport chain"), ("creatine-explained.html", "Creatine explained")],
    faq=[
        ("What does ATP stand for?", "Adenosine triphosphate. It consists of the base adenine, the sugar ribose, and a chain of three phosphate groups."),
        ("Why does breaking down ATP release energy?", "The negatively charged phosphate groups repel each other, putting the molecule under electrostatic strain. Hydrolysis relieves that strain and yields products that are more stable and better solvated, so energy is released overall."),
        ("How much ATP does the body use per day?", "Cells hold only seconds' worth at any moment but recycle it constantly. Total turnover across a day is on the order of a person's own body weight in ATP."),
    ],
)

add(
    "enzymes-explained",
    "Enzymes: Function, Cofactors and Inhibition",
    "How enzymes lower activation energy, the induced-fit model, what cofactors and coenzymes do, and how competitive and non-competitive inhibition differ.",
    "science", "Biochemistry", "Enzymes: function, cofactors and inhibition",
    "Almost every reaction keeping you alive would be far too slow at body temperature without a catalyst to speed it up.",
    sec('''      <h2>What enzymes actually do</h2>
      <p>Enzymes are biological catalysts, nearly all of them proteins. They work by <strong>lowering the activation energy</strong> of a reaction — the energy barrier reactants must overcome. Critically, they do <em>not</em> change the reaction's equilibrium position or its overall free energy change; they only change how fast equilibrium is reached.</p>
      <h2>Lock-and-key vs. induced fit</h2>
      <p>The older lock-and-key model pictured a rigid active site precisely complementary to the substrate. The accepted <strong>induced-fit model</strong> holds that the active site is flexible and changes shape slightly on substrate binding, tightening around it and straining the bonds to be broken.</p>''') +
    sec('''      <h2>Cofactors and coenzymes</h2>
      <p>Many enzymes need a non-protein helper to function:</p>
      <ul class="checklist">
        <li><strong>Cofactors</strong> — usually inorganic ions such as Mg<sup>2+</sup>, Zn<sup>2+</sup>, or Fe<sup>2+</sup>. See <a href="magnesium-explained.html">magnesium</a> and <a href="zinc-explained.html">zinc</a>.</li>
        <li><strong>Coenzymes</strong> — organic molecules, very often derived from <strong>B vitamins</strong>: NAD<sup>+</sup> from niacin (B3), FAD from riboflavin (B2), coenzyme A from pantothenic acid (B5).</li>
      </ul>
      <p>That link is the reason B-vitamin deficiencies produce such broad, systemic symptoms — they disable enzymes across many pathways at once, rather than one specific function.</p>''', bg="var(--color-pop4-bg)", tight=True) +
    sec('''      <h2>Inhibition</h2>
      <table class="data-table">
        <tr><th>Type</th><th>Binds to</th><th>Effect on V<sub>max</sub></th><th>Effect on K<sub>m</sub></th></tr>
        <tr><td>Competitive</td><td>Active site</td><td>Unchanged</td><td>Increases</td></tr>
        <tr><td>Non-competitive</td><td>Allosteric site</td><td>Decreases</td><td>Unchanged</td></tr>
      </table>
      <p>The logic: a competitive inhibitor can be outcompeted by adding more substrate, so maximum velocity is still reachable — it just takes more substrate, which reads as a higher K<sub>m</sub>. A non-competitive inhibitor changes the enzyme's shape regardless of substrate concentration, so V<sub>max</sub> falls and no amount of extra substrate restores it. See <a href="enzyme-kinetics-explained.html">enzyme kinetics</a> for the graphs.</p>
      <h2>What denatures enzymes</h2>
      <p>Temperature and pH extremes disrupt the hydrogen bonds and ionic interactions holding the tertiary structure together. Once the active site's shape is lost, the enzyme cannot bind substrate — and above a certain point, denaturation is irreversible.</p>'''),
    [("enzyme-kinetics-explained.html", "Enzyme kinetics explained"), ("protein-structure-levels.html", "Levels of protein structure"), ("b-vitamins-and-metabolism.html", "B vitamins and metabolism")],
    faq=[
        ("How do enzymes speed up reactions?", "They lower the activation energy required for a reaction to proceed. They do not change the equilibrium position or the overall free energy change, only the rate at which equilibrium is reached."),
        ("What is the difference between a cofactor and a coenzyme?", "Cofactors are typically inorganic ions such as magnesium, zinc, or iron. Coenzymes are organic molecules, often derived from B vitamins, such as NAD+ from niacin and FAD from riboflavin."),
        ("How do competitive and non-competitive inhibitors differ?", "A competitive inhibitor binds the active site, raising Km while leaving Vmax unchanged, and can be overcome with more substrate. A non-competitive inhibitor binds an allosteric site, lowering Vmax while leaving Km unchanged, and cannot be outcompeted."),
    ],
)

add(
    "enzyme-kinetics-explained",
    "Enzyme Kinetics: Km, Vmax and Michaelis-Menten",
    "What Km and Vmax actually mean, how to read a Michaelis-Menten curve and a Lineweaver-Burk plot, and how inhibitors shift them.",
    "science", "Biochemistry", "Enzyme kinetics: Km, Vmax and Michaelis-Menten",
    "Two constants describe most of what you need to know about how an enzyme behaves — and students routinely mix up what they mean.",
    sec('''      <h2>The Michaelis-Menten equation</h2>
      <div class="panel">
        <h3>v = (V<sub>max</sub> × [S]) / (K<sub>m</sub> + [S])</h3>
        <p>Where <strong>v</strong> is reaction velocity and <strong>[S]</strong> is substrate concentration.</p>
      </div>
      <h2>What the two constants mean</h2>
      <ul class="checklist">
        <li><strong>V<sub>max</sub></strong> — the maximum rate, reached when every enzyme active site is saturated with substrate. Adding more substrate beyond this point does nothing.</li>
        <li><strong>K<sub>m</sub></strong> — the substrate concentration at which the reaction runs at <em>half</em> V<sub>max</sub>. It is an inverse measure of <strong>affinity</strong>: a <em>low</em> K<sub>m</sub> means high affinity, because little substrate is needed to reach half-maximal rate.</li>
      </ul>
      <div class="panel warn">
        <h3>The most common mistake</h3>
        <p>K<sub>m</sub> is not a rate and not a measure of enzyme speed. It has units of concentration. Low K<sub>m</sub> = high affinity is the relationship to memorize, and the inversion trips up more students than any other part of this topic.</p>
      </div>''') +
    sec('''      <h2>Reading the curves</h2>
      <p>The Michaelis-Menten plot (v against [S]) is a hyperbola: steep at low substrate concentration, flattening toward a plateau at V<sub>max</sub>. Because that plateau is approached asymptotically, reading V<sub>max</sub> accurately off it is difficult.</p>
      <p>The <strong>Lineweaver-Burk plot</strong> solves this by plotting 1/v against 1/[S], producing a straight line:</p>
      <ul class="checklist">
        <li><strong>y-intercept</strong> = 1/V<sub>max</sub></li>
        <li><strong>x-intercept</strong> = −1/K<sub>m</sub></li>
        <li><strong>slope</strong> = K<sub>m</sub>/V<sub>max</sub></li>
      </ul>
      <h2>How inhibitors change the plot</h2>
      <table class="data-table">
        <tr><th>Inhibitor</th><th>K<sub>m</sub></th><th>V<sub>max</sub></th><th>Lineweaver-Burk</th></tr>
        <tr><td>Competitive</td><td>Increases</td><td>Unchanged</td><td>Same y-intercept, steeper slope</td></tr>
        <tr><td>Non-competitive</td><td>Unchanged</td><td>Decreases</td><td>Same x-intercept, higher y-intercept</td></tr>
      </table>
      <p>A quick way to identify the type from a plot: if the lines meet on the <em>y</em>-axis it is competitive; if they meet on the <em>x</em>-axis it is non-competitive.</p>''', bg="var(--color-pop4-bg)", tight=True),
    [("enzymes-explained.html", "Enzymes explained"), ("protein-structure-levels.html", "Levels of protein structure"), ("glycolysis-explained.html", "Glycolysis explained")],
    faq=[
        ("What does Km tell you about an enzyme?", "Km is the substrate concentration at which the reaction proceeds at half of Vmax. It is an inverse measure of affinity: a low Km means high affinity, because little substrate is needed to reach half-maximal velocity."),
        ("What is Vmax?", "Vmax is the maximum reaction velocity, reached when all enzyme active sites are saturated with substrate. Beyond that point, adding more substrate does not increase the rate."),
        ("Why use a Lineweaver-Burk plot?", "Plotting 1/v against 1/[S] linearises the hyperbolic Michaelis-Menten curve, making Vmax and Km much easier to read accurately from the intercepts than from the asymptotic plateau."),
    ],
)

add(
    "protein-structure-levels",
    "The Four Levels of Protein Structure",
    "Primary, secondary, tertiary and quaternary structure — the bonds holding each together, and what happens during denaturation.",
    "science", "Biochemistry", "The four levels of protein structure",
    "A protein's function is dictated entirely by its shape, and that shape is built up in four describable stages.",
    sec('''      <h2>The four levels</h2>
      <table class="data-table">
        <tr><th>Level</th><th>What it is</th><th>Held together by</th></tr>
        <tr><td>Primary</td><td>The linear sequence of amino acids</td><td>Peptide (covalent) bonds</td></tr>
        <tr><td>Secondary</td><td>Local folding: α-helices and β-pleated sheets</td><td>Hydrogen bonds along the backbone</td></tr>
        <tr><td>Tertiary</td><td>The overall 3D shape of one polypeptide</td><td>R-group interactions: hydrophobic, hydrogen, ionic, disulfide bridges</td></tr>
        <tr><td>Quaternary</td><td>Two or more polypeptide subunits assembled together</td><td>Same interactions as tertiary, between subunits</td></tr>
      </table>
      <p>Not every protein has quaternary structure — it exists only in multi-subunit proteins. Haemoglobin, with four subunits, is the standard example; myoglobin, with one, has no quaternary structure at all.</p>''') +
    sec('''      <h2>Why primary structure determines everything</h2>
      <p>The sequence of amino acids dictates where hydrophobic residues sit, where disulfide bridges can form, and where charges attract or repel. Change one amino acid and the folding can change. In sickle cell anaemia, a single substitution — valine for glutamic acid at position 6 of the β-globin chain — changes a charged residue to a hydrophobic one, causing haemoglobin to polymerize and distort the red blood cell.</p>
      <div class="panel">
        <h3>Bond strength, ranked</h3>
        <p>Disulfide bridges (covalent) are strongest, followed by ionic bonds, then hydrogen bonds, then hydrophobic interactions. But there are so many weak interactions that collectively they dominate the folded structure.</p>
      </div>''', bg="var(--color-pop4-bg)", tight=True) +
    sec('''      <h2>Denaturation</h2>
      <p>Heat, pH extremes, heavy metals, and organic solvents disrupt the weak interactions maintaining secondary, tertiary and quaternary structure. The <strong>primary structure survives</strong> — peptide bonds are covalent and are not broken by denaturation. This is exactly why a cooked egg white turns solid and opaque but is still protein, and still <a href="complete-vs-incomplete-protein.html">nutritionally complete</a>.</p>
      <p>Denaturation in the stomach is a normal, useful part of digestion: stomach acid unfolds dietary protein so that proteases can reach the peptide bonds. See <a href="how-digestion-works.html">how digestion works</a>.</p>'''),
    [("enzymes-explained.html", "Enzymes explained"), ("complete-vs-incomplete-protein.html", "Complete vs. incomplete protein"), ("how-digestion-works.html", "How digestion works")],
    faq=[
        ("What are the four levels of protein structure?", "Primary is the amino acid sequence held by peptide bonds; secondary is local folding into alpha-helices and beta-sheets held by backbone hydrogen bonds; tertiary is the overall 3D shape of one polypeptide; quaternary is the assembly of multiple subunits."),
        ("Does denaturation break the primary structure?", "No. Denaturation disrupts the weak interactions maintaining secondary, tertiary and quaternary structure, but peptide bonds are covalent and remain intact, so the amino acid sequence is preserved."),
        ("Do all proteins have quaternary structure?", "No. Quaternary structure exists only in proteins made of two or more polypeptide subunits. Haemoglobin has four subunits and therefore has quaternary structure; single-chain myoglobin does not."),
    ],
)

add(
    "insulin-and-glucagon",
    "Insulin and Glucagon: Blood Glucose Control",
    "How insulin and glucagon act as opposing hormones to keep blood glucose stable, their target tissues, and what goes wrong in diabetes.",
    "science", "Physiology", "Insulin and glucagon: blood glucose control",
    "This is the textbook example of negative feedback, and one of the clearest antagonistic hormone pairs in human physiology.",
    sec('''      <h2>The two hormones</h2>
      <table class="data-table">
        <tr><th></th><th>Insulin</th><th>Glucagon</th></tr>
        <tr><td>Secreted by</td><td>Beta cells of the pancreas</td><td>Alpha cells of the pancreas</td></tr>
        <tr><td>Trigger</td><td>High blood glucose</td><td>Low blood glucose</td></tr>
        <tr><td>Overall effect</td><td>Lowers blood glucose</td><td>Raises blood glucose</td></tr>
        <tr><td>Metabolic mode</td><td>Anabolic (storage)</td><td>Catabolic (mobilization)</td></tr>
      </table>
      <p>Both are produced in the islets of Langerhans — an easy detail to lose marks on, since alpha and beta cells are frequently swapped in exam answers. Mnemonic: <strong>I</strong>nsulin comes from <strong>b</strong>eta cells and moves glucose <strong>i</strong>n.</p>''') +
    sec('''      <h2>What insulin does</h2>
      <ul class="checklist">
        <li>Triggers GLUT4 transporters to move to the cell membrane in muscle and fat tissue, allowing glucose uptake</li>
        <li>Stimulates <strong>glycogenesis</strong> — storing glucose as <a href="what-is-glycogen.html">glycogen</a> in liver and muscle</li>
        <li>Stimulates lipogenesis and inhibits fat breakdown</li>
        <li>Promotes amino acid uptake and protein synthesis</li>
      </ul>
      <h2>What glucagon does</h2>
      <ul class="checklist">
        <li>Stimulates <strong>glycogenolysis</strong> — breaking liver glycogen back down into glucose</li>
        <li>Stimulates <strong>gluconeogenesis</strong> — making new glucose from amino acids, lactate and glycerol</li>
        <li>Promotes lipolysis, releasing fatty acids for fuel</li>
      </ul>
      <div class="panel warn">
        <h3>Liver vs. muscle glycogen</h3>
        <p>Only the <em>liver</em> can release glucose back into the bloodstream, because muscle lacks the enzyme glucose-6-phosphatase. Muscle glycogen fuels the muscle that stores it and cannot raise blood glucose for the rest of the body.</p>
      </div>''', bg="var(--color-pop4-bg)", tight=True) +
    sec('''      <h2>When the system fails</h2>
      <p>In <strong>type 1 diabetes</strong>, autoimmune destruction of beta cells means little or no insulin is produced. In <strong>type 2 diabetes</strong>, insulin is produced but target tissues respond poorly to it — insulin resistance — and beta-cell function may decline over time. In both, glucose accumulates in the blood because it cannot be moved into cells efficiently.</p>'''),
    [("what-is-glycogen.html", "What is glycogen?"), ("homeostasis-explained.html", "Homeostasis explained"), ("glycemic-index-explained.html", "The glycemic index")],
    faq=[
        ("Which pancreatic cells make insulin and glucagon?", "Beta cells in the islets of Langerhans secrete insulin in response to high blood glucose. Alpha cells secrete glucagon in response to low blood glucose."),
        ("Why can't muscle glycogen raise blood sugar?", "Muscle lacks glucose-6-phosphatase, the enzyme needed to release free glucose into the bloodstream. Only liver glycogen can be broken down and exported to raise blood glucose for the rest of the body."),
        ("What is the difference between type 1 and type 2 diabetes?", "In type 1, autoimmune destruction of pancreatic beta cells means little or no insulin is produced. In type 2, insulin is produced but tissues respond poorly to it, and beta-cell function may decline over time."),
    ],
)

add(
    "homeostasis-explained",
    "Homeostasis and Negative Feedback Explained",
    "How negative feedback loops keep internal conditions stable, the receptor-control centre-effector model, and how positive feedback differs.",
    "science", "Physiology", "Homeostasis and negative feedback",
    "Homeostasis is the organizing principle of physiology — once you can see the loop, most regulatory systems in the body follow the same shape.",
    sec('''      <h2>The components of a feedback loop</h2>
      <p>Every homeostatic system has the same four parts, and exam answers earn marks for naming them explicitly:</p>
      <ul class="checklist">
        <li><strong>Stimulus</strong> — a change in the variable being regulated</li>
        <li><strong>Receptor / sensor</strong> — detects the change</li>
        <li><strong>Control centre</strong> — compares the value against a set point (often the hypothalamus)</li>
        <li><strong>Effector</strong> — produces the response that opposes the change</li>
      </ul>
      <h2>Negative feedback</h2>
      <p>In negative feedback the response <em>opposes</em> the original stimulus, returning the variable toward its set point. It's the mechanism behind blood glucose control, thermoregulation, blood pressure, blood pH, and osmoregulation. The variable oscillates gently around the set point rather than sitting perfectly still.</p>''') +
    sec('''      <h2>Worked example: thermoregulation</h2>
      <table class="data-table">
        <tr><th></th><th>Too hot</th><th>Too cold</th></tr>
        <tr><td>Blood vessels</td><td>Vasodilation — more heat lost at skin</td><td>Vasoconstriction — heat conserved</td></tr>
        <tr><td>Sweat glands</td><td>Increased sweating, evaporative cooling</td><td>Sweating stops</td></tr>
        <tr><td>Muscle</td><td>—</td><td>Shivering generates heat</td></tr>
        <tr><td>Metabolic rate</td><td>—</td><td>Increases (thyroid, adrenaline)</td></tr>
      </table>''', bg="var(--color-pop4-bg)", tight=True) +
    sec('''      <h2>Positive feedback</h2>
      <p>Positive feedback <em>amplifies</em> the stimulus rather than opposing it, driving the system further from its starting point. It is much rarer, and used where a process needs to run rapidly to completion:</p>
      <ul class="checklist">
        <li><strong>Blood clotting</strong> — activated platelets recruit more platelets</li>
        <li><strong>Childbirth</strong> — oxytocin strengthens contractions, which triggers more oxytocin</li>
        <li><strong>Action potentials</strong> — sodium influx opens further sodium channels</li>
      </ul>
      <div class="panel warn">
        <h3>Frequently confused</h3>
        <p>"Positive" and "negative" describe the <em>direction of the response relative to the stimulus</em>, not whether the outcome is good or bad. Positive feedback is not "beneficial feedback" — uncontrolled positive feedback is often dangerous.</p>
      </div>''', tight=True),
    [("insulin-and-glucagon.html", "Insulin and glucagon"), ("kidney-function-explained.html", "Kidney function explained"), ("electrolytes-explained.html", "Electrolytes explained")],
    faq=[
        ("What are the four components of a feedback loop?", "A stimulus, a receptor that detects the change, a control centre that compares the value against a set point, and an effector that produces the response."),
        ("What is the difference between negative and positive feedback?", "Negative feedback opposes the original stimulus and returns a variable toward its set point. Positive feedback amplifies the stimulus, driving the system further from its starting point, as in blood clotting and childbirth."),
        ("Is positive feedback harmful?", "Not inherently. The terms describe the direction of the response relative to the stimulus, not whether the outcome is desirable. Positive feedback is used where a process must run quickly to completion, though uncontrolled positive feedback can be dangerous."),
    ],
)

add(
    "cell-membrane-transport",
    "Cell Membrane Transport: Passive and Active",
    "Simple and facilitated diffusion, osmosis, primary and secondary active transport, and endocytosis — with the key distinctions exams test.",
    "science", "Cell Biology", "Cell membrane transport: passive and active",
    "The membrane is selectively permeable, and how a substance crosses it depends on its size, charge, and whether the cell is willing to spend ATP.",
    sec('''      <h2>Passive transport — no ATP required</h2>
      <ul class="checklist">
        <li><strong>Simple diffusion</strong> — small, non-polar molecules (O<sub>2</sub>, CO<sub>2</sub>, steroid hormones) pass straight through the phospholipid bilayer, down their concentration gradient.</li>
        <li><strong>Facilitated diffusion</strong> — larger or charged particles (glucose, ions) move down their gradient <em>through a protein</em>. Still passive, still no ATP — the protein provides a route, not a push.</li>
        <li><strong>Osmosis</strong> — the movement of <em>water</em> across a semi-permeable membrane, from higher to lower water potential.</li>
      </ul>
      <div class="panel warn">
        <h3>Facilitated diffusion is not active transport</h3>
        <p>Involving a protein does not make transport active. The distinction is direction and energy: passive transport always moves down a gradient and costs no ATP, regardless of whether a protein is involved.</p>
      </div>''') +
    sec('''      <h2>Active transport — ATP required</h2>
      <ul class="checklist">
        <li><strong>Primary active transport</strong> — directly uses ATP to move substances <em>against</em> their gradient. The sodium-potassium pump is the standard example: 3 Na<sup>+</sup> out, 2 K<sup>+</sup> in, per ATP.</li>
        <li><strong>Secondary active transport (co-transport)</strong> — uses the gradient built by primary active transport rather than ATP directly. Glucose absorption in the small intestine works this way, riding the sodium gradient inward via SGLT1.</li>
      </ul>
      <h2>Bulk transport</h2>
      <p><strong>Endocytosis</strong> brings large material into the cell in a vesicle (phagocytosis for solids, pinocytosis for fluids); <strong>exocytosis</strong> releases material out. Both require ATP.</p>''', bg="var(--color-pop4-bg)", tight=True) +
    sec('''      <h2>Tonicity, quickly</h2>
      <table class="data-table">
        <tr><th>Solution</th><th>Relative solute</th><th>Effect on an animal cell</th></tr>
        <tr><td>Hypotonic</td><td>Lower outside</td><td>Water enters; cell swells and may lyse</td></tr>
        <tr><td>Isotonic</td><td>Equal</td><td>No net movement</td></tr>
        <tr><td>Hypertonic</td><td>Higher outside</td><td>Water leaves; cell shrinks (crenation)</td></tr>
      </table>
      <p>This is why intravenous fluids must be isotonic, and it underlies <a href="hydration-and-performance.html">fluid balance during exercise</a> — including why overdrinking dilutes blood sodium.</p>'''),
    [("kidney-function-explained.html", "Kidney function explained"), ("how-digestion-works.html", "How digestion works"), ("electrolytes-explained.html", "Electrolytes explained")],
    faq=[
        ("Is facilitated diffusion active or passive?", "Passive. It moves substances down their concentration gradient and requires no ATP. The involvement of a transport protein does not make it active; only movement against a gradient using energy does."),
        ("How does the sodium-potassium pump work?", "It is primary active transport, using one ATP to move three sodium ions out of the cell and two potassium ions in, against their concentration gradients."),
        ("What happens to a cell in a hypotonic solution?", "Water moves into the cell because solute concentration is lower outside. An animal cell swells and may burst, a process called lysis."),
    ],
)

add(
    "muscle-contraction-explained",
    "Muscle Contraction: The Sliding Filament Theory",
    "Sarcomere anatomy, the cross-bridge cycle, the role of calcium and ATP, and why rigor mortis happens — a revision guide.",
    "science", "Physiology", "Muscle contraction: the sliding filament theory",
    "Muscles don't shorten because the filaments shorten — they shorten because the filaments slide past one another. That distinction is the whole theory.",
    sec('''      <h2>Sarcomere anatomy</h2>
      <p>The sarcomere is the functional unit of a muscle fibre, running from one Z-line to the next.</p>
      <table class="data-table">
        <tr><th>Region</th><th>Contains</th><th>During contraction</th></tr>
        <tr><td>Z-line</td><td>Anchors thin filaments</td><td>Z-lines move closer together</td></tr>
        <tr><td>I band</td><td>Thin (actin) only</td><td><strong>Shortens</strong></td></tr>
        <tr><td>A band</td><td>Full thick (myosin) length</td><td><strong>Stays the same</strong></td></tr>
        <tr><td>H zone</td><td>Thick only, no overlap</td><td><strong>Shortens</strong></td></tr>
      </table>
      <div class="panel warn">
        <h3>The classic exam question</h3>
        <p>Which band does <em>not</em> change length during contraction? The <strong>A band</strong>. It corresponds to the full length of the myosin filament, and myosin does not shorten — the actin simply slides further over it.</p>
      </div>''') +
    sec('''      <h2>The cross-bridge cycle</h2>
      <ol>
        <li>A nerve impulse triggers <strong>calcium release</strong> from the sarcoplasmic reticulum.</li>
        <li>Ca<sup>2+</sup> binds <strong>troponin</strong>, which shifts <strong>tropomyosin</strong> off the myosin-binding sites on actin.</li>
        <li>The myosin head binds actin, forming a <strong>cross-bridge</strong>.</li>
        <li>The <strong>power stroke</strong>: the head pivots, pulling actin inward, and ADP + P<sub>i</sub> are released.</li>
        <li>A new <strong>ATP</strong> binds myosin, causing it to <em>detach</em> from actin.</li>
        <li>ATP is hydrolysed, re-cocking the head, and the cycle repeats while calcium remains elevated.</li>
      </ol>
      <div class="panel">
        <h3>ATP has two separate jobs here</h3>
        <p>ATP binding causes <em>detachment</em>; ATP hydrolysis <em>re-cocks</em> the head. This is why rigor mortis occurs — with no ATP after death, myosin heads cannot detach from actin, and the muscle locks in place.</p>
      </div>''', bg="var(--color-pop4-bg)", tight=True) +
    sec('''      <h2>Fibre types</h2>
      <p>Which fibres a muscle recruits shapes its fuel demands — slow-twitch fibres rely heavily on oxidative metabolism, fast-twitch fibres on <a href="glycolysis-explained.html">glycolysis</a> and phosphocreatine. See <a href="muscle-fiber-types-and-nutrition.html">muscle fibre types and nutrition</a> and <a href="energy-systems-explained.html">the three energy systems</a>.</p>'''),
    [("muscle-fiber-types-and-nutrition.html", "Muscle fibre types"), ("energy-systems-explained.html", "The three energy systems"), ("atp-explained.html", "What is ATP?")],
    faq=[
        ("Which sarcomere band stays the same length during contraction?", "The A band. It corresponds to the full length of the myosin filament, which does not shorten. The I band and H zone both shorten as actin slides over myosin."),
        ("What is the role of calcium in muscle contraction?", "Calcium binds troponin, which moves tropomyosin away from the myosin-binding sites on actin, allowing cross-bridges to form. Without calcium, those binding sites remain blocked."),
        ("Why does rigor mortis occur?", "ATP is required for myosin heads to detach from actin. After death, ATP production stops, so cross-bridges cannot release and the muscle remains locked in a contracted state."),
    ],
)

add(
    "energy-systems-explained",
    "The Three Energy Systems Explained",
    "The phosphagen, glycolytic and oxidative systems — their fuel, duration, power output, and how they overlap during exercise.",
    "science", "Physiology", "The three energy systems",
    "All three systems run at once. What changes with exercise intensity and duration is which one dominates.",
    sec('''      <h2>Side by side</h2>
      <table class="data-table">
        <tr><th>System</th><th>Fuel</th><th>Duration</th><th>Power</th><th>Oxygen?</th></tr>
        <tr><td>Phosphagen (ATP-PC)</td><td>Stored ATP, creatine phosphate</td><td>~0–10 s</td><td>Highest</td><td>No</td></tr>
        <tr><td>Glycolytic (anaerobic)</td><td>Glucose, muscle glycogen</td><td>~10 s–2 min</td><td>High</td><td>No</td></tr>
        <tr><td>Oxidative (aerobic)</td><td>Carbohydrate, fat, some protein</td><td>2 min onward</td><td>Lowest</td><td>Yes</td></tr>
      </table>
      <p>The trade-off is consistent: the faster a system can produce ATP, the shorter it can sustain that output.</p>''') +
    sec('''      <h2>How each works</h2>
      <ul class="checklist">
        <li><strong>Phosphagen</strong> — creatine phosphate donates a phosphate to ADP, regenerating ATP almost instantly. This is the system <a href="creatine-explained.html">creatine supplementation</a> targets, and it powers a maximal sprint or a heavy set.</li>
        <li><strong>Glycolytic</strong> — <a href="glycolysis-explained.html">glycolysis</a> breaks glucose down to pyruvate, which becomes lactate when demand outpaces oxygen delivery. Fast, but limited.</li>
        <li><strong>Oxidative</strong> — pyruvate and fatty acids enter the <a href="krebs-cycle-explained.html">Krebs cycle</a> and <a href="electron-transport-chain-explained.html">electron transport chain</a>. Far slower to ramp up, but its capacity is enormous.</li>
      </ul>
      <div class="panel warn">
        <h3>Lactate is not the cause of soreness</h3>
        <p>Lactate clears within roughly an hour of exercise, whereas delayed-onset muscle soreness peaks 24–48 hours later. DOMS is associated with mechanical damage and inflammation, not lingering lactate. Lactate is also a usable fuel — the heart and liver take it up readily.</p>
      </div>''', bg="var(--color-pop4-bg)", tight=True) +
    sec('''      <h2>Why fat can't fuel sprinting</h2>
      <p>Fat carries more energy per gram than carbohydrate, but oxidizing it requires more oxygen per unit of ATP and proceeds through more steps. It cannot deliver ATP fast enough for high-intensity effort. This is the physiological reason carbohydrate availability limits high-intensity performance, and why <a href="carb-loading-for-athletes.html">carb loading</a> matters for endurance events.</p>'''),
    [("glycolysis-explained.html", "Glycolysis explained"), ("carb-loading-for-athletes.html", "Carb loading for athletes"), ("creatine-explained.html", "Creatine explained")],
    faq=[
        ("What are the three energy systems?", "The phosphagen (ATP-PC) system for efforts up to about 10 seconds, the glycolytic system for roughly 10 seconds to 2 minutes, and the oxidative (aerobic) system for sustained effort beyond about 2 minutes."),
        ("Does lactic acid cause muscle soreness?", "No. Lactate clears within about an hour of exercise, while delayed-onset muscle soreness peaks 24 to 48 hours later. DOMS is associated with mechanical damage and inflammation rather than lactate."),
        ("Why can't fat fuel high-intensity exercise?", "Oxidising fat requires more oxygen per unit of ATP and involves more metabolic steps than using carbohydrate, so it cannot supply ATP quickly enough to sustain high-intensity effort."),
    ],
)

add(
    "kidney-function-explained",
    "Kidney Function: The Nephron Explained",
    "Filtration, reabsorption and secretion in the nephron, how ADH and aldosterone regulate water and sodium, and how urine is concentrated.",
    "science", "Physiology", "Kidney function: the nephron explained",
    "The kidneys filter your entire blood volume many times a day, then reclaim almost everything they filtered — the reabsorption is the impressive part.",
    sec('''      <h2>Three processes</h2>
      <ul class="checklist">
        <li><strong>Filtration</strong> — at the glomerulus, pressure forces water and small solutes into Bowman's capsule. Blood cells and most proteins are too large to pass, so their presence in urine is a sign of damage.</li>
        <li><strong>Reabsorption</strong> — useful substances are returned to the blood. Around 180 litres are filtered per day but only 1–2 litres leave as urine, meaning over 99% of filtrate is reabsorbed.</li>
        <li><strong>Secretion</strong> — additional wastes, drugs, and excess H<sup>+</sup> or K<sup>+</sup> are actively added to the filtrate.</li>
      </ul>
      <h2>Along the nephron</h2>
      <table class="data-table">
        <tr><th>Segment</th><th>Main job</th></tr>
        <tr><td>Proximal convoluted tubule</td><td>Bulk reabsorption — all glucose and amino acids, most Na<sup>+</sup> and water</td></tr>
        <tr><td>Descending loop of Henle</td><td>Permeable to water only — water leaves, filtrate concentrates</td></tr>
        <tr><td>Ascending loop of Henle</td><td>Impermeable to water — Na<sup>+</sup>/K<sup>+</sup>/Cl<sup>−</sup> pumped out, building the medullary gradient</td></tr>
        <tr><td>Distal convoluted tubule</td><td>Fine-tuning of Na<sup>+</sup>, K<sup>+</sup> and pH, under hormonal control</td></tr>
        <tr><td>Collecting duct</td><td>Final water reabsorption, controlled by ADH</td></tr>
      </table>''') +
    sec('''      <h2>Hormonal control</h2>
      <ul class="checklist">
        <li><strong>ADH (vasopressin)</strong> — released when blood is too concentrated. It inserts aquaporins into the collecting duct, increasing water reabsorption, producing smaller volumes of more concentrated urine. Alcohol suppresses ADH, which is why it is a diuretic — see <a href="alcohol-and-macros.html">alcohol and macros</a>.</li>
        <li><strong>Aldosterone</strong> — released via the renin-angiotensin system when blood pressure or sodium falls. It increases Na<sup>+</sup> reabsorption in the distal tubule, and water follows osmotically.</li>
      </ul>
      <div class="panel">
        <h3>Countercurrent multiplication</h3>
        <p>The loop of Henle establishes a salt gradient in the medulla, becoming saltier with depth. The collecting duct passes back down through that gradient, so water can be drawn out along its whole length. Animals needing highly concentrated urine have notably longer loops.</p>
      </div>''', bg="var(--color-pop4-bg)", tight=True) +
    sec('''      <p>These mechanisms are what make <a href="electrolytes-explained.html">electrolyte balance</a> and <a href="hydration-and-performance.html">hydration</a> physiologically self-correcting for most people under normal conditions.</p>'''),
    [("electrolytes-explained.html", "Electrolytes explained"), ("hydration-and-performance.html", "Hydration and performance"), ("homeostasis-explained.html", "Homeostasis explained")],
    faq=[
        ("What are the three main processes of the nephron?", "Filtration at the glomerulus, reabsorption of useful substances back into the blood, and secretion of additional wastes into the filtrate."),
        ("How much filtrate is reabsorbed?", "Around 180 litres are filtered per day but only 1 to 2 litres are excreted as urine, meaning over 99% of the filtrate is reabsorbed."),
        ("What does ADH do?", "Antidiuretic hormone inserts aquaporins into the collecting duct, increasing water reabsorption and producing a smaller volume of more concentrated urine. Alcohol suppresses ADH, which is why it acts as a diuretic."),
    ],
)

add(
    "beta-oxidation-explained",
    "Beta-Oxidation: How Fat Is Burned for Energy",
    "How fatty acids are broken down into acetyl-CoA — activation, carnitine shuttle, the four repeating steps, and why fat yields more ATP than glucose.",
    "science", "Metabolism", "Beta-oxidation: how fat is burned for energy",
    "Fat is the body's largest energy store, and beta-oxidation is the pathway that converts it into something the Krebs cycle can use.",
    sec('''      <h2>Getting the fatty acid into the mitochondrion</h2>
      <ol>
        <li><strong>Activation</strong> — in the cytosol, the fatty acid is joined to coenzyme A to form fatty acyl-CoA. This costs the equivalent of 2 ATP.</li>
        <li><strong>The carnitine shuttle</strong> — long-chain fatty acyl-CoA cannot cross the inner mitochondrial membrane directly. Carnitine palmitoyltransferase I (CPT-1) transfers it to carnitine for transport, and it is reassembled inside.</li>
      </ol>
      <div class="panel">
        <h3>Why CPT-1 matters</h3>
        <p>CPT-1 is the rate-limiting step of fat oxidation, and it is inhibited by malonyl-CoA — a molecule produced when fatty acid <em>synthesis</em> is active. That reciprocal control prevents the cell from building and breaking down fat simultaneously.</p>
      </div>''') +
    sec('''      <h2>The four repeating steps</h2>
      <p>Each cycle removes two carbons from the fatty acid chain, in the same order every time:</p>
      <ol>
        <li><strong>Oxidation</strong> — produces FADH<sub>2</sub></li>
        <li><strong>Hydration</strong> — water is added across the double bond</li>
        <li><strong>Oxidation</strong> — produces NADH</li>
        <li><strong>Thiolysis</strong> — the chain is cleaved, releasing acetyl-CoA</li>
      </ol>
      <p>A mnemonic that holds: <strong>oxidise, hydrate, oxidise, cleave</strong>. The cycle repeats until the chain is fully converted to acetyl-CoA, which feeds the <a href="krebs-cycle-explained.html">Krebs cycle</a>.</p>
      <h2>Why fat yields more energy</h2>
      <p>Palmitate (16 carbons) undergoes 7 cycles, producing 8 acetyl-CoA, 7 FADH<sub>2</sub>, and 7 NADH — roughly <strong>106 net ATP</strong>, versus about 30–32 for glucose. Fatty acids are far more reduced (more C-H bonds, less oxygen) than carbohydrate, so there are simply more electrons to harvest. That's the same reason fat supplies 9 kcal/g against carbohydrate's 4.</p>''', bg="var(--color-pop4-bg)", tight=True) +
    sec('''      <h2>Where ketones come in</h2>
      <p>When carbohydrate is scarce, oxaloacetate is diverted toward gluconeogenesis, so acetyl-CoA cannot all enter the Krebs cycle. The liver converts the excess into ketone bodies, which other tissues — including the brain — can use. This is the biochemistry underlying <a href="ketogenic-diet-explained.html">the ketogenic diet</a>.</p>'''),
    [("krebs-cycle-explained.html", "The Krebs cycle explained"), ("ketogenic-diet-explained.html", "The ketogenic diet"), ("fats.html", "What fat actually does")],
    faq=[
        ("What are the four steps of beta-oxidation?", "Oxidation producing FADH2, hydration, a second oxidation producing NADH, and thiolysis which cleaves off acetyl-CoA. The cycle repeats until the fatty acid chain is fully converted."),
        ("What is the rate-limiting step of fat oxidation?", "Carnitine palmitoyltransferase I (CPT-1), which transfers long-chain fatty acyl-CoA onto carnitine for transport into the mitochondrion. It is inhibited by malonyl-CoA."),
        ("Why does fat provide more energy than carbohydrate?", "Fatty acids are more reduced, with more carbon-hydrogen bonds and less oxygen, so more electrons can be harvested per gram. This is why fat supplies about 9 kcal/g compared with 4 kcal/g for carbohydrate."),
    ],
)

add(
    "b-vitamins-and-metabolism",
    "B Vitamins as Coenzymes in Metabolism",
    "How each B vitamin functions as a coenzyme in energy metabolism, which pathway it serves, and what deficiency causes.",
    "science", "Biochemistry", "B vitamins as coenzymes in metabolism",
    "B vitamins don't provide energy themselves — they're the coenzymes without which the pathways that release energy cannot run.",
    sec('''      <h2>The coenzyme map</h2>
      <table class="data-table">
        <tr><th>Vitamin</th><th>Coenzyme form</th><th>Role</th><th>Deficiency disease</th></tr>
        <tr><td>B1 (thiamine)</td><td>TPP</td><td>Pyruvate → acetyl-CoA; α-ketoglutarate step</td><td>Beriberi; Wernicke-Korsakoff</td></tr>
        <tr><td>B2 (riboflavin)</td><td>FAD, FMN</td><td>Electron carrier in Krebs and beta-oxidation</td><td>Ariboflavinosis</td></tr>
        <tr><td>B3 (niacin)</td><td>NAD<sup>+</sup>, NADP<sup>+</sup></td><td>Principal electron carrier across metabolism</td><td>Pellagra</td></tr>
        <tr><td>B5 (pantothenic acid)</td><td>Coenzyme A</td><td>Carries acyl groups; forms acetyl-CoA</td><td>Rare</td></tr>
        <tr><td>B6 (pyridoxine)</td><td>PLP</td><td>Amino acid transamination</td><td>Anaemia, neuropathy</td></tr>
        <tr><td>B7 (biotin)</td><td>Biotin</td><td>Carboxylation reactions</td><td>Rare</td></tr>
        <tr><td>B9 (folate)</td><td>THF</td><td>One-carbon transfer; DNA synthesis</td><td>Megaloblastic anaemia; neural tube defects</td></tr>
        <tr><td>B12 (cobalamin)</td><td>Methylcobalamin</td><td>Works with folate; myelin maintenance</td><td>Megaloblastic anaemia; nerve damage</td></tr>
      </table>''') +
    sec('''      <h2>Why deficiency symptoms are so broad</h2>
      <p>Because these coenzymes serve many enzymes across many pathways at once, deficiency rarely produces one isolated symptom. Fatigue is near-universal, since energy metabolism itself is impaired. Neurological symptoms are also common — nervous tissue has high metabolic demand and little capacity to compensate.</p>
      <div class="panel warn">
        <h3>The folate and B12 trap</h3>
        <p>High folate intake can correct the anaemia of B12 deficiency while the neurological damage continues unchecked — the blood picture normalizes, but nerve damage progresses and can become irreversible. This is why B12 status matters independently, particularly on a <a href="vitamin-b12-and-vegan-diets.html">vegan diet</a>.</p>
      </div>''', bg="var(--color-pop4-bg)", tight=True) +
    sec('''      <h2>Water-soluble, with a caveat</h2>
      <p>Most B vitamins are water-soluble and excess is excreted, so toxicity is uncommon — but not impossible. High-dose B6 supplementation over long periods can cause peripheral neuropathy, and B12 is stored in the liver for years, which is why deficiency there develops slowly. See <a href="fat-soluble-vitamins-explained.html">fat-soluble vitamins</a> for the contrast.</p>'''),
    [("enzymes-explained.html", "Enzymes explained"), ("vitamin-b12-and-vegan-diets.html", "B12 on a vegan diet"), ("micronutrients-vs-macronutrients.html", "Micronutrients vs. macronutrients")],
    faq=[
        ("Do B vitamins give you energy?", "Not directly. They contain no calories. They act as coenzymes that allow the pathways releasing energy from carbohydrate, fat, and protein to function, so deficiency causes fatigue but supplementation does not add energy when status is already adequate."),
        ("Which B vitamin becomes NAD+?", "Niacin (vitamin B3) forms NAD+ and NADP+, the principal electron carriers used throughout glycolysis, the Krebs cycle, and beta-oxidation."),
        ("Why is taking folate without B12 a problem?", "Folate can correct the megaloblastic anaemia caused by B12 deficiency while the neurological damage continues undetected. Masking the blood abnormality allows nerve damage to progress and potentially become irreversible."),
    ],
)

# --------------------------------------------------------- HEALTH LITERACY BATCH --

add(
    "antioxidants-and-free-radicals",
    "Antioxidants and Free Radicals Explained",
    "What free radicals and oxidative stress are, how antioxidants work, and why antioxidant supplements haven't lived up to the food-based evidence.",
    "science", "Biochemistry", "Antioxidants and free radicals explained",
    "Antioxidants get marketed like a superpower. The biochemistry behind them is real — the supplement claims built on top of it mostly aren't.",
    sec('''      <h2>What a free radical actually is</h2>
      <p>A free radical is a molecule with an unpaired electron, which makes it unstable and reactive. To stabilize itself, it steals an electron from a nearby molecule — DNA, a protein, a cell membrane lipid — which creates a new free radical and can trigger a damaging chain reaction. This process is called oxidative stress when it outpaces the body's ability to neutralize it.</p>
      <p>Free radicals aren't purely a problem to eliminate: your immune cells deliberately generate them to destroy pathogens, and cell signaling relies on them in small amounts. The issue is <em>excess</em>, from sources like UV exposure, air pollution, smoking, and normal metabolic byproducts.</p>''') +
    sec('''      <h2>How antioxidants work</h2>
      <p>An antioxidant is a molecule that can donate an electron to a free radical without becoming unstable itself, ending the chain reaction. Vitamin C, vitamin E, beta-carotene, and selenium are the best-studied dietary antioxidants, alongside plant compounds like flavonoids and polyphenols found in berries, tea, and colorful vegetables.<sup class="ref"><a href="sources.html#health1">[1]</a></sup></p>
      <div class="panel warn">
        <h3>Why supplement trials disappointed</h3>
        <p>Despite strong observational links between antioxidant-rich <em>diets</em> and lower disease risk, large randomized trials of concentrated antioxidant <em>supplements</em> (particularly high-dose beta-carotene and vitamin E) have repeatedly failed to reduce disease risk, and in a few cases showed harm. The leading explanation: food-based antioxidants arrive alongside fiber, hundreds of other plant compounds, and a different absorption pattern than an isolated, concentrated pill — the whole-food package appears to matter, not just the isolated molecule.<sup class="ref"><a href="sources.html#health1">[1]</a></sup></p>
      </div>''', bg="var(--color-pop4-bg)", tight=True) +
    sec('''      <p>The practical takeaway most researchers converge on: get antioxidants from a varied diet of fruits, vegetables, nuts, and tea rather than from high-dose isolated supplements. See <a href="vitamin-c-and-immunity.html">vitamin C</a> and <a href="fat-soluble-vitamins-explained.html">vitamin E's fat-soluble relatives</a> for the individual nutrients.</p>'''),
    [("vitamin-c-and-immunity.html", "Vitamin C and immunity"), ("fiber-and-gut-microbiome.html", "Fiber and your gut microbiome"), ("ultra-processed-foods-explained.html", "Ultra-processed foods")],
    faq=[
        ("Do antioxidant supplements prevent disease?", "Large randomized trials of concentrated antioxidant supplements, particularly high-dose beta-carotene and vitamin E, have generally failed to reduce disease risk despite strong observational links between antioxidant-rich diets and lower risk."),
        ("What is oxidative stress?", "Oxidative stress occurs when free radicals — reactive molecules with an unpaired electron — outpace the body's ability to neutralize them, potentially damaging DNA, proteins, and cell membranes."),
        ("Are free radicals always bad?", "No. Immune cells deliberately produce free radicals to destroy pathogens, and they play a role in normal cell signaling. Problems arise from excess, driven by sources like UV exposure, pollution, and smoking."),
    ],
)

add(
    "probiotics-and-gut-health",
    "Probiotics Explained: What the Evidence Supports",
    "What probiotics are, which strains have real evidence behind them, and where the science is still too new to justify strong claims.",
    "science", "Physiology", "Probiotics explained: what the evidence supports",
    "\"Probiotic\" is a broad label covering everything from clinically tested strains to yogurt cups with a marketing sticker.",
    sec('''      <h2>What counts as a probiotic</h2>
      <p>A probiotic is a live microorganism that, administered in adequate amounts, confers a health benefit. That definition is strain-specific — evidence for one strain of <em>Lactobacillus</em> doesn't automatically apply to a different strain, even within the same species. This is the single most misunderstood part of probiotic marketing.<sup class="ref"><a href="sources.html#health2">[1]</a></sup></p>
      <h2>Where the evidence is strongest</h2>
      <ul class="checklist">
        <li><strong>Antibiotic-associated diarrhea</strong> — certain strains modestly reduce incidence when taken alongside antibiotics</li>
        <li><strong>Some forms of infectious diarrhea</strong>, particularly in children — moderate evidence for reduced duration</li>
        <li><strong>Certain IBS symptom patterns</strong> — mixed but promising for specific strains</li>
      </ul>''') +
    sec('''      <h2>Where the evidence is weaker</h2>
      <p>Broad claims about "boosting immunity" or "detoxing" outrun what strain-specific trials actually show. Effects tend to be modest, strain-specific, and often don't replicate cleanly across studies — a common pattern in a young and fast-moving research area.<sup class="ref"><a href="sources.html#health2">[1]</a></sup></p>
      <div class="panel">
        <h3>Food sources vs. supplements</h3>
        <p>Fermented foods — yogurt with live cultures, kefir, sauerkraut, kimchi, miso — deliver live bacteria alongside genuine nutritional value, though the specific strains and doses are far less standardized than in a clinical supplement. Both are reasonable; neither is a cure-all.</p>
      </div>
      <p>Feeding the bacteria you already have — via fiber — has a stronger and broader evidence base than adding new ones. See <a href="fiber-and-gut-microbiome.html">fiber and your gut microbiome</a>.</p>''', bg="var(--color-pop4-bg)", tight=True),
    [("fiber-and-gut-microbiome.html", "Fiber and your gut microbiome"), ("how-digestion-works.html", "How digestion works"), ("ultra-processed-foods-explained.html", "Ultra-processed foods")],
    faq=[
        ("Are all probiotics the same?", "No. Evidence is strain-specific — a benefit shown for one strain doesn't automatically apply to a different strain, even within the same bacterial species. This is the most commonly overlooked detail in probiotic marketing."),
        ("What health benefits do probiotics have the strongest evidence for?", "The best-supported uses are reducing antibiotic-associated diarrhea and shortening some forms of infectious diarrhea, particularly in children. Broader immunity claims have much weaker support."),
        ("Are fermented foods as good as probiotic supplements?", "Fermented foods like yogurt, kefir, and sauerkraut deliver live bacteria along with real nutritional value, but strains and doses are far less standardized than in a clinical-grade supplement. Both are reasonable choices."),
    ],
)

add(
    "understanding-a-lipid-panel",
    "Understanding a Lipid Panel",
    "What a cholesterol blood test actually measures, what the numbers mean, and how diet realistically moves each one.",
    "general", "Health Literacy", "Understanding a lipid panel",
    "A standard lipid panel reports four numbers. Knowing what each one represents makes the results far less mysterious.",
    sec('''      <h2>The four numbers</h2>
      <table class="data-table">
        <tr><th>Marker</th><th>What it is</th><th>General target</th></tr>
        <tr><td>Total cholesterol</td><td>Sum of all cholesterol carried in the blood</td><td>Below 200 mg/dL</td></tr>
        <tr><td>LDL ("bad")</td><td>Low-density lipoprotein — deposits cholesterol into artery walls</td><td>Below 100 mg/dL</td></tr>
        <tr><td>HDL ("good")</td><td>High-density lipoprotein — carries cholesterol back to the liver for removal</td><td>Above 40 mg/dL (men), 50 mg/dL (women)</td></tr>
        <tr><td>Triglycerides</td><td>The main storage form of fat in blood, from excess calories of any kind</td><td>Below 150 mg/dL</td></tr>
      </table>
      <p>These are general reference ranges from the American Heart Association; your own targets should come from your doctor, since risk depends on more than a single number.<sup class="ref"><a href="sources.html#health4">[1]</a></sup></p>''') +
    sec('''      <h2>Why "LDL" and "HDL" aren't literally cholesterol types</h2>
      <p>Cholesterol itself is one molecule — LDL and HDL are the <em>carriers</em> that transport it through the bloodstream, since cholesterol doesn't dissolve in blood on its own. LDL tends to deposit cholesterol into artery walls, contributing to plaque buildup; HDL tends to remove it. That's the biological basis for calling one "bad" and the other "good," though the full picture involves particle size and number too.</p>
      <div class="panel">
        <h3>What actually moves each number</h3>
        <ul class="checklist">
          <li><strong>LDL</strong> — most reduced by lowering saturated fat and replacing it with unsaturated fat; see <a href="saturated-vs-unsaturated-fat.html">saturated vs. unsaturated fat</a></li>
          <li><strong>HDL</strong> — modestly raised by regular aerobic exercise and unsaturated fat; lowered by smoking</li>
          <li><strong>Triglycerides</strong> — most responsive to excess calories, added sugar, and alcohol, more than dietary fat specifically</li>
        </ul>
      </div>''', bg="var(--color-fat-bg)", tight=True) +
    sec('''      <p>Dietary cholesterol itself (from eggs, shellfish) has a smaller effect on blood cholesterol for most people than once believed — see <a href="egg-yolks-cholesterol-myth.html">the egg yolks and cholesterol myth</a> and <a href="cholesterol-explained.html">dietary vs. blood cholesterol</a> for the full distinction.</p>'''),
    [("cholesterol-explained.html", "Dietary vs. blood cholesterol"), ("saturated-vs-unsaturated-fat.html", "Saturated vs. unsaturated fat"), ("egg-yolks-cholesterol-myth.html", "Egg yolks and cholesterol")],
    faq=[
        ("What is a good LDL level?", "The American Heart Association generally targets LDL below 100 mg/dL, though individual targets vary based on overall cardiovascular risk and should be set with a doctor."),
        ("What's the difference between LDL and HDL?", "Both are carriers that transport cholesterol through the blood. LDL tends to deposit cholesterol into artery walls, contributing to plaque; HDL tends to carry it back to the liver for removal — the basis for calling them 'bad' and 'good' cholesterol."),
        ("What raises triglycerides the most?", "Triglycerides respond most strongly to excess calories, added sugar, and alcohol — more than to dietary fat specifically."),
    ],
)

add(
    "nutrition-during-pregnancy",
    "Nutrition During Pregnancy: Key Nutrients",
    "How calorie and nutrient needs shift during pregnancy, which nutrients need the most deliberate attention, and what changes by trimester.",
    "general", "Health Literacy", "Nutrition during pregnancy",
    "Pregnancy doesn't mean \"eating for two\" in the literal sense — the actual changes are more specific and, for some nutrients, much larger than a simple calorie bump.",
    sec('''      <h2>Calories: a smaller increase than people expect</h2>
      <p>Additional calorie needs are modest and trimester-specific: roughly none in the first trimester, about 340 extra calories/day in the second, and about 450 extra/day in the third, for someone starting at a healthy weight.<sup class="ref"><a href="sources.html#health5">[1]</a></sup> "Eating for two" as a doubling of intake overstates the real requirement substantially.</p>
      <h2>The nutrients that matter most</h2>
      <table class="data-table">
        <tr><th>Nutrient</th><th>Why it matters more now</th></tr>
        <tr><td>Folate</td><td>Reduces neural tube defect risk; needs are highest very early, often before pregnancy is confirmed</td></tr>
        <tr><td>Iron</td><td>Blood volume expands substantially; requirement roughly triples to 27 mg/day</td></tr>
        <tr><td>Protein</td><td>Supports fetal tissue growth and expanding maternal blood volume</td></tr>
        <tr><td>Choline</td><td>Supports fetal brain development; commonly under-consumed even outside pregnancy</td></tr>
        <tr><td>DHA (omega-3)</td><td>Structural fat in fetal brain and eye development</td></tr>
      </table>''') +
    sec('''      <div class="panel warn">
        <h3>Why folate timing matters so much</h3>
        <p>The neural tube forms in the first 3-4 weeks after conception — often before a person knows they're pregnant. This is why folic acid supplementation is recommended for anyone who could become pregnant, not just after a positive test.<sup class="ref"><a href="sources.html#health6">[1]</a></sup></p>
      </div>
      <h2>What to avoid or limit</h2>
      <ul class="checklist">
        <li><strong>Alcohol</strong> — no amount has been established as safe during pregnancy</li>
        <li><strong>High-mercury fish</strong> — shark, swordfish, king mackerel; lower-mercury fish like salmon are still recommended for their DHA</li>
        <li><strong>Unpasteurized dairy and undercooked meat/eggs</strong> — listeria and other foodborne illness risk is higher during pregnancy</li>
      </ul>''', bg="var(--color-carbs-bg)", tight=True) +
    sec('''      <p>This is general education, not individualized guidance — prenatal nutrition should be discussed with an OB-GYN or midwife, who can account for your specific health history.</p>'''),
    [("iron-deficiency-and-athletes.html", "Iron deficiency"), ("b-vitamins-and-metabolism.html", "B vitamins as coenzymes"), ("protein-intake-for-women.html", "Protein intake for women")],
    faq=[
        ("How many extra calories do you need during pregnancy?", "Roughly none in the first trimester, about 340 extra per day in the second, and about 450 extra per day in the third, for someone starting at a healthy weight — far less than 'eating for two' implies."),
        ("Why is folate so important early in pregnancy?", "The neural tube forms in the first 3-4 weeks after conception, often before pregnancy is confirmed, which is why folic acid is recommended for anyone who could become pregnant, not just after a positive test."),
        ("How much does iron need increase during pregnancy?", "The RDA roughly triples, from 18 mg/day to 27 mg/day, to support the substantial expansion in blood volume during pregnancy."),
    ],
)

add(
    "nutrition-for-children-and-teens",
    "Nutrition for Children and Teens",
    "How nutrient needs for children and teenagers differ from adults, why growth spurts change requirements, and common gaps to watch for.",
    "general", "Health Literacy", "Nutrition for children and teens",
    "Kids aren't small adults nutritionally — growth itself creates demands that don't exist once growth has finished.",
    sec('''      <h2>Why growth changes the math</h2>
      <p>Children and teens are building new tissue, not just maintaining existing tissue, which raises requirements for protein, calcium, iron, and calories relative to body size — particularly during growth spurts. Needs also shift noticeably at puberty, with the increase generally larger and later for boys than girls due to differing growth timelines.<sup class="ref"><a href="sources.html#health7">[1]</a></sup></p>
      <h2>Nutrients commonly falling short</h2>
      <table class="data-table">
        <tr><th>Nutrient</th><th>Why gaps are common</th></tr>
        <tr><td>Calcium</td><td>Peak bone mass is built by the end of adolescence; low intake here has lifelong effects</td></tr>
        <tr><td>Iron</td><td>Growth demand plus, after menarche, menstrual losses in girls</td></tr>
        <tr><td>Fiber</td><td>Diets skew toward refined, low-fiber packaged foods</td></tr>
        <tr><td>Vitamin D</td><td>Same risk factors as adults — limited sun exposure, few dietary sources</td></tr>
      </table>''') +
    sec('''      <h2>What actually helps, practically</h2>
      <ul class="checklist">
        <li><strong>Regular meals and snacks</strong> — smaller stomach capacity relative to needs means kids often need to eat more frequently than adults to meet requirements</li>
        <li><strong>Modeling, not lecturing</strong> — children's food preferences form substantially through repeated exposure and watching what adults around them eat</li>
        <li><strong>Limiting sugary drinks specifically</strong> — one of the highest-leverage single changes, given how much added sugar in kids' diets comes from beverages</li>
      </ul>
      <div class="panel">
        <h3>Growth charts, not adult BMI categories</h3>
        <p>Pediatric growth is tracked against age- and sex-specific percentile charts, not adult BMI cutoffs, because normal, healthy growth trajectories vary considerably by age and stage of development.</p>
      </div>''', bg="var(--color-protein-bg)", tight=True),
    [("calcium-and-bone-health.html", "Calcium and bone health"), ("added-sugar-vs-natural-sugar.html", "Added vs. natural sugar"), ("iron-deficiency-and-athletes.html", "Iron deficiency")],
    faq=[
        ("Do children need more protein relative to their size than adults?", "Yes, relative to body weight, because they're actively building new tissue rather than just maintaining it. Requirements also rise further during growth spurts and puberty."),
        ("Why is calcium intake so important in childhood and adolescence?", "Peak bone mass is built by the end of adolescence, and low calcium intake during these years can have effects on bone density that persist for life."),
        ("What's the single highest-leverage dietary change for kids?", "Limiting sugary drinks specifically, since they contribute a disproportionate share of added sugar in children's diets and are one of the more straightforward things to change."),
    ],
)

add(
    "extended-fasting-and-omad",
    "Extended Fasting and OMAD: What the Evidence Says",
    "How extended fasts and one-meal-a-day eating differ from standard intermittent fasting, what the research supports, and the real risks.",
    "diets", "Diets", "Extended fasting and OMAD explained",
    "Compressing all your food into one meal or going days without eating is a different proposition than a 16-hour overnight fast — the evidence base is thinner, and the risks are real.",
    sec('''      <h2>Where this differs from standard intermittent fasting</h2>
      <p>Common <a href="intermittent-fasting-and-macros.html">intermittent fasting</a> protocols (16:8, for instance) mostly compress eating into a shorter window without necessarily reducing total food eaten. <strong>OMAD</strong> (one meal a day) and <strong>extended fasting</strong> (24+ hours without food) go further — and the evidence quality drops accordingly, with far fewer controlled human trials than for standard time-restricted eating.</p>
      <h2>What OMAD tends to do</h2>
      <ul class="checklist">
        <li><strong>Makes hitting protein and micronutrient targets harder</strong> — fitting 100g+ of protein and a full day's micronutrients into one sitting is a real practical challenge</li>
        <li><strong>Often reduces total calories</strong> — simply through the difficulty of eating a full day's calories in one meal, which is frequently the actual mechanism behind any weight loss, not something metabolically special about meal frequency</li>
        <li><strong>Can affect blood sugar regulation</strong> — a very large single meal produces a bigger glucose and insulin response than the same calories spread across the day</li>
      </ul>''') +
    sec('''      <h2>Extended fasting (24+ hours)</h2>
      <p>Multi-day fasting shows some evidence for short-term metabolic markers in small studies, but longer fasts carry real risks: electrolyte imbalances, gallstones (from prolonged periods without gallbladder stimulation), and — critically — muscle loss, since the body draws on protein for gluconeogenesis once glycogen is depleted.<sup class="ref"><a href="sources.html#health8">[1]</a></sup></p>
      <div class="panel warn">
        <h3>Who should avoid this entirely</h3>
        <p>People who are pregnant or breastfeeding, have a history of disordered eating, are underweight, have diabetes on medication, or have any condition requiring regular food intake should not attempt extended fasting without direct medical supervision.<sup class="ref"><a href="sources.html#health8">[1]</a></sup></p>
      </div>''', bg="var(--color-pop3-bg)", tight=True) +
    sec('''      <p>For most people pursuing fat loss or metabolic health, standard time-restricted eating has a stronger evidence base and a much lower risk profile than OMAD or multi-day fasting. See <a href="intermittent-fasting-and-macros.html">intermittent fasting and macros</a>.</p>'''),
    [("intermittent-fasting-and-macros.html", "Intermittent fasting and macros"), ("metabolic-damage-is-it-real.html", "Is metabolic damage real?"), ("how-to-track-your-macros.html", "How to track your macros")],
    faq=[
        ("Is OMAD better than spreading meals across the day?", "Not inherently. Any weight loss from OMAD is generally attributed to eating fewer total calories, since fitting a full day's food into one meal is difficult — not to a special metabolic effect of meal frequency."),
        ("What are the risks of extended fasting?", "Multi-day fasts carry risks including electrolyte imbalances, gallstones, and muscle loss, since the body turns to protein for gluconeogenesis once glycogen stores are depleted."),
        ("Who should avoid extended fasting?", "People who are pregnant or breastfeeding, have a history of disordered eating, are underweight, take diabetes medication, or have conditions requiring regular food intake should not attempt extended fasting without medical supervision."),
    ],
)

add(
    "supplement-label-terms-explained",
    "Supplement Label Terms: What They Actually Mean",
    "What terms like proprietary blend, %DV, and third-party tested actually mean on a supplement label, and which ones matter.",
    "general", "Health Literacy", "Supplement label terms explained",
    "Supplement labels use precise regulatory language that reads like marketing. Knowing what each term legally requires changes how you read the label.",
    sec('''      <h2>Terms with real regulatory meaning</h2>
      <ul class="checklist">
        <li><strong>%DV (% Daily Value)</strong> — the percentage of a standardized reference intake in one serving. Useful for comparison, though the reference values are general population targets, not individualized.</li>
        <li><strong>USP Verified / NSF Certified</strong> — third-party testing marks confirming the product contains what the label claims, in the stated amount, without specific contaminants. These are the most meaningful quality signals on a supplement label, because supplements themselves aren't FDA-approved for efficacy before sale.<sup class="ref"><a href="sources.html#health9">[1]</a></sup></li>
        <li><strong>"This statement has not been evaluated by the FDA..."</strong> — required by law on structure/function claims (e.g., "supports immune health"). It signals the claim hasn't been independently verified, not that the product is necessarily ineffective.</li>
      </ul>''') +
    sec('''      <h2>The term worth watching closely</h2>
      <div class="panel warn">
        <h3>"Proprietary blend"</h3>
        <p>This lets a manufacturer list a combined weight for several ingredients without disclosing how much of <em>each individual</em> ingredient is included. A blend might contain a clinically studied dose of one ingredient and a token amount of another, and there's no way to tell from the label alone. Products that list each ingredient's exact individual amount are more transparent by definition.<sup class="ref"><a href="sources.html#health9">[1]</a></sup></p>
      </div>
      <h2>What "natural" and "clinically proven" don't guarantee</h2>
      <p>Neither term has a strict, enforced legal definition on supplement labels the way "USP Verified" does. "Natural" says nothing about dose, safety, or effectiveness — plenty of natural substances are potent or harmful in the wrong amount. "Clinically proven" can refer to a single small trial, not a robust evidence base.</p>''', bg="var(--color-fat-bg)", tight=True) +
    sec('''      <p>For specific supplements with genuine evidence behind them, see <a href="creatine-explained.html">creatine</a> and <a href="caffeine-and-athletic-performance.html">caffeine</a> — two of the few with strong, consistent research support.</p>'''),
    [("creatine-explained.html", "Creatine explained"), ("collagen-supplements-explained.html", "Do collagen supplements work?"), ("caffeine-and-athletic-performance.html", "Caffeine and performance")],
    faq=[
        ("What does a 'proprietary blend' hide on a supplement label?", "It lets a manufacturer list a combined weight for several ingredients without disclosing how much of each individual ingredient is included, making it impossible to know if a key ingredient is present in a meaningful dose."),
        ("What do USP Verified or NSF Certified marks mean?", "They indicate third-party testing confirmed the product contains what the label claims in the stated amount, without specified contaminants — among the most meaningful quality signals available, since supplements aren't FDA-approved for efficacy before sale."),
        ("Does 'natural' mean a supplement is safe?", "No. The term has no strict legal definition on supplement labels and says nothing about dose, safety, or effectiveness. Many natural substances are potent or harmful in the wrong amount."),
    ],
)

add(
    "metabolic-syndrome-explained",
    "Metabolic Syndrome: The Five Risk Factors",
    "What metabolic syndrome is, the five diagnostic criteria, and which dietary changes have the strongest evidence for reversing it.",
    "general", "Health Literacy", "Metabolic syndrome: the five risk factors",
    "Metabolic syndrome isn't one disease — it's a cluster of risk factors that, together, substantially raise the risk of heart disease and type 2 diabetes.",
    sec('''      <h2>The five criteria</h2>
      <p>Metabolic syndrome is diagnosed when a person has three or more of the following:<sup class="ref"><a href="sources.html#health10">[1]</a></sup></p>
      <table class="data-table">
        <tr><th>Factor</th><th>Threshold</th></tr>
        <tr><td>Waist circumference</td><td>≥40 in (men), ≥35 in (women)</td></tr>
        <tr><td>Triglycerides</td><td>≥150 mg/dL (or on medication for it)</td></tr>
        <tr><td>HDL cholesterol</td><td>&lt;40 mg/dL (men), &lt;50 mg/dL (women)</td></tr>
        <tr><td>Blood pressure</td><td>≥130/85 mmHg (or on medication for it)</td></tr>
        <tr><td>Fasting blood glucose</td><td>≥100 mg/dL (or on medication for it)</td></tr>
      </table>
      <p>Each factor individually raises risk; having several together raises it more than the sum of the parts would suggest, which is exactly why they're tracked as a cluster.</p>''') +
    sec('''      <h2>What drives it</h2>
      <p>Insulin resistance sits at the center of most cases — cells respond less efficiently to insulin, so the pancreas produces more to compensate, which contributes to several of the five factors simultaneously. Excess visceral fat (the fat around abdominal organs, reflected in waist circumference) is both a cause and a consequence of that resistance.<sup class="ref"><a href="sources.html#health10">[1]</a></sup> See <a href="insulin-and-glucagon.html">insulin and glucagon</a> for the underlying physiology.</p>
      <div class="panel">
        <h3>What has the strongest evidence for reversing it</h3>
        <ul class="checklist">
          <li><strong>Modest weight loss</strong> — even 5-10% of body weight measurably improves multiple factors at once</li>
          <li><strong>Regular physical activity</strong> — improves insulin sensitivity independent of weight change</li>
          <li><strong>A <a href="mediterranean-diet-explained.html">Mediterranean-style diet</a></strong> — the dietary pattern with the strongest trial evidence for this specific cluster</li>
          <li><strong>Reducing added sugar and refined carbohydrate</strong> — most directly targets triglycerides and blood glucose</li>
        </ul>
      </div>''', bg="var(--color-carbs-bg)", tight=True),
    [("insulin-and-glucagon.html", "Insulin and glucagon"), ("understanding-a-lipid-panel.html", "Understanding a lipid panel"), ("mediterranean-diet-explained.html", "The Mediterranean diet")],
    faq=[
        ("How many risk factors are needed to diagnose metabolic syndrome?", "Three or more of five: elevated waist circumference, high triglycerides, low HDL cholesterol, high blood pressure, and elevated fasting blood glucose."),
        ("What causes metabolic syndrome?", "Insulin resistance sits at the center of most cases, often accompanied by excess visceral fat around the abdominal organs, which is both a cause and consequence of that resistance."),
        ("What's most effective for reversing metabolic syndrome?", "Modest weight loss of 5-10% of body weight, regular physical activity, a Mediterranean-style dietary pattern, and reducing added sugar and refined carbohydrate all have strong supporting evidence."),
    ],
)

def main():
    for a in ARTICLES:
        html = page(a["slug"], a["title"], a["meta"], a["category"],
                    a["eyebrow"], a["h1"], a["intro"], a["body"], a["related"], extra_head=a["extra_head"])
        path = os.path.join(ROOT, f'{a["slug"]}.html')
        with open(path, "w") as f:
            f.write(html)
        print("wrote", path)
    print(f"\n{len(ARTICLES)} articles generated.")
    build_hub()
    build_404()
    build_about()
    build_privacy()
    build_contact()
    build_terms()
    build_sitemap()
    return ARTICLES


if __name__ == "__main__":
    main()
