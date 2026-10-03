"""Report repetition in existing authored pages without rewriting shared copy.

Run from any directory: python tools/release_copy_audit.py
Only root HTML files tracked by Git and absent from the release resource payloads
are included. New resources are audited separately by their publication gates. This is a source-text check,
not a claim that every page has been visually or editorially reviewed.
"""
from __future__ import annotations

import argparse
import html
from collections import defaultdict
from difflib import SequenceMatcher
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/release-2026-10-03/copy-audit.json"
BLOCKS = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
EXCLUDED_TAGS = {"nav", "footer", "script", "style", "template", "table"}
EXCLUDED_CLASSES = {
    "article-byline", "article-meta", "guide-toc", "article-toc",
    "related-links", "related-guides", "related-grid", "breadcrumbs",
    "source-list", "article-sources", "source-note", "disclaimer", "meta",
    "submission-sources",
}
SHARED_HEADINGS = {
    "sources", "related guides", "related reading", "on this page",
    "quick answer", "how to use this calculator", "about this estimate",
    "sources and further reading", "sources and scope", "sources and limitations",
}
SHARED_SENTENCES = {
    "getmacros is independent of these restaurants.",
    "opens your mail service in a new tab.",
    "sign in if needed.",
    "a dash means we could not confirm that value.",
    "protein per 100 calories = protein grams ÷ calories × 100.",
    "it is a transparent efficiency metric, not a health score.",
    "scroll the table sideways to compare all nutrients.",
    "comparison written september 28, 2026 using the existing records.",
    "this is not a new verification of restaurant data; the source dates below remain unchanged.",
    "figures checked against the linked official sources on september 9, 2026.",
    "selected source values were inspected october 3, 2026; individual nutrient check dates and source editions are recorded above.",
}


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


class AuthoredBlocks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.open_blocks = []
        self.blocks = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set(attrs.get("class", "").split())
        parent_skip = self.stack[-1][1] if self.stack else False
        in_main = tag == "main" or (self.stack[-1][2] if self.stack else False)
        skip = parent_skip or tag in EXCLUDED_TAGS or bool(classes & EXCLUDED_CLASSES)
        skip = skip or attrs.get("id") in {"sources", "article-sources"}
        depth = len(self.stack)
        if tag not in VOID:
            self.stack.append((tag, skip, in_main))
        if tag in BLOCKS and in_main and not skip:
            self.open_blocks.append({"tag": tag, "depth": depth, "parts": [], "links": 0,
                                     "referenceLabel": any(node[0] == "a" for node in self.stack), "line": self.getpos()[0]})
        if tag == "a":
            for block in self.open_blocks:
                block["links"] += 1

    def handle_data(self, data):
        if self.stack and not self.stack[-1][1]:
            for block in self.open_blocks:
                block["parts"].append(data)

    def handle_endtag(self, tag):
        matching = next((i for i in range(len(self.stack) - 1, -1, -1) if self.stack[i][0] == tag), None)
        if matching is None:
            return
        done = [b for b in self.open_blocks if b["depth"] >= matching]
        self.open_blocks = [b for b in self.open_blocks if b["depth"] < matching]
        for block in done:
            text = norm("".join(block.pop("parts")))
            if not text or text.lower() in SHARED_HEADINGS:
                continue
            # A list consisting of one short destination label is navigation.
            if block["tag"] == "li" and block["links"] and len(text.split()) < 12:
                continue
            # Publication attribution is a legitimate shared disclosure.
            if re.match(r"^(?:By GetMacros|Published |Updated |This article is general information)", text):
                continue
            block["text"] = text
            self.blocks.append(block)
        del self.stack[matching:]


def existing_pages():
    names = subprocess.check_output(["git", "ls-files", "--", "*.html"], cwd=ROOT, text=True).splitlines()
    new_routes = set()
    for payload in ["release_explainers.json", "release_collections.json"]:
        path = ROOT / "tools" / payload
        if path.is_file():
            new_routes.update(row["slug"] for row in json.loads(path.read_text(encoding="utf-8")))
    return sorted(name for name in names if name not in new_routes and "/" not in name and "\\" not in name and (ROOT / name).is_file())


