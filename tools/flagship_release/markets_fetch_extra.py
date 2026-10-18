"""Capture only public official menu sources linked in reviewed local pages."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.request,urllib.parse,json,hashlib,re
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/flagship-release-2026-10-18/markets'

def run():
    from lxml import html
    index=html.fromstring((DOC/'sources/hjs-au-index.html').read_bytes())
    urls={}
    for a in index.xpath('//a[@href]'):
        link=a.attrib['href']
        if link.endswith('.pdf') and 'Allergen' not in link and ('Nutritionals' in link or 'Nutritional-Values' in link):
            urls['hjs-au-'+str(len(urls)+1).zfill(2)+'.pdf']='https://www.hungryjacks.com.au'+link
    urls.update({'bk-nz.pdf':'https://bknzpublic.z8.web.core.windows.net/nutritionalguide/nutritionalguide.pdf',
      'bk-nz.js':'https://www.burgerking.co.nz/assets/index.js',
      'kfc-jp-index.html':'https://www.kfc.co.jp/food/allergy.html',
      'burgerking-jp-index.html':'https://www.burgerking.co.jp/#/allergen',
      'subway-uki-index.html':'https://www.subway.com/en-GB/MenuNutrition/Nutrition',
      'dominos-in-site.html':'https://www.dominos.co.in/menu/nutritional-information',
      'tacobell-in-index.html':'https://www.tacobell.co.in/nutrition',
      'mcd-ie-index.html':'https://www.mcdonalds.com/ie/en-ie/food/nutrition-calculator.html',
      'dominos-au-nutrition.html':'https://www.dominos.com.au/menu/nutritional-information',
      'dominos-nz-nutrition.html':'https://www.dominos.co.nz/menu/nutritional-information',
      'kfc-za-nutrition.html':'https://www.kfc.co.za/nutrition',
      'nandos-za-nutrition.html':'https://www.nandos.co.za/eat/nutrition',
      'mcd-mx-nutrition.html':'https://www.mcdonalds.com.mx/nutricional',
      'starbucks-mx-nutrition.html':'https://www.starbucks.com.mx/menu/informacion-nutricional'})
    def one(item):
        f,u=item
        try:
            with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0','Accept-Encoding':'identity'}),timeout=35) as r:data=r.read();final=r.url
            (DOC/'sources'/f).write_bytes(data)
            return {'file':(DOC/'sources'/f).relative_to(ROOT).as_posix(),'url':u,'finalUrl':final,'retrievedAt':'2026-10-18','sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'retrievalIsVerification':False}
        except Exception as e:return {'file':f,'url':u,'retrievedAt':'2026-10-18','error':str(e)}
    with ThreadPoolExecutor(max_workers=8) as p:result=list(p.map(one,urls.items()))
    old=json.loads((DOC/'retrieval.json').read_text(encoding='utf-8'))
    old=[r for r in old if r['url'] not in urls.values()]+result
    (DOC/'retrieval.json').write_text(json.dumps(old,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([{k:v for k,v in r.items() if k in ('file','bytes','error')} for r in result],indent=2))
if __name__=='__main__':run()
