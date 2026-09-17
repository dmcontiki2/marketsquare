import { chromium } from 'playwright';
import fs from 'fs';
const B='http://127.0.0.1:8000';
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args:['--no-sandbox'] });
const ctx = await browser.newContext({ viewport:{width:412,height:915}, isMobile:true, hasTouch:true, deviceScaleFactor:2 });
await ctx.addCookies([{name:'ts_review', value: fs.readFileSync(process.env.RIG_REVIEW_TOKEN_FILE || '/home/claude/rig_review_token.txt','utf8').trim(), domain:'127.0.0.1', path:'/'}]);
const page = await ctx.newPage();
const fails=[]; const errs=[]; page.on('pageerror', e => errs.push(String(e.message).slice(0,160)));
function check(c,m){ if(!c) fails.push(m); }
async function state(){ return page.evaluate(() => ({ items: sfDcb().items.map(i=>({key:i.key,name:i.file.name,slot:i.slot,rejected:!!i.rejected})), cover: sfDcb().cover, files: Object.keys(sfState.files).map(k=>[k, sfState.files[k].name]), photos: sfState.photos, mainPhase: sfState.mainPhase, tiles: [...document.querySelectorAll('.dcb-tile:not(.add)')].map(t=>({key:t.dataset.key, cover:t.classList.contains('cover'), h:t.getBoundingClientRect().height, w:t.getBoundingClientRect().width, badge:t.querySelector('.dcb-badge')?.textContent})) })); }
const pics = ['0_kitchen','1_exterior','2_bedroom','3_detail','4_lounge'].map(n=>(process.env.PICS_DIR||'/home/claude/pics')+'/'+n+'.jpg');

// flag OFF: slot step unchanged
await page.goto(B+'/?baseline=0',{waitUntil:'domcontentloaded'});
await page.waitForFunction(() => typeof sfInit==='function', null, {timeout:30000});
await page.evaluate(() => { try{ localStorage.setItem('ms_aa_email','david.jnr@example.com'); }catch(e){} goTo('sell-flow'); sfInit(); sfStartCat('Property'); });
await page.waitForTimeout(400);
const off = await page.evaluate(() => ({ slots: document.querySelectorAll('.sf-slot').length, dcb: document.querySelectorAll('.dcb-grid').length }));
check(off.slots>0 && off.dcb===0, 'flag OFF: photo step changed: '+JSON.stringify(off));
console.log('flag OFF: named-slot step intact', off);

