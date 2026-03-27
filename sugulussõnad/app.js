// Rakenduse peamine loogika — vis.js versioon

// Helper: Isiku label (hetkel lihtsalt nimi, kuid valmis tulevaste eristusteks)
function personLabel(p) {
  return p.name;
}

const STORAGE_KEY = "sugulussõnad_v1";
let graph = new FamilyGraph();
let network = null;
let nodesDS = null;
let edgesDS = null;
let editingPersonId = null;
let selectedRelType = "parent";
let activeNodeId = null;
let inlineCtx = null;

// ── Initsialiseerimine ────────────────────────────────────

function graphToHash(data) {
  return btoa(unescape(encodeURIComponent(JSON.stringify(data))));
}

function hashToGraph(hash) {
  return JSON.parse(decodeURIComponent(escape(atob(hash))));
}

function init() {
  const hash = window.location.hash.slice(1); // eemalda '#'

  if (hash) {
    try {
      graph = FamilyGraph.fromJSON(hashToGraph(hash));
      // Eemalda hash URL-ist ilma lehe uuendamiseta
      history.replaceState(null, '', window.location.pathname);
      showToast("Jagatud perekond laaditud!");
    } catch (e) {
      graph = FamilyGraph.fromJSON(DEMO_DATA);
      showToast("Linki ei saanud laadida, näidisandmed kasutatud.");
    }
  } else {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try { graph = FamilyGraph.fromJSON(JSON.parse(saved)); }
      catch (e) { graph = FamilyGraph.fromJSON(DEMO_DATA); }
    } else {
      graph = FamilyGraph.fromJSON(DEMO_DATA);
    }
  }
  renderAll();
}

function resetToDemo() {
  if (!confirm("Asenda praegused andmed näidisperekonnaga?")) return;
  graph = FamilyGraph.fromJSON(DEMO_DATA);
  destroyNetwork();
  saveToStorage(); renderAll();
  showToast("Näidisandmed laaditud!");
}

function clearAll() {
  if (!confirm("Kustuta kõik inimesed ja seosed? Seda ei saa tagasi võtta.")) return;
  graph = new FamilyGraph();
  destroyNetwork();
  saveToStorage(); renderAll();
  showToast("Kõik kustutatud.");
}

function destroyNetwork() {
  if (network) { network.destroy(); network = null; nodesDS = null; edgesDS = null; }
}

function saveToStorage() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(graph.toJSON()));
}

// ── Renderdumine ──────────────────────────────────────────

function renderAll() {
  renderGraph();
  renderExamples();
  renderQueryDropdowns();
  runQuery();
}

// ── vis.js graaf ──────────────────────────────────────────

function makeVisNode(p) {
  const m = p.gender === 'male', f = p.gender === 'female';
  return {
    id: p.id,
    label: p.birthYear ? `${p.name}\n(${p.birthYear})` : p.name,
    shape: m ? 'box' : f ? 'ellipse' : 'diamond',
    color: {
      background: m ? '#3b82f6' : f ? '#ec4899' : '#94a3b8',
      border:     m ? '#2563eb' : f ? '#db2777' : '#64748b',
      highlight: {
        background: m ? '#93c5fd' : f ? '#f9a8d4' : '#cbd5e1',
        border: '#6366f1',
      },
    },
    font: { color: '#fff', face: 'Inter, system-ui, sans-serif', size: 13 },
    borderWidth: 1,
    borderWidthSelected: 3,
    margin: 10,
  };
}

function makeVisEdge(rel) {
  if (rel.type === 'parent') {
    return {
      id: rel.id, from: rel.from, to: rel.to,
      arrows: { to: { enabled: true, scaleFactor: 0.7 } },
      color: { color: '#3b82f6', opacity: 0.9 },
      width: 3,
      length: 160,
      label: '↓',
      font: { size: 16, color: '#3b82f6', face: 'Inter', background: 'white', strokeWidth: 0 },
      smooth: { type: 'curvedCW', roundness: 0.1 },
    };
  }
  if (rel.type === 'spouse') {
    return {
      id: rel.id, from: rel.from, to: rel.to,
      arrows: { to: { enabled: false } },
      color: { color: '#ec4899', opacity: 0.85 },
      dashes: [8, 4], width: 2,
      label: '♥',
      length: 80,
      font: { size: 18, color: '#ec4899', face: 'Inter', background: 'white', strokeWidth: 0 },
      smooth: { type: 'curvedCW', roundness: 0.1 },
    };
  }
  // sibling (subtle)
  return {
    id: rel.id, from: rel.from, to: rel.to,
    arrows: { to: { enabled: false } },
    color: { color: '#d8b4fe', opacity: 0.5 },
    dashes: [5, 4], width: 1.2,
    label: '↔',
    length: 120,
    font: { size: 12, color: '#c084fc', face: 'Inter', background: 'white', strokeWidth: 0 },
    smooth: { type: 'curvedCCW', roundness: 0.1 },
  };
}

