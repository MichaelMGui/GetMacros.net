"""Render the first quiz question at build time from the runtime's shared config."""
from pathlib import Path
import html,json,re
from normalize_calculator_layouts import Document

ROOT=Path(__file__).resolve().parents[1]

def first_question():
 js=(ROOT/'js/meal-quiz.js').read_text(encoding='utf-8')
 config=json.loads(re.search(r'var FIRST_STEP = (\{.*?\});',js)[1])
 thresholds=dict((k,int(v)) for k,v in re.findall(r'(\w+):(\d+)',re.search(r'window.GM_THRESHOLDS = (\{.*?\});',(ROOT/'js/meal-data.js').read_text(encoding='utf-8'))[1]))
 paths=dict(re.findall(r"(\w+): '([^']*)'",js.split('var paths = {',1)[1].split('\n    };',1)[0]))
 options=[('',*config['none'])]+config['options']
 cards=[]
 for value,title,hint,icon in options:
  attr='data-facet="goal"' if value else 'data-any="goal"'
  cards.append('<label class="quiz-option'+('' if value else ' quiz-option-any')+'"><input type="checkbox" name="q-goal" '+attr+' value="'+value+'"><span class="option-icon"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'+paths[icon]+'</svg></span><span class="option-copy"><b>'+html.escape(title)+'</b>'+('<small>'+html.escape(hint.format(**thresholds))+'</small>' if hint else '')+'</span><span class="option-check" aria-hidden="true">✓</span></label>')
 return '<div class="quiz-card"><div class="quiz-progress-row"><span>Question 1 of 5</span></div><div class="quiz-progress"><span style="width:20%"></span></div><h2 tabindex="-1">'+config['title']+'</h2><p class="quiz-hint">'+config['hint']+'</p><div class="quiz-options step-goal">'+''.join(cards)+'</div><div class="quiz-nav"><button type="button" class="btn btn-primary quiz-continue" data-go="1">Continue</button></div></div>'

BOOT='''<script data-quiz-bootstrap>(function(){
var root=document.getElementById('meal-quiz'),pending=false,timer;
function notice(text){var p=root.querySelector('.quiz-load-note');if(!p){p=document.createElement('p');p.className='quiz-load-note';p.setAttribute('role','status');root.firstElementChild.append(p);}p.textContent=text;}
function earlyChange(event){var input=event.target;if(!input.matches('input'))return;if(input.hasAttribute('data-any')){root.querySelectorAll('[data-facet]').forEach(function(i){i.checked=false;});}else{var any=root.querySelector('[data-any]');if(any)any.checked=false;}}
function earlyClick(event){var button=event.target.closest('[data-go]');if(!button||root.dataset.ready==='true')return;event.preventDefault();pending=true;notice('Opening the next question…');clearTimeout(timer);timer=setTimeout(function(){notice('Taking longer than usual. You can also browse all meals below.');},10000);}
root.addEventListener('change',earlyChange);root.addEventListener('click',earlyClick);
window.GM_QUIZ_BOOT={finish:function(){clearTimeout(timer);root.removeEventListener('change',earlyChange);root.removeEventListener('click',earlyClick);var note=root.querySelector('.quiz-load-note');if(note)note.remove();if(pending){var next=root.querySelector('[data-go="1"]');if(next)next.click();}}};
if(['goal','size','diet','meal','chain'].some(function(k){return new URLSearchParams(location.search).has(k);})){root.removeAttribute('data-first-question');root.innerHTML='<div class="quiz-card"><h2>Your meal matches</h2><p role="status">Finding meals for your choices…</p></div>';}
})();</script>'''

def run():
 p=ROOT/'restaurant-meal-finder.html';s=p.read_text(encoding='utf-8')
 s=re.sub(r'<script data-quiz-bootstrap>.*?</script>','',s,flags=re.S)
 s=re.sub(r'<noscript data-quiz-fallback>.*?</noscript>','',s,flags=re.S)
 doc=Document(s);node=next(n for n in doc.nodes if n['attrs'].get('id')=='meal-quiz')
 fallback='<noscript data-quiz-fallback><style>#meal-quiz{display:none}</style><p>JavaScript is off. You can still <a class="btn action-link" href="#browse-meals">Browse all meals</a>.</p></noscript>'
 s=s[:node['start']]+'<div id="meal-quiz" data-first-question>'+first_question()+'</div>'+BOOT+fallback+s[node['end']:]
 # Discover and fetch essential quiz code while the browser parses the header.
 scripts=re.findall(r'<script src="js/meal-(?:data|quiz)\.js[^\"]*"[^>]*></script>',s)
 for script in scripts:s=s.replace(script,'')
 # Earlier generators may preserve an old head while adding body scripts.
 # Emit each dependency once, in data-before-controller order.
 scripts=[next(tag for tag in scripts if 'js/meal-'+name+'.js' in tag) for name in ('data','quiz')]
 s=re.sub(r'<link[^>]*data-quiz-preload[^>]*>','',s)
 head=''.join('<link rel="preload" as="script" href="'+re.search(r'src="([^\"]+)"',tag)[1]+'" fetchpriority="high" data-quiz-preload>'+tag for tag in scripts)
 s=s.replace('</head>',head+'</head>')
 s=s.replace('Choose cutting, bulking, high protein and dietary goals to get ranked fast-food meals from 15 chains, with complete calories, protein, fiber and sodium.','Choose your goals and food preferences to compare fast-food meals from 15 restaurant chains.')
 p.write_text(s,encoding='utf-8')

if __name__=='__main__':run()
