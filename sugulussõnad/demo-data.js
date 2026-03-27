// Näidisandmed - katab kõik haruldased sugulussõnad
//
// Perekond Tamm:
//
//   Aleksander (m) ─── Helgi (f)        Eduard (m) ─── Leida (f)
//        │                                    │
//   ┌────┴────┐                         ┌─────┴─────┐
//  Toomas(m) Jüri(m) ─────────── Mari(f)          Kalev(m)
//             │
//        ┌────┴────┐
//      Peeter(m)  Tiina(f)
//             │
//           Leeni(f) (Peetri naine)
//
// Terminid:
//   Toomas → Jürile:  LELL (isa vend - sest Aleksander on isa)
//   Kalev  → Marile:  ONU  (ema vend - sest Leida on ema)
//   Mari   → Jürile:  NAINE / Jüri → Marile: MEES
//   Leeni  → Jürile:  MINIA (poja naine)
//   Leeni  → Marile:  MINIA
//   Peeter → Marile:  POEG / Tiina → Marile: TÜTAR
//   Toomas → Peetrile: LELL
//   Kalev  → Peetrile: ONU
//   Tiina  → Peetrile: ÕDE / Peeter → Tiinale: VEND
//   Jüri   → Helgile:  POEG / Helgi → Jürile: EMA
//   Helgi  → Peetrile: VANAEMA
//   Mari   → Helgile:  MINIA... (tegelikult: naise ema = ämm)
//   Helgi  → Marile:   ÄMM (abikaasa ema)... ei, Helgi on Jüri ema, mitte Mari ema
//   Leida  → Marile:   EMA / Eduard → Marile: ISA
//   Leida  → Jürile:   ÄMM (abikaasa ema)
//   Eduard → Jürile:   ÄI  (abikaasa isa)
//   Jüri   → Leidele:  ÄI... ei - Jüri → Leida: ÄMM? ei - Leida on Mari ema, seega Jürile ÄMM
//   Tiina  → Leenile:  NADU (abikaasa õde - Peeter on Tiina vend, Leeni on Peetri naine)
//   Leeni  → Tiinale:  NADU
//   Peeter → Tiinale: VEND

const DEMO_DATA = {
  version: 1,
  persons: [
    { id: "aleksander", name: "Aleksander", genitive: "Aleksandri", gender: "male",   birthYear: 1935, notes: "Perepea" },
    { id: "helgi",      name: "Helgi",      genitive: "Helgi",      gender: "female", birthYear: 1938, notes: "" },
    { id: "toomas",     name: "Toomas",     genitive: "Toomase",    gender: "male",   birthYear: 1960, notes: "" },
    { id: "jueri",      name: "Jüri",       genitive: "Jüri",       gender: "male",   birthYear: 1963, notes: "" },
    { id: "mari",       name: "Mari",       genitive: "Mari",       gender: "female", birthYear: 1965, notes: "" },
    { id: "peeter",     name: "Peeter",     genitive: "Peetri",     gender: "male",   birthYear: 1990, notes: "" },
    { id: "tiina",      name: "Tiina",      genitive: "Tiina",      gender: "female", birthYear: 1993, notes: "" },
    { id: "leeni",      name: "Leeni",      genitive: "Leeni",      gender: "female", birthYear: 1991, notes: "" },
    { id: "eduard",     name: "Eduard",     genitive: "Eduardi",    gender: "male",   birthYear: 1940, notes: "" },
    { id: "leida",      name: "Leida",      genitive: "Leida",      gender: "female", birthYear: 1942, notes: "" },
    { id: "kalev",      name: "Kalev",      genitive: "Kalevi",     gender: "male",   birthYear: 1968, notes: "" },
  ],
  relations: [
    // Aleksander + Helgi on abielus
    { id: "r1",  from: "aleksander", to: "helgi",      type: "spouse" },
    // Aleksander on Toomase vanem
    { id: "r2",  from: "aleksander", to: "toomas",     type: "parent" },
    // Aleksander on Jüri vanem
    { id: "r3",  from: "aleksander", to: "jueri",      type: "parent" },
    // Helgi on Toomase vanem
    { id: "r4",  from: "helgi",      to: "toomas",     type: "parent" },
    // Helgi on Jüri vanem
    { id: "r5",  from: "helgi",      to: "jueri",      type: "parent" },
    // Jüri + Mari on abielus
    { id: "r6",  from: "jueri",      to: "mari",       type: "spouse" },
    // Jüri on Peetri vanem
    { id: "r7",  from: "jueri",      to: "peeter",     type: "parent" },
    // Jüri on Tiina vanem
    { id: "r8",  from: "jueri",      to: "tiina",      type: "parent" },
    // Mari on Peetri vanem
    { id: "r9",  from: "mari",       to: "peeter",     type: "parent" },
    // Mari on Tiina vanem
    { id: "r10", from: "mari",       to: "tiina",      type: "parent" },
    // Peeter + Leeni on abielus
    { id: "r11", from: "peeter",     to: "leeni",      type: "spouse" },
    // Eduard + Leida on abielus
    { id: "r12", from: "eduard",     to: "leida",      type: "spouse" },
    // Eduard on Mari vanem
    { id: "r13", from: "eduard",     to: "mari",       type: "parent" },
    // Leida on Mari vanem
    { id: "r14", from: "leida",      to: "mari",       type: "parent" },
    // Eduard on Kalevi vanem
    { id: "r15", from: "eduard",     to: "kalev",      type: "parent" },
    // Leida on Kalevi vanem
    { id: "r16", from: "leida",      to: "kalev",      type: "parent" },
    // Toomas ja Jüri on vennad
    { id: "r17", from: "toomas",     to: "jueri",      type: "sibling" },
    // Peeter ja Tiina on õe-venna seoses
    { id: "r18", from: "peeter",     to: "tiina",      type: "sibling" },
  ],
};

if (typeof module !== "undefined") module.exports = { DEMO_DATA };
