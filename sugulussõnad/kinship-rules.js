// Sugulussõnade reeglistik
// Tee on kodeeritud sammudena:
// "P" = vanem (parent), "C" = laps (child), "S" = õde/vend (sibling), "Sp" = abikaasa (spouse)
// subjectParentGender: vahepealse vanema sugu (lell vs onu eristuseks)
// siblingGender: vahepealse õe/venna sugu (käli vs nadu eristuseks)
// spouseGender: abikaasa sugu — vahepealse sõlme sugu Sp→S teel (küdi/nääl/nadu eristuseks)
//   küdi = MEHEvend (abikaasa on mees) | nääl = NAISEvend (abikaasa on naine)
//   Toimib ka sama sooga abielude puhul.
// requesterGender: küsija sugu (muude eristuste jaoks)

const KINSHIP_RULES = [
  // ── Lähisugulased ─────────────────────────────────
  { path: ["P"],     targetGender: "male",   term: "isa",     desc: "meessoost vanem" },
  { path: ["P"],     targetGender: "female", term: "ema",     desc: "naissoost vanem" },
  { path: ["P"],     term: "vanem",   desc: "isa või ema" },

  { path: ["C"],     targetGender: "male",   term: "poeg",    desc: "meessoost laps" },
  { path: ["C"],     targetGender: "female", term: "tütar",   desc: "naissoost laps" },
  { path: ["C"],     term: "laps",    desc: "laps" },

  { path: ["Sp"],    targetGender: "male",   term: "mees",    desc: "meessoost abikaasa" },
  { path: ["Sp"],    targetGender: "female", term: "naine",   desc: "naissoost abikaasa" },
  { path: ["Sp"],    term: "abikaasa", desc: "abikaasa" },

  // ── Õed-vennad ────────────────────────────────────
  { path: ["S"],     targetGender: "male",   term: "vend",    desc: "meessoost õde-vend" },
  { path: ["S"],     targetGender: "female", term: "õde",     desc: "naissoost õde-vend" },
  { path: ["S"],     term: "õde/vend", desc: "õde-vend" },

  // ── Vanavanemad / lapselapsed ──────────────────────
  { path: ["P","P"], targetGender: "male",   term: "vanaisa",  desc: "meessoost vanavaneм" },
  { path: ["P","P"], targetGender: "female", term: "vanaema",  desc: "naissoost vanavaneм" },
  { path: ["P","P"], term: "vanavaneм", desc: "vanavaneм" },

  { path: ["C","C"], targetGender: "male",   term: "pojapoeg / tütrepoeg", desc: "lapselaps" },
  { path: ["C","C"], targetGender: "female", term: "pojatütar / tütretütar", desc: "lapselaps" },
  { path: ["C","C"], term: "lapselaps", desc: "lapselaps" },

  // ── Vanavanaemad/isad ─────────────────────────────
  { path: ["P","P","P"], targetGender: "male",   term: "vanavanaisa",  desc: "meessoost vanavaneneм" },
  { path: ["P","P","P"], targetGender: "female", term: "vanavanaema",  desc: "naissoost vanavaneм" },

  { path: ["C","C","C"], targetGender: "male",   term: "lapselapsepoeg",   desc: "lapselapse laps" },
  { path: ["C","C","C"], targetGender: "female", term: "lapselapsettütar", desc: "lapselapse laps" },

  // ── Onud ja tädid (HARULDASED distinktsioonid) ────
  // lell = ISA vend, onu = EMA vend, sõtse = ISA õde
  { path: ["P","S"], targetGender: "male",   subjectParentGender: "male",   term: "lell",  desc: "isa vend" },
  { path: ["P","S"], targetGender: "male",   subjectParentGender: "female", term: "onu",   desc: "ema vend" },
  { path: ["P","S"], targetGender: "female", subjectParentGender: "male",   term: "sõtse", desc: "isa õde" },
  { path: ["P","S"], targetGender: "female", term: "tädi",  desc: "vanemate õde" },
  { path: ["P","S"], targetGender: "male",   term: "onu/lell", desc: "onu või lell" },

  // ── Onupoeg / tädipoeg (nõod) ─────────────────────
  { path: ["P","S","C"], term: "nõbu", desc: "tädi või onu laps" },
  { path: ["P","S","C","C"], term: "nõbu laps", desc: "nõbu lapselaps" },

  // ── Tädipoeg / onupoeg täpsem ─────────────────────
  { path: ["P","S","C"], targetGender: "male",   subjectParentGender: "male",   term: "lellpoeg",  desc: "lell laps" },
  { path: ["P","S","C"], targetGender: "female", subjectParentGender: "male",   term: "lelltütar", desc: "lell laps" },
  { path: ["P","S","C"], targetGender: "male",   subjectParentGender: "female", term: "onupoeg",   desc: "onu laps" },
  { path: ["P","S","C"], targetGender: "female", subjectParentGender: "female", term: "onutütar",  desc: "onu laps" },

  // ── Õdede-vendade lapsed ──────────────────────────
  { path: ["S","C"], targetGender: "male",   siblingGender: "male",   term: "vennapoeg",  desc: "venna laps" },
  { path: ["S","C"], targetGender: "female", siblingGender: "male",   term: "vennatütar", desc: "venna laps" },
  { path: ["S","C"], targetGender: "male",   siblingGender: "female", term: "õepoeg",     desc: "õe laps" },
  { path: ["S","C"], targetGender: "female", siblingGender: "female", term: "õetütar",    desc: "õe laps" },
  { path: ["S","C"], targetGender: "male",   term: "vennapoeg / õepoeg",   desc: "venna või õe laps" },
  { path: ["S","C"], targetGender: "female", term: "vennatütar / õetütar", desc: "venna või õe laps" },

  // ── Abielu kaudu sugulusest (HARULDASED) ──────────
  { path: ["Sp","P"], targetGender: "male",   term: "äi",   desc: "abikaasa isa" },
  { path: ["Sp","P"], targetGender: "female", term: "ämm",  desc: "abikaasa ema" },

  { path: ["P","Sp"], targetGender: "male",   term: "kasuisa",  desc: "vanema uus abikaasa" },
  { path: ["P","Sp"], targetGender: "female", term: "kasuema",  desc: "vanema uus abikaasa" },

  // ── Abikaasa sugulased (HARULDASED — küsija sugu eristab) ─
  //
  // KÜDI = abikaasa vend (naise seisukohast)
  { path: ["Sp","S"], requesterGender: "female", targetGender: "male",   term: "küdi", desc: "naise abikaasa vend" },
  // NÄÄL = abikaasa vend (mehe seisukohast)
  { path: ["Sp","S"], requesterGender: "male",   targetGender: "male",   term: "nääl", desc: "mehe abikaasa vend" },
  // NADU = abikaasa õde (naise seisukohast)
  { path: ["Sp","S"], requesterGender: "female", targetGender: "female", term: "nadu", desc: "naise abikaasa õde" },
  // KÄLI = abikaasa õde (mehe seisukohast)
  { path: ["Sp","S"], requesterGender: "male",   targetGender: "female", term: "käli", desc: "mehe abikaasa õde" },
  // Fallback
  { path: ["Sp","S"], targetGender: "male",   term: "küdi / nääl", desc: "abikaasa vend" },
  { path: ["Sp","S"], targetGender: "female", term: "nadu / käli", desc: "abikaasa õde" },

  // VÄI = tütre abikaasa
  { path: ["C","Sp"], targetGender: "male",   childGender: "female", term: "väi",   desc: "tütre abikaasa" },
  // MINIA = poja abikaasa
  { path: ["C","Sp"], targetGender: "female", childGender: "male",   term: "minia", desc: "poja abikaasa" },
  { path: ["C","Sp"], targetGender: "male",   term: "väi",   desc: "lapse abikaasa" },
  { path: ["C","Sp"], targetGender: "female", term: "minia", desc: "lapse abikaasa" },

  // KÄLI = venna naine JA mehe abikaasa õde
  { path: ["S","Sp"], targetGender: "female", siblingGender: "male",   term: "käli", desc: "venna naine" },
  // KÄLIMEES = naise õe mees (naise seisukohast)
  { path: ["S","Sp"], requesterGender: "female", targetGender: "male",   siblingGender: "female", term: "kälimees", desc: "naise õe mees" },
  // KÜDI = õe abikaasa (generic)
  { path: ["S","Sp"], targetGender: "male",   siblingGender: "female", term: "küdi", desc: "õe abikaasa" },
  // venna abikaasa / õe abikaasa (kaasaeg)
  { path: ["S","Sp"], targetGender: "male",   siblingGender: "male",   term: "küdi", desc: "venna abikaasa" },
  { path: ["S","Sp"], targetGender: "female", siblingGender: "female", term: "käli", desc: "õe naine" },
  { path: ["S","Sp"], term: "õe/venna abikaasa", desc: "õe või venna abikaasa" },

  // ── Laiendatud abielu ─────────────────────────────
  { path: ["Sp","S","C"], term: "abikaasa nõbu laps", desc: "abikaasa nõbu laps" },
];

