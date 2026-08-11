#!/usr/bin/env node
/*
 * CV-GUARD-1 repro — TS-0006 / TS-0021, 11 Aug 2026.
 *
 * Reproduces the two crashes the testers' console tails captured, against whichever
 * ms.js you point it at, and proves the guarded version survives them:
 *
 *   TS-0021 (Chrome/Win)   "Cannot read properties of undefined (reading 'headline')"
 *   TS-0006 (Safari/iPhone) "undefined is not an object (evaluating 'l.trust')"
 *
 * Both come from openSellerCV, the sibling entry point RG-0031 missed: SELLERS can be
 * empty on a cold / live-only load, and findListing() misses whenever the card is not
 * in the ACTIVE city (LISTINGS only ever holds one city).
 *
 * Usage:  node scripts/repro_cv_guard.js [path/to/ms.js]
 * Exit 0 = the file under test is GUARDED. Exit 1 = it still crashes.
 * Run it against a .bak to watch the original fail, which is the point.
 */
const fs = require('fs');
const vm = require('vm');
const path = require('path');

const target = process.argv[2] || path.join(__dirname, '..', 'ms.js');
const src = fs.readFileSync(target, 'utf8');

function extract(name, header) {
  const start = src.indexOf(header);
  if (start < 0) throw new Error(`could not find ${name} in ${target}`);
  const nextRe = /\n(?:async )?function /g;
  nextRe.lastIndex = start + header.length;
  const m = nextRe.exec(src);
  if (!m) throw new Error(`could not find the end of ${name}`);
  return src.slice(start, m.index);
}

// Any global the function reaches for that we have not deliberately pinned resolves to a
// permissive stub, so the ONLY absences under test are the ones we are actually testing.
function makeStub() {
  const f = function () { return makeStub(); };
  return new Proxy(f, {
    get(t, k) {
      if (k === Symbol.toPrimitive || k === 'toString') return () => '';
      if (k === 'then') return undefined;
      return makeStub();
    },
    apply() { return makeStub(); },
    has() { return true },
  });
}

function run(label, fnSrc, pinned) {
  const el = { innerHTML: '', textContent: '', style: {} };
  const base = {
    console,
    SELLERS: [],
    LISTINGS: [],
    SELLER_PHOTOS: [],
    CATS: {},
    acceptedIntros: new Set(),
    prevScreen: 'browse',
    findListing: (id) => undefined,                       // the miss TS-0006 hit
    trustTier: (s) => ({ label: 'New', c: '#6b7280', bg: '#f3f4f6' }),
    fspark: (l) => (l.founders ? '*' : ''),               // real fspark derefs its arg
    isFounders: (l) => !!(l && l.founders),
    cvAvatarHtml: () => '',
    openBEASellerProfile: () => {},
    goTo: () => {},
    document: {
      getElementById: () => el,
      querySelector: () => ({ id: 'screen-browse', classList: { contains: () => true } }),
      querySelectorAll: () => [],
    },
  };
  Object.assign(base, pinned || {});
  const ctx = new Proxy(base, {
    has: () => true,
    get: (t, k) => (k in t ? t[k] : makeStub()),
    set: (t, k, v) => { t[k] = v; return true; },
  });
  vm.createContext(ctx);
  try {
    vm.runInContext(fnSrc + '\n' + label.call, ctx, { timeout: 5000 });
    return { ok: true };
  } catch (e) {
    return { ok: false, err: String(e && e.message || e) };
  }
}

const cases = [
  {
    ref: 'TS-0021',
    name: 'openSellerCV with an EMPTY seller roster',
    tail: "Cannot read properties of undefined (reading 'headline')",
    fnSrc: () => extract('openSellerCV', 'function openSellerCV(sellerIdx,listingId){'),
    call: 'openSellerCV(0, 12345);',
    pinned: { SELLERS: [], findListing: () => ({ id: 12345, trust: 62, city: 'Pretoria' }) },
  },
  {
    ref: 'TS-0006',
    name: 'openSellerCV when the listing is not in the active city',
    tail: "undefined is not an object (evaluating 'l.trust')",
    fnSrc: () => extract('openSellerCV', 'function openSellerCV(sellerIdx,listingId){'),
    call: 'openSellerCV(0, 999999);',
    pinned: { SELLERS: [{ idx: 0, headline: 'Waterkloof specialist', cat: 'Property', stats: [] }], findListing: () => undefined },
  },
  {
    ref: 'CV-GUARD-1',
    name: 'renderProfilePreview with an EMPTY seller roster',
    tail: "same class: SELLERS[0] undefined",
    fnSrc: () => extract('renderProfilePreview', 'function renderProfilePreview(){'),
    call: 'renderProfilePreview();',
    pinned: { SELLERS: [], SELLER_PHOTOS: [], CATS: {} },
  },
];

console.log(`CV-GUARD-1 repro -- ${path.relative(process.cwd(), target)}\n`);
let failed = 0;
for (const c of cases) {
  const r = run({ call: c.call }, c.fnSrc(), c.pinned);
  if (r.ok) {
    console.log(`[ pass ] ${c.ref}  ${c.name}\n           rendered without throwing`);
  } else {
    failed++;
    console.log(`[ CRASH ] ${c.ref}  ${c.name}\n           ${r.err}\n           tester saw: ${c.tail}`);
  }
}
console.log('');
if (failed) {
  console.log(`RESULT: ${failed}/${cases.length} still crash -- this ms.js is NOT guarded.`);
  process.exit(1);
}
console.log(`RESULT: all ${cases.length} guarded -- a missing seller or off-city listing renders, never throws.`);
process.exit(0);
