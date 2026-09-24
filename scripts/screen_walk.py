#!/usr/bin/env python3
"""screen_walk.py -- SCREEN-WALK-1 (24 Sep 2026): look at the live app the way a person does,
in every language, and say so when the screens disagree.

WHY IT EXISTS. On 24 Sep David found, with his own eyes, that every home tile read
"0 advertensies" in Afrikaans over 58 loaded listings. Nothing in the machinery could have
seen it: the regression ledger guards faults we have ALREADY named (it looks backward),
the code checks read source text, and the one browser harness on disk (smoke_harness/)
runs only when a session remembers it, in English. A change that is correct where it was
made and wrong in a setting nobody looked at -- another language, another country -- is
the commonest fault of building on a live app, and a human was the only detector.

WHAT IT DOES. A real headless browser opens the live app once per language (the five
South African languages with checked dictionaries) and reads, off the SCREEN:
  * the six home category tiles' numbers,
  * how many Featured cards show,
  * how many cards each category's Browse screen shows,
  * any JavaScript error the page threw.
English is the reference. Every other language must show the SAME numbers -- a translation
changes words, never quantities. English itself must not read all-zero while listings are
loaded. A language whose words never got painted is NOT MEASURED, never a pass.

    python3 scripts/screen_walk.py            # walk, write the witness, exit 0/1/2
    python3 scripts/screen_walk.py --install  # (re)build the browser toolkit if missing

Exit 0 = every language agrees with English. 1 = a mismatch or a page error (the witness
names it). 2 = NOT MEASURED (no browser here, gate closed, site not answering).

THE TOOLKIT lives OUTSIDE the repo at Projects/.tools/screen_walk (python package, headless
Chromium shell, one missing system library) so a cold sandbox needs no download at all and
repo-walking tools never trip over 400 MB of binaries. --install rebuilds whatever piece is
missing; each piece fits inside one ~180 s sandbox command on its own.

WITNESS: ledger_runs/screen_walk_status.json (gitignored). Ledger RG-0456 reads it.
Producer: scripts/maintenance_agent.py _screen_walk_lane(), every daily loop run.
"""
import json, os, re, subprocess, sys, time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PROJECTS = os.path.dirname(REPO)
KIT = os.path.join(PROJECTS, ".tools", "screen_walk")
WITNESS = os.path.join(REPO, "ledger_runs", "screen_walk_status.json")
BASE = os.environ.get("MS_BEA_URL", "https://trustsquare.co").rstrip("/")
LANGS = ["en", "af", "zu", "xh", "nso"]
BROWSE_CATS = ["Property", "Tutors", "Services", "Collectors", "Cars"]
# --serve-ms-js=PATH: PROOF MODE ONLY. Serves that file in place of the live ms.js so the walk can
# be shown to FAIL on a known-bad build (e.g. the pre-I18N-KEY-1 file). Never writes the witness.
SERVE_MSJS = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--serve-ms-js=")), "")


def say(m):
    print("[screen-walk] " + m, flush=True)


def _kit_env():
    py = os.path.join(KIT, "py")
    if os.path.isdir(py) and py not in sys.path:
        sys.path.insert(0, py)
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(KIT, "browsers")
    libs = os.path.join(KIT, "libs")
    os.environ["LD_LIBRARY_PATH"] = libs + (":" + os.environ["LD_LIBRARY_PATH"]
                                           if os.environ.get("LD_LIBRARY_PATH") else "")


def install():
    """Idempotent. Each missing piece is fetched on its own; re-run until it says complete."""
    if not sys.platform.startswith("linux"):
        say("install: Linux sandbox only -- nothing to do here"); return 2
    os.makedirs(KIT, exist_ok=True)
    py = os.path.join(KIT, "py")
    if not os.path.isdir(os.path.join(py, "playwright")):
        say("install: python package -> %s (~35 s)" % py)
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages",
                            "--target", py, "playwright"], capture_output=True, text=True, timeout=170)
        if r.returncode:
            say("install: pip FAILED: " + (r.stderr or r.stdout).strip()[-200:]); return 1
        return 0   # one piece per call keeps each call inside the sandbox command cap
    _kit_env()
    shells = [d for d in os.listdir(os.environ["PLAYWRIGHT_BROWSERS_PATH"])
              if d.startswith("chromium_headless_shell")] if os.path.isdir(os.environ["PLAYWRIGHT_BROWSERS_PATH"]) else []
    if not shells:
        say("install: headless Chromium shell (~75 s)")
        env = dict(os.environ, PYTHONPATH=py)
        r = subprocess.run([sys.executable, "-s", "-m", "playwright", "install", "--only-shell", "chromium"],
                           env=env, capture_output=True, text=True, timeout=170)
        if r.returncode:
            say("install: browser FAILED: " + (r.stderr or r.stdout).strip()[-200:]); return 1
        return 0
    libs = os.path.join(KIT, "libs")
    if not os.path.exists(os.path.join(libs, "libXdamage.so.1")):
        say("install: libXdamage (the one system library the sandbox lacks)")
        os.makedirs(libs, exist_ok=True)
        tmp = os.path.join("/tmp", "sw_deb")
        os.makedirs(tmp, exist_ok=True)
        subprocess.run(["apt-get", "download", "libxdamage1"], cwd=tmp, capture_output=True, timeout=90)
        debs = [f for f in os.listdir(tmp) if f.endswith(".deb")]
        if not debs:
            say("install: could not download libxdamage1"); return 1
        subprocess.run(["dpkg-deb", "-x", os.path.join(tmp, debs[0]), os.path.join(tmp, "x")], timeout=60)
        for root, _d, files in os.walk(os.path.join(tmp, "x")):
            for f in files:
                if f.startswith("libXdamage.so"):
                    subprocess.run(["cp", "-P", os.path.join(root, f), libs])
    say("install: complete -- toolkit at %s" % KIT)
    return 0


