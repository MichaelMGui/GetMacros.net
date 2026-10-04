"""Static and interactive meals share exactly the same presentation."""
from pathlib import Path
import subprocess,json
ROOT=Path(__file__).resolve().parents[1]
def build():
 script="""const fs=require('fs'),vm=require('vm'),s={window:{}};vm.createContext(s);for(const f of ['meal-data','meal-provenance','meal-engine','meal-view'])vm.runInContext(fs.readFileSync('js/'+f+'.js','utf8'),s);const E=s.window.GetMacrosMeals,V=s.window.GetMacrosMealView,all=s.window.GM_MEALS,state=E.normalize({},all),matches=E.results(all,state);const featured=['Chick-fil-A','Chipotle','CAVA','Panda Express'].map(chain=>matches.find(m=>m.chain===chain)).filter(Boolean);console.log(JSON.stringify([featured.map(m=>V.card(m,all.indexOf(m),{home:true})).join(''),V.shell(all,state,E,{rows:matches.slice(0,12).map(m=>V.card(m,all.indexOf(m))).join(''),count:matches.length})]));"""
 return json.loads(subprocess.run(['node','-e',script],cwd=ROOT,capture_output=True,check=True,encoding='utf-8').stdout)
if __name__=='__main__':
 home,full=build();print('Shared meal markup:',len(home),len(full))
