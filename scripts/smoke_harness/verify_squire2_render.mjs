// verify_squire2_render.mjs -- SQUIRE-2 Phase 1, the RENDERED half (SQUIRE_2_BUILD_BRIEF.md s5 item 10).
// Loads the real marketsquare.html + ms.js in headless Chromium at phone size (412x915) against the real BEA rig
// (seeded by verify_squire2.py with RIG_LEAVE_ARMED=1), signed in as the Pro rig user, and asserts what a user SEES:
// the kind/rules/card-list form, per-line advice chips, the reality-check line, "Not for me" learning, the crux
// report on a property match, alerts + the monthly report, the PA panel ABSENT while squire_pro_pa is OFF and
// present (caution + accept box, Start refused until ticked) only when a TEST flags file turns it on, and a
// Starter user seeing what Pro buys with no capability. Baseline is turned on only by ?baseline=1 on localhost.
// Env: B (default http://127.0.0.1:8000), CHROME (executable), LDLP (extra lib path), FLAGS (the rig's flags file),
//      SHOT_DIR (screenshots), JWT (rig secret), REVIEW (rig review secret).
import { chromium } from 'playwright-core';
import fs from 'fs';
import crypto from 'crypto';
const B = process.env.B || 'http://127.0.0.1:8000';
const PRO = 'pro@rig.test', STARTER = 'starter@rig.test';
function b64u(o){ return Buffer.from(typeof o==='string'?o:JSON.stringify(o)).toString('base64url'); }
function jwt(payload, secret){ const h=b64u({alg:'HS256',typ:'JWT'}), p=b64u(payload); return h+'.'+p+'.'+crypto.createHmac('sha256', secret).update(h+'.'+p).digest('base64url'); }
const JWT = process.env.JWT || 'rigjwt_rigjwt_rigjwt_rigjwt_rigjwt_rigjwt', REVIEW = process.env.REVIEW || 'rigsecret_rigsecret_rigsecret_rigsecret';
const exp = Math.floor(Date.now()/1000) + 86400;
const tok = em => jwt({scope:'user', sub:em, exp}, JWT);
const fails = []; const check = (c, m) => { if(!c){ fails.push(m); console.log('  FAIL:', m); } };
const browser = await chromium.launch({ executablePath: process.env.CHROME, args:['--no-sandbox'], env:{...process.env, LD_LIBRARY_PATH: process.env.LDLP || ''} });
const ctx = await browser.newContext({ viewport:{width:412,height:915}, isMobile:true, hasTouch:true, deviceScaleFactor:2 });
await ctx.addCookies([{name:'ts_review', value: jwt({scope:'review', exp}, REVIEW), domain:'127.0.0.1', path:'/'},
                      {name:'ts_user', value: tok(PRO), domain:'127.0.0.1', path:'/'}]);
const page = await ctx.newPage(); const errs = [];
page.on('pageerror', e => errs.push(String(e.message).slice(0,160)));
page.on('dialog', d => d.dismiss());
await page.goto(B + '/?baseline=1', {waitUntil:'domcontentloaded'});
await page.waitForFunction(() => typeof goTo==='function' && typeof msRenderSquireCard==='function', null, {timeout:60000});
await page.evaluate(e => { localStorage.setItem('ms_user_email', e); localStorage.setItem('ms_aa_email', e); goTo('myspace'); }, PRO);
await page.waitForFunction(() => document.querySelector('#ms-squire-card #sq-kind'), null, {timeout:30000}).catch(()=>{});
// 1. the form
const form = await page.evaluate(() => { const c=document.getElementById('ms-squire-card'); if(!c) return null; const r=c.getBoundingClientRect();
  const h = s => { const e=c.querySelector(s); return e ? Math.round(e.getBoundingClientRect().height) : 0; };
  return {w:Math.round(r.width), kind:!!c.querySelector('#sq-kind'), pct:!!c.querySelector('#sq-pct'), nm:!!c.querySelector('#sq-nm'), cards:!!c.querySelector('#sq-cards'),
          btnH:h('#sq-brief-btn'), kindH:h('#sq-kind'), briefs:c.querySelectorAll('.sq-kind-badge').length, text:c.textContent}; });
