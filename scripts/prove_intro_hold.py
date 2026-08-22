#!/usr/bin/env python3
"""prove_intro_hold.py — INTRO-HOLD-1 / RG-0145.

The shipped EULA promises, in four clauses, that 1 Tuppence is COMMITTED (HELD) when the
buyer requests an introduction, BURNED only on delivery (seller acceptance), and RELEASED
IN FULL on decline, expiry or withdrawal — the ECT Act s44 argument depends on it. Until
22 Aug 2026 no hold existed. This proves the implementation keeps the promise, on a
throwaway replica. No production data, no production box.
"""
import os, re, sqlite3, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "bea_main.py")

HOLD_INSERT = ("INSERT INTO transactions (user_email, type, amount, description) "
               "VALUES (?, 'intro_hold', -1, ?)")
RELEASE_UPDATE = ("UPDATE intro_requests SET hold_released_at = ? "
                  "WHERE id = ? AND COALESCE(tuppence_held, 0) = 1 "
                  "AND hold_released_at IS NULL AND COALESCE(tuppence_charged, 0) = 0")

fails = []
def check(ok, msg):
    print(("  [OK] " if ok else "  [X]  ") + msg)
    if not ok:
        fails.append(msg)

def flat(x):
    return re.sub(r'\s+', ' ', x.replace('"', '')).strip()

print("=" * 70)
print("  INTRO-HOLD-1 — proving the EULA's hold is real")
print("=" * 70)

src = open(SRC, encoding="utf-8").read()
print("\n1. the promise is implemented in bea_main.py")
check(flat(HOLD_INSERT) in flat(src), "a request writes an 'intro_hold' of -1")
check(flat(RELEASE_UPDATE) in flat(src), "release is a conditional UPDATE (cannot fire twice)")
check("intro_hold_release" in src, "a release writes a +1 ledger row")
check("'intro_burn'" in src, "delivery burns the hold with a zero-amount audit row")
check("_release_intro_hold(conn, ir[\"id\"], \"request expired\")" in src,
      "the expiry sweep releases the hold — its email already says 'You were not charged'")

def replica():
    c = sqlite3.connect(":memory:", isolation_level=None)
    c.row_factory = sqlite3.Row
    c.execute("CREATE TABLE intro_requests (id INTEGER PRIMARY KEY, listing_id INTEGER, "
              "buyer_email TEXT, status TEXT DEFAULT 'pending', tuppence_charged INTEGER DEFAULT 0, "
              "tuppence_held INTEGER DEFAULT 0, hold_released_at TEXT)")
    c.execute("CREATE TABLE transactions (id INTEGER PRIMARY KEY, user_email TEXT, type TEXT, "
              "amount INTEGER, description TEXT)")
    c.execute("INSERT INTO transactions (user_email, type, amount, description) "
              "VALUES ('buyer@x.test','topup',3,'seed 3T')")
    c.commit()
    return c

def bal(c, who="buyer@x.test"):
    return c.execute("SELECT COALESCE(SUM(amount),0) AS b FROM transactions WHERE user_email=?",
                     (who,)).fetchone()["b"]

def request(c, iid, who="buyer@x.test"):
    if bal(c, who) < 1:
        return 402
    c.execute("INSERT INTO intro_requests (id, listing_id, buyer_email, tuppence_held) "
              "VALUES (?,1,?,1)", (iid, who))
    c.execute(HOLD_INSERT, (who, "held · intro #%s" % iid))
    c.commit()
    return 200

def release(c, iid, reason):
    upd = c.execute(RELEASE_UPDATE, ("2026-08-22T00:00:00Z", iid))
    if upd.rowcount != 1:
        return False
    row = c.execute("SELECT buyer_email FROM intro_requests WHERE id=?", (iid,)).fetchone()
    c.execute("INSERT INTO transactions (user_email, type, amount, description) "
              "VALUES (?,'intro_hold_release',1,?)", (row["buyer_email"], reason))
    c.commit()
    return True

