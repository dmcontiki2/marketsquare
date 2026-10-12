#!/usr/bin/env python3
"""TRUST-BADGE-ONE-RULE-1 (David, 12 Oct 2026: "i see a recurring fault, her TS has gone to 90 - it was still 100 last
night and even shows 100 on the detail but show 90 in the adverts").

Cause, from the server journal: the Bee Lady opened Edit on her Services adverts (#538, #539). Edit asks
/trust-score/breakdown?category=Services-Technical, which scored her under the Services set (90) and wrote 90 onto her
Services adverts. The buyer's panel (/sellers/credentials/<id>) scores her under the Local Market set (100) -- SUPER-CRED-2,
22 Jul: a seller with ANY Local Market advert is scored under the Local Market model on ALL her adverts -- and writes 100.
So the badge showed whichever screen was opened last. Fourth fault in this family (base-40, TRUST-ONE-SET-1,
CRED-SCORE-SYNC-1): the seller rule was copied into two surfaces and missing from the third, and AUD-101 (4 Oct audit)
had the same shape on the profile read.

Cure: ONE key rule (_seller_score_key) and ONE badge writer (_write_listing_badges); the Edit screen, the buyer's panel,
the profile read and the credential decision all go through them. Write scope per surface is unchanged.

Usage:  python3 apply_trust_badge_one_rule.py <repo>      Idempotent; asserts every anchor; honours the work lock."""
import io, os, re, subprocess, sys

R = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["bea_main.py", "test_trust_base40.py", "test_trust_one_set.py", "scripts/regression_ledger.py"]
if "--no-lock" not in sys.argv:
    lk = subprocess.run([sys.executable, os.path.join(R, "scripts", "work_lock.py"), "check"] + FILES, cwd=R,
                        capture_output=True, text=True)
    if lk.returncode == 3:
        print("STAND-OFF (RUL-140): " + lk.stdout.strip().splitlines()[0]); sys.exit(3)

def load(rel):
    return io.open(os.path.join(R, rel), encoding="utf-8", newline="").read()

def save(rel, s):
    p = os.path.join(R, rel)
    io.open(p, "w", encoding="utf-8", newline="").write(s)
    assert io.open(p, encoding="utf-8", newline="").read() == s, "write-back of %s did not read back identical" % rel

def rep(s, a, b, name):
    if b in s:
        return s
    assert s.count(a) == 1, "anchor %s: found %d times" % (name, s.count(a))
    return s.replace(a, b)

# ───────────────────────────── bea_main.py ─────────────────────────────
s = load("bea_main.py"); n0 = len(s)
assert s.rstrip().endswith(")") and "is_superuser=_gate_is_superuser" in s[-400:], "bea_main.py reads torn (MOUNT-READ-1) -- not patching"

HELPERS = '''

def _seller_score_key(conn, email: str, category=None, service_class=None) -> str:
    """TRUST-BADGE-ONE-RULE-1 (12 Oct 2026, David: "her TS has gone to 90 ... shows 100 on the detail but show 90 in
    the adverts"): THE rule for which signal set one advert of a seller is scored under -- in one place. SUPER-CRED-2
    (22 Jul 2026): a seller with ANY Local Market advert is scored under the Local Market model on ALL her adverts.
    The buyer's panel and the credential decision each carried a copy of that rule; the Edit screen's
    /trust-score/breakdown?category= had none (AUD-047 taught it the advert's own category on 4 Oct, never the
    seller's), so it scored the Bee Lady's Services adverts under Services (90) and wrote that over the 100 the panel
    writes -- the badge moved with whichever screen was opened last. Every surface asks here."""
    em = (email or "").strip().lower()
    if conn.execute("SELECT 1 FROM listings WHERE LOWER(seller_email) = ? "
                    "AND LOWER(TRIM(category)) IN ('local_market', 'local market') LIMIT 1", (em,)).fetchone():
        return "local_market"
    return _norm_cat_key(category, service_class) or _category_key_for_user(conn, email)


def _write_listing_badges(conn, email: str, db_category=None) -> int:
    """TRUST-BADGE-ONE-RULE-1: THE only writer of an advert's stored Trust Score badge (listings.trust_score). Each
    of the seller's adverts gets the score of the set it is scored under (_seller_score_key) -- per category AND
    service class -- so no two screens can write different numbers onto the same advert (AUD-101: the profile read
    wrote the primary-category score onto every advert; the panel and the Edit screen wrote theirs back).
    db_category narrows the write to one listings.category; the values are the same whoever asks. Does not commit.
    Returns the number of adverts whose badge changed."""
    em = (email or "").strip().lower()
    q, args = "SELECT DISTINCT category, service_class FROM listings WHERE LOWER(seller_email) = ?", [em]
    if db_category:
        q += " AND category = ?"
        args.append(db_category)
    changed = 0
    for r in conn.execute(q, args).fetchall():
        sc = int(_trust_evidence(conn, em, _seller_score_key(conn, em, r["category"], r["service_class"]))["score"])
        cur = conn.execute("UPDATE listings SET trust_score = ? WHERE LOWER(seller_email) = ? AND category = ? "
                           "AND COALESCE(service_class,'') = COALESCE(?,'') AND COALESCE(trust_score,-1) != ?",
                           (sc, em, r["category"], r["service_class"], sc))
        changed += max(0, cur.rowcount or 0)
    return changed
'''
if "def _seller_score_key(" not in s:
    a = "    return _TRUST_CAT_NORM.get(cat, cat)\n"
    assert s.count(a) == 1, "anchor norm-key tail: %d" % s.count(a)
    s = s.replace(a, a + HELPERS)

