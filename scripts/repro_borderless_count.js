#!/usr/bin/env node
/*
 * BORDERLESS-COUNT-1 repro — TS-0032 (Maun) / TS-0033 (Sydney), 14 Aug 2026.
 *
 * Two testers, opposite ends of the world, filed the same fault: pick a city, the
 * Adventures tile shows a small number ("2 listings" in Sydney, "1" in Maun), tap it,
 * and the Adventures page shows every adventure on the platform — "it reverts away
 * from Botswana and shows me many adventures".
 *
 * Neither surface was wrong on its own. renderCatCounts() filtered EVERY category to
 * activeCity; renderAdvGrid() has no city filter at all, by design (Adventures is
 * deliberately borderless — the 28 Jun ruling, and COUNTRY-FILTER-1 made ALL the
 * default). They simply disagreed, and the tile was the liar: it counted a set the
 * grid can never show.
 *
 * This reproduces the DISAGREEMENT itself rather than either number: it runs the tile
 * predicate and the grid predicate over one fixture and asserts they agree.
 *
 * Usage:  node scripts/repro_borderless_count.js [path/to/ms.js]
 * Exit 0 = tile and grid agree. Exit 1 = the tile promises what the grid won't show.
 * Run it against ms.js.bak-borderless-* to watch the original fail — that is the point.
 */
const fs = require('fs');
const path = require('path');

const target = process.argv[2] || path.join(__dirname, '..', 'ms.js');
const src = fs.readFileSync(target, 'utf8');

// The fixture is the testers' world: one Botswana adventure, two Australian, three ZA.
const LISTINGS = [
  { id: 'l1', cat: 'adventures_experiences', city: 'Maun',      country: 'BW', isLive: true },
  { id: 'l2', cat: 'adventures_experiences', city: 'Sydney',    country: 'AU', isLive: true },
  { id: 'l3', cat: 'adventures_accommodation', city: 'Sydney',  country: 'AU', isLive: true },
  { id: 'l4', cat: 'adventures_experiences', city: 'Cape Town', country: 'ZA', isLive: true },
  { id: 'l5', cat: 'adventures_accommodation', city: 'Pretoria', country: 'ZA', isLive: true },
  { id: 'l6', cat: 'adventures_experiences', city: 'Pretoria',  country: 'ZA', isLive: true },
  { id: 'l7', cat: 'cars',                   city: 'Pretoria',  country: 'ZA', isLive: true },
];

const isAdv = l => String(l.cat || '').toLowerCase().startsWith('adventures');

// What the Adventures GRID shows: country filter only, never a city filter.
function gridCount(advCountry) {
  return LISTINGS.filter(l => {
    if (!isAdv(l)) return false;
    if (advCountry !== 'ALL') {
      const lc = (l.country || l.city_country || 'ZA').toUpperCase();
      if (lc !== advCountry) return false;
    }
    return true;
  }).length;
}

// What the TILE claims, read out of the file under test: does renderCatCounts exempt
// borderless categories from the active-city filter, or not?
const exempts = /BORDERLESS_CATS/.test(src) &&
                /isBorderlessCat\(normCat\(l\.cat\)\)/.test(src) &&
                /isBorderlessCat\(_cat0\)/.test(src);

function tileCount(activeCity, advCountry) {
  return LISTINGS.filter(l => {
    if (!isAdv(l)) return false;
    if (exempts) {
      if (advCountry !== 'ALL') {
        const lc = (l.country || l.city_country || 'ZA').toUpperCase();
        if (lc !== advCountry) return false;
      }
      return true;
    }
    if (l.isLive) {                       // the pre-fix behaviour: city-scoped count
      const lCity = l.city || l.area || '';
      if (lCity && activeCity && lCity !== activeCity) return false;
    }
    return true;
  }).length;
}

let bad = 0;
console.log(`file under test: ${target}`);
console.log(`renderCatCounts exempts borderless categories: ${exempts ? 'YES' : 'NO'}\n`);
for (const [city, advCountry, who] of [
  ['Sydney',    'ALL', 'TS-0033'],
  ['Maun',      'ALL', 'TS-0032'],
  ['Cape Town', 'ALL', 'baseline ZA'],
  ['Sydney',    'AU',  'picker narrowed to AU'],
]) {
  const t = tileCount(city, advCountry), g = gridCount(advCountry);
  const ok = t === g;
  if (!ok) bad++;
  console.log(`  ${ok ? 'OK  ' : 'FAIL'}  ${who.padEnd(22)} city=${city.padEnd(10)} ` +
              `advCountry=${advCountry.padEnd(4)} tile says ${t}, grid shows ${g}` +
              (ok ? '' : `  <-- the tile promises ${t}, the tap delivers ${g}`));
}
console.log();
if (bad) {
  console.log(`REPRO: ${bad} case(s) where the Adventures tile disagrees with its own page.`);
  console.log('That is TS-0032 / TS-0033 exactly.');
  process.exit(1);
}
console.log('Tile and grid agree in every case — the number on the tile survives the tap.');
process.exit(0);
