#!/usr/bin/env python3
"""prove_auto_renew.py -- AUTO-RENEW-1 (RUL-224, 12 Oct 2026): EXECUTE the renewal lane against the real
bea_main.py, imported with a throwaway SQLite file (never the live database).

Paystack is an in-process stand-in: payments.requests is replaced by a fake that keeps plans, transactions
and subscriptions in memory and records every request it is sent. No network, no money. The webhook events
are real HTTP POSTs to /payment/webhook, signed HMAC-SHA512 with the test key, through the security gate.

What it proves:
  A  switch OFF: the plan checkout, the verify answer, the subscription answer, the webhook and the lapse
     pass are today's -- same Paystack request, same answers, no subscription, no new write
  B  arming makes each plan once (and adopts a plan that already exists)
  C  tick box ON opens a subscription; tick box OFF or a non-card payment is the one-off payment
  D  a renewal extends the paid period by 30 days from the previous end, grants the month's Tuppence once,
     and a replayed reference is ignored
  E  a failed renewal tells her once (one Buzz + one email) and the plan ends as RUL-201 ends it
  F  subscription.disable / subscription.not_renew mark renewal off and change nothing else
  G  Cancel renewal acts only as the signed-in session, stops the subscription, and the paid days run on
  H  nobody is billed for two plans; a move to Free or a closed account stops the subscription

What it does NOT prove: Paystack itself. The stand-in follows Paystack's published API and event shapes;
the first real subscription on a Paystack test key is the one step this script can not take.

Run: python3 scripts/prove_auto_renew.py      (needs fastapi, boto3, pyjwt, pillow, httpx)
"""
import os, sys, json, hmac, hashlib, tempfile, asyncio, re
from datetime import datetime, timedelta, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO); sys.path.insert(0, REPO)
SECRET = "sk_test_" + "prove" + os.urandom(8).hex()          # a made-up test key, never a real one
os.environ.setdefault("MS_API_KEY", "k"); os.environ.setdefault("MS_ADMIN_KEY", "adm")
os.environ.setdefault("MS_JWT_SECRET", "test-only-" + os.urandom(8).hex())
os.environ["TUPPENCE_MONTHLY_ENABLED"] = "1"
os.environ["PAYSTACK_SECRET_KEY"] = SECRET
os.environ["ALLOW_TEST_PAYMENTS"] = "1"
for k in ("RESEND_API_KEY", "PAYSTACK_WEBHOOK_SECRET", "GMAIL_APP_PASSWORD"):
    os.environ.pop(k, None)
_mk = os.makedirs
os.makedirs = lambda p, *a, **k: None if str(p).startswith("/var/www") else _mk(p, *a, **k)
import starlette.staticfiles as _sf
_i = _sf.StaticFiles.__init__
def _i2(self, *a, **k):
    k["check_dir"] = False; return _i(self, *a, **k)
_sf.StaticFiles.__init__ = _i2
import database
DB = os.path.join(tempfile.mkdtemp(), "autorenew.db"); database.DB_PATH = DB
os.environ["MS_DB"] = os.path.join(os.path.dirname(DB), "flights.db")
import bea_main as b, payments, launch_redemption
from fastapi.testclient import TestClient
import jwt as _jwt

fails = []
def check(ok, msg):
    print(("  [OK] " if ok else "  [X]  ") + msg)
    if not ok: fails.append(msg)
def q(sql, *p):
    c = database.get_db(); r = c.execute(sql, p).fetchall(); c.close(); return r
def x(sql, *p):
    c = database.get_db(); c.execute(sql, p); c.commit(); c.close()
def iso(dt): return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
NOW = datetime.now(timezone.utc).replace(microsecond=0)


# ── the Paystack stand-in ────────────────────────────────────────────────────────────────────────
class _Resp:
    def __init__(self, body): self._b = body; self.status_code = 200
    def json(self): return self._b

