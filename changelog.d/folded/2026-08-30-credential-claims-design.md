## 2026-08-30 — FIDE-CLAIM-1 designed: credential claims into backend + flows

David ratified the registry use case (non-intrusive verification that makes the trust
score mean what it was intended to mean) and asked for the backend/flow design. Delivered:
CREDENTIAL_CLAIMS_DESIGN.md + Navy .docx — generalized credential_registry +
credential_claims tables (additive, ONE_DEPLOY-conformant seed of the 4,237-row FIDE
export), 60-second claim flow, two-tier anti-hijack evidence ladder (Tier B registry-match,
Tier A anchored to the EXISTING id-verify lane), A2 anonymity mechanics (badge shows class,
never person), collision/upgrade/revocation rules, env-flagged endpoints incl. no-deploy
monthly registry refresh, capped trust-score weighting (credential = floor-raiser, not
crown), status-truth conformant badge (live JOIN only). RG-0216 (OPEN) live-probes
/credentials/mine and carries the build to the first post-launch-stabilization session.
