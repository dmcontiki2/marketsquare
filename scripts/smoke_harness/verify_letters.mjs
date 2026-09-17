import { chromium } from 'playwright';
import fs from 'fs';
const B='http://127.0.0.1:8000';
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args:['--no-sandbox'] });
const ctx = await browser.newContext({ viewport:{width:412,height:915}, isMobile:true, hasTouch:true, deviceScaleFactor:2 });
await ctx.addCookies([{name:'ts_review', value: fs.readFileSync((process.env.RIG_REVIEW_TOKEN_FILE||'/home/claude/rig_review_token.txt'),'utf8').trim(), domain:'127.0.0.1', path:'/'}]);
const fails=[]; function check(c,m){ if(!c) fails.push(m); }
const res = JSON.parse(fs.readFileSync((process.env.LETTERS_DIR||'/home/claude/letters')+'/render_result.json','utf8'));
for (const fn of Object.keys(res)){
  const r = res[fn];
  check(r.console_link && r.lanes.every(Boolean) && !r.reply && r.placeholders_left.length===0, fn+' rendered wrong: '+JSON.stringify(r));
  // the rendered letter at phone width: the three lanes read, the CTA is the console link
  const html = fs.readFileSync((process.env.LETTERS_DIR||'/home/claude/letters')+'/rendered_'+fn,'utf8');
  const page = await ctx.newPage();
  await page.setContent(html, {waitUntil:'domcontentloaded'});
  const view = await page.evaluate(() => { const h=[...document.querySelectorAll('h3')].map(e=>e.textContent.trim()); const cta=[...document.querySelectorAll('a.cta-button')].map(a=>({t:a.textContent.trim(), href:a.getAttribute('href')})); return {h, cta, hasLane: /pick your lane/i.test(document.body.textContent), support: !!document.querySelector('a[href="https://trustsquare.co/support"]'), reply: /reply to this email/i.test(document.body.textContent), w: document.documentElement.scrollWidth}; });
  console.log(fn, '→', view.h.find(h=>/lane/i.test(h)), '| CTA:', view.cta.map(c=>c.t+' → '+c.href.slice(0,40)).join(' ; '), '| support link', view.support, '| reply', view.reply);
  check(view.hasLane && view.support && !view.reply, fn+': the rendered letter does not tell the agency story via the support door');
  check(view.cta.some(c=>/signin=/.test(c.href) && /(agency|operator|dealer)=1/.test(c.href)), fn+': the rendered CTA is not a console link: '+JSON.stringify(view.cta));
  if (fn==='agency_outreach.html') await page.screenshot({path:(process.env.SHOT_DIR||'/home/claude')+'/letter_agency.png', fullPage:false});
  await page.close();
}
// the console link WORKS: open it on the rig origin (same JWT secret) -- the app signs in and opens the agency console
const link = res['agency_outreach.html'].link ? fs.readFileSync((process.env.LETTERS_DIR||'/home/claude/letters')+'/rendered_agency_outreach.html','utf8').match(/href="([^"]*signin=[^"]*)"/)[1] : null;
const rigLink = link.replace('https://trustsquare.co', B).replace(/&amp;/g,'&');
const page = await ctx.newPage(); const errs=[]; page.on('pageerror', e=>errs.push(String(e.message).slice(0,140)));
await page.goto(rigLink, {waitUntil:'domcontentloaded'});
await page.waitForFunction(() => localStorage.getItem('ms_aa_email')==='ntombi.dlamini@example.com', null, {timeout:30000}).catch(()=>{});
await page.waitForTimeout(2500);
const state = await page.evaluate(() => ({ email: localStorage.getItem('ms_aa_email'), screen: document.querySelector('.screen.active')?.id, consoleOpen: !!document.querySelector('#screen-agency.active, #agency-console, [id^=ag-console], #screen-agency-console.active'), title: (document.querySelector('.screen.active h1, .screen.active .ag-title')||{}).textContent }));
console.log('console link opened →', state);
check(state.email==='ntombi.dlamini@example.com', 'the console link did not sign the agency admin in');
check(/agency/i.test(state.screen||'') || state.consoleOpen, 'the console link did not open the agency console: '+JSON.stringify(state));
await page.screenshot({path:(process.env.SHOT_DIR||'/home/claude')+'/letter_console.png'});
const realErrs = errs.filter(e=>!/r2Fallback/.test(e)); check(realErrs.length===0, 'page errors: '+realErrs.join(' | '));
await browser.close();
if(fails.length){ console.log('\nFAIL'); fails.forEach(f=>console.log(' -',f)); process.exit(1); }
console.log('\nALL AGENCY LETTER RENDERED CHECKS PASS (412x915)');
