"""Read source-separated JSON partitions in either legacy or gzip storage."""
from pathlib import Path
import gzip,json

def source_path(path):
    path=Path(path)
    if path.is_file():return path
    packed=Path(str(path)+'.gz')
    if packed.is_file():return packed
    raise FileNotFoundError(path)

def read_json(path):
    path=source_path(path)
    if path.suffix=='.gz':
        with gzip.open(path,'rt',encoding='utf-8') as file:return json.load(file)
    with path.open(encoding='utf-8') as file:return json.load(file)

def write_json(path,value,compressed=False):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n').encode('utf-8')
    if compressed:
        path=Path(str(path)+'.gz') if path.suffix!='.gz' else path
        with path.open('wb') as raw:
            with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0,compresslevel=6) as file:file.write(data)
    else:path.write_bytes(data)
    return path

def records(partition):
    partition=Path(partition);manifest=read_json(partition/'manifest.json')
    for shard in manifest['recordShards']:
        yield from read_json(partition/'records'/(shard+'.json'))
