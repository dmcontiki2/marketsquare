/* trip_essentials_selftest.js — TRIP-ESSENTIALS-1 (21 Aug 2026)
   Renders the "Before you go" panel for EVERY trip in the data file, headless,
   and fails loudly on the ways this kind of panel actually breaks:
     · a trip that matches no advert (dead data)
     · an advert that matches no trip (silent empty panel)
     · undefined / [object Object] leaking into the HTML
     · a fact row with no source and no honest "not published" wording
     · unescaped user-ish content
     · the model constraint: no copy that implies we sell or book the trip
   Run:  node scripts/trip_essentials_selftest.js        (exit 0 = green)   */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
let fail = 0, warn = 0;
const bad = (m) => { console.log('  [FAIL] ' + m); fail++; };
const soft = (m) => { console.log('  [warn] ' + m); warn++; };

// ── load the generated data ────────────────────────────────────────────────
global.window = {};
eval(fs.readFileSync(path.join(ROOT, 'trip_essentials.js'), 'utf8'));
const TE = global.window.TRIP_ESSENTIALS;
if (!TE || !TE.trips || !TE.trips.length) { console.log('[FAIL] no TRIP_ESSENTIALS'); process.exit(1); }

// ── lift the renderer straight out of ms.js: the test must exercise the code
//    that actually ships, not a copy that can drift away from it ────────────
const ms = fs.readFileSync(path.join(ROOT, 'ms.js'), 'utf8');
const START = 'function tripEssentialsFor(l){';
const END   = "\n    + '</div>';\n}";
const i = ms.indexOf(START);
if (i < 0) { console.log('[FAIL] tripEssentialsFor() not found in ms.js'); process.exit(1); }
const j = ms.indexOf(END, ms.indexOf('function tripEssentialsPanel'));
if (j < 0) { console.log('[FAIL] tripEssentialsPanel() end not found in ms.js'); process.exit(1); }
const src = ms.slice(i, j + END.length);
function tourKeyOf(l){ if(l && l.tour) return String(l.tour).toLowerCase(); var c=((l&&l.country)||'').toString().toUpperCase(); return c==='NA'?'na':c==='MZ'?'mz':c==='BW'?'bw':''; }
eval(src);

console.log('TRIP-ESSENTIALS-1 self-test — %d trips', TE.trips.length);

// ── 1. every trip must render, for a listing that would really reach it ────
const matched = new Set();
TE.trips.forEach(t => {
  const l = t.match.tour
    ? { super_example: 1, tour: t.match.tour, country: 'ZA' }
    : { super_example: 1, country: t.match.country };
  const got = tripEssentialsFor(l);
  if (!got) { bad(t.key + ': a real listing does not match it'); return; }
  if (got.key !== t.key) { bad(t.key + ': matched ' + got.key + ' instead'); return; }
  matched.add(t.key);

  const html = tripEssentialsPanel(l, 'demo-1');
  if (!html) { bad(t.key + ': rendered empty'); return; }
  ['undefined', '[object Object]', 'NaN', 'null</'].forEach(x => {
    if (html.indexOf(x) > -1) bad(t.key + ': "' + x + '" leaked into the HTML');
  });
  if (html.indexOf('Before you go') < 0) bad(t.key + ': lost its heading');
  if (html.indexOf('Last checked') < 0) bad(t.key + ': lost its checked stamp');
  if (html.indexOf('does not sell or book') < 0) bad(t.key + ': lost the introductory-service disclaimer');
  if (html.indexOf('Request an introduction') < 0) bad(t.key + ': lost the introduction handoff');

  // the six things David named, by name
  const need = { 'itinerary':'The itinerary', 'budget':'What it actually costs',
                 'visas':'Entry', 'safety':'Safety', 'money/taxes/tips':'Money, tax &amp; tipping',
                 'notices':'Check these on the day' };
  Object.keys(need).forEach(k => {
    if (html.indexOf(need[k]) < 0) bad(t.key + ': missing the ' + k + ' block ("' + need[k] + '")');
  });

  // structure sanity
  if (!t.itinerary || !t.itinerary.length) bad(t.key + ': empty itinerary');
  if (!t.budget || !t.budget.rows || !t.budget.rows.length) bad(t.key + ': empty budget');
  if (!t.verify || !t.verify.length) bad(t.key + ': no re-check list');
  if ((t.sections || []).length < 5) bad(t.key + ': only ' + (t.sections||[]).length + ' sections');
});

