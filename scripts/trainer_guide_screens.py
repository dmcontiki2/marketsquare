"""trainer_guide_screens.py -- TRAINER-SCREENS-1 (David, 10 Oct 2026: "this is the Sport & fitness but it is showing
maths ... fix these in all of the How flows to be related to the actual selections").
Each trainer's OWN Quick screens for its How guide, captured on the live site (the Tutors door's Sport & fitness):
    python3 scripts/trainer_guide_screens.py <out_dir> <sport_key> [...]
 -> <out_dir>/<sport>/r_what, r_price, r_where, r_draft, r_saved (seller) and r_find_what, r_results (finder).
Nothing reaches the server: every non-GET request (the save, /onboard/step) is answered locally by the route below,
so the saved card is drawn exactly as she sees it without a listing being made. Copy each folder to stories/img/<sport>/,
then scripts/build_trainer_guides.py, scripts/build_help.py, scripts/build_help.py --push-images.
Run where Playwright's Chromium is (the cloud session)."""
import asyncio, sys, os, json
from playwright.async_api import async_playwright
UA='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
OUT=sys.argv[1]; ROLES=[a for a in sys.argv[2:] if not a.startswith('--')]
AREAS=['Menlyn','Pretoria East']
LOG=[]
async def block(route):
    req=route.request
    if req.method!='GET':
        LOG.append(req.method+' '+req.url)
        await route.fulfill(status=200,content_type='application/json',body=json.dumps({"id":1,"ok":True,"need":"eula","identity":"email"}))
    else:
        await route.continue_()
async def shot(pg,path,top=True):
    await pg.wait_for_timeout(900)
    if top: await pg.evaluate("()=>{var s=document.querySelector('#screen');if(s)s.scrollTop=0;window.scrollTo(0,0)}")
    await pg.screenshot(path=path,type='jpeg',quality=82)
async def newpage(b):
    ctx=await b.new_context(viewport={'width':390,'height':844},device_scale_factor=420/390,is_mobile=True,has_touch=True,user_agent=UA,locale='en-ZA',timezone_id='Africa/Johannesburg',
        geolocation={'latitude':-25.78,'longitude':28.27},permissions=['geolocation'])
    await ctx.add_init_script("try{localStorage.setItem('ts_qcc','ZA');localStorage.setItem('ts_qcity','ZA|Pretoria');localStorage.setItem('ts_qlang','en');localStorage.setItem('ms_user_city','Pretoria');}catch(e){}")
    await ctx.route('**/*',block)
    return ctx, await ctx.new_page()
async def areas(pg):
    for a in AREAS:
        loc=pg.locator('#screen button',has_text=a)
        if await loc.count(): await loc.first.click(); await pg.wait_for_timeout(150)
async def seller(b,r):
    d=os.path.join(OUT,r); os.makedirs(d,exist_ok=True)
    ctx,pg=await newpage(b)
    await pg.goto('https://trustsquare.co/quick/?role='+r,wait_until='networkidle'); await pg.wait_for_timeout(1200)
    # the sport screen: back one step
    await pg.evaluate("()=>{picks=picks.filter(p=>p.key!=='what');step=2;drawStep();}")
    await pg.wait_for_timeout(800)
    lbl=await pg.evaluate("(r)=>trnRole(r).l",r)
    t=pg.locator('#screen button.tile',has_text=lbl).first
    if await t.count(): await t.scroll_into_view_if_needed()
    await shot(pg,os.path.join(d,'r_what.jpg'),top=False)
    await t.click(); await pg.wait_for_timeout(900)
    assert await pg.evaluate("()=>qHelpAt()")=='price'
    await pg.fill('#rta','250'); await pg.wait_for_timeout(300)
    await shot(pg,os.path.join(d,'r_price.jpg'))
    await pg.click('#rtgo'); await pg.wait_for_timeout(900)
    assert await pg.evaluate("()=>qHelpAt()")=='where', await pg.evaluate("()=>qHelpAt()")
    await areas(pg)
    await shot(pg,os.path.join(d,'r_where.jpg'))
    await pg.click('#qareas-next'); await pg.wait_for_timeout(1500)
    await shot(pg,os.path.join(d,'r_draft.jpg'))
    inp=pg.locator('#screen input')
    n=await inp.count()
    for i in range(n):
        ph=(await inp.nth(i).get_attribute('placeholder')) or ''
        if 'name' in ph.lower(): await inp.nth(i).fill('Zanele')
        elif 'email' in ph.lower(): await inp.nth(i).fill('zanele@example.com')
    await pg.locator('#screen button',has_text='Save my listing').first.click()
    await pg.wait_for_timeout(3500)
    await pg.screenshot(path=os.path.join(d,'r_saved.jpg'),type='jpeg',quality=82)
    await ctx.close()
async def finder(b,r):
    d=os.path.join(OUT,r)
    ctx,pg=await newpage(b)
    await pg.goto('https://trustsquare.co/quick/',wait_until='networkidle'); await pg.wait_for_timeout(1200)
    await pg.evaluate("""(r)=>{var R=trnRole(r);for(var i=0;i<CATS.length;i++) if(CATS[i].key==='tutors') ci=i; start('find');
      picks.push({label:'Sport & fitness', photo:null, key:'tdoor', trn:1}); picks.push({label:R.g, photo:'role_'+R.k, key:'group', g:R.g});
      step=2; drawStep();}""",r)
    await pg.wait_for_timeout(900)
    lbl=await pg.evaluate("(r)=>trnRole(r).l",r)
    t=pg.locator('#screen button.tile',has_text=lbl).first
    if await t.count(): await t.scroll_into_view_if_needed()
    await shot(pg,os.path.join(d,'r_find_what.jpg'),top=False)
    await t.click(); await pg.wait_for_timeout(900)
    await areas(pg)
    if await pg.locator('#qareas-next').count(): await pg.click('#qareas-next')
    await pg.wait_for_timeout(3500)
    await shot(pg,os.path.join(d,'r_results.jpg'))
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for r in ROLES:
            try:
                await seller(b,r)
                if '--seller' not in sys.argv: await finder(b,r); print('ok',r)
            except Exception as e: print('FAIL',r,repr(e)[:200])
        await b.close()
    print('non-GET blocked:',len(LOG),LOG[:5])
asyncio.run(main())
