#!/usr/bin/env python3
"""ops_guard.py -- OPS-GUARD-1 (14 Oct 2026). David: "Please build it Claude. Please give me in the Ops Dashboard a
clear report regarding subscriptions, to also monitor the onboarding and status ... along with a number of real
listers for all subscription types."  (RUL-230)

Four nightly checks and balances plus one hourly report, all READ-ONLY against the app's database:
  page     -> orchestrator/v2/subscriptions.html : tiers, real vs tester users, real listers per tier, onboarding funnel
  money    -> every successful Paystack payment must be in our records, and every top-up we credited must be a
              successful Paystack payment; no negative balances; no unknown kind of money row; free-credit totals
  data     -> how many people's contact details were opened today (intros accepted, Buzz pairs), per account and
              in total, against the last 7 days; sign-up spikes
  drift    -> (a) live MarketSquare code == the released source (no hand edits on the server);
              (b) every change to the CityLauncher/SMS code and the server's timers since last night is listed and
                  sent to the independent reviewer (OpenAI, the QA Bot's judge, inside its own daily $ cap)
  nightly  -> money + data + drift + page; writes orchestrator/v2/guard.html; e-mails David ONLY when something is red.
A check that cannot see what it needs says NOT MEASURED -- never green by default.
"""
import datetime, difflib, hashlib, html, json, os, re, shutil, sqlite3, subprocess, sys, urllib.parse, urllib.request

LIVE = os.environ.get("MS_LIVE", "/var/www/marketsquare")
SRC = os.environ.get("MS_SRC", "/opt/marketsquare-src")
CL = os.environ.get("CL_DIR", "/var/www/citylauncher")
DB = os.environ.get("MS_DB", os.path.join(LIVE, "marketsquare.db"))
STATE = os.environ.get("GUARD_STATE", "/var/lib/trustsquare-ops")
OUT = os.path.join(LIVE, "orchestrator", "v2")
sys.path.insert(0, os.path.join(SRC, "qa_bot"))

TIERS = [("free", "Free", "#6b8bb3"), ("starter", "Starter $5", "#2e9e6b"), ("pro", "Pro $20", "#7b5cc4"),
         ("agency", "Agency", "#d08a1e")]
KNOWN_MONEY_TYPES = {"ai_service", "tester_grant", "ai_release", "ai_hold_released", "ai_burn", "intro_hold", "intro_burn",
                     "topup", "welcome_ai_sessions", "lm_intro_deduct", "intro_hold_release", "intro_deduct", "dev_credit",
                     "refund", "first_lister_bonus", "ai_hold", "monthly_grant", "referral_bonus", "intro_refund"}
FREE_CREDIT_TYPES = {"tester_grant", "dev_credit", "first_lister_bonus", "welcome_ai_sessions", "monthly_grant", "referral_bonus"}


def now():
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


def sast(dt=None):
    return ((dt or now()) + datetime.timedelta(hours=2)).strftime("%a %d %b %H:%M SAST")


def jload(p, d):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return d


def jsave(p, o):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    json.dump(o, open(tmp, "w", encoding="utf-8"), indent=1, default=str)
    os.replace(tmp, p)


def db():
    c = sqlite3.connect("file:%s?mode=ro" % DB, uri=True, timeout=30)
    c.row_factory = sqlite3.Row
    return c


def esc(s):
    return html.escape(str(s if s is not None else ""))


def _ts(v):
    v = str(v or "")[:19].replace("T", " ")
    try:
        return datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return datetime.datetime(1970, 1, 1)


def mask(email):
    e = (email or "").lower()
    if "@" not in e:
        return "(no e-mail)"
    a, b = e.split("@", 1)
    return "%s***@%s" % (a[:1], b)


# ------------------------------------------------------------------ who is a tester
def _lines(name):
    try:
        return {l.strip().lower() for l in open(os.path.join(STATE, name), encoding="utf-8") if l.strip() and not l.startswith("#")}
    except OSError:
        return set()


def rule_tester(email, name="", title=""):
    e = (email or "").lower()
    local, _, dom = e.partition("@")
    return bool(dom in ("example.com", "trustsquare.co") or local.startswith("dmcontiki2")
                or re.match(r"^(probe|flowtest|walkproof|qa[-_.]|test[-_.]?|demo)", local) or "+qa" in local
                or "+probe" in local or (name or "").upper().startswith("PROBE")
                or re.search(r"\b(PROBE|FLOW TEST|QA TEST)\b", (title or "").upper()))


