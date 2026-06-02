# Design Critique: TrustSquare (trustsquare.co)

**Date:** 1 June 2026 · **Stage:** live (BEA v1.3.1) · **Surfaces:** buyer marketplace (FEA) + admin/seller onboarding · **Viewports:** mobile + desktop
**Focus (requested):** first impression · usability & flows · visual hierarchy · accessibility · trust & anonymity cues

> **Method note.** Live Chrome/headless screenshots were blocked this session (extension offline + sandbox network throttling on the browser download). This critique is therefore grounded in the *live source* — `marketsquare.html`, `ms.css` (v115), `ms.js` (v129), `marketsquare_admin.html` — which makes the accessibility findings exact (measured hex/px values, computed contrast) but limits the holistic "visual feel" of real photos and spacing in motion. I can run a screenshot pass for those once Chrome reconnects.

---

## Overall impression

The bones are good. There's a disciplined token system — a tight palette, consistent 10/6px radii, two restrained shadows, and a clean Syne (display) + Inter (body) pairing — and the product's whole thesis (anonymous sellers, *trust score*, *Tuppence* introductions) is surfaced relentlessly and consistently. Real `<button>` elements give baseline keyboard support, and the admin onboarding wizard is genuinely clear.

The biggest opportunity is **first-run comprehension**: the home screen jumps straight into category browsing and never explains the novel model, so the first "spend 1 Tuppence to reveal a seller" moment arrives unscaffolded. The second theme is **density** — the type scale leans heavily on 9–12px text, which makes a mobile-first UI feel busy and flattens hierarchy. Both are fixable without touching the architecture.

---

## Priority recommendations (ranked)

1. **Teach the model on first run — highest impact.** The hero (`#screen-home`) has an empty `.hero-body` and goes straight to a category grid. For a novel mechanic (anonymous trusted sellers + a non-refundable introduction currency), add a concise value proposition and a 1–2 line explainer of *anonymity → trust score → Tuppence introduction* in or above the hero, or a skippable first-run card. Without it, users meet the vocabulary for the first time *at the paywall*.
2. **Lift the type floor.** 9–11px text is pervasive (see evidence below). Move metadata up to 12–13px, reserve 11px for true micro-labels, and widen the size gap between primary (16–18px) and secondary text. Single biggest readability win on mobile, and it restores hierarchy for free.
3. **Restore a visible focus indicator.** `outline:none` appears 10× and focus is otherwise only a subtle `border-color` change; there's no `:focus-visible` ring, and JS-rendered controls have no focus style at all. Add a global 2px accent focus ring. Cheap fix for a real WCAG 2.4.7 keyboard failure.
4. **Announce dynamic changes to screen readers.** There are zero `aria-live` regions across all four files. The Tuppence balance, async listing loads, and toast/error messages are silent to assistive tech. Add `aria-live="polite"` to the balance + a global status region, `assertive` for errors.
5. **Fix document structure + admin labelling.** 31 `<h1>` (≈ one per screen) and no `<header>/<main>/<footer>/<section>` landmarks; the admin file has 0 `alt`, 0 `aria-label`, 0 `role`. One `<h1>` per screen wrapped in `<main>`/`<section>`, plus alt text on admin listing images and labels on icon-only controls.

Minor, low-cost: swap emoji category icons (🛍️) for the icon set; guarantee a consistent scrim under text-on-photo tiles; keep amber `#fbbf24` text on dark backgrounds only.

---

## Buyer marketplace (FEA)

### First impression
The home hero is a dark navy (`#111827`) band with the **"TrustSquare" wordmark at only 15px/700** — undersized for the one moment that should establish identity and trust. A 10px uppercase eyebrow sits at 45% white (4.48:1 — borderline), the city badge (South Africa / Pretoria) sits top-right, then the screen immediately becomes a 3-column category image grid, a full-width "🛍️ Local Market" tile, a featured horizontal scroll, and a World Heritage "wonders" strip.

It's attractive but it *sells nothing* — `.hero-body` is empty and there's no tagline or concept explainer. The eye lands on photo tiles, which is fine for a known marketplace but wrong for a novel one. Emoji used as category iconography also clashes with the otherwise refined type system and renders inconsistently across platforms.

### Usability & flows
The core path is browse → listing → **Request Introduction** (costs 1 Tuppence) → **Reveal** seller ("reveal" appears 46×). Observations:

| Finding | Severity | Recommendation |
|---|---|---|
| Novel value-exchange (non-refundable spend to unlock a contact) arrives with no prior education | 🔴 Critical | Front-load a one-time explainer; at the spend moment, state plainly *what you get* for 1 Tuppence and that it's non-refundable (11 "non-refundable" strings already exist — good; make the pre-spend confirm unmissable) |
| 209 real `<button>` elements (not div-onclick) | 🟢 Works | Keep — this is the right baseline |
| 28 screens via class-toggle, only one `<nav>`; no persistent landmark nav found in markup | 🟡 Moderate | Confirm the primary/bottom nav is persistent and obvious on every screen |
| "How introductions work" recently reworked into a compact picker (Session 104) | 🟢 Works | Good direction — extend that clarity to first-run |

