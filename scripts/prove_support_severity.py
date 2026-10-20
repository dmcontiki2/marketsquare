#!/usr/bin/env python3
"""prove_support_severity.py -- SUPPORT-SEVERITY-1 (20 Oct 2026): EXECUTE the support-form refile against the real
bea_main.py, imported with a throwaway SQLite file (never the live database). The support agent's classifier and every
mail sender are stand-ins, so the run needs no network and mails nobody.

Born of the Ops Map's NCR layer on 20 Oct 2026: two "major" faults, one of them "I'm looking for a domestic nanny job"
(TS-0042) -- every support-form message is stored as major before anyone reads it, and nothing re-filed it after.

What it proves:
  A  a message the agent judged a QUESTION (is_report false) is re-filed minor + triaged, binned where the agent said,
     with the customer-safe note
  B  a message the agent judged a REPORT of something broken stays major + new
  C  a message nobody judged (classifier fallback) stays major + new -- the safe direction
  D  a complaint about a listing stays major whatever the agent says, and is binned LIST
  E  the topic the form really sends ("Listing issue") reaches its bin (it used to be MISC for every row)
  F  sending the held reply from the Ops Dashboard closes the question's row -- and never a real fault's row
  G  a question the agent answered itself is closed at once
Run: python3 scripts/prove_support_severity.py      (exit 0 = all proven)
"""
import os, sys, tempfile
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO); sys.path.insert(0, REPO)
os.environ.setdefault("MS_API_KEY", "k"); os.environ.setdefault("MS_ADMIN_KEY", "adm")
os.environ.setdefault("MS_JWT_SECRET", "test-only-" + os.urandom(8).hex())
for k in ("RESEND_API_KEY", "PAYSTACK_WEBHOOK_SECRET", "GMAIL_APP_PASSWORD", "PAYSTACK_SECRET_KEY"):
    os.environ.pop(k, None)
_mk = os.makedirs
os.makedirs = lambda p, *a, **k: None if str(p).startswith("/var/www") else _mk(p, *a, **k)
import starlette.staticfiles as _sf
_i = _sf.StaticFiles.__init__
def _i2(self, *a, **k):
    k["check_dir"] = False; return _i(self, *a, **k)
_sf.StaticFiles.__init__ = _i2
try:
    import boto3  # noqa: F401  -- storage.py imports it at load; this proof never touches R2
except ImportError:            # so a box without the AWS SDK can still run the proof (R2 is never called)
    import types
    _b3 = types.ModuleType("boto3"); _b3.client = lambda *a, **k: None
    _bc = types.ModuleType("botocore"); _bcc = types.ModuleType("botocore.client"); _bcc.Config = lambda *a, **k: None
    sys.modules.update({"boto3": _b3, "botocore": _bc, "botocore.client": _bcc})
import database
DB = os.path.join(tempfile.mkdtemp(), "supportsev.db"); database.DB_PATH = DB
os.environ["MS_DB"] = os.path.join(os.path.dirname(DB), "flights.db")
import bea_main as b
from fastapi.testclient import TestClient

VERDICT = {}
async def _fake_classify(from_addr, subject, body, lane="customer"):
    return dict(VERDICT)
b._classify_email = _fake_classify
SENT = []
b._smtp_send_reply = lambda to, subj, text, *a, **k: SENT.append((to, subj)) or True
b._send_system_email = lambda *a, **k: "sent"
b._alert_held_reply = lambda *a, **k: None

fails = []
def check(ok, msg):
    print(("  [OK] " if ok else "  [X]  ") + msg)
    if not ok: fails.append(msg)
def q(sql, *p):
    c = database.get_db(); r = c.execute(sql, p).fetchall(); c.close(); return r
C = TestClient(b.app, raise_server_exceptions=False)
QUESTION = {"category": "other", "urgency": "normal", "draft_reply": "Hello, here is how it works on TrustSquare.",
            "auto_safe": False, "bin": "BROWSE", "is_report": False, "classified": True}
REPORT = dict(QUESTION, is_report=True, bin="LIST")
FALLBACK = {"category": "other", "urgency": "normal", "draft_reply": "", "auto_safe": False,
            "bin": "MISC", "is_report": False, "classified": False}
def send(verdict, message, email, topic="", page_url="https://trustsquare.co/support#support-form"):
    VERDICT.clear(); VERDICT.update(verdict)
    r = C.post("/support/message", data={"message": message, "email": email, "name": "Test Person",
                                         "topic": topic, "page_url": page_url})
    ref = (r.json() or {}).get("ref") if r.status_code == 200 else None
    row = q("SELECT * FROM app_faults WHERE ref = ?", ref)[0] if ref else None
    return r, ref, row