def audit():
    pages = existing_pages()
    sentences, headings, paragraphs = defaultdict(list), defaultdict(list), []
    block_count = 0
    for name in pages:
        parser = AuthoredBlocks()
        parser.feed((ROOT / name).read_text(encoding="utf-8"))
        block_count += len(parser.blocks)
        for block in parser.blocks:
            location = {"route": name, "line": block["line"], "tag": block["tag"]}
            if block["tag"].startswith("h"):
                if not block["referenceLabel"] and not block["links"] and len(block["text"].split()) >= 4:
                    headings[block["text"].casefold()].append({**location, "text": block["text"]})
                continue
            for sentence in re.split(r"(?<=[.!?])\s+(?=[A-Z‘“])", block["text"]):
                sentence = norm(sentence)
                if block["tag"] == "p" and len(sentence.split()) >= 8 and sentence.endswith((".", "?", "!")) and sentence.casefold() not in SHARED_SENTENCES:
                    sentences[sentence.casefold()].append({**location, "text": sentence})
            if block["tag"] == "p" and len(block["text"].split()) >= 25:
                paragraphs.append({**location, "text": block["text"]})
    repeated = lambda corpus: [values for values in corpus.values() if len(values) > 1]
    near = []
    for i, first in enumerate(paragraphs):
        for second in paragraphs[i + 1:]:
            if first["route"] == second["route"] or first["text"].casefold() == second["text"].casefold():
                continue
            if min(len(first["text"]), len(second["text"])) / max(len(first["text"]), len(second["text"])) < .9:
                continue
            words_a, words_b = set(first["text"].casefold().split()), set(second["text"].casefold().split())
            if len(words_a & words_b) / len(words_a | words_b) < .8:
                continue
            ratio = SequenceMatcher(None, first["text"].casefold(), second["text"].casefold(), autojunk=False).ratio()
            if ratio >= .94:
                near.append({"similarity": round(ratio, 3), "locations": [first, second]})
    return {
        "scope": "Tracked root HTML before new release resources; source-text check only",
        "pages": pages,
        "pageCount": len(pages),
        "authoredBlockCount": block_count,
        "exclusions": "Outside main; navigation/footer/scripts; table records (factual values/serving/source notes); source lists, publication metadata, shared navigation labels and named disclosure classes. Legal pages retained for review; legitimate legal/source reuse is not automatically rewritten.",
        "thresholds": {"sentenceMinimumWords": 8, "headingMinimumWords": 4, "paragraphMinimumWords": 25, "nearParagraphSimilarity": .94},
        "repeatedSentences": repeated(sentences),
        "repeatedHeadings": repeated(headings),
        "nearParagraphs": near,
    }


