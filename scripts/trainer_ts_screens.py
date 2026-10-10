"""trainer_ts_screens.py -- TRAINER-SCREENS-2 (David, 10 Oct 2026: "Yes please fix all").
The TrustSquare side of every sport How guide (Edit, Seller Hub, advert, Join queue, the request, Accept, the parent's intros),
captured as the QA test seller Zanele and parent Nosipho on their walked listing #457 with the sport's title, price, photo and
message swapped in the API answers on screen. Every write is answered locally -- nothing reaches the server.
Needs jars.json (the two QA sessions, from /qa/signin) and mine.json / pub478.json / trn.json beside it; delete jars.json after.
    python3 trainer_ts_screens.py <out_dir> <sport_key> [...]   -> <out_dir>/<sport>/t_*.jpg
"""
import asyncio,json,sys,re
from playwright.async_api import async_playwright
UA='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
J=json.load(open('jars.json'))
INIT="""try{['ms_user_country','ms_auto_country'].forEach(k=>localStorage.setItem(k,'ZA'));['ms_user_city','ms_auto_city','ms_city'].forEach(k=>localStorage.setItem(k,'Pretoria'));localStorage.setItem('ts_lang','en');}catch(e){}"""
async def new(b,who,rewrite=None,dump=None):
    ctx=await b.new_context(viewport={'width':390,'height':844},device_scale_factor=420/390,is_mobile=True,has_touch=True,user_agent=UA,locale='en-ZA',timezone_id='Africa/Johannesburg',
        geolocation={'latitude':-25.78,'longitude':28.27},permissions=['geolocation'])
    await ctx.add_cookies(J[who]); await ctx.add_init_script(INIT)
    async def rt(route):
        r=route.request
        if r.method not in ('GET','HEAD'):
            await route.fulfill(status=200,content_type='application/json',body='{"ok":true}'); return
        if r.resource_type in ('fetch','xhr') and 'trustsquare.co' in r.url and (rewrite or dump is not None):
            resp=await route.fetch(); body=await resp.text()
            if dump is not None: dump.append((r.url.replace('https://trustsquare.co',''),body))
            if rewrite:
                nb=rewrite(r.url,body)
                if nb!=body and resp.status>=400:
                    await route.fulfill(status=200,content_type='application/json',body=nb); return
                body=nb
            await route.fulfill(response=resp,body=body); return
        await route.continue_()
    await ctx.route('**/*',rt)
    return ctx, await ctx.new_page()
async def shot(pg,path,wait=1500):
    await pg.wait_for_timeout(wait); await pg.screenshot(path=path,type='jpeg',quality=82)
import asyncio,json,sys,os,copy,re
MINE=json.load(open('mine.json'))[0]
PUB=json.load(open('pub478.json'))
for _k in ['attested_email','desc_extra','extra_back','hidden_from_strangers','search_en','seller_email','street_address','suburb_lat','suburb_lng','title_extra']: MINE.pop(_k,None)
for _k in ['demo_example','location_precision','seller_can_receive','seller_id_checked','seller_id_green_tick']: MINE[_k]=PUB.get(_k)
MINE.update(demo_example=False,is_demo=0,super_example=0,seller_can_receive=True,seller_id_checked=False,seller_id_green_tick=False)
TRN=json.load(open('trn.json'))
LID=457
def mk(k):
    L=TRN[k]; T='%s — Menlyn, Pretoria East'%L; P='https://trustsquare.co/static/quick/role_%s.jpg?v=photo1'%k
    noun=L if L.startswith('MMA') else L[0].lower()+L[1:]
    art='an' if (noun[0].lower() in 'aeiou' or noun.startswith('MMA')) else 'a'
    M='Molo Zanele, my son would like lessons with %s %s. Can you help on Saturdays?'%(art,noun)
    def fix_listing(d):
        d.update(title=T,price='R250 / session',price_num=250.0,subject=L,level=None,mode=None,service_class='Trainers',service_type=L,
                 description='[photos:%s]\n**Travel radius:** 15 km\n\n%s in Menlyn, Pretoria East. Rate: R250 / session. Send me an introduction request on TrustSquare and I will get back to you.'%(P,L),
                 thumb_url=P,medium_url=P,photo_urls=json.dumps([P]),listing_status='live')
    REP=[('Maths — High school',T),('Maths, Maths Literacy, Physical Science',L),('R280 / hour','R250 / session'),
         ('Molo Zanele, my son is in Grade 11 and struggles with functions. Can you help on Tuesdays, in person?',M)]
    def walk(o):
        if isinstance(o,dict):
            if o.get('id')==LID and 'title' in o: fix_listing(o)
            for kk,v in list(o.items()): o[kk]=walk(v)
            return o
        if isinstance(o,list): return [walk(x) for x in o]
        if isinstance(o,str):
            for a,b in REP: o=o.replace(a,b)
            o=re.sub(r'https://pub-[^"\s|\]]*_tutor[12]\.jpg',P,o)
            return o
        return o
    return T,M,walk,fix_listing
