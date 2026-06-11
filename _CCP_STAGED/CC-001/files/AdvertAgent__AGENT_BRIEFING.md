# AdvertAgent · Master Agent Briefing
**Version 1.1 · 13 April 2026 (Session 4 — Tuppence language rules added)**
*Read this document at the start of every Claude Code session.*
*Read STATUS.md first, then this file.*

---

## 1 · What the Advert Agent Is

The Advert Agent is a **seller-facing AI listing coach** embedded inside the MarketSquare app (trustsquare.co). It helps sellers write better listings and improve their Trust Score before publishing.

**This is NOT:**
- A general AI chatbot
- A buyer-facing feature
- A replacement for the seller admin tool
- Mandatory — sellers can publish without ever using Stage 3

Governed by PRINCIPLE_REQUIREMENTS.md Part G (G1–G4). All of Parts A–F apply without exception.

---

## 2 · Architecture (Confirmed Session 4)

| Concern | Decision |
|---|---|
| Platform | Embedded in `marketsquare.html` (new screens) + new `/advert-agent/*` BEA endpoints |
| AI model | `claude-haiku-4-5-20251001` — hardcoded. Do not change without pricing model review. |
| Token budget | Server-side, per-call. Free first use (lifetime) then 1T ($2) per 8-session pack. |
| Local storage | IndexedDB (`aa_drafts` store) — drafts never leave device until Publish |
| Photos (draft) | Blobs in IndexedDB keyed to draft id |
| Photos (publish) | Multipart POST to `/advert-agent/publish` → BEA uploads to R2 (HETZNER_S3_*) |
| PDF generation | WeasyPrint server-side (fallback: reportlab if libpango missing on Hetzner) |
| Trust Score feed | Hardcoded in BEA system prompt (A5 is locked governance — changes with Codex only) |
| Auth columns | `aa_free_used INTEGER DEFAULT 0` + `aa_sessions_remaining INTEGER DEFAULT 0` on `users` table |

---

## 3 · The Four-Stage Flow

| Stage | Screen | AI call? | Cost | Notes |
|---|---|---|---|---|
| 1 | `#screen-aa-detail` | No | Free | Category-aware form, fully offline |
| 2 | `#screen-aa-photos` | No | Free | Rule-based photo checklist, fully offline |
| 3 | `#screen-aa-coach` | Yes | Free (1st) then 1T/8-pack | Optional — skip to Stage 4 any time |
| 4 | `#screen-aa-publish` | No | Free | PDF + MarketSquare pending draft |

Navigation is non-linear tabs. Draft list is `#screen-aa-home`.

---

## 4 · File Map

```
AdvertAgent/
├── docs/
│   ├── AdvertAgent_SOW_v0.1.docx
│   └── AdvertAgent_SOW_v0.2.docx
├── AdvertAgent_Pricing_Model.xlsx
├── AdvertAgent_HMI_Spec_v0.1.docx
├── PRINCIPLE_REQUIREMENTS.md       ← read-only
├── AGENT_BRIEFING.md               ← this file
├── STATUS.md                       ← read first every session
├── CHANGELOG.md
└── CLAUDE.md

Code lives in MarketSquare files:
  marketsquare.html                 ← new #screen-aa-* screens + aaDB + AA logic
  bea_main.py                       ← new /advert-agent/* endpoints
```

---

## 5 · Tuppence Language Rules — Critical

The platform uses Tuppence for two completely different purposes. Every agent and every UI string must distinguish them absolutely. Never use bare "1 Tuppence" or "1T" without context that makes the purpose clear.

| | Introduction Fee | AI Coach Pack |
|---|---|---|
| **Who pays** | Buyer | Seller |
| **When** | On seller accepting an introduction | When purchasing AI coaching credits |
| **What 1T buys** | One introduction event | Advanced AI features per use (in-app guidance free) |
| **Governed by** | A1 (product principle — locked) | G1 (AdvertAgent principle) |
| **Wallet display** | "Tuppence balance · used for introductions" | "AI Coach Credits · not used for introductions" |

**Mandatory UI copy rules (AdvertAgent screens only):**

| Context | Forbidden ❌ | Required ✅ |
|---|---|---|
| Pack purchase button | "Buy pack · 1 Tuppence" | "Buy AI Pack · 8 sessions · 1T" |
| Wallet AI card title | "AI Credits" | "AI Coach Credits" |
| Wallet AI card subtitle | — | "Not used for introductions" |
| Stage 3 balance display | "1 session remaining" | "1 coaching session remaining" |
| Stage 3 zero-balance CTA | "Buy 1T pack" | "Buy AI Pack — 8 sessions · 1T" |
| Free session badge | "Free" | "1 free coaching session included" |
| Any intro-fee reference | "AI pack" or "coaching" | "Introduction fee · 1T committed on request, burned on seller acceptance" |

