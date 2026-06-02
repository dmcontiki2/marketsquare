# Roadmap 1 — Home Page Redesign (First-Run)

**Date:** 2 June 2026 · **Author:** Layout/UX pass · **Stage:** PLANNING / DESIGN ONLY (no code touched)
**Builds on:** `DESIGN_CRITIQUE_2026-06-01.md` — whose headline finding is that the home screen *teaches the novel model at the paywall, not before*. This roadmap turns that finding into a concrete, implementable first-run redesign.
**Companion artifact:** `home_mockup.html` — a standalone static mockup of the proposed hero + first-run explainer card, using the live palette and fonts (Syne + Inter). Open it in a browser to see the target.

> **Scope discipline.** This is a redesign of the **`#screen-home` hero + the top of the home feed**, plus two cross-cutting fixes (type floor, emoji→icon, desktop frame). It is deliberately *not* a rewrite. Every change below is a surgical edit to `marketsquare.html` / `ms.css` and is sized to fit the project's "one feature per task" rule. Nothing here changes the Tuppence ledger, the API surface, or the demo/live wiring.

---

## 0 · The problem in one screen

Today `#screen-home` is:

```
[ TrustSquare (15px) ]            [ ZA / Pretoria badge ]   ← hero-top
[ empty .hero-body ]                                         ← sells nothing
Categories                                          All →
[ 3-col photo grid ] [ 🛍️ Local Market ] [ Featured ] [ 🌍 World Heritage ] [ For You ]
```

A first-time visitor meets a photo grid and never learns *what makes this marketplace different*. The three load-bearing concepts — **anonymous sellers**, an earned **trust score**, and a **non-refundable Tuppence introduction** — are introduced for the first time *at the moment money is spent*. That is the worst possible place to teach a novel mechanic: comprehension and the payment decision collide.

The fix is not more copy everywhere — it is **one confident hero that states the value prop and explains the model in 1–2 lines, plus a one-time dismissible explainer card, shown before the paywall.** Everything else on the home screen stays.

---

## 1 · Ranked changes (by impact)

| # | Change | Impact | Effort | File |
|---|---|---|---|---|
| **1** | **Hero states value prop + 1-line model explainer** | 🔴 Highest | S | `marketsquare.html` `.hero-body` + `ms.css` `.home-hero` |
| **2** | **One-time first-run explainer card** (anonymity → trust → Tuppence, 3 steps) | 🔴 Highest | M | `marketsquare.html` new block + small JS flag |
| **3** | **Lift the sub-12px type floor** (9–11px → 12–13px; widen primary↔secondary gap) | 🟠 High | S | `ms.css` (token-level) |
| **4** | **Emoji → inline SVG icons** (categories, Local Market, World Heritage, "For You" gear) | 🟡 Medium | M | `marketsquare.html` + `ms.css` |
| **5** | **Pleasant desktop frame** for the 430px column (branded backdrop + device shell) | 🟡 Medium | S | `ms.css` `@media (min-width:768px)` |
| **6** | **Hero wordmark + trust micro-proof** (15px → 22px Syne; add "23 verified sellers · Pretoria") | 🟢 Polish | S | `marketsquare.html` + `ms.css` |

S = under an hour · M = a focused session.

---

## 2 · Change 1 — A hero that sells (and explains)

### Before
```css
.home-hero{background:#111827;padding:36px 20px 10px;...}
.hero-logo{font-size:15px;font-weight:700;...}
.hero-body{}            /* EMPTY */
```
The hero is a thin dark strip with a small wordmark and an empty body. It establishes a mood but communicates nothing.

### After
A taller hero (still the same `#111827` navy, same overflow rules) carrying **three things in strict hierarchy**:

