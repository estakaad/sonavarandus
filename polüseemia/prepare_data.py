"""
Töötleb polüseemia andmeid: sõnad → tähendused → semantilised tüübid + seletused.

Sisend: data/polyseemia.csv
  Veerud: word, meaning_id, level1, level2, semantic_type_code, definition
  Üks rida iga (tähendus, semantiline tüüp) kombinatsiooni kohta.
  SQL: data/polyseemia.sql

Väljund: data/polyseemia.json
"""

import csv, json
from collections import defaultdict, OrderedDict

CSV_FILE = "../data/polyseemia.csv"
JSON_FILE = "../data/polyseemia.json"

words = defaultdict(lambda: {"meanings": OrderedDict()})

with open(CSV_FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        word = row["word"].strip()
        meaning_id = row["meaning_id"].strip()
        level1 = int(row.get("level1", 1) or 1)
        level2 = int(row.get("level2", 0) or 0)
        type_code = row.get("semantic_type_code", "").strip()
        definition = row.get("definition", "").strip()

        if meaning_id not in words[word]["meanings"]:
            words[word]["meanings"][meaning_id] = {
                "level1": level1,
                "level2": level2,
                "types": [],
                "def": definition
            }

        if type_code:
            types = words[word]["meanings"][meaning_id]["types"]
            if type_code not in types:
                types.append(type_code)

result = []
all_types = set()

for word, data in words.items():
    meanings = list(data["meanings"].values())
    for m in meanings:
        all_types.update(m["types"])
    result.append({
        "word": word,
        "count": len(meanings),
        "meanings": meanings
    })

result.sort(key=lambda x: -x["count"])

with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump({"words": result, "types": sorted(all_types)}, f, ensure_ascii=False)

print(f"Sõnu kokku: {len(result)}")
print(f"Mitmemõttelisi (2+ tähendust): {sum(1 for x in result if x['count'] > 1)}")
print(f"Max tähendusi: {result[0]['count']} ({result[0]['word']})")
print(f"Semantilised tüübid ({len(all_types)}): {', '.join(sorted(all_types))}")
print(f"Salvestatud: {JSON_FILE}")
