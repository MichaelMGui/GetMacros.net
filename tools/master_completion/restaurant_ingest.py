"""Generate pinned, country-scoped records from reviewed official-source facts.

Production never fetches a changing menu. The original two-page Canadian source
was rendered during research; only selected numeric facts are persisted here.
"""
from pathlib import Path
import hashlib, json, math, re

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "tools/master_completion"
DATE = "2026-10-13"
FIELDS = ["cal", "p", "c", "fat", "f", "na", "sugar", "sat"]
CORE = ["cal", "p", "c", "fat"]
UNITS = {k: "kcal" if k == "cal" else "mg" if k == "na" else "g" for k in FIELDS}


def slug(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def quantity(value):
    """Absent fields remain absent; only real nonnegative quantities are valid."""
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise ValueError("A boolean is not a nutrient quantity")
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise ValueError("Invalid nutrient quantity")
    return number


def sum_nutrients(parts):
    return {field: sum(part[field] for part in parts)
            if parts and all(part.get(field) is not None for part in parts) else None
            for field in FIELDS}


def build():
    facts = json.loads((OUT / "restaurant_facts.json").read_text(encoding="utf-8"))
    assert facts["market"] == "CA"
    assert re.fullmatch("[a-f0-9]{64}", facts["sourceHash"])
    records = []
    for cells in facts["rows"]:
        assert len(cells) == len(facts["columns"])
        raw = dict(zip(facts["columns"], cells))
        serving = raw["serving"] + " · " + str(raw["grams"]) + " g"
        identity = hashlib.sha256((raw["name"] + "|" + serving).encode()).hexdigest()[:16]
        nutrients = {key: quantity(raw.get(key)) for key in FIELDS}
        extra = raw["category"] == "component"
        note = ("Canadian guide dated August 20, 2026. Exact named source serving; "
                "no sides, drinks or unspecified condiments are added. "
                "Tracked selection, not the full live menu or a branch-availability guarantee.")
        if extra:
            note = ("Published extra amount for a snack-size poutine. The source says "
                    "regular extras use twice and large extras three times this amount. "
                    "This rule does not scale a whole poutine.")
        record = {
            "id": "CA|new-york-fries|" + identity,
            "chain": "New York Fries", "restaurantId": "new-york-fries",
            "restaurantMarketId": "CA|new-york-fries",
            "name": raw["name"], "market": "CA", "country": "CA", "region": "CA",
            "language": "en", "serving": serving, "servingGrams": raw["grams"],
            "sourceServing": raw["serving"], "sourceServingGrams": raw["grams"],
            "category": raw["category"], "meal": "main", "size": "",
            "diet": [], "t": [], "components": [], **nutrients,
            "source": facts["source"], "sourceParent": facts["sourceParent"],
            "sourceDate": facts["sourceDate"], "sourceDateProvenance": facts["sourceDateProvenance"],
            "retrievedAt": DATE, "checked": DATE, "sourcePage": raw["sourcePage"],
            "sourceHash": facts["sourceHash"], "sourceVersion": facts["sourceHash"],
            "verificationStatus": "official-table-reviewed",
            "nativeNutrients": {k: raw.get(k) for k in FIELDS},
            "nutrientBasis": "per named source serving", "units": UNITS.copy(),
            "conversions": [], "notes": note,
            "url": "/ca/en/restaurants/new-york-fries/",
            "macroComplete": all(nutrients[k] is not None for k in CORE),
            "finderSupported": all(nutrients[k] is not None for k in CORE) and not extra,
            "nutrientProvenance": {
                k: {"method": "official published serving", "source": facts["source"],
                    "page": raw["sourcePage"], "edition": facts["sourceDate"],
                    "verifiedAt": DATE}
                for k, value in nutrients.items() if value is not None
            },
            "additionalNutrients": {
                k: {"value": quantity(raw.get(k)), "unit": "mg",
                    "method": "official published serving"}
                for k in ["chol", "potassium", "calcium", "iron"]
                if quantity(raw.get(k)) is not None
            },
        }
        if extra:
            record.update({
                "builderScope": "CA|new-york-fries|snack-poutine-extra",
                "sourceItem": raw["name"],
                "servingRules": {"snack": 1, "regular": 2, "large": 3,
                                 "appliesTo": "extra ingredient amount only"},
            })
        records.append(record)
    by_name = {row["name"]: row for row in records}
    for name, keys in [
        ("Hot dog with bun + snack fries", ["Hot Dog with Bun", "Fries, Snack"]),
        ("Hot dog with bun + regular fries", ["Hot Dog with Bun", "Fries, Regular"]),
    ]:
        parts = [by_name[key] for key in keys]
        serving = "1 hot dog with bun + 1 " + ("snack" if "snack" in name else "regular") + " fries order"
        identity = hashlib.sha256((name + "|" + serving).encode()).hexdigest()[:16]
        record = parts[0].copy()
        record.update({
            "id": "CA|new-york-fries|" + identity, "name": name, "category": "entree",
            "t": [],
            "serving": serving, "servingGrams": sum(p["servingGrams"] for p in parts),
            "sourceServing": None, "sourceServingGrams": None,
            "verificationStatus": "calculated-from-official-components",
            "nativeNutrients": None,
            "calculatedFrom": [{"id": part["id"], "quantity": 1} for part in parts],
            "calculation": "Sum of one named hot dog and one named fries portion.",
            "components": [{"item": part["name"], "quantity": 1, "recordId": part["id"]} for part in parts],
            "notes": ("GetMacros adds the rounded Canadian source values for these two exact items. "
                      "Drink, dips and extra condiments are excluded. This is a calculated order, "
                      "not a separately published restaurant combo."),
        })
        record.update(sum_nutrients(parts))
        record["additionalNutrients"] = {
            field: {"value": sum(p["additionalNutrients"][field]["value"] for p in parts),
                    "unit": "mg", "method": "sum of official component values"}
            for field in ["chol", "potassium", "calcium", "iron"]
        }
        record["nutrientProvenance"] = {
            k: {"method": "sum of official component values", "source": facts["source"],
                "page": 1, "edition": facts["sourceDate"],
                "componentIds": [part["id"] for part in parts], "verifiedAt": DATE}
            for k in FIELDS
        }
        records.append(record)
    for record in records:
        for tag, field, check in [
            ("protein", "p", lambda n: n >= 25), ("light", "cal", lambda n: n <= 400),
            ("energy", "cal", lambda n: n >= 600), ("fibre", "f", lambda n: n >= 5),
            ("lowsodium", "na", lambda n: n <= 600),
        ]:
            if record[field] is not None and check(record[field]):
                record["t"].append(tag)
    assert len({r["id"] for r in records}) == len(records)
    return {
        "schemaVersion": 1, "checkedAt": DATE, "records": records,
        "counts": {"newRecords": len(records), "officialServingRecords": len(facts["rows"]),
                   "calculatedOrders": 2, "components": sum(r["category"] == "component" for r in records),
                   "finderRecords": sum(r["finderSupported"] for r in records)},
        "source": {k: facts[k] for k in ["source", "sourceParent", "sourceHash", "sourceDate", "rights", "limits"]},
    }


if __name__ == "__main__":
    result = build()
    (OUT / "restaurant_records.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"]))