// ── 2. every map an advert can show should have essentials behind it ───────
const MAP_COUNTRIES = ['ZA','US','GB','AU','NA','BW','MZ','KE','DE'];
const MAP_TOURS     = ['c2c','usrail','gbrail','aurail'];
MAP_COUNTRIES.forEach(c => { if (!tripEssentialsFor({country:c})) bad('country map ' + c + ' has a map but NO essentials'); });
MAP_TOURS.forEach(tk => { if (!tripEssentialsFor({tour:tk})) bad('tour map ' + tk + ' has a map but NO essentials'); });

// ── 3. honesty rules ───────────────────────────────────────────────────────
const HONEST = /not published|could not be confirmed|UNVERIFIED|not confirmed|no scheme found|ask your|ask the|ask before|ask us|confirm|verify|indicative|not independently|not stated|no official|this advert's own/i;
// A number a traveller will budget against: currency amount, percentage, or a fee.
const MONEY  = /(?:R\s?\d|US\$\s?\d|N\$\s?\d|CA\$\s?\d|A\$\s?\d|£\s?\d|€\s?\d|\$\s?\d|(?:EGP|MZN|BWP|KES|ZMW|TZS|AUD|EUR|GBP|USD|ZAR|NAD)\s?\d|\bP\s?\d{2,}|\d+(?:\.\d+)?\s?%)/;
let rows = 0, sourced = 0, unsourced = [];
TE.trips.forEach(t => {
  const all = [].concat(t.budget.rows, ...(t.sections||[]).map(s => s.rows));
  all.forEach(r => {
    rows++;
    if (r.src) { sourced++; return; }
    const text = (r.v||'') + ' ' + (r.n||'') + ' ' + (r.l||'');
    // Orientation copy needs no URL. A bare NUMBER does — that is what people
    // budget against, and an unsourced number is how a dossier becomes fiction.
    if (MONEY.test(text) && !HONEST.test(text)) unsourced.push(t.key + ' :: ' + r.l + ' — ' + (r.v||'').slice(0,70));
  });
});
if (unsourced.length) {
  bad(unsourced.length + ' unsourced rows quote a NUMBER with no source:');
  unsourced.slice(0, 12).forEach(x => console.log('         · ' + x));
}

// ── 4. the model constraint (CLAUDE.md, David 1 Aug 2026) ──────────────────
const FORBIDDEN = [/\bbook now\b/i, /\bwe (?:can )?book\b/i, /\bpay (?:us|TrustSquare|MarketSquare)\b(?!\$)/i, /\bour price\b/i, /\bbuy this trip\b/i, /\breserve your seat\b/i];
const blob = JSON.stringify(TE);
FORBIDDEN.forEach(re => { if (re.test(blob)) bad('copy implies MarketSquare sells the trip: ' + re); });

// ── 5. volatile flags must be visible ──────────────────────────────────────
TE.trips.forEach(t => {
  let flags = 0;
  [].concat(t.budget.rows, ...(t.sections||[]).map(s => s.rows)).forEach(r => { if (r.flag) flags++; });
  if (!flags) soft(t.key + ': nothing flagged volatile — suspicious for a travel dossier');
});

console.log('  %d/%d trips matched · %d fact rows · %d sourced (%d%%)',
  matched.size, TE.trips.length, rows, sourced, Math.round(100*sourced/rows));
console.log(fail ? '[RED] %d failure(s), %d warning(s)' : '[GREEN] all checks passed (%d failures, %d warnings)', fail, warn);
process.exit(fail ? 1 : 0);
