"""Explicit reviewed dispositions, never HTTP-success-based presence inference."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs/flagship-release-2026-10-18/markets'
batch=json.loads((ROOT/'tools/flagship_release/markets_release_records.json').read_text(encoding='utf-8'))
rows=[]
def add(m,b,u,note,site=None,menu=None,status='confirmed',gaps=None):
    rows.append({'market':m,'chain':b,'presenceStatus':status,'evidenceUrl':u,'officialMarketWebsite':site or u,'localMenuEvidence':menu or u,
      'checkedAt':'2026-10-18','observation':note,'disposition':'retain country-specific source coverage; resolve remaining source gaps' if status=='confirmed' else 'record announcement separately; do not substitute U.S. nutrition',
      'unresolvedGaps':gaps or 'Source-scoped coverage only; not every branch or the entire live menu.'})
for r in batch['presenceUpserts']:
    add(r['country'],r['restaurantBrand'],r['presence']['evidenceUrl'],r['presence']['observation'],r['officialCountryWebsite'],r['localMenuSource'])
extra=[
('US','Five Guys','https://restaurants.fiveguys.com/','Official directory identifies all Five Guys restaurants in the United States, with state location links.'),
('US','Tim Hortons','https://locations.timhortons.com/en/','Official directory lists current U.S. states; this operating evidence does not supply verified U.S. nutrition.'),
('US','Jollibee','https://www.jollibeefoods.com/pages/locations','Official Jollibee USA restaurant directory and U.S. menu; no Canadian inference.'),
('US','Papa Johns','https://locations.papajohns.com/','Official location directory separately links United States and Canada.'),
('CA','Chick-fil-A','https://www.chick-fil-a.ca/locations','Official Canadian locations and country nutrition reviewed; official FAQ explicitly says Canadian restaurants do not serve breakfast.'),
('CA','Shake Shack','https://shakeshack.ca/locations','Official CANADIAN LOCATIONS page gives Toronto Union Station and other Canadian addresses. Menu existence is distinct from numeric nutrition, which remains unavailable in captured pages.'),
('CA','Tim Hortons','https://locations.timhortons.ca/en/','Official Canadian directory lists provinces and territories; not a claim that every menu item is available at every branch.'),
('MX','Wendy’s','https://www.wendys.com.mx/','Official Wendy’s México page includes local menu and Encuentra un Wendy’s links. No U.S. nutrient substitution.'),
('MX','Popeyes','https://popeyes.com.mx/','Official Mexico menu explicitly names CDMX, MTY, MEX and Guadalajara. Numeric local nutrient source remains unresolved.'),
('MX','Starbucks','https://www.starbucks.com.mx/menu/bebidas/calientes','38 exact named-size calorie-only hot drinks across11 products are staged from current official Mexican category; separate Latte page agrees. Protein, carbs, fat, fibre, sodium and sugar remain unknown; no complete-macro claim or foreign-market substitution.'),
('MX','Papa Johns','https://www.papajohns.com.mx/','Current official Papa Johns México site provides local menu and ordering. This is operating/menu evidence, not a verified numeric nutrient table.'),
('GB','Taco Bell','https://www.tacobell.co.uk/locations','Official UK locations directory reviewed. Local availability remains branch-specific.'),
('GB','Five Guys','https://restaurants.fiveguys.co.uk/','Official directory identifies United Kingdom restaurants and regions.'),
('GB','Shake Shack','https://www.shakeshack.co.uk/locations','Official UK location directory gives current UK locations, not countrywide availability.'),
('GB','Chick-fil-A','https://www.chick-fil-a.co.uk/locations/','Official UK directory lists Kingston, Leeds, Lisburn South, Liverpool and Templepatrick. Northern Ireland belongs in UK scope. Hamilton Palace Grounds Scotland opening is announced for October29, 2026 and is future as of this review; not counted as open.'),
('IE','Wendy’s','https://wendys.ie/','Official Irish site explicitly says Now open in Tullamore Retail Park. This is not a UK/NI presence inference.'),
('IE','Five Guys','https://www.fiveguys.ie/','Official Irish menu and Locations site for Republic of Ireland reviewed; no UK nutrient equivalence inferred.'),
('IE','Papa Johns','https://www.papajohns.ie/','Official Papa John’s Ireland restaurant site includes Food Menu, Locations and Irish ordering links.'),
('AU','Burger King','https://www.hungryjacks.com.au/','Australian local brand is Hungry Jack’s. Keep its identity and source records separate; do not label U.S. Burger King nutrition as Australian.'),
('AU','Starbucks','https://www.starbucks.com.au/','Current official Starbucks Australia menu and store-finder site; numeric nutrition coverage remains a separate review.'),
('AU','Taco Bell','https://www.tacobell.com.au/','Current official Australian Taco Bell menu and restaurant-finder content reviewed.'),
('AU','Five Guys','https://fiveguys.com.au/','Official Australian menu/locations resource reviewed; no overseas portion substitution.'),
('NZ','Starbucks','https://www.starbucks.co.nz/','Official New Zealand menu lists local beverages and food, with country-specific menu navigation.'),
('NZ','Taco Bell','https://tacobell.co.nz/','Official Taco Bell NZ menu and Find a Taco Bell destination; no Australian/U.S. numeric equivalence assumed.'),
('JP','Wendy’s','https://wendys-firstkitchen.co.jp/','Official Wendy’s First Kitchen Japanese operating identity and SHOP/menu links; do not equate its menu to U.S. Wendy’s.'),
('JP','Subway','https://www.subway.co.jp/','Official Japanese Subway menu and dated 2026 local announcements reviewed.'),
('JP','Domino’s','https://www.dominos.jp/','Official Japanese menu and 店舗/location selection with Japan-specific ordering; no AU/NZ/IN menu copied.'),
('JP','Shake Shack','https://shakeshack.jp/','Official Japanese site provides LOCATIONS 店舗一覧 and FOOD & DRINK; not proof that every global product is available.'),
('FR','Domino’s','https://www.dominos.fr/','Official French menu and restaurant navigation reviewed; numeric French serving source remains a separate task.'),
('FR','Five Guys','https://restaurants.fiveguys.fr/','Official restaurant directory explicitly identifies France and local locations.'),
('FR','Chipotle','https://www.chipotle.fr/','Official French menu with NOS RESTOS and ordering links; do not equate French builds to Canadian component weights.'),
('SG','McDonald’s','https://www.mcdonalds.com.sg/','Current official Singapore menu covers breakfast, mains, McCafé and sides; country nutrients require their own evidence.'),
('SG','Popeyes','https://www.popeyes.com.sg/','Official Popeyes Singapore site includes local offers, menu and locations.'),
('SG','Domino’s','https://www.dominos.com.sg/','Official page explicitly offers pizza delivery/pickup in Singapore and Locate Us.'),
('SG','Starbucks','https://www.starbucks.com.sg/','Official Starbucks Singapore menu and Find a Store reviewed.'),
('SG','Five Guys','https://fiveguys.sg/','Official Singapore Five Guys menu/locations resource reviewed; not a U.S. formula claim.'),
('SG','Shake Shack','https://shakeshack.com.sg/','Official Shake Shack Singapore site has local menu and locations.'),
('SG','Chick-fil-A','https://www.chick-fil-a.com.sg/locations/','Official directory gives Bugis+ (201 Victoria Street) and Millenia Walk (9 Raffles Boulevard) addresses/hours. Source November2025 nutrition guide does not cover every2026 addition.'),
('SG','Tim Hortons','https://timhortons.sg/','Official site explicitly says brewing in Singapore with Restaurants and local menu links.'),
('SG','Jollibee','https://jollibee.com.sg/','Current official Jollibee Singapore menu/location site reviewed.'),
('ZA','Burger King','https://www.burgerking.co.za/frequently-asked-questions','Official South African FAQ confirms local operation and points to nutrition explorer. Both current and legacy public nutrition views failed to expose usable numeric rows in fresh browser sessions.'),
('ZA','Starbucks','https://www.starbucks.co.za/','Current official South African Starbucks menu/store resource reviewed; no foreign nutrient substitution.'),
('ZA','Nando’s','https://www.nandos.co.za/eat/order/menu','Official South African menu rendered and public country dataset captured. Its declared CALORIES/GRAMS units contradict plausible per-serving figures; all65 nutrient-bearing definitions withheld pending explicit unit clarification.'),
('IE','Zizzi','https://www.zizzi.co.uk/italian-restaurants/ireland/dublin','Official Dublin location page names Dundrum, Liffey Valley and Suffolk Street; explicit ROI/Belfast guide separately reviewed, not a UK-only menu inference.')]
for m,b,u,n in extra:add(m,b,u,n)
add('MX','Chipotle','https://ir.chipotle.com/2026-07-13-CHIPOTLE-ENTERS-MEXICO-WITH-FIRST-RESTAURANT-IN-NUEVO-LEON',
    'July13, 2026 official announcement says first Nuevo León opening planned July16 in San Pedro Garza García. This supersedes blanket no-Mexico assumptions but the captured announcement alone does not independently reconfirm operation on October18.',
    status='announced-opening-past-date-not-reconfirmed',gaps='Current local operating follow-up and Mexican nutrient/portion source not established; no U.S. substitutions.')
# Later explicit operating evidence replaces a duplicate nutrition-only row.
unique={(r['market'],r['chain']):r for r in rows}
(D/'presence-reviewed.json').write_text(json.dumps(list(unique.values()),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Explicit reviewed current dispositions:',len(unique))
