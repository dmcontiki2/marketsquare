#!/usr/bin/env python3
"""TUPPENCE-DORMANCY-1 — the sweep that makes EULA §6.3's expiry promise true.

EULA §6.3 (live since v1.13) says:

    "Unused Tuppence expires after 24 consecutive months of account inactivity
     (no login, no Introduction, no purchase). The Platform will notify you by
     email not less than 30 days before expiry."

Until 21 Aug 2026 NOTHING on disk implemented either half — we published a notice
commitment we could not keep. This script is that implementation.

DESIGN — the notice is a HARD PRECONDITION, not a courtesy
----------------------------------------------------------
Nothing is ever expired unless a warning email was actually sent AND at least
NOTICE_DAYS have elapsed since it was sent. If the warning was never sent, or was
sent too recently, the balance is left alone and the run says so. The failure mode
is "expiry is late", never "money vanished without warning".

ACTIVITY is the LATEST of: users.last_seen · users.created_at ·
any transactions row · any intro_requests row (as buyer) · any listing (as seller).
A superset is deliberate — every extra signal makes the user look MORE active, which
can only delay expiry. Erring toward the user is the correct direction here.

RE-ACTIVATION VOIDS A WARNING. The warning is bound to the activity timestamp it was
issued against. If the user does anything at all, activity moves, the old warning no
longer matches, and the 24-month clock starts again from scratch.

SAFETY
  · DRY-RUN BY DEFAULT. --apply is required to write anything.
  · Balance <= 0 is skipped (nothing to expire).
  · Expiry is one offsetting `dormancy_expiry` transactions row — the wallet stays a
    pure SUM(amount), exactly like `grant_expiry`. No destructive UPDATE, full audit trail.
  · Idempotent: a second run on the same day changes nothing.
  · --limit caps how many accounts are touched in one run.

USAGE
    python3 scripts/tuppence_dormancy.py                  # dry run, report only
    python3 scripts/tuppence_dormancy.py --apply          # send warnings + expire
    python3 scripts/tuppence_dormancy.py --apply --warn-only
    python3 scripts/tuppence_dormancy.py --db /path/to/marketsquare.db
    python3 scripts/tuppence_dormancy.py --as-of 2028-01-01   # test a future date

ENV   RESEND_API_KEY — required to SEND. Without it, --apply refuses to warn (it will
      not expire on the back of a warning it could not send).
Stdlib only. Exit 0 ok · 1 nothing-sent-but-expiry-due (needs attention) · 2 config error.
"""
import argparse, json, os, sqlite3, sys, urllib.request, urllib.error
from datetime import datetime, timedelta, timezone

DORMANT_MONTHS = 24
NOTICE_DAYS = 30
FROM_ADDR = os.environ.get("TS_DORMANCY_FROM", "TrustSquare <noreply@trustsquare.co>")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DBS = ["/var/www/marketsquare/marketsquare.db",
               os.path.join(REPO, "marketsquare.db")]


def envkey(name):
    v = os.getenv(name)
    if v:
        return v
    for f in ("/var/www/marketsquare/.env", os.path.join(REPO, ".env")):
        try:
            for ln in open(f, encoding="utf-8"):
                ln = ln.strip()
                if ln.startswith(name + "="):
                    return ln.split("=", 1)[1].strip()
        except OSError:
            pass
    return None


