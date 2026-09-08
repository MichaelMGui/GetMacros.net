"""Final deterministic metadata and tool repairs after legacy generation."""
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1]
for path in ROOT.glob('*.html'):
    text=path.read_text(encoding='utf-8')
    text=re.sub(r'(<meta name="theme-color" content=")[^"]+',r'\g<1>#f6f4ec',text)
    # Build breadcrumbs from the visible navigation rather than stale removed hubs.
    def repair(match):
        try: data=json.loads(match.group(1))
        except ValueError: return match.group(0)
        if data.get('@type')!='BreadcrumbList': return match.group(0)
        items=data.get('itemListElement',[])
        for item in items:
            url=item.get('item','')
            if not url.startswith('https://getmacros.net/'):continue
            target=url.split('https://getmacros.net/',1)[1].split('#')[0]
            if target and not (ROOT/target).exists():
                item['item']='https://getmacros.net/articles.html';item['name']='Nutrition guides'
        if 'calculator' in path.name or path.name in ['recipe-macro-scaler.html','nutrition-label-comparison-tool.html','sodium-label-comparison-tool.html','carbohydrate-label-portion-tool.html','budget-meal-builder.html']:
            if len(items)>2:items[1]['item']='https://getmacros.net/calculators.html';items[1]['name']='Calculators'
        return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False)+'</script>'
    text=re.sub(r'<script type="application/ld\+json">(.*?)</script>',repair,text,flags=re.S)
    if path.name=='protein-value-calculator.html':
        text=re.sub(r'<script>const ids=\["ap".*?</script>','<script src="js/protein-value.js" defer></script>',text,flags=re.S)
    if path.name=='budget-meal-builder.html':
        text=re.sub(r'<script>\s*\(function\(\)\{const form=document.getElementById\("builder"\).*?</script>','<script src="js/budget-builder.js" defer></script>',text,flags=re.S)
    if 'calculator' in path.name or path.name in ['recipe-macro-scaler.html','nutrition-label-comparison-tool.html','sodium-label-comparison-tool.html','carbohydrate-label-portion-tool.html','budget-meal-builder.html']:
        text=re.sub(r'<nav class="breadcrumb".*?</nav>',lambda m:m.group(0).replace('<a href="articles.html">Articles</a>','<a href="calculators.html">Calculators</a>'),text,flags=re.S)
    text=re.sub(r'<link rel="stylesheet" href="css/tide\.css(?:\?[^"]*)?">','',text)
    if path.name=='index.html':
        text=re.sub(r'<link rel="stylesheet" href="css/home-extension\.css(?:\?[^"]*)?">','',text)
        text=text.replace('</head>','<link rel="stylesheet" href="css/home-extension.css"></head>',1)
    text=text.replace('</head>','<link rel="stylesheet" href="css/tide.css"></head>',1)
    # Search is regenerated after asset injection; keep the final motion layer
    # here as well so every route receives exactly one copy after any rebuild.
    text=re.sub(r'<link rel="stylesheet" href="css/tide-motion\.css(?:\?[^"]*)?">','',text)
    text=re.sub(r'<script[^>]*src="js/tide-motion\.js(?:\?[^"]*)?"[^>]*>\s*</script>','',text)
    text=text.replace('</head>','<link rel="stylesheet" href="css/tide-motion.css"></head>',1)
    text=text.replace('</body>','<script src="js/tide-motion.js" defer></script></body>',1)
    path.write_text(text,encoding='utf-8')
