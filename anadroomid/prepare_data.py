"""
Semordnilindide andmete ettevalmistus.
Semordnilind: sõnapaar kus A tagurpidi = B (A ≠ B, ≠ palindroom).

Sisend:  data/words.csv
Väljund: data/semordnilindid.json

Filtreerimine:
- Ei kuva nimesid (pos_codes sisaldab 'prop')
- Ei kuva lühendeid (word_type_codes sisaldab 'l')
- Ei kuva tähiseid sisaldavaid sõnu
"""

import csv, json

INPUT_CSV   = '../data/words.csv'
OUTPUT_JSON = '../data/semordnilindid.json'

words = set()
with open(INPUT_CSV, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        w = row['value'].strip().lower()
        pos = row.get('pos_codes', '').strip()
        word_type = row.get('word_type_codes', '').strip()

        # Skip nimed ja lühendid ja tähiseid
        if 'prop' in pos or 'l' in word_type:
            continue

        if w and len(w) >= 2:
            words.add(w)

pairs = []
seen = set()
for w in sorted(words):
    r = w[::-1]
    if r in words and r != w and w not in seen:
        pairs.append({'a': w, 'b': r, 'length': len(w)})
        seen.add(w)
        seen.add(r)

pairs.sort(key=lambda p: (-p['length'], p['a']))

result = {'pairs': pairs, 'total': len(pairs)}
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)

print(f'Eksporditud: {len(pairs)} anadroompaari -> {OUTPUT_JSON}')
if pairs:
    p = pairs[0]
    print(f'Pikim: {p["a"]} <-> {p["b"]} ({p["length"]} tähte)')
