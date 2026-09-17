import { chromium } from 'playwright';
import fs from 'fs';
const B='http://127.0.0.1:8000';
const EMAIL='super-tutors@trustsquare.co';
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args:['--no-sandbox'] });
const ctx = await browser.newContext({ viewport:{width:412,height:915}, isMobile:true, hasTouch:true, deviceScaleFactor:2 });
await ctx.addCookies([{name:'ts_review', value: fs.readFileSync((process.env.RIG_REVIEW_TOKEN_FILE||'/home/claude/rig_review_token.txt'),'utf8').trim(), domain:'127.0.0.1', path:'/'},
                      {name:'ts_user', value: fs.readFileSync((process.env.RIG_USER_TOKEN_FILE||'/home/claude/rig_user_token.txt'),'utf8').trim(), domain:'127.0.0.1', path:'/'}]);
const page = await ctx.newPage();
const fails=[]; const errs=[]; page.on('pageerror', e => errs.push(String(e.message).slice(0,160)));
function check(c,m){ if(!c) fails.push(m); }
async function api(path, opts){ const r = await ctx.request.fetch(B+path, opts); let j=null; try{ j=await r.json(); }catch(e){} return {status:r.status(), j}; }

// ── flag OFF: the lane is dark (404) and no badge is served ───────────────────
let r = await api('/credentials/mine?email='+EMAIL);
check(r.status===404, 'flag OFF: /credentials/mine answered '+r.status);
let ls = await api('/listings?city=Pretoria&category=Tutors');
check(!ls.j.some(l => l.credential_badges), 'flag OFF: a badge was served');
console.log('flag OFF: /credentials/mine 404, no badges on /listings');

// ── arm the flag on the rig only (David's act on live: POST /admin/flags) ──────
// the rig DB is a copy; here we flip it directly to prove the lit lane
const sqlite = (await import('child_process')).execSync;
sqlite(`python3 -c "import sqlite3; c=sqlite3.connect('/var/www/marketsquare/marketsquare.db'); c.execute('UPDATE launch_switches SET baseline_q4=1 WHERE id=1'); c.commit()"`);
r = await api('/flags'); check(r.j.baseline_q4===true && r.j.effective.baseline_q4===true, 'flags did not report baseline_q4 armed: '+JSON.stringify(r.j.baseline_q4));
r = await api('/credentials/mine?email='+EMAIL, {headers:{Cookie:'ts_user='+fs.readFileSync((process.env.RIG_USER_TOKEN_FILE||'/home/claude/rig_user_token.txt'),'utf8').trim()}});
check(r.status===200 && r.j.registry && r.j.registry.FIDE===4237, '/credentials/mine after arming: '+r.status+' '+JSON.stringify(r.j&&r.j.registry));
console.log('armed: /credentials/mine →', r.status, 'registry', r.j.registry);

