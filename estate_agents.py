"""
TrustSquare — Professional Agents as a Service (AGENT-SVC-1 + AGENT-SVC-2, 19 Jul 2026)
=======================================================================================
VERTICALS: "property" (estate agents — PPRA/FFC/NQF), "cars" (car sales
agents/dealers a la WeBuyCars — MIRA, inspection) and "travel" (tour agents —
ASATA/IATA/CIPC/bonding; leads come from holiday SEARCHERS, not sellers).
Same single process for both: template → profile → pending credentials →
verified gate → ranked anonymous list → seller-side reverse INTRO at 1T.
Agents are listed as a SERVICE, not just as sellers of stock. This module:

  1. Canonical agent listing TEMPLATE — profile fields + credential slots that
     map 1:1 onto the existing Property trust-signal catalog (PPRA 15 · FFC 10 ·
     mandate 8 · NQF4 6 · NQF5 +6 · NQF6+ +8 · body 5), so an agent's trust
     score is computed by the SAME verified-evidence pipeline as everyone else.
  2. Anonymised agent profile (anon_ref like "Agent TS-4F2A9C") — years
     experience, properties sold (banded), areas served, verified cert badges.
     No name, no agency brand, no contact — anonymity-first, like listings.
  3. Bulk agency onboarding — agency uploads agents WITH credential claims;
     claims land as PENDING user_credentials (never auto-earned), so the trust
     score is correct by construction: it only moves when ops verifies via the
     existing /trust-score/credential flow.
  4. Local ranked agent list for private sellers — rank = 50% listing quality
     (avg of the same 100-pt server quality score used by the import gate,
     across the agent's live listings) + 50% trust score. David's rule:
     listing quality carries at least half the weight.
  5. Reverse INTRO at 1T — the private seller picks an agent; the agent sees
     the seller's trust score + property summary (seller stays anonymous),
     and accepts at 1 Tuppence (the lead fee — no cold calls, no third-party
     lead sellers) or declines free. Contact revealed on accept only.

Seams injected by bea_main via configure() — this module never imports
bea_main (no circular import; standalone-testable):
    anon_fn(text)      -> (clean_text, hit_labels)   [_anon_regex_clean]
    quality_fn(row)    -> (score_0_100, missing[])   [_import_quality_score]
Fallbacks keep the module functional if configure() is never called.
"""

import re
import uuid
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

import auth
import database

router = APIRouter()

# ── Injected seams (bea_main.configure) ──────────────────────────────────────
_ANON_FN = None       # text -> (clean, hits)
_QUALITY_FN = None    # listings row/dict -> (score, missing)
_INVITE_FN = None     # email, agency_name -> 'sent'|'failed'|'dry'  (AGENCY-INVITE-MAIL-1)

def configure(anon_fn=None, quality_fn=None, invite_fn=None):
    global _ANON_FN, _QUALITY_FN, _INVITE_FN
    if anon_fn:
        _ANON_FN = anon_fn
    if quality_fn:
        _QUALITY_FN = quality_fn
    if invite_fn:
        _INVITE_FN = invite_fn

_FALLBACK_STRIP = [
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"(?:https?://|www\.)[^\s,;)]+", re.I),
    re.compile(r"(?:\+|00)\d[\d\s().-]{7,}\d"),
    re.compile(r"\b0\d{2}[\s.-]?\d{3}[\s.-]?\d{4}\b"),
]

def _anon(text: str):
    if _ANON_FN:
        return _ANON_FN(text)
    out = str(text or "")
    hits = []
    for pat in _FALLBACK_STRIP:
        out, n = pat.subn(" ", out)
        if n:
            hits.append("stripped")
    return re.sub(r"[ \t]{2,}", " ", out).strip(), sorted(set(hits))

def _quality(row):
    if _QUALITY_FN:
        return _QUALITY_FN(row)
    return 0, ["quality scorer not configured"]

def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ── Schema (idempotent; mirrors bea_main migration style) ────────────────────

