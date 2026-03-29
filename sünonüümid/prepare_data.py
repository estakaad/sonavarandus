"""
Sünonüümitiheduse andmete ettevalmistus.

Sisend:  data/synonyms_raw.csv  (veerud: meaning_id, word, definition)
Väljund: data/synonyms.json

SQL eksport (DBeaveris):
    COPY (
        WITH syn_meanings AS (
            SELECT l.meaning_id FROM lexeme l
            JOIN word w ON w.id = l.word_id
            WHERE w.lang = 'est' AND w.is_public = true AND l.is_public = true
            AND l.dataset_code = 'eki'
            GROUP BY l.meaning_id HAVING count(DISTINCT w.id) >= 2
        )
        SELECT l.meaning_id, w.value AS word, d.value AS definition
        FROM syn_meanings sm
        JOIN lexeme l ON l.meaning_id = sm.meaning_id AND l.is_public = true
        JOIN word w ON w.id = l.word_id AND w.lang = 'est' AND w.is_public = true
        LEFT JOIN LATERAL (
            SELECT value FROM definition
            WHERE meaning_id = l.meaning_id AND lang = 'est' AND is_public = true
            ORDER BY order_by LIMIT 1
        ) d ON true
        ORDER BY l.meaning_id, w.value
    ) TO '.../synonyms_raw.csv' WITH CSV HEADER;
"""

import csv, json
from collections import defaultdict

INPUT_CSV   = 'data/synonyms_raw.csv'
OUTPUT_JSON = 'data/synonyms.json'
MAX_EXAMPLES = 80  # sõnade arv loendi reas (preview)

# ── loe ja grupeeri tähenduse järgi ──────────────────────────
meanings = defaultdict(lambda: {'words': set(), 'definition': None})

with open(INPUT_CSV, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        mid = row['meaning_id'].strip()
        w   = row['word'].strip()
        d   = row['definition'].strip() if row['definition'] else None
        if w:
            meanings[mid]['words'].add(w)
        if d and not meanings[mid]['definition']:
            meanings[mid]['definition'] = d

# ── koosta loend ──────────────────────────────────────────────
result_list = []
for mid, data in meanings.items():
    words = sorted(data['words'])
    count = len(words)
    if count < 2:
        continue
    result_list.append({
        'id':         mid,
        'count':      count,
        'preview':    words[:MAX_EXAMPLES],
        'words':      words,
        'definition': data['definition'] or '',
    })

result_list.sort(key=lambda x: -x['count'])

result = {'meanings': result_list, 'total': len(result_list)}

with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)

max_c = result_list[0]['count'] if result_list else 0
print(f'Eksporditud: {len(result_list)} tähendust, max sünonüüme {max_c} → {OUTPUT_JSON}')
