"""door_render_proof.py -- ONE-DOOR-1 (DOOR_BRIEF.md U6): the door, the AI PA page and the explainer RENDERED in a headless
phone (Playwright Chromium, 390x844). door.html / pa.html / pa_about.html come from this repo, the pictures from assets/door,
the listings are the app's own Pretoria view (a saved copy of GET /listings); /door/me, /squire/status and every tap are
mocked, so nothing is written anywhere. 21 checks: collage, last app, interest filter, advert tap, Snap tap, AI PA door,
AI PA page + new brief body, explainer, Afrikaans.
Usage: python3 scripts/door_render_proof.py <listings.json saved from https://trustsquare.co/listings?city=Pretoria> [out_dir]"""
import json, os, re, urllib.request, urllib.parse, sys
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = ROOT + "/"
A = os.environ.get("DOOR_ASSETS", os.path.join(ROOT, "assets", "door")) + "/"
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "visuals", "door_proof"); os.makedirs(OUT, exist_ok=True)
LIST = open(sys.argv[1]).read()
ORIGIN = "https://trustsquare.co"
calls = []
ME = {"signed_in": False, "interest": [], "via": None, "last_app": None, "pro": False, "squire_pa": False}
SQ = {"pro": True, "tier": "pro", "included": 20, "allowance": {"used": 3, "limit": 20},
      "briefs": [{"id": 7, "kind": "buy", "category": "Collectors", "need_text": "A Krugerrand from the 1970s under R40 000, Pretoria", "rules": {"max_price": 40000, "buy_discount_pct": 10},
                  "matches": 4, "new_matches": 1, "pa": None}],
      "alerts": [{"kind": "buy", "urgency": "high", "title": "SA Krugerrand Collection · 1967–1985 matches your rule", "body": "R 32 000 · 9% under the band · Centurion"}],
      "reports": [{"period": "2026-09", "body": {"title": "Squire monthly report — Collectors — 2026-09", "matches": 4,
                   "movement": ["Median asking of matching listings: R 34 500 (first month on record)"], "reality": "2 of 4 matches meet your rule today."}}]}
cache = {}
def ext(url):
    if url not in cache:
        try: cache[url] = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read()
        except Exception: cache[url] = b""
    return cache[url]
def handler(route, request):
    u = urllib.parse.urlparse(request.url); path = u.path
    def ok(body, ct): route.fulfill(status=200, body=body, headers={"Content-Type": ct})
    if u.netloc != "trustsquare.co":
        b = ext(request.url); return ok(b, "image/jpeg") if b else route.fulfill(status=404, body="")
    if path == "/door": return ok(open(W + "door.html", "rb").read(), "text/html")
    if path == "/pa": return ok(open(W + "pa.html", "rb").read(), "text/html")
    if path == "/pa/about": return ok(open(W + "pa_about.html", "rb").read(), "text/html")
    if path.startswith("/static/door/"): return ok(open(A + path.split("/")[-1], "rb").read(), "image/jpeg")
    if path == "/door/me": return ok(json.dumps(ME), "application/json")
    if path == "/quick/me": return ok(json.dumps({"city": GEO["city"], "geo": {"city": GEO["city"]}}), "application/json")
    if path == "/listings": calls.append(("listings", request.url)); return ok(LIST, "application/json")
    if path == "/door/last": calls.append(("last", request.post_data)); return ok('{"ok":true,"stored":true}', "application/json")
    if path == "/squire/status": return ok(json.dumps(SQ), "application/json")
    if path == "/squire/brief" and request.method == "POST": calls.append(("brief", request.post_data)); return ok('{"brief_id":8}', "application/json")
    if path.startswith("/squire/brief/") and path.endswith("/shortlist"):
        L = json.loads(LIST); col = [l for l in L if l.get("category") == "Collectors"][:3]
        return ok(json.dumps({"shortlist": [{"listing_id": l["id"], "reasons": ["trust %s" % l.get("trust_score"), "matches your chip"], "listing": {"title": l["title"], "price": l["price"]}} for l in col]}), "application/json")
    if path.startswith("/static/") or path.startswith("/media/"):
        b = ext(ORIGIN + path); return ok(b, "image/jpeg") if b else route.fulfill(status=404, body="")
    # any app the door opens: a stub page that names where we landed
    calls.append(("nav", request.url)); return ok("<html><body style='background:#fff'><h1>landed: %s</h1></body></html>" % request.url, "text/html")
