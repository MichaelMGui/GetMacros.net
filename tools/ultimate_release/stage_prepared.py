"""Verify and stage the explicit completed copy receipt, without rescanning catalogs."""
from pathlib import Path
import importlib.util,json,shutil,argparse
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/ultimate-release-2026-10-19'
spec=importlib.util.spec_from_file_location('guard',ROOT/'tools/global_coverage_2026_10_17/prepare_publication.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
EXTRA={'tools/ultimate_release/prepare_publication.py','tools/ultimate_release/stage_prepared.py','tools/ultimate_release/production_browser.cjs','tools/build_ultimate_release.py','tools/product-navigation.css','tools/ultimate_release/baseline.cjs','tools/ultimate_release/browser.cjs','tools/ultimate_release/calibrate.cjs','images/meal-cutouts/provenance.json'}
EXTRA.add('docs/clarity-release-2026-10-14/editorial-source-evidence/tim-hortons.pdf')

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--stage',action='store_true');args=parser.parse_args()
 file=OUT/'publication-preparation.json';report=json.loads(file.read_text(encoding='utf-8'))
 p.require(report['expectedHead']=='00e89456e2c9e59f7ce8789059704b2a0396e301','Unexpected receipt base')
 p.require(Path(report['publisher']).resolve()==p.DEST.resolve(),'Unexpected publisher')
 p.require(Path(p.git('rev-parse','--show-toplevel')).resolve()==p.DEST.resolve(),'Git resolved another checkout')
 p.require(p.git('rev-parse','HEAD')==report['expectedHead'],'Publisher HEAD changed')
 p.require(p.git('remote','get-url','origin')==report['origin']==p.EXPECTED_ORIGIN,'Origin changed')
 prepared={row['path']:row for row in report['copied']};pruned=set(report['pruned'])
 staged=set(p.git('diff','--cached','--name-only','--no-renames','-z',nul=True))
 p.require(not staged or report['mode']=='staging-in-progress' and staged<=set(report['stagePaths']) or report['mode']=='staged-explicit-paths' and staged==set(report['staged']),'Preserve unrelated staged work')
 untracked=set(p.git('ls-files','--others','--exclude-standard','-z',nul=True))
 p.require(p.PROTECTED_UNTRACKED<=untracked and untracked<=p.PROTECTED_UNTRACKED|set(prepared),'Unexpected untracked work')
 dirty=set(p.git('diff','--name-only','--no-renames','-z',nul=True))
 if report['mode']=='staged-explicit-paths':p.require(not dirty,'Prepared index/worktree changed independently')
 p.require(dirty<=set(prepared)|pruned,'Unexpected unstaged work')
 for name,digest in report['protectedInheritedUntracked'].items():
  p.no_reparse(p.DEST/name,p.DEST);p.require(p.sha(p.DEST/name)==digest,'Protected bytes changed: '+name)
 for name,row in prepared.items():
  target=p.target_path(name);p.require(target.is_file() and p.sha(target)==row['sha256'],'Prepared target changed: '+name)
  source=p.source_path(name)
  p.require(name in EXTRA or p.sha(source)==row['sha256'],'Source changed after reviewed copy: '+name)
 for name in pruned:p.require(not p.target_path(name).exists(),'Pruned asset reappeared: '+name)
 for name in sorted(EXTRA):
  source=p.source_path(name);target=p.target_path(name)
  p.require(source.is_file() and source.stat().st_size<p.MAX_FILE_BYTES,'Missing/oversized explicit addition: '+name)
  if not p.same_contents(source,target):target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,p.target_path(name))
  p.require(p.sha(source)==p.sha(target),'Copy hash differs: '+name)
  prepared[name]={'path':name,'bytes':target.stat().st_size,'sha256':p.sha(target)}
 tracked=set(p.git('ls-files','-z',nul=True))
 stage_paths=sorted(set(prepared)|{name for name in pruned if name in tracked}|staged)
 report.update({'copied':sorted(prepared.values(),key=lambda r:r['path']),'selectedFiles':sorted(set(report['selectedFiles'])|EXTRA),'stagePaths':stage_paths,'mode':'staging-in-progress' if args.stage else 'copy-receipt-verified'})
 file.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 if args.stage:
  for start in range(0,len(stage_paths),50):
   batch=[name for name in stage_paths[start:start+50] if name not in staged or name in EXTRA]
   if batch:p.git('add','--',*batch)
  staged=set(p.git('diff','--cached','--name-only','--no-renames','-z',nul=True))
  p.require(staged<=set(stage_paths) and not staged&p.PROTECTED_UNTRACKED,'Unexpected staged paths')
  report.update({'mode':'staged-explicit-paths','staged':sorted(staged)})
  (OUT/'changed-files.txt').write_text('\n'.join(sorted(staged))+'\n',encoding='utf-8')
  file.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'verifiedPreparedFiles':len(prepared),'staged':len(staged),'protectedFiles':5,'rootGitModified':False}))

if __name__=='__main__':main()
