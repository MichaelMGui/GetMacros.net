#!/usr/bin/env python3
"""One-off migration: put every hand-authored page on the site-v3 visual system.

The generated pages come from the four generate_*.py scripts. This covers the
remaining standalone pages so nothing depends on runtime nav/footer patching.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
ASSET_VERSION = "20260816i"

NAV = (
    '<header class="site-header modern-header"><nav class="full-nav" aria-label="Main navigation">'
    '<a class="modern-brand" href="index.html" aria-label="GetMacros.net home">'
    '<span class="brand-mark" aria-hidden="true">G</span><span>GetMacros<span class="brand-dot">.</span></span></a>'
    '<div class="full-nav-links">'
    '<a href="index.html">Home</a><a href="articles.html">Articles</a>'
    '<a href="calculators.html">Calculators</a><a href="quiz.html">Quizzes &amp; Games</a>'
    '<a href="healthy-fast-food.html">Healthy Fast Food</a><a href="glossary.html">Glossary</a>'
    '<a href="sources.html">Sources</a><a href="search.html">Search</a>'
    '<a href="contact.html">Contact</a></div>'
    '<div class="lang-switch"><a href="index.html" aria-current="page">EN</a>'
    '<a href="es/">ES</a><a href="fr/">FR</a></div>'
    '<a class="nav-action" href="restaurant-meal-finder.html">Find my meal</a>'
    "</nav></header>"
)

FOOTER = (
    '<footer class="modern-footer">'
    '<div><a class="modern-brand footer-brand" href="index.html">'
    '<span class="brand-mark" aria-hidden="true">G</span><span>GetMacros<span class="brand-dot">.</span></span></a>'
    "<p>Clear nutrition tools for real decisions. Independent, evidence-led and judgment-free.</p></div>"
    '<div><strong>Explore</strong><a href="healthy-fast-food.html">Healthy fast food</a>'
    '<a href="calculators.html">Calculators</a><a href="articles.html">Articles</a>'
    '<a href="quiz.html">Quizzes &amp; games</a></div>'
    '<div><strong>Reference</strong><a href="glossary.html">Glossary</a>'
    '<a href="sources.html">Sources</a><a href="editorial-policy.html">Editorial policy</a></div>'
    '<div><strong>Company</strong><a href="about.html">About</a>'
    '<a href="privacy.html">Privacy</a><a href="terms.html">Terms of use</a>'
    '<a href="contact.html">Contact</a></div>'
    "<small>&copy; 2026 GetMacros.net &middot; Educational information, not individualized medical advice.</small>"
    "</footer>"
)

# Text mangled by an earlier latin-1/utf-8 round trip.
MOJIBAKE = {
    "Â©": "©", "Â·": "·", "Â ": " ", "Â": "",
    "â€œ": "“", "â€\x9d": "”", "â€™": "’", "â€˜": "‘",
    "â€”": "—", "â€“": "–", "â€¦": "…",
    "Ã©": "é", "Ã¨": "è", "Ã ": "à", "Ã§": "ç", "Ã´": "ô", "Ã®": "î",
}

HEADER_RE = re.compile(r"<header\b[^>]*\bclass=\"site-header\"[^>]*>.*?</header>", re.S)
SIMPLE_FOOTER_RE = re.compile(r"<footer(?!\s+class=\"modern-footer\")\b[^>]*>.*?</footer>", re.S)


def fix_mojibake(text):
    for bad, good in MOJIBAKE.items():
        text = text.replace(bad, good)
    return text


def migrate(path):
    with open(path, encoding="utf-8") as fh:
        original = fh.read()
    text = original

    text = fix_mojibake(text)

    # Old-style header/footer -> the v3 markup the rest of the site uses.
    if 'class="site-header modern-header"' not in text:
        text = HEADER_RE.sub(lambda m: NAV, text, count=1)
    text = SIMPLE_FOOTER_RE.sub(lambda m: FOOTER, text, count=1)

    # v3 theme stylesheet, right after the base sheet.
    if "site-v3.css" not in text:
        text = re.sub(
            r'(<link rel="stylesheet" href="css/style\.css[^"]*">)',
            r'\1<link rel="stylesheet" href="css/site-v3.css?v=%s">' % ASSET_VERSION,
            text,
            count=1,
        )

    # v3 body classes.
    def body_sub(m):
        attrs = m.group(1) or ""
        cls = re.search(r'class="([^"]*)"', attrs)
        if cls:
            names = cls.group(1).split()
            for want in ("site-v3", "article-page"):
                if want not in names:
                    names.append(want)
            return "<body" + attrs.replace(cls.group(0), 'class="%s"' % " ".join(names)) + ">"
        return '<body class="site-v3 article-page"%s>' % attrs

    text = re.sub(r"<body([^>]*)>", body_sub, text, count=1)

    # Landmark + skip link.
    text = re.sub(r"<main(?![^>]*\bid=)([^>]*)>", r'<main id="main-content"\1>', text, count=1)
    if "skip-link" not in text and "<main" in text:
        text = re.sub(
            r"(<body[^>]*>)",
            r'\1<a class="skip-link" href="#main-content">Skip to main content</a>',
            text,
            count=1,
        )

    # Retire the dead third-party ad bootstrap.
    text = re.sub(r'\s*<script src="js/ads-config\.js[^"]*"></script>', "", text)
    text = re.sub(r'\s*<script src="js/ads\.js[^"]*"></script>', "", text)
    text = re.sub(r'\s*<link rel="preconnect" href="https://www\.highperformanceformat\.com">', "", text)

    if text != original:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        return True
    return False


def main():
    os.chdir(ROOT)
    # es/ and fr/ live one level down and need ../ prefixes, so they carry
    # their own hand-maintained copy of the nav.
    targets = sorted(glob.glob("*.html"))
    changed = [p for p in targets if migrate(p)]
    print(f"migrated {len(changed)} of {len(targets)} pages")


if __name__ == "__main__":
    sys.exit(main())
