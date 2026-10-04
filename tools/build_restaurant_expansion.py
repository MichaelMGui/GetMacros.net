#!/usr/bin/env python3
"""Build verified restaurant expansion artifacts; --apply explicitly integrates them.

Default operation writes only tools/restaurant_release/. Import metadata_overrides()
before meal_provenance.pack() in rebuild_publication.py. No network in this build.
"""
from pathlib import Path
import argparse
import hashlib
import html
import importlib.util
import json
import re
import sys
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'tools/restaurant_release'
sys.path.insert(0, str(ROOT / 'tools'))
from build_meal_finder import parse_meals, goal_tags
from restaurant_identity import mark
from build_playful_interface import food, ARROW

def payload():
    return json.loads((DATA / 'expansion-payload.json').read_text(encoding='utf-8'))

def metadata_overrides():
    """Lossless provenance to merge AFTER legacy overrides, BEFORE pack(metadata)."""
    return {r['recordKey']: r['provenance'] for r in payload()['records']}

def review_records():
    rows = []
    for r in payload()['records']:
        m, p = r['meal'], r['provenance']
        rows.append({'chain': m['chain'], 'name': m['name'], 'source': p['source'],
                     'checked': p['checked'], 'values': {k:r['values'][k] for k in ('cal','p','c','f','na')},
                     **{k:p[k] for k in ('sourceDate','region','serving','fat','components','notes','nutrientProvenance','verificationStatus')}})
    return rows

def serialize(meal):
    m = dict(meal)
    m['t'] = goal_tags(m)
    # These bare keys and the {chain: prefix retain compatibility with the
    # existing generator; values stay valid JSON with properly escaped strings.
    return re.sub(r'"([A-Za-z_]\w*)":', r'\1:', json.dumps(m, ensure_ascii=False, separators=(',', ':')))

def append_meals(src):
    """Pure, idempotent source adapter. Updates only this expansion's known keys."""
    addition = {r['recordKey']:r['meal'] for r in payload()['records']}
    raw_pattern = r'\{chain:.*?\}(?=,\n|\n\];|\n\])'
    present = set()
    def substitute(match):
        parsed = parse_meals(match.group(0) + '\n];')
        if len(parsed) != 1:
            raise ValueError('Existing meal source no longer uses the supported format')
        key = parsed[0]['chain'] + '||' + parsed[0]['name']
        if key not in addition:
            return match.group(0)
        if key in present:
            raise ValueError('Duplicate expansion row already in source: ' + key)
        present.add(key)
        return serialize(addition[key])
    result = re.sub(raw_pattern, substitute, src, flags=re.S)
    missing = [serialize(m) for k,m in addition.items() if k not in present]
    if missing:
        at = result.rfind('\n];')
        if at < 0:
            raise ValueError('No recognized GM_MEALS array terminator; refusing source mutation')
        result = result[:at] + ',\n' + ',\n'.join(missing) + result[at:]
    before, after = parse_meals(src), parse_meals(result)
    expected = len(before) + len(missing)
    if len(after) != expected or len({m['chain']+'||'+m['name'] for m in after}) != expected:
        raise ValueError('Append failed unique-record/count validation')
    return result

def merge_review(existing):
    add = {r['chain']+'||'+r['name']:r for r in review_records()}
    out = []
    for r in existing:
        key = r['chain']+'||'+r['name']
        out.append(add.pop(key, r))
    out.extend(add.values())
    keys = [r['chain']+'||'+r['name'] for r in out]
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate review keys; refusing mutation')
    return out