def tester_set(c):
    """REAL-LISTER-1: a tester is a superuser, anyone ever given a tester grant or a tester invite, David's own
    addresses and +aliases, the platform's own and example.com accounts, probe/flow/QA accounts, and anyone in
    STATE/testers.txt. STATE/real.txt forces an address back to real. Fails towards 'tester' only on those rules."""
    t = set()
    for r in c.execute("SELECT LOWER(email) e, COALESCE(is_superuser,0) su, COALESCE(name,'') n FROM users"):
        e, n = r["e"] or "", r["n"]
        local, _, dom = e.partition("@")
        if (r["su"] == 1 or dom in ("example.com", "trustsquare.co") or local.startswith("dmcontiki2")
                or re.match(r"^(probe|flowtest|walkproof|qa[-_.]|test[-_.]?|demo)", local) or "+qa" in local
                or "+probe" in local or n.upper().startswith("PROBE")):
            t.add(e)
    for r in c.execute("SELECT DISTINCT LOWER(user_email) FROM transactions WHERE type='tester_grant'"):
        t.add(r[0])
    try:
        for r in c.execute("SELECT DISTINCT LOWER(claimed_by) FROM tester_invites WHERE claimed_by IS NOT NULL"):
            t.add(r[0])
    except sqlite3.OperationalError:
        pass
    t |= _lines("testers.txt")
    for r in c.execute("SELECT DISTINCT LOWER(seller_email) e, title FROM listings"):
        if rule_tester(r["e"], "", r["title"]):
            t.add(r["e"])
    t -= _lines("real.txt")
    t.discard(None)
    return t


def real_listing_sql(alias="l"):
    return ("COALESCE({a}.is_demo,0)=0 AND COALESCE({a}.super_example,0)=0 AND COALESCE({a}.import_source,'')='' "
            "AND UPPER(COALESCE({a}.title,'')) NOT LIKE '%QA TEST%'").format(a=alias)