// Abifunktsioon - leia reegel tee ja soo järgi
function findKinshipTerm(pathSteps, targetGender, context = {}) {
  const pathKey = pathSteps.join(",");

  // Proovi täpne sobivus koos kõigi kontekstiatribuutidega
  for (const rule of KINSHIP_RULES) {
    const ruleKey = rule.path.join(",");
    if (ruleKey !== pathKey) continue;
    if (rule.targetGender      && rule.targetGender      !== targetGender)             continue;
    if (rule.subjectParentGender && rule.subjectParentGender !== context.parentGender) continue;
    if (rule.siblingGender     && rule.siblingGender     !== context.siblingGender)    continue;
    if (rule.childGender       && rule.childGender       !== context.childGender)      continue;
    if (rule.requesterGender   && rule.requesterGender   !== context.requesterGender)  continue;
    if (rule.spouseGender      && rule.spouseGender      !== context.spouseGender)     continue;
    return rule;
  }

  // Proovi ilma kontekstita (üldsugu)
  for (const rule of KINSHIP_RULES) {
    const ruleKey = rule.path.join(",");
    if (ruleKey !== pathKey) continue;
    if (rule.targetGender && rule.targetGender !== targetGender) continue;
    if (rule.subjectParentGender || rule.siblingGender || rule.childGender || rule.requesterGender || rule.spouseGender) continue;
    return rule;
  }

  // Proovi täiesti üldist (ilma soota)
  for (const rule of KINSHIP_RULES) {
    const ruleKey = rule.path.join(",");
    if (ruleKey !== pathKey) continue;
    if (!rule.targetGender) return rule;
  }

  return null;
}

if (typeof module !== "undefined") module.exports = { KINSHIP_RULES, findKinshipTerm };
