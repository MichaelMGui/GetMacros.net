"""Reconcile only this release's post-preparation generator/test outputs."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess
import prepare_publication as p

assert p.git('rev-parse','HEAD') == '8e5a7d70b428fbaa7eae2eac04a1a97e27783874'
assert p.git('remote','get-url','origin') == p.EXPECTED_ORIGIN
receipt=json.loads((p.OUT/'publication-followup-preparation.json').read_text(encoding='utf-8'))
protected=receipt['protectedInheritedUntracked']
for name,digest in protected.items():assert p.sha(p.DEST/name)==digest
results=json.loads((p.DEST/'docs/global-coverage-2026-10-17/ci-command-results.json').read_text(encoding='utf-8'))
assert results['passAll'] and results['completed']==results['planned']==32

sources={'.github/workflows/site-quality.yml','tools/ci_failure_summary.py',
 'tools/build_global_coverage_release.py','tools/international/test-markets.cjs',
 'tools/global_coverage_2026_10_17/prepare_publication.py',
 'tools/global_coverage_2026_10_17/finalize_followup.py',
 'tools/global_coverage_2026_10_17/restaurant_newmarkets_stage.py',
 'docs/global-coverage-2026-10-17/restaurants/newmarkets/source-register.json',
 *{'docs/global-coverage-2026-10-17/restaurants/newmarkets/'+name for name in ['quick-fr-index.html','mcd-in-ne-index.html','bk-sg-main.js']}}
markets=json.loads(re.search(r'window.GM_MARKETS=(.*);',(p.ROOT/'js/market-definitions.js').read_text(encoding='utf-8'))[1])
for info in markets.values():
    route=info['finder'];sources.add(route.strip('/')+'/index.html' if route.endswith('/') else route.lstrip('/'))
for name in sorted(sources):
    source,target=p.source_path(name),p.target_path(name)
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,target)
    assert p.sha(source)==p.sha(target)

# These paths were clean before our repeat-generator rehearsal and changed
# only because those tests regenerate historical diagnostic reports.
generated_reports={
 'docs/clarity-release-2026-10-14/coverage.csv',
 'docs/clarity-release-2026-10-14/editorial-facts.json',
 'docs/clarity-release-2026-10-14/editorial-manifest.json',
 'docs/clarity-release-2026-10-14/restaurant-integration.json',
 'docs/cozy-redesign-2026-10-03/engine-tests.json',
 'docs/master-completion-2026-10-13/grocery-coverage.json',
 'docs/master-completion-2026-10-13/restaurant-integration.json',
 'docs/master-release-2026-10-12/homepage-manifest.json',
 'docs/release-2026-10-03/content-tests.json',
}
verified_outputs={
 'docs/global-coverage-2026-10-17/restaurants/newmarkets/test-results.json',
 'docs/global-coverage-2026-10-17/restaurants/test-results.json',
 'docs/master-completion-2026-10-13/grocery-integrity.json',
}
allowed=set(receipt['stagePaths'])|sources|generated_reports|verified_outputs
dirty=set(p.git('diff','--name-only','--no-renames','-z',nul=True))
assert dirty<=allowed, 'Unexpected post-test changes: '+str(sorted(dirty-allowed))
restore=sorted(dirty&generated_reports-set(receipt['stagePaths']))
if restore:p.git('restore','--worktree','--',*restore)
stage=sorted(sources | (dirty & (set(receipt['stagePaths'])|verified_outputs)))
for offset in range(0,len(stage),50):p.git('add','--',*stage[offset:offset+50])
staged=set(p.git('diff','--cached','--name-only','--no-renames','-z',nul=True))
assert staged<=set(receipt['stagePaths'])|sources|verified_outputs
assert not set(protected)&staged
for name,digest in protected.items():assert p.sha(p.DEST/name)==digest
for directory in ['restaurants','restaurants/newmarkets','restaurants/supplement']:
    register=p.OUT/directory/'source-register.json'
    for row in json.loads(register.read_text(encoding='utf-8')):
        blob=subprocess.check_output(['git','show',':'+row['file']],cwd=p.DEST)
        assert hashlib.sha256(blob).hexdigest()==row['sha256'],row['file']+' staged source bytes'
subprocess.run(['node','tools/international/test-markets.cjs'],cwd=p.DEST,check=True)
print(json.dumps({'stagedFiles':len(staged),'restoredOwnDiagnosticReports':len(restore),'publisherCommandsPassed':32,'inheritedUntrackedPreserved':len(protected)}))
