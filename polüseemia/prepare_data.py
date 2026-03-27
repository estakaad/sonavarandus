"""
Töötleb polüseemia andmeid: sõnad → tähendused → semantilised tüübid + seletused.

Sisend: data/polysemy_raw.csv
  Veerud: word, meaning_id, semantic_types (koma-eraldatud), definition

Väljund: data/polysemy.json

SQL Dbeaveris (ekspordi CSV-na nimega polysemy_raw.csv):

  Iga rida = üks tähendus (meaning_id). Skript loeb kokku mitu tähendust sõnal on.
  meaning_count on ainult kontrolliks — skript arvutab selle ise ümber.

    SELECT
        w.value AS word,
        l.meaning_id,
        COUNT(*) OVER (PARTITION BY w.value) AS meaning_count,
        string_agg(mst.semantic_type_code, ',' ORDER BY mst.order_by) AS semantic_types,
        (SELECT d.value
         FROM definition d
         JOIN definition_dataset dd ON dd.definition_id = d.id AND dd.dataset_code = 'eki'
         WHERE d.meaning_id = l.meaning_id
           AND d.lang = 'est'
           AND d.is_public = true
         ORDER BY d.order_by
         LIMIT 1) AS definition
    FROM word w
    JOIN lexeme l ON l.word_id = w.id
        AND l.dataset_code = 'eki'
        AND l.is_public = true
        AND l.is_collocation IS NOT TRUE
    LEFT JOIN meaning_semantic_type mst ON mst.meaning_id = l.meaning_id
    WHERE w.lang = 'est'
      AND w.is_public = true
      AND w.value NOT LIKE '% %'
    GROUP BY w.value, l.meaning_id
    ORDER BY meaning_count DESC, w.value, l.meaning_id;
"""

import csv, json
from collections import defaultdict, OrderedDict

CSV_FILE = "data/polysemy_raw.csv"
JSON_FILE = "data/polysemy.json"

words = defaultdict(lambda: {"meanings": OrderedDict()})

with open(CSV_FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        word = row["word"].strip()
        meaning_id = row["meaning_id"].strip()
        types_raw = row.get("semantic_types", "").strip()
        types = [t.strip() for t in types_raw.split(",") if t.strip()] if types_raw else []
        definition = row.get("definition", "").strip()

        if meaning_id not in words[word]["meanings"]:
            words[word]["meanings"][meaning_id] = {"types": types, "def": definition}

result = []
all_types = set()

for word, data in words.items():
    meanings = list(data["meanings"].values())
    for m in meanings:
        all_types.update(m["types"])
    result.append({
        "word": word,
        "count": len(meanings),
        "meanings": meanings
    })

result.sort(key=lambda x: -x["count"])

with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump({"words": result, "types": sorted(all_types)}, f, ensure_ascii=False)

print(f"Sõnu kokku: {len(result)}")
print(f"Mitmemõttelisi (2+ tähendust): {sum(1 for x in result if x['count'] > 1)}")
print(f"Max tähendusi: {result[0]['count']} ({result[0]['word']})")
print(f"Semantilised tüübid ({len(all_types)}): {', '.join(sorted(all_types))}")
print(f"Salvestatud: {JSON_FILE}")