def init_schema(conn=None):
    own = conn is None
    if own:
        conn = database.get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS agent_profiles (
        agent_email      TEXT PRIMARY KEY,
        anon_ref         TEXT NOT NULL,
        agency_id        INTEGER,
        headline         TEXT,
        bio_anon         TEXT,
        years_experience INTEGER,
        properties_sold  INTEGER,
        sold_source      TEXT NOT NULL DEFAULT 'declared',
        city             TEXT,
        suburbs          TEXT,
        specialties      TEXT,
        languages        TEXT,
        profile_status   TEXT NOT NULL DEFAULT 'draft',
        vertical         TEXT NOT NULL DEFAULT 'property',
        created_at       TEXT NOT NULL,
        updated_at       TEXT NOT NULL
    )""")
    # AGENT-SVC-2 migration: vertical column on pre-existing tables
    _cols = [r[1] for r in conn.execute("PRAGMA table_info(agent_profiles)").fetchall()]
    if "vertical" not in _cols:
        conn.execute("ALTER TABLE agent_profiles ADD COLUMN vertical TEXT NOT NULL DEFAULT 'property'")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_agent_profiles_ref ON agent_profiles(anon_ref)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_profiles_city ON agent_profiles(city, profile_status)")
    conn.execute("""CREATE TABLE IF NOT EXISTS agent_intros (
        id                    INTEGER PRIMARY KEY AUTOINCREMENT,
        seller_email          TEXT NOT NULL,
        agent_email           TEXT NOT NULL,
        listing_id            INTEGER,
        message               TEXT,
        seller_trust_snapshot INTEGER NOT NULL DEFAULT 0,
        listing_quality_snapshot INTEGER NOT NULL DEFAULT 0,
        status                TEXT NOT NULL DEFAULT 'pending',
        tuppence_charged      INTEGER NOT NULL DEFAULT 0,
        created_at            TEXT NOT NULL,
        responded_at          TEXT
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_intros_agent ON agent_intros(agent_email, status)")
    conn.commit()
    if own:
        conn.close()

# ── The template (the canonical agent listing definition) ────────────────────

CREDENTIAL_SLOTS_PROPERTY = [
    {"slot": "ppra_number",  "signal_id": "category.property.ppra",      "points": 15,
     "label": "PPRA / EAAB registration", "legal": True,
     "verify": "Checked against the PPRA register (ppra.org.za). Mandatory for professional agents in SA."},
    {"slot": "ffc_year",     "signal_id": "category.property.ffc",       "points": 10,
     "label": "Fidelity Fund Certificate (FFC)", "legal": True,
     "verify": "Current-year FFC. Lapses annually — an agent may not legally trade without it. Profile cannot go live until verified."},
    {"slot": "nqf_level",    "signal_id": None,                          "points": None,
     "label": "NQF Real Estate qualification (4 / 5 / 6+)", "legal": False,
     "verify": "Certificate upload. NQF5 implies NQF4; NQF6+ implies both (points stack: 6 / +6 / +8)."},
    {"slot": "body_memberships", "signal_id": "category.property.body",  "points": 5,
     "label": "Professional body (IEASA, SAPOA, NAR)", "legal": False,
     "verify": "Membership card or letter."},
]

CREDENTIAL_SLOTS_CARS = [
    {"slot": "mira_number", "signal_id": "category.cars.dealer_reg", "points": 8,
     "label": "MIRA dealer / trader registration", "legal": True,
     "verify": "Upload MIRA dealer licence (SA) or equivalent trade registration. The professional minimum to trade — gates go-live. Shows 'Registered Dealer' to buyers."},
    {"slot": "inspection_partner", "signal_id": "category.cars.inspection", "points": 5,
     "label": "Independent inspection partner", "legal": False,
     "verify": "Evidence of a standing third-party inspection arrangement (AA South Africa, DEKRA etc.) — every car you broker can carry an independent report."},
]

CREDENTIAL_SLOTS_TRAVEL = [
    {"slot": "asata_number", "signal_id": "category.travel.asata_member", "points": 10,
     "label": "ASATA membership", "legal": True,
     "verify": "ASATA membership number — verified against the public member register. The professional minimum to trade — gates go-live."},
    {"slot": "iata_code", "signal_id": "category.travel.iata_accredited", "points": 10,
     "label": "IATA accreditation", "legal": False,
     "verify": "IATA agency code — verified via IATA CheckACode where available. Required for issuing flight tickets."},
    {"slot": "cipc_number", "signal_id": "category.travel.cipc_registered", "points": 6,
     "label": "Registered company (CIPC)", "legal": True,
     "verify": "CIPC registration number — must at least be submitted before go-live."},
    {"slot": "bonding_proof", "signal_id": "category.travel.financial_bonding", "points": 5,
     "label": "Financial bonding / client payment guarantee", "legal": False,
     "verify": "Proof of a bonding or guarantee scheme protecting client payments — the strongest anti-scam signal for travellers."},
]

# ── VERT-4-1 (RUL-049, 24 Aug 2026): the four recruited verticals, gates registry-
# verified 23 Aug (SKIN_DESIGNS — nice.docx carries sources + David's ratification). ──
CREDENTIAL_SLOTS_COLLECTOR = [
    {"slot": "shg_registration", "signal_id": "category.collector.shg_registered", "points": 12,
     "label": "SAPS Second-Hand Goods dealer registration", "legal": True,
     "verify": "Checked against the SAPS second-hand goods dealer register (Act 6 of 2009). Statutory to trade — gates go-live."},
    {"slot": "cipc_number", "signal_id": "category.collector.cipc_registered", "points": 5,
     "label": "Registered company (CIPC)", "legal": True,
     "verify": "CIPC registration number — must at least be submitted before go-live."},
    {"slot": "assoc_memberships", "signal_id": "category.collector.assoc_member", "points": 5,
     "label": "Dealer association (SAADA / SAAND / NAADA)", "legal": False,
     "verify": "Membership letter or card — verified against the association's member list."},
    {"slot": "grading_partner", "signal_id": "category.collector.grading", "points": 4,
     "label": "Grading partner (SANGS / NGC / PCGS)", "legal": False,
     "verify": "Evidence of a standing grading/authentication arrangement."},
]

CREDENTIAL_SLOTS_INSTITUTION = [
    {"slot": "clearance_refs", "signal_id": "category.institution.clearances", "points": 10,
     "label": "Safety clearances (SAPS PCC + Child Protection Register + Sexual Offenders Register)", "legal": True,
     "verify": "REFERENCE NUMBERS ONLY — ops sight-verifies against the issuing bodies; clearance documents are never stored (POPIA). The child-safety minimum — gates go-live. A verified SACE registration covers all three."},
    {"slot": "sace_number", "signal_id": "category.institution.sace", "points": 12,
     "label": "SACE registration", "legal": True,
     "verify": "Verified against the SACE register. SACE registration embeds police clearance + both register screenings — verifying it also earns the clearances gate."},
    {"slot": "saqa_ref", "signal_id": "category.institution.saqa", "points": 6,
     "label": "SAQA-verified qualification", "legal": False,
     "verify": "SAQA verification reference for the tutor's qualification."},
]

CREDENTIAL_SLOTS_SERVICE = [
    {"slot": "trade_licence", "signal_id": "category.service.trade_licence", "points": 12,
     "label": "Trade licence (PIRB / DoEL Installation Electrician / class-statutory)", "legal": True,
     "verify": "The CoC-issuing licence for the technician's trade — PIRB for plumbing, DoEL IE/Wireman's for electrical. Gates go-live for regulated trades; unregulated trades are flagged to ops for the CIPC+insurance fallback."},
    {"slot": "cipc_number", "signal_id": "category.service.cipc_registered", "points": 5,
     "label": "Registered company (CIPC)", "legal": True,
     "verify": "CIPC registration number — must at least be submitted before go-live."},
    {"slot": "insurance_ref", "signal_id": "category.service.insured", "points": 6,
     "label": "Public liability insurance", "legal": False,
     "verify": "Policy schedule or broker letter."},
    {"slot": "cidb_grade", "signal_id": "category.service.cidb", "points": 4,
     "label": "CIDB grading (construction)", "legal": False,
     "verify": "CIDB registration number and grade."},
]

CREDENTIAL_SLOTS_PLACEMENT = [
    {"slot": "del_pea_number", "signal_id": "category.placement.del_registered", "points": 12,
     "label": "DEL private employment agency registration", "legal": True,
     "verify": "Verified against the Department of Employment and Labour register (Employment Services Act 4 of 2014). Statutory — and the Act prohibits charging workseekers, which is exactly the TrustSquare model. Gates go-live."},
    {"slot": "cipc_number", "signal_id": "category.placement.cipc_registered", "points": 5,
     "label": "Registered company (CIPC)", "legal": True,
     "verify": "CIPC registration number — must at least be submitted before go-live."},
    {"slot": "apso_member", "signal_id": "category.placement.apso", "points": 5,
     "label": "APSO membership", "legal": False,
     "verify": "APSO membership — verified against the member directory."},
    {"slot": "sponsor_network", "signal_id": "category.placement.sponsors", "points": 5,
     "label": "Sponsor network (IAPA / J-1 sponsors / cruise lines)", "legal": False,
     "verify": "Evidence of standing sponsor/partner relationships (IAPA membership, J-1 sponsor agreements, cruise-line contracts)."},
]

_NQF_CHAIN = {
    4: ["category.property.nqf4"],
    5: ["category.property.nqf4", "category.property.nqf5"],
    6: ["category.property.nqf4", "category.property.nqf5", "category.property.nqf6_plus"],
}

EXPERIENCE_BANDS = [(0, 2, "Under 2 years"), (2, 5, "2-5 years"), (5, 10, "5-10 years"), (10, 999, "10+ years")]
SOLD_BANDS = [(0, 10, "Fewer than 10"), (10, 50, "10-49 properties sold"), (50, 200, "50-199 properties sold"), (200, 10**9, "200+ properties sold")]

def _band(value, bands):
    v = int(value or 0)
    for lo, hi, label in bands:
        if lo <= v < hi:
            return label
    return bands[0][2]

AGENT_ADVANTAGES_PROPERTY = [
    "Correct market pricing — agents price against live comparable sales, not hope.",
    "Legal compliance handled — mandatory disclosure forms, FICA, compliance certificates (electrical, gas, electric fence), offer-to-purchase drafting.",
    "Qualified buyers only — agents pre-qualify bond affordability before viewings.",
    "Negotiation and closing — an experienced agent typically recovers their commission in the final price.",
    "Your time back — viewings, phone calls and paperwork handled for you.",
]

LEGAL_NOTE_PROPERTY = ("Selling property carries legal obligations you keep even as a private seller: "
              "mandatory property condition disclosure, FICA verification, compliance certificates "
              "and a legally sound offer to purchase. See the legal must-haves card for your country "
              "in the sell flow (Step 6) — an agent manages what they may, and facilitates the rest.")

# ── Buyer-side pitch (JNR round: David asked the Adventures "why book through a
# tour agent" panel be replicated on Property and Cars BROWSE — buyer framing,
# not the sell-flow copy above) ─────────────────────────────────────────────
AGENT_ADVANTAGES_PROPERTY_BUY = [
    "Priced against real sales — agents know what comparable homes actually sold for, so you do not overpay on hope.",
    "Paperwork that protects you — a legally sound offer to purchase, mandatory disclosure forms and compliance certificates checked before you sign.",
    "Your deposit protected — PPRA-registered agents hold a Fidelity Fund Certificate; trust monies are covered by law.",
    "The full picture — defects, servitudes, levies, rates clearance and transfer costs surfaced before they become your problem.",
    "A guided transfer — bond approval, conveyancer and occupation dates coordinated by someone who closes sales every month.",
]

LEGAL_NOTE_PROPERTY_BUY = ("Buying property directly carries real risks you keep: hidden defects, unsigned "
              "mandatory disclosures, deposits paid without trust protection, and offers drafted from "
              "templates. A PPRA-registered agent with a Fidelity Fund Certificate carries what they may, "
              "and facilitates the rest.")

AGENT_ADVANTAGES_CARS_BUY = [
    "Right price, real market — priced against live trade and retail data, not a stranger's asking price.",
    "The car is what it claims — NATIS history, outstanding finance and accident checks done before you commit.",
    "Roadworthy and registration handled — RWC, licence and change of ownership done properly, within the legal 21 days.",
    "Safe payment — money and transfer through proper channels, not cash handovers or EFT-and-hope.",
    "Recourse if it goes wrong — registered dealers stand under the Consumer Protection Act; a private seller's 'voetstoots' usually does not.",
]

LEGAL_NOTE_CARS_BUY = ("Buying a car privately carries real risks you keep: cloned or still-financed vehicles, "
              "odometer fraud, voetstoots terms, and cash handovers with no recourse. A MIRA-registered "
              "sales agent carries what they may, and facilitates the rest.")

AGENT_ADVANTAGES_CARS = [
    "Right price, real market — priced against live trade and retail data, not guesswork or lowball WhatsApp offers.",
    "Paperwork handled — NATIS change of ownership, roadworthy certificate, licence and registration done properly.",
    "Finance settled safely — outstanding finance verified and settled through the right channels before transfer.",
    "Qualified buyers only — no tyre-kickers; buyers are screened and finance pre-checked before a test drive.",
    "Safe viewings — no strangers at your home with your keys; viewings and test drives are managed for you.",
]

LEGAL_NOTE_CARS = ("Selling a car privately still carries legal steps you keep: NATIS change of ownership "
              "(within 21 days), a valid roadworthy certificate for re-registration, settling any outstanding "
              "finance before transfer, and honest disclosure of defects. See the legal must-haves card in the "
              "sell flow (Step 6) — a registered dealer manages what they may, and facilitates the rest.")

VERTICALS = {
    "property": {
        "label": "Estate Agent",
        "listing_category": "property",
        "slots": CREDENTIAL_SLOTS_PROPERTY,
        "badge_signals": {
            "category.property.ppra":      "PPRA registered",
            "category.property.ffc":       "Fidelity Fund Certificate",
            "category.property.nqf4":      "NQF4 Real Estate",
            "category.property.nqf5":      "NQF5 Real Estate",
            "category.property.nqf6_plus": "NQF6+ / Professional designation",
            "category.property.body":      "Professional body member",
        },
        "stock_photo": "/static/agent-stock/property.jpg",
        "gate_signal": "category.property.ffc",
        "gate_label": "FFC",
        "gate_desc": "legal minimum to trade",
        "submit_required": [("category.property.ppra", "PPRA registration not submitted")],
        "advantages": AGENT_ADVANTAGES_PROPERTY,
        "legal_note": LEGAL_NOTE_PROPERTY,
        "advantages_buy": AGENT_ADVANTAGES_PROPERTY_BUY,
        "legal_note_buy": LEGAL_NOTE_PROPERTY_BUY,
        "sold_noun": "properties",
    },
    "cars": {
        "label": "Car Sales Agent",
        "listing_category": "cars",
        "slots": CREDENTIAL_SLOTS_CARS,
        "badge_signals": {
            "category.cars.dealer_reg": "MIRA Registered Dealer",
            "category.cars.inspection": "Independent inspection partner",
        },
        "stock_photo": "/static/agent-stock/cars.jpg",
        "gate_signal": "category.cars.dealer_reg",
        "gate_label": "MIRA dealer registration",
        "gate_desc": "professional minimum to trade",
        "submit_required": [],
        "advantages": AGENT_ADVANTAGES_CARS,
        "legal_note": LEGAL_NOTE_CARS,
        "advantages_buy": AGENT_ADVANTAGES_CARS_BUY,
        "legal_note_buy": LEGAL_NOTE_CARS_BUY,
        "sold_noun": "cars",
    },
    "travel": {
        "label": "Tour Agent",
        "listing_category": "adventures",
        "slots": CREDENTIAL_SLOTS_TRAVEL,
        "badge_signals": {
            "category.travel.asata_member":      "ASATA member",
            "category.travel.iata_accredited":   "IATA accredited",
            "category.travel.cipc_registered":   "Registered company (CIPC)",
            "category.travel.financial_bonding": "Client payments bonded",
            "category.travel.client_insurance":  "Travel insurance facility",
        },
        "stock_photo": "/static/agent-stock/travel.jpg",
        "gate_signal": "category.travel.asata_member",
        "gate_label": "ASATA membership",
        "gate_desc": "professional minimum to trade",
        "submit_required": [("category.travel.cipc_registered", "CIPC company registration not submitted")],
        "advantages": [
            "Better trips for the same money — package rates, route knowledge and operator deals you cannot get booking piecemeal.",
            "Vetted operators only — no fly-by-night 'tour companies' that vanish with your deposit.",
            "Your money protected — bonded agents and travel-insurance facilities cover client payments if things fall over.",
            "Itineraries that actually work — connections, seasons, visas and permits planned by someone who does it daily.",
            "Help when it goes wrong — a cancelled flight or closed border becomes the agent's problem to fix, not yours.",
        ],
        "legal_note": ("Booking travel directly carries real risks you keep: unbonded operators, deposit scams, "
                       "visa and permit requirements, and cancellation terms buried in fine print. A bonded, "
                       "accredited tour agent carries what they may, and facilitates the rest."),
        "sold_noun": "trips",
    },
    "collector": {
        "label": "Collector Dealer",
        "listing_category": "collectors",
        "slots": CREDENTIAL_SLOTS_COLLECTOR,
        "badge_signals": {
            "category.collector.shg_registered": "SAPS SHG registered dealer",
            "category.collector.cipc_registered": "Registered company (CIPC)",
            "category.collector.assoc_member": "Dealer association member",
            "category.collector.grading": "Grading partner",
        },
        "stock_photo": "/static/agent-stock/property.jpg",
        "gate_signal": "category.collector.shg_registered",
        "gate_label": "SAPS Second-Hand Goods registration",
        "gate_desc": "statutory minimum to trade",
        "submit_required": [("category.collector.cipc_registered", "CIPC company registration not submitted")],
        "advantages": [
            "Authentication and provenance — a dealer stakes a reputation on what a piece IS, before you pay for what it claims to be.",
            "Fair, catalogue-based valuation — priced against Numista, auction records and grading standards, not sentiment.",
            "Serious collectors, not chancers — introductions come from buyers who already paid to reach you.",
            "Safe handover — no strangers with cash at your door; the exchange is arranged properly.",
        ],
        "legal_note": ("Trading collectibles privately carries risks you keep: fakes, misgraded pieces, and "
                       "Second-Hand Goods Act obligations on dealers. A SAPS-registered dealer carries what "
                       "they may, and facilitates the rest."),
        "sold_noun": "pieces",
    },
    "institution": {
        "label": "Tutor",
        "listing_category": "tutors",
        "slots": CREDENTIAL_SLOTS_INSTITUTION,
        "badge_signals": {
            "category.institution.clearances": "Safety-cleared (PCC + CPR + NRSO)",
            "category.institution.sace": "SACE registered",
            "category.institution.saqa": "SAQA-verified qualification",
        },
        "stock_photo": "/static/agent-stock/property.jpg",
        "gate_signal": "category.institution.clearances",
        "gate_label": "Safety clearances (PCC + CPR + NRSO)",
        "gate_desc": "child-safety minimum — a verified SACE registration covers all three",
        "submit_required": [],
        "advantages": [
            "Register-cleared tutors — police clearance plus the Child Protection and Sexual Offenders registers, checked before anyone meets your child.",
            "Verified qualifications — SACE or SAQA-verified, not a claimed degree.",
            "Subject-matched — ranked by the subjects and levels your learner actually needs.",
            "Progress accountability — an institution behind the tutor, not a stranger from a flyer.",
        ],
        "legal_note": ("Hiring a tutor privately carries risks you keep: unverified strangers with your child, "
                       "claimed qualifications, no recourse. Schools are legally required to run register checks "
                       "on anyone working with children — our gate simply applies the same standard."),
        "sold_noun": "learners",
    },
    "service_company": {
        "label": "Technician",
        "listing_category": "services",
        "slots": CREDENTIAL_SLOTS_SERVICE,
        "badge_signals": {
            "category.service.trade_licence": "Licensed (CoC-issuing)",
            "category.service.cipc_registered": "Registered company (CIPC)",
            "category.service.insured": "Public liability insured",
            "category.service.cidb": "CIDB graded",
        },
        "stock_photo": "/static/agent-stock/property.jpg",
        "gate_signal": "category.service.trade_licence",
        "gate_label": "Trade licence",
        "gate_desc": "the CoC-issuing minimum for regulated trades",
        "submit_required": [("category.service.cipc_registered", "CIPC company registration not submitted")],
        "advantages": [
            "Licensed, CoC-issuing professionals — the certificate your insurance and property transfer depend on, signed by someone allowed to sign it.",
            "Insured work — public liability cover before anyone lifts a tool.",
            "Vetted local teams — ranked by trust and the quality of their work, in your area.",
            "No cash-at-door chancers — introductions are accepted by the technician, with a score attached.",
        ],
        "legal_note": ("Hiring trades privately carries risks you keep: unlicensed work that voids insurance, "
                       "invalid Certificates of Compliance, and no recourse. A licensed technician carries what "
                       "they may, and facilitates the rest."),
        "sold_noun": "jobs",
    },
    "placement": {
        "label": "Placement Consultant",
        "listing_category": "placement",
        "slots": CREDENTIAL_SLOTS_PLACEMENT,
        "badge_signals": {
            "category.placement.del_registered": "DEL-registered agency",
            "category.placement.cipc_registered": "Registered company (CIPC)",
            "category.placement.apso": "APSO member",
            "category.placement.sponsors": "Sponsor network",
        },
        "stock_photo": "/static/agent-stock/travel.jpg",
        "gate_signal": "category.placement.del_registered",
        "gate_label": "DEL registration",
        "gate_desc": "statutory minimum for a private employment agency",
        "submit_required": [("category.placement.cipc_registered", "CIPC company registration not submitted")],
        "advantages": [
            "DEL-registered agencies only — registration with the Department of Employment and Labour is the law, and our gate.",
            "You never pay the agency — the Employment Services Act prohibits charging workseekers, and so do we: the consultant pays 1T to accept YOUR introduction.",
            "Honest programme facts — sourced and dated, no guaranteed-visa promises (the rules that protect you are our rules too).",
            "Dossier-ready handoff — your preparation arrives organised, so the consultant starts on your plan, not your paperwork.",
        ],
        "legal_note": ("Overseas placement carries real risks you keep: unregistered agencies, fees the law "
                       "prohibits, and visa promises nobody can make. A DEL-registered, bonded agency carries "
                       "what they may, and facilitates the rest."),
        "sold_noun": "placements",
    },
}

def _vert(v):
    v = str(v or "property").strip().lower()
    return v if v in VERTICALS else "property"

@router.get("/agents/template")
def agent_template(vertical: str = "property"):
    """Canonical agent service-listing template (per vertical) — used by the
    profile editor, the agency bulk uploader and the ops verification queue."""
    v = _vert(vertical); V = VERTICALS[v]
    return {
        "version": "2.0",
        "vertical": v,
        "verticals": list(VERTICALS),
        "label": V["label"],
        "category": V["listing_category"],
        "service": v + "_agent",
        "profile_fields": {
            "headline":         {"required": True,  "anonymised": True, "max_len": 90,
                                 "hint": "What you are best at — no names, no agency brand."},
            "bio":              {"required": True,  "anonymised": True, "min_words": 30,
                                 "hint": "Comprehensive but anonymous: track record, specialty, how you work."},
            "years_experience": {"required": True,  "type": "int", "display": "banded"},
            "properties_sold":  {"required": False, "type": "int", "display": "banded",
                                 "hint": "Declared by you or your agency; shown banded with its source."},
            "city":             {"required": True},
            "suburbs":          {"required": False, "hint": "Areas served, comma-separated."},
            "specialties":      {"required": False, "hint": "e.g. residential, rentals, commercial, farms, sectional title"},
            "languages":        {"required": False},
        },
        "credential_slots": V["slots"],
        "experience_bands": [b[2] for b in EXPERIENCE_BANDS],
        "sold_bands": [b[2] for b in SOLD_BANDS],
        "go_live_gate": V["gate_label"] + " verified (earned) — the " + V["gate_desc"] + ". Everything else raises the score but does not block.",
        "ranking": "0.5 x avg live-listing quality (0-100) + 0.5 x trust score (0-100). Listing quality never weighs less than half.",
        "anonymisation": "Name, agency, contact details and links are stripped (regex + AI pass). Agents appear as 'Agent TS-XXXXXX' until an introduction is accepted.",
        "photo_rule": "PHOTO-ANON-1: agent service cards NEVER show a person. Every agent in a vertical carries the same generic stock scene (stock_photo). The agent's own listing photos become visible only through their live listings and on accepted introduction.",
        "stock_photo": V["stock_photo"],
    }

# ── Profile create / read / publish ─────────────────────────────────────────

class AgentProfileIn(BaseModel):
    email: str
    headline: Optional[str] = None
    bio: Optional[str] = None
    years_experience: Optional[int] = None
    properties_sold: Optional[int] = None
    city: Optional[str] = None
    suburbs: Optional[str] = None
    specialties: Optional[str] = None
    languages: Optional[str] = None
    agency_id: Optional[int] = None
    vertical: Optional[str] = None

def _new_ref():
    return "TS-" + uuid.uuid4().hex[:6].upper()

def _upsert_profile(conn, p: AgentProfileIn, sold_source: str = "declared"):
    email = p.email.strip().lower()
    head, _h = _anon(p.headline or "")
    bio, _b = _anon(p.bio or "")
    conn.execute("INSERT OR IGNORE INTO users (email) VALUES (?)", (email,))
    existing = conn.execute("SELECT anon_ref FROM agent_profiles WHERE agent_email=?", (email,)).fetchone()
    if existing:
        conn.execute("""UPDATE agent_profiles SET
            headline=COALESCE(NULLIF(?,''), headline), bio_anon=COALESCE(NULLIF(?,''), bio_anon),
            years_experience=COALESCE(?, years_experience), properties_sold=COALESCE(?, properties_sold),
            sold_source=?, city=COALESCE(NULLIF(?,''), city), suburbs=COALESCE(NULLIF(?,''), suburbs),
            specialties=COALESCE(NULLIF(?,''), specialties), languages=COALESCE(NULLIF(?,''), languages),
            agency_id=COALESCE(?, agency_id), vertical=COALESCE(NULLIF(?,''), vertical), updated_at=?
            WHERE agent_email=?""",
            (head, bio, p.years_experience, p.properties_sold, sold_source,
             (p.city or "").strip(), (p.suburbs or "").strip(), (p.specialties or "").strip(),
             (p.languages or "").strip(), p.agency_id, _vert(p.vertical) if p.vertical else "", _now(), email))
        return existing["anon_ref"]
    ref = _new_ref()
    conn.execute("""INSERT INTO agent_profiles
        (agent_email, anon_ref, agency_id, headline, bio_anon, years_experience, properties_sold,
         sold_source, city, suburbs, specialties, languages, profile_status, vertical, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?, 'draft', ?, ?, ?)""",
        (email, ref, p.agency_id, head, bio, p.years_experience, p.properties_sold, sold_source,
         (p.city or "").strip(), (p.suburbs or "").strip(), (p.specialties or "").strip(),
         (p.languages or "").strip(), _vert(p.vertical), _now(), _now()))
    return ref

def _credential_status(conn, email: str, signal_id: str) -> str:
    r = conn.execute("SELECT status FROM user_credentials WHERE email=? AND signal_id=?",
                     (email, signal_id)).fetchone()
    return r["status"] if r else "missing"

def _cred_pending(conn, email: str, signal_id: str):
    """Insert credential claim as PENDING — never downgrade earned (mirror of
    bea_main._upsert_credential semantics, kept local to avoid circular import)."""
    existing = conn.execute("SELECT status FROM user_credentials WHERE email=? AND signal_id=?",
                            (email, signal_id)).fetchone()
    if not existing:
        conn.execute("""INSERT INTO user_credentials (email, signal_id, status, listing_category, updated_at)
                        VALUES (?,?,'pending','Property',?)""", (email, signal_id, _now()))

def _badges(conn, email: str, vertical: str = "property"):
    sig_map = VERTICALS[_vert(vertical)]["badge_signals"]
    rows = conn.execute("SELECT signal_id, status FROM user_credentials WHERE email=? AND signal_id IN (%s)"
                        % ",".join("?" * len(sig_map)), (email, *list(sig_map))).fetchall()
    out = {"earned": [], "pending": []}
    for r in rows:
        if r["status"] == "earned":
            out["earned"].append(sig_map[r["signal_id"]])
        elif r["status"] == "pending":
            out["pending"].append(sig_map[r["signal_id"]])
    return out

def _agent_listing_stats(conn, email: str, vertical: str = "property"):
    """Live listings in the vertical's category + avg quality (same 100-pt scorer
    as the import gate)."""
    cat = VERTICALS[_vert(vertical)]["listing_category"]
    rows = conn.execute("""SELECT * FROM listings WHERE LOWER(seller_email)=?
                           AND LOWER(category) LIKE ? AND COALESCE(listing_status,'live')='live'""",
                        (email, cat + '%')).fetchall()   # ADV-FIX-3: adventures subtypes (adventures_experiences etc.)
    n = len(rows)
    if not n:
        return 0, 0
    total = 0
    for r in rows:
        s, _m = _quality(r)
        total += int(s)
    return n, int(round(total / n))

@router.post("/agents/profile")
def upsert_agent_profile(p: AgentProfileIn):
    if "@" not in (p.email or ""):
        raise HTTPException(status_code=400, detail="valid email required")
    conn = database.get_db()
    try:
        init_schema(conn)
        ref = _upsert_profile(conn, p)
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "anon_ref": ref, "profile_status": "draft",
            "note": "Upload FFC + PPRA under Trust Score to unlock go-live."}

