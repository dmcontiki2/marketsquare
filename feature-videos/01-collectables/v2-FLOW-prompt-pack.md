# Collectables Advert v2 — Flow Prompt Pack

**Canonical script:** `v2-REVISION-script.md` · **Walkthrough decision:** splice (regen snap + typing only, keep the rest of the 55s) · **Card:** `card_bodyguard.jpg` (source: `C:\Users\David\OneDrive\Pictures\Iphone photos`, being staged into `production-kit/cast/`).

## Global Flow settings (from the production kit)
- Video → Ingredients → **9:16 → 1× → Omni Flash → 8s** (unless noted).
- **Attach `student_ref.png` as an ingredient to EVERY presenter clip** — keeps the same face/room.
- Character line if needed: *"The same young man from the reference image — same face, short brown hair, navy hoodie, same warm room with bookshelf."*
- One spoken sentence per clip, ≤ ~22 words. The model voices whatever is inside the quotes.
- Cost: 8s ≈ 12 cr · 6s ≈ 10 · 4s ≈ 7 (mid-2026 promo). Free tier ≈ 50/day.
- **Negative / avoid:** no brand logos, no Pokémon or trademarked card art, no gibberish text on screens.

---

## STEP 0 — Girlfriend cast still (Flow **image** mode, 0 credits — do this first)
> "Photorealistic portrait, 9:16 vertical. A friendly young South African woman, early 20s, warm smile, casual jumper, sitting on a couch in a cosy warm-lit living room with a bookshelf behind her, looking toward someone beside her. Natural candid moment, shallow depth of field."

→ Save as `production-kit/cast/girlfriend.png`. Attach to Clip A.

---

## Clip A — NEW HOOK (8s) · attach `girlfriend.png` + `card_bodyguard.jpg`
> "The young man from the reference image (navy hoodie) sits on a couch holding a sleeved vintage trading card, beside his girlfriend. He looks at it, a bit stuck, and says: 'I've got this rare card I want to sell — but I don't even know how, or where.' She smiles and says: 'Try TrustSquare.' Warm light, handheld vlog feel, 9:16 vertical."

## Clip C1 — SNAP, REGEN (fix #1) · attach `card_bodyguard.jpg`
> "The young man from the reference image holds up the Veteran Bodyguard card, then snaps a photo of it with his phone, talking to camera: 'Selling rare cards? Just snap them. AI checks real market prices, then writes your advert — done.' Clean delivery, no repeats. Warm light, vlog, 9:16."

## Clip C2 — TYPING, REGEN (fix #2)
> "The young man from the reference image types on his phone, glancing at the card, then to camera: 'Next I type a short description of my card, my asking price, my city — Pretoria — and my currency, ZAR.' He says the words 'city' and 'Pretoria' clearly and separately. Warm light, vlog, 9:16."

## Clip E1 — 5T PRESS, REGEN to corrected wording (fix #3) · *optional — I can revoice the existing segment instead*
> "He taps Run on his phone and says to camera: 'I press Run — that just holds 5 Tuppence, nothing's charged yet.' Confident, clear. Warm light, vlog, 9:16."

## Clip E2 — 5T DELIVERY (fix #3) · *optional — see E1 note*
> "He looks at his phone, pleased: 'When my report's ready those 5 Tuppence are spent — and here's everything I get.' Then he turns the phone to camera. Warm light, vlog, 9:16."

## Clip G1 — NEW PAYOFF (fix #6)
> "The young man, eyes wide at his phone: 'Wow — it lets me list the card automatically!' He taps the screen once, decisive. Warm light, vlog, 9:16."

## Clip G2 — NEW PAYOFF (fix #6)
> "The young man turns his phone to camera, grinning: 'Look at that — listed. That's exactly how it looks.' Warm light, vlog, 9:16."

*(Optional save/forward spoken line, only if we don't use the caption insert: "And I can save the report, or forward it to anyone — anytime.")*

---

## Generation order & credit estimate
girlfriend still (0) → A (12) → C1 (12) → C2 (12) → G1 (10) → G2 (10) **≈ 56 cr core** · + E1/E2 (≈ 20) only if generating rather than revoicing · + retakes. Roughly one paid sitting or ~2 free daily refreshes.

## Inserts (I build — 0 Flow credits)
- form-fill + Run press — existing `production-kit/inserts.py` output (Collectables).
- report scroll — **rebuilt to Veteran Bodyguard / R350** (continuity fix).
- save/forward — already built (`inserts/insert-save-forward.mp4`).
- listing screen — to build (Bodyguard · R350 · Trust 65 · COLLECTORS · Join Queue 1T).

## v2 stitch order
A (hook) → logo-sting → C1 → form-insert → C2 → run-insert → E1 → E2 → report-insert (R350) → save-forward-insert → G1 → listing-insert → G2 → logo-sting.

*Splice note:* the walkthrough body (form/run narration steps) is reused from the existing 55s tutor; only C1 and C2 are regenerated and cut in over the two glitched moments, and the 5T wording is corrected (regen E1/E2 or revoice).
