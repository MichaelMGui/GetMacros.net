#!/usr/bin/env python3
"""Stamp every local CSS and JS link with a hash of that file's contents.

The version stamps were hand-written in eleven generators -- thirty-seven of
them -- and only changed when someone remembered to change them. They did not
get bumped for three commits of CSS work, so every browser and CDN that already
held `css/theme-fix.css?v=20260828g` kept serving the old file: the site was
deployed and correct, and looked completely unchanged on a phone.

A stamp taken from the file's own bytes cannot go stale. It changes exactly when
the file changes, and stays put when it does not, so an unchanged asset keeps
its cache entry. This runs last, over the generated HTML, which is why it fixes
all eleven generators at once instead of asking each to remember.
"""
import glob
import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
LINK = re.compile(r'(?P<attr>href|src)="(?P<prefix>(?:\.\./)?)(?P<path>(?:css|js)/[A-Za-z0-9._-]+\.(?:css|js))(?:\?v=[^"]*)?"')


def digest(path, cache={}):
    if path not in cache:
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            cache[path] = None
        else:
            with open(full, "rb") as handle:
                cache[path] = hashlib.sha256(handle.read()).hexdigest()[:10]
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

    pages = sorted(glob.glob("*.html")) + [
        p for p in sorted(glob.glob("*/*.html")) if not p.startswith("design/")
    ]
    for page in pages:
        text = open(page, encoding="utf-8").read()
        out = LINK.sub(stamp, text)
        if out != text:
            open(page, "w", encoding="utf-8").write(out)
            changed += 1

    for path in sorted(missing):
        print(f"  WARNING linked asset does not exist: {path}")
    print(f"asset versions stamped from file contents on {changed} page(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
