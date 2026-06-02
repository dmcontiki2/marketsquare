# ROADMAP #6 — TrustSquare Outreach Email Overhaul

**Author:** Lifecycle-email design + copy pass
**Date:** 2026-06-02
**Status:** PLANNING + 1 refreshed draft (`property_outreach_v2.html`). Nothing sent, deployed, or committed.
**Scope:** 9 templates in `n8n/email_templates/` — 7 `*_outreach` (cold seller acquisition) + 2 lifecycle (`intro_accepted`, `intro_declined`).

> **DEPENDENCY — READ FIRST.** These emails are the brand's first impression and must mirror the live app. They therefore **inherit the home-page design direction from Roadmap #1 (home-page redesign).** Do not mass-produce the other 8 templates until #1 locks the refreshed palette, type scale, hero treatment, and the canonical listing-card / trust-badge look. The single `property_outreach_v2.html` draft in this batch is built against the **current** `ms.css` tokens so it is shippable today and doubles as the reference skin once #1 is signed off. If #1 changes a token, only the shared header block (below) needs re-touching, not nine bespoke layouts.

---

## A · Audit — 9 templates vs. current branding & product model

### A.1 The headline problem: the emails predate the rebrand and the current design system
All seven `*_outreach` templates are dated April and were written **before** the `trustsquare.co` rebrand and before the current `ms.css` design system existed. They are internally consistent with each other but **diverged from the live app**. Concretely:

| Dimension | Emails (April) | Live app (`ms.css` / `ms.js`, Jun 2026) | Verdict |
|---|---|---|---|
| Primary navy | `#1a1a2e` (indigo-black) | `--navy:#111827` (true slate-black) | **Drift** — warmer/bluer than current |
| Action / accent | `#d4a853` warm gold on **everything** (CTA buttons, headers, prices) | `--accent:#1e3a5f` steel-blue is the primary action colour; CTA buttons in-app are `var(--accent)` blue, **not** gold | **Wrong** — gold is now a *tier* signal, not the brand action colour |
| Gold's real role | Generic brand colour | Reserved: `--gold:#92400e`/bg `#fef3c7` = **Highly Trusted** badge tier + dark-hero eyebrow (`rgba(200,135,58)`) only | **Misused** — over-applied gold cheapens the "Highly Trusted" signal |
| Fonts | System stack only (`-apple-system…`) | **Syne** 700/800 (headings) + **Inter** 300–700 (body), loaded from Google Fonts | **Missing** — no brand type at all |
| Trust badge | Hand-coded chips: "✓ Trusted", "★ Established", "⭐ Highly Trusted" with **ad-hoc colours** (`#2a7a2a`, `#2a4aaa`, `#8a6000`) and inconsistent label↔colour mapping | Single source of truth `trustTier(s)` → `tbadge(s)` renders `★ {score}` with fixed tiers (see C.2) | **Inconsistent** — labels, colours, and the score-number convention don't match the app |
| Card chrome | "Phone mockup" (notch bar, `9:41 ●●●●○ WiFi` status bar) | Real cards are flat `.lcard` tiles, no phone frame | **Dated** — skeuomorphic phone frame is 2019-era; app itself doesn't show one |
| CTA verb | "Request Introduction · 1T" (correct concept) | In-app primary is "Request Introduction" + cost pill | **OK concept**, wrong colour token |

### A.2 What's actually GOOD and must be preserved
The April templates are not a teardown job. Keep:
- **The send-gated, magic-link flow.** `?magic=…` → personalised pre-filled draft → "you sign on when you accept your listing." This matches the live onboarding funnel (`#screen-guided-onboard`) and the "account created at accept" rule. Do not touch the mechanic.
- **The "no commission / pay-to-introduce filters tyre-kickers / you stay anonymous until you accept" three-pillar argument.** It is on-model and Codex-aligned.
- **The "✏️ A quick draft for {{first_name}}" personalised-card block.** This is the single strongest conversion device in the set — it shows the prospect their *own* listing already half-built. Keep it; just reskin it to the real card.
- **Per-vertical hero gradients** (property=navy/blue, collectors=oxblood, adventures=green, accommodation=amber, services=steel, tutors=teal). A vertical accent stripe is fine **as long as** the brand navy + the real CTA colour + the real trust badge stay consistent across all of them. Vertical colour = flavour; brand colour = constant.
- **POPIA-adjacent footer honesty** ("you're receiving this because your … appears in {{city}}'s public records") + unsubscribe. Legally load-bearing for cold B2B outreach. Keep and standardise wording.