def validate(require_source_snapshots=False):
    p = payload()
    rows = p['records']
    if len(rows) != p['newOrders'] or len({r['recordKey'] for r in rows}) != len(rows):
        raise ValueError('Record count or unique-key mismatch')
    chains = {c['id']:c for c in p['chains']}
    for r in rows:
        m, v, provenance = r['meal'], r['values'], r['provenance']
        if r['recordKey'] != m['chain']+'||'+m['name']:
            raise ValueError('Wrong identity')
        if m.get('diet') != [] or m.get('meal') not in ('main','breakfast'):
            raise ValueError('Unsupported dietary or meal-time classification')
        for k in ('cal','p','c','f','na','fat'):
            n = v[k]
            if n is not None and (not isinstance(n,(int,float)) or n < 0):
                raise ValueError('Invalid nutrient')
            if k != 'fat' and m[k] != n:
                raise ValueError('Meal/provenance mismatch')
            if not provenance['nutrientProvenance'].get(k):
                raise ValueError('Missing nutrient provenance')
        if v['f'] is not None and v['f'] > v['c']:
            raise ValueError('Fiber exceeds carbohydrate')
        if provenance['region'] != 'U.S.' or not provenance['serving'] or not provenance['source'].startswith('https://'):
            raise ValueError('Missing scope/portion/source')
        for k, info in provenance['nutrientProvenance'].items():
            if info.get('publishedBound') and v[k] is not None:
                raise ValueError('Bound was converted into an exact number')
        if provenance['components']:
            for k in v:
                parts = provenance['components']
                expected = None if any(i['values'][k] is None for i in parts) else sum(i['values'][k]*i['count'] for i in parts)
                if expected != v[k]:
                    raise ValueError('Calculated sum or missing-value propagation failed')
        if r['sourceId'] not in chains:
            raise ValueError('Unknown source identity')
    verified_snapshots = []
    unavailable_snapshots = []
    for c in chains.values():
        if c['records'] != sum(r['sourceId']==c['id'] for r in rows):
            raise ValueError('Chain count mismatch')
        s = c['source']
        if s.get('sha256'):
            f = DATA/'sources'/s['file']
            if not f.exists():
                unavailable_snapshots.append(c['id'])
                if require_source_snapshots:
                    raise ValueError('Private research snapshot unavailable: '+c['id'])
                continue
            if not f.read_bytes().startswith(b'%PDF') or hashlib.sha256(f.read_bytes()).hexdigest()!=s['sha256']:
                raise ValueError('Source snapshot changed: '+c['id'])
            verified_snapshots.append(c['id'])
        elif c['id'] != 'in-n-out' or not s.get('inspection'):
            raise ValueError('Unexplained missing source snapshot')
    return {'newOrders':len(rows),'newChains':len(chains),'publishedOrders':sum(not r['provenance']['components'] for r in rows),
            'calculatedOrders':sum(bool(r['provenance']['components']) for r in rows),
            'incompleteExactNutrition':sum(any(r['values'][k] is None for k in ('cal','p','c','f','na','fat')) for r in rows),
            'sourceSnapshotsVerified':verified_snapshots, 'sourceSnapshotsUnavailable':unavailable_snapshots,
            'checks':['unique identities','known units','U.S. scope','servings','per-nutrient provenance','available private source PDF hashes','fiber bound preservation','component sums','unknown-value propagation']}

def esc(s):
    return html.escape(str(s), quote=True)

def number(v):
    return '—' if v is None else f'{v:,}'

def portion(r):
    p = r['provenance']
    method = 'GetMacros sum of listed individual portions.' if p['components'] else 'Restaurant-published nutrition.'
    text = f'<p>{esc(p["serving"])}</p><p>{method}</p>'
    if p['notes']:
        text += f'<p>{esc(p["notes"])}</p>'
    return '<details><summary>Portion and source</summary>'+text+f'<p><a href="{esc(p["source"])}">Official source, page {r["sourcePage"]}</a></p></details>'

def table(rows):
    head = '<div class="table-wrap" tabindex="0" role="region" aria-label="Recorded order nutrition"><table class="comparison-table restaurant-comparison-table"><thead><tr><th scope="col">Order</th><th scope="col">Calories</th><th scope="col">Protein (g)</th><th scope="col">Carbs (g)</th><th scope="col">Fat (g)</th><th scope="col">Fiber (g)</th><th scope="col">Sodium (mg)</th></tr></thead><tbody>'
    body = ''.join('<tr><th scope="row"><strong>'+esc(r['meal']['name'])+'</strong>'+portion(r)+'</th>'+''.join('<td>'+number(r['values'][k])+'</td>' for k in ('cal','p','c','fat','f','na'))+'</tr>' for r in rows)
    return head+body+'</tbody></table></div>'

