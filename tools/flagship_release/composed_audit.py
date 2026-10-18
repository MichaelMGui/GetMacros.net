"""Read-only integration audit. Writes only the owned composed-order report."""
from pathlib import Path
from collections import Counter
import copy,hashlib,json,re,unittest
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/flagship-release-2026-10-18/markets/composed-order-audit.json'
FIELDS=('cal','p','c','fat','f','na','sugar','sat')
DATE='2026-10-18'
def norm(x):return re.sub(r'[^a-z0-9]+','',str(x).lower())
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def audit():
    path=ROOT/'js/order-registry.json';raw=path.read_bytes();records=json.loads(raw)['records']
    by_id={r['id']:r for r in records if r.get('id')}
    refreshed=json.loads((ROOT/'tools/flagship_release/markets_release_records.json').read_text(encoding='utf-8'))['updates']
    updated_ids={r['id']for r in refreshed};findings=[];patches=[];summary=Counter()
    def lookup(order,c):
        rid=c.get('recordId')or c.get('id')
        if rid:return by_id.get(rid),'exact dependency ID'
        name=c.get('name')or c.get('item')
        if order['market']=='US' and order['chain']=='Chick-fil-A' and name=='Grilled Chicken Club Sandwich':
            return by_id.get('US|chick-fil-a|official-10309'),'official product page explicitly names Colby Jack; 520kcal/37P/45C/22F/1055Na agree with this exact variant'
        exact=[r for r in records if r['market']==order['market'] and r['chain']==order['chain'] and norm(r['name'])==norm(name) and r is not order and r.get('verificationStatus')!='calculated-from-official-components']
        if len(exact)==1:return exact[0],'exact same-market same-chain name'
        reviewed=[r for r in exact if r.get('verificationStatus')=='official-table-reviewed']
        if len(reviewed)==1:return reviewed[0],'unique exact name in current reviewed local snapshot'
        return None,'no unambiguous source-linked current identity'
    for i,r in enumerate(records):
        if r['market']not in('US','CA')or not r.get('components')or r.get('verificationStatus')=='official-table-reviewed':continue
        deps=r.get('calculatedFrom')or r['components'];parts=[];snapshot_parts=[];resolution=[];problems=[]
        for c in deps:
            q=c.get('quantity',c.get('count'))
            current,method=lookup(r,c)
            embedded=c.get('values')or(c if isinstance(c.get('cal'),(int,float))else None)
            use=current if current and (r.get('calculatedFrom')or c.get('recordId')or c.get('id')or (r['chain']=='Chick-fil-A'))else embedded
            if q is None:problems.append('Unspecified component quantity: '+str(c.get('item')or c.get('name')))
            if use is None:problems.append('No numeric/source-linked component: '+str(c.get('item')or c.get('name')))
            parts.append((use,q));snapshot_parts.append((embedded,q))
            resolution.append({'name':c.get('item')or c.get('name'),'quantity':q,'currentRecordId':current.get('id')if current else None,'currentSourceDate':current.get('sourceDate')if current else None,'currentChecked':current.get('checked')if current else None,
                'method':method,'usesRefreshedSource':bool(current and current.get('id')in updated_ids),'embeddedSnapshotPreserved':embedded is not None,
                'embeddedNutrientChanges':{k:{'snapshot':embedded.get(k),'current':current.get(k)}for k in FIELDS if embedded is not None and current is not None and embedded.get(k)is not None and embedded.get(k)!=current.get(k)}})
        expected={};differences={};published=[]
        if not problems:
            for k in FIELDS:
                if all(p is not None and p.get(k)is not None and isinstance(q,(int,float))for p,q in parts):expected[k]=round(sum(p[k]*q for p,q in parts),8)
                else:expected[k]=None
                actual=r.get(k)
                if actual is None or expected[k]is None:continue
                if abs(actual-expected[k])>.01:
                    prov=r.get('nutrientProvenance',{}).get(k,{})
                    if prov.get('method')=='published':published.append({'nutrient':k,'published':actual,'componentArithmetic':expected[k],'reason':'Source explicitly identifies this field as restaurant-published, not component-derived. Preserve published value and visible methodology.'})
                    else:differences[k]={'current':actual,'expectedComponentSum':expected[k]}
        status='unresolved original component metadata'if problems else 'derived arithmetic correction required'if differences else 'matches component arithmetic; published exceptions documented'if published else 'matches component arithmetic'
        key={'id':r.get('id'),'market':r['market'],'chain':r['chain'],'name':r['name']}
        finding={**key,'registryPositionForEvidenceOnly':i,'status':status,'source':r.get('source'),'sourceDate':r.get('sourceDate'),'storedCheckedAt':r.get('checked'),'componentResolution':resolution,'expectedFromExplicitComponents':expected,'differences':differences,'publishedExceptions':published,'unresolved':problems,'historicalPolicy':'Retain source editions and embedded portion snapshots. This audit does not touch diary, saved-order or exported historical snapshots.'}
        if r['chain']=='Chick-fil-A':
            finding['inclusionScope']='Only the named sandwich/side/nugget/fruit/tea portions. No additional sauce or drink is inferred. Official U.S. Club page names Colby Jack and says it pairs well with Honey Roasted BBQ; no packet is added to the published520-kcal sandwich total.'
            if r['market']=='US':
                finding['sourceCheck']={'url':'https://www.chick-fil-a.com/menu/entrees/chick-fil-a-grilled-chicken-club-sandwich','checkedAt':DATE,'observed':{'cal':520,'p':37,'c':45,'fat':22,'na':1055,'cheese':'Colby Jack'},'scope':'U.S. default Club only; Canadian recipes remain separate.'}
            else:
                finding['sourceCheck']={'url':'https://www.chick-fil-a.ca/nutrition-allergens','checkedAt':DATE,'scope':'Exact Canadian 205g grilled sandwich,96g small fries and451g small unsweet tea from reviewed local snapshot; no U.S. recipe used.'}
        findings.append(finding);summary[status]+=1
        if differences:
            patches.append({'selector':key,'expectedRecordSha256':digest(r),'before':{k:v['current']for k,v in differences.items()},'set':{k:v['expectedComponentSum']for k,v in differences.items()},'reason':'Explicit known component arithmetic mismatch; no source-published total overwritten.','preserveHistoricalDiarySnapshots':True})
    # Calorie-only opportunities are data candidates, not imported records.
    from lxml import html
    food_path=ROOT/'docs/flagship-release-2026-10-18/markets/sources/starbucks-mx-hot.html'
    tree=html.fromstring(food_path.read_bytes());data=json.loads(tree.xpath('//script[@id="__NEXT_DATA__"]')[0].text)['props']['pageProps']
    calories=[];unsized=[]
    for p in data['products']:
        sizes=re.findall(r'(Corto|Alto|Grande|Venti):\s*(\d+(?:\.\d+)?)\s*kcal',p['subtitle'])
        for size,value in sizes:
            calories.append({'market':'MX','restaurant':'Starbucks','name':p['title'],'size':size,'serving':'1 default named '+size+' drink; volume not supplied','cal':float(value),'p':None,'c':None,'fat':None,'source':'https://www.starbucks.com.mx'+p['url'],'verificationStatus':'official source-reported calories only','macroComplete':False,'finderSupported':False,'allowCustomizations':False})
        if not sizes:unsized.append({'name':p['title'],'subtitle':p['subtitle'],'source':'https://www.starbucks.com.mx'+p['url'],'disposition':'No size/volume parsed; defer exact-portion publication until reviewed.'})
    mexico={'status':'Usable official calorie-only servings exist; not fully unavailable','sourceMenu':'https://www.starbucks.com.mx/menu/bebidas/calientes','capturedFile':food_path.relative_to(ROOT).as_posix(),'sourceHash':hashlib.sha256(food_path.read_bytes()).hexdigest(),
        'productTitlesInCapturedCategory':len(data['products']),'explicitNamedSizeServings':len(calories),'sourceReportedZeroCalorieServings':sum(r['cal']==0 for r in calories),'candidates':calories,'unsizedProductsDeferred':unsized,
        'independentItemCheck':{'source':'https://www.starbucks.com.mx/producto/latte','capturedFile':'docs/flagship-release-2026-10-18/markets/sources/starbucks-mx-latte.html','observedCalories':{'Alto':120,'Grande':150,'Venti':200}},
        'publicationConditions':['Label calories-only and show all macros unknown, including source zero-calorie drinks.','Retain named Mexican sizes; do not infer U.S. volumes or formulations.','Default published recipe only; no custom milk, syrup, size or hot/iced changes guessed.','Suitable for honest local logging and source-backed calorie comparison, not macro-complete matching.','Not evidence of every current menu, local stock, official serving-weight or exact-image rights.'],
        'noImportPerformed':True,'sourcePublicationDate':None,'retrievedAt':DATE}
    out={'reviewedAt':DATE,'registrySha256':hashlib.sha256(raw).hexdigest(),'scope':'US/CA stored component-bearing derived records, excluding official item ingredient lists. Source refresh dependency audit, not a complete new verification of every restaurant source.',
         'summary':dict(summary),'ordersAudited':len(findings),'cfaOrdersAudited':sum(r['chain']=='Chick-fil-A'for r in findings),'refreshAffectedCfaNumericChanges':sum(bool(c['embeddedNutrientChanges'])for r in findings if r['chain']=='Chick-fil-A'for c in r['componentResolution']),
         'requiredCorrectionPatch':{'updates':patches,'removeIds':[],'policy':'Apply catalog corrections only after precondition match; preserve historical diaries/saved nutrient snapshots.'},'findings':findings,'mexicoCalorieOnly':mexico}
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return out

