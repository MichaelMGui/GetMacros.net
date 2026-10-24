"""Stage only reviewed article utility changes in the established publisher."""
from pathlib import Path
import importlib.util,json,shutil

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/article-utility-2026-10-24'
spec=importlib.util.spec_from_file_location('guard',ROOT/'tools/global_coverage_2026_10_17/prepare_publication.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
BASE='8844900612ec56ee62071d0f72a1c4325e17423f'

def main():
    p.require(p.git('rev-parse','HEAD')==BASE,'Publisher revision changed')
    p.require(p.git('remote','get-url','origin')==p.EXPECTED_ORIGIN,'Publisher origin changed')
    p.require(not p.git('diff','--name-only') and not p.git('diff','--cached','--name-only'),'Preserve publisher edits')
    p.require(set(p.git('ls-files','--others','--exclude-standard','-z',nul=True))==p.PROTECTED_UNTRACKED,'Unexpected inherited work')
    protected={n:p.sha(p.DEST/n) for n in sorted(p.PROTECTED_UNTRACKED)}
    prior=json.loads((ROOT/'docs/search-discovery-2026-10-23/publication.json').read_text(encoding='utf-8'))
    p.require(protected==prior['protectedInheritedUntracked'],'Inherited file hashes changed')
    checks=json.loads((OUT/'checks-final.json').read_text(encoding='utf-8'))
    p.require(len(checks)>=12 and all(r['exitCode']==0 for r in checks),'Final checks incomplete')
    for name in ['js/order-registry.json','data/restaurant-presence.json','data/food-library/manifest.json','js/analytics.js']:
        p.require(p.sha(ROOT/name)==p.sha(p.DEST/name),'Unexpected data/analytics change '+name)
    names={'.github/workflows/site-quality.yml','tools/test_publication.py','tools/search_recovery/build.py',
        'tools/search_recovery/article_tools.py','tools/search_recovery/test_article_tools.py',
        'tools/search_recovery/test_article_tools.cjs','tools/search_recovery/prepare_article_utility.py',
        'js/article-tools.js','css/article-tools.css','sitemap.xml','assets/generated/manifest.json','sw.js',
        'docs/article-utility-2026-10-24/README.md','docs/article-utility-2026-10-24/implementation.json',
        'docs/article-utility-2026-10-24/checks-final.json','search.html'}
    plans=[OUT/'implementation.json',ROOT/'docs/search-discovery-2026-10-23/implementation.json']
    for path in plans:
        for route in json.loads(path.read_text(encoding='utf-8'))['routes']:
            names.add('index.html' if route=='/' else route.lstrip('/')+('index.html' if route.endswith('/') else ''))
    manifest=json.loads((ROOT/'assets/generated/manifest.json').read_text(encoding='utf-8'))
    names.update(v['url'].lstrip('/') for v in manifest.values())
    old=json.loads(p.git('show','HEAD:assets/generated/manifest.json'))
    p.require(set(manifest)==set(old)|{'js/article-tools.js','css/article-tools.css'},'Unexpected asset sources')
    p.require(all(manifest[k]==v for k,v in old.items()),'Unrelated asset change')
    copied=[]
    for name in sorted(names):
        source=p.source_path(name);target=p.target_path(name)
        p.require(source.is_file() and source.stat().st_size<p.MAX_FILE_BYTES,'Missing/oversized source '+name)
        if target.exists() and p.sha(source)==p.sha(target):continue
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        p.require(p.sha(source)==p.sha(target),'Copy differs '+name);copied.append(name)
    for i in range(0,len(copied),50):p.git('add','--',*copied[i:i+50])
    p.require(set(p.git('diff','--cached','--name-only','--no-renames','-z',nul=True))==set(copied),'Unexpected staged paths')
    p.require(all(p.sha(p.DEST/n)==h for n,h in protected.items()),'Inherited files changed')
    (OUT/'publication.json').write_text(json.dumps({'base':BASE,'copied':copied,'protectedInheritedUntracked':protected,'rootGitModified':False},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'copied':len(copied),'staged':True}))

if __name__=='__main__':main()
