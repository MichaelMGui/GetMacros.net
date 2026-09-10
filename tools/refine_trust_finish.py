"""Serve neutral original restaurant markers and remove unverified image references."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
MARKS={'chipotle':'CH','chick-fil-a':'CF','cava':'CA','sweetgreen':'SG','subway':'SU','panera':'PA','starbucks':'SB','mcdonalds':'MC','wendys':'WE','taco-bell':'TB','panda-express':'PE','kfc':'KF','popeyes':'PO','jersey-mikes':'JM','dunkin':'DU'}
def run():
 out=ROOT/'images/restaurant-marks';out.mkdir(exist_ok=True)
 for i,(slug,initials) in enumerate(MARKS.items()):
  bg,ink=[('#e3edd8','#355b36'),('#e1edf2','#305d70'),('#f4e5ce','#805328')][i%3]
  (out/(slug+'.svg')).write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="20" fill="'+bg+'"/><text x="32" y="40" text-anchor="middle" font-family="Arial,sans-serif" font-weight="700" font-size="24" fill="'+ink+'">'+initials+'</text></svg>',encoding='utf-8')
 for p in ROOT.glob('*.html'):
  original=p.read_text(encoding='utf-8');s=re.sub(r'images/restaurant-logos/([a-z-]+)\.png',r'images/restaurant-marks/\1.svg',original)
  s=s.replace('images/editorial-recipe-portions.webp','images/meal-plate.svg')
  if s!=original:p.write_text(s,encoding='utf-8')
 p=ROOT/'js/meal-quiz.js';original=p.read_text(encoding='utf-8');s=original.replace('"images/restaurant-logos/" + slug + ".png"','"images/restaurant-marks/" + slug + ".svg"')
 if s!=original:p.write_text(s,encoding='utf-8')
if __name__=='__main__':run()