@router.get("/agents/profile")
def get_agent_profile(email: str):
    email = email.strip().lower()
    conn = database.get_db()
    try:
        init_schema(conn)
        prof = conn.execute("SELECT * FROM agent_profiles WHERE agent_email=?", (email,)).fetchone()
        if not prof:
            raise HTTPException(status_code=404, detail="No agent profile — POST /agents/profile first")
        user = conn.execute("SELECT trust_score FROM users WHERE LOWER(email)=?", (email,)).fetchone()
        _v = _vert(prof["vertical"] if "vertical" in prof.keys() else "property")
        n_live, avg_q = _agent_listing_stats(conn, email, _v)
        badges = _badges(conn, email, _v)
        gate = _go_live_gaps(conn, dict(prof))
        trust = int(user["trust_score"] or 0) if user else 0
        # MAROUSHKA-CRED-1 (3 Aug 2026, Maroushka feedback): "I could not add my
        # agency info like the FFC etc." The profile form had no field for any of
        # it. Return the vertical's credential slots WITH their live status so the
        # form can render an upload row per slot, and resolve the agent's agency
        # from membership so they can see which firm they sit under.
        slots = []
        for s in VERTICALS[_v]["slots"]:
            sig = s.get("signal_id")
            slots.append({
                "slot": s["slot"], "label": s["label"], "signal_id": sig,
                "points": s.get("points"), "legal": bool(s.get("legal")),
                "verify": s.get("verify", ""),
                "status": _credential_status(conn, email, sig) if sig else "n/a",
            })
        try:
            ag = conn.execute(
                "SELECT a.id, a.name, a.verified, m.listing_cap, m.status "
                "FROM agency_members m JOIN agencies a ON a.id = m.agency_id "
                "WHERE LOWER(m.agent_email)=? AND m.status != 'removed' LIMIT 1", (email,)).fetchone()
        except Exception:
            ag = None   # agency tables live in the main app migration; absent on a bare schema
        agency = ({"id": ag["id"], "name": ag["name"], "verified": bool(ag["verified"]),
                   "listing_cap": ag["listing_cap"], "member_status": ag["status"]}
                  if ag else None)
        return {**{k: prof[k] for k in prof.keys()},
                "credential_slots": slots,
                "agency": agency,
                "trust_score": trust,
                "live_listings": n_live, "avg_listing_quality": avg_q,
                "match_rank": round(0.5 * avg_q + 0.5 * trust, 1),
                "stock_photo": VERTICALS[_v]["stock_photo"],
                "metrics_note": "Trust Score = verified credentials (upload under Trust Score). Avg Listing Quality = your live adverts, coached toward 100. Match Rank = 50/50 blend — this is your position in the list prospects choose from.",
                "badges": badges, "go_live_gaps": gate}
    finally:
        conn.close()

