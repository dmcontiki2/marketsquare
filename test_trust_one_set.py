#!/usr/bin/env python3
# test_trust_one_set.py - the ONE-EVIDENCE-SET guard (15 Sep 2026, David: "lets fix
# the scores to be consistent").
#
# The third bug in this family, and the first the other two guards could not see:
#   * test_trust_evidence_true.py checks a headline against its OWN list  -> both were
#     right together, so it passed.
#   * test_trust_base40.py checks the ARITHMETIC canon                     -> the panel
#     used the shared formula correctly, so it passed too.
# What differed was the EVIDENCE SET. The buyer-facing panel hand-rolled its own
# universal/track SQL, counted less than the scorer, and then wrote its answer over the
# stored score and over every listing - so David saw 80 on the dashboard, 57 on the
# seller profile, and a number that moved depending on which screen he opened last.
#
# This guard protects the cure: one builder, and write authority narrowed to what each
# surface actually knows.
#
# Runs with pytest OR plain `python test_trust_one_set.py [project_dir]`.
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

SRC = _read("bea_main.py")

# ---- there is exactly one evidence builder, and it is shared -----------------
def test_one_builder_exists():
    assert "def _trust_evidence(" in SRC, "the shared evidence builder is missing"
    body = _func_body(SRC, "def _trust_evidence(")
    for fn in ("_build_breakdown_items(", "_sum_earned_with_replaces(", "_trust_math("):
        assert fn in body, "the shared builder must use %s" % fn

def test_nobody_else_builds_evidence():
    """_build_breakdown_items is the raw evidence reader — only the shared builder
    may call it. Any other caller is a second opinion about the same seller."""
    callers = []
    for m in re.finditer(r"\n(?:@app\.[^\n]*\n)?def (\w+)\(", SRC):
        name = m.group(1)
        if name in ("_build_breakdown_items", "_trust_evidence"):
            continue
        body = _func_body(SRC, "def %s(" % name)
        if "_build_breakdown_items(" in body:
            callers.append(name)
    assert not callers, ("these build their own evidence set instead of asking "
                         "_trust_evidence: %s" % callers)

# ---- the two surfaces David compared must read the same set -----------------
def test_both_surfaces_use_the_builder():
    for fn in ("trust_score_breakdown", "seller_public_credentials"):
        body = _func_body(SRC, "def %s(" % fn)
        assert "_trust_evidence(" in body, "%s must read the shared evidence set" % fn

def test_panel_has_no_private_evidence_sql():
    """The panel may read what it needs for NOTES (intro counts, mandate documents,
    agency peers) but must not re-derive scoring evidence from user_credentials or
    user_declarations — that is how it came to count a different set."""
    body = _func_body(SRC, "def seller_public_credentials(")
    for table in ("user_credentials", "user_declarations"):
        assert table not in body, \
            "the panel re-reads %s — evidence must come from _trust_evidence" % table

def test_panel_list_and_total_are_built_together():
    body = _func_body(SRC, "def seller_public_credentials(")
    assert "_earned_display(" in body, \
        "the panel's visible list and its subtotal must be produced in one pass"

# ---- the visible list must still sum to the headline after the caps ---------
def test_panel_subtotals_are_capped_like_the_formula():
    """CAP-VISIBLE-1. Universal caps at 40 (RUL-142, via _UNI_CAP) and Track Record at 30 in the formula. The
    moment the panel started counting the FULL set, an uncapped group subtotal made the
    list sum to 87 over an 80 headline — the same class of bug, arriving from the other
    direction. Each group shows its capped subtotal; the formula gets the raw sums."""
    body = _func_body(SRC, "def seller_public_credentials(")
    assert re.search(r"_uni_sub\s*=\s*min\(_UNI_CAP,\s*_uni_raw\)", body), \
        "the identity group must show its CAPPED subtotal or the list sums above the headline"
    assert re.search(r"_trk_sub\s*=\s*min\(30,\s*_trk_raw\)", body), \
        "the track-record group must show its CAPPED subtotal"
    assert re.search(r"_trust_math\(_uni_raw,\s*_trk_raw,", body), \
        "the formula must receive the RAW sums — the capping is its job, not the panel's"


# ---- write authority: a surface may not answer a question it was not asked ---
def test_panel_listing_writes_are_category_scoped():
    body = _func_body(SRC, "def seller_public_credentials(")
    ups = re.findall(r"UPDATE listings SET trust_score[^\"']*", body)
    assert ups, "the panel's listing heal disappeared"
    for u in ups:
        assert "AND category" in u, \
            "the panel wrote a per-listing score to EVERY listing: %r" % u

def test_panel_user_write_requires_primary_category():
    body = _func_body(SRC, "def seller_public_credentials(")
    m = re.search(r"if\s+cat_key\s*==\s*_category_key_for_user\(conn,\s*email\)[^\n]*\n\s*#[^\n]*\n\s*#[^\n]*\n\s*conn\.execute\(\"UPDATE users SET trust_score"
                  r"|if\s+cat_key\s*==\s*_category_key_for_user\(conn,\s*email\)[^\n]*\n(?:\s*#[^\n]*\n)*\s*conn\.execute\(\"UPDATE users SET trust_score", body)
    assert m, ("users.trust_score must only be healed when this advert's category IS "
               "the seller's primary one — otherwise a secondary listing overwrites the badge")

def test_scorer_still_only_persists_on_primary():
    body = _func_body(SRC, "def trust_score_breakdown(")
    assert re.search(r"if not category and prior_score != score_total", body), \
        "the scorer lost the rule that a ?category= override never writes users.trust_score"

if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(list(globals().items())):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print("PASS  " + name)
            except AssertionError as e:
                fails += 1; print("FAIL  %s - %s" % (name, e))
    print("\nALL ONE-SET CHECKS PASS" if not fails else "\n%d ONE-SET CHECK(S) FAILED" % fails)
    sys.exit(1 if fails else 0)
