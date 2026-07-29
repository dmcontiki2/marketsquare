#!/usr/bin/env python3
# test_trust_base40.py - the BASE-40 canon guard (28 Jul 2026, David's ruling:
# "Please fix it to be right... We can check the checkers if they detect it").
#
# Today's bug class: a trust surface that re-implements the score arithmetic
# and drops the universal 40-point base (SUPER-CRED-1 panel, 20 Jul), then
# gains write authority (JNR-FIX-2 self-heal, 24 Jul) and rewrites stored
# scores to the base-less total (a viewed seller dropped 40 -> 5).
# test_trust_evidence_true.py could NOT catch it: the panel's list summed to
# its headline - both were wrong together. THIS guard checks the arithmetic
# canon itself, in every place it is written down.
#
# Runs with pytest OR plain `python test_trust_base40.py [project_dir]`.
import os, re, sys

HERE = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))

def _read(name):
    with open(os.path.join(HERE, name), encoding="utf-8", errors="replace") as f:
        return f.read()

def _func_body(src, header):
    i = src.index(header)
    rest = src[i + len(header):]
    m = re.search(r"\n(?=@app\.|def )", rest)
    return rest[:m.start()] if m else rest

# ---- the canon formula, as published (agency email: "40 + 45 = 85") ---------
def canon_score(uni, track, cat, penalties, lm=False):
    c = cat if lm else min(40, cat)
    return max(0, min(100, 40 + min(30, uni) + min(30, track) + c) + penalties)

def test_published_examples_hold():
    # The agency outreach email promises: base 40 + 45 credentials = 85.
    assert canon_score(20, 30, 0, -5) == 85, "the email's 40+45=85 example must hold"
    # A profile-only seller: 40 base + 5 = 45 (the '40 -> 5' bug seller, repaired).
    assert canon_score(5, 0, 0, 0) == 45
    # Floor and cap.
    assert canon_score(0, 0, 0, -60) == 0
    assert canon_score(30, 30, 40, 0) == 100
    # LM (Addendum 2026-07-21 §2): credential group UNCAPPED, total caps at 100.
    # Bee Lady (id 273): full-catalog evidence must reach 100, not the capped 85.
    assert canon_score(5, 0, 60, 0, lm=True) == 100   # 40+5+60=105 -> caps at 100
    assert canon_score(5, 0, 60, 0, lm=False) == 85   # standard 40-cap bites: 40+5+40
    assert canon_score(20, 20, 140, -8, lm=True) == 92  # penalties visible past surplus

# ---- the scorer must carry the base ----------------------------------------
def test_scorer_has_base40():
    src = _read("bea_main.py")
    assert "def _trust_math(" in src, "the single shared trust formula is missing"
    hb = _func_body(src, "def _trust_math(")
    assert re.search(r"cat_pts if lm else min\(40,\s*cat_pts\)", hb), \
        "LM credential group must be uncapped in the shared formula (Addendum 2026-07-21)"
    assert re.search(r"max\(0,\s*min\(100,\s*40\s*\+", hb), "formula lost base-40/cap/penalty order"
    body = _func_body(src, "def trust_score_breakdown(")
    assert "_trust_math(" in body, "scorer must compute via the shared formula"
    assert re.search(r"if _is_lm_score else min\(40", body), "scorer lost the LM-uncapped rule"

# ---- the buyer-facing seller panel must carry the base (today's bug) --------
def test_seller_panel_has_base40():
    src = _read("bea_main.py")
    body = _func_body(src, "def seller_public_credentials(")
    assert '"title": "Foundation"' in body and '"points": 40' in body, \
        "seller_public_credentials lost the universal Foundation-40 group " \
        "(the 40->5 bug: its self-heal then rewrites stored scores base-less)"
    assert "Local Market foundation" in body, "LM foundation-40 group missing"
    assert "_trust_math(" in body, \
        "seller panel must compute via the shared formula (no local arithmetic)"

# ---- any surface that self-heals stored scores must prove the base first ----
def test_selfheal_only_with_base():
    src = _read("bea_main.py")
    body = _func_body(src, "def seller_public_credentials(")
    heal = body.find("UPDATE users SET trust_score")
    base = body.find('"title": "Foundation"')
    assert heal == -1 or (base != -1 and base < heal), \
        "a base-less total must never gain write authority over stored scores"
    # LISTINGS-SYNC (28 Jul): the listings heal must run unconditionally — gating it
    # on the users-differ check strands browse cards at a stale score forever.
    ls = body.find("UPDATE listings SET trust_score")
    assert ls != -1 and "AND trust_score != ?" in body, \
        "listings self-heal must be unconditional (guarded only by value-changed)"

# ---- the sell-flow preview (ms.js) must agree ------------------------------
def test_sellflow_preview_has_base40():
    js = _read("ms.js")
    i = js.index("function sbCalcScore()")
    body = js[i:i+400]
    assert re.search(r"pts\s*=\s*40", body), "sell-flow preview lost the 40-point base"

if __name__ == "__main__":
    failed = 0
    for name, fn in sorted({k: v for k, v in list(globals().items())
                            if k.startswith("test_") and callable(v)}.items()):
        try:
            fn()
            print("PASS  " + name)
        except AssertionError as e:
            failed += 1
            print("FAIL  " + name + " - " + str(e))
        except Exception as e:
            failed += 1
            print("FAIL  " + name + " - error: %r" % e)
    sys.exit(1 if failed else 0)
