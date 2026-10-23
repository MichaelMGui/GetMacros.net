"""Stage the visitor/click repair in the guarded publisher; never touch root Git."""
from pathlib import Path
import importlib.util
import json
import re
import shutil

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/analytics-2026-10-23'
spec=importlib.util.spec_from_file_location('guard',ROOT/'tools/global_coverage_2026_10_17/prepare_publication.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
BASE='11cfe9985f7f203785f69a29ebf0dd1998978428'


def main():
    p.require(p.git('rev-parse','HEAD')==BASE,'Publisher revision changed')
    p.require(p.git('remote','get-url','origin')==p.EXPECTED_ORIGIN,'Publisher origin changed')
    p.require(not p.git('diff','--name-only') and not p.git('diff','--cached','--name-only'),'Preserve publisher edits')
    p.require(set(p.git('ls-files','--others','--exclude-standard','-z',nul=True))==p.PROTECTED_UNTRACKED,'Unexpected inherited files')
    protected={n:p.sha(p.DEST/n) for n in sorted(p.PROTECTED_UNTRACKED)}
    prior=json.loads((OUT/'publication-preparation.json').read_text(encoding='utf-8'))
    p.require(protected==prior['protectedInheritedUntracked'],'Inherited file hashes changed')
    p.require('PASS: repeat integration' in (OUT/'recovery-repeat-build.log').read_text(encoding='utf-8'),'Repeat integration incomplete')
    tests=json.loads((OUT/'recovery-checks.json').read_text(encoding='utf-8'))
    p.require(len(tests)==7 and all(r['exitCode']==0 for r in tests),'Final checks incomplete')
    for name in ['js/order-registry.json','data/restaurant-presence.json','data/food-library/manifest.json','data/food-library/index.json']:
        p.require(p.sha(ROOT/name)==p.sha(p.DEST/name),'Unexpected data change '+name)
    names={'js/analytics.js','assets/generated/manifest.json','sw.js','docs/analytics-2026-10-23/README.md',
        'docs/analytics-2026-10-23/route-scope.json','docs/analytics-2026-10-23/recovery-checks.json'}
    names.update('tools/analytics_measurement/'+n for n in ['build.py','runtime.test.cjs','test_build.py','browser.cjs','production.cjs','prepare_recovery.py'])
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
    old=json.loads(p.git('show','HEAD:assets/generated/manifest.json'))
    stale={v['url'].lstrip('/') for v in old.values()}-{v['url'].lstrip('/') for v in manifest.values()}
    removed=[]
    for name in sorted(stale):
        p.require(re.fullmatch(r'assets/generated/[A-Za-z0-9._-]+-[a-f0-9]{12}\.(css|js|json)',name) is not None,'Unexpected generated filename')
        target=p.target_path(name)
        if target.exists():target.unlink();removed.append(name)
    changes=copied+removed
    for i in range(0,len(changes),50):p.git('add','--',*changes[i:i+50])
    p.require(set(p.git('diff','--cached','--name-only','--no-renames','-z',nul=True))==set(changes),'Unexpected staged files')
    p.require(all(p.sha(p.DEST/n)==h for n,h in protected.items()),'Inherited files changed')
    (OUT/'recovery-publication.json').write_text(json.dumps({'base':BASE,'copied':copied,'removed':removed,
        'protectedInheritedUntracked':protected,'rootGitModified':False},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'copied':len(copied),'removed':removed,'staged':True}))


if __name__=='__main__':main()
