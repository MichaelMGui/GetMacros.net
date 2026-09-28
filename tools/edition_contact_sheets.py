from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]/'docs/redesign/reset/families'
for theme in ['light','dark']:
 for width in [390,1440]:
  files=sorted(root.glob('*-'+theme+'-'+str(width)+'.png'))
  for batch in range(0,len(files),6):
   sheet=Image.new('RGB',(1440,1160),'#ddd');d=ImageDraw.Draw(sheet)
   for i,p in enumerate(files[batch:batch+6]):
    im=Image.open(p);im.thumbnail((470,530));x=(i%3)*480;y=(i//3)*580;sheet.paste(im,(x,y+30));d.text((x+4,y+5),p.name,fill='black')
   sheet.save(root/f'sheet-{theme}-{width}-{batch//6}.jpg')