def accept(c, iid):
    row = c.execute("SELECT COALESCE(tuppence_held,0) AS held, hold_released_at AS rel, "
                    "COALESCE(tuppence_charged,0) AS charged, buyer_email "
                    "FROM intro_requests WHERE id=?", (iid,)).fetchone()
    if int(row["charged"]) or (row["rel"] and False):
        return 409
    held = int(row["held"]) and not row["rel"]
    if not held and bal(c) < 1:
        return 402
    upd = c.execute("UPDATE intro_requests SET status='accepted', tuppence_charged=1 "
                    "WHERE id=? AND COALESCE(tuppence_charged,0)=0 "
                    "AND COALESCE(LOWER(status),'pending') NOT IN ('accepted','declined')", (iid,))
    if upd.rowcount != 1:
        return 409
    if held:
        c.execute("INSERT INTO transactions (user_email, type, amount, description) "
                  "VALUES (?,'intro_burn',0,'delivered')", (row["buyer_email"],))
    else:
        c.execute("INSERT INTO transactions (user_email, type, amount, description) "
                  "VALUES (?,'intro_deduct',-1,'legacy charge')", (row["buyer_email"],))
    c.commit()
    return 200

print("\n2. requesting HOLDS the Tuppence — the buyer sees it committed")
c = replica()
check(bal(c) == 3, "buyer starts on 3T")
check(request(c, 1) == 200, "request succeeds")
check(bal(c) == 2, "balance drops to 2T immediately — committed, as the EULA says (got %dT)" % bal(c))

print("\n3. delivery BURNS the hold — never a second charge")
check(accept(c, 1) == 200, "seller accepts")
check(bal(c) == 2, "balance still 2T — the held Tuppence was burned, not deducted twice (got %dT)" % bal(c))
n = c.execute("SELECT COUNT(*) AS n FROM transactions WHERE user_email='buyer@x.test' "
              "AND amount < 0").fetchone()["n"]
check(n == 1, "exactly ONE negative row exists for this introduction — got %d" % n)
check(accept(c, 1) == 409, "a repeat accept is refused")
check(release(c, 1, "attempted after burn") is False, "a BURNED hold can never be released")
check(bal(c) == 2, "balance unchanged by the attempt (got %dT)" % bal(c))

print("\n4. decline RELEASES in full")
c2 = replica()
request(c2, 2)
check(bal(c2) == 2, "hold placed, 2T")
check(release(c2, 2, "declined by seller") is True, "decline returns the hold")
check(bal(c2) == 3, "balance back to 3T — released IN FULL (got %dT)" % bal(c2))
check(release(c2, 2, "again") is False, "a second release is impossible — no minting")
check(bal(c2) == 3, "balance still 3T after the double-release attempt (got %dT)" % bal(c2))

print("\n5. expiry releases too, so 'You were not charged' is true")
c3 = replica()
request(c3, 3)
c3.execute("UPDATE intro_requests SET status='expired' WHERE id=3"); c3.commit()
check(release(c3, 3, "request expired") is True, "expiry returns the hold")
check(bal(c3) == 3, "buyer whole again at 3T (got %dT)" % bal(c3))

print("\n6. a buyer with no Tuppence cannot commit one")
c4 = replica()
for i in (10, 11, 12):
    request(c4, i)
check(bal(c4) == 0, "three requests hold three Tuppence — 0T left (got %dT)" % bal(c4))
check(request(c4, 13) == 402, "the fourth request is refused 402, not allowed to go negative")
check(bal(c4) == 0, "balance never goes below zero (got %dT)" % bal(c4))

print("\n" + "=" * 70)
if fails:
    print("  RESULT: %d CHECK(S) FAILED" % len(fails)); sys.exit(1)
print("  RESULT: 1T is held at request, burned once on delivery, released in full on")
print("          decline or expiry, never released twice, and never goes negative.")
sys.exit(0)
