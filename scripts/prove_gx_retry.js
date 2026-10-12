#!/usr/bin/env node
/* prove_gx_retry.js -- GX-RETRY-1 (David, 12 Oct 2026), executed. Runs the REAL msGenericExLoad out of ms.js with a
   network that drops the first request for the trainer examples (what happened on his page load) and checks that the
   Tutors cards arrive within seconds, without waiting for the 3-minute refresh.   node scripts/prove_gx_retry.js [ms.js] */
const fs = require('fs'), path = require('path');
const src = fs.readFileSync(process.argv[2] || path.join(__dirname, '..', 'ms.js'), 'utf8');
const a = src.indexOf('const _msGxCache = new Map();'), b = src.indexOf('\nfunction msGenericExSheet(', a);
if (a < 0 || b < 0) { console.log('FAIL: msGenericExLoad not found'); process.exit(1); }
const hasRetry = src.slice(a, b).includes('_msGxRetry(tkey, seq)');
const calls = { roles: 0, trainers: 0 }; let dropTrainers = 1, dropRoles = 0, renders = 0;
const mk = (cat, n, trainer) => Array.from({ length: n }, (_, i) => ({ role_key: (trainer ? 't' : 'r') + i, service_type: (trainer ? 'Coach ' : 'Worker ') + i, category: cat }));
const sandbox = {
  BEA_ENABLED: true, BEA_URL: '', isOffline: () => false, activeCountry: { iso2: 'ZA' }, activeCity: { name: 'Pretoria' },
  localStorage: { getItem: () => 'en' }, LISTINGS: [], _msListSeq: 1, console,
  _svcTypeMatches: () => false, _msMapBeaListing: row => ({ cat: row.category, title: row.service_type, service_type: row.service_type }),
  renderGrid: () => { renders++; }, renderCatCounts: () => {}, setTimeout, encodeURIComponent,
  fetch: async url => {
    const k = url.includes('/examples/trainers') ? 'trainers' : 'roles'; calls[k]++;
    if (k === 'trainers' && dropTrainers-- > 0) throw new Error('dropped');
    if (k === 'roles' && dropRoles-- > 0) throw new Error('dropped');
    return { ok: true, json: async () => (k === 'trainers' ? mk('Tutors', 47, true) : mk('Services', 45, false)) };
  },
};
const fn = new Function(...Object.keys(sandbox), src.slice(a, b) + '\nreturn { load: msGenericExLoad };');
const api = fn(...Object.values(sandbox));
const count = cat => sandbox.LISTINGS.filter(l => l.cat === cat && l.generic).length;
(async () => {
  let fails = 0; const say = (ok, msg) => { console.log((ok ? 'PASS  ' : 'FAIL  ') + msg); if (!ok) fails++; };
  await api.load(1);
  console.log('page load, the trainer request dropped: Services cards %d, Tutors cards %d', count('Services'), count('Tutors'));
  say(count('Services') === 45 && count('Tutors') === 0, 'the fault is reproduced: Services has its cards, Tutors has none');
  await new Promise(r => setTimeout(r, 2600));
  console.log('2.6 s later:                            Services cards %d, Tutors cards %d (trainer requests made: %d)', count('Services'), count('Tutors'), calls.trainers);
  say(count('Tutors') === 47 && count('Services') === 45, 'the Tutors cards arrive within seconds, Services unchanged (no duplicates)');
  say(calls.trainers === 2, 'exactly one ask-again was needed');
  sandbox.LISTINGS.length = 0; dropRoles = 1;
  const fn2 = new Function(...Object.keys(sandbox), src.slice(a, b) + '\nreturn { load: msGenericExLoad };'); const api2 = fn2(...Object.values(sandbox));
  await api2.load(1); const before = count('Services');
  await new Promise(r => setTimeout(r, 2600));
  say(before === 0 && count('Services') === 45 && count('Tutors') === 47, 'a dropped Services request recovers the same way (both tiles filled)');
  console.log(fails ? '\nFAULT REPRODUCES (' + (hasRetry ? 'retry present but not working' : 'no retry in this ms.js') + ')' : '\nPROVED: a dropped example request is asked again within seconds');
  process.exit(fails ? 1 : 0);
})();
