#!/usr/bin/env python3
"""
i18n_parity_harness.py -- I18N_READINESS.md item 2 (RUL-075 / RUL-152). Built 1 Oct 2026.

THE RENDERED-TEXT PARITY GATE. Loads the app headless TWICE -- a baseline build and a
candidate build -- under identical, frozen conditions, walks every screen, and diffs every
string the page puts in front of a person. With only English in play the two must be
IDENTICAL. That is the gate for any string extraction (Phase A), any change to the paint
layer that already translates the live app, and any refactor that should not move a word.

WHAT IS SERVED. Both builds are served from DISK, never from the live site: every request
for a path listed in ops/autodeploy/deploy_manifest.txt is answered from the local file the
manifest maps it to (exactly what the server would serve). A candidate is an OVERLAY
directory that mirrors repo paths -- any file present there (ms.js, marketsquare.html,
ms.css, roles/app_i18n_af.json ...) replaces the working-tree file for that run only.
Nothing in the repo is edited; the live app is never touched.

WHAT IS FROZEN, so that a difference means the BUILD differs and nothing else:
  * TIME ITSELF: the page runs on a virtual clock (Date, timers, animation frames) that moves
    only when the harness moves it, in fixed steps, and only after every request in flight
    has been answered -- so a toast that hides after 4 s is hidden in BOTH builds, always.
    Math.random is seeded; service workers are blocked;
  * the data -- API GETs are replayed from a recorded fixture
    (ledger_runs/i18n_parity_fixture.json, gitignored: it holds live adverts). With no
    fixture every API call is refused the same way on both sides, and the app's empty /
    offline wording is what gets compared. `record` builds the fixture through the gate.
  * images, fonts and anything off-site are refused on both sides.
  * translation: the live /i18n/translate is NEVER called (it can spend on the AI lane). It is
    answered from the checked dictionaries on disk (roles/app_i18n_<lang>.json), so --langs af
    compares the paint layer exactly as the checked words would paint it, at $0.

WHAT IS READ, per state (page load, then every .screen via goTo(), each Browse category,
and the first advert's detail): every DOM text node (hidden screens included), every
translatable attribute (placeholder/title/aria-label/alt/button value/data-tooltip/
data-label), the active screen's innerText (what CSS actually lets show), document.title,
<html lang>, and any page error. Equality is judged on the joined text + attribute
multiset + visible text -- so wrapping a word in a <span data-i18n> is NOT a difference,
but changing, dropping or adding a single character IS.

KNOWN LIMITS (stated, not hidden): CSS ::before/::after `content:` text, canvas/SVG
images of text, toasts that vanish before the read, and screens that need a signed-in
seller beyond what the fixture carries. Modal sheets are read as part of the chrome.

  python3 scripts/i18n_parity_harness.py prove                 # clean pass + planted faults -> i18n/parity_proof.json
  python3 scripts/i18n_parity_harness.py check --candidate DIR [--langs en,af]   # THE GATE
  python3 scripts/i18n_parity_harness.py record                # (re)build the data fixture via the gate
  python3 scripts/i18n_parity_harness.py snapshot --out F.json [--candidate DIR] [--lang en]
  python3 scripts/i18n_parity_harness.py compare A.json B.json

Exit 0 = parity (or proof complete). 1 = a difference (or proof failed). 2 = NOT MEASURED
(no browser toolkit, fixture unobtainable, ...) -- never reported as a pass.

Browser toolkit: the SCREEN-WALK-1 kit at Projects/.tools/screen_walk (reused, not rebuilt;
`python3 scripts/screen_walk.py --install` repairs it).
"""
import difflib, hashlib, json, os, re, shutil, sys, tempfile, time
from datetime import datetime, timezone
from urllib.parse import urlsplit, parse_qsl, urlencode

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
MANIFEST = os.path.join(REPO, "ops", "autodeploy", "deploy_manifest.txt")
FIXTURE = os.path.join(REPO, "ledger_runs", "i18n_parity_fixture.json")
LAST = os.path.join(REPO, "ledger_runs", "i18n_parity_last.json")
PROOF = os.path.join(REPO, "i18n", "parity_proof.json")
ORIGIN = "https://trustsquare.co"
DEFAULT_CLOCK = "2026-10-01T09:00:00+02:00"
VOLATILE_PARAMS = {"buyer_token", "_", "t", "ts", "cb", "nocache", "v"}
TRACKED = {"document", "script", "stylesheet", "fetch", "xhr"}
BROWSE_CATS = ["Property", "Tutors", "Services", "Adventures", "Collectors", "Cars"]
CT = {"html": "text/html; charset=utf-8", "js": "application/javascript; charset=utf-8",
      "css": "text/css; charset=utf-8", "json": "application/json; charset=utf-8",
      "md": "text/plain; charset=utf-8", "webmanifest": "application/manifest+json",
      "svg": "image/svg+xml"}
