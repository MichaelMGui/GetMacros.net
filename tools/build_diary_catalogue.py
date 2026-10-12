"""Make existing source foods discoverable without duplicating nutrient records."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
GROUPS=[
('eggs-dairy','Eggs, milk & yogurt',['Eggs and omelets','Yogurt, Greek','Yogurt, regular','Cheese','Cottage/ricotta cheese','Dairy and Egg Products','Milk, whole','Milk, reduced fat','Milk, lowfat','Milk, nonfat','Plant-based yogurt']),
('bread-cereal','Bread, oats & breakfast',['Oatmeal','Bagels and English muffins','Yeast breads','Pancakes, waffles, French toast','Breakfast Cereals','Grits and other cooked cereals','Biscuits, muffins, quick breads','Egg/breakfast sandwiches','Ready-to-eat cereal, lower sugar (=<21.2g/100g)','Ready-to-eat cereal, higher sugar (>21.2g/100g)']),
('grains-potatoes','Rice, pasta & potatoes',['Rice','Pasta, noodles, cooked grains','Cereal Grains and Pasta','White potatoes, baked or boiled','Mashed potatoes and white potato mixtures','Tortillas','Rolls and buns','Corn']),
('protein','Chicken, meat & seafood',['Chicken, whole pieces','Turkey, duck, other poultry','Fish','Shellfish','Ground beef','Beef, excludes ground','Pork','Poultry Products','Finfish and Shellfish Products','Beef Products','Pork Products']),
('plant-protein','Beans & plant proteins',['Beans, peas, legumes','Soy and meat-alternative products','Legumes and Legume Products','Bean, pea, legume dishes','Vegetable sandwiches/burgers']),
('fruit','Fruit',['Bananas','Apples','Blueberries and other berries','Strawberries','Grapes','Citrus fruits','Melons','Mango and papaya','Pineapple','Peaches and nectarines','Pears','Dried fruits','Other fruits and fruit salads','Fruits and Fruit Juices']),
('vegetables','Vegetables',['Broccoli','Carrots','Tomatoes','Spinach','String beans','Cabbage','Lettuce and lettuce salads','Onions','Other dark green vegetables','Other red and orange vegetables','Other starchy vegetables','Other vegetables and combinations','Vegetables and Vegetable Products']),
('dishes','Meals, soups & sandwiches',['Soups, broth-based','Soups, cream-based','Ramen and Asian broth-based soups','Egg rolls, dumplings, sushi','Burritos and tacos','Rice mixed dishes','Pasta mixed dishes, excludes macaroni and cheese','Poultry mixed dishes','Meat mixed dishes','Seafood mixed dishes','Vegetable dishes','Cheese sandwiches','Deli and cured meat sandwiches','Other Mexican mixed dishes','Fried rice and lo/chow mein','Pizza','Meals, Entrees, and Side Dishes']),
('snacks','Snacks & chocolate',['Popcorn','Crackers, excludes saltines','Saltine crackers','Pretzels/snack mix','Potato chips','Tortilla, corn, other chips','Cookies and brownies','Candy containing chocolate','Candy not containing chocolate','Cereal bars','Nutrition bars','Ice cream and frozen dairy desserts','Gelatins, ices, sorbets','Snacks','Sweets']),
('nuts','Nuts, seeds & nut butter',['Nuts and seeds','Nut and Seed Products']),
('drinks','Drinks',['Coffee','Tea','Tap water','Bottled water','Plant-based milk','Apple juice','Citrus juice','Other fruit juice','Smoothies and grain drinks','Soft drinks','Diet soft drinks','Flavored or carbonated water','Milk shakes and other dairy drinks','Vegetable juice']),
('sauces','Oils, sauces & extras',['Salad dressings and vegetable oils','Fats and Oils','Butter and animal fats','Mayonnaise','Mustard and other condiments','Tomato-based condiments','Pasta sauces, tomato-based','Dips, gravies, other sauces','Soy-based condiments','Olives, pickles, pickled vegetables','Spices and Herbs','Sugars and honey','Jams, syrups, toppings']),
]
# Source IDs, not invented nutrient profiles. Keep familiar ingredients near the top.
PINS={
 'eggs-dairy':['fdc:173424','fdc:171287','fdc:330137','fdc:746782'],
 'bread-cereal':['fdc:2708381','fdc:2346396','fdc:2346397','fdc:172688'],
 'grains-potatoes':['fdc:168878','fdc:169704','fdc:170112','fdc:2346401'],
 'protein':['fdc:171477','fdc:2646170'],
 'plant-protein':['fdc:173735','fdc:175254','fdc:172475'],
 'fruit':['fdc:173944','fdc:2346409'],
 'vegetables':['fdc:747447','fdc:170393','fdc:321360'],
 'snacks':['fdc:170273','fdc:2708219'],
 'nuts':['fdc:170567'],
 'drinks':['fdc:2710707','fdc:171890'],
 'sauces':['fdc:171413','fdc:2710186'],
}

def category(row):
    """Route coarse source categories by explicit food names where necessary."""
    name=row['name'].casefold()
    if row['category']=='Cereal Grains and Pasta' and name.startswith('oats,'):return 'Oatmeal'
    if row['category']=='Fruits and Fruit Juices' and 'juice' in name:return 'Other fruit juice'
    if row['category']=='Legumes and Legume Products' and name.startswith('peanut butter'):return 'Nuts and seeds'
    if row['category']=='Vegetables and Vegetable Products' and name.startswith(('potatoes,','sweet potato')):return 'White potatoes, baked or boiled'
    if row['category']=='Baked Products':
        if name.startswith(('bread,','bagels,','bagel,','rolls,','english muffins','tortillas,')):return 'Yeast breads'
        return 'Cookies and brownies' if name.startswith(('cookies,','crackers,','cake,','doughnuts,','pie,','pastries,')) else 'Biscuits, muffins, quick breads'
    if row['category']=='Beverages':return 'Other fruit juice'
    return row['category']
def build():
    index=json.loads((ROOT/'data/food-library/index.json').read_text())
    manifest=json.loads((ROOT/'data/food-library/manifest.json').read_text())
    by_category=defaultdict(list)
    excluded=re.compile(r'mcdonald|burger king|wendy|starbucks|chick-fil|kfc|taco bell|subway|panda express|panera|popeye|gerber|baby food|infant|formula|sustain|ensure|boost plus|\bNFS\b|\bNS as to\b|,\s*NS\b',re.I)
    for row in index:
        if excluded.search(row['name']) or len(row['name'])>170:continue
        by_category[category(row)].append(row)
    rank={'foundation':0,'legacy':1,'prepared':2}
    for rows in by_category.values():
        rows.sort(key=lambda row:(rank[row['type']],len(row['name']),row['name']))
    seen_names=set();groups=[]
    eligible={r['id']:r for rows in by_category.values() for r in rows}
    for key,title,categories in GROUPS:
        rows=[];pools=[iter(by_category[c]) for c in categories]
        for food_id in PINS.get(key,[]):
            row=eligible.get(food_id)
            if not row or category(row) not in categories:raise ValueError('Pinned food is not in its source group: '+food_id)
            normalized=re.sub(r'\W+',' ',row['name'].casefold()).strip()
            if normalized not in seen_names:
                seen_names.add(normalized);rows.append({k:row[k] for k in ['id','name','type','shard']})
        while pools:
            remaining=[]
            for pool in pools:
                for row in pool:
                    normalized=re.sub(r'\W+',' ',row['name'].casefold()).strip()
                    if normalized not in seen_names:
                        seen_names.add(normalized)
                        rows.append({k:row[k] for k in ['id','name','type','shard']})
                        break
                else:continue
                remaining.append(pool)
            pools=remaining
        groups.append({'id':key,'name':title,'foods':rows})
    payload={'schemaVersion':1,'libraryVersion':manifest['libraryVersion'],'scope':'Shared food-composition references for every country; not local restaurant or packaged-product formulations. Prepared dishes are source reference recipes.','groups':groups,'foodCount':sum(len(g['foods']) for g in groups)}
    data=(json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n').encode()
    digest=hashlib.sha256(data).hexdigest()[:12]
    path=ROOT/f'data/food-library/diary-foods-{digest}.json'
    path.write_bytes(data)
    # Remove only obsolete outputs of this generator, inside its fixed directory.
    for old in (ROOT/'data/food-library').glob('diary-foods-*.json'):
        if old!=path and re.fullmatch(r'diary-foods-[a-f0-9]{12}\.json',old.name):old.unlink()
    print('Shared diary browse catalogue:',payload['foodCount'],'source foods in',len(groups),'groups;',len(data),'bytes.')
    return '/'+path.relative_to(ROOT).as_posix()
if __name__=='__main__':build()
