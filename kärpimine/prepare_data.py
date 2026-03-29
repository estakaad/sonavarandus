"""
Kärpimisahelate ettevalmistus.
Beheadment: sõna mille esimese tähe mahavõtmine annab uue sõna, ja nii edasi.
Nt: kraad → raad → aad

Sisend:  ../anagrammid/data/anagrams_raw.csv  (veerg: value)
Väljund: data/beheadments.json
"""

import csv, json

INPUT_CSV   = '../anagrammid/data/anagrams_raw.csv'
OUTPUT_JSON = 'data/beheadments.json'
MIN_CHAIN   = 3   # minimaalne ahela pikkus
TOP_N       = 300

words = set()
with open(INPUT_CSV, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        w = row['value'].strip().lower()
        if w:
            words.add(w)

def follow_chain(word):
    chain = [word]
    cur = word
    while len(cur) > 1:
        cur = cur[1:]
        if cur in words:
            chain.append(cur)
        else:
            break
    return chain

# Leia kõige pikemad ahelad — alusta pikematest sõnadest
all_chains = []
seen_heads = set()

for w in sorted(words, key=lambda x: -len(x)):
    if w in seen_heads:
        continue
    chain = follow_chain(w)
    if len(chain) >= MIN_CHAIN:
        all_chains.append({'depth': len(chain), 'chain': chain})
        for word in chain:
            seen_heads.add(word)

all_chains.sort(key=lambda c: (-c['depth'], c['chain'][0]))
top = all_chains[:TOP_N]

result = {'chains': top, 'total': len(all_chains)}
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)

print(f'Eksporditud: {len(top)} / {len(all_chains)} ahelat → {OUTPUT_JSON}')
if top:
    c = top[0]
    print(f'Pikim ({c["depth"]}): {" → ".join(c["chain"])}')
