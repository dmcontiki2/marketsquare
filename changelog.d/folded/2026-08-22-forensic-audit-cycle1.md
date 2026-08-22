## 2026-08-22 — Launch-readiness forensic audit, Cycle 1 (HALT pass)

Ran Cycle 1 of the three-cycle launch-readiness forensic audit against the live site as the D-7
gate evidence base (soft launch 29 Aug, full 1 Sep — RUL-001). Framed as HALT: over-stress each
dimension to precipitate the weak link, record operating/destruct limits, harden.

- **Scoreboard: 2 RED · 6 AMBER · 2 GREEN.** RED = Hardening + Hack-proofness, both from ONE root:
  DW-057/DW-029 exposed secrets still unrotated while the gate + WAF are effectively down (probed:
  app shell, live /listings and /dashboard/summary all 200 anonymously). 15 Aug rule → HOLD
  indicated; the launch ruling is David's.
- **Probe pass:** /health ok v1.3.1, /dashboard/bit 8/8, 3 AI lanes live, rulings 39/39, predeploy ok.
- **Ledger regression healed:** RG-0015 tripped RED (stranded .git/index.lock + HEAD.lock >60 min);
  healed via scripts/git_unlock.py, ledger re-run clean (129 entries, 126 holding, 0 regressed, 3 open).
- **HALT security:** app auth is hard — no SQL injection, no enumeration, no limit-exhaustion, fails
  closed (POST /intros → 401), forge endpoints 404. IL-01 (/tuppence/balance?email=) now 401 —
  the 15 Aug launch-blocker is CLEARED. The destruct limit is the burnt credentials in front, not the code.
- **HALT economics:** profitable at 60/600/6000 even under 2× churn + 40% demand drop + 15% FX +
  vendor reprice at once; break-even ~25–30 sellers. Weak link is revenue realization, never cost.
- **Server capacity NOT MEASURED at launch scale** — Cloudflare edge 403s synthetic non-browser load;
  won't bypass edge protection to stress prod. Honest RG-0133 answer.
- Deliverables: FORENSIC_AUDIT_CYCLE1 — nice.docx + FORENSIC_READINESS_BOARD_CYCLE1.html (indexed to Visuals).
- Cycle 3 sized at $0: ~$0.26/lens ceiling; six lenses ≈ $1.00–1.60 total. Paid call awaits David's approval.