console.log('form:', form && {w:form.w, briefs:form.briefs, btnH:form.btnH, kindH:form.kindH});
check(form && form.kind && form.pct && form.nm && form.cards, 'brief form lacks kind / rule / Near Mint / card list');
check(form && form.w > 0 && form.w <= 412, 'card wider than the phone');
check(form && form.btnH >= 44 && form.kindH >= 44, 'touch targets under 44px');
check(form && form.briefs >= 4, 'briefs not listed with their kind');
check(form && /sell/.test(form.text) && /Your rules:/.test(form.text), 'kind or rule summary not shown');
check(form && !/Premium data/.test(form.text), 'PA panel shown while squire_pro_pa is OFF');
check(form && /Recent alerts/.test(form.text) && /Squire monthly report/.test(form.text), 'alerts / monthly report not shown');
await page.screenshot({path:(process.env.SHOT_DIR||'.')+'/squire2_card.png'});
// 2. advice on the 30-card sell list
const sellId = await page.evaluate(() => (_sqState.status.briefs.filter(b => b.kind==='sell' && b.lines>0)[0]||{}).id);
await page.evaluate(id => sqAdvice(id), sellId);
await page.waitForFunction(id => document.querySelectorAll('#sq-adv-'+id+' .sq-adv-line').length > 0, sellId, {timeout:20000}).catch(()=>{});
const adv = await page.evaluate(id => { const el=document.getElementById('sq-adv-'+id); return {n: el.querySelectorAll('.sq-adv-line').length, text: el.textContent}; }, sellId);
console.log('advice lines rendered:', adv.n);
check(adv.n === 31 && /pass/.test(adv.text) && /warn/.test(adv.text) && /could not identify/.test(adv.text), 'advice not rendered one line per card with pass/warn/unidentified');
await page.locator('#sq-adv-'+sellId).screenshot({path:(process.env.SHOT_DIR||'.')+'/squire2_advice.png'}).catch(()=>{});
// 3. property brief: reality line, shortlist with "Not for me", crux report
const propId = await page.evaluate(() => (_sqState.status.briefs.filter(b => b.category==='Property' && b.rules && b.rules.exclude_suburbs)[0]||{}).id);
await page.evaluate(id => sqOpen(id), propId);
await page.waitForFunction(id => document.querySelector('#sq-sl-'+id+' .sq-fb'), propId, {timeout:30000}).catch(()=>{});
await page.waitForFunction(id => /Reality-check/.test((document.getElementById('sq-real-'+id)||{}).textContent||''), propId, {timeout:15000}).catch(()=>{});
const sl = await page.evaluate(id => ({fb: document.querySelectorAll('#sq-sl-'+id+' .sq-fb').length, crux: [...document.querySelectorAll('#sq-sl-'+id+' button')].filter(b=>/Crux report/.test(b.textContent)).length,
  intro: /Introduce me \(1T\)/.test(document.getElementById('sq-sl-'+id).textContent), real: (document.getElementById('sq-real-'+id)||{}).textContent||''}), propId);
