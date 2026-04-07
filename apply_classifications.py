#!/usr/bin/env python3
"""
Apply automatic classifications directly to fras.csv
Creates fras_classified.csv with unclassified expressions assigned to suggested categories
"""

import csv
import json

# Load suggestions
with open('fras_suggestions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    suggestions = data['suggestions']

# Load and process CSV
output_rows = []
with open('fras.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        keelend = row['keelend']
        is_unclassified = row['semantilised_tuubid'].strip() in ['NULL', '{}', '{NULL}', '']

        if is_unclassified and keelend in suggestions:
            # Use first suggestion
            suggested_types = suggestions[keelend]
            if suggested_types and suggested_types[0]:
                row['semantilised_tuubid'] = f"{{{suggested_types[0]}}}"

        output_rows.append(row)

# Write output
with open('fras_classified.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['word_id', 'keelend', 'keel', 'semantilised_tuubid', 'seletused'])
    writer.writeheader()
    writer.writerows(output_rows)

print("✓ Applied automatic classifications")
print(f"✓ Saved to fras_classified.csv")
print(f"✓ Total expressions with new classifications: {len(suggestions)}")
