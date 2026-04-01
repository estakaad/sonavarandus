"""
Scrabble-skoori andmete ettevalmistus.

Sisend:  data/words_raw.csv  (veerg: value)
         — sama eksport mis anagrammid/data/anagrams_raw.csv,
           võib kopeerida/sümlingida.

Väljund: data/scrabble.json

SQL eksport (DBeaveris):
    COPY (
        SELECT DISTINCT w.value
        FROM word w
        JOIN lexeme l ON l.word_id = w.id
            AND l.is_public = true
            AND l.dataset_code = 'eki'
        WHERE w.lang = 'est'
          AND w.is_public = true
          AND length(w.value) >= 2
          AND NOT EXISTS (
              SELECT 1 FROM lexeme_pos lp
              WHERE lp.lexeme_id = l.id
                AND lp.pos_code = 'prop'
          )
          AND NOT EXISTS (
              SELECT 1 FROM word_word_type wwt
              WHERE wwt.word_id = w.id
                AND wwt.word_type_code IN ('l', 'lz')
          )
        ORDER BY w.value
    ) TO '.../words_raw.csv' WITH CSV HEADER;

Tähevaartused: Eesti Scrabble (vt https://www.scrabble.ee/)
"""

import csv, json, re

INPUT_CSV   = '../data/words_raw.csv'
OUTPUT_JSON = '../data/scrabble.json'
TOP_N       = 500

# Eesti Scrabble ametlikud tähevaartused
SCORES = {
    'a': 1, 'e': 1, 'i': 1, 'l': 1, 'n': 1,
    'o': 1, 'r': 1, 's': 1, 't': 1, 'u': 1,
    'd': 2, 'g': 2, 'h': 2, 'k': 2, 'm': 2, 'v': 2,
    'ä': 3, 'b': 3, 'j': 3, 'p': 3, 'ü': 3,
    'ö': 4,
    'f': 5, 'õ': 5,
    'c': 8, 'š': 8, 'w': 8, 'x': 8, 'y': 8, 'z': 8, 'ž': 8,
    'q': 10,
}

VALID = set(SCORES.keys())

def word_score(w):
    return sum(SCORES.get(ch, 0) for ch in w)

def is_valid(w):
    """Ainult scrabble-tähed, ei tühik/sidekriips/number."""
    return bool(w) and all(ch in VALID for ch in w)

results = []

with open(INPUT_CSV, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        w = row['value'].strip().lower()
        if is_valid(w):
            score = word_score(w)
            results.append({'word': w, 'score': score, 'len': len(w)})

results.sort(key=lambda x: (-x['score'], -x['len'], x['word']))
top = results[:TOP_N]

# Lisa tähejaotus paneeli jaoks
for item in top:
    item['letters'] = [
        {'ch': ch, 'pts': SCORES[ch]} for ch in item['word']
    ]

out = {
    'words': top,
    'scores': SCORES,
    'total_valid': len(results),
}

with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False)

print(f'Eksporditud: top {len(top)} / {len(results)} sobivat sõna → {OUTPUT_JSON}')
if top:
    print(f'Parim: {top[0]["word"]} ({top[0]["score"]} punkti)')
