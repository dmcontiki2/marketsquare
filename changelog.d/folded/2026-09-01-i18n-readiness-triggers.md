## 2026-09-01 — I18N readiness TRIGGERS wired (RUL-075 lane)

Readiness is now measured, not remembered. New scripts/i18n_readiness_check.py probes
all 7 I18N_READINESS.md items (1/7 done at first run — inventory; 59 days to target)
and defines the artifact contract each future build must satisfy. Two one-off scheduled
tasks created: i18n-readiness-midpoint (Thu 1 Oct 09:00 SAST — gap report + progress
next item) and i18n-readiness-day (Fri 30 Oct 09:00 SAST — READY/NOT-READY verdict;
if READY, David's single decision is opening sandbox testing). Triggers section
appended to I18N_READINESS.md. Freeze intact — nothing live-served touched.