def _cookie():
    os.environ.setdefault("MS_BEA_URL", BASE)
    sys.path.insert(0, HERE)
    argv, sys.argv = sys.argv, ["screen_walk"]
    try:
        import maintenance_agent as m          # GATE-CACHE-1: shares the one on-disk credential
        return m._review_cookie() or ""
    finally:
        sys.argv = argv


# The instrument reads the English under the paint with ITS OWN walk -- never the app's msEnText --
# so a broken helper in the app cannot also blind the check that is meant to catch it.
READ_JS = r"""() => {
  const en = el => { if (!el) return ''; let o = ''; const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    let n; while ((n = w.nextNode())) o += (n.__en !== undefined && n.nodeValue === n.__tr) ? n.__en : n.nodeValue;
    return o.trim(); };
  const tiles = {}; let painted = 0;
  document.querySelectorAll('#home-cat-grid .cat-tile').forEach(t => {
    if (t.id === 'lm-home-tile') return;
    const nm = t.querySelector('.cat-name'), ct = t.querySelector('.cat-count');
    const key = en(nm); const shown = nm ? nm.textContent.trim() : '';
    if (shown && shown !== key) painted++;
    const m = ct ? (ct.textContent.match(/\d+/) || [null])[0] : null;
    tiles[key] = m === null ? null : parseInt(m, 10);
  });
  return { build: (document.querySelector('script[src*="ms.js"]') || {}).src || '',
           city: (typeof activeCity !== 'undefined' && activeCity) ? activeCity.name : null,
           live: (typeof LISTINGS !== 'undefined') ? LISTINGS.filter(l => l.isLive).length : null,
           lang: document.documentElement.lang || '', tiles, painted,
           featured: document.querySelectorAll('#home-featured .hcard').length };
}"""

BROWSE_JS = r"""(cats) => {
  const out = {};
  for (const c of cats) {
    try { filterBrowse(c);
          out[c] = document.querySelectorAll('#listing-grid [onclick*="openDetail"]').length; }
    catch (e) { out[c] = 'ERR ' + String(e.message || e).slice(0, 80); }
  }
  try { goTo('home'); } catch (e) {}
  return out;
}"""


def _ready(snap, lang):
    if not snap or not snap.get("live"):
        return False
    if not snap["tiles"] or any(v is None for v in snap["tiles"].values()):
        return False
    return lang == "en" or snap.get("painted", 0) > 0


