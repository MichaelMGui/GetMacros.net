"""Read the finished outputs; never run mutating generators during verification."""
from pathlib import Path
from collections import Counter
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urljoin
import json, re, subprocess, unittest, xml.etree.ElementTree as ET, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
HERE = Path(__file__).resolve().parent
FIELDS = ["cal", "p", "c", "fat"]
GLOBAL = "tools/global_coverage_2026_10_17/"


def read(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def finder_supported(row):
    return (row.get("category") not in ["component", "sauce"]
            and row.get("finderSupported", True))


def route_source(route):
    path = ROOT / (route.strip("/") + "/index.html" if route.endswith("/") else route.lstrip("/"))
    return path.read_text(encoding="utf-8")


def identity(row):
    return row.get('id') or '|'.join([row.get('market', 'US'), row['chain'], row['name']])


def published_batches(markets):
    batches = []
    for name in ['restaurant-records.json', 'restaurant-newmarkets-records.json', 'restaurant-supplement-records.json']:
        path = ROOT / GLOBAL / name
        if path.exists():
            batch = read(GLOBAL + name)
            rows = [row for row in batch['records'] + batch.get('updates', []) if row['market'] in markets]
            batches.append((name, rows))
    for name in ['markets_release_records.json','uk_records.json','markets_mexico_calories.json']:
        path=ROOT/'tools/flagship_release'/name
        if path.exists():
            batch=json.loads(path.read_text(encoding='utf-8'))
            batches.append((name,[row for row in batch['records']+batch.get('updates',[]) if row['market'] in markets]))
    return batches


class Markup(HTMLParser):
    """Inspect links/cards across old and current markup without CSS assumptions."""
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = {'tag': 'document', 'attrs': {}, 'children': []}
        self.stack = [self.root]
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = {'tag': tag, 'attrs': dict(attrs), 'children': []}
        self.stack[-1]['children'].append(node)
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index]['tag'] == tag:
                self.stack = self.stack[:index]
                break

    def handle_data(self, data):
        self.stack[-1]['children'].append(data)

    @staticmethod
    def nodes(node, tag):
        result = [node] if node['tag'] == tag else []
        for child in node['children']:
            if isinstance(child, dict):
                result.extend(Markup.nodes(child, tag))
        return result

    @staticmethod
    def text(node):
        return ' '.join(child if isinstance(child, str) else Markup.text(child) for child in node['children'])

    @staticmethod
    def links(node):
        return {link['attrs'].get('href') for link in Markup.nodes(node, 'a')}


def actual_finder_counts():
    """Execute the trusted data assets used by the real finder, not the registry."""
    script = r"""
const fs=require('node:fs'),vm=require('node:vm');
const definitions={window:{}};vm.runInNewContext(fs.readFileSync('js/market-definitions.js','utf8'),definitions);
const files=Object.fromEntries(Object.keys(definitions.window.GM_MARKETS).map(market=>[market,market==='CA'?'canada-meals.js':market.toLowerCase()+'-meals.js']));
const result={};
for(const [market,file]of Object.entries(files)){
 const scope={window:{}};
 vm.runInNewContext(fs.readFileSync('js/'+file,'utf8'),scope,{filename:file});
 const rows=scope.window.GM_MEALS;
 if(!Array.isArray(rows))throw Error(file+' has no finder meal array');
 const chains={},markets={};
 for(const r of rows){chains[r.chain]=(chains[r.chain]||0)+1;const country=r.market||r.country||'missing';markets[country]=(markets[country]||0)+1;}
 result[market]={file,count:rows.length,chains,markets,ids:rows.map(r=>r.id||[r.market||'US',r.chain,r.name].join('|'))};
}
const baseline={window:{}};vm.createContext(baseline);for(const file of ['meal-data.js','meal-provenance.js'])vm.runInContext(fs.readFileSync('js/'+file,'utf8'),baseline);
console.log(JSON.stringify({finders:result,baselineUS:baseline.window.GM_MEALS}));
"""
    result = subprocess.run(["node", "-e", script], cwd=ROOT,
                            capture_output=True, encoding="utf-8", check=True)
    return json.loads(result.stdout)


class CompletedRestaurantIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = read("js/order-registry.json")["records"]
        cls.additions = read("tools/master_completion/restaurant_records.json")["records"]
        cls.presence = read("data/restaurant-presence.json")["relationships"]
        cls.changes = read("tools/master_completion/restaurant_presence.json")
        cls.markets = json.loads(re.search(
            r"window.GM_MARKETS=(.*);",
            (ROOT / "js/market-definitions.js").read_text(encoding="utf-8"))[1])
        cls.batches = published_batches(cls.markets)
        cls.reviewed = list({row['id']:row for _, rows in cls.batches for row in rows}.values())
        cls.actual = actual_finder_counts()
        baseline_us = cls.actual['baselineUS']
        catalogue = read('js/order-catalogue.json')['records']
        rechecked = {r['baselineKey']: r for r in catalogue if not r['isNew']}
        for row in baseline_us:
            key = row['chain'] + '||' + row['name']
            if key in rechecked:
                row['id'] = key
        baseline = baseline_us + [{'id':r['id'], 'market':'US'} for r in catalogue if r['isNew']]
        for source in ['tools/international/records.json', 'tools/master_release/restaurant_records.json', 'tools/master_completion/restaurant_records.json', 'tools/clarity_release/restaurant_additions.json', 'tools/product_release/menu-records.json']:
            baseline.extend(read(source)['records'])
        cls.expected = {identity(row): row for row in baseline}
        cls.expected.update({identity(row): row for row in cls.reviewed})
        cls.upserts = {}
        for path in sorted((ROOT / GLOBAL).glob('*presence*.json')):
            cls.upserts.update({row['id']:row for row in read(str(path.relative_to(ROOT)))['relationships'] if row['country'] in cls.markets})
        current=read('tools/flagship_release/markets_release_records.json')
        mexico=read('tools/flagship_release/markets_mexico_calories.json')
        from flagship_release.uk_integration import presence_upserts
        cls.upserts.update({row['id']:row for row in current['presenceUpserts']+mexico['presenceUpserts']+presence_upserts()})
        for row in cls.presence:
            for alias in row.get('previousPresenceIds',[]):
                if row['id'] in cls.upserts:cls.upserts[alias]=cls.upserts[row['id']]

    def test_all_reviewed_records_integrated_once(self):
        actual = {identity(row):row for row in self.registry}
        self.assertEqual(len(actual), len(self.registry), 'Duplicate registry identity')
        self.assertEqual(set(actual), set(self.expected), 'Registry must contain exactly baseline plus reviewed, published source batches')
        self.assertEqual(set(read('js/order-registry.json')['markets']), set(self.markets))
        for r in self.additions + self.reviewed:
            matched = [x for x in self.registry if x.get("id") == r["id"]]
            self.assertEqual(len(matched), 1, r["id"])
            for field in FIELDS + ["market", "country", "region", "serving", "servingGrams",
                                   "source", "sourceDate", "sourceHash", "sourceVersion",
                                   "additionalNutrients", "nutrientProvenance", "nativeNutrients", "conversions", "nutrientBounds", "finderSupported", "nutrientBasis", "operatingRegion", "localOperatingEntity", "sourceVariants", "servingMillilitres"]:
                if field == 'nutrientBasis' and r['id'] not in {row['id'] for row in self.reviewed}:continue
                self.assertEqual(matched[0].get(field), r.get(field), (r["name"], field))

    def test_country_dataset_and_finder_do_not_leak(self):
        ca = read("js/canada-meals.json")["records"]
        expected = [r for r in self.registry if r["market"] == "CA"]
        self.assertEqual(ca, expected)
        script = (ROOT / "js/canada-meals.js").read_text(encoding="utf-8")
        start = re.search(r"window.GM_MEALS\s*=\s*", script)
        self.assertIsNotNone(start, "Canadian finder has no serialized local meal array")
        # The shipped payload packs repeated keys and strings. Evaluate the
        # same JavaScript as the browser before comparing every factual field.
        replay = "const fs=require('fs'),vm=require('vm'),c={window:{}};vm.runInNewContext(fs.readFileSync(0,'utf8'),c);process.stdout.write(JSON.stringify(c.window.GM_MEALS));"
        finder = json.loads(subprocess.run(['node','-e',replay],input=script,capture_output=True,encoding='utf-8',check=True,cwd=ROOT).stdout)
        from build_global_coverage_release import finder_record
        self.assertEqual(finder, [finder_record(r) for r in expected if finder_supported(r)])
        self.assertTrue(all(r["market"] == "CA" for r in finder))
        self.assertFalse(any(r.get("category") in ["component", "sauce"] for r in finder))
        self.assertFalse(any(r["chain"] == "Pizza Nova" for r in finder))
        self.assertEqual(sum(r["chain"] == "New York Fries" for r in finder), sum(finder_supported(r) for r in self.additions))

    def test_presence_counts_reflect_real_country_rows(self):
        self.assertEqual(len({r["id"] for r in self.presence}), len(self.presence))
        baseline = read("tools/master_release/restaurant_presence.json")["relationships"]
        clarity=read('tools/clarity_release/restaurant_additions.json')['presenceRelationships']
        expected_ids = {r["id"] for r in baseline + self.changes["relationships"] + clarity} | set(self.upserts)
        expected_ids.update(row['restaurantMarketId'] for row in self.reviewed)
        expected_ids-=set(alias for r in self.presence for alias in r.get('previousPresenceIds',[]))
        self.assertEqual({r["id"] for r in self.presence}, expected_ids)
        for p in self.presence:
            rows = [r for r in self.registry
                    if r["market"] == p["country"] and r["chain"] == p["restaurantBrand"]]
            supported = [r for r in rows if finder_supported(r)]
            full = [r for r in rows if all(r.get(k) is not None for k in FIELDS)]
            calories_only = [r for r in rows if r.get("cal") is not None
                             and all(r.get(k) is None for k in ["p", "c", "fat"])]
            self.assertEqual(p["trackedRecords"], len(rows), p["id"])
            self.assertEqual(p["completeMacroRecords"], len(full), p["id"])
            self.assertEqual(p["finderRecords"], len(supported), p["id"])
            self.assertEqual(p["finderSupported"], bool(supported), p["id"])
            self.assertEqual(p["caloriesOnlyRecords"], len(calories_only), p["id"])
            self.assertEqual(p["calculatedOrders"], sum(bool(r.get("calculatedFrom")) for r in rows))

    def test_new_operating_presence_never_fakes_nutrition(self):
        by_id = {key:r for r in self.presence for key in [r['id']]+r.get('previousPresenceIds',[])}
        for original in self.changes["relationships"]:
            input_row = self.upserts.get(original['id'], original)
            published = by_id[input_row["id"]]
            self.assertEqual(published["country"], input_row["country"])
            self.assertEqual(published["presence"], input_row["presence"])
            local = [row for row in self.registry if row['market']==published['country'] and row['chain']==published['restaurantBrand']]
            if not local:
                self.assertEqual(published["trackedRecords"], 0)
                self.assertEqual(published["finderRecords"], 0)
                self.assertFalse(published["finderSupported"])
                if input_row.get('nutritionSourceStatus')=='official-source-withheld-conflicts':
                    self.assertEqual(published['nutritionAvailable'],input_row['nutritionAvailable'])
                    self.assertEqual(published['nutritionSources'],input_row['nutritionSources'])
                    self.assertTrue(published['nutritionSources'])
                    self.assertRegex(published['limitations'].lower(),r'(?:discrepanc|conflict|withheld)')
                else:
                    self.assertFalse(published["nutritionAvailable"])
                    self.assertEqual(published["nutritionSources"], [])
            else:
                self.assertTrue(published['nutritionAvailable'])
                self.assertEqual(published['trackedRecords'],len(local))
                self.assertEqual(set(published['nutritionSources']),{row['source'] for row in local})
        for update in self.changes["updates"]:
            published = by_id[update["id"]]
            current = self.upserts.get(update['id'],update)
            self.assertEqual(published["nutritionSourceStatus"], current["nutritionSourceStatus"])
            if update['id'] not in self.upserts:
                self.assertEqual(published["trackedRecords"], 0)
                self.assertFalse(published["finderSupported"])

    def test_new_york_fries_coverage_counts_and_source(self):
        nyf = next(p for p in self.presence if p["id"] == "CA|new-york-fries")
        self.assertEqual((nyf["trackedRecords"], nyf["completeMacroRecords"],
                          nyf["finderRecords"], nyf["calculatedOrders"]), (27, 27, 19, 2))
        self.assertTrue(nyf["nutritionAvailable"])
        self.assertEqual(nyf["nutritionSourceStatus"], "official-table-reviewed")
        self.assertEqual(nyf["nutritionSources"], [self.additions[0]["source"]])
        self.assertEqual(nyf["localMenuSource"], self.additions[0]["sourceParent"])
        self.assertIn("not a complete", nyf["limitations"])

    def test_us_finder_count_matches_the_actual_primary_dataset(self):
        actual = self.actual['finders']['US']['count']
        usa = [r for r in self.registry if r['market'] == 'US']
        self.assertEqual(sum(finder_supported(r) for r in usa), actual)
        original_ids={r['id'] for r in read('js/order-catalogue.json')['records'] if r['isNew']}
        additional = [r for r in usa if r.get('id') in original_ids]
        self.assertEqual(len(additional),sum(r['isNew'] for r in read('js/order-catalogue.json')['records']))
        refreshed={r['id']:r for r in read('tools/flagship_release/markets_release_records.json')['updates']}
        for row in additional:
            self.assertEqual(row['finderSupported'],refreshed[row['id']]['finderSupported'] if row['id'] in refreshed else False)
            if row['finderSupported']:self.assertEqual(row['verificationStatus'],'official-table-reviewed')
        self.assertTrue(all(r.get('source') for r in additional))

    def test_world_index_uses_every_tracked_chain(self):
        html = route_source("/world-restaurant-menus.html")
        document = Markup(html)
        main = Markup.nodes(document.root,'main')[0]
        countries = Markup.nodes(main,'article')
        self.assertEqual(len(countries), len(self.markets))
        for country, info in self.markets.items():
            block = next(x for x in countries if info['home'] in Markup.links(x))
            text = ' '.join(Markup.text(block).split())
            records = [r for r in self.registry if r["market"] == country]
            count = len([r for r in records if finder_supported(r)])
            self.assertRegex(text,rf'\b{len(records)} tracked servings\b',country)
            if 'finder entries' in text:self.assertRegex(text,rf'\b{count} finder entries\b',country)
            if re.search(r'\d+ restaurants\b',text):self.assertRegex(text,rf'\b{len({r["chain"] for r in records})} restaurants\b',country)
            for chain in {r["chain"] for r in records}:
                self.assertIn(chain, text, (country, chain))
            self.assertIn(info['restaurants'],Markup.links(block))
        canada = Markup.text(next(x for x in countries if '/ca/en/' in Markup.links(x)))
        for chain in ["Subway", "Domino’s", "Pizza Nova", "New York Fries", "Booster Juice"]:
            self.assertIn(chain, canada)

    def test_directories_link_local_operations_honestly(self):
        for country, info in self.markets.items():
            with self.subTest(country=country):
                self._assert_directory(country,info)
        ca = unescape(route_source("/ca/en/restaurants/"))
        self.assertIn('href="/ca/en/restaurants/new-york-fries/"', ca)
        self.assertRegex(ca,r'\b27 tracked servings\b')
        self.assertRegex(ca,r'(?:Local nutrition records are not yet available here|Usable nutrition records are not published here yet)')

    def _assert_directory(self,country,info):
        html = route_source(info["restaurants"])
        document=Markup(html);main=Markup.nodes(document.root,'main')[0]
        articles=Markup.nodes(main,'article')
        for row in self.presence:
            if row['country']!=country:continue
            local=[r for r in self.registry if r['market']==country and r['chain']==row['restaurantBrand']]
            cards=[card for card in articles if any(row['restaurantBrand'] in Markup.text(heading) for heading in Markup.nodes(card,'h2'))]
            legacy_card = False
            if not cards and not articles:
                cards=[link for link in Markup.nodes(main,'a') if re.match(r'^\s*'+re.escape(row['restaurantBrand'])+r'(?:\s|→|$)',Markup.text(link))]
                legacy_card = True
            self.assertEqual(len(cards),1,(country,row['restaurantBrand']))
            card=cards[0];text=' '.join(Markup.text(card).split());links={urljoin(info['restaurants'],href) for href in Markup.links(card) if href}
            expected_route=local[0]['url'] if local else row['officialCountryWebsite']
            if not expected_route.startswith(('https://','/')):expected_route='/'+expected_route
            self.assertIn(expected_route,links,(country,row['restaurantBrand']))
            if local:
                if legacy_card:
                    self.assertRegex(text,rf'\b{sum(finder_supported(r) for r in local)} recorded orders\b',(country,row['restaurantBrand']))
                else:
                    self.assertRegex(text,rf'\b{len(local)} (?:tracked servings|source-defined entries)\b',(country,row['restaurantBrand']))
                guide=route_source(expected_route)
                self.assertTrue(any(source in unescape(guide) for source in {r['source'] for r in local}),(country,row['restaurantBrand'],'guide source'))
            else:
                self.assertRegex(text.lower(),r'(?:not (?:yet )?(?:available|published)|unavailable)')
        self.assertRegex(Markup.text(main).lower(),r'(?:another country|country recipes.*separate|country-specific|no u\.s\.|u\.s\.)')

    def test_guide_source_portions_and_seo_are_real(self):
        route = "/ca/en/restaurants/new-york-fries/"
        html = route_source(route)
        main = unescape(re.search(r"<main\b[^>]*>(.*?)</main>", html, re.S)[1])
        self.assertEqual(len(re.findall(r"<h1(?:\s|>)", main)), 1)
        self.assertIn(self.additions[0]["source"], html)
        for term in ["August 20, 2026", "October 13, 2026", "910 kcal",
                     "28 g protein", "1,320 kcal", "33 g protein", "snack", "regular", "large"]:
            self.assertIn(term, main)
        for record in self.additions:
            self.assertIn(record["name"], main)
            self.assertIn(record["serving"], main)
        self.assertRegex(main, r"(?:(?:twice|two|2).{0,40}regular|regular.{0,40}(?:twice|two|2))")
        self.assertRegex(main, r"(?:(?:three|3).{0,40}large|large.{0,40}(?:three|3))")
        self.assertIn("not separately published", main)
        self.assertIn('rel="canonical" href="https://getmacros.net' + route + '"', html)
        self.assertNotRegex(html, r'<meta name="robots"[^>]*noindex')
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        urls = [u.find(ns + "loc").text for u in ET.parse(ROOT / "sitemap.xml").getroot()]
        self.assertEqual(urls.count("https://getmacros.net" + route), 1)
        search = route_source("/search.html")
        self.assertIn('href="' + route + '"', search)

    def test_country_market_chain_definition_comes_from_actual_finder(self):
        for market in self.markets:
            expected=sorted({r['chain'] for r in self.registry if r['market']==market and finder_supported(r)})
            self.assertEqual(self.markets[market]['chains'],expected,market)
        expected=self.markets['CA']['chains']
        self.assertIn("New York Fries", expected)
        self.assertNotIn("McDonald’s", expected)
        self.assertNotIn("Freshii", expected)
        self.assertNotIn("Pizza Nova", expected)

    def test_restaurant_adapter_unit_conversion_and_country_search(self):
        result = subprocess.run(["node", str(HERE / "test_restaurant_adapter.cjs")],
                                cwd=ROOT, capture_output=True, encoding="utf-8", check=True)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "passed")
        self.assertGreaterEqual(report["checks"], 30)

    def test_actual_finder_membership_matches_presence_per_chain(self):
        counts = self.actual['finders']
        for market, actual in counts.items():
            self.assertEqual(actual["markets"], {market: actual["count"]}, actual["file"])
            rows = [r for r in self.registry if r["market"] == market and finder_supported(r)]
            self.assertEqual(len(rows), actual["count"], market)
            self.assertEqual(dict(Counter(r["chain"] for r in rows)), actual["chains"], market)
            self.assertEqual(set(actual['ids']),{identity(r) for r in rows},market)
            self.assertEqual(len(set(actual['ids'])),actual['count'],market)
            page=route_source(self.markets[market]['finder'])
            asset='/js/'+actual['file'];stamps=read('assets/generated/manifest.json') if (ROOT/'assets/generated/manifest.json').exists() else {}
            urls={asset,asset.lstrip('/')}
            if asset.lstrip('/') in stamps:urls.add(stamps[asset.lstrip('/')]['url'])
            scripts={node['attrs'].get('src','').split('?')[0] for node in Markup.nodes(Markup(page).root,'script')}
            self.assertTrue(urls & scripts,(market,'finder does not load its market dataset'))
            for presence in self.presence:
                if presence["country"] == market:
                    self.assertEqual(presence["finderRecords"],
                                     actual["chains"].get(presence["restaurantBrand"], 0),
                                     presence["id"])
        # The U.S. catalogue also has logging/builder records that are deliberately
        # outside the established finder. Their existence must not inflate it.
        baseline_cfa=[r for r in self.actual['baselineUS'] if r['chain']=='Chick-fil-A']
        self.assertEqual(counts['US']['chains']['Chick-fil-A'],sum(finder_supported(r) for r in self.registry if r['market']=='US' and r['chain']=='Chick-fil-A'))
        us_cfa = next(p for p in self.presence
                      if p["country"] == "US" and p["restaurantBrand"] == "Chick-fil-A")
        current=[r for r in read('tools/flagship_release/markets_release_records.json')['records'] if r['market']=='US' and r['chain']=='Chick-fil-A']
        self.assertEqual(us_cfa['trackedRecords'],len(baseline_cfa)+sum(r['isNew'] for r in read('js/order-catalogue.json')['records'])+len(current))
        self.assertEqual(us_cfa['finderRecords'],sum(finder_supported(r) for r in self.expected.values() if r.get('market','US')=='US' and r.get('chain')=='Chick-fil-A'))


if __name__ == "__main__":
    unittest.main(verbosity=2)
