// FIND-HONOUR-1 + FIND-BANDS-1 (RG-0817, RG-0841, 4 Oct 2026): Quick's Find honours every answer and fills local-first (RUL-118).
// LIVE=1 node verify_quick_find_honour.mjs        -> walks the real https://trustsquare.co/quick/ (writes refused)
// node verify_quick_find_honour.mjs quick.html    -> pre-deploy: serves that file as /quick/, reads pass through to the live API
import { chromium } from 'playwright';
import fs from 'fs';
const FILE = process.argv[2] || 'new.html', SHOT = process.argv[3] || '';
const html = fs.readFileSync(FILE, 'utf8');
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args:['--no-sandbox'] });
const ctx = await browser.newContext({ viewport:{width:400,height:900}, isMobile:true, hasTouch:true, deviceScaleFactor:1, timezoneId:'Africa/Johannesburg', locale:'en-ZA' });
await ctx.route('**/*', async route => {
  const u = route.request().url();
  if (/^https:\/\/trustsquare\.co\/quick\/?(\?|$)/.test(u)) return route.fulfill({status:200, contentType:'text/html', body:html});
  if (route.request().method() !== 'GET') return route.fulfill({status:204, body:''});   // never write to live
  return route.continue();
});
const page = await ctx.newPage(); const errs=[]; page.on('pageerror', e=>errs.push(String(e.message).slice(0,160)));
await page.goto('https://trustsquare.co/quick/?cc=ZA&city=Pretoria', {waitUntil:'domcontentloaded'});
await page.waitForFunction(() => typeof CATS!=='undefined' && typeof drawLookup==='function', null, {timeout:30000});
await page.waitForTimeout(1500);
async function find(catKey, pk, shot){
  const r = await page.evaluate(async ({catKey, pk}) => {
    ci = CATS.findIndex(c => c.key===catKey); mode='find'; step=0; picks = pk.map(p => Object.assign({photo:null}, p)); narrow=[];
    drawLookup();
    const t0=Date.now(); while(Date.now()-t0<20000){ await new Promise(r=>setTimeout(r,250)); if(!/Looking on/.test(document.querySelector('#screen .q')?.textContent||'')) break; }
    await new Promise(r=>setTimeout(r,300));
    let band=''; const ads=[];
    for (const el of document.querySelectorAll('#screen .grid > *')){
      if (el.classList.contains('lkband')){ band=el.textContent; continue; }
      if (!el.classList.contains('ad')) continue;
      ads.push({t:el.querySelector('.t')?.textContent, sub:el.querySelector('.sub')?.textContent, band,
        ex: !!el.querySelector('.exrib'), lid: el.getAttribute('data-lid'), img: el.querySelector('img')?.getAttribute('src')}); }
    return {head: document.querySelector('#screen .q')?.textContent, count: document.querySelector('#screen .count')?.textContent, ads};
  }, {catKey, pk});
  if (shot && SHOT) await page.screenshot({path: SHOT + shot + '.png'});
  return r;
}
const cases = [
  ['A townhouse to RENT in Pretoria East', 'property', [{key:'what',label:'Townhouse',photo:'prop_townhouse'},{key:'deal',label:'Renting'},{key:'where',label:'Pretoria East'}], 'rent_pe'],
  ['A townhouse to BUY in Menlyn',         'property', [{key:'what',label:'Townhouse',photo:'prop_townhouse'},{key:'deal',label:'Buying'},{key:'where',label:'Menlyn'}], 'buy_menlyn'],
  ['A townhouse to BUY in Mamelodi',       'property', [{key:'what',label:'Townhouse',photo:'prop_townhouse'},{key:'deal',label:'Buying'},{key:'where',label:'Mamelodi'}], 'buy_mamelodi'],
  ['A townhouse to BUY in Rietvalleirand (typed)', 'property', [{key:'what',label:'Townhouse',photo:'prop_townhouse'},{key:'deal',label:'Buying'},{key:'where',label:'Rietvalleirand'}], 'buy_riet'],
  ['A flat to RENT in Waterkloof (typed)', 'property', [{key:'what',label:'Flat',photo:'prop_flat'},{key:'deal',label:'Renting'},{key:'where',label:'Waterkloof'}], 'rent_wk'],
  ['A flat to BUY in Waterkloof (typed)',  'property', [{key:'what',label:'Flat',photo:'prop_flat'},{key:'deal',label:'Buying'},{key:'where',label:'Waterkloof'}], 'buy_wk'],
  ['Cars: a bakkie under R150k in Pretoria East', 'cars', [{key:'what',label:'Bakkie'},{key:'price',label:'Under R150k'},{key:'where',label:'Pretoria East'}], 'cars'],
  ['Tutors: maths, high school, Centurion', 'tutors', [{key:'what',label:'Maths'},{key:'level',label:'High school'},{key:'where',label:'Centurion'}], 'tutors'],
  ['Local Market: food, Menlyn', 'localmarket', [{key:'what',label:'Food & preserves'},{key:'where',label:'Menlyn'}], 'lm'],
  ['A house to BUY in Pretoria East',      'property', [{key:'what',label:'House',photo:'prop_main'},{key:'deal',label:'Buying'},{key:'where',label:'Pretoria East'}], 'buy_house_pe'],
];
const out = {};
for (const [name, k, pk, shot] of cases){ out[shot] = await find(k, pk, shot); console.log('\n# '+name+'\n  '+out[shot].head+' | '+(out[shot].count||'')); out[shot].ads.forEach(a=>console.log('   -', a.band?('['+a.band+']'):'', a.t, '|', a.sub, a.ex?'[AI EXAMPLE]':'', 'lid='+a.lid, (a.img||'').split('/').pop())); }
// FIND-AREAS-LIVE-1: the area question offers the suburbs of live adverts that fit her answers so far
async function areaOptions(catKey, pk){
  return await page.evaluate(async ({catKey, pk}) => {
    ci = CATS.findIndex(c => c.key===catKey); mode='find'; picks = pk.map(p => Object.assign({photo:null}, p)); narrow=[];
    flow(); await new Promise(r=>setTimeout(r,4000));
    const f=flow(), s=f.steps.find(x=>x.key==='where'); step=f.steps.indexOf(s); drawStep();
    await new Promise(r=>setTimeout(r,500));
    return {kind:s.kind, opts:s.tiles.map(t=>t.t)};
  }, {catKey, pk});
}
const optRent = await areaOptions('property', [{key:'what',label:'Flat',photo:'prop_flat'},{key:'deal',label:'Renting'}]);
if (SHOT) await page.screenshot({path: SHOT + 'where_flat_rent.png'});
const optBuyTown = await areaOptions('property', [{key:'what',label:'Townhouse',photo:'prop_townhouse'},{key:'deal',label:'Buying'}]);
console.log('\n# area options, Flat + Renting:', optRent.kind, optRent.opts.join(', '));
console.log('# area options, Townhouse + Buying:', optBuyTown.kind, optBuyTown.opts.join(', '));
out.brooklyn = await find('property', [{key:'what',label:'Flat',photo:'prop_flat'},{key:'deal',label:'Renting'},{key:'where',label:'Brooklyn'}], 'rent_brooklyn');
console.log('# Flat+Renting+Brooklyn:', out.brooklyn.head, out.brooklyn.ads.map(a=>(a.band?'['+a.band+'] ':'')+a.t+' | '+a.sub+(a.ex?' [EX]':'')).join(' ; '));
out.menlynflat = await find('property', [{key:'what',label:'Flat',photo:'prop_flat'},{key:'deal',label:'Renting'},{key:'where',label:'Menlyn'}], 'rent_menlyn');
console.log('# Flat+Renting+Menlyn:', out.menlynflat.head, out.menlynflat.ads.map(a=>(a.band?'['+a.band+'] ':'')+a.t+' | '+a.sub+(a.ex?' [EX]':'')).join(' ; '));
const ad468 = s => out[s].ads.find(a => a.lid==='468');
const fails=[];
if (ad468('rent_pe')) fails.push('468 (to sell) shown under Renting');
if (out.rent_pe.ads.some(a=>!a.ex && /rent|let/i.test('') )) {}
if (ad468('buy_menlyn') && !/near you/.test(out.buy_menlyn.head)) fails.push('Menlyn head claims 468 is in Menlyn: '+out.buy_menlyn.head);
if (ad468('buy_menlyn') && ad468('buy_menlyn').band!=='Nearby') fails.push('468 under Menlyn is not labelled Nearby');
if (!ad468('buy_riet') || ad468('buy_riet').band==='Nearby' || !/on TrustSquare/.test(out.buy_riet.head)) fails.push('468 not first-band for Rietvalleirand');
if (!out.rent_wk.ads.some(a=>a.lid && !a.ex && /Waterkloof/.test(a.sub) && a.band!=='Nearby')) fails.push('no first-band Waterkloof flat for Flat+Renting');
if (out.buy_wk.ads.some(a=>a.lid && !a.ex && /Apartment — (Waterkloof|Brooklyn)/.test(a.t||''))) fails.push('a rental apartment shown under Buying');
if (!optRent.opts.includes('Brooklyn') || !optRent.opts.includes('Waterkloof')) fails.push('Brooklyn/Waterkloof not offered as areas for Flat+Renting');
if (!optBuyTown.opts.includes('Rietvalleirand')) fails.push('Rietvalleirand not offered for Townhouse+Buying');
if (optBuyTown.opts.includes('Brooklyn')) fails.push('Brooklyn (rentals) offered for Townhouse+Buying');
if (!out.brooklyn.ads.some(a=>/Brooklyn/.test(a.sub) && !a.ex && a.band!=='Nearby')) fails.push('the Brooklyn flat is not first-band under Brooklyn');
const bm = out.menlynflat.ads.filter(a=>/Brooklyn/.test(a.sub) && !a.ex);
if (bm.some(a=>a.band!=='Nearby') || (bm.length && !/near you/.test(out.menlynflat.head))) fails.push('the Brooklyn flat is presented as IN Menlyn');
console.log('\npage errors:', errs.length ? errs : 'none');
console.log(fails.length ? 'FAIL:\n - '+fails.join('\n - ') : 'PASS: every answer honoured, local-first bands (RUL-118)');
await browser.close();
process.exit(fails.length ? 1 : 0);
