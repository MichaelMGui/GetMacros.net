"""Import the real 2026 Canadian reference file, never a fake branded catalogue."""
from pathlib import Path
from collections import defaultdict, Counter
import csv, hashlib, io, json, zipfile
from import_branded_foods import ROOT, RAW, DATE, NUTRIENTS, finite, publish, dump, hash_value

OUT=ROOT/'data/branded-foods/cnf'
MAP={'cal':'208','p':'203','c':'205','fat':'204','f':'291','na':'307','sugar':'269','sat':'606','chol':'601','calcium':'301','iron':'303','magnesium':'304','phosphorus':'305','potassium':'306','zinc':'309','selenium':'317','vitaminC':'401','thiamin':'404','riboflavin':'405','niacin':'406','vitaminB6':'415','folate':'417','folateDFE':'435','vitaminB12':'418','vitaminA':'320','vitaminD':'328','vitaminE':'323','vitaminK':'430','monoFat':'645','polyFat':'646'}
UNIT={'Gram':'g','Milligram':'mg','Microgram':'µg','kilocalorie':'kcal'}

def rows(archive,name):return csv.DictReader(io.TextIOWrapper(archive.open(name),encoding='utf-8-sig',newline=''))
def number(value):
    try:n=float(value)
    except (ValueError,TypeError):return None
    return n if finite(n) else None

def run():
    path=RAW/'cnf-2026.zip';sha=hashlib.file_digest(path.open('rb'),'sha256').hexdigest();records=[]
    with zipfile.ZipFile(path) as z:
        foods={r['Food_Code']:r for r in rows(z,'Food_Name.csv')}
        names={r['Nutrient_Code']:r for r in rows(z,'Nutrient_Name.csv')}
        sources={r['Nutrient_Source_Code']:r['Nutrient_Source_Description_EN'] for r in rows(z,'Nutrient_Source.csv')}
        food_sources={r['Food_Source_Code']:r['Food_Source_Description_EN'] for r in rows(z,'Food_Source.csv')}
        groups={r['CNF_Food_Group_Code']:r['CNF_Food_Group_Description_EN'] for r in rows(z,'CNF_Food_Group.csv')}
        measures={r['Measure_Code']:r['Measure_Description_and_Unit_EN'] for r in rows(z,'Measure_Name.csv')}
        values=defaultdict(dict);portions=defaultdict(list)
        relevant=set(MAP.values())
        for r in rows(z,'Nutrient_Amount.csv'):
            if r['Nutrient_Code'] in relevant:values[r['Food_Code']][r['Nutrient_Code']]=r
        for r in rows(z,'Measure_Weight_Conversion.csv'):
            # 2026 publishes direct gram weights; refuse/yield measures are not edible portions.
            gram=number(r['Measure_Weight_Conversion'])
            if r['Measure_Type_Code']=='6' and gram and r['Measure_Code'] in measures:
                portions[r['Food_Code']].append({'id':'cnf-measure:'+r['Measure_Code'],'label':measures[r['Measure_Code']],'grams':gram,'sourceUpdated':r['Measure_Weight_Conversion_Last_Updated_Date']})
        for code,food in foods.items():
            nutrients={};provenance={}
            for k,ncode in MAP.items():
                assert UNIT.get(names[ncode]['Nutrient_Unit'])==NUTRIENTS[k][1],f'Unexpected units for {k}'
                row=values[code].get(ncode);value=number(row['Nutrient_Amount']) if row else None;nutrients[k]=value
                if value is not None:provenance[k]={'nutrientCode':ncode,'method':sources.get(row['Nutrient_Source_Code'],'Source-reported'),'sourceCode':row['Nutrient_Source_Code'],'updatedAt':row['Nutrient_Last_Updated_Date']}
            if not any(nutrients[k] is not None for k in ['cal','p','c','fat']):continue
            record={'id':'cnf:'+code,'name':food['Food_Description_EN'],'nameFr':food['Food_Description_FR'],'aliases':[food['Alternate_Description_EN']],
                    'type':'reference','category':groups.get(food['CNF_Food_Group_Code'],'Other foods'),'market':'CA-reference','markets':['CA-reference'],'language':'en','brand':None,'barcode':None,
                    'sourceId':'health-canada-cnf-2026','sourceOrigin':'Health Canada — Canadian Nutrient File','sourceRef':code,'sourceRelease':'2026 reference edition',
                    'sourceUrl':'https://open.canada.ca/data/en/dataset/1b6139bd-ed7e-4043-bc28-ff00e10f3109','sourcePublished':'2026','sourceModified':food['Food_Last_Updated_Date'],
                    'sourceChecked':None,'retrievedAt':DATE,'status':'reference-source-imported','basis':{'amount':100,'unit':'g'},'nutrients':nutrients,'portions':portions[code],
                    'provenance':provenance,'foodProvenance':food_sources.get(food['Food_Source_Code']),'flags':['Canadian reference profile; not a current branded package or exact restaurant dish.'],
                    'note':food['Comment_EN'],'license':'Open Government Licence - Canada','formulation':None}
            if nutrients['sugar'] is not None and nutrients['c'] is not None and nutrients['sugar']>nutrients['c']+1:record['flags'].append('Source total sugars exceed carbohydrate; source methods or rounding may differ.')
            record['version']=hash_value(record);records.append(record)
    source={'id':'health-canada-cnf-2026','name':'Health Canada — Canadian Nutrient File 2026','edition':'2026','url':'https://open.canada.ca/data/en/dataset/1b6139bd-ed7e-4043-bc28-ff00e10f3109',
            'downloadUrl':'https://open.canada.ca/data/dataset/1b6139bd-ed7e-4043-bc28-ff00e10f3109/resource/019f2a90-e3a9-489d-b6e1-f74f4ba1d006/download/cnf_fcen_all-files-data_2026.zip',
            'sha256':sha,'license':'Open Government Licence - Canada','licenseUrl':'https://open.canada.ca/en/open-government-licence-canada','retrievedAt':DATE,
            'attribution':'Contains information licensed under the Open Government Licence – Canada. Canadian Nutrient File, Health Canada, 2026.',
            'quality':'Reference composition from mixed analytical, label, calculated and imputed sources; individual nutrient provenance retained. Not brand-level inventory.'}
    manifest=publish(records,output=OUT,source=source)
    dump(ROOT/'docs/master-release-2026-10-12/cnf-import.json',{'sourceRows':len(foods),'published':len(records),'sourceSha256':sha,'bytes':sum(p.stat().st_size for p in OUT.rglob('*.json')),'version':manifest['version'],'measureRule':'2026 measure weights are direct grams; 2015 conversion factor multiplication is not used.'})
    print('Imported',len(records),'real Canadian reference profiles; not counted as branded groceries.')
if __name__=='__main__':run()
