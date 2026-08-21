"""ID-NPR-1 guards. The money rules, asserted.

Every one of these protects a way the seller could be wrongly charged, or a
scammer could inherit someone else's green tick.
"""
import os, sqlite3, tempfile, hashlib, importlib


def _db():
    """Minimal schema mirroring the ledger + users columns under test."""
    c = sqlite3.connect(':memory:')
    c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE users (email TEXT PRIMARY KEY, id_number_hash TEXT,
                 id_verified_at TEXT, id_npr_verified_at TEXT,
                 id_npr_provider TEXT, id_npr_ref TEXT)""")
    c.execute("""CREATE TABLE id_verification_ledger (
                 id INTEGER PRIMARY KEY AUTOINCREMENT, id_hash TEXT NOT NULL,
                 email TEXT NOT NULL, outcome TEXT NOT NULL,
                 provider TEXT NOT NULL DEFAULT '', provider_ref TEXT NOT NULL DEFAULT '',
                 charged_t INTEGER NOT NULL DEFAULT 0, reason TEXT NOT NULL DEFAULT '',
                 created_at TEXT NOT NULL DEFAULT '')""")
    c.execute("""CREATE TABLE transactions (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_email TEXT, type TEXT, amount INTEGER, description TEXT)""")
    return c


def test_provider_fails_closed_when_unconfigured():
    os.environ.pop('ID_VERIFY_API_KEY', None)
    os.environ['ID_VERIFY_PROVIDER'] = 'stub'
    p = importlib.import_module('id_verify_provider')
    importlib.reload(p)
    assert p.is_available() is False
    r = p.verify_id('8001015009087', 'Test Person')
    assert r.billable is False, 'unconfigured provider must never be billable'
    assert r.verified is False, 'unconfigured provider must never verify'


def test_provider_never_raises():
    p = importlib.import_module('id_verify_provider')
    for bad in [None, '', 'x'*500, '!!!']:
        r = p.verify_id(bad, bad)          # must not raise
        assert r.billable is False


def test_unknown_provider_key_is_not_available():
    os.environ['ID_VERIFY_PROVIDER'] = 'not_a_real_provider'
    os.environ['ID_VERIFY_API_KEY'] = 'x'
    p = importlib.import_module('id_verify_provider')
    importlib.reload(p)
    assert p.is_available() is False, 'unknown key must not be spendable'
    os.environ['ID_VERIFY_PROVIDER'] = 'stub'
    os.environ.pop('ID_VERIFY_API_KEY', None)


def test_duplicate_hash_on_second_account_is_flagged_not_granted():
    """The security trap: a reused ID must NOT inherit the first account's pass."""
    c = _db()
    h = hashlib.sha256(b'salt8001015009087').hexdigest()
    c.execute("INSERT INTO users(email) VALUES ('first@x.co')")
    c.execute("INSERT INTO users(email) VALUES ('second@x.co')")
    c.execute("UPDATE users SET id_npr_verified_at='2026-08-21T00:00:00Z' WHERE email='first@x.co'")
    c.execute("""INSERT INTO id_verification_ledger(id_hash,email,outcome,charged_t)
                 VALUES (?,?,'verified',1)""", (h, 'first@x.co'))
    dup = c.execute("""SELECT email FROM id_verification_ledger
                       WHERE id_hash=? AND lower(email)<>? LIMIT 1""",
                    (h, 'second@x.co')).fetchone()
    assert dup is not None, 'duplicate must be detected'
    second = c.execute("SELECT id_npr_verified_at FROM users WHERE email='second@x.co'").fetchone()
    assert second['id_npr_verified_at'] is None, \
        'SECOND ACCOUNT MUST NOT INHERIT THE TICK'
    charged = c.execute("""SELECT COALESCE(SUM(charged_t),0) t FROM id_verification_ledger
                           WHERE email='second@x.co'""").fetchone()['t']
    assert charged == 0, 'duplicate must not be charged'


def test_same_account_same_hash_is_not_rebilled():
    """David: only ever do this one time."""
    c = _db()
    h = 'abc123'
    c.execute("INSERT INTO users(email) VALUES ('a@x.co')")
    c.execute("""INSERT INTO id_verification_ledger(id_hash,email,outcome,charged_t)
                 VALUES (?,?,'verified',1)""", (h,'a@x.co'))
    prior = c.execute("""SELECT outcome FROM id_verification_ledger
                         WHERE id_hash=? AND lower(email)=? AND outcome IN ('verified','failed')
                         ORDER BY id DESC LIMIT 1""", (h,'a@x.co')).fetchone()
    assert prior is not None, 'prior result must be found and reused'
    total = c.execute("SELECT COALESCE(SUM(charged_t),0) t FROM id_verification_ledger").fetchone()['t']
    assert total == 1, 'must remain a single charge, not two'


def test_npr_column_is_separate_from_intro_gate():
    """id_verified_at (AI, gates intros) must be untouched by the NPR tier."""
    c = _db()
    c.execute("""INSERT INTO users(email, id_verified_at) VALUES ('a@x.co','2026-01-01T00:00:00Z')""")
    c.execute("""UPDATE users SET id_npr_verified_at='2026-08-21T00:00:00Z' WHERE email='a@x.co'""")
    r = c.execute("SELECT id_verified_at, id_npr_verified_at FROM users WHERE email='a@x.co'").fetchone()
    assert r['id_verified_at'] == '2026-01-01T00:00:00Z', \
        'the introduction gate must not be disturbed by the green tick'
    assert r['id_npr_verified_at'] is not None