class FakePaystack:
    def __init__(self):
        self.plans, self.tx, self.subs, self.calls, self.down, self.n = [], {}, {}, [], False, 0
    def _next(self): self.n += 1; return self.n
    def post(self, url, json=None, headers=None, timeout=None): return self.request("POST", url, json=json)
    def get(self, url, params=None, headers=None, timeout=None): return self.request("GET", url, params=params)
    def request(self, method, url, json=None, params=None, headers=None, timeout=None):
        path = url.split("api.paystack.co", 1)[-1]
        self.calls.append((method, path, json))
        if self.down:
            raise ConnectionError("stand-in: Paystack unreachable")
        if method == "POST" and path == "/transaction/initialize":
            self.tx[json["reference"]] = {"payload": dict(json), "paid_at": None}
            return _Resp({"status": True, "data": {"authorization_url": "https://checkout.paystack.test/" + json["reference"],
                                                   "reference": json["reference"]}})
        if method == "GET" and path.startswith("/transaction/verify/"):
            ref = path.rsplit("/", 1)[-1]; t = self.tx.get(ref)
            if not t or not t["paid_at"]:
                return _Resp({"status": True, "data": {"status": "abandoned", "reference": ref}})
            return _Resp({"status": True, "data": self.charge_data(ref)})
        if method == "POST" and path == "/plan":
            p = {"plan_code": "PLN_%04d" % self._next(), "name": json["name"], "amount": json["amount"],
                 "interval": json["interval"], "currency": json.get("currency", "ZAR")}
            self.plans.append(p); return _Resp({"status": True, "data": p})
        if method == "GET" and path == "/plan":
            return _Resp({"status": True, "data": list(self.plans)})
        if method == "GET" and path.startswith("/customer/"):
            em = path.rsplit("/", 1)[-1].replace("%40", "@")
            subs = [dict(s, plan=s["plan_id"]) for s in self.subs.values() if s["email"] == em]   # plan as a bare id, as the customer record can carry it
            return _Resp({"status": True, "data": {"email": em, "subscriptions": subs}})
        if method == "GET" and path.startswith("/subscription/"):
            s = self.subs.get(path.rsplit("/", 1)[-1])
            if not s: return _Resp({"status": False, "message": "Subscription not found"})
            return _Resp({"status": True, "data": dict(s, plan={"plan_code": s["plan_code"]}, customer={"email": s["email"]})})
        if method == "POST" and path in ("/subscription/disable", "/subscription/enable"):
            s = self.subs.get(json.get("code"))
            if not s or s["email_token"] != json.get("token"):
                return _Resp({"status": False, "message": "Subscription with code not found or already inactive"})
            if path.endswith("disable"):
                if s["status"] != "active":
                    return _Resp({"status": False, "message": "Subscription with code not found or already inactive"})
                s["status"] = "non-renewing"; return _Resp({"status": True, "message": "Subscription disabled successfully"})
            if s["status"] != "non-renewing":
                return _Resp({"status": False, "message": "Subscription can not be enabled"})
            s["status"] = "active"; return _Resp({"status": True, "message": "Subscription enabled successfully"})
        return _Resp({"status": False, "message": "stand-in: no such endpoint " + path})
    # helpers the proof drives
    def charge_data(self, ref):
        t = self.tx[ref]; p = t["payload"]; plan = p.get("plan")
        return {"status": "success", "reference": ref, "amount": (self.plan(plan)["amount"] if plan else p["amount"]),
                "currency": "ZAR", "paid_at": t["paid_at"], "channel": "card", "metadata": p.get("metadata") or {},
                "customer": {"id": 7, "email": p["email"], "customer_code": "CUS_x"},
                "plan": plan or None, "plan_object": ({"plan_code": plan} if plan else {}),
                "authorization": {"reusable": True, "channel": "card"}}
    def plan(self, code): return next(p for p in self.plans if p["plan_code"] == code)
    def pay(self, ref, when=None):
        """The customer pays on Paystack's page. With a plan, Paystack opens the subscription."""
        t = self.tx[ref]; t["paid_at"] = iso(when or NOW); plan = t["payload"].get("plan"); sub = None
        if plan:
            n = self._next()
            sub = {"subscription_code": "SUB_%04d" % n, "email_token": "tok%04d" % n, "status": "active",
                   "plan_code": plan, "plan_id": 9000 + n, "email": t["payload"]["email"],
                   "createdAt": iso(when or NOW), "next_payment_date": iso((when or NOW) + timedelta(days=30))}
            self.subs[sub["subscription_code"]] = sub
        return sub
    def renewal(self, sub, ref, when, amount=None):
        p = self.plan(sub["plan_code"])
        return {"status": "success", "reference": ref, "amount": p["amount"] if amount is None else amount,
                "currency": "ZAR", "paid_at": iso(when), "channel": "card", "metadata": "",
                "customer": {"id": 7, "email": sub["email"], "customer_code": "CUS_x"},
                "plan": {"plan_code": sub["plan_code"], "name": p["name"]}, "authorization": {"reusable": True}}
    def disables(self): return [c for c in self.calls if c[1] == "/subscription/disable"]

PS = FakePaystack()
payments.requests = PS                                       # every Paystack call in payments.py goes to the stand-in

sent = {"email": [], "push": []}
b._send_system_email = lambda to, subj, html: (sent["email"].append((to, subj)) or "sent")
b._push_to_seller = lambda conn, em, title, body, timeout=8: (sent["push"].append((em, title)) or 1)

app = b.app
C = TestClient(app, raise_server_exceptions=False)
def cookie(email):
    return {"ts_user": _jwt.encode({"scope": "user", "sub": email, "iat": NOW, "exp": NOW + timedelta(hours=2)},
                                   b._JWT_SECRET, algorithm=b._JWT_ALGO)}
def hook(event, data):
    raw = json.dumps({"event": event, "data": data}).encode()
    sig = hmac.new(SECRET.encode(), raw, hashlib.sha512).hexdigest()
    return C.post("/payment/webhook", content=raw, headers={"X-Paystack-Signature": sig, "Content-Type": "application/json"})
def mkuser(email, **cols):
    x("INSERT INTO users (email, eula_accepted_at) VALUES (?, ?)", email, iso(NOW))
    for k, v in cols.items():
        x("UPDATE users SET %s=? WHERE email=?" % k, v, email)
def user(email):
    return dict(q("SELECT seller_tier, slot_limit, billing_period_end, pending_downgrade_tier, auto_renew, "
                  "paystack_subscription_code AS code, paystack_email_token AS tok, renewal_failed_at FROM users WHERE email=?", email)[0])