NOTES = {
 'arbys':('A sandwich or a bowl?', 'The sweet brisket sandwich and bowl include different builds, not interchangeable serving sizes. A sauce packet or side is another item; breakfast and limited-time entries may not be sold at your location.'),
 'sonic':('Keep the whole order in view', 'A burger, a breakfast sandwich and a hot dog are different starting points. These rows exclude separate drinks and sides. Optional menu items in the brochure require a local availability check.'),
 'qdoba':('Start with the named build', 'A published bowl is not a sum of whichever toppings sound similar. Rice, beans and sauces belong to that exact named build. Change them in QDOBA’s live nutrition tool rather than carrying the original total forward.'),
 'el-pollo-loco':('Dressing and sides change the comparison', 'The salads and tostadas marked in the source exclude dressing. The two-piece chicken meals name tortillas, beans and rice. Compare that full named meal with another full meal, rather than treating a chicken piece as the entire order.'),
 'del-taco':('One taco is still one taco', 'Taco rows use one published taco and its gram weight. A burrito, salad or crispy-chicken box is a separate order. If you want two tacos or a drink, their portions need to be added rather than assumed included.'),
 'noodles':('Regular is not small', 'The source prints regular and small sizes side by side. Every dish here uses the regular column. Add-on chicken, tofu or steak is included only when the dish’s name explicitly includes it.'),
 'culvers':('What “dinner” includes here', 'In the July 2025 guide, dinner nutrition covers the protein, lemon wedge, dinner roll and butter. The shrimp basket covers the shrimp and lemon wedge. Extra sides and drinks are not part of those totals.'),
 'taco-johns':('A taco, a burrito or a bowl', 'Each row retains its listed beef, chicken or other filling. Potato Olés, drinks and sauce packets are separate unless the item itself names them. Select-location and limited-time items need an availability check.'),
 'in-n-out':('Which version of the burger?', 'The published alternatives replace spread with mustard and ketchup, or replace the bun with lettuce. They are different recorded builds. Extra spread, fries and drinks are not included in the burger figures.'),
 'raising-canes':('Published sandwich, calculated orders', 'The sandwich uses Cane’s published row. The two finger orders add the exact individual portions named below. They are not substitutes for the restaurant’s published combo totals, which do not reconcile to the individual-item sums. Exact fiber remains unknown when a component is listed as less than 1 g.')}

def render_main(chain, rows):
    name, slug = chain['chain'], chain['id']
    url = 'restaurant-meal-finder.html?' + urlencode({'chain':name})
    a = min(rows,key=lambda r:r['values']['cal'])
    b = max(rows,key=lambda r:r['values']['p'])
    if a == b:
        b = next(r for r in rows if r != a)
    comparison = [a,b]
    nh, note = NOTES[slug]
    source = chain['source']
    edition = chain['sourceDate'] or 'Not established from the printed document'
    previews = preview_orders(comparison)
    s = f'''<main id="main-content" class="restaurant-reference">
<nav class="breadcrumb" aria-label="Breadcrumb"><div class="container"><a href="index.html">Home</a><span aria-hidden="true"> › </span><a href="restaurant-meal-guides.html">Restaurants</a><span aria-hidden="true"> › </span><span aria-current="page">{esc(name)}</span></div></nav>
<section class="guide-masthead container"><div><div class="guide-identity">{mark(name)}<span>{len(rows)} recorded orders · U.S.</span></div><h1>{esc(name)} nutrition</h1><p>{esc(chain['intro'])}</p></div><div class="guide-character">{food(chain['character'],True)}</div></section>
<section class="guide-discovery container" id="chain-meal-finder"><header><h2>Your order.<br> Your priorities.</h2></header><form class="guide-filter-entry" action="restaurant-meal-finder.html" method="get"><input type="hidden" name="chain" value="{esc(name)}"><label>Calories, up to<input type="number" name="maxCal" min="150" max="2500" placeholder="Any" inputmode="numeric"></label><label>Protein, at least (g)<input type="number" name="minProtein" min="0" max="200" placeholder="Any" inputmode="numeric"></label><button class="btn btn-primary" type="submit">Find meals {ARROW}</button></form></section>
<section class="guide-preview container" aria-labelledby="guide-preview-title"><div class="guide-preview-head"><h2 id="guide-preview-title">Two places to start.</h2><p>Different listed orders. Compare the portions, too.</p></div><div class="guide-orders">{previews}</div></section>
<section class="chain-picks-section"><div class="container"><div class="section-head"><h2>Two orders, side by side</h2></div><p>{esc(a['meal']['name'])} has {number(a['values']['cal'])} calories and {number(a['values']['p'])} g protein. {esc(b['meal']['name'])} has {number(b['values']['cal'])} calories and {number(b['values']['p'])} g protein. These are the listed portions, with their inclusions shown below.</p><p class="table-scroll-note">Scroll sideways for all nutrients. A dash means an exact value is not published.</p>{table(comparison)}<h3>{esc(nh)}</h3><p>{esc(note)}</p></div></section>
<section class="chain-menu-section" id="menu-comparison"><div class="container"><details class="restaurant-menu-sheet"><summary>Compare all {len(rows)} recorded {esc(name)} orders</summary><div class="restaurant-menu-content"><p>Calories are kcal; protein, carbohydrate, fat and fiber are grams; sodium is milligrams. These are listed U.S. orders, not a complete live menu. A dash stays unknown, including published “less than” amounts.</p><p class="table-scroll-note">Scroll sideways for all nutrients.</p>{table(rows)}</div></details></div></section>
<section class="guide-sources"><div class="container"><div class="source-box"><h2>Sources and portions</h2><p>Official nutrition inspected October 4, 2026. Printed source edition: {esc(edition)}. Retrieval does not mean the recipe was re-tested. Local portions, availability and later menu changes can differ.</p><details><summary>View sources and limits</summary><ul><li><a href="{esc(source['url'])}">{esc(name)} official nutrition document</a></li><li><a href="{esc(source['landing'])}">Restaurant nutrition or menu page</a></li><li><a href="sources.html">How GetMacros records nutrition</a></li></ul><p>Each order shows its own serving assumptions and any calculation. Prices and allergen safety are not inferred. GetMacros is independent of {esc(name)}.</p></details></div></div></section>
<section class="guide-return container"><a class="text-action" href="restaurant-meal-guides.html">Another restaurant? {ARROW}</a></section></main>'''
    return s

