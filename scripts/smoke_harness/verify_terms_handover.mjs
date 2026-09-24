/* TERMS-HANDOVER-1 / RG-0449 — the cold seller's last mile, walked rather than reasoned.
   (24 Sep 2026, onboarding run 19.)

   WHAT IT WALKS, on the LIVE site at phone size, as a seller with no acceptance on record:
     letter link (?signin=<7-day token>&draft=<id>) -> hub shows his advert -> tap Publish
     -> server refuses with 403 (EULA) -> he must LAND ON THE TERMS -> scroll to the end
     -> tick both boxes -> Go live -> a logged-out reader sees the advert.

   Run it from the cloud container (Playwright's Chromium):
     node scripts/smoke_harness/verify_terms_handover.mjs "<signin url>" <listing id>

   Minting the URL is a SERVER-side job (MS_JWT_SECRET lives only on the box, and
   QUICK-RETURN-TTL-1 / RG-0447 says a letter-borne token gets seven days, never the
   interactive lane's twenty minutes). On the box:
     secret = MS_JWT_SECRET from /etc/marketsquare/secrets.env   (empty => mint nothing)
     token  = jwt({email, purpose:'signin', iat, exp: iat+7*86400}, secret, 'HS256')
     url    = https://trustsquare.co/?signin=<token>&draft=<id>&src=<tag>
   Create the draft through the app's own door (POST /listings with X-Api-Key, from
   127.0.0.1:8000 — the edge answers 403 to a non-browser client, RG-0401), and ARCHIVE the
   probe in the same breath: a probe that publishes is publicly visible while it lives. */
import pw from '/home/claude/.npm-global/lib/node_modules/playwright/index.js';
const { chromium } = pw;
const URL = process.argv[2], LID = parseInt(process.argv[3], 10);
if (!URL || !LID) { console.error('usage: verify_terms_handover.mjs "<signin url>" <listing id>'); process.exit(2); }
const fails = [];
const step = m => console.log('· ' + m);
const check = (c, m) => { if (!c) { fails.push(m); console.log('  FAIL: ' + m); } else console.log('  ok: ' + m); };

const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox'] });
const ctx = await browser.newContext({ viewport: { width: 412, height: 915 }, isMobile: true, hasTouch: true });
const page = await ctx.newPage();
const reqs = [];
page.on('response', r => { const u = r.url().replace('https://trustsquare.co', ''); if (/^\/(users|auth|listings)/.test(u)) reqs.push(r.status() + ' ' + r.request().method() + ' ' + u.slice(0, 64)); });
const perr = []; page.on('pageerror', e => perr.push(String(e.message).slice(0, 160)));

