#!/usr/bin/env python3
"""TrustSquare QA Bot -- the independent security auditor (QA-BOT-1, 24 Sep 2026).

David, 24 Sep 2026: "the tester should not be a human tester. I am a one man owner,
i need you to create an independent QA Bot to perform the audit."

WHO DECIDES WHAT -- the independence this bot exists for
  * OpenAI (a different vendor from the Author, Claude) rules what every route SHOULD
    require. Its rulings live ONLY on the server (STATE/policy.json), never in git, so
    the Author cannot mark its own new route "public" to get past the bot.
  * The bot then tests reality against those rulings by attacking the running app.
  * Claude only fixes code. It never writes the policy and never grades its own work.

PERSONAS (who the bot pretends to be)
  stranger   no sign-in and no keys at all
  publickey  only the X-Api-Key that ships inside the public ms.js (anyone has it)
  intruder   a real signed-in account that does NOT own the target -- aimed at a QA
             fixture advert owned by a second QA account, checked before and after

VERDICTS (per route)
  PASS      every persona was refused
  FAIL      a persona got the work done, or the route looked the data up before
            asking who is calling (404 on a made-up target) -- the audit class
  CRASH     a stranger's request made the server error (5xx)
  UNPROVEN  the bot could not get a well-formed request past validation, so the
            route is neither proven open nor proven closed

COMMANDS
  classify [--all]  ask OpenAI to rule on routes it has not ruled on yet
  probe             attack every protected route, write the report
  gate              deploy gate: classify new routes + probe; exit 1 if any route that
                    was closed (or is brand new) is now open -- server_deploy.sh rolls back
  nightly           classify + probe + OpenAI review of the last 24h of code changes;
                    emails the report to the ops address when anything is red
  appeal ID TEXT    the Author argues with one ruling; OpenAI re-rules (or --file appeals.json)
  show              print OpenAI's rulings

Stdlib only. Runs ON the server as root (it reads the service's secrets to mint the
intruder's session and to clean up after itself; it never prints a secret).
Exit: 0 green / gate pass · 1 red / regression · 2 configuration problem.
"""
import ast, base64, datetime, hashlib, hmac, html, json, os, re, shlex, sqlite3, subprocess
import sys, threading, time, urllib.error, urllib.parse, urllib.request, uuid, warnings

warnings.filterwarnings("ignore", category=SyntaxWarning)   # the app source has old regex strings

LIVE    = os.environ.get("MS_LIVE", "/var/www/marketsquare")
SRC     = os.environ.get("MS_SRC", "/opt/marketsquare-src")
STATE   = os.environ.get("QA_STATE", "/var/lib/trustsquare-qabot")
# The bot attacks through the FRONT DOOR a stranger uses (https://trustsquare.co -> nginx -> app),
# so nginx-level locks count and nginx-level holes show. The name is pinned to this box
# (127.0.0.1) so the attack never leaves the server and Cloudflare's rate limits do not apply.
BASE    = os.environ.get("QA_BASE", "https://trustsquare.co")
PIN_HOST = os.environ.get("QA_PIN_HOST", "trustsquare.co")
SPEC_URL = os.environ.get("QA_SPEC_URL", "http://127.0.0.1:8000/openapi.json")   # route list, internal only
SERVICE = os.environ.get("QA_SERVICE", "marketsquare")
MODEL   = os.environ.get("QA_MODEL", "gpt-5.6-terra")
DB      = os.path.join(LIVE, "marketsquare.db")

PROBE_EMAIL = "qa-bot-probe@example.invalid"      # RFC 2606: can never be a real inbox
INTRUDER    = "qa-bot-intruder@example.invalid"
VICTIM      = "qa-bot-victim@example.invalid"
FAKE_ID     = 999999937
FIXTURE_TITLE = "QA-BOT FIXTURE - not a real advert"
PNG_1PX = base64.b64decode(
    b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==")

CLASSES   = ("public", "session", "owner", "admin", "secret-link", "webhook", "buyer-token")
IDENTITY  = ("session", "owner", "admin")          # must refuse anyone unproven with 401/403
BEARER    = ("secret-link", "webhook", "buyer-token")  # must refuse a bogus secret
ID_HEADERS = {"x-admin-key", "x-api-key", "authorization", "x-admin-token", "cookie",
              "x-actor-email", "x-deploy-token"}
DELAY = float(os.environ.get("QA_DELAY", "0.12"))


# ── small utilities ─────────────────────────────────────────────────────────────────────
def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

def jload(path, default):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default

def jsave(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True)
    os.replace(tmp, path)

def say(*a):
    print(*a, flush=True)


# ── secrets: read the way the service sees them; never printed ──────────────────────────
def load_env():
    env = {}
    try:
        out = subprocess.run(["systemctl", "show", "-p", "Environment", "--value", SERVICE],
                             capture_output=True, text=True, timeout=15).stdout
        for tok in shlex.split(out):
            if "=" in tok:
                k, v = tok.split("=", 1)
                env[k] = v
    except Exception:
        pass
    for f in ("/etc/environment", "/etc/marketsquare/secrets.env"):   # EnvironmentFile= wins
        env.update(_read_envfile(f))
    for k, v in _read_envfile(os.path.join(LIVE, ".env")).items():    # .env only fills gaps
        env.setdefault(k, v)
    return env

def _read_envfile(path):
    out = {}
    try:
        for ln in open(path, encoding="utf-8"):
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1)
                out[k.strip().replace("export ", "")] = v.strip().strip('"').strip("'")
    except OSError:
        pass
    return out

def public_app_key():
    """The key a stranger can read out of the public ms.js -- proof it is not a secret."""
    try:
        m = re.search(r"API_KEY\s*=\s*'([^']+)'", open(os.path.join(LIVE, "ms.js"), encoding="utf-8").read())
        return m.group(1) if m else None
    except OSError:
        return None

def mint_session(email, secret):
    """A real ts_user session for a QA account (JWT scope 'user'), 15 minutes."""
    def b64(b):
        return base64.urlsafe_b64encode(b).rstrip(b"=").decode()
    t = int(time.time())
    head = b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    body = b64(json.dumps({"sub": email, "scope": "user", "iat": t, "exp": t + 900}).encode())
    sig = hmac.new(secret.encode(), (head + "." + body).encode(), hashlib.sha256).digest()
    return head + "." + body + "." + b64(sig)


