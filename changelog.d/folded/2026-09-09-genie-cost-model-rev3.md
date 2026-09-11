## 09 September 2026 — Genie cost model REV 3: two more of my assumptions corrected

David, same evening: *"I used my PC as an example, it will reside on Hetzner server, and the three
subscriptions are not the plug ins, the plug ins will be actual API AI's. The three subscriptions is Claude
the backbone, Open AI an independent test ground and auditor, and Grok which i may use for video's and
Graphics as well as for security."*

Two errors of mine, both removed from `MarketSquare/genie/GENIE_COST_MODEL.html` rather than amended:

1. **Rev 1** costed a rented A100 at $785/month, assuming "open source" meant self-hosting a model.
2. **Rev 2** placed the harness on his PC and had it driving his three subscriptions, then spent a whole
   panel explaining why consumer subscriptions cannot serve app users and why his PC cannot be in the live
   path. Neither objection applied — the harness runs on the **Hetzner server**, its **plug-ins are API
   models**, and the three subscriptions are **his own bench**, never in a visitor's request path.

**The corrected architecture, as recorded on the page:**
- Hetzner runs the **harness** — routing software only. It holds no model, so it is light on the box.
- The **plug-ins are API models** (DeepSeek, the free lanes). This is the only thing with a bill attached.
- **Ahead-of-time work** (journeys, templates) runs on the same harness on a queue, served afterwards as
  plain data — the pre-computation point from rev 2 survives, it just runs server-side, not on his PC.
- **His bench, separate:** Claude the backbone; OpenAI an independent test ground and auditor; Grok for
  video, graphics and security. No per-user cost; appears nowhere in the figures.

**The per-call arithmetic is unchanged by either correction** — envelopes from `AI_BASELINE.json` v2.0,
DeepSeek published rates. Design tier $0.18 → $0.0028 (98% cheaper) remains the whole cost story.

**Rev 3's watch list replaces rev 2's two dead objections:**
- Scaleway/DeepSeek still **UNCONFIRMED** (unchanged from rev 2; David holds the account).
- **n8n is already a harness on that box**, self-hosted in Docker. Worth deciding once whether plug-in
  routing belongs inside it or beside it — two schedulers on one small VPS is invisible until both are busy.
- Batch write-ups and live requests share the same CPUs; the batch queue needs a lower priority and an
  off-peak window.
- **Caps must live in the seam, not per plug-in.** Three lanes each under their own ceiling can still total
  past his. Capping everything is his stated condition, so this one matters.