def walk():
    if not sys.platform.startswith("linux"):
        return _write("NOT_MEASURED", reason="not a Linux sandbox -- the walk runs in the Cowork sandbox")
    _kit_env()
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        return _write("NOT_MEASURED", reason="browser toolkit missing (%s) -- run screen_walk.py --install"
                      % type(e).__name__)
    cookie = _cookie()
    if not cookie:
        return _write("NOT_MEASURED", reason="no review credential -- the gate would show a login page")
    name, val = cookie.split("=", 1)
    res = {}
    t0 = time.time()
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(headless=True, args=["--no-sandbox"])
        except Exception as e:
            return _write("NOT_MEASURED", reason="browser would not start: %s" % str(e).splitlines()[0][:160])
        pages = {}
        for lang in LANGS:                      # open all five at once: ~30 s, not ~100 s
            ctx = b.new_context(viewport={"width": 412, "height": 915}, is_mobile=True, has_touch=True)
            ctx.add_cookies([{"name": name, "value": val, "domain": BASE.split("//")[1],
                              "path": "/", "secure": True, "httpOnly": True}])
            ctx.add_init_script("try{localStorage.setItem('ts_lang','%s')}catch(e){}" % lang)
            pg = ctx.new_page()
            if SERVE_MSJS:                      # proof mode: serve a chosen ms.js instead of the live one
                pg.route(re.compile(r".*/static/ms\.js.*"),
                         lambda route: route.fulfill(status=200, content_type="application/javascript",
                                                     body=open(SERVE_MSJS, encoding="utf-8").read()))
            errs = []
            pg.on("pageerror", lambda e, errs=errs: errs.append(str(e)[:160]))
            try:
                pg.goto(BASE + "/", wait_until="commit", timeout=45000)
            except Exception as e:
                errs.append("load: " + str(e).splitlines()[0][:120])
            pages[lang] = (pg, errs)
        # RETURNING-READER-1: the 24 Sep fault only showed for a reader whose dictionary was already
        # cached -- the words paint at once, BEFORE the counts are drawn. A first visit fetches the
        # dictionary late, the counts come out right, and the walk would pass over the broken build
        # (proven: it did, against the pre-fix ms.js). So: first visit until the words are painted
        # (the cache is now warm), then reload -- and judge the RETURNING visit, as David saw it.
        warm_deadline = time.time() + 40
        cold = set(LANGS)
        while cold and time.time() < warm_deadline:
            for lang in list(cold):
                try:
                    s = pages[lang][0].evaluate(READ_JS)
                except Exception:
                    continue
                if _ready(s, lang):
                    cold.discard(lang)
            time.sleep(1.0)
        for lang in LANGS:
            pg, errs = pages[lang]
            try:
                pg.reload(wait_until="commit", timeout=45000)
            except Exception as e:
                errs.append("reload: " + str(e).splitlines()[0][:120])
        deadline = time.time() + 45
        pending = set(LANGS)
        while pending and time.time() < deadline:
            for lang in list(pending):
                pg, errs = pages[lang]
                try:
                    s = pg.evaluate(READ_JS)
                except Exception:
                    continue
                if _ready(s, lang):
                    time.sleep(2.0)             # settle: a second read must agree
                    s2 = pg.evaluate(READ_JS)
                    if s2 == s:
                        s["browse"] = pg.evaluate(BROWSE_JS, BROWSE_CATS)
                        s["errors"] = list(errs)
                        res[lang] = s
                        pending.discard(lang)
            time.sleep(1.0)
        for lang in pending:
            pg, errs = pages[lang]
            try:
                s = pg.evaluate(READ_JS)
            except Exception:
                s = {}
            res[lang] = dict(s or {}, errors=list(errs), not_ready=True)
        b.close()
    say("walked %d languages in %.0fs" % (len(res), time.time() - t0))
    return _judge(res)


def _judge(res):
    en = res.get("en") or {}
    if en.get("not_ready") or not en.get("tiles"):
        return _write("NOT_MEASURED", res=res, reason="the English reference never finished loading")
    problems, blind = [], []
    if en.get("live") and not any((v or 0) > 0 for v in en["tiles"].values()):
        problems.append("en: %d listings loaded but every home tile reads 0" % en["live"])
    for lang in LANGS:
        s = res.get(lang) or {}
        for e in s.get("errors") or []:
            problems.append("%s: page error: %s" % (lang, e))
        if lang == "en":
            continue
        if s.get("not_ready") or not s.get("painted"):
            blind.append(lang)
            continue
        for fld in ("city", "tiles", "featured", "browse"):
            if s.get(fld) != en.get(fld):
                problems.append("%s: %s differs from English -- %s shows %r, English shows %r"
                                % (lang, fld, lang, s.get(fld), en.get(fld)))
    if problems:
        return _write("MISMATCH", res=res, problems=problems, blind=blind)
    if len(blind) == len(LANGS) - 1:
        return _write("NOT_MEASURED", res=res, blind=blind,
                      reason="no other language got its words painted in time -- nothing to compare")
    return _write("OK", res=res, blind=blind)


def _write(state, res=None, problems=None, blind=None, reason=""):
    if SERVE_MSJS:
        say("PROOF MODE (%s served) -> %s -- witness NOT written" % (os.path.basename(SERVE_MSJS), state))
        for p in (problems or [])[:12]:
            say("  " + p)
        return {"OK": 0, "MISMATCH": 1}.get(state, 2)
    rec = {"at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "state": state,
           "reason": reason, "problems": problems or [], "not_measured_langs": blind or [],
           "languages": res or {}, "base": BASE}
    os.makedirs(os.path.dirname(WITNESS), exist_ok=True)
    body = json.dumps(rec, indent=1, ensure_ascii=False)
    with open(WITNESS, "w", encoding="utf-8") as f:
        f.write(body)
    say("%s%s" % (state, (" -- " + reason) if reason else ""))
    for p in (problems or [])[:12]:
        say("  " + p)
    if blind:
        say("  NOT MEASURED (words never painted): " + ", ".join(blind))
    return {"OK": 0, "MISMATCH": 1}.get(state, 2)


if __name__ == "__main__":
    sys.exit(install() if "--install" in sys.argv else walk())
