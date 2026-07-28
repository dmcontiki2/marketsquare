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

- [ ] Re-run deploy: step 3c-phone (added 28 Jul) uploads the nine phone-card images
      (first deploy left them 404 — no upload step existed), and step 3f2 retries the
      showcase insert (flag still armed after a non-clean first apply — watch its output).
- [ ] Next deploy runs EMAIL-SHOWCASE-1 (flag armed 28 Jul) → harvest the nine printed
      `SHOWCASE id=` values → point the three phone-card "Click to view" links at
      `https://trustsquare.co/?listing=<id>`.
- [ ] Rank explainer live at /static (ships via deploy step 3c-rank — in place).
- [ ] EARLY/full decision (rule 2) on send day.
- [ ] Dry-run via emailer.py, preview eyeballed, then send.

## Transactional estate (working, not launch-wave)

- Login magic-link — LIVE (Resend, Gmail fallback).
- Intro accepted / declined — n8n lifecycle, live when workflows on.
- Demand-loop invite — built, triple-gated, dormant until demand loop flips on.
- Inbound triage — Cloudflare worker + BEA drafts; auto-send OFF; Gmail copy always.
- Brevo signup sync — wired.
