#!/usr/bin/env python3
"""
Prepare fraseological expressions data for treemap visualization.
Filters to only classified expressions, groups by category.
"""

import csv
import json
from collections import defaultdict

# Load CSV
expressions = []
with open('../fras.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        expressions.append(row)

# Filter to only classified
classified = [e for e in expressions if e['semantilised_tuubid'].strip() not in ['NULL', '{}', '{NULL}', '']]

print(f"Total: {len(expressions)}")
print(f"Classified: {len(classified)}")

# Group by category
categories = defaultdict(list)

for e in classified:
    sem_type = e['semantilised_tuubid'].strip('{}')
    # Use first type if multiple
    main_type = sem_type.split(',')[0].split('(nt')[0].strip() if sem_type else 'Teadmata'

    categories[main_type].append({
        'id': e['word_id'],
        'keelend': e['keelend'],
        'seletused': e['seletused'].strip('{}')
    })

# Sort categories by count
sorted_cats = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)

print(f"\nTop 10 categories:")
for cat, items in sorted_cats[:10]:
    print(f"  {len(items):3d}  {cat}")

# Create color palette (HSL for better distribution)
def hsl_to_hex(h, s, l):
    import colorsys
    h = h / 360.0
    s = s / 100.0
    l = l / 100.0
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

colors = {}
for i, (cat, _) in enumerate(sorted_cats):
    hue = (i * 360 / len(sorted_cats)) % 360
    colors[cat] = hsl_to_hex(hue, 70, 60)

# Prepare output for treemap
categories_data = []
for cat, items in sorted_cats:
    categories_data.append({
        'name': cat,
        'count': len(items),
        'color': colors[cat],
        'expressions': [
            {
                'id': item['id'],
                'keelend': item['keelend'],
                'seletused': item['seletused']
            }
            for item in items
        ]
    })

data = {
    'categories': categories_data,
    'total': len(classified),
    'categoryCount': len(categories)
}

# Save
with open('../data/fraseoloogilised.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nOutput: {len(classified)} expressions across {len(categories)} categories")
print(f"Saved to data/fraseoloogilised.json")
