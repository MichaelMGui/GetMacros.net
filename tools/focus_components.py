"""Shared HTML components for the focused GetMacros product pages."""
from __future__ import annotations

import html
import json

from apply_atelier_v5 import FOOTER as ATELIER_FOOTER, HEADER as ATELIER_HEADER

SITE = "https://getmacros.net"
PUBLISHER = "ca-pub-2316153877942502"
ASSET_VERSION = "20260828f"
THEME_BOOT = '<script>try{document.documentElement.dataset.theme=localStorage.getItem("gm-theme")||"light"}catch(e){document.documentElement.dataset.theme="light"}</script>'

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
<link rel="icon" href="/favicon.svg?v=20260828b" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#f4f7f2">
<link rel="preload" href="/fonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/inter-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="css/style.css?v={ASSET_VERSION}">
<link rel="stylesheet" href="css/site-v3.css?v={ASSET_VERSION}">
<link rel="stylesheet" href="css/recovery.css?v={ASSET_VERSION}">
<link rel="stylesheet" href="css/readability-v2.css?v=20260823d">
<link rel="stylesheet" href="css/premium-v4.css?v=20260826b">
<link rel="stylesheet" href="css/liquid.css?v=20260826b">
<link rel="stylesheet" href="css/contrast-fix.css?v=20260826b">
<link rel="stylesheet" href="css/polish.css?v=20260826b">
<link rel="stylesheet" href="css/atelier-v5.css?v=20260827b">
<link rel="stylesheet" href="css/studio-v6.css?v=20260828c">
{THEME_BOOT}
<link rel="stylesheet" href="css/unified-v7.css?v=20260828f">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={PUBLISHER}" crossorigin="anonymous"></script>
{jsonld}
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="referrer" content="strict-origin-when-cross-origin">
{extra}
</head>'''


def nav(current="") -> str:
    return '<a class="skip-link" href="#main-content">Skip to main content</a>\n' + ATELIER_HEADER


def footer() -> str:
    return ATELIER_FOOTER + '<script src="js/unified-v7.js?v=20260828f" defer></script>'


def breadcrumbs(items: list[tuple[str, str | None]]) -> str:
    parts = []
    for label, href in items:
        if href:
            parts.append(f'<a href="{href}">{html.escape(label)}</a>')
        else:
            parts.append(f'<span aria-current="page">{html.escape(label)}</span>')
    return '<nav class="breadcrumb" aria-label="Breadcrumb"><div class="container">' + \
        ' <span aria-hidden="true">&rsaquo;</span> '.join(parts) + '</div></nav>'
