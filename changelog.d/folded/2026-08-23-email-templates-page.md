## 2026-08-23 — Orchestration Email Templates page refreshed to the current wave set

- email_templates.html (ops dashboard, /orchestrator/v2/) rebuilt: 15 outreach
  templates (placement_agency_outreach added to the agency lane) plus a new
  Placement Onboarding section with all 8 sequence emails and their Day 0-18
  cadence (SAW-5/RUL-046). Every card's badges are now COMPUTED from the template
  files on disk (unsubscribe, launch-special absence per RUL-047, {{magic_link}}
  CTA, three-lane onboarding) instead of hand-painted — the stale green "launch
  special" chips (all 14 were false since RUL-047) and the ambiguous "no magic
  link"/"no Ruby Spark" chips are gone. Header documents the AGENCY-WAVE-1
  console-link rule and the wave-day runbook. Metadata dated + method-stamped.