res = []
GEO = {"city": "Pretoria"}
def check(c, what): res.append(("PASS" if c else "FAIL", what)); print(("PASS " if c else "FAIL ") + what)
with sync_playwright() as p:
    b = p.chromium.launch()
    def page(lang="en"):
        ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True, locale=lang)
        ctx.route("**/*", handler); pg = ctx.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e))); return ctx, pg, errs
    def slide(pg, v): pg.evaluate("v=>{const s=document.getElementById('slider');s.value=v;s.dispatchEvent(new Event('input'))}", v)
    # 1 first-time visitor: collage at rest
    ctx, pg, errs = page(); pg.goto(ORIGIN + "/door"); pg.wait_for_timeout(3500)
    pg.screenshot(path=OUT + "/1_open_collage.png")
    check(pg.locator("#collage .pane img.on").count() >= 5, "opening: the collage is showing journey photographs")
    check(pg.inner_text("#tap") == "AI PA", "opening (left): the bottom button says AI PA, like the top pill (RUL-247/248)")
    # 2 slide to TrustSquare, no interest -> everything near you
    slide(pg, 3); pg.wait_for_timeout(2500); pg.screenshot(path=OUT + "/2_trustsquare_everything.png")
    n_ads = pg.locator(".ad").count(); n_pa = pg.locator(".pa").count()
    check(n_ads > 10 and n_pa > 2, "TrustSquare: local adverts (%d) with AI PA cards woven in (%d)" % (n_ads, n_pa))
    check("Everything near you" in pg.inner_text("#ibar"), "no interest known -> 'Everything near you'")
    check(not errs, "no script errors (%s)" % errs[:1]); ctx.close()
    # 3 interest from the prospect row: Collectors
    ME.update(signed_in=True, interest=["Collectors"], via="prospect", last_app="quick", pro=False)
    ctx, pg, errs = page(); pg.goto(ORIGIN + "/door"); pg.wait_for_timeout(2500)
    pg.mouse.click(195, 760); pg.wait_for_timeout(1200)
    check(("nav", ORIGIN + "/pa") in calls or pg.url.endswith("/pa") or pg.url.endswith("/pa/about"), "left: a tap on the collage opens the AI PA door (/pa)")
    pg.goto(ORIGIN + "/door"); pg.wait_for_timeout(2500)
    slide(pg, 3); pg.wait_for_timeout(2500); pg.screenshot(path=OUT + "/3_interest_collectors.png")
    cats = set(pg.eval_on_selector_all(".ad .cat", "e=>e.map(x=>x.textContent)"))
    check(cats == {"Collectors"}, "interest Collectors: only Collectors adverts (%s)" % sorted(cats))
    check("from your public adverts" in pg.inner_text("#ibar"), "the line says where the interest came from")
    # RUL-249: Pretoria has no real Collectors adverts -> Collectors examples, each saying "Your listing here", tapping opens selling
    nex = pg.locator(".ad.ex").count(); nyours = pg.locator(".ad.ex .yours").count(); nreal = pg.locator(".ad:not(.ex)").count()
    check(nex > 0 and nyours == nex and nreal == 0 and "Your listing here" in pg.inner_text(".ad.ex .yours >> nth=0"),
          "too few local Collectors: examples top up the stream, every one says 'Your listing here' (%d examples)" % nex)
    n0 = len(calls); pg.mouse.click(195, 480); pg.wait_for_timeout(1200)
    check(("nav", ORIGIN + "/quick/?src=door-example") in calls[n0:], "tapping an example opens selling in Quick, never the example")
    check(any(c[0] == "last" for c in calls[n0:]), "the tap records the last app"); ctx.close()
    # RUL-249: a city with no local adverts at all -> examples + "Be the first seller in Johannesburg"
    saved = dict(ME); ME.update(interest=[], via=None); GEO["city"] = "Johannesburg"
    ctx, pg, errs = page(); pg.goto(ORIGIN + "/door"); pg.wait_for_timeout(2000); slide(pg, 3); pg.wait_for_timeout(2000)
    pg.screenshot(path=OUT + "/3b_empty_city_invite.png")
    ncats = len(set(pg.eval_on_selector_all(".ad.ex .cat", "e=>e.map(x=>x.textContent)")))
    check("Be the first seller in Johannesburg" in pg.inner_text("#ibar") and pg.locator(".ad:not(.ex)").count() == 0 and ncats >= 3,
          "an empty city: 'Be the first seller in Johannesburg' over examples from %d categories, no real adverts from elsewhere" % ncats)
    check(not errs, "no script errors in an empty city (%s)" % errs[:1]); ctx.close()
    GEO["city"] = "Pretoria"; ME.clear(); ME.update(saved)
    # 4 Snap: the bottom button opens Snap; an advert opens that advert in TrustSquare (RUL-248)
    ctx, pg, errs = page(); pg.goto(ORIGIN + "/door"); pg.wait_for_timeout(1500); slide(pg, 1); pg.wait_for_timeout(1500)
    pg.screenshot(path=OUT + "/4_snap.png"); pg.click("#tap"); pg.wait_for_timeout(1200)
    check(("nav", ORIGIN + "/quick/?p=snap") in calls, "Snap: the bottom button opens Snap (/quick/?p=snap)"); ctx.close()
    saved = dict(ME); ME.update(interest=[], via=None)
    ctx, pg, errs = page(); pg.goto(ORIGIN + "/door"); pg.wait_for_timeout(1500); slide(pg, 1); pg.wait_for_timeout(1500)
    lid = pg.evaluate("()=>{const e=document.elementFromPoint(195,480).closest('.ad');return e?e.dataset.id:null}"); pg.mouse.click(195, 480); pg.wait_for_timeout(1200)
    check(lid and ("nav", ORIGIN + "/?listing=" + lid) in calls, "Snap: tapping a scrolling advert opens that advert in TrustSquare (/?listing=%s)" % lid); ctx.close()
    ME.clear(); ME.update(saved)
    # 4a RUL-248: local only, fresh random draw
    city_of = {str(l["id"]): (l.get("city") or "") for l in json.loads(LIST)}
    saved = dict(ME); ME.update(interest=[], via=None)
    ctx, pg, errs = page(); pg.goto(ORIGIN + "/door"); pg.wait_for_timeout(1500); slide(pg, 3); pg.wait_for_timeout(1500)
    ids = pg.eval_on_selector_all(".ad", "e=>e.map(x=>x.dataset.id)"); cities = {city_of.get(i, "?") for i in ids}
    check(ids and cities == {"Pretoria"}, "the stream is local only: every advert is listed in Pretoria (%s)" % sorted(cities))
    check(any(c[0] == "listings" and "sort=random" in c[1] for c in calls), "the stream asks for a random draw (sort=random)")
    first1 = pg.eval_on_selector_all(".ad", "e=>e.slice(0,8).map(x=>x.dataset.id).join()"); ctx.close()
    ctx, pg, errs = page(); pg.goto(ORIGIN + "/door"); pg.wait_for_timeout(1500); slide(pg, 3); pg.wait_for_timeout(1500)
    first2 = pg.eval_on_selector_all(".ad", "e=>e.slice(0,8).map(x=>x.dataset.id).join()"); ctx.close()
    check(first1 != first2, "every visit draws a new order (%s | %s)" % (first1[:30], first2[:30]))
    ME.clear(); ME.update(saved)
    # 4e DOOR-WHEEL-1: swipe the top wheel left -> next name in the centre pill, and the bottom button follows it
    ctx, pg, errs = page(); pg.goto(ORIGIN + "/door"); pg.wait_for_timeout(1500)
    wb = pg.locator("#wheel").bounding_box(); wy = wb["y"] + wb["height"] / 2; wx = wb["x"] + wb["width"] / 2
    on0 = pg.inner_text("#strip span.on")
    pg.mouse.move(wx + 60, wy); pg.mouse.down(); pg.mouse.move(wx - 20, wy, steps=6); pg.mouse.move(wx - 70, wy, steps=6); pg.mouse.up(); pg.wait_for_timeout(500)
    on1 = pg.inner_text("#strip span.on"); t1 = pg.inner_text("#tap")
    pg.mouse.move(wx + 60, wy); pg.mouse.down(); pg.mouse.move(wx - 20, wy, steps=6); pg.mouse.move(wx - 70, wy, steps=6); pg.mouse.up(); pg.wait_for_timeout(500)
    on2 = pg.inner_text("#strip span.on"); t2 = pg.inner_text("#tap"); pg.screenshot(path=OUT + "/4e_wheel_quick.png")
    sb = pg.locator("#strip span.on").bounding_box(); tb = pg.locator("#tap").bounding_box()
    centred = abs((sb["x"] + sb["width"] / 2) - (tb["x"] + tb["width"] / 2)) < 4
    check(on0 == "AI PA" and on1 == "SNAP" and t1 == "SNAP" and on2 == "QUICK" and t2 == "QUICK" and centred,
          "a swipe on the top wheel moves AI PA -> Snap -> Quick, centred over the bottom button, which follows (%s/%s/%s, centred=%s)" % (on0, on1, on2, centred))
    pg.click("#strip span[data-i='3']"); pg.wait_for_timeout(500)
    check(pg.inner_text("#strip span.on") == "TRUSTSQUARE" and pg.inner_text("#tap") == "TRUSTSQUARE", "a tap on a name in the wheel picks it")
    check(not errs, "no script errors on the wheel (%s)" % errs[:1]); ctx.close()
    # 4b DOOR-SPEED-1: a finger drag scrolls the stream and is never a tap
    ctx, pg, errs = page(); pg.goto(ORIGIN + "/door"); pg.wait_for_timeout(1500); slide(pg, 3); pg.wait_for_timeout(1500)
    n0 = len(calls); t0 = pg.eval_on_selector("#lane", "e=>e.style.transform")
    pg.mouse.move(195, 600); pg.mouse.down(); pg.mouse.move(195, 450, steps=8); pg.mouse.move(195, 300, steps=8); pg.mouse.up(); pg.wait_for_timeout(600)
    t1 = pg.eval_on_selector("#lane", "e=>e.style.transform")
    check(t0 != t1 and not any(c[0] == "nav" for c in calls[n0:]), "a finger drag scrolls the stream (%s -> %s) and opens nothing" % (t0, t1)); ctx.close()
    # 4c DOOR-TOUCH-1: a real finger (touch events) scrolls the stream on a phone and opens nothing
    ctx, pg, errs = page(); pg.goto(ORIGIN + "/door"); pg.wait_for_timeout(1500); slide(pg, 3); pg.wait_for_timeout(1500)
    n0 = len(calls); t0 = pg.eval_on_selector("#lane", "e=>e.style.transform"); cdp = ctx.new_cdp_session(pg)
    cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": 195, "y": 600}]})
    for y in range(590, 290, -20): cdp.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": 195, "y": y}]})
    cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []}); pg.wait_for_timeout(600)
    t1 = pg.eval_on_selector("#lane", "e=>e.style.transform")
    def ty(t): return float(t.split("(")[1].split("px")[0]) if t and "(" in t else 0.0
    check(ty(t0) - ty(t1) > 200 and not any(c[0] == "nav" for c in calls[n0:]), "a finger on a phone scrolls the stream (%s -> %s) and opens nothing" % (t0, t1)); ctx.close()
    # 4d DOOR-SYNC-1: play with the top, then press the bottom button -- it opens what the top shows, even with an AI PA card under it
    ctx, pg, errs = page(); pg.goto(ORIGIN + "/door"); pg.wait_for_timeout(1500)
    for v in (3, 1, 2, 3, 2): slide(pg, v); pg.wait_for_timeout(250)
    box = pg.locator("#tap").bounding_box(); cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    n0 = len(calls); pg.mouse.click(cx, cy); pg.wait_for_timeout(1200)
    navs = [c[1] for c in calls[n0:] if c[0] == "nav"]
    check(navs == [ORIGIN + "/quick/"], "the bottom button opens what the top shows (Quick), never the card under it: %s" % navs); ctx.close()
    # 4f DOOR-PICK-1 (RUL-250): the hidden side swipe -> her categories; the hint tab; one tap picks; remembered; All clears
    saved = dict(ME); ME.update(interest=[], via=None)
    ctx, pg, errs = page(); pg.goto(ORIGIN + "/door"); pg.wait_for_timeout(1500); slide(pg, 3); pg.wait_for_timeout(1900)
    nudged = pg.eval_on_selector("#lane", "e=>e.classList.contains('nudge')") or pg.eval_on_selector("#cattab", "e=>e.classList.contains('pulse')")
    check(pg.locator("#cattab").is_visible() and "Categories" in pg.inner_text("#cattab") and nudged, "the hint: a 'Categories' tab on the right edge, and a one-time nudge")
    n0 = len(calls)
    pg.mouse.move(330, 500); pg.mouse.down(); pg.mouse.move(250, 505, steps=6); pg.mouse.move(150, 508, steps=6); pg.mouse.up(); pg.wait_for_timeout(700)
    tiles = pg.locator("#pl .ct").count()
    check(pg.eval_on_selector("#picker", "e=>e.classList.contains('open')") and tiles == 8 and not any(c[0] == "nav" for c in calls[n0:]),
          "a right-to-left swipe on the adverts opens the categories (%d tiles incl. All), opens nothing else" % tiles)
    pg.wait_for_timeout(1500); pg.screenshot(path=OUT + "/4f_categories.png")
    pg.click("#pl .ct[data-cat='Cars'] b"); pg.wait_for_timeout(900)
    cats = set(pg.eval_on_selector_all(".ad .cat", "e=>e.map(x=>x.textContent)"))
    check(not pg.eval_on_selector("#picker", "e=>e.classList.contains('open')") and cats == {"Cars"} and "Your choice: Cars" in pg.inner_text("#ibar")
          and any(c[0] == "last" and '"choice":"Cars"' in (c[1] or "") for c in calls[n0:]),
          "one tap on Cars: back to the adverts, only Cars (%s), 'Your choice: Cars', saved" % sorted(cats))
    pg.screenshot(path=OUT + "/4g_choice_cars.png")
    pg.reload(); pg.wait_for_timeout(1500); slide(pg, 3); pg.wait_for_timeout(1200)
    check("Your choice: Cars" in pg.inner_text("#ibar"), "the choice is remembered on the next visit")
    pg.click("#cattab"); pg.wait_for_timeout(600)
    chip = pg.locator("#pl .ct[data-cat='Property'] .subs span").first
    sub = chip.inner_text() if chip.count() else ""
    if sub: chip.click(); pg.wait_for_timeout(900)
    subs_ok = sub and pg.eval_on_selector_all(".ad .cat", "e=>e.every(x=>x.textContent==='Property')") and ("Property · " + sub) in pg.inner_text("#ibar")
    check(bool(subs_ok), "a sub-category chip narrows it (Property · %s)" % sub)
    pg.click("#cattab"); pg.wait_for_timeout(600); pg.click("#pl .ct.all"); pg.wait_for_timeout(900)
    check("Your choice" not in pg.inner_text("#ibar") and len(set(pg.eval_on_selector_all(".ad .cat", "e=>e.map(x=>x.textContent)"))) > 1, "All clears her choice")
    check(not errs, "no script errors in the categories (%s)" % errs[:1]); ctx.close()
    ME.clear(); ME.update(saved)
    # 5 AI PA card -> /pa (Pro) -> the AI PA page
    ME.update(pro=True)
    ctx, pg, errs = page(); pg.goto(ORIGIN + "/door"); pg.wait_for_timeout(1500); slide(pg, 2); pg.wait_for_timeout(1500)
    pg.locator(".pa").first.click(); pg.wait_for_timeout(2500)
    check(pg.url.endswith("/pa"), "an AI PA card opens the AI PA door (/pa)")
    pg.screenshot(path=OUT + "/5_ai_pa_page.png", full_page=True)
    check("Krugerrand" in pg.inner_text("body") and "monthly report" in pg.inner_text("body").lower(), "AI PA page: briefs, alerts and the monthly report from /squire/status")
    pg.click("[data-sl='7']"); pg.wait_for_timeout(800); check(pg.locator("#sl7 a").count() >= 1, "See matches lists the shortlist")
    pg.fill("#need", "A 4-bed with a pool in Waterkloof under R4.5m"); pg.select_option("#cat", "Property"); pg.fill("#maxp", "4500000"); pg.fill("#pct", "5")
    pg.click("button[type=submit]"); pg.wait_for_timeout(1200)
    bb = [json.loads(c[1]) for c in calls if c[0] == "brief"]
    check(bb and bb[-1]["kind"] == "buy" and bb[-1]["rules"] == {"max_price": 4500000, "buy_discount_pct": 5} and bb[-1]["category"] == "Property",
          "New brief posts kind, category and rules to /squire/brief")
    pg.screenshot(path=OUT + "/6_ai_pa_brief_saved.png"); check(not errs, "no script errors on the AI PA page (%s)" % errs[:1]); ctx.close()
    # 6 explainer
    ctx, pg, errs = page(); pg.goto(ORIGIN + "/pa/about"); pg.wait_for_timeout(2500); pg.screenshot(path=OUT + "/7_ai_pa_explainer.png", full_page=True)
    t = pg.inner_text("body"); check("Included in Pro" in t and "$20" in t and pg.locator("a#go").get_attribute("href") == "/?go=plans", "explainer: what it does, $20 / R360 Included in Pro, Go Pro")
    ctx.close()
    # 7 Afrikaans
    ME.update(interest=[], pro=False)
    ctx, pg, errs = page("af-ZA"); pg.goto(ORIGIN + "/door"); pg.wait_for_timeout(1500); slide(pg, 2); pg.wait_for_timeout(1500)
    pg.screenshot(path=OUT + "/8_afrikaans.png"); check("Tik om Quick oop te maak" in (pg.get_attribute("#tap", "aria-label") or ""), "the door speaks Afrikaans for an Afrikaans phone"); ctx.close()
    b.close()
print("RENDER PROOF: %d/%d PASS" % (sum(1 for r in res if r[0] == "PASS"), len(res)))
