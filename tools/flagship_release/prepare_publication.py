"""Scoped release publication. Only the established publisher Git is writable."""
from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('guarded_publisher',ROOT/'tools/global_coverage_2026_10_17/prepare_publication.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
p.EXPECTED_HEAD='7f33f665c04b8203fc5eba6645b8669fc343a65b'
collect_previous=p.collect_paths
RELEASE=ROOT/'docs/flagship-release-2026-10-18'
CHANGED={'_config.yml','tools/build_flagship_release.py','tools/integrate_playful_release.py','tools/test_publication.py','tools/validate_site.py','tools/master_completion/test_integration.py','tools/international/test-markets.cjs','tools/product_release/test-food.cjs','tools/build_global_coverage_release.py','tools/build_edition_css.py','tools/build_visible_workspace.py','tools/food-design.css','tools/release-product.css','tools/product-navigation.css','tools/liquid-motion.css','tools/home-workspace.css','tools/playful-system.css','tools/run_food_build.py','tools/build_site.sh','tools/site_scope.py','tools/product_release/render-finder.cjs','tools/product_release/test-generators.py','tools/test_visible_workspace.py','tools/test_master_homepages.py','tools/test-meal-view.cjs','tools/flagship_release/prepare_publication.py'}
CHANGED.add('tools/global_coverage_2026_10_17/mexico-supplement-test.py')
CHANGED.add('docs/publication-page-audit.csv')
def collect():
    paths,evidence=collect_previous()
    paths.update(CHANGED)
    for f in (ROOT/'tools/flagship_release').rglob('*'):
        if f.is_file() and '__pycache__' not in f.parts and f.suffix in {'.py','.cjs','.js','.json','.css'}:paths.add(f.relative_to(ROOT).as_posix())
    for f in (ROOT/'native/app').rglob('*'):
        rel=f.relative_to(ROOT/'native/app')
        if any(x in rel.parts for x in ['node_modules','www','public','.git','DerivedData','build','capacitor-cordova-ios-plugins']):continue
        if f.is_file() and f.name not in ['build-report.json','.DS_Store'] and rel.as_posix() not in ['ios/App/App/capacitor.config.json','ios/App/App/config.xml']:paths.add(f.relative_to(ROOT).as_posix())
    # Exact primary captures used by source-hash regression tests are review
    # evidence, not public website assets. Keep their source names and bytes.
    for f in RELEASE.rglob('*'):
        rel=f.relative_to(RELEASE)
        if not f.is_file() or 'checkpoint' in rel.parts or f.suffix in {'.log','.pyc'} or f.name=='publication-preparation.json':continue
        if f.suffix.lower() not in {'.md','.txt','.json','.csv','.html','.pdf','.js','.png','.jpg','.jpeg','.zip','.webm'}:continue
        if f.stat().st_size>30_000_000:continue
        name=f.relative_to(ROOT).as_posix();paths.add(name);evidence.append(name)
    for name in paths:
        source=p.source_path(name)
        p.require(source.is_file() and source.stat().st_size<p.MAX_FILE_BYTES,'Selected release source absent/oversized: '+name)
    p.require('native/app/capacitor.config.json' in paths,'The authored native build configuration must be published')
    return paths,sorted(set(evidence))
p.collect_paths=collect
# Keep the previous collector's historical evidence roots while selecting files.
previous_out=p.OUT
def collect_scoped():
    p.OUT=previous_out
    try:return collect()
    finally:p.OUT=RELEASE
p.collect_paths=collect_scoped
p.OUT=RELEASE;p.REPORT=RELEASE/'publication-preparation.json'
previous_prunes=p.generated_prunes
def generated_prunes(paths):
    result=previous_prunes(paths)
    # Only this preparation's own ignored native build receipt may be removed.
    # The actual package evidence lives in docs; the project regenerates it.
    generated=['native/app/build-report.json','native/app/ios/App/App/config.xml','native/app/ios/capacitor-cordova-ios-plugins/CordovaPluginsResources.podspec','native/app/ios/capacitor-cordova-ios-plugins/resources/.gitkeep','native/app/ios/capacitor-cordova-ios-plugins/sources/.gitkeep']
    for name in generated:
        target=p.target_path(name)
        if target.is_file() and name not in paths:
            receipt=json.loads(p.REPORT.read_text(encoding='utf-8')) if p.REPORT.exists() else {}
            row=next((r for r in receipt.get('copied',[]) if r['path']==name),None)
            p.require(row and p.sha(target)==row['sha256'],'Unrelated native generated file must be preserved')
            result.append(name)
    return result
p.generated_prunes=generated_prunes
if __name__=='__main__':p.main()
