"""Reproducible research queue and source-backed existing-market coverage matrix.

Sources are evidence to review, never an automated assertion that an HTTP 200
means a restaurant operates in a country. Unconfirmed is not absent.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import csv,gzip,hashlib,json,re,urllib.request,urllib.parse
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/flagship-release-2026-10-18/markets'
DATE='2026-10-18'
MARKETS=('US','CA','MX','GB','IE','AU','NZ','JP','FR','IN','SG','ZA')
CANDIDATES=('McDonald’s','Wendy’s','KFC','Burger King','Popeyes','Subway','Domino’s','Pizza Hut','Starbucks','Taco Bell','Five Guys','Shake Shack','Chick-fil-A','Chipotle','Tim Hortons','Jollibee','Papa Johns')
GLOBAL={
 'McDonald’s':'https://corporate.mcdonalds.com/corpmcd/our-company/where-we-operate.html',
 'Wendy’s':'https://www.wendys.com/international',
 'KFC':'https://global.kfc.com/',
 'Burger King':'https://www.rbi.com/English/brands/default.aspx',
 'Popeyes':'https://www.rbi.com/English/brands/default.aspx',
 'Subway':'https://www.subway.com/en-US/ExploreOurWorld',
 'Domino’s':'https://biz.dominos.com/about-us/international/',
 'Pizza Hut':'https://www.yum.com/wps/portal/yumbrands/Yumbrands/company/our-brands/pizza-hut',
 'Starbucks':'https://www.starbucks.com/store-locator',
 'Taco Bell':'https://www.tacobell.com/international',
 'Five Guys':'https://restaurants.fiveguys.com/',
 'Shake Shack':'https://shakeshack.com/locations',
 'Chick-fil-A':'https://www.chick-fil-a.com/locations',
 'Chipotle':'https://locations.chipotle.com/',
 'Tim Hortons':'https://locations.timhortons.com/',
 'Jollibee':'https://www.jollibeegroup.com/brands/jollibee/',
 'Papa Johns':'https://www.papajohns.com/international/'
}
# Candidate official local sources. Retrieval alone does not confirm presence.
LOCAL={
 'US':{'Domino’s':'https://www.dominos.com/en/','Pizza Hut':'https://www.pizzahut.com/','Five Guys':'https://restaurants.fiveguys.com/','Shake Shack':'https://shakeshack.com/locations','Tim Hortons':'https://locations.timhortons.com/en/','Jollibee':'https://www.jollibeefoods.com/pages/locations','Papa Johns':'https://locations.papajohns.com/'},
 'CA':{'Chick-fil-A':'https://www.chick-fil-a.ca/locations','Shake Shack':'https://shakeshack.ca/locations','Pizza Hut':'https://www.pizzahut.ca/','Tim Hortons':'https://locations.timhortons.ca/en/','Jollibee':'https://ca.jollibeefoods.com/pages/locations','Papa Johns':'https://www.papajohns.ca/'},
 'MX':{'Wendy’s':'https://www.wendys.com.mx/','Popeyes':'https://popeyes.com.mx/','Pizza Hut':'https://www.pizzahut.com.mx/','Starbucks':'https://www.starbucks.com.mx/','Five Guys':'https://fiveguys.mx/','Shake Shack':'https://shakeshack.com.mx/','Chipotle':'https://ir.chipotle.com/2026-07-13-CHIPOTLE-ENTERS-MEXICO-WITH-FIRST-RESTAURANT-IN-NUEVO-LEON','Tim Hortons':'https://timhortons.com.mx/','Papa Johns':'https://www.papajohns.com.mx/'},
 'GB':{'Wendy’s':'https://www.wendys.com/en-uk','Burger King':'https://www.burgerking.co.uk/','Popeyes':'https://popeyesuk.com/restaurants','Domino’s':'https://www.dominos.co.uk/','Pizza Hut':'https://www.pizzahut.co.uk/','Starbucks':'https://www.starbucks.co.uk/store-locator','Taco Bell':'https://www.tacobell.co.uk/locations','Five Guys':'https://restaurants.fiveguys.co.uk/','Shake Shack':'https://www.shakeshack.co.uk/locations','Chick-fil-A':'https://www.chick-fil-a.co.uk/locations/','Chipotle':'https://www.chipotle.co.uk/','Tim Hortons':'https://timhortons.co.uk/locations','Jollibee':'https://www.jollibee.uk/locations','Papa Johns':'https://www.papajohns.co.uk/'},
 'IE':{'Wendy’s':'https://wendys.ie/','Burger King':'https://www.burgerking.ie/','Domino’s':'https://www.dominos.ie/','Pizza Hut':'https://www.pizzahut.ie/','Starbucks':'https://www.starbucks.ie/','Five Guys':'https://www.fiveguys.ie/','Papa Johns':'https://www.papajohns.ie/'},
 'AU':{'Wendy’s':'https://www.wendys.com.au/','Burger King':'https://www.hungryjacks.com.au/','Subway':'https://www.subway.com/en-au/','Domino’s':'https://www.dominos.com.au/','Pizza Hut':'https://www.pizzahut.com.au/','Starbucks':'https://www.starbucks.com.au/','Taco Bell':'https://www.tacobell.com.au/','Five Guys':'https://fiveguys.com.au/','Papa Johns':'https://www.papajohns.com.au/'},
 'NZ':{'Wendy’s':'https://www.wendys.co.nz/','Burger King':'https://www.burgerking.co.nz/','Popeyes':'https://www.popeyes.co.nz/','Domino’s':'https://www.dominos.co.nz/','Pizza Hut':'https://www.pizzahut.co.nz/','Starbucks':'https://www.starbucks.co.nz/','Taco Bell':'https://tacobell.co.nz/'},
 'JP':{'Wendy’s':'https://wendys-firstkitchen.co.jp/','Burger King':'https://www.burgerking.co.jp/','Subway':'https://www.subway.co.jp/','Domino’s':'https://www.dominos.jp/','Pizza Hut':'https://www.pizzahut.jp/','Taco Bell':'https://tacobell.co.jp/','Shake Shack':'https://shakeshack.jp/'},
 'FR':{'McDonald’s':'https://www.mcdonalds.fr/','KFC':'https://www.kfc.fr/','Burger King':'https://www.burgerking.fr/','Popeyes':'https://www.popeyesfrance.fr/','Subway':'https://restaurants.subway.com/fr/france','Domino’s':'https://www.dominos.fr/','Pizza Hut':'https://www.pizzahut.fr/','Starbucks':'https://www.starbucks.fr/','Five Guys':'https://restaurants.fiveguys.fr/','Chipotle':'https://www.chipotle.fr/'},
 'IN':{'Wendy’s':'https://wendys.in/','KFC':'https://online.kfc.co.in/','Burger King':'https://www.burgerking.in/','Popeyes':'https://www.popeyes.in/','Subway':'https://www.subway.in/','Domino’s':'https://www.dominos.co.in/','Pizza Hut':'https://www.pizzahut.co.in/','Starbucks':'https://www.starbucks.in/','Taco Bell':'https://www.tacobell.co.in/','Tim Hortons':'https://www.timhortonsindia.com/','Papa Johns':'https://www.papajohns.in/'},
 'SG':{'McDonald’s':'https://www.mcdonalds.com.sg/','KFC':'https://www.kfc.com.sg/','Popeyes':'https://www.popeyes.com.sg/','Subway':'https://www.subway.com/en-SG/','Domino’s':'https://www.dominos.com.sg/','Pizza Hut':'https://www.pizzahut.com.sg/','Starbucks':'https://www.starbucks.com.sg/','Five Guys':'https://fiveguys.sg/','Shake Shack':'https://shakeshack.com.sg/','Chick-fil-A':'https://www.chick-fil-a.com.sg/locations/','Tim Hortons':'https://timhortons.sg/','Jollibee':'https://jollibee.com.sg/'},
 'ZA':{'McDonald’s':'https://www.mcdonalds.co.za/','KFC':'https://www.kfc.co.za/','Burger King':'https://www.burgerking.co.za/','Popeyes':'https://www.popeyes.co.za/','Subway':'https://www.subway.com/en-ZA/','Domino’s':'https://www.dominos.co.za/','Pizza Hut':'https://www.pizzahut.co.za/','Starbucks':'https://www.starbucks.co.za/','Taco Bell':'https://www.tacobell.co.za/','Papa Johns':'https://www.papajohns.co.za/'}
}

def slug(x):return re.sub('[^a-z0-9]+','-',x.lower()).strip('-')
def alias(x):
    if x.startswith('McDonald'):return 'McDonald’s'
    return x

def retrieve():
    todo={**{('GLOBAL',brand):url for brand,url in GLOBAL.items()},**{(m,b):u for m,v in LOCAL.items() for b,u in v.items()}}
    D=DOC/'presence-captures';D.mkdir(exist_ok=True)
    def one(item):
        (m,b),u=item;row={'market':m,'chain':b,'url':u,'retrievedAt':DATE,'retrievalIsVerification':False}
        try:
            with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 (GetMacros menu research)','Accept-Encoding':'identity'}),timeout=20) as z:
                data=z.read();row.update({'finalUrl':z.url,'contentType':z.headers.get('Content-Type',''),'contentEncoding':z.headers.get('Content-Encoding','')})
            row['sha256']=hashlib.sha256(data).hexdigest();row['bytes']=len(data)
            file=D/(m.lower()+'-'+slug(b)+'.html.gz');file.write_bytes(gzip.compress(data,mtime=0));row['file']=file.relative_to(ROOT).as_posix()
            from lxml import html
            tree=html.fromstring(data)
            for e in tree.xpath('//script|//style|//noscript'):e.drop_tree()
            text=' '.join(tree.text_content().split())
            row['title']=' '.join(tree.xpath('//title/text()'))[:240]
            row['textExcerpt']=text[:1800]
            row['locationWords']=len(re.findall(r'(?i)\b(?:locations?|restaurants?|stores?|find us|nos restaurants|店舗|店舗検索|sucursales|restaurantes|commande|order now)\b',text))
            row['blockedPage']=bool(re.search(r'(?i)access denied|verify you are human|just a moment|robot or human|forbidden|request unsuccessful',row['title']+' '+text[:500]))
        except Exception as e:row['error']=str(e)
        return row
    with ThreadPoolExecutor(max_workers=10) as p:rows=list(p.map(one,todo.items()))
    (DOC/'presence-retrieval.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'attempts':len(rows),'captured':sum('sha256'in r for r in rows),'failures':sum('error'in r for r in rows),'blocked':sum(r.get('blockedPage',False) for r in rows)},indent=2))
    return rows

def matrix():
    relationships=json.loads((ROOT/'data/restaurant-presence.json').read_text(encoding='utf-8'))['relationships']
    existing=json.loads((ROOT/'js/order-registry.json').read_text(encoding='utf-8'))['records']
    extra=json.loads((ROOT/'tools/flagship_release/markets_release_records.json').read_text(encoding='utf-8'))
    mexico_file=ROOT/'tools/flagship_release/markets_mexico_calories.json'
    if mexico_file.exists():
        mexico=json.loads(mexico_file.read_text(encoding='utf-8'))
        extra['records']+=mexico['records'];extra['updates']+=mexico.get('updates',[])
    existing=[r for r in existing if r.get('id')not in set(extra.get('withdrawnIds',[]))]
    staged={r['id']:r for r in extra['records']+extra['updates']}
    all_records=[staged.pop(r.get('id'),r) for r in existing]+list(staged.values())
    known={(r['country'],alias(r['restaurantBrand'])):r for r in relationships}
    research=json.loads((DOC/'presence-retrieval.json').read_text(encoding='utf-8'))
    captures={(r['market'],r['chain']):r for r in research}
    review_file=DOC/'presence-reviewed.json'
    reviewed=json.loads(review_file.read_text(encoding='utf-8')) if review_file.exists() else []
    manual={(r['market'],r['chain']):r for r in reviewed}
    keys={(m,b) for m in MARKETS for b in CANDIDATES}|set(known)|set(manual)|{(r['market'],alias(r['chain']))for r in extra['records']}
    rows=[]
    for m,b in sorted(keys):
        old=known.get((m,b));review=manual.get((m,b),{})
        scoped=[r for r in all_records if r['market']==m and alias(r['chain'])==b]
        cap=captures.get((m,b)) or captures.get(('GLOBAL',b),{})
        status=review.get('presenceStatus') or ('confirmed-existing-evidence' if old else 'unconfirmed')
        evidence=review.get('evidenceUrl') or (old['presence']['evidenceUrl'] if old else cap.get('url') or GLOBAL.get(b,''))
        limitations=review.get('observation') or (old['presence']['observation'] if old else 'No reviewed current local operating evidence established in this release. This is unconfirmed, not a claim that the chain is absent.')
        nutrition=sorted({r['source'] for r in scoped}) or (old.get('nutritionSources',[]) if old else [])
        complete=sum(all(r.get(k)is not None for k in('cal','p','c','fat'))for r in scoped)
        calories_only=sum(r.get('cal')is not None and all(r.get(k)is None for k in('p','c','fat'))for r in scoped)
        row={'market':m,'chain':b,'candidateScope':'global chain queue' if b in CANDIDATES else 'additional existing market coverage',
             'presenceStatus':status,'presenceEvidenceUrl':evidence,
             'presenceCheckedAt':review.get('checkedAt') or (old['presence'].get('checkedAt') if old else DATE),
             'officialMarketWebsite':review.get('officialMarketWebsite') or (old.get('officialCountryWebsite') if old else LOCAL.get(m,{}).get(b,'')),
             'localMenuEvidence':review.get('localMenuEvidence') or (old.get('localMenuSource') if old else ''),
             'nutritionSources':nutrition,'existingRecords':sum(r['market']==m and alias(r['chain'])==b for r in existing),
             'newPortionRecords':sum(r['market']==m and alias(r['chain'])==b and r.get('verificationStatus')!='calculated-from-official-components' for r in extra['records']),
             'newCalculatedOrders':sum(r['market']==m and alias(r['chain'])==b and r.get('verificationStatus')=='calculated-from-official-components' for r in extra['records']),
             'completeMacroRecords':complete,'caloriesOnlyRecords':calories_only,
             'newCalorieOnlyRecords':sum(r['market']==m and alias(r['chain'])==b and r.get('cal')is not None and all(r.get(k)is None for k in('p','c','fat'))for r in extra['records']),
             'existingCategories':dict(Counter(r.get('category','unspecified') for r in scoped)),
             'menuCoverageStatus':('reviewed calories-only snapshot selection'if calories_only and not complete else 'reviewed snapshot selection; includes partial data'if calories_only else 'reviewed snapshot selection')if scoped else 'local numeric nutrition not implemented',
             'imageCoverageAndRights':'No exact image acquisition in this market-data workstream; separate image-rights audit applies.',
             'lastResearchAttempt':DATE,'capture':{k:cap[k] for k in ('url','file','sha256','error','blockedPage') if k in cap},
             'disposition':review.get('disposition') or ('retain published source-scoped coverage; continue category audit' if scoped else 'research local menu and numeric nutrition; no substitute-country records'),
             'observation':limitations,
             'unresolvedGaps':review.get('unresolvedGaps') or ('Complete live-menu and branch availability not established.' if scoped else ('Captured page needs explicit operating-presence review; no nutrition publication claim.' if 'sha256'in cap else 'Official local operating and nutrition evidence not captured.'))}
        rows.append(row)
    (DOC/'country-restaurant-matrix.json').write_text(json.dumps({'reviewedAt':DATE,'markets':list(MARKETS),'globalCandidates':list(CANDIDATES),'scope':'17 candidates × 12 existing markets, plus previously tracked chains. Unconfirmed is not absent; source captures are not automatic verification.','rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    fields=['market','chain','presenceStatus','presenceEvidenceUrl','presenceCheckedAt','officialMarketWebsite','localMenuEvidence','nutritionSources','existingRecords','newPortionRecords','newCalculatedOrders','completeMacroRecords','caloriesOnlyRecords','newCalorieOnlyRecords','menuCoverageStatus','disposition','observation','unresolvedGaps']
    with (DOC/'country-restaurant-matrix.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fields);w.writeheader()
        for r in rows:w.writerow({k:' | '.join(r[k]) if isinstance(r[k],list) else r[k] for k in fields})
    print(json.dumps({'relationships':len(rows),'globalQueue':17*12,'dispositions':dict(Counter(r['presenceStatus'] for r in rows))},indent=2))
    return rows

if __name__=='__main__':
    import sys
    if '--fetch' in sys.argv:retrieve()
    else:matrix()
