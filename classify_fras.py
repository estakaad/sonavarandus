#!/usr/bin/env python3
"""
Automatically classify unclassified phraseological expressions in fras.csv
based on their explanations and semantic patterns from classified expressions.
"""

import csv
import json
from collections import defaultdict
import re

# Load the CSV
expressions = []
with open('fras.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        expressions.append(row)

# Separate classified and unclassified
classified = [e for e in expressions if e['semantilised_tuubid'].strip() not in ['NULL', '{}', '{NULL}', '']]
unclassified = [e for e in expressions if e['semantilised_tuubid'].strip() in ['NULL', '{}', '{NULL}', '']]

print(f"Total: {len(expressions)} | Classified: {len(classified)} | Unclassified: {len(unclassified)}")
print()

# Extract and analyze semantic types
type_keywords = defaultdict(lambda: {'count': 0, 'keywords': set(), 'examples': []})

for e in classified:
    types_str = e['semantilised_tuubid'].strip('{}')
    # Parse multiple types if present
    types_list = [t.strip() for t in types_str.split(',') if t.strip()]

    for sem_type in types_list:
        # Split off the "(nt ...)" examples part
        base_type = sem_type.split('(nt')[0].strip() if '(nt' in sem_type else sem_type

        type_keywords[base_type]['count'] += 1

        # Extract keywords from explanation
        explanation = e['seletused'].lower().replace('{', '').replace('}', '')
        words = re.findall(r'\b\w+\b', explanation)

        # Filter to meaningful words (length > 2, exclude common Estonian words)
        stop_words = {'et', 'ja', 'või', 'jne', 'nt', 'jms', 'on', 'on', 'on', 'kohta', 'kus', 'see', 'selle',
                      'seda', 'kellegi', 'millegi', 'midagi', 'kes', 'mis', 'kui', 'kui', 'siis', 'see',
                      'see', 'seda', 'selles', 'sellest', 'kelle', 'mille', 'kuidas', 'kuhu', 'kust',
                      'mingi', 'igale', 'igal', 'igaks', 'ei', 'ka', 'ju', 'ju', 'da', 'ta'}

        for w in words:
            if len(w) > 2 and w not in stop_words and not w.isdigit():
                type_keywords[base_type]['keywords'].add(w)

        if len(type_keywords[base_type]['examples']) < 2:
            type_keywords[base_type]['examples'].append((e['keelend'], explanation[:60]))

# Show the semantic types and their keyword patterns
print("Semantic type patterns (sorted by frequency):")
for sem_type, data in sorted(type_keywords.items(), key=lambda x: x[1]['count'], reverse=True)[:15]:
    print(f"\n{data['count']:3d}  {sem_type}")
    print(f"    Keywords: {', '.join(sorted(list(data['keywords'])[:10]))}")
    print(f"    Examples: {data['examples'][0][0]}")

print("\n" + "="*80)
print("AUTOMATIC CLASSIFICATION RESULTS")
print("="*80)

# Classify unclassified expressions
def find_best_type(explanation, type_keywords):
    """Find the best matching semantic type(s) for an explanation."""
    explanation_lower = explanation.lower()
    scores = {}

    for sem_type, data in type_keywords.items():
        score = 0
        # Match keywords
        for keyword in data['keywords']:
            if keyword in explanation_lower:
                score += 1

        # Type pattern matching (hardcoded heuristics)
        if 'olek' in sem_type and any(w in explanation_lower for w in ['seisus', 'olukorras', 'seisundis', 'peal', 'all', 'sees']):
            score += 3
        if 'suhtlusüksus' in sem_type and any(w in explanation_lower for w in ['väljendab', 'öeldakse', 'väljendusel', 'hüüatus']):
            score += 3
        if 'tegevus' in sem_type and any(w in explanation_lower for w in ['tegemist', 'tegema', 'tegemas', 'teda']):
            score += 3
        if 'omadus' in sem_type and any(w in explanation_lower for w in ['omadus', 'iseloom', 'loomult', 'olemuslik', 'karakte']):
            score += 3
        if 'psüühika' in sem_type and any(w in explanation_lower for w in ['mõtte', 'tunne', 'kujutelu', 'teadvus', 'aru']):
            score += 3
        if 'ajalõik' in sem_type and any(w in explanation_lower for w in ['aeg', 'aasta', 'kestus', 'alati', 'igal']):
            score += 3
        if 'entiteet' in sem_type and any(w in explanation_lower for w in ['vahend', 'süsteem', 'meetod', 'tee', 'lahendus']):
            score += 3

        if score > 0:
            scores[sem_type] = score

    if not scores:
        return None

    # Return top 1-2 matches
    top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]
    return [t[0] for t in top if t[1] > 0]

# Classify
suggested = []
for e in unclassified:
    explanation = e.get('seletused', '').replace('{', '').replace('}', '')
    if explanation.strip():
        matches = find_best_type(explanation, type_keywords)
        if matches:
            suggested.append({
                'keelend': e['keelend'],
                'seletused': explanation,
                'suggested_types': matches
            })

# Show sample results
print(f"\nProcessed {len(suggested)} unclassified expressions with suggestions:\n")
for item in suggested[:15]:
    print(f"• {item['keelend']}")
    print(f"  Explanation: {item['seletused'][:80]}")
    print(f"  Suggested: {', '.join(item['suggested_types'])}")
    print()

# Save enriched CSV
output_data = []
type_suggestions = {}

for e in unclassified:
    explanation = e['seletused'].replace('{', '').replace('}', '')
    if explanation.strip():
        matches = find_best_type(explanation, type_keywords)
        type_suggestions[e['keelend']] = matches

# Output for review
print("="*80)
print(f"Total unclassified with suggestions: {len(type_suggestions)}")
print(f"Total still unclassified (empty explanation or no matches): {len(unclassified) - len(type_suggestions)}")

# Save suggestion file for manual review
with open('fras_suggestions.json', 'w', encoding='utf-8') as f:
    json.dump({
        'summary': {
            'total': len(expressions),
            'classified': len(classified),
            'unclassified': len(unclassified),
            'suggested': len(type_suggestions)
        },
        'suggestions': type_suggestions
    }, f, indent=2, ensure_ascii=False)

print(f"\nSuggestions saved to fras_suggestions.json")
print("Next step: Manual review and refinement")