The Tuppence wallet screen must show two visually separated sections:
1. **"Tuppence Balance"** — introduction currency, buyer-only cost
2. **"AI feature credits"** — Tuppence spent on advanced AI features (in-app guidance is free; AI-uses packs RETIRED 6 Jun 2026), with note "not used for introductions"

These must never appear in the same card or under the same heading.

---

## 6 · BEA Endpoints (MVP set)


| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| GET | `/advert-agent/status?email=` | None | Free-use flag + sessions remaining |
| POST | `/advert-agent/coach` | None* | Gate check + Claude call + return coaching |
| POST | `/advert-agent/publish` | None* | Receive draft + photos, write listing, return PDF URL |

*Seller identified by email in request body. API key not required for seller self-service.

DB migration runs idempotently at BEA startup:
```sql
ALTER TABLE users ADD COLUMN aa_free_used INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN aa_sessions_remaining INTEGER DEFAULT 0;
```

---

## 7 · IndexedDB Schema

```js
// DB: "advertAgentDB"  version: 1
// Store: "aa_drafts"  keyPath: "id"

{
  id: uuid,                    // e.g. "aa_1713000000000"
  category: "Real Estate",     // drives form fields + photo checklist
  stage: 1,                    // highest stage reached (1–4)
  fields: {                    // Stage 1 form values (category-specific)
    title: "",
    price: "",
    // ... category fields
  },
  photos: [],                  // Array of { slot: "lounge", blob: Blob }
  coachOutput: null,           // Stage 3 result (string) or null
  created_at: 1713000000000,
  updated_at: 1713000000000
}
```

---

## 8 · Category Intelligence

Five canonical categories (see PRINCIPLE_REQUIREMENTS.md D7). Stage 1 form fields and Stage 2 photo checklist are driven by `category` + `service_class` (for Services):

| Category | Phase | service_class | Key Stage 1 Fields | Required Photos |
|---|---|---|---|---|
| Property | Live | — | price, listing_type, prop_type, beds, baths, garages, floor_area, erf_size, suburb | lounge, kitchen, master_bed, bathroom, exterior_front, exterior_rear |
| Tutors | Live | — | subject, level, mode, rate, area | profile, teaching_example |
| Services | Phase 1 | **Technical** | service_type, area, rate, experience, registered | work_example_1, work_example_2, certificate (optional) |
| Services | Phase 1 | **Casuals** | service_type, availability, rate, days_available, area, references | work_example (optional), reference_letter (optional) |
| Adventures — Experiences | Phase 2 | Experiences | destination, activity_type, duration, group_size, price_per_person, difficulty, whats_included, guide_cert | hero, experience_1, experience_2, experience_3 |
| Adventures — Accommodation | Phase 2 | Accommodation | property_name_anon, property_type, star_rating, suburb, price_per_night, rooms, amenities, tgcsa_grade | exterior, lounge, bedroom, bathroom, pool_or_garden |
| Collectors | Phase 2 | — | item_type (Stamps/Cards/Coins/Memorabilia/Other), item_name, condition, catalogue_ref, edition_year, price | front, back, condition_closeup |

**Deferred:** Automotive (no phase). MTG/Collectibles and Philately are replaced by Collectors in Phase 2.

`service_class` is stored in the draft record and sent to `/advert-agent/publish` as a field. The AA wizard shows a class selector chip row at the top of the Services Stage 1 form before rendering the field set.

---

## 9 · Operating Rules

Same as MarketSquare — applied without exception:

1. **Uncertainty** — Implement best guess, flag at end. Never stop mid-task.
2. **Change size** — One feature or bug fix per task. Complete fully before starting next.
3. **Git commits** — Auto-commit after every completed task.
4. **Definition of done** — Code works AND CHANGELOG.md updated. Both required.
5. **Codex first** — Check Codex before any business logic.
6. **Anonymity absolute** — Every feature must preserve seller anonymity (A2).
7. **Subscription gate** — Never call Claude API without confirming free-use or sessions > 0.
8. **No large rewrites** — Surgical edits only.
9. **Secrets** — Never hardcode API keys. Read from environment always.

---

## 10 · Parent Project Reference

| Resource | Location |
|---|---|
| Codex | `Solar_Council_Codex_v4_5.docx` (upload to Claude Chat) |
| Platform briefing | `C:\Users\David\Projects\MarketSquare\AGENT_BRIEFING.md` |
| Platform status | `C:\Users\David\Projects\MarketSquare\STATUS.md` |
| BEA API | `https://trustsquare.co` |
| API key | `X-Api-Key: ms_mk_2026_pretoria_admin` |
| Server | Hetzner CPX32 · 178.104.73.239 · Ubuntu 24.04 · 4 vCPU · 8 GB RAM (upgraded from CPX22 on 25 May 2026) |

---

*End of AGENT_BRIEFING.md v1.0. Architecture locked at Session 4 kickoff.*
*Append updates to CHANGELOG.md, not here. Increment version only for architecture changes.*
