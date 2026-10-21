"""Scoped asset/copy release through the established protected publisher checkout."""
from pathlib import Path
import importlib.util,json,shutil,re,argparse
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/brand-assets-2026-10-21'
spec=importlib.util.spec_from_file_location('guard',ROOT/'tools/global_coverage_2026_10_17/prepare_publication.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
BASE='8da2c6f8b434fcfc4dabbf0887d9c749fd429346'
SOURCES={'.github/workflows/site-quality.yml','tools/build_ultimate_release.py','tools/build_global_coverage_release.py','tools/botanical_release/layout.py','tools/home-workspace.css','tools/food-design.css','tools/release-product.css','css/publication.css','css/home-workspace.css','js/meal-guide.js','js/meal-images.js','js/meal-view.js','js/restaurant-brands.js','js/unified-v7.js','sitemap.xml','sw.js'}
def main():
    a=argparse.ArgumentParser();a.add_argument('--stage',action='store_true');args=a.parse_args()
    p.require(p.git('rev-parse','HEAD')==BASE,'Publisher changed')
    p.require(p.git('remote','get-url','origin')==p.EXPECTED_ORIGIN,'Origin changed')
    p.require(not p.git('diff','--name-only') and not p.git('diff','--cached','--name-only'),'Preserve publisher edits')
    p.require(set(p.git('ls-files','--others','--exclude-standard','-z',nul=True))==p.PROTECTED_UNTRACKED,'Unexpected untracked work')
    protected={n:p.sha(p.DEST/n) for n in sorted(p.PROTECTED_UNTRACKED)}
    previous=json.loads((ROOT/'docs/diary-reference-2026-10-20/publication-preparation.json').read_text())
    p.require(protected==previous['protectedInheritedUntracked'],'Inherited files changed')
    paths=set(SOURCES);paths.update(f.relative_to(ROOT).as_posix() for f in ROOT.glob('*.html'));paths.update(f.relative_to(ROOT).as_posix() for f in ROOT.glob('*/en/**/index.html'))
    paths.update('js/'+name+'-meals.js' for name in ['us','canada','mx','gb','ie','au','nz','jp','fr','in','sg','za'])
    paths.update(f.relative_to(ROOT).as_posix() for f in (ROOT/'tools/brand_assets').iterdir() if f.suffix in {'.py','.cjs'})
    paths.update(f.relative_to(ROOT).as_posix() for f in OUT.iterdir() if f.suffix in {'.json','.txt'} and not f.name.startswith('publication-'))
    paths.update('images/restaurant-logos/'+f for f in ['manifest.json']+[Path(r['src']).name for r in json.loads((ROOT/'images/restaurant-logos/manifest.json').read_text())['logos'].values()])
    for folder,names in {'before':['home-390','home-1440'],'after':['home-light-390','home-light-1440','home-dark-390','quiz-390','quiz-1440','logo-contact-sheet','official-item-detail-390']}.items():
        for name in names:
            f=OUT/folder/(name+'.png')
            if f.exists():paths.add(f.relative_to(ROOT).as_posix())
    manifest=json.loads((ROOT/'assets/generated/manifest.json').read_text());paths.add('assets/generated/manifest.json');paths.update(v['url'].lstrip('/') for v in manifest.values())
    copied=[]
    for name in sorted(paths):
        source=p.source_path(name);target=p.target_path(name);p.require(source.is_file() and source.stat().st_size<p.MAX_FILE_BYTES,'Missing/oversized source '+name)
        if target.exists() and p.sha(source)==p.sha(target):continue
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);p.require(p.sha(source)==p.sha(target),'Copy mismatch '+name);copied.append(name)
    old=json.loads(p.git('show','HEAD:assets/generated/manifest.json'));stale={v['url'].lstrip('/') for v in old.values()}-{v['url'].lstrip('/') for v in manifest.values()};pruned=[]
    for name in sorted(stale):
        p.require(re.fullmatch(r'assets/generated/[A-Za-z0-9._-]+-[a-f0-9]{12}\.(css|js|json)',name) is not None,'Unexpected asset path');target=p.target_path(name)
        if target.exists():target.unlink();pruned.append(name)
    report={'base':BASE,'protectedInheritedUntracked':protected,'copied':copied,'pruned':pruned,'rootGitModified':False,'staged':False}
    if args.stage:
        names=copied+pruned
        for i in range(0,len(names),50):p.git('add','--',*names[i:i+50])
        actual=set(p.git('diff','--cached','--name-only','--no-renames','-z',nul=True));p.require(actual==set(names) and not actual&p.PROTECTED_UNTRACKED,'Unexpected staged files');report['staged']=True
    p.require(all(p.sha(p.DEST/n)==v for n,v in protected.items()),'Inherited files changed')
    (OUT/'publication-preparation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'copied':len(copied),'pruned':len(pruned),'staged':report['staged'],'rootGitModified':False}))
if __name__=='__main__':main()
