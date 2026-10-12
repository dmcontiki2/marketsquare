#!/usr/bin/env python3
"""ANON-TITLE-TAIL-1 (12 Oct 2026, found on the Bee Lady's five adverts while fixing her audit price for David).

ANON-NAMES-1 (4 Oct) takes business and personal names out of an advert on every private publish and edit. In a
title the name "simply goes" -- and the words that led up to it stayed. When she saved her adverts on 12 Oct all five
titles went live as "... — by the" / "... via the", and "Misty Forest raw honey" became "raw honey".
A title never ends on a joining word or a dash, and never starts in lower case because the name in front of it went.

Usage:  python3 apply_anon_title_tail.py <repo>      Idempotent; asserts every anchor; honours the work lock."""
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

s = rep(s, '''def _anon_names_apply(text, names, title=False):
    if not text or not names:
        return text
''', '''# ANON-TITLE-TAIL-1 (12 Oct 2026, the Bee Lady's five adverts): ANON-NAMES-1 takes a name out of a title and the words
# that led up to it stayed -- "Beehive Audit & Consulting for farms — by the", live to every buyer. A title never
# ends on a joining word or a dash, and never starts in lower case because the name in front of it went.
_ANON_TITLE_TAIL_RX = re.compile(
    r"(?i)[\\s,;:|/\\u2013\\u2014-]*\\b(?:next to|close to|by|via|from|at|with|for|of|in|near|on|opposite|inside|behind"
    r"|deur|van|naby|op)(?:\\s+(?:the|a|an|die|'n))?\\s*$")


def _anon_title_tidy(out, original=""):
    t = out or ""
    for _ in range(3):
        t2 = re.sub(r"[\\s,;:|/\\u2013\\u2014-]+$", "", _ANON_TITLE_TAIL_RX.sub("", t))
        if t2 == t:
            break
        t = t2
    t = re.sub(r"^[\\s,;:|/\\u2013\\u2014-]+", "", t)
    if t and t[0].islower() and (original or "").lstrip()[:1].isupper():
        t = t[0].upper() + t[1:]
    return t or out


def _anon_names_apply(text, names, title=False):
    if not text or not names:
        return text
''', "tidy helper")

s = rep(s, '''        out = re.sub(r"(?i)(?<![\\w])" + re.escape(n["text"]) + r"(?![\\w])", "" if title else n["replace"], out)
    out = re.sub(''', '''        out = re.sub(r"(?i)(?<![\\w])" + re.escape(n["text"]) + r"(?![\\w])", "" if title else n["replace"], out)
    _went = (out != text)
    out = re.sub(''', "name went")

s = rep(s, '''    out = re.sub(r"(?im)^[ \\t]+|[ \\t]+$", "", out)
    return out.strip() if out.strip() else text
''', '''    out = re.sub(r"(?im)^[ \\t]+|[ \\t]+$", "", out)
    if title and _went:
        out = _anon_title_tidy(out, text)   # ANON-TITLE-TAIL-1: no dangling "by the", no lower-case start
    return out.strip() if out.strip() else text
''', "tidy call")
compile(s, "bea_main.py", "exec")
save("bea_main.py", s)

g = load("scripts/regression_ledger.py")
if "ANON-TITLE-TAIL-1 (12 Oct 2026)" not in g:
    nums = [int(x) for x in re.findall(r"@entry\(.RG-(\d{4}).", g)]
    rid = "RG-%04d" % (max(nums) + 1)
    ENTRY = '''

@entry("%s", "ANON-TITLE-TAIL-1 (12 Oct 2026): when a name is taken out of an advert's title (ANON-NAMES-1) the title still "
       "reads as a title -- the Bee Lady's five adverts went live as '... \\u2014 by the' when she saved them",
       OPEN, fixed_on="2026-10-12",
       scope="bea_main.py _anon_title_tidy + _anon_names_apply(title=True): the joining words and dash before a removed name "
             "go with it; a title whose first word was the name starts with a capital. Table-tested here on her five titles.",
       ref="Listing versions of #273/#274/#275/#538/#539, 12 Oct 2026 02:29-02:35Z; journal 'ANON-NAMES-1 (edit #538) ... "
           "[Bee Lady]'. The five live titles were tidied by hand the same morning.")
def rg_anon_title_tail_1():
    py = repo_file("bea_main.py")
    if py is None:
        return [(INFO, "NOT EVALUATED - repo not readable from here")]
    import re as _re
    i = py.find("_ANON_TITLE_TAIL_RX = re.compile(")
    j = py.find("\\n_PHOTOS_PREFIX_RX", i)
    if i < 0 or j < 0 or "def _anon_names_apply(" not in py[i:j]:
        return [(FAIL, "a title that loses a name keeps its dangling words again (the tidy is gone)")]
    ns = {"re": _re}
    try:
        exec(py[i:j], ns)
    except Exception as e:
        return [(FAIL, "the title tidy no longer runs on its own: %%r" %% (e,))]
    names = [{"text": "Bee Lady", "replace": "the seller", "kind": "person"}, {"text": "Misty Forest", "replace": "the seller", "kind": "business"}]
    table = [
        ("Beehive Audit & Consulting for farms \\u2014 by the Bee Lady", "Beehive Audit & Consulting for farms"),
        ("Beekeeping course \\u2014 hands-on at the hive, tailored to your group, by the Bee Lady", "Beekeeping course \\u2014 hands-on at the hive, tailored to your group"),
        ("Bee Talks at your venue \\u2014 schools, clubs, lodges & events, by the Bee Lady", "Bee Talks at your venue \\u2014 schools, clubs, lodges & events"),
        ("Bee removals in Pretoria & district \\u2014 certified beekeepers via the Bee Lady", "Bee removals in Pretoria & district \\u2014 certified beekeepers"),
        ("Misty Forest raw honey, propolis & beeswax \\u2014 by the Bee Lady", "Raw honey, propolis & beeswax"),
        ("3 Bed 2 Bath modern unit for sale", "3 Bed 2 Bath modern unit for sale"),
    ]
    out = []
    for before, want in table:
        got = ns["_anon_names_apply"](before, names, title=True)
        if got != want:
            out.append((FAIL, "title %%r became %%r, not %%r" %% (before, got, want)))
    return out or [(INFO, "a title that loses a name still reads as a title (6 of 6)")]
''' % rid
    a = "\n\ndef _server_vantage_wrap():"
    assert g.count(a) == 1, "anchor ledger tail: %d" % g.count(a)
    g = g.replace(a, ENTRY.rstrip("\n") + "\n" + a)
    print("ledger entry", rid)
compile(g, "regression_ledger.py", "exec"); save("scripts/regression_ledger.py", g)
print("ANON-TITLE-TAIL-1 applied: bea_main.py %d -> %d chars" % (n0, len(s)))