# the buyer's panel: the key
s = rep(s,
'''        _is_lm = (l["category"] or "").strip().lower() in ("local_market", "local market")
        if not _is_lm:
            _is_lm = bool(conn.execute(
                "SELECT 1 FROM listings WHERE LOWER(seller_email)=? AND category='local_market' LIMIT 1",
                (email,)).fetchone())
        cat_key = "local_market" if _is_lm else (
            _norm_cat_key(l["category"], l["service_class"]) or _category_key_for_user(conn, email))
''',
'''        cat_key = _seller_score_key(conn, email, l["category"], l["service_class"])   # TRUST-BADGE-ONE-RULE-1: the one rule
        _is_lm = (cat_key == "local_market")
''', "panel key")

# the buyer's panel: the heal
s = rep(s,
'''            conn.execute(
                "UPDATE listings SET trust_score = ? WHERE LOWER(seller_email) = ? AND category = ? AND trust_score != ?",
                (_persist, email, l["category"], _persist))
            conn.commit()
''',
'''            # TRUST-BADGE-ONE-RULE-1: badges go through the one writer -- this advert's category only (the panel's
            # write authority, TRUST-ONE-SET-1), each service class under its own set; unconditional (LISTINGS-SYNC).
            _write_listing_badges(conn, email, l["category"])
            conn.commit()
''', "panel heal")

# the Edit screen / profile read: the key
s = rep(s,
'''    cat_key = _norm_cat_key(category) if category else _category_key_for_user(conn, email)
''',
'''    # TRUST-BADGE-ONE-RULE-1 (12 Oct 2026): a ?category= read obeys the seller rule too -- a Local Market seller's
    # Services advert is scored under the Local Market model here exactly as on the buyer's panel (SUPER-CRED-2).
    cat_key = _seller_score_key(conn, email, category) if category else _category_key_for_user(conn, email)
''', "breakdown key")

# the profile read: every advert under its own set (AUD-101)
s = rep(s,
'''        # Sync score to all listing rows for this seller+category so the
        # browse card badge stays accurate without a separate job.
        conn.execute(
            "UPDATE listings SET trust_score = ? WHERE LOWER(seller_email) = LOWER(?)",
            (score_total, email)
        )
        conn.commit()
''',
'''        # TRUST-BADGE-ONE-RULE-1 (AUD-101): each advert's badge is written under ITS OWN set by the one writer. This
        # used to put the primary-category score on every advert, and the panel / Edit screen wrote theirs back.
        _write_listing_badges(conn, email)
        conn.commit()
''', "breakdown profile write")

# the Edit screen: this category's adverts, through the one writer
s = rep(s,
'''        conn.execute(
            "UPDATE listings SET trust_score = ? WHERE LOWER(seller_email) = LOWER(?) AND category = ?",
            (score_total, email, db_cat)
        )
        conn.commit()
''',
'''        _write_listing_badges(conn, email, db_cat)   # TRUST-BADGE-ONE-RULE-1: the one writer -- never a score computed here
        conn.commit()
''', "breakdown category write")

# the credential decision
s = rep(s,
'''        _em = (req.email or "").strip().lower()
        _rows = conn.execute("SELECT DISTINCT category, service_class FROM listings WHERE LOWER(seller_email) = ?",
                             (_em,)).fetchall()
        _lm_any = any((r["category"] or "").strip().lower() in ("local_market", "local market") for r in _rows)
        for _r in _rows:
            _ck = "local_market" if _lm_any else (_norm_cat_key(_r["category"], _r["service_class"])
                                                  or _category_key_for_user(conn, _em))
            _sc = int(_trust_evidence(conn, _em, _ck)["score"])
            conn.execute("UPDATE listings SET trust_score = ? WHERE LOWER(seller_email) = ? AND category = ? "
                         "AND COALESCE(service_class,'') = COALESCE(?,'') AND COALESCE(trust_score,-1) != ?",
                         (_sc, _em, _r["category"], _r["service_class"], _sc))
''',
'''        _em = (req.email or "").strip().lower()
        _write_listing_badges(conn, _em)   # TRUST-BADGE-ONE-RULE-1: the same one writer every other surface uses
''', "credential decision sync")

