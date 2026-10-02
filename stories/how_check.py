#!/usr/bin/env python3
"""
how_check.py -- HOW-CHECK-1 (1 Oct 2026): the cloud check of Quick's How guides.

David, 1 Oct 2026: "the quick app now has great 'How it works' card-flow-examples, linked to the actual quick stage. What
cloud check and fix can you perform on the two apps and their interface to improve the ease and flow and also to check the
unique functions of each 'How'?"

It walks Quick on trustsquare.co as a phone does (390x844, South Africa), with the tester cookie so How shows, once for
every guide walked in Quick and once for a listing each guide says it serves (its own step 2: "Car, bakkie, SUV or bike").
On every screen it presses How and reads the card the guide opened at. It FAILS when
  - How opens no guide, or the wrong one, for a listing a guide serves (a house TO LET must not get the FOR SALE guide);
  - the card is not the one for her screen -- or, for a screen the guide has no card for, the last card she passed;
  - a buyer in Find is shown a seller's card instead of the buyer's half;
  - a guide walked in TrustSquare's Sell (no Quick card) is opened from Quick.
And it checks each guide's own promise -- the unique function of each How -- against the live site:
  - a gate note names a passed step marked gate, so the banner shows (the electrician's licence gate never did);
  - a paid report's price on the guide ([[Get the report · 3T]]) is the live price (/ai/functions);
  - every passed step's screen loads, and the live guide is the repo's.
A screen the guide has no card of its own for is a WARN: the guide still opens at the last card she passed, and the next
walk of that flow should give it its own.

  python3 stories/how_check.py                  # the live site, every guide (about 8 minutes)
  python3 stories/how_check.py --candidate      # this checkout's quick.html + stories/ served over the live site: prove a
                                                #   change BEFORE committing it with [ship]
  python3 stories/how_check.py nanny cars_bakkie   # only these guides
  python3 stories/how_check.py --static         # no browser: gate notes, report prices, screens, live = repo
  ... --out <file>                              # write the report there instead of docs/HOW_CHECK_<date>[_candidate].md

Needs the cloud QA key (python3 stories/cloud_kit.py ping) and Playwright (pip install playwright; the browser is the
preinstalled /opt/pw-browsers/chromium -- never 'playwright install'). The browser must trust the session's proxy CA:
this script adds it to the NSS store when certutil is present (apt-get install -y libnss3-tools).
Writes docs/HOW_CHECK_<yyyy-mm-dd>.md. Exit 0 = no FAIL.
"""
import asyncio, datetime, json, os, re, ssl, subprocess, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import cloud_kit  # noqa: E402

BASE = cloud_kit.BASE
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
      "Version/17.5 Mobile/15E148 Safari/604.1")
CHROME = os.environ.get("TS_CHROME", "/opt/pw-browsers/chromium")
REPORT_FN = {"property": "property_dossier", "cars": "car_dossier", "collectors": "collectables_advert"}   # door -> /ai function
PRICE = {"property": "1850000", "cars": "185000", "collectors": "72000", "adventures": "950", "localmarket": "85"}
FAIL, WARN, OK = "FAIL", "WARN", "ok"


def slug(t):
    return re.sub(r"^_+|_+$", "", re.sub(r"[^a-z0-9]+", "_", str(t).lower()))


def load_guides():
    out = {}
    for fn in sorted(os.listdir(HERE)):
        if fn.endswith(".json") and fn != "gallery.json":
            out[fn[:-5]] = json.load(open(os.path.join(HERE, fn), encoding="utf-8"))
    return out


def passed(g):
    return [s for s in g.get("steps", []) if s.get("pass")]


def expected_card(g, at, seen, side=""):
    """The card help.html must open at (HOW-PLACE-1): the buyer's half for Find; else her screen's card; else the
    card of the last screen she passed; else step 1."""
    S = passed(g)
    if side == "find":
        for s in S:
            if s.get("who") == "customer":
                return s["n"]
    for k in [at] + list(reversed([x for x in seen.split(",") if x])):
        for s in S:
            if k in (s.get("quick") or []):
                return s["n"]
    return S[0]["n"] if S else None


def _get(path):
    ca = os.environ.get("SSL_CERT_FILE") or "/root/.ccr/ca-bundle.crt"
    ctx = ssl.create_default_context(cafile=ca) if os.path.isfile(ca) else ssl.create_default_context()
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "ts-cloud-walk"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:  # network
        return str(e)[:80], b""


