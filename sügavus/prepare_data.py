"""
Liitsõnade pesastussügavuse andmete ettevalmistus.

Sisend:  ../liitsõnasild/data/compounds_raw.csv
Väljund: data/depth.json

Algoritm: iga liitsõna sügavus = 1 + max(esiosa sügavus, järelosa sügavus).
Leiame sügavaima ahela iga liitsõna jaoks (memoiseering + tsüklituvastus).
"""

import csv, json, sys
from collections import defaultdict

sys.setrecursionlimit(300000)

INPUT_CSV   = '../liitsõnasild/data/compounds_raw.csv'
OUTPUT_JSON = 'data/depth.json'
TOP_N       = 300   # sügavaimate ahelate arv väljundis
MAX_CHILDREN = 60  # max järglasi ühe sõna kohta puu-kaardis

# ── loe sisend ────────────────────────────────────────────────
compound_parts = {}  # liitsõna → (esiosa, järelosa)

with open(INPUT_CSV, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    cols = reader.fieldnames
    # handle both liitsona/liitsõna etc.
    ls_col = next(c for c in cols if 'liits' in c.lower())
    e_col  = next(c for c in cols if c.lower() == 'esiosa')
    j_col  = next(c for c in cols if 'osa' in c.lower() and c != e_col)
    for row in reader:
        ls = row[ls_col].strip()
        e  = row[e_col].strip()
        j  = row[j_col].strip()
        if ls and e and j and ls != e and ls != j:
            compound_parts[ls] = (e, j)

print(f'Loetud: {len(compound_parts)} liitsõna')

# ── komponent → liitsõnad ─────────────────────────────────────
comp_to_compounds = defaultdict(list)
for compound, (e, j) in compound_parts.items():
    comp_to_compounds[e].append(compound)
    comp_to_compounds[j].append(compound)

# ── sügavus + parim ahel (memoiseering) ───────────────────────
memo       = {}
in_progress = set()

def get_depth_chain(word):
    if word in memo:
        return memo[word]
    if word in in_progress:          # tsükkel — lõpeta
        return (1, [word])
    in_progress.add(word)

    if word not in compound_parts:
        result = (1, [word])
    else:
        e, j = compound_parts[word]
        d_e, chain_e = get_depth_chain(e)
        d_j, chain_j = get_depth_chain(j)
        best = chain_e if d_e >= d_j else chain_j
        result = (max(d_e, d_j) + 1, best + [word])

    in_progress.discard(word)
    memo[word] = result
    return result

print('Arvutan sügavust...')
all_results = []
for compound in compound_parts:
    depth, chain = get_depth_chain(compound)
    if depth >= 3:                   # vähem huvitavad jätame välja
        all_results.append((depth, chain))

all_results.sort(key=lambda x: -x[0])

# Deduplika — iga liitsõna esindub ainult üks kord (kõige pikem ahel)
seen = set()
top_chains = []
for depth, chain in all_results:
    end = chain[-1]
    if end not in seen:
        seen.add(end)
        top_chains.append({'depth': depth, 'chain': chain})
    if len(top_chains) >= TOP_N:
        break

# ── puu-kaart (compound_map) ──────────────────────────────────
# Sisaldab kõik sõnad mis esinevad top_chains-is + nende lapsed
interesting = set()
for item in top_chains:
    for w in item['chain']:
        interesting.add(w)

compound_map = {}
for word in interesting:
    children = sorted(comp_to_compounds.get(word, []))
    if children:
        compound_map[word] = children[:MAX_CHILDREN]

# ── salvesta ─────────────────────────────────────────────────
result = {'top_chains': top_chains, 'compound_map': compound_map}
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)

max_d = top_chains[0]['depth'] if top_chains else 0
print(f'Eksporditud: {len(top_chains)} ahelat, max sügavus {max_d} → {OUTPUT_JSON}')
