from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
root=Path(__file__).resolve().parents[1]/'docs/cozy-redesign-2026-10-03/final'
groups={
 'tools':['calculators','nutrition-label-comparison-tool','recipe-macro-scaler','protein-value-calculator','budget-meal-builder','sodium-label-comparison-tool','carbohydrate-label-portion-tool','weight-goal-timeline-calculator','sweat-rate-calculator'],
 'reading':['chipotle-healthy-meals-macros','restaurant-meal-guides','protein-density-fast-food','how-to-read-a-nutrition-label','articles','blog','sources','privacy','contact','404'],
}
for group,names in groups.items():
 for theme,appearance in [('light','fresh'),('dark','harvest')]:
  for width in [390,1440]:
   sheet=Image.new('RGB',(280*3,570*((len(names)+2)//3)),'#e8e8e2');draw=ImageDraw.Draw(sheet)
   for i,name in enumerate(names):
    image=Image.open(root/f'{name}.html-{theme}-{appearance}-{width}.png').convert('RGB')
    # Actual screenshot crops; thumbnails do not substitute for full-page QA.
    if width==390:image=image.crop((0,0,width,min(image.height,2300)))
    else:image=image.crop((0,0,width,min(image.height,2200)))
    image.thumbnail((268,540));x=(i%3)*280;y=(i//3)*570
    sheet.paste(image,(x+(280-image.width)//2,y+25));draw.text((x+5,y+7),name[:33],fill='#111')
   sheet.save(root/f'review-{group}-{theme}-{width}.jpg',quality=88)
