# Professional Agent Listing Template (AGENT-SVC-1/2/3)
**Built 19 Jul 2026 · module `estate_agents.py` · wired into bea_main behind the launch_redemption include · NOT yet deployed**

## What this is
Agents are now listable as a **service**, not just as sellers of stock. The template leverages what an agent can *prove* — every credential slot maps 1:1 onto the existing Property trust-signal catalog, so there is one scoring pipeline, not two.

## The profile (anonymised)
| Field | Rule |
|---|---|
| Anonymous handle | `Agent TS-4F2A9C` — random, stable; identity revealed only on accepted intro |
| Headline | ≤90 chars, anonymised (regex strip + same AI pass as agency import) |
| Bio | ≥30 words, comprehensive but anonymous |
| Years experience | Stored exact, **displayed banded**: Under 2 · 2–5 · 5–10 · 10+ |
| Properties sold | Stored exact, **displayed banded**: <10 · 10–49 · 50–199 · 200+, with source label (`declared` / `agency`) |
| City + suburbs served · specialties · languages | plain fields |

## Verticals (AGENT-SVC-2, 19 Jul 2026)
One template, one process, per-vertical credentials — `?vertical=property|cars`:

| Vertical | Label | Go-live gate | Credential slots | Sell-flow trigger |
|---|---|---|---|---|
| property | Estate Agent | FFC verified | PPRA 15 · FFC 10 · NQF4/5/6+ 6/+6/+8 · body 5 | Property listings |
| cars | Car Sales Agent (WeBuyCars, Wheelie et al.) | MIRA dealer reg verified | MIRA 8 · inspection partner 5 | Cars listings |
| travel | Tour Agent | ASATA membership verified (CIPC submitted) | ASATA 10 · IATA 10 · CIPC 6 · bonding 5 | **Searcher-side**: Adventures page pill (buyers, not sellers) |

Ranking quality is vertical-scoped: a car agent's property listings never count toward his cars quality score (tested). Cars pitch covers: real market pricing, NATIS transfer + RWC paperwork, safe finance settlement, screened buyers, managed viewings/test drives.

## Credential slots → trust signals (existing catalog, existing points)
| Slot | Signal | Pts | Note |
|---|---|---|---|
| PPRA number | category.property.ppra | 15 | verified vs ppra.org.za — legally mandatory |
| FFC year | category.property.ffc | 10 | annual, legal minimum to trade — **go-live gate** |
| NQF level 4/5/6+ | nqf4 / nqf5 / nqf6_plus | 6 / +6 / +8 | claiming 5 auto-claims 4; 6+ claims all three |
| Professional body | category.property.body | 5 | IEASA / SAPOA / NAR |

## Bulk agency onboarding — score correct by construction
`POST /agencies/{id}/agents/bulk` (api-key gated) takes agents **with credential claims**. Claims land as **pending** `user_credentials` — never auto-earned. Trust score moves only when ops verifies via the existing `/trust-score/credentials/pending` queue. A profile **cannot go live until the FFC is verified** (422 with a fix list, same pattern as the import quality gate).

## Ranking (seller-facing list)
`rank = 0.5 × avg live-listing quality (0–100, same scorer as IMPORT-QUALITY-1) + 0.5 × trust score` — listing quality never weighs less than half (David's rule). Suburb-match agents sort first. Card shows: handle, banded experience/sold, earned badges, trust score, avg quality, live listing count. Nothing identifying.

## The seller → agent INTRO (reverse intro, 1T)
1. Private seller in the sell flow is shown **why an agent** (5 advantages) + the **legal obligations** note (points at the Step-6 legal must-haves cards) — `GET /agents/pitch?city=`.
2. Local anonymised ranked list — `GET /agents/nearby?city=&suburb=`.
3. Seller picks one → `POST /agents/intro` (seller trust + listing quality snapshotted; message anonymised).
4. Agent inbox shows the lead **with the seller's trust score and property summary, seller anonymous** — `GET /agents/intros?email=`.
5. Agent **accepts at 1T** (charged to the agent — the lead fee that replaces cold calling and lead brokers; 402 if wallet <1T) or **declines free**. Contact revealed both ways on accept only.

## Verified
`test_estate_agents.py` — 26 functional checks green on a temp DB (bulk onboard, NQF chain, anonymisation, publish gate, 50/50 rank math, banding, intro lifecycle, 1T ledger charge, double-accept + broke-agent guards, anonymity reveals). bea_main.py py_compile clean after the anchored include (+11 lines, backup `bea_main.py.bak-agentsvc-*`).

## Frontend — BUILT (19 Jul 2026, second pass)
One process, two doors, all generated from `GET /agents/template`:
- **Sell flow**: new `agents` step for Property between Step 6 (legal) and the scorecard — pitch + ranked anonymised local agents + "Introduce me" (ms.js v316; demo-mode blocked).
- **Agent Hub** (`screen-agent-suite`, entry banner on the Seller Hub): profile editor (same template fields) + seller-leads inbox with Accept 1T / Decline free.
- **Agency console**: "⇪ Bulk add" beside Invite — CSV/JSON roster paste → `/agencies/{id}/agents/bulk`, per-agent report with anon refs + pending credentials.
Verified: `node --check` clean, HTML tail intact, anchored edits (5 in ms.js, 3 in marketsquare.html), backups `*-agentsvc-*` beside every touched file. Deploy is yours (`/ship`).
