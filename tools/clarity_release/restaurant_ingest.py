"""Pin reviewed local restaurant facts without mutating the shared registry.

Builds are offline. Retrieval, source-edition review and arithmetic are different
events; none implies that a location's entire current menu was audited.
"""
from pathlib import Path
import copy
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
FIELDS = ("cal", "p", "c", "fat", "f", "na", "sugar", "sat")
CORE = ("cal", "p", "c", "fat")
UNITS = {key: "kcal" if key == "cal" else "mg" if key == "na" else "g" for key in FIELDS}


def quantity(value):
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise ValueError("Boolean is not a nutrient quantity")
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise ValueError("Nutrient quantities must be finite and nonnegative")
    return number


def total(parts, field):
    """One unknown component leaves the order's corresponding total unknown."""
    values = [part.get(field) for part in parts]
    return sum(values) if values and all(v is not None for v in values) else None


def identity(name, serving):
    return "CA|triple-os|" + hashlib.sha256((name + "|" + serving).encode()).hexdigest()[:16]


def validate(record):
    if record.get("market") != "CA" or record.get("country") != "CA":
        raise ValueError("Cross-market record")
    for field in FIELDS:
        quantity(record.get(field))
    if record.get("cal") is not None and all(record.get(k) is not None for k in ("p", "c", "fat")):
        # This only gates substantial contradictions. Food factors and rounding
        # are not a license to replace a restaurant's reported energy figure.
        approximate = 4 * (record["p"] + record["c"]) + 9 * record["fat"]
        if abs(approximate - record["cal"]) > max(35, record["cal"] * 0.20):
            raise ValueError("Energy/macros need review: " + record["name"])
    for subset, whole in (("sat", "fat"), ("sugar", "c"), ("f", "c")):
        if record.get(subset) is not None and record.get(whole) is not None and record[subset] > record[whole] + 1:
            raise ValueError("Contradictory nutrients: " + record["name"])
    if record["finderSupported"] != (record["category"] not in ("component", "sauce") and all(record.get(k) is not None for k in CORE)):
        raise ValueError("Incorrect finder eligibility")


