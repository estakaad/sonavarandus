"""
Lipogrammide ettevalmistus.
Lipogramm: sõna milles puudub täielikult mõni sage täht.
Kategooriad: puudub 'a', puudub 'e', puudub 'i'.

Sisend:  ../anagrammid/data/anagrams_raw.csv  (veerg: value)
Väljund: data/lipograms.json
"""

import csv, json
from collections import defaultdict

INPUT_CSV   = '../data/words_raw.csv'
OUTPUT_JSON = '../data/lipograms.json'
BANNED_LETTERS = ['a', 'e', 'i']
MIN_LENGTH = 6   # lühemad ei ole huvitavad
TOP_PER_LENGTH = 200

words = []
with open(INPUT_CSV, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        w = row['value'].strip().lower()
        if len(w) >= MIN_LENGTH:
            words.append(w)

categories = []
for letter in BANNED_LETTERS:
    by_length = defaultdict(list)
    for w in words:
        if letter not in w:
            by_length[len(w)].append(w)
    groups = []
    for length in sorted(by_length.keys(), reverse=True):
        ws = sorted(set(by_length[length]))[:TOP_PER_LENGTH]
        groups.append({'length': length, 'words': ws})
    categories.append({'letter': letter, 'groups': groups,
                       'total': sum(len(g['words']) for g in groups)})

result = {'categories': categories}
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)

for cat in categories:
    print(f"Puudub '{cat['letter']}': {cat['total']} sõna")
    if cat['groups']:
        g = cat['groups'][0]
        print(f"  Pikim ({g['length']} tähte): {g['words'][0]}")
