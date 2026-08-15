## 14 August 2026 — EULA v1.13: AI disclosure up front, and the three-way EULA fork closed (EULA-FORK-1)

**Why.** David: "we will have to declare in our EULA up front that we use AI in the app,
designed with it, and did use it to create photos for demos and for demo listings."
Everything we produce is watermarked/provenance-marked; the exposure is not the marker,
it is an undisclosed method.

**Found while doing it — the EULA had silently forked into three copies.**
`terms.html` was v1.12. `eula_clean.html` (the nominal source) and the `_EULA_HTML`
literal inside `ms.js` — **the copy a user actually clicks Accept on** — were both still
v1.11 and missing §6.1B Partner Content entirely. Users were accepting an agreement the
site did not publish. Nothing detected it because nothing compared them. Same shape as
CHANGELOG-COLLISION-1 and STATUS-COLLISION-1: N hand-maintained copies of one truth, no
comparator.

**Fixed — machinery, not memory.**
- `scripts/eula_sync.py` — `eula_clean.html` is now the SOURCE and this is the ONE writer
  of `terms.html` and the `ms.js` literal. Idempotent, timestamped backups, refuses rather
  than guesses if an anchor is missing. `--check` exits 1 on drift.
- All three copies are now byte-identical (100,775 bytes) and at v1.13.
- Regression ledger **RG-0077** (LOCKED) asserts both halves: the copies stay identical,
  and the AI disclosure stays in. Source-side by design — /terms sits behind the reviewer
  gate, so an anonymous live fetch would prove nothing.

**EULA v1.13 content (14 August 2026), added to the shared body:**
- **Up-front AI disclosure block**, placed before §1 Definitions — AI was used to design
  and build the Platform and this Agreement; AI image/video generation produced the
  demonstration and marketing imagery; the Platform uses AI in operation and offers
  optional paid AI features. States plainly that none of it changes the user's rights,
  and points to §§8.3, 7.6, 5.5, 7.7.
- **New §7.7 — Disclosure of the Platform's Own Use of Artificial Intelligence**:
  design/build under human direction with undiluted Operator accountability; AI-generated
  imagery depicts imagined subjects, not real people or properties; demonstration listings
  appear only in demo mode behind the persistent "Demo mode" banner and cannot be
  transacted on; provenance markers (visible credit, C2PA content credentials, invisible
  watermarks) are never stripped or defeated; and a user-facing rule that AI-generated or
  AI-altered media must not misrepresent what is listed (enhancement yes, generation no).
- **New §8.3 bullet** — Your Content is never sold, licensed or supplied to any third party
  for training, fine-tuning or evaluating AI/ML models, and is never used to train a model
  for use outside the Platform. In-Platform processing under §§7.6/7.7 is expressly not
  external training material.

**Verification.** `node --check ms.js` passes. All three bodies compared byte-for-byte and
identical. `scripts/eula_sync.py --check` clean. `check_canon_pointers.py` ALL IN LINE.
Full regression ledger run: no regressions, RG-0077 green.

**State.** On disk only — **not deployed**. `ms.js` and `terms.html` are both in
`deploy_manifest.txt`, so the next `deploy` push ships the new acceptance modal and the
published page together. `canon.yml` and `LEGAL_VERSIONS.md` bumped to v1.13; the A6
counsel review remains open and now also covers §7.7 and the §8.3 commitment.
