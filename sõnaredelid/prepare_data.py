"""
Ehitab sõnaredelite andmestiku.

Kasutab Ekilex sõnastikust väljundit:
  SELECT DISTINCT value FROM word
  WHERE lang = 'est' AND is_public = true AND length(value) BETWEEN 3 AND 8
  ORDER BY value;

Väljund: data/ladder.json
  Sõnaredelid on samapikkused sõnad, mis erinevad vaid ühe tähe poolest.
  Näide: kala → kana → kuna → küna
"""

import json, re
from collections import defaultdict, deque

INPUT_TXT = "../data/words_raw.txt"
OUTPUT_JSON = "data/ladder.json"

# Eesti tähestik (ilma q, w, x, y-ta, mida eesti keeles poliitikas)
ESTONIAN_PATTERN = r"^[a-züõäö]+$"

def load_words():
    try:
        with open(INPUT_TXT, "r", encoding="utf-8") as f:
            words = [line.strip().lower() for line in f]
            # Filter: eesti tähed, pikkus 3-8
            words = [w for w in words if re.match(ESTONIAN_PATTERN, w) and 3 <= len(w) <= 8]
            return words
    except FileNotFoundError:
        print(f"❌ {INPUT_TXT} ei leitud")
        return []

def build_graph(words):
    """
    Pattern bucket meetod: O(n × L) asemel O(n²).
    Kaks sõna on naaber, kui nad erinevad täpselt ühe tähe poolest.
    """
    graph_by_length = defaultdict(lambda: defaultdict(list))

    for word in words:
        length = len(word)
        for i in range(length):
            pattern = word[:i] + "_" + word[i+1:]
            graph_by_length[length][pattern].append(word)

    # Ehita sidusus: bucketis olevad sõnad = naabrid
    graph = defaultdict(set)
    edges = 0
    for length, buckets in graph_by_length.items():
        for pattern, words_in_bucket in buckets.items():
            if len(words_in_bucket) >= 2:
                for w in words_in_bucket:
                    for neighbor in words_in_bucket:
                        if w != neighbor and neighbor not in graph[w]:
                            graph[w].add(neighbor)
                            edges += 1

    return {w: sorted(list(ns)) for w, ns in graph.items()}, edges

def bfs_farthest(graph, start):
    """BFS start-sõnast, tagasta kõige kaugemal olev sõna ja vahemaa."""
    dist = {start: 0}
    parent = {start: None}
    queue = deque([start])
    farthest, max_dist = start, 0

    while queue:
        cur = queue.popleft()
        for nb in graph.get(cur, []):
            if nb not in dist:
                dist[nb] = dist[cur] + 1
                parent[nb] = cur
                queue.append(nb)
                if dist[nb] > max_dist:
                    max_dist = dist[nb]
                    farthest = nb

    return farthest, max_dist, parent

def reconstruct_path(parent, start, end):
    """Taastada teekond start → end kasutades parent-kaardi."""
    path = []
    cur = end
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    return list(reversed(path))

def find_longest_ladder(graph, words):
    """
    Leia pikim ahel (diameter) graafis.
    Tsikliga läbi iga sõna, jooksutades BFS-i, ja jälgi globaalset parimat.
    """
    by_length = defaultdict(list)
    for w in words:
        by_length[len(w)].append(w)

    best = {"distance": 0, "from": None, "to": None, "path": [], "start": None}

    for length in sorted(by_length.keys()):
        group = by_length[length]
        print(f"  Pikkus {length}: {len(group)} sõna", end="", flush=True)

        # Eelkontroll: kas graafis on üle 1 sõna selle pikkusega?
        connected = [w for w in group if w in graph]
        if len(connected) < 2:
            print(" → pole seotud")
            continue

        for start in connected:
            farthest, dist, parent = bfs_farthest(graph, start)
            if dist > best["distance"]:
                path = reconstruct_path(parent, start, farthest)
                best["distance"] = dist
                best["from"] = start
                best["to"] = farthest
                best["path"] = path
                best["start"] = start

        print(f" → parim {best['distance']} sammu" if best["start"] == group[0] or best["start"] is None else "")

    return {
        "from": best["from"],
        "to": best["to"],
        "path": best["path"],
        "steps": best["distance"]
    }

def main():
    print("Laadin sõnu...")
    words = load_words()
    if not words:
        print("⚠️ Sõnu ei laaditud")
        return

    print(f"✓ Laaditud {len(words)} sõna")

    print("Ehitan graafi (pattern-bucket meetod)...")
    graph, edges = build_graph(words)

    connected_words = sorted(graph.keys())
    print(f"✓ {len(connected_words)} sõna vähemalt ühe naabriga")
    print(f"✓ Kogu {edges} seost")

    print("Otsin pikemat redelit...")
    longest = find_longest_ladder(graph, connected_words)
    print(f"✓ Pikim redel: {' → '.join(longest['path'])} ({longest['steps']} sammu)")

    # JSON väljund
    output = {
        "words": connected_words,
        "graph": graph,
        "longest": longest,
        "stats": {
            "total_words": len(connected_words),
            "edges": edges
        }
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✓ Salvestatud: {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
