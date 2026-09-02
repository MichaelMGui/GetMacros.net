"""Apply the Studio v6 product system and rebuild the homepage hierarchy."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
VERSION = "20260828c"

LIBRARY_CONTROLS = '''<section class="gm6-library-controls"><div class="container gm6-library-search"><label for="article-library-search">Find a useful guide<input id="article-library-search" type="search" placeholder="Try protein, weight loss, labels or meal prep" autocomplete="off"></label><p id="library-search-status" aria-live="polite">Showing a curated selection from each topic.</p></div></section>'''

HOME_MAIN = r'''<main id="main-content">
<section class="home-intro" data-spotlight>
  <div class="container home-intro-grid">
    <div class="home-intro-copy">
      <p class="home-kicker"><span>Free healthy fast food finder</span><b>83 meals across 15 chains</b></p>
      <h1>Healthy fast food, <em>matched to your goals.</em></h1>
      <p class="home-intro-lede">GetMacros is a free restaurant meal finder. Answer five quick questions about your goals, appetite and dietary needs. We rank real meals from 15 chains and explain which options fit you best.</p>
      <div class="home-intro-actions">
        <a class="btn home-primary" href="restaurant-meal-finder.html">Find my best meal <span aria-hidden="true">↗</span></a>
        <a class="home-text-link" href="restaurant-meal-guides.html">Browse the 15 restaurants <span aria-hidden="true">→</span></a>
      </div>
      <ul class="home-signals" aria-label="How GetMacros helps">
        <li><span>01</span><b>Choose your nutrition goals</b></li>
        <li><span>02</span><b>We rank real restaurant meals</b></li>
        <li><span>03</span><b>See why every match fits</b></li>
      </ul>
    </div>
    <aside class="order-console" aria-label="Example result from the Healthy Fast Food Finder" data-console>
      <div class="order-console-rail" aria-hidden="true"><b>GM</b><span></span><small>01 / 03</small></div>
      <div class="order-console-body">
        <header class="order-console-head"><span><i></i> Healthy Fast Food Finder</span><b>High protein + bulking</b></header>
        <div class="order-console-ticket">
          <p>Your match / Chick-fil-A</p>
          <h2>Grilled nuggets, waffle fries &amp; fruit</h2>
          <div class="order-console-macros">
            <span><small>Calories</small><strong>1,050</strong></span>
            <span><small>Protein</small><strong>104<em>g</em></strong></span>
            <span><small>Fiber</small><strong>10<em>g</em></strong></span>
            <span><small>Sodium</small><strong>1,950<em>mg</em></strong></span>
          </div>
        </div>
        <div class="order-console-reason"><span aria-hidden="true">✓</span><p><b>Why it matched</b>High energy and exceptional protein for a serious bulking meal. Sodium stays visible, not hidden.</p></div>
        <div class="order-console-foot"><span>83 real meals compared</span><a href="restaurant-meal-finder.html">Find my meal <span aria-hidden="true">→</span></a></div>
      </div>
    </aside>
  </div>
</section>

<section class="gm6-trust-strip" aria-label="How GetMacros works">
  <div class="container gm6-trust-inner">
    <p>Useful numbers. Clear limits. No “perfect food” claims.</p>
    <span class="gm6-trust-point"><i aria-hidden="true">01</i>Official chain nutrition sources</span>
    <span class="gm6-trust-point"><i aria-hidden="true">02</i>Missing values stay missing</span>
    <span class="gm6-trust-point"><i aria-hidden="true">03</i>Goals change the ranking</span>
  </div>
</section>

<section class="gm6-finder-showcase">
  <div class="container">
    <div class="gm6-section-intro studio-reveal">
      <div><p class="eyebrow">Healthy Order Match</p><h2>Find meals for your goals.</h2></div>
      <div><p>Combine goals such as high protein and bulking, or cutting and lower sodium. See why each match fits.</p></div>
    </div>
    <div class="gm6-finder-shell studio-reveal" data-spotlight>
      <div class="gm6-finder-copy">
        <p class="eyebrow">Five quick questions</p>
        <h3>Get five meals ranked for you.</h3>
        <p>Results use published restaurant nutrition data.</p>
        <ol class="gm6-flow"><li>Choose your goals</li><li>Set dietary needs and appetite</li><li>Select nearby restaurants</li><li>Compare your matches</li></ol>
        <a class="btn btn-primary" href="restaurant-meal-finder.html">Build my shortlist <span class="gm6-arrow" aria-hidden="true">→</span></a>
      </div>
      <div class="gm6-finder-preview" aria-label="Healthy Order Match question preview">
        <span class="gm6-question">Question 1 of 5</span>
        <h3>What are you working toward?</h3>
        <div class="gm6-choice-grid">
          <div class="gm6-choice is-selected"><b>High protein</b><small>25 g or more</small></div>
          <div class="gm6-choice is-selected"><b>Bulking</b><small>600+ calories</small></div>
          <div class="gm6-choice"><b>Higher fiber</b><small>5 g or more</small></div>
          <div class="gm6-choice"><b>Lower sodium</b><small>Published values only</small></div>
        </div>
        <div class="gm6-preview-result"><strong>12 meals fit both selected goals</strong><span>Continue →</span></div>
      </div>
    </div>
  </div>
</section>

<section class="gm6-goal-story">
  <div class="container">
    <div class="gm6-section-intro studio-reveal">
      <div><p class="eyebrow">The goal changes the answer</p><h2>Healthy is not one number.</h2></div>
      <div><p>Scroll through the priorities people actually bring to a restaurant. The strongest meal changes as the job changes.</p></div>
    </div>
    <div class="gm6-story-grid">
      <aside class="gm6-story-visual" aria-live="polite">
        <span class="gm6-story-label">Current lens</span>
        <h3 data-story-title>High protein</h3>
        <p data-story-copy>Prioritize protein while calories, fiber and sodium remain visible.</p>
        <div class="gm6-story-number"><strong data-story-number>112</strong><span>g protein at the top</span></div>
        <div class="gm6-story-meter" aria-hidden="true"><i></i></div>
      </aside>
      <div class="gm6-story-steps">
        <article class="gm6-story-step" data-title="High protein" data-copy="Prioritize protein while calories, fiber and sodium remain visible." data-number="112" data-width="92%"><span>01 · Protein</span><h3>Make every calorie work harder.</h3><p>Useful for muscle gain, recovery, or simply building a more filling order. Rankings never hide the energy cost.</p></article>
        <article class="gm6-story-step" data-title="Lower calorie" data-copy="Find substantial entrées without filling the list with tiny sides." data-number="275" data-width="38%"><span>02 · Cutting</span><h3>Keep the meal. Lower the total.</h3><p>We separate real meals from apple slices and side vegetables so a low number still represents a practical order.</p></article>
        <article class="gm6-story-step" data-title="Bulking" data-copy="Surface large meals that also deliver meaningful protein." data-number="1,595" data-width="100%"><span>03 · Energy</span><h3>Some days need a bigger plate.</h3><p>Higher-calorie options reach well beyond 1,000 calories for people intentionally eating in a surplus.</p></article>
        <article class="gm6-story-step" data-title="Higher fiber" data-copy="Find beans, grains and vegetables where the chain publishes fiber." data-number="18" data-width="66%"><span>04 · Fiber</span><h3>Look beyond protein alone.</h3><p>Fiber can distinguish two meals with similar calories and protein. Missing data never becomes a fake zero.</p></article>
        <article class="gm6-story-step" data-title="Lower sodium" data-copy="Rank only substantial meals with a published sodium value." data-number="450" data-width="46%"><span>05 · Sodium</span><h3>Use the number with context.</h3><p>Restaurant meals often run high in sodium. We show it plainly and never make a medical promise.</p></article>
      </div>
    </div>
  </div>
</section>


<section class="gm6-compare">
  <div class="container">
    <div class="gm6-section-intro studio-reveal"><div><p class="eyebrow">Meal comparison</p><h2>Compare meals at a glance.</h2></div><div><p>Review calories, protein and fiber side by side.</p></div></div>
    <div class="gm6-compare-shell studio-reveal" tabindex="0" role="region" aria-label="Meal nutrition comparison">
      <div class="gm6-compare-head"><strong>Meal</strong><strong>Calories</strong><strong>Protein</strong><strong>Fiber</strong></div>
      <div class="gm6-compare-row"><div class="gm6-compare-meal"><strong>Chicken Bowl, rice &amp; beans</strong><small>Chipotle</small></div><span class="gm6-compare-value">650</span><span class="gm6-compare-value is-protein">48 g</span><span class="gm6-compare-value">14 g</span></div>
      <div class="gm6-compare-row"><div class="gm6-compare-meal"><strong>Egg White Grill</strong><small>Chick-fil-A</small></div><span class="gm6-compare-value">290</span><span class="gm6-compare-value is-protein">26 g</span><span class="gm6-compare-value">1 g</span></div>
      <div class="gm6-compare-row"><div class="gm6-compare-meal"><strong>Footlong Rotisserie Chicken</strong><small>Subway</small></div><span class="gm6-compare-value">640</span><span class="gm6-compare-value is-protein">58 g</span><span class="gm6-compare-value">8 g</span></div>
    </div>
    <p class="gm6-compare-hint">Swipe the table to see protein and fiber.</p>
  </div>
</section>

<section class="gm6-calculator">
  <div class="container gm6-calculator-shell">
    <div class="gm6-calculator-copy studio-reveal">
      <p class="eyebrow">Free Macro Calculator</p>
      <h2>Calculate your daily macros.</h2>
      <p>Estimate calories, protein, carbs and fat, then use those targets in the meal finder.</p>
      <a class="btn btn-outline" href="calculators.html">Open the full calculator</a>
    </div>
    <form id="home-macro-form" class="home-calc-form gm6-home-form studio-reveal">
      <div class="compact-fields">
        <div><label for="hc-age">Age</label><input id="hc-age" name="age" type="number" min="18" max="100" value="30" required></div>
        <div><label for="hc-sex">Equation sex</label><select id="hc-sex" name="sex"><option value="male">Male</option><option value="female">Female</option></select></div>
        <div><label for="hc-weight">Weight (lb)</label><input id="hc-weight" name="weight" type="number" min="66" max="660" value="170" required></div>
        <div><label for="hc-height">Height (in)</label><input id="hc-height" name="height" type="number" min="48" max="90" value="69" required></div>
        <div class="span-two"><label for="hc-activity">Activity</label><select id="hc-activity" name="activity"><option value="1.2">Mostly sitting</option><option value="1.375">Light activity</option><option value="1.55" selected>Moderate activity</option><option value="1.725">High activity</option><option value="1.9">Very high activity</option></select></div>
        <div class="span-two"><label for="hc-goal">Goal</label><select id="hc-goal" name="goal"><option value="lose">Lose weight</option><option value="recomp">Lose fat + build muscle</option><option value="maintain" selected>Maintain weight</option><option value="gain">Gain weight + build muscle</option></select></div>
      </div>
      <button class="calc-submit" type="submit">Get my free macro estimate</button>
      <p id="hc-error" class="calc-error" hidden></p>
      <div id="hc-results" class="home-calc-results" hidden aria-live="polite"><div class="result-head"><span>Estimated daily target</span><strong id="hc-calories">—</strong><small>calories</small></div><div class="result-macros"><span><b id="hc-protein">—</b>protein</span><span><b id="hc-carbs">—</b>carbs</span><span><b id="hc-fat">—</b>fat</span></div><p id="hc-context"></p><a class="text-link result-meal-link" href="restaurant-meal-finder.html">Find a restaurant meal for these targets →</a></div>
      <p class="calc-fineprint">Educational estimate for generally healthy adults. It may not fit pregnancy, growth, illness or eating-disorder recovery.</p>
    </form>
  </div>
</section>

<section class="gm6-tools gm6-tools-joined" id="tools" aria-labelledby="home-tools-title">
  <div class="container">
    <div class="gm6-tools-head">
      <div><p class="eyebrow">Free nutrition tools</p><h2 id="home-tools-title">Pick a tool. Get a clear answer.</h2><p>Calculate daily targets, compare labels or plan a meal. No account required.</p></div>
      <a class="gm6-tools-all" href="calculators.html">View all nine tools <span aria-hidden="true">→</span></a>
    </div>
    <div class="gm6-tool-bento">
      <a class="gm6-tool studio-reveal" href="calculators.html"><span class="gm6-tool-num">01 · Start here</span><div><h3>Free Macro Calculator</h3><p>Estimate calories, protein, carbs and fat for your goal.</p></div><span class="gm6-tool-icon"><svg aria-hidden="true"><use href="icon-sprite.svg#icon-calculator"></use></svg></span><span class="gm6-tool-arrow" aria-hidden="true">→</span></a>
      <a class="gm6-tool studio-reveal" href="nutrition-label-comparison-tool.html"><span class="gm6-tool-num">02 · Compare</span><div><h3>Compare labels</h3><p>Put two foods side by side.</p></div><span class="gm6-tool-arrow" aria-hidden="true">→</span></a>
      <a class="gm6-tool studio-reveal" href="recipe-macro-scaler.html"><span class="gm6-tool-num">03 · Cook</span><div><h3>Scale a recipe</h3><p>Change servings without redoing the math.</p></div><span class="gm6-tool-arrow" aria-hidden="true">→</span></a>
      <a class="gm6-tool studio-reveal" href="protein-value-calculator.html"><span class="gm6-tool-num">04 · Shop</span><div><h3>Protein value</h3><p>Compare price per gram of protein.</p></div><span class="gm6-tool-arrow" aria-hidden="true">→</span></a>
      <a class="gm6-tool studio-reveal" href="budget-meal-builder.html"><span class="gm6-tool-num">05 · Plan</span><div><h3>Budget meals</h3><p>Build a meal around cost and macros.</p></div><span class="gm6-tool-arrow" aria-hidden="true">→</span></a>
    </div>
  </div>
</section>

<section class="gm6-learning">
  <div class="container">
    <div class="gm6-section-intro studio-reveal"><div><p class="eyebrow">Nutrition guides</p><h2>Practical answers, clearly explained.</h2></div><div><p>Learn about protein, calorie targets, food labels and common supplement questions.</p></div></div>
    <div class="gm6-learning-grid">
      <a class="gm6-editorial studio-reveal" href="best-fast-food-restaurants-for-your-goals.html"><small>Restaurant decisions · 8 min</small><h3>Which fast-food restaurant fits your goal?</h3><p>Compare chains without pretending one winner works for everyone.</p></a>
      <div class="gm6-reading-list">
        <a class="gm6-reading-link studio-reveal" href="how-much-protein-can-your-body-absorb.html"><small>Protein · 7 min</small><h3>How much protein can your body absorb at once?</h3><span>Read the evidence →</span></a>
        <a class="gm6-reading-link studio-reveal" href="macros-for-weight-loss.html"><small>Goals · 6 min</small><h3>Macros for weight loss</h3><span>Read the guide →</span></a>
        <a class="gm6-reading-link studio-reveal" href="how-many-calories-should-i-eat-a-day.html"><small>Calorie targets · 6 min</small><h3>How many calories should I eat a day?</h3><span>Work out your number →</span></a>
      </div>
      <div class="gm6-reading-list">
        <a class="gm6-reading-link studio-reveal" href="does-creatine-cause-hair-loss.html"><small>Supplements · 7 min</small><h3>Does creatine cause hair loss?</h3><span>See what changed →</span></a>
        <a class="gm6-reading-link studio-reveal" href="how-to-read-a-nutrition-label.html"><small>Food labels · 8 min</small><h3>How to read a nutrition label</h3><span>Read the guide →</span></a>
        <a class="gm6-reading-link studio-reveal" href="what-are-macros.html"><small>Macro basics · 5 min</small><h3>What are macros, in plain English?</h3><span>Start here →</span></a>
      </div>
    </div>
  </div>
</section>

<section class="gm6-method">
  <div class="container gm6-method-grid">
    <div class="studio-reveal"><p class="eyebrow">Data you can check</p><h2>See the source behind each number.</h2><p>Menus and portions change. We publish sources, review dates and corrections so you can judge the data.</p><a class="text-link" href="editorial-policy.html">Read the editorial standards →</a></div>
    <div class="gm6-method-points studio-reveal"><div><strong>Published sources</strong><span>Menu figures trace back to each restaurant’s current nutrition information.</span></div><div><strong>Visible dates</strong><span>Restaurant guides state when the source was last checked.</span></div><div><strong>Missing stays missing</strong><span>An unpublished sodium or fiber value never becomes zero.</span></div><div><strong>Corrections welcome</strong><span>Material errors have a clear reporting and correction path.</span></div></div>
  </div>
</section>

<section class="gm6-final">
  <div class="container studio-reveal"><p class="eyebrow">Ready when the menu is</p><h2>Find the meal that fits today.</h2><p>Choose your goals, appetite, dietary needs and available restaurants. Get a shortlist you can actually order.</p><div class="gm6-hero-actions"><a class="btn btn-primary" href="restaurant-meal-finder.html">Start Healthy Order Match <span class="gm6-arrow" aria-hidden="true">→</span></a><a class="btn btn-outline" href="healthy-fast-food.html">Explore all restaurants</a></div></div>
</section>
</main>'''

# Homepage order, applied as one pass so each step does not depend on a section
# an earlier step may have removed. Two rewrites here silently stopped matching
# when the section they anchored to was deleted, which put the goal story back
# and dropped the tools bento entirely.


def _drop_section(markup: str, name: str) -> str:
    """Remove one top-level <section class="NAME ..."> block from the homepage."""
    match = re.search(
        r'\n<section class="' + re.escape(name) + r'(?:[ "][^>]*)?>.*?\n</section>\n',
        markup, re.S)
    return markup[:match.start()] + "\n" + markup[match.end():] if match else markup


def _extract_section(markup: str, name: str):
    match = re.search(
        r'\n<section class="' + re.escape(name) + r'(?:[ "][^>]*)?>.*?\n</section>\n',
        markup, re.S)
    if not match:
        return markup, ""
    return markup[:match.start()] + "\n" + markup[match.end():], match.group(0).strip("\n")


# The scrolling goal story repeated what Healthy Order Match already does and
# depended on a fragile sticky animation.
HOME_MAIN = _drop_section(HOME_MAIN, "gm6-goal-story")

# The restaurant explorer was a third route to pages the navigation and the
# finder results already reach, sitting directly under two sections that send
# you to them.
HOME_MAIN = _drop_section(HOME_MAIN, "gm6-restaurants")

# The final banner repeated the same finder call-to-action already presented
# in the hero and product section without adding new information.
HOME_MAIN = _drop_section(HOME_MAIN, "gm6-final")

# Keep the homepage focused on two immediate jobs: finding a restaurant meal
# and opening a useful calculator. These sections repeated the same promise,
# previewed a non-interactive quiz, or added methodology before the visitor had
# chosen a task.
for _redundant_home_section in (
        "gm6-trust-strip", "gm6-finder-showcase", "gm6-compare",
        "gm6-calculator", "gm6-method"):
    HOME_MAIN = _drop_section(HOME_MAIN, _redundant_home_section)
HOME_MAIN = re.sub(
    r'\n\s*<ul class="home-signals".*?</ul>', "", HOME_MAIN, flags=re.S)

# The tools bento sat seventh, so the clearest statement of what the site gives
# you was three screens down. It moves directly under the hero and shares its
# ground, so opening the site shows the offer and every tool that delivers it
# in one view.
HOME_MAIN, _tools = _extract_section(HOME_MAIN, "gm6-tools")
if _tools:
    anchor = re.search(r'\n(?=<section class="gm6-trust-strip")', HOME_MAIN)
    if anchor:
        HOME_MAIN = HOME_MAIN[:anchor.start()] + "\n" + _tools + "\n" + HOME_MAIN[anchor.start():]

# The homepage is now intentionally hand-composed around three real entry
# points. Preserve that reviewed markup instead of reviving the retired demo
# ticket and hidden prototype sections when this maintenance script is rerun.
_current_home = (ROOT / "index.html").read_text(encoding="utf-8")
_current_main = re.search(r'<main id="main-content">[\s\S]*?</main>', _current_home)
if _current_main:
    HOME_MAIN = _current_main.group(0)

RESTAURANT_FILES = {
    "cava-healthy-meals-macros.html", "chick-fil-a-healthy-meals-macros.html",
    "chipotle-healthy-meals-macros.html", "dunkin-healthy-breakfast-macros.html",
    "jersey-mikes-healthy-subs-macros.html", "kfc-healthy-meals-macros.html",
    "mcdonalds-healthy-meals-macros.html", "panda-express-healthy-meals-macros.html",
    "panera-healthy-meals-macros.html", "popeyes-healthy-meals-macros.html",
    "starbucks-healthy-food-meals-macros.html", "subway-healthy-meals-macros.html",
    "sweetgreen-healthy-meals-macros.html", "taco-bell-healthy-meals-macros.html",
    "wendys-healthy-meals-macros.html",
}

TOOL_FILES = {
    "calculators.html", "recipe-macro-scaler.html", "nutrition-label-comparison-tool.html",
    "protein-value-calculator.html", "budget-meal-builder.html", "sodium-label-comparison-tool.html",
    "carbohydrate-label-portion-tool.html", "weight-goal-timeline-calculator.html",
    "sweat-rate-calculator.html",
}

LIBRARY_FILES = {"articles.html", "blog.html", "search.html", "restaurant-meal-guides.html"}

def add_body_class(html: str, class_name: str) -> str:
    match = re.search(r'<body class="([^"]*)"', html)
    if not match:
        return html
    classes = match.group(1).split()
    if class_name not in classes:
        classes.append(class_name)
    return html[:match.start(1)] + " ".join(classes) + html[match.end(1):]

def apply_page(path: Path) -> bool:
    html = path.read_text(encoding="utf-8")
    original = html
    name = path.name.lower()

    html = re.sub(r'<link rel="stylesheet" href="css/studio-v6\.css\?v=[^"]+">', '', html)
    html = re.sub(r'<script src="js/studio-v6\.js\?v=[^"]+" defer></script>', '', html)
    html = html.replace("</head>", f'<link rel="stylesheet" href="css/studio-v6.css?v={VERSION}"></head>')
    html = html.replace("</body>", f'<script src="js/studio-v6.js?v={VERSION}" defer></script></body>')

    if name == "index.html":
        html = re.sub(r'<main id="main-content">[\s\S]*?</main>', HOME_MAIN, html, count=1)
        html = add_body_class(html, "home-studio")
    elif name == "healthy-fast-food.html":
        html = add_body_class(html, "flagship-page")
    elif name == "restaurant-meal-finder.html":
        html = add_body_class(html, "meal-finder-page")
    elif name in RESTAURANT_FILES:
        html = add_body_class(html, "restaurant-page")
    elif name in TOOL_FILES:
        html = add_body_class(html, "tools-page")
    elif name in LIBRARY_FILES:
        html = add_body_class(html, "library-page")

    if name == "articles.html":
        if 'id="article-library-search"' not in html:
            html = html.replace('</section><section class="guide-group data-section">', f'</section>{LIBRARY_CONTROLS}<section class="guide-group data-section">', 1)
        if 'js/article-library.js' not in html:
            html = html.replace('</body>', '<script src="js/article-library.js?v=20260827b" defer></script></body>')

    hero_h1 = re.search(r'(<(?:section|header)[^>]*(?:hero|Hero)[^>]*>[\s\S]{0,5000}?<h1)([^>]*>)', html)
    if hero_h1 and "data-reveal-title" not in hero_h1.group(0):
        html = html[:hero_h1.start(2)] + ' data-reveal-title' + html[hero_h1.start(2):]

    if html != original:
        path.write_text(html, encoding="utf-8", newline="\n")
        return True
    return False

changed = sum(apply_page(path) for path in ROOT.glob("*.html"))
print(f"Applied Studio v6 to {changed} pages.")
