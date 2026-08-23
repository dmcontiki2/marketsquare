## 2026-08-23 — AGENCY-WAVE-1 SHIPPED LIVE + E2E-proven; three SAW entries promoted

- Release fd22db5 published via ms-deploy (all gates green after two fixes: wave-prep
  SQL made portable, fault widget wired into the three SAW pages). Live validation:
  /health ok · live ms.js carries AGENCY-LINK-1 · POST /agencies/wave-prep works on
  live (idempotent, Kronberg agency 1) · minted console link opened in Chrome landed
  signed-in INSIDE the agency console. Ledger after: 158 entries, 0 regressed,
  RG-0163/0164/0165 LOCKED and holding.
- RG-0159/0161/0162 (SAW lane) first passed with this release — promoted to LOCKED
  per the READY-TO-LOCK rule. RG-0160 stays OPEN: the example-dossier PDFs ride the
  media lane (media_push.bat), which has not run.