print("A  a question is not a major fault")
r, ref_q, row = send(QUESTION, "I'm looking for a domestic nanny job", "nanny@x.test")
check(r.status_code == 200 and row is not None, "the message is stored (%s, %s)" % (r.status_code, ref_q))
check(row and row["severity"] == "minor" and row["status"] == "triaged", "re-filed minor + triaged (got %s / %s)"
      % (row and row["severity"], row and row["status"]))
check(row and row["bin"] == "BROWSE", "binned where the agent said (got %s)" % (row and row["bin"]))
check(row and row["fix_note"].startswith("A question, not a fault report"), "customer-safe note: %r" % (row and row["fix_note"]))

print("B  a real report stays major")
r, ref_b, row = send(REPORT, "The photos on my listing disappear when I save it", "seller@x.test")
check(row and row["severity"] == "major" and row["status"] == "new", "major + new (got %s / %s)"
      % (row and row["severity"], row and row["status"]))

print("C  nobody judged it -- stays major")
r, ref_c, row = send(FALLBACK, "Something is wrong with my account please help", "acct@x.test")
check(row and row["severity"] == "major" and row["status"] == "new", "major + new on a classifier fallback (got %s / %s)"
      % (row and row["severity"], row and row["status"]))

print("D  a listing complaint stays major whatever the agent says")
r, ref_d, row = send(QUESTION, "Complaint about listing #482 (https://trustsquare.co/?listing=482):\n\nThe photos are of another house",
                     "complainer@x.test", topic="Report a problem",
                     page_url="https://trustsquare.co/support?topic=report&listing=482#support-form")
check(row and row["severity"] == "major" and row["status"] == "new", "major + new (got %s / %s)"
      % (row and row["severity"], row and row["status"]))
check(row and row["bin"] == "LIST", "binned LIST (got %s)" % (row and row["bin"]))
r = C.post("/support/message", data={"message": "Complaint about listing #482 (https://trustsquare.co/?listing=482):\n\n",
                                     "email": "empty@x.test", "topic": "Report a problem"})
check(r.status_code == 400, "an EMPTY listing complaint is still refused (REPORT-EMPTY-1) (%s)" % r.status_code)

print("E  the topic the form sends reaches its bin")
r, ref_e, row = send(FALLBACK, "My listing will not publish at all", "topic@x.test", topic="Listing issue")
check(row and row["bin"] == "LIST", "'Listing issue' -> LIST (got %s)" % (row and row["bin"]))
r, ref_e2, row = send(FALLBACK, "I cannot sign in with my email link", "topic2@x.test", topic="Account access")
check(row and row["bin"] == "AUTH", "'Account access' -> AUTH (got %s)" % (row and row["bin"]))

print("F  sending the held reply closes the question -- never a real fault")
def triage_id(ref):
    rows = q("SELECT id FROM email_triage WHERE subject LIKE ?", "%" + ref + "%")
    return rows[0]["id"] if rows else None
tq, tb = triage_id(ref_q), triage_id(ref_b)
check(tq is not None and tb is not None, "both held replies are in the support queue (#%s, #%s)" % (tq, tb))
r = C.post("/dashboard/email-triage/%s/send" % tq, json={"text": "Hello, you can list your nanny services for free."},
           headers={"X-Admin-Key": "adm"})
check(r.status_code == 200 and (r.json() or {}).get("closed_ref") == ref_q, "reply sent, question closed (%s %s)"
      % (r.status_code, r.text[:120]))
row = q("SELECT status FROM app_faults WHERE ref = ?", ref_q)[0]
check(row["status"] == "closed", "the question's row reads closed (got %s)" % row["status"])
r = C.post("/dashboard/email-triage/%s/send" % tb, json={"text": "Thank you, we are fixing this now."},
           headers={"X-Admin-Key": "adm"})
row = q("SELECT status, severity FROM app_faults WHERE ref = ?", ref_b)[0]
check(r.status_code == 200 and row["status"] == "new" and row["severity"] == "major",
      "a reply to a REAL fault leaves it open (got %s / %s)" % (row["status"], row["severity"]))

print("G  a question the agent answered itself is closed at once")
r, ref_g, row = send(FALLBACK, "How do I contact a seller about a listing", "answered@x.test")
ok = b._support_refile(ref_g, dict(QUESTION, status="sent"))
row = q("SELECT severity, status, fix_note FROM app_faults WHERE ref = ?", ref_g)[0]
check(ok and row["severity"] == "minor" and row["status"] == "closed" and "answered it" in row["fix_note"],
      "minor + closed + 'answered it' (got %s / %s / %r)" % (row["severity"], row["status"], row["fix_note"]))

print()
print("RESULT: %s" % ("ALL PROVEN" if not fails else "%d FAILED" % len(fails)))
sys.exit(1 if fails else 0)
