"""
Genereerib paradigm_stat.csv-st slim-versiooni:
ainult word_class, inflection_type_nr, inflection_type, word_count ja 60 näitesõna.
Väljund: ../data/paradigm_stat_slim.csv (~50KB, sobib andmerepole)
"""
import csv

csv.field_size_limit(10 ** 7)

rows = []
with open('../data/paradigm_stat.csv', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        examples = [w.strip() for w in row['soned'].split(',') if w.strip()]
        rows.append({
            'word_class': row['word_class'],
            'inflection_type_nr': row['inflection_type_nr'],
            'inflection_type': row['inflection_type'],
            'word_count': row['word_count'],
            'soned': ', '.join(examples[:60]),
        })

with open('../data/paradigm_stat_slim.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['word_class', 'inflection_type_nr', 'inflection_type', 'word_count', 'soned'])
    writer.writeheader()
    writer.writerows(rows)

import os
size = os.path.getsize('../data/paradigm_stat_slim.csv')
print(f'Valmis: {len(rows)} rida, {size / 1024:.1f} KB')