// flag ON
await page.goto(B+'/?baseline=1',{waitUntil:'domcontentloaded'});
await page.waitForFunction(() => typeof sfInit==='function', null, {timeout:30000});
await page.evaluate(() => { goTo('sell-flow'); sfInit(); sfStartCat('Property'); });
await page.waitForTimeout(400);
let on = await page.evaluate(() => ({ dcb: document.querySelectorAll('.dcb-grid').length, add: document.querySelectorAll('.dcb-tile.add').length }));
check(on.dcb===1 && on.add===1, 'flag ON: DCB grid missing '+JSON.stringify(on));
// 1. batch upload in an arbitrary order (kitchen, exterior, bedroom, detail, lounge)
await page.setInputFiles('#sf-file-dcb', pics);
await page.waitForFunction(() => sfDcb().items.length===5, null, {timeout:10000});
await page.waitForTimeout(600);
let s = await state();
console.log('after batch:', s.items.map(i=>i.name+'→'+i.slot).join(', '), '| cover', s.cover, '| tiles', s.tiles.length);
check(s.items.length===5 && s.cover===s.items[0].key, 'batch upload: cover not first item');
check(s.files.some(f=>f[0]==='main'), 'batch upload: no main slot derived');
check(s.tiles.every(t=>t.h>=44 && t.w>=44), 'tiles under 44px');
const sw = await page.evaluate(() => document.documentElement.scrollWidth); check(sw<=412, 'overflow '+sw);
await page.screenshot({path:(process.env.SHOT_DIR||'/home/claude')+'/dcb_grid.png'});
// 2. tap ONE as cover (exterior = index 1)
const exteriorKey = s.items.find(i=>/exterior/.test(i.name)).key;
await page.click('.dcb-tile[data-key="'+exteriorKey+'"]');
await page.waitForTimeout(500);
s = await state();
console.log('after cover tap:', s.items.map(i=>i.name+'→'+i.slot).join(', '), '| cover', s.cover);
check(s.cover===exteriorKey && s.items[0].key===exteriorKey, 'tap did not set the cover');
check(s.files.find(f=>f[0]==='main')?.[1]==='1_exterior.jpg', 'main slot is not the tapped cover: '+JSON.stringify(s.files));
check(s.tiles[0].cover && /Cover/.test(s.tiles[0].badge), 'cover tile not badged');
// 3. AI order (rig has no vision key -> rules answer; the button must still complete)
await page.evaluate(() => sfDcbAiOrder());
await page.waitForFunction(() => !sfDcb().busy, null, {timeout:20000});
await page.waitForTimeout(300);
s = await state();
const note = await page.evaluate(() => document.querySelector('.dcb-note')?.textContent);
console.log('after AI order:', s.items.map(i=>i.name+'→'+i.slot).join(', '), '| note:', note);
check(s.items[0].key===exteriorKey, 'AI order moved the cover');
check(/Ordered/.test(note||''), 'AI order gave no answer: '+note);
check(s.items.slice(1).every(i=>i.slot && i.slot!=='main'), 'named slots not assigned after order: '+JSON.stringify(s.items));
// 4. drag to adjust: move the LAST tile onto the second position via pointer events
const keys = s.items.map(i=>i.key);
const last = keys[keys.length-1], second = keys[1];
await page.$eval('#dcb-grid', el => el.scrollIntoView({block:'center'})); await page.waitForTimeout(300);
const from = await page.$eval('.dcb-tile[data-key="'+last+'"]', el => { const r=el.getBoundingClientRect(); return {x:r.x+r.width/2,y:r.y+r.height/2}; });
const to = await page.$eval('.dcb-tile[data-key="'+second+'"]', el => { const r=el.getBoundingClientRect(); return {x:r.x+r.width/2,y:r.y+r.height/2}; });
await page.mouse.move(from.x, from.y); await page.mouse.down(); await page.mouse.move(from.x+10, from.y+10, {steps:3}); await page.mouse.move(to.x, to.y, {steps:8}); await page.mouse.up();
await page.waitForTimeout(500);
s = await state();
console.log('after drag:', s.items.map(i=>i.name+'→'+i.slot).join(', '));
check(s.items[1].key===last, 'drag did not move the tile to position 2: '+JSON.stringify(s.items.map(i=>i.name)));
check(s.items[0].key===exteriorKey, 'drag disturbed the cover');
// 5. arrows as the accessible fallback
await page.evaluate(k => sfDcbMove(k, 1), last); await page.waitForTimeout(300);
s = await state(); check(s.items[2].key===last, 'arrow move failed');
// 6. remove one, cover holds
const gone = s.items[3].key; await page.evaluate(k => sfDcbRemove(k), gone); await page.waitForTimeout(300);
s = await state(); check(s.items.length===4 && s.cover===exteriorKey && !s.items.find(i=>i.key===gone), 'remove broke the set');
// 7. publish holds the cover: the file list sfFinish builds starts with the cover
const pub = await page.evaluate(() => { var files=[]; var f=sfFlow(); f.slots.forEach(function(sl){ if(sfState.files[sl[0]]) files.push(sfState.files[sl[0]].name); }); Object.keys(sfState.files).forEach(function(k){ if(k.indexOf('extra')===0) files.push(sfState.files[k].name); }); return files; });
console.log('publish order:', pub.join(' > '));
check(pub[0]==='1_exterior.jpg', 'publish order does not start with the cover');
check(pub.length===4, 'publish order lost a photo: '+pub.length);
const disp = s.items.map(i=>i.name); check(JSON.stringify(pub)===JSON.stringify(disp), 'publish order != the grid order the seller made: '+JSON.stringify({pub,disp}));
// quality meter counts the set
const meter = await page.evaluate(() => sfScore().total);
console.log('quality score with 4 photos:', meter);
check(meter>=10, 'quality meter ignores the set');
await page.screenshot({path:(process.env.SHOT_DIR||'/home/claude')+'/dcb_after.png'});
const realErrs = errs.filter(e=>!/r2Fallback/.test(e)); check(realErrs.length===0, 'page errors: '+realErrs.join(' | '));
await browser.close();
if(fails.length){ console.log('\nFAIL'); fails.forEach(f=>console.log(' -',f)); process.exit(1); }
console.log('\nALL DCB-001 RENDERED CHECKS PASS (412x915)');
