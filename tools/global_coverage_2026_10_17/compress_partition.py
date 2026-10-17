"""Compress generator-owned grocery shards without changing a source fact or ID."""
from pathlib import Path
import argparse,gzip,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser();parser.add_argument('partition',choices=['usda','off','cnf','retailer-ca']);args=parser.parse_args()
base=(ROOT/'data/branded-foods'/args.partition).resolve();assert base.is_relative_to((ROOT/'data/branded-foods').resolve())
before=after=count=0
for kind in ['records','index','tokens','barcodes','markets','brands']:
    directory=base/kind
    if not directory.is_dir():continue
    for file in sorted(directory.glob('*.json')):
        assert file.resolve().is_relative_to(base)
        data=file.read_bytes();packed=Path(str(file)+'.gz')
        with packed.open('wb') as raw:
            with gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0,compresslevel=6) as stream:stream.write(data)
        assert gzip.decompress(packed.read_bytes())==data
        before+=len(data);after+=packed.stat().st_size;count+=1
        file.unlink()
        if count%1500==0:print(args.partition,count,'shards',flush=True)
manifest_path=base/'manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'));manifest['jsonEncoding']='gzip';manifest['storagePolicy']='On-demand gzip JSON shards; source IDs, values, units and licenses remain unchanged.';manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
report={'partition':args.partition,'compressedShards':count,'previousBytes':before,'compressedBytes':after,'savedBytes':before-after,'profileCount':manifest['profileCount'],'factChanges':0}
out=ROOT/'docs/global-coverage-2026-10-17';out.mkdir(parents=True,exist_ok=True);(out/('compression-'+args.partition+'.json')).write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report),flush=True)
