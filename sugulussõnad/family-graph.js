// Perekonnagraafi andmestruktuur
// Primitiivsed seosed: parent (A on B vanem) ja spouse (A on B abikaasa)
// Kõik teised seosed (sibling, child jne) tuletatakse

class FamilyGraph {
  constructor() {
    this.persons = new Map();   // id -> PersonNode
    this.relations = new Map(); // id -> RelationEdge
  }

  // ── Isikud ────────────────────────────────────────

  addPerson({ id, name, gender = "unknown", birthYear = null, notes = "" }) {
    const person = { id, name, gender, birthYear, notes };
    this.persons.set(id, person);
    return person;
  }

  updatePerson(id, updates) {
    const p = this.persons.get(id);
    if (!p) return null;
    Object.assign(p, updates);
    return p;
  }

  deletePerson(id) {
    this.persons.delete(id);
    // Kustuta kõik seosed selle isikuga
    for (const [rid, rel] of this.relations) {
      if (rel.from === id || rel.to === id) {
        this.relations.delete(rid);
      }
    }
  }

  // ── Seosed ────────────────────────────────────────

  // type: "parent" (from on to vanem) | "spouse" (from on to abikaasa)
  addRelation({ id, from, to, type }) {
    const rel = { id, from, to, type };
    this.relations.set(id, rel);
    return rel;
  }

  deleteRelation(id) {
    this.relations.delete(id);
  }

  // ── Päringud ──────────────────────────────────────

  getParents(personId) {
    // Leia kõik kus type=parent ja to=personId (A on personId vanem)
    const parents = [];
    for (const rel of this.relations.values()) {
      if (rel.type === "parent" && rel.to === personId) {
        const p = this.persons.get(rel.from);
        if (p) parents.push(p);
      }
    }
    return parents;
  }

  getChildren(personId) {
    // Leia kõik kus type=parent ja from=personId (personId on A vanem)
    const children = [];
    for (const rel of this.relations.values()) {
      if (rel.type === "parent" && rel.from === personId) {
        const p = this.persons.get(rel.to);
        if (p) children.push(p);
      }
    }
    return children;
  }

  getSpouses(personId) {
    const spouses = [];
    for (const rel of this.relations.values()) {
      if (rel.type === "spouse") {
        if (rel.from === personId) {
          const p = this.persons.get(rel.to);
          if (p) spouses.push(p);
        } else if (rel.to === personId) {
          const p = this.persons.get(rel.from);
          if (p) spouses.push(p);
        }
      }
    }
    return spouses;
  }

  getSiblings(personId) {
    const siblingIds = new Set();
    // Tuletatavad õed-vennad (ühise vanema kaudu)
    const parents = this.getParents(personId);
    for (const parent of parents) {
      for (const child of this.getChildren(parent.id)) {
        if (child.id !== personId) siblingIds.add(child.id);
      }
    }
    // Otsesed sibling-seosed
    for (const rel of this.relations.values()) {
      if (rel.type === "sibling") {
        if (rel.from === personId) siblingIds.add(rel.to);
        else if (rel.to === personId) siblingIds.add(rel.from);
      }
    }
    return [...siblingIds].map(id => this.persons.get(id)).filter(Boolean);
  }

  // Kõik naabrid koos seose tüübiga
  getNeighbors(personId) {
    const neighbors = [];

    for (const p of this.getParents(personId)) {
      neighbors.push({ person: p, step: "P" });
    }
    for (const c of this.getChildren(personId)) {
      neighbors.push({ person: c, step: "C" });
    }
    for (const s of this.getSpouses(personId)) {
      neighbors.push({ person: s, step: "Sp" });
    }
    for (const s of this.getSiblings(personId)) {
      neighbors.push({ person: s, step: "S" });
    }

    return neighbors;
  }

  // ── Serialiseerimine ──────────────────────────────

  toJSON() {
    return {
      version: 1,
      persons: [...this.persons.values()],
      relations: [...this.relations.values()],
    };
  }

  static fromJSON(data) {
    const g = new FamilyGraph();
    for (const p of data.persons || []) g.persons.set(p.id, p);
    for (const r of data.relations || []) g.relations.set(r.id, r);
    return g;
  }
}

if (typeof module !== "undefined") module.exports = { FamilyGraph };