def events(email=None, ev=None):
    sql, p = "SELECT email, event, tier, reference FROM subscription_events WHERE 1=1", []
    if email: sql += " AND email=?"; p.append(email)
    if ev: sql += " AND event=?"; p.append(ev)
    return q(sql, *p)
def bal(e): return q("SELECT COALESCE(SUM(amount),0) AS b FROM transactions WHERE user_email=?", e)[0]["b"]
def grants(e): return q("SELECT COUNT(*) AS n FROM transactions WHERE user_email=? AND type='monthly_allocation'", e)[0]["n"]
def init(email, tier, **kw):
    params = {"email": email, "tier": tier, "callback_url": "https://trustsquare.co/?ps_sub_return=1"}; params.update(kw)
    # RUL-227 (13 Oct 2026): the plan checkout acts as the signed-in session (route_policy user + bind(email)), as the app calls it
    return C.post("/payment/seller-subscription/initialize", params=params, cookies=cookie(email))
def verify(ref): return C.get("/payment/seller-subscription/verify", params={"reference": ref})
def switch(on): b.set_flags(b._FlagsUpdate(auto_renew=on, reason="prove_auto_renew"), _admin={"name": "prove"})
def last_init_payload(): return [c for c in PS.calls if c[1] == "/transaction/initialize"][-1][2]
ONEOFF_PAYLOAD_KEYS = ["amount", "callback_url", "currency", "email", "metadata", "reference"]
ONEOFF_META = {"type": "seller_subscription", "tier": "starter", "is_downgrade": False}
INIT_KEYS = ["status", "reference", "authorization_url", "tier", "label", "amount_rands", "is_downgrade"]
# the gate hides `email` from a caller who is not signed in (route_policy "hide"), which is how the app calls it on return
VERIFY_KEYS = ["status", "tier", "label", "slot_limit", "is_downgrade", "effective"]
SUB_KEYS = ["circle_caps_on", "circle_limit", "circle_allowance", "circle_used", "circle_resting", "listings_resting",
            "email", "seller_tier", "tier_label", "slot_limit", "slots_used", "slots_available", "draft_count",
            "pending_downgrade_tier", "billing_period_end", "usd_per_month"]

# ════════════════════════════════════════════════════════════════════════════════════════════════
print("A -- SWITCH OFF: the one-off 30-day payment of RUL-201 is untouched")
flags = C.get("/flags").json()
check(flags.get("auto_renew") is False and flags["effective"].get("auto_renew") is False and flags.get("auto_renew_tiers") == [],
      "the switch ships OFF and /flags says so (auto_renew false, no tiers ready)")
cols = {r[1]: r[4] for r in q("PRAGMA table_info(users)")}
check(all(c in cols for c in ("auto_renew", "paystack_subscription_code", "paystack_email_token", "renewal_failed_at"))
      and str(cols["auto_renew"]) == "1", "the four users columns exist; auto_renew defaults to 1")
mkuser("thandi@x.test")
r = init("thandi@x.test", "starter", auto_renew=1, channel="card")       # even with the tick box sent, OFF means one-off
pl = last_init_payload()
check(r.status_code == 200 and list(r.json().keys()) == INIT_KEYS, "initialize answers with exactly today's keys: %s" % list(r.json().keys()))
check(sorted(pl.keys()) == ONEOFF_PAYLOAD_KEYS and "plan" not in pl and "channels" not in pl,
      "Paystack is sent exactly today's request - no plan, no channels: %s" % sorted(pl.keys()))
check(pl["metadata"] == dict(ONEOFF_META, email="thandi@x.test") and pl["amount"] == 9000 and pl["currency"] == "ZAR",
      "the request carries today's metadata and R90.00 (9000)")
ref = r.json()["reference"]; PS.pay(ref)
calls_before = len(PS.calls)
v = verify(ref)
check(v.status_code == 200 and list(v.json().keys()) == VERIFY_KEYS and v.json()["effective"] == "immediate",
      "verify answers with exactly today's keys: %s" % list(v.json().keys()))
u = user("thandi@x.test")
check(u["seller_tier"] == "starter" and u["slot_limit"] == 10 and u["billing_period_end"] == iso(NOW + timedelta(days=30)),
      "the plan is applied for 30 days from the payment (%s)" % u["billing_period_end"])
check(u["code"] is None and u["tok"] is None and u["renewal_failed_at"] is None and u["auto_renew"] == 1,
      "no subscription is recorded and the renewal columns were not written")
check(len(PS.calls) - calls_before == 1 and PS.calls[-1][1].startswith("/transaction/verify/"),
      "verify made one Paystack call (the verify itself) and nothing else")
check(not PS.subs and not events(), "no subscription exists at Paystack and no renewal event was recorded")
s = C.get("/users/thandi@x.test/subscription", cookies=cookie("thandi@x.test"))
check(s.status_code == 200 and list(s.json().keys()) == SUB_KEYS, "the subscription answer has exactly today's keys")
g = C.get("/users/thandi@x.test", cookies=cookie("thandi@x.test"), headers={"X-Api-Key": "k"})
check(g.status_code == 200 and not any(k in g.json() for k in ("auto_renew", "paystack_subscription_code", "paystack_email_token", "renewal_failed_at")),
      "GET /users/{email} carries none of the new columns")
