## 09 September 2026 — Genie cost model REV 2: my "open source = rent a GPU" assumption was wrong

David corrected rev 1 the same day: *"whenever i refer to open source you immidietly think of renting a GPU
server. I wont do that, it will be as simple as installing a Harness like Deepseeks, which runs on the PC,
with plug ins, with a Claude Pro, Open AI and Grok subscription, using deepseek API from Scaleway, and that
would be the expensive option, all options to be capped."*

Rev 1's whole GPU comparison ($785/month A100, 1 768/day crossover) rested on an assumption I made and he
never stated. It is **removed, not amended**. `MarketSquare/genie/GENIE_COST_MODEL.html` is now rev 2.

**Re-costed on his actual setup**, same `AI_BASELINE.json` v2.0 envelopes, DeepSeek published rates
(31 Jul 2026: V4 Flash $0.14/$0.28 per Mtok, V4 Pro $0.435/$0.87):

| Job (envelope) | Base lane | DS V4 Flash | Saving |
|---|---|---|---|
| triage 2 500/400 | $0.00098 | $0.00046 | 53% |
| haiku 4 000/1 800 | $0.00296 | $0.00106 | 64% |
| **design 12 000/4 000** | **$0.18000** | **$0.00280** | **98%** |
| free conversation (5 calls) | $0.0148 | $0.0053 | 64% |
| paid 5T dossier (earns $10) | $0.1948 (1.95%) | **$0.0081 (0.08%)** | 96% |

**The design tier is the entire cost story.** The base lane uses a premium model for the write-up at 18c;
Flash does the same envelope for under a third of a cent.

**The architecture point his correction unlocked, which rev 1 missed entirely:** the expensive call does not
have to be live. Journeys, question sets, dossier templates and advert drafts can be batch-written on his PC
via the harness + subscriptions he already holds, and shipped as data. Twelve journeys already exist; ~100
would cover most first-year requests. The live call then shrinks to the small routing one.

**Two constraints stated plainly in the page:**
1. Consumer subscriptions (Claude Pro / OpenAI / Grok) cannot serve trustsquare.co's users — they are for the
   holder's own use and there is no supported path. They belong on the **build** side, where they are correct
   and already paid for.
2. His PC cannot sit in the live request path (uptime). Hence: harness produces ahead of time, never answers
   a user.
3. **UNCONFIRMED:** could not verify Scaleway carries DeepSeek. Their supported-models page did not render;
   a provider comparison describes Scaleway as hosting Llama 3.3 and other open-weight models with no DeepSeek.
   Prices quoted are DeepSeek's own, not Scaleway's. Flagged to David — he holds that account. Matters beyond
   price: Scaleway was chosen for EU hosting; DeepSeek's own API is not that.

**Proposed additions to the 14 Aug lane ruling** (not applied — a ruling change is David's): a free lane is
base for the free conversation only and fails over *to* a paid lane, never the reverse; and the design tier
gets its own monthly ceiling, separate from the rest, since one call there can cost more than a hundred others.
