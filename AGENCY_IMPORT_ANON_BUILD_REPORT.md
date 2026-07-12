# Agency Import — Text Anonymisation Pass · Build Report
**Autonomous build · 7 Jul 2026 · spec §1 ("Text pass") of AGENCY_IMPORT_ANONYMISATION_SPEC.md · NOT deployed**

## What changed — one file, one endpoint
`bea_main.py` only. Four anchored heredoc edits (mount guard run first, exit 0; backup taken; every anchor asserted `count==1` before replacing):

| # | Anchor replaced | What it did |
|---|---|---|
| A | `class _AgencyImport(_BaseModel):` (insert above) | New module-private helpers used only by agency_import: `_ANON_PATTERNS`, `_anon_regex_clean()`, `_ANON_AI_SYSTEM`, `_anon_ai_rewrite()` |
| B1 | agency_import docstring | Documents the anonymise pass + needs_review fallback |
| B2 | `imported = 0; unmatched = 0; capped = 0` | Adds `needs_rev = 0; rows = []` counters |
| C | the `city = …` / INSERT / `return {…}` block | Runs the two-leg clean before storage; extends the response |

Diff vs backup: **4 hunks, all at lines ~10205–10372** (the agency_import region), +126/−6 lines. No other endpoint, no frontend, no schema, no other file touched.

