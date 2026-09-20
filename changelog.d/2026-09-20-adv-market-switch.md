## 2026-09-20 — ADV-CO-CHIP-1c: the home-page market switch reaches Adventures again

David, same evening, after ADV-CO-CHIP-1 shipped: *"i changed to US in the home page, then went
to adventures where the switch did not happen, it was still anywhere with a rand value, or it
was still stuck in ZA?"*

**He is right, and it was this morning's fix that did it.** ADV-CO-CHIP-1 read the city sync in
`selectDemoCity` as the thing pinning South Africa and removed it. That was wrong. The pin was
the hardcoded ZA chip literal plus a boot default of Pretoria — both already fixed. Removing the
sync as well cut the one link that makes a market switch mean anything: switching the home page
to the United States left Adventures exactly where it was.

**Restored, through one writer.** The explicit market switch — `selectDemoCity` and the real geo
`selectCountry` — now calls `selectAdvCountry`, which persists the choice, repaints the chip and
re-renders. No direct assignment to `advCountry` anywhere, so the markup and the filter cannot
drift apart again (that split was the original fault).

**BORDERLESS-COUNT-1 stands.** Nothing in that path runs at boot, so a visitor who has chosen no
market still opens on *All countries*, and the ZA exemplars no longer sit in a block at the top
(ADV-CO-CHIP-1b). The borderless default is what you get until you choose; choosing is what
moves it.

**RG-0425 amended the same day** — a design-phase amendment, not a broken rule. It now asserts
BOTH halves: no hardcoded country in the markup, and the market switch actually reaching the
adventures list. The earlier clause, which would have failed the restored sync, was replaced by a
one-writer clause; the entry's ref records why.