const VIS_OPTIONS = {
  layout: {
    randomSeed: 42,
    improvedLayout: true,
  },
  physics: {
    enabled: true,
    solver: 'forceAtlas2Based',
    forceAtlas2Based: {
      gravitationalConstant: -60,
      centralGravity: 0.008,
      springLength: 140,
      springConstant: 0.06,
      damping: 0.5,
      avoidOverlap: 0.8,
    },
    stabilization: {
      enabled: true,
      iterations: 300,
      updateInterval: 50,
      fit: true,
    },
  },
  interaction: {
    dragNodes: true,
    dragView: true,
    zoomView: true,
    selectConnectedEdges: false,
    hover: false,
    navigationButtons: false,
    tooltipDelay: 999999,
  },
};

function renderGraph() {
  const container = document.getElementById("graph");

  if (!network) {
    nodesDS = new vis.DataSet([...graph.persons.values()].map(makeVisNode));
    edgesDS = new vis.DataSet([...graph.relations.values()].map(makeVisEdge));
    network = new vis.Network(container, { nodes: nodesDS, edges: edgesDS }, VIS_OPTIONS);

    // Peale stabiliseerumist lülita füüsika välja — kasutaja saab sõlmi lohistada
    network.once('stabilized', () => {
      network.setOptions({ physics: { enabled: false } });
    });

    attachVisEvents();
  } else {
    const existNodeIds = new Set(nodesDS.getIds());
    const existEdgeIds = new Set(edgesDS.getIds());

    // Eemalda kustutatud
    nodesDS.remove([...existNodeIds].filter(id => !graph.persons.has(id)));
    edgesDS.remove([...existEdgeIds].filter(id => !graph.relations.has(id)));

    // Lisa/uuenda sõlmed
    for (const p of graph.persons.values()) {
      const n = makeVisNode(p);
      existNodeIds.has(p.id) ? nodesDS.update(n) : nodesDS.add(n);
    }

    // Lisa uued servad
    for (const rel of graph.relations.values()) {
      if (!existEdgeIds.has(rel.id)) edgesDS.add(makeVisEdge(rel));
    }
  }
}

function attachVisEvents() {
  network.on('click', function(params) {
    if (params.nodes.length > 0) {
      const id = params.nodes[0];
      clearActiveCard();

      // Täida küsimispaneeli valikud
      const subj = document.getElementById('q-subject');
      const obj  = document.getElementById('q-object');
      if (!subj.value) {
        subj.value = id;
      } else if (!obj.value && id !== subj.value) {
        obj.value = id; runQuery();
      } else {
        subj.value = id; obj.value = '';
      }

      // Toimingute paneel (toggle)
      const domPos = network.canvasToDOM(network.getPositions([id])[id]);
      if (document.getElementById('node-actions').classList.contains('visible') && activeNodeId === id) {
        closeNodeActions();
      } else {
        showNodeActionsAt(id, domPos.x, domPos.y);
      }
    } else {
      closeNodeActions();
      closeInlineForm();
    }
  });

  network.on('doubleClick', function(params) {
    closeInlineForm();
    if (params.nodes.length > 0) {
      closeNodeActions();
      openEditPersonModal(params.nodes[0]);
    } else {
      closeNodeActions();
      const domPos = params.pointer.DOM;
      const canvasPos = network.DOMtoCanvas(domPos);
      showInlineForm(domPos.x, domPos.y, "Lisa inimene",
        { mode: 'new', canvasX: canvasPos.x, canvasY: canvasPos.y });
    }
  });

  // Peida paneel lohistamise ajal
  network.on('dragStart', function(params) {
    if (params.nodes.length > 0) closeNodeActions();
  });
}

// ── Sõlme toimingute paneel ───────────────────────────────

