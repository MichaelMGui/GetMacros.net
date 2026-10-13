"""Validate only the staged release in an isolated checkout, including CI checks."""
from pathlib import Path
import json, os, subprocess, tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/master-completion-2026-10-13'
PUBLISHER = ROOT / 'docs/master-release-2026-10-12/publisher'
PYTHON = 'C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'

quality = [
    ['node', 'tools/test_macro_math.js'],
    ['node', 'tools/product_release/test-food.cjs'],
    ['node', 'tools/product_release/test-ingredient-comparison.cjs'],
    [PYTHON, '-X', 'utf8', 'tools/product_release/test-generators.py'],
    ['node', '--test', 'server/test/service.test.cjs'],
    ['node', 'tools/test-companion-engine.cjs'],
    ['node', 'tools/test-meal-view.cjs'],
    ['node', 'tools/test-growth-tools.cjs'],
    ['node', 'tools/international/test-markets.cjs'],
    [PYTHON, '-X', 'utf8', 'tools/growth_release/review-source.py', '--validate'],
    [PYTHON, '-X', 'utf8', 'tools/test_growth_release.py'],
    ['node', 'tools/play_release/test-rules.cjs'],
    [PYTHON, '-X', 'utf8', 'tools/test-release-content.py'],
    [PYTHON, '-X', 'utf8', 'tools/test_asset_stamps.py'],
    ['node', 'tools/master_release/test-branded-search.cjs'],
    ['node', 'tools/master_release/test-branded-integrity.cjs'],
    ['node', 'tools/master_release/test-diary-meals.cjs'],
    ['node', 'tools/master_completion/test-source-ui.cjs'],
    [PYTHON, '-X', 'utf8', 'tools/master_completion/grocery_integrity_off.py'],
    [PYTHON, '-X', 'utf8', 'tools/master_completion/test_integration.py'],
    ['node', 'tools/master_completion/grocery-search-off.cjs'],
    ['node', 'tools/master_completion/test_restaurant_adapter.cjs'],
]

def equivalent(relative, left, right):
    if relative.suffix not in ['.gz', '.png', '.jpg', '.webp', '.zip']:
        left = left.replace(b'\r\n', b'\n')
        right = right.replace(b'\r\n', b'\n')
    if left == right:
        return True
    if relative.as_posix() == 'js/meal-data.js':
        script = "const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');const x=JSON.parse(fs.readFileSync(0,'utf8')),load=s=>{const c={window:{}};vm.runInNewContext(s,c);return JSON.parse(JSON.stringify(c.window.GM_MEALS))};assert.deepEqual(load(x.a),load(x.b));"
        result = subprocess.run(['node', '-e', script], input=json.dumps({'a': left.decode(), 'b': right.decode()}), text=True, capture_output=True)
        return result.returncode == 0
    return False

with tempfile.TemporaryDirectory(prefix='getmacros-completion-index-') as directory:
    clean = Path(directory).resolve()
    assert clean.is_relative_to(Path(tempfile.gettempdir()).resolve())
    subprocess.run(['git', 'checkout-index', '--all', '--prefix=' + clean.as_posix() + '/'], cwd=PUBLISHER, check=True)
    environment = {**os.environ, 'GIT_DIR': str(PUBLISHER / '.git'), 'GIT_WORK_TREE': str(clean)}
    outcomes = []
    with (OUT / 'clean-source-build.log').open('w', encoding='utf-8') as log:
        commands = [[PYTHON, '-X', 'utf8', 'tools/run_food_build.py']] + quality
        for command in commands:
            log.write('\nCOMMAND: ' + ' '.join(command) + '\n'); log.flush()
            result = subprocess.run(command, cwd=clean, env=environment, stdout=log, stderr=subprocess.STDOUT)
            outcomes.append({'command': command, 'exitCode': result.returncode})
            print(command[-1], 'exit', result.returncode, flush=True)
            if result.returncode:
                break
    differences = []
    excluded = {'docs', 'tools', 'server', 'music-platform', 'node_modules', '.git', '.github', 'design'}
    for file in clean.rglob('*'):
        relative = file.relative_to(clean)
        if not file.is_file() or relative.parts[0] in excluded:
            continue
        active = ROOT / relative
        if not active.exists():
            differences.append({'path': relative.as_posix(), 'reason': 'unexpected generated public file'})
        elif not equivalent(relative, file.read_bytes(), active.read_bytes()):
            differences.append({'path': relative.as_posix(), 'reason': 'public bytes differ from reviewed application'})
    report = {'commands': outcomes, 'publicDifferences': differences, 'source': 'isolated approved publisher Git index; inherited untracked inputs excluded'}
    (OUT / 'clean-source-check.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('Isolated commands:', len(outcomes), '; public differences:', len(differences), flush=True)
    if any(row['exitCode'] for row in outcomes) or differences:
        print(json.dumps(differences[:20], indent=2))
        raise SystemExit(1)
