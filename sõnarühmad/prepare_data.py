"""
Grupeerib kaashüponüümid klastritesse union-find abil.
Kaashüponüümid on sõnad mis jagavad sama ülemmõistet (nt herbivoor, karnivoor, taimetoiduline).
"""

import csv, json
from collections import defaultdict

CSV_FILE = "../data/sonavorgustik.csv"
JSON_FILE = "../data/sonarühmad.json"


class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px != py:
            self.parent[px] = py


uf = UnionFind()

with open(CSV_FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["meaning_rel_type_code"] == "kaashüponüüm":
            w1 = row["word1"].strip()
            w2 = row["word2"].strip()
            if w1 and w2:
                uf.union(w1, w2)

# grupeeri sõnad klastritesse
groups = defaultdict(set)
for word in uf.parent:
    root = uf.find(word)
    groups[root].add(word)

# sorteeri klastrid suuruse järgi, seejärel esimese sõna järgi
clusters = sorted(
    [sorted(words) for words in groups.values() if len(words) >= 2],
    key=lambda w: (-len(w), w[0])
)

with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump({"clusters": clusters}, f, ensure_ascii=False)

print(f"Klastreid kokku: {len(clusters)}")
print(f"Suurim klaster: {len(clusters[0])} sõna — {clusters[0][:5]}")
print(f"Salvestatud: {JSON_FILE}")