function showNodeActionsAt(nodeId, rx, ry) {
  const p = graph.persons.get(nodeId);
  if (!p || !network) return;
  activeNodeId = nodeId;

  const panel = document.getElementById("node-actions");
  const container = document.getElementById("graph-container");
  const cw = container.offsetWidth, ch = container.offsetHeight;

  document.getElementById("na-name").textContent = personLabel(p);
  document.getElementById("na-lbl-parent").textContent  = "Lisa vanem";
  document.getElementById("na-lbl-child").textContent   = "Lisa laps";
  document.getElementById("na-lbl-spouse").textContent  = "Lisa abikaasa";
  document.getElementById("na-lbl-sibling").textContent = "Lisa vend/õde";
  panel.classList.add("visible");

  const pw = 180, offset = 20;
  let left = rx + offset, top = ry - 40;
  if (left + pw > cw - 10) left = rx - pw - offset;
  if (top < 5) top = 5;
  if (top + 210 > ch) top = ch - 215;
  panel.style.left = left + "px";
  panel.style.top = top + "px";
}

function closeNodeActions() {
  document.getElementById("node-actions").classList.remove("visible");
  if (!inlineCtx) activeNodeId = null;
}

// ── Inline lisamisvorm ────────────────────────────────────

function showInlineForm(domX, domY, title, ctx) {
  inlineCtx = ctx;
  const form = document.getElementById("inline-form");
  const container = document.getElementById("graph-container");
  const cw = container.offsetWidth, ch = container.offsetHeight;

  document.getElementById("if-title").textContent = title;
  document.getElementById("if-name").value = "";
  document.getElementById("if-genitive").value = "";
  document.querySelector('input[name="ifg"][value="male"]').checked = true;

  const isRelative = ctx.mode === "relative";
  document.getElementById("if-toggle").style.display = isRelative ? "block" : "none";
  setInlineMode("new");

  form.classList.add("visible");

  const fw = form.offsetWidth || 220, fh = form.offsetHeight || 155;
  let left = domX + 14, top = domY - 20;
  if (left + fw > cw - 8) left = domX - fw - 14;
  if (top + fh > ch - 8) top = ch - fh - 8;
  if (top < 5) top = 5;
  if (left < 5) left = 5;
  form.style.left = left + "px";
  form.style.top = top + "px";

  setTimeout(() => document.getElementById("if-name").focus(), 50);
}

function setInlineMode(mode) {
  inlineCtx = inlineCtx ? { ...inlineCtx, inputMode: mode } : { inputMode: mode };
  document.getElementById("tog-new").classList.toggle("selected", mode === "new");
  document.getElementById("tog-exist").classList.toggle("selected", mode === "exist");
  document.getElementById("if-new-fields").style.display = mode === "new" ? "block" : "none";
  document.getElementById("if-exist-fields").style.display = mode === "exist" ? "block" : "none";

  if (mode === "exist") {
    const anchorId = inlineCtx.anchorId;
    const sorted = [...graph.persons.values()]
      .filter(p => p.id !== anchorId)
      .sort((a, b) => a.name.localeCompare(b.name, "et"));
    const sel = document.getElementById("if-existing");
    sel.innerHTML = '<option value="">— vali isik —</option>'
      + sorted.map(p => `<option value="${p.id}">${personLabel(p)}</option>`).join("");
    setTimeout(() => sel.focus(), 50);
  } else {
    setTimeout(() => document.getElementById("if-name").focus(), 50);
  }
}

function closeInlineForm() {
  document.getElementById("inline-form").classList.remove("visible");
  inlineCtx = null;
}

