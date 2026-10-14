"""Interpret reviewed Mexican Subway sections, including page continuations.

A heading that mentions an amount for a 6-inch sandwich does not describe a
complete sandwich. Published record IDs are retained while labels are corrected.
"""
import hashlib
import re

REVIEW_DATE = "2026-10-14"
SOURCE_GROUPS = {
    "series": ('6" Subway Series', '6-inch sub', 'entree'),
    "sandwiches": ('6" Sandwiches', '6-inch sub', 'entree'),
    "salads": ('Salads', 'Salad', 'entree'),
    "breads": ('Breads', 'Breads', 'component'),
    "condiments": ('Sandwich Condiments and Toppings (amount on 6-inch sandwich)', 'Condiment portion', 'component'),
    "vegetables": ('Vegetables (amount on 6-inch sandwich)', 'Vegetable portion', 'component'),
    "cheese": ('Cheese (amount on 6-inch sandwich)', 'Cheese portion', 'component'),
    "meats": ('Individual Meats (amount on 6" sub or salad)', 'Individual meat portion', 'component'),
    "desserts": ('Desserts', 'Desserts', 'dessert'),
    "sides": ('Sides', 'Sides', 'side'),
}


def number(value):
    text = str(value if value is not None else "").strip()
    return float(text) if re.fullmatch(r"\d+(?:\.\d+)?", text) else None


def section(text):
    """Only explicit known headings can establish a meal category."""
    text = " ".join(str(text or "").split())
    low = text.lower()
    for prefix, key in (("individual meats", "meats"), ("sandwich condiments", "condiments"),
                        ("vegetables (", "vegetables"), ("cheese (", "cheese"),
                        ("breads", "breads"), ("desserts", "desserts"), ("sides", "sides")):
        if low.startswith(prefix) and low != "breads & condiments":
            return key
    if '6" Subway Series' in text:
        return "series"
    if text.startswith('6" Sandwiches'):
        return "sandwiches"
    if text == "Salads" or ("Salads" in text and "Values include" in text):
        return "salads"
    return None


def old_identity(name, serving):
    """Compatibility identity; never call the historical label a correct meal."""
    return "MX|subway|" + hashlib.sha256((name + "|" + serving).encode()).hexdigest()[:16]


def normalize(pages):
    result = []
    current = None
    for page in pages:
        # The old generator reset this at each page. Preserve only its ID,
        # while the real source section continues across a page boundary.
        legacy_group = ""
        for cells in page["tables"][0]:
            if len(cells) != 11:
                continue
            if number(cells[1]) is None:
                if cells[0] and all(x is None for x in cells[1:]):
                    legacy_group = " ".join(cells[0].split())
                    found = section(cells[0])
                    # Unknown new section headings invalidate the old section;
                    # they must be reviewed before another numeric row imports.
                    current = found
                continue
            if current is None or not cells[0]:
                raise ValueError("Unclassified numeric Mexican source row")
            group, prefix, category = SOURCE_GROUPS[current]
            legacy_prefix = '6-inch sub' if '6"' in legacy_group else 'Salad' if 'Salads' in legacy_group else legacy_group
            legacy_name = legacy_prefix + ' — ' + cells[0]
            legacy_serving = '1 ' + legacy_prefix.lower() + ' · ' + cells[1] + ' g'
            unit = {
                "series": "1 6-inch sub", "sandwiches": "1 6-inch sub", "salads": "1 salad",
                "breads": "1 named bread portion", "condiments": "1 condiment portion for a 6-inch sandwich",
                "vegetables": "1 vegetable portion for a 6-inch sandwich", "cheese": "1 cheese portion for a 6-inch sandwich",
                "meats": "1 individual meat portion for a 6-inch sub or salad",
                "desserts": "1 named dessert", "sides": "1 named side",
            }[current]
            values = {key: number(cells[i]) for key, i in {'cal': 2, 'fat': 4, 'sat': 5,
                       'na': 6, 'c': 7, 'f': 8, 'sugar': 9, 'p': 10}.items()}
            note = "November 2025 Mexican source snapshot; local availability and subsequent menu changes are not audited. "
            if category == "component":
                note += "One separately listed ingredient amount, not a complete sandwich or meal. Bread, vegetables, cheese and sauces are not added unless this row names them."
            elif current == "salads":
                note += "Published salad includes its listed vegetables; dressing is excluded unless named by the source."
            elif current in ("series", "sandwiches"):
                note += "Published complete 6-inch recipe; no extra sauces, sides or drinks are added."
            else:
                note += "One named source dessert or side; not a sandwich, ingredient amount or complete combo."
            result.append({
                "id": old_identity(legacy_name, legacy_serving),
                "name": prefix + " — " + cells[0], "serving": unit + " · " + cells[1] + " g",
                "category": category, "sourceGroup": group, "sourcePage": page["page"],
                "servingGrams": number(cells[1]), "values": values, "notes": note,
                "finderSupported": category != "component" and all(values[k] is not None for k in ("cal", "p", "c", "fat")),
                "components": ['Lettuce', 'Tomatoes', 'Onions', 'Green peppers', 'Cucumbers', 'Olives'] if current == "salads" else [],
                "classificationReviewedAt": REVIEW_DATE,
                "identityProvenance": "Existing public record ID retained after source-section and serving-label review.",
            })
    if len({r["id"] for r in result}) != len(result):
        raise ValueError("Duplicate Mexican source identity")
    return result
