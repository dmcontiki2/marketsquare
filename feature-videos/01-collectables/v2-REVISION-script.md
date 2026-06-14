# Collectables Advert + Market Report — VIDEO v2 (revision script)

Upgrades the existing 55s tutor (`collectables-advert-howto-7steps-55s.mp4`) into the full ad format with David's 6 fixes. Same cast: GUY = `production-kit/student_ref.png`; CARD = `card_bodyguard.jpg` (the Veteran Bodyguard). NEW: GIRLFRIEND.

## The 6 changes
1. **Stutter fix — snap-card clip** ("writes you… writes you an advert"): regenerate clean.
2. **Stutter fix — typing clip** ("my citoria" = mangled "city, Pretoria"): regenerate clean.
3. **5T wording — corrected to HOLD → SPENT ON DELIVERY** (app rule: holds on request · burns on delivery · released on failure).
4. **Add** a save/forward-the-report beat.
5. **NEW hook** — guy + girlfriend.
6. **NEW payoff/exit** — list automatically → listing shown → logo.

---

## Final clip list & exact lines (for Flow, Omni Flash, 9:16, 8s unless noted)

### A · NEW HOOK (1 clip) — needs GIRLFRIEND still + card
Attach: girlfriend still + `card_bodyguard.jpg`.
Prompt: "The young man from the reference image (navy hoodie) sits on a couch holding a sleeved vintage trading card, beside his girlfriend. He looks at it, a bit stuck, and says: 'I've got this rare card I want to sell — but I don't even know how, or where.' She smiles and says: 'Try TrustSquare.' Warm light, handheld vlog feel, 9:16 vertical."

### B · LOGO STING — `production-kit/logo-sting-1.6s.mp4` (free)

### C · Walkthrough (regenerate the 2 glitched clips; keep the rest)
**C1 snap-card (REGEN, fixes #1):** attach `card_bodyguard.jpg`.
"The young man from the reference image holds up the Veteran Bodyguard card, then snaps a photo of it with his phone, talking to camera: 'Selling rare cards? Just snap them. AI checks real market prices, then writes your advert — done.' Clean delivery, no repeats. Warm light, vlog, 9:16."

**C2 typing (REGEN, fixes #2):**
"The young man from the reference image types on his phone, glancing at the card, then to camera: 'Next I type a short description of my card, my asking price, my city — Pretoria — and my currency, ZAR.' He says the words 'city' and 'Pretoria' clearly and separately. Warm light, vlog, 9:16."

### D · UI inserts (free, already built / to build)
- form-fill + Run press: existing `production-kit/inserts.py` output (Collectables).
- report scroll: existing.
- **NEW save/forward beat:** `01-collectables/inserts/insert-save-forward.mp4` (built this session).

### E · 5T beat (REGEN to corrected wording, fixes #3) — two short clips
**E1 press:** "He taps Run on his phone and says to camera: 'I press Run — that just holds 5 Tuppence, nothing's charged yet.' Confident, clear. Warm light, vlog, 9:16."
**E2 delivery:** "He looks at his phone, pleased: 'When my report's ready those 5 Tuppence are spent — and here's everything I get.' Then he turns the phone to camera. Warm light, vlog, 9:16."
> Note: this replaces the old "just reserves… nothing charged" + "once I accept the 5T from my wallet" lines so HOLD→SPENT is consistent. If keeping the old two clips (which are already roughly correct), only a light re-voice is needed — but a clean regen is simplest.

### F · Save/forward line (fixes #4) — short clip OR caption over the new insert
Spoken option (clip): "And I can save the report, or forward it to anyone — anytime."
(If saving credits, the built insert already shows this as a caption over the Save/Forward buttons — no clip needed.)

### G · NEW PAYOFF (fixes #6) — 2 clips + listing insert
**G1:** "The young man, eyes wide at his phone: 'Wow — it lets me list the card automatically!' He taps the screen once, decisive. Warm light, vlog, 9:16."
**Listing UI insert** (~6s, free, rebuild from app — content already transcribed in `scripts/01-collectables-advert.md`: R350, Trust Score 65, COLLECTORS, Join Queue 1T).
**G2:** "The young man turns his phone to camera, grinning: 'Look at that — listed. That's exactly how it looks.' Warm light, vlog, 9:16."

### H · LOGO STING out → app.

---

## GIRLFRIEND cast still (Flow image mode, 0 credits — generate first)
Prompt: "Photorealistic portrait, 9:16 vertical. A friendly young South African woman, early 20s, warm smile, casual jumper, sitting on a couch in a cosy warm-lit living room with a bookshelf behind her, looking toward someone beside her. Natural candid moment, shallow depth of field." → save to `production-kit/cast/girlfriend.png`, attach to clip A.

## Credit estimate
New video clips: A (hook), C1, C2, E1, E2, G1, G2 = 7 × ~15 ≈ **~105 credits** (+ retakes). Girlfriend still + listing/save inserts are free. Spans ~2-3 daily refreshes on the free tier, or one sitting on a paid plan.

## Stitch order (v2)
hook(A) → sting → C1 → form-insert → C2 → run-insert → E1 → E2 → report-insert → save-forward-insert(F) → G1 → listing-insert → G2 → sting.