# ── the app's routes: live OpenAPI + the source of each handler ─────────────────────────
def pin_front_door():
    """Resolve the public hostname to this box, so requests go through the local nginx with the
    real certificate and virtual host -- exactly the path a visitor's request takes after
    Cloudflare -- without ever leaving the server."""
    import socket
    real = socket.getaddrinfo

    def pinned(host, *a, **k):
        if host == PIN_HOST:
            host = "127.0.0.1"
        return real(host, *a, **k)
    socket.getaddrinfo = pinned

def load_openapi():
    """The route list. SEC-GATE-1 (24 Sep) closed /openapi.json to the public, so the bot asks as an
    admin when refused, and keeps the last good copy so a refused or broken spec can never stop it."""
    cache = os.path.join(STATE, "openapi_cache.json")
    hdrs = [{}]
    try:
        adm = load_env().get("MS_ADMIN_KEY")
        if adm:
            hdrs.append({"X-Admin-Key": adm})
    except Exception:
        pass
    for h in hdrs:
        try:
            req = urllib.request.Request(SPEC_URL, headers=dict(h, **{"User-Agent": "TrustSquare-QA-Bot/1"}))
            with urllib.request.urlopen(req, timeout=30) as r:
                spec = json.loads(r.read().decode())
            if spec.get("paths"):
                jsave(cache, spec)
                return spec
        except urllib.error.HTTPError as e:
            if e.code not in (401, 403):
                break
        except Exception:
            break
    spec = jload(cache, None)
    if spec:
        say("openapi: live spec unavailable -- using the last good copy")
        return spec
    raise RuntimeError("no route list: /openapi.json refused and no cached copy")

def operations(spec):
    ops = []
    for path, item in spec.get("paths", {}).items():
        for method, op in item.items():
            if method.lower() in ("get", "post", "put", "delete", "patch"):
                ops.append((method.upper(), path, op))
    return ops

def handler_sources(src_path):
    """{'METHOD /path': (function name, source text)} from the running bea_main.py."""
    out = {}
    try:
        text = open(src_path, encoding="utf-8").read()
        tree = ast.parse(text)
    except (OSError, SyntaxError):
        return out
    lines = text.split("\n")
    for n in ast.walk(tree):
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for d in n.decorator_list:
            if (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                    and isinstance(d.func.value, ast.Name) and d.func.attr in ("get", "post", "put", "delete", "patch")
                    and d.args and isinstance(d.args[0], ast.Constant)):
                first = min([x.lineno for x in n.decorator_list] + [n.lineno])
                out["%s %s" % (d.func.attr.upper(), d.args[0].value)] = (n.name, "\n".join(lines[first - 1:n.end_lineno]))
    return out


# ── OpenAI: the independent judge ───────────────────────────────────────────────────────
JUDGE_SYSTEM = """You are the INDEPENDENT SECURITY JUDGE for TrustSquare, a peer-to-peer introductions
marketplace (FastAPI). Another vendor's AI (the Author) wrote this code; your rulings are what an
automatic QA bot will attack the live app against. The Author cannot change your rulings.

For each route, decide what it SHOULD require from WHAT IT DOES - not from what the code happens to
check today. The code may be wrong; that is the point.

How identity works in this app:
- A signed-in person is proven ONLY by the ts_user session cookie (set after an emailed/SMS code).
- The X-Api-Key "app key" ships inside the public ms.js file. Every visitor has it. It is NOT
  identity and NOT a secret. A route protected only by it is effectively public.
- An email address typed into a request (query, path or body) is NOT identity.
- Admin is proven by the server-held X-Admin-Key or an admin token from /admin/login.

Classes (pick exactly one):
- public: anyone may call it with no identity at all - reading public adverts, catalogues, geo data,
  starting a sign-in, anonymous beacons/counters, a public contact form, creating an unpublished
  draft for a brand-new visitor where the code's own documented design says so.
- session: must be a signed-in person; acts only on the caller's own account.
- owner: must be signed in AND own the specific target (advert, photo, watch, document...).
- admin: operator/admin-only actions (verifying, moderating, curating, deploying, ops, bulk import).
- secret-link: authorised by a one-time/secret value the person received (magic link, opt-out link,
  employer-confirm link, a per-agency secret api key) - not by the public app key.
- webhook: server-to-server callback authorised by a shared secret or signature (payments, email worker).
- buyer-token: anonymous buyer feature authorised by possession of that buyer's own buyer_token.

Rules of thumb: anything that changes, deletes, spends money or AI budget, sends messages on
someone's behalf, or reveals a specific person's non-public data is NEVER public. When unsure between
public and a protected class, choose the protected class.

Reply with JSON only: {"routes":[{"id":"<METHOD /path exactly as given>","class":"<class>",
"reason":"<one plain sentence a non-programmer understands>"}]}"""


DAILY_USD = float(os.environ.get("QA_DAILY_USD", "3.00"))
PRICE_IN, PRICE_OUT = 2.0, 12.0          # $/Mtok for the judge model; used for the cap and the report


class BudgetExceeded(Exception):
    pass


def _spend_file():
    return os.path.join(STATE, "spend.json")

def spent_today():
    day = datetime.date.today().isoformat()
    return float(jload(_spend_file(), {}).get(day, 0.0))

def _record_spend(usd):
    day = datetime.date.today().isoformat()
    d = jload(_spend_file(), {})
    d = {k: v for k, v in d.items() if k >= (datetime.date.today() - datetime.timedelta(days=30)).isoformat()}
    d[day] = round(float(d.get(day, 0.0)) + usd, 4)
    jsave(_spend_file(), d)


