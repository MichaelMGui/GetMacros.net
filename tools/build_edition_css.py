from pathlib import Path
root=Path(__file__).resolve().parents[1]
def build():
 (root/'css/publication.css').write_text('\n'.join((root/'tools'/name).read_text(encoding='utf-8') for name in ['market-content.css','companion-system.css','food-characters.css','release-product.css']),encoding='utf-8')
if __name__=='__main__':build()