1. **Eyebrow** (overline): `LOCAL MARKETPLACE · PRETORIA` — 12px, Inter 600, letter-spacing 1.5px, white @ 70% (lifted from the current 45%/10px — see Change 3).
2. **Headline** (the value prop): **"Buy from trusted neighbours — without trading your privacy."** — Syne 800, 28–30px, white, `line-height:1.1`, `letter-spacing:-0.4px`. This is the single biggest element on the screen and the first thing the eye lands on.
3. **Sub / model line** (the explainer): *"Sellers stay anonymous and earn a **trust score**. Spend one **Tuppence** for a verified introduction when you find someone you like."* — Inter 400, 14px, white @ 60%, `line-height:1.5`, max 2 lines. The two product nouns (`trust score`, `Tuppence`) are weighted to 600 so the novel vocabulary is visually flagged on first sight.

### Rationale
- States *what* (buy from neighbours), *why it's different* (privacy / anonymity), and *the mechanic* (trust score + one-Tuppence introduction) **before** any category tap or paywall — directly answering the critique's #1 recommendation.
- Keeps the existing visual language: same navy band, same `z-index` layering, no new colours. It is a content + sizing change, not a restyle.
- The explainer line is the *teaser*; the full lesson lives in the one-time card (Change 2) so the hero never becomes a wall of text on repeat visits.

### Markup sketch (for `.hero-body`, currently empty)
```html
<div class="hero-body">
  <div class="hero-eyebrow">LOCAL MARKETPLACE · PRETORIA</div>
  <h1>Buy from trusted neighbours — without trading your privacy.</h1>
  <p>Sellers stay anonymous and earn a <b>trust score</b>. Spend one
     <b>Tuppence</b> for a verified introduction when you find someone you like.</p>
  <button class="hero-learn" onclick="openFirstRunExplainer()">How it works</button>
</div>
```
`.home-hero h1` and `.home-hero p` rules already exist in `ms.css` (30px/800 and 14px/55% respectively) — they just have nothing to style today. This change *uses* them and only nudges the eyebrow + adds the `.hero-learn` text-button.

---

## 3 · Change 2 — One-time first-run explainer card

A dismissible card shown **once** (gated on a `localStorage` flag, e.g. `ts_seen_intro`) directly under the hero on a visitor's first session, and re-openable any time via the hero's "How it works" button. Three numbered steps, each an icon + a 13–14px line:

| Step | Icon (SVG) | Copy |
|---|---|---|
| **1 · Browse anonymously** | eye-off / shield | Sellers list what they offer but stay private. No names, no spam, no contact details on display. |
| **2 · Read the trust score** | shield-check | Every seller earns a score from verified ID, credentials and successful introductions. Higher = more proven. |
| **3 · Spend a Tuppence to connect** | handshake / coin | When you find the right one, one Tuppence buys a verified introduction. **It's non-refundable — it's your signal that you're serious.** |

A primary **"Start browsing"** button dismisses it; a quiet **"Don't show again"** sets the flag.

