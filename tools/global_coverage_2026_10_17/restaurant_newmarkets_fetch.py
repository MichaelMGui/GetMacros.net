"""Public local official sources for proposed additional countries; separate batch."""
from pathlib import Path
import os,json,hashlib,urllib.request,concurrent.futures
os.environ.pop('SSLKEYLOGFILE',None)
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs/global-coverage-2026-10-17/restaurants/newmarkets'
D.mkdir(parents=True,exist_ok=True)
URLS={
 'quick-fr.pdf':'https://assets.quick.fr/Declaration_Nutritionnelle_au_09_JUIN_26_ec88e7a66b.pdf',
 'quick-fr-index.html':'https://www.quick.fr/',
 'mcd-in-ne.pdf':'https://mcdindia.com/wp-content/uploads/2025/12/product-nutritional-information-bookletpdf.pdf',
 'mcd-in-ne-index.html':'https://mcdindia.com/nutritional-information/',
 'mcd-in-ne-about.html':'https://mcdindia.com/about-us/',
 'steers-za-index.html':'https://steers.co.za/nutritional-guide/',
 'bk-sg-index.html':'https://burgerking.com.sg/',
 'mcd-sg-index.html':'https://www.mcdonalds.com.sg/nutrition-calculator',
 'mcd-ae.pdf':'https://www.mcdonalds.com/content/dam/sites/ArabiaGWS/english/Feature-Callout/Desktop/AllergensGuide.pdf',
}
def get(item):
 file,url=item
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(req,timeout=35) as r:data=r.read();final=r.url
  (D/file).write_bytes(data)
  return {'file':file,'url':url,'finalUrl':final,'retrievedAt':'2026-10-17','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'retrievalIsVerification':False}
 except Exception as exc:return {'file':file,'url':url,'error':str(exc)}
if __name__=='__main__':
 import sys
 if '--extra' in sys.argv:
  URLS={
   'quick-fr-current.pdf':'https://assets.quick.fr/Declaration_Nutritionnelle_des_produits_Quick_valable_a_partir_du_6_octobre_2026_a98adac17b.pdf',
   'bk-sg-menu.html':'https://burgerking.com.sg/Menu',
   'mcd-sg-calculator.js':'https://www.mcdonalds.com.sg/modules/custom/mcdonalds_nutrition_calculator/js/mcdonalds_nutrition_calculator.js?v=1',
  }
 if '--sg' in sys.argv:
  URLS={
   'bk-sg-category1.html':'https://burgerking.com.sg/Menu/Category/1',
   'mcd-sg-full-menu.html':'https://www.mcdonalds.com.sg/full-menu',
   'debonairs-za-index.html':'https://debonairspizza.co.za/nutritional-and-allergen-guide/',
  }
 if '--sgcategories' in sys.argv:URLS={f'bk-sg-category{i}.html':f'https://burgerking.com.sg/Menu/Category/{i}' for i in (2,3,4,5,7,8,9,11)}
 if '--sgverify' in sys.argv:URLS={'bk-sg-item2.html':'https://burgerking.com.sg/Menu/Item/2','bk-sg-category4.html':'https://burgerking.com.sg/Menu/Category/4','bk-sg-main.js':'https://burgerking.com.sg/Content/js/main.js'}
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:rows=list(pool.map(get,URLS.items()))
 if any(x in sys.argv for x in ('--extra','--sg','--sgcategories','--sgverify')):rows=json.loads((D/'retrieval.json').read_text(encoding='utf-8'))+rows
 (D/'retrieval.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
 print(json.dumps([{k:v for k,v in r.items() if k in ('file','bytes','error')} for r in rows],indent=2))
