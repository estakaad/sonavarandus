"""
Tuletusliidete andmete ettevalmistus.

Sisend:  data/derivation_raw.csv  (veerud: alussõna, tuletis)
Väljund: data/derivation.json

SQL eksport:
    COPY (
        SELECT w2.value AS alussõna, w1.value AS tuletis
        FROM word_relation wr
        JOIN word w1 ON w1.id = wr.word1_id
        JOIN word w2 ON w2.id = wr.word2_id
        WHERE wr.word_rel_type_code = 'deriv_base'
          AND w1.lang = 'est' AND w2.lang = 'est'
          AND w1.is_public = true
        ORDER BY w2.value
    ) TO '.../derivation_raw.csv' WITH CSV HEADER;
"""

import csv, json
from collections import defaultdict

DATA_DIR   = "../data"
INPUT_CSV  = f"{DATA_DIR}/derivation_raw.csv"
OUTPUT_JSON = "data/derivation.json"
MIN_COUNT  = 5   # minimaalne tuletiste arv sufiksi kuvamiseks
MAX_EXAMPLES = 80  # maksimaalne näidete arv paneelis

# ── loe sisend ────────────────────────────────────────────────
pairs = []
with open(INPUT_CSV, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        pairs.append((row["alussõna"].strip(), row["tuletis"].strip()))

print(f"Loetud: {len(pairs)} tuletuspaari")

# ── eralduda sufiksid ─────────────────────────────────────────
# Kasutame otsest eraldamist: tuletis = alussõna + sufiks
by_suffix = defaultdict(set)  # sufiks → {(alussõna, tuletis)}

for base, derived in pairs:
    if (derived.startswith(base)
            and len(derived) > len(base)
            and len(derived) - len(base) <= 10):   # mõistlik sufiksi pikkus
        suffix = derived[len(base):]
        by_suffix[suffix].add((base, derived))

# ── koosta väljund ────────────────────────────────────────────
suffixes = []
for suffix, pair_set in by_suffix.items():
    if len(pair_set) < MIN_COUNT:
        continue
    examples = sorted(pair_set, key=lambda x: x[0])
    suffixes.append({
        "suffix":   "-" + suffix,
        "count":    len(examples),
        "examples": [{"base": b, "derived": d} for b, d in examples[:MAX_EXAMPLES]],
    })

suffixes.sort(key=lambda x: -x["count"])

total = sum(s["count"] for s in suffixes)
result = {"suffixes": suffixes, "total": total}

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False)

print(f"Eksporditud: {len(suffixes)} sufiksit, {total} tuletuspaarid → {OUTPUT_JSON}")
