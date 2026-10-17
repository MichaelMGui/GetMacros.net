"""Brand research queue reconciled with actual source-attributed market profiles.

These are source-brand text counts, not endorsements, inventory, independent label
verification, or proof that a retailer operates in the country.
"""
from pathlib import Path
import csv,json,re,sys
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/branded-foods/off'
sys.path.insert(0,str(ROOT/'tools'))
from source_json import read_json
PATTERNS={'Kirkland Signature':r'^kirkland(?:$|\s|,|[-•])','Great Value':r'great value',"President\'s Choice":r"president[’']?s?\s+choice",'No Name':r'(?:\bno\s*name\b)','Compliments':r'compliments','Selection':r'^selection(?:$|[\s,])','Irresistibles':r'irresistibl','Our Finest':r'our finest','Western Family':r'western family',"Nature’s Emporium":r"nature[’']?s?\s+emporium","Trader Joe’s":r'trader joe','Good & Gather':r'good\s*&?\s*gather','Market Pantry':r'market pantry','365 by Whole Foods':r'365','Simple Truth':r'simple truth','Kroger':r'kroger',"Member’s Mark":r"member[’']?s?\s+mark",'Signature Select':r'signature select','Oreo':r'oreo','Erewhon':r'erewhon'}
def run():
    path=ROOT/'docs/master-completion-2026-10-13/grocery-brand-coverage.csv'
    with path.open('w',encoding='utf-8',newline='') as file:
        writer=csv.writer(file);writer.writerow(['market','requested_brand','source','market_label_profiles','matched_source_brand_variants','status','limitations'])
        for market in ['CA','US']:
            counts=read_json(OUT/'brands'/(market+'.json'))
            for brand,pattern in PATTERNS.items():
                matches={name:count for name,count in counts.items() if re.search(pattern,name,re.I)}
                writer.writerow([market,brand,'Open Food Facts',sum(matches.values()),'; '.join(matches),'community-label-imported' if matches else 'no-qualifying-source-records','Source brand text match, not independently checked current package; no inventory or endorsement claim'])
    print('Reconciled',path)
if __name__=='__main__':run()