def openai_chat(key, system, user, max_out=16000, timeout=300):
    """One judge call, inside a HARD daily dollar cap (QA_DAILY_USD, default $3). The worst case of
    the call is charged against the cap BEFORE it is made; the real cost is recorded after."""
    worst = (len(system) + len(user)) / 4 / 1e6 * PRICE_IN + max_out / 1e6 * PRICE_OUT
    if spent_today() + worst > DAILY_USD:
        raise BudgetExceeded("daily OpenAI cap $%.2f reached (spent $%.3f today)" % (DAILY_USD, spent_today()))
    body = {"model": MODEL, "max_completion_tokens": max_out,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions",
                                 data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + key, "Content-Type": "application/json",
                                          "User-Agent": "TrustSquare-QA-Bot/1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        resp = json.loads(r.read().decode())
    text = (resp.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()
    u = resp.get("usage", {})
    cost = u.get("prompt_tokens", 0) / 1e6 * PRICE_IN + u.get("completion_tokens", 0) / 1e6 * PRICE_OUT
    _record_spend(cost)
    return json.loads(text) if text else {}, cost


def classify(env, only_new=True, batch=14, workers=4):
    """Ask OpenAI to rule on every route it has not ruled on. Returns (policy, new ids, $)."""
    key = env.get("OPENAI_API_KEY")
    policy = jload(os.path.join(STATE, "policy.json"), {})
    spec = load_openapi()
    srcs = handler_sources(os.path.join(LIVE, "bea_main.py"))
    todo = []
    for method, path, op in operations(spec):
        rid = "%s %s" % (method, path)
        if only_new and rid in policy:
            continue
        name, src = srcs.get(rid, (op.get("operationId", "?"), ""))
        if not src:
            src = "(source not found) summary: %s\n%s" % (op.get("summary", ""), (op.get("description") or "")[:1500])
        todo.append({"id": rid, "handler": name, "source": src[:3500] + ("\n# ...[truncated]" if len(src) > 3500 else "")})
    if not todo:
        return policy, [], 0.0
    if not key:
        say("classify: OPENAI_API_KEY missing -- %d route(s) left unruled" % len(todo))
        return policy, [], 0.0
    chunks = [todo[i:i + batch] for i in range(0, len(todo), batch)]
    results, cost, lock = {}, [0.0], threading.Lock()

    def run(chunk):
        user = "Rule on these %d routes:\n\n" % len(chunk) + "\n\n".join(
            "===== ROUTE %s  (handler %s) =====\n%s" % (c["id"], c["handler"], c["source"]) for c in chunk)
        for attempt in range(3):
            try:
                data, c = openai_chat(key, JUDGE_SYSTEM, user)
                with lock:
                    cost[0] += c
                    for r in data.get("routes", []):
                        if r.get("id") in {x["id"] for x in chunk} and r.get("class") in CLASSES:
                            results[r["id"]] = {"class": r["class"], "reason": (r.get("reason") or "")[:300],
                                                "by": MODEL, "at": now_iso()}
                return
            except BudgetExceeded as e:
                say("classify: %s -- remaining routes stay unruled and are treated as protected" % e)
                return
            except Exception as e:  # network / rate limit -- retry, then leave unruled
                say("classify: batch attempt %d failed: %r" % (attempt + 1, e)[:200])
                time.sleep(5 * (attempt + 1))

    pending = list(chunks)
    while pending:
        threads = [threading.Thread(target=run, args=(c,)) for c in pending[:workers]]
        pending = pending[workers:]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    policy.update(results)
    jsave(os.path.join(STATE, "policy.json"), policy)
    return policy, sorted(results), cost[0]


def appeal(env, rid, objection):
    """The Author may ARGUE with a ruling, never set one: OpenAI re-reads the route's code with the
    objection and rules again. Both the objection and the earlier ruling are kept on record."""
    key = env.get("OPENAI_API_KEY")
    policy = jload(os.path.join(STATE, "policy.json"), {})
    old = policy.get(rid)
    if not key or not old:
        say("appeal: no key, or %r has no ruling yet" % rid)
        return None
    name, src = handler_sources(os.path.join(LIVE, "bea_main.py")).get(rid, ("?", "(source not found)"))
    user = ("APPEAL of one ruling. Your earlier ruling: %s -- %s\n\nThe Author objects: %s\n\n"
            "The Author's argument is not evidence by itself: check it against the code below, then rule "
            "again on this ONE route (you may keep your ruling).\n\n===== ROUTE %s  (handler %s) =====\n%s"
            % (old["class"], old.get("reason", ""), objection, rid, name, src[:6000]))
    try:
        data, cost = openai_chat(key, JUDGE_SYSTEM, user)
    except BudgetExceeded as e:
        say("appeal: %s" % e)
        return None
    r = next((x for x in data.get("routes", []) if x.get("class") in CLASSES), None)
    if not r:
        say("appeal: no valid ruling returned")
        return None
    history = old.get("history", []) + [{"class": old["class"], "reason": old.get("reason", ""),
                                         "objection": objection, "at": now_iso()}]
    policy[rid] = {"class": r["class"], "reason": (r.get("reason") or "")[:300], "by": MODEL, "at": now_iso(),
                   "history": history}
    jsave(os.path.join(STATE, "policy.json"), policy)
    say("appeal %s: %s -> %s (%s) $%.3f" % (rid, old["class"], r["class"], policy[rid]["reason"], cost))
    return policy[rid]


# ── building a well-formed request from the OpenAPI schema ──────────────────────────────
def _deref(schema, spec):
    seen = 0
    while isinstance(schema, dict) and "$ref" in schema and seen < 20:
        ref = schema["$ref"].split("/")[-1]
        schema = spec.get("components", {}).get("schemas", {}).get(ref, {})
        seen += 1
    return schema or {}

def _value(name, schema, spec, ctx, depth=0):
    schema = _deref(schema, spec)
    lname = (name or "").lower()
    for comb in ("anyOf", "oneOf", "allOf"):
        if comb in schema:
            opts = [_deref(s, spec) for s in schema[comb] if _deref(s, spec).get("type") != "null"]
            if comb == "allOf":
                merged = {"type": "object", "properties": {}, "required": []}
                for o in opts:
                    merged["properties"].update(o.get("properties", {}))
                    merged["required"] += o.get("required", [])
                schema = merged
            else:
                schema = opts[0] if opts else {"type": "string"}
    if "enum" in schema and schema["enum"]:
        return schema["enum"][0]
    t = schema.get("type")
    if "email" in lname:
        return ctx["email"]
    if lname in ("listing_id", "id") and ctx.get("listing_id"):
        return ctx["listing_id"]
    if any(k in lname for k in ("token", "secret", "sig", "code", "key", "otp", "pin", "password")):
        return "qa-bogus-" + uuid.uuid4().hex[:16]
    if t == "integer":
        return FAKE_ID
    if t == "number":
        return 1.5
    if t == "boolean":
        return True
    if t == "array":
        return [] if depth > 2 else [_value(name, schema.get("items", {}), spec, ctx, depth + 1)]
    if t == "object" or "properties" in schema:
        if depth > 3:
            return {}
        req = set(schema.get("required", []))
        out = {}
        for pname, psch in schema.get("properties", {}).items():
            if pname in req or "email" in pname.lower() or pname.lower() in ("listing_id",):
                out[pname] = _value(pname, psch, spec, ctx, depth + 1)
        return out
    if schema.get("format") == "binary":
        return PNG_1PX
    return "qa-probe"

def build_request(method, path, op, spec, persona, ctx):
    """-> (url, headers, body bytes or None)."""
    headers = {"User-Agent": "TrustSquare-QA-Bot/1"}
    query = {}
    url_path = path
    for p in op.get("parameters", []):
        p = _deref(p, spec)
        name, where = p.get("name", ""), p.get("in")
        if where == "path":
            v = _value(name, p.get("schema", {}), spec, ctx)
            url_path = url_path.replace("{%s}" % name, urllib.parse.quote(str(v), safe=""))
        elif where == "query" and (p.get("required") or "email" in name.lower()):
            query[name] = _value(name, p.get("schema", {}), spec, ctx)
        elif where == "header" and name.lower() not in ID_HEADERS and (
                p.get("required") or any(k in name.lower() for k in ("sig", "secret", "token"))):
            headers[name] = str(_value(name, p.get("schema", {}), spec, ctx))
    url = BASE + url_path + ("?" + urllib.parse.urlencode(query, doseq=True) if query else "")
    body = None
    rb = _deref(op.get("requestBody", {}), spec)
    content = rb.get("content", {}) if rb else {}
    if "application/json" in content:
        val = _value("body", content["application/json"].get("schema", {}), spec, ctx)
        body = json.dumps(val).encode()
        headers["Content-Type"] = "application/json"
    elif "multipart/form-data" in content:
        sch = _deref(content["multipart/form-data"].get("schema", {}), spec)
        boundary = "qabot" + uuid.uuid4().hex
        parts = []
        for pname, psch in sch.get("properties", {}).items():
            psch = _deref(psch, spec)
            is_file = psch.get("format") == "binary" or (psch.get("type") == "array" and
                                                       _deref(psch.get("items", {}), spec).get("format") == "binary")
            if is_file:
                parts.append(b"--%s\r\nContent-Disposition: form-data; name=\"%s\"; filename=\"qa.png\"\r\n"
                             b"Content-Type: image/png\r\n\r\n" % (boundary.encode(), pname.encode()) + PNG_1PX + b"\r\n")
            elif pname in sch.get("required", []) or "email" in pname.lower():
                v = _value(pname, psch, spec, ctx)
                parts.append(b"--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n"
                             % (boundary.encode(), pname.encode(), str(v).encode()))
        body = b"".join(parts) + b"--%s--\r\n" % boundary.encode()
        headers["Content-Type"] = "multipart/form-data; boundary=" + boundary
    elif "application/x-www-form-urlencoded" in content:
        sch = _deref(content["application/x-www-form-urlencoded"].get("schema", {}), spec)
        form = {k: _value(k, v, spec, ctx) for k, v in sch.get("properties", {}).items()
                if k in sch.get("required", []) or "email" in k.lower()}
        body = urllib.parse.urlencode(form).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    elif method in ("POST", "PUT", "PATCH"):
        body = b"{}"
        headers["Content-Type"] = "application/json"
    if persona == "publickey" and ctx.get("pubkey"):
        headers["X-Api-Key"] = ctx["pubkey"]
    if persona == "intruder" and ctx.get("intruder_cookie"):
        headers["Cookie"] = "ts_user=" + ctx["intruder_cookie"]
    return url, headers, body

def _ctx_for(url):
    """The pinned front door is this box talking to itself over loopback; its certificate is a
    Cloudflare ORIGIN certificate that only Cloudflare trusts, so verification is skipped for
    that one pinned loopback hop only. Every other HTTPS call keeps full verification."""
    import ssl
    host = urllib.parse.urlsplit(url).hostname
    if host == PIN_HOST:
        return ssl._create_unverified_context()
    return None

def send(method, url, headers, body):
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=25, context=_ctx_for(url)) as r:
                body = r.read(4000).decode("utf-8", "replace")
                if "ts_user=" in (r.headers.get("Set-Cookie") or ""):
                    body = "[SET-SESSION-COOKIE] " + body
                return r.status, body
        except urllib.error.HTTPError as e:
            txt = e.read(1500).decode("utf-8", "replace")
            if e.code == 429 and attempt == 0:
                time.sleep(3)
                continue
            return e.code, txt
        except Exception as e:
            return 0, repr(e)[:200]
    return 429, "rate limited"


# ── the QA objects: an archived advert + two accounts that only the bot uses ────────────
def ensure_fixture():
    """Returns the fixture listing id (never shown publicly: archived + is_demo)."""
    conn = sqlite3.connect(DB, timeout=15)
    try:
        conn.execute("PRAGMA busy_timeout=15000")
        for em in (VICTIM, INTRUDER):
            conn.execute("INSERT OR IGNORE INTO users (email, name, aa_free_used, aa_sessions_remaining) "
                         "VALUES (?, ?, 0, 0)", (em, "QA Bot account"))
        row = conn.execute("SELECT id FROM listings WHERE seller_email=? AND title=? ORDER BY id LIMIT 1",
                           (VICTIM, FIXTURE_TITLE)).fetchone()
        if row:
            lid = row[0]
        else:
            cur = conn.execute("INSERT INTO listings (title, category, city, description, seller_email, "
                               "listing_status, is_demo) VALUES (?,?,?,?,?,?,1)",
                               (FIXTURE_TITLE, "Services", "Pretoria", "qa-fixture-marker", VICTIM, "archived"))
            lid = cur.lastrowid
        conn.commit()
        return lid
    finally:
        conn.close()

def _victim_tables(conn):
    """Every (table, column) that can hold the victim's email -- found from the live schema, so a
    new table is covered the day it appears."""
    out = []
    for (tbl,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
        try:
            cols = [r[1] for r in conn.execute("PRAGMA table_info(%s)" % tbl)]
        except sqlite3.Error:
            continue
        for c in cols:
            if "email" in c.lower() and tbl not in ("listings",):
                out.append((tbl, c))
    return out

def snapshot(lid):
    """Exact copy of everything the QA victim owns: its archived advert, the advert's cities and
    every row in every table keyed by the victim's email. Anything a probe gets through is put
    back precisely, and any change at all is evidence."""
    conn = sqlite3.connect("file:%s?mode=ro" % DB, uri=True, timeout=15)
    conn.row_factory = sqlite3.Row
    try:
        snap = {"listing": dict(conn.execute("SELECT * FROM listings WHERE id=?", (lid,)).fetchone()),
                "tables": {}}
        try:
            snap["cities"] = [dict(r) for r in conn.execute("SELECT * FROM listing_cities WHERE listing_id=?", (lid,))]
        except sqlite3.Error:
            snap["cities"] = None
        for tbl, col in _victim_tables(conn):
            try:
                rows = conn.execute("SELECT rowid AS _rowid_, * FROM %s WHERE LOWER(%s)=?" % (tbl, col), (VICTIM,)).fetchall()
                snap["tables"]["%s.%s" % (tbl, col)] = [dict(r) for r in rows]
            except sqlite3.Error:
                pass
        return snap
    finally:
        conn.close()

def fingerprint(lid):
    s = snapshot(lid)
    return hashlib.sha256(json.dumps(s, sort_keys=True, default=str).encode()).hexdigest()

def changed_where(lid, snap):
    now = snapshot(lid)
    out = []
    if now["listing"] != snap["listing"] or now.get("cities") != snap.get("cities"):
        out.append("listings")
    for k in set(now["tables"]) | set(snap["tables"]):
        if now["tables"].get(k) != snap["tables"].get(k):
            out.append(k.split(".")[0])
    return sorted(set(out))

def restore(lid, snap):
    conn = sqlite3.connect(DB, timeout=15)
    try:
        conn.execute("PRAGMA busy_timeout=15000")
        row = snap["listing"]
        cols = [c for c in row if c != "id"]
        conn.execute("UPDATE listings SET %s WHERE id=?" % ", ".join("%s=?" % c for c in cols),
                     [row[c] for c in cols] + [row["id"]])
        if snap.get("cities") is not None:
            conn.execute("DELETE FROM listing_cities WHERE listing_id=?", (lid,))
            for r in snap["cities"]:
                conn.execute("INSERT INTO listing_cities (%s) VALUES (%s)" % (", ".join(r), ", ".join("?" * len(r))),
                             list(r.values()))
        for key, rows in snap["tables"].items():
            tbl, col = key.split(".", 1)
            conn.execute("DELETE FROM %s WHERE LOWER(%s)=?" % (tbl, col), (VICTIM,))
            for r in rows:
                r = dict(r)
                rid = r.pop("_rowid_")
                conn.execute("INSERT OR REPLACE INTO %s (rowid, %s) VALUES (?, %s)" % (tbl, ", ".join(r), ", ".join("?" * len(r))),
                             [rid] + list(r.values()))
        conn.commit()
    finally:
        conn.close()

def cleanup(env, fixture):
    """Remove any advert a probe managed to create (only ever under the QA addresses)."""
    removed = 0
    try:
        conn = sqlite3.connect("file:%s?mode=ro" % DB, uri=True, timeout=15)
        ids = [r[0] for r in conn.execute(
            "SELECT id FROM listings WHERE LOWER(seller_email) IN (?,?,?) AND id<>?",
            (PROBE_EMAIL, INTRUDER, VICTIM, fixture)).fetchall()]
        conn.close()
    except sqlite3.Error:
        ids = []
    # rows the probes left under the two throw-away addresses (never the victim's, never accounts)
    try:
        conn = sqlite3.connect(DB, timeout=15)
        conn.execute("PRAGMA busy_timeout=15000")
        for tbl, col in _victim_tables(conn):
            if tbl != "users":
                conn.execute("DELETE FROM %s WHERE LOWER(%s) IN (?, ?)" % (tbl, col), (INTRUDER, PROBE_EMAIL))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        say("cleanup: %r" % e)
    adm, pub = env.get("MS_ADMIN_KEY"), public_app_key()
    for lid in ids:
        if adm:
            hdr = {"X-Admin-Key": adm}
            if pub:
                hdr["X-Api-Key"] = pub          # the route also wants the (public) app key
            st, _ = send("DELETE", "%s/listings/%d" % (BASE, lid), hdr, None)
            removed += 1 if st in (200, 204) else 0
    return removed, ids


# ── judging one response ────────────────────────────────────────────────────────────────
def _empty(text):
    """True when a response carries no data at all: {}, [], null, or only empty/false values."""
    try:
        v = json.loads(text)
    except ValueError:
        return not text.strip()
    def blank(x):
        if isinstance(x, dict):
            return all(blank(y) for y in x.values())
        if isinstance(x, list):
            return len(x) == 0
        return x in (None, False, 0, "", "anonymous")
    return blank(v)

def judge(cls, persona, status, text, changed, fake_target, created, method="GET"):
    """Honest verdicts: FAIL only with evidence (work done, data shown, object changed or created)."""
    leaked = VICTIM in text or "qa-fixture-marker" in text
    if changed:
        return "FAIL", "changed another person's data (%s)" % changed
    if created:
        return "FAIL", "created an advert for a caller it should have refused"
    if status == 0:
        return "UNPROVEN", "no answer (%s)" % text[:60]
    if status in (502, 503, 504):
        return "UNPROVEN", "front door answered %d (switched off or not reachable)" % status
    if status >= 500:
        return "CRASH", "server error %d for a caller it should simply refuse" % status
    if status in (401, 403):
        return "PASS", "refused (%d)" % status
    ok = 200 <= status < 300
    if cls == "buyer-token":
        if ok and leaked:
            return "FAIL", "showed another person's data for a made-up token"
        if ok or status in (400, 404, 410):
            return "PASS", "a made-up token reached only its own empty space (%d)" % status
        return "UNPROVEN", "answered %d" % status
    if cls in ("secret-link", "webhook"):
        # these routes often echo the address they were given, so an echo is not evidence;
        # evidence is a session handed out, the victim's advert shown, or data changed (above)
        if ok and ("[SET-SESSION-COOKIE]" in text or "qa-fixture-marker" in text):
            return "FAIL", "accepted a made-up secret (%d)" % status
        if ok:
            return "UNPROVEN", "answered %d; no session given and nothing the bot watches changed" % status
        if status in (400, 404, 410):
            return "PASS", "refused the made-up secret (%d)" % status
        return "UNPROVEN", "answered %d" % status
    # session / owner / admin
    if persona == "intruder":
        if ok and leaked:
            return "FAIL", "showed another person's data to a signed-in stranger (%d)" % status
        if ok or status == 404:
            return "PASS", "answered %d, other person's data untouched and not shown" % status
        return "UNPROVEN", "answered %d" % status
    if ok and leaked:
        return "FAIL", "showed another person's data to someone not signed in (%d)" % status
    if ok and _empty(text):
        return "PASS", "answered a stranger with nothing and changed nothing (%d)" % status
    if ok:
        return "FAIL", ("answered someone not signed in with data (%d)" % status if method == "GET"
                        else "did the work for someone not signed in (%d)" % status)
    if status == 404:
        if fake_target:
            return "UNPROVEN", "made-up target (404): the bot has no real object of this kind to aim at yet"
        return "PASS", "refused (404), nothing shown or changed"
    if status in (400, 402, 405, 409, 422, 429):
        return "UNPROVEN", "answered %d before any sign-in check" % status
    return "UNPROVEN", "answered %d" % status

RANK = {"FAIL": 3, "CRASH": 2, "UNPROVEN": 1, "PASS": 0, "SKIP": -1}


def _qa_listing_ids(fixture):
    conn = sqlite3.connect("file:%s?mode=ro" % DB, uri=True, timeout=15)
    try:
        return {r[0] for r in conn.execute("SELECT id FROM listings WHERE LOWER(seller_email) IN (?,?,?) AND id<>?",
                                          (PROBE_EMAIL, INTRUDER, VICTIM, fixture))}
    finally:
        conn.close()


def probe(env, policy):
    pin_front_door()
    spec = load_openapi()
    pubkey = public_app_key()
    jwt_secret = env.get("MS_JWT_SECRET", "")
    fixture = ensure_fixture()
    snap = snapshot(fixture)
    good = fingerprint(fixture)
    intruder_cookie = mint_session(INTRUDER, jwt_secret) if jwt_secret else None
    # every persona aims at REAL objects that belong to the QA victim account: its archived
    # advert and its account. A hole then shows as work done, not as an ambiguous 404.
    ctx_base = {"pubkey": pubkey, "email": VICTIM, "listing_id": fixture}
    results = []
    for method, path, op in sorted(operations(spec), key=lambda x: (x[1], x[0])):
        rid = "%s %s" % (method, path)
        rule = policy.get(rid)
        cls = rule["class"] if rule else "unruled"
        if cls == "public":
            results.append({"id": rid, "class": cls, "verdict": "SKIP", "personas": {}, "reason": rule.get("reason", "")})
            continue
        eff = "session" if cls == "unruled" else cls       # fail-safe: unruled is treated as protected
        personas = {}
        plist = ["stranger"] + (["publickey"] if pubkey else [])
        if eff in ("owner", "session") and intruder_cookie:
            plist.append("intruder")
        for persona in plist:
            ctx = dict(ctx_base)
            if persona == "intruder":
                ctx["intruder_cookie"] = intruder_cookie
            before_ids = _qa_listing_ids(fixture)
            url, headers, body = build_request(method, path, op, spec, persona, ctx)
            fake_target = str(FAKE_ID) in url.split("?", 1)[0]
            status, text = send(method, url, headers, body)
            changed = ""
            if fingerprint(fixture) != good:
                changed = ", ".join(changed_where(fixture, snap)) or "records"
                restore(fixture, snap)
            new_ids = _qa_listing_ids(fixture) - before_ids
            created = bool(new_ids)
            if created:                       # take it down at once, before anyone can see it
                cleanup(env, fixture)
            v, why = judge(eff, persona, status, text, changed, fake_target, created, method)
            personas[persona] = {"status": status, "verdict": v, "detail": why}
            time.sleep(DELAY)
        worst = max((p["verdict"] for p in personas.values()), key=lambda x: RANK[x])
        results.append({"id": rid, "class": cls, "verdict": worst, "personas": personas,
                        "reason": (rule or {}).get("reason", "not yet ruled by OpenAI - treated as protected")})
    removed, ids = cleanup(env, fixture)
    if fingerprint(fixture) != good:
        restore(fixture, snap)
    return {"at": now_iso(), "base": BASE, "results": results,
            "cleanup": {"found": len(ids), "removed": removed, "ids": ids},
            "pubkey_found": bool(pubkey), "intruder": bool(intruder_cookie), "fixture": fixture}


def summarise(run):
    c = {}
    for r in run["results"]:
        c[r["verdict"]] = c.get(r["verdict"], 0) + 1
    return c


def regressions(run, last):
    """Routes open now that were closed at the last accepted run, or that are brand new."""
    out = []
    for r in run["results"]:
        if r["verdict"] not in ("FAIL", "CRASH"):
            continue
        prev = last.get(r["id"])
        if prev is None or prev in ("PASS", "UNPROVEN", "SKIP"):
            out.append(dict(r, previous=prev or "new route"))
    return out


# ── nightly: OpenAI reviews the last day's code changes ─────────────────────────────────
REVIEW_SYSTEM = """You are the independent nightly security reviewer for TrustSquare. Another vendor's AI
wrote these code changes. Identity rules: only the ts_user session cookie proves a person; the X-Api-Key
in the public ms.js is NOT a secret; a typed email is NOT identity; admin needs the server-held admin key.
Find, concretely, any change that: lets someone act as or on another person; trusts a typed email or the
public key; shows a person's private data; stores or shows user text as page code; spends money or AI
budget without a limit; or WEAKENS tests, the QA bot (qa_bot/) or the deploy gate. Ignore style.
Reply JSON only: {"verdict":"GREEN|AMBER|RED","findings":[{"severity":"RED|AMBER","file":"...",
"summary":"one plain sentence a non-programmer understands"}]}"""

def nightly_review(env):
    key = env.get("OPENAI_API_KEY")
    if not key or not os.path.isdir(os.path.join(SRC, ".git")):
        return {"verdict": "SKIPPED", "findings": [], "cost": 0.0}
    diff = subprocess.run(["git", "-C", SRC, "log", "--since=26 hours ago", "-p", "--no-color", "--",
                           "*.py", "*.js", "*.html", "ops/"], capture_output=True, text=True, timeout=60).stdout
    if not diff.strip():
        return {"verdict": "GREEN", "findings": [], "cost": 0.0, "note": "no code changes in the last day"}
    capped = diff[:150000] + ("\n...[truncated at 150k chars]" if len(diff) > 150000 else "")
    try:
        data, cost = openai_chat(key, REVIEW_SYSTEM, capped, timeout=600)
    except BudgetExceeded as e:
        return {"verdict": "SKIPPED", "findings": [], "cost": 0.0, "note": str(e)}
    except Exception as e:
        return {"verdict": "SKIPPED", "findings": [], "cost": 0.0, "note": "review failed: %r" % e}
    data["cost"] = cost
    return data


# ── report (colour-coded, David is a visual person) + email ─────────────────────────────
def render(run, title, review=None, regress=None, new_rules=None):
    c = summarise(run)
    esc = html.escape
    col = {"FAIL": ("#b3261e", "#fbe9e7"), "CRASH": ("#c2660a", "#fdf0e1"), "UNPROVEN": ("#8a6d00", "#faf4d9"),
           "PASS": ("#1f7a45", "#e5f4ea"), "SKIP": ("#6b625d", "#eeeae7")}
    words = {"FAIL": "Open to the wrong person", "CRASH": "Crashes", "UNPROVEN": "Not proven",
             "PASS": "Closed correctly", "SKIP": "Public by OpenAI's ruling"}
    tiles = "".join('<div class="tile" style="background:%s;color:%s"><b>%d</b><span>%s</span></div>'
                    % (col[k][1], col[k][0], c.get(k, 0), words[k]) for k in ("FAIL", "CRASH", "UNPROVEN", "PASS", "SKIP"))
    rows = []
    for r in sorted(run["results"], key=lambda r: (-RANK[r["verdict"]], r["id"].split(" ", 1)[1])):
        if r["verdict"] in ("SKIP",):
            continue
        ps = "; ".join("%s → %s (%s)" % (k, v["status"], v["detail"]) for k, v in r["personas"].items())
        rows.append('<tr><td><span class="v" style="background:%s;color:%s">%s</span></td><td><code>%s</code></td>'
                    '<td>%s</td><td>%s<div class="why">OpenAI: %s</div></td></tr>'
                    % (col[r["verdict"]][1], col[r["verdict"]][0], r["verdict"], esc(r["id"]), esc(r["class"]),
                       esc(ps), esc(r.get("reason", ""))))
    extra = ""
    if regress is not None:
        extra += "<h2>Deploy gate</h2><p>%s</p>" % (
            "No route that was closed has opened, and no new route is open." if not regress else
            "<b>%d route(s) opened by this deploy — rolled back:</b> %s" % (
                len(regress), ", ".join("<code>%s</code>" % esc(x["id"]) for x in regress)))
    if new_rules:
        extra += "<h2>New routes OpenAI ruled on</h2><p>%s</p>" % ", ".join("<code>%s</code>" % esc(x) for x in new_rules)
    if review:
        f = "".join('<li><b>%s</b> %s — %s</li>' % (esc(x.get("severity", "")), esc(x.get("file", "")),
                                                     esc(x.get("summary", ""))) for x in review.get("findings", []))
        extra += "<h2>OpenAI's review of the last day's code — %s</h2><ul>%s</ul>" % (esc(review.get("verdict", "")), f or "<li>No findings.</li>")
    return """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title><style>
body{margin:0;background:#f6f4f2;color:#1d1715;font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif;padding:24px 16px}
.w{max-width:1000px;margin:0 auto;display:grid;gap:18px} h1{margin:0;font-size:28px} h2{margin:8px 0 0;font-size:18px}
.eb{font:600 12px ui-monospace,monospace;letter-spacing:.06em;text-transform:uppercase;color:#b5431f}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
.tile{border-radius:10px;padding:12px 14px;display:grid} .tile b{font-size:28px} .tile span{font-weight:600}
.tw{overflow-x:auto;background:#fff;border:1px solid #e4ddd8;border-radius:8px}
table{border-collapse:collapse;width:100%%;font-size:13.5px} td{padding:8px 10px;border-bottom:1px solid #eee;vertical-align:top}
code{font:12.5px ui-monospace,monospace} .v{font:700 11px ui-monospace,monospace;padding:3px 6px;border-radius:4px}
.why{color:#5b504b;font-size:12.5px;margin-top:3px} p,ul{margin:0}
</style></head><body><div class="w"><div class="eb">TrustSquare · QA Bot · %s · judge: OpenAI · attacker: the bot</div>
<h1>%s</h1><div class="tiles">%s</div>%s<h2>Every protected route, worst first</h2>
<div class="tw"><table>%s</table></div>
<p style="color:#5b504b;font-size:13px">OpenAI spend today $%.3f of a $%.2f hard daily cap. Personas: stranger (no sign-in, no key) · publickey (only the key inside the public ms.js) · intruder (a signed-in QA account aimed at another QA account's archived advert). Things a probe managed to create are removed afterwards: %d of %d.</p>
</div></body></html>""" % (esc(title), esc(run["at"]), esc(title), tiles, extra, "".join(rows),
                             spent_today(), DAILY_USD, run["cleanup"]["removed"], run["cleanup"]["found"])


def email_body(run, title, review=None, regress=None):
    """What David reads: the red items only, one line each. The full route-by-route page stays on the
    server (latest.html) -- a 100 KB table of routes is not an email, and mail filters agree."""
    esc = html.escape
    c = summarise(run)
    red = [r for r in run["results"] if r["verdict"] in ("FAIL", "CRASH")]
    li = "".join("<li><b style='color:%s'>%s</b> <code>%s</code> &mdash; %s</li>" % (
        "#b3261e" if r["verdict"] == "FAIL" else "#c2660a", r["verdict"], esc(r["id"]),
        esc(next((v["detail"] for v in r["personas"].values() if v["verdict"] in ("FAIL", "CRASH")), "")))
        for r in red)
    parts = ["<h2 style='margin:0 0 8px'>%s</h2>" % esc(title),
             "<p><b style='color:#b3261e'>%d open</b> &middot; <b style='color:#c2660a'>%d crash</b> &middot; "
             "<b style='color:#1f7a45'>%d closed</b> &middot; %d not yet provable &middot; %d public by ruling</p>"
             % (c.get("FAIL", 0), c.get("CRASH", 0), c.get("PASS", 0), c.get("UNPROVEN", 0), c.get("SKIP", 0))]
    if regress:
        parts.append("<p><b>This deploy was rolled back.</b> Opened: %s</p>"
                     % ", ".join("<code>%s</code>" % esc(x["id"]) for x in regress))
    if red:
        parts.append("<p>Still open:</p><ul>%s</ul>" % li)
    if review and review.get("findings"):
        parts.append("<p>OpenAI's review of the day's code (%s):</p><ul>%s</ul>" % (esc(review.get("verdict", "")), "".join(
            "<li><b>%s</b> %s &mdash; %s</li>" % (esc(f.get("severity", "")), esc(f.get("file", "")), esc(f.get("summary", "")))
            for f in review["findings"][:12])))
    parts.append("<p style='color:#6b625d;font-size:13px'>Judge: OpenAI. Attacker: the QA Bot. Full report on the server: "
                 "/var/lib/trustsquare-qabot/latest.html</p>")
    return "<div style='font:15px/1.5 system-ui,sans-serif;color:#1d1715;max-width:760px'>%s</div>" % "".join(parts)


def email(env, subject, html_body):
    key, to = env.get("RESEND_API_KEY"), env.get("QA_REPORT_TO") or env.get("GMAIL_ADDRESS")
    if not key or not to:
        say("email: no RESEND_API_KEY or ops address -- report kept on the server only")
        return False
    req = urllib.request.Request("https://api.resend.com/emails", data=json.dumps({
        "from": "TrustSquare QA Bot <hello@mail.trustsquare.co>", "to": [to], "subject": subject,
        "html": html_body}).encode(), headers={"Authorization": "Bearer " + key, "Content-Type": "application/json",
                                               "User-Agent": "TrustSquare-QA-Bot/1"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            say("email: accepted by Resend (%d) %s" % (r.status, r.read(120).decode("utf-8", "replace")))
            return 200 <= r.status < 300
    except Exception as e:
        say("email failed: %r" % e)
        return False


def save_run(run, html_text, tag):
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    d = os.path.join(STATE, "reports")
    os.makedirs(d, exist_ok=True)
    jsave(os.path.join(d, "%s-%s.json" % (stamp, tag)), run)
    for p in (os.path.join(d, "%s-%s.html" % (stamp, tag)), os.path.join(STATE, "latest.html")):
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(html_text)
    # keep 60 of each
    files = sorted(os.listdir(d))
    for f in files[:-120]:
        try:
            os.remove(os.path.join(d, f))
        except OSError:
            pass
    return os.path.join(d, "%s-%s.html" % (stamp, tag))


def accept(run):
    jsave(os.path.join(STATE, "last.json"), {r["id"]: r["verdict"] for r in run["results"]})


def print_table(run):
    for r in sorted(run["results"], key=lambda r: (-RANK[r["verdict"]], r["id"])):
        if r["verdict"] in ("FAIL", "CRASH", "UNPROVEN"):
            ps = " | ".join("%s:%s" % (k, v["status"]) for k, v in r["personas"].items())
            say("%-8s %-9s %-60s %s" % (r["verdict"], r["class"], r["id"][:60], ps))
    say("SUMMARY", json.dumps(summarise(run)), "cleanup", run["cleanup"])


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "probe"
    os.makedirs(STATE, exist_ok=True)
    env = load_env()
    if cmd == "show":
        for k, v in sorted(jload(os.path.join(STATE, "policy.json"), {}).items()):
            say("%-12s %-60s %s" % (v["class"], k, v["reason"]))
        return 0
    if cmd == "appeal":
        if "--file" in args:
            items = json.load(open(args[args.index("--file") + 1], encoding="utf-8"))
        else:
            items = [{"id": args[1], "objection": args[2]}]
        for it in items:
            appeal(env, it["id"], it["objection"])
        return 0
    if cmd == "classify":
        policy, new, cost = classify(env, only_new="--all" not in args)
        say("classify: %d route(s) ruled now, %d in policy, cost $%.3f" % (len(new), len(policy), cost))
        return 0
    if cmd in ("probe", "gate", "nightly"):
        policy, new, cost = classify(env, only_new=True)
        run = probe(env, policy)
        run["classify_cost"] = cost
        print_table(run)
        last = jload(os.path.join(STATE, "last.json"), None)
        if cmd == "gate":
            reg = regressions(run, last or {}) if last is not None else []
            page = render(run, "Deploy gate", regress=reg, new_rules=new)
            path = save_run(run, page, "gate")
            if reg:
                say("GATE: %d route(s) opened by this deploy -> ROLL BACK" % len(reg))
                for x in reg:
                    say("  OPENED  %s  (was %s)" % (x["id"], x["previous"]))
                email(env, "QA Bot stopped a deploy: %d route(s) opened" % len(reg),
                      email_body(run, "QA Bot stopped a deploy", regress=reg))
                return 1
            accept(run)
            say("GATE: pass -- report %s" % path)
            return 0
        if cmd == "nightly":
            review = nightly_review(env)
            rej = os.path.join(STATE, "rejected_sha")
            if os.path.exists(rej) and time.time() - os.path.getmtime(rej) < 26 * 3600:
                review.setdefault("findings", []).insert(0, {
                    "severity": "RED", "file": "deploy gate",
                    "summary": "The gate refused commit %s in the last day; it did not go live." % open(rej).read().strip()[:10]})
                review["verdict"] = "RED"
            run["review"] = review
            page = render(run, "Nightly security audit", review=review, new_rules=new)
            path = save_run(run, page, "nightly")
            c = summarise(run)
            red = c.get("FAIL", 0) + c.get("CRASH", 0) > 0 or review.get("verdict") == "RED"
            if red:
                email(env, "QA Bot nightly audit: RED - %d open, %d crash, review %s" % (
                    c.get("FAIL", 0), c.get("CRASH", 0), review.get("verdict")),
                      email_body(run, "QA Bot nightly audit", review=review))
            if last is None or not regressions(run, last):
                accept(run)
            say("NIGHTLY:", "RED" if red else "GREEN", path)
            return 1 if red else 0
        page = render(run, "QA Bot probe", new_rules=new)
        path = save_run(run, page, "probe")
        if "--accept" in args:
            accept(run)
        say("report:", path)
        return 1 if summarise(run).get("FAIL", 0) else 0
    say(__doc__)
    return 2


if __name__ == "__main__":
    # exit 1 means "a route opened" to the deploy gate; any crash of the bot itself must never be
    # mistaken for that verdict, so it exits 2 (the gate then fails closed and says why)
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:
        import traceback
        traceback.print_exc()
        say("QA BOT ERROR: the bot itself failed (exit 2) -- not a verdict on the code")
        sys.exit(2)
