"""
Anagrammigruppide andmete ettevalmistus.

Sisend:  data/anagrams_raw.csv  (veerg: value)
Väljund: data/anagrams.json

SQL eksport (DBeaveris):
    COPY (
        SELECT DISTINCT w.value
        FROM word w
        JOIN lexeme l ON l.word_id = w.id
            AND l.is_public = true
            AND l.dataset_code = 'eki'
        WHERE w.lang = 'est'
          AND w.is_public = true
          AND length(w.value) >= 3
        ORDER BY w.value
    ) TO '.../anagrams_raw.csv' WITH CSV HEADER;
"""

import csv, json
from collections import defaultdict  # buckets jaoks

INPUT_CSV   = 'data/anagrams_raw.csv'
OUTPUT_JSON = 'data/anagrams.json'

def anagram_key(word):
    return ''.join(sorted(word.lower()))

buckets = defaultdict(list)
seen_lower = set()

with open(INPUT_CSV, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        w = row['value'].strip().lower()
        if w and w not in seen_lower:
            seen_lower.add(w)
            buckets[anagram_key(w)].append(w)

def is_boring_pair(a, b):
    """True kui paar on igav: samad liitsõnaosad lihtsalt erinevas järjekorras."""
    # Rotatsioon: b = suffix(a) + prefix(a) — nt petrooleumvalgustus / valgustuspetrooleum
    if len(a) == len(b) and b in (a + a):
        return True
    # Sidekriipsuga liitsõnad: samad osad erinevas järjekorras
    # nt muna-piima-taimetoitlane / piima-muna-taimetoitlane
    if '-' in a and '-' in b:
        if sorted(a.split('-')) == sorted(b.split('-')):
            return True
    return False

def filter_boring(words):
    """Eemalda sõnad millel pole ühtegi huvitavat (mitte-igavat) partnerit grupis."""
    kept = [w for w in words
            if any(not is_boring_pair(w, v) for v in words if v != w)]
    return kept

groups = []
filtered_count = 0
for key, words in buckets.items():
    if len(words) >= 2:
        words_sorted = sorted(words)
        cleaned = filter_boring(words_sorted)
        if len(cleaned) >= 2:
            groups.append({
                'length': len(cleaned[0]),
                'size':   len(cleaned),
                'words':  cleaned,
            })
        elif len(cleaned) < len(words_sorted):
            filtered_count += 1

# pika sõna ja suure grupi järgi kahanevas järjestuses
groups.sort(key=lambda g: (-g['length'], -g['size']))

total_words = sum(g['size'] for g in groups)
result = {'groups': groups, 'total_groups': len(groups), 'total_words': total_words}

with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)

print(f'Eksporditud: {len(groups)} anagrammigruppi, {total_words} sõna (filtreeritud {filtered_count} rotatsioonigrupp)')
