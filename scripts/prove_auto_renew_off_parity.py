#!/usr/bin/env python3
"""prove_auto_renew_off_parity.py -- AUTO-RENEW-1 (RUL-224, 12 Oct 2026): with the switch OFF, is the paid-plan
flow BYTE-FOR-BYTE what it was before the build?

This is a DIFFERENTIAL proof. It runs ONE scenario twice -- once against a copy of the source from before
the build, once against the source after it -- each in its own process with its own throwaway database
and the same in-process Paystack stand-in, and compares everything the flow produces:
  * every HTTP answer (status + body) of initialize, verify, the webhook, the subscription answer,
    GET /users/{email}, downgrade-free, account close, /subscription/tiers
  * every request sent to Paystack (method, path, body)
  * the rows the flow writes (users, transactions, payment_refs_consumed, tuppence_monthly_grants)
Only random references are normalised (REF1, REF2 ... in order of appearance) and the wall-clock stamp
on the /flags row (updated_at, the second each throwaway database was created) is left out. Nothing else
is masked.
The one difference that is ALLOWED is listed in ALLOWED below and asserted exactly: /flags gains the
switch's three keys (all reading off). Anything else is a failure.

    git worktree add /tmp/ar_base <commit before AUTO-RENEW-1>      # or: git archive <commit> | tar -x -C /tmp/ar_base
    python3 scripts/prove_auto_renew_off_parity.py --base /tmp/ar_base --new .

Run 12 Oct 2026 against 031273f (the commit the build was laid on): IDENTICAL.
"""
import os, sys, json, subprocess, tempfile

ALLOWED = "the /flags answer gains auto_renew=false, auto_renew_tiers=[] and effective.auto_renew=false"


