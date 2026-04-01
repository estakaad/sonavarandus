"""
Prisoner's constraint (Macao constraint) — sõnad ilma ascendereid/descenderitega tähtedeta.

Välistatud tähed (ascenderid + descenderid): b, d, f, g, h, j, k, l, p, q, t, y

Väljund: data/prisoner.json
"""

import csv, json
from collections import defaultdict

INPUT_CSV = "../data/words_raw.csv"
OUTPUT_JSON = "data/prisoner.json"

# Tähed, mis on välistatud (ascenderid ja descenderid)
FORBIDDEN = set('bdfghjklpqty')

by_length = defaultdict(list)

with open(INPUT_CSV, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        w = row['value'].strip().lower()
        # Kontrolli, et ei sisalda keelatud tähti
        if w and not any(ch in FORBIDDEN for ch in w):
            by_length[len(w)].append(w)

# Sorteeri pikkuse järgi, igal pikkusel sorteeri sõnad
groups = []
for length in sorted(by_length.keys(), reverse=True):
    words = sorted(set(by_length[length]))
    if words:
        groups.append({
            'length': length,
            'count': len(words),
            'words': words,
        })

total_words = sum(g['count'] for g in groups)
result = {'groups': groups, 'total_words': total_words}

with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)

print(f'Eksporditud: {total_words} sõna (Prisoner\'s constraint)')
