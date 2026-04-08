"""
Ehitab adjacency-list JSON kõigist meaning_relation seostest.
Mõlemad suunad, duplikaadid eemaldatud.
"""

import csv, json
from collections import defaultdict

CSV_FILE = "../data/sonavorgustik.csv"
JSON_FILE = "../data/graph.json"

adjacency = defaultdict(list)

with open(CSV_FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        w1 = row["word1"]
        w2 = row["word2"]
        rel = row["meaning_rel_type_code"]
        adjacency[w1].append({"word": w2, "type": rel})
        adjacency[w2].append({"word": w1, "type": rel})

# eemalda duplikaadid
for word in adjacency:
    seen = set()
    deduped = []
    for item in adjacency[word]:
        key = (item["word"], item["type"])
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    adjacency[word] = deduped

with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump({"adjacency": dict(adjacency)}, f, ensure_ascii=False)

print(f"Sõnu: {len(adjacency)}")
print(f"Salvestatud: {JSON_FILE}")