def _go_live_gaps(conn, prof: dict) -> list:
    gaps = []
    if not (prof.get("headline") or "").strip():
        gaps.append("headline missing")
    if len(re.findall(r"\S+", prof.get("bio_anon") or "")) < 30:
        gaps.append("bio too thin (30+ words)")
    if not (prof.get("city") or "").strip():
        gaps.append("city missing")
    if prof.get("years_experience") is None:
        gaps.append("years of experience missing")
    V = VERTICALS[_vert(prof.get("vertical"))]
    gate = _credential_status(conn, prof["agent_email"], V["gate_signal"])
    if gate != "earned":
        gaps.append(f"{V['gate_label']} not verified (status: {gate}) — {V['gate_desc']}")
    for sig, msg in V["submit_required"]:
        if _credential_status(conn, prof["agent_email"], sig) not in ("earned", "pending"):
            gaps.append(msg)
    return gaps

@router.put("/agents/profile/publish")
def publish_agent_profile(email: str):
    email = email.strip().lower()
    conn = database.get_db()
    try:
        init_schema(conn)
        prof = conn.execute("SELECT * FROM agent_profiles WHERE agent_email=?", (email,)).fetchone()
        if not prof:
            raise HTTPException(status_code=404, detail="No agent profile")
        gaps = _go_live_gaps(conn, dict(prof))
        if gaps:
            raise HTTPException(status_code=422, detail={"message": "Profile cannot go live yet", "fix": gaps})
        conn.execute("UPDATE agent_profiles SET profile_status='live', updated_at=? WHERE agent_email=?",
                     (_now(), email))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "profile_status": "live"}

