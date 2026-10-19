#!/usr/bin/env python3
"""Read-only public-source audit; no analytics credentials or account claims."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/ultimate-release-2026-10-19"
EXCLUDED = {".git", ".github", "design", "docs", "tools", "server", "native", "music-platform", "node_modules"}
BASE = "https://getmacros.net/"
GA = re.compile(r"googletagmanager\.com/(?:gtag/js|gtm\.js)|google-analytics\.com|\bgtag\s*\(|\bG-[A-Z0-9]{6,}\b")
ADS = re.compile(r"pagead2\.googlesyndication\.com|adsbygoogle\.js|scripts\.mediavine\.com|scripts\.journeymv\.com|scriptwrapper|grow\.me", re.I)


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = []
        self.h1 = []
        self.metas = {}
        self.canonicals = []
        self.alternates = []
        self.scripts = []
        self.links = []
        self.images = []
        self.jsonld = []
        self.main = []
        self._intitle = self._inh1 = self._inmain = False
        self._inscript = False
        self._scriptattrs = {}
        self._scripttext = []
        self.lang = None
        self.adslots = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html": self.lang = a.get("lang")
        if tag == "title": self._intitle = True
        if tag == "h1": self._inh1 = True; self.h1.append([])
        if tag == "main": self._inmain = True
        if tag == "meta": self.metas[a.get("name", a.get("property", ""))] = a.get("content", "")
        if tag == "link":
            rel = a.get("rel", "").split()
            if "canonical" in rel: self.canonicals.append(a.get("href", ""))
            if "alternate" in rel and a.get("hreflang"): self.alternates.append({"language": a["hreflang"], "href": a.get("href", "")})
        if tag == "script": self._inscript = True; self._scriptattrs = a; self._scripttext = []
        if tag == "a" and a.get("href"): self.links.append(a["href"])
        if tag == "img": self.images.append({"src": a.get("src"), "alt": a.get("alt"), "width": a.get("width"), "height": a.get("height")})
        if "data-ad-placement" in a: self.adslots.append(a["data-ad-placement"])

    def handle_endtag(self, tag):
        if tag == "title": self._intitle = False
        if tag == "h1": self._inh1 = False
        if tag == "main": self._inmain = False
        if tag == "script" and self._inscript:
            text = "".join(self._scripttext)
            self.scripts.append({"src": self._scriptattrs.get("src"), "type": self._scriptattrs.get("type"), "text": text})
            if self._scriptattrs.get("type") == "application/ld+json":
                try: self.jsonld.append(json.loads(text))
                except json.JSONDecodeError: self.jsonld.append({"error": "invalid JSON"})
            self._inscript = False

    def handle_data(self, text):
        if self._intitle: self.title.append(text)
        if self._inh1: self.h1[-1].append(text)
        if self._inscript: self._scripttext.append(text)
        if self._inmain and not self._inscript: self.main.append(text)


def route(path):
    name = path.relative_to(ROOT).as_posix()
    return "/" + (name[:-10] if name.endswith("index.html") else name)


def pages():
    # A market may legitimately contain /tools/; exclude development roots only.
    return sorted(p for p in ROOT.rglob("*.html") if p.relative_to(ROOT).parts[0] not in EXCLUDED)


def clean(parts): return " ".join(" ".join(parts).split())


def audit():
    records = []
    parsed = {}
    external = Counter()
    for path in pages():
        text = path.read_text(encoding="utf-8")
        page = Page(); page.feed(text)
        current = route(path)
        parsed[urljoin(BASE, current)] = page
        runtime_scripts = [s for s in page.scripts if s["type"] != "application/ld+json"]
        ga = [s for s in runtime_scripts if GA.search((s["src"] or "") + " " + s["text"])]
        ads = [s for s in runtime_scripts if ADS.search((s["src"] or "") + " " + s["text"])]
        for s in runtime_scripts:
            if s["src"] and s["src"].startswith("https:"): external[s["src"]] += 1
        records.append({
            "route": current, "file": path.relative_to(ROOT).as_posix(),
            "title": clean(page.title), "description": page.metas.get("description", ""),
            "h1_count": len(page.h1), "h1": " | ".join(clean(h) for h in page.h1),
            "canonical_count": len(page.canonicals), "canonical": " | ".join(page.canonicals),
            "robots": page.metas.get("robots", "index (default)"), "language": page.lang,
            "hreflang_count": len(page.alternates), "ga4_loader_count": len(ga),
            "production_ad_loader_count": len(ads), "editorial_ad_slot_count": len(page.adslots),
            "image_count": len(page.images), "images_missing_alt": sum(i["alt"] is None for i in page.images),
            "images_missing_dimensions": sum(not i["width"] or not i["height"] for i in page.images),
            "invalid_jsonld_count": sum(isinstance(j, dict) and j.get("error") == "invalid JSON" for j in page.jsonld),
            "sha256": hashlib.sha256(text.replace("\r\n", "\n").encode()).hexdigest(),
        })
    titles = Counter(r["title"] for r in records if "noindex" not in r["robots"])
    descriptions = Counter(r["description"] for r in records if "noindex" not in r["robots"])
    reciprocal = []
    for href, page in parsed.items():
        for alt in page.alternates:
            target = parsed.get(alt["href"])
            if target is None: reciprocal.append({"from": href, "to": alt["href"], "issue": "not a local canonical source route"})
            elif not any(a["href"] == href for a in target.alternates): reciprocal.append({"from": href, "to": alt["href"], "issue": "missing reciprocal annotation"})
    sitemap = ET.parse(ROOT / "sitemap.xml").getroot()
    sitemap_urls = [n.text for n in sitemap.findall(".//{*}loc")]
    policies = {}
    for name in ["about.html", "contact.html", "privacy.html", "terms.html", "editorial-policy.html", "corrections.html", "sources.html", "accessibility.html"]:
        p = parsed.get(urljoin(BASE, name))
        policies[name] = {"present": bool(p), "main_words": len(clean(p.main).split()) if p else 0,
                          "linked_from_home": any(urljoin(BASE, a) == urljoin(BASE, name) for a in parsed[BASE].links)}
    summary = {
        "auditedAt": datetime.now(timezone.utc).isoformat(), "scope": "local public HTML and authored runtime scripts, not an account or live-network audit",
        "counts": {"publicHTML": len(records), "sitemapURLs": len(sitemap_urls),
                   "indexablePages": sum("noindex" not in r["robots"] for r in records),
                   "pagesWithGA4Loader": sum(bool(r["ga4_loader_count"]) for r in records),
                   "pagesWithProductionAdLoader": sum(bool(r["production_ad_loader_count"]) for r in records),
                   "pagesWithAdSlots": sum(bool(r["editorial_ad_slot_count"]) for r in records)},
        "issues": {"duplicateIndexableTitles": {k: v for k,v in titles.items() if v > 1},
                   "duplicateIndexableDescriptions": {k: v for k,v in descriptions.items() if v > 1},
                   "invalidJSONLD": [r["route"] for r in records if r["invalid_jsonld_count"]],
                   "missingCanonical": [r["route"] for r in records if not r["canonical_count"]],
                   "multipleCanonical": [r["route"] for r in records if r["canonical_count"] > 1],
                   "nonSelfCanonical": [r["route"] for r in records if r["canonical_count"] == 1 and r["canonical"] != urljoin(BASE, r["route"])],
                   "missingTitleOrDescription": [r["route"] for r in records if not r["title"] or not r["description"]],
                   "nonSingleH1": [r["route"] for r in records if r["h1_count"] != 1],
                   "missingImageAlt": [r["route"] for r in records if r["images_missing_alt"]],
                   "hreflang": reciprocal,
                   "sitemapUnknownLocalRoutes": [u for u in sitemap_urls if u not in parsed],
                   "sitemapDuplicates": [u for u,n in Counter(sitemap_urls).items() if n > 1],
                   "noindexInSitemap": [r["route"] for r in records if "noindex" in r["robots"] and urljoin(BASE,r["route"]) in sitemap_urls],
                   "indexableNotInSitemap": [r["route"] for r in records if "noindex" not in r["robots"] and urljoin(BASE,r["route"]) not in sitemap_urls]},
        "externalRuntimeScriptURLs": dict(external), "policies": policies,
        "privacyBoundary": {"eventsModule": "js/product-events.js", "providerFree": True,
                            "observedEventPayload": "Whitelisted event name and version only; no inputs, searches or food identifiers",
                            "advertisingModule": "js/ad-placements.js", "default": "disabled, consent unknown, no adapter"},
        "accountEvidence": {"GA4": "not connected or inspected", "SearchConsole": "not connected or inspected",
                            "Journey": "not connected or inspected", "AdSenseStanding": "not connected or inspected"},
        "limitations": ["Presence or absence of GA4 in these source files cannot prove what a CDN, tag manager or account does in production.",
                        "No visitor, session, pageview, click, indexing or revenue metrics were available.",
                        "No visual quality or performance outcome is inferred from HTML parsing."]
    }
    return records, summary


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--suffix", default="baseline"); args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rows, summary = audit()
    path = OUT / ("technical-monetization-audit-" + args.suffix + ".json")
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (OUT / ("technical-page-audit-" + args.suffix + ".csv")).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"report": str(path.relative_to(ROOT)), "counts": summary["counts"], "issueCounts": {k: len(v) for k,v in summary["issues"].items()}, "externalScripts": summary["externalRuntimeScriptURLs"]}, ensure_ascii=False))
