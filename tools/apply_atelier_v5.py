"""Apply the shared GetMacros Atelier v5 shell to every HTML page.

The script is intentionally idempotent. It replaces only the shared header and
footer contracts and ensures the finishing CSS/JS assets are loaded once.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
VERSION = "20260827b"

HEADER = """<header class="site-header modern-header"><nav class="full-nav" aria-label="Main navigation">
<a class="modern-brand" href="index.html" aria-label="GetMacros.net home"><span class="brand-mark" aria-hidden="true">G</span><span>GetMacros<span class="brand-dot">.</span></span></a>
<div class="full-nav-links" id="primary-navigation">
<div class="nav-group"><button class="nav-group-trigger" type="button" aria-expanded="false">Eat Out</button><div class="nav-popover">
<a href="healthy-fast-food.html"><svg aria-hidden="true"><use href="icon-sprite.svg#icon-rice-bowl"></use></svg><strong>Healthy Fast Food</strong><small>Browse practical chain picks</small></a>
<a href="restaurant-meal-finder.html"><svg aria-hidden="true"><use href="icon-sprite.svg#icon-target"></use></svg><strong>Healthy Order Match</strong><small>Five questions, ranked meals</small></a>
<a href="restaurant-meal-guides.html"><svg aria-hidden="true"><use href="icon-sprite.svg#icon-document"></use></svg><strong>Restaurant Guides</strong><small>Compare all tracked chains</small></a>
</div></div>
<div class="nav-group"><button class="nav-group-trigger" type="button" aria-expanded="false">Tools</button><div class="nav-popover">
<a href="calculators.html"><svg aria-hidden="true"><use href="icon-sprite.svg#icon-calculator"></use></svg><strong>Free Macro Calculator</strong><small>Estimate calories and macros</small></a>
<a href="recipe-macro-scaler.html"><svg aria-hidden="true"><use href="icon-sprite.svg#icon-carbs"></use></svg><strong>Recipe Macro Scaler</strong><small>Recalculate portions</small></a>
<a href="nutrition-label-comparison-tool.html"><svg aria-hidden="true"><use href="icon-sprite.svg#icon-document"></use></svg><strong>Compare Labels</strong><small>See foods side by side</small></a>
</div></div>
<div class="nav-group"><button class="nav-group-trigger" type="button" aria-expanded="false">Learn</button><div class="nav-popover">
<a href="articles.html"><svg aria-hidden="true"><use href="icon-sprite.svg#icon-book"></use></svg><strong>Nutrition Guides</strong><small>Clear, practical explainers</small></a>
<a href="blog.html"><svg aria-hidden="true"><use href="icon-sprite.svg#icon-article"></use></svg><strong>The GetMacros Journal</strong><small>New evidence and ideas</small></a>
<a href="high-protein-foods-list.html"><svg aria-hidden="true"><use href="icon-sprite.svg#icon-protein"></use></svg><strong>High-Protein Foods</strong><small>Compare useful choices</small></a>
</div></div>
<a class="nav-direct" href="about.html">About</a>
<a class="nav-mobile-search" href="search.html">Search GetMacros</a>
</div>
<div class="nav-utility">
<button class="theme-toggle" type="button" data-theme-toggle aria-pressed="false" aria-label="Switch to dark theme"><span class="theme-icon" aria-hidden="true"><svg class="theme-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M20.2 14.2A8.4 8.4 0 0 1 9.8 3.8a8.4 8.4 0 1 0 10.4 10.4Z"/></svg><svg class="theme-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4.1"/><path d="M12 2.4v2.3M12 19.3v2.3M4.2 4.2l1.7 1.7M18.1 18.1l1.7 1.7M2.4 12h2.3M19.3 12h2.3M4.2 19.8l1.7-1.7M18.1 5.9l1.7-1.7"/></svg></span><span class="theme-label">Dark</span></button>
<a class="nav-action" href="search.html" aria-label="Search GetMacros">Search</a>
<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="primary-navigation"><span class="sr-only">Open site menu</span><span class="nav-toggle-lines" aria-hidden="true"><i></i><i></i><i></i></span></button>
</div>
</nav>
<p class="site-purpose"><span>Free tool: find fast-food meals that fit your goal &mdash; 15 chains, no sign-up.</span> <a href="restaurant-meal-finder.html">Find my meal <span aria-hidden="true">&rarr;</span></a></p>
</header>"""

FOOTER = """<footer class="modern-footer">
<div><a class="modern-brand footer-brand" href="index.html"><span class="brand-mark" aria-hidden="true">G</span><span>GetMacros<span class="brand-dot">.</span></span></a><p>Find fast-food meals that fit your calories, protein and goals—then understand the numbers.</p></div>
<div><strong>Use GetMacros</strong><a href="healthy-fast-food.html">Healthy fast food</a><a href="restaurant-meal-finder.html">Healthy Order Match</a><a href="calculators.html">Free macro calculator</a><a href="search.html">Search</a></div>
<div><strong>Read</strong><a href="articles.html">Nutrition guides</a><a href="blog.html">The GetMacros Journal</a><a href="restaurant-meal-guides.html">Restaurant guides</a><a href="sources.html">Sources</a></div>
<div><strong>About &amp; legal</strong><a href="about.html">About</a><a href="editorial-policy.html">Editorial policy</a><a href="corrections.html">Corrections</a><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a><a href="accessibility.html">Accessibility</a><a href="contact.html">Contact</a></div>
<small>&copy; 2026 GetMacros.net &middot; Educational information, not individualized medical advice.</small>
</footer>"""


def convert_newlines(value: str, newline: str) -> str:
    return value.replace("\n", newline)


def apply(path: Path) -> bool:
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    original = text

    text = re.sub(
        r'<header class="site-header modern-header">.*?</header>',
        convert_newlines(HEADER, newline),
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r'<footer class="modern-footer">.*?</footer>',
        convert_newlines(FOOTER, newline),
        text,
        count=1,
        flags=re.DOTALL,
    )

    css = f'<link rel="stylesheet" href="css/atelier-v5.css?v={VERSION}">'
    js = f'<script src="js/atelier-v5.js?v={VERSION}" defer></script>'
    text = re.sub(r'<link rel="stylesheet" href="css/atelier-v5\.css\?v=[^"]+">', '', text)
    text = re.sub(r'<script src="js/atelier-v5\.js\?v=[^"]+" defer></script>', '', text)
    text = re.sub(r'js/polish\.js\?v=[0-9a-z]+', f'js/polish.js?v={VERSION}', text)
    text = text.replace("</head>", css + "</head>", 1)
    text = text.replace("</body>", js + "</body>", 1)
    text = re.sub(r'<meta name="theme-color" content="#[0-9a-fA-F]{6}">', '<meta name="theme-color" content="#f4f7f2">', text)

    if text == original:
        return False
    path.write_bytes(text.encode("utf-8"))
    return True


def main() -> None:
    changed = [path.name for path in sorted(ROOT.glob("*.html")) if apply(path)]
    print(f"Applied Atelier v5 to {len(changed)} pages.")


if __name__ == "__main__":
    main()
