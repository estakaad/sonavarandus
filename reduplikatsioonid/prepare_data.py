"""
Reduplikatsioonide ettevalmistus.
Reduplikatsioon: sõna kus esimene pool = teine pool (nt kuku, papa, tiptop).

Sisend:  data/words.csv
Väljund: data/reduplications.json

Filtreerimine:
- Ei kuva nimesid (pos_codes sisaldab 'prop')
- Ei kuva lühendeid (word_type_codes sisaldab 'l')
- Ei kuva tähiseid sisaldavaid sõnu
"""

import csv, json
from collections import defaultdict

INPUT_CSV   = '../data/words.csv'
OUTPUT_JSON = '../data/reduplications.json'

by_length = defaultdict(list)

with open(INPUT_CSV, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        w = row['value'].strip().lower()
        pos = row.get('pos_codes', '').strip()
        word_type = row.get('word_type_codes', '').strip()

        # Skip nimed ja lühendid
        if 'prop' in pos or 'l' in word_type:
            continue

        n = len(w)
        if n >= 4 and n % 2 == 0:
            half = n // 2
            if w[:half] == w[half:]:
                by_length[n].append(w)

groups = []
for length in sorted(by_length.keys(), reverse=True):
    words = sorted(set(by_length[length]))
    groups.append({'length': length, 'words': words})

total = sum(len(g['words']) for g in groups)
result = {'groups': groups, 'total': total}

with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)

print(f'Eksporditud: {total} reduplikatsiooni -> {OUTPUT_JSON}')
