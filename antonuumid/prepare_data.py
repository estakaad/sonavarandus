"""
Antonüümide ettevalmistus.
Grupeerib iga sõna antonüümid, deduplitseerib meaning ID põhjal.
"""

import csv, json
from collections import defaultdict

CSV_FILE = "../data/sonavorgustik.csv"
JSON_FILE = "../data/antonüümid.json"

# word -> {antonyms, meaning_id}
entries = {}  # meaning_id -> {word, antonyms: set}

with open(CSV_FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["meaning_rel_type_code"] != "antonüüm":
            continue
        w1, w2 = row["word1"].strip(), row["word2"].strip()
        id1, id2 = row["meaning1_id"], row["meaning2_id"]

        if id1 not in entries:
            entries[id1] = {"word": w1, "antonyms": set()}
        if id2 not in entries:
            entries[id2] = {"word": w2, "antonyms": set()}

        # lisa ainult üks suund (väiksem ID -> suurem ID)
        if id1 < id2:
            entries[id1]["antonyms"].add(w2)
        else:
            entries[id2]["antonyms"].add(w1)

# filtreeri välja tühjad (sõnad kellel pole antonüüme pärast dedupl.)
result = [
    {"word": e["word"], "antonyms": sorted(e["antonyms"])}
    for e in entries.values()
    if e["antonyms"]
]

# sorteeri: enim antonüüme ees, seejärel tähestiku järgi
result.sort(key=lambda x: (-len(x["antonyms"]), x["word"]))

with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump({"pairs": result}, f, ensure_ascii=False)

print(f"Sõnu antonüümidega: {len(result)}")
print(f"Suurim: {result[0]['word']} ({len(result[0]['antonyms'])} antonüümi): {result[0]['antonyms']}")
print(f"Salvestatud: {JSON_FILE}")
