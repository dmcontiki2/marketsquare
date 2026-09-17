import { chromium } from 'playwright';
import fs from 'fs';
import { execSync } from 'child_process';
const B='http://127.0.0.1:8000';
const ADM=fs.readFileSync((process.env.RIG_ADMIN_TOKEN_FILE||'/home/claude/rig_admin_token.txt'),'utf8').trim();
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args:['--no-sandbox'] });
const ctx = await browser.newContext({ viewport:{width:412,height:915}, isMobile:true, hasTouch:true, deviceScaleFactor:2 });
await ctx.addCookies([{name:'ts_review', value: fs.readFileSync((process.env.RIG_REVIEW_TOKEN_FILE||'/home/claude/rig_review_token.txt'),'utf8').trim(), domain:'127.0.0.1', path:'/'}]);
const fails=[]; function check(c,m){ if(!c) fails.push(m); }
function sql(q){ return JSON.parse(execSync(`python3 -c "import sqlite3,json; c=sqlite3.connect('/var/www/marketsquare/marketsquare.db'); r=c.execute(\\"${q}\\").fetchall(); c.commit(); print(json.dumps(r))"`).toString().trim()); }
async function api(p, opts){ const r=await ctx.request.fetch(B+p, opts||{}); return {status:r.status(), j: await r.json().catch(()=>null)}; }
// a LIVE Global subscriber on the free seller tier (the case RUL-128 protects), unexpired, Paystack ref on the row
sql("UPDATE launch_switches SET baseline_q4=0 WHERE id=1");
sql("delete from wishlist_subscriptions"); sql("delete from admin_audit where action='RUL-128 fold'"); sql("update users set seller_tier='free', slot_limit=2, buyer_token='rigglobaltoken123' where email='tutors-nairobi-c@trustsquare.co'");
sql("insert into wishlist_subscriptions (buyer_token, tier, activated_at, expires_at, paystack_ref) values ('rigglobaltoken123','global','2026-09-01T00:00:00+00:00','2026-10-01T00:00:00+00:00','ms_wishlist_rigref01')");
const wl0 = sql("select buyer_token, tier, expires_at, paystack_ref from wishlist_subscriptions");
// dark: two $5 products, the buyer checkout still opens (Paystack refuses on the rig, but the lane is not 410)
let r = await api('/pricing/ladder'); check(r.j.armed===false && r.j.buyer_subscription && r.j.buyer_subscription.usd===5 && !r.j.ladder[1].features.some(f=>/reach/i.test(f)), 'dark ladder wrong: '+JSON.stringify(r.j).slice(0,200));
r = await api('/wishlist/subscription/initialize?buyer_token=rigglobaltoken123&email=tutors-nairobi-c@trustsquare.co', {method:'POST'}); check(r.status!==410, 'dark: buyer checkout already retired ('+r.status+')');
r = await api('/wishlist/subscription/status?buyer_token=rigglobaltoken123'); check(r.j.tier==='global', 'the Global subscriber does not read global before arming');
console.log('dark: two $5 products, buyer checkout open, Global subscriber reads global');
// ARM -- David's act via POST /admin/flags -- the fold runs once
r = await api('/admin/flags', {method:'POST', headers:{'X-Admin-Token':ADM,'Content-Type':'application/json'}, data:{baseline_q4:true, reason:'rig proof of RUL-128'}});
check(r.status===200 && r.j.baseline_q4===true, 'arming failed: '+r.status+' '+JSON.stringify(r.j).slice(0,120));
const u = sql("select seller_tier, slot_limit, billing_period_end from users where email='tutors-nairobi-c@trustsquare.co'")[0];
console.log('after arming, the Global subscriber →', u);
check(u[0]==='starter' && u[1]===10 && u[2]==='2026-10-01T00:00:00+00:00', 'the Global subscriber was not folded into Starter at the same price: '+JSON.stringify(u));
const wl1 = sql("select buyer_token, tier, expires_at, paystack_ref from wishlist_subscriptions");
check(JSON.stringify(wl1)===JSON.stringify(wl0), 'the LIVE Paystack-backed row was touched: '+JSON.stringify(wl1));
const audit = sql("select action, field, prior, new from admin_audit where action='RUL-128 fold'");
check(audit.length===1 && audit[0][2]==='free' && audit[0][3]==='starter', 'no audit row for the fold: '+JSON.stringify(audit));
r = await api('/wishlist/subscription/status?buyer_token=rigglobaltoken123'); check(r.j.tier==='global', 'the folded subscriber lost reach');
// the separate buyer product is retired; the ladder has one $5 rung with reach; Pro carries Squire
r = await api('/wishlist/subscription/initialize?buyer_token=someoneelse123&email=x@y.z', {method:'POST'}); check(r.status===410 && /Starter/.test(r.j.detail), 'buyer checkout not retired after arming: '+r.status);
r = await api('/pricing/ladder'); console.log('armed ladder:', r.j.ladder.map(t=>t.label+' $'+t.usd+' · '+t.reach));
check(r.j.armed && r.j.buyer_subscription===null && r.j.ladder[1].reach==='global' && r.j.ladder[1].usd===5 && r.j.ladder[2].features.some(f=>/Squire/.test(f)), 'armed ladder wrong: '+JSON.stringify(r.j).slice(0,300));
// re-arm moves nobody twice; a Starter/Pro account is left alone
r = await api('/admin/flags', {method:'POST', headers:{'X-Admin-Token':ADM,'Content-Type':'application/json'}, data:{baseline_q4:false}});
r = await api('/admin/flags', {method:'POST', headers:{'X-Admin-Token':ADM,'Content-Type':'application/json'}, data:{baseline_q4:true}});
check(sql("select count(*) from admin_audit where action='RUL-128 fold'")[0][0]===1, 'the fold moved somebody twice');
// a Starter seller now reads global reach (RUL-128) -- through both resolvers
sql("update users set seller_tier='starter', buyer_token='rigstartertoken1' where email='tutors-nairobi-b@trustsquare.co'");
r = await api('/wishlist/subscription/status?buyer_token=rigstartertoken1'); check(r.j.tier==='global', 'a Starter seller does not read global once armed: '+JSON.stringify(r.j));
const z = await api('/zoom/next?category=Property&city=Pretoria&rows=0&email=tutors-nairobi-b@trustsquare.co'); check(z.j.tier==='global', 'Zoom does not give a Starter global reach once armed');
console.log('Starter → reach', r.j.tier, '| zoom tier', z.j.tier);
// the pricing page, rendered (armed)
const page = await ctx.newPage(); const errs=[]; page.on('pageerror', e=>errs.push(String(e.message).slice(0,140)));
await page.goto(B+'/?baseline=1',{waitUntil:'domcontentloaded'});
await page.waitForFunction(() => typeof goTo==='function' && typeof msRenderLadder==='function', null, {timeout:30000});
await page.evaluate(() => goTo('plans')); await page.waitForFunction(() => document.getElementById('plans-one-ladder-note'), null, {timeout:15000});
const cards = await page.evaluate(() => ['free','starter','pro'].map(id => { const c=document.getElementById('plan-card-'+id); return {id, price: c.querySelector('.plan-price').textContent, feats: [...c.querySelectorAll('.plan-feat')].map(f=>f.textContent.trim()), w: c.getBoundingClientRect().width}; }));
console.log('rendered ladder:', cards.map(c=>c.id+' '+c.price+' → '+c.feats.join(' | ')).join('\n  '));
check(cards[1].feats.some(f=>/Global buyer reach/.test(f)) && cards[2].feats.some(f=>/Squire/.test(f)) && !cards[0].feats.some(f=>/Global/.test(f)), 'the rendered ladder is not the one-ladder shape');
check(cards.every(c=>c.w<=412), 'plan cards overflow');
await page.screenshot({path:(process.env.SHOT_DIR||'/home/claude')+'/fold_plans.png', fullPage:false});
// the Watch screen no longer sells the separate buyer product
await page.evaluate(() => goTo('wishlist')); await page.waitForTimeout(1500);
const wlBtn = await page.evaluate(() => (document.getElementById('wl-upgrade-btn')||{}).textContent||'');
console.log('watch screen button:', wlBtn);
check(/Starter/.test(wlBtn), 'the Watch screen still sells Global as a separate product: '+wlBtn);
// dark again: the page is the page as it was
sql("UPDATE launch_switches SET baseline_q4=0 WHERE id=1");
await page.goto(B+'/?baseline=0',{waitUntil:'domcontentloaded'}); await page.waitForFunction(() => typeof goTo==='function', null, {timeout:30000});
await page.evaluate(() => goTo('plans')); await page.waitForTimeout(800);
const darkFeats = await page.evaluate(() => [...document.querySelectorAll('#plan-card-starter .plan-feat')].map(f=>f.textContent.trim()));
check(!darkFeats.some(f=>/Global/.test(f)), 'dark: the pricing page changed'); 
console.log('dark pricing page starter feats:', darkFeats);
const realErrs = errs.filter(e=>!/r2Fallback/.test(e)); check(realErrs.length===0, 'page errors: '+realErrs.join(' | '));
await browser.close();
if(fails.length){ console.log('\nFAIL'); fails.forEach(f=>console.log(' -',f)); process.exit(1); }
console.log('\nALL RUL-128 FOLD CHECKS PASS (412x915)');
