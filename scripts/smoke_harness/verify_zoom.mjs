// ZOOM rendered proof at phone width (412x915) against the REAL app on the rig origin.
import { chromium } from 'playwright';
const B = 'http://127.0.0.1:8000';
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args:['--no-sandbox'] });
const ctx = await browser.newContext({ viewport: { width: 412, height: 915 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
await ctx.addCookies([{name:'ts_review', value: (await import('fs')).readFileSync('process.env.RIG_REVIEW_TOKEN_FILE || '/home/claude/rig_review_token.txt'','utf8').trim(), domain:'127.0.0.1', path:'/'}]);
const page = await ctx.newPage();
const fails = [];
const errs = [];
page.on('pageerror', e => errs.push(String(e.message).slice(0,200)));
async function waitListings(){ await page.waitForFunction(() => typeof LISTINGS!=='undefined' && LISTINGS.some(l => l.isLive), null, {timeout: 30000}); }
async function sheet(){ return page.evaluate(() => { const el=document.getElementById('zoom-sheet'); if(!el||!el.classList.contains('open')) return null; const r=el.getBoundingClientRect(); const opts=[...el.querySelectorAll('.zoom-opts .zoom-opt:not(.more):not(.locked)')].map(o=>({label:o.querySelector('.lbl')?.textContent, n:parseInt(o.querySelector('.n')?.textContent||'0'), h:o.getBoundingClientRect().height, w:o.getBoundingClientRect().width})); const locked=[...el.querySelectorAll('.zoom-opt.locked')].map(o=>({label:o.querySelector('.lbl')?.textContent, n:parseInt(o.querySelector('.n')?.textContent||'0')})); return {top:r.top, height:r.height, q: el.querySelector('.zoom-q span')?.textContent||null, opts, locked, chips:[...el.querySelectorAll('.zoom-chip')].map(c=>c.textContent.replace('×','').trim()), count: el.querySelector('.zoom-count')?.textContent, bar: el.querySelector('.zoom-bar')?.textContent||null, state: JSON.parse(JSON.stringify({chips: zoomState.chips, mode: zoomState.mode, total: zoomState.res&&zoomState.res.total, qfacet: zoomState.res&&zoomState.res.question&&zoomState.res.question.facet}))}; }); }
async function gridCount(){ return page.evaluate(() => document.querySelectorAll('#listing-grid .lcard').length); }
async function advCount(){ return page.evaluate(() => document.querySelectorAll('#adv-grid .lcard, #adv-grid .adv-card, #adv-grid [class*=card]').length); }
async function settle(){ await page.waitForFunction(() => !zoomState.busy, null, {timeout: 15000}); await page.waitForTimeout(150); }
function check(cond, msg){ if(!cond) fails.push(msg); }

// ── 1. flag OFF: nothing changes ─────────────────────────────────────────────
await page.goto(B + '/?baseline=0', { waitUntil: 'domcontentloaded' });
await waitListings();
await page.evaluate(() => filterBrowse('Property'));
await page.waitForTimeout(400);
let s = await sheet();
check(s === null, 'flag OFF: zoom sheet rendered (' + JSON.stringify(s) + ')');
await page.evaluate(() => openFilterSheet('property'));
await page.waitForTimeout(300);
const oldSheet = await page.evaluate(() => document.getElementById('fs-property').classList.contains('open'));
check(oldSheet, 'flag OFF: the pre-Zoom filter sheet did not open');
const dataFlag = await page.evaluate(() => document.documentElement.getAttribute('data-baseline'));
check(dataFlag === '0', 'flag OFF: data-baseline=' + dataFlag);
console.log('flag OFF: pre-Zoom view intact, no funnel');

// ── 2. flag ON (local preview) — Property door ───────────────────────────────
await page.goto(B + '/?baseline=1', { waitUntil: 'domcontentloaded' });
await waitListings();
await page.evaluate(() => filterBrowse('Property'));
await settle();
s = await sheet();
check(s && s.q, 'Property: no question on the door: ' + JSON.stringify(s));
console.log('Property door →', s.q, s.opts.map(o=>o.label+'('+o.n+')').join(', '), '| grid', await gridCount(), '| count', s.count);
check(s.state.qfacet && !String(s.state.qfacet).startsWith('geo_'), 'Property: geography opened the funnel');
check(s.opts.length <= 6, 'Property: more than 6 options rendered');
check(s.opts.every(o => o.n > 0), 'Property: a zero-count option rendered');
check(s.opts.every(o => o.h >= 44), 'Property: an option under 44px: ' + JSON.stringify(s.opts.map(o=>o.h)));
check(s.top >= 915/2, 'Property: question not in the lower half (top=' + s.top + ')');
const sw = await page.evaluate(() => document.documentElement.scrollWidth);
check(sw <= 412, 'horizontal overflow: scrollWidth=' + sw);
const sumOpts = s.opts.reduce((a,o)=>a+o.n,0);
check(sumOpts === s.state.total, 'Property: option counts ' + sumOpts + ' != result count ' + s.state.total);
check((await gridCount()) === s.state.total, 'Property: grid cards ' + (await gridCount()) + ' != funnel total ' + s.state.total);
// journey: rent -> next question -> ...
const rent = s.opts.find(o => /rent/i.test(o.label));
check(!!rent, 'Property: Rent not offered');
await page.evaluate(() => zoomPick('mode','Rent')); await settle();
s = await sheet();
console.log('after Rent →', s.q, s.opts.map(o=>o.label+'('+o.n+')').join(', '), '| chips', s.chips, '| total', s.state.total, '| grid', await gridCount());
check((await gridCount()) === s.state.total, 'Property/Rent: grid != total');
check(s.opts.every(o => o.n > 0), 'Property/Rent: zero-count option');
let taps = 1;
// walk to a suburb then a street if offered, always the top option, max 3 more taps
for (let i=0;i<3; i++){
  if(s.state.mode==='bar'){ await page.evaluate(() => zoomKeepNarrowing()); await page.waitForTimeout(150); s = await sheet(); }
  if(!s || !s.q) break;
  const top = s.opts[0];
  await page.evaluate(({f,v}) => zoomPick(f,v), {f:s.state.qfacet, v:(await page.evaluate(()=>zoomState.res.question.options[0].v))});
  taps++; await settle(); s = await sheet();
  console.log('tap', taps, '→', s.q || '(arrived)', s.chips, 'total', s.state.total, 'grid', await gridCount(), 'mode', s.state.mode);
  check((await gridCount()) === s.state.total, 'walk: grid != total at tap ' + taps);
}
check(taps <= 4, 'Property walk took ' + taps + ' taps');
// dropping a parent drops children: drop 'mode' and check beds/budget/pets chips vanish
await page.evaluate(() => zoomDrop('mode')); await settle(); s = await sheet();
check(!('beds' in s.state.chips) && !('budget' in s.state.chips) && !('pets' in s.state.chips), 'dropping mode left a child chip: ' + JSON.stringify(s.state.chips));
console.log('drop mode → chips', s.state.chips);

// ── 3. Cars: model never before make; make→model dependency in the rendered app ──
await page.evaluate(() => filterBrowse('Cars')); await settle(); s = await sheet();
console.log('Cars door →', s.q, s.opts.map(o=>o.label+'('+o.n+')').join(', '), 'auto', s.chips);
check(s.state.qfacet !== 'model' || ('make' in s.state.chips), 'Cars asked model before make');
check(s.state.qfacet && !String(s.state.qfacet).startsWith('geo_'), 'Cars: geography opened the funnel');
// typed shortcut
await page.evaluate(() => { document.getElementById('zoom-type-in') && (document.getElementById('zoom-type-in').value='toyota hilux automatic'); zoomType(); }); await settle(); s = await sheet();
console.log('typed "toyota hilux automatic" → chips', s.state.chips, 'total', s.state.total);
check(s.state.chips.make === 'Toyota' && /hilux/i.test(s.state.chips.model||''), 'typed shortcut did not fill make/model: ' + JSON.stringify(s.state.chips));
await page.evaluate(() => zoomDrop('make')); await settle(); s = await sheet();
// with every other chip still pinning the set to one vehicle, make/model may return as AUTO
// chips (3.6, lossless) -- what must be gone is the USER's chip: any make/model present is auto
const mm = await page.evaluate(() => (zoomState.res.chips||[]).filter(c => c.facet==='make'||c.facet==='model'));
check(mm.every(c => c.auto), 'Cars: dropping make left a user model/make chip: ' + JSON.stringify(mm));
console.log('drop make →', mm.map(c=>c.facet+'='+c.v+(c.auto?' (auto)':'')).join(', '));

// ── 4. Collectors: never asked a street; Tutors: no geo first ─────────────────
for (const cat of ['Collectors','Tutors','Services']){
  await page.evaluate(c => filterBrowse(c), cat); await settle(); s = await sheet();
  console.log(cat + ' door →', s.q, s.opts.map(o=>o.label+'('+o.n+')').join(', '), 'auto', s.chips);
  check(!s.state.qfacet || !String(s.state.qfacet).startsWith('geo_'), cat + ': geography opened the funnel');
  if (cat==='Collectors'){
    // walk every question and record facets asked
    const asked = [];
    for (let i=0;i<6;i++){ if(s.state.mode==='bar'){ await page.evaluate(() => zoomKeepNarrowing()); await page.waitForTimeout(120); s = await sheet(); } if(!s.state.qfacet) break; asked.push(s.state.qfacet); await page.evaluate(() => zoomPick(zoomState.res.question.facet, zoomState.res.question.options[0].v)); await settle(); s = await sheet(); }
    check(!asked.includes('geo_street') && !asked.includes('geo_suburb'), 'Collectors asked ' + asked.join(','));
    console.log('Collectors asked:', asked.join(' → '));
  }
}

// ── 5. Adventures (Travel): geography opens at COUNTRY, borderless ────────────
await page.evaluate(() => filterBrowse('Adventures')); await settle(); s = await sheet();
console.log('Adventures door →', s.q, s.opts.map(o=>o.label+'('+o.n+')').join(', '), 'auto', s.chips, 'total', s.state.total);
check(s.state.qfacet && !String(s.state.qfacet).startsWith('geo_'), 'Travel: geography opened the funnel');
const askedT = [];
for (let i=0;i<6;i++){ if(s.state.mode==='bar'){ await page.evaluate(() => zoomKeepNarrowing()); await page.waitForTimeout(120); s = await sheet(); } if(!s.state.qfacet) break; askedT.push(s.state.qfacet); if(String(s.state.qfacet).startsWith('geo_')) break; await page.evaluate(() => zoomPick(zoomState.res.question.facet, zoomState.res.question.options[0].v)); await settle(); s = await sheet(); }
console.log('Travel asked:', askedT.join(' → '));
const firstGeo = askedT.find(f => f.startsWith('geo_'));
check(!firstGeo || firstGeo === 'geo_country', 'Travel geography opened at ' + firstGeo + ', not country');
const advGrid = await page.evaluate(() => document.querySelectorAll('#adv-grid > *').length);
console.log('adventures grid children', advGrid, 'total', s.state.total);

// ── 6. arrival bar + save + screenshot ────────────────────────────────────────
await page.evaluate(() => filterBrowse('Property')); await settle();
await page.evaluate(() => zoomPick('mode','Rent')); await settle(); s = await sheet();
await page.screenshot({ path: (process.env.SHOT_DIR||'/home/claude')+'/zoom_phone_question.png' });
await page.evaluate(() => { zoomState.mode='bar'; _zoomRender(); }); await page.waitForTimeout(200);
s = await sheet(); check(!!s.bar && /tap/.test(s.bar), 'arrival bar missing: ' + s.bar);
await page.screenshot({ path: (process.env.SHOT_DIR||'/home/claude')+'/zoom_phone_bar.png' });
await page.evaluate(() => zoomSave()); await page.waitForTimeout(300);
const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('ts_zoom_watches')||'[]').length);
check(saved >= 1, 'watch not saved');
// ranking order: cards in the grid follow the server ids order, pinned first
const order = await page.evaluate(() => { const ids=[...document.querySelectorAll('#listing-grid .lcard')].map(c=>(c.getAttribute('onclick')||'').match(/openDetail\('([^']+)'\)/)?.[1]).filter(Boolean); return {ids, srv: zoomState.res.ids.map(i=>'bea_'+i)}; });
check(JSON.stringify(order.ids) === JSON.stringify(order.srv.slice(0, order.ids.length)), 'grid order != ranking order\n' + JSON.stringify(order));
console.log('grid order follows ranking score:', order.ids.length, 'cards');
const realErrs = errs.filter(e => !/r2Fallback/.test(e)); check(realErrs.length === 0, 'page errors: ' + realErrs.join(' | '));
await browser.close();
if (fails.length){ console.log('\nFAIL'); fails.forEach(f => console.log(' -', f)); process.exit(1); }
console.log('\nALL ZOOM RENDERED CHECKS PASS (412x915)');
