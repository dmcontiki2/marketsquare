## 2026-08-24 — Third-party launch register: daily sweep (5 days to soft launch, AMBER)

**THIRD-PARTY-SWEEP (scheduled, unattended).** All probes green: /health ok 1.3.1 · root 200 in
0.28 s · google:true (start 302s with real client_id) / apple 503 by RUL-030 · Didit READY 1T ·
/terms serves v1.15 (sync green, 117,749 B) · ledger exit 0 (167 entries, 0 REGRESSED, 14 open) ·
rulings 51/51 reflected.

Register rewritten from evidence. Changed since 23 Aug:
- **Yesterday's #1 red CLEARED:** the 4-commit deploy debt shipped 04:25Z (deploy_drift clean,
  DW-058 closed). RG-0154/RG-0158 closed on the ride; RG-0171 + RG-0174 LOCKED (bulk roster invites
  send real links; customer email = support pipeline, one reply per inbound, personal inbox
  dead-letter; CF worker wrangler-deployed).
- **Probe overruled the file — SSL row:** register said cert expires 2026-09-24 (32 d); live cert
  is RENEWED to **2026-11-22 (90 d)**. Corrected.
- **Probe path fixed in the record:** post_deploy_status.json serves at /static/ (bare path 404s).
- New deploy debt: 3 record-only commits (eb928d1/819341a/5e2b0df), no app code.
- New ledger opens tracked: RG-0160 (dossier PDFs) + RG-0173 (agency journey probe); both must
  ride/precede the ≤27 Aug ship alongside RG-0156 (orchestrator, gate G2).
- Registrar RDAP probe attempted (rdap.org 404 for .co; registry RDAP unreachable from sandbox) —
  the four DOMAIN_* fields remain genuinely David-only, like GOOGLE_CONSENT_SCREEN.
- Noted: the scheduled task's own prompt is stale on two rows (secrets rotation done 22 Aug;
  Resend 422 = healthy) — recorded in the register's watch-outs, not re-raised.

Remaining reds for 29 Aug: RG-0139 consent screen unrecorded · RG-0137 domain unrecorded ·
RG-0156 orchestrator build · RG-0138 uptime watcher undeployed (David, 3 commands).
