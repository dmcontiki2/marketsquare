# UGC_TRANSLATION_DESIGN.md — Lane 2: translating the introduction itself (RUL-086)
**Registered 1 Sep 2026 · design only — RUL-075 freeze untouched, nothing live-served edited**

Lane 1 (RUL-075) translates the app's CHROME with dictionaries. But MarketSquare's core
act is the introduction, and the introduction is user-authored: a Mandarin seller's
listing, the messages she exchanges with a Portuguese buyer, the dossier that carries
the handoff. David's requirement (1 Sep): translation between introduced parties must
be EFFORTLESS. That is runtime machine translation of user-generated content — a
different machine from dictionaries, designed here so the build is sandbox-ready.

## Decisions (CTO, per the specs that delegate them)

1. **Store once, in the author's language.** Every translatable content row (listing
   text, message body, dossier source) carries a `lang` tag — detected at write time,
   author-overridable. Translations are DERIVED, CACHED artifacts. The original is
   never overwritten and remains the authoritative text in any dispute — an EULA line
   says so at build time (counsel ratification = ordinary follow-up, not blocker,
   SS6.1A pattern).
2. **Translate-at-read through our own adapter.** One server-side endpoint
   (`translate(content_hash, src, dst)`); the MT supplier sits behind it, swappable
   per the supplier-fallback doctrine — no vendor is ever load-bearing. Vendor
   selection is RUL-009 class: David's, from the full field, at build time. The AI
   swap architecture (AI_SWAP_ARCHITECTURE.md) is the natural home.
3. **Pay once per pair.** Cache keyed `(content_version_hash, dst_lang)`. Listings
   translate once per edit per language, whatever the read fan-out; messages are
   short, so per-message cost is flat-ish. A HARD MONTHLY CAP on MT spend, panel
   probe when it nears. Flat + cappable = pricing-canon compatible; no ad-valorem
   anywhere. Feature pricing in fixed Tuppence, if charged at all, is David's call.
4. **Effortless UX, honest labels.** Each party reads and writes in their profile
   language (the Lane-1 language choice drives both lanes). Translation happens on
   delivery, both directions, automatically when the parties' languages differ — no
   per-message buttons. Every translated rendering wears a machine-translated label
   with one-tap access to the original (trust-brand honesty pattern, DEMO-banner
   style). Never hide the original wording.
5. **Scope order.** Listings first (cache-friendly, highest fan-out) → introduction
   messages/chat → dossiers (the dossier engine is parameterised, so it GENERATES in
   the target language via the AI lane rather than translating its output).
6. **Sequencing against the freeze.** Lane 2 only matters once users HAVE different
   languages, so: DESIGN now (this doc = readiness item 8) → BUILD sandbox-first
   alongside readiness item 4 (schema `lang` columns + translations cache table
   arrive as a migrations/ draft, ONE_DEPLOY pattern) → ARM only after Phase C is
   live. No live-app edit before David re-opens the build.

## Readiness item 8 contract
`scripts/i18n_readiness_check.py` marks item 8 DONE when this file exists and carries
its three anchors (store once / translate-at-read / machine-translated). The build
artifacts themselves are gated by items 4 (sandbox) and the Phase map, not item 8.