# ── Bulk agency onboarding ──────────────────────────────────────────────────

class BulkAgentIn(BaseModel):
    email: str
    name: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    suburbs: Optional[str] = None
    headline: Optional[str] = None
    bio: Optional[str] = None
    years_experience: Optional[int] = None
    properties_sold: Optional[int] = None
    listing_cap: Optional[int] = None
    vertical: Optional[str] = None
    ppra_number: Optional[str] = None
    ffc_year: Optional[int] = None
    nqf_level: Optional[int] = None
    body_memberships: Optional[List[str]] = None
    mira_number: Optional[str] = None
    inspection_partner: Optional[str] = None
    asata_number: Optional[str] = None
    iata_code: Optional[str] = None
    cipc_number: Optional[str] = None
    bonding_proof: Optional[str] = None
    # VERT-4-1 (RUL-049): the four recruited verticals' credential slots
    shg_registration: Optional[str] = None
    assoc_memberships: Optional[str] = None
    grading_partner: Optional[str] = None
    sace_number: Optional[str] = None
    clearance_refs: Optional[str] = None
    saqa_ref: Optional[str] = None
    trade_licence: Optional[str] = None
    insurance_ref: Optional[str] = None
    cidb_grade: Optional[str] = None
    del_pea_number: Optional[str] = None
    apso_member: Optional[str] = None
    sponsor_network: Optional[str] = None

