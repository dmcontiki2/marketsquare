# FILING BASELINE — FROZEN 2026-06-29
Single frozen, internally-consistent baseline for the CIPC provisional filing **and** the
whitepaper publication. Created after the 29 Jun alignment edits. The `.docx` are the artifacts
you file/publish from; they are git-ignored (`*.docx`), so they are pinned here by sha256.

## Frozen filing pack (sha256)
| Artifact | Version | sha256 |
|---|---|---|
| TrustSquare_Provisional_Specification_FILING.docx | provisional (v6.6 + align) | `fd37e1bf00385da6bd165ca9e447383aaa7941e4fd50bba8f94b77ceccc65ee8` |
| TrustSquare_WhitePaper_PUBLICATION.docx | v3.11 + align | `8e3340255d357a5cba5105d39b092d08e8e350d6a23af69eb78d0bda63cd8722` |
| archive/patent.v6.6-align-20260629.md (source snapshot) | v6.6 + align | `2dc4f3f90c0991a2e5cbfdc7c4a98c8b6608efa173d10fa197ec4b3dd8166ed9` |
| archive/whitepaper.v3.11-align-20260629.md (source snapshot) | v3.11 + align | `e07b46b8009a5f2ddbed5e6338f8d7b5af5cbee2b579d9aeafe363bde38f87f7` |

## Alignment edits applied 29 Jun (post-convergence)
1. **Patent** — Detailed-Description annex pointer `whitepaper v3.8` → `v3.11`.
2. **Whitepaper §9** — "file with CIPC on Day 0 (launch day)" → **file FIRST, before publication/launch** (novelty gate).
3. **Whitepaper §8** — "Merchant of Record (Paddle/**Stripe**)" → "(Paddle / **Lemon Squeezy**)" + SA via Paystack.

## Consistency proof (no drift)
- Source-of-truth `working/patent.md` + `working/whitepaper.md` updated to match the `.docx` (edits no longer live only in the rendered docx).
- Immutable dated snapshots written to `archive/…-align-20260629.md` (Jun-23 v6.6/v3.11 snapshots retained as pre-alignment convergence outputs).
- `canon.yml` + `LEGAL_VERSIONS.md` corrected: whitepaper pointer `v3.5` → `v3.11`. `scripts/check_canon_pointers.py` = **ALL IN LINE ✓** (run 29 Jun).
- Backups beside every edited file (`*.bak-align-*`, `*.bak-wpver-*`); restore = `cp backup file`.

## Parked for David (his hands — not done here)
1. **Commit the tracked baseline** (the `.md`, this manifest, and the registers; the `.docx` stay git-ignored by design):
   ```
   cd C:\Users\David\Projects\MarketSquare
   git add -A
   git commit -m "Freeze filing baseline (whitepaper v3.11): align edits + dated snapshots + canon/LEGAL register"
   ```
2. **Optional — formal MAJOR-baseline promotion** (patent v7.0 / whitepaper v4.0). The 23 Jun convergence audit reserved this milestone for your decision. **Not required to file the provisional.**

## Out of scope of this freeze
- **IP Brief v6** — counsel-gated, v5 controlling; unchanged.
- The **7 counsel items** (CPA s63 claim text, §101/COMVIK framing, novelty search, etc.) → belong to the **complete** specification (≤12 months), not the provisional.
