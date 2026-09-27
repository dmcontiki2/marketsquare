## 2026-09-27 — TRUST-WORDS-1 (CC-005, RUL-186, RG-0526): Trust Score bands name the evidence, not the person

- Labels everywhere: New · Some evidence (40+) · Strong evidence (70+) · Fullest evidence (90+) — replacing Established / Trusted / Highly Trusted (ms.js trustTier, sbScoreBadge, detail labels, tier showcase, filter chips in both filter rows, next-band nudge; quick.html trustBand; Terms table in eula_clean.html, terms.html and the embedded copy; bea_main.py TRUST_TIERS and the AI coach's labels and prompt).
- Both trust bars and the Local Market filter guidance now carry the two approved lines: the score explainer and the new-seller line.
- Afrikaans, isiZulu, isiXhosa and Sepedi for every new phrase (app_i18n_* + quick_i18n.json); migration 062 loads them into the translation cache.
- CHANGE_REGISTER CC-005 → DONE. Built by scripts/apply_trust_words.py (exact-match, refuses on drift).
