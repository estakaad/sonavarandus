"""
Fraseoloogiliste väljendite andmete ettevalmistus.

Sisend: data/fras.csv
  Veerud: word_id, keelend, semantic_type_code, semantic_type_label, definition
  SQL: export_data.sql päring 13 (FRASEOLOOGILISED VÄLJENDID)

Väljund: data/fraseoloogilised.json
"""

import csv, json, colorsys
from collections import defaultdict

CSV_FILE  = "../data/fras.csv"
JSON_FILE = "../data/fraseoloogilised.json"

# keelend → {word_id, semantic_type_code, semantic_type_label, definition}
# grupeerime semantic_type_label järgi
categories = defaultdict(lambda: {"code": None, "expressions": {}})

with open(CSV_FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        label = row["semantic_type_label"].strip()
        code  = row["semantic_type_code"].strip()
        wid   = row["word_id"].strip()
        keelend   = row["keelend"].strip()
        definition = row["definition"].strip()

        categories[label]["code"] = code
        categories[label]["expressions"][wid] = {
            "id":       wid,
            "keelend":  keelend,
            "definition": definition
        }

# Sorteeri kategooriad arvu järgi
sorted_cats = sorted(categories.items(), key=lambda x: len(x[1]["expressions"]), reverse=True)

# Värviskeem
def hsl_to_hex(h, s, l):
    h /= 360.0; s /= 100.0; l /= 100.0
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

categories_data = []
for i, (label, data) in enumerate(sorted_cats):
    hue = (i * 360 / len(sorted_cats)) % 360
    expressions = sorted(data["expressions"].values(), key=lambda e: e["keelend"])
    categories_data.append({
        "name":        label,
        "code":        data["code"],
        "count":       len(expressions),
        "color":       hsl_to_hex(hue, 70, 60),
        "expressions": expressions
    })

result = {
    "categories":    categories_data,
    "total":         sum(c["count"] for c in categories_data),
    "categoryCount": len(categories_data)
}

with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False)

print(f"Kategooriaid: {len(categories_data)}")
print(f"Väljendeid kokku: {result['total']}")
print(f"Salvestatud: {JSON_FILE}")
