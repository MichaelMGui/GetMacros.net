"""Reproducible extraction candidates. These are NOT publication approval."""
from pathlib import Path
import re,json
BASE=Path(__file__).resolve().parent
SPECS={'arbys':(12,dict(cal=1,fat=3,na=7,c=8,f=9,p=11),0),'del-taco':(11,dict(cal=1,fat=2,na=6,c=7,f=8,p=10),0),'sonic':(10,dict(cal=0,fat=1,na=5,c=6,f=7,p=9),None),'culvers':(10,dict(cal=0,fat=1,na=5,c=6,f=7,p=9),None),'taco-johns':(10,dict(cal=0,fat=1,na=5,c=6,f=7,p=9),None),'qdoba':(13,dict(cal=1,fat=3,c=7,f=8,p=10,na=11),0),'el-pollo-loco':(12,dict(cal=1,fat=3,na=7,c=8,f=9,p=11),0),'noodles':(12,dict(cal=0,fat=2,na=6,c=7,f=9,p=11),None)}
NUMBER=r'(?:<\s*)?\d+(?:\.\d+)?g?'
def extract():
 result={}
 for id,(count,columns,portion) in SPECS.items():
  rows=[];page=0
  for line in (BASE/'sources'/f'{id}.txt').read_text(encoding='utf8').splitlines():
   if line.startswith('PAGE '):page=int(line.split()[1]);continue
   line=re.sub(r'<\s+(\d)',r'<\1',line).strip()
   # Remove allergen markers after data. Never expose this as allergen safety.
   line=re.sub(r'\s+(?:[•X]|[A-Z]{2,})[\s•XA-Z*]*$','',line)
   if id=='raising-canes':continue
   pattern=r'^(.*?)\s+('+r'\s+'.join([f'({NUMBER})']*count)+r')$'
   match=None if id=='noodles' else re.match(pattern,line)
   if not match and id=='noodles':
    # Paired regular/small columns. Retain only the regular published portion.
    pair=re.match(r'^(.*?)\s+('+r'\s+'.join([f'({NUMBER})']*24)+r')$',line)
    if pair: match=pair
    else:match=re.match(pattern,line)
   if not match:continue
   tokens=re.findall(NUMBER,match[2]);name=match[1].strip()
   if id=='noodles' and len(tokens)==24:tokens=tokens[::2]
   if id=='arbys':name=name.split(' Contains:')[0].split(' May Contain:')[0]
   if id=='qdoba':name=re.sub(r'\s+(?:-|[A-Z*]+)$','',name)
   if id=='del-taco':name=re.sub(r'^(TACOS|BURRITOS|QUESADILLAS|BURGERS|BREAKFAST|FIESTA PACKS)\s+','',name)
   values={key:(None if tokens[index].startswith('<') else float(tokens[index].rstrip('g'))) for key,index in columns.items()}
   if values['cal']<70 or not name or values['p'] is None:continue
   qualifiers={key:tokens[index] for key,index in columns.items() if tokens[index].startswith('<')}
   rows.append({'sourceId':id,'page':page,'sourceRow':line,'name':name,'portion':tokens[portion] if portion is not None else None,'values':values,'qualifiers':qualifiers})
  result[id]=rows
 (BASE/'extracted-candidates.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 for key,rows in result.items():print(key,len(rows),' | '.join(r['name'] for r in rows[:4]))
if __name__=='__main__':extract()
