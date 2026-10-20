# QUICK-SNAP-1 U6 rendered proof: the WORKTREE quick.html served locally, APIs mocked (flags ON, snap-draft canned from the
# route proof's real answers, quick-publish mocked). Nothing touches the live site except read-only static files.
import asyncio, json, re, base64, io, sys
from playwright.async_api import async_playwright
BASE='http://127.0.0.1:8787'; LIVE='https://trustsquare.co'
flags=json.load(open('live_flags.json')); flags['quick_snap']=True; flags.setdefault('effective',{})['quick_snap']=True; flags['effective']['quick_fastlane']=True
me=json.load(open('live_me.json')); me['geo']={"country":"ZA","city":"Pretoria","lat":-25.7479,"lng":28.2293}
mocks=json.load(open('snap_mocks.json'))
log=[]
async def route_all(route):
  try:
    await _route(route)
  except Exception as e:
    print('  ROUTE ERR', route.request.url[-60:], repr(e)[:160]); await route.abort()
async def _route(route):
    req=route.request; url=req.url; path=url.replace(BASE,'')
    if path.startswith('/quick/') and (path.split('?')[0] in ('/quick/','/quick/index.html')): return await route.continue_()   # the CANDIDATE page itself, served locally
    if path.startswith('/flags'): return await route.fulfill(json=flags)
    if path.startswith('/quick/me'): return await route.fulfill(json=me)
    if path.startswith('/listings/snap-draft'):
        body=req.post_data_buffer or b''
        has_photo=b'filename="snap.jpg"' in body
        m=re.search(rb'name="sentence"\r\n\r\n(.*?)\r\n', body, re.S); sent=(m.group(1).decode('utf-8','ignore') if m else '')
        m2=re.search(rb'name="category_hint"\r\n\r\n(.*?)\r\n', body, re.S); hint=(m2.group(1).decode() if m2 else '')
        log.append(('snap-draft', has_photo, sent[:60], hint))
        if has_photo and not sent: j=mocks['snap_card']
        elif 'Something nice' in sent: j=mocks['say_unplaced']
        else: j=mocks['say_cleaner']
        return await route.fulfill(json=j)
    if path.startswith('/listings/quick-publish'):
        log.append(('quick-publish', (req.post_data_buffer or b'')[:200].decode('utf-8','ignore')))
        return await route.fulfill(json={"id":9001,"live":True,"identity":"email","open_url":LIVE+"/?listing=9001"})
    if path.startswith('/quality/preview'): return await route.fulfill(json={"score":60})
    if req.method=='POST': return await route.fulfill(status=204, body='')
    # everything else read-only from the live site (pictures, roles, help)
    try:
        r=await route.fetch(url=LIVE+path); return await route.fulfill(response=r)
    except Exception: return await route.fulfill(status=404, body='')