# ── the guides' own promises: the unique function of each How ────────────────────────────────────────────────────
def static_checks(guides, compare_live=True):
    rows = []
    fns = {}
    st, body = _get("/ai/functions")
    if st == 200:
        fns = {f.get("id"): f for f in json.loads(body)}
    else:
        rows.append((WARN, "-", "/ai/functions answered %s -- report prices not compared" % st))
    for t, g in guides.items():
        S = passed(g)
        gates = [s for s in S if s.get("gate")]
        if g.get("gate_note"):
            if not gates:
                rows.append((FAIL, t, "the gate note promises a gate but no passed step is marked gate -- its banner never shows"))
            else:
                n = str(gates[0]["n"])
                wrong = [lg for lg, txt in g["gate_note"].items() if n not in re.findall(r"\d+", txt)]
                rows.append((FAIL, t, "the gate note does not name step %s (%s)" % (n, ", ".join(wrong))) if wrong
                            else (OK, t, "gate banner: step %s, '%s'" % (n, S[[x["n"] for x in S].index(gates[0]["n"])]["en"][0])))
        door = t.split("_")[0]
        for s in S:
            for m in re.finditer(r"\[\[Get the report · (\d+)T\]\]", " ".join(s["en"])):
                f = fns.get(REPORT_FN.get(door, ""))
                if not fns:
                    continue
                if not f:
                    rows.append((WARN, t, "step %s quotes a %sT report but no live report is known for the %s door" % (s["n"], m.group(1), door)))
                elif int(m.group(1)) != int(f.get("price_t") or 0):
                    rows.append((FAIL, t, "step %s says %sT; the live %s costs %sT" % (s["n"], m.group(1), f.get("name"), f.get("price_t"))))
                else:
                    rows.append((OK, t, "step %s: %s, %sT = live" % (s["n"], f.get("name"), f.get("price_t"))))
        if compare_live:
            st, body = _get("/help/data/%s.json" % t)
            if st != 200 or json.loads(body) != g:
                rows.append((FAIL, t, "the live guide is not the repo's (%s)" % st))
        bad = [s["img"] for s in S if _get("/help/img/%s/%s.jpg" % (t, s["img"]))[0] != 200]
        rows.append((FAIL, t, "screens not loading: %s" % ", ".join(bad)) if bad
                    else (OK, t, "%d screens load" % len(S)))
    return rows


# ── the walk ─────────────────────────────────────────────────────────────────────────────────────────────────────
STATE_JS = """() => { let f=null; try{ f=flow(); }catch(e){}
  const seen=['door']; try{ if(mode){ const n=Math.min(step,f.steps.length); for(let i=0;i<n;i++) if(f.steps[i]&&f.steps[i].key) seen.push(f.steps[i].key); } }catch(e){}
  return {at: qHelpAt(), type: qHelpType(), mode: (typeof mode!=='undefined')?mode:null, step: step, cat: cat().key,
   q: (document.querySelector('#screen .q')||{}).innerText||'', seen: seen.join(','),
   week: !!document.getElementById('wk'), multi: !!document.getElementById('qareas-next')}; }"""
CARD_JS = """() => { const n=document.querySelector('#now .k span'), h=document.querySelector('#now h2');
  return {k: n?n.innerText:'', h2: h?h.innerText:'', path: location.pathname, list: !!document.getElementById('grid'),
          first: (document.querySelector('#grid a')||{}).getAttribute ? document.querySelector('#grid a').getAttribute('href') : ''}; }"""


def _browser_trust():
    """Chromium reads the NSS store, not the CA bundle: the session's proxy CA must be in it or every page fails."""
    ca = "/root/.ccr/agent-proxy-ca.crt"
    db = "sql:" + os.path.expanduser("~/.pki/nssdb")
    if not os.path.isfile(ca):
        return
    try:
        if "ccr-agent-proxy" in subprocess.run(["certutil", "-L", "-d", db], capture_output=True, text=True).stdout:
            return
        os.makedirs(os.path.expanduser("~/.pki/nssdb"), exist_ok=True)
        subprocess.run(["certutil", "-A", "-d", db, "-n", "ccr-agent-proxy", "-t", "C,,", "-i", ca], check=True)
    except FileNotFoundError:
        sys.exit("certutil is missing: apt-get install -y libnss3-tools (the browser must trust the proxy CA)")


