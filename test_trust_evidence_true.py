#!/usr/bin/env python3
# test_trust_evidence_true.py - the reliability flow that stops a Trust Score
# headline from ever again diverging from the evidence shown beside it (the
# 87-over-50 class of bug: JNR-FIX-2, 24 Jul; this guard, 25 Jul).
#
# Runs with pytest OR plain `python test_trust_evidence_true.py [project_dir]`,
# so predeploy_check / CI can call it with no app or DB running. It checks the
# SOURCE, so it catches a regression the moment someone reverts a fix or adds a
# new trust surface that reads a stored score instead of summing the evidence.
import os, re, sys

HERE = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))

def _read(name):
    with open(os.path.join(HERE, name), encoding="utf-8", errors="replace") as f:
        return f.read()

def _func_body(src, header):
    """Return the text of a python function from its 'def name' to the next
    top-level 'def '/'@app' at column 0."""
    i = src.index(header)
    rest = src[i + len(header):]
    m = re.search(r"\n(?=@app\.|def )", rest)
    return rest[:m.start()] if m else rest

# ---- the pure invariant (concept sanity) -------------------------------------
def evidence_true(claimed, parts):
    true_sum = int(sum(int(p) for p in parts))
    return true_sum, (claimed is None or int(claimed) == true_sum)

def test_invariant_math():
    total, ok = evidence_true(87, [15, 5, 5, 5, 5, 10, 5])      # =50, claim 87
    assert total == 50 and not ok, "must flag 87-over-50"
    total, ok = evidence_true(50, [15, 5, 5, 5, 5, 10, 5])
    assert total == 50 and ok, "50 over a 50 list must pass"

# ---- backend: get_user_trust must SUM its evidence, not return the stored score
def test_get_user_trust_is_evidence_true():
    src = _read("bea_main.py")
    assert "def _assert_evidence_true(" in src, "evidence-true guard helper missing"
    body = _func_body(src, "def get_user_trust(email: str):")
    # the returned score must pass through the guard...
    assert "_assert_evidence_true(" in body, \
        "get_user_trust must derive its headline via _assert_evidence_true"
    # ...and the guard call must sit BEFORE the response is built
    assert body.index("_assert_evidence_true(") < body.index("return {"), \
        "guard must run before the score is returned"

# ---- frontend: the live-seller hero must be reconcilable to computed_total ----
def test_frontend_header_is_reconcilable():
    js = _read("ms.js")
    # the credentials callback must reconcile the profile HERO to computed_total.
    # The hero paints .cv-trust-* by class, so the sync must target it by class
    # inside #screen-seller-cv (the id-based sync only reaches the detail view).
    assert "getElementById('screen-seller-cv')" in js, \
        "no seller-profile hero reconciliation -> header can drift from evidence"
    assert "querySelector('.cv-trust-num')" in js, \
        "hero score (.cv-trust-num) is never synced to the computed evidence total"

def test_trust_catalog_excludes_listing_quality():
    """Fraud firewall (TRUST_SCORE_CRITERIA Amendment v1.4): listing quality / SPS must
    never score trust points - a flawless advert for a fake product must not buy a trust
    halo. The _TRUST_SIGNALS catalog (Universal + Track Record) must hold no quality/SPS
    signal. (Category *credential* certs are a separate, legitimate thing.)"""
    src = _read("bea_main.py")
    i = src.index("_TRUST_SIGNALS = {")
    j = src.index("_CATEGORY_SIGNALS = {", i)
    catalog = src[i:j].lower()
    for token in ("quality", "avg_listing_quality", "listing_quality"):
        assert token not in catalog, \
            "listing-quality/SPS token %r in the trust catalog -> trust and quality merged" % token

if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print("PASS", name)
            except AssertionError as e:
                fails += 1; print("FAIL", name, "->", e)
    print("\n%s" % ("ALL EVIDENCE-TRUE CHECKS PASS" if not fails else "%d CHECK(S) FAILED" % fails))
    sys.exit(1 if fails else 0)
