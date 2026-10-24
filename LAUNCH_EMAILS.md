# LAUNCH EMAILS — the one page of truth (28 Jul 2026)

> Anything about launch emails is answered HERE. ROADMAP_6_EMAIL_OVERHAUL.md and the
> April n8n outreach fleet are SUPERSEDED (archived in n8n/email_templates/_archive_2026-04/).
> The live outreach machine is CityLauncher/emailer (Resend, dry-run-guarded, opt-out wired).

## Current state (24 Oct 2026 -- OUTREACH-AUDIT-2; read this before the history below)

- **The letters that send** are CityLauncher/emailer/templates/*.v2.html (emailer.py TEMPLATES, RUL-232(e)/RUL-241(b)); sports clubs keep sports_club_outreach.html. Every CTA opens Quick's door for her category (`/q/<door>?src=&cc=&city=`) or the one door (`/door?src=&cc=&city=`, RUL-243); "founding" wording is gone (RUL-047).
- **Footers** (localize.py `_FOOTER`): no footer promises a single letter -- a further letter may follow after at least 60 days, never after an unsubscribe (RUL-251); RECONTACT-1's 60-day floor (RUL-106) and the GB/NZ exclusions stand.
- **Hold:** nothing sends. emailer/SEND_FREEZE and the absent SMS ARM file stand on the server (RUL-241(c)); the New York e-mail wave sends only after David's old-versus-new review (RUL-252(a)); no SMS to the US (RUL-252(b)); an SMS goes only to a real person's number (RUL-252(c)).
- **The audit board:** visuals/outreach_audit/OUTREACH_AUDIT_2026-10-24.html. The wave table below is history (28 Jul).

## The rule set (three lines)

1. **Skin ruling:** the LIVE reference is `CityLauncher/emailer/templates/agency_outreach.html`
   (built 27–28 Jul against the current brand). New wave templates derive from it.
2. **EARLY vs full:** provisional patent filed before send day → full; not filed → _EARLY
   (outcome only, no mechanism). One decision per wave, decided at send time.
3. **Build an email only when its wave has a date.** Early builds drift.
4. **A wrong-city send STANDS (RUL-073, 30 Aug 2026):** sent is sent — never recalled, never followed by a correction. One touch stays one touch; the fix is upstream (pull_from_server.py runs before every wave so geo-verdicts reach the send pool).

## Wave table

| Wave | Audience | Template | Status | Send date |
|---|---|---|---|---|
| 1 | Property agencies (Pretoria + national accounts) | CityLauncher `agency_outreach.html` | **CURRENT** — phone cards in; rank-explainer CTA in (28 Jul); "Click to view" links await showcase advert ids (flag armed, applies on next deploy) | launch − 7 days (**date TBD — David**) |
| 2–5 | Cars dealers, collectors, services, adventures/tutors | derive from wave-1 skin when dated | not built (deliberate) | TBD per 5-Wave plan |

Reference copy/plan: docs/TrustSquare_LaunchEmails_5Wave_v2 (niced 20 Jul).

## Wave-1 remaining checklist

- [x] EMAIL-SHOWCASE-1 applied (28 Jul, second deploy — flag consumed). Nine showcase ids,
      verified in the live feed: property 315 stand / 316 home / 317 penthouse ·
      cars 318 AMG / 319 LC79 / 320 250SE · experiences 312 game walk / 313 quad / 314 balloon.
- [x] Email "Click to view" deep-links wired to ?listing=315/316/317 (both link+image per card;
      .bak-20260728-deeplinks kept).
- [x] Phone-card images deployed (28 Jul, deploy #3) — all three phone_prop_*.jpg return 200.
      (Belt-and-braces anyway: inline_images.py CID-embeds them, so the email never depends
      on /static.)
- [ ] SO-1 CHECK (David's call): showcase adverts name real places (Dinokeng, Pilanesberg,
      Hartbeespoort) and listing 270's live title shows "Dinokeng" again — confirm intended
      for normal demo adverts, or genericise before the send.
- [x] Rank explainer live: https://trustsquare.co/static/ranking_explainer.html?v=1 → 200 (28 Jul).
- [ ] EARLY/full decision (rule 2) on send day.
- [x] E2E TEST PASSED (28 Jul 2026): 5 fictional 'Estate Agency' prospects (category value
      unused by real rows — safe isolation; DB backed up .bak-20260728-e2etest) sent through
      the real pipeline to David + 4 testers. All delivered to INBOX (not spam), links verified
      in the delivered copy (deep-links, magic, explainer, optout), 4 CID images rendered.
      Message-ids in emailer/sent_log.json. Fixes made during the test:
      · FROM address → david@mail.trustsquare.co (CANON: mail. subdomain is the only
        Resend-verified sender; root trustsquare.co was never verified → 403. Subdomain
        sending is also bulk best practice. emailer.py.bak-20260728-mailfrom kept.)
      · CTA typo fixed in all 7 outreach templates: "Claim our founding" → "Claim your
        founding" (.bak-20260728-claimyour kept).
      · Note: unsubscribe landing page says "MarketSquare" while emails say TrustSquare —
        brand mismatch, David's call.
- [ ] Wave-1 real send on send day (wave_runner gates: --arm + armed + gates_green + Tue-Thu).

## Transactional estate (working, not launch-wave)

- Login magic-link — LIVE (Resend, Gmail fallback).
- Intro accepted / declined — n8n lifecycle, live when workflows on.
- Demand-loop invite — built, triple-gated, dormant until demand loop flips on.
- Inbound triage — Cloudflare worker + BEA drafts; auto-send OFF; Gmail copy always.
- Brevo signup sync — wired.
