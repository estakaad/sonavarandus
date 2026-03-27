// BFS algoritm perekonnagraafis tee leidmiseks
// Tagastab annoteeritud sammude jada koos kontekstiinfoga

class PathFinder {
  constructor(graph) {
    this.graph = graph;
  }

  // Leiab lühima tee fromId -> toId
  // Tagastab: [{ fromId, toId, step, fromPerson, toPerson }] või null
  findPath(fromId, toId) {
    if (fromId === toId) return [];

    const visited = new Set([fromId]);
    // Järjekord: [currentId, teeAntud]
    const queue = [[fromId, []]];

    while (queue.length > 0) {
      const [currentId, path] = queue.shift();

      for (const { person: neighbor, step } of this.graph.getNeighbors(currentId)) {
        if (visited.has(neighbor.id)) continue;

        const newStep = {
          fromId: currentId,
          toId: neighbor.id,
          step,
          fromPerson: this.graph.persons.get(currentId),
          toPerson: neighbor,
        };
        const newPath = [...path, newStep];

        if (neighbor.id === toId) {
          return newPath;
        }

        visited.add(neighbor.id);
        queue.push([neighbor.id, newPath]);
      }
    }

    return null; // Teed ei leitud
  }

  // Teisendab tee sammude järjestuse lihtsaks stringijadaks ["P","C","S","Sp",...]
  // ja kogub kontekstiinfo (vahepealse isikute sood)
  analyzePath(path) {
    if (!path || path.length === 0) return null;

    const steps = path.map(s => s.step);
    const target = path[path.length - 1].toPerson;

    const context = {};

    // Lell vs onu: ["P","S"] - vahepealne vanem on path[0].toPerson
    if (steps.length >= 2 && steps[0] === "P" && steps[1] === "S") {
      context.parentGender = path[0].toPerson.gender;
    }

    // käli vs nadu: ["S","Sp"] - vahepealne õde/vend on path[0].toPerson
    if (steps.length >= 2 && steps[0] === "S" && steps[1] === "Sp") {
      context.siblingGender = path[0].toPerson.gender;
    }

    // vennapoeg vs õepoeg: ["S","C"] - vahepealne õde/vend on path[0].toPerson
    if (steps.length >= 2 && steps[0] === "S" && steps[1] === "C") {
      context.siblingGender = path[0].toPerson.gender;
    }

    // väi vs minia: ["C","Sp"] - vahepealne laps on path[0].toPerson
    if (steps.length >= 2 && steps[0] === "C" && steps[1] === "Sp") {
      context.childGender = path[0].toPerson.gender;
    }

    // nõbu täpsem: ["P","S","C"] - vahemae isiku sugu
    if (steps.length >= 2 && steps[0] === "P" && steps[1] === "S") {
      context.parentGender = path[0].toPerson.gender;
    }

    // Abikaasa sugu Sp→S teel: path[0].toPerson on abikaasa (vahepealne sõlm)
    // See eristab küdi (mehevend) vs nääl (naisevend) sõltumata küsija soost —
    // ka sama sooga abielupaarid saavad õige termini.
    if (steps.length >= 2 && steps[0] === "Sp") {
      context.spouseGender = path[0].toPerson.gender;
    }

    // Küsija sugu (muude eristuste jaoks)
    if (path.length > 0 && path[0].fromPerson) {
      context.requesterGender = path[0].fromPerson.gender;
    }

    return {
      steps,
      targetGender: target.gender,
      target,
      context,
      path,
    };
  }
}

if (typeof module !== "undefined") module.exports = { PathFinder };