class BulkOnboardIn(BaseModel):
    agents: List[BulkAgentIn]
    vertical: Optional[str] = None   # agency-level default; per-agent overrides
    api_key: Optional[str] = None    # AGENCY-KEY-1 (23 Aug 2026): the agency's OWN key may auth the roster --
                                     # the Import Guide always promised "same API key"; now the code agrees

@router.post("/agencies/{agency_id}/agents/bulk")
def bulk_onboard_agents(agency_id: int, req: BulkOnboardIn,
                        x_api_key: Optional[str] = Header(default=None, alias="X-Api-Key")):
    """Agency bulk onboarding: membership + anonymised service profile + credential
    CLAIMS (pending, verified by ops before they score).
    AUTH (AGENCY-KEY-1): EITHER the app X-Api-Key header (console path) OR the
    agency's own api_key in the body (the IT-person path the Import Guide documents,
    mirroring /agencies/{id}/import)."""
    conn = database.get_db()
    try:
        init_schema(conn)
        _ag = conn.execute("SELECT id, api_key, name FROM agencies WHERE id=?", (agency_id,)).fetchone()
        if not _ag:
            raise HTTPException(status_code=404, detail="Agency not found")
        if not ((x_api_key and x_api_key == auth.API_KEY) or (req.api_key and req.api_key == _ag["api_key"])):
            raise HTTPException(status_code=401, detail="Auth failed: send the app X-Api-Key header, or your agency api_key in the body")
        report = []
        for a in req.agents:
            email = (a.email or "").strip().lower()
            if "@" not in email:
                report.append({"email": a.email, "ok": False, "error": "invalid email"})
                continue
            cap = int(a.listing_cap or 10)
            conn.execute("INSERT OR IGNORE INTO users (email) VALUES (?)", (email,))
            conn.execute("UPDATE users SET slot_limit=?, seller_tier='starter' WHERE LOWER(email)=?", (cap, email))
            conn.execute("""INSERT INTO agency_members (agency_id, agent_email, listing_cap, status, agent_name, city, country)
                VALUES (?,?,?,'invited',?,?,?)
                ON CONFLICT(agency_id, agent_email) DO UPDATE SET listing_cap=excluded.listing_cap,
                agent_name=COALESCE(excluded.agent_name, agent_name), city=COALESCE(excluded.city, city),
                country=COALESCE(excluded.country, country)""",
                (agency_id, email, cap, (a.name or "").strip() or None,
                 (a.city or "").strip() or None, (a.country or "").strip().upper() or None))
            _v = _vert(a.vertical or req.vertical)
            ref = _upsert_profile(conn, AgentProfileIn(
                email=email, headline=a.headline, bio=a.bio, years_experience=a.years_experience,
                properties_sold=a.properties_sold, city=a.city, suburbs=a.suburbs, agency_id=agency_id,
                vertical=_v),
                sold_source="agency")
            pending = []
            # VERT-4-1 (RUL-049): GENERIC slot walk -- a new vertical needs slots in
            # VERTICALS and fields on BulkAgentIn, never another branch here. This is
            # the class fix for the hardcoded if/elif that silently routed unknown
            # verticals into the travel branch.
            _V = VERTICALS[_v]
            for _slot in _V["slots"]:
                _sid = _slot.get("signal_id")
                if not _sid:
                    if _slot["slot"] == "nqf_level" and a.nqf_level in _NQF_CHAIN:
                        for _s2 in _NQF_CHAIN[a.nqf_level]:
                            _cred_pending(conn, email, _s2)
                        pending.append(f"nqf{a.nqf_level}")
                    continue
                _val = getattr(a, _slot["slot"], None)
                if _val is None:
                    continue
                if isinstance(_val, str) and not _val.strip():
                    continue
                if isinstance(_val, list) and not _val:
                    continue
                _cred_pending(conn, email, _sid)
                pending.append(_slot["slot"])
            # INSTITUTION rule (RUL-049): a submitted SACE number embeds the three
            # safety clearances -- mark the clearances gate pending alongside it, so
            # ops verifying SACE earns the gate in one act.
            if _v == "institution" and (a.sace_number or "").strip() and not (a.clearance_refs or "").strip():
                _cred_pending(conn, email, "category.institution.clearances")
                if "clearance_refs" not in pending:
                    pending.append("clearance_refs")
            report.append({"email": email, "ok": True, "anon_ref": ref, "vertical": _v,
                           "credentials_pending": pending,
                           "note": "Score moves only when ops verifies each credential."})
        conn.commit()
    finally:
        conn.close()
    # AGENCY-INVITE-MAIL-1 (24 Aug 2026): the lane PROMISES 'each agent instantly
    # gets a sign-in link' (outreach lane 2 + Import Guide step 1) -- so send it,
    # per agent, and report what actually happened. 'dry' = no invite seam
    # configured (standalone tests) or no mail transport on the server.
    _ag_name = ""
    try:
        _ag_name = (_ag["name"] or "") if "name" in _ag.keys() else ""
    except Exception:
        pass
    for _r in report:
        if _r.get("ok"):
            try:
                _r["link"] = _INVITE_FN(_r["email"], _ag_name) if _INVITE_FN else "dry"
            except Exception:
                _r["link"] = "failed"
    ok_n = sum(1 for r in report if r.get("ok"))
    return {"ok": True, "agency_id": agency_id, "onboarded": ok_n,
            "failed": len(report) - ok_n, "agents": report,
            "next": "Sign-in links emailed to each onboarded agent (per-agent 'link' shows sent/failed). Ops verifies pending credentials via /trust-score/credentials/pending; then each agent publishes their profile."}