def build(facts=None):
    facts = facts or json.loads((OUT / "restaurant_facts.json").read_text(encoding="utf-8"))
    if facts["market"] != "CA" or facts["restaurantId"] != "triple-os":
        raise ValueError("Wrong local source")
    records = []
    for cells in facts["rows"]:
        if len(cells) != len(facts["columns"]):
            raise ValueError("Misaligned source cells")
        row = dict(zip(facts["columns"], cells))
        grams = quantity(row["grams"])
        serving = row["sourceServing"] + " · " + format(grams, "g") + " g"
        nutrients = {field: quantity(row.get(field)) for field in FIELDS}
        source_variant = row["modification"] == "without sauce"
        note = ("Named serving from the currently linked Canadian guide, edition June 2025. "
                "Tracked selection, not a full current-menu audit or location availability guarantee.")
        if source_variant:
            note += " Without Sauce is a separately published source row, not a GetMacros subtraction."
        if row["category"] == "sauce":
            note += " This is one named dip portion, not a complete meal or an assumed included sauce."
        record = {
            "id": identity(row["name"], serving), "chain": "Triple O’s",
            "restaurantId": "triple-os", "restaurantMarketId": "CA|triple-os",
            "name": row["name"], "market": "CA", "country": "CA", "region": "CA",
            "language": "en", "serving": serving, "servingGrams": grams,
            "sourceServing": row["sourceServing"], "sourceServingGrams": grams,
            "sourceItem": row["name"].removesuffix(" - Without Sauce"),
            "sourceModification": row["modification"], "category": row["category"],
            "meal": row["meal"], "size": "", "diet": [], "t": [], "components": [],
            "ingredients": None, "ingredientCompleteness": "not-sourced", **nutrients,
            "source": facts["source"], "sourceParent": facts["sourceParent"],
            "sourceDate": facts["sourceDate"], "sourceDatePrecision": "month",
            "sourceDateProvenance": facts["sourceDateProvenance"],
            "retrievedAt": facts["retrievedAt"], "checked": facts["verifiedAt"],
            "sourcePage": int(row["sourcePage"]), "sourceHash": facts["sourceHash"],
            "sourceVersion": facts["sourceHash"], "verificationStatus": "official-table-reviewed",
            "nativeNutrients": {k: row.get(k) for k in FIELDS}, "units": UNITS.copy(),
            "nutrientBasis": "per named serving", "conversions": [], "notes": note,
            "url": "/ca/en/restaurants/triple-os/",
            "macroComplete": all(nutrients[k] is not None for k in CORE),
            "finderSupported": all(nutrients[k] is not None for k in CORE) and row["category"] not in ("component", "sauce"),
            "nutrientProvenance": {
                field: {"method": "official published serving", "source": facts["source"],
                        "page": int(row["sourcePage"]), "edition": facts["sourceDate"],
                        "verifiedAt": facts["verifiedAt"]}
                for field, value in nutrients.items() if value is not None
            },
            "additionalNutrients": {
                "chol": {"value": quantity(row.get("chol")), "unit": "mg", "method": "official published serving"},
                "trans": {"value": quantity(row.get("trans")), "unit": "g", "method": "official published serving"},
            },
        }
        validate(record)
        records.append(record)
    by_name = {r["name"]: r for r in records}
    for order in facts["calculatedOrders"]:
        parts = [by_name[name] for name in order["parts"]]
        if any(part["market"] != "CA" for part in parts):
            raise ValueError("Cross-market calculation")
        serving = order["description"]
        record = copy.deepcopy(parts[0])
        record.update({
            "id": identity(order["name"], serving), "name": order["name"],
            "meal": order["meal"], "category": "entree", "serving": serving,
            "servingGrams": sum(part["servingGrams"] for part in parts),
            "sourceServing": None, "sourceServingGrams": None,
            "sourceItem": None, "sourceModification": None, "sourcePage": None,
            "verificationStatus": "calculated-from-official-components", "nativeNutrients": None,
            "calculatedFrom": [{"id": part["id"], "quantity": 1} for part in parts],
            "calculation": "Sum of one of each explicitly named local source serving.",
            "components": [{"item": part["name"], "quantity": 1, "recordId": part["id"],
                            "serving": part["serving"]} for part in parts],
            "notes": "GetMacros adds the source values for these exact servings. This is a calculated order, not a separately published restaurant combo. " + order["description"],
            **{field: total(parts, field) for field in FIELDS},
        })
        record["additionalNutrients"] = {
            key: {"value": total([part["additionalNutrients"][key] for part in parts], "value"),
                  "unit": unit, "method": "sum of official component values"}
            for key, unit in (("chol", "mg"), ("trans", "g"))
        }
        record["macroComplete"] = all(record[k] is not None for k in CORE)
        record["finderSupported"] = record["macroComplete"]
        record["nutrientProvenance"] = {
            field: {"method": "sum of official component values", "source": facts["source"],
                    "edition": facts["sourceDate"], "verifiedAt": facts["verifiedAt"],
                    "componentIds": [part["id"] for part in parts]}
            for field in FIELDS if record[field] is not None
        }
        validate(record)
        records.append(record)
    for record in records:
        for tag, field, threshold, direction in (("protein", "p", 25, 1), ("energy", "cal", 600, 1),
                ("light", "cal", 400, -1), ("fibre", "f", 5, 1), ("lowsodium", "na", 600, -1)):
            if record[field] is not None and direction * record[field] >= direction * threshold:
                record["t"].append(tag)
    if len({r["id"] for r in records}) != len(records):
        raise ValueError("Duplicate source identities")
    finder = sum(r["finderSupported"] for r in records)
    presence = {
        "id": "CA|triple-os", "country": "CA", "restaurantBrand": "Triple O’s",
        "restaurantId": "triple-os", "localOperatingEntity": "White Spot Limited",
        "officialCountryWebsite": "https://www.tripleos.com/", "localMenuSource": facts["sourceParent"],
        "presence": {"status": "confirmed", "evidenceUrl": "https://www.tripleos.com/locations/",
                     "evidenceType": "current official local restaurant directory",
                     "checkedAt": facts["verifiedAt"],
                     "observation": "Expanded official directory lists locations in Alberta, British Columbia and Ontario. Airport and venue menus may differ."},
        "nutritionSources": [facts["source"]], "nutritionAvailable": True,
        "nutritionSourceStatus": "reviewed-selection", "finderSupported": finder > 0,
        "trackedRecords": len(records), "completeMacroRecords": sum(r["macroComplete"] for r in records),
        "finderRecords": finder, "calculatedOrders": len(facts["calculatedOrders"]),
        "caloriesOnlyRecords": 0, "partialMacroRecords": 0,
        "coverageStatus": "tracked-macro-selection", "lastCheckedDate": facts["verifiedAt"],
        "sourceRetrievalIsVerification": False,
        "limitations": "Selected named Canadian servings from the currently linked June 2025 source edition. No complete current-menu, inventory or allergen-safety claim. Contradictory source rows are withheld."}
    return {
        "schemaVersion": 1, "checkedAt": facts["verifiedAt"], "records": records,
        "counts": {"newRecords": len(records), "officialServingRecords": len(facts["rows"]),
                   "calculatedOrders": len(facts["calculatedOrders"]),
                   "components": sum(r["category"] in ("component", "sauce") for r in records),
                   "finderRecords": finder, "newRestaurants": 1, "groceryRecordsAdded": 0},
        "source": {key: facts[key] for key in ("source", "sourceParent", "sourceHash", "sourceDate", "sourceDatePrecision", "rights", "limits")},
        "presenceRelationships": [presence],
        "guide": {"route": "/ca/en/restaurants/triple-os/", "market": "CA",
                  "title": "Triple O’s Canada nutrition: breakfast, chicken, sides & exact orders",
                  "description": "Compare named Canadian Triple O’s servings, printed without-sauce variants and three calculated orders, with native gram weights and a clear source trail.",
                  "h1": "Triple O’s Canada nutrition.",
                  "firstAction": "Choose the named serving or compare a complete order.",
                  "sections": ["Breakfast and its exact sauce variants", "Chicken, fish and side portions", "Three explicitly calculated orders", "Coffee and small milkshakes", "Source edition and limitations"],
                  "sourceEditionText": "June 2025", "sourceCheckedText": "October 14, 2026"},
        "withheld": facts["withheld"],
    }


if __name__ == "__main__":
    result = build()
    (OUT / "restaurant_additions.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"]))
