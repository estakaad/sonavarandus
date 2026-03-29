"""
Palindroomide andmete ettevalmistus.

Sisend:  data/palindromes_raw.csv  (veerg: value)
Väljund: data/palindromes.json

SQL eksport (DBeaveris):
    COPY (
        SELECT DISTINCT w.value
        FROM word w
        JOIN lexeme l ON l.word_id = w.id
            AND l.is_public = true
            AND l.dataset_code = 'eki'
        WHERE w.lang = 'est'
          AND w.is_public = true
          AND w.value = reverse(w.value)
          AND length(w.value) >= 3
        ORDER BY w.value
    ) TO '.../palindromes_raw.csv' WITH CSV HEADER;
"""

import csv, json
from collections import defaultdict

INPUT_CSV   = 'data/palindromes_raw.csv'
OUTPUT_JSON = 'data/palindromes.json'

by_length = defaultdict(list)

with open(INPUT_CSV, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        w = row['value'].strip()
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
