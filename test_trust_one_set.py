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
    # TRUST-BADGE-ONE-RULE-1 (12 Oct 2026): the panel no longer carries an UPDATE of its own -- it asks the one
    # writer, and only for THIS advert's category.
    assert not re.findall(r"UPDATE listings\s+SET\s+trust_score", body), \
        "the panel writes badges itself again -- only _write_listing_badges may"
    assert '_write_listing_badges(conn, email, l["category"])' in body, \
        "the panel's listing heal disappeared, or lost its category scope"

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

# ---- TRUST-BADGE-ONE-RULE-1 (12 Oct 2026): one key rule, one badge writer ----
# The fourth bug in this family. David: "her TS has gone to 90 - it was still 100 last night and even shows 100 on
# the detail but show 90 in the adverts". The Edit screen scored the Bee Lady's Services adverts under Services (90);
# the buyer's panel scored them under Local Market (100, SUPER-CRED-2); each wrote its own number onto the cards.
def test_one_rule_decides_the_set_on_every_surface():
    key = _func_body(SRC, "def _seller_score_key(")
    assert "local_market" in key and "_norm_cat_key(category, service_class)" in key, \
        "the seller rule (any Local Market advert -> Local Market model on all her adverts) left _seller_score_key"
    assert "_seller_score_key(conn, email, category)" in _func_body(SRC, "def trust_score_breakdown("), \
        "the Edit screen's ?category= read ignores the seller rule again"
    assert '_seller_score_key(conn, email, l["category"], l["service_class"])' in _func_body(SRC, "def seller_public_credentials("), \
        "the buyer's panel decides the signal set on its own again"
    assert "_seller_score_key(" in _func_body(SRC, "def _write_listing_badges("), \
        "the badge writer scores an advert without the seller rule"

def test_only_the_one_writer_writes_a_badge():
    ups = re.findall(r"UPDATE listings\s+SET\s+trust_score\s*=\s*\?", SRC)
    assert len(ups) == 1, "%d places write listings.trust_score -- only _write_listing_badges may" % len(ups)
    assert "UPDATE listings SET trust_score" in _func_body(SRC, "def _write_listing_badges("), \
        "the one badge writer no longer writes the badge"
    for fn in ("def seller_public_credentials(", "def trust_score_breakdown(", "def trust_score_set_credential("):
        assert "_write_listing_badges(" in _func_body(SRC, fn), "%s no longer heals the badges" % fn

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