# ── Local ranked agent list (seller-facing, anonymised) ─────────────────────

def _rank_agents(conn, city: str, suburb: str = "", limit: int = 10, vertical: str = "property"):
    v = _vert(vertical)
    q = "SELECT * FROM agent_profiles WHERE profile_status='live' AND vertical=?"
    params = [v]
    if city:
        q += " AND LOWER(city)=?"
        params.append(city.strip().lower())
    rows = conn.execute(q, params).fetchall()
    out = []
    for prof in rows:
        email = prof["agent_email"]
        user = conn.execute("SELECT trust_score FROM users WHERE LOWER(email)=?", (email,)).fetchone()
        trust = int(user["trust_score"] or 0) if user else 0
        n_live, avg_q = _agent_listing_stats(conn, email, v)
        rank = round(0.5 * avg_q + 0.5 * trust, 1)
        suburb_match = bool(suburb) and suburb.strip().lower() in (prof["suburbs"] or "").lower()
        badges = _badges(conn, email, v)
        out.append({
            "anon_ref": prof["anon_ref"],
            "photo": VERTICALS[v]["stock_photo"],   # PHOTO-ANON-1: same scene for every agent in the vertical
            "headline": prof["headline"],
            "bio": prof["bio_anon"],
            "city": prof["city"],
            "suburbs": prof["suburbs"],
            "specialties": prof["specialties"],
            "languages": prof["languages"],
            "experience": _band(prof["years_experience"], EXPERIENCE_BANDS),
            "vertical": v,
            "properties_sold": (_band(prof["properties_sold"], SOLD_BANDS).replace("properties sold", VERTICALS[v]["sold_noun"] + " sold") if prof["properties_sold"] else None),
            "sold_source": prof["sold_source"],
            "trust_score": trust,
            "avg_listing_quality": avg_q,
            "live_listings": n_live,
            "rank_score": rank,
            "suburb_match": suburb_match,
            "badges_earned": badges["earned"],
        })
    out.sort(key=lambda r: (not r["suburb_match"], -r["rank_score"]))
    return out[:max(1, min(50, limit))]

@router.get("/agents/nearby")
def agents_nearby(city: str, suburb: str = "", limit: int = 10, vertical: str = "property"):
    conn = database.get_db()
    try:
        init_schema(conn)
        agents = _rank_agents(conn, city, suburb, limit, vertical)
    finally:
        conn.close()
    return {"city": city, "suburb": suburb or None, "vertical": _vert(vertical),
            "count": len(agents), "agents": agents}

@router.get("/agents/pitch")
def agent_pitch(city: str = "", suburb: str = "", vertical: str = "property", side: str = "sell"):
    """Seller-side nudge content for the sell flow: why use an agent/dealer, the
    legal reality, and a preview of local listed agents (anonymised, ranked)."""
    v = _vert(vertical); V = VERTICALS[v]
    conn = database.get_db()
    try:
        init_schema(conn)
        preview = _rank_agents(conn, city, suburb, 3, v) if city else []
        _q = "SELECT COUNT(*) AS n FROM agent_profiles WHERE profile_status='live' AND vertical=?"
        _p = [v]
        if city:
            _q += " AND LOWER(city)=?"; _p.append(city.strip().lower())
        n = conn.execute(_q, _p).fetchone()["n"]
    finally:
        conn.close()
    _buy = (side or "sell").strip().lower() == "buy"
    return {"vertical": v, "label": V["label"], "side": ("buy" if _buy else "sell"),
            "advantages": (V.get("advantages_buy") or V["advantages"]) if _buy else V["advantages"],
            "legal_note": (V.get("legal_note_buy") or V["legal_note"]) if _buy else V["legal_note"],
            "local_agent_count": n, "preview": preview,
            "cta": ("Pick one and we introduce you — no phoning around, no lead brokers. They pay 1T only if they accept."
                    if v != "travel" else
                    "Tell us what you are dreaming of and we introduce you — free for you. The agent pays 1T only if they accept your request.")}

