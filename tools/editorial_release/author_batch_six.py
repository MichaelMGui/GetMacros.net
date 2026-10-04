"""Intent-review replacements: existing resources are not counted twice."""
from author_batch_five import *
rows[:]=[r for r in rows if r['slug'] not in ('calculator-estimate-not-shared-personal-input.html','protein-value-usable-yield-break-even.html')]

add('calculator-height-feet-inches-not-decimal','5 feet 10 inches is not 5.10 feet','Convert compound height correctly before using an estimate.','Calculator notes','Prevent decimal-foot interpretation of a feet-and-inches height in calorie calculator inputs.','Original compound-unit conversion, round-trip and input-mode verification.', '''Five feet ten inches means five whole feet plus ten inches. It does not mean 5.10 decimal feet. Entering the latter as a decimal number changes the height substantially and can make a calculator estimate look inconsistent for a reason unrelated to its formula.

## Convert the compound measurement

There are 12 inches per foot. Five feet ten inches is 5 × 12 + 10 = 70 inches. Using NIST’s exact 2.54 cm per inch conversion, that is 177.8 cm. Keep the whole feet and remaining inches separate until this conversion is complete.

By contrast, 5.10 feet is 5.1 × 12 = 61.2 inches, or 155.448 cm. The decimal fraction 0.10 of a foot is 1.2 inches, not ten inches. The two interpretations differ by about 22.4 cm.

## Match the calculator’s field

If it requests total inches, enter 70 for this example. If it requests centimetres, enter 177.8 at an appropriate supported precision. If a tool supplies separate feet and inches fields, use 5 and 10. Never put 5.10 into a field labeled total inches or centimetres.

## A useful reverse check

Seventy inches contains five groups of 12, with ten left over. This returns the original five feet ten inches and helps catch a conversion error before you calculate. A unit selector changes how the number is interpreted; it does not make a wrongly encoded compound measurement correct.

The height is an arithmetic example, not personal data or a prescription. Keep the existing formula intact and correct the input basis first when investigating a surprising energy estimate. Changing assumptions or rounding cannot repair a height entered in the wrong unit.''',src=(CONVERT,CAL),tool='calculators.html',tool_label='Check the height unit before calculating',scope='The height values demonstrate a unit conversion only. They are not the inputs or energy requirements of an actual person.',checks=[['5*12+10',70],['70*2.54',177.8],['5.1*12',61.2],['61.2*2.54',155.448],['177.8-155.448',22.352]])

analysis('protein-value-price-range-overlap','When uncertain prices prevent a confident protein-value ranking','A range is more honest than choosing a convenient unverified price.','Compare cost-per-protein intervals for two real orders under explicitly hypothetical price ranges.',[160,170],'''If a food price is uncertain, a single cost-per-protein ranking may not be supported. You can calculate the range of possible ratios and see whether the conclusion survives the uncertainty. The example price intervals here are invented, not verified Culver’s prices.

## Calculate both ends

Culver’s Single ButterBurger lists 20 g protein. Suppose its food-only price could be between $4 and $6. Its ratio ranges from $0.20 to $0.30 per gram. Grilled Chicken Sandwich lists 36 g; an invented $7–$9 range gives about $0.194 to $0.25 per gram.

The intervals overlap. At a $4 burger and $9 chicken sandwich, the burger has the lower ratio: $0.20 versus $0.25. At a $6 burger and $7 chicken sandwich, the chicken sandwich has the lower ratio: $0.30 versus about $0.194. A confident universal winner would hide the unverified price inputs.

## Ask what would settle it

Current matching food-only checkout prices collapse the ranges to concrete ratios. A combo, discount or delivery total requires a compatible nutrition and price boundary instead. Do not treat a plausible regional price range as a live menu survey.

## Preserve the rest of the decision

Protein value is not total cash required, taste or a health score. The restaurant’s published source supplies standard-order protein, not prices or a promise about the next kitchen portion. Its older Culver’s edition remains labeled. When necessary evidence is missing, show the range or leave the ranking undecided; uncertainty does not need to be filled with a made-up number.''',category='Budget and value',checks=[['4/20',.2],['6/20',.3],['7/36',7/36],['9/36',.25]])

if __name__=='__main__':write()
