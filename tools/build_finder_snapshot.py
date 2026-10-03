"""Build the visible default finder from the same verified data and shared engine.

No browser dependency or separate recommendation formula. JavaScript then applies
the visitor's URL and local saved state to this usable, source-linked baseline.
"""
from pathlib import Path
from html import escape
import subprocess,json
from normalize_calculator_layouts import Document
ROOT=Path(__file__).resolve().parents[1]
def build():
 script="const fs=require('fs'),vm=require('vm'),s={window:{}};vm.createContext(s);for(const f of ['meal-data','meal-provenance','meal-engine'])vm.runInContext(fs.readFileSync('js/'+f+'.js','utf8'),s);const E=s.window.GetMacrosMeals;const all=s.window.GM_MEALS;console.log(JSON.stringify({all,matches:E.results(all,E.normalize({},all))}));"
 result=subprocess.run(['node','-e',script],cwd=ROOT,capture_output=True,check=True,encoding='utf-8');data=json.loads(result.stdout)
 text=(ROOT/'tools/market-home-finder.inc').read_text(encoding='utf-8');doc=Document(text);grid=next(n for n in doc.nodes if 'results-grid' in n['attrs'].get('class','').split())
 def num(v,u=''):return f'{v:,}'+(' '+u if u else '') if isinstance(v,(int,float)) else 'Not verified'
 def row(m):
  e=lambda k:escape(str(m.get(k,'')),quote=True)
  ident=data['all'].index(m)
  return f'''<article class="order-ticket meal-row" data-meal-id="{ident}"><header class="order-identity"><a href="{e('url')}"><span>{e('chain')}</span></a><button type="button" data-save="{ident}" aria-pressed="false">Save meal</button></header><div class="order-heading"><h2>{escape(m['name'].replace('High-protein bulking order: ',''))}</h2><p>{e('serving')} · U.S. menu</p></div><dl class="order-nutrition meal-numbers"><div class="order-major"><dt>Calories</dt><dd>{num(m.get('cal'))}</dd></div><div class="order-major"><dt>Protein</dt><dd>{num(m.get('p'),'g')}</dd></div><div><dt>Carbs</dt><dd>{num(m.get('c'),'g')}</dd></div><div><dt>Fat</dt><dd>{num(m.get('fat'),'g')}</dd></div></dl><div class="order-included"><p>{e('why')}</p></div><footer class="order-actions"><details><summary>Details &amp; source</summary><p>Fiber: {num(m.get('f'),'g')} · Sodium: {num(m.get('na'),'mg')}.</p><p>Unverified values are not zero.</p><a href="{e('source')}">Official nutrition source</a> · Source inspected {e('checked')}.<p>{e('notes')}</p><a href="{e('url')}">Restaurant menu</a></details><label class="compare-choice"><input type="checkbox" data-compare="{ident}">Compare meal</label></footer></article>'''
 def snapshot(count):
  output=text[:grid['inner']]+''.join(row(m) for m in data['matches'][:count])+text[grid['close']:]
  import re
  output=re.sub(r'(<p class="results-count"[^>]*>).*?</p>',r'\g<1>'+str(len(data['matches']))+' meals match</p>',output)
  return output
 return snapshot(4),snapshot(12)
if __name__=='__main__':
 home,full=build();print('Default snapshot:',len(home),'home bytes;',len(full),'finder bytes')