def plans(guides, idx, roles):
    """One walk per guide walked in Quick, one per listing it serves, one Find walk per door, and the stay that must not
    open a Sell guide. Each: (name, door, side, choose{screen-key: tile text}, expected guide type or '')."""
    out = []
    role = {r["k"]: r for r in roles}
    exact = {s["type"] for s in idx}
    doors = ("property", "cars", "tutors", "collectors", "adventures", "localmarket")
    for s in idx:   # an index from before HOW-NEAREST-1 has no door / quick / serves: take them from the repo's guides
        g = guides.get(s["type"], {})
        s.setdefault("door", s["type"].split("_")[0] if s["type"].split("_")[0] in doors else "services")
        s.setdefault("quick", any(x.get("quick") for x in passed(g)))
        for k in ("serves", "deal"):
            if k not in s and g.get(k):
                s[k] = g[k]
    for s in idx:
        t, door, deal = s["type"], s["door"], s.get("deal")
        dl = {"sale": "To sell", "let": "To let"}.get(deal)
        if not s.get("quick"):
            continue
        if door == "services":
            r = role.get(t)
            if r:
                out.append((t, "services", "sell", {"group": r["g"], "what": r["l"]}, t))
            for k in s.get("serves", []):
                if role.get(k):
                    out.append(("%s (serves %s)" % (t, k), "services", "sell", {"group": role[k]["g"], "what": role[k]["l"]}, t))
                    break
        else:
            out.append((t, door, "sell", dict({"what~": t[len(door) + 1:]}, **({"deal": dl} if dl else {})), t))
            for o in idx:   # the other deal's own listing: a house TO LET must open the TO LET guide, not House FOR SALE
                if deal and o["door"] == door and o.get("deal") and o["deal"] != deal:
                    out.append(("%s (a %s %s)" % (t, o["type"][len(door) + 1:], dl.lower()), door, "sell",
                                {"what~": o["type"][len(door) + 1:], "deal": dl}, t))
            if any(p.endswith("*") for p in s.get("serves", [])):
                out.append(("%s (serves another %s)" % (t, door), door, "sell",
                            dict({"what!": sorted(x for x in exact if x.startswith(door + "_"))}, **({"deal": dl} if dl else {})), t))
    for door in sorted({s["door"] for s in idx if s.get("quick")}):
        out.append(("Find in %s" % door, door, "find", {}, "*"))
    # STAY-WHERE-1 made a Quick stay path on 1 Oct; the guest-house guide was walked in TrustSquare's Sell
    out.append(("Quick stay (B&B / guest house)", "adventures", "sell", {"what": "Place to stay", "kind": "Guest house"}, ""))
    return out


async def read_how(pg):
    await pg.click("#qhb")
    card = {}
    src = await pg.evaluate("() => (document.getElementById('qhov')||document.body).getAttribute('data-src') || ''")
    want = src.split("?")[0].split("#")[0].rstrip("/") or "/help"
    for _ in range(48):
        await pg.wait_for_timeout(250)
        el = await pg.query_selector("#qhov iframe")
        fr = await el.content_frame() if el else None
        if not fr:
            continue
        try:
            card = await fr.evaluate(CARD_JS)
        except Exception:
            continue
        if (card.get("path") or "").rstrip("/") != want:   # still the page from the previous press
            continue
        if card.get("k") or (card.get("list") and card.get("first")):
            break
    card["src"] = src
    await pg.click("#qhb")
    await pg.wait_for_timeout(150)
    return card


async def walk(browser, cookies, plan, guides, candidate):
    name, door, side, choose, want = plan
    # service_workers=block: the site's worker (assets/service-worker.js, caches nothing) re-fetches every navigation --
    # the guide's iframe too -- from the network, which would walk past --candidate's routing to the live guide page
    ctx = await browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, user_agent=UA,
                                    timezone_id="Africa/Johannesburg", locale="en-ZA", service_workers="block")
    await ctx.add_cookies(cookies)
    if candidate:
        await serve_checkout(ctx)
    pg = await ctx.new_page()
    errs, rows = [], []
    pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
    await pg.goto(BASE + "/quick/?cc=ZA", wait_until="networkidle")
    await pg.wait_for_selector("#qhb", timeout=20000)
    for _ in range(12):
        if await pg.evaluate("() => cat().key") == door:
            break
        await pg.click("#next")
        await pg.wait_for_timeout(200)
    await pg.click("#bFind" if side == "find" else "#bSell")
    await pg.wait_for_timeout(450)
    last = None
    for _ in range(14):
        st = await pg.evaluate(STATE_JS)
        if st["at"] in ("draft", "saved", "buzz") and rows and rows[-1][1] == st["at"]:
            break
        if (st["at"], st["step"], st["q"]) == last:
            rows.append((FAIL, st["at"], "%s %r" % (st["at"], st["q"][:34]), "the walk could not get past this screen"))
            break
        last = (st["at"], st["step"], st["q"])
        card = await read_how(pg)
        rows.append(judge(name, st, card, want, guides, side))
        if st["at"] in ("draft", "saved", "buzz") or st["mode"] is None:
            break
        await advance(pg, st, choose)
    await ctx.close()
    if errs:
        rows.append((FAIL, "-", "-", "page errors: " + " | ".join(errs[:3])))
    return name, rows


