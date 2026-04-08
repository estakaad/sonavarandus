"""
Ehitab registrite koosesinemismaatriksi.

Sisend: data/registers.csv
  Veerud: word, lexeme_id, register_code
  SQL: export_data.sql päring 5 (REGISTRID)

Väljund: data/registers.json
"""

import csv, json
from collections import defaultdict

CSV_FILE = "../data/registers.csv"
JSON_FILE = "../data/registers.json"

# Välja jäetavad registrid (kohanimega seotud, ajalooline ja ametlik)
EXCLUDE = {"koh", "mta", "teg", "aja", "ame"}  # kohalik, mitteametlik, tegelik (de facto), ajalooline, ametlik

# lekseemi → {word, registers: set}
lexemes = {}

with open(CSV_FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        reg_code = row["register_code"].strip()
        if reg_code in EXCLUDE:
            continue
        lid = row["lexeme_id"]
        if lid not in lexemes:
            lexemes[lid] = {"word": row["word"], "registers": set()}
        lexemes[lid]["registers"].add(reg_code)

# registrite kogusummad
totals = defaultdict(int)
# koosesinemine: (reg1, reg2) → count
cooc   = defaultdict(int)
# sõnad paari kohta (kõik sõnad)
pairs  = defaultdict(list)

for lid, data in lexemes.items():
    regs = sorted(data["registers"])
    word = data["word"]
    for r in regs:
        totals[r] += 1
    for i, r1 in enumerate(regs):
        for r2 in regs[i:]:
            key = f"{r1}|{r2}"
            cooc[key] += 1
            pairs[key].append(word)

# registrid sageduse järjekorras
registers = sorted(totals.keys(), key=lambda r: -totals[r])

# maatriks (sümmeetriline)
matrix = {}
for r1 in registers:
    matrix[r1] = {}
    for r2 in registers:
        key = f"{min(r1,r2)}|{max(r1,r2)}"
        matrix[r1][r2] = cooc.get(key, 0)

result = {
    "registers": [{"code": r, "total": totals[r]} for r in registers],
    "matrix": matrix,
    "pairs": {k: sorted(set(v)) for k, v in pairs.items()}
}

with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False)

print(f"Registreid: {len(registers)}")
print(f"Lekseeme kokku: {len(lexemes)}")
print(f"Top 10 registrit: {registers[:10]}")
print(f"Salvestatud: {JSON_FILE}")
