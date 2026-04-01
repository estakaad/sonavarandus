"""
Univokaalide ettevalmistus.
Univokaal: sõna milles esineb ainult üks täishäälik (nt ainult 'u', ainult 'a').

Sisend:  ../anagrammid/data/anagrams_raw.csv  (veerg: value)
Väljund: data/univocals.json
"""

import csv, json
from collections import defaultdict

INPUT_CSV   = '../data/words_raw.csv'
OUTPUT_JSON = '../data/univocals.json'

VOWELS = set('aeiouõäöü')
MIN_LENGTH = 3

by_vowel = defaultdict(lambda: defaultdict(list))

with open(INPUT_CSV, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        w = row['value'].strip().lower()
        if len(w) < MIN_LENGTH:
            continue
        vowels_in_word = {ch for ch in w if ch in VOWELS}
        if len(vowels_in_word) == 1:
            v = next(iter(vowels_in_word))
            by_vowel[v][len(w)].append(w)

categories = []
for vowel in sorted(by_vowel.keys()):
    groups = []
    for length in sorted(by_vowel[vowel].keys(), reverse=True):
        words = sorted(set(by_vowel[vowel][length]))
        groups.append({'length': length, 'words': words})
    total = sum(len(g['words']) for g in groups)
    categories.append({'vowel': vowel, 'groups': groups, 'total': total})

# sordi: kõigepealt kategooriad kus kõige pikemad sõnad
categories.sort(key=lambda c: -c['groups'][0]['length'] if c['groups'] else 0)

result = {'categories': categories}
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)

for cat in categories:
    pikim = cat['groups'][0] if cat['groups'] else None
    ex = pikim['words'][0] if pikim else '-'
    print(f"Ainult '{cat['vowel']}': {cat['total']} sõna, pikim: {ex}")
