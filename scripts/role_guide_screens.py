"""role_guide_screens.py -- ROLE-GUIDES-1 (8 Oct 2026): each role's own Quick screens for its How guide, captured on the live site.
    python3 scripts/role_guide_screens.py <out_dir> <role_key> [...]   -> <out_dir>/<role>/<screen>.jpg (what, qual, where, days, price/how, draft)
Run where Playwright's Chromium is (the cloud session); copy each to stories/img/<role>/r_<screen>.jpg, then
scripts/build_role_guides.py, scripts/build_help.py, scripts/build_help.py --push-images. Nothing is saved or published:
the walk stops on 'Here is your listing'."""
import asyncio, json, sys, os
from playwright.async_api import async_playwright
OUT=sys.argv[1]; ROLES=sys.argv[2:]
UA='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
AREAS=['Menlyn','Pretoria East']
async def shot(pg, path):
    await pg.wait_for_timeout(700)
    await pg.screenshot(path=path, type='jpeg', quality=82)
async def key(pg):
    return await pg.evaluate("()=>{try{return qHelpAt()}catch(e){return '?'}}")
async def walk(b, r):
    d=os.path.join(OUT,r); os.makedirs(d,exist_ok=True)
    ctx=await b.new_context(viewport={'width':390,'height':844},device_scale_factor=420/390,is_mobile=True,has_touch=True,user_agent=UA,locale='en-ZA',timezone_id='Africa/Johannesburg',
                            geolocation={'latitude':-25.78,'longitude':28.27},permissions=['geolocation'])
    await ctx.add_init_script("try{localStorage.setItem('ts_qcc','ZA');localStorage.setItem('ts_qcity','ZA|Pretoria');localStorage.setItem('ts_qlang','en');}catch(e){}")
    pg=await ctx.new_page()
    await pg.goto('https://trustsquare.co/quick/?v=g1',wait_until='networkidle')
    await pg.evaluate("()=>{try{localStorage.setItem('ms_user_city','Pretoria');}catch(e){}}")
    R=await pg.evaluate("(r)=>SVC_ROLES.find(x=>x.k===r)", r)
    await pg.get_by_role('button', name='Offer a service').click()
    await pg.wait_for_timeout(600)
    await pg.locator('#screen button.tile', has_text=R['g']).first.click()
    await pg.wait_for_timeout(700)
    t=pg.locator('#screen button.tile', has_text=R['l']).first
    await t.scroll_into_view_if_needed()
    await shot(pg, os.path.join(d,'what.jpg'))
    await t.click(); await pg.wait_for_timeout(700)
    seen=[]
    for i in range(14):
        k=await key(pg); q=await pg.evaluate("()=>{var e=document.querySelector('#screen .q');return e?e.innerText:''}")
        seen.append((k,q))
        if k in ('draft','saved') or 'Here is your listing' in q:
            await pg.evaluate("()=>{var s=document.querySelector('#screen');if(s)s.scrollTop=0;window.scrollTo(0,0)}")
            await shot(pg, os.path.join(d,'draft.jpg')); break
        await shot(pg, os.path.join(d,'%s.jpg'%k))
        has=await pg.evaluate("""()=>({rate:!!document.getElementById('rtgo'), menu:document.querySelectorAll('.rtm').length,
            week:!!document.querySelector('#screen [data-d], #screen .wk, #screen .day'),
            next:!!document.getElementById('qareas-next'), tiles:document.querySelectorAll('#screen button.tile:not(.free)').length,
            chips:document.querySelectorAll('#screen .chips button.chip:not(.free)').length, ask:!!document.getElementById('apgo')})""")
        if await pg.locator('#wk').count():
            for i in range(5): await pg.locator('#wk button.wd').nth(i).click()
            await pg.click('#wkgo')
        elif has['rate']:
            if has['menu']:
                vals=['60','90','120','250']
                for j in range(has['menu']): await pg.locator('.rtm').nth(j).fill(vals[j%4])
            else:
                await pg.fill('#rta','350')
                if await pg.locator('#rth').is_visible(): await pg.fill('#rth','350')
            await pg.wait_for_timeout(200); await pg.click('#rtgo')
        elif has['next']:
            for a in AREAS:
                loc=pg.locator('#screen button', has_text=a)
                if await loc.count(): await loc.first.click()
            await pg.click('#qareas-next')
        elif has['tiles']:
            await pg.locator('#screen button.tile:not(.free)').first.click()
        elif has['chips']:
            await pg.locator('#screen .chips button.chip:not(.free)').first.click()
        else:
            # week screen: tap Mon..Fri then the foot button
            done=False
            for dname in ['Mon','Tue','Wed','Thu','Fri']:
                loc=pg.locator('#screen button', has_text=dname)
                if await loc.count(): await loc.first.click(); done=True
            fb=pg.locator('#screen .foot button')
            if await fb.count(): await fb.first.click()
            elif not done: break
        await pg.wait_for_timeout(600)
    await ctx.close()
    return seen
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        res={}
        for r in ROLES:
            try: res[r]=await walk(b,r)
            except Exception as e: res[r]='ERR %s'%e
            print(r, res[r], flush=True)
        await b.close()
        json.dump(res, open(os.path.join(OUT,'_walk.json'),'w'), indent=1)
asyncio.run(main())
