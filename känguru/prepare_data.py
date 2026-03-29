"""
Kängurusõnade ettevalmistus.
Kängurusõna: sõna mis sisaldab oma sünonüümi tähti algses järjekorras
(järjend ehk subsequence — tähed ei pea olema järjestikku).

Näide: kui "elamine" ja "elu" on sünonüümid ning "elu" tähed esinevad
sõnas "elamine" samas järjekorras → "elamine" on kängurusõna.

Sisend:  ../sünonüümid/data/synonyms_raw.csv  (veerud: meaning_id, word)
Väljund: data/kangaroo.json

Sünonüümiandmed on olemas — sama fail mida kasutab sünonüümitiheduse moodul.
"""

import csv, json
from collections import defaultdict

INPUT_CSV   = '../sünonüümid/data/synonyms_raw.csv'
OUTPUT_JSON = 'data/kangaroo.json'
MIN_DIFF    = 2   # kangaroo peab olema vähemalt 2 tähte pikem

def is_subsequence(short, long):
    """Kas 'short' esineb 'long'-is järjendina?"""
    it = iter(long)
    return all(ch in it for ch in short)

# Loe sünonüümigrupid
groups = defaultdict(list)
with open(INPUT_CSV, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        mid = row['meaning_id'].strip()
        w   = row['word'].strip().lower()
        if w:
            groups[mid].append(w)

pairs = []
for mid, syns in groups.items():
    if len(syns) < 2:
        continue
    # Proovi kõiki paare (pikem, lühem)
    syns_sorted = sorted(set(syns), key=len)
    for i, short in enumerate(syns_sorted):
        for long in syns_sorted[i+1:]:
            if len(long) - len(short) >= MIN_DIFF and is_subsequence(short, long):
                # Leia positsioonid visualiseerimiseks
                positions = []
                j = 0
                for k, ch in enumerate(long):
                    if j < len(short) and ch == short[j]:
                        positions.append(k)
                        j += 1
                pairs.append({
                    'word':      long,
                    'hidden':    short,
                    'positions': positions,
                    'length':    len(long),
                })

# De-duplikeeri: sama (long, short) paar ainult üks kord
seen = set()
unique = []
for p in pairs:
    key = (p['word'], p['hidden'])
    if key not in seen:
        seen.add(key)
        unique.append(p)

unique.sort(key=lambda p: (-p['length'], p['word']))

result = {'pairs': unique, 'total': len(unique)}
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)

print(f'Eksporditud: {len(unique)} kängurusõna → {OUTPUT_JSON}')
if unique:
    p = unique[0]
    print(f'Näide: {p["word"]} sisaldab {p["hidden"]}')
