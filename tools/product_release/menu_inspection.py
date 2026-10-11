from pathlib import Path
import json
import pdfplumber
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs/global-product-release-2026-10-11/sources'
class Tables(HTMLParser):
    def __init__(self):
        super().__init__();self.tables=[];self.table=None;self.row=None;self.cell=None;self.href=None
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='table':self.table=[]
        if tag=='tr' and self.table is not None:self.row=[]
        if tag in ('td','th') and self.row is not None:self.cell=[];self.href=None
        if tag=='a' and self.cell is not None:self.href=attrs.get('href')
    def handle_data(self,data):
        if self.cell is not None:self.cell.append(data)
    def handle_endtag(self,tag):
        if tag in ('td','th') and self.cell is not None:
            self.row.append({'text':' '.join(''.join(self.cell).split()),'href':self.href});self.cell=None
        if tag=='tr' and self.row is not None:self.table.append(self.row);self.row=None
        if tag=='table' and self.table is not None:self.tables.append(self.table);self.table=None

for name in ['greggs','gyg','subway-mexico','mcdonalds-india']:
    source=D/(name+'.pdf')
    if not source.exists():continue
    pages=[]
    with pdfplumber.open(source) as pdf:
        for i,p in enumerate(pdf.pages):
            text=p.extract_text() or ''
            pages.append({'page':i+1,'text':text,'tables':p.extract_tables()})
            print(name,'page',i+1,'first text',text[:180].replace('\n',' / '),'tables',len(pages[-1]['tables']))
            if (name=='gyg' and i in [5,6,7,8]) or name=='subway-mexico':p.to_image(resolution=120).save(D/(name+'-'+str(i+1)+'.png'))
    (D/(name+'-extracted.json')).write_text(json.dumps(pages,ensure_ascii=False),encoding='utf-8')
    print(name,'sample',str(pages[0]['tables'])[:900])
p=Tables();p.feed((D/'mcdonalds-japan.html').read_text(encoding='utf-8'))
(D/'mcdonalds-japan-tables.json').write_text(json.dumps(p.tables,ensure_ascii=False),encoding='utf-8')
print('JAPAN tables',len(p.tables),'first',str(p.tables[0])[:2000])
