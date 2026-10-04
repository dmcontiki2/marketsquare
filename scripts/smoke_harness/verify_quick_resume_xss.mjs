// AUD-003 (4 Oct 2026 audit): a crafted /quick/?resume= link must never run script.
// Usage: serve the OLD quick.html at http://127.0.0.1:8701/quick/ and the NEW at :8702/quick/, then
//   PW=/path/to/playwright/index.mjs CHROME=/path/to/chrome node verify_quick_resume_xss.mjs
// EXECUTED 4 Oct 2026: OLD pwned 1-6 per link (with or without a tap); NEW 0 in every case, payload shown as text.
const { chromium } = await import(process.env.PW || 'playwright');
const b64u = o => Buffer.from(JSON.stringify(o),'utf8').toString('base64').replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
const evil = '<img src=x onerror="window.__pwned=(window.__pwned||0)+1">';
const payloads = {
  trail: {cat:'property',mode:'sell',step:1,picks:[{key:'what',label:evil}]},
  draft: {cat:'property',mode:'sell',step:99,picks:[{key:'what',label:evil},{key:'deal',label:evil,photo:'x" onerror="window.__pwned=9'}]},
};
const browser = await chromium.launch(process.env.CHROME ? {executablePath: process.env.CHROME} : {});
async function run(port, name, pl, opts={}) {
  const ctx = await browser.newContext({viewport:{width:412,height:915}});
  const page = await ctx.newPage();
  let url = `http://127.0.0.1:${port}/quick/?resume=${b64u(pl)}`;
  if (opts.nonce) {
    await page.goto(`http://127.0.0.1:${port}/quick/`);
    await page.evaluate(n => localStorage.setItem('ts_q_gn', n+'|'+Date.now()), 'abc123');
    url += '&rn=abc123';
  }
  await page.goto(url); await page.waitForTimeout(1500);
  let tapped = false;
  if (opts.tap) { const g = await page.$('#qswipgo'); if (g) { await g.click(); tapped = true; await page.waitForTimeout(1200); } }
  const r = await page.evaluate(() => ({pwned: window.__pwned||0, injectedImg: document.querySelectorAll('img[src="x"]').length,
     shownAsText: (document.getElementById('screen')||document.body).textContent.includes('onerror'),
     carryOn: !!document.getElementById('qswipgo'), screenCls: (document.getElementById('screen')||{}).className}));
  console.log(name.padEnd(28), JSON.stringify({...r, tapped}));
  await ctx.close();
}
for (const [label, port] of [['OLD',8701],['NEW',8702]]) {
  await run(port, label+' trail (no tap)', payloads.trail);
  await run(port, label+' draft (no tap)', payloads.draft);
  await run(port, label+' trail +tap', payloads.trail, {tap:true});
  await run(port, label+' draft +tap', payloads.draft, {tap:true});
  await run(port, label+' draft own-nonce', payloads.draft, {nonce:true});
}
await browser.close();