# ------------------------------------------------------------------ subscriptions + onboarding page
def gather(c):
    T = tester_set(c)
    nowiso = now().strftime("%Y-%m-%d %H:%M:%S")
    users = [dict(r) for r in c.execute(
        "SELECT LOWER(email) email, COALESCE(seller_tier,'free') tier, created_at, billing_period_end, auto_renew, "
        "renewal_failed_at, pending_downgrade_tier, closed_at FROM users")]
    listings = [dict(r) for r in c.execute(
        "SELECT id, LOWER(seller_email) email, category, city, listing_status st, created_at, published_at, title "
        "FROM listings l WHERE " + real_listing_sql())]
    by_email = {}
    for l in listings:
        by_email.setdefault(l["email"], []).append(l)
    tiers = {k: {"real_users": 0, "test_users": 0, "real_listers_live": 0, "real_listers_any": 0, "real_live_listings": 0,
                 "paid_active": 0, "auto_renew": 0, "renew_failed": 0, "downgrade": 0} for k, _, _ in TIERS}
    for u in users:
        if u["closed_at"]:
            continue
        k = u["tier"] if u["tier"] in tiers else "free"
        row = tiers[k]
        if u["email"] in T:
            row["test_users"] += 1
            continue
        row["real_users"] += 1
        ls = by_email.get(u["email"], [])
        live = [l for l in ls if l["st"] == "live"]
        if ls:
            row["real_listers_any"] += 1
        if live:
            row["real_listers_live"] += 1
            row["real_live_listings"] += len(live)
        if k != "free" and (u["billing_period_end"] or "") >= nowiso[:10]:
            row["paid_active"] += 1
            if int(u["auto_renew"] or 0) == 1:
                row["auto_renew"] += 1
        if u["renewal_failed_at"]:
            row["renew_failed"] += 1
        if u["pending_downgrade_tier"]:
            row["downgrade"] += 1
    tierof = {u["email"]: (u["tier"] if u["tier"] in tiers else "free") for u in users}
    recent = []
    for e, ls in by_email.items():
        if e in T:
            continue
        for l in ls:
            recent.append({"who": mask(e), "tier": tierof.get(e, "(no account)"), "cat": l["category"], "city": l["city"],
                           "status": l["st"], "at": l["created_at"], "title": (l["title"] or "")[:48]})
    recent.sort(key=lambda r: r["at"] or "", reverse=True)
    # onboarding: sessions in the last 30 days, humans only, testers out where we know the address
    since = (now() - datetime.timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S")
    live_real = [l for l in listings if l["st"] == "live" and l["email"] not in T and l["created_at"]]
    sess = {}
    for r in c.execute("SELECT sid, LOWER(COALESCE(email,'')) email, COALESCE(src,'') src, step, created_at FROM onboard_steps "
                       "WHERE COALESCE(bot,0)=0 AND created_at >= ? ORDER BY id", (since,)):
        s = sess.setdefault(r["sid"], {"email": "", "src": r["src"], "steps": set(), "first": r["created_at"], "handover": []})
        if r["step"] == "q_handover":
            s["handover"].append(r["created_at"])
        if r["email"]:
            s["email"] = r["email"]
        if r["src"] and not s["src"]:
            s["src"] = r["src"]
        s["steps"].add(r["step"])
    def group(src):
        s = src.lower()
        if s.startswith("sms"):
            return "SMS"
        if s.startswith(("em", "mail", "wave", "cl-")) or "email" in s:
            return "E-mail"
        if s.startswith("p-") or s.startswith("promo"):
            return "Promoter"
        return "Direct / other"
    stages = [("Opened the link", lambda st: True),
              ("Started step 1", lambda st: bool(st & {"q_step_1", "step1", "sf_step_1"})),
              ("Saved a draft", lambda st: bool(st & {"q_draft", "draft"})),
              ("Reached hand-over / sign-in", lambda st: bool(st & {"q_handover", "q_signin", "handover"})),
              ("Advert live", None)]
    funnel = {}
    for sid, s in sess.items():
        if s["email"] and s["email"] in T:
            continue
        g = group(s["src"])
        row = funnel.setdefault(g, [0] * len(stages))
        for i, (_, fn) in enumerate(stages):
            if fn is None:
                # LIVE-LINK-1: Quick creates the advert at the hand-over (same second), so a session is 'live' when a
                # real advert that is live now was created within 2 minutes of one of its hand-overs.
                ok = bool(s["steps"] & {"q_live", "q_published", "published"}) or any(
                    abs((_ts(l["created_at"]) - _ts(h)).total_seconds()) <= 120 for h in s["handover"] for l in live_real)
            else:
                ok = fn(s["steps"])
            if ok:
                row[i] += 1
    daily = {}
    for u in users:
        if u["email"] in T or not u["created_at"]:
            continue
        d = str(u["created_at"])[:10]
        if d >= (now() - datetime.timedelta(days=14)).strftime("%Y-%m-%d"):
            daily.setdefault(d, [0, 0])[0] += 1
    for l in listings:
        if l["email"] in T or not l["created_at"]:
            continue
        d = str(l["created_at"])[:10]
        if d >= (now() - datetime.timedelta(days=14)).strftime("%Y-%m-%d"):
            daily.setdefault(d, [0, 0])[1] += 1
    events = [dict(r) for r in c.execute("SELECT email, event, tier, created_at FROM subscription_events ORDER BY id DESC LIMIT 15")]
    prices = {}
    try:
        for r in c.execute("SELECT tier, amount_kobo FROM paystack_plans WHERE active=1"):
            prices[r["tier"]] = (r["amount_kobo"] or 0) / 100.0
    except sqlite3.OperationalError:
        pass
    return {"tiers": tiers, "recent": recent[:25], "funnel": funnel, "stages": [s for s, _ in stages], "daily": daily,
            "events": events, "prices": prices, "testers": len(T)}


CSS = """:root{--bg:#f4f6fa;--card:#fff;--ink:#1c2a3a;--mut:#64748b;--line:#e2e8f0;--navy:#13294b;--red:#c0392b;--amb:#d08a1e;--grn:#2e9e6b;--grey:#94a3b8}
@media (prefers-color-scheme:dark){:root{--bg:#0f1720;--card:#17212b;--ink:#e8eef3;--mut:#93a4b3;--line:#263241;--navy:#cfe0ff}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,Segoe UI,sans-serif;padding:16px;max-width:1100px;margin:auto}
h1{font-size:21px;margin:4px 0;color:var(--navy)}h2{font-size:16px;margin:22px 0 8px;color:var(--navy)}.mut{color:var(--mut);font-size:13px}
.k{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px}.kc{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px}
.kc b{display:block;font-size:24px}.t{width:100%;border-collapse:collapse;background:var(--card);border-radius:10px;overflow:hidden;font-size:14px}
.t th,.t td{padding:7px 9px;border-bottom:1px solid var(--line);text-align:left}.t th{font-size:12px;color:var(--mut);font-weight:600}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;vertical-align:middle}
.bar{height:12px;border-radius:6px;background:var(--line);overflow:hidden}.bar span{display:block;height:100%}
.pill{display:inline-block;font-size:11px;font-weight:700;padding:2px 8px;border-radius:9px;color:#fff}
a.back{font-size:13px;text-decoration:none;color:var(--navy)}.wrap{overflow-x:auto}"""


def render_page(g):
    T = g["tiers"]
    tot = lambda k: sum(v[k] for v in T.values())
    mrr = sum(T[k]["paid_active"] * g["prices"].get(k, 0) for k in T)
    h = ["<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>",
         "<title>Subscriptions & Onboarding</title><style>%s</style></head><body>" % CSS,
         "<a class='back' href='cockpit.html'>&larr; Ops Dashboard</a><h1>Subscriptions, onboarding and real listers</h1>",
         "<div class='mut'>Built %s from the live database (read-only). Testers are left out of every 'real' number "
         "(%d tester accounts: superusers, tester grants, David's own addresses, probe and QA accounts).</div>" % (esc(sast()), g["testers"]),
         "<h2>At a glance</h2><div class='k'>"]
    for lab, val, col in [("Real users", tot("real_users"), "var(--navy)"), ("Real listers with a live advert", tot("real_listers_live"), "var(--grn)"),
                          ("Real listers (any advert)", tot("real_listers_any"), "var(--grn)"), ("Real live adverts", tot("real_live_listings"), "var(--grn)"),
                          ("Paying subscribers", tot("paid_active"), "#7b5cc4"), ("Monthly income from plans", "R%.0f" % mrr if g["prices"] else "NOT MEASURED", "#7b5cc4"),
                          ("Renewals that failed", tot("renew_failed"), "var(--red)" if tot("renew_failed") else "var(--grey)")]:
        h.append("<div class='kc'><span class='mut'>%s</span><b style='color:%s'>%s</b></div>" % (esc(lab), col, esc(val)))
    h.append("</div><h2>By subscription type</h2><div class='wrap'><table class='t'><tr><th>Plan</th><th>Real users</th><th>Testers</th>"
             "<th>Real listers, live advert</th><th>Real listers, any advert</th><th>Real live adverts</th><th>Paying now</th>"
             "<th>Auto-renew on</th><th>Renewal failed</th><th>Downgrade waiting</th></tr>")
    for k, lab, col in TIERS:
        r = T[k]
        h.append("<tr><td><span class='dot' style='background:%s'></span>%s</td>%s</tr>" % (col, esc(lab), "".join(
            "<td>%s</td>" % ("-" if (k == "free" and f in ("paid_active", "auto_renew")) else r[f]) for f in
            ("real_users", "test_users", "real_listers_live", "real_listers_any", "real_live_listings", "paid_active", "auto_renew", "renew_failed", "downgrade"))))
    h.append("</table></div><div class='mut'>Agency counts each agency seat. 'Paying now' = a paid plan whose period has not ended.</div>")
    # funnel
    h.append("<h2>Onboarding: where new people get to (last 30 days, humans only)</h2>")
    if not g["funnel"]:
        h.append("<div class='mut'>No onboarding sessions recorded in the last 30 days.</div>")
    cols = ["#6b8bb3", "#4f7fd1", "#2e9e6b", "#d08a1e", "#7b5cc4"]
    for src, row in sorted(g["funnel"].items(), key=lambda kv: -kv[1][0]):
        top = max(row[0], 1)
        h.append("<div class='kc' style='margin-bottom:10px'><b style='font-size:15px'>%s</b>" % esc(src))
        for i, (lab, n) in enumerate(zip(g["stages"], row)):
            h.append("<div style='display:flex;gap:8px;align-items:center;margin:4px 0'><div style='width:200px' class='mut'>%s</div>"
                     "<div class='bar' style='flex:1'><span style='width:%d%%;background:%s'></span></div><div style='width:70px;text-align:right'>%d%s</div></div>"
                     % (esc(lab), round(100 * n / top), cols[i], n, "" if i == 0 else " (%d%%)" % round(100 * n / top)))
        h.append("</div>")
    # daily
    h.append("<h2>New real sign-ups and adverts per day (last 14 days)</h2><div class='wrap'><table class='t'><tr><th>Day</th><th>New real accounts</th><th>New real adverts</th></tr>")
    for d in sorted(g["daily"], reverse=True):
        a, b = g["daily"][d]
        h.append("<tr><td>%s</td><td>%d</td><td>%d</td></tr>" % (esc(d), a, b))
    h.append("</table></div>")
    # recent listers
    h.append("<h2>Latest adverts by real listers</h2><div class='wrap'><table class='t'><tr><th>When</th><th>Who</th><th>Plan</th><th>Category</th><th>City</th><th>Status</th><th>Title</th></tr>")
    stc = {"live": "var(--grn)", "draft": "var(--grey)", "paused": "var(--amb)", "archived": "var(--grey)"}
    for r in g["recent"]:
        h.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td><span class='pill' style='background:%s'>%s</span></td><td>%s</td></tr>" % (
            esc(str(r["at"])[:16]), esc(r["who"]), esc(r["tier"]), esc(r["cat"]), esc(r["city"]), stc.get(r["status"], "var(--grey)"), esc(r["status"]), esc(r["title"])))
    h.append("</table></div><h2>Latest subscription events</h2>")
    if not g["events"]:
        h.append("<div class='mut'>No subscription events yet (no paid plan has been bought, renewed or cancelled).</div>")
    else:
        h.append("<div class='wrap'><table class='t'><tr><th>When</th><th>Who</th><th>Event</th><th>Plan</th></tr>")
        for e in g["events"]:
            h.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (esc(str(e["created_at"])[:16]), esc(mask(e["email"])), esc(e["event"]), esc(e["tier"])))
        h.append("</table></div>")
    h.append("<p class='mut'>Rebuilt every hour by ops/guard/ops_guard.py (OPS-GUARD-1). Addresses are masked; nothing here can change data.</p></body></html>")
    return "".join(h)


