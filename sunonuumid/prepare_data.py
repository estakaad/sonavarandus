"""
Sünonüümitiheduse andmete ettevalmistus.

Sisend:  data/synonyms.csv  (veerud: meaning_id, word_id, word, definition)
  SQL: export_data.sql päring 4 (SÜNONÜÜMID)

Väljund: data/synonyms.json
"""

import csv, json
from collections import defaultdict

INPUT_CSV   = '../data/synonyms.csv'
OUTPUT_JSON = '../data/synonyms.json'
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
