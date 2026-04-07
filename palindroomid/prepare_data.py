"""
Palindroomide andmete ettevalmistus.

Sisend:  data/words_raw.csv
Väljund: data/palindromes.json

Filtreerimine:
- Ei kuva lühendeid (word_type_codes sisaldab 'l')
- Ei kuva nimesid (pos_codes sisaldab 'prop')
"""

import csv, json
from collections import defaultdict

INPUT_CSV   = '../data/words_raw.csv'
OUTPUT_JSON = '../data/palindromes.json'

by_length = defaultdict(list)

with open(INPUT_CSV, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        w = row['value'].strip()
        word_type = row.get('word_type_codes', '').strip()
        pos = row.get('pos_codes', '').strip()

        # Skip lühendid ja nimed
        if 'l' in word_type or 'prop' in pos:
            continue

        if w and w == w[::-1] and len(w) >= 3:
            by_length[len(w)].append(w)

groups = []
for length in sorted(by_length.keys(), reverse=True):
    words = sorted(by_length[length])
    groups.append({'length': length, 'words': words})

total = sum(len(g['words']) for g in groups)
result = {'groups': groups, 'total': total}

with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)

print(f'Eksporditud: {total} palindroomi, {len(groups)} pikkusegruppi → {OUTPUT_JSON}')
