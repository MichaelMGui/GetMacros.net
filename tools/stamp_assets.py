#!/usr/bin/env python3
"""Stamp every local CSS, JS, favicon, and icon-sprite reference with a content hash.

The version stamps were hand-written in eleven generators -- thirty-seven of
them -- and only changed when someone remembered to change them. They did not
get bumped for three commits of CSS work, so every browser and CDN that already
held `css/theme-fix.css?v=20260828g` kept serving the old file: the site was
deployed and correct, and looked completely unchanged on a phone.

A stamp taken from the asset's content cannot go stale. Text line endings are
normalized so Windows checkout and Linux CI produce the same versions. It changes
when the content changes, and stays put when it does not, so an unchanged asset keeps
its cache entry. This runs last, over the generated HTML, which is why it fixes
all eleven generators at once instead of asking each to remember.
"""
import glob
import hashlib
import os
import re
import sys
import json
import posixpath

ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
LINK = re.compile(r'(?P<attr>href|src)="(?P<prefix>(?:\.\./|/)?)(?P<path>(?:(?:css|js)/[A-Za-z0-9._-]+\.(?:css|js)|favicon\.svg))(?:\?v=[^"]*)?"')
SPRITE = re.compile(r'href="(?P<prefix>(?:\.\./|/)?)(?P<path>icon-sprite\.svg|images/food-characters\.svg)(?:\?v=[^"#]*)?#(?P<symbol>[A-Za-z0-9._-]+)"')


def digest(path, cache={}):
    if path not in cache:
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            cache[path] = None
        else:
            with open(full, "rb") as handle:
                cache[path] = hashlib.sha256(handle.read().replace(b"\r\n", b"\n")).hexdigest()[:10]
    return cache[path]