// ── the claim moment on My Space (rendered) ───────────────────────────────────
await page.goto(B+'/?baseline=1',{waitUntil:'domcontentloaded'});
await page.waitForFunction(() => typeof goTo==='function' && typeof msRenderCredentialCard==='function', null, {timeout:30000});
await page.evaluate(e => { localStorage.setItem('ms_user_email', e); localStorage.setItem('ms_aa_email', e); goTo('myspace'); msTab('trust', document.querySelectorAll('.ms-tab')[2]); }, EMAIL);
await page.waitForFunction(() => document.getElementById('ms-cred-card') && document.getElementById('ms-cred-card').style.display!=='none', null, {timeout:15000}).catch(()=>{});
let card = await page.evaluate(() => { const c=document.getElementById('ms-cred-card'); if(!c) return null; const r=c.getBoundingClientRect(); return {shown:c.style.display!=='none', w:r.width, btn: c.querySelector('#ms-cred-btn')?.getBoundingClientRect().height}; });
console.log('My Space credential card:', card);
check(card && card.shown && card.btn>=44, 'credential card not rendered on My Space: '+JSON.stringify(card));
// 1. wrong ID -> honest decline (registry we hold, re-check)
await page.fill('#ms-cred-id', '999999999'); await page.fill('#ms-cred-name', 'Nobody Here'); await page.click('#ms-cred-btn');
await page.waitForFunction(() => /registry/.test(document.getElementById('ms-cred-out').textContent), null, {timeout:15000});
let out = await page.$eval('#ms-cred-out', e => e.textContent); console.log('unknown ID →', out.slice(0,90));
check(/not in the FIDE registry/.test(out) && /4,237/.test(out), 'unknown ID did not get the honest decline');
// 2. right ID, wrong name -> name mismatch
await page.fill('#ms-cred-id', '1130420'); await page.fill('#ms-cred-name', 'Someone Else Entirely'); await page.click('#ms-cred-btn');
await page.waitForFunction(() => /name/.test(document.getElementById('ms-cred-out').textContent), null, {timeout:15000});
out = await page.$eval('#ms-cred-out', e => e.textContent); console.log('wrong name →', out.slice(0,80));
check(/does not match/.test(out), 'wrong name was not refused');
// 3. right ID + registry name -> Tier B (no id-verify yet)
await page.fill('#ms-cred-name', 'Kacper Piorun'); await page.click('#ms-cred-btn');
await page.waitForFunction(() => /Claimed/.test(document.getElementById('ms-cred-out').textContent), null, {timeout:15000});
out = await page.$eval('#ms-cred-out', e => e.textContent); console.log('registry name →', out.slice(0,80));
r = await api('/credentials/mine?email='+EMAIL, {headers:{Cookie:'ts_user='+fs.readFileSync((process.env.RIG_USER_TOKEN_FILE||'/home/claude/rig_user_token.txt'),'utf8').trim()}});
check(r.j.claims.length===1 && r.j.claims[0].tier==='B' && r.j.claims[0].status==='active', 'Tier B claim not recorded: '+JSON.stringify(r.j.claims));
console.log('claims:', r.j.claims.map(c=>c.tier+'/'+c.status+'/'+c.badge));
// 4. the badge on the rendered Tutors cards, from the live JOIN -- and NOTHING identifying in the payload
ls = await api('/listings?city=Pretoria&category=Tutors');
const mine = ls.j.filter(l => l.credential_badges);
check(mine.length>=1, 'no listing carries the badge after the claim');
check(mine.every(l => !('seller_email' in l) && JSON.stringify(l.credential_badges).indexOf('1130420')<0 && !/piorun/i.test(JSON.stringify(l.credential_badges)) && !/federation/i.test(JSON.stringify(l.credential_badges))), 'the public payload leaks identity');
console.log('badged listings:', mine.length, mine[0].credential_badges);
await page.evaluate(async () => { await loadLiveListings(0); filterBrowse('Tutors'); }); await page.waitForTimeout(1500);
let badges = await page.$$eval('#listing-grid .cred-badge', els => els.map(e=>e.textContent));
console.log('rendered card badges:', badges.slice(0,3));
check(badges.length>=1 && badges.every(b => /FIDE-listed trainer/.test(b)), 'Tier B badge not rendered on cards: '+JSON.stringify(badges));
await page.screenshot({path:(process.env.SHOT_DIR||'/home/claude')+'/cred_cards_tierB.png'});
// 5. one account per credential: a second account claiming the same ID is refused
const other = 'tutors-nairobi-a@trustsquare.co';
const otherTok = (await import('child_process')).execSync('python3 /home/claude/rig_user_token.py '+other+' 2>/dev/null').toString().trim();
r = await api('/credentials/claim', {method:'POST', headers:{'Content-Type':'application/json', Cookie:'ts_user='+otherTok}, data:{email:other, source:'FIDE', credential_id:'1130420', claimed_name:'Kacper Piorun'}});
console.log('second account →', r.status, r.j && r.j.status);
check(r.j && r.j.status==='taken', 'a second account was allowed onto a claimed credential');
// 6. identity anchor: id-verify the account with the registry name -> Tier A, badge upgrades, trust signal earned
sqlite(`python3 -c "import sqlite3; c=sqlite3.connect('/var/www/marketsquare/marketsquare.db'); c.execute(\\"UPDATE users SET id_verified=1, id_name='Kacper Piorun' WHERE LOWER(email)='${EMAIL}'\\"); c.commit()"`);
await page.evaluate(() => { goTo('myspace'); msTab('trust', document.querySelectorAll('.ms-tab')[2]); }); await page.waitForTimeout(800);
await page.fill('#ms-cred-id', '1130420'); await page.fill('#ms-cred-name', 'Kacper Piorun'); await page.click('#ms-cred-btn');
await page.waitForFunction(() => /Claimed/.test(document.getElementById('ms-cred-out').textContent), null, {timeout:15000});
r = await api('/credentials/mine?email='+EMAIL, {headers:{Cookie:'ts_user='+fs.readFileSync((process.env.RIG_USER_TOKEN_FILE||'/home/claude/rig_user_token.txt'),'utf8').trim()}});
check(r.j.claims[0].tier==='A' && /Verified FIDE Trainer \(FT\)/.test(r.j.claims[0].badge||''), 'Tier A not reached after id-verify: '+JSON.stringify(r.j.claims));
console.log('after id-verify:', r.j.claims.map(c=>c.tier+'/'+c.status+'/'+c.badge));
const sig = (await import('child_process')).execSync(`python3 -c "import sqlite3; c=sqlite3.connect('/var/www/marketsquare/marketsquare.db'); print(c.execute(\\"select signal_id, status from user_credentials where email='${EMAIL}' and signal_id like 'category.tutors.fide_%'\\").fetchall())"`).toString().trim();
console.log('trust signals earned:', sig);
check(/fide_ft', 'earned'/.test(sig), 'Tier A did not earn the title signal via the VEL lane');
// trust breakdown reads it through the ordinary lane (points from the catalogue)
r = await api('/users/'+EMAIL+'/trust?category=Tutors'); if(r.status!==200) r = await api('/trust/'+EMAIL+'?category=Tutors');
await page.evaluate(async () => { await loadLiveListings(0); filterBrowse('Tutors'); }); await page.waitForTimeout(1500);
badges = await page.$$eval('#listing-grid .cred-badge', els => els.map(e=>e.textContent));
console.log('rendered card badges (A):', badges.slice(0,2));
check(badges.some(b => /Verified FIDE Trainer \(FT\)/.test(b)), 'Tier A badge not rendered on cards');
// 7. no surface calls a person safe (RG-0238): the badge copy is about the credential
const toastCopy = await page.evaluate(() => document.querySelector('#listing-grid .cred-badge')?.getAttribute('onclick')||'');
check(/never that a person is safe/.test(toastCopy), 'badge copy does not carry the RG-0238 line');
await page.screenshot({path:(process.env.SHOT_DIR||'/home/claude')+'/cred_cards_tierA.png'});
// ── disarm: dark again, badge gone ────────────────────────────────────────────
sqlite(`python3 -c "import sqlite3; c=sqlite3.connect('/var/www/marketsquare/marketsquare.db'); c.execute('UPDATE launch_switches SET baseline_q4=0 WHERE id=1'); c.commit()"`);
await new Promise(r=>setTimeout(r,1200));
r = await api('/credentials/mine?email='+EMAIL); check(r.status===404, 'after disarm /credentials/mine still answers '+r.status);
ls = await api('/listings?city=Pretoria&category=Tutors'); check(!ls.j.some(l => l.credential_badges), 'after disarm a badge is still served');
console.log('disarmed: lane dark again, badge gone from /listings');
const realErrs = errs.filter(e=>!/r2Fallback/.test(e)); check(realErrs.length===0, 'page errors: '+realErrs.join(' | '));
await browser.close();
if(fails.length){ console.log('\nFAIL'); fails.forEach(f=>console.log(' -',f)); process.exit(1); }
console.log('\nALL CREDENTIAL-CLAIM RENDERED CHECKS PASS (412x915)');
