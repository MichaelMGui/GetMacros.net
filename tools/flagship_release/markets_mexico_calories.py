"""Source-reviewed Mexican calories-only servings; no macro inference/import."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,unittest
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs/flagship-release-2026-10-18/markets'
TARGET=Path(__file__).with_suffix('.json')
DATE='2026-10-18'
def version(r):return hashlib.sha256(json.dumps(r,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
def read_page(file):
    source=(D/'sources'/file).read_text(encoding='utf-8')
    script=re.search(r'<script\b[^>]*\bid=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',source,re.S)
    if not script:raise ValueError('Official page has no captured product data')
    return json.loads(script[1])['props']['pageProps']
def build():
    capture=D/'sources/starbucks-mx-hot.html';sha=hashlib.sha256(capture.read_bytes()).hexdigest()
    url='https://www.starbucks.com.mx/menu/bebidas/calientes';data=read_page(capture.name)
    rows=[];excluded=[]
    for p in data['products']:
        parsed=re.findall(r'(Corto|Alto|Grande|Venti):\s*(\d+(?:\.\d+)?)\s*kcal',p['subtitle'])
        if not parsed:
            excluded.append({'sourceProductId':p['id'],'name':p['title'],'sourceSubtitle':p['subtitle'],'sourceItemUrl':'https://www.starbucks.com.mx'+p['url'],'reason':'No explicit named size parsed; not among the38 reviewed size-specific records.'})
        for size,text in parsed:
            r={'id':'MX|starbucks|calories-'+p['id']+'-'+size.lower(),'chain':'Starbucks','restaurantId':'starbucks','restaurantMarketId':'MX|starbucks',
               'market':'MX','country':'MX','region':'MX','language':'es','name':p['title']+' — '+size,'size':size,
               'serving':'1 '+size+' drink · published Mexican menu recipe','sourceServing':size,'servingGrams':None,
               'category':'drink','meal':'main','diet':[],'components':[],
               'cal':float(text),'p':None,'c':None,'fat':None,'f':None,'na':None,'sugar':None,'sat':None,
               'nativeNutrients':{'cal':float(text),'p':None,'c':None,'fat':None,'f':None,'na':None,'sugar':None,'sat':None},
               'units':{'cal':'kcal','p':'g','c':'g','fat':'g','f':'g','na':'mg','sugar':'g','sat':'g'},
               'source':url,'sourceItemUrl':'https://www.starbucks.com.mx'+p['url'],'sourceProductId':p['id'],'sourceProductFamily':p['id'],
               'sourceSubtitle':p['subtitle'],'sourcePage':'hot-drinks/product/'+p['id']+'/size/'+size,
               'sourceDate':None,'retrievedAt':DATE,'checked':DATE,'sourceHash':sha,
               'sourceCaptureMethod':'official rendered Mexican hot-drinks category and public embedded product text',
               'sourceGroup':'Bebidas calientes','sourceGroups':['Bebidas calientes'],'nutrientBasis':'per named default Mexican drink size',
               'verificationStatus':'official-calories-only-reviewed','coverageStatus':'calories-only','macroComplete':False,
               'finderSupported':True,'finderEligibility':'incomplete-data browsing only; macro limits must reject unknown nutrients',
               'conversions':[],'t':[],'url':'/mx/en/restaurants/starbucks/',
               'nutrientProvenance':{'cal':{'method':'official published named-size calories only','source':url,'sourceProductId':p['id'],'size':size,'verifiedAt':DATE,'edition':None}},
               'notes':'Calories only. Protein, carbs and fat are not published here. Standard Mexican menu drink; customizations and serving volume are not inferred.'}
            r['sourceVersion']=version(r);rows.append(r)
    source={'id':'starbucks-mx-hot-calories','marketScope':'MX','chain':'Starbucks','file':capture.relative_to(ROOT).as_posix(),'url':url,'sha256':sha,
       'retrievedAt':DATE,'verifiedAt':DATE,'sourceEdition':None,'captureMethod':'official public rendered category with embedded product subtitles','retrievalIsVerification':False,
       'coverage':'38 explicitly named-size calorie entries across11 products in the captured13-product hot-drinks category. Two unsized espresso products withheld.',
       'limitations':'Calories-only source, not complete macros or whole menu. Source zero is retained as reported kcal, never translated into zero protein/carbohydrate/fat. No volume, custom milk/syrup effects, local availability or image rights inferred.'}
    latte=D/'sources/starbucks-mx-latte.html'
    item_source={'id':'starbucks-mx-latte-check','marketScope':'MX','chain':'Starbucks','file':latte.relative_to(ROOT).as_posix(),'url':'https://www.starbucks.com.mx/producto/latte','sha256':hashlib.sha256(latte.read_bytes()).hexdigest(),
       'retrievedAt':DATE,'verifiedAt':DATE,'sourceEdition':None,'captureMethod':'official individual item page checked against category subtitles','retrievalIsVerification':False,
       'coverage':'Independent Latte product-page match: Alto120kcal, Grande150kcal, Venti200kcal.','limitations':'No complete nutrient panel, size volume or customization nutrient effects supplied.'}
    presence={'id':'MX|starbucks','country':'MX','restaurantBrand':'Starbucks','restaurantId':'starbucks','localOperatingEntity':None,
       'officialCountryWebsite':'https://www.starbucks.com.mx/','localMenuSource':url,
       'presence':{'status':'confirmed','evidenceUrl':url,'evidenceType':'official country-specific current menu','observation':'Official Mexican Starbucks site publishes country menu products and named-size calories. This does not establish every branch or complete macros.','checkedAt':DATE},
       'nutritionSources':[url,item_source['url']],'lastCheckedDate':DATE,'coverageStatus':'calories-only-selection','nutritionAvailable':True,
       'nutritionSourceStatus':'reviewed-calories-only-selection','finderSupported':True,'trackedRecords':38,'completeMacroRecords':0,'partialMacroRecords':38,'caloriesOnlyRecords':38,'finderRecords':38,'calculatedOrders':0,
       'sourceRetrievalIsVerification':False,'guideUrl':'/mx/en/restaurants/starbucks/',
       'limitations':'38 named-size calorie-only hot-drink servings. Macro-constrained results cannot treat unknown protein, carbohydrate, fat, fibre, sugar or sodium as zero. Default Mexican recipes only; not every live menu item or location.'}
    out={'schemaVersion':1,'reviewedAt':DATE,'records':rows,'updates':[],'withdrawnIds':[],'presenceUpserts':[presence],'sources':[source,item_source],
       'counts':{'newCalorieOnlyPortionRecords':38,'newMacroCompleteRecords':0,'sourceProductIdentities':11,'sourceReportedZeroKcalSizes':8,'deferredUnsizedProducts':2},
       'scope':'Source-reported calories-only Mexican hot-drink sizes; count separately from macro-complete menu additions. No macros inferred from another country.',
       'excludedSourceProducts':excluded}
    assert len(rows)==38 and len({r['id']for r in rows})==38
    TARGET.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (D/'mexico-calories-source-register.json').write_text(json.dumps(out['sources'],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return out

# Independent literal transcription of all printed sized category subtitles.
EXPECTED={
 'Café del día':{'Corto':0,'Alto':0,'Grande':0,'Venti':0},
 'Espresso Americano':{'Corto':0,'Alto':0,'Grande':0,'Venti':0},
 'Latte Macchiato':{'Corto':120,'Alto':130,'Grande':220,'Venti':300},
 'Flat White':{'Corto':110,'Alto':120,'Grande':170,'Venti':230},
 'Mocha Blanco':{'Alto':240,'Grande':410,'Venti':510},
 'Mocha':{'Alto':240,'Grande':410,'Venti':510},
 'Caramel Macchiato':{'Alto':160,'Grande':200,'Venti':260},
 'Cappuccino':{'Alto':120,'Grande':150,'Venti':190},
 'Latte':{'Alto':120,'Grande':150,'Venti':200},
 'Chocolate Caliente':{'Corto':230,'Alto':320,'Grande':410,'Venti':500},
 'Chocolate Mexicano':{'Alto':243,'Grande':308,'Venti':408}}
class MexicoCaloriesTests(unittest.TestCase):
    def setUp(self):self.b=json.loads(TARGET.read_text(encoding='utf-8'))
    def test_every_source_size(self):
        expected={(name,size):value for name,sizes in EXPECTED.items()for size,value in sizes.items()}
        actual={(r['name'].rsplit(' — ',1)[0],r['size']):r['cal']for r in self.b['records']}
        self.assertEqual(actual,expected);self.assertEqual(len(actual),38)
    def test_known_zero_does_not_create_zero_macros(self):
        rows=self.b['records'];self.assertEqual(sum(r['cal']==0 for r in rows),8)
        for r in rows:
            for k in('p','c','fat','f','na','sugar','sat'):self.assertIsNone(r[k]);self.assertIsNone(r['nativeNutrients'][k])
            self.assertFalse(r['macroComplete']);self.assertEqual(r['coverageStatus'],'calories-only')
    def test_country_portions_units_and_no_customization(self):
        for r in self.b['records']:
            self.assertEqual(r['market'],'MX');self.assertEqual(r['country'],'MX');self.assertTrue(r['id'].startswith('MX|starbucks|'))
            self.assertEqual(r['units']['cal'],'kcal');self.assertIsNone(r['servingGrams']);self.assertNotIn('ml',r['serving'].lower())
            self.assertIn('starbucks.com.mx',r['source']);self.assertIn('starbucks.com.mx',r['sourceItemUrl']);self.assertEqual(r['diet'],[])
    def test_capture_and_versions(self):
        for s in self.b['sources']:
            self.assertEqual(hashlib.sha256((ROOT/s['file']).read_bytes()).hexdigest(),s['sha256']);self.assertFalse(s['retrievalIsVerification'])
        for r in self.b['records']:
            self.assertEqual(r['sourceVersion'],version({k:v for k,v in r.items()if k!='sourceVersion'}));self.assertIsNone(r['sourceDate'])
    def test_independent_latte_page(self):
        p=read_page('starbucks-mx-latte.html')['product']
        self.assertEqual(p['title'],'Latte');self.assertEqual(p['subtitle'].strip(),'Alto: 120 kcal  / Grande: 150 kcal / Venti: 200 kcal')
        self.assertEqual(self.b['presenceUpserts'][0]['completeMacroRecords'],0)
        self.assertEqual(len(self.b['excludedSourceProducts']),2)

if __name__=='__main__':
    import sys
    if'--test'in sys.argv:sys.argv.remove('--test');unittest.main(verbosity=2)
    else:print(json.dumps(build()['counts'],indent=2))