def cmd_page():
    c = db()
    g = gather(c)
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, "subscriptions.html.tmp")
    open(tmp, "w", encoding="utf-8").write(render_page(g))
    os.replace(tmp, os.path.join(OUT, "subscriptions.html"))
    jsave(os.path.join(STATE, "subscriptions.json"), {"at": now().isoformat() + "Z", "tiers": g["tiers"], "funnel": g["funnel"]})
    print("page: wrote", os.path.join(OUT, "subscriptions.html"), {k: v["real_listers_live"] for k, v in g["tiers"].items()})
    return g


# ------------------------------------------------------------------ env + mail (the QA Bot's own helpers)
def env():
    try:
        import qa_bot
        return qa_bot.load_env()
    except Exception:
        out = {}
        for f in ("/etc/environment", "/etc/marketsquare/secrets.env"):
            try:
                for ln in open(f, encoding="utf-8"):
                    if "=" in ln and not ln.strip().startswith("#"):
                        k, v = ln.strip().split("=", 1)
                        out[k.replace("export ", "").strip()] = v.strip().strip('"').strip("'")
            except OSError:
                pass
        return out


def mail(E, subject, body):
    try:
        import qa_bot
        qa_bot.email(E, subject, body)
    except Exception as e:
        print("mail failed:", e)


