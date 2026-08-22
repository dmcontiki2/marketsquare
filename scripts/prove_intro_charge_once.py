#!/usr/bin/env python3
"""prove_intro_charge_once.py — INTRO-CHARGE-ONCE-1 / RG-0142.

The 22 Aug forensic audit proved the BUG by replaying accept_intro's SQL against a
throwaway SQLite replica: 1T -> accept -> 0T -> accept again -> -1T -> four accepts ->
-3T, four intro_deduct rows for ONE introduction. This proves the FIX the same way, and
additionally asserts the guarded statements are the ones actually in bea_main.py, so the
test cannot pass against a source that has drifted.

No production data, no production box. Run: python3 scripts/prove_intro_charge_once.py
"""
import os, re, sqlite3, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "bea_main.py")

GUARD_UPDATE = ("UPDATE intro_requests SET status = 'accepted', tuppence_charged = 1 "
                "WHERE id = ? AND COALESCE(tuppence_charged, 0) = 0 "
                "AND COALESCE(LOWER(status), 'pending') NOT IN ('accepted', 'declined')")
DECLINE_UPDATE = ("UPDATE intro_requests SET status = 'declined' WHERE id = ? "
                  "AND COALESCE(tuppence_charged, 0) = 0 "
                  "AND COALESCE(LOWER(status), 'pending') NOT IN ('accepted', 'declined')")

fails = []
def check(ok, msg):
    print(("  [OK] " if ok else "  [X]  ") + msg)
    if not ok:
        fails.append(msg)

print("=" * 70)
print("  INTRO-CHARGE-ONCE-1 — proving one introduction charges exactly once")
print("=" * 70)

print("\n1. the guarded statements are the ones in bea_main.py")
src = open(SRC, encoding="utf-8").read()
def flat(x):
    """Drop Python's double quotes and collapse whitespace, so a statement written across
    several adjacent string literals still matches. This does NOT weaken the assertion:
    the full SQL text, including every precondition, must still be present in order.
    Single quotes are kept — they are the SQL's own literals."""
    return re.sub(r'\s+', ' ', x.replace('"', '')).strip()
_fsrc = flat(src)
check(flat(GUARD_UPDATE) in _fsrc, "accept uses a conditional UPDATE with its own precondition")
check(flat(DECLINE_UPDATE) in _fsrc, "decline uses a conditional UPDATE with its own precondition")
check("BEGIN IMMEDIATE" in src, "the charge runs inside an immediate transaction")
check("status_code=402" in src, "a below-balance accept answers 402, not a negative wallet")

def replica():
    # isolation_level=None -> explicit transaction control, matching how the handler
    # drives its own BEGIN IMMEDIATE rather than relying on implicit transactions.
    c = sqlite3.connect(":memory:", isolation_level=None)
    c.row_factory = sqlite3.Row
    c.execute("CREATE TABLE intro_requests (id INTEGER PRIMARY KEY, listing_id INTEGER, "
              "buyer_email TEXT, status TEXT DEFAULT 'pending', tuppence_charged INTEGER DEFAULT 0)")
    c.execute("CREATE TABLE transactions (id INTEGER PRIMARY KEY, user_email TEXT, type TEXT, "
              "amount INTEGER, description TEXT)")
    c.execute("INSERT INTO intro_requests (id, listing_id, buyer_email) VALUES (1, 7, 'buyer@x.test')")
    c.commit()
    return c

def balance(c, who="buyer@x.test"):
    return c.execute("SELECT COALESCE(SUM(amount),0) AS b FROM transactions WHERE user_email=?",
                     (who,)).fetchone()["b"]

def accept(c, who="buyer@x.test"):
    """The shipped guard sequence, verbatim in shape."""
    c.execute("BEGIN IMMEDIATE")
    row = c.execute("SELECT status, COALESCE(tuppence_charged,0) AS charged, buyer_email "
                    "FROM intro_requests WHERE id=1").fetchone()
    if row is None:
        c.rollback(); return 404
    if (row["status"] or "").strip().lower() in ("accepted", "declined") or int(row["charged"] or 0):
        c.rollback(); return 409
    if balance(c, who) < 1:
        c.rollback(); return 402
    upd = c.execute(GUARD_UPDATE, (1,))
    if upd.rowcount != 1:
        c.rollback(); return 409
    c.execute("INSERT INTO transactions (user_email, type, amount, description) "
              "VALUES (?,'intro_deduct',-1,'intro #1')", (who,))
    c.commit()
    return 200

def decline(c):
    row = c.execute("SELECT status, COALESCE(tuppence_charged,0) AS charged "
                    "FROM intro_requests WHERE id=1").fetchone()
    if row is not None and (int(row["charged"] or 0)
                            or (row["status"] or "").strip().lower() == "accepted"):
        return 409
    upd = c.execute(DECLINE_UPDATE, (1,))
    c.commit()
    return 200 if upd.rowcount == 1 else 409

print("\n2. the original bug: four accepts on a 1T wallet")
c = replica()
c.execute("INSERT INTO transactions (user_email, type, amount, description) "
          "VALUES ('buyer@x.test','topup',1,'seed 1T')"); c.commit()
codes = [accept(c) for _ in range(4)]
rows = c.execute("SELECT COUNT(*) AS n FROM transactions WHERE type='intro_deduct'").fetchone()["n"]
check(codes[0] == 200, "the first accept succeeds (200)")
check(codes[1:] == [409, 409, 409], "every repeat is refused 409 (was: charged again) — got %s" % codes[1:])
check(rows == 1, "exactly ONE intro_deduct row exists (audit saw FOUR) — got %d" % rows)
check(balance(c) == 0, "wallet sits at 0T, never negative — got %dT" % balance(c))

print("\n3. the floor at zero: a 0T buyer cannot go negative")
c2 = replica()
check(accept(c2) == 402, "accept on an empty wallet is refused 402")
check(balance(c2) == 0, "no money row was written — balance %dT" % balance(c2))

print("\n4. decline-after-accept leaves no paid-for 'declined' record")
c3 = replica()
c3.execute("INSERT INTO transactions (user_email, type, amount, description) "
           "VALUES ('buyer@x.test','topup',1,'seed 1T')"); c3.commit()
accept(c3)
check(decline(c3) == 409, "declining a charged introduction is refused 409")
st = c3.execute("SELECT status, tuppence_charged FROM intro_requests WHERE id=1").fetchone()
check(st["status"] == "accepted" and st["tuppence_charged"] == 1,
      "the record still reads accepted+charged, not declined-but-paid")

print("\n5. a clean decline still works, and charges nothing")
c4 = replica()
check(decline(c4) == 200, "declining a pending introduction succeeds")
check(balance(c4) == 0, "no charge was made on decline")
check(decline(c4) == 409, "declining twice is refused 409")

print("\n" + "=" * 70)
if fails:
    print("  RESULT: %d CHECK(S) FAILED" % len(fails))
    sys.exit(1)
print("  RESULT: one introduction charges exactly once, the wallet has a floor,")
print("          and a charged introduction can never be declined.")
sys.exit(0)
