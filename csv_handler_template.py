"""
CSV andmete käitlemise template.
Kasuta seda erinevates prepare_data.py skriptides.

Kasutus:
  1. Kopeer base.csv, relations.csv jne oma mooduli /data/ kausta
  2. Kasuta siit näiteid, et need andmed lugeda
"""

import csv
from collections import defaultdict

# ============================================================
# NÄIDE 1: Sõnaredelid — base.csv kasutamine
# ============================================================

def load_words_from_csv(csv_file='data/base.csv'):
    """Loe sõnad base.csv-st."""
    words = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            word = row['value'].lower().strip()
            length = int(row['word_length'])
            # Filter: 3-8 tähe sõnad
            if 3 <= length <= 8 and word.isalpha() and all(c in 'abcdefghijklmnoprstuvwäöüõ' for c in word):
                words.append(word)
    return sorted(list(set(words)))


# ============================================================
# NÄIDE 2: Galaktika/sõnatee — relations.csv kasutamine
# ============================================================

def load_relations_from_csv(csv_file='data/relations.csv'):
    """Loe tähenduste seosed relations.csv-st."""
    graph = defaultdict(set)
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            word1 = row['word1'].lower()
            word2 = row['word2'].lower()
            rel_type = row['meaning_rel_type_code']
            # Mõlemad suunad
            graph[word1].add((word2, rel_type))
            graph[word2].add((word1, rel_type))
    # Konverdi set-id list-ideks
    return {w: list(ns) for w, ns in graph.items()}


# ============================================================
# NÄIDE 3: Liitsõnasild — compounds.csv kasutamine
# ============================================================

def load_compounds_from_csv(csv_file='data/compounds.csv'):
    """Loe liitsõnad compounds.csv-st."""
    graph = defaultdict(list)
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            compound = row['liitsona'].lower()
            prefix = row['esiosa'].lower()
            suffix = row['jarelosa'].lower()
            # Mõlemad suunad
            graph[prefix].append({'via': compound, 'to': suffix})
            graph[suffix].append({'via': compound, 'to': prefix})
    return dict(graph)


# ============================================================
# NÄIDE 4: Polüseemia — polysemy.csv kasutamine
# ============================================================

def load_polysemy_from_csv(csv_file='data/polysemy.csv'):
    """Loe polüseemiat polysemy.csv-st."""
    words = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            words.append({
                'word': row['word'].lower(),
                'meaning_count': int(row['meaning_count'])
            })
    # Sorteeri tähenduste arvu järgi
    return sorted(words, key=lambda x: -x['meaning_count'])


# ============================================================
# NÄIDE 5: Registrid — word_registers.csv kasutamine
# ============================================================

def load_registers_from_csv(csv_file='data/word_registers.csv'):
    """Loe registrid word_registers.csv-st."""
    word_regs = defaultdict(set)
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            word = row['word'].lower()
            reg = row['word_register_code']
            word_regs[word].add(reg)
    return {w: list(rs) for w, rs in word_regs.items()}


# ============================================================
# NÄIDE 6: Tuletusliited — derivation.csv kasutamine
# ============================================================

def load_derivation_from_csv(csv_file='data/derivation.csv'):
    """Loe tuletusliiteid derivation.csv-st."""
    graph = defaultdict(list)
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            base = row['base_word'].lower()
            derived = row['derived_word'].lower()
            rel_type = row['word_rel_type_code']
            graph[base].append({
                'derived': derived,
                'type': rel_type
            })
    return dict(graph)


# ============================================================
# NÄIDE 7: Minimaalpaarid — base.csv kasutamine
# ============================================================

def load_minimal_pairs_from_csv(csv_file='data/base.csv'):
    """
    Loe sõnad ja leia minimaalpaarid.
    Minimaalpaarid = sama pikkus, erinevad ühe tähe poolest samal positsioonil.
    """
    from collections import defaultdict

    words = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            word = row['value'].lower().strip()
            if word.isalpha():
                words.append(word)

    pairs = []
    by_length = defaultdict(list)

    # Grupeeri pikkuse järgi
    for word in words:
        by_length[len(word)].append(word)

    # Leia minimaalpaarid (pattern-bucket meetod)
    for length, words_of_len in by_length.items():
        buckets = defaultdict(list)
        for word in words_of_len:
            for i in range(length):
                pattern = word[:i] + '_' + word[i+1:]
                buckets[pattern].append(word)

        # Bucketis olevad sõnad erinevad ühe tähe poolest
        for pattern, bucket_words in buckets.items():
            if len(bucket_words) >= 2:
                for i in range(len(bucket_words)):
                    for j in range(i + 1, len(bucket_words)):
                        pairs.append({
                            'a': bucket_words[i],
                            'b': bucket_words[j],
                            'position': pattern.index('_'),
                            'length': length
                        })

    return pairs


# ============================================================
# KASUTUSE NÄITED
# ============================================================

if __name__ == '__main__':
    # Sõnaredelid
    # words = load_words_from_csv('data/base.csv')
    # print(f"Sõnaredelite sõnad: {len(words)}")

    # Galaktika
    # graph = load_relations_from_csv('data/relations.csv')
    # print(f"Tähenduste seosed: {sum(len(ns) for ns in graph.values())}")

    # Liitsõnasild
    # compounds = load_compounds_from_csv('data/compounds.csv')
    # print(f"Liitsõna komponendid: {len(compounds)}")

    # Polüseemia
    # polysemy = load_polysemy_from_csv('data/polysemy.csv')
    # print(f"Polüseemiad: {polysemy[:5]}")

    # Registrid
    # regs = load_registers_from_csv('data/word_registers.csv')
    # print(f"Sõnad registritega: {len(regs)}")

    # Minimaalpaarid
    # pairs = load_minimal_pairs_from_csv('data/base.csv')
    # print(f"Minimaalpaarid: {len(pairs)}")

    pass