snap = user("thandi@x.test"); n_calls = len(PS.calls)
for ev, data in (("subscription.create", {"subscription_code": "SUB_x", "email_token": "t", "customer": {"email": "thandi@x.test"}, "plan": {"plan_code": "PLN_none"}}),
                 ("invoice.payment_failed", {"subscription": {"subscription_code": "SUB_x"}, "customer": {"email": "thandi@x.test"}}),
                 ("subscription.disable", {"subscription_code": "SUB_x"}), ("subscription.not_renew", {"subscription_code": "SUB_x"}),
                 ("charge.success", {"reference": "T_unknown_plan", "amount": 9000, "currency": "ZAR", "plan": {"plan_code": "PLN_none"},
                                     "customer": {"email": "thandi@x.test"}, "metadata": ""}),
                 ("subscription.expiring_cards", [{"subscription": {"subscription_code": "SUB_x"}}])):
    hr = hook(ev, data)
    check(hr.status_code == 200 and hr.json() == {"status": "ok"}, "webhook %s answers 200 ok and does nothing" % ev)
check(user("thandi@x.test") == snap and not events() and len(PS.calls) == n_calls, "after those six events her row is unchanged, nothing recorded, Paystack not called")
bad = C.post("/payment/webhook", content=b'{"event":"charge.success","data":{}}', headers={"X-Paystack-Signature": "00"})
check(bad.status_code == 400, "an unsigned webhook is still refused (400)")
x("UPDATE users SET billing_period_end=? WHERE email='thandi@x.test'", iso(NOW - timedelta(hours=1)))
b._apply_pending_downgrades()
u = user("thandi@x.test")
check(u["seller_tier"] == "free" and u["slot_limit"] == 2 and u["billing_period_end"] is None,
      "the lapse pass ends her plan the hour it is over, as RUL-201 rules (no wait for a one-off payment)")
check(not PS.disables() and not sent["email"] and not sent["push"] and not events(), "the lapse sent nothing and called nothing")

# ════════════════════════════════════════════════════════════════════════════════════════════════
print("B -- ARMING: each plan is made once, by maintenance, never by a checkout")
dry = b._auto_renew_sync_plans(dry_run=True)
check([p["state"] for p in dry["plans"]] == ["missing"] * 3 and not PS.plans, "a dry run reports three missing plans and makes none")
switch(True)
check(sorted((p["name"], p["amount"], p["interval"], p["currency"]) for p in PS.plans) ==
      [("TrustSquare Agency Pro seat", 9000, "monthly", "ZAR"), ("TrustSquare Pro", 36000, "monthly", "ZAR"), ("TrustSquare Starter", 9000, "monthly", "ZAR")],
      "arming made three monthly plans at Paystack: Starter R90, Pro R360, Agency Pro seat R90")
rows = q("SELECT tier, plan_code, key_mode, amount_kobo, active FROM paystack_plans ORDER BY tier")
check(len(rows) == 3 and all(r["key_mode"] == "test" and r["active"] == 1 for r in rows), "the three plan codes are stored against the key mode they were made in (test)")
again = b._auto_renew_sync_plans()
check(len(PS.plans) == 3 and [p["state"] for p in again["plans"]] == ["known"] * 3, "running maintenance again makes nothing new")
x("DELETE FROM paystack_plans")
adopt = b._auto_renew_sync_plans()
check(len(PS.plans) == 3 and [p["state"] for p in adopt["plans"]] == ["adopted"] * 3, "a plan that already exists at Paystack is adopted, not made twice")
flags = C.get("/flags").json()
check(flags["auto_renew"] is True and flags["effective"]["auto_renew"] is True and flags["auto_renew_tiers"] == ["starter", "pro"],
      "/flags now reports the switch on and Starter + Pro ready for the tick box")
STARTER = q("SELECT plan_code FROM paystack_plans WHERE tier='starter' AND active=1")[0]["plan_code"]
PRO = q("SELECT plan_code FROM paystack_plans WHERE tier='pro' AND active=1")[0]["plan_code"]
n_plans = len(PS.plans)

# ════════════════════════════════════════════════════════════════════════════════════════════════
print("C -- THE TICK BOX: on = a subscription; off, or not a card = today's one-off payment")
mkuser("lerato@x.test")
r = init("lerato@x.test", "starter")                                     # tick box off
pl = last_init_payload()
check(list(r.json().keys()) == INIT_KEYS and sorted(pl.keys()) == ONEOFF_PAYLOAD_KEYS and pl["metadata"] == dict(ONEOFF_META, email="lerato@x.test"),
      "tick box OFF with the switch on: the request and the answer are the one-off ones")
ref = r.json()["reference"]; PS.pay(ref); v = verify(ref)
check(list(v.json().keys()) == VERIFY_KEYS and not PS.subs and user("lerato@x.test")["code"] is None and not events("lerato@x.test"),
      "tick box OFF: the plan is bought once, no subscription is created")
