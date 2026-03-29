"""
Heterogrammide ettevalmistus.
Heterogramm: sõna kus ükski täht ei kordu.

Sisend:  ../anagrammid/data/anagrams_raw.csv  (veerg: value)
Väljund: data/heterograms.json
"""

import csv, json
from collections import defaultdict

INPUT_CSV   = '../anagrammid/data/anagrams_raw.csv'
OUTPUT_JSON = 'data/heterograms.json'

by_length = defaultdict(list)

with open(INPUT_CSV, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        w = row['value'].strip().lower()
        if w and len(set(w)) == len(w):
            by_length[len(w)].append(w)

groups = []
for length in sorted(by_length.keys(), reverse=True):
    words = sorted(set(by_length[length]))
    groups.append({'length': length, 'words': words})

total = sum(len(g['words']) for g in groups)
result = {'groups': groups, 'total': total}

with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)

print(f'Eksporditud: {total} heterogrammi → {OUTPUT_JSON}')
if groups:
    print(f'Pikim ({groups[0]["length"]} tähte): {", ".join(groups[0]["words"][:5])}')