async def shot(pg, name): await pg.screenshot(path=name); print('  shot', name)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ctx=await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, locale='en-ZA', timezone_id='Africa/Johannesburg', is_mobile=True, has_touch=True, geolocation={'latitude':-25.7830,'longitude':28.2760}, permissions=['geolocation'])
        pg=await ctx.new_page(); await pg.route(BASE+'/**', route_all)
        pg.on('pageerror', lambda e: print('  PAGEERROR', str(e)[:160]))
        # ---- A: Say it (cleaner) ----
        await pg.goto(BASE+'/quick/?cc=ZA', wait_until='networkidle'); await pg.wait_for_timeout(1500)
        print('A door buttons:', await pg.locator('#qsSnap').count(), await pg.locator('#qsSay').count(), '| texts:', await pg.locator('#qsacts').inner_text() if await pg.locator('#qsacts').count() else '-')
        await shot(pg,'snap_1_door.png')
        await pg.locator('#qsSay').click(); await pg.wait_for_timeout(800)
        chips=await pg.locator('#qsdoors button').all_text_contents(); print('A door chips:', [c.strip() for c in chips][:12])
        for c in await pg.locator('#qsdoors button').all():
            t=(await c.text_content() or '').strip()
            if re.search(r'home|casual|house|help', t, re.I): await c.click(); print('  chose chip', t); break
        await pg.locator('#qssay').fill('Home cleaner, Mamelodi, Tuesdays and Thursdays, R350 a day'); await pg.wait_for_timeout(300)
        await shot(pg,'snap_2_say_screen.png')
        await pg.locator('#qsgo').click(); await pg.wait_for_timeout(2500)
        q=(await pg.locator('#screen .q').first.text_content() or '').strip() if await pg.locator('#screen .q').count() else ''
        print('A after Make my advert -> screen:', q, '| pub button:', await pg.locator('#pub').count())
        await shot(pg,'snap_3_cleaner_draft.png')
        card=(await pg.locator('#screen .card').first.inner_text())[:300].replace('\n',' | ') if await pg.locator('#screen .card').count() else ''
        print('A card:', card)
        if await pg.locator('#qpmail').count():
            await pg.locator('#qpname').fill('Thandi'); await pg.locator('#qpmail').fill('qa-snap@example.com')
            await pg.locator('#pub').scroll_into_view_if_needed(); await pg.locator('#pub').click(); await pg.wait_for_timeout(1500)
            txt=await pg.evaluate("document.body.innerText"); print('A arrival live line:', 'Your listing is live.' in txt)
            await shot(pg,'snap_4_cleaner_live_mocked.png')
        # ---- B: Snap it (card photo) ----
        await pg.goto(BASE+'/quick/?cc=ZA', wait_until='networkidle'); await pg.wait_for_timeout(1200)
        await pg.locator('#qsSnap').click(); await pg.wait_for_timeout(800)
        for c in await pg.locator('#qsdoors button').all():
            t=(await c.text_content() or '').strip()
            if re.search(r'collect|card', t, re.I): await c.click(); print('  chose chip', t); break
        # a real photo: the app's own example card picture
        png=await (await ctx.request.get(LIVE+'/assets/quick_ph/col_cards_1.jpg')).body() if False else None
        import urllib.request
        try: img=urllib.request.urlopen(LIVE+'/assets/quick_ph/col_cards_1.jpg', timeout=15).read()
        except Exception as e: img=None; print('  no live sample photo', e)
        if img is None:
            from PIL import Image; bio=io.BytesIO(); Image.new('RGB',(600,800),(90,60,30)).save(bio,'JPEG'); img=bio.getvalue()
        async with pg.expect_file_chooser() as fc:
            await pg.locator('#qslast').click()
        chooser=await fc.value; await chooser.set_files({'name':'card.jpg','mimeType':'image/jpeg','buffer':img}); await pg.wait_for_timeout(1200)
        print('B photo shown:', await pg.locator('#qsph img').count())
        await shot(pg,'snap_5_snap_screen_photo.png')
        await pg.locator('#qsgo').click(); await pg.wait_for_timeout(2500)
        q=(await pg.locator('#screen .q').first.text_content() or '').strip() if await pg.locator('#screen .q').count() else ''
        print('B after -> screen:', q, '| pub:', await pg.locator('#pub').count())
        card=(await pg.locator('#screen .card').first.inner_text())[:300].replace('\n',' | ') if await pg.locator('#screen .card').count() else ''
        print('B card:', card)
        await shot(pg,'snap_6_card_draft.png')
        # ---- C: a sentence the reader cannot place (cars) ----
        await pg.goto(BASE+'/quick/?cc=ZA', wait_until='networkidle'); await pg.wait_for_timeout(1200)
        await pg.locator('#qsSay').click(); await pg.wait_for_timeout(600)
        for c in await pg.locator('#qsdoors button').all():
            t=(await c.text_content() or '').strip()
            if re.search(r'car', t, re.I): await c.click(); print('  chose chip', t); break
        await pg.locator('#qssay').fill('Something nice for sale'); await pg.locator('#qsgo').click(); await pg.wait_for_timeout(2000)
        q=(await pg.locator('#screen .q').first.text_content() or '').strip() if await pg.locator('#screen .q').count() else ''
        note=(await pg.locator('.qf-note').first.text_content() or '').strip() if await pg.locator('.qf-note').count() else ''
        print('C lands on:', q, '| note:', note[:120])
        await shot(pg,'snap_7_unplaced_lands_on_step.png')
        # ---- D: switch OFF hides the buttons ----
        flags['effective']['quick_snap']=False; flags['quick_snap']=False
        await pg.goto(BASE+'/quick/?cc=ZA', wait_until='networkidle'); await pg.wait_for_timeout(1500)
        print('D switch OFF -> buttons:', await pg.locator('#qsSnap').count(), await pg.locator('#qsSay').count())
        print('LOG:', log)
        await b.close()
asyncio.run(main())
