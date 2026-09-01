## 2026-09-01 — RUL-086: cross-language introductions get Lane 2 (UGC translation)

David: introduced parties must translate effortlessly (Mandarin seller ↔ Portuguese
buyer). Registered RUL-086 + full CTO design in i18n/UGC_TRANSLATION_DESIGN.md: store
once in author's language + lang tag, translate-at-read via our own swappable adapter
(MT vendor = RUL-009, David's, at build time), pay-once cache per content-version+
target, hard monthly cap (pricing-canon compatible), machine-translated label with
one-tap original, scope listings → messages → dossiers (dossiers generate in target
language). Readiness item 8 added and probed DONE; rulings_check wired (86/86 green).
Sequencing: build sandbox-first with item 4, arm only after Phase C. Freeze intact —
nothing live-served touched. Readiness now 2/8, 59 days to 30 Oct.
