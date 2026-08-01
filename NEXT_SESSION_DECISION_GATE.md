# Decision-gate process: BUILT 31 Jul late session (Addendum 8) — this file now holds only the leftovers

DONE same evening: Model Register v2 (prices + AA scores + golden-set status + policy on
the card) · price_truth.py funnel (value proposes / gate disposes / anti-jitter restrains)
· RG-0019 live-switch trigger · Addendum 8. First reading: sitting models win every tier
except sonnet (Medium +42%, held for 2 refreshes); Luna is the prize behind the gate.

STILL OPEN:
- OpenAI SERVER key + Luna/Terra golden set (pin effort — Luna 51 max / 33 low). This is
  the single highest-value action on the board.
- Scaleway free-tier monthly cap -> record on the card when found.
- P2a build, preceded by design v1.2 (MUST include Correction 2: executable pre-dispatch cost rails — max requests/retries/fallbacks, token + currency budgets, worst-case charge computable before dispatch; plus full-sweep findings: T1 consecutive state,
  async-safe heartbeat, _anthropic envkey consistency, timeout stacking).
- Sandbox ban drill after key + golden set.
- Monthly: /housekeep runs price_truth.py --check (RG-0018/0019 already enforce via ledger).
UPDATE 1 Aug (later): +1 dashboard ops layer BUILT (funnel strip order+types, manual pin w/ 24h decay, RG-0020) — needs DEPLOY (bea_main.py + apply_ai_provider_card.py run on the server dashboard + ai_funnel_snapshot.json shipped). TTL review ~1 Nov 2026 (1h candidate).