SEED_JS = ("(()=>{let s=0x2F6E2B1;Math.random=function(){s|=0;s=s+0x6D2B79F5|0;"
           "let t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;"
           "return((t^t>>>14)>>>0)/4294967296;};})();")


def say(m):
    print("[parity] " + m, flush=True)


# ---------------------------------------------------------------- serving ----
def load_manifest():
    """served path ('/static/ms.js') -> repo-relative local path ('ms.js')."""
    served = {}
    for raw in open(MANIFEST, encoding="utf-8"):
        line = raw.strip()
        if not line or line.startswith("#") or "|" not in line:
            continue
        local, dest = [x.strip() for x in line.split("|", 1)]
        dest = dest.split("#", 1)[0].strip()
        if local and dest:
            served["/" + dest.lstrip("/")] = local
    if "/index.html" in served:
        served.setdefault("/", served["/index.html"])
    return served


class Build:
    """The working tree, optionally overlaid by a candidate directory that mirrors repo paths."""
    def __init__(self, overlay=None, label="baseline", lang=None, translate=None):
        self.overlay = os.path.abspath(overlay) if overlay else None
        self.label = label
        self.served = load_manifest()
        self.used = {}
        self.lang = lang              # pin this build to one language (else walk()'s langs apply)
        self.translate = translate    # callable(phrase)->text: answers /i18n/translate instead of the dictionary
        self.asked = set()            # every phrase the paint layer asked to have translated

    def local_file(self, served_path):
        rel = self.served.get(served_path)
        if not rel:
            return None
        if self.overlay:
            o = os.path.join(self.overlay, rel)
            if os.path.isfile(o):
                return o
        p = os.path.join(REPO, rel)
        return p if os.path.isfile(p) else None

    def fingerprint(self):
        return {k: hashlib.sha256(open(v, "rb").read()).hexdigest()[:16] for k, v in sorted(self.used.items())}


def fixture_key(url):
    u = urlsplit(url)
    q = sorted((k, v) for k, v in parse_qsl(u.query, keep_blank_values=True) if k not in VOLATILE_PARAMS)
    return u.path + ("?" + urlencode(q) if q else "")


def load_fixture():
    try:
        return json.load(open(FIXTURE, encoding="utf-8"))
    except Exception:
        return None


def _translate_stub(route, build):
    """The live /i18n/translate can SPEND (it calls the AI lane for any phrase not yet cached), so
    the harness never sends it there -- not even while recording. It answers instead from the
    CHECKED dictionary on disk (roles/app_i18n_<lang>.json, overlay-aware, so a candidate's edited
    dictionary is what its own run paints). A phrase not in that dictionary comes back
    untranslated, the same on both sides. $0, deterministic."""
    try:
        body = json.loads(route.request.post_data or "{}")
    except Exception:
        body = {}
    lang = re.sub(r"[^a-z]", "", str(body.get("lang") or "").lower())[:8]
    out = {}
    if build.translate is not None:          # pseudo-locale (item 3): every phrase asked gets an answer
        for t in body.get("strings") or []:
            k = (t or "").strip()
            if k:
                build.asked.add(k)
                out[k] = build.translate(k)
        return route.fulfill(status=200, content_type="application/json",
                             body=json.dumps({"lang": lang, "out": out, "from_cache": len(out), "translated": 0}))
    f = build.local_file("/roles/app_i18n_%s.json" % lang) if lang else None
    if f:
        build.used["/roles/app_i18n_%s.json" % lang] = f
        try:
            table = (json.load(open(f, encoding="utf-8")) or {}).get("t") or {}
        except Exception:
            table = {}
        for t in body.get("strings") or []:
            k = (t or "").strip()
            if k in table:
                out[k] = table[k]
    return route.fulfill(status=200, content_type="application/json",
                         body=json.dumps({"lang": lang, "out": out, "from_cache": len(out), "translated": 0}))


