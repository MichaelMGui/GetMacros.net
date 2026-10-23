"""Publish only consent/measurement integration, preserving inherited publisher work."""
from pathlib import Path
import argparse
import importlib.util
import json
import re
import shutil

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/analytics-2026-10-23'
spec=importlib.util.spec_from_file_location('publication_guard',ROOT/'tools/global_coverage_2026_10_17/prepare_publication.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
BASE='b5344df1ab554566089acfcd91b204b48579f87c'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stage',action='store_true');args=parser.parse_args()
    p.require(p.git('rev-parse','HEAD')==BASE,'Publisher revision changed')
    p.require(p.git('remote','get-url','origin')==p.EXPECTED_ORIGIN,'Publisher origin changed')
    p.require(not p.git('diff','--name-only') and not p.git('diff','--cached','--name-only'),'Preserve publisher edits')
    p.require(set(p.git('ls-files','--others','--exclude-standard','-z',nul=True))==p.PROTECTED_UNTRACKED,'Unexpected inherited files')
    protected={n:p.sha(p.DEST/n) for n in sorted(p.PROTECTED_UNTRACKED)}
    prior=json.loads((ROOT/'docs/search-recovery-2026-10-21/ci-followup-preparation.json').read_text(encoding='utf-8'))
    p.require(protected==prior['protectedInheritedUntracked'],'Inherited file hashes changed')
    p.require('PASS: repeat integration' in (OUT/'repeat-build.log').read_text(encoding='utf-8'),'Repeat integration incomplete')
    browser=json.loads((OUT/'browser.json').read_text(encoding='utf-8'))
    p.require(not browser['errors'] and any(r['status']==204 for r in browser['collectorResponses']),'Browser/collector verification incomplete')
    names={'js/analytics.js','css/analytics-consent.css','tools/build_ultimate_release.py','tools/build_site.sh',
        'tools/run_food_build.py','tools/product_release/test-generators.py','tools/test_publication.py','.github/workflows/site-quality.yml',
        'docs/monetization/journey-readiness.md','sw.js','assets/generated/manifest.json'}
    names.update(f.relative_to(ROOT).as_posix() for f in ROOT.glob('*.html'))
    names.update(f.relative_to(ROOT).as_posix() for f in ROOT.glob('*/en/**/index.html'))
    names.update(f.relative_to(ROOT).as_posix() for f in (ROOT/'tools/analytics_measurement').iterdir() if f.is_file() and f.suffix in ('.py','.cjs'))
    names.update('docs/analytics-2026-10-23/'+n for n in ['README.md','route-scope.json','browser.json',*browser['screenshots']])
    manifest=json.loads((ROOT/'assets/generated/manifest.json').read_text(encoding='utf-8'))
    names.update(v['url'].lstrip('/') for v in manifest.values())
    copied=[]
    for name in sorted(names):
        source=p.source_path(name);target=p.target_path(name)
        p.require(source.is_file() and source.stat().st_size<p.MAX_FILE_BYTES,'Missing/oversized source '+name)
        if target.exists() and p.sha(source)==p.sha(target): continue
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        p.require(p.sha(source)==p.sha(target),'Copy differs '+name);copied.append(name)
    old=json.loads(p.git('show','HEAD:assets/generated/manifest.json'))
    stale={v['url'].lstrip('/') for v in old.values()}-{v['url'].lstrip('/') for v in manifest.values()}
    pruned=[]
    for name in sorted(stale):
        p.require(re.fullmatch(r'assets/generated/[A-Za-z0-9._-]+-[a-f0-9]{12}\.(css|js|json)',name) is not None,'Unexpected generated filename')
        target=p.target_path(name)
        if target.exists():target.unlink();pruned.append(name)
    if args.stage:
        changes=copied+pruned
        for i in range(0,len(changes),50):p.git('add','--',*changes[i:i+50])
        p.require(set(p.git('diff','--cached','--name-only','--no-renames','-z',nul=True))==set(changes),'Unexpected staged files')
    p.require(all(p.sha(p.DEST/n)==h for n,h in protected.items()),'Inherited files changed')
    (OUT/'publication-preparation.json').write_text(json.dumps({'base':BASE,'copied':copied,'pruned':pruned,
        'protectedInheritedUntracked':protected,'rootGitModified':False,'staged':args.stage},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'copied':len(copied),'pruned':len(pruned),'staged':args.stage}))


if __name__=='__main__':main()
