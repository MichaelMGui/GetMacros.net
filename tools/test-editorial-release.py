"""Editorial arithmetic, overlap, provenance and generated-page quality gates."""
from pathlib import Path
from html import unescape
from difflib import SequenceMatcher
import ast, json, math, re, sys, hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_editorial_release import load,plain,render

def calc(expr):
    node=ast.parse(expr,mode='eval')
    allowed=(ast.Expression,ast.Constant,ast.BinOp,ast.UnaryOp,ast.Add,ast.Sub,ast.Mult,ast.Div,ast.USub,ast.UAdd,ast.Load)
    assert all(isinstance(n,allowed) for n in ast.walk(node)),expr
    return eval(compile(node,'<checked arithmetic>','eval'),{'__builtins__':{}},{})

def run():
    rows=load();checked=[r for r in rows if r['status']=='checked']
    assert len({r['slug'] for r in rows})==len(rows)
    assert len({r['intent'] for r in checked})==len(checked)
    assert len({r['title'] for r in checked})==len(checked)
    assert len({hashlib.sha256(r['body'].encode()).hexdigest() for r in checked})==len(checked)
    source_urls={r['url'] for r in json.loads((ROOT/'tools/editorial_release/sources.json').read_text(encoding='utf-8')) if r['status']=='inspected'}
    baseline=json.loads((ROOT/'tools/editorial_release/existing-routes.json').read_text(encoding='utf-8'))
    payload=json.loads((ROOT/'tools/restaurant_release/expansion-payload.json').read_text(encoding='utf-8'))
    records={r['recordKey']:r for r in payload['records']}
    arithmetic=0;facts=0;dataset_checks=0;paragraphs={};repeated=[];scores=[]
    template=(ROOT/'how-to-read-a-nutrition-label.html').read_text(encoding='utf-8')
    for row in checked:
        assert row['slug'] not in baseline,row['slug']
        assert len(plain(row['body']).split())>=200,(row['slug'],'short body')
        assert row['body'].count('<h2>')>=2,(row['slug'],'structure')
        assert all(s['url'] in source_urls for s in row['sources']),row['slug']
        assert row['utility'] and row['scope'] and len(row['description'])>=30,row['slug']
        assert not re.search(r'\b(unlock|supercharge|perfect for you|expert reviewed)\b',plain(row['body']),re.I),row['slug']
        for expr,expected in row.get('arithmeticChecks',[]):
            arithmetic+=1;assert math.isclose(calc(expr),expected,rel_tol=1e-10,abs_tol=1e-10),(row['slug'],expr,expected,calc(expr))
        for fact in row.get('tableFacts',[]):
            facts+=1;actual=records[fact['recordKey']]
            assert fact['values']==actual['values'],(row['slug'],'nutrition payload changed')
            assert fact['serving']==actual['provenance']['serving'],(row['slug'],'serving changed')
            assert fact['sourcePage']==actual['sourcePage'] and fact['sourceRow']==actual['sourceRow'],(row['slug'],'source identity changed')
            assert actual['provenance']['source'] in [s['url'] for s in row['sources']],(row['slug'],'missing supporting source')
        if row.get('datasetCalculation'):
            dataset_checks+=1;kind=row['datasetCalculation']['type']
            assert len(payload['records'])==380 and len(payload['chains'])==10
            if kind=='methods':assert sum(r['orderKind']=='calculated complete order' for r in payload['records'])==2
            elif kind=='inNOutVariants':assert sum(r['meal']['chain']=='In-N-Out' for r in payload['records'])==9
            elif kind=='breakfastByChain':assert sum(r['meal']['meal']=='breakfast' for r in payload['records'])==48
            elif kind=='fiberExactness':assert sum(r['values']['f'] is None for r in payload['records'])==10
            elif kind=='countsByChain':assert sum(c['records'] for c in payload['chains'])==380
            else:raise AssertionError(kind)
        text=render(row,template)
        assert text.count('<main ')==1 and text.count('<h1>')==1
        assert 'https://getmacros.net/'+row['slug'] in text
        for p in re.findall(r'<p>(.*?)</p>',row['body'],re.S):
            p=plain(p)
            if len(p.split())<10:continue
            if p in paragraphs:repeated.append({'routes':[paragraphs[p],row['slug']],'paragraph':p})
            paragraphs[p]=row['slug']
        for r in row['related']:
            target=ROOT/r['url'].split('?')[0].lstrip('/')
            if target.is_dir():target=target/'index.html'
            assert target.is_file(),(row['slug'],r['url'])
        if (ROOT/row['slug']).exists():
            html=(ROOT/row['slug']).read_text(encoding='utf-8')
            assert row['title'] in unescape(html)
            for p in re.findall(r'<p>(.*?)</p>',row['body'],re.S):assert plain(p) in plain(html),(row['slug'],'authored copy missing')
    for i,a in enumerate(checked):
        for b in checked[i+1:]:
            ratio=SequenceMatcher(None,plain(a['body']),plain(b['body']),autojunk=True).ratio()
            if ratio>.55:scores.append({'routes':[a['slug'],b['slug']],'ratio':round(ratio,3)})
    assert not repeated, repeated
    assert not scores,scores
    out=ROOT/'docs/playful-release-2026-10-04/editorial';out.mkdir(parents=True,exist_ok=True)
    # Title similarity is a review aid, not a claim of semantic equivalence.
    old=[]
    for route in baseline:
        path=ROOT/route
        if not path.is_file():continue
        match=re.search(r'<title>(.*?)</title>',path.read_text(encoding='utf-8'),re.S)
        if match:old.append((route,plain(match[1]).split(' | ')[0]))
    overlaps=[]
    for row in checked:
        ranked=sorted([(SequenceMatcher(None,row['title'].lower(),title.lower()).ratio(),route,title) for route,title in old],reverse=True)[:2]
        overlaps.append({'newRoute':row['slug'],'intendedQuestion':row['intent'],'closestExistingTitles':[{'route':route,'title':title,'characterSimilarity':round(ratio,3)} for ratio,route,title in ranked]})
    (out/'existing-intent-review.json').write_text(json.dumps(overlaps,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'checks.json').write_text(json.dumps({'checkedNewArticles':len(checked),'arithmeticCases':arithmetic,'restaurantFactsCrossChecked':facts,'datasetCalculationsChecked':dataset_checks,'exactRepeatedAuthoredParagraphs':repeated,'nearDuplicateBodies':scores,'checks':['distinct titles/reader intents/routes against baseline','authored body and semantic headings','inspected source URL registry','safe reproducible arithmetic','exact restaurant fields/portions/source identity against verified payload','snapshot denominator and classification counts','internal references exist','rendered template metadata/main count','all authored paragraphs retained when generated'],'notCovered':['human visual inspection of every article','medical expert review','field performance','external source reachability on every build']},indent=2),encoding='utf-8')
    print('PASS:',len(checked),'new articles;',arithmetic,'arithmetic cases;',facts,'restaurant rows;',dataset_checks,'snapshot checks; no repeated authored paragraphs or near-duplicate bodies.')

if __name__=='__main__':run()