def make_handler(build, fixture, record=None):
    entries = (fixture or {}).get("entries", {})
    by_path = {}
    for k in entries:
        by_path.setdefault(k.split("?", 1)[0], []).append(k)

    def handler(route):
        req = route.request
        url = req.url
        if not url.startswith(ORIGIN + "/"):
            return route.abort()
        path = urlsplit(url).path
        if req.method == "GET":
            f = build.local_file(path)
            if f:
                build.used[path] = f
                ext = f.rsplit(".", 1)[-1].lower()
                return route.fulfill(status=200, body=open(f, "rb").read(),
                                     headers={"content-type": CT.get(ext, "application/octet-stream"),
                                              "cache-control": "no-store"})
        if req.method == "POST" and path == "/i18n/translate":
            return _translate_stub(route, build)
        if req.resource_type not in ("fetch", "xhr") or req.method != "GET":
            return route.abort()          # images, fonts, POSTs: refused identically on both sides
        key = fixture_key(url)
        if record is not None:            # RECORD: pass the GET through the gate, keep the answer
            try:
                resp = route.fetch(timeout=30000)
                body = resp.text()
                record[key] = {"status": resp.status, "ct": resp.headers.get("content-type", ""), "body": body}
                return route.fulfill(response=resp, body=body)
            except Exception:
                return route.abort()
        e = entries.get(key)
        if e is None and len(by_path.get(path, [])) == 1:
            e = entries[by_path[path][0]]
        if e is None:
            return route.abort()
        return route.fulfill(status=e["status"], body=e["body"],
                             headers={"content-type": e.get("ct") or "application/json"})
    return handler


# ---------------------------------------------------------------- reading ----
READ_JS = r"""(scope) => {
  const norm = s => (s || '').replace(/\s+/g, ' ').trim();
  const ATTRS = ['placeholder','title','aria-label','alt','data-tooltip','data-label','value'];
  const SKIP = {SCRIPT:1, STYLE:1, NOSCRIPT:1, TEMPLATE:1};
  function collect(root, skipScreens) {
    const texts = [], attrs = [];
    if (!root) return {texts, attrs, missing: true};
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT, {
      acceptNode(n) {
        if (n.nodeType === 1) {
          if (SKIP[n.tagName]) return NodeFilter.FILTER_REJECT;
          if (skipScreens && n.classList && n.classList.contains('screen')) return NodeFilter.FILTER_REJECT;
        }
        return NodeFilter.FILTER_ACCEPT; } });
    let n;
    while ((n = w.nextNode())) {
      if (n.nodeType === 3) { const t = norm(n.nodeValue); if (t) texts.push(t); continue; }
      for (const a of ATTRS) {
        if (!n.hasAttribute(a)) continue;
        if (a === 'value' && !(n.tagName === 'INPUT' && /^(button|submit|reset)$/i.test(n.type || ''))) continue;
        const v = norm(n.getAttribute(a)); if (v) attrs.push(n.tagName.toLowerCase() + '@' + a + '=' + v);
      }
    }
    return {texts, attrs};
  }
  const out = {chrome: collect(document.body, true), title: norm(document.title),
               lang: document.documentElement.lang || '', active: (document.querySelector('.screen.active') || {}).id || ''};
  if (scope === '*') {
    out.screens = {};
    document.querySelectorAll('.screen').forEach(s => { out.screens[s.id] = collect(s, false); });
  } else {
    out.screens = {}; out.screens[scope] = collect(document.getElementById(scope), false);
  }
  const act = document.querySelector('.screen.active');
  out.visible = act ? norm(act.innerText) : '';
  return out;
}"""

