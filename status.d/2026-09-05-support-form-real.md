### The support form was a black hole — found on David's question, fixed and proven (5 Sep 2026)

134 visitors, a live listing bug, zero complaints. David asked us to check Support rather than take the
silence as good news. `support.html` was a placeholder: it showed "✅ Message sent" and posted nothing,
its inputs had no `name` attributes, and the `mailto:` fallback did nothing on a desktop with no mail
client. Since 29 Aug (RUL-064) that page was the customer complaint lane.

Fixed: `POST /support/message` stores into `app_faults`, emails David, acks the sender, anonymous by
design (RUL-100), row committed before either email. The page only says "sent" when the server confirms.
PROVEN: **TS-0036** submitted live, row present, both emails read back out of Gmail. Locked as **RG-0282**.

Also fixed on the way: `showToast` ignored its duration argument at 13 call sites (**RG-0283**), and the
publish failures were dead ends — they now name trustsquare.co/support.

Confirmed working and left alone: support@trustsquare.co delivers to David's Gmail in ~12 s.
Coverage map: 66 green · 0 blue · 0 amber · 0 red · 10 grey (76 cards).