## How the pass works (per imported advert)
1. **Regex hard strip — always runs; raw text is never stored.** Phones (SA local + international/0027 formats), emails, URLs + bare domains, social handles, street number + street name (EN + Afrikaans street types — suburb/area kept). Patterns are prefix-shaped so prices (R2 450 000), erf sizes and bed/bath counts can't match. A lookahead stops "…Bedrooms Close to schools" false-positives.
2. **AI rewrite — reuses the existing seam, no new AI client.** `ai_provider.complete(task="haiku")` with `_ts_active_provider()`, exactly like `/advert-agent/market-note`. Instructed to remove agent/agency names, contact CTAs ("call/WhatsApp/viewing by appointment/our office") and identifying phrasing; keep price, beds/baths/erf, condition, suburb, selling points; never name the agency (spec decision #3 default: brand fully hidden). `_check_cost_ceiling()` (C1) runs before each call; real token spend logged via `_log_ai_spend()` under `/agencies/import#anonymise`.
3. **Belt-and-braces:** the AI output is regex-re-stripped, so a model echo of a phone/email can never reach the stored draft.
4. **Fail-safe:** any AI-leg failure (no key, provider down, ceiling hit, unparseable output) → the regex-only clean is stored and that row is flagged `needs_review: true` in the response. Nothing uncleaned is ever stored.
5. **Unchanged behaviour:** every advert still lands `listing_status='draft'` under the agent's cap; nothing auto-publishes. Existing response keys untouched; response adds `anonymised`, `needs_review`, and per-advert `rows` (title, agent_email, needs_review, removed-labels — the data for the spot-check-first-N ops step, spec decision #2 default).

## Proof test (throwaway, deleted after run)
Sample advert carried a phone, intl phone, email, URL, street address, handle, agent name ("Piet Jansen"), agency name and "Call our office…".

**BEFORE (desc):** `…Call or WhatsApp Piet on 082 123 4567 or +27 71 234 5678, or email piet@jansenproperties.co.za. Visit www.jansenproperties.co.za or find our office at 14 Jan Shoba Street, Lynnwood, Pretoria. Follow @jansenprops. R2 450 000 | 3 beds | 2 baths | erf 800m2…`

**AFTER regex (leg 1, real):** all five categories stripped (`['address','email','handle','phone','url']`); R2 450 000, Lynnwood, erf 800m2, "2 Spacious Bedrooms Close to top schools" all survived. Names + CTAs remain after regex-only — which is exactly why fallback rows are needs_review.

**AFTER AI leg (leg 2):** `TITLE: Stunning 3-bed family home in Lynnwood` / `DESCRIPTION: Immaculate 3-bedroom, 2-bathroom home on an 800m2 erf in Lynnwood, Pretoria. R2 450 000. …` — no Piet, no Jansen, no CTA; a deliberately-planted phone echo in the AI output was caught by the re-strip guard.

**Leg 3:** provider `ok=False` AND provider exception both return `ok=False` → needs_review path. ALL ASSERTIONS PASSED.

## Verification status (flat)
- `python3 -m py_compile bea_main.py` — **passed** (before and after).
- Torn-mount guard — **passed** (exit 0) before writing; tail + line count verified after (13 750 → 13 870).
- Regex leg — **tested for real**. AI leg — **tested with a stubbed provider only** (no API key in sandbox): parse, re-strip guard and both failure modes proven; the live-key call path is byte-identical in shape to market-note but **unverified against the live API**. First real import batch should be spot-checked.
- Scope — **verified**: diff vs backup shows only the agency_import region changed.
- CHANGELOG.md — entry appended (with Cost model impact line). Not deployed; git not touched.

## Deploy (when you've reviewed)
```
cd C:\Users\David\Projects\MarketSquare
.\deploy_bea_safe.bat
```
Undo path if ever needed: `cp bea_main.py.bak-20260707-063851 bea_main.py` (backup sits beside the file; delete it after a happy deploy so `git add -A` doesn't sweep it).

Cost note: +1 haiku call (~$0.002, real-token logged) per imported advert with text, gated by the C1 daily ceiling. Photo pass (Phase B) and Phase 2 remain unbuilt, as scoped.

---

# Phase B addendum — Photo Anonymisation Pass · 7 Jul 2026
**Same file, same endpoint. Diff vs `bea_main.py.bak-phaseB-20260707-073657`: 4 hunks, all in the agency_import region (~10291–10594), +230/−8. py_compile clean. NOT deployed.**

## Design stance: FAIL-CLOSED (your "no slips" instruction)
The text pass fails open to regex-only because regex provably catches the hard identifiers. Photos have no such fallback — an unscanned photo cannot be proven clean — so **every failure path holds the photo back entirely**. A photo reaches the draft ONLY via: scan says `clean`, or scan says `redact` AND the blur was actually applied, AND confidence ≥ 0.75. Held photos are simply not stored — the agent re-uploads clean ones through the normal flow. The originals are never written anywhere.

## Pipeline per photo (max 6 per advert)
1. **Fetch** — `photos`/`images` list on each advert (https URL or data-URI). Redirects re-checked hop-by-hop; private/loopback/link-local hosts refused (SSRF guard); 12 MB cap; content-type must be image/*.
2. **Vision scan** — one seam-routed call (`ai_provider.complete`, `task="sonnet"` — upgraded from Haiku to Sonnet for detection quality, 7 Jul 2026) on an ~896px probe. Strict JSON verdict: `clean` / `redact` + 0-1000-normalised regions / `reject`. Prompt covers the full spec list — contact bars, agency logos/watermarks, boards & For-Sale signage, flyers/collages, agent headshot overlays, number plates, house/street numbers — and instructs *"if in ANY doubt, reject"*. C1 ceiling checked per photo; real tokens logged under `/agencies/import#photo-scan`.
3. **Redact** — regions blurred on the FULL-SIZE image, boxes padded (~3% + ≥12px), Gaussian radius ≥18 (≈box/4). `redact` with no usable regions = held, never trusted.
4. **Store** — re-encoded thumb+medium (EXIF/GPS metadata cannot survive re-encode) via the existing `_s3_upload`/`storage` path; first photo becomes `thumb_url`/`medium_url`, all attached photos go into the standard `[photos:…]` description prefix — added AFTER text cleaning so the text pass can't eat our own URLs.
5. **Review hooks** — any held photo ⇒ row `needs_review:true`; response adds `photos_attached`/`photos_held` totals, per-row `photos{received,attached,held,notes}` (notes name what was redacted/why held), and `spot_check:true` on each agency's first 10 imports (spec decision #2 default).

## Proof test (throwaway, deleted)
Synthetic 1600×1200 agency photo: house + white contact bar ("CALL PIET JANSEN 082 123 4567 – JANSEN PROPERTIES") + red JANSEN logo block + EXIF `"Agent Piet Jansen 082 123 4567 GPS -25.7461,28.1881"`.
- **Fetch guards:** loopback host, bad scheme, junk data-URI all refused; good data-URI passes.
- **Blur geometry (real):** contact-bar and logo pixel spread collapsed below 35%/50% of original (text unreadable); pixels outside the padded regions **byte-identical** to the original.
- **Routing (stubbed vision):** clean→attached · branded→blurred+attached · flyer→held · confidence 0.40→held · garbage JSON→held · redact-without-regions→held · provider-down→held · **ceiling breach→held**. Spend logged per scan.
- **EXIF:** both stored files contain zero bytes of the agent string or GPS coords; `getexif()` empty.
ALL ASSERTIONS PASSED.

## Verification status (flat)
- py_compile — **passed**. Mount guard — **passed** before write. Scope — **verified** (4 hunks, agency_import region only; no schema change — thumb_url/medium_url columns already exist; no new server dependency — PIL + httpx already on the box).
- Blur, EXIF-strip, routing, fail-closed paths — **tested for real**.
- Live vision detection quality (does Haiku catch every board/watermark on real agency photos?) — **unverified in sandbox** (no key). This is the residual risk; the mitigations are the "any doubt → reject" prompt posture, the 0.75 confidence gate, drafts-only storage, and the first-10 spot-check flag. **Spot-check the first real import batch before trusting it.**

## Deploy (both phases together, when you've reviewed)
```
cd C:\Users\David\Projects\MarketSquare
.\deploy_bea_safe.bat
```
Undo: `cp bea_main.py.bak-phaseB-20260707-073657 bea_main.py` (pre-Phase-B) or `cp bea_main.py.bak-20260707-063851 bea_main.py` (pre-everything). Delete the .bak files after a happy deploy.

Cost (Sonnet, per _MODEL_PRICE): ~$0.0048/photo, max 6/advert, under the C1 ceiling and logged as sonnet_vision. A 50-advert × 6-photo batch ≈ $1.45; 1,000 photos ≈ $4.80.