def main():
    os.chdir(ROOT)
    changed = 0
    missing = set()

    def stamp(match):
        version = digest(match.group("path"))
        if version is None:
            missing.add(match.group("path"))
            return match.group(0)
        return f'{match.group("attr")}="{match.group("prefix")}{match.group("path")}?v={version}"'

    def stamp_sprite(match):
        version = digest(match.group("path"))
        if version is None:
            missing.add(match.group("path"))
            return match.group(0)
        return f'href="{match.group("prefix")}{match.group("path")}?v={version}#{match.group("symbol")}"'

    design_prefix = os.path.normcase("design" + os.sep)
    pages = sorted(glob.glob("*.html")) + sorted(glob.glob("*/en/**/index.html",recursive=True)) + [
        p for p in sorted(glob.glob("*/*.html"))
        if not os.path.normcase(p).startswith(design_prefix)
    ]
    for page in pages:
        text = open(page, encoding="utf-8").read()
        out = SPRITE.sub(stamp_sprite, LINK.sub(stamp, text))
        if out != text:
            open(page, "w", encoding="utf-8").write(out)
            changed += 1

    # Older service workers matched only the pathname and could return an old
    # bundle even when ?v changed. Immutable filenames keep HTML/code coherent
    # on the very first visit after a major release, before worker activation.
    generated = os.path.join(ROOT, 'assets', 'generated')
    os.makedirs(generated, exist_ok=True)
    manifest = {}
    def immutable(source):
        if source in manifest:
            return manifest[source]['url']
        original = open(os.path.join(ROOT,source),'rb').read().replace(b'\r\n',b'\n')
        data = original
        if source.endswith('.css'):
            css = original.decode('utf-8-sig')
            def absolute_url(match):
                value=match[1].strip('"\' ')
                if value.startswith(('/', '#', 'data:', 'http:', 'https:')):
                    return match[0]
                return 'url("/'+posixpath.normpath(posixpath.join(posixpath.dirname(source),value))+'")'
            data=re.sub(r'url\(([^)]+)\)',absolute_url,css).encode('utf-8')
        version=hashlib.sha256(data).hexdigest()[:12]
        name=source.replace('/','-').rsplit('.',1)
        filename=name[0]+'-'+version+'.'+name[1]
        open(os.path.join(generated,filename),'wb').write(data)
        url='/assets/generated/'+filename
        manifest[source]={'url':url,'sourceSha256':hashlib.sha256(original).hexdigest(),'assetSha256':hashlib.sha256(data).hexdigest()}
        return url
    registry=immutable('js/order-registry.json') if os.path.exists('js/order-registry.json') else None
    for page in pages:
        text=open(page,encoding='utf-8').read()
        text=re.sub(r'<script data-public-assets>.*?</script>','',text,flags=re.S)
        def immutable_tag(match):
            tag=match[0]
            logical=re.search(r'data-source-path="([^"]+)"',tag)
            target=re.search(r'\b(?:href|src)="/?((?:css|js)/[A-Za-z0-9._-]+\.(?:css|js))(?:\?[^" ]*)?"',tag)
            source=logical[1] if logical else target[1] if target else None
            if not source or not os.path.isfile(os.path.join(ROOT,source)):
                return tag
            tag=re.sub(r'\sdata-source-path="[^"]+"','',tag)
            tag=re.sub(r'\b(href|src)="[^"]+"',lambda m:m[1]+'="'+immutable(source)+'"',tag,count=1)
            return tag[:-1]+' data-source-path="'+source+'">'
        text=re.sub(r'<(?:link|script)\b[^>]*>',immutable_tag,text)
        seen_links=set()
        def unique_link(match):
            tag=match[0]
            attrs=dict(re.findall(r'([\w-]+)="([^"]*)"',tag))
            key=(attrs.get('rel'),attrs.get('as'),attrs.get('href'),attrs.get('hreflang'),attrs.get('type'),attrs.get('media'))
            if key in seen_links:return ''
            seen_links.add(key)
            return tag
        text=re.sub(r'<link\b[^>]*>',unique_link,text)
        # Header replacement must not accumulate blank separators on rebuild.
        text=re.sub(r'</header>\s+(?=<main\b)','</header>\n',text)
        text=re.sub(r'</footer>\s+(?=<script\b)','</footer>\n',text)
        text=re.sub(r'</script>\s+(?=<script\b|</body>)','</script>\n',text)
        if registry:
            text=text.replace('</head>','<script data-public-assets>window.GM_PUBLIC_ASSETS='+json.dumps({'/js/order-registry.json':registry},separators=(',',':'))+';</script></head>')
        open(page,'w',encoding='utf-8').write(text)
    open(os.path.join(generated,'manifest.json'),'w',encoding='utf-8').write(json.dumps(manifest,indent=2)+'\n')
    # Only remove this generator's obsolete immutable artifacts, never sources.
    needed={os.path.basename(v['url']) for v in manifest.values()}|{'manifest.json'}
    for name in os.listdir(generated):
        target=os.path.abspath(os.path.join(generated,name))
        if os.path.commonpath([os.path.abspath(generated),target])==os.path.abspath(generated) and name not in needed and re.fullmatch(r'[A-Za-z0-9._-]+-[a-f0-9]{12}\.(css|js|json)',name):
            os.remove(target)

    # A content-addressed app shell prevents stale arithmetic/UI after a release.
    if os.path.exists('sw.js'):
        app_files=['food-diary.html','food-library.html','offline.html','site.webmanifest','icon-sprite.svg','js/order-registry.json','data/food-library/manifest.json','data/food-library/index.json']
        app_files += sorted(glob.glob('data/branded-foods/*/manifest.json'))
        app_files += ['data/restaurant-foods/manifest.json'] if os.path.exists('data/restaurant-foods/manifest.json') else []
        app_files += sorted(glob.glob('data/food-library/diary-foods-*.json'))
        app_files += sorted(glob.glob('js/*.js'))+sorted(glob.glob('css/*.css'))
        fingerprint=hashlib.sha256(b''.join(open(p,'rb').read().replace(b'\r\n',b'\n') for p in app_files if os.path.isfile(p))).hexdigest()[:16]
        sw=open('sw.js',encoding='utf-8').read()
        sw=re.sub(r"const VERSION='[^']+'", "const VERSION='gm-food-app-"+fingerprint+"'",sw,count=1)
        offline_assets={'/favicon.svg','/icon-sprite.svg'}
        offline_assets.update('/'+p.replace('\\','/') for p in glob.glob('data/food-library/diary-foods-*.json'))
        for page in ['food-diary.html','food-library.html']:
            offline_assets.update(re.findall(r'(?:href|src)="(/assets/generated/[^"]+\.(?:css|js))"',open(page,encoding='utf-8').read()))
        sw=re.sub(r'const APP_ASSETS=.*?;', 'const APP_ASSETS='+json.dumps(sorted(offline_assets),separators=(',',':'))+';',sw,count=1)
        open('sw.js','w',encoding='utf-8').write(sw)
    for path in sorted(missing):
        print(f"  WARNING linked asset does not exist: {path}")
    print(f"asset versions stamped from file contents on {changed} page(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
