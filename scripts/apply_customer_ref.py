#!/usr/bin/env python3
"""CUSTOMER-REF-1 (David 25 Sep 2026, on a Local Market Plants draft: the referral "should rather say 'a customer'
than 'someone you worked for'"). Local Market sellers are vouched for by A CUSTOMER; cars keep
"Someone who has bought from you". Idempotent; asserts every anchor. Then run sync_quick_roles.py and copy
quick.html over genie/HARNESS.html (the two are kept identical)."""
import io, os, json
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p): return io.open(os.path.join(R, p), encoding="utf-8").read()
def wr(p, s):
    io.open(os.path.join(R, p), "w", encoding="utf-8").write(s); assert rd(p) == s, p
q = rd("quick.html")
A = "  if(k==='localmarket' || k==='cars') return {subj:'Someone who has bought from you', demo:'You have bought from them'};   /* GOODS-FIT-1 */"
B = ("  if(k==='localmarket') return {subj:'A customer', demo:'You have bought from them'};   /* CUSTOMER-REF-1 */\n"
     "  if(k==='cars') return {subj:'Someone who has bought from you', demo:'You have bought from them'};   /* GOODS-FIT-1 */")
if B not in q:
    assert q.count(A) == 1, "vouchWho anchor %d" % q.count(A); q = q.replace(A, B)
wr("quick.html", q)
f = "roles/quick_i18n.json"; d = json.loads(rd(f))
d["w"].setdefault("A customer says", ["'n Klant sê", "Ikhasimende lithi", "Moreki o re", "Umthengi uthi", "Moreki o re"])  # af, zu, st, xh, nso
wr(f, json.dumps(d, ensure_ascii=False, indent=1))
print("CUSTOMER-REF-1 applied")
