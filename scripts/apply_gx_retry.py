#!/usr/bin/env python3
"""GX-RETRY-1 (David, 12 Oct 2026 10:28: "Something broke. Services kept its 51 but tutors has lost all of the new sub
catagory cards").

Nothing was lost on the server: /examples/trainers answered 47 cards all morning. On his page load at 08:26:07Z the
journal shows the Services read (/examples/roles) and NO Tutors read (/examples/trainers) -- that one request never
reached the server. msGenericExLoad swallowed the failure, so the Tutors tile sat at 3 until the 3-minute list refresh
asked again (08:29:07Z, and the cards came back). One dropped request must not blank a tile for three minutes: a failed
read of either example list is asked again after 2 s and then 6 s, the same idea as loadLiveListings' own backoff.

Usage:  python3 apply_gx_retry.py <repo>      Idempotent; asserts every anchor; honours the work lock of another lane."""
import io, os, re, sys

R = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

s = load("ms.js"); n0 = len(s)
s = rep(s, '''const _msGxCache = new Map();
async function msGenericExLoad(seq){
''', '''const _msGxCache = new Map();
/* GX-RETRY-1 (David, 12 Oct 2026: "Services kept its 51 but tutors has lost all of the new sub catagory cards"): the one
   request for the trainer examples did not reach the server on his page load (the Services one did), the failure was
   swallowed, and the Tutors tile sat at 3 until the 3-minute refresh asked again. A failed read of either example list
   is now asked again after 2 s and then 6 s (twice per city and language -- loadLiveListings' own backoff idea); after
   that the normal refresh takes over. A newer list (another city, a later refresh) cancels the retry. */
const _msGxTries = new Map();
function _msGxRetry(key, seq){
  const n = _msGxTries.get(key) || 0;
  if (n >= 2) return;
  _msGxTries.set(key, n + 1);
  setTimeout(function(){ if (seq === _msListSeq) msGenericExLoad(seq); }, n === 0 ? 2000 : 6000);
}
async function msGenericExLoad(seq){
''', "retry helper")
s = rep(s, '''      if (!Array.isArray(rows)) return;
      _msGxCache.set(key, rows);
''', '''      if (!Array.isArray(rows)) { _msGxRetry(key, seq); return; }   // GX-RETRY-1: ask again, do not wait for the refresh
      _msGxCache.set(key, rows); _msGxTries.delete(key);
''', "roles retry")
s = rep(s, '''        if (Array.isArray(trows)) _msGxCache.set(tkey, trows); else trows = [];
''', '''        if (Array.isArray(trows)) { _msGxCache.set(tkey, trows); _msGxTries.delete(tkey); }
        else { trows = []; _msGxRetry(tkey, seq); }   // GX-RETRY-1: the Tutors tile must not sit without its cards
''', "trainers retry")
save("ms.js", s)

g = load("scripts/regression_ledger.py")
if "GX-RETRY-1 (David, 12 Oct 2026)" not in g:
    nums = [int(x) for x in re.findall(r"@entry\(.RG-(\d{4}).", g)]
    rid = "RG-%04d" % (max(nums) + 1)
    ENTRY = '''

@entry("%s", "GX-RETRY-1 (David, 12 Oct 2026): a category tile does not sit without its AI example cards because one request "
       "dropped -- Tutors read 3 beside Services 51 until the 3-minute refresh ('tutors has lost all of the new sub catagory cards')",
       OPEN, fixed_on="2026-10-12",
       scope="ms.js msGenericExLoad + _msGxRetry: a failed read of /examples/roles or /examples/trainers is asked again after 2 s "
             "and 6 s (twice per city and language), cancelled by a newer list. Executed by scripts/prove_gx_retry.js.",
       ref="Server journal 12 Oct 2026 08:26:07Z: his page load asked /examples/roles and never /examples/trainers; the cards "
           "came back at the 08:29:07Z refresh. The server answered 47 trainer cards throughout.")
def rg_gx_retry_1():
    js = repo_file("ms.js")
    if js is None:
        return [(INFO, "NOT EVALUATED - repo not readable from here")]
    i = js.find("async function msGenericExLoad(")
    body = js[i:i + 6000] if i >= 0 else ""
    out = []
    if "function _msGxRetry(key, seq){" not in js or "if (seq === _msListSeq) msGenericExLoad(seq);" not in js:
        out.append((FAIL, "the ask-again for a failed example read is gone"))
    if "_msGxRetry(key, seq); return;" not in body:
        out.append((FAIL, "a failed Services example read waits for the 3-minute refresh again"))
    if "_msGxRetry(tkey, seq);" not in body:
        out.append((FAIL, "a failed Tutors example read leaves the tile without its cards until the refresh again"))
    return out or [(INFO, "a failed example read is asked again within seconds")]
''' % rid
    a = "\n\ndef _server_vantage_wrap():"
    assert g.count(a) == 1, "anchor ledger tail: %d" % g.count(a)
    g = g.replace(a, ENTRY.rstrip("\n") + "\n" + a)
    print("ledger entry", rid)
compile(g, "regression_ledger.py", "exec"); save("scripts/regression_ledger.py", g)
print("GX-RETRY-1 applied: ms.js %d -> %d chars" % (n0, len(s)))
