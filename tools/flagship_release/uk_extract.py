"""Recreate reviewed intermediate extracts from bounded official captures.

This is an explicit research-time command, never imported by the site build.
Requires pdfplumber for PDFs; uses no network. --check compares in memory without
overwriting frozen extraction artifacts. A changed layout still needs review.
"""
from pathlib import Path
import argparse, json, re

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'docs/flagship-release-2026-10-18/uk/sources'
PDFS=['wendys','fiveguys','starbucks-food','starbucks-drinks','zizzi','askitalian','pizzaexpress','tortilla','timhortons','wasabi']

def serialized_stream(text):
    chunks=[]
    for body in re.findall(r'<script\b[^>]*>(.*?)</script>',text,re.S):
        prefix='self.__next_f.push('
        if not body.startswith(prefix):continue
        try:value=json.loads(body[len(prefix):].rstrip(';').removesuffix(')'))
        except json.JSONDecodeError:continue
        if isinstance(value,list) and len(value)>1 and isinstance(value[1],str):chunks.append(value[1])
    return ''.join(chunks)

def leon_extract(text):
    stream=serialized_stream(text);decoder=json.JSONDecoder();items=[]
    for match in re.finditer(r'\{"_id":',stream):
        try:item,_=decoder.raw_decode(stream[match.start():])
        except json.JSONDecodeError:continue
        if isinstance(item,dict) and 'nutritionInfo' in item:items.append(item)
    return stream,items

def nuxt_extract(text):
    match=re.search(r'<script[^>]+id="__NUXT_DATA__"[^>]*>(.*?)</script>',text,re.S)
    if not match:raise ValueError('No public Nuxt data script')
    values=json.loads(match.group(1));cache={}
    def resolve(index):
        if index<0:return 0 if index==-6 else None
        if index in cache:return cache[index]
        value=values[index]
        if isinstance(value,dict):
            result={};cache[index]=result
            result.update({k:resolve(v) for k,v in value.items()});return result
        if isinstance(value,list):
            if value and value[0] in ('ShallowReactive','Reactive','Ref','ShallowRef'):
                result=resolve(value[1]);cache[index]=result;return result
            if value and value[0]=='Set':
                result=[resolve(v) for v in value[1:]];cache[index]=result;return result
            result=[];cache[index]=result
            result.extend(resolve(v) for v in value);return result
        cache[index]=value;return value
    root=resolve(0)
    def find(value):
        if isinstance(value,dict):
            if 'tenkites-menu-menu' in value:return value['tenkites-menu-menu']
            for v in value.values():
                result=find(v)
                if result is not None:return result
        elif isinstance(value,list):
            for v in value:
                result=find(v)
                if result is not None:return result
    menu=find(root['data'])
    if not menu or not menu.get('Menus'):raise ValueError('Public menu missing')
    # Only the menu subtree is emitted, not unrelated request/session state.
    return menu

def emit(name,value,check):
    path=SRC/name
    if check:
        previous=json.loads(path.read_text(encoding='utf-8'))
        if previous!=value:raise ValueError(f'{name}: reconstructed values differ; review before replacing')
    else:path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(('checked ' if check else 'wrote ')+name)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--only',choices=['html','pdf','coordinates'],default=None)
    args=parser.parse_args()
    if args.only in (None,'html'):
        _,items=leon_extract((SRC/'leon.html').read_text(encoding='utf-8'))
        if len(items)!=175:raise ValueError(f'LEON expected175 occurrences, received {len(items)}')
        emit('leon-products.json',items,args.check)
        emit('wagamama-menu.json',nuxt_extract((SRC/'wagamama.html').read_text(encoding='utf-8')),args.check)
    if args.only in (None,'pdf','coordinates'):
        import pdfplumber
        if args.only!='coordinates':
            for stem in PDFS+['chipotle']:
                file=SRC/(stem+'.html' if stem=='chipotle' else stem+'.pdf')
                if not file.read_bytes().startswith(b'%PDF'):raise ValueError(str(file)+' is not a PDF')
                with pdfplumber.open(file) as pdf:
                    pages=[dict(page=i+1,text=page.extract_text(),tables=page.extract_tables()) for i,page in enumerate(pdf.pages)]
                emit(stem+'-extracted.json',pages,args.check)
        if args.only!='pdf':
            with pdfplumber.open(SRC/'starbucks-food.pdf') as pdf:
                coords=[dict(page=i+1,names=page.crop((20,80,116,550)).extract_words(),numbers=page.crop((523,80,728,550)).extract_words()) for i,page in enumerate(pdf.pages) if i>=3]
            emit('starbucks-food-coordinates.json',coords,args.check)

if __name__=='__main__':main()
