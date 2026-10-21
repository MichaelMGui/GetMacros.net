"""Publish only reviewed landing-page fixes through the established checkout."""
from pathlib import Path
import argparse,importlib.util,json,re,shutil
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/search-recovery-2026-10-21'
spec=importlib.util.spec_from_file_location('guard',ROOT/'tools/global_coverage_2026_10_17/prepare_publication.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
BASE='59c53a746c0b063c81a5cc0bfd47cd655feb8678'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stage',action='store_true');args=parser.parse_args()
    p.require(p.git('rev-parse','HEAD')==BASE,'Publisher HEAD changed')
    p.require(p.git('remote','get-url','origin')==p.EXPECTED_ORIGIN,'Origin changed')
    p.require(not p.git('diff','--name-only') and not p.git('diff','--cached','--name-only'),'Preserve publisher edits')
    p.require(set(p.git('ls-files','--others','--exclude-standard','-z',nul=True))==p.PROTECTED_UNTRACKED,'Unexpected inherited work')
    protected={n:p.sha(p.DEST/n) for n in sorted(p.PROTECTED_UNTRACKED)}
    prior=json.loads((ROOT/'docs/brand-assets-2026-10-21/publication-preparation.json').read_text())
    p.require(protected==prior['protectedInheritedUntracked'],'Inherited file hashes changed')
    names={'.github/workflows/site-quality.yml','tools/validate_site.py','tools/test_asset_stamps.py','tools/run_food_build.py','tools/build_site.sh','sitemap.xml','sw.js','assets/generated/manifest.json'}
    names.update(f.relative_to(ROOT).as_posix() for f in ROOT.glob('*.html'))
    names.update(f.relative_to(ROOT).as_posix() for f in ROOT.glob('*/en/**/index.html'))
    names.update(f.relative_to(ROOT).as_posix() for f in (ROOT/'tools/search_recovery').iterdir() if f.is_file() and f.suffix in ('.py','.cjs','.json','.txt'))
    names.update('docs/search-recovery-2026-10-21/'+n for n in ['implementation.json','README.txt','legacy-redirects.json','browser.json'])
    names.update(f.relative_to(ROOT).as_posix() for folder in ['before','after'] for f in (OUT/folder).glob('*.png'))
    manifest=json.loads((ROOT/'assets/generated/manifest.json').read_text());names.update(v['url'].lstrip('/') for v in manifest.values())
    copied=[]
    for name in sorted(names):
        source=p.source_path(name);target=p.target_path(name);p.require(source.is_file() and source.stat().st_size<p.MAX_FILE_BYTES,'Source missing/oversized '+name)
        if target.exists() and p.sha(source)==p.sha(target):continue
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);p.require(p.sha(source)==p.sha(target),'Copy differs '+name);copied.append(name)
    old=json.loads(p.git('show','HEAD:assets/generated/manifest.json'));stale={v['url'].lstrip('/') for v in old.values()}-{v['url'].lstrip('/') for v in manifest.values()};pruned=[]
    for name in sorted(stale):
        p.require(re.fullmatch(r'assets/generated/[A-Za-z0-9._-]+-[a-f0-9]{12}\.(css|js|json)',name) is not None,'Unexpected immutable asset')
        target=p.target_path(name)
        if target.exists():target.unlink();pruned.append(name)
    if args.stage:
        changes=copied+pruned
        for i in range(0,len(changes),50):p.git('add','--',*changes[i:i+50])
        actual=set(p.git('diff','--cached','--name-only','--no-renames','-z',nul=True));p.require(actual==set(changes),'Unexpected staged paths')
    p.require(all(p.sha(p.DEST/n)==h for n,h in protected.items()),'Protected files changed')
    report={'base':BASE,'copied':copied,'pruned':pruned,'protectedInheritedUntracked':protected,'rootGitModified':False,'staged':args.stage}
    (OUT/'publication-preparation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'copied':len(copied),'pruned':len(pruned),'staged':args.stage}))

if __name__=='__main__':main()
