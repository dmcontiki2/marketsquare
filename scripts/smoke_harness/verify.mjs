// Executes openDetail() on every super listing and asserts real rendering.
// Usage: node verify.mjs   (server.py must be running on :8471; ms.js in static/ with BEA_URL rebased to '')
import { chromium } from 'playwright';
const b = await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
const page = await b.newPage();
await page.goto('http://127.0.0.1:8471/', {waitUntil:'domcontentloaded'});
await page.waitForTimeout(2500);
const r = await page.evaluate(async () => {
  await loadLiveListings(); await new Promise(r=>setTimeout(r,1200));
  const supers = LISTINGS.filter(l=>l.super_example);
  const out = {listings: LISTINGS.length, supers: supers.length, tests: {}};
  for (const s of supers) {
    try {
      openDetail(s.id);
      const h = document.getElementById('screen-detail').innerHTML;
      out.tests[s.id] = { title:(h.match(/dtitle">([^<]+)</)||[])[1]||'?', rendered:h.length,
        map:(h.match(/adventures_([a-z0-9]+)_map\.html/)||[])[1]||'none',
        extensions:(h.match(/font-weight:700;font-size:14px/g)||[]).length };
    } catch(e) { out.tests[s.id] = {THREW: e.message}; }
  }
  return out;
});
console.log(JSON.stringify(r,null,1));
const bad = Object.entries(r.tests).filter(([k,v])=>v.THREW);
if (bad.length) { console.error('FAIL: listings threw:', bad.map(b=>b[0]).join(', ')); process.exit(1); }
console.log('SMOKE OK - every super listing opens and renders.');
await b.close();
