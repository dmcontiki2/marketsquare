# Super Advert Trust Ladder — sign-off sheet (27 Jul 2026)

Goal: ahead of the agency auto-email, Cars and Property each show a three-rung trust
ladder — the existing baseline super stays, two new supers per category demonstrate
the two routes up. All scores are computed from the live _TRUST_SIGNALS tables
(base 40 + verified signals; tiers locked at 40/70/90 — Principle A5). Adventures
unchanged (three supers already). David Jnr's live test advert: ARCHIVED, not deleted.

## CARS

**C1 (exists, unchanged) — baseline · Trust 50 · Established (blue)**
The measuring stick: where every seller starts.

**C2 NEW — "the credential route" · Trust 80 · TRUSTED (green)**
Persona: private seller, Centurion — one meticulously documented family SUV
(white Corolla Cross type, fictional reg). Zero sales history; pure paperwork.
Credential sheet (verified points): ID verified +15 · Complete profile +5 ·
NATIS ownership +10 · Roadworthy cert +6 · Service history +4 → 40+40 = **80**
Lesson: a first-time private seller can reach Trusted before their first sale.

**C3 NEW — "the earned route" · Trust ≈92 · HIGHLY TRUSTED (gold)**
Persona: small family dealership, Polokwane (fictional name), blue double-cab.
Sheet: ID +15 · Profile +5 · MIRA dealer registration +8 · NATIS ownership +10 ·
1–4 intros +8 · 5–14 intros +6 → 40+52 = **92**
(tx milestone point values to be confirmed from the live table at seed time —
composition adjusts to land in gold either way.)
Lesson: registration plus a real trading record buys gold — time in the arena counts.

## PROPERTY

**P1 (exists, unchanged) — baseline.**

**P2 NEW — "the credential route" · Trust 81 · TRUSTED (green)**
Persona: newly registered solo agent, Bloemfontein; one 3-bed family home.
Sheet: ID +15 · Profile +5 · Active PPRA registration +15 · NQF4 +6 → 40+41 = **81**
(FFC shown as *pending* — a deliberate, honest gap that teaches the next step.)

**P3 NEW — "the earned route" · Trust 95 · HIGHLY TRUSTED (gold)**
Persona: established agency, 12 years, Gqeberha; one 4-bed with garden.
Sheet: ID +15 · Profile +5 · PPRA +15 · FFC +10 · 10+ years experience +5 ·
Professional body (IEASA) +5 → 40+55 = **95**, plus a 15+ introduction history displayed.

## Standards (all four)

- Listing Quality built to ~100: 5+ photos, every required field, 15+ word
  description, real price, suburb — model adverts, so Rank (50% Trust + 50% Quality)
  reads clean on every card.
- Same subject throughout: 8 photos per advert of ONE car / ONE home,
  via Higgsfield reference-image consistency (the proven cream-Land-Cruiser method).
  Car shots: ¾ front hero, ¾ rear, side profile, dash, seats, engine bay, boot, detail.
  Home shots: facade hero, lounge, kitchen, main bedroom, bathroom, garden, patio, garage/plot.
- SO-1: all names, registrations and addresses fictional; city-level locators only.
- Scores seeded as real user_credentials rows (status=verified) so the Trust Hub
  breakdown reconciles perfectly with the badge — computed, never painted.
- Seed via idempotent dry-run-first scripts in the house pattern, armed as a deploy flag.

## Assumed defaults (say if wrong)

1. Self-declared chips: VISIBLE to buyers, greyed "+0 — unverified" (matches the
   ranking explainer, panel 1).
2. Gold prominence: as currently built — gold badge on cards, no extra featuring.
3. Launch date: STILL NEEDED from David to anchor the email-minus-one-week deadline.