n_up = len(re.findall(r"UPDATE listings\s+SET\s+trust_score\s*=\s*\?", s))
assert n_up == 1, "after the patch %d places still write listings.trust_score -- expected the one writer only" % n_up
compile(s, "bea_main.py", "exec")
save("bea_main.py", s)

# ───────────────────────────── test_trust_base40.py ─────────────────────────────
t = load("test_trust_base40.py")
t = rep(t,
'''    ls = body.find("UPDATE listings SET trust_score")
    assert ls != -1 and "AND trust_score != ?" in body, \\
        "listings self-heal must be unconditional (guarded only by value-changed)"
''',
'''    # TRUST-BADGE-ONE-RULE-1 (12 Oct 2026): the heal goes through the one writer, _write_listing_badges. It must
    # still be unconditional here -- at the indent of the users-differ `if`, never inside it -- and the
    # value-changed guard now lives in the writer.
    lines = body.split("\\n")
    ifs = [x for x in lines if x.strip().startswith("if cat_key == _category_key_for_user(conn, email)")]
    calls = [x for x in lines if x.strip().startswith('_write_listing_badges(conn, email, l["category"])')]
    assert ifs and calls and (len(calls[0]) - len(calls[0].lstrip())) == (len(ifs[0]) - len(ifs[0].lstrip())), \\
        "listings self-heal must be unconditional (guarded only by value-changed)"
    w = _func_body(src, "def _write_listing_badges(")
    assert "UPDATE listings SET trust_score" in w and "COALESCE(trust_score,-1) != ?" in w, \\
        "the one badge writer lost its value-changed guard"
''', "base40 heal test")
compile(t, "test_trust_base40.py", "exec"); save("test_trust_base40.py", t)

# ───────────────────────────── test_trust_one_set.py ─────────────────────────────
t = load("test_trust_one_set.py")
t = rep(t,
'''    body = _func_body(SRC, "def seller_public_credentials(")
    ups = re.findall(r"UPDATE listings SET trust_score[^\\"']*", body)
    assert ups, "the panel's listing heal disappeared"
    for u in ups:
        assert "AND category" in u, \\
            "the panel wrote a per-listing score to EVERY listing: %r" % u
''',
'''    body = _func_body(SRC, "def seller_public_credentials(")
    # TRUST-BADGE-ONE-RULE-1 (12 Oct 2026): the panel no longer carries an UPDATE of its own -- it asks the one
    # writer, and only for THIS advert's category.
    assert not re.findall(r"UPDATE listings\\s+SET\\s+trust_score", body), \\
        "the panel writes badges itself again -- only _write_listing_badges may"
    assert '_write_listing_badges(conn, email, l["category"])' in body, \\
        "the panel's listing heal disappeared, or lost its category scope"
''', "one-set panel scope test")
NEW_TESTS = '''
# ---- TRUST-BADGE-ONE-RULE-1 (12 Oct 2026): one key rule, one badge writer ----
# The fourth bug in this family. David: "her TS has gone to 90 - it was still 100 last night and even shows 100 on
# the detail but show 90 in the adverts". The Edit screen scored the Bee Lady's Services adverts under Services (90);
# the buyer's panel scored them under Local Market (100, SUPER-CRED-2); each wrote its own number onto the cards.
def test_one_rule_decides_the_set_on_every_surface():
    key = _func_body(SRC, "def _seller_score_key(")
    assert "local_market" in key and "_norm_cat_key(category, service_class)" in key, \\
        "the seller rule (any Local Market advert -> Local Market model on all her adverts) left _seller_score_key"
    assert "_seller_score_key(conn, email, category)" in _func_body(SRC, "def trust_score_breakdown("), \\
        "the Edit screen's ?category= read ignores the seller rule again"
    assert '_seller_score_key(conn, email, l["category"], l["service_class"])' in _func_body(SRC, "def seller_public_credentials("), \\
        "the buyer's panel decides the signal set on its own again"
    assert "_seller_score_key(" in _func_body(SRC, "def _write_listing_badges("), \\
        "the badge writer scores an advert without the seller rule"

def test_only_the_one_writer_writes_a_badge():
    ups = re.findall(r"UPDATE listings\\s+SET\\s+trust_score\\s*=\\s*\\?", SRC)
    assert len(ups) == 1, "%d places write listings.trust_score -- only _write_listing_badges may" % len(ups)
    assert "UPDATE listings SET trust_score" in _func_body(SRC, "def _write_listing_badges("), \\
        "the one badge writer no longer writes the badge"
    for fn in ("def seller_public_credentials(", "def trust_score_breakdown(", "def trust_score_set_credential("):
        assert "_write_listing_badges(" in _func_body(SRC, fn), "%s no longer heals the badges" % fn

'''
if "def test_only_the_one_writer_writes_a_badge" not in t:
    a = '\nif __name__ == "__main__":\n'
    assert t.count(a) == 1, "anchor one-set runner: %d" % t.count(a)
    t = t.replace(a, NEW_TESTS + a.lstrip("\n"))