function submitInlineForm() {
  const { mode, inputMode, relType, anchorId, canvasX, canvasY } = inlineCtx;
  const isExist = inputMode === "exist";

  let targetId, targetName;
  if (isExist) {
    targetId = document.getElementById("if-existing").value;
    if (!targetId) { document.getElementById("if-existing").focus(); return; }
    targetName = graph.persons.get(targetId)?.name;
  } else {
    const name = document.getElementById("if-name").value.trim();
    if (!name) { document.getElementById("if-name").focus(); return; }
    const genitive = document.getElementById("if-genitive").value.trim() || name;
    const gender = document.querySelector('input[name="ifg"]:checked').value;
    targetId = generateId();
    targetName = name;
    graph.addPerson({ id: targetId, name, genitive, gender });
  }

  if (mode === "new") {
    saveToStorage();
    closeInlineForm();
    renderAll();
    // Aseta uus sõlm klikitud kohta
    if (network && canvasX != null) {
      setTimeout(() => network.moveNode(targetId, canvasX, canvasY), 50);
    }
    showToast(`${targetName} lisatud!`);
    return;
  }

  let from, to, type;
  if (relType === "child")   { from = anchorId; to = targetId; type = "parent"; }
  if (relType === "parent")  { from = targetId; to = anchorId; type = "parent"; }
  if (relType === "spouse")  { from = anchorId; to = targetId; type = "spouse"; }
  if (relType === "sibling") { from = anchorId; to = targetId; type = "sibling"; }

  const symmetric = type === "spouse" || type === "sibling";
  for (const rel of graph.relations.values()) {
    if (rel.type === type) {
      if ((rel.from === from && rel.to === to) || (symmetric && rel.from === to && rel.to === from)) {
        showToast("See seos on juba olemas!"); return;
      }
    }
  }

  graph.addRelation({ id: generateId(), from, to, type });

  // Kui lisatakse sibling, kopeeritakse automaatselt vanemad
  if (type === "sibling") {
    autoAssignParentsForSibling(from, to);
  }

  // Kui lisatakse parent, luuakse automaatselt õe/venna seosed
  if (type === "parent") {
    autoCreateSiblingRelations(to);
  }

  saveToStorage();
  closeInlineForm();
  closeNodeActions();
  renderAll();
  showToast(isExist ? "Seos lisatud!" : `${targetName} lisatud!`);
}

// Kui lisatakse sibling-seos, kopeeritakse automaatselt vanemad
function autoAssignParentsForSibling(sourceId, targetId) {
  for (const rel of graph.relations.values()) {
    if (rel.type === "parent" && rel.to === sourceId) {
      // Kontrollime, et sellist seost ei ole juba
      let exists = false;
      for (const r of graph.relations.values()) {
        if (r.type === "parent" && r.from === rel.from && r.to === targetId) {
          exists = true;
          break;
        }
      }
      if (!exists) {
        graph.addRelation({ id: generateId(), from: rel.from, to: targetId, type: "parent" });
      }
    }
  }
}

// Automaatselt loovad sibling-seosed inimeste vahel, kes jagavad SAMA VANEMAD
function autoCreateSiblingRelations(personId) {
  // Leia kõik selle isiku vanemad
  const myParents = new Set();
  for (const rel of graph.relations.values()) {
    if (rel.type === "parent" && rel.to === personId) {
      myParents.add(rel.from);
    }
  }

  if (myParents.size === 0) return; // Ei ole vanemate, ei saa õesid/vendi leida

  // Leia kõik inimesed, kelle vanemad on TÄPSELT samad
  const candidates = [];
  for (const otherPerson of graph.persons.values()) {
    if (otherPerson.id === personId) continue;

    const otherParents = new Set();
    for (const rel of graph.relations.values()) {
      if (rel.type === "parent" && rel.to === otherPerson.id) {
        otherParents.add(rel.from);
      }
    }

    // Kontrollime, et vanemad on täpselt samad
    if (otherParents.size === myParents.size &&
        [...myParents].every(p => otherParents.has(p))) {
      candidates.push(otherPerson.id);
    }
  }

  // Luo sibling-seosed
  for (const siblingId of candidates) {
    let exists = false;
    for (const rel of graph.relations.values()) {
      if (rel.type === "sibling") {
        if ((rel.from === personId && rel.to === siblingId) ||
            (rel.from === siblingId && rel.to === personId)) {
          exists = true;
          break;
        }
      }
    }
    if (!exists) {
      graph.addRelation({ id: generateId(), from: personId, to: siblingId, type: "sibling" });
    }
  }
}

function inlineAddRelative(relType) {
  if (!activeNodeId) return;
  const p = graph.persons.get(activeNodeId);
  if (!p) return;
  const gen = p.genitive || p.name;
  const titles = {
    parent:  `Lisa ${gen}le vanem`,
    child:   `Lisa ${gen}le laps`,
    spouse:  `Lisa ${gen}le abikaasa`,
    sibling: `Lisa ${gen}le vend/õde`,
  };
  const domPos = network.canvasToDOM(network.getPositions([activeNodeId])[activeNodeId]);
  showInlineForm(domPos.x, domPos.y, titles[relType], { mode: 'relative', relType, anchorId: activeNodeId });
}