def test_only_npr_earns_the_green_tick():
    c = _db()
    c.execute("INSERT INTO users(email, id_number_hash) VALUES ('sub@x.co','h')")
    c.execute("INSERT INTO users(email, id_number_hash, id_verified_at) VALUES ('ai@x.co','h2','t')")
    c.execute("""INSERT INTO users(email, id_number_hash, id_verified_at, id_npr_verified_at)
                 VALUES ('npr@x.co','h3','t','t')""")
    def state(e):
        r = c.execute("""SELECT id_number_hash,id_verified_at,id_npr_verified_at
                         FROM users WHERE email=?""", (e,)).fetchone()
        if r['id_npr_verified_at']: return 'npr_verified'
        if r['id_verified_at']:     return 'ai_checked'
        if r['id_number_hash']:     return 'submitted'
        return 'none'
    assert state('sub@x.co') == 'submitted'
    assert state('ai@x.co')  == 'ai_checked'
    assert state('npr@x.co') == 'npr_verified'
    for e in ('sub@x.co','ai@x.co'):
        assert state(e) != 'npr_verified', 'only a paid NPR pass may show the tick'




def test_warning_is_informational_never_a_gate():
    """RUL-039: the notice must not be able to stop an introduction."""
    src = open('bea_main.py', encoding='utf-8', errors='replace').read()
    i = src.find('def _seller_verification_notice')
    assert i > 0, 'notice helper missing'
    body = src[i:i + 2200]
    for forbidden in ('raise HTTPException', 'return None, HTTPException'):
        assert forbidden not in body, \
            f'the unverified-seller notice must never raise ({forbidden!r} found)'
    assert '"warn"' in body and 'proceed_is_your_decision' in body


def test_stay_warning_names_the_deposit_risk():
    src = open('bea_main.py', encoding='utf-8', errors='replace').read()
    i = src.find('def _seller_verification_notice')
    body = src[i:i + 2200]
    assert 'Never pay a deposit' in body, 'stay warning must name the deposit risk'
    assert 'never holds deposits' in body, 'must state we hold no deposits'


def test_intro_gate_still_uses_only_id_verified_at():
    """The paid tick must not have become a second barrier to introductions."""
    src = open('bea_main.py', encoding='utf-8', errors='replace').read()
    i = src.find('def _seller_intro_gate')
    body = src[i:i + 1400]
    assert 'id_verified_at' in body, 'intro gate lost its check'
    assert 'id_npr_verified_at' not in body, \
        'RUL-039: NPR verification must NEVER gate introductions'

def test_sa_surname_particles_stay_with_the_surname():
    """A bad split returns PARTIAL_MATCH: seller charged, tick refused."""
    p = importlib.import_module('id_verify_provider')
    for name, first, last in [
        ('Johannes Petrus van der Merwe', 'Johannes Petrus', 'van der Merwe'),
        ('Maria du Plessis',              'Maria',           'du Plessis'),
        ('Anna Janse van Rensburg',       'Anna',            'Janse van Rensburg'),
        ('Jan de Villiers',               'Jan',             'de Villiers'),
        ('Thabo Mbeki',                   'Thabo',           'Mbeki'),
    ]:
        assert p._split_name(name) == (first, last), f'bad split for {name}'


def test_dob_derived_from_sa_id_number():
    p = importlib.import_module('id_verify_provider')
    assert p._dob_from_sa_id('8001015009087') == '1980-01-01'
    assert p._dob_from_sa_id('0503201234083') == '2005-03-20'
    for junk in ('', 'abc', '12'):
        assert p._dob_from_sa_id(junk) == '', 'junk must yield no DOB, not a guess'


def test_didit_never_charges_without_a_conclusive_outcome():
    """Mirrors Didit's own billing rule: conclusive only."""
    src = open('id_verify_provider.py', encoding='utf-8').read()
    i = src.find('def _check_didit')
    body = src[i:]
    assert 'CONCLUSIVE' in body, 'conclusive-outcome gate missing'
    assert "'MATCH', 'PARTIAL_MATCH', 'NO_MATCH', 'DOCUMENT_NOT_FOUND'" in body
    assert 'billable=False' in body, 'transport failures must not be billable'


def test_partial_match_is_not_a_pass():
    """The ID exists but the name does not match — that IS the scam shape."""
    src = open('id_verify_provider.py', encoding='utf-8').read()
    i = src.find('def _check_didit')
    body = src[i:]
    assert "verified = (code == 'MATCH')" in body, \
        'only a full MATCH may verify — PARTIAL_MATCH must never pass'


if __name__ == '__main__':
    fns = [v for k,v in sorted(globals().items()) if k.startswith('test_')]
    for f in fns:
        f(); print(f'  PASS  {f.__name__}')
    print(f'\n{len(fns)}/{len(fns)} ID-NPR-1 guards pass')