await page.goto(URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
await page.waitForFunction(() => typeof window.msLandDraft === 'function', null, { timeout: 40000 });
await page.waitForTimeout(4000);
check(!!(await page.evaluate(() => localStorage.getItem('ms_aa_email'))), 'the letter link signs him in');
for (let i = 0; i < 20; i++) { if (await page.$(`[onclick="dashPublish(${LID})"]`)) break; await page.waitForTimeout(1000); }
check(!!(await page.$(`[onclick="dashPublish(${LID})"]`)), 'the hub puts his advert in front of him with Publish in reach');

await page.click(`[onclick="dashPublish(${LID})"]`);
await page.waitForTimeout(4500);
const landed = await page.evaluate(() => (document.querySelector('.sob-phase.sob-active') || {}).id);
step('handover landed on ' + landed + '   [requests: ' + reqs.slice(-2).join(' · ') + ']');
check(landed === 'sob-p3', 'tapping Publish lands him ON THE TERMS he was just told to read (landed: ' + landed + ')');
const note = await page.evaluate(() => { const n = document.getElementById('sob-returning-eula-note'); return n ? !!n.offsetParent : null; });
check(note === true, 'the screen says WHY he is here (the returning-seller terms note is shown)');

// forward by hand if the jump failed, so the rest of the mile is still measured
for (let hop = 0; hop < 4; hop++) {
  const p = await page.evaluate(() => (document.querySelector('.sob-phase.sob-active') || {}).id);
  if (p === 'sob-p3') break;
  await page.evaluate(() => { const b = [...document.querySelectorAll('.sob-phase.sob-active button,.sob-phase.sob-active [onclick]')].filter(e => e.offsetParent && !e.disabled).find(e => /looks good|continue|next|→/i.test(e.textContent || '')); if (b) b.click(); });
  await page.waitForTimeout(4000);
}
const box = await page.evaluate(() => { const b = document.getElementById('sob-eula-scroll'); return { chars: b.innerText.length, ver: (b.innerText.match(/Version\s+(\d+\.\d+)/) || [])[1], scrollH: b.scrollHeight, clientH: b.clientHeight }; });
step('terms box: ' + JSON.stringify(box) + '  (= ' + Math.round(box.scrollH / box.clientH) + ' screenfuls on a phone)');
check(box.chars > 50000 && !!box.ver, 'the terms render in the box, v' + box.ver);

let atBottom = false;
for (let i = 0; i < 400 && !atBottom; i++) {
  atBottom = await page.evaluate(() => { const b = document.getElementById('sob-eula-scroll'); b.scrollTop = Math.min(b.scrollHeight, b.scrollTop + b.clientHeight * 0.9); b.dispatchEvent(new Event('scroll')); return b.scrollTop + b.clientHeight >= b.scrollHeight - 40; });
}
await page.waitForTimeout(1200);
const gate = await page.evaluate(() => ({
  confirmVisible: !!(document.getElementById('sob-eula-confirm') || {}).offsetParent,
  eulaChk: !!(document.getElementById('sob-eula-chk') || {}).offsetParent,
  contentChk: !!(document.getElementById('sob-content-chk') || {}).offsetParent,
}));
check(gate.confirmVisible === true, 'reaching the end of the terms reveals the confirm row');
if (gate.eulaChk) await page.click('#sob-eula-chk');
if (gate.contentChk) await page.click('#sob-content-chk');
await page.waitForTimeout(800);
const nx = await page.evaluate(() => { const b = document.getElementById('sob-p3-next'); return b ? { text: (b.textContent || '').trim(), disabled: b.disabled } : null; });
check(nx && !nx.disabled, 'after ticking, Go live is enabled');
reqs.length = 0;
if (nx && !nx.disabled) { await page.click('#sob-p3-next'); await page.waitForTimeout(11000); }
step('requests during go-live: ' + JSON.stringify(reqs));
const after = await page.evaluate(() => ({ phase: (document.querySelector('.sob-phase.sob-active') || {}).id, text: document.body.innerText.replace(/\n+/g, ' | ').slice(0, 160) }));
step('after: ' + JSON.stringify(after));
check(/publish/i.test(reqs.join(' ')) && /200 PUT \/listings/.test(reqs.join(' ')), 'the publish call answers 200');

const p2 = await (await browser.newContext()).newPage();
const r = await p2.goto('https://trustsquare.co/listings/' + LID, { waitUntil: 'domcontentloaded', timeout: 60000 });
let j = null; try { j = JSON.parse(await p2.evaluate(() => document.body.innerText)); } catch (e) {}
step('logged-out GET /listings/' + LID + ' -> ' + r.status() + ' listing_status=' + JSON.stringify(j && j.listing_status));
check(!!j && (j.listing_status === 'live' || j.listing_status === null), 'the advert is live to a logged-out reader');
if (perr.length) { step('page errors:'); perr.slice(0, 5).forEach(e => console.log('    ' + e)); }
console.log('\nVERDICT: ' + (fails.length ? 'FAIL (' + fails.length + ')' : 'PASS'));
fails.forEach(f => console.log('  - ' + f));
console.log('\nREMEMBER: archive the probe listing now — it is public while it lives.');
await browser.close();
process.exit(fails.length ? 1 : 0);