def make_rewrite(k,mode):
    T,M,walk,fix_listing=mk(k)
    def rw(url,body):
        u=url.replace('https://trustsquare.co','')
        if re.match(r'^/listings/%d(\?|$)'%LID,u):
            d=copy.deepcopy(MINE); fix_listing(d); return json.dumps(d)
        if mode=='seller_pending' and re.match(r'^/intros(\?|$)',u):
            return json.dumps([{"id":154,"listing_id":LID,"buyer_email":"dmcontiki2+qa-nosipho0930@gmail.com","message":M,"status":"pending","tuppence_charged":0,
               "created_at":"2026-10-10 08:00:00","buyer_name":"Nosipho","intro_type":"standard","tuppence_held":1,"listing_title":T,"category":"Tutors","city":"Pretoria","listing_type":None}])
        if mode=='seller_none' and re.match(r'^/intros(\?|$)',u): return '[]'
        try: o=json.loads(body)
        except Exception: return body
        return json.dumps(walk(o))
    return rw
async def go_hub(pg):
    await pg.goto('https://trustsquare.co/',wait_until='networkidle'); await pg.wait_for_timeout(2000)
    await pg.get_by_text('Seller Hub').first.click(); await pg.wait_for_timeout(3500)
async def run(b,k,out):
    os.makedirs(out,exist_ok=True)
    # seller, no requests: published hub + edit listing
    ctx,pg=await new(b,'zanele0930',rewrite=make_rewrite(k,'seller_none'))
    await go_hub(pg); await shot(pg,out+'/t_published.jpg',500)
    await pg.locator('button:has-text("Edit")').first.click(); await pg.wait_for_timeout(3000)
    await shot(pg,out+'/t_photos.jpg',500); await ctx.close()
    # seller with a waiting request, then accept
    ctx,pg=await new(b,'zanele0930',rewrite=make_rewrite(k,'seller_pending'))
    await go_hub(pg); await shot(pg,out+'/t_request.jpg',500)
    await pg.locator('button:has-text("Accept")').first.click(); await pg.wait_for_timeout(1800)
    await shot(pg,out+'/t_accept.jpg',300); await ctx.close()
    # parent: detail, join queue, her intros
    ctx,pg=await new(b,'nosipho0930',rewrite=make_rewrite(k,'buyer'))
    await pg.goto('https://trustsquare.co/?listing=%d'%LID,wait_until='networkidle'); await pg.wait_for_timeout(3500)
    await shot(pg,out+'/t_detail.jpg',500)
    jq=pg.locator('button:has-text("Join queue"), button:has-text("Request introduction")').first
    await jq.click(); await pg.wait_for_timeout(1500)
    ta=pg.locator('textarea:visible').first
    if await ta.count(): await ta.fill(mk(k)[1])
    await shot(pg,out+'/t_ask.jpg',600)
    await pg.goto('https://trustsquare.co/',wait_until='networkidle'); await pg.wait_for_timeout(1500)
    await pg.locator('text=My Space').last.click(); await pg.wait_for_timeout(2500)
    await pg.locator(':text-is("Intros"):visible').first.click(); await pg.wait_for_timeout(2500)
    await shot(pg,out+'/t_buyer_intros.jpg',500); await ctx.close()
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    for k in sys.argv[2:]:
        try: await run(b,k,os.path.join(sys.argv[1],k)); print('ok',k,flush=True)
        except Exception as e: print('FAIL',k,repr(e)[:300],flush=True)
    await b.close()
asyncio.run(main())
