"""
Leiab liitsõnad, mida saab poolitada mitmel erineval viisil nii,
et mõlemad osad on eraldivõetuna kehtivad sõnad.

Näide: silmatera → silma+tera ja silm+atera (kui mõlemad on sõnad)

Kasutab:
  ../data/words.csv     — kõik kehtivad sõnad (veerg: value)
  ../data/liit.csv      — liitsõnad (veerud: liitsona, esiosa, jarelosa)

Väljund: ../data/kahepoolitused.json
"""

import csv, json

WORDS_FILE  = "../data/words.csv"
LIIT_FILE   = "../data/liit.csv"
JSON_FILE   = "../data/kahepoolitused.json"

# Lae kõik kehtivad üksikud sõnad (ilma tühikuteta, väiketähtedena)
words = set()
with open(WORDS_FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        v = row["value"].strip().lower()
        if v and " " not in v and "-" not in v:
            words.add(v)

print(f"Sõnavara: {len(words)} sõna")

# Lae kõik liitsõnad
compounds = set()
with open(LIIT_FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        w = row["liitsona"].strip().lower()
        if w and "-" not in w:
            compounds.add(w)

print(f"Liitsõnu: {len(compounds)}")

# Leia mitmetähenduslikult poolitatavad
# Tingimus: kumbki osa ei tohi ise olla liitsõna (st sõna koosneb täpselt 2 osast)
results = []
for compound in compounds:
    n = len(compound)
    valid_splits = []
    for i in range(2, n - 1):  # vähemalt 2 tähte mõlemal poolel
        esiosa   = compound[:i]
        jarelosa = compound[i:]
        if (esiosa in words and jarelosa in words
                and esiosa not in compounds and jarelosa not in compounds):
            valid_splits.append({"esiosa": esiosa, "jarelosa": jarelosa})
    if len(valid_splits) >= 2:
        results.append({
            "word":   compound,
            "splits": valid_splits
        })

# Sorteeri: enim poolitusvalikuid ees, siis tähestikuliselt
results.sort(key=lambda x: (-len(x["splits"]), x["word"]))

print(f"Mitmetähenduslikult poolitatavaid: {len(results)}")
if results:
    print("Näiteid:")
    for r in results[:10]:
        splits_str = " | ".join(f"{s['esiosa']}+{s['jarelosa']}" for s in r["splits"])
        print(f"  {r['word']}: {splits_str}")

with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump({"words": results}, f, ensure_ascii=False)

print(f"Salvestatud: {JSON_FILE}")