def _iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse(s):
    """Tolerant timestamp parse — the DB mixes ISO-Z and 'YYYY-MM-DD HH:MM:SS'."""
    if not s:
        return None
    s = str(s).strip().replace("T", " ").replace("Z", "")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d"):
        try:
            return datetime.strptime(s[:26], fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def ensure_schema(conn):
    """Additive only. Records every warning so expiry can PROVE one was sent."""
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS tuppence_dormancy_notices (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        email         TEXT NOT NULL,
        activity_at   TEXT NOT NULL,   -- the inactivity anchor this warning was issued against
        warned_at     TEXT NOT NULL,
        balance_at_warning INTEGER NOT NULL,
        expired_at    TEXT,
        expired_amount INTEGER,
        message_id    TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_dormancy_email ON tuppence_dormancy_notices(email);
    CREATE UNIQUE INDEX IF NOT EXISTS idx_dormancy_once
        ON tuppence_dormancy_notices(email, activity_at);
    """)
    conn.commit()


def last_activity(conn, email, created_at):
    """Latest signal of life. Superset by design: more signals = later expiry."""
    stamps = [_parse(created_at)]
    for sql, args in (
        ("SELECT MAX(created_at) FROM transactions WHERE user_email=?", (email,)),
        ("SELECT MAX(created_at) FROM intro_requests WHERE buyer_email=?", (email,)),
    ):
        try:
            r = conn.execute(sql, args).fetchone()
            if r and r[0]:
                stamps.append(_parse(r[0]))
        except sqlite3.Error:
            pass
    for sql in ("SELECT MAX(created_at) FROM listings WHERE seller_email=?",
                "SELECT MAX(created_at) FROM listings WHERE user_email=?"):
        try:
            r = conn.execute(sql, (email,)).fetchone()
            if r and r[0]:
                stamps.append(_parse(r[0]))
            break
        except sqlite3.Error:
            continue
    stamps = [s for s in stamps if s]
    return max(stamps) if stamps else None


def balance(conn, email):
    r = conn.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE user_email=?",
                     (email,)).fetchone()
    return int(r[0]) if r else 0


def send_warning(key, to, bal, expire_on, dry):
    subject = f"Your {bal} Tuppence will expire on {expire_on:%d %B %Y}"
    body = f"""<p>Hello,</p>
<p>Your TrustSquare account has been inactive for close to 24 months. Under clause 6.3 of
our Terms, unused Tuppence expires after 24 consecutive months of inactivity, and we
undertake to tell you at least 30 days beforehand. This is that notice.</p>
<p><b>Balance: {bal} Tuppence &middot; Expires: {expire_on:%d %B %Y}</b></p>
<p><b>To keep it, simply use your account before that date</b> — sign in, request an
introduction, or top up. Any one of those resets the clock in full and this notice falls away.</p>
<p>Tuppence is a platform service credit. It is not money, it earns no interest, and it is
not redeemable for cash — so there is nothing to pay out, only something to use.</p>
<p>If you would rather not keep the account at all, you can close it at
support@trustsquare.co.</p>
<p>&mdash; TrustSquare</p>"""
    if dry:
        return "DRY-RUN"
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps({"from": FROM_ADDR, "to": [to], "subject": subject,
                         "html": body}).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode()).get("id", "sent")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="actually send and expire")
    ap.add_argument("--warn-only", action="store_true", help="send warnings, never expire")
    ap.add_argument("--db")
    ap.add_argument("--limit", type=int, default=500)
    ap.add_argument("--as-of", help="pretend today is YYYY-MM-DD (testing)")
    a = ap.parse_args()

    db = a.db or next((p for p in DEFAULT_DBS if os.path.exists(p)), None)
    if not db or not os.path.exists(db):
        print("no database found — pass --db", file=sys.stderr); sys.exit(2)

    now = (_parse(a.as_of) if a.as_of else datetime.now(timezone.utc))
    dormant_before = now - timedelta(days=DORMANT_MONTHS * 30.44)
    warn_before = dormant_before + timedelta(days=NOTICE_DAYS)

    key = envkey("RESEND_API_KEY")
    dry = not a.apply
    if a.apply and not key:
        print("RESEND_API_KEY not set — refusing to run with --apply.\n"
              "Expiry may never ride on a warning that could not be sent.", file=sys.stderr)
        sys.exit(2)

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    if a.apply:
        ensure_schema(conn)
    else:
        try:
            conn.execute("SELECT 1 FROM tuppence_dormancy_notices LIMIT 1")
        except sqlite3.Error:
            print("note: notices table does not exist yet (created on first --apply)\n")

    users = conn.execute("SELECT email, created_at FROM users").fetchall()
    warned = expired = skipped_no_notice = 0
    total_expired = 0
    print(f"TUPPENCE-DORMANCY-1 · {'DRY RUN' if dry else 'APPLY'} · db={db}")
    print(f"as-of {now:%Y-%m-%d} · dormant if inactive since {dormant_before:%Y-%m-%d} "
          f"· warn if inactive since {warn_before:%Y-%m-%d}\n")

    for u in users:
        email = u["email"]
        if warned + expired >= a.limit:
            break
        bal = balance(conn, email)
        if bal <= 0:
            continue
        act = last_activity(conn, email, u["created_at"])
        if not act or act > warn_before:
            continue                      # still active enough — nothing due

        act_key = _iso(act)
        notice = None
        try:
            notice = conn.execute(
                "SELECT * FROM tuppence_dormancy_notices WHERE email=? AND activity_at=?",
                (email, act_key)).fetchone()
        except sqlite3.Error:
            pass

        expire_on = act + timedelta(days=DORMANT_MONTHS * 30.44)

        # ---- 1. expiry due? only ever on the back of a real, aged warning ----
        if act <= dormant_before and not a.warn_only:
            if not notice or not notice["warned_at"]:
                skipped_no_notice += 1
                print(f"  HOLD    {email:38} {bal:>5}T  dormant since {act:%Y-%m-%d} "
                      f"but NO warning on record — warning first, expiry deferred")
            else:
                w = _parse(notice["warned_at"])
                age = (now - w).days if w else -1
                if age < NOTICE_DAYS:
                    print(f"  WAIT    {email:38} {bal:>5}T  warned {age}d ago "
                          f"(needs {NOTICE_DAYS}d)")
                    continue
                if notice["expired_at"]:
                    continue              # already done — idempotent
                print(f"  EXPIRE  {email:38} {bal:>5}T  inactive since {act:%Y-%m-%d}, "
                      f"warned {age}d ago")
                if a.apply:
                    conn.execute(
                        "INSERT INTO transactions (user_email, type, amount, description) "
                        "VALUES (?,?,?,?)",
                        (email, "dormancy_expiry", -bal,
                         f"Dormancy expiry · {bal}T after {DORMANT_MONTHS} months inactive (EULA 6.3)"))
                    conn.execute(
                        "UPDATE tuppence_dormancy_notices SET expired_at=?, expired_amount=? "
                        "WHERE email=? AND activity_at=?", (_iso(now), bal, email, act_key))
                    conn.commit()
                expired += 1
                total_expired += bal
                continue

        # ---- 2. warning due? ----
        if notice and notice["warned_at"]:
            continue                      # already warned for this dormancy window
        print(f"  WARN    {email:38} {bal:>5}T  inactive since {act:%Y-%m-%d}, "
              f"expires {expire_on:%Y-%m-%d}")
        if a.apply:
            try:
                mid = send_warning(key, email, bal, expire_on, dry=False)
            except (urllib.error.URLError, urllib.error.HTTPError) as e:
                print(f"          send FAILED ({e}) — not recorded, will retry next run")
                continue
            conn.execute(
                "INSERT OR IGNORE INTO tuppence_dormancy_notices "
                "(email, activity_at, warned_at, balance_at_warning, message_id) "
                "VALUES (?,?,?,?,?)", (email, act_key, _iso(now), bal, mid))
            conn.commit()
        warned += 1

    print(f"\n{len(users)} accounts · warned {warned} · expired {expired} "
          f"({total_expired}T) · held for notice {skipped_no_notice}")
    if dry:
        print("DRY RUN — nothing was sent or written. Re-run with --apply.")
    conn.close()
    sys.exit(1 if skipped_no_notice and not dry else 0)


if __name__ == "__main__":
    main()
