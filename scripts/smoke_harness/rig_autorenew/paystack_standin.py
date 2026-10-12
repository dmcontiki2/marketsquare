"""paystack_standin.py -- AUTO-RENEW-1 rig only. A LOCAL STAND-IN for the Paystack API, for the rendered proof.

It is NOT Paystack. It follows Paystack's published API and webhook shapes closely enough for the real app
to run its whole renewal lane against it: plans, a hosted checkout page, a subscription opened by the first
card payment, signed webhooks, disable / enable. It holds everything in memory, takes no money, and only
answers on 127.0.0.1.
"""
import hashlib, hmac, html, json, os, threading, time, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

KEY = os.environ.get("RIG_PS_KEY", "sk_test_rig")
RIG = os.environ.get("RIG_ORIGIN", "http://127.0.0.1:8000")
S = {"plans": [], "tx": {}, "subs": {}, "n": 0, "down": False, "hooks": [], "calls": []}
LOCK = threading.Lock()


def now(): return datetime.now(timezone.utc).replace(microsecond=0)
def iso(d): return d.strftime("%Y-%m-%dT%H:%M:%S.000Z")
def nxt():
    S["n"] += 1; return S["n"]


def send_hook(event, data, delay=0.0):
    def go():
        if delay: time.sleep(delay)
        raw = json.dumps({"event": event, "data": data}).encode()
        sig = hmac.new(KEY.encode(), raw, hashlib.sha512).hexdigest()
        req = urllib.request.Request("http://127.0.0.1:8000/payment/webhook", data=raw, method="POST",
                                     headers={"X-Paystack-Signature": sig, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                S["hooks"].append({"event": event, "status": r.status})
        except Exception as e:
            S["hooks"].append({"event": event, "status": "failed: %s" % type(e).__name__})
    threading.Thread(target=go, daemon=True).start()


def plan_by(code): return next((p for p in S["plans"] if p["plan_code"] == code), None)


def charge_data(ref):
    t = S["tx"][ref]; p = t["payload"]; plan = p.get("plan"); po = plan_by(plan) if plan else None
    return {"id": 1000 + list(S["tx"]).index(ref), "status": "success", "reference": ref,
            "amount": po["amount"] if po else p["amount"], "currency": "ZAR", "paid_at": t["paid_at"],
            "channel": t.get("channel") or "card", "metadata": p.get("metadata") or {},
            "customer": {"id": 7, "email": p["email"], "customer_code": "CUS_rig"},
            "plan": plan or None, "plan_object": ({"plan_code": plan, "name": po["name"]} if po else {}),
            "authorization": {"reusable": (t.get("channel") or "card") == "card", "channel": t.get("channel") or "card",
                              "last4": "4081", "brand": "visa"}}


def sub_public(s):
    po = plan_by(s["plan_code"]) or {}
    return {"subscription_code": s["subscription_code"], "email_token": s["email_token"], "status": s["status"],
            "amount": po.get("amount"), "next_payment_date": s["next_payment_date"], "createdAt": s["createdAt"],
            "plan": {"plan_code": s["plan_code"], "name": po.get("name"), "interval": "monthly"},
            "customer": {"email": s["email"], "customer_code": "CUS_rig"}}


def pay(ref, channel="card"):
    t = S["tx"][ref]
    if t["paid_at"]:
        return
    t["paid_at"] = iso(now()); t["channel"] = channel
    plan = t["payload"].get("plan")
    if plan and channel == "card":
        n = nxt()
        s = {"subscription_code": "SUB_rig%04d" % n, "email_token": "tokrig%04d" % n, "status": "active", "plan_code": plan,
             "email": t["payload"]["email"], "createdAt": iso(now()), "next_payment_date": iso(now() + timedelta(days=30))}
        S["subs"][s["subscription_code"]] = s
        send_hook("subscription.create", dict(sub_public(s), subscription_code=s["subscription_code"], email_token=s["email_token"]), delay=1.5)
    send_hook("charge.success", charge_data(ref), delay=2.0)


PAGE = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Checkout - Paystack stand-in</title>
<style>body{font-family:Arial,Helvetica,sans-serif;background:#f1f5f9;margin:0;padding:18px;color:#0f172a}
.c{background:#fff;border-radius:14px;padding:20px;max-width:420px;margin:0 auto;box-shadow:0 2px 10px rgba(0,0,0,.08)}
.tag{background:#fde68a;color:#78350f;font-weight:700;font-size:12px;padding:8px 10px;border-radius:8px;margin-bottom:14px}
h1{font-size:18px;margin:0 0 4px}.amt{font-size:28px;font-weight:800;margin:10px 0}
.row{font-size:13px;color:#475569;margin:6px 0}.sub{background:#eef2ff;color:#3730a3;font-size:13px;padding:10px;border-radius:8px;margin:12px 0}
button{width:100%;border:none;border-radius:10px;padding:14px;font-size:15px;font-weight:700;margin-top:10px;cursor:pointer}
.go{background:#0ea5e9;color:#fff}.alt{background:#e2e8f0;color:#334155}.no{background:none;color:#64748b}</style></head><body>
<div class="c"><div class="tag">PAYSTACK STAND-IN (local rig) &mdash; this is not Paystack and takes no money</div>
<h1>TrustSquare</h1><div class="row">%(email)s</div><div class="amt">R %(amount)s</div>
%(subnote)s
<form method="post" action="/pay/%(ref)s/card"><button class="go" id="pay-card" type="submit">Pay R %(amount)s with test card</button></form>
%(eft)s
<form method="get" action="/pay/%(ref)s/cancel"><button class="no" id="pay-cancel" type="submit">Cancel payment</button></form>
</div></body></html>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _json(self, code, body):
        raw = json.dumps(body).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)

    def _html(self, body):
        raw = body.encode()
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)

    def _redir(self, url):
        self.send_response(303); self.send_header("Location", url); self.send_header("Content-Length", "0"); self.end_headers()

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b""
        try: return json.loads(raw) if raw else {}
        except Exception: return {}

    def _api_ok(self):
        if S["down"]:
            self._json(503, {"status": False, "message": "stand-in: Paystack is down"}); return False
        if self.headers.get("Authorization", "") != "Bearer " + KEY:
            self._json(401, {"status": False, "message": "Invalid key"}); return False
        return True

    def _back(self, ref):
        cb = S["tx"][ref]["payload"].get("callback_url") or (RIG + "/?ps_sub_return=1")   # the dashboard's default callback
        sep = "&" if "?" in cb else "?"
        return cb + sep + "trxref=" + ref + "&reference=" + ref

    def do_GET(self):
        u = urllib.parse.urlparse(self.path); p = u.path
        with LOCK:
            if p == "/__standin/state":
                return self._json(200, {"plans": S["plans"], "subs": list(S["subs"].values()), "down": S["down"], "hooks": S["hooks"][-12:],
                                        "tx": {r: {"paid_at": t["paid_at"], "channel": t.get("channel"), "plan": t["payload"].get("plan"),
                                                   "channels": t["payload"].get("channels"), "amount": t["payload"].get("amount"),
                                                   "email": t["payload"].get("email"), "metadata": t["payload"].get("metadata")}
                                               for r, t in S["tx"].items()},
                                        "calls": S["calls"][-40:]})
            if p.startswith("/pay/"):
                parts = p.split("/"); ref = parts[2]; t = S["tx"].get(ref)
                if not t: return self._html("<p>Unknown transaction</p>")
                if len(parts) > 3 and parts[3] == "cancel":
                    return self._redir(RIG + "/?ps_sub_return=1")
                pl = t["payload"]; plan = plan_by(pl.get("plan")) if pl.get("plan") else None
                amount = "%.2f" % (((plan or {}).get("amount") or pl["amount"]) / 100.0)
                card_only = bool(plan) or (pl.get("channels") == ["card"])
                subnote = ('<div class="sub" id="sub-note"><b>%s</b> &middot; this card will be charged R %s every month until you cancel.</div>'
                           % (html.escape(plan["name"]), amount)) if plan else '<div class="row" id="oneoff-note">One payment. No subscription.</div>'
                eft = "" if card_only else ('<form method="post" action="/pay/%s/eft"><button class="alt" id="pay-eft" type="submit">Pay by instant EFT (test)</button></form>' % ref)
                page = PAGE
                for k, v in (("email", html.escape(pl["email"])), ("amount", amount), ("subnote", subnote), ("ref", ref), ("eft", eft)):
                    page = page.replace("%(" + k + ")s", v)
                return self._html(page)
            S["calls"].append(["GET", p])
            if not self._api_ok(): return
            if p.startswith("/transaction/verify/"):
                ref = urllib.parse.unquote(p.rsplit("/", 1)[-1]); t = S["tx"].get(ref)
                if not t: return self._json(400, {"status": False, "message": "Transaction reference not found"})
                if not t["paid_at"]: return self._json(200, {"status": True, "data": {"status": "abandoned", "reference": ref}})
                return self._json(200, {"status": True, "message": "Verification successful", "data": charge_data(ref)})
            if p == "/plan":
                return self._json(200, {"status": True, "data": S["plans"], "meta": {"total": len(S["plans"])}})
            if p.startswith("/customer/"):
                em = urllib.parse.unquote(p.rsplit("/", 1)[-1]).lower()
                subs = [dict(sub_public(s), plan=9000 + i) for i, s in enumerate(S["subs"].values()) if s["email"].lower() == em]
                return self._json(200, {"status": True, "data": {"email": em, "customer_code": "CUS_rig", "subscriptions": subs}})
            if p.startswith("/subscription/"):
                s = S["subs"].get(urllib.parse.unquote(p.rsplit("/", 1)[-1]))
                if not s: return self._json(404, {"status": False, "message": "Subscription not found"})
                return self._json(200, {"status": True, "data": sub_public(s)})
            if p == "/balance":
                return self._json(200, {"status": True, "data": [{"currency": "ZAR", "balance": 0}]})
            return self._json(404, {"status": False, "message": "stand-in: no such endpoint"})

    def do_POST(self):
        u = urllib.parse.urlparse(self.path); p = u.path; body = self._body()
        with LOCK:
            if p == "/__standin/down":
                S["down"] = bool(body.get("down")); return self._json(200, {"down": S["down"]})
            if p == "/__standin/renew":           # Paystack bills the card on the payment date
                s = S["subs"].get(body.get("code"))
                if not s: return self._json(404, {"error": "no such subscription"})
                po = plan_by(s["plan_code"])
                if body.get("ok", True):
                    ref = "T_rig%06d" % nxt()
                    send_hook("charge.success", {"status": "success", "reference": ref, "amount": po["amount"], "currency": "ZAR",
                                                 "paid_at": body.get("paid_at") or iso(now()), "channel": "card", "metadata": "",
                                                 "customer": {"id": 7, "email": s["email"], "customer_code": "CUS_rig"},
                                                 "plan": {"plan_code": s["plan_code"], "name": po["name"]},
                                                 "authorization": {"reusable": True, "last4": "4081"}})
                    return self._json(200, {"sent": "charge.success", "reference": ref})
                s["status"] = "attention"
                send_hook("invoice.payment_failed", {"subscription": sub_public(s), "customer": {"email": s["email"]},
                                                     "description": "Insufficient Funds", "paid": False, "status": "failed"})
                return self._json(200, {"sent": "invoice.payment_failed"})
            if p.startswith("/pay/"):
                parts = p.split("/"); ref = parts[2]
                if ref not in S["tx"]: return self._html("<p>Unknown transaction</p>")
                pay(ref, "card" if parts[3] == "card" else "eft")
                return self._redir(self._back(ref))
            S["calls"].append(["POST", p, {k: v for k, v in body.items() if k not in ("token",)}])
            if not self._api_ok(): return
            if p == "/transaction/initialize":
                if "@" not in str(body.get("email", "")): return self._json(400, {"status": False, "message": "Invalid Email Address Passed"})
                if body.get("plan") and not plan_by(body["plan"]): return self._json(400, {"status": False, "message": "Plan not found"})
                S["tx"][body["reference"]] = {"payload": body, "paid_at": None}
                return self._json(200, {"status": True, "message": "Authorization URL created",
                                        "data": {"authorization_url": "http://127.0.0.1:8999/pay/" + body["reference"],
                                                 "access_code": "rig", "reference": body["reference"]}})
            if p == "/plan":
                pl = {"plan_code": "PLN_rig%04d" % nxt(), "name": body["name"], "amount": int(body["amount"]),
                      "interval": body.get("interval", "monthly"), "currency": body.get("currency", "ZAR"),
                      "is_deleted": False, "is_archived": False}
                S["plans"].append(pl); return self._json(201, {"status": True, "message": "Plan created", "data": pl})
            if p in ("/subscription/disable", "/subscription/enable"):
                s = S["subs"].get(body.get("code"))
                if not s or s["email_token"] != body.get("token"):
                    return self._json(400, {"status": False, "message": "Subscription with code not found or already inactive"})
                if p.endswith("disable"):
                    if s["status"] not in ("active", "attention"):
                        return self._json(400, {"status": False, "message": "Subscription with code not found or already inactive"})
                    s["status"] = "non-renewing"
                    send_hook("subscription.not_renew", dict(sub_public(s), subscription_code=s["subscription_code"]), delay=1.0)
                    return self._json(200, {"status": True, "message": "Subscription disabled successfully"})
                if s["status"] != "non-renewing":
                    return self._json(400, {"status": False, "message": "Subscription can not be enabled"})
                s["status"] = "active"
                return self._json(200, {"status": True, "message": "Subscription enabled successfully"})
            return self._json(404, {"status": False, "message": "stand-in: no such endpoint"})


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8999), H).serve_forever()
