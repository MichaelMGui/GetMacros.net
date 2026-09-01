"""Integrate the five editorial journal posts into site discovery surfaces."""

from pathlib import Path
import html
import re

ROOT = Path(__file__).resolve().parents[1]

POSTS = [
    ("best-fast-food-restaurants-for-your-goals.html", "Which fast-food restaurant fits your goal?", "Compare chains for high protein, cutting, bulking, fiber and plant-based meals without declaring one universal winner."),
    ("how-much-protein-can-your-body-absorb.html", "How much protein can your body absorb at once?", "Separate digestion from muscle protein synthesis—and retire the 30-gram absorption myth."),
    ("are-diet-drinks-bad-for-you.html", "Are diet drinks bad for you?", "Understand sweetener safety, weight-control evidence and what the drink is replacing."),
    ("does-creatine-cause-hair-loss.html", "Does creatine cause hair loss?", "See what changed when a 2025 trial measured hair follicles instead of only hormones."),
    ("calories-vs-macros-what-matters-more.html", "Calories vs. macros: what matters more?", "Use a clear priority order for weight change, muscle, fullness and performance."),
]

JOURNAL_SECTION = '<section class="guide-group data-section"><div class="container"><div class="section-head"><p class="eyebrow">Featured guides</p><h2>Five questions worth a closer look</h2><p>Evidence-aware stories with a direct answer, visible limitations and a practical next step.</p></div><div class="guide-grid">' + "".join(
    f'<a class="guide-card" href="{path}"><h3>{title}</h3><p>{description}</p></a>'
    for path, title, description in POSTS
) + '</div><p><a class="btn btn-primary" href="blog.html">Visit the GetMacros Journal</a></p></div></section>'


def write_if_changed(path: Path, text: str) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if current != text:
        path.write_text(text, encoding="utf-8", newline="")


def update_articles() -> None:
    path = ROOT / "articles.html"
    text = path.read_text(encoding="utf-8")
    if "Five questions worth a closer look" not in text:
        marker = '<section class="guide-group"><div class="container"><div class="section-head"><h2>Macros and goals</h2>'
        text = text.replace(marker, JOURNAL_SECTION + marker, 1)
    text = re.sub(r'("numberOfItems"\s*:\s*)79\b', r'\g<1>84', text)
    write_if_changed(path, text)


def update_home() -> None:
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    marker = '</a></div></div></section>\n<section class="story-section">'
    replacement = '</a></div><p><a class="btn btn-primary" href="blog.html">Read the GetMacros Journal</a></p></div></section>\n<section class="story-section">'
    if "Read the GetMacros Journal" not in text:
        text = text.replace(marker, replacement, 1)
    write_if_changed(path, text)


def update_search() -> None:
    path = ROOT / "search.html"
    text = path.read_text(encoding="utf-8")
    entries = [("blog.html", "The GetMacros Journal", "Evidence-aware stories about restaurant choices, protein, supplements, diet drinks and practical macro questions.")] + POSTS
    cards = "".join(
        '<article class="result-card" data-search="' + html.escape((title + " " + description + " journal nutrition evidence").lower(), quote=True) + '">' +
        f'<span>Journal</span><h2><a href="{target}">{html.escape(title)}</a></h2><p>{html.escape(description)}</p></article>'
        for target, title, description in entries
    )
    if 'href="blog.html">The GetMacros Journal</a></h2>' not in text:
        text = text.replace('</div></section></main>', cards + '</div></section></main>', 1)
    count = len(re.findall(r'class="result-card"', text))
    text = re.sub(r'Showing \d+ resources', f'Showing {count} resources', text, count=1)
    write_if_changed(path, text)


def update_sitemap() -> None:
    pages = []
    for path in sorted(ROOT.glob("*.html")):
        text = path.read_text(encoding="utf-8")
        robots = re.search(r'<meta[^>]+name="robots"[^>]+content="([^"]+)"', text, re.I)
        if robots and "noindex" in robots.group(1).lower():
            continue
        url = "https://getmacros.net/" if path.name == "index.html" else "https://getmacros.net/" + path.name
        pages.append(url)
    body = "\n".join(f"  <url><loc>{url}</loc></url>" for url in pages)
    write_if_changed(ROOT / "sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + '\n</urlset>\n')


def update_feed() -> None:
    path = ROOT / "feed.xml"
    text = path.read_text(encoding="utf-8")
    items = "".join(
        f'<item><title>{html.escape(title)}</title><link>https://getmacros.net/{target}</link><guid>https://getmacros.net/{target}</guid><pubDate>Thu, 27 Aug 2026 12:00:00 GMT</pubDate><description>{html.escape(description)}</description></item>'
        for target, title, description in POSTS
    )
    if "best-fast-food-restaurants-for-your-goals.html" not in text:
        text = text.replace("</description>", "</description>" + items, 1)
    write_if_changed(path, text)


def sync_social_metadata() -> None:
    targets = ["blog.html"] + [target for target, _, _ in POSTS]
    for name in targets:
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        title = re.search(r'<title>(.*?)</title>', text, re.I | re.S).group(1)
        description = re.search(r'<meta name="description" content="([^"]+)">', text, re.I).group(1)
        canonical = re.search(r'<link rel="canonical" href="([^"]+)">', text, re.I).group(1)
        text = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{title}">', text)
        text = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{description}">', text)
        text = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{canonical}">', text)
        text = re.sub(r'<meta name="twitter:title" content="[^"]*">', '', text)
        text = re.sub(r'<meta name="twitter:description" content="[^"]*">', '', text)
        marker = '<meta name="twitter:card" content="summary_large_image">'
        text = text.replace(marker, marker + f'<meta name="twitter:title" content="{title}"><meta name="twitter:description" content="{description}">', 1)
        write_if_changed(path, text)


def main() -> None:
    update_articles()
    update_home()
    update_search()
    update_sitemap()
    update_feed()
    sync_social_metadata()
    print("Integrated the journal into articles, home, search, sitemap and RSS.")


if __name__ == "__main__":
    main()
