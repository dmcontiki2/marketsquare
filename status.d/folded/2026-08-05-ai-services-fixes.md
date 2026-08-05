## 2026-08-05 — AI services fixes (audit acted on)

- AI-SERVICES-AUDIT-1 findings ACTED ON same day per David: F1 any-lane gates (15x),
  F2 deliver-then-charge (AI1/AI2/AI5), F3 vendor-neutral card copy, F5 HEARTBEAT-1
  idle-recovery live in code. RG-0032..0035 LOCKED. py_compile green; NOT yet
  deployed — rides next /tsl. Post-deploy: re-run both ban-drill variants.
- Peer pack v2 ready (extract generator answers the packet complaint) — David
  re-runs PEER_AUDIT_AI_SERVICES.bat.
- ALERT: RG-0028 regression — origin accepts direct connections (Hetzner firewall
  likely off). David: Hetzner console. Not fixable from a session.
