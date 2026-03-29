"""
Minimaalpaaride ettevalmistus.
Minimaalpar: kaks sama pikkusega sõna mis erinevad täpselt ühel positsioonil.

Sisend:  ../anagrammid/data/anagrams_raw.csv  (veerg: value)
Väljund: data/minimalpairs.json
"""

import csv, json
from collections import defaultdict

INPUT_CSV   = '../anagrammid/data/anagrams_raw.csv'
OUTPUT_JSON = 'data/minimalpairs.json'
MIN_LENGTH  = 4    # lühemad ei ole huvitavad
MAX_PAIRS   = 3000

words_by_length = defaultdict(set)

with open(INPUT_CSV, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        w = row['value'].strip().lower()
        if len(w) >= MIN_LENGTH:
            words_by_length[len(w)].add(w)

# Muster-meetod: asenda iga positsioon '_'-ga, rühmita mustri järgi
pairs = []

for length in sorted(words_by_length.keys(), reverse=True):
    word_list = sorted(words_by_length[length])
    buckets = defaultdict(list)
    for w in word_list:
        for i in range(length):
            pattern = w[:i] + '_' + w[i+1:]
            buckets[pattern].append(w)
    for pattern, group in buckets.items():
        if len(group) >= 2:
            pos = pattern.index('_')
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    pairs.append({
                        'a': group[i], 'b': group[j],
                        'pos': pos, 'length': length
                    })
    if len(pairs) >= MAX_PAIRS:
        break

pairs.sort(key=lambda p: (-p['length'], p['a']))
pairs = pairs[:MAX_PAIRS]

result = {'pairs': pairs, 'total': len(pairs)}
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)

print(f'Eksporditud: {len(pairs)} minimaalpaar → {OUTPUT_JSON}')
if pairs:
    p = pairs[0]
    print(f'Näide: {p["a"]} / {p["b"]} (erinev positsioon {p["pos"]})')
