"""Prepare the reviewed global release in its established publisher checkout.

Default: scoped copy, safe generated-file pruning, and a preparation report.
--stage: additionally stage explicit prepared paths in batches. No commit,
push, build, deployment, root Git operation, or generic workspace sync exists.
Offline import archives and duplicate staging partitions are never copied.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'docs/master-release-2026-10-12/publisher'
OUT = ROOT / 'docs/global-coverage-2026-10-17'
REPORT = OUT / 'publication-preparation.json'
EXPECTED_HEAD = '8b35778b390192859e48c12ac265d1a80ce75862'
EXPECTED_ORIGIN = 'https://github.com/MichaelMGui/GetMacros.net.git'
MAX_PUBLIC_BYTES = 1_000_000_000
MAX_FILE_BYTES = 95_000_000
MAX_EVIDENCE_FILE = 2_000_000
MAX_EVIDENCE_TOTAL = 20_000_000

PROTECTED_UNTRACKED = {
    'docs/playful-release-2026-10-04/editorial/existing-intent-review.json',
    'docs/playful-release-2026-10-04/editorial/integration.json',
    'tools/restaurant_release/metadata-overrides.json',
    'tools/restaurant_release/review-records.json',
    'tools/restaurant_release/validation-report.json',
}
ROOT_FILES = {
    '.gitignore', '.gitattributes', '.nojekyll', '_config.yml', 'CNAME', 'ads.txt', 'robots.txt',
    'sitemap.xml', 'feed.xml', 'site.webmanifest', 'sw.js', 'favicon.svg',
    'icon-sprite.svg', 'apple-touch-icon.png', '.well-known/security.txt',
}
# Exact reviewed build/reader/test changes. Existing unchanged build dependencies
# already belong to the guarded publisher HEAD; unrelated root tools are omitted.
SOURCE_FILES = {
    '.github/workflows/site-quality.yml',
    'tools/source_json.py', 'tools/source-json.cjs',
    'tools/build_global_coverage_release.py', 'tools/build_master_completion.py',
    'tools/build_site.sh', 'tools/run_food_build.py', 'tools/site_scope.py',
    'tools/refresh_release_search.py', 'tools/validate_site.py',
    'tools/stamp_assets.py',
    'tools/master_completion/test_integration.py',
    'tools/international/test-markets.cjs',
    'tools/product_release/test-food.cjs',
    'tools/product_release/test-generators.py',
    'tools/clarity_release/test-comparison.cjs',
    'tools/clarity_release/test_editorial.py',
    'tools/master_release/test-branded-integrity.cjs',
    'tools/master_release/test-branded-search.cjs',
    'tools/master_release/test_branded_import.py',
    'tools/master_completion/grocery-search-off.cjs',
    'tools/master_completion/grocery_brand_coverage.py',
    'tools/master_completion/grocery_integrity_off.py',
    'tools/master_completion/grocery_test_off.py',
}
PUBLIC_EXTENSIONS = {
    'css': {'.css'}, 'js': {'.js', '.json'},
    'fonts': {'.woff', '.woff2', '.ttf', '.otf', '.txt', '.md'},
    'images': {'.svg', '.png', '.jpg', '.jpeg', '.webp', '.avif', '.gif', '.ico', '.txt', '.md'},
    # OFF's licensed source/normalized exports, rights and normalizer are public
    # data dependencies. The offline raw download archives live under docs.
    'data': {'.json', '.gz', '.py', '.txt', '.md', '.csv', '.tsv'},
    'assets': {'.css', '.js', '.json', '.svg', '.png', '.jpg', '.jpeg', '.webp', '.woff', '.woff2', '.txt', '.md'},
}
TEXT_EXTENSIONS = {'.html', '.css', '.js', '.json', '.py', '.cjs', '.sh', '.yml', '.yaml', '.md', '.txt', '.csv', '.xml', '.svg', '.webmanifest'}
EVIDENCE_METADATA = {'guide-briefs.json', 'source-register.json', 'summary.json', 'test-results.json', 'withheld.json', 'retrieval.json', 'source-research.json', 'handoff.txt'}
SKIP_EVIDENCE = {'publication-preparation.json', 'baseline.json'}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def no_reparse(path, boundary):
    """Reject symlinks/junctions before any file operation under either tree."""
    boundary = boundary.absolute()
    for item in (path.absolute(), *path.absolute().parents):
        require(not item.is_symlink() and not getattr(item, 'is_junction', lambda: False)(), 'Reparse point is outside publication policy: ' + str(item))
        if item == boundary:
            return
    raise RuntimeError('Path is not below its declared boundary: ' + str(path))


def source_path(name):
    path = ROOT / name
    no_reparse(path, ROOT)
    resolved = path.resolve()
    require(resolved.is_relative_to(ROOT.resolve()) and not resolved.is_relative_to(DEST.resolve()), 'Source escapes the workspace or recurses into publisher: ' + name)
    require('.git' not in Path(name).parts and name not in PROTECTED_UNTRACKED, 'Protected source path: ' + name)
    return path


def target_path(name):
    require(not Path(name).is_absolute() and '..' not in Path(name).parts and '.git' not in Path(name).parts, 'Unsafe publisher-relative path: ' + name)
    path = DEST / name
    no_reparse(path, DEST)
    resolved = path.resolve()
    require(resolved != DEST.resolve() and resolved.is_relative_to(DEST.resolve()), 'Resolved target is outside publisher: ' + name)
    require(name not in PROTECTED_UNTRACKED, 'Inherited untracked input must not be overwritten: ' + name)
    return path


def sha(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def git(*arguments, nul=False):
    # Even inherited Git environment overrides cannot redirect this script into
    # root .git. All Git commands explicitly run in the checked publisher.
    environment = {key: value for key, value in os.environ.items() if key not in {'GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'}}
    result = subprocess.run(['git', '--no-optional-locks', '-c', 'gc.auto=0', '-c', 'core.safecrlf=false', *arguments], cwd=DEST, env=environment, check=True, capture_output=True)
    value = result.stdout.decode('utf-8')
    return [part for part in value.split('\0') if part] if nul else value.strip()


def collect_paths():
    paths = {path.relative_to(ROOT).as_posix() for path in ROOT.glob('*.html')}
    for directory in ROOT.iterdir():
        if directory.is_dir() and re.fullmatch(r'[a-z]{2}', directory.name) and (directory / 'en').is_dir():
            paths.update(path.relative_to(ROOT).as_posix() for path in (directory / 'en').rglob('*.html') if path.is_file())
    paths.update(name for name in ROOT_FILES if (ROOT / name).is_file())
    for name in SOURCE_FILES:
        require((ROOT / name).is_file(), 'Required release source is absent: ' + name)
        paths.add(name)
    for directory, extensions in PUBLIC_EXTENSIONS.items():
        for path in (ROOT / directory).rglob('*'):
            if path.is_file() and path.suffix.lower() in extensions and '__pycache__' not in path.parts:
                name = path.relative_to(ROOT).as_posix()
                if not name.startswith('assets/generated/'):
                    paths.add(name)
    asset_manifest = json.loads((ROOT / 'assets/generated/manifest.json').read_text(encoding='utf-8'))
    paths.add('assets/generated/manifest.json')
    for entry in asset_manifest.values():
        name = entry['url'].lstrip('/')
        require(name.startswith('assets/generated/') and re.fullmatch(r'[A-Za-z0-9._-]+-[a-f0-9]{12}\.(css|js|json)', Path(name).name), 'Unexpected generated asset manifest output: ' + name)
        paths.add(name)
    family = ROOT / 'tools/global_coverage_2026_10_17'
    paths.update(path.relative_to(ROOT).as_posix() for path in family.iterdir() if path.is_file() and path.suffix in {'.py', '.cjs', '.js', '.json', '.sh', '.css'})
    evidence = set()
    for directory in (OUT, OUT / 'usda', OUT / 'off'):
        if directory.exists():
            evidence.update(path for path in directory.iterdir() if path.is_file() and path.suffix in {'.json', '.md', '.txt', '.csv'} and path.name not in SKIP_EVIDENCE)
    for directory in (OUT / 'restaurants', OUT / 'restaurants/newmarkets'):
        if not directory.exists():
            continue
        evidence.update(path for path in directory.iterdir() if path.is_file() and path.name in EVIDENCE_METADATA)
        register = directory / 'source-register.json'
        if register.exists():
            for row in json.loads(register.read_text(encoding='utf-8')):
                path = ROOT / row['file']
                established_gyg=ROOT/'docs/global-product-release-2026-10-11/sources/gyg.pdf'
                require(path.resolve().is_relative_to((OUT / 'restaurants').resolve()) or path.resolve()==established_gyg.resolve(), 'Registered evidence is outside the reviewed evidence scope')
                require(path.suffix.lower() in {'.json', '.txt', '.html', '.pdf', '.png', '.jpg', '.jpeg'}, 'Offline archive is not bounded publication evidence: ' + str(path))
                evidence.add(path)
    for path in evidence:
        require(path.is_file() and path.stat().st_size <= MAX_EVIDENCE_FILE, 'Required evidence is absent or exceeds 2 MB: ' + str(path))
    require(sum(path.stat().st_size for path in evidence) <= MAX_EVIDENCE_TOTAL, 'Bounded release evidence exceeds 20 MB')
    paths.update(path.relative_to(ROOT).as_posix() for path in evidence)
    for name in paths:
        path = source_path(name)
        require(path.is_file() and path.stat().st_size < MAX_FILE_BYTES, 'Selected source is absent or exceeds the 95 MB file ceiling: ' + name)
    return paths, sorted(path.relative_to(ROOT).as_posix() for path in evidence)


def generated_prunes(paths):
    result = []
    directory = DEST / 'assets/generated'
    if directory.exists():
        no_reparse(directory, DEST)
        for path in directory.iterdir():
            name = path.relative_to(DEST).as_posix()
            if path.is_file() and re.fullmatch(r'[A-Za-z0-9._-]+-[a-f0-9]{12}\.(css|js|json)', path.name) and name not in paths:
                target_path(name); result.append(name)
    for source in ('usda', 'off', 'cnf', 'retailer-ca'):
        for kind in ('records', 'index', 'tokens', 'barcodes', 'markets', 'brands'):
            directory = DEST / 'data/branded-foods' / source / kind
            if not directory.exists():
                continue
            no_reparse(directory, DEST)
            for path in directory.iterdir():
                name = path.relative_to(DEST).as_posix()
                match = re.fullmatch(r'(.+)\.json(?:\.gz)?', path.name)
                if not path.is_file() or not match or name in paths:
                    continue
                stem = match[1]
                owned = (kind == 'records' and bool(re.fullmatch(r'[a-f0-9]{2,3}', stem)) or kind == 'index' and stem.isdigit() and len(stem) >= 4 or kind == 'tokens' and len(stem) in (1, 2) and stem.isalnum() or kind == 'barcodes' and bool(re.fullmatch(r'\d{3}', stem)) or kind in ('markets', 'brands') and bool(re.fullmatch(r'[A-Z]{2}(?:-reference)?', stem)))
                if owned:
                    target_path(name); result.append(name)
    return sorted(set(result))


def public_inventory(overrides=None, removed=()):
    """Conservative actual publishable tree, honoring current Jekyll excludes."""
    config = (ROOT / '_config.yml').read_text(encoding='utf-8')
    exclusions = {'.git', '.github', '.agents', '.codex', '.aws', 'node_modules'}
    block = re.search(r'(?m)^exclude:\s*\n((?:[ \t]+-.*\n?)*)', config)
    require(block is not None, 'Current publication configuration must declare exclusions')
    exclusions.update(line.strip()[1:].strip().strip('"\'').rstrip('/') for line in block[1].splitlines())
    files = {}
    for base, directories, names in os.walk(DEST, followlinks=False):
        relative = Path(base).relative_to(DEST)
        directories[:] = [name for name in directories if (relative / name).as_posix() not in exclusions and name != '.git']
        for leaf in names:
            name = (relative / leaf).as_posix()
            if name not in exclusions and name not in removed:
                no_reparse(DEST / name, DEST)
                files[name] = (DEST / name).stat().st_size
    for name, size in (overrides or {}).items():
        if name not in exclusions and not any(name == excluded or name.startswith(excluded + '/') for excluded in exclusions):
            files[name] = size
    largest = max(files, key=files.get) if files else None
    total = sum(files.values())
    require(total < MAX_PUBLIC_BYTES, 'Actual publishable tree reaches the 1 GB ceiling')
    require(not largest or files[largest] < MAX_FILE_BYTES, 'Actual publishable file reaches the 95 MB ceiling: ' + str(largest))
    return {'files': len(files), 'bytes': total, 'largestFile': largest, 'largestFileBytes': files.get(largest, 0), 'policy': 'Conservative publisher file inventory excluding configured development paths; no packing or compression estimates.'}


def same_contents(source, target):
    if not target.is_file():
        return False
    if source.suffix.lower() in TEXT_EXTENSIONS or source.name in {'.gitignore', 'CNAME'}:
        return source.read_bytes().replace(b'\r\n', b'\n') == target.read_bytes().replace(b'\r\n', b'\n')
    return source.stat().st_size == target.stat().st_size and sha(source) == sha(target)


def write_report(report):
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', action='store_true', help='Stage explicit prepared files only; never commit or push')
    parser.add_argument('--recover-interrupted-copy', action='store_true', help='Recover this release\'s interrupted copy receipt; only explicitly selected files may be adopted')
    args = parser.parse_args()
    no_reparse(DEST, ROOT)
    require((DEST / '.git').is_dir() and DEST.resolve().is_relative_to((ROOT / 'docs').resolve()), 'Publisher checkout is missing or outside workspace docs')
    require(Path(git('rev-parse', '--show-toplevel')).resolve() == DEST.resolve(), 'Git resolved a different checkout')
    require(git('rev-parse', 'HEAD') == EXPECTED_HEAD, 'Publisher HEAD changed; review and update the pinned base explicitly')
    require(git('remote', 'get-url', 'origin') == EXPECTED_ORIGIN, 'Publisher origin differs from the reviewed repository')
    require(not git('diff', '--cached', '--name-only', '-z', nul=True), 'Existing staged publisher work must be preserved')
    protected = {}
    for name in sorted(PROTECTED_UNTRACKED):
        path = DEST / name; no_reparse(path, DEST)
        require(path.is_file(), 'Inherited untracked input is missing: ' + name)
        protected[name] = sha(path)
    previous = json.loads(REPORT.read_text(encoding='utf-8')) if REPORT.exists() else {}
    if previous:
        require(previous.get('expectedHead') == EXPECTED_HEAD and previous.get('publisher') == str(DEST.resolve()), 'Previous preparation report belongs to another checkout/base')
    prepared = {row['path']: row for row in previous.get('copied', [])}
    old_prunes = set(previous.get('pruned', []))
    for name, row in prepared.items():
        target = target_path(name)
        require(target.is_file() and sha(target) == row['sha256'], 'Prepared publisher file changed independently: ' + name)
    for name in old_prunes:
        require(not target_path(name).exists(), 'Previously pruned generated file reappeared: ' + name)
    untracked = set(git('ls-files', '--others', '--exclude-standard', '-z', nul=True))
    paths, evidence = collect_paths()
    if args.recover_interrupted_copy:
        require(not previous,'A completed preparation receipt already exists')
        changed=set(git('diff','--name-only','--no-renames','-z',nul=True))
        for name in (untracked-PROTECTED_UNTRACKED)|changed:
            target=target_path(name)
            if target.is_file():
                require(name in paths,'Interrupted copy contains an unrelated path: '+name)
                prepared[name]={'path':name,'bytes':target.stat().st_size,'sha256':sha(target)}
            else:
                require(name not in paths and (name.startswith('assets/generated/') or re.match(r'^data/branded-foods/(usda|off)/(records|index|tokens|barcodes|markets|brands)/[^/]+\.json(?:\.gz)?$',name)), 'Unexpected deleted path: '+name)
                old_prunes.add(name)
    require(PROTECTED_UNTRACKED <= untracked and untracked <= PROTECTED_UNTRACKED | set(prepared), 'Unexpected untracked publisher work must be reviewed separately')
    dirty = set(git('diff', '--name-only', '--no-renames', '-z', nul=True))
    require(dirty <= set(prepared) | old_prunes, 'Unrelated unstaged publisher work must be preserved')
    prunes = generated_prunes(paths)
    require(set(prepared) <= paths | set(prunes), 'A previous copied path left the explicit publication scope')
    tracked = set(git('ls-files', '-z', nul=True))
    projected = public_inventory({name: source_path(name).stat().st_size for name in paths}, set(prunes) | old_prunes)
    copied_now = []
    for name in prunes:
        # Recheck the resolved absolute target immediately before each unlink.
        target_path(name).unlink()
        prepared.pop(name, None)
    for name in sorted(paths):
        source, target = source_path(name), target_path(name)
        if same_contents(source, target):
            if name not in tracked:
                prepared[name]={'path':name,'bytes':target.stat().st_size,'sha256':sha(target)}
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target = target_path(name)
        shutil.copyfile(source, target)
        require(sha(source) == sha(target), 'Copied bytes differ from reviewed source: ' + name)
        prepared[name] = {'path': name, 'bytes': target.stat().st_size, 'sha256': sha(target)}
        copied_now.append(name)
    pruned = sorted((old_prunes | set(prunes)) - paths)
    actual = public_inventory()
    # Byte-identical text after newline normalization can retain an existing
    # CRLF file, so its actual size may exceed the LF source projection. The
    # actual tree, not that estimate, is checked against both hard ceilings.
    worker = (DEST / 'sw.js').read_text(encoding='utf-8')
    assets = re.search(r'const APP_ASSETS=(\[.*?\]);', worker)
    require(assets is not None, 'Worker app asset list is missing')
    for name in json.loads(assets[1]):
        require(target_path(name.lstrip('/')).is_file(), 'Worker app asset was omitted: ' + name)
    for name, digest in protected.items():
        require(sha(DEST / name) == digest, 'Inherited untracked bytes changed: ' + name)
    stage_paths = sorted(set(prepared) | {name for name in pruned if name in tracked})
    counts = Counter(name.split('/')[0] if '/' in name else '(root)' for name in paths)
    report = {'schemaVersion': 1, 'expectedHead': EXPECTED_HEAD, 'publisher': str(DEST.resolve()), 'origin': EXPECTED_ORIGIN, 'mode': 'stage-requested' if args.stage else 'copy-only', 'copied': sorted(prepared.values(), key=lambda row: row['path']), 'copiedThisRun': copied_now, 'pruned': pruned, 'selectedFiles': sorted(paths), 'selectedCounts': dict(counts), 'sourceFiles': sorted(name for name in paths if name.startswith('tools/') or name.startswith('.github/')), 'boundedEvidenceFiles': evidence, 'protectedInheritedUntracked': protected, 'publicTree': actual, 'offlineAssetsChecked': len(json.loads(assets[1])), 'stagePaths': stage_paths, 'staged': []}
    write_report(report)
    if args.stage:
        require(git('rev-parse', 'HEAD') == EXPECTED_HEAD, 'Publisher HEAD changed during preparation; staging stopped')
        require(not git('diff', '--cached', '--name-only', '-z', nul=True), 'Staged publisher work appeared during preparation; staging stopped')
        capture='docs/global-product-release-2026-10-11/sources/gyg.pdf'
        regular=[name for name in stage_paths if name!=capture]
        for offset in range(0, len(regular), 50):
            git('add', '--', *regular[offset:offset + 50])
        # This one bounded official source capture is required by the reviewed
        # menu regression. Other offline source archives remain ignored.
        if capture in stage_paths:git('add','-f','--',capture)
        staged = git('diff', '--cached', '--name-only', '--no-renames', '-z', nul=True)
        require(set(staged) <= set(stage_paths) and not set(staged) & PROTECTED_UNTRACKED, 'Unrelated staged work appeared')
        report.update({'mode': 'staged-explicit-paths', 'staged': staged})
        write_report(report)
    print(json.dumps({'mode': report['mode'], 'selectedFiles': len(paths), 'copiedThisRun': len(copied_now), 'pruned': len(prunes), 'staged': len(report['staged']), 'publicBytes': actual['bytes'], 'largestPublicFileBytes': actual['largestFileBytes'], 'inheritedUntrackedPreserved': len(protected), 'report': str(REPORT)}, indent=2))


if __name__ == '__main__':
    main()
