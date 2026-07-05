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

## Upload-ready filing document (added 30 Jun)
The provisional spec only *references* its Detailed Description; the whitepaper must be filed **with** it.
Assembled single A4 PDF (spec + Annex A cover + whitepaper) = the document to upload behind Form P6:
- `TrustSquare_Provisional_FILING_with_Annex_2026-06-29.pdf` (14 pp, A4) · sha256 `5c59fbe95deb6f6500430a41809cba2872e6187f4bd7ca649a95c1f6a97f2ac5`
- Built from the frozen FILING + PUBLICATION docx (their sha256 unchanged); originals not modified.

## Claims cleanup — superseding clean filing set (30 Jun)
Removed working annotations from the provisional's **claims** section only (substance unchanged): "(DRAFT — two-anchor structure…)" → "(provisional — indicative scope…)", "(DRAFT)" dropped from Dependent claims, "CONDITIONAL on Pingsby clearance" note dropped from C3, internal IP-Brief cross-refs and the `▍` glyph removed. No claim limitation altered. (Rationale: a provisional needs no claims at all — these are illustrative — but should not be filed with visible working labels.)
- The original `TrustSquare_Provisional_Specification_FILING.docx` was **open in Word (lock file present)** so it could not be overwritten; clean versions use new names and **supersede** it:
- `TrustSquare_Provisional_Specification_FILING_clean_2026-06-30.docx` · sha256 `9b8cb5f03e3ab8554210fe086055bf23b1c29d88c823e5e6cc4571e006a0559f`
- `TrustSquare_Provisional_FILING_with_Annex_2026-06-30.pdf` (14 pp, A4) · sha256 `5bde1613d60d1ced5b6014a6b7c50f9a645487b890c127a1ea1790e1394416a1` ← **the file to upload**

## Claim 7 truncation fix (30 Jun)
The whitepaper's §4 claims table had **Claim 7 dropped out of the table and truncated** mid-word at "(the number of t" — a write-truncation from when the .docx was originally generated (the source .md always held the full text, so nothing was lost). Fix: restored Claim 7 as a complete 8th table row ("…Tuppence-gated AI Services, and the AI Guardrail… the combination is the core protectable contribution."), deleted the stray truncated line. Verified by rendering page 14. Whitepaper §3 heading "▍" accents render as clean navy bars (not funny signs).
- `TrustSquare_WhitePaper_PUBLICATION.docx` (fixed) · sha256 `a0fe9390c1867b43a684a7bbe1300de22b491a9478699c616696cb4b1eab4cef`
- `TrustSquare_Provisional_FILING_with_Annex_2026-06-30.pdf` (rebuilt, 14 pp, A4) · sha256 `03bc5aa364b586e67c266b9b245432a3d7f02c0b86e640564b03b070ec4d112c` ← the file to upload
