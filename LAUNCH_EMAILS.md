# LAUNCH EMAILS — the one page of truth (28 Jul 2026)

> Anything about launch emails is answered HERE. ROADMAP_6_EMAIL_OVERHAUL.md and the
> April n8n outreach fleet are SUPERSEDED (archived in n8n/email_templates/_archive_2026-04/).
> The live outreach machine is CityLauncher/emailer (Resend, dry-run-guarded, opt-out wired).

## The rule set (three lines)

1. **Skin ruling:** the LIVE reference is `CityLauncher/emailer/templates/agency_outreach.html`
   (built 27–28 Jul against the current brand). New wave templates derive from it.
2. **EARLY vs full:** provisional patent filed before send day → full; not filed → _EARLY
   (outcome only, no mechanism). One decision per wave, decided at send time.
3. **Build an email only when its wave has a date.** Early builds drift.

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
- [ ] ONE more deploy for the phone-card images: step 3c-phone found no files on the first
      pass (the nine jpgs existed in the workspace view but not on the Windows disk — sync
      ghost, now re-materialised into CityLauncher\emailer\assets via the desktop bridge).
      After it: verify https://trustsquare.co/static/phone_prop_stand.jpg returns 200.
- [ ] SO-1 CHECK (David's call): showcase adverts name real places (Dinokeng, Pilanesberg,
      Hartbeespoort) and listing 270's live title shows "Dinokeng" again — confirm intended
      for normal demo adverts, or genericise before the send.
- [ ] Rank explainer live at /static (ships via deploy step 3c-rank — in place).
- [ ] EARLY/full decision (rule 2) on send day.
- [ ] Dry-run via emailer.py, preview eyeballed, then send.

## Transactional estate (working, not launch-wave)

- Login magic-link — LIVE (Resend, Gmail fallback).
- Intro accepted / declined — n8n lifecycle, live when workflows on.
- Demand-loop invite — built, triple-gated, dormant until demand loop flips on.
- Inbound triage — Cloudflare worker + BEA drafts; auto-send OFF; Gmail copy always.
- Brevo signup sync — wired.
