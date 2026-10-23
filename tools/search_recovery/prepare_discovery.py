"""Stage only the reviewed discovery repair in the established publisher."""
from pathlib import Path
import importlib.util
import json
import re
import shutil

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/search-discovery-2026-10-23'
spec=importlib.util.spec_from_file_location('guard',ROOT/'tools/global_coverage_2026_10_17/prepare_publication.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
BASE='158cf453faba9825c15e1ca0c1042352a7862634'


def main():
    p.require(p.git('rev-parse','HEAD')==BASE,'Publisher revision changed')
    p.require(p.git('remote','get-url','origin')==p.EXPECTED_ORIGIN,'Publisher origin changed')
    p.require(not p.git('diff','--name-only') and not p.git('diff','--cached','--name-only'),'Preserve publisher edits')
    p.require(set(p.git('ls-files','--others','--exclude-standard','-z',nul=True))==p.PROTECTED_UNTRACKED,'Unexpected inherited work')
    protected={n:p.sha(p.DEST/n) for n in sorted(p.PROTECTED_UNTRACKED)}
    prior=json.loads((ROOT/'docs/analytics-2026-10-23/recovery-publication.json').read_text(encoding='utf-8'))
    p.require(protected==prior['protectedInheritedUntracked'],'Inherited file hashes changed')
    p.require('PASS: repeat integration' in (OUT/'repeat-build.log').read_text(encoding='utf-8'),'Repeat integration incomplete')
    checks=json.loads((OUT/'checks.json').read_text(encoding='utf-8'))
    p.require(len(checks)>=8 and all(c['exitCode']==0 for c in checks),'Final checks incomplete')
    for name in ['js/order-registry.json','data/restaurant-presence.json','data/food-library/manifest.json','data/food-library/index.json','js/analytics.js']:
        p.require(p.sha(ROOT/name)==p.sha(p.DEST/name),'Unexpected data/analytics change '+name)
    names={'.github/workflows/site-quality.yml','tools/search_recovery/build.py','tools/search_recovery/discovery.py',
        'tools/search_recovery/test_discovery.py','tools/search_recovery/prepare_discovery.py',
        'tools/search_recovery/discovery-production.cjs','docs/search-discovery-2026-10-23/README.md',
        'docs/search-discovery-2026-10-23/implementation.json','docs/search-discovery-2026-10-23/checks.json',
        'sitemap.xml','assets/generated/manifest.json','sw.js'}
    names.update(f.relative_to(ROOT).as_posix() for f in ROOT.glob('*.html'))
    names.update(f.relative_to(ROOT).as_posix() for f in ROOT.glob('*/en/**/index.html'))
    manifest=json.loads((ROOT/'assets/generated/manifest.json').read_text(encoding='utf-8'))
    names.update(v['url'].lstrip('/') for v in manifest.values())
    copied=[]
    for name in sorted(names):
        source=p.source_path(name);target=p.target_path(name)
        p.require(source.is_file() and source.stat().st_size<p.MAX_FILE_BYTES,'Missing/oversized source '+name)
        if target.exists() and p.sha(source)==p.sha(target):continue
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        p.require(p.sha(source)==p.sha(target),'Copy differs '+name);copied.append(name)
    # No script/style/data changes are expected. Guard against an accidental
    # unrelated immutable-asset removal instead of recursively synchronizing.
    old=json.loads(p.git('show','HEAD:assets/generated/manifest.json'))
    p.require({v['url'] for v in old.values()}=={v['url'] for v in manifest.values()},'Unexpected asset changes')
    for i in range(0,len(copied),50):p.git('add','--',*copied[i:i+50])
    p.require(set(p.git('diff','--cached','--name-only','--no-renames','-z',nul=True))==set(copied),'Unexpected staged paths')
    p.require(all(p.sha(p.DEST/n)==h for n,h in protected.items()),'Inherited files changed')
    (OUT/'publication.json').write_text(json.dumps({'base':BASE,'copied':copied,'protectedInheritedUntracked':protected,'rootGitModified':False},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'copied':len(copied),'staged':True}))


if __name__=='__main__':main()