compile(t, "test_trust_one_set.py", "exec"); save("test_trust_one_set.py", t)

# ───────────────────────────── scripts/regression_ledger.py ─────────────────────────────
g = load("scripts/regression_ledger.py")
g = rep(g,
'''    if "CRED-SCORE-SYNC-1" not in body or '_trust_evidence(conn, _em, _ck)["score"]' not in body or "UPDATE listings SET trust_score" not in body:
''',
'''    # TRUST-BADGE-ONE-RULE-1 (12 Oct 2026): the decision calls the one badge writer; the writer holds the scoring and the SQL.
    _w = py.find("def _write_listing_badges(")
    _wb = py[_w:_w + 2500] if _w >= 0 else ""
    if ("CRED-SCORE-SYNC-1" not in body or "_write_listing_badges(conn, _em)" not in body
            or "_trust_evidence(" not in _wb or "UPDATE listings SET trust_score" not in _wb):
''', "RG-0681 assertion")
if "TRUST-BADGE-ONE-RULE-1 (David, 12 Oct 2026)" not in g:
    nums = [int(x) for x in re.findall(r"@entry\(.RG-(\d{4}).", g)]
    rid = "RG-%04d" % (max(nums) + 1)
    ENTRY = '''

@entry("%s", "TRUST-BADGE-ONE-RULE-1 (David, 12 Oct 2026): a seller's Trust Score badge is the same on every screen -- the "
       "Bee Lady's adverts read 100 on the detail and 90 on the cards, moving with whichever screen was opened last",
       OPEN, fixed_on="2026-10-12",
       scope="bea_main.py _seller_score_key (the one key rule, SUPER-CRED-2) + _write_listing_badges (the one badge writer); "
             "trust_score_breakdown, seller_public_credentials, trust_score_set_credential all go through them. "
             "Proved on a copy of the live database by scripts/prove_trust_badge_one_rule.py.",
       ref="David 12 Oct 2026. Server journal: Edit's /trust-score/breakdown?category=Services-Technical wrote 90 on #538/#539 "
           "while /sellers/credentials/<id> writes 100 (Local Market model). Fourth in the family after base-40, "
           "TRUST-ONE-SET-1 and CRED-SCORE-SYNC-1; closes AUD-101 (4 Oct audit).")
def rg_trust_badge_one_rule_1():
    py = repo_file("bea_main.py")
    if py is None:
        return [(INFO, "NOT EVALUATED - repo not readable from here")]
    import re as _re
    out = []
    if "def _seller_score_key(" not in py or "def _write_listing_badges(" not in py:
        return [(FAIL, "the one rule and the one writer for an advert's Trust Score badge are gone")]
    n = len(_re.findall(r"UPDATE listings\\s+SET\\s+trust_score\\s*=\\s*\\?", py))
    if n != 1:
        out.append((FAIL, "%%d places write an advert's Trust Score badge -- only _write_listing_badges may" %% n))
    k = py.find("def _seller_score_key("); kb = py[k:k + 2200]
    if "local_market" not in kb or "_norm_cat_key(category, service_class)" not in kb:
        out.append((FAIL, "_seller_score_key lost the seller rule (any Local Market advert -> Local Market model)"))
    for fn, need, said in (
            ("def trust_score_breakdown(", "_seller_score_key(conn, email, category)", "the Edit screen scores a Local Market seller's other adverts under the wrong set again"),
            ("def seller_public_credentials(", '_seller_score_key(conn, email, l["category"], l["service_class"])', "the buyer's panel decides the signal set on its own again"),
            ("def trust_score_set_credential(", "_write_listing_badges(conn, _em)", "a credential decision no longer writes the badges through the one writer")):
        i = py.find(fn)
        j = py.find("\\n@app.", i + 10)
        if i < 0 or need not in py[i:(j if j > i else i + 12000)]:
            out.append((FAIL, said))
    return out or [(INFO, "one rule decides the signal set and one writer writes every Trust Score badge")]
''' % rid
    a = "\n\ndef _server_vantage_wrap():"
    assert g.count(a) == 1, "anchor ledger tail: %d" % g.count(a)
    g = g.replace(a, ENTRY.rstrip("\n") + "\n" + a)
    print("ledger entry", rid)
compile(g, "regression_ledger.py", "exec"); save("scripts/regression_ledger.py", g)

print("TRUST-BADGE-ONE-RULE-1 applied: bea_main.py %d -> %d chars" % (n0, len(s)))
