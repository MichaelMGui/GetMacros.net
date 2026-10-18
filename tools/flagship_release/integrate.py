"""Install reviewed source snapshots using the established country pipeline."""
from pathlib import Path
from collections import Counter
import json
ROOT=Path(__file__).resolve().parents[2]
DATE='2026-10-18'
def build():
    import build_global_coverage_release as coverage
    from build_master_interface import build as homes
    from build_visible_workspace import build as workspace
    files=[Path(__file__).with_name('markets_release_records.json'),Path(__file__).with_name('uk_records.json')]
    mexico=Path(__file__).with_name('markets_mexico_calories.json')
    if mexico.exists():files.append(mexico)
    batches=[json.loads(p.read_text(encoding='utf-8')) for p in files]
    additions=[r for b in batches for r in b['records']];updates=[r for b in batches for r in b.get('updates',[])]
    assert len({r['id'] for r in additions})==len(additions)
    assert not {r['id'] for r in additions}&{r['id'] for r in updates}
    presence=[r for b in batches for r in b.get('presenceUpserts',[])]
    from flagship_release.uk_integration import presence_upserts
    presence+=presence_upserts()
    coverage.DATE=DATE
    extra=dict(records=additions,updates=updates,presenceUpserts=presence,withdrawnIds=[r for b in batches for r in b.get('withdrawnIds',[])])
    all_additions,registry,markets,presence=coverage.integrate(extra)
    coverage.guides(extra,registry,markets,presence)
    homes();workspace()
    count=Counter(r['market'] for r in registry['records'])
    report=dict(date=DATE,inputFiles=[p.relative_to(ROOT).as_posix() for p in files],newSourcePortions=sum(r.get('verificationStatus')!='calculated-from-official-components' for r in additions),newCalculatedOrders=sum(r.get('verificationStatus')=='calculated-from-official-components' for r in additions),refreshedSourcePortions=len(updates),registryRecords=len(registry['records']),newByMarket=dict(Counter(r['market'] for r in additions)),recordsByMarket=dict(count),chainsByMarket={code:len({r['chain'] for r in registry['records'] if r['market']==code}) for code in markets},newSourceChainRelationships=len({(r['market'],r['chain']) for r in additions}),scope='Exact source snapshots. Products, named portions and calculated orders are separate. See source reports for category limits and withheld records.')
    (ROOT/'docs/flagship-release-2026-10-18/integration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return registry,markets
