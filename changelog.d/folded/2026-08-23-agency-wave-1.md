## 2026-08-23 — AGENCY-WAVE-1: the agency email wave is real — console links, wave lane, honest templates (RG-0163/64/65 CLOSED)

- **RG-0164 (console landing)**: create_agency now emails the admin a magic console
  link (?signin=<jwt>&agency=1); new idempotent `POST /agencies/wave-prep` pre-creates
  scraped agencies (verified=0) and mints 14-day console links in batch WITHOUT
  emailing (the outreach email is the first contact); ms.js signin success chains
  straight into the org console (agency/operator/dealer skins) and the standalone
  org-param handlers skip when signin is present — the 150ms race is closed; My Space
  now shows an "Agency console" card to any real agency admin (by-admin resolved) —
  until now the only doors were the superuser OPS card and a naked deep link.
- **RG-0165 (honest templates)**: all three recruited-vertical outreach templates
  (agency, travel_agency, cars_dealer) replace the solo-seller 4-step story with the
  three-lane block — concierge reply / 5-min console self-serve / IT import guide —
  plus the drafts+50/100-gate safety line and Import Guide + Agents-as-a-Service links.
- **RG-0163 (wave lane)**: n8n payload node maps Estate Agents/Agency → agency_outreach,
  sends prospect.magic_link when present (console links from wave-prep) and DROPS
  agency prospects without one (a console CTA that can't open a console is a lie);
  citylauncher carries the lane map. Live half asserts /agencies/wave-prep is deployed.
- All three promoted OPEN → LOCKED (fixed_on 2026-08-23). Wave-day checklist:
  AGENCY_WAVE_RUNBOOK.md (gate-down precondition, n8n re-import, reply-to, dry-run).
