"""Retrieve only the public U.S. CMS nutrition explorer used by the official app.

The public app code builds the Sanity dataset from environment/brand/region,
and its country enums explicitly distinguish US and CA. This selects US;
Canadian response data is never relabelled as U.S. data.
"""
from pathlib import Path
from datetime import datetime,timezone
import urllib.request,urllib.parse,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs/global-coverage-2026-10-17/restaurants/supplement'
captured=json.loads((D/'browser-responses.json').read_text())
retrieval=json.loads((D/'retrieval.json').read_text())
def fetch(operation,file,variables=None,market='US'):
 sample=next(r['url'] for r in captured if 'operationName='+operation+'&' in r['url'])
 parsed=urllib.parse.urlparse(sample);args=urllib.parse.parse_qs(parsed.query)
 if variables is not None:args['variables']=[json.dumps(variables,separators=(',',':'))]
 url=urllib.parse.urlunparse(parsed._replace(path=parsed.path.replace('/prod_bk_ca/','/prod_bk_'+market.lower()+'/'),query=urllib.parse.urlencode({k:v[0] for k,v in args.items()})))
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=35) as r:body=r.read();status=r.status
 (D/file).write_bytes(body)
 retrieval.append({'file':file,'url':url,'finalUrl':url,'retrievedAt':datetime.now(timezone.utc).isoformat(),'status':status,'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body),'marketScope':market,'captureMethod':'official public app CMS query; explicit country dataset'})
 (D/'retrieval.json').write_text(json.dumps(retrieval,ensure_ascii=False,indent=2)+'\n')
 data=json.loads(body)
 if data.get('errors'):raise ValueError(data['errors'])
 print(file,len(body),flush=True)
 return data
for market in ('CA','US'):
 routes=fetch('GetStaticPageRoutes','bk-'+market.lower()+'-routes.json',market=market)
 row=next(r for r in routes['data']['allStaticPages'] if r.get('path',{}).get('current')=='nutrition-explorer')
 print(market,'nutrition route',row['_id'],row['title'],flush=True)
 nutrition=fetch('staticNutritionPage','bk-'+market.lower()+'-nutrition.json',{'id':row['_id']},market)
 print(market,'page',nutrition['data']['StaticPage']['title'])
