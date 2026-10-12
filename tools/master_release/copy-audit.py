"""Report repeated public main-content copy, excluding shared shell and numeric rows."""
from pathlib import Path
from html import unescape
from collections import defaultdict
import json,re
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[2]
class Text(HTMLParser):
    def __init__(self):super().__init__();self.main=False;self.skip=0;self.block=None;self.parts=[];self.blocks=[]
    def handle_starttag(self,tag,attrs):
        if tag=='main':self.main=True
        if not self.main:return
        if tag in ['script','style','table']:self.skip+=1
        if not self.skip and tag in ['p','h1','h2','h3']:
            self.block=tag;self.parts=[]
    def handle_data(self,data):
        if self.main and self.block and not self.skip:self.parts.append(data)
    def handle_endtag(self,tag):
        if self.block==tag:
            value=re.sub(r'\s+',' ',' '.join(self.parts)).strip()
            if value:self.blocks.append((tag,value))
            self.block=None
        if tag in ['script','style','table'] and self.skip:self.skip-=1
        if tag=='main':self.main=False

paths=list(ROOT.glob('*.html'))+list(ROOT.glob('*/en/**/index.html'))
groups=defaultdict(list);internal=[]
for p in paths:
    parser=Text();parser.feed(p.read_text(encoding='utf-8'))
    for tag,value in parser.blocks:
        if len(value)<70 or len(value)>1400:continue
        normalized=re.sub(r'\s+',' ',value).casefold()
        groups[normalized].append({'route':p.relative_to(ROOT).as_posix(),'element':tag,'text':value})
        if re.search(r'\b(this release|pipeline|implementation|repository|payload|scope expansion)\b',value,re.I):internal.append({'route':p.relative_to(ROOT).as_posix(),'text':value})
report={'date':'2026-10-12','routesChecked':len(paths),'method':'Automated authored main-content paragraphs/headings; excludes navigation and numeric tables. A report is not manual review of every sentence.','repeatedBlocks':sorted([v for v in groups.values() if len({r['route'] for r in v})>1],key=len,reverse=True),'internalLanguageCandidates':internal}
out=ROOT/'docs/master-release-2026-10-12/copy-audit.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Checked',len(paths),'routes;',len(report['repeatedBlocks']),'repeated block groups;',len(internal),'internal-language candidates.')
for group in report['repeatedBlocks'][:5]:print(len(group),'routes:',group[0]['text'][:180])
for item in internal[:8]:print('Review:',item['route'],item['text'][:160])
