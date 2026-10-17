"""Retrieve explicitly reviewed official public restaurant sources; no private APIs."""
from pathlib import Path
import os, json, hashlib, urllib.request, concurrent.futures
os.environ.pop('SSLKEYLOGFILE', None)
ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'docs/global-coverage-2026-10-17/restaurants'
DEST.mkdir(parents=True,exist_ok=True)
URLS={
 'mos-jp.pdf':'https://www.mos.jp/menu/pdf/nutrition.pdf',
 'mos-jp-index.html':'https://www.mos.jp/omoi/quality/product_info/',
 'kfc-uki.pdf':'https://brand-uk.assets.kfc.co.uk/nutrition-allergens.pdf',
 'kfc-uki-index.html':'https://www.kfc.co.uk/nutrition-allergens',
 'kfc-ca.pdf':'https://assets.ctfassets.net/a2mgcrjjefyo/3AUi2N7aacNo4rjQ1jE3di/ab5513730957082e372dd36fd0a7c950/KFC_Nutritional_Information__W8__EN_FR.pdf',
 'kfc-ca-index.html':'https://www.kfc.ca/nutrition-and-allergy-info',
 'kfc-nz-index.html':'https://help.kfc.co.nz/hc/en-us/articles/360028815991-Allergens-Nutrition',
 'kfc-au-index.html':'https://www.kfc.com.au/nutrition-allergen',
 'panda-us.html':'https://www.pandaexpress.com/nutritioninformation',
 'subway-mx-index.html':'https://www.subway.com/es-mx/menunutrition/nutrition',
 'supermacs-ie.pdf':'https://supermacs.ie/wp-content/uploads/2024/06/Nutritional-SUPERMACS-PAPA-JOHNS-Rev005.pdf',
}
EXTRA_URLS={
 'kfc-mx-index.html':'https://kfc.com.mx/tabla-nutricional',
 'kfc-nz-menu.html':'https://kfc.co.nz/nutrition',
 'subway-nz-2026.pdf':'https://media.subway.com/dam/urn:aaid:aem:0e28bcc2-9385-4a0d-b54f-3a177e7dd86d/original/as/NZ%20Nutritional%20Web%20Guide%20May%202026.pdf',
}
def get(item):
 name,url=item
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; GetMacros source review)'})
  with urllib.request.urlopen(req,timeout=40) as response:
   data=response.read(); final=response.url; content=response.headers.get('Content-Type')
  (DEST/name).write_bytes(data)
  return {'file':name,'url':url,'finalUrl':final,'retrievedAt':'2026-10-17','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'contentType':content,'retrievalIsVerification':False}
 except Exception as exc:return {'file':name,'url':url,'retrievedAt':'2026-10-17','error':str(exc)}
if __name__=='__main__':
 import sys
 extra='--extra' in sys.argv
 if '--images' in sys.argv:
  import re,urllib.parse
  source=(DEST/'kfc-mx-index.html').read_text(encoding='utf-8')
  EXTRA_URLS={f'kfc-mx-{i:02d}.jpg':urllib.parse.quote(url,safe=':/%') for i,url in enumerate(re.findall(r'<img src="(https://cdn.tictuk.com/[^"<>]*Nutrimentales[^"<>]+)"',source),1)}
  extra=True
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: rows=list(pool.map(get,(EXTRA_URLS if extra else URLS).items()))
 if extra:rows=json.loads((DEST/'retrieval.json').read_text(encoding='utf-8'))+rows
 (DEST/'retrieval.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
 print(json.dumps([{k:v for k,v in r.items() if k in ('file','bytes','error')} for r in rows],indent=2))
