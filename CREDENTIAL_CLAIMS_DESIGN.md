# CREDENTIAL_CLAIMS_DESIGN — FIDE-CLAIM-1 and the general claim flow
**30 Aug 2026 · CTO design under RUL-037 · consumes the fide_trainers registry (RUL-072)**
**Status: DESIGN — build slot = first post-launch-stabilization session (RUL-065 timing class). Tracked: RG-0216 (OPEN).**

## 0. The one-sentence design
A seller privately claims an official credential ID; the backend matches it against a
locally-held public registry; the listing wears only the TIER BADGE — verification
without identification, evidence without intrusion.

## 1. Server data (new, generalized from day one)
```sql
CREATE TABLE credential_registry(          -- the public lists, held locally
  source TEXT NOT NULL,                    -- 'FIDE' (first), later 'SACE','CELTA',...
  credential_id TEXT NOT NULL,             -- FIDE ID as text (future sources non-numeric)
  name_norm TEXT NOT NULL,                 -- lowercased, unaccented, comma-order folded
  detail TEXT,                             -- 'FT','FI','NI','DI' for FIDE
  federation TEXT, harvested_at TEXT,
  PRIMARY KEY(source, credential_id));

CREATE TABLE credential_claims(            -- PRIVATE: account <-> credential link
  user_id INTEGER NOT NULL,
  source TEXT NOT NULL, credential_id TEXT NOT NULL,
  claimed_name TEXT NOT NULL,
  tier TEXT NOT NULL,                      -- 'A' | 'B' (see §3)
  status TEXT NOT NULL DEFAULT 'active',   -- active | revoked | displaced
  claimed_at TEXT NOT NULL,
  UNIQUE(source, credential_id));          -- ONE account per credential, ever
```
Seed: migrations/NNN_credential_registry.py loads fide_registry_seed.json
(export of CityLauncher fide_trainers; 4,237 rows) — idempotent upsert, ONE_DEPLOY
conformant (code+seed ride the deploy ref; NEVER scp).

## 2. Claim flow (seller side, ≤60 seconds)
Profile / listing-create, Tutors category first: "Hold an official credential?
Verify it — free, private."
1. Seller picks source (FIDE), enters credential ID + name-as-registered.
2. POST /credentials/claim → normalize name → registry lookup:
   - id match + name similarity ≥ 0.85 → CLAIMED (tier per §3)
   - id match, name 0.60–0.85 → PENDING (admin review queue)
   - no id match → honest decline: "not in the registry we hold (2022→now
     seminar awards); registry grows monthly" — never a dead end, links the
     re-check toggle.
3. Badge appears on listings; claim record stays private.

## 3. Evidence tiers — the anti-hijack design (the registry is PUBLIC, so
possession of an ID proves nothing; identity must anchor the claim)
- **Tier B — Registry-matched:** claimed name matches registry. Weak-anchor;
  badge shows "FIDE-listed trainer". Displaceable (§5).
- **Tier A — Identity-anchored:** the app's EXISTING id-verify lane
  (/id-verify/status) has verified the account's legal name AND that name
  matches the registry entry. Badge shows "✓ Verified FIDE Trainer (FT)".
  Trust-score weight sits here.
This is the tiered-grading doctrine applied to sellers themselves: evidence
ladder, never self-claim. No new identity machinery — we reuse the lane that exists.

## 4. Anonymity mechanics (A2 absolute)
Public buyer view renders ONLY: badge + tier + title class ("Verified FIDE
Trainer (FT)"). Never name, never FIDE ID, never federation (federation narrows
identity in small pools). The claims table is private; admin surfaces show it
gated. The credential proves the CLASS, the platform withholds the PERSON.

## 5. Collisions, upgrades, revocation
- UNIQUE(source,credential_id): second claimant on a taken ID → if newcomer
  reaches Tier A and holder is Tier B, holder is DISPLACED (status flag, both
  notified); Tier A vs Tier A cannot happen (id-verify uniqueness upstream).
- Title upgrades ride the monthly re-harvest (housekeep): registry upsert keeps
  highest title; badges re-render from registry JOIN, so an FI→FT upgrade is
  automatic, zero touch.
- Revocation: admin endpoint sets status='revoked' (FIDE sanctions — rare).

## 6. Endpoints (FastAPI, bea_main.py; ALL behind env flag CREDENTIAL_CLAIMS, default off)
- POST /credentials/claim        {source, credential_id, claimed_name}
- GET  /credentials/mine         → claims + tiers for the session user
- GET  /admin/credentials        → pending queue + registry stats (admin-gated)
- POST /admin/credentials/registry-upsert  → monthly refresh WITHOUT a deploy:
  capped JSON payload, idempotent, reviewer-token-gated. (Data lane, not code lane.)

## 7. Trust score wiring
Trust engine reads credential_claims JOIN registry: Tier A adds weight by title
rank (FT > FI > NI > DI), capped so a credential ALONE never outranks conduct
(trust = credential + behaviour, the credential is a floor-raiser not a crown).
Weights land in the trust config, not code constants.

## 8. Status-truth conformance (21 Aug doctrine)
The badge is painted ONLY from a live JOIN at render time — no cached verdict,
no hand-set flag. /credentials/mine is the probe; RG-0216 asserts endpoint +
flag + seeded registry count once built. Grey/absent until data answers.

## 9. Build order (one session, small pieces, each complete)
1. migration + seed export from CityLauncher (registry table live, flag dark)
2. claim endpoint + mine endpoint + unit tests (flag dark)
3. profile/listing UI moment + badge render (flag dark)
4. admin queue + refresh endpoint
5. flip CREDENTIAL_CLAIMS=1 → probe → ledger RG-0216 READY TO LOCK → LOCK
Rollback story: flag off = whole feature dark, tables inert. No schema risk to
existing tables (purely additive).

## 10. Generalization contract
Adding SACE / CELTA / arbiters later = new registry rows with a new `source` +
one chooser entry. NO schema change, NO new endpoints. That contract is the
point of §1's shape.
