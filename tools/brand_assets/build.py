"""Generate one small, reviewed logo registry. Never infer meal-photo permission."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[2]
def main():
    review=json.loads((ROOT/'docs/brand-assets-2026-10-21/logo-source-review.json').read_text())
    records=[r for r in review['records'] if r.get('localPath')]
    # The downloaded Popeyes file is its superseded pre-2020 wordmark.
    records=[r for r in records if r['id']!='popeyes']
    aliases={'mcdonalds':['McDonald’s','McDonald’s Japan','McDonald’s North & East India'], 'dominos':['Domino’s',"Domino's"], 'dunkin':['Dunkin’',"Dunkin'"], 'chick-fil-a':['Chick-fil-A']}
    logo={r['id']:{'name':r['name'],'src':r['localPath'],'sourcePage':r['sourcePage'],'aliases':aliases.get(r['id'],[r['name']]),'width':r['width'],'height':r['height']} for r in records}
    (ROOT/'images/restaurant-logos/manifest.json').write_text(json.dumps({'checked':'2026-10-21','notice':'Trademarks identify independent restaurants. GetMacros is not affiliated with or endorsed by these brands.','logos':logo},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    js="/* Reviewed public-domain text/geometry marks; trademarks remain with their owners. */\n(function(root){'use strict';const logos="+json.dumps(logo,ensure_ascii=False,separators=(',',':'))+";\nconst key=s=>String(s||'').normalize('NFKD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]/g,'');const names=new Map();Object.values(logos).forEach(l=>l.aliases.forEach(n=>names.set(key(n),l)));const esc=s=>String(s).replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'}[c]));function get(name){return names.get(key(name))||null;}function mark(name){const l=get(name);return l?'<span class=\"brand-logo\" aria-hidden=\"true\"><img src=\"'+esc(l.src)+'\" width=\"48\" height=\"40\" alt=\"\" loading=\"lazy\" decoding=\"async\"></span>':'';}root.GetMacrosBrands={get,mark};})(typeof window==='undefined'?globalThis:window);\n"
    (ROOT/'js/restaurant-brands.js').write_text(js,encoding='utf-8')
    chains=sorted({r['chain'] for r in json.loads((ROOT/'js/order-registry.json').read_text())['records']}|{r['restaurantBrand'] for r in json.loads((ROOT/'data/restaurant-presence.json').read_text())['relationships']})
    def key(s):return re.sub('[^a-z0-9]','',s.lower().replace('’',"'"))
    covered={key(n) for l in logo.values() for n in l['aliases']}
    inventory=[{'chain':n,'status':'logo-integrated' if key(n) in covered else 'typographic-fallback','blocker':None if key(n) in covered else 'No asset approved in this limited review; further brand-specific source and rights review required. This is not a finding that every use is prohibited.'} for n in chains]
    (ROOT/'docs/brand-assets-2026-10-21/coverage.json').write_text(json.dumps({'logos':len(logo),'catalogAndDirectoryBrands':len(chains),'records':inventory},indent=2)+'\n')
    print('Reviewed logo assets:',len(logo),'Catalog brands:',len(chains))
if __name__=='__main__':main()