st = C.get("/users/lerato@x.test/subscription", cookies=cookie("lerato@x.test")).json()
check(st.get("auto_renew_on") is True and st.get("auto_renew") is False and st.get("renews_on") is None
      and st.get("runs_to") == user("lerato@x.test")["billing_period_end"] and st.get("after_label") == "Free",
      "her plan card data says: not renewing, runs to the end date, then Free")
r = init("lerato@x.test", "pro", auto_renew=1, channel="eft")            # not a card
check("plan" not in last_init_payload() and "auto_renew" not in r.json(), "a non-card payment never opens a subscription, even with the tick box sent")
mkuser("sipho@x.test")
r = init("sipho@x.test", "starter", auto_renew=1, channel="card")        # tick box on
pl = last_init_payload()
check(r.status_code == 200 and r.json().get("auto_renew") is True and pl.get("plan") == STARTER and pl.get("channels") == ["card"],
      "tick box ON: the checkout is started with the Starter plan code, card only")
check(pl["metadata"] == {"type": "seller_subscription", "tier": "starter", "email": "sipho@x.test", "is_downgrade": False,
                         "auto_renew": True, "plan_code": STARTER}, "the request carries the renewal choice in its metadata")
check(len(PS.plans) == n_plans, "the checkout made no plan")
ref = r.json()["reference"]; sub = PS.pay(ref); v = verify(ref); u = user("sipho@x.test")
check(v.status_code == 200 and v.json().get("auto_renew") is True and v.json().get("renews_on") == u["billing_period_end"],
      "verify says the plan renews, and on which date (%s)" % u["billing_period_end"])
check(u["seller_tier"] == "starter" and u["code"] == sub["subscription_code"] and u["tok"] == sub["email_token"] and u["auto_renew"] == 1,
      "the subscription Paystack opened is stored on her account (code + token)")
check(len(events("sipho@x.test", "created")) == 1, "one 'created' line is recorded")
t_before = len(q("SELECT id FROM transactions WHERE user_email='sipho@x.test'")); end_before = u["billing_period_end"]
hook("subscription.create", {"subscription_code": sub["subscription_code"], "email_token": sub["email_token"],
                             "customer": {"email": "sipho@x.test"}, "plan": {"plan_code": STARTER}})
hr = hook("charge.success", PS.charge_data(ref))
check(hr.status_code == 200 and user("sipho@x.test")["billing_period_end"] == end_before
      and len(q("SELECT id FROM transactions WHERE user_email='sipho@x.test'")) == t_before and len(events("sipho@x.test", "created")) == 1,
      "the first payment's own webhooks arriving afterwards change nothing (applied once)")
st = C.get("/users/sipho@x.test/subscription", cookies=cookie("sipho@x.test")).json()
check(st["auto_renew"] is True and st["renews_on"] == end_before and st["auto_renew_tiers"] == ["starter", "pro"]
      and not any("code" in k or "token" in k for k in st), "the plan card data says 'renews on <date>' and carries no code or token")
mkuser("bongani@x.test")                                                  # she closes the tab at Paystack
r = init("bongani@x.test", "starter", auto_renew=1, channel="card"); ref_b = r.json()["reference"]; sub_b = PS.pay(ref_b)
hook("subscription.create", {"subscription_code": sub_b["subscription_code"], "email_token": sub_b["email_token"],
                             "customer": {"email": "bongani@x.test"}, "plan": {"plan_code": STARTER}})
hook("charge.success", PS.charge_data(ref_b)); u = user("bongani@x.test")
check(u["seller_tier"] == "starter" and u["billing_period_end"] == iso(NOW + timedelta(days=30)) and u["code"] == sub_b["subscription_code"],
      "a seller who never returns from Paystack still gets the plan she is billed for (applied by the webhook)")
check(verify(ref_b).json().get("effective") == "already_applied", "and her late return applies nothing a second time")