def judge(name, st, card, want, guides, side):
    at, got = st["at"], ""
    m = re.match(r"^/help/([a-z0-9_]+)$", card.get("path") or "")
    got = m.group(1) if m else ""
    step = re.search(r"(\d+)\s+(?:OF|of|/)\s+(\d+)", card.get("k") or "")
    shown = int(step.group(1)) if step else None
    where = "%s %r" % (at, st["q"][:34])
    if at in ("door", "group") or (at == "what" and not st["type"]):
        return (OK if not got else WARN, at, where, "the list" if not got else "guide %s" % got)
    if want == "":
        return (OK, at, where, "the list (no guide walked in Quick)") if not got else \
               (FAIL, at, where, "opened %s -- a guide walked in TrustSquare's Sell, at step %s" % (got, shown))
    if want == "*":
        want = st["type"]
        if not want:
            return (WARN, at, where, "no guide for this listing; the list opened")
    if at == "deal" and got and got.split("_")[0] == want.split("_")[0]:   # not chosen yet: either deal's guide
        return (OK, at, where, "%s (sale or let is not chosen yet)" % got)
    if got != want:
        return (FAIL, at, where, "opened %s, not %s" % (got or "the list", want))
    g = guides[want]
    exp = expected_card(g, at, st["seen"], side)
    own = any(at in (s.get("quick") or []) for s in passed(g))
    if shown != exp:
        return (FAIL, at, where, "%s opened step %s, not step %s" % (want, shown, exp))
    if side == "find":
        return (OK, at, where, "%s step %s (the buyer's half)" % (want, shown))
    return (OK if own else WARN, at, where, "%s step %s%s" % (want, shown, "" if own else " -- no card of its own; the last card she passed"))


async def advance(pg, st, choose):
    if await pg.query_selector("#rtgo"):
        await pg.fill("#rta", PRICE.get(st["cat"], "450"))
        if await pg.is_visible("#rth"):
            await pg.fill("#rth", "450")
        await pg.wait_for_timeout(150)
        await pg.click("#rtgo")
        await pg.wait_for_timeout(400)
        return
    inp = await pg.query_selector("#screen input[type=text]:visible, #screen input[type=number]:visible, #screen input[type=tel]:visible")
    if inp and not await pg.query_selector("#screen [data-i], #screen [data-c]"):
        await inp.fill(PRICE.get(st["cat"], "450"))
        await pg.wait_for_timeout(150)
        b = await pg.query_selector("#screen button:not([disabled]):has-text('Next')")
        if b:
            await b.click(); await pg.wait_for_timeout(400)
        return
    city = await pg.query_selector_all("#screen [data-c]")
    if city:
        for n in city:
            if (await n.inner_text()).strip() == "Pretoria":
                await n.click(); break
        else:
            await city[0].click()
        await pg.wait_for_timeout(400)
        return
    if st["week"]:
        await pg.click("#wk button >> nth=0"); await pg.click("#wkgo"); await pg.wait_for_timeout(400); return
    if st["multi"]:
        await pg.click("#screen [data-i] >> nth=0"); await pg.click("#qareas-next"); await pg.wait_for_timeout(400); return
    nodes = await pg.query_selector_all("#screen [data-i]")
    texts = [(await n.inner_text()).strip() for n in nodes]
    pick = 0
    if st["at"] in choose and choose[st["at"]] in texts:
        pick = texts.index(choose[st["at"]])
    elif st["at"] == "what" and "what~" in choose:
        pick = next((i for i, x in enumerate(texts) if slug(x) == choose["what~"]), 0)
    elif st["at"] == "what" and "what!" in choose:   # a sibling no guide is written for
        pick = next((i for i, x in enumerate(texts) if "%s_%s" % (st["cat"], slug(x)) not in choose["what!"]), 0)
    if nodes:
        before = await pg.evaluate("() => [step, picks.length]")
        await nodes[pick].click()
        await pg.wait_for_timeout(400)
        if await pg.evaluate("() => [step, picks.length]") == before:
            b = await pg.query_selector("#screen .foot button:not([disabled])")
            if b:
                await b.click(); await pg.wait_for_timeout(400)


