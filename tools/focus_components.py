"""Shared HTML components for the focused GetMacros product pages."""
from __future__ import annotations

import html
import json

SITE = "https://getmacros.net"
PUBLISHER = "ca-pub-2316153877942502"
ASSET_VERSION = "20260826a"

CSP = (
    "default-src 'self'; script-src 'self' 'unsafe-inline' "
    "https://pagead2.googlesyndication.com https://*.googlesyndication.com "
    "https://*.doubleclick.net https://*.google.com https://*.googletagservices.com "
    "https://*.adtrafficquality.google https://*.gstatic.com https://*.googleapis.com; "
    "style-src 'self' 'unsafe-inline' https://*.googlesyndication.com; "
    "img-src 'self' data: https://*.googlesyndication.com https://*.doubleclick.net "
    "https://*.google.com https://*.gstatic.com https://*.adtrafficquality.google; "
    "font-src 'self'; connect-src 'self' https://*.googlesyndication.com "
    "https://*.doubleclick.net https://*.google.com https://*.adtrafficquality.google "
    "https://*.googleapis.com; frame-src 'self' https://*.googlesyndication.com "
    "https://*.doubleclick.net https://*.google.com https://*.adtrafficquality.google; "
    "frame-ancestors 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; "
    "upgrade-insecure-requests"
)


def canonical(path: str) -> str:
    return f"{SITE}/" if path == "index.html" else f"{SITE}/{path}"


def head(path: str, title: str, description: str, *, schema=None,
         image="images/og-default.png", extra="") -> str:
    url = canonical(path)
    image_url = f"{SITE}/{image}"
    schemas = schema if isinstance(schema, list) else ([schema] if schema else [])
    jsonld = "\n".join(
        f'<script type="application/ld+json">{json.dumps(item, ensure_ascii=False)}</script>'
        for item in schemas
    )
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<script>if(self!==top){{try{{top.location=self.location;}}catch(e){{document.documentElement.style.display="none";}}}}</script>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description, quote=True)}">
<meta name="author" content="The GetMacros.net editorial team">
<meta name="google-adsense-account" content="{PUBLISHER}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="GetMacros.net">
<meta property="og:title" content="{html.escape(title, quote=True)}">
<meta property="og:description" content="{html.escape(description, quote=True)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image_url}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="GetMacros.net practical nutrition tools">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title, quote=True)}">
<meta name="twitter:description" content="{html.escape(description, quote=True)}">
<meta name="twitter:image" content="{image_url}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#123f2d">
<link rel="preload" href="/fonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/inter-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="css/style.css?v={ASSET_VERSION}">
<link rel="stylesheet" href="css/site-v3.css?v={ASSET_VERSION}">
<link rel="stylesheet" href="css/recovery.css?v={ASSET_VERSION}">
<link rel="stylesheet" href="css/readability-v2.css?v=20260823d">
<link rel="stylesheet" href="css/premium-v4.css?v={ASSET_VERSION}">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={PUBLISHER}" crossorigin="anonymous"></script>
{jsonld}
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="referrer" content="strict-origin-when-cross-origin">
{extra}
</head>'''


def nav(current="") -> str:
    links = [
        ("healthy-fast-food.html", "Healthy Fast Food", "fastfood"),
        ("restaurant-meal-finder.html", "Meal Finder", "finder"),
        ("calculators.html", "Macro Calculator", "calculators"),
        ("articles.html", "Nutrition Guides", "guides"),
        ("about.html", "About", "about"),
    ]
    anchors = []
    for href, label, key in links:
        mark = ' aria-current="page"' if key == current else ""
        anchors.append(f'<a href="{href}"{mark}>{label}</a>')
    return f'''<a class="skip-link" href="#main-content">Skip to main content</a>
<header class="site-header modern-header"><nav class="full-nav" aria-label="Main navigation">
<a class="modern-brand" href="index.html" aria-label="GetMacros.net home"><span class="brand-mark" aria-hidden="true">G</span><span>GetMacros<span class="brand-dot">.</span></span></a>
<div class="full-nav-links">{''.join(anchors)}</div>
<a class="nav-action" href="search.html">Search</a>
</nav></header>'''


def footer() -> str:
    return '''<footer class="modern-footer">
<div><a class="modern-brand footer-brand" href="index.html"><span class="brand-mark" aria-hidden="true">G</span><span>GetMacros<span class="brand-dot">.</span></span></a><p>Find fast-food meals that fit your calories, protein and goals—then understand the numbers.</p></div>
<div><strong>Use GetMacros</strong><a href="healthy-fast-food.html">Healthy fast food</a><a href="restaurant-meal-finder.html">Meal finder</a><a href="calculators.html">Macro calculator</a><a href="articles.html">Nutrition guides</a></div>
<div><strong>Trust</strong><a href="about.html">About</a><a href="editorial-policy.html">Editorial policy</a><a href="sources.html">Sources</a><a href="corrections.html">Corrections</a></div>
<div><strong>Legal &amp; contact</strong><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a><a href="accessibility.html">Accessibility</a><a href="contact.html">Contact</a></div>
<small>&copy; 2026 GetMacros.net &middot; Educational information, not individualized medical advice.</small>
</footer><script src="js/site-motion.js?v=20260826a"></script>'''


def breadcrumbs(items: list[tuple[str, str | None]]) -> str:
    parts = []
    for label, href in items:
        if href:
            parts.append(f'<a href="{href}">{html.escape(label)}</a>')
        else:
            parts.append(f'<span aria-current="page">{html.escape(label)}</span>')
    return '<nav class="breadcrumb" aria-label="Breadcrumb"><div class="container">' + \
        ' <span aria-hidden="true">&rsaquo;</span> '.join(parts) + '</div></nav>'