### Visual hierarchy
The type scale is bottom-heavy. Most-used sizes by declaration count: **13px ×76, 12px ×64, 11px ×58, 14px ×47, 10px ×44, 9px ×16** (plus a couple of 8px). Display sizes (22–80px) exist but are rare. Net effect: lots of small secondary text all competing at similar weight — everything whispers, nothing leads. Pill CTAs in Syne 700/800 do punch well, and elevation/shadow restraint is good. Lifting the floor (rec #2) is the fix.

### Accessibility (measured)
Color discipline is genuinely strong — core text and every semantic badge pair clear AA, and the lightest gray is correctly kept off text:

| Foreground on background | Ratio | Verdict |
|---|---|---|
| text `#111827` on bg `#f4f5f7` | 16.3:1 | ✅ |
| text-2 `#4b5563` on white | 7.6:1 | ✅ |
| text-3 `#555f6e` on white | 6.5:1 | ✅ |
| gold `#92400e` on gold-bg `#fef3c7` | 6.4:1 | ✅ |
| green `#065f46` on green-bg `#d1fae5` | 6.8:1 | ✅ |
| blue `#1d4ed8` on blue-bg `#dbeafe` | 5.5:1 | ✅ |
| white on accent navy `#1e3a5f` | 11.5:1 | ✅ |
| `#9ca3af` — used only for borders/backgrounds, never text | 2.5:1 as text | ✅ (correctly avoided) |
| hero eyebrow white @45% on navy (10px) | 4.48:1 | ⚠️ borderline |
| amber `#fbbf24` as text on white | 1.67:1 | ❌ keep on dark only (10.6:1 on navy ✅) |
| category name (white) over photo | image-dependent | ⚠️ needs guaranteed scrim |

Beyond color, the real gaps: **sub-12px text everywhere** (readability), **no visible focus** (`outline:none` ×10, no `:focus-visible`), **no `aria-live`** (dynamic content silent to SR), **31 `<h1>` + no landmarks**, and **emoji-as-icon**. Wins worth keeping: listing images carry `alt` (22 in ms.js), and the viewport meta allows pinch-zoom (no `maximum-scale` lock).

### Trust & anonymity cues
This is the product's entire thesis and it *is* front-and-centre: `tuppence` 316×, `introduction` 254×, `trust score` 136×, `anonymity/anonymous` 69×, `verified` 41×. Trust score is earned via credentials + verified ID + successful introductions, shown as a badge ("New" for new sellers). Strength: trust is a first-class, repeated signal. Opportunity: because the vocabulary is novel, the *meaning* of the badge and the *why* of anonymity should be taught on the home screen, not inferred — and the trust score/badge must not be carried at 9–10px where it's hard to read.

---

## Admin / seller onboarding

### First impression & flow
Refreshingly conventional and clear: a **4-step wizard** with plain-language titles — *"Who is the seller? → What are they selling? → Add listings → Review & save draft"* — each with a "Step N of 4" eyebrow and an eyebrow/title/sub hierarchy. Low ambiguity, sequential, with review-before-commit. This is the strongest-structured surface of the two.

### Accessibility
The admin file has **0 `aria-label`, 0 `role`, 0 `alt`, 0 `tabindex`** (it does carry 9 `:focus` rules — marginally better focus handling than the buyer app). Lower-stakes as an internal tool, but seller-uploaded listing images with no alt and unlabelled icon controls are still worth fixing — admins may themselves rely on assistive tech. The trust-data capture is well-labelled ("Private docs used for Trust Score verification", "Visible after intro" toggle).

---

## Both viewports

The app shell is `body { max-width: 430px; margin: 0 auto }` with a **single** media query (`min-width: 768px`). So there is effectively **no desktop layout** — on a wide screen the whole app is a 430px phone-width column centred on the page gutter. That's a defensible mobile-first call, but it means the desktop *first impression* is "an un-optimised phone view floating in empty space." Two paths: (a) embrace it — give desktop a pleasant branded frame/backdrop around the column; or (b) build a true multi-column layout for the highest-traffic screens (listing grid, home). At minimum, make sure what sits *beside* the 430px column on desktop looks intentional.

---

## What works well

- Disciplined design tokens — tight palette, consistent radii/shadows, restrained two-font pairing. The system is coherent.
- Strong colour-contrast discipline: lightest gray kept off text; every semantic badge pair clears AA.
- Real `<button>` elements → keyboard operability by default.
- Trust / anonymity / Tuppence concepts surfaced consistently and often.
- Admin onboarding wizard is clear, sequential, and review-gated.
- Evidence of active refinement (compact "how intros work", transaction filters, refund mechanism removed in recent sessions).

---

*Critique grounded in live source (ms.css v115 · ms.js v129 · marketsquare.html · marketsquare_admin.html). Offer: a live mobile + desktop screenshot pass to confirm the visual-feel items (hero balance, photo scrims, desktop gutter) once the Chrome extension is back.*