def run_scenario(src):
    """Child process: import the app from `src` and play the scenario. Prints one JSON document."""
    import hmac, hashlib, re
    from datetime import datetime, timedelta, timezone
    os.chdir(src); sys.path.insert(0, src)
    SECRET = "sk_test_parity_0123456789"
    os.environ.update({"MS_API_KEY": "k", "MS_ADMIN_KEY": "adm", "MS_JWT_SECRET": "parity-only-secret-parity-only-secret",
                       "TUPPENCE_MONTHLY_ENABLED": "1", "PAYSTACK_SECRET_KEY": SECRET, "ALLOW_TEST_PAYMENTS": "1"})
    for k in ("RESEND_API_KEY", "PAYSTACK_WEBHOOK_SECRET", "GMAIL_APP_PASSWORD"):
        os.environ.pop(k, None)
    _mk = os.makedirs
    os.makedirs = lambda p, *a, **k: None if str(p).startswith("/var/www") else _mk(p, *a, **k)
    import starlette.staticfiles as _sf
    _i = _sf.StaticFiles.__init__
    def _i2(self, *a, **k):
        k["check_dir"] = False; return _i(self, *a, **k)
    _sf.StaticFiles.__init__ = _i2
    import logging; logging.disable(logging.CRITICAL)
    real_stdout = sys.stdout; sys.stdout = open(os.devnull, "w")
    import database
    DB = os.path.join(tempfile.mkdtemp(), "parity.db"); database.DB_PATH = DB
    os.environ["MS_DB"] = os.path.join(os.path.dirname(DB), "flights.db")
    import bea_main as b, payments
    from fastapi.testclient import TestClient
    import jwt as _jwt
    T0 = datetime(2026, 10, 1, 9, 0, 0, tzinfo=timezone.utc)
    iso = lambda d: d.strftime("%Y-%m-%dT%H:%M:%SZ")

    class _Resp:
        def __init__(self, body): self._b = body; self.status_code = 200
        def json(self): return self._b
    class Fake:
        def __init__(self): self.tx, self.calls = {}, []
        def post(self, url, json=None, headers=None, timeout=None): return self.request("POST", url, json=json)
        def get(self, url, params=None, headers=None, timeout=None): return self.request("GET", url, params=params)
        def request(self, method, url, json=None, params=None, headers=None, timeout=None):
            path = url.split("api.paystack.co", 1)[-1]
            self.calls.append([method, path, json, params])
            if path == "/transaction/initialize":
                self.tx[json["reference"]] = {"payload": dict(json), "paid_at": None}
                return _Resp({"status": True, "data": {"authorization_url": "https://checkout.paystack.test/" + json["reference"], "reference": json["reference"]}})
            if path.startswith("/transaction/verify/"):
                ref = path.rsplit("/", 1)[-1]; t = self.tx.get(ref)
                if not t or not t["paid_at"]:
                    return _Resp({"status": True, "data": {"status": "abandoned", "reference": ref}})
                p = t["payload"]
                return _Resp({"status": True, "data": {"status": "success", "reference": ref, "amount": p["amount"], "currency": "ZAR",
                                                       "paid_at": t["paid_at"], "channel": "card", "metadata": p.get("metadata") or {},
                                                       "customer": {"id": 7, "email": p["email"]}, "plan": None, "plan_object": {},
                                                       "authorization": {"reusable": True}}})
            return _Resp({"status": False, "message": "stand-in: no such endpoint"})
        def pay(self, ref, when): self.tx[ref]["paid_at"] = iso(when)
    PS = Fake(); payments.requests = PS
    b._send_system_email = lambda *a, **k: "sent"
    b._push_to_seller = lambda *a, **k: 0
    C = TestClient(b.app, raise_server_exceptions=False)
    def q(sql, *p):
        c = database.get_db(); r = [dict(x) for x in c.execute(sql, p).fetchall()]; c.close(); return r
    def x(sql, *p):
        c = database.get_db(); c.execute(sql, p); c.commit(); c.close()
    def cookie(email):
        return {"ts_user": _jwt.encode({"scope": "user", "sub": email, "iat": T0, "exp": datetime.now(timezone.utc) + timedelta(hours=2)},
                                       b._JWT_SECRET, algorithm=b._JWT_ALGO)}
    out = []
    def rec(label, r):
        try: body = r.json()
        except Exception: body = r.text
        out.append([label, r.status_code, body])
    def hook(label, event, data):
        raw = json.dumps({"event": event, "data": data}).encode()
        sig = hmac.new(SECRET.encode(), raw, hashlib.sha512).hexdigest()
        rec(label, C.post("/payment/webhook", content=raw, headers={"X-Paystack-Signature": sig, "Content-Type": "application/json"}))
    def init(label, email, tier):
        r = C.post("/payment/seller-subscription/initialize", params={"email": email, "tier": tier, "callback_url": "https://trustsquare.co/?ps_sub_return=1"})
        rec(label, r); return r.json().get("reference")
    def verify(label, ref): rec(label, C.get("/payment/seller-subscription/verify", params={"reference": ref}))

    for em in ("thandi@x.test", "sipho@x.test", "lerato@x.test"):
        x("INSERT INTO users (email, eula_accepted_at) VALUES (?, ?)", em, iso(T0))
    rec("flags", C.get("/flags"))
    rec("tiers", C.get("/subscription/tiers"))
    rec("init no terms", C.post("/payment/seller-subscription/initialize", params={"email": "stranger@x.test", "tier": "starter"}))
    rec("init bad tier", C.post("/payment/seller-subscription/initialize", params={"email": "thandi@x.test", "tier": "elite"}))
    rec("init agency", C.post("/payment/seller-subscription/initialize", params={"email": "thandi@x.test", "tier": "agency"}))
    r1 = init("init starter", "thandi@x.test", "starter")
    verify("verify unpaid", r1)
    PS.pay(r1, T0); verify("verify paid", r1); verify("verify replay", r1)
    hook("hook first charge", "charge.success", {"reference": r1, "amount": 9000, "currency": "ZAR", "paid_at": iso(T0),
                                                  "metadata": {"type": "seller_subscription", "tier": "starter", "email": "thandi@x.test", "is_downgrade": False},
                                                  "customer": {"email": "thandi@x.test"}, "plan": {}})
    hook("hook tuppence", "charge.success", {"reference": "ms_tuppence_fixed0001", "amount": 100000, "currency": "ZAR", "paid_at": iso(T0),
                                              "metadata": {"tuppence": 3, "email": "thandi@x.test", "ai_pack_sessions": 0}, "customer": {"email": "thandi@x.test"}})
    hook("hook tuppence replay", "charge.success", {"reference": "ms_tuppence_fixed0001", "amount": 100000, "currency": "ZAR",
                                                     "metadata": {"tuppence": 3, "email": "thandi@x.test"}, "customer": {"email": "thandi@x.test"}})
    hook("hook sub.create", "subscription.create", {"subscription_code": "SUB_zz", "email_token": "tok", "customer": {"email": "thandi@x.test"}, "plan": {"plan_code": "PLN_zz"}})
    hook("hook charge with plan", "charge.success", {"reference": "T_plan_1", "amount": 9000, "currency": "ZAR", "paid_at": iso(T0),
                                                      "metadata": "", "customer": {"email": "thandi@x.test"}, "plan": {"plan_code": "PLN_zz"}})
    hook("hook invoice.create", "invoice.create", {"subscription": {"subscription_code": "SUB_zz"}, "customer": {"email": "thandi@x.test"}})
    hook("hook invoice.update", "invoice.update", {"subscription": {"subscription_code": "SUB_zz"}, "customer": {"email": "thandi@x.test"}})
    hook("hook invoice.payment_failed", "invoice.payment_failed", {"subscription": {"subscription_code": "SUB_zz"}, "customer": {"email": "thandi@x.test"}})
    hook("hook sub.not_renew", "subscription.not_renew", {"subscription_code": "SUB_zz", "customer": {"email": "thandi@x.test"}})
    hook("hook sub.disable", "subscription.disable", {"subscription_code": "SUB_zz", "customer": {"email": "thandi@x.test"}})
    hook("hook expiring_cards", "subscription.expiring_cards", [{"subscription": {"subscription_code": "SUB_zz"}}])
    rec("hook unsigned", C.post("/payment/webhook", content=b'{"event":"charge.success","data":{}}', headers={"X-Paystack-Signature": "00"}))
    rec("subscription thandi", C.get("/users/thandi@x.test/subscription", cookies=cookie("thandi@x.test")))
    u = C.get("/users/thandi@x.test", cookies=cookie("thandi@x.test"), headers={"X-Api-Key": "k"})
    try: body = {k: v for k, v in u.json().items() if k not in ("created_at", "last_seen", "eula_accepted_at")}
    except Exception: body = u.text
    out.append(["get user thandi", u.status_code, body])
    r2 = init("init pro (upgrade)", "thandi@x.test", "pro"); PS.pay(r2, T0 + timedelta(days=3)); verify("verify pro", r2)
    r3 = init("init starter (downgrade)", "thandi@x.test", "starter"); PS.pay(r3, T0 + timedelta(days=5)); verify("verify downgrade", r3)
    rec("subscription thandi 2", C.get("/users/thandi@x.test/subscription", cookies=cookie("thandi@x.test")))
    rec("downgrade-free scheduled", C.post("/users/thandi@x.test/seller-tier/downgrade-free", cookies=cookie("thandi@x.test")))
    r4 = init("init starter sipho", "sipho@x.test", "starter"); PS.pay(r4, T0); verify("verify sipho", r4)
    x("UPDATE users SET billing_period_end=? WHERE email='sipho@x.test'", "2026-01-01T00:00:00Z")
    x("UPDATE users SET billing_period_end=? WHERE email='thandi@x.test'", "2026-01-02T00:00:00Z")
    b._apply_pending_downgrades()
    rec("subscription sipho after lapse", C.get("/users/sipho@x.test/subscription", cookies=cookie("sipho@x.test")))
    rec("subscription thandi after downgrade", C.get("/users/thandi@x.test/subscription", cookies=cookie("thandi@x.test")))
    rec("downgrade-free immediate", C.post("/users/sipho@x.test/seller-tier/downgrade-free", cookies=cookie("sipho@x.test")))
    rec("admin set tier", C.put("/users/lerato@x.test/seller-tier", params={"tier": "starter"}, headers={"X-Api-Key": "k", "X-Admin-Key": "adm"}))
    rec("admin set tier free", C.put("/users/lerato@x.test/seller-tier", params={"tier": "free"}, headers={"X-Api-Key": "k", "X-Admin-Key": "adm"}))
    rec("close lerato", C.delete("/users/lerato@x.test", cookies=cookie("lerato@x.test"), headers={"X-Api-Key": "k"}))
    COLS = "email, seller_tier, slot_limit, pending_downgrade_tier, billing_period_end, is_superuser, aa_sessions_remaining, circle_grandfather"
    db = {"users": q("SELECT %s FROM users ORDER BY email" % COLS),
          "transactions": q("SELECT user_email, type, amount, description FROM transactions ORDER BY id"),
          "payment_refs_consumed": q("SELECT kind, reference FROM payment_refs_consumed ORDER BY id"),
          "tuppence_monthly_grants": q("SELECT email, period, amount, badge_bonus FROM tuppence_monthly_grants ORDER BY email, period")}
    doc = json.dumps({"answers": out, "paystack_calls": PS.calls, "db": db}, sort_keys=True, default=str)
    refs = []
    for m in re.finditer(r"ms_sub_[a-z]+_[0-9a-f]{12}", doc):
        if m.group(0) not in refs: refs.append(m.group(0))
    for i, r in enumerate(refs):
        doc = doc.replace(r, "REF%d" % (i + 1))
    sys.stdout = real_stdout
    print(doc)


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "--run":
        return run_scenario(os.path.abspath(sys.argv[2]))
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="source tree from BEFORE the build")
    ap.add_argument("--new", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))), help="source tree after the build")
    ap.add_argument("--keep", default="", help="write the two documents to this folder")
    a = ap.parse_args()
    docs = {}
    for name, src in (("base", a.base), ("new", a.new)):
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--run", os.path.abspath(src)],
                           capture_output=True, text=True, timeout=600, stdin=subprocess.DEVNULL)
        line = (r.stdout or "").strip().splitlines()[-1] if (r.stdout or "").strip() else ""
        if r.returncode != 0 or not line.startswith("{"):
            print("could not run the %s scenario:\n%s" % (name, (r.stderr or r.stdout)[-1200:])); return 2
        docs[name] = json.loads(line)
        if a.keep:
            os.makedirs(a.keep, exist_ok=True)
            json.dump(docs[name], open(os.path.join(a.keep, "off_parity_%s.json" % name), "w"), indent=1, sort_keys=True)
    base, new = docs["base"], docs["new"]
    # the ONE allowed difference, asserted exactly and then removed
    nf = [x for x in new["answers"] if x[0] == "flags"][0][2]
    for doc in (base, new):                         # the wall clock of each run, not behaviour
        [x for x in doc["answers"] if x[0] == "flags"][0][2].pop("updated_at", None)
    ok_flags = (nf.pop("auto_renew", None) is False and nf.pop("auto_renew_tiers", None) == []
                and nf["effective"].pop("auto_renew", None) is False)
    diffs = []
    if not ok_flags:
        diffs.append("/flags does not report the switch OFF in the new source")
    if len(base["answers"]) != len(new["answers"]):
        diffs.append("the scenario produced %d answers before and %d after" % (len(base["answers"]), len(new["answers"])))
    for x_, y_ in zip(base["answers"], new["answers"]):
        if json.dumps(x_, sort_keys=True) != json.dumps(y_, sort_keys=True):
            diffs.append("ANSWER %s\n      before: %s\n      after:  %s" % (x_[0], json.dumps(x_[1:], sort_keys=True)[:400], json.dumps(y_[1:], sort_keys=True)[:400]))
    if json.dumps(base["paystack_calls"], sort_keys=True) != json.dumps(new["paystack_calls"], sort_keys=True):
        diffs.append("the requests sent to Paystack differ (%d before, %d after)" % (len(base["paystack_calls"]), len(new["paystack_calls"])))
    for t in base["db"]:
        if json.dumps(base["db"][t], sort_keys=True) != json.dumps(new["db"][t], sort_keys=True):
            diffs.append("table %s differs" % t)
    print("scenario: %d answers, %d Paystack requests, %d tables compared" % (len(base["answers"]), len(base["paystack_calls"]), len(base["db"])))
    print("allowed difference: " + ALLOWED + (" -- present, exactly" if ok_flags else " -- NOT as expected"))
    if diffs:
        print("NOT IDENTICAL: %d difference(s)" % len(diffs))
        for d in diffs: print("  - " + d)
        return 1
    print("IDENTICAL: with the switch OFF the paid-plan flow is byte-for-byte what it was")
    return 0


if __name__ == "__main__":
    sys.exit(main())
