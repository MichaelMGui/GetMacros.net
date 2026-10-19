"""Publish only the reviewed visual/editorial release through the existing checkout.

This preparation never touches root Git, force-pushes, changes hosting or copies
raw catalog archives. The guarded publisher owns all Git operations.
"""
from pathlib import Path
import importlib.util,os
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('guarded_publisher',ROOT/'tools/global_coverage_2026_10_17/prepare_publication.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
p.EXPECTED_HEAD='00e89456e2c9e59f7ce8789059704b2a0396e301'
p.PUBLIC_EXTENSIONS['images'].add('.json')
collect_previous=p.collect_paths
previous_out=p.OUT
RELEASE=ROOT/'docs/ultimate-release-2026-10-19'
CHANGED={
 'tools/build_ultimate_release.py','tools/theme-palettes.css',
 'tools/build_master_interface.py','tools/build_visible_workspace.py',
 'tools/build_edition_css.py','tools/build_site.sh','tools/run_food_build.py',
 'tools/food-design.css','tools/release-product.css','tools/product-navigation.css',
 'tools/home-workspace.css','tools/liquid-motion.css','tools/play-release.css',
 'tools/release-library.css','tools/product_release/test-generators.py',
 'tools/test_publication.py','tools/validate_site.py','tools/site_scope.py',
 '.github/workflows/site-quality.yml','.gitattributes',
 'docs/publication-page-audit.csv','docs/monetization/journey-readiness.md',
 'docs/clarity-release-2026-10-14/editorial-source-evidence/tim-hortons.pdf',
 'tools/flagship_release/production_verify.cjs',
}

def collect():
 p.OUT=previous_out
 try:paths,evidence=collect_previous()
 finally:p.OUT=RELEASE
 paths.update(CHANGED)
 for f in (ROOT/'tools/ultimate_release').rglob('*'):
  if f.is_file() and '__pycache__' not in f.parts and f.suffix in {'.py','.cjs','.js','.json','.css'}:paths.add(f.relative_to(ROOT).as_posix())
 # Include exact source captures required by source-hash tests. These remain
 # development evidence excluded from the public Jekyll site.
 for f in RELEASE.rglob('*'):
  rel=f.relative_to(RELEASE)
  if not f.is_file() or any(x in rel.parts for x in ['checkpoint','__pycache__']) or f.suffix in {'.log','.pyc'} or f.name=='publication-preparation.json':continue
  # This external capture contains credential-like strings, unrelated to nutrient checks.
  if rel.as_posix()=='editorial/foodtools-sources/gs1_origin.html':continue
  if f.suffix.lower() not in {'.md','.txt','.json','.csv','.html','.pdf','.js','.png','.jpg','.jpeg','.zip','.webm'}:continue
  if f.stat().st_size>30_000_000:continue
  name=f.relative_to(ROOT).as_posix();paths.add(name);evidence.append(name)
 # Only authored native sources, never the rebuildable copied web bundle.
 excluded={'node_modules','www','public','.git','DerivedData','build','capacitor-cordova-ios-plugins'}
 for base,directories,files in os.walk(ROOT/'native/app',followlinks=False):
  # Prune before descent, including Windows package-manager junction trees.
  directories[:]=[name for name in directories if name not in excluded]
  for name in files:
   f=Path(base)/name;rel=f.relative_to(ROOT/'native/app')
   if name not in ['build-report.json','.DS_Store'] and rel.as_posix() not in ['ios/App/App/capacitor.config.json','ios/App/App/config.xml']:paths.add(f.relative_to(ROOT).as_posix())
 for name in paths:
  source=p.source_path(name)
  p.require(source.is_file() and source.stat().st_size<p.MAX_FILE_BYTES,'Selected release source absent/oversized: '+name)
 return paths,sorted(set(evidence))

p.collect_paths=collect
p.OUT=RELEASE;p.REPORT=RELEASE/'publication-preparation.json'
if __name__=='__main__':p.main()
