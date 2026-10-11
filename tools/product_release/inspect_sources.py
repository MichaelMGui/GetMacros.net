from pathlib import Path
import json, zipfile, re
import pdfplumber
ROOT=Path(__file__).resolve().parents[2]
DIR=ROOT/'docs/global-product-release-2026-10-11/sources'
for name in ['foundation','sr-legacy','survey']:
    with zipfile.ZipFile(DIR/(name+'.zip')) as archive:
        entry=next(x for x in archive.namelist() if x.endswith('.json'))
        data=json.loads(archive.read(entry))
    key=next(k for k in data if isinstance(data[k],list))
    foods=data[key]
    print(name, key, len(foods), 'sample',json.dumps(foods[0],ensure_ascii=False)[:5200])
for name in ['greggs','gyg']:
    with pdfplumber.open(DIR/(name+'.pdf')) as document:
        print(name,'pages',len(document.pages))
        for i in ([0] if name=='greggs' else [0,1,2]):
            p=document.pages[i]
            print('PAGE',i+1,p.extract_text()[:4400])
            print('TABLE',str(p.extract_tables())[:800])
            try:p.to_image(resolution=120).save(DIR/(name+'-'+str(i+1)+'.png'))
            except Exception as error:print('Render error',error)
bad=[]
for p in ROOT.rglob('*.html'):
    if p.relative_to(ROOT).as_posix().startswith(('design/','docs/','tools/')):continue
    if 'name="description"' not in p.read_text(encoding='utf-8'):bad.append(p.relative_to(ROOT).as_posix())
print('Pages without descriptions',bad)
