# Autonomous prompt — Agency import anonymisation (text pass)

You are working autonomously on David's LIVE project **MarketSquare**, an anonymity-first marketplace at trustsquare.co. No user is available — make sensible, conservative decisions and NEVER wait for input. You have ONE tightly-scoped build to complete.

## Read these first, in order (do not skip)
1. `C:\Users\David\Projects\MarketSquare\CLAUDE.md` — the working rules. They are mandatory and override any default behaviour.
2. `C:\Users\David\Projects\MarketSquare\AGENCY_IMPORT_ANONYMISATION_SPEC.md` — the spec for what you are building. **Build "1 · Text pass" ONLY.** The photo pass (section 2 / Phase B) and Phase 2 recruit-agents are explicitly OUT OF SCOPE.
3. In `C:\Users\David\Projects\MarketSquare\bea_main.py`: the endpoint `@app.post("/agencies/{agency_id}/import")` (function `agency_import`) — this is the ONLY endpoint you may modify. Also read `ai_provider.py` and the existing `/advert-agent/market-note` endpoint to find the project's existing AI-call helper — REUSE it. Do not write a new AI client, key handling, or HTTP wrapper.

## The build — a text anonymisation step inside `agency_import`
Before each imported advert is stored, clean its title + description:
- **Regex strip:** phone numbers (South African + international formats), emails, URLs / social handles, and street number + street name (keep suburb / area only).
- **AI rewrite** the description via the existing AI helper, instructed to remove agent names, agency names, contact CTAs ("call / WhatsApp / viewing by appointment / our office"), and any identifying phrasing — while KEEPING price, beds/baths/erf, condition, suburb, and the genuine selling points.
- **Fail-safe:** if the AI call fails or the API key is missing, fall back to the regex-only clean and mark that row `needs_review` in the response. NEVER store an uncleaned advert as publishable.
- Keep the existing behaviour that each advert lands as a **draft** (`listing_status='draft'`). Nothing auto-publishes.
- For the spec's 3 open decisions, use its recommended defaults (redact-if-localised; spot-check first N; agency brand fully hidden). Do NOT invent new pricing or product behaviour.

## Hard rules (from CLAUDE.md — follow exactly)
- The Projects folder is a FUSE mount where the **Edit/Write tools TRUNCATE files**. Do ALL writes through bash with a Python heredoc: exact-match anchor with `assert src.count(anchor) == 1` before replacing; back up first (`cp bea_main.py bea_main.py.bak-<timestamp>`); run `python3 -m py_compile bea_main.py` after every change. If py_compile fails, restore from the .bak and retry.
- **Additive only.** Do NOT change any endpoint or flow other than `agency_import`. Do NOT touch the frontend (ms.js, marketsquare.html) or any other file. Reuse before recreate.
- **Do NOT deploy.** Leave everything staged for David to review and deploy himself.

## Verify before you finish
- `python3 -m py_compile bea_main.py` passes.
- Write a throwaway Python test that calls your anonymise function on a sample advert containing a phone number, an email, an agent name and "call our office", and print the before/after to prove they are removed. Delete the test file afterwards.
- Confirm you changed ONLY `agency_import` (show a diff of your edit).

## When done
Write `C:\Users\David\Projects\MarketSquare\AGENCY_IMPORT_ANON_BUILD_REPORT.md` summarising: exactly what you changed (file, function, the anchors you replaced), the before/after test output, and the single command David runs to deploy (`ms-deploy`). If anything is ambiguous, risky, or would require touching another flow, STOP and write what is blocking instead of guessing.
