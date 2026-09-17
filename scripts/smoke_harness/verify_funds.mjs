import { chromium } from 'playwright';
import fs from 'fs';
const B='http://127.0.0.1:8000';
const ADM=fs.readFileSync((process.env.RIG_ADMIN_TOKEN_FILE||'/home/claude/rig_admin_token.txt'),'utf8').trim();
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args:['--no-sandbox'] });
const ctx = await browser.newContext({ viewport:{width:412,height:915}, isMobile:true, hasTouch:true, deviceScaleFactor:2 });
const fails=[]; function check(c,m){ if(!c) fails.push(m); }
await ctx.request.post(B+'/admin/ai-funds', {headers:{'X-Admin-Token':ADM,'Content-Type':'application/json'}, data:{lane:'openai', clear:true, auto_topup:'unknown'}});   // start from NOT MEASURED
const page = await ctx.newPage(); const errs=[]; page.on('pageerror', e=>errs.push(String(e.message).slice(0,140)));
await page.goto(B+'/dashboard.html',{waitUntil:'domcontentloaded'});
await page.waitForFunction(() => document.querySelector('#apv3-funds') && !/Loading/.test(document.querySelector('#apv3-funds').textContent), null, {timeout:30000});
let strip = await page.evaluate(() => { const el=document.querySelector('[data-ai-funds]'); const r=el.getBoundingClientRect(); return {rows: el.querySelectorAll('div[style*="border-top"]').length, text: el.textContent.replace(/\s+/g,' ').slice(0,600), w:r.width, nm: (el.textContent.match(/NOT MEASURED/g)||[]).length}; });
console.log('strip:', strip.rows, 'rows |', strip.text.slice(0,300));
check(strip.rows===4, 'the gauge does not carry one row per app AI function: '+strip.rows);
check(strip.nm>=4, 'unprobeable balances are not marked NOT MEASURED');
check(/lane openai/.test(strip.text) && /today \$/.test(strip.text) && /ceiling left/.test(strip.text), 'the row lacks lane / measured spend / ceiling');
check(/auto-top-up state unknown|auto-top-up/.test(strip.text), 'no auto-top-up state on the row');
check(strip.w<=412, 'strip overflows phone width');
const sw = await page.evaluate(() => document.documentElement.scrollWidth); check(sw<=412+2, 'dashboard horizontal overflow '+sw);
await page.screenshot({path:(process.env.SHOT_DIR||'/home/claude')+'/funds_gauge_unmeasured.png'});
// a person enters a dated figure after reading the vendor console -> the row shows it, dated, with a derived runway
const r = await ctx.request.post(B+'/admin/ai-funds', {headers:{'X-Admin-Token':ADM,'Content-Type':'application/json'}, data:{lane:'openai', balance_usd: 42.10, as_of:'2026-09-12', auto_topup:'armed'}});
check(r.status()===200, 'admin funds write failed '+r.status());
const bad = await ctx.request.post(B+'/admin/ai-funds', {headers:{'Content-Type':'application/json'}, data:{lane:'openai', balance_usd: 1}}); check(bad.status()===401, 'unauthenticated write was accepted');
await page.evaluate(() => window.apv3FundsLoad()); await page.waitForTimeout(1200);
strip = await page.evaluate(() => { const el=document.querySelector('[data-ai-funds]'); return el.textContent.replace(/\s+/g,' '); });
console.log('after manual figure:', strip.slice(0,260));
check(/\$42\.10 manual, 2026-09-12/.test(strip) && /auto-top-up armed/.test(strip), 'the dated manual figure / armed state is not on the row');
check(/runway ≈ ([\d.]+ days|over a year)/.test(strip), 'runway not rendered from the figure');
const j = await (await ctx.request.get(B+'/dashboard/ai-funds')).json();
const f = j.functions.find(x=>x.task==='fast'); console.log('fast:', f.funds, 'runway', f.runway_days, '|', f.runway_basis);
check(f.funds.balance_usd===42.1 && /manual figure of \$42.10 on 2026-09-12 minus/.test(f.runway_basis), 'runway basis does not name the manual figure and the measured spend');
await page.screenshot({path:(process.env.SHOT_DIR||'/home/claude')+'/funds_gauge_manual.png'});
// reset the rig figure
await ctx.request.post(B+'/admin/ai-funds', {headers:{'X-Admin-Token':ADM,'Content-Type':'application/json'}, data:{lane:'openai', clear:true, auto_topup:'unknown'}});
const realErrs = errs.filter(e=>!/r2Fallback/.test(e)); check(realErrs.length===0, 'page errors: '+realErrs.join(' | '));
await browser.close();
if(fails.length){ console.log('\nFAIL'); fails.forEach(f=>console.log(' -',f)); process.exit(1); }
console.log('\nALL FUNDS GAUGE RENDERED CHECKS PASS (412x915)');
