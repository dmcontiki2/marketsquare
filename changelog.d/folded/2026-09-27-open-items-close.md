## 2026-09-27 — Watch open items closed: LANG-COST-RAIL-1 (DW-149), payment verdict re-pointed (DW-158), CC-002 superseded

- `bea_main.py` `_lang_ai()`: the second-language listing draft now checks the platform AI ceiling before each call and logs every call's real tokens (same pattern as I18N-COST-RAIL-1). Cost sweep exit 0 (was 1). Ledger RG-0525.
- Daily watch task: the payment verdict now comes from the server's subscription monitor (Paystack row: UP + key ok). `/payment/test` is admin-only by design since SEC-GATE-1, so its 401 is no longer read as blindness.
- `CHANGE_REGISTER.md` CC-002: SUPERSEDED by RUL-107 + PRICING_CANON — its staged package targeted the retired five-tier model and was never landed.
