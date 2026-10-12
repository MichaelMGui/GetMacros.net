"""A small reviewed factual Canadian sample, separate from licensed bulk sources."""
import hashlib, json, re
from import_branded_foods import ROOT, RAW, DATE, NUTRIENTS, publish, dump, hash_value
OUT=ROOT/'data/branded-foods/retailer-ca'
def run():
    rows=json.loads((ROOT/'tools/master_release/retailer-ca-reviewed.json').read_text(encoding='utf-8'));records=[]
    for row in rows:
        path=RAW/('retailer-ca-'+row['slug']+'.html')
        html=path.read_text(encoding='utf-8');assert row['item'] in html and 'Nutritional' in html,'Private source evidence missing'
        gram=row['servingGrams'];source={k:row['nutrients'].get(k) for k in NUTRIENTS};values={k:v*100/gram if v is not None else None for k,v in source.items()}
        identity={k:row[k] for k in ['item','name','package','ingredients','servingGrams']};identity['market']='CA'
        record={'id':'branded:retailer-ca:costco:'+row['item'],'name':row['name'],'brand':row['brand'],'brandName':row['brand'],'brandOwner':None,'type':'branded','market':'CA','markets':['CA'],
                'category':'Canadian retailer label sample','language':'en','barcode':None,'barcodeNormalized':None,'package':row['package'],'productId':row['item'],'formulation':hash_value(identity),'ingredients':row['ingredients'],
                'sourceId':'costco-canada-label-sample-2026-10','sourceOrigin':'Costco Canada — supplier label table','sourceRef':row['item'],'sourceUrl':row['url'],'sourceRelease':'Four source pages reviewed October 2026',
                'sourcePublished':None,'sourceModified':None,'labelDate':None,'sourceChecked':DATE,'retrievedAt':DATE,'status':'retailer-label-source-checked',
                'basis':{'amount':100,'unit':'g'},'nutrients':values,'portions':[{'id':'source-serving','label':f'{gram:g} g retailer label serving','grams':gram}],
                'serving':f'{gram:g} g retailer label serving','sourceServing':{'amount':gram,'unit':'g','label':None},'sourcePerServing':source,
                'provenance':{k:{'method':'Retailer supplier-label fact; per-serving value × 100 / serving grams','nativeAmount':v,'nativeUnit':NUTRIENTS[k][1],'nativeBasisGrams':gram} for k,v in source.items() if v is not None},
                'flags':row['flags']+['Official Canadian retailer page checked; today\'s physical package was not independently inspected. Barcode is not published in this sample.'],
                'availability':'A Canadian source listing, not real-time stock or an assertion of availability in every warehouse.','rights':'GetMacros factual extraction; source text, site, trademarks and images retain their respective rights.',
                'sourceEvidenceSha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        record['version']=hash_value(record);records.append(record)
    manifest=publish(records,output=OUT,source={'id':'costco-canada-label-sample-2026-10','name':'Costco Canada — four reviewed supplier-label tables','edition':'October 2026 retrieval',
        'url':'https://www.costco.ca/','sourcePages':[r['url'] for r in rows],'retrievedAt':DATE,'license':'GetMacros factual curation; third-party website/text/image rights not relicensed',
        'quality':'Canadian retailer source nutrition and serving facts reviewed; barcode and label formulation dates not supplied. Source limitations retained. Not independent package verification.',
        'scope':'Four Canadian Kirkland products. Not a bulk Costco catalogue, complete store range, or warehouse inventory.'})
    dump(ROOT/'docs/master-release-2026-10-12/retailer-ca-import.json',{'published':len(records),'market':'CA','records':[{'id':r['id'],'name':r['name'],'source':r['sourceUrl'],'sourceSha256':r['sourceEvidenceSha256']} for r in records],'barcodesPublished':0,'flagged':['macadamia-container-serving-count'],'bytes':sum(p.stat().st_size for p in OUT.rglob('*.json')),'version':manifest['version']})
    print('Published',len(records),'specific Canadian retailer-label foods; no barcode or inventory invented.')
if __name__=='__main__':run()