### Rationale
- This is where the *full* model lesson lives, so the hero stays lean. It runs **before** the first paywall, defusing the collision the critique identified.
- The "non-refundable = serious signal" framing is stated **here, calmly, as a feature** — not first encountered as a scary line at the spend confirm. This aligns with the no-refunds rule (it's load-bearing for commitment-signal, Banks Act, and patent novelty) and with the existing 11 "non-refundable" strings; we are *teaching* it earlier, not weakening it.
- One-time + re-openable = no nag on repeat visits, but always recoverable. Matches the critique's "skippable first-run card" suggestion.

### Wiring note (project rule)
The card reads no API and no Tuppence balance — it is pure static content gated by `localStorage`. **No `DEMO_MODE` branch needed** (it makes no BEA call). The "How it works" button just toggles the card's visibility. Flag this explicitly in the implementing session so the demo-wiring audit is satisfied trivially.

---

## 4 · Change 3 — Lift the sub-12px type floor

The critique measured the scale as bottom-heavy: **13px ×76, 12px ×64, 11px ×58, 14px ×47, 10px ×44, 9px ×16**, plus stray 8px. Everything whispers; nothing leads. Concrete floor:

| Role | Today | Proposed | Where (examples) |
|---|---|---|---|
| Body / metadata | 9–11px | **13px** | `.cat-count` (9px), card meta, `#wf-empty-hint` (12px ok) |
| Secondary labels | 10px | **12px** | `.hero-eyebrow`, `.nb` bottom-nav (10px), `.cat-name` (11px → 12px) |
| Micro-labels (true overlines/badges only) | 8–9px | **11px floor** | `.tbadge` (9px), `.feat-badge` (8px), `.model-badge` (9px), `.paused-badge` (9px) |
| Primary text | 14–15px | **15–16px** | unchanged, but now clearly above secondary |
| Section headers | 15px | **16–17px** | `.sec-head h2` |

**Rule of thumb to adopt:** nothing that conveys *meaning* renders below 12px; **11px is the absolute floor and is reserved for genuine micro-labels** (uppercase overlines, status pills). Widen the gap between primary (15–16px) and secondary (12–13px) so hierarchy reads at a glance.

### Rationale
- Single biggest readability win on mobile and it restores hierarchy *for free* — no new components, just token nudges (critique rec #2).
- Most of these live in `ms.css` as single declarations, so this is a find-tune-verify pass, not a refactor. Keep the change isolated to size values; do not touch colours (contrast already clears AA per the critique).
- Watch item: a few dense rows (trust badges, feat badges) may need 1–2px more vertical padding once text grows — verify the category overlay and card footers don't clip after the bump.

---

## 5 · Change 4 — Emoji → inline SVG icons

Emoji used as iconography (🛍️ Local Market, 🌍 World Heritage, ⚙️ For-You gear, the flag/type emoji in the wonder selects) render inconsistently across OSes and clash with the otherwise refined Syne/Inter system.

| Location | Today | Proposed |
|---|---|---|
| Local Market home tile | `🛍️ Local Market` | inline `<svg>` storefront/tag glyph, `currentColor`, 18px, sitting left of the label |
| World Heritage header | `🌍 World Heritage` | inline `<svg>` globe glyph |
| "For You" settings | `⚙️` link | inline `<svg>` gear (also gets an `aria-label="Wishlist settings"`) |
| Explainer-card steps | — | the eye-off / shield-check / handshake SVGs from Change 2 |

Keep **country-flag emoji in the `<select>` options** — those are genuine flags, render acceptably, and swapping 50+ to SVG is out of scope. The fix targets *UI iconography only*.

### Rationale
- Restores visual consistency and removes the cross-platform rendering lottery (critique "minor, low-cost" item).
- Use a single tiny inline-SVG style (stroke, `currentColor`, 1.5–2px) so icons inherit text colour and stay crisp at any DPI — the app already uses this pattern (e.g. the cat-home back chevron, plan-feat checkmarks).
- Pair every icon-only control with an `aria-label` (the gear has none today) — also closes a small a11y gap.

---

## 6 · Change 5 — A pleasant desktop frame

Today `@media (min-width:768px)` just widens `body` from 430px → 900px and stretches a few bars. On a wide screen the app is "an un-optimised phone view floating in empty space." We **embrace mobile-first** (path (a) from the critique) rather than rebuild a multi-column layout:

- **Backdrop:** behind the column, a soft branded field — a subtle navy→bg vertical gradient or a very low-contrast geometric/topographic texture in `--accent-light`, so the gutter looks *intentional*.
- **Device shell:** wrap the 430px column in a faint card — `border-radius:24px`, a single soft shadow (reuse `--sh-md`), 1px `--border` — so it reads as a deliberate "app preview" frame, not a stranded mobile page.
- **Keep it at 430px on desktop** (revert the 900px body widen for the home/feed surfaces, or cap the *frame* at ~430 and let the backdrop fill the rest). The 900px widen currently distorts the carefully-tuned mobile column.
- Optional, cheap: a slim left-aligned wordmark + one-line tagline in the desktop gutter beside the frame, so a desktop first impression also carries the value prop.

### Rationale
- Lowest-effort path to a credible desktop first impression — pure CSS in the existing media query, no new layout system, no risk to mobile (critique "both viewports" section).
- A framed column signals "designed for your phone" rather than "broken on desktop," which on a trust-led product matters for credibility.
- Watch item: ensure fixed-position bars (`.bnav`, `.sticky-cta`, `.cv-sticky`, `.pub-footer`) align to the *framed column*, not the 900px width — they currently re-pin to `max-width:900px` in the desktop query.

---

## 7 · Change 6 — Wordmark + trust micro-proof

Small but high-leverage on a trust product:

- **Wordmark:** `.hero-logo` 15px/700 → **20–22px Syne 800**. It's the one moment that should establish identity; 15px undersells it (critique first-impression note).
- **Micro-proof line** under or beside the city badge: e.g. **"23 verified sellers in Pretoria"** (Inter 600, 12px, white @ 70%). Turns the abstract "trusted" claim into a concrete number on first sight. (Pull from live count where available; in DEMO mode show the seeded count — this *does* read data, so gate it: `if (DEMO_MODE) {...seeded count...} else {...GET count...}`.)

### Rationale
- Cheap credibility: a real number ("23 verified sellers") does more for first-run trust than another adjective.
- The wordmark bump costs one CSS value and fixes the "identity moment is undersized" finding.

---

## 8 · Proposed first-run home, end state

```
┌──────────────────────────────────────────────┐  ← desktop: framed 430px column on branded backdrop
│  TrustSquare (22px)            ZA / Pretoria   │
│  23 verified sellers in Pretoria               │
│                                                │
│  LOCAL MARKETPLACE · PRETORIA                  │  ← 12px eyebrow @70%
│  Buy from trusted neighbours —                 │  ← 28px Syne 800 (value prop)
│  without trading your privacy.                 │
│  Sellers stay anonymous and earn a trust       │  ← 14px @60% (model line)
│  score. Spend one Tuppence for a verified      │
│  introduction.                  [How it works] │
├──────────────────────────────────────────────┤
│  ┌── How TrustSquare works ─────────  ✕ ──┐   │  ← one-time card (first session only)
│  │ ◉ 1  Browse anonymously                 │   │
│  │ ◉ 2  Read the trust score               │   │
│  │ ◉ 3  Spend a Tuppence to connect        │   │
│  │              [ Start browsing ]          │   │
│  └──────────────────────────────────────────┘  │
├──────────────────────────────────────────────┤
│  Categories                            All →   │  ← unchanged below here
│  [ Property ][ Tutors ][ Services ] …          │  ← cat-count lifted 9px→13px, names 11px→12px
│  [ ▦ Local Market ]   (SVG icon, not 🛍️)       │
│  Featured  ‹ … ›                               │
│  ▦ World Heritage   (SVG globe, not 🌍)        │
│  For You                              ⚙(SVG)   │
└──────────────────────────────────────────────┘
```

---

## 9 · Sequencing & guardrails

**Suggested order (each is a standalone task, smoke-test between):**
1. **Change 3 (type floor)** first — it's token-level, touches everything, and de-risks the visual sizing for all later changes.
2. **Change 1 (hero copy/hierarchy)** — uses the now-correct type scale.
3. **Change 2 (explainer card)** — depends on the hero "How it works" hook.
4. **Change 4 (emoji→icon)** + **Change 6 (wordmark/proof)** — cosmetic, bundle if desired.
5. **Change 5 (desktop frame)** — isolated CSS, last.

**Guardrails (from CLAUDE.md):**
- HTML edits to `marketsquare.html` use the **Python string-replace driver**, never Write/Edit (the file truncates). Verify the `</html>` tail after every write.
- Any data-reading addition (the "23 verified sellers" count in Change 6) **must carry a `DEMO_MODE` branch**; the explainer card and hero copy read no data and need none — state this in the session note so the demo audit passes.
- No ledger / API / pricing impact in any change here → **no `Cost model impact:` line** needed in CHANGELOG.
- Don't touch colour tokens; contrast already clears AA. This pass is sizing, copy, icons, and one frame.

**What this roadmap deliberately does NOT do:** rebuild the feed, add a multi-column desktop layout, restyle the category grid imagery, or change the spend-confirm flow. Those are separate, lower-priority items; the win here is *first-run comprehension*, achieved with surgical edits.

---

*Companion mockup: `home_mockup.html` (open in browser). Palette/fonts match live (`ms.css` v115 tokens, Syne + Inter via Google Fonts). Mockup is illustrative — final copy/counts come from live data and the Codex.*
