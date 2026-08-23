## 2026-08-23 — AGENCY-AUDIT-1: agency onboarding audited for the soft-launch email wave

- Audited the full agency onboarding surface ahead of the scraped-agency email wave
  (David's ask, 23 Aug). VERDICT: both lanes exist and are live — API import
  (POST /agencies/{id}/agents/bulk roster + /agencies/{id}/import adverts, per-advert
  report, anonymisation + photo scan + 50/100 publish gate) AND self-serve console
  (invite agent, CSV/JSON bulk add, seat tiers, caps, remove, filters). Import guide,
  Agents-as-a-Service page and Agency Playbook PDF all probed live behind the gate.
- Three OPEN ledger entries added for the gaps that block the wave being effortless:
  RG-0163 (no Agency lane in citylauncher/n8n — agency_outreach.html is deployed but
  nothing can send it), RG-0164 (?signin= token never chains to ?agency=1 — combined
  links race, and create_agency emails the admin nothing), RG-0165 (agency_outreach
  "how it works" steps describe the solo-seller flow, not the console/import lanes).
- Deliverable: AGENCY_ONBOARDING_AUDIT — nice.docx (findings, evidence grades, the
  three-lane "effortless" email copy ready to paste once RG-0164 lands).