### A.3 Product-model accuracy check (against CLAUDE.md + memory)
- ✅ **Tuppence = USD $2, 1T per accepted introduction, charged on accept only.** `intro_declined` correctly states "No Tuppence was charged." Consistent with the no-refunds rule (memory: Tuppence non-refundable) — keep that framing; never imply refundability anywhere.
- ✅ **AI Listing Coach = "1 Tuppence for 8 coaching sessions."** Consistent across templates. Leave the pricing as a variable-friendly phrase so a cost-model change is a one-string edit, not a nine-file hunt.
- ⚠️ **"USD $2" hard-coded.** Fine for now, but flag: if the cost model changes the Tuppence price, every outreach template needs it. **Recommendation:** template it as `{{intro_fee_display}}` (default "1 Tuppence (~USD $2)") in v2 so n8n injects one value. (Not done in this draft beyond the property file — noted as a batch task.)
- ⚠️ **Legal entity / footer.** The two *lifecycle* emails already carry the correct full footer: `Trustsquare (Pty) Ltd · Reg 2026/340128/07 · Pretoria, South Africa`. The seven *outreach* emails carry only "TrustSquare · trustsquare.co". **Standardise all nine on the lifecycle footer** (reg number is required for commercial email; matches memory's legal-entity record).
- ⚠️ **Launch city.** Templates are `{{city_name}}`-driven (good, geo-portable per scale-shape invariant #5). Current launch city is **Pretoria** — sample suburbs in mockups (Waterkloof, Centurion, Pretoria East) are correct. Keep city as a variable; never hard-code.

### A.4 Per-template one-liners
1. **property_outreach.html** — Strongest of the set. Reskin to current tokens (done → v2). Reference template for the batch.
2. **collectors_outreach.html** — Oxblood hero is striking; "POA/ENF/Firm" price tags are a nice collector-authentic touch — preserve. Highest-value vertical → lean hardest into discretion + the Highly-Trusted (gold) badge here.
3. **adventures_experiences_outreach.html** — Good "ready to book" angle. Update FGASA/PADI credential chips to real trust-badge component.
4. **adventures_accommodation_outreach.html** — The OTA-commission maths callout ("Airbnb takes ~R460…") is the best single persuasion block in the whole set. Keep verbatim, reskin frame.
5. **services_technical_outreach.html** — Call-out-fee + hourly-rate split is correct and useful. Keep.
6. **services_casuals_outreach.html** — (not re-read in full; same family) — align to Casuals = Queue model badge (`👥 Queue`) vs Technical = Commit, per `ms.js` model-badge logic. Flag for the batch.
7. **tutors_outreach.html** — "online or in-person" + subject list good. Reskin.
8. **intro_accepted.html** — Already on rebrand footer + correct Tuppence-deduct copy. Lightest touch: swap gold CTA→accent-blue, add Syne/Inter, embed the real accepted-listing card (live visual) instead of the plain text `.listing-card` strip.
9. **intro_declined.html** — Already empathetic + "no charge" correct. Same light touch: type + colour + show 2–3 *alternative* live cards in the same category (re-engagement) instead of a flat tip list.

---

## B · Embedding LIVE APP VISUALS inside the emails

David's ask: *"the app's visual pages inside the email."* The strategy is to render **faithful, hand-built HTML/table reproductions** of three app surfaces — not screenshots, not the live DOM (email clients run no JS and won't load the SPA). Each is a static, inline-styled twin of the real component, so the inbox looks like the app.

### B.1 Three reusable visual blocks
1. **Listing card** (`.lcard` twin) — image (or emoji/solid fallback), category eyebrow, title, `📍 area`, price (`formatZAR`-style "R 3,200,000"), and the **real trust badge** `★ {score}` in tier colour. This is the hero visual in `property_outreach_v2.html`.
2. **Trust badge** (`tbadge` twin) — standalone, reused inside the card and callable on its own in lifecycle emails. Exact tier mapping in C.2.
3. **Marketplace strip** — a horizontal row of 3 mini listing cards = the "Other listings in {{city}}" social-proof band. Replaces the dated phone-mockup frames with flat cards that match the live `.lgrid`.

### B.2 Render-faithfully rules
- **Build from the component source, not by eye.** Colours, the `★ {score}` convention, tier thresholds, and the "Request Introduction · 1T" CTA come straight from `ms.js` (`trustTier`, `tbadge`, the `.lcard` template at ms.js:2339). When #1 restyles the card, update these twins from the same source in lockstep.
- **Tables + inline CSS only** (see D). No flex/grid in the visual blocks — Outlook ignores them. The marketplace strip is a single `<tr>` of `<td width="33%">` cells.
- **Image with graceful fallback (3 layers):**
  1. Real photo via `background-image` **and** an `<img>` with `alt`.
  2. If images are off/blocked: a solid `bgcolor` (the category colour) carries the card so text + badge still read.
  3. `alt` text states the listing ("4-bed family home, Pretoria East") so screen-readers + image-off inboxes still get the offer.
- **Personalised card uses the prospect's own data** (`{{prospect_listing_title}}`, `{{prospect_suburb}}`) on a "New Seller" badge (score shown as the New/grey tier, since a brand-new seller starts pre-trust). The 3-up strip uses generic-but-realistic neighbours with varied tiers (Established/Trusted/Highly Trusted) to show the ladder a seller can climb.
- **No phone frame.** Drop the notch + `9:41 WiFi` chrome. Show the flat card exactly as the app renders it. (This is the single biggest "looks like 2025 not 2019" upgrade.)

### B.3 Image hosting
Mockup photos currently hot-link Unsplash with sizing params — fine for deliverability (HTTPS, cached). **Scale-shape invariant #4 (media is a URL):** keep all email imagery as hosted URLs (R2/Cloudflare or Unsplash), never inline base64 (bloats the email, trips spam filters). When real listing photos exist, point the strip at R2 URLs.

---

## C · Authoritative design tokens (the shared "email skin")

> Build one shared header/footer/badge partial; every vertical imports it. This is what makes #1's output a one-place change.

### C.1 Palette (from `ms.css :root`, current)
```
--navy     #111827   header bar, footer-on-dark, hero base
--accent   #1e3a5f   PRIMARY ACTION (CTA buttons, links, card CTA) — steel blue, NOT gold
--bg       #f4f5f7   email body background
--surface  #ffffff   card / wrapper background
--border   #e2e5ea   hairlines
--text     #111827 / --text-2 #4b5563 / --text-3 #555f6e
Eyebrow/dark-hero gold accent: rgba(200,135,58,.85)  (#C8873A) — sparingly, on dark only
```
Per-vertical hero gradient stays as flavour, but the **CTA button is always `--accent` blue** and the **header bar is always `--navy`**, across all nine.

### C.2 Trust badge — single source of truth (`trustTier` @ ms.js:815)
Render as `★ {score}` in a rounded chip, `background:{bg}; color:{c}`:

| Score | Label | Text colour | Chip bg |
|---|---|---|---|
| `< 40` | New | `#6b7280` (grey) | `#f3f4f6` |
| `40–69` | Established | `--blue #1d4ed8` | `--blue-bg #dbeafe` |
| `70–89` | Trusted | `--green #065f46` | `--green-bg #d1fae5` |
| `≥ 90` | Highly Trusted | `--gold #92400e` | `--gold-bg #fef3c7` |

(Note: `ms.js` has a *second* tier function ~line 6330 using `#16a34a`/`#2563eb`/`#C8873A` for a different surface. For the **card badge twin**, use the `tbadge()` CSS-var set above — that is what renders on `.lcard`.) Emails must hard-code the hex (no CSS vars in email) but the values come from here.

### C.3 Type
- Headings: `'Syne', sans-serif` 700/800. Body: `'Inter', sans-serif`.
- Load via `<link>` in `<head>` **and** name them in a `font-family` stack with a system fallback (`'Syne', 'Segoe UI', Arial, sans-serif`) — many clients ignore web fonts; the fallback must look intentional.

---

## D · Email-client-safe constraints (hard rules for the batch)

1. **Table-based layout.** Outer 600px `<table>` wrapper; all multi-column rows (the 3-up strip, feature lists) are `<table><tr><td>`. No CSS `display:flex` / `grid` for structural layout — Outlook (Word engine) drops them. (The current April templates already do this for the mockups; extend it to the feature rows that currently use `display:flex`.)
2. **Inline CSS on every element.** A `<style>` block in `<head>` is fine for progressive enhancement (and the `.class` styles the April files use will work in most modern clients), **but** every visually-critical rule (bg colour, padding, font, the badge colours) must **also** be inline so it survives Gmail/Outlook stripping `<head>`. The visual blocks (B.1) are already fully inline — keep that discipline.
3. **No JavaScript, no `<form>`, no external CSS file.** CTAs are bulletproof `<a>` buttons (padded `<a>` with bg colour; for Outlook robustness, a VML roundrect comment is optional but recommended for the primary CTA).
4. **No web-font dependency for legibility.** See C.3 — always a system fallback.
5. **Dark-mode fallback.**
   - Don't rely on pure-white card backgrounds being preserved — some clients invert. Give cards an explicit `bgcolor="#ffffff"` on the `<td>` (attribute, not just CSS) so inversion is predictable.
   - Avoid pure-black text on transparent; use the explicit `--text` hex so dark-mode auto-contrast behaves.
   - The navy header (`#111827`) already reads in both modes — keep dark UI elements genuinely dark so they don't get force-lightened oddly.
6. **Image-off fallback (B.2).** Every image has `alt`; every image-bearing cell has a solid `bgcolor` underneath; the offer never depends on an image loading. CTA is never an image.
7. **Width + mobile.** 600px max wrapper; single-column body; the 3-up strip uses `width="33%"` cells that gracefully narrow. `<meta name="viewport">` present. Min tap target 44px on the CTA.
8. **Preheader.** Add a hidden preheader span (first ~90 chars shown in inbox preview) — currently missing on all nine. e.g. *"No commission, ever. List anonymously in {{city_name}} — buyers pay to reach you."*
9. **Plain-text part.** n8n should send a `text/plain` alternative (deliverability + accessibility). Note for the n8n workflow owner; not an HTML concern.
10. **Spam-hygiene.** Real reg-number footer, working unsubscribe, no all-caps subject, balanced text:image ratio (the flat-card strip is mostly live HTML text, which helps).

---

## E · Agent-targeted messaging angles — the three priority verticals

The cold-outreach insight: we are emailing **professionals who already do this for a living** (estate agents, travel agents, collection dealers). The generic "list your stuff" framing under-sells. Each needs a tailored wedge that respects their existing business and positions TrustSquare as *additional, commission-free, anonymous demand* — not a replacement for their livelihood.

### E.1 Estate agents (→ `property_outreach_v2.html`, this batch)
- **Wedge:** "A second pipeline that costs you nothing per deal." Agents live on commission; lead-gen portals (Property24, Private Property) charge listing fees and flood them with tyre-kickers. TrustSquare flips it: **buyers pay to reach you**, you stay anonymous until you accept, and **TrustSquare never takes a cut of the sale or rental** — only the buyer's intro fee.
- **Reframe anonymity for a pro:** not "hide your identity" (an agent *wants* to be known) but **"qualify before you reveal"** — you don't burn your number on a casual browser; the intro fee pre-filters. Anonymity = lead-quality filter, not secrecy.
- **Proof device:** the embedded live listing card showing a Pretoria property with a **Trusted/Highly-Trusted** badge — signals "this is where serious buyers already are."
- **CTA:** "List a Property in {{city_name}}" — and note an agent can list **multiple** properties (their whole roll), each a separate magic-link listing.
- **Tone:** peer-to-peer, commercially literate, ROI-first. Avoid consumer hand-holding.

### E.2 Travel agents (→ batch; touches `adventures_experiences` + `adventures_accommodation`)
- **Wedge:** "Direct bookings, zero OTA commission." Travel agents and the operators they represent bleed 15–25% to Booking.com / Airbnb / Viator. TrustSquare = **commission-free direct demand**; the agent keeps the full margin and the client relationship.
- **Reframe:** for an agent who packages experiences/stays, TrustSquare is a **commission-free distribution channel** they can list their portfolio on — each experience or property a listing, each enquiry pre-paid and serious (no time-wasting "just checking availability" floods).
- **Proof device:** keep the accommodation OTA-maths callout ("On a R2,000/night booking: Airbnb takes ~R460… TrustSquare takes a once-off intro fee") — it is devastatingly concrete for this audience. Pair with a live "Stays" card carrying a trust badge.
- **CTA:** "List Your Experiences / Stays in {{city_name}}" — multi-listing framing again.
- **Tone:** margin-protection, "own your guest relationship," anti-platform-dependency.

### E.3 Collection dealers / shops (→ batch; `collectors_outreach`)
- **Wedge:** "Move high-value stock discreetly, without auction commission or a public price." Dealers hate two things: auction-house buyer's+seller's premiums (often 25%+ combined) and **publicly visible asking prices / unsold-lot stigma.** TrustSquare gives a **private, no-public-bidding** channel where price and identity stay hidden until a serious, pre-paid buyer is introduced.
- **Reframe anonymity for a dealer:** discretion is a *feature they already sell* to their own clients. TrustSquare extends it — **"no public price, no failed-auction record, no premium."** The intro fee guarantees the enquirer is a real buyer, not a rival dealer fishing for your inventory/pricing.
- **Proof device:** lean hardest into the **gold "Highly Trusted" badge** here — for high-value items, the trust tier *is* the product. Show a collectors card (e.g. a watch or coin lot) with `★ 92` gold badge + "Provenance" cue.
- **CTA:** "List an Item in {{city_name}}" + multi-listing (dealers have stock, not one item).
- **Tone:** discreet, connoisseur-literate, premium. No emoji-heavy consumer voice; restraint signals seriousness to this audience.

### E.4 Cross-vertical copy spine (shared across all three)
1. **Hook:** name their pain in their language (commission / tyre-kickers / public price).
2. **Mechanic in one line:** buyer pays a small intro fee to reach you → you stay private → you accept only who you want → TrustSquare never touches your deal.
3. **Live proof:** the embedded card + trust badge (the app, in the inbox).
4. **Founding-seller urgency:** first sellers in {{city}} are featured first + free to list.
5. **Send-gated CTA:** magic link → pre-filled draft → sign on only at accept.

---

## F · Execution plan & sequencing

**Phase 0 — BLOCKED ON #1.** Lock the home-page redesign (palette / type / card look). The tokens in §C are the *current* system and what `property_outreach_v2.html` is built on; if #1 evolves them, update §C + the shared partial first.

**Phase 1 — Reference draft (THIS BATCH, done).**
- `property_outreach_v2.html`: current tokens, embedded live listing-card + trust-badge, 3-up marketplace strip (flat cards, no phone frame), agent-tailored copy (§E.1), preheader, rebrand footer with reg number, all client-safe per §D. Send-gated CTA unchanged.

**Phase 2 — Build the shared partial, then re-skin the other 6 outreach templates** (collectors, experiences, accommodation, services-technical, services-casuals, tutors) from the property v2 reference:
- Swap legacy `#1a1a2e`/`#d4a853` → §C tokens (navy header + accent-blue CTA + correct tier badge).
- Add Syne/Inter + preheader + standard reg-number footer.
- Replace phone-mockups with the flat marketplace strip.
- Apply the per-vertical messaging wedge (§E.2, §E.3) — collectors → gold-tier lean; travel → OTA-maths; services → keep call-out/rate + correct Commit/Queue model badge.
- Template `{{intro_fee_display}}` so a cost-model change is one variable.

**Phase 3 — Re-skin the 2 lifecycle templates** (`intro_accepted`, `intro_declined`):
- Lightest touch (already on rebrand footer + correct Tuppence copy). Type + colour only, **plus** embed the real listing card: accepted → show the accepted listing as a live card; declined → show 2–3 *alternative* same-category live cards for re-engagement (replacing the flat tip list).

**Phase 4 — QA matrix.** Render-test all nine in Gmail (web/iOS/Android), Apple Mail, Outlook (Windows/web), dark mode, and images-off. Verify: CTA is accent-blue everywhere; trust badges match §C; no broken layout in Outlook; preheader correct; unsubscribe + reg footer present; offer survives images-off.

**Phase 5 — n8n wiring (workflow owner, not HTML):** plain-text alternative part; `{{intro_fee_display}}` injection; per-vertical → per-template routing already exists.

### Deliverables in THIS batch
1. `ROADMAP_6_EMAIL_OVERHAUL.md` (this file).
2. `property_outreach_v2.html` (the reference draft).

### Flags / assumptions
- §C tokens are the **current** system; they are the dependency hand-off point with #1. Built v2 on them so it ships even if #1 slips.
- Did not re-read `services_casuals_outreach.html` in full (same April family); its one model-specific note (Casuals = Queue badge) is captured for Phase 2.
- "USD $2" left literal in v2's prose for now; `{{intro_fee_display}}` templating is a Phase-2 batch task to avoid a nine-file edit later.