function inlineEditNode() {
  if (!activeNodeId) return;
  const nodeId = activeNodeId;
  closeNodeActions();
  openEditPersonModal(nodeId);
}

function inlineDeleteNode() {
  if (!activeNodeId) return;
  const id = activeNodeId;
  closeNodeActions();
  deletePerson(id);
}

// ── Küsimisloogika ────────────────────────────────────────

function runQuery() {
  const subjId = document.getElementById("q-subject").value;
  const objId = document.getElementById("q-object").value;
  const resultEl = document.getElementById("query-result");

  if (!subjId || !objId) {
    resultEl.innerHTML = '<div class="result-empty">Vali kaks inimest</div>';
    return;
  }
  if (subjId === objId) {
    resultEl.innerHTML = '<div class="result-empty">Sama isik</div>';
    return;
  }

  const finder = new PathFinder(graph);
  const path = finder.findPath(objId, subjId);

  if (!path || path.length === 0) {
    resultEl.innerHTML = '<div class="result-none">Sugulust ei leitud</div>';
    return;
  }

  const analysis = finder.analyzePath(path);
  const objPerson = graph.persons.get(objId);
  if (objPerson && objPerson.gender) {
    analysis.context.requesterGender = objPerson.gender;
  }
  const rule = findKinshipTerm(analysis.steps, analysis.targetGender, analysis.context);

  const subjPerson = graph.persons.get(subjId);
  const subjName = personLabel(subjPerson);
  const objName = objPerson?.name || objId;
  const objGenitive = objPerson?.genitive || objName;
  const pathDesc = buildPathDescription(path, objGenitive);

  if (rule) {
    resultEl.innerHTML = `
      <div style="margin-bottom:6px; font-size:0.8rem; color:var(--muted)">
        <strong>${subjName}</strong> on <strong>${objGenitive}</strong>:
      </div>
      <div class="result-term">${rule.term}</div>
      <div class="result-desc">${rule.desc}</div>
      <div class="result-path">${pathDesc}</div>
    `;
  } else {
    const described = describePathInEstonian(analysis.steps, path);
    resultEl.innerHTML = `
      <div style="margin-bottom:6px; font-size:0.8rem; color:var(--muted)">
        <strong>${subjName}</strong> on <strong>${objGenitive}</strong>:
      </div>
      <div class="result-term" style="font-size:1.2rem">${described}</div>
      <div class="result-path">${pathDesc}</div>
    `;
  }
}

function buildPathDescription(path, startName) {
  const parts = [];
  let currentName = startName;
  let currentGenitive = startName;
  for (const step of path) {
    const p = step.toPerson;
    const g = p.gender;
    const m = g === "male", f = g === "female";
    const rel = {
      P:  m ? "isa" : f ? "ema" : "vanem",
      C:  m ? "poeg" : f ? "tütar" : "laps",
      S:  m ? "vend" : f ? "õde" : "õde/vend",
      Sp: m ? "mees" : f ? "naine" : "abikaasa",
    }[step.step] || "sugulane";
    const pLabel = personLabel(p);
    const pGenitive = p.genitive || p.name;
    parts.push(`<strong>${pLabel}</strong> on <strong>${currentGenitive}</strong> ${rel}`);
    currentName = pLabel;
    currentGenitive = pGenitive;
  }
  return `<ol style="margin:8px 0; padding-left:20px; font-size:0.85rem;">
    ${parts.map(p => `<li>${p}</li>`).join("")}
  </ol>`;
}

const GENITIVE_FORMS = {
  isa: "isa", ema: "ema", poeg: "poja", tütar: "tütre",
  mees: "mehe", naine: "naise", vend: "venna", õde: "õe",
  vanem: "vanema", laps: "lapse", abikaasa: "abikaasa",
  lell: "lella", onu: "onu", tädi: "tädi", nõbu: "nõo",
  küdi: "küdi", nääl: "näälu", nadu: "nao", käli: "käli",
  väi: "väi", minia: "minia", äi: "äia", ämm: "ämma",
  kasuisa: "kasuisa", kasuema: "kasuema",
  vennapoeg: "vennapoja", vennatütar: "vennatütre",
  õepoeg: "õepoja", õetütar: "õetütre",
  lellpoeg: "lellpoja", lelltütar: "lelltütre",
  onupoeg: "onupoja", onutütar: "onutütre",
  vanaisa: "vanaisa", vanaema: "vanaema",
  vanavanaisa: "vanavanaisa", vanavanaema: "vanavanaema",
};

