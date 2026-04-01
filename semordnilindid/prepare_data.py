"""
Semordnilindide andmete ettevalmistus.
Semordnilind: sõnapaar kus A tagurpidi = B (A ≠ B, ≠ palindroom).

Sisend:  ../anagrammid/data/anagrams_raw.csv  (veerg: value)
Väljund: data/semordnilindid.json

Sama SQL eksport mis anagrammid/data/words_raw.csv:
    COPY (
        SELECT DISTINCT w.value
        FROM word w
        JOIN lexeme l ON l.word_id = w.id
            AND l.is_public = true AND l.dataset_code = 'eki'
        WHERE w.lang = 'est' AND w.is_public = true
          AND NOT EXISTS (
              SELECT 1 FROM lexeme_pos lp
              WHERE lp.lexeme_id = l.id AND lp.pos_code = 'prop')
          AND NOT EXISTS (
              SELECT 1 FROM word_word_type wwt
              WHERE wwt.word_id = w.id AND wwt.word_type_code IN ('l','lz'))
        ORDER BY w.value
    ) TO '.../words_raw.csv' WITH CSV HEADER;
"""

import csv, json

INPUT_CSV   = '../data/words_raw.csv'
OUTPUT_JSON = '../data/semordnilindid.json'

words = set()
with open(INPUT_CSV, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        w = row['value'].strip().lower()
        if w:
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

print(f'Eksporditud: {len(pairs)} semordnilindpaari → {OUTPUT_JSON}')
if pairs:
    p = pairs[0]
    print(f'Pikim: {p["a"]} ↔ {p["b"]} ({p["length"]} tähte)')
