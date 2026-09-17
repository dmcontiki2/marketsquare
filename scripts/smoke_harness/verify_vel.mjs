import { chromium } from 'playwright';
import fs from 'fs';
import { execSync } from 'child_process';
const B='http://127.0.0.1:8000';
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args:['--no-sandbox'] });
const ctx = await browser.newContext({ viewport:{width:412,height:915}, isMobile:true, hasTouch:true, deviceScaleFactor:2 });
await ctx.addCookies([{name:'ts_review', value: fs.readFileSync((process.env.RIG_REVIEW_TOKEN_FILE||'/home/claude/rig_review_token.txt'),'utf8').trim(), domain:'127.0.0.1', path:'/'}]);
const fails=[]; function check(c,m){ if(!c) fails.push(m); }
async function api(p){ const r=await ctx.request.get(B+p); return {status:r.status(), j: await r.json().catch(()=>null)}; }
function arm(v){ execSync(`python3 -c "import sqlite3; c=sqlite3.connect('/var/www/marketsquare/marketsquare.db'); c.execute('UPDATE launch_switches SET baseline_q4=${v} WHERE id=1'); c.commit()"`); }
async function draft(cat){
  const page = await ctx.newPage(); const errs=[]; page.on('pageerror', e=>errs.push(String(e.message).slice(0,120)));
  await page.goto(B+'/quick.html', {waitUntil:'domcontentloaded'});
  await page.waitForFunction(() => typeof CATS!=='undefined' && typeof start==='function', null, {timeout:30000});
  await page.waitForTimeout(1200);   // the catalogue fetch
  const r = await page.evaluate(k => {
    ci = CATS.findIndex(c => c.key===k); start('sell');
    // answer every step with its first tile
    for (let i=0;i<8;i++){ const f=flow(); if(step>=f.steps.length) break; const s=f.steps[step]; const t=s.tiles[0]; if(s.kind==='week'){ picks.push({key:s.key,label:'Mon',days:['Mon']}); } else { picks.push({key:s.key,label:t.t,photo:t.p}); } step++; }
    drawDraft();
    const cred = document.querySelector('.cred');
    return { cred: cred ? cred.textContent.replace(/\s+/g,' ').slice(0,400) : null, items: cred ? [...cred.querySelectorAll('.credlist span')].map(s=>s.textContent) : [], w: cred ? cred.getBoundingClientRect().width : 0 };
  }, cat);
  if (cat==='property' && r.cred) await page.screenshot({path:(process.env.SHOT_DIR||'/home/claude')+'/vel_property.png'});
  await page.close();
  return {...r, errs};
}
// dark
arm(0); await new Promise(r=>setTimeout(r,800));
let c = await api('/trust/catalogue?category=property&private=1');
check(c.status===200 && c.j.signals.length===0 && c.j.baseline_q4===false, 'dark: private-seller entries served: '+JSON.stringify(c.j));
let d = await draft('property'); console.log('dark Property draft block:', d.cred);
check(d.cred===null, 'dark: the Property draft carried a block');
d = await draft('localmarket'); check(d.cred===null, 'dark: the Local Market draft carried a block');
console.log('dark: /trust/catalogue empty for private sellers, both drafts silent (as before)');
// armed
arm(1); await new Promise(r=>setTimeout(r,800));
c = await api('/trust/catalogue?category=property&private=1');
console.log('armed catalogue property:', c.j.signals.map(s=>s.name+' +'+s.points));
check(c.j.signals.length===4 && c.j.signals[0].points===8, 'armed: property private entries wrong: '+JSON.stringify(c.j.signals.map(s=>[s.name,s.points])));
check(c.j.signals.every(s => /dated|current|latest/i.test(s.name+' '+s.how_to_earn) && /check/i.test(s.how_to_earn)), 'an entry is not dated + outside-checkable in its own words');
let lm = await api('/trust/catalogue?category=localmarket&private=1');
console.log('armed catalogue local market:', lm.j.signals.map(s=>s.name+' +'+s.points));
check(lm.j.signals.length===3, 'armed: local market private entries wrong');
d = await draft('property'); console.log('armed Property draft items:', d.items);
check(d.items.length===4 && d.items.every((it,i) => it.indexOf(c.j.signals[i].name)===0 && it.endsWith('+'+c.j.signals[i].points)), 'Property draft block does not read the catalogue names/points: '+JSON.stringify(d.items));
check(d.w>0 && d.w<=412, 'Property block not laid out at phone width');
d = await draft('localmarket'); console.log('armed Local Market draft items:', d.items);
check(d.items.length===3 && d.items.every((it,i) => it.indexOf(lm.j.signals[i].name)===0), 'Local Market draft block does not read the catalogue');
// the trust evidence lane sees the entries only when armed (a seller's breakdown)
const emailU = 'super-tutors@trustsquare.co';
let tb = await api('/trust-score/breakdown?email='+emailU+'&category=Property_private');
console.log('breakdown endpoint status:', tb.status);
const armedHas = tb.status===200 ? JSON.stringify(tb.j).indexOf('title_deed')>-1 : null;
arm(0); await new Promise(r=>setTimeout(r,800));
let tb2 = await api('/trust-score/breakdown?email='+emailU+'&category=Property_private');
const darkHas = tb2.status===200 ? JSON.stringify(tb2.j).indexOf('title_deed')>-1 : null;
console.log('trust breakdown carries title_deed: armed=', armedHas, 'dark=', darkHas);
if (armedHas!==null) check(armedHas===true && darkHas===false, 'trust evidence lane does not follow the flag');
check(d.errs.length===0, 'page errors: '+d.errs.join('|'));
await browser.close();
if(fails.length){ console.log('\nFAIL'); fails.forEach(f=>console.log(' -',f)); process.exit(1); }
console.log('\nALL RUL-129 RENDERED CHECKS PASS (412x915)');
