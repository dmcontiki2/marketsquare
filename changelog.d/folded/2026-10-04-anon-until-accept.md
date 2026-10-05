## 2026-10-04 — RUL-202: a seller sees no buyer name until she accepts

David, on the Batch 2 report: *"I cant remember that we agreed to give the prospective buyers first name to a seller ... 100% anonymous"*.
PROBED on disk: no ruling allowed a name; the first name came from E2E-HMI-1 (24 Sep) and AUD-024 had only trimmed the full name to it.
- bea_main.py `_intro_for_viewer`: a pending request reaches the seller with `buyer_name = ""` (was the first name).
- n8n new-intro payloads (paid and Local Market): `buyer_name` is "A buyer".
- ms.js live-intro card: a pending request always reads "A buyer".
- Ledger RG-0827 tightened (demands no name, repo and live); rulings_check RUL-202; prove_audit_b2.py updated.