def _idle(runs, max_s=5.0):
    """Wait (real time) until no page has a request in flight, then one round-trip each so
    resolved fetches have run their callbacks. Returns False if something never answered."""
    t_end = time.time() + max_s
    while time.time() < t_end:
        if all(r["inflight"][0] <= 0 for r in runs):
            for r in runs:
                try:
                    r["page"].evaluate("()=>new Promise(res=>Promise.resolve().then(res))")
                except Exception:
                    pass
            if all(r["inflight"][0] <= 0 for r in runs):
                return True
        try:   # NOT time.sleep: the sync API only runs our route handlers while it is pumping
            runs[0]["page"].wait_for_timeout(25)
        except Exception:
            time.sleep(0.025)
    return False


def advance(runs, total_ms, chunk=500):
    """Move every page's virtual clock forward by total_ms, chunk by chunk, letting the network
    go idle before each tick. Same inputs -> same sequence of timer firings -> same DOM."""
    _idle(runs)
    for _ in range(max(1, total_ms // chunk)):
        for r in runs:
            try:
                r["page"].clock.run_for(chunk)
            except Exception as e:
                r["errs"].append("clock: " + str(e).splitlines()[0][:120])
        _idle(runs)


def _steps(screen_ids):
    steps = [("load", None, "*")]
    for sid in screen_ids:
        name = sid[len("screen-"):]
        steps.append(("goto:" + name, "(n)=>{goTo(n)}", sid, name))
    for c in BROWSE_CATS:
        steps.append(("browse:" + c, "(c)=>{filterBrowse(c)}", "screen-browse", c))
    steps.append(("detail:first", "()=>{const a=document.querySelector('#listing-grid [onclick*=\"openDetail\"]');"
                  "if(!a) throw new Error('no advert card in the grid'); a.click();}", "screen-detail", None))
    steps.append(("goto:home#end", "(n)=>{goTo(n)}", "screen-home", "home"))
    return [s if len(s) == 4 else s + (None,) for s in steps]


def walk(builds, langs=("en",), fixture=None, record=None, deadline_s=165, extra_js=None):
    """Snapshot every build (x every lang) in parallel contexts of ONE browser. Returns
    {(label, lang): snapshot} or raises RuntimeError('NOT_MEASURED: ...')."""
    import screen_walk as sw
    sw._kit_env()
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        raise RuntimeError("NOT_MEASURED: browser toolkit missing (%s) -- run scripts/screen_walk.py --install" % type(e).__name__)
    clock_iso = (fixture or {}).get("clock") or DEFAULT_CLOCK
    clock_ms = int(datetime.fromisoformat(clock_iso).timestamp() * 1000)
    t0 = time.time()
    out = {}
    with sync_playwright() as p:
        try:
            br = p.chromium.launch(headless=True, args=["--no-sandbox"])
        except Exception as e:
            raise RuntimeError("NOT_MEASURED: browser would not start: %s" % str(e).splitlines()[0][:160])
        runs = []
        for b in builds:
            for lang in ([b.lang] if b.lang else langs):
                ctx = br.new_context(viewport={"width": 412, "height": 915}, is_mobile=True, has_touch=True,
                                     service_workers="block", locale="en-ZA", timezone_id="Africa/Johannesburg")
                if record is not None and record.get("_cookie"):
                    n, v = record["_cookie"].split("=", 1)
                    ctx.add_cookies([{"name": n, "value": v, "domain": ORIGIN.split("//")[1], "path": "/",
                                      "secure": True, "httpOnly": True}])
                ctx.clock.install(time=clock_ms)
                ctx.add_init_script(SEED_JS)
                ctx.add_init_script("try{localStorage.setItem('ts_lang','%s')}catch(e){}" % lang)
                rec = None if record is None else record.setdefault("entries", {})
                ctx.route("**/*", make_handler(b, fixture, rec))
                pg = ctx.new_page()
                errs = []
                inflight = [0]
                pg.on("pageerror", lambda e, errs=errs: errs.append(str(e).splitlines()[0][:200]))
                # Only requests that can change WORDS are waited for. Images are refused anyway, and a
                # refused image can sit "in flight" in Chromium for a long time (seen 1 Oct on the
                # sell-flow category pictures) -- waiting on them cost 5 s per clock tick.
                def _tr(q, d, f=inflight):
                    if q.resource_type in TRACKED:
                        f[0] += d
                pg.on("request", lambda q, _t=_tr: _t(q, 1))
                pg.on("requestfinished", lambda q, _t=_tr: _t(q, -1))
                pg.on("requestfailed", lambda q, _t=_tr: _t(q, -1))
                runs.append({"build": b, "lang": lang, "page": pg, "ctx": ctx, "errs": errs, "inflight": inflight,
                             "snap": {"states": {}, "errors": {}}})
        for r in runs:
            try:
                r["page"].goto(ORIGIN + "/", wait_until="load", timeout=45000)
            except Exception as e:
                r["errs"].append("load: " + str(e).splitlines()[0][:160])
        advance(runs, 8000)
        screen_ids = runs[0]["page"].evaluate("()=>[...document.querySelectorAll('.screen')].map(s=>s.id)")
        steps = _steps(screen_ids)
        for key, act, scope, arg in steps:
            if time.time() - t0 > deadline_s:
                raise RuntimeError("NOT_MEASURED: walk ran past %ds at step %s" % (deadline_s, key))
            for r in runs:
                r["errs_before"] = len(r["errs"])
                if act:
                    try:
                        r["page"].evaluate(act, arg) if arg is not None else r["page"].evaluate(act)
                    except Exception as e:
                        r["snap"]["errors"].setdefault(key, []).append("step: " + str(e).splitlines()[0][:200])
            if act:
                advance(runs, 2000)
            for r in runs:
                try:
                    r["snap"]["states"][key] = r["page"].evaluate(READ_JS, scope)
                    if extra_js:
                        r["snap"].setdefault("extra", {})[key] = r["page"].evaluate(extra_js, scope)
                except Exception as e:
                    r["snap"]["errors"].setdefault(key, []).append("read: " + str(e).splitlines()[0][:200])
                new = r["errs"][r.pop("errs_before"):]
                if new:
                    r["snap"]["errors"].setdefault(key, []).extend("page: " + x for x in new)
        for r in runs:
            r["snap"].update({"label": r["build"].label, "lang": r["lang"], "overlay": r["build"].overlay,
                              "files": r["build"].fingerprint(), "clock": clock_iso,
                              "fixture": bool(fixture), "steps": len(steps),
                              "taken": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
            out[(r["build"].label, r["lang"])] = r["snap"]
        for r in runs:
            try:
                r["ctx"].unroute_all(behavior="ignoreErrors")
            except Exception:
                pass
        br.close()
    say("walked %d run(s) x %d states in %.0fs" % (len(out), len(steps), time.time() - t0))
    return out


# -------------------------------------------------------------- comparing ----
def _sig(c):
    return (" ".join(c.get("texts", [])), sorted(c.get("attrs", [])), bool(c.get("missing")))


def compare(a, b, limit=40):
    """List of human-readable differences between two snapshots ([] = parity)."""
    diffs = []
    sa, sb = a.get("states", {}), b.get("states", {})
    for key in sorted(set(sa) | set(sb)):
        x, y = sa.get(key), sb.get(key)
        if x is None or y is None:
            diffs.append("%s: state only in %s" % (key, "baseline" if y is None else "candidate"))
            continue
        for fld in ("title", "lang", "active"):
            if x.get(fld) != y.get(fld):
                diffs.append("%s: %s %r -> %r" % (key, fld, x.get(fld), y.get(fld)))
        if x.get("visible") != y.get("visible"):
            d = _textdiff(x.get("visible", "").split(" "), y.get("visible", "").split(" "), 6)
            diffs.append("%s: visible text differs: %s" % (key, d))
        regions = [("chrome", x.get("chrome", {}), y.get("chrome", {}))]
        for sid in sorted(set(x.get("screens", {})) | set(y.get("screens", {}))):
            regions.append((sid, x.get("screens", {}).get(sid, {}), y.get("screens", {}).get(sid, {})))
        for name, cx, cy in regions:
            tx, ax, mx = _sig(cx)
            ty, ay, my = _sig(cy)
            if tx != ty:
                diffs.append("%s/%s: text: %s" % (key, name, _textdiff(cx.get("texts", []), cy.get("texts", []))))
            if ax != ay:
                gone = sorted(set(ax) - set(ay))[:4]
                came = sorted(set(ay) - set(ax))[:4]
                diffs.append("%s/%s: attrs: -%s +%s" % (key, name, gone, came))
            if mx != my:
                diffs.append("%s/%s: region present in only one build" % (key, name))
    ea, eb = a.get("errors", {}), b.get("errors", {})
    for key in sorted(set(ea) | set(eb)):
        if ea.get(key) != eb.get(key):
            diffs.append("%s: errors %r -> %r" % (key, ea.get(key), eb.get(key)))
    return diffs[:limit] + (["... %d more" % (len(diffs) - limit)] if len(diffs) > limit else [])


def _textdiff(xa, xb, n=4):
    out = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, xa, xb, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        out.append("%r -> %r" % (" | ".join(xa[i1:i2])[:120], " | ".join(xb[j1:j2])[:120]))
        if len(out) >= n:
            break
    return "; ".join(out) or "(whitespace/ordering only)"


def _count(snap):
    n = 0
    for st in snap.get("states", {}).values():
        n += len(st.get("chrome", {}).get("texts", []))
        for c in st.get("screens", {}).values():
            n += len(c.get("texts", [])) + len(c.get("attrs", []))
    return n


# ------------------------------------------------------------ planted faults --
def _mutate(s):
    """Change exactly one letter, visibly but subtly (the kind of slip an extraction makes)."""
    for i in range(len(s) - 1, -1, -1):
        ch = s[i]
        if ch.isalpha() and ch.isascii():
            rep = "q" if ch.lower() != "q" else "z"
            rep = rep.upper() if ch.isupper() else rep
            return s[:i] + rep + s[i + 1:]
    return None


def _mutate_word(pl):
    """The single word that changed (visible-text diffs are word-level)."""
    ow, mw = pl["original"].split(" "), pl["mutated"].split(" ")
    for x, y in zip(ow, mw):
        if x != y:
            return y
    return pl["mutated"]


def plan_faults(base_snap, workdir):
    """Pick three real strings off the baseline's screens and plant a one-letter fault in a COPY
    of the file that carries each: a static HTML word, a JS-rendered word, and an attribute.
    Returns [(label, overlay_dir, original, mutated, file)]. Never touches the repo files."""
    html = open(os.path.join(REPO, "marketsquare.html"), encoding="utf-8").read()
    msjs = open(os.path.join(REPO, "ms.js"), encoding="utf-8").read()
    load = base_snap["states"].get("load", {})
    static_texts = []
    for sid, c in sorted(load.get("screens", {}).items()):
        static_texts += c.get("texts", [])
    rendered = []
    for key, st in base_snap["states"].items():
        if key == "load":
            continue
        for c in st.get("screens", {}).values():
            rendered += c.get("texts", [])
    faults = []

    def pick(cands, src, other, need):
        seen = set()
        for t in cands:
            if t in seen or len(t) < 8 or not re.search(r"[A-Za-z]{4}", t):
                continue
            seen.add(t)
            if need == "html" and src.count(">" + t + "<") == 1 and other.count(t) == 0:
                return t, ">" + t + "<"
            if need == "js" and other.count(t) == 0 and src.count(t) == 1 and \
                    re.search(r"['\"`>]" + re.escape(t) + r"['\"`<]", src):
                return t, t
        return None, None

    t, anchor = pick(static_texts, html, msjs, "html")
    if t:
        faults.append(("static-html-text", "marketsquare.html", t, _mutate(t), anchor))
    t, anchor = pick(rendered, msjs, html, "js")
    if t:
        faults.append(("js-rendered-text", "ms.js", t, _mutate(t), anchor))
    for m in re.finditer(r'placeholder="([^"<>{}$]{10,80})"', html):
        v = m.group(1)
        if html.count(v) == 1 and msjs.count(v) == 0 and _mutate(v):
            faults.append(("attribute-placeholder", "marketsquare.html", v, _mutate(v), 'placeholder="' + v + '"'))
            break
    plans = []
    for i, (label, fname, orig, mut, anchor) in enumerate(faults):
        d = os.path.join(workdir, "plant_%d_%s" % (i, label))
        os.makedirs(d, exist_ok=True)
        src = html if fname == "marketsquare.html" else msjs
        assert src.count(anchor) == 1, "anchor not unique: %r" % anchor
        with open(os.path.join(d, fname), "w", encoding="utf-8") as fh:
            fh.write(src.replace(anchor, anchor.replace(orig, mut), 1))
        plans.append({"label": label, "file": fname, "original": orig, "mutated": mut, "overlay": d})
    return plans


# -------------------------------------------------------------- commands -----
def cmd_prove():
    fx = load_fixture()
    say("fixture: %s" % ("%d recorded API answers, clock %s" % (len(fx["entries"]), fx.get("clock")) if fx
                         else "none -- every API call refused on both sides (offline wording compared)"))
    work = tempfile.mkdtemp(prefix="i18n_parity_")
    try:
        # walk 1: the baseline twice, side by side (identical inputs, separate browser contexts)
        snaps = walk([Build(label="baseline"), Build(label="baseline-again")], fixture=fx)
        a, b = snaps[("baseline", "en")], snaps[("baseline-again", "en")]
        within = compare(a, b)
        # walk 2: a third baseline beside the planted builds. The third baseline must match walk 1
        # too -- a gate whose verdict depends on WHEN it ran is not a gate.
        plans = plan_faults(a, work)
        builds = [Build(label="baseline-walk2")] + [Build(overlay=pl["overlay"], label=pl["label"]) for pl in plans]
        fsnaps = walk(builds, fixture=fx)
        c = fsnaps[("baseline-walk2", "en")]
        across = compare(a, c)
        clean = within + across
        say("clean pass: within one walk %s; across two walks %s (%d strings read per run)" % (
            "IDENTICAL" if not within else "%d DIFFERENCES" % len(within),
            "IDENTICAL" if not across else "%d DIFFERENCES" % len(across), _count(a)))
        for d in clean[:15]:
            say("  noise: " + d)
        caught_all = bool(plans)
        for pl in plans:
            s = fsnaps[(pl["label"], "en")]
            d = compare(c, s, limit=100000)
            hit = [x for x in d if pl["mutated"] in x or pl["original"] in x
                   or ("visible text" in x and _mutate_word(pl) in x)]
            stray = [x for x in d if x not in hit]
            pl["caught"] = bool(hit)
            pl["exact"] = bool(hit) and not stray
            pl["diff"] = d[:8] + (["... %d more" % (len(d) - 8)] if len(d) > 8 else [])
            pl.pop("overlay", None)
            caught_all = caught_all and pl["caught"] and pl["exact"]
            say("planted %-22s %r -> %r : %s" % (pl["label"], pl["original"][:40], pl["mutated"][:40],
                ("CAUGHT EXACTLY" if pl["exact"] else "CAUGHT, BUT WITH UNRELATED DIFFERENCES") if pl["caught"] else "MISSED"))
        proof = {
            "built": "1 Oct 2026 (I18N_READINESS item 2)",
            "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "clean_pass": not clean,
            "clean_within_walk": not within, "clean_across_walks": not across,
            "planted_fault_caught": caught_all and len(plans) >= 2,
            "clean_differences": clean[:20],
            "planted": plans,
            "strings_read_per_run": _count(a),
            "states_walked": len(a.get("states", {})),
            "fixture": bool(fx), "fixture_clock": (fx or {}).get("clock"),
            "baseline_files": a.get("files"),
            "how": "python3 scripts/i18n_parity_harness.py prove",
        }
        os.makedirs(os.path.dirname(PROOF), exist_ok=True)
        with open(PROOF, "w", encoding="utf-8") as fh:
            json.dump(proof, fh, indent=1, ensure_ascii=False)
        ok = proof["clean_pass"] and proof["planted_fault_caught"]
        say("PROOF %s -> %s" % ("COMPLETE" if ok else "FAILED", os.path.relpath(PROOF, REPO)))
        return 0 if ok else 1
    finally:
        shutil.rmtree(work, ignore_errors=True)


def cmd_check(candidate, langs):
    if not candidate or not os.path.isdir(candidate):
        say("check needs --candidate DIR (an overlay that mirrors repo paths)")
        return 2
    fx = load_fixture()
    snaps = walk([Build(label="baseline"), Build(overlay=candidate, label="candidate")], langs=langs, fixture=fx)
    bad = {}
    for lang in langs:
        d = compare(snaps[("baseline", lang)], snaps[("candidate", lang)])
        if d:
            bad[lang] = d
        say("%s: %s" % (lang, "PARITY" if not d else "%d DIFFERENCES" % len(d)))
        for x in d[:20]:
            say("  " + x)
    os.makedirs(os.path.dirname(LAST), exist_ok=True)
    with open(LAST, "w", encoding="utf-8") as fh:
        json.dump({"at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "candidate": candidate,
                   "langs": list(langs), "fixture": bool(fx), "differences": bad}, fh, indent=1, ensure_ascii=False)
    return 1 if bad else 0


def cmd_record():
    import screen_walk as sw
    cookie = sw._cookie()
    if not cookie:
        say("NOT MEASURED: no review credential -- the gate would refuse every API read")
        return 2
    rec = {"_cookie": cookie}
    walk([Build(label="record")], fixture=None, record=rec)
    entries = rec.get("entries", {})
    ok = {k: v for k, v in entries.items() if v.get("status") == 200}
    if not ok:
        say("NOT MEASURED: the gate answered nothing usable (%d non-200 answers)" % len(entries))
        return 2
    fx = {"recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
          "clock": datetime.now(timezone.utc).replace(microsecond=0, second=0).isoformat(),
          "origin": ORIGIN, "entries": entries,
          "note": "gitignored: live API answers replayed identically to both builds by i18n_parity_harness.py"}
    os.makedirs(os.path.dirname(FIXTURE), exist_ok=True)
    with open(FIXTURE, "w", encoding="utf-8") as fh:
        json.dump(fx, fh, ensure_ascii=False)
    say("recorded %d API answers (%d x 200) -> %s" % (len(entries), len(ok), os.path.relpath(FIXTURE, REPO)))
    return 0


def _arg(name, default=None):
    for i, a in enumerate(sys.argv):
        if a == name and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
        if a.startswith(name + "="):
            return a.split("=", 1)[1]
    return default


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "prove"
    try:
        if cmd == "prove":
            return cmd_prove()
        if cmd == "check":
            return cmd_check(_arg("--candidate"), tuple((_arg("--langs", "en")).split(",")))
        if cmd == "record":
            return cmd_record()
        if cmd == "snapshot":
            out = _arg("--out")
            lang = _arg("--lang", "en")
            b = Build(overlay=_arg("--candidate"), label="snapshot")
            s = walk([b], langs=(lang,), fixture=load_fixture())[("snapshot", lang)]
            with open(out, "w", encoding="utf-8") as fh:
                json.dump(s, fh, ensure_ascii=False)
            say("snapshot -> %s (%d strings)" % (out, _count(s)))
            return 0
        if cmd == "compare":
            a = json.load(open(sys.argv[2], encoding="utf-8"))
            b = json.load(open(sys.argv[3], encoding="utf-8"))
            d = compare(a, b)
            for x in d:
                say(x)
            say("PARITY" if not d else "%d DIFFERENCES" % len(d))
            return 1 if d else 0
    except RuntimeError as e:
        if str(e).startswith("NOT_MEASURED"):
            say(str(e).replace("NOT_MEASURED", "NOT MEASURED"))
            return 2
        raise
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