function extractSubContext(subPath, subSteps) {
  const ctx = {};
  const first = subPath[0].toPerson;
  if (subSteps[0] === "P" && subSteps[1] === "S") ctx.parentGender = first.gender;
  if (subSteps[0] === "S") ctx.siblingGender = first.gender;
  if (subSteps[0] === "C" && subSteps[1] === "Sp") ctx.childGender = first.gender;
  if (subSteps[0] === "Sp") ctx.spouseGender = first.gender;
  return ctx;
}

function describePathInEstonian(steps, path) {
  const segments = [];
  let i = 0;
  while (i < steps.length) {
    let matched = false;
    for (const len of [3, 2]) {
      if (i + len > steps.length) continue;
      const subSteps = steps.slice(i, i + len);
      const subPath  = path.slice(i, i + len);
      const targetGender = subPath[len - 1].toPerson.gender;
      const ctx = extractSubContext(subPath, subSteps);
      const rule = findKinshipTerm(subSteps, targetGender, ctx);
      if (rule) { segments.push({ term: rule.term }); i += len; matched = true; break; }
    }
    if (!matched) {
      segments.push({ step: steps[i], gender: path[i].toPerson.gender });
      i++;
    }
  }

  return segments.map((seg, j) => {
    const isLast = j === segments.length - 1;
    if (seg.term) {
      return isLast ? seg.term : (GENITIVE_FORMS[seg.term] || seg.term);
    }
    const m = seg.gender === "male", f = seg.gender === "female";
    if (isLast) {
      return { P: m?"isa":f?"ema":"vanem", C: m?"poeg":f?"tütar":"laps", S: m?"vend":f?"õde":"õde/vend", Sp: m?"mees":f?"naine":"abikaasa" }[seg.step] || seg.step;
    }
    return { P: m?"isa":f?"ema":"vanema", C: m?"poja":f?"tütre":"lapse", S: m?"venna":f?"õe":"õe/venna", Sp: m?"mehe":f?"naise":"abikaasa" }[seg.step] || seg.step;
  }).join(" ");
}

// ── Terminite näited ──────────────────────────────────────

const COMMON_TERMS = new Set([
  "isa", "ema", "poeg", "tütar", "mees", "naine", "vend", "õde",
  "vanaisa", "vanaema", "lapselaps", "vanem", "laps", "abikaasa",
  "õde/vend", "vanavaneм", "pojapoeg / tütrepoeg", "pojatütar / tütretütar",
  "lapselapsepoeg", "lapselapsettütar",
]);

const TERM_COLORS = {
  lell:       "#6366f1",
  onu:        "#3b82f6",
  tädi:       "#ec4899",
  nadu:       "#8b5cf6",
  küdi:       "#10b981",
  nääl:       "#059669",
  käli:       "#f59e0b",
  minia:      "#a855f7",
  väi:        "#0ea5e9",
  äi:         "#14b8a6",
  ämm:        "#e879f9",
  nõbu:       "#84cc16",
  lellpoeg:   "#6366f1",
  lelltütar:  "#818cf8",
  onupoeg:    "#3b82f6",
  onutütar:   "#60a5fa",
  vennapoeg:  "#10b981",
  vennatütar: "#34d399",
  õepoeg:     "#0ea5e9",
  õetütar:    "#38bdf8",
};

function computeRareExamples() {
  const finder = new PathFinder(graph);
  const persons = [...graph.persons.values()];
  const results = [];
  const seenTerms = new Set();

  for (let i = 0; i < persons.length; i++) {
    for (let j = 0; j < persons.length; j++) {
      if (i === j) continue;
      const a = persons[i], b = persons[j];
      const path = finder.findPath(b.id, a.id);
      if (!path || path.length === 0) continue;
      const analysis = finder.analyzePath(path);
      const rule = findKinshipTerm(analysis.steps, analysis.targetGender, analysis.context);
      if (!rule || COMMON_TERMS.has(rule.term) || seenTerms.has(rule.term)) continue;
      seenTerms.add(rule.term);
      results.push({ subjectId: a.id, objectId: b.id, subjectName: a.name, objectName: b.name, rule });
    }
  }
  results.sort((a, b) => a.rule.term.localeCompare(b.rule.term, "et"));
  return results;
}

