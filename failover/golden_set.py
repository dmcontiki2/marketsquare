"""
failover/golden_set.py - the 16 TrustSquare Cloud AI calls, each with its tier
and an output schema template.

The schema doubles as (a) the contract the eval checks any backend against and
(b) the deterministic $0 dry-run payload. Replace the placeholder fixtures with
real anonymised inputs in Phase 1 when you tune prompts per backend.
"""
from failover.ai_backends import FAST, FAST_VISION, REASON, REASON_VISION

GOLDEN = [
    {"name": "aa_market_note",             "tier": FAST,          "schema": {"note": "<market note>"}},
    {"name": "aa_coach",                   "tier": FAST,          "schema": {"advice": "<coaching>"}},
    {"name": "ai_listing_rewrite",         "tier": FAST,          "schema": {"title": "<t>", "description": "<d>"}},
    {"name": "ai_seller_audit",            "tier": FAST,          "schema": {"issues": [], "score": 0}},
    {"name": "ai_yield_calc",              "tier": FAST,          "schema": {"explanation": "<why>"}},
    {"name": "trust_score_guidance",       "tier": FAST,          "schema": {"steps": []}},
    {"name": "trust_score_upload_comment", "tier": FAST,          "schema": {"comment": "<c>"}},
    {"name": "_classify_email",            "tier": FAST,          "schema": {"category": "<cat>", "priority": "<p>"}},
    {"name": "_vision_orient_image",       "tier": FAST_VISION,   "schema": {"rotation_degrees": 0}},
    {"name": "listing_draft_from_photo",   "tier": FAST_VISION,   "schema": {"title": "<t>", "description": "<d>", "category": "<c>"}},
    {"name": "listing_draft_from_photos",  "tier": FAST_VISION,   "schema": {"title": "<t>", "description": "<d>", "category": "<c>"}},
    {"name": "ai_price_check",             "tier": REASON,        "schema": {"fair": True, "estimate": 0, "rationale": "<r>"}},
    {"name": "_sonnet_verify_identity",    "tier": REASON_VISION, "schema": {"match": True, "extracted_id": "<id>", "notes": "<n>"}},
    {"name": "vision_draft",               "tier": REASON_VISION, "schema": {"title": "<t>", "description": "<d>", "attributes": []}},
    {"name": "ai_batch_card_listings",     "tier": REASON_VISION, "schema": {"cards": []}},
    {"name": "grade_card_condition",       "tier": REASON_VISION, "schema": {"grade": "<g>", "rationale": "<r>"}},
]
