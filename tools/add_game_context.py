#!/usr/bin/env python3
"""Give JS-rendered game pages some crawlable content.

These pages build everything in JavaScript, so a crawler sees roughly 30 words
of HTML. The block below is generated from each page's own title, lead and
question data, so it is unique per page rather than boilerplate, and it tells a
reader what the game covers before they start.
"""
import glob
import html as H
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
MARK = "game-context"
MIN_WORDS = 150


def visible_words(c):
    b = c[c.index("<body"):]
    for pat in (r"<script.*?</script>", r"<style.*?</style>", r"<header\b.*?</header>",
                r"<footer\b.*?</footer>", r'<section class="related-explore".*?</section>',
                r"<nav\b.*?</nav>"):
        b = re.sub(pat, " ", b, flags=re.S)
    return len(H.unescape(re.sub(r"<[^>]+>", " ", b)).split())


def statements(c):
    """Pull the prompts out of the inline question array, without the answers."""
    out = []
    for m in re.finditer(r"\[(['\"])(.{25,190}?)\1\s*,", c):
        s = m.group(2).strip()
        if s.endswith("\\") or "<" in s:
            continue
        out.append(s)
    seen, uniq = set(), []
    for s in out:
        if s.lower() in seen:
            continue
        seen.add(s.lower())
        uniq.append(s)
    return uniq[:8]


def build(title, lead, items):
    li = "".join("<li>" + H.escape(s) + "</li>" for s in items)
    covers = (f"      <h2>What this covers</h2>\n"
              f"      <p>Each round gives you a claim to judge, then explains the reasoning behind the "
              f"answer rather than just marking it right or wrong. Statements you will weigh up include:</p>\n"
              f'      <ul class="checklist">{li}</ul>\n') if items else ""
    return (f'  <section class="tight {MARK}">\n    <div class="container">\n'
            f"      <h2>How it works</h2>\n"
            f"      <p>{H.escape(lead)} Answer each prompt, read why the answer is what it is, and move on. "
            f"There is no timer, no sign-up and nothing is saved &mdash; you can restart whenever you like.</p>\n"
            f"{covers}"
            f"      <h2>Why bother</h2>\n"
            f'      <p>Recognising a shaky nutrition claim is a more durable skill than memorising a food list, '
            f'because the claims change every year and the reasoning does not. If you would rather read first, '
            f'browse the <a href="articles.html">guide library</a> or try a '
            f'<a href="quiz.html">quiz</a>.</p>\n'
            f"    </div>\n  </section>\n")


def main():
    os.chdir(ROOT)
    done = 0
    for f in sorted(glob.glob("*.html")):
        if not re.search(r"(game|challenge)\.html$", f):
            continue
        c = open(f, encoding="utf-8").read()
        # The generator-owned games already carry a bespoke "How to play"
        # section; adding a second, generic one duplicates content across them.
        if (MARK in c or "<h2>How to play</h2>" in c
                or visible_words(c) >= MIN_WORDS or "</main>" not in c):
            continue
        t = re.search(r"<h1[^>]*>(.*?)</h1>", c, re.S)
        lead = re.search(r'<p class="lead">(.*?)</p>', c, re.S)
        title = H.unescape(re.sub(r"<[^>]+>", "", t.group(1))).strip() if t else f
        lead_txt = H.unescape(re.sub(r"<[^>]+>", "", lead.group(1))).strip() if lead else \
            "A short set of prompts on this topic."
        block = build(title, lead_txt, statements(c))
        open(f, "w", encoding="utf-8").write(c.replace("</main>", block + "</main>", 1))
        done += 1
    print(f"context block added to {done} game pages")


if __name__ == "__main__":
    sys.exit(main())
