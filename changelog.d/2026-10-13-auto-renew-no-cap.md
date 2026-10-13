## 2026-10-13 — QA Bot RED review of auto-renew closed; no end date on auto-renew (RUL-227)
- QA-RED-AR-1: plan checkout starts only as the signed-in seller (handler + route_policy user/bind). PROBED live 13 Oct 05:20 SAST: stranger -> 401.
- QA-RED-AR-2: renewal state (on/cancelled/failed) shown only to the owner or admin key. Live app: David's own plan card still carries it.
- QA-RED-AR-3: a 12-charge cap was added and REVERSED the same morning by David (RUL-227) — auto-renew renews until she cancels. Finding answered by RUL-224 (one-tap cancel, fixed plan price, disclosed "until cancelled").
- Ledger RG-0971 locks all three, including that no end date returns.
