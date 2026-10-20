"""Scoped publication into the established checkout; never write root Git."""
from pathlib import Path
import importlib.util,json,shutil,re,argparse
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/botanical-release-2026-10-20'
spec=importlib.util.spec_from_file_location('guard',ROOT/'tools/global_coverage_2026_10_17/prepare_publication.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
BASE='34d86d33d2fb59de8a826c4b2dea3bbf159f32e8'
SOURCES={'tools/build_ultimate_release.py','tools/home-workspace.css','tools/food-design.css','tools/release-product.css','tools/release-library.css','tools/product-navigation.css','css/publication.css','css/home-workspace.css','css/release-library.css','css/food-app.css','js/meal-guide.js','js/unified-v7.js','js/food-app.js','sw.js','sitemap.xml','images/README.md'}

def selected():
    paths=set(SOURCES)
    paths.update(f.relative_to(ROOT).as_posix() for f in ROOT.glob('*.html'))
    paths.update(f.relative_to(ROOT).as_posix() for f in ROOT.glob('*/en/**/index.html'))
    paths.update(f.relative_to(ROOT).as_posix() for f in (ROOT/'tools/botanical_release').iterdir() if f.suffix in {'.py','.cjs','.json','.css'})
    manifest=json.loads((ROOT/'assets/generated/manifest.json').read_text(encoding='utf-8'))
    paths.add('assets/generated/manifest.json')
    paths.update(row['url'].lstrip('/') for row in manifest.values())
    for f in OUT.iterdir():
        if f.suffix in {'.json','.txt','.csv','.md'} and f.name not in {'publication-preparation.json','browser-before-zoom-fix.json','deployment-progress.json'}:paths.add(f.relative_to(ROOT).as_posix())
    for folder,names in {'before':['home-390','home-1440','food-diary-390','food-diary-1440','restaurant-quiz-390','calculators-1440','articles-1440'],'after':['home-light-390','home-light-1440','food-diary-light-390','food-diary-light-1440','quiz-selected-light-390','diary-search-light-390','diary-review-light-390','calculator-result-light-390','calculators-light-1440','articles-light-1440','home-dark-390','food-diary-dark-390','photo-fallback-390']}.items():
        for name in names:
            f=OUT/folder/(name+'.png')
            if f.exists():paths.add(f.relative_to(ROOT).as_posix())
    for theme in ['light','citrus','berry','dark']:
        f=OUT/'after'/('review-visible-action-'+theme+'-390.png')
        if f.exists():paths.add(f.relative_to(ROOT).as_posix())
    return paths

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stage',action='store_true');args=parser.parse_args()
    p.require(Path(p.git('rev-parse','--show-toplevel')).resolve()==p.DEST.resolve(),'Wrong publisher checkout')
    p.require(p.git('rev-parse','HEAD')==BASE,'Publisher revision changed')
    p.require(p.git('remote','get-url','origin')==p.EXPECTED_ORIGIN,'Origin changed')
    p.require(not p.git('diff','--name-only') and not p.git('diff','--cached','--name-only'),'Preserve existing publisher edits')
    untracked=set(p.git('ls-files','--others','--exclude-standard','-z',nul=True))
    p.require(untracked==p.PROTECTED_UNTRACKED,'Unexpected publisher untracked work')
    protected={name:p.sha(p.DEST/name) for name in sorted(p.PROTECTED_UNTRACKED)}
    previous=json.loads((ROOT/'docs/ultimate-release-2026-10-19/publication-preparation.json').read_text(encoding='utf-8'))
    p.require(protected==previous['protectedInheritedUntracked'],'Inherited files changed')
    paths=selected();copied=[]
    for name in sorted(paths):
        source=p.source_path(name);target=p.target_path(name)
        p.require(source.is_file() and source.stat().st_size<p.MAX_FILE_BYTES,'Missing/oversized source: '+name)
        if target.is_file() and p.sha(source)==p.sha(target):continue
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        p.require(p.sha(source)==p.sha(target),'Copy differs: '+name)
        copied.append({'path':name,'bytes':target.stat().st_size,'sha256':p.sha(target)})
    # Only superseded immutable assets are removed; nothing else is pruned.
    old=json.loads(p.git('show','HEAD:assets/generated/manifest.json'))
    current=json.loads((ROOT/'assets/generated/manifest.json').read_text())
    stale={row['url'].lstrip('/') for row in old.values()}-{row['url'].lstrip('/') for row in current.values()}
    pruned=[]
    for name in sorted(stale):
        p.require(re.fullmatch(r'assets/generated/[A-Za-z0-9._-]+-[a-f0-9]{12}\.(css|js|json)',name) is not None,'Unexpected generated path')
        target=p.target_path(name)
        if target.exists():target.unlink();pruned.append(name)
    report={'base':BASE,'origin':p.EXPECTED_ORIGIN,'copied':copied,'pruned':pruned,'protectedInheritedUntracked':protected,'rootGitModified':False,'staged':False}
    (OUT/'publication-preparation.json').write_text(json.dumps(report,indent=2)+'\n')
    if args.stage:
        names=[row['path'] for row in copied]+pruned
        for i in range(0,len(names),50):p.git('add','--',*names[i:i+50])
        actual=set(p.git('diff','--cached','--name-only','--no-renames','-z',nul=True))
        p.require(actual==set(names) and not actual&p.PROTECTED_UNTRACKED,'Unexpected staged paths')
        report['staged']=True;report['stagedPaths']=sorted(actual)
        (OUT/'publication-preparation.json').write_text(json.dumps(report,indent=2)+'\n')
    p.require(all(p.sha(p.DEST/name)==digest for name,digest in protected.items()),'Protected files changed')
    print(json.dumps({'copied':len(copied),'pruned':len(pruned),'staged':report['staged'],'rootGitModified':False}))

if __name__=='__main__':main()