async def serve_checkout(ctx):
    """--candidate: answer Quick and the guides from this checkout; everything else (APIs, screens) stays live."""
    def body(p):
        return open(os.path.join(ROOT, p), "rb").read()

    async def route(r):
        u = r.request.url.split("#")[0]
        path = re.sub(r"^https?://[^/]+", "", u).split("?")[0]
        ct, data = "text/html; charset=utf-8", None
        if path in ("/quick/", "/quick"):
            data = body("quick.html")
        elif path in ("/help/", "/help"):
            data = body("stories/index.html")
        elif path == "/help/data/index.json":
            data, ct = body("stories/gallery.json"), "application/json"
        elif re.match(r"^/help/data/[a-z0-9_]+\.json$", path):
            data, ct = body("stories/" + path.rsplit("/", 1)[1]), "application/json"
        elif re.match(r"^/help/[a-z0-9_]+/?$", path):
            data = body("stories/help.html")
        if data is None:
            await r.continue_()
        else:
            await r.fulfill(status=200, body=data, headers={"Content-Type": ct, "Cache-Control": "no-store"})
    await ctx.route(re.compile(r"^https://trustsquare\.co/(quick|help)(/.*)?(\?.*)?$"), route)


async def run_walks(guides, only, candidate):
    from playwright.async_api import async_playwright
    _browser_trust()
    raw = cloud_kit.signin_cookies("qa-howcheck1001", "Howcheck", review=True)
    tester = [c for c in raw if c["name"] == "ts_review"]   # the tester cookie only: How shows, Quick stays a stranger's
    if candidate:
        idx = json.load(open(os.path.join(HERE, "gallery.json"), encoding="utf-8"))["stories"]
    else:
        idx = json.loads(_get("/help/data/index.json")[1])["stories"]
    results = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME if os.path.exists(CHROME) else None)
        ctx = await b.new_context()
        pg = await ctx.new_page()
        await pg.goto(BASE + "/quick/?cc=ZA", wait_until="domcontentloaded")
        roles = await pg.evaluate("() => SVC_ROLES.map(r => ({k: r.k, l: r.l, g: r.g}))")
        await ctx.close()
        for plan in plans(guides, idx, roles):
            if only and not any(o in plan[0] for o in only):
                continue
            try:
                results.append(await walk(b, tester, plan, guides, candidate))
            except Exception as e:
                results.append((plan[0], [(FAIL, "-", "-", "the walk broke: %s" % str(e)[:200])]))
            print("%-44s %s" % (results[-1][0], " ".join(r[0] for r in results[-1][1])), flush=True)
        await b.close()
    return results


def report(static_rows, walks, candidate, out=None):
    day = datetime.date.today().isoformat()
    n_fail = sum(r[0] == FAIL for r in static_rows) + sum(r[0] == FAIL for _, rows in walks for r in rows)
    n_warn = sum(r[0] == WARN for r in static_rows) + sum(r[0] == WARN for _, rows in walks for r in rows)
    L = ["# How check, %s%s" % (day, " (candidate: this checkout over the live site)" if candidate else " (live site)"),
         "", "*Written by `stories/how_check.py` (HOW-CHECK-1). %d FAIL, %d WARN.*" % (n_fail, n_warn), "",
         "## Each guide's own promise", "", "| | Guide | Check |", "|---|---|---|"]
    L += ["| %s | %s | %s |" % r for r in static_rows]
    L += ["", "## Quick's How, screen by screen", ""]
    for name, rows in walks:
        L += ["### %s" % name, "", "| | Screen | How opened |", "|---|---|---|"]
        L += ["| %s | %s | %s |" % (r[0], r[2].replace("|", "/"), r[3]) for r in rows]
        L.append("")
    p = out or os.path.join(ROOT, "docs", "HOW_CHECK_%s%s.md" % (day, "_candidate" if candidate else ""))
    open(p, "w", encoding="utf-8").write("\n".join(L) + "\n")
    return p, n_fail, n_warn


def main():
    a = sys.argv[1:]
    static_only, candidate = "--static" in a, "--candidate" in a
    out = a[a.index("--out") + 1] if "--out" in a else None
    only = [x for x in a if not x.startswith("--") and x != out]
    guides = load_guides()
    if only:
        guides_s = {t: g for t, g in guides.items() if any(o in t for o in only)}
    else:
        guides_s = guides
    rows = static_checks(guides_s, compare_live=not candidate)
    walks = [] if static_only else asyncio.run(run_walks(guides, only, candidate))
    p, nf, nw = report(rows, walks, candidate, out)
    print("%d FAIL, %d WARN -> %s" % (nf, nw, os.path.relpath(p, ROOT)))
    sys.exit(1 if nf else 0)


if __name__ == "__main__":
    main()