# ------------------------------------------------------------------ money
def paystack_success(key, days=120):
    refs, page = {}, 1
    frm = (now() - datetime.timedelta(days=days)).strftime("%Y-%m-%dT00:00:00Z")
    while page < 50:
        q = urllib.parse.urlencode({"status": "success", "perPage": 100, "page": page, "from": frm})
        req = urllib.request.Request("https://api.paystack.co/transaction?" + q, headers={"Authorization": "Bearer " + key, "User-Agent": "TrustSquare-OpsGuard/1.0", "Accept": "application/json"})
        d = json.load(urllib.request.urlopen(req, timeout=30))
        for t in d.get("data") or []:
            refs[t.get("reference")] = {"amount": (t.get("amount") or 0) / 100.0, "at": t.get("paid_at") or t.get("created_at"),
                                        "email": ((t.get("customer") or {}).get("email") or "").lower(), "plan": bool(t.get("plan"))}
        meta = d.get("meta") or {}
        if page >= int(meta.get("pageCount") or 1):
            break
        page += 1
    return refs


def cmd_money(E):
    c = db()
    res = {"check": "money", "status": "GREEN", "findings": [], "numbers": {}}
    ours = {}
    for r in c.execute("SELECT user_email, amount, description, created_at FROM transactions WHERE type='topup'"):
        m = re.search(r"ref\s+(\S+)", r["description"] or "")
        if m:
            ours[m.group(1)] = {"what": "Tuppence top-up %sT" % r["amount"], "email": (r["user_email"] or "").lower(), "at": r["created_at"]}
    for r in c.execute("SELECT reference, email, event, tier, created_at FROM subscription_events WHERE COALESCE(reference,'')<>''"):
        ours.setdefault(r["reference"], {"what": "plan %s (%s)" % (r["tier"], r["event"]), "email": (r["email"] or "").lower(), "at": r["created_at"]})
    key = E.get("PAYSTACK_SECRET_KEY") or ""
    mode = "live" if key.startswith("sk_live") else ("test" if key.startswith("sk_test") else "?")
    res["numbers"]["paystack_mode"] = mode
    base = jload(os.path.join(STATE, "money_baseline.json"), None)
    if not key:
        res["status"] = "NOT MEASURED"
        res["findings"].append("No Paystack key on the server, so payments could not be compared.")
    else:
        try:
            ps = paystack_success(key)
        except Exception as e:
            ps = None
            res["status"] = "NOT MEASURED"
            res["findings"].append("Paystack could not be read tonight (%s)." % type(e).__name__)
        if ps is not None:
            paid_not_ours = sorted(r for r in ps if r not in ours)
            ours_not_paid = sorted(r for r in ours if r not in ps and (ours[r]["at"] or "") >= (now() - datetime.timedelta(days=110)).strftime("%Y-%m-%d"))
            res["numbers"].update({"paystack_success_120d": len(ps), "paystack_rand_120d": round(sum(v["amount"] for v in ps.values()), 2),
                                   "our_paid_records": len(ours), "paid_not_recorded": len(paid_not_ours), "recorded_not_paid": len(ours_not_paid)})
            if base is None:
                base = {"at": now().isoformat() + "Z", "paid_not_ours": paid_not_ours, "ours_not_paid": ours_not_paid, "mode": mode}
                jsave(os.path.join(STATE, "money_baseline.json"), base)
                res["findings"].append("First run: %d old difference(s) recorded as the starting point (mode %s); from tonight only NEW differences raise the alarm."
                                       % (len(paid_not_ours) + len(ours_not_paid), mode))
            new_a = [r for r in paid_not_ours if r not in set(base.get("paid_not_ours", []))]
            new_b = [r for r in ours_not_paid if r not in set(base.get("ours_not_paid", []))]
            for r in new_a:
                res["status"] = "RED"
                res["findings"].append("Paid on Paystack but NOT in our records: R%.2f from %s on %s (ref %s) -- someone paid and may not have received it."
                                       % (ps[r]["amount"], mask(ps[r]["email"]), str(ps[r]["at"])[:16], r))
            for r in new_b:
                res["status"] = "RED"
                res["findings"].append("In our records but NOT a successful Paystack payment: %s for %s on %s (ref %s) -- credit given without money."
                                       % (ours[r]["what"], mask(ours[r]["email"]), str(ours[r]["at"])[:16], r))
    neg = c.execute("SELECT LOWER(user_email) e, SUM(amount) b FROM transactions GROUP BY 1 HAVING SUM(amount) < 0").fetchall()
    nb = jload(os.path.join(STATE, "negative_baseline.json"), None)
    if nb is None:
        nb = sorted(r["e"] for r in neg)
        jsave(os.path.join(STATE, "negative_baseline.json"), nb)
        if nb:
            res["findings"].append("First run: %d account(s) already below zero recorded as known: %s." % (len(nb), ", ".join(mask(e) for e in nb)))
    res["numbers"]["accounts_below_zero"] = len(neg)
    for r in neg:
        if r["e"] in nb:
            continue
        res["status"] = "RED"
        res["findings"].append("Tuppence balance went below zero: %s has %s T." % (mask(r["e"]), r["b"]))
    types = {r[0] for r in c.execute("SELECT DISTINCT type FROM transactions")}
    unknown = sorted(t for t in types if t not in KNOWN_MONEY_TYPES)
    if unknown:
        if res["status"] == "GREEN":
            res["status"] = "AMBER"
        res["findings"].append("New kind of Tuppence entry nobody has reviewed yet: %s." % ", ".join(unknown))
    day = (now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    free = c.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE created_at >= ? AND type IN (%s) AND amount > 0"
                     % ",".join("?" * len(FREE_CREDIT_TYPES)), (day, *FREE_CREDIT_TYPES)).fetchone()[0]
    res["numbers"]["free_tuppence_24h"] = free
    if free > 200:
        if res["status"] == "GREEN":
            res["status"] = "AMBER"
        res["findings"].append("%s free Tuppence was handed out in the last 24 hours (grants, bonuses, test credit)." % free)
    return res


