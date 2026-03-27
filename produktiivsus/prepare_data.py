"""
Ehitab liitsõnade produktiivsuse andmestiku.

Kasutab sama CSV-d mis liitsõnasild:
  ../liitsõnasild/data/compounds_raw.csv
  Veerud: liitsona, esiosa, jarelosa

Väljund: data/productivity.json
"""

import csv, json
from collections import defaultdict

CSV_FILE = "../liitsõnasild/data/compounds_raw.csv"
JSON_FILE = "data/productivity.json"

MAX_EXAMPLES = 10

esiosa_of   = defaultdict(set)   # sõna → liitsõnad kus ta on esiosa
jarelosa_of = defaultdict(set)   # sõna → liitsõnad kus ta on järelosa

with open(CSV_FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        liitsona = row["liitsona"].strip()
        esiosa   = row["esiosa"].strip()
        jarelosa = row["jarelosa"].strip()
        if not liitsona or not esiosa or not jarelosa:
            continue
        esiosa_of[esiosa].add(liitsona)
        jarelosa_of[jarelosa].add(liitsona)

all_words = set(esiosa_of) | set(jarelosa_of)

words = []
for w in all_words:
    e = sorted(esiosa_of[w])
    j = sorted(jarelosa_of[w])
    words.append({
        "word":             w,
        "esiosa":           len(e),
        "jarelosa":         len(j),
        "total":            len(e) + len(j),
        "esiosa_ex":        e[:MAX_EXAMPLES],
        "jarelosa_ex":      j[:MAX_EXAMPLES],
    })

words.sort(key=lambda x: -x["total"])

with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump({"words": words}, f, ensure_ascii=False)

print(f"Sõnu: {len(words)}")
print(f"Top 10: {[w['word'] for w in words[:10]]}")
print(f"Salvestatud: {JSON_FILE}")
