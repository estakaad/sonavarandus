"""
Ehitab liitsõnasilla andmestiku.

Sisend: data/compounds_raw.csv
  Veerud: liitsona, esiosa, jarelosa

SQL DBeaveris (ekspordi CSV-na nimega compounds_raw.csv):

    SELECT
        wc.value AS liitsona,
        we.value AS esiosa,
        wj.value AS jarelosa
    FROM word wc
    JOIN word_relation re ON re.word1_id = wc.id AND re.word_rel_type_code = 'ls-esiosa'
    JOIN word we ON we.id = re.word2_id
    JOIN word_relation rj ON rj.word1_id = wc.id AND rj.word_rel_type_code = 'ls-järelosa'
    JOIN word wj ON wj.id = rj.word2_id
    WHERE wc.lang = 'est' AND wc.is_public = true
      AND we.lang = 'est' AND wj.lang = 'est'
    ORDER BY wc.value;

Väljund: data/compounds.json
"""

import csv, json
from collections import defaultdict

CSV_FILE = "data/compounds_raw.csv"
JSON_FILE = "data/compounds.json"

# word -> set of (via, to) tuples
raw = defaultdict(set)

with open(CSV_FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        liitsona  = row["liitsona"].strip()
        esiosa    = row["esiosa"].strip()
        jarelosa  = row["jarelosa"].strip()
        if not liitsona or not esiosa or not jarelosa:
            continue
        raw[esiosa].add((liitsona, jarelosa))
        raw[jarelosa].add((liitsona, esiosa))

# Konverdi listi ja sorteeri
graph = {}
for word, edges in raw.items():
    graph[word] = sorted(
        [{"via": via, "to": to} for via, to in edges],
        key=lambda x: x["via"]
    )

# Mängitavad sõnad: need mis esinevad vähemalt 2 liitsõnas
# (et ei oleks kohe tupik startsõnana/sihtmärgina)
playable = sorted(w for w, edges in graph.items() if len(edges) >= 2)

result = {
    "graph":    graph,
    "playable": playable,
}

with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False)

print(f"Komponentsõnu kokku:  {len(graph)}")
print(f"Mängitavaid sõnu:     {len(playable)}")
print(f"Salvestatud: {JSON_FILE}")