# ── Reverse INTRO: seller → agent, 1T on accept ─────────────────────────────

class AgentIntroIn(BaseModel):
    seller_email: str
    agent_ref: str
    listing_id: Optional[int] = None
    message: Optional[str] = None

@router.post("/agents/intro")
def request_agent_intro(req: AgentIntroIn):
    seller = (req.seller_email or "").strip().lower()
    if "@" not in seller:
        raise HTTPException(status_code=400, detail="valid seller email required")
    conn = database.get_db()
    try:
        init_schema(conn)
        prof = conn.execute("SELECT * FROM agent_profiles WHERE anon_ref=? AND profile_status='live'",
                            (req.agent_ref,)).fetchone()
        if not prof:
            raise HTTPException(status_code=404, detail="Agent not found or not live")
        if prof["agent_email"] == seller:
            raise HTTPException(status_code=409, detail="You cannot request an introduction to yourself")
        dup = conn.execute("""SELECT id FROM agent_intros WHERE seller_email=? AND agent_email=?
                              AND status='pending'""", (seller, prof["agent_email"])).fetchone()
        if dup:
            raise HTTPException(status_code=409, detail="You already have a pending introduction to this agent")
        u = conn.execute("SELECT trust_score FROM users WHERE LOWER(email)=?", (seller,)).fetchone()
        seller_trust = int(u["trust_score"] or 0) if u else 0
        lq = 0
        if req.listing_id:
            lrow = conn.execute("SELECT * FROM listings WHERE id=? AND LOWER(seller_email)=?",
                                (req.listing_id, seller)).fetchone()
            if not lrow:
                raise HTTPException(status_code=404, detail="Listing not found under your account")
            lq, _m = _quality(lrow)
        msg, _hits = _anon(req.message or "")
        conn.execute("""INSERT INTO agent_intros (seller_email, agent_email, listing_id, message,
                        seller_trust_snapshot, listing_quality_snapshot, status, created_at)
                        VALUES (?,?,?,?,?,?,'pending',?)""",
                     (seller, prof["agent_email"], req.listing_id, msg, seller_trust, int(lq), _now()))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "status": "pending",
            "note": "The agent sees your trust score and property summary — not your identity. Contact is shared only if they accept."}

@router.get("/agents/intros")
def agent_intro_inbox(email: str, status: str = "pending"):
    """Agent inbox — seller anonymous until accept; trust + quality visible."""
    email = email.strip().lower()
    conn = database.get_db()
    try:
        init_schema(conn)
        q = "SELECT * FROM agent_intros WHERE agent_email=?"
        params = [email]
        if status != "all":
            q += " AND status=?"
            params.append(status)
        rows = conn.execute(q + " ORDER BY created_at DESC", params).fetchall()
        out = []
        for r in rows:
            item = {k: r[k] for k in r.keys()}
            listing = None
            if r["listing_id"]:
                lrow = conn.execute("SELECT title, city, suburb, prop_type, beds, baths, price FROM listings WHERE id=?",
                                    (r["listing_id"],)).fetchone()
                if lrow:
                    listing = {k: lrow[k] for k in lrow.keys()}
            item["listing"] = listing
            if r["status"] != "accepted":
                item.pop("seller_email", None)
            out.append(item)
    finally:
        conn.close()
    return out

@router.get("/agents/intros/for-seller")
def seller_intro_status(email: str):
    email = email.strip().lower()
    conn = database.get_db()
    try:
        init_schema(conn)
        rows = conn.execute("""SELECT ai.id, ai.status, ai.created_at, ai.responded_at, ai.listing_id, ap.anon_ref,
                               CASE WHEN ai.status='accepted' THEN ai.agent_email ELSE NULL END AS agent_email
                               FROM agent_intros ai LEFT JOIN agent_profiles ap ON ap.agent_email=ai.agent_email
                               WHERE ai.seller_email=? ORDER BY ai.created_at DESC""", (email,)).fetchall()
        return [{k: r[k] for k in r.keys()} for r in rows]
    finally:
        conn.close()

def _tuppence_balance(conn, email: str) -> int:
    r = conn.execute("SELECT COALESCE(SUM(amount),0) AS bal FROM transactions WHERE user_email=?", (email,)).fetchone()
    return int(r["bal"] or 0)

@router.put("/agents/intros/{intro_id}/accept")
def accept_agent_intro(intro_id: int, email: str):
    """Agent accepts the seller lead — 1T charged to the AGENT (the lead fee that
    replaces cold calling and paid lead brokers). Contact revealed both ways."""
    email = email.strip().lower()
    conn = database.get_db()
    try:
        init_schema(conn)
        intro = conn.execute("SELECT * FROM agent_intros WHERE id=? AND agent_email=?", (intro_id, email)).fetchone()
        if not intro:
            raise HTTPException(status_code=404, detail="Intro not found for this agent")
        if intro["status"] != "pending":
            raise HTTPException(status_code=409, detail=f"Intro already {intro['status']}")
        if _tuppence_balance(conn, email) < 1:
            raise HTTPException(status_code=402, detail="Insufficient Tuppence — top up to accept this introduction (1T)")
        conn.execute("UPDATE agent_intros SET status='accepted', tuppence_charged=1, responded_at=? WHERE id=?",
                     (_now(), intro_id))
        conn.execute("INSERT INTO transactions (user_email, type, amount, description) VALUES (?,'intro_deduct',-1,?)",
                     (email, f"Seller lead accepted · agent intro #{intro_id}"))
        conn.commit()
        seller = intro["seller_email"]
    finally:
        conn.close()
    return {"ok": True, "status": "accepted", "charged": "1T", "seller_email": seller,
            "note": "Contact details are now shared with the seller."}

@router.put("/agents/intros/{intro_id}/decline")
def decline_agent_intro(intro_id: int, email: str):
    email = email.strip().lower()
    conn = database.get_db()
    try:
        init_schema(conn)
        intro = conn.execute("SELECT * FROM agent_intros WHERE id=? AND agent_email=?", (intro_id, email)).fetchone()
        if not intro:
            raise HTTPException(status_code=404, detail="Intro not found for this agent")
        if intro["status"] != "pending":
            raise HTTPException(status_code=409, detail=f"Intro already {intro['status']}")
        conn.execute("UPDATE agent_intros SET status='declined', responded_at=? WHERE id=?", (_now(), intro_id))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "status": "declined", "charged": "0T"}