# ------------------------------------------------------------------ data exposure
def cmd_data():
    c = db()
    res = {"check": "data", "status": "GREEN", "findings": [], "numbers": {}}
    t0 = now()
    def cnt(sql, a):
        try:
            return c.execute(sql, a).fetchall()
        except sqlite3.OperationalError as e:
            res["findings"].append("Could not read: %s" % e)
            res["status"] = "NOT MEASURED"
            return []
    d1 = (t0 - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    d8 = (t0 - datetime.timedelta(days=8)).strftime("%Y-%m-%d %H:%M:%S")
    intro_today = cnt("SELECT LOWER(buyer_email) e, COUNT(*) n FROM intro_requests WHERE status IN ('accepted','completed','hired') "
                      "AND created_at >= ? GROUP BY 1", (d1,))
    intro_week = cnt("SELECT COUNT(*) FROM intro_requests WHERE status IN ('accepted','completed','hired') AND created_at >= ? AND created_at < ?", (d8, d1))
    buzz_today = cnt("SELECT LOWER(created_by) e, COUNT(*) n FROM buzz_pairs WHERE created_at >= ? GROUP BY 1", (d1,))
    buzz_week = cnt("SELECT COUNT(*) FROM buzz_pairs WHERE created_at >= ? AND created_at < ?", (d8, d1))
    users_today = cnt("SELECT COUNT(*) FROM users WHERE created_at >= ?", (d1,))
    users_week = cnt("SELECT COUNT(*) FROM users WHERE created_at >= ? AND created_at < ?", (d8, d1))
    tot_i = sum(r["n"] for r in intro_today)
    tot_b = sum(r["n"] for r in buzz_today)
    avg_i = (intro_week[0][0] if intro_week else 0) / 7.0
    avg_b = (buzz_week[0][0] if buzz_week else 0) / 7.0
    nu = users_today[0][0] if users_today else 0
    avg_u = (users_week[0][0] if users_week else 0) / 7.0
    res["numbers"] = {"contacts_opened_24h": tot_i + tot_b, "intros_24h": tot_i, "buzz_pairs_24h": tot_b,
                      "intros_7d_daily_avg": round(avg_i, 1), "buzz_7d_daily_avg": round(avg_b, 1), "signups_24h": nu, "signups_7d_daily_avg": round(avg_u, 1)}
    for r in intro_today:
        if r["n"] > 10:
            res["status"] = "RED"
            res["findings"].append("One account (%s) opened %d people's contact details through introductions in 24 hours." % (mask(r["e"]), r["n"]))
    for r in buzz_today:
        if r["n"] > 15:
            res["status"] = "RED"
            res["findings"].append("One account (%s) opened %d Buzz connections in 24 hours." % (mask(r["e"]), r["n"]))
    if tot_i + tot_b > max(20, 3 * (avg_i + avg_b)):
        if res["status"] == "GREEN":
            res["status"] = "AMBER"
        res["findings"].append("Contacts opened in 24 hours (%d) is more than three times the daily average (%.1f)." % (tot_i + tot_b, avg_i + avg_b))
    if nu > max(30, 3 * avg_u):
        if res["status"] == "GREEN":
            res["status"] = "AMBER"
        res["findings"].append("Sign-ups in 24 hours (%d) are more than three times the daily average (%.1f) -- check for robot sign-ups." % (nu, avg_u))
    return res


# ------------------------------------------------------------------ drift + independent review
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def watched_files():
    out = {}
    for root, dirs, files in os.walk(CL):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", "logs", "data", ".git", "node_modules", "previews", "output")]
        for f in files:
            if f.endswith((".py", ".sh", ".json")) and ".bak" not in f and not f.endswith(".tmp"):
                p = os.path.join(root, f)
                if os.path.getsize(p) < 2_000_000:
                    out["citylauncher/" + os.path.relpath(p, CL)] = p
    for d in ("/etc/systemd/system",):
        for f in sorted(os.listdir(d)):
            if f.endswith((".service", ".timer")) and os.path.isfile(os.path.join(d, f)):
                out["systemd/" + f] = os.path.join(d, f)
    out["sms/ARM.json"] = "/var/lib/citylauncher-sms/ARM.json"
    return {k: v for k, v in out.items() if os.path.isfile(v)}


REVIEW_EXTRA = ("These changes are to the outreach (CityLauncher) e-mail/SMS sender and the server's scheduled jobs, made "
                "outside the normal git release. Also flag: a send that ignores STOP or opt-out lists, texting or e-mailing "
                "outside sociable hours, removing a spend cap, or sending personal data to a new place. ")


def cmd_drift(E, review=True):
    res = {"check": "drift", "status": "GREEN", "findings": [], "numbers": {}, "review": None}
    # (a) live MarketSquare code == released source
    man = os.path.join(SRC, "ops", "autodeploy", "deploy_manifest.txt")
    diffs, checked = [], 0
    try:
        for ln in open(man, encoding="utf-8"):
            if "|" not in ln or ln.strip().startswith("#"):
                continue
            s, d = [x.strip() for x in ln.split("|", 1)]
            if not s.endswith((".py", ".sh")):
                continue
            sp, dp = os.path.join(SRC, s), os.path.join(LIVE, d)
            if not os.path.isfile(sp):
                continue
            checked += 1
            if not os.path.isfile(dp):
                diffs.append("%s is missing on the live server" % d)
            elif sha(sp) != sha(dp):
                diffs.append("%s on the live server differs from the released code (changed by hand?)" % d)
        res["numbers"]["marketsquare_files_checked"] = checked
    except OSError:
        res["status"] = "NOT MEASURED"
        res["findings"].append("The release manifest could not be read, so live code was not compared.")
    if diffs:
        res["status"] = "RED"
        res["findings"] += diffs[:20]
    # (b) CityLauncher + timers: what changed since the last nightly, reviewed independently
    snapdir = os.path.join(STATE, "snapshot")
    snap = jload(os.path.join(STATE, "snapshot.json"), None)
    cur = {k: sha(p) for k, p in watched_files().items()}
    res["numbers"]["outreach_and_timer_files_watched"] = len(cur)
    if snap is None:
        res["findings"].append("First run: %d outreach and timer files recorded as the starting point." % len(cur))
        changed = []
    else:
        changed = sorted(k for k in cur if snap.get(k) != cur[k])
        removed = sorted(k for k in snap if k not in cur)
        for k in removed:
            res["findings"].append("Removed since last night: %s" % k)
        for k in changed:
            res["findings"].append("Changed since last night: %s" % k)
        res["numbers"]["changed_since_last_night"] = len(changed) + len(removed)
        if changed or removed:
            if res["status"] == "GREEN":
                res["status"] = "AMBER"
    if changed and review:
        parts = []
        files = watched_files()
        for k in changed:
            old = os.path.join(snapdir, k)
            a = open(old, encoding="utf-8", errors="replace").read().splitlines() if os.path.isfile(old) else []
            b = open(files[k], encoding="utf-8", errors="replace").read().splitlines()
            parts.append("\n".join(difflib.unified_diff(a, b, "a/" + k, "b/" + k, lineterm="", n=3)))
        diff = "\n".join(parts)
        key = E.get("OPENAI_API_KEY")
        if not key:
            res["review"] = {"verdict": "NOT MEASURED", "findings": [], "note": "no OpenAI key on the server"}
        else:
            try:
                import qa_bot
                capped = diff[:120000] + ("\n...[truncated]" if len(diff) > 120000 else "")
                data, cost = qa_bot.openai_chat(key, qa_bot.REVIEW_SYSTEM + "\n" + REVIEW_EXTRA, capped, timeout=600)
                data["cost"] = cost
                res["review"] = data
            except Exception as e:
                res["review"] = {"verdict": "NOT MEASURED", "findings": [], "note": "review could not run: %s" % e}
        v = (res["review"] or {}).get("verdict")
        if v == "RED":
            res["status"] = "RED"
    # roll the snapshot forward (the review covered these changes)
    files = watched_files()
    for k, p in files.items():
        dst = os.path.join(snapdir, k)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        try:
            shutil.copy2(p, dst)
        except OSError:
            pass
    jsave(os.path.join(STATE, "snapshot.json"), cur)
    return res


# ------------------------------------------------------------------ nightly report
COL = {"GREEN": "#2e9e6b", "AMBER": "#d08a1e", "RED": "#c0392b", "NOT MEASURED": "#94a3b8"}
TITLE = {"money": "Money: Paystack vs our records", "data": "Data: contact details opened", "drift": "Config: code and timer changes"}


def render_guard(results, g):
    h = ["<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>",
         "<title>Checks & Balances</title><style>%s</style></head><body><a class='back' href='cockpit.html'>&larr; Ops Dashboard</a>" % CSS,
         "<h1>Checks and balances (nightly)</h1><div class='mut'>Last run %s. Green = checked and fine; amber = look at it; red = e-mailed to David; "
         "grey = could not be measured (never shown as green).</div>" % esc(sast())]
    for r in results:
        h.append("<h2><span class='pill' style='background:%s'>%s</span> %s</h2>" % (COL.get(r["status"], "#94a3b8"), esc(r["status"]), esc(TITLE[r["check"]])))
        if r["numbers"]:
            h.append("<div class='k'>" + "".join("<div class='kc'><span class='mut'>%s</span><b style='font-size:18px'>%s</b></div>" % (esc(k.replace("_", " ")), esc(v))
                                                for k, v in r["numbers"].items()) + "</div>")
        if r["findings"]:
            h.append("<ul>" + "".join("<li>%s</li>" % esc(f) for f in r["findings"][:40]) + "</ul>")
        else:
            h.append("<div class='mut'>Nothing to report.</div>")
        rv = r.get("review")
        if rv:
            h.append("<div class='kc'><b style='font-size:14px'>Independent review (OpenAI): <span style='color:%s'>%s</span></b>%s%s</div>" % (
                COL.get(rv.get("verdict"), "#94a3b8"), esc(rv.get("verdict")), "<div class='mut'>%s</div>" % esc(rv.get("note")) if rv.get("note") else "",
                "<ul>" + "".join("<li><b>%s</b> %s: %s</li>" % (esc(f.get("severity")), esc(f.get("file")), esc(f.get("summary"))) for f in rv.get("findings", [])) + "</ul>"))
    h.append("<p class='mut'>ops/guard/ops_guard.py nightly (OPS-GUARD-1, RUL-230). It reads; it never changes data.</p></body></html>")
    return "".join(h)


def cmd_nightly():
    E = env()
    g = cmd_page()
    results = []
    for name, fn in (("money", lambda: cmd_money(E)), ("data", cmd_data), ("drift", lambda: cmd_drift(E))):
        try:
            results.append(fn())
        except Exception as e:
            results.append({"check": name, "status": "NOT MEASURED", "findings": ["The check crashed: %r" % e], "numbers": {}})
    page = render_guard(results, g)
    tmp = os.path.join(OUT, "guard.html.tmp")
    open(tmp, "w", encoding="utf-8").write(page)
    os.replace(tmp, os.path.join(OUT, "guard.html"))
    jsave(os.path.join(STATE, "guard_last.json"), {"at": now().isoformat() + "Z", "results": results})
    for r in results:
        print("%-6s %-12s %s" % (r["check"], r["status"], " | ".join(r["findings"][:3])[:300]))
    red = [r for r in results if r["status"] == "RED"]
    if red and "--no-mail" not in sys.argv:
        mail(E, "TrustSquare checks: %s RED" % ", ".join(r["check"] for r in red), page)
    return 0


if __name__ == "__main__":
    cmd = (sys.argv[1:] or ["page"])[0]
    if cmd == "page":
        cmd_page()
    elif cmd == "money":
        print(json.dumps(cmd_money(env()), indent=1, default=str))
    elif cmd == "data":
        print(json.dumps(cmd_data(), indent=1, default=str))
    elif cmd == "drift":
        print(json.dumps(cmd_drift(env(), review="--no-review" not in sys.argv), indent=1, default=str))
    elif cmd == "nightly":
        sys.exit(cmd_nightly())
    else:
        sys.exit("usage: ops_guard.py page|money|data|drift|nightly")
