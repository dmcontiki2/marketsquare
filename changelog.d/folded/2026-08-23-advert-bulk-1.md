## 2026-08-23 — ADVERT-BULK-1: the console can bulk-import ADVERTS (David's question closed a real gap)

- David, eyeballing: "How would a property agency bulk upload all of their property
  adverts?" Answer before today: only via the API (IT person) or concierge — the
  console's Bulk add covered agents, not stock. That broke the wave's effortless
  promise for non-IT agencies.
- New "⇪ Bulk import adverts" button in the console's imports card: paste CSV from
  Excel (agent_email + title required; photos as |-separated URLs; category defaults
  to the console skin), copy-header/copy-example buttons, honest empty-state, and the
  pipeline's full per-advert report rendered back (imported / needs review / skipped
  no-agent / over-cap / photos attached & held). Drives the SAME locked
  /agencies/{id}/import pipeline — no second engine. Ledger RG-0166 (LOCKED).
- Copy synced everywhere the lane is promised: lane 2 of all three outreach templates,
  the Import Guide page + canon md ("No IT person?" callout), and the wave runbook's
  concierge step.
