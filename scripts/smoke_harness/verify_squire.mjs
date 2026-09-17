import { chromium } from 'playwright';
import fs from 'fs';
import { execSync } from 'child_process';
const B='http://127.0.0.1:8000';
const PRO='tutors-nairobi-a@trustsquare.co', STARTER='tutors-nairobi-b@trustsquare.co';
const proTok=fs.readFileSync((process.env.RIG_PRO_TOKEN_FILE||'/home/claude/rig_pro_token.txt'),'utf8').trim(), stTok=fs.readFileSync((process.env.RIG_STARTER_TOKEN_FILE||'/home/claude/rig_starter_token.txt'),'utf8').trim();
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args:['--no-sandbox'] });
const ctx = await browser.newContext({ viewport:{width:412,height:915}, isMobile:true, hasTouch:true, deviceScaleFactor:2 });
await ctx.addCookies([{name:'ts_review', value: fs.readFileSync((process.env.RIG_REVIEW_TOKEN_FILE||'/home/claude/rig_review_token.txt'),'utf8').trim(), domain:'127.0.0.1', path:'/'},{name:'ts_user', value: proTok, domain:'127.0.0.1', path:'/'}]);
const fails=[]; function check(c,m){ if(!c) fails.push(m); }
async function api(p, tok, body){ const o = body ? {method:'POST', headers:{'Content-Type':'application/json', Cookie:'ts_user='+tok}, data: body} : {headers:{Cookie:'ts_user='+tok}}; const r=await ctx.request.fetch(B+p, o); return {status:r.status(), j: await r.json().catch(()=>null)}; }
function sql(q){ return execSync(`python3 -c "import sqlite3,json; c=sqlite3.connect('/var/www/marketsquare/marketsquare.db'); r=c.execute(\\"${q}\\").fetchall(); c.commit(); print(json.dumps(r))"`).toString().trim(); }
function arm(v){ sql(`UPDATE launch_switches SET baseline_q4=${v} WHERE id=1`); }
const intros0 = JSON.parse(sql("select count(*) from intro_requests"))[0][0];
const bal0 = JSON.parse(sql(`select coalesce(sum(amount),0) from transactions where user_email='${PRO}'`))[0][0];
// dark
arm(0); await new Promise(r=>setTimeout(r,700));
let r = await api('/squire/status?email='+PRO, proTok); check(r.status===404, 'dark: /squire/status answered '+r.status);
console.log('dark: /squire/status 404');
arm(1); await new Promise(r=>setTimeout(r,700));
// criterion 1: Pro-only
r = await api('/squire/brief', stTok, {email:STARTER, need_text:'maths tutor for a grade 9 learner in Menlo Park'}); check(r.status===403, 'Starter was allowed a brief: '+r.status);
r = await api('/squire/status?email='+STARTER, stTok); check(r.status===200 && r.j.pro===false && !r.j.allowance, 'Starter status leaked capability: '+JSON.stringify(r.j));
console.log('Starter: brief refused 403; status shows what Pro buys, no allowance');
// criterion 9: _buyer_tier consults the Pro subscription
r = await api('/wishlist/subscription/status?buyer_token=rigprotoken12345', proTok); check(r.j && r.j.tier==='global', '_buyer_tier did not resolve Pro to global: '+JSON.stringify(r.j));
console.log('Pro buyer_token → reach', r.j.tier);
// specify: words -> chips + brief + the two questions; minor minimised
r = await api('/squire/brief', proTok, {email:PRO, need_text:'Maths tutor for my 14-year-old son named Thabo at Menlo Park High School, failing trig, patient, in person, Menlo Park, weekday afternoons', category:'Tutors', city:'Pretoria'});
check(r.status===200 && r.j.brief_id, 'brief not created: '+r.status+' '+JSON.stringify(r.j));
const bid = r.j.brief_id;
console.log('brief:', r.j.category, 'chips', r.j.chips.map(c=>c.facet+'='+c.v), 'minor', r.j.is_minor, 'matches', r.j.matches, '\n  text:', r.j.brief_text.slice(0,160));
check(r.j.is_minor===true, 'a brief about a child was not flagged as a minor brief');
check(!/thabo/i.test(r.j.brief_text) && !/menlo park high/i.test(r.j.brief_text), 'the minor brief carries an identifying detail: '+r.j.brief_text);
check(r.j.questions.length===2, 'the two forgotten questions are missing');
check(r.j.chips.some(c=>c.facet==='subject'||c.facet==='mode'), 'the need did not become a Zoom path: '+JSON.stringify(r.j.chips));
// shortlist with reasons; seller identity never in the payload
r = await api('/squire/brief/'+bid+'/shortlist?email='+PRO, proTok);
check(r.status===200 && Array.isArray(r.j.shortlist), 'no shortlist');
const sl = r.j.shortlist; console.log('shortlist:', sl.length, sl[0] && sl[0].reasons);
check(sl.every(m => m.reasons.length>=2 && !('seller_email' in (m.listing||{})) && !JSON.stringify(m).match(/@trustsquare\.co/)), 'shortlist leaks seller identity or lacks reasons');
// rung 2: warn before composing (nothing charged, nothing written)
const before = JSON.parse(sql(`select count(*) from squire_approaches where email='${PRO}'`))[0][0];
r = await api('/squire/approach', proTok, {email:PRO, brief_id:bid, listing_id: sl[0].listing_id, draft_only:1});
check(r.j.status==='ok' && r.j.allowance.remaining===20, 'draft-only check wrong: '+JSON.stringify(r.j));
check(JSON.parse(sql(`select count(*) from squire_approaches where email='${PRO}'`))[0][0]===before, 'draft_only wrote an approach');
// send one approach -> metered
r = await api('/squire/approach', proTok, {email:PRO, brief_id:bid, listing_id: sl[0].listing_id, text:'Would Thursday 15:00 work?'});
check(r.j.status==='sent' && r.j.allowance.used===1, 'approach not metered: '+JSON.stringify(r.j));
console.log('approach sent; allowance', r.j.allowance.used+'/'+r.j.allowance.limit);
// the seller sees the NEED, answers, the buyer reads it
const sellerEmail = JSON.parse(sql(`select seller_email from listings where id=${sl[0].listing_id}`))[0][0];
const sellerTok = execSync('python3 /home/claude/rig_user_token.py '+sellerEmail+' 2>/dev/null').toString().trim();
let inbox = await api('/squire/inbox?email='+sellerEmail, sellerTok); check(inbox.j.approaches.length>=1 && !JSON.stringify(inbox.j).includes(PRO), 'seller inbox missing or leaks the buyer');
await api('/squire/approach/'+inbox.j.approaches[0].id+'/answer', sellerTok, {email:sellerEmail, answer:'Yes, Thursdays are open.'});
r = await api('/squire/brief/'+bid+'/shortlist?email='+PRO, proTok); check(r.j.shortlist[0].approach && r.j.shortlist[0].approach.answer==='Yes, Thursdays are open.', 'answer did not reach the buyer');
console.log('seller answered through Squire; buyer sees:', r.j.shortlist[0].approach.answer);
// criterion 3: no introduction was granted by any of this
check(JSON.parse(sql("select count(*) from intro_requests"))[0][0]===intros0, 'Squire created an intro_requests row');
// rungs 1+3: hit the cap -> the offer arrives with the limit, no charge, draft returned, telemetry
sql(`insert into squire_approaches (brief_id, listing_id, email, text, status, created_at) select ${bid}, ${sl[0].listing_id}, '${PRO}', 'filler', 'sent', strftime('%Y-%m-%dT%H:%M:%SZ','now') from (select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9 union all select 10 union all select 11 union all select 12 union all select 13 union all select 14 union all select 15 union all select 16 union all select 17 union all select 18 union all select 19)`);
r = await api('/squire/approach', proTok, {email:PRO, brief_id:bid, listing_id: sl[0].listing_id, text:'A drafted brief that must survive'});
console.log('at cap →', r.j.status, '|', r.j.message);
check(r.j.status==='ceiling' && /Another 5 for 1T\?/.test(r.j.message) && r.j.draft==='A drafted brief that must survive', 'ceiling did not arrive with the offer / lose the draft: '+JSON.stringify(r.j));
const balAfterCap = JSON.parse(sql(`select coalesce(sum(amount),0) from transactions where user_email='${PRO}'`))[0][0];
check(balAfterCap===bal0, 'a rejected attempt was charged: '+bal0+' -> '+balAfterCap);
const ev = JSON.parse(sql("select kind, tier, category, limit_n from squire_events where kind='ceiling_hit' order by id desc limit 1"));
check(ev.length===1 && ev[0][1]==='pro' && ev[0][2]==='Tutors' && ev[0][3]===20, 'ceiling telemetry missing limit/tier/category: '+JSON.stringify(ev));
console.log('ceiling event:', ev[0]);
// criterion 8: top-up in Tuppence, no second currency
r = await api('/squire/topup', proTok, {email:PRO});
check(r.status===200 && r.j.charged_tuppence===1 && r.j.allowance.limit===25 && r.j.allowance.remaining===5, 'top-up wrong: '+JSON.stringify(r.j));
const balAfterTopup = JSON.parse(sql(`select coalesce(sum(amount),0) from transactions where user_email='${PRO}'`))[0][0];
check(balAfterTopup===bal0-1, 'top-up did not debit exactly 1T: '+bal0+' -> '+balAfterTopup);
console.log('top-up: 1T debited, allowance now', r.j.allowance.limit);
const src = fs.readFileSync('/home/claude/rig/bea_main.py','utf8'); check(!/squire_token|squire_credit|SquireCoin/i.test(src), 'a second currency name appears in the code');
// the rendered card at phone width (Pro)
const page = await ctx.newPage(); const errs=[]; page.on('pageerror', e=>errs.push(String(e.message).slice(0,140)));
await page.goto(B+'/?baseline=1',{waitUntil:'domcontentloaded'});
await page.waitForFunction(() => typeof goTo==='function' && typeof msRenderSquireCard==='function', null, {timeout:30000});
await page.evaluate(e => { localStorage.setItem('ms_user_email', e); localStorage.setItem('ms_aa_email', e); goTo('myspace'); }, PRO);
await page.waitForFunction(() => document.querySelector('#ms-squire-card #sq-need'), null, {timeout:15000}).catch(()=>{});
let card = await page.evaluate(() => { const c=document.getElementById('ms-squire-card'); if(!c) return null; const r=c.getBoundingClientRect(); return {w:r.w||r.width, text:c.textContent.slice(0,120), briefs: c.querySelectorAll('.ms-cred-claim').length, btn: c.querySelector('#sq-brief-btn')?.getBoundingClientRect().height}; });
console.log('Squire card (Pro):', card);
check(card && card.w>0 && card.w<=412 && card.briefs>=1 && card.btn>=44, 'Squire card not rendered for the Pro user: '+JSON.stringify(card));
await page.evaluate(id => sqOpen(id), bid); await page.waitForFunction(() => document.querySelector('[id^=sq-sl-] .ms-cred-claim'), null, {timeout:15000}).catch(()=>{});
const slText = await page.evaluate(() => (document.querySelector('[id^=sq-sl-]')||{}).textContent||'');
check(/Shortlist, with reasons/.test(slText) && /trust \d+/.test(slText) && /Introduce me \(1T\)/.test(slText), 'rendered shortlist lacks reasons or the ordinary 1T intro path');
check(/5 of 25 approaches left/.test(card.text), 'rendered card does not show the topped-up allowance');
await page.screenshot({path:(process.env.SHOT_DIR||'/home/claude')+'/squire_phone.png'});
// Starter sees what Pro buys, no capability
await page.evaluate(e => { localStorage.setItem('ms_user_email', e); localStorage.setItem('ms_aa_email', e); }, STARTER);
await ctx.addCookies([{name:'ts_user', value: stTok, domain:'127.0.0.1', path:'/'}]);
await page.evaluate(() => { goTo('home'); goTo('myspace'); }); await page.waitForTimeout(1500);
const stCard = await page.evaluate(() => (document.getElementById('ms-squire-card')||{}).textContent||'');
const stHasBox = await page.evaluate(() => !!document.querySelector('#ms-squire-card #sq-need'));
check(/Pro plan/.test(stCard) && !stHasBox, 'Starter card leaks the Squire capability: '+stCard.slice(0,80));
console.log('Starter card:', stCard.slice(0,70)+'…');
arm(0);
const realErrs = errs.filter(e=>!/r2Fallback/.test(e)); check(realErrs.length===0, 'page errors: '+realErrs.join(' | '));
await browser.close();
if(fails.length){ console.log('\nFAIL'); fails.forEach(f=>console.log(' -',f)); process.exit(1); }
console.log('\nALL SQUIRE RENDERED CHECKS PASS (412x915)');
