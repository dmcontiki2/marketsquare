#!/usr/bin/env python3
"""ANON-PSEUDONYM-1 (RUL-225, David 12 Oct 2026 05:37: "Bee Lady is a pseudo name like the Handyman").

ANON-NAMES-1 (4 Oct) takes business and personal names out of an advert on every private publish and edit. When the
Bee Lady saved her adverts on 12 Oct it took "Bee Lady" out of all five titles. David's ruling: a trade pseudonym -- a
working nickname made of ordinary words for what the seller does -- is not a name. It names a trade, not a person or a
registered business, so it stays. The AI read is told so, and a fixed check drops a pseudonym the AI flags anyway.

Usage:  python3 apply_anon_pseudonym.py <repo>      Idempotent; asserts every anchor; honours the work lock."""
import io, os, re, subprocess, sys

R = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["bea_main.py", "scripts/regression_ledger.py"]
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

s = load("bea_main.py"); n0 = len(s)
assert s.rstrip().endswith(")") and "is_superuser=_gate_is_superuser" in s[-400:], "bea_main.py reads torn (MOUNT-READ-1) -- not patching"

s = rep(s, '''    "university degree); or generic words (complex, estate, townhouse, simplex). "
''', '''    "university degree); a trade pseudonym -- a working nickname made of ordinary words for what the seller does "
    "('the Bee Lady', 'the Handyman', 'the Cake Lady', 'die Byetannie'): it names a trade, not a person or a "
    "registered business, so it is NEVER a name to remove (RUL-225); "
    "or generic words (complex, estate, townhouse, simplex). "
''', "prompt")

s = rep(s, '''_ANON_NAMES_MEMO = {}   # pure memo of identical text (idempotent) -- not shared state; a cold box just asks again
''', '''_ANON_NAMES_MEMO = {}   # pure memo of identical text (idempotent) -- not shared state; a cold box just asks again

# ANON-PSEUDONYM-1 (RUL-225, David 12 Oct 2026: "Bee Lady is a pseudo name like the Handyman"): a trade pseudonym -- a
# working nickname made of ordinary words for what the seller does -- names a trade, not a person or a registered
# business, so it stays in her advert. The AI read is told so; this fixed check drops one it flags anyway (it took
# "Bee Lady" out of all five of her titles on 12 Oct). The LAST word must be a persona word; a possessive, a digit or
# a fourth word makes it an ordinary name again ("Pam's Cleaning", "Tannie Maria" and "Smith Properties" still go).
_ANON_PSEUDONYM_ROLES = frozenset((
    "lady", "man", "guy", "girl", "woman", "auntie", "aunty", "uncle", "tannie", "oom", "queen", "king", "doctor",
    "doc", "whisperer", "wizard", "guru", "mama", "papa", "gogo", "handyman", "handywoman", "handylady"))


def _anon_is_trade_pseudonym(name) -> bool:
    w = re.sub(r"^(?:the|die|a|an)\\s+", "", str(name or "").strip().lower())
    parts = w.split()
    if not parts or len(parts) > 3 or any(not re.fullmatch(r"[a-z\\u00e0-\\u024f-]+", p) for p in parts):
        return False
    return parts[-1] in _ANON_PSEUDONYM_ROLES
''', "pseudonym helper")

s = rep(s, '''            continue                      # never the advert's own suburb; never a name the text does not contain
''', '''            continue                      # never the advert's own suburb; never a name the text does not contain
        if _anon_is_trade_pseudonym(nt):
            continue                      # ANON-PSEUDONYM-1 (RUL-225): 'the Bee Lady', 'the Handyman' -- a trade, not a person
''', "backstop")
compile(s, "bea_main.py", "exec")
save("bea_main.py", s)

g = load("scripts/regression_ledger.py")
if "ANON-PSEUDONYM-1 (RUL-225" not in g:
    nums = [int(x) for x in re.findall(r"@entry\(.RG-(\d{4}).", g)]
    rid = "RG-%04d" % (max(nums) + 1)
    ENTRY = '''

@entry("%s", "ANON-PSEUDONYM-1 (RUL-225, David 12 Oct 2026: 'Bee Lady is a pseudo name like the Handyman'): a trade pseudonym "
       "stays in an advert -- the name removal took 'Bee Lady' out of all five of her titles when she saved them",
       OPEN, fixed_on="2026-10-12",
       scope="bea_main.py _ANON_NAMES_SYSTEM (the AI read is told a trade pseudonym is never a name) + _anon_is_trade_pseudonym "
             "in _anon_names_find (a fixed check drops one the AI flags anyway). Real names still go. Table-tested here.",
       ref="RULINGS.md RUL-225. Journal 12 Oct 2026 02:29-02:35Z: 'ANON-NAMES-1 (edit #538) ... [Bee Lady]' on #273/#274/#275/#538/#539.")
def rg_anon_pseudonym_1():
    py = repo_file("bea_main.py")
    if py is None:
        return [(INFO, "NOT EVALUATED - repo not readable from here")]
    import re as _re
    out = []
    p = py.find("_ANON_NAMES_SYSTEM = (")
    if p < 0 or "'the Bee Lady', 'the Handyman'" not in py[p:p + 4000] or "NEVER a name to remove (RUL-225)" not in py[p:p + 4000]:
        out.append((FAIL, "the name read is no longer told that a trade pseudonym stays"))
    f = py.find("def _anon_names_find(")
    if f < 0 or "if _anon_is_trade_pseudonym(nt):" not in py[f:f + 3500]:
        out.append((FAIL, "the fixed pseudonym check left the name read -- 'Bee Lady' can be taken out again"))
    i = py.find("_ANON_PSEUDONYM_ROLES = frozenset(")
    j = py.find("\\n\\ndef _anon_names_find(", i)
    if i < 0 or j < 0:
        return out + [(FAIL, "the trade-pseudonym rule is gone")]
    ns = {"re": _re}
    try:
        exec(py[i:j], ns)
    except Exception as e:
        return out + [(FAIL, "the trade-pseudonym rule no longer runs on its own: %%r" %% (e,))]
    keep = ["Bee Lady", "the Bee Lady", "The Handyman", "Handyman", "the Cake Lady", "die Bye Tannie", "Plant Man"]
    go = ["Pam's Cleaning", "Smith Properties", "iQ Rondebosch", "Tannie Maria", "Villa Toscana", "Marietjie", "Misty Forest",
          "Kronborg Luxury Apartments", "The Willows Estate", "Lady Grey"]
    for n in keep:
        if not ns["_anon_is_trade_pseudonym"](n):
            out.append((FAIL, "the trade pseudonym %%r would be taken out of an advert" %% n))
    for n in go:
        if ns["_anon_is_trade_pseudonym"](n):
            out.append((FAIL, "the real name %%r would be left in an advert as a pseudonym" %% n))
    return out or [(INFO, "a trade pseudonym stays, a real name still goes (%%d + %%d cases)" %% (len(keep), len(go)))]
''' % rid
    a = "\n\ndef _server_vantage_wrap():"
    assert g.count(a) == 1, "anchor ledger tail: %d" % g.count(a)
    g = g.replace(a, ENTRY.rstrip("\n") + "\n" + a)
    print("ledger entry", rid)
compile(g, "regression_ledger.py", "exec"); save("scripts/regression_ledger.py", g)
print("ANON-PSEUDONYM-1 applied: bea_main.py %d -> %d chars" % (n0, len(s)))
