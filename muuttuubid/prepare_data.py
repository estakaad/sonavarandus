import csv
import json

csv.field_size_limit(10 ** 7)

data = {'noomen': [], 'verb': [], 'muutumatu': []}

with open('../data/paradigm_stat_slim.csv', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        wc = row['word_class'].strip()
        if wc not in data:
            continue
        examples = [w.strip() for w in row['soned'].split(',') if w.strip()]
        data[wc].append({
            'type': row['inflection_type'].strip(),
            'type_nr': row['inflection_type_nr'].strip(),
            'count': int(row['word_count']),
            'examples': examples[:60]
        })

for wc in data:
    data[wc].sort(key=lambda x: x['count'], reverse=True)

with open('../data/paradigm_stat.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)

for wc, items in data.items():
    print(f'{wc}: {len(items)} tüüpi')