def preview_orders(rows):
    return ''.join('<article class="guide-order"><h3>'+esc(r['meal']['name'])+'</h3><dl><div><dd>'+number(r['values']['cal'])+'<span> kcal</span></dd><dt>Calories</dt></div><div><dd>'+number(r['values']['p'])+'<span> g</span></dd><dt>Protein</dt></div></dl><p>'+esc(r['provenance']['serving'])+'</p><a class="text-action" href="#menu-comparison">Full nutrition &amp; source '+ARROW+'</a></article>' for r in rows)

def generate_pages():
    template = (ROOT/'chipotle-healthy-meals-macros.html').read_text(encoding='utf-8')
    p = payload()
    output = DATA/'pages'
    output.mkdir(exist_ok=True)
    for c in p['chains']:
        rows = [r for r in p['records'] if r['sourceId']==c['id']]
        title = f'{c["chain"]} Nutrition: Calories & Protein | GetMacros'
        description = f'Compare {len(rows)} recorded U.S. {c["chain"]} orders by calories, protein, carbs, fat, fiber and sodium. Check the exact portion and official source.'
        url = 'https://getmacros.net/'+c['route']
        s = re.sub(r'<main\b.*?</main>',render_main(c,rows),template,count=1,flags=re.S)
        s = re.sub(r'<title>.*?</title>', '<title>'+esc(title)+'</title>',s,count=1,flags=re.S)
        s = re.sub(r'<script type="application/ld\+json">.*?</script>','',s,flags=re.S)
        s = re.sub(r'(<meta\s+(?:name|property)="(?:description|og:description|twitter:description)"\s+content=")[^"]*(")',lambda m:m[1]+esc(description)+m[2],s)
        s = re.sub(r'(<meta\s+(?:name|property)="(?:og:title|twitter:title)"\s+content=")[^"]*(")',lambda m:m[1]+esc(title)+m[2],s)
        s = re.sub(r'(<link rel="canonical" href=")[^"]*(")',lambda m:m[1]+url+m[2],s)
        s = re.sub(r'(<meta property="og:url" content=")[^"]*(")',lambda m:m[1]+url+m[2],s)
        structured = {'@context':'https://schema.org','@type':'WebPage','name':c['chain']+' nutrition','url':url,'description':description}
        s = s.replace('</head>','<script type="application/ld+json">'+json.dumps(structured,ensure_ascii=False)+'</script></head>',1)
        (output/c['route']).write_text(s,encoding='utf-8')
    return [c['route'] for c in p['chains']]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true',help='Explicitly append data/review rows and install generated guides in the repository')
    parser.add_argument('--validate-only',action='store_true')
    args = parser.parse_args()
    result = validate()
    if not args.validate_only:
        result['generatedPages'] = generate_pages()
        (DATA/'metadata-overrides.json').write_text(json.dumps(metadata_overrides(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (DATA/'review-records.json').write_text(json.dumps(review_records(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if args.apply:
        data_path, review_path = ROOT/'js/meal-data.js', ROOT/'tools/restaurant-review.json'
        source = append_meals(data_path.read_text(encoding='utf-8'))
        review = merge_review(json.loads(review_path.read_text(encoding='utf-8')))
        # Validate both artifacts before changing either source of truth.
        data_path.write_text(source,encoding='utf-8')
        review_path.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        for route in result['generatedPages']:
            (ROOT/route).write_text((DATA/'pages'/route).read_text(encoding='utf-8'),encoding='utf-8')
        result['applied'] = True
    result['browserInspection'] = 'Not performed by this data generator; verify installed guides in the integrated release.'
    (DATA/'validation-report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))

if __name__ == '__main__':
    main()
