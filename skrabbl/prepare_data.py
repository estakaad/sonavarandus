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
    'a': 1, 'e': 1, 'i': 1, 'o': 1, 's': 1, 't': 1, 'u': 1,
    'd': 2, 'm': 2, 'n': 2, 'r': 2,
    'g': 3, 'v': 3,
    'b': 4, 'h': 4, 'j': 4, 'p': 4, 'õ': 4,
    'ä': 5, 'ü': 5,
    'ö': 6,
    'f': 8,
    'z': 10, 'š': 10, 'ž': 10,
}

# Mängus olevad klotsid (tile counts)
TILE_COUNTS = {
    'a': 10, 'b': 1, 'd': 4, 'e': 9, 'f': 1, 'g': 2, 'h': 2, 'i': 9,
    'j': 2, 'k': 5, 'l': 5, 'm': 4, 'n': 4, 'o': 5, 'p': 2, 'r': 2,
    's': 8, 't': 7, 'u': 5, 'v': 2, 'z': 1, 'õ': 2, 'ä': 2, 'ö': 2, 'ü': 2,
    'š': 1, 'ž': 1,  # eriklotssid
    '': 2,  # tühjad klotsid (wildcard)
}

VALID = set(SCORES.keys())

def word_score(w):
    return sum(SCORES.get(ch, 0) for ch in w)

def is_valid(w):
    """Ainult scrabble-tähed, ei tühik/sidekriips/number. Max 15 tähte. Iga tähe arv <= klotside arv mängus."""
    if not (bool(w) and len(w) <= 15 and all(ch in VALID for ch in w)):
        return False
    # Kontrolli, et iga tähe arv sõnas ei ületa klotsidest arvu mängus
    for ch in w:
        if w.count(ch) > TILE_COUNTS.get(ch, 0):
            return False
    return True

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
    'tile_counts': TILE_COUNTS,
    'total_valid': len(results),
}

with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False)

print(f'Eksporditud: top {len(top)} / {len(results)} sobivat sõna → {OUTPUT_JSON}')
if top:
    print(f'Parim: {top[0]["word"]} ({top[0]["score"]} punkti)')
