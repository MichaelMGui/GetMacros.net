"""Capture public official restaurant source pages without credentials."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys,urllib.request
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs/global-coverage-2026-10-17/restaurants/supplement'
D.mkdir(parents=True,exist_ok=True)
urls={
 'mcd-ca-menu.html':'https://www.mcdonalds.com/ca/en-ca/full-menu.html',
 'mcd-ca-calculator.html':'https://www.mcdonalds.com/ca/en-ca/about-our-food/nutrition-calculator.html',
 'bk-us-help.html':'https://help.bk.com/hc/en-us/articles/36913083446935-Where-can-I-view-the-nutrition-and-allergen-information-for-Burger-King-menu-items',
 'bk-us-explorer.html':'https://www.bk.com/nutrition-explorer',
}
if __name__=='__main__':
 if len(sys.argv)>2:urls={sys.argv[1]:sys.argv[2]}
 old=json.loads((D/'retrieval.json').read_text(encoding='utf-8')) if (D/'retrieval.json').exists() else []
 for file,url in urls.items():
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=35) as r:
    body=r.read();final=r.url;status=r.status;mime=r.headers.get('Content-Type')
   (D/file).write_bytes(body)
   evidence={'file':file,'url':url,'finalUrl':final,'retrievedAt':datetime.now(timezone.utc).isoformat(),'status':status,'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body),'contentType':mime}
  except Exception as e:evidence={'file':file,'url':url,'retrievedAt':datetime.now(timezone.utc).isoformat(),'error':str(e)}
  old=[x for x in old if x['file']!=file]+[evidence]
  (D/'retrieval.json').write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  print(json.dumps(evidence,ensure_ascii=False),flush=True)
