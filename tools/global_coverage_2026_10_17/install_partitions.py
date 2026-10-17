"""Install audited source partitions; retire only files owned by those partitions."""
from pathlib import Path
import json, shutil

ROOT = Path(__file__).resolve().parents[2]
STAGES = {
    'usda': ROOT/'docs/global-coverage-2026-10-17/usda/staged',
    'off': ROOT/'docs/global-coverage-2026-10-17/off/partition',
}

def install():
    report = {}
    for provider, stage in STAGES.items():
        target = (ROOT/'data/branded-foods'/provider).resolve()
        assert target.parent == (ROOT/'data/branded-foods').resolve()
        manifest = json.loads((stage/'manifest.json').read_text(encoding='utf-8'))
        assert manifest['jsonEncoding'] == 'gzip'
        assert manifest['profileCount'] > 200000
        owned = {p.relative_to(stage) for p in stage.rglob('*') if p.is_file()}
        for relative in sorted(owned, key=str):
            if relative == Path('manifest.json'): continue
            dest = target/relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(stage/relative, dest)
        # Only generated query/record files are retired. Rights, old evidence and
        # source documents outside those generated directories are preserved.
        removed = 0
        for folder in ('records','index','tokens','barcodes','brands','markets'):
            for path in (target/folder).rglob('*'):
                if not path.is_file() or path.relative_to(target) in owned: continue
                assert path.resolve().is_relative_to(target)
                assert path.suffix in ('.json','.gz')
                path.unlink(); removed += 1
        shutil.copy2(stage/'manifest.json', target/'manifest.json')
        report[provider] = dict(profiles=manifest['profileCount'], version=manifest['version'], copied=len(owned), retiredGeneratedFiles=removed)
    (ROOT/'docs/global-coverage-2026-10-17/installed.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))

if __name__ == '__main__': install()
