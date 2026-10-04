from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
def build():
 css='\n'.join((root/'tools'/name).read_text(encoding='utf-8') for name in ['market-content.css','food-design.css','food-characters.css','release-product.css'])
 css=re.sub(r'/\*.*?\*/','',css,flags=re.S)
 css=re.sub(r'\s+',' ',css)
 css=re.sub(r'\s*([{}:;,])\s*',r'\1',css)
 (root/'css/publication.css').write_text(css.strip(),encoding='utf-8')
if __name__=='__main__':build()