console.log('property shortlist:', sl);
check(sl.fb >= 1 && sl.crux >= 1 && sl.intro, 'shortlist lacks Not-for-me / Crux report / the ordinary 1T intro');
check(/Reality-check/.test(sl.real), 'reality-check line not rendered');
const lid = await page.evaluate(id => { const b=[...document.querySelectorAll('#sq-sl-'+id+' button')].filter(b=>/Crux report/.test(b.textContent))[0]; const m=/sqCrux\(\d+,(\d+)\)/.exec(b.getAttribute('onclick')); return +m[1]; }, propId);
await page.evaluate(([b,l]) => sqCrux(b,l), [propId, lid]);
await page.waitForFunction(l => /Risks|no report/i.test((document.getElementById('sq-crux-'+l)||{}).textContent||''), lid, {timeout:60000}).catch(()=>{});
const crux = await page.evaluate(l => (document.getElementById('sq-crux-'+l)||{}).textContent||'', lid);
console.log('crux:', crux.slice(0,160));
check(/Risks/.test(crux) && /Advantages/.test(crux) && /Sold median nearby/.test(crux) || /no report, no charge/.test(crux), 'crux report neither rendered nor honestly refused');
await page.screenshot({path:(process.env.SHOT_DIR||'.')+'/squire2_property.png', fullPage:false});
// 4. learning through the UI: pick "Not that suburb" on the first match
const before = await page.evaluate(id => _sqState.status.briefs.filter(b=>b.id===id)[0].rules.exclude_suburbs.length, propId);
await page.evaluate(id => { const s=document.querySelector('#sq-sl-'+id+' .sq-fb'); s.value='not_suburb'; s.dispatchEvent(new Event('change')); }, propId);
await page.waitForFunction(([id,n]) => { const b=(_sqState.status.briefs||[]).filter(b=>b.id===id)[0]; return b && b.rules.exclude_suburbs && b.rules.exclude_suburbs.length>n; }, [propId, before], {timeout:20000}).catch(()=>{});
const after = await page.evaluate(id => _sqState.status.briefs.filter(b=>b.id===id)[0].rules.exclude_suburbs, propId);
console.log('learned exclusions:', after);
check(after.length > before, 'Not-for-me did not change the stored brief');
// 5. PA panel only with the switch on (TEST flags file), caution + accept box, Start refused until ticked
if (process.env.FLAGS) {
  fs.writeFileSync(process.env.FLAGS, JSON.stringify({paid_tiers_enabled:true, providers:{propertydata:true}, switches:{squire_pro_pa:true}, feed_costs_usd_month:{propertydata:30}}));
  await new Promise(r => setTimeout(r, 6000));          // the flag store re-reads its file within 5 s
  await page.evaluate(() => sqLoad()); await page.waitForTimeout(1500);
  const paId = await page.evaluate(() => (_sqState.status.briefs.filter(b => b.category==='Property' && !(b.rules&&b.rules.exclude_suburbs) && !b.pa)[0]||{}).id);
  await page.evaluate(id => { if(_sqState.open!==id) sqOpen(id); }, paId); await page.waitForTimeout(2500);
  const pa = await page.evaluate(() => /Premium data/.test(document.getElementById('ms-squire-card').textContent));
  check(pa, 'PA panel missing with the switch ON');
  await page.evaluate(id => { document.getElementById('sq-pa-feeds-'+id).value='propertydata'; sqPaQuote(id); }, paId);
  await page.waitForFunction(() => document.querySelector('.sq-caution'), null, {timeout:15000}).catch(()=>{});
  const q = await page.evaluate(() => ({caution:(document.querySelector('.sq-caution')||{}).textContent||'', box:!!document.querySelector('.sq-pa-quote input[type=checkbox]')}));
  console.log('PA quote caution:', q.caution.slice(0,90)+'…');
  check(/every month/.test(q.caution) && /monthly report/.test(q.caution) && q.box, 'caution text or accept box missing');
  const cid = await page.evaluate(() => +document.querySelector('.sq-pa-quote input[type=checkbox]').id.split('-').pop());
  await page.evaluate(c => sqPaAccept(c), cid); await page.waitForTimeout(1200);
  let st = await page.evaluate(async c => { const r = await fetch(location.origin+'/squire/status?email=pro@rig.test',{credentials:'include'}); const d=await r.json(); return (d.briefs.map(b=>b.pa).filter(p=>p&&p.charge_id===c)[0]||{}).status; }, cid);
  check(st === 'quoted', 'Start without ticking the caution was accepted: '+st);
  await page.screenshot({path:(process.env.SHOT_DIR||'.')+'/squire2_pa_caution.png'});
  await page.evaluate(c => { document.getElementById('sq-pa-ok-'+c).checked = true; sqPaAccept(c); }, cid); await page.waitForTimeout(2000);
  st = await page.evaluate(async c => { const r = await fetch(location.origin+'/squire/status?email=pro@rig.test',{credentials:'include'}); const d=await r.json(); return (d.briefs.map(b=>b.pa).filter(p=>p&&p.charge_id===c)[0]||{}).status; }, cid);
  check(st === 'active', 'ticked caution + Start did not start the plan: '+st);
  await page.evaluate(c => sqPaCancel(c), cid); await page.waitForTimeout(800);
  fs.writeFileSync(process.env.FLAGS, JSON.stringify({paid_tiers_enabled:false}));   // back to the shipped default
}
// 6. Starter sees what Pro buys, no capability
await ctx.addCookies([{name:'ts_user', value: tok(STARTER), domain:'127.0.0.1', path:'/'}]);
await page.evaluate(e => { localStorage.setItem('ms_user_email', e); localStorage.setItem('ms_aa_email', e); goTo('home'); goTo('myspace'); }, STARTER);
await page.waitForTimeout(2500);
const st2 = await page.evaluate(() => ({t:(document.getElementById('ms-squire-card')||{}).textContent||'', box: !!document.querySelector('#ms-squire-card #sq-kind')}));
check(/Pro plan/.test(st2.t) && !st2.box, 'Starter card leaks the capability');
const real = errs.filter(e => !/r2Fallback/.test(e)); check(real.length === 0, 'page errors: '+real.join(' | '));
await browser.close();
if (fails.length) { console.log('\nFAIL'); fails.forEach(f => console.log(' -', f)); process.exit(1); }
console.log('\nALL SQUIRE-2 RENDERED CHECKS PASS (412x915, real Chromium, real app code)');