function renderExamples() {
  const grid = document.getElementById("examples-grid");
  const examples = computeRareExamples();

  if (examples.length === 0) {
    grid.innerHTML = '<div class="examples-empty">Haruldasi termineid ei leitud.<br>Lisa rohkem perekonnaliikmeid!</div>';
    return;
  }

  grid.innerHTML = "";
  for (const ex of examples) {
    const color = TERM_COLORS[ex.rule.term] || "#6366f1";
    const card = document.createElement("div");
    card.className = "example-card";
    card.style.setProperty("--card-color", color);
    const objGenitive = graph.persons.get(ex.objectId)?.genitive || ex.objectName;
    card.innerHTML = `
      <div class="card-persons">
        <span class="name">${ex.subjectName}</span> on
        <span class="name">${objGenitive}</span>
        <strong>${ex.rule.term}</strong>
      </div>
      <div class="card-desc">${ex.rule.desc}</div>
    `;
    card.addEventListener("click", () => {
      document.querySelectorAll(".example-card.active-card").forEach(c => c.classList.remove("active-card"));
      card.classList.add("active-card");
      document.getElementById("q-subject").value = ex.subjectId;
      document.getElementById("q-object").value = ex.objectId;
      runQuery();
      if (network) {
        network.unselectAll();
        network.selectNodes([ex.subjectId, ex.objectId]);
      }
    });
    grid.appendChild(card);
  }
}

function renderQueryDropdowns() {
  const sorted = [...graph.persons.values()].sort((a, b) => a.name.localeCompare(b.name, "et"));
  const options = sorted.map(p => `<option value="${p.id}">${personLabel(p)}</option>`).join("");

  const subj = document.getElementById("q-subject");
  const obj = document.getElementById("q-object");
  const prevSubj = subj.value, prevObj = obj.value;

  subj.innerHTML = '<option value="">— vali isik —</option>' + options;
  obj.innerHTML  = '<option value="">— kellele? —</option>' + options;

  if (prevSubj) subj.value = prevSubj;
  if (prevObj)  obj.value  = prevObj;
}

// ── Isiku CRUD ────────────────────────────────────────────

function openAddPersonModal() {
  editingPersonId = null;
  document.getElementById("modal-person-title").textContent = "Lisa uus isik";
  document.getElementById("p-name").value = "";
  document.getElementById("p-genitive").value = "";
  document.querySelector('input[name="pgender"][value="male"]').checked = true;
  document.getElementById("modal-person").classList.add("active");
  document.getElementById("p-name").focus();
}

function openEditPersonModal(id) {
  editingPersonId = id;
  const p = graph.persons.get(id);
  if (!p) return;
  document.getElementById("modal-person-title").textContent = "Muuda isikut";
  document.getElementById("p-name").value = p.name;
  document.getElementById("p-genitive").value = p.genitive || p.name;
  const genderRadio = document.querySelector(`input[name="pgender"][value="${p.gender}"]`);
  if (genderRadio) genderRadio.checked = true;
  document.getElementById("modal-person").classList.add("active");
}

function savePerson() {
  const name = document.getElementById("p-name").value.trim();
  if (!name) { showToast("Sisesta nimi!"); return; }
  const genitive = document.getElementById("p-genitive").value.trim() || name;
  const gender = document.querySelector('input[name="pgender"]:checked').value;

  if (editingPersonId) {
    graph.updatePerson(editingPersonId, { name, genitive, gender });
  } else {
    graph.addPerson({ id: generateId(), name, genitive, gender });
  }
  saveToStorage();
  closeModal("modal-person");
  renderAll();
  showToast(editingPersonId ? "Isik uuendatud!" : `${name} lisatud!`);
}

function deletePerson(id) {
  const p = graph.persons.get(id);
  if (!p) return;
  if (!confirm(`Kustuta ${p.name}? Kõik seosed kustutatakse ka.`)) return;
  graph.deletePerson(id);
  saveToStorage();
  renderAll();
  showToast(`${p.name} kustutatud.`);
}

// ── Seose CRUD ────────────────────────────────────────────

function openAddRelationModal() {
  const sorted = [...graph.persons.values()].sort((a, b) => a.name.localeCompare(b.name, "et"));
  const options = sorted.map(p => `<option value="${p.id}">${personLabel(p)}</option>`).join("");
  document.getElementById("r-from").innerHTML = options;
  document.getElementById("r-to").innerHTML = options;
  selectRelType("parent");
  updateRelPreview();
  document.getElementById("r-from").onchange = updateRelPreview;
  document.getElementById("r-to").onchange = updateRelPreview;
  document.getElementById("modal-relation").classList.add("active");
}

