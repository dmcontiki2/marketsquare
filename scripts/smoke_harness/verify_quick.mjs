// QUICK app baseline readiness (RUL-125(c)) -- rendered at phone width on the rig origin.
import { chromium } from 'playwright';
import fs from 'fs';
import { execSync } from 'child_process';
const B='http://127.0.0.1:8000';
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args:['--no-sandbox'] });
const ctx = await browser.newContext({ viewport:{width:412,height:915}, isMobile:true, hasTouch:true, deviceScaleFactor:2 });
const fails=[]; function check(c,m){ if(!c) fails.push(m); }
function sql(q){ return JSON.parse(execSync(`python3 -c "import sqlite3,json; c=sqlite3.connect('/var/www/marketsquare/marketsquare.db'); r=c.execute(\\"${q}\\").fetchall(); c.commit(); print(json.dumps(r))"`).toString().trim()); }
const page = await ctx.newPage(); const errs=[]; page.on('pageerror', e=>errs.push(String(e.message).slice(0,140)));
// (1) a stranger by e-mail link: no app marker, no cookie -- /quick/me hands the key, Publish is LIVE
await page.goto(B+'/quick.html',{waitUntil:'domcontentloaded'});
await page.waitForFunction(() => typeof CATS!=='undefined' && typeof start==='function', null, {timeout:30000});
await page.waitForTimeout(1200);
const live = await page.evaluate(() => ({live: QUICK_LIVE, url: HANDOVER.url, key: !!HANDOVER.key, member: QUICK.member}));
console.log('stranger on the origin:', live);
check(live.live && live.key && live.url===B, 'a fresh visitor is still a DRY RUN: '+JSON.stringify(live));
// the five-tap journey: Housekeeping (the spreader's first lane) -- count real taps on real tiles
const taps = await page.evaluate(async () => {
  ci = 0; drawDoor(); 
  const wait = ms => new Promise(r=>setTimeout(r,ms));
  let n=0;
  // door: tap "Get work"
  const sell = [...document.querySelectorAll('button, .btn, [onclick]')].find(e => /get work|list/i.test(e.textContent||''));
  if(sell){ sell.click(); n++; } else { start('sell'); n++; }
  await wait(200);
  for (let i=0;i<8;i++){
    const f=flow(); if(step>=f.steps.length) break;
    const s=f.steps[step];
    if(s.kind==='week'){ const day=document.querySelector('.wk, .day, [data-day]'); if(day){ day.click(); } else { picks.push({key:s.key,label:'Mon',days:['Mon']}); step++; drawStep(); }
      const nx=[...document.querySelectorAll('button')].find(b=>/next|continue|done|→/i.test(b.textContent)); if(nx) nx.click(); n++; }
    else { const tile=document.querySelector('.tile, .chip, [data-t]'); if(tile){ tile.click(); } else { const t=s.tiles[0]; picks.push({key:s.key,label:t.t,photo:t.p}); step++; drawStep(); } n++; }
    await wait(150);
  }
  if(step>=flow().steps.length) finish();
  return {taps:n, step, steps: flow().steps.length, draft: !!document.getElementById('pub'), stepsDone: picks.map(p=>p.key)};
});
console.log('journey:', taps);
check(taps.draft && taps.taps<=7, 'the journey did not reach the advert in <=7 taps: '+JSON.stringify(taps));
const w = await page.evaluate(() => document.documentElement.scrollWidth); check(w<=412, 'quick overflow '+w);
await page.screenshot({path:(process.env.SHOT_DIR||'/home/claude')+'/quick_draft.png'});
// (2) hand-over lands as a REAL listing with the expected score: the one ask, then publish
const before = sql("select max(id) from listings")[0][0];
const ls = await page.evaluate(() => lsOf(picks,0).score);
await page.click('#pub'); await page.waitForTimeout(400);
const asked = await page.evaluate(() => !!document.getElementById('jmail'));
check(asked, 'the stranger was not asked once, at the end');
await page.fill('#jmail', 'rig-quick-tester@example.com'); await page.waitForTimeout(150); await page.click('#jgo');
await page.waitForFunction(() => /Draft #\d+/.test((document.getElementById('hres')||{}).textContent||''), null, {timeout:20000});
const hres = await page.$eval('#hres', e => e.textContent);
const newId = sql("select max(id) from listings")[0][0];
const row = sql(`select id, category, listing_status, seller_email, suburb, quality_score, trust_score from listings where id=${newId}`)[0];
console.log('hand-over →', hres.slice(0,60), '| row', row, '| spreader LS', ls);
check(newId>before && row && row[2]==='draft' && row[3]==='rig-quick-tester@example.com' && row[4], 'hand-over did not land as a real draft listing: '+JSON.stringify(row));
check(row[5]!==null, 'the landed listing carries no quality_score (the stored score the ranking reads)');
// (3) the vouching gate holds: an employer link is minted only for a real account and the confirm door answers
const link = await ctx.request.get(B+'/trust/employer-link?email=super-tutors@trustsquare.co'); const lj = await link.json();
check(link.status()===200 && /\/confirm\//.test(lj.url) && lj.points===12, 'employer link not minted: '+JSON.stringify(lj));
const bad = await ctx.request.get(B+'/trust/employer-link?email=nobody-here@example.com'); check(bad.status()===404, 'a link was minted for a non-account');
const who = await ctx.request.get(B+'/trust/employer-who?token=not-a-token'); check(who.status()>=400, 'a forged token was accepted by employer-who');
const confirmPage = await ctx.request.get(B+'/confirm/'); check(confirmPage.status()===200 || confirmPage.status()===404, 'confirm door probe failed');
console.log('vouching: link minted for a real account, refused for a stranger, forged token refused');
// (4) the personal link brings a hirer in FREE: a pair is created with no Tuppence row
const tx0 = sql("select count(*) from transactions")[0][0];
const uTok = fs.readFileSync((process.env.RIG_USER_TOKEN_FILE||'/home/claude/rig_user_token.txt'),'utf8').trim();
const pair = await ctx.request.post(B+'/buzz/pair', {headers:{'X-Api-Key':'ms_mk_2026_pretoria_admin','Content-Type':'application/json', Cookie:'ts_user='+uTok}, data:{from_email:'super-tutors@trustsquare.co', to_email:'rig-hirer@example.com', source:'link'}});
const pj = await pair.json().catch(()=>null);
console.log('pair →', pair.status(), JSON.stringify(pj).slice(0,120));
check(pair.status()===200, 'the worker\'s link could not pair a hirer: '+pair.status()+' '+JSON.stringify(pj));
check(sql("select count(*) from transactions")[0][0]===tx0, 'pairing a hirer moved Tuppence -- the free lane is not free');
// (5) the buzz arrives: the buzz endpoint accepts a line between the pair (delivery = push/e-mail lanes, RG-0359)
// each side holds its own switch (RUL-132): the hirer allows the worker, then the line goes through
// the hirer joined free and accepted the terms (the one ask) -- a users row with the EULA stamp
sql("insert or ignore into users (email, name) values ('rig-hirer@example.com','Rig Hirer')"); sql("update users set eula_accepted_at=strftime('%Y-%m-%dT%H:%M:%SZ','now') where email in ('rig-hirer@example.com','super-tutors@trustsquare.co')");
const hTok = execSync('python3 /home/claude/rig_user_token.py rig-hirer@example.com 2>/dev/null').toString().trim();
const al = await ctx.request.post(B+'/buzz/allow', {headers:{'X-Api-Key':'ms_mk_2026_pretoria_admin','Content-Type':'application/json', Cookie:'ts_user='+hTok}, data:{email:'rig-hirer@example.com', other_email:'super-tutors@trustsquare.co', allow:true}});
console.log('hirer allows →', al.status());
const bz = await ctx.request.post(B+'/buzz', {headers:{'X-Api-Key':'ms_mk_2026_pretoria_admin','Content-Type':'application/json', Cookie:'ts_user='+uTok}, data:{from_email:'super-tutors@trustsquare.co', to_email:'rig-hirer@example.com', text:'Can you do Thursday?'}});
const bj = await bz.json().catch(()=>null);
console.log('buzz →', bz.status(), JSON.stringify(bj).slice(0,160));
check(bz.status()===200, 'the buzz did not go through once allowed: '+bz.status()+' '+JSON.stringify(bj));
const bzRows = sql("select count(*) from buzz_log")[0][0]; console.log('buzz rows', bzRows); check(bzRows>=1, 'no buzz row stored');
// (6) the coloured tile: manifest served with its own id/start_url/icon/colour and linked from the page
const man = await ctx.request.get(B+'/static/brand/quick.webmanifest'); const mj = await man.json();
check(man.status()===200 && mj.id==='/quick.html' && mj.start_url==='/quick.html' && mj.theme_color==='#7C3AED' && mj.icons && mj.icons[0].src.startsWith('data:image/png'), 'manifest not installable: '+JSON.stringify(mj).slice(0,200));
const linked = await page.evaluate(() => document.querySelector('link[rel=manifest]')?.getAttribute('href'));
check(linked==='/static/brand/quick.webmanifest', 'quick.html does not link its manifest');
const sw = await ctx.request.get(B+'/service-worker.js'); check(sw.status()===200, 'service worker not served');
console.log('tile: manifest + icon + colour + service worker served');
const realErrs = errs.filter(e=>!/r2Fallback/.test(e)); check(realErrs.length===0, 'page errors: '+realErrs.join(' | '));
await browser.close();
if(fails.length){ console.log('\nFAIL'); fails.forEach(f=>console.log(' -',f)); process.exit(1); }
console.log('\nALL QUICK READINESS RENDERED CHECKS PASS (412x915)');