# ════════════════════════════════════════════════════════════════════════════════════════════════
print("D -- A RENEWAL: 30 more days from the previous end, the month's Tuppence once, a replay ignored")
prev_end = datetime.strptime(user("sipho@x.test")["billing_period_end"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
x("UPDATE tuppence_monthly_grants SET period='2000-01' WHERE email='sipho@x.test'")   # her first month's grant belongs to an earlier month
g0 = grants("sipho@x.test")
hr = hook("charge.success", PS.renewal(sub, "T_renew_early", prev_end - timedelta(days=2)))     # Paystack bills 2 days early (February)
u = user("sipho@x.test")
check(hr.status_code == 200 and u["billing_period_end"] == iso(prev_end + timedelta(days=30)) and u["seller_tier"] == "starter",
      "a renewal paid before the end date runs 30 days from the PREVIOUS END (%s)" % u["billing_period_end"])
check(g0 == 1 and grants("sipho@x.test") == 2, "the month's Tuppence grant (2T, Starter) is made with the renewal")
snap, bal1 = user("sipho@x.test"), bal("sipho@x.test")
hook("charge.success", PS.renewal(sub, "T_renew_early", prev_end - timedelta(days=2)))
check(user("sipho@x.test") == snap and bal("sipho@x.test") == bal1 and grants("sipho@x.test") == 2 and len(events("sipho@x.test", "renewal")) == 1,
      "the same reference replayed is ignored: no extra days, no extra Tuppence")
end1 = prev_end + timedelta(days=30)
hook("charge.success", PS.renewal(sub, "T_renew_late", end1 + timedelta(days=1)))               # a 31-day month: charged a day after the end
u = user("sipho@x.test")
check(u["billing_period_end"] == iso(end1 + timedelta(days=31)), "a renewal paid after the end date runs 30 days from the payment - no paid day is lost")
check(bal("sipho@x.test") == bal1 and grants("sipho@x.test") == 2, "a second renewal in the same calendar month grants no second Tuppence (once a month)")
snap = user("sipho@x.test")
hook("charge.success", PS.renewal(sub, "T_renew_cheap", end1 + timedelta(days=40), amount=100))
check(user("sipho@x.test") == snap, "a renewal that paid less than the plan costs is not applied (PAY-AMOUNT-1)")
os.environ["ALLOW_TEST_PAYMENTS"] = "0"
hook("charge.success", PS.renewal(sub, "T_renew_gated", end1 + timedelta(days=41)))
check(user("sipho@x.test") == snap, "with test-key grants gated, a renewal grants nothing (same gate as every payment)")
os.environ["ALLOW_TEST_PAYMENTS"] = "1"

print("D2 -- the wait at the end date: a plan whose renewal is due is not ended a day early")
x("UPDATE users SET billing_period_end=? WHERE email='bongani@x.test'", iso(NOW - timedelta(hours=20)))
b._apply_pending_downgrades()
check(user("bongani@x.test")["seller_tier"] == "starter", "20 hours past the end date with a renewal due: she still has her plan")
hook("charge.success", PS.renewal(sub_b, "T_bongani_1", NOW))
check(user("bongani@x.test")["billing_period_end"] == iso(NOW + timedelta(days=30)), "the renewal then lands and she never lost the plan")
x("UPDATE users SET billing_period_end=? WHERE email='bongani@x.test'", iso(NOW - timedelta(hours=73)))
n_dis = len(PS.disables()); sent["email"].clear(); sent["push"].clear()
b._apply_pending_downgrades(); u = user("bongani@x.test")
check(u["seller_tier"] == "free" and u["code"] is None and u["auto_renew"] == 0 and u["renewal_failed_at"] is None,
      "73 hours past the end with no renewal: the plan ends as RUL-201 ends it and the subscription is forgotten")
check(len(PS.disables()) == n_dis + 1 and PS.subs[sub_b["subscription_code"]]["status"] == "non-renewing",
      "the subscription is switched off at Paystack, so her card is not tried again a month later")
check(len(sent["email"]) == 1 and len(sent["push"]) == 1, "she is told once: one Buzz and one email")

# ════════════════════════════════════════════════════════════════════════════════════════════════
print("E -- A FAILED RENEWAL: told once; the plan ends on its date as RUL-201 ends it")
mkuser("nomsa@x.test")
r = init("nomsa@x.test", "pro", auto_renew=1, channel="card"); ref_n = r.json()["reference"]; sub_n = PS.pay(ref_n); verify(ref_n)
sent["email"].clear(); sent["push"].clear()
hr = hook("invoice.payment_failed", {"subscription": {"subscription_code": sub_n["subscription_code"]}, "customer": {"email": "nomsa@x.test"}})
u = user("nomsa@x.test")
check(hr.status_code == 200 and u["renewal_failed_at"] and u["seller_tier"] == "pro", "invoice.payment_failed marks the renewal failed; her plan is untouched until its date")
check(len(sent["email"]) == 1 and len(sent["push"]) == 1 and sent["email"][0][0] == "nomsa@x.test", "one Buzz and one email are sent")
hook("invoice.payment_failed", {"subscription": {"subscription_code": sub_n["subscription_code"]}, "customer": {"email": "nomsa@x.test"}})
check(len(sent["email"]) == 1 and len(sent["push"]) == 1 and len(events("nomsa@x.test", "payment_failed")) == 1, "the same failure reported again sends nothing more")
st = C.get("/users/nomsa@x.test/subscription", cookies=cookie("nomsa@x.test")).json()
check(st["renewal_failed"] is True and st["auto_renew"] is False and st["renews_on"] is None, "her plan card data says the renewal did not go through")
x("UPDATE users SET billing_period_end=? WHERE email='nomsa@x.test'", iso(NOW - timedelta(minutes=5)))
n_dis = len(PS.disables()); b._apply_pending_downgrades(); u = user("nomsa@x.test")
check(u["seller_tier"] == "free" and u["slot_limit"] == 2 and u["code"] is None and u["renewal_failed_at"] is None,
      "once the end date passes the plan ends at once (no wait after a failure) - Free, nothing deleted")
check(len(PS.disables()) == n_dis + 1 and len(sent["email"]) == 1, "the subscription is switched off at Paystack and she is not told a second time")
mkuser("themba@x.test")
r = init("themba@x.test", "starter", auto_renew=1, channel="card"); ref_t = r.json()["reference"]; sub_t = PS.pay(ref_t); verify(ref_t)
hook("invoice.payment_failed", {"subscription": {"subscription_code": sub_t["subscription_code"]}})
hook("charge.success", PS.renewal(sub_t, "T_themba_1", NOW + timedelta(days=29)))
u = user("themba@x.test")
check(u["renewal_failed_at"] is None and u["seller_tier"] == "starter", "a renewal that goes through after a failure clears the mark")

# ════════════════════════════════════════════════════════════════════════════════════════════════
print("F -- subscription.not_renew / subscription.disable: renewal marked off, nothing else")
snap = user("themba@x.test")
hr = hook("subscription.not_renew", {"subscription_code": sub_t["subscription_code"], "customer": {"email": "themba@x.test"}})
u = user("themba@x.test")
check(hr.status_code == 200 and u["auto_renew"] == 0 and {k: v for k, v in u.items() if k != "auto_renew"} == {k: v for k, v in snap.items() if k != "auto_renew"},
      "subscription.not_renew sets auto_renew=0 and changes nothing else")
hook("subscription.disable", {"subscription_code": sub_t["subscription_code"]})
check(user("themba@x.test") == u and len(events("themba@x.test", "cancelled")) == 1, "subscription.disable after it changes nothing more (recorded once)")

# ════════════════════════════════════════════════════════════════════════════════════════════════
print("G -- CANCEL RENEWAL: one tap, only as the signed-in seller; the paid days run on")
end_s = user("sipho@x.test")["billing_period_end"]
r = C.post("/payment/seller-subscription/cancel", json={"email": "sipho@x.test"})
check(r.status_code == 401 and user("sipho@x.test")["auto_renew"] == 1, "a stranger is refused (401) and nothing changes")
r = C.post("/payment/seller-subscription/cancel", json={"email": "sipho@x.test"}, cookies=cookie("lerato@x.test"))
check(r.status_code == 409 and user("sipho@x.test")["auto_renew"] == 1, "another signed-in seller typing her address acts only as herself (409) - Sipho still renews")
PS.down = True
r = C.post("/payment/seller-subscription/cancel", json={"email": "sipho@x.test"}, cookies=cookie("sipho@x.test"))
check(r.status_code == 502 and user("sipho@x.test")["auto_renew"] == 1, "if Paystack can not be reached she is told nothing changed - never 'cancelled' while it may still charge")
PS.down = False; n_dis = len(PS.disables())
r = C.post("/payment/seller-subscription/cancel", json={"email": "sipho@x.test"}, cookies=cookie("sipho@x.test"))
u = user("sipho@x.test")
check(r.status_code == 200 and r.json() == {"status": "ok", "auto_renew": False, "tier": "starter", "label": "Starter", "runs_to": end_s},
      "the owner's one tap answers with the end date: %s" % r.json())
check(len(PS.disables()) == n_dis + 1 and PS.disables()[-1][2] == {"code": sub["subscription_code"], "token": sub["email_token"]}
      and PS.subs[sub["subscription_code"]]["status"] == "non-renewing", "Paystack was told to disable that subscription, with its code and token")
check(u["auto_renew"] == 0 and u["seller_tier"] == "starter" and u["billing_period_end"] == end_s, "her plan and her end date are untouched; only renewal is off")
r = C.post("/payment/seller-subscription/cancel", json={"email": "sipho@x.test"}, cookies=cookie("sipho@x.test"))
check(r.status_code == 200 and len(PS.disables()) == n_dis + 1, "tapping it again is harmless (no second call)")
st = C.get("/users/sipho@x.test/subscription", cookies=cookie("sipho@x.test")).json()
check(st["auto_renew"] is False and st["auto_renew_cancelled"] is True and st["runs_to"] == end_s, "her plan card data says 'runs to <date>, then Free'")
r = C.post("/payment/seller-subscription/resume", json={"email": "sipho@x.test"}, cookies=cookie("sipho@x.test"))
check(r.status_code == 200 and r.json()["auto_renew"] is True and user("sipho@x.test")["auto_renew"] == 1
      and PS.subs[sub["subscription_code"]]["status"] == "active", "Renew again switches the same subscription back on; nothing is charged now")
C.post("/payment/seller-subscription/cancel", json={"email": "sipho@x.test"}, cookies=cookie("sipho@x.test"))
x("UPDATE users SET billing_period_end=? WHERE email='sipho@x.test'", iso(NOW - timedelta(minutes=5)))
sent["email"].clear(); sent["push"].clear(); b._apply_pending_downgrades(); u = user("sipho@x.test")
check(u["seller_tier"] == "free" and u["code"] is None and not sent["email"] and not sent["push"],
      "after a cancelled renewal the plan ends on its date (Free) with no failure message - it is what she chose")

# ════════════════════════════════════════════════════════════════════════════════════════════════
print("H -- never two plans billed; moving to Free or closing the account stops the subscription")
mkuser("zanele@x.test")
r = init("zanele@x.test", "starter", auto_renew=1, channel="card"); ref_z = r.json()["reference"]; sub_z1 = PS.pay(ref_z); verify(ref_z)
r = init("zanele@x.test", "pro", auto_renew=1, channel="card"); ref_z2 = r.json()["reference"]
check(last_init_payload().get("plan") == PRO, "upgrading with the tick box on starts the checkout with the Pro plan code")
sub_z2 = PS.pay(ref_z2); verify(ref_z2); u = user("zanele@x.test")
check(u["seller_tier"] == "pro" and u["code"] == sub_z2["subscription_code"] and PS.subs[sub_z1["subscription_code"]]["status"] == "non-renewing",
      "her new Pro subscription is stored and the old Starter one is switched off at Paystack")
r = C.post("/users/zanele@x.test/seller-tier/downgrade-free", cookies=cookie("zanele@x.test"))
u = user("zanele@x.test")
check(r.status_code == 200 and u["pending_downgrade_tier"] == "free" and u["auto_renew"] == 0 and PS.subs[sub_z2["subscription_code"]]["status"] == "non-renewing",
      "booking a move to Free also stops the renewal - nothing is charged again")
r = C.post("/payment/seller-subscription/resume", json={"email": "zanele@x.test"}, cookies=cookie("zanele@x.test"))
u = user("zanele@x.test")
check(r.status_code == 200 and u["auto_renew"] == 1 and u["pending_downgrade_tier"] is None, "Renew again lifts the booked move to Free")
r = init("zanele@x.test", "starter"); ref_z3 = r.json()["reference"]; PS.pay(ref_z3); v = verify(ref_z3); u = user("zanele@x.test")
check(v.json().get("auto_renew") is False and u["code"] is None and u["auto_renew"] == 0 and PS.subs[sub_z2["subscription_code"]]["status"] == "non-renewing",
      "a one-off payment by a seller who was renewing replaces the subscription (switched off, forgotten)")
mkuser("ayanda@x.test")
r = init("ayanda@x.test", "starter", auto_renew=1, channel="card"); ref_a = r.json()["reference"]; sub_a = PS.pay(ref_a); verify(ref_a)
PS.down = True
r = C.delete("/users/ayanda@x.test", cookies=cookie("ayanda@x.test"), headers={"X-Api-Key": "k"})
u = user("ayanda@x.test")
check(r.status_code == 200 and u["code"] is None and u["auto_renew"] == 0 and len(q("SELECT 1 FROM paystack_stop_queue WHERE subscription_code=?", sub_a["subscription_code"])) == 1,
      "closing an account while Paystack is unreachable queues the stop instead of losing it")
PS.down = False; b._auto_renew_hourly()
check(PS.subs[sub_a["subscription_code"]]["status"] == "non-renewing" and not q("SELECT 1 FROM paystack_stop_queue"),
      "the hourly retry then switches it off at Paystack - a closed account is never charged again")

print("I -- the switch turned OFF again: nobody new starts renewing; a seller who renews is still served")
mkuser("palesa@x.test")
r = init("palesa@x.test", "starter", auto_renew=1, channel="card"); ref_p = r.json()["reference"]; sub_p = PS.pay(ref_p); verify(ref_p)
switch(False)
r = init("lerato@x.test", "starter", auto_renew=1, channel="card")
check("plan" not in last_init_payload() and list(r.json().keys()) == INIT_KEYS, "with the switch off again a new checkout is the one-off payment")
end_p = datetime.strptime(user("palesa@x.test")["billing_period_end"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
hook("charge.success", PS.renewal(sub_p, "T_palesa_1", end_p))
check(user("palesa@x.test")["billing_period_end"] == iso(end_p + timedelta(days=30)), "her renewal is still applied - she paid for it")
r = C.post("/payment/seller-subscription/cancel", json={"email": "palesa@x.test"}, cookies=cookie("palesa@x.test"))
check(r.status_code == 200 and user("palesa@x.test")["auto_renew"] == 0, "and she can still cancel with one tap")
switch(True)

print("J -- the dashboard tiles")
m = {t["id"]: t for t in asyncio.run(b.dashboard_launch_metrics(_admin={"via": "prove"}))["metrics"]}
n_ren, n_fail, n_can = len(events(ev="renewal")), len(events(ev="payment_failed")), len(events(ev="cancelled"))
check(m["renewals_month"]["measured"] and m["renewals_month"]["value"] == n_ren and n_ren >= 5, "renewals this month: %s" % m["renewals_month"]["value"])
check(m["renewals_failed_month"]["value"] == n_fail and n_fail == 3, "failed renewals this month: %s" % m["renewals_failed_month"]["value"])
check(m["renewals_cancelled_month"]["value"] == n_can and n_can >= 5, "renewals cancelled this month: %s" % m["renewals_cancelled_month"]["value"])
check(m["auto_renew_share"]["measured"] and re.match(r"^\d+ of \d+ \(\d+%\)$", str(m["auto_renew_share"]["value"])), "auto-renew share: %s" % m["auto_renew_share"]["value"])
src = open(os.path.join(REPO, "bea_main.py"), encoding="utf-8").read() + open(os.path.join(REPO, "payments.py"), encoding="utf-8").read()
check("charge_authorization" not in src.replace("no charge_authorization call", ""), "no charge_authorization call exists - this server never charges a stored card itself")

print()
if fails:
    print("FAILED: %d check(s)" % len(fails))
    for f in fails: print("  - " + f)
    sys.exit(1)
print("ALL AUTO-RENEW-1 CHECKS PASS")