class AuditTests(unittest.TestCase):
    def test_cross_market_and_unknowns(self):
        report=audit();self.assertGreater(report['ordersAudited'],20)
        for row in report['findings']:
            for c in row['componentResolution']:
                rid=c['currentRecordId']
                if rid and'|'in rid and rid.split('|')[0]in('US','CA'):self.assertEqual(rid.split('|')[0],row['market'])
        mx=report['mexicoCalorieOnly'];self.assertEqual(mx['explicitNamedSizeServings'],38)
        for r in mx['candidates']:
            self.assertIsNone(r['p']);self.assertIsNone(r['c']);self.assertIsNone(r['fat']);self.assertFalse(r['finderSupported'])
    def test_cfa_refresh_dependencies(self):
        r=audit();self.assertEqual(r['refreshAffectedCfaNumericChanges'],0)
        cfa=[x for x in r['findings']if x['chain']=='Chick-fil-A']
        self.assertEqual(len(cfa),3)
        self.assertTrue(all(not x['differences']and not x['unresolved']for x in cfa))

if __name__=='__main__':
    import sys
    if'--test'in sys.argv:sys.argv.remove('--test');unittest.main(verbosity=2)
    else:
        r=audit();print(json.dumps({k:r[k]for k in('ordersAudited','cfaOrdersAudited','summary','refreshAffectedCfaNumericChanges')},indent=2));print('Required catalog updates:',len(r['requiredCorrectionPatch']['updates']));print('Mexican named calorie-only sizes:',r['mexicoCalorieOnly']['explicitNamedSizeServings'])