function selectRelType(type) {
  selectedRelType = type;
  document.getElementById("rtype-parent").classList.toggle("selected", type === "parent");
  document.getElementById("rtype-spouse").classList.toggle("selected", type === "spouse");
  updateRelPreview();
}

function updateRelPreview() {
  const fromEl = document.getElementById("r-from");
  const toEl   = document.getElementById("r-to");
  const fromName = fromEl.options[fromEl.selectedIndex]?.text || "A";
  const toName   = toEl.options[toEl.selectedIndex]?.text   || "B";
  const desc = selectedRelType === "parent"
    ? `${fromName} on ${toName} vanem`
    : `${fromName} ja ${toName} on abielus`;
  document.getElementById("rel-preview").textContent = "→ " + desc;
}

function saveRelation() {
  const from = document.getElementById("r-from").value;
  const to   = document.getElementById("r-to").value;
  if (!from || !to) { showToast("Vali mõlemad isikud!"); return; }
  if (from === to)  { showToast("Isik ei saa olla iseenda sugulane!"); return; }

  for (const rel of graph.relations.values()) {
    if (rel.type === selectedRelType) {
      if ((rel.from === from && rel.to === to) || (rel.from === to && rel.to === from)) {
        showToast("See seos on juba olemas!"); return;
      }
    }
  }

  graph.addRelation({ id: generateId(), from, to, type: selectedRelType });

  // Kui lisatakse sibling, kopeeritakse automaatselt vanemad
  if (selectedRelType === "sibling") {
    autoAssignParentsForSibling(from, to);
  }

  // Kui lisatakse parent, luuakse automaatselt õe/venna seosed
  if (selectedRelType === "parent") {
    autoCreateSiblingRelations(to);
  }

  saveToStorage();
  closeModal("modal-relation");
  renderAll();
  showToast("Seos lisatud!");
}

// ── Utiliidid ─────────────────────────────────────────────

function clearActiveCard() {
  document.querySelectorAll(".example-card.active-card").forEach(c => c.classList.remove("active-card"));
}

function closeModal(id) {
  document.getElementById(id).classList.remove("active");
}

function showToast(msg) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 2500);
}

function generateId() {
  return "id_" + Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
}

// ── Klaviatuur + sündmused ────────────────────────────────

document.addEventListener("keydown", e => {
  if (e.key === "Escape") {
    closeModal("modal-person");
    closeModal("modal-relation");
    closeInlineForm();
    closeNodeActions();
  }
});

document.getElementById("if-name").addEventListener("keydown", e => {
  if (e.key === "Enter") submitInlineForm();
  if (e.key === "Escape") closeInlineForm();
});

document.getElementById("p-name").addEventListener("keydown", e => {
  if (e.key === "Enter") savePerson();
});

document.getElementById("r-from").addEventListener("keydown", e => {
  if (e.key === "Enter") saveRelation();
});

document.getElementById("r-to").addEventListener("keydown", e => {
  if (e.key === "Enter") saveRelation();
});

document.querySelectorAll(".modal-overlay").forEach(overlay => {
  overlay.addEventListener("click", e => {
    if (e.target === overlay) overlay.classList.remove("active");
  });
});

// ── Jagamine ──────────────────────────────────────────

function generateShareCode() {
  return Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
}

function showShareModal() {
  document.getElementById("modal-share").classList.add("active");
  document.getElementById("share-loading").style.display = "block";
  document.getElementById("share-content").style.display = "none";

  // Genereeri share kood ja salvesta graaf
  const shareCode = generateShareCode();
  const shareKey = `share_${shareCode}`;
  localStorage.setItem(shareKey, JSON.stringify(graph.toJSON()));

  // Genereeri link
  const baseUrl = window.location.origin + window.location.pathname;
  const shareLink = `${baseUrl}?share=${shareCode}`;

  // Näita linki
  setTimeout(() => {
    document.getElementById("share-link").value = shareLink;
    document.getElementById("share-loading").style.display = "none";
    document.getElementById("share-content").style.display = "block";
  }, 300);
}

function copyShareLink() {
  const linkInput = document.getElementById("share-link");
  linkInput.select();
  document.execCommand("copy");
  showToast("Link kopeeritud!");
}

// Käivita rakendus
init();