def apply_reviewed_edits():
    """Reapply only the six reviewed release edits after a shared page build.

    This opt-in operation does not alter restaurant guides, formulas, dataset,
    legal copy, publication dates, or new generated resources.
    """
    from build_restaurant_pages import parse_meals, n
    from refine_search_visibility import rankings

    meals = parse_meals()
    changed = []
    path = ROOT / "healthy-fast-food.html"
    before = path.read_text(encoding="utf-8")
    after, featured = rankings(before, meals)
    def schema(match):
        node = json.loads(match[1])
        if node.get("@type") == "CollectionPage" and before != after:
            node["dateModified"] = "2026-10-03"
        if node.get("@type") == "ItemList":
            node["numberOfItems"] = len(featured)
            node["itemListElement"] = [
                {"@type": "ListItem", "position": i, "name": m["name"],
                 "url": "https://getmacros.net/" + m["url"] + "#menu-comparison"}
                for i, m in enumerate(featured, 1)]
        return '<script type="application/ld+json">' + json.dumps(node, ensure_ascii=False) + '</script>'
    after = re.sub(r'<script type="application/ld\+json">(.*?)</script>', schema, after, flags=re.S)
    if before != after:
        path.write_text(after, encoding="utf-8")
        changed.append(path.name)

    path = ROOT / "best-fast-food-restaurants-for-your-goals.html"
    before = path.read_text(encoding="utf-8")
    indexed = {(m["chain"], m["name"]): m for m in meals}
    keys = [
        ("Chick-fil-A", "Grilled Nuggets, 12 count"),
        ("Chipotle", "High Protein-High Fiber Bowl"),
        ("Subway", "6-inch Grilled Chicken & Fresh Avocado"),
        ("Panera", "Hearty Fireside Chili, bowl"),
        ("Sweetgreen", "Shroomami"),
        ("Panda Express", "Bigger Plate: fried rice + 3 grilled teriyaki chicken entrées"),
    ]
    rows = []
    for key in keys:
        m = indexed[key]
        rows.append('<tr><th scope="row">' + html.escape(" — ".join(key)) + '</th>' + ''.join(
            '<td data-label="' + label + '">' + n(m[field], unit) + '</td>'
            for field, label, unit in [("cal", "Calories", ""), ("p", "Protein", " g"),
                                       ("f", "Fiber", " g"), ("na", "Sodium", " mg")]) + '</tr>')
    after = re.sub(r'(<table class="data-table">.*?<tbody>).*?(</tbody>)',
                   lambda match: match[1] + ''.join(rows) + match[2], before, count=1, flags=re.S)
    after = after.replace(
        "This very large order combines fried rice and three chicken entrées. It may suit a large appetite, but has more than a day’s 2,300 mg sodium reference before extra sauce.",
        "This very large order combines a full fried-rice side and three chicken entrées. Its 2,640 mg sodium exceeds the 2,300 mg daily label reference before extra sauce. Compare both the portion and sodium with a smaller order.")
    after = after.replace(
        "We have removed older Power Menu Bowl examples. Where we could not confirm a current nutrient value, the finder shows a dash and excludes that item from filters that require the missing number.",
        "A dash means a nutrient value has not been confirmed. The finder excludes that order when a filter needs the missing number; it does not treat the dash as zero.")
    after = after.replace('2,300 mg daily label reference',
        '<a href="https://www.fda.gov/food/nutrition-facts-label/how-understand-and-use-nutrition-facts-label">2,300 mg daily label reference</a>') if 'href="https://www.fda.gov/food/nutrition-facts-label/how-understand-and-use-nutrition-facts-label">2,300' not in after else after
    # This source-backed comparison changes actual data, not merely its design.
    if before != after:
        after = after.replace("By GetMacros · Updated September 9, 2026", "By GetMacros · Comparison data updated October 3, 2026")
        after = after.replace('"dateModified": "2026-09-09"', '"dateModified": "2026-10-03"')
        path.write_text(after, encoding="utf-8")
        changed.append(path.name)

    edits = {
        "are-diet-drinks-bad-for-you.html": [
            ("What to take away", "Choose drinks by what they replace"),
            ("Diet drinks are not poison and they are not a requirement.", "Diet drinks are optional.")],
        "calories-vs-macros-what-matters-more.html": [
            ("What to take away", "Start with calories, then check protein and fat"),
            ("For restaurant meals, select the calorie range and one or two priorities in", "For restaurant meals, choose a calorie range and one or two priorities in"),
            ("Calories decide the size of the energy budget. Macros influence what the budget supports and how livable it feels.", "Calories describe your energy intake. Protein, carbohydrate and fat affect what you eat and how the plan fits your day.")],
        "does-creatine-cause-hair-loss.html": [
            ("What to take away", "What the evidence means for your decision")],
        "how-much-protein-can-your-body-absorb.html": [
            ("What to take away", "Plan the daily total, then your meals"),
            ("Three questions that get collapsed into one", "Absorption, muscle growth and daily intake"),
            ("For general health rather than maximizing hypertrophy, needs and priorities differ.", "For general health rather than maximizing muscle growth, needs and priorities differ.")],
    }
    for name, pairs in edits.items():
        path = ROOT / name
        before = path.read_text(encoding="utf-8")
        after = before
        for old, new in pairs:
            after = after.replace(old, new)
        if before != after:
            path.write_text(after, encoding="utf-8")
            changed.append(name)
    return changed


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=OUT)
    ap.add_argument("--apply-reviewed", action="store_true", help="Reapply six reviewed copy/data edits after the shared builder, then run the report")
    args = ap.parse_args()
    if args.apply_reviewed:
        print("Reviewed edits applied: " + (", ".join(apply_reviewed_edits()) or "already current"))
    result = audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Checked {result['pageCount']} existing pages / {result['authoredBlockCount']} authored blocks; "
          f"{len(result['repeatedSentences'])} sentence groups, {len(result['repeatedHeadings'])} heading groups, "
          f"{len(result['nearParagraphs'])} near-paragraph pairs. Written {args.output}")


if __name__ == "__main__":
    main()
