## 2026-09-20 — I18N-TRANSLATE-1: a Translate button in the main app, cached so each phrase is paid for once

David, 20 Sep 2026 (from the airport, offsite in the Cape): *"Please build the button in the main app please,
it worked well in the quick listing app."*

**The shape, which is his own design (19-20 Sep):** the Quick door speaks her language from the first tap, because
those are the few screens that decide whether she finishes. The main app stays English — English carries furthest —
and a reader who wants another language taps ONE button. Five choices: English, isiZulu, Sesotho, Afrikaans,
isiXhosa (RUL-149's four plus the Cape's fifth).

**Server — `POST /i18n/translate`.** Caps of 60 strings per call and 240 characters per string; every phrase is
cached in `i18n_cache` FOREVER, so the first reader of a phrase pays for it once and every reader after that is
free and instant; a per-day AI-call ceiling (`i18n_spend`, 400) puts a hard roof on spend; the model is chosen by
the baseline for the task tier and is never named in the code (David, 17 Sep). A failed or capped translation
returns what it has and the screen simply stays English.

**Client — `ms.js`.** A globe pill bottom-left, the same one that works on the Quick door; it walks the page's own
text nodes, keeps every original in memory so English is restored word for word, remembers the reader's choice per
device, caches translations in the browser as well, and re-translates content the feed loads later.

**What it never touches:** the EULA and terms (`data-notranslate` — RUL-143 keeps the English binding, with its own
checked translation), form inputs, and any string with no letters, so prices, scores, dates and numbers travel
unchanged.

Proven before shipping against a stubbed endpoint in a rendered phone-width browser: 1,371 strings translated on the
home screen, the language remembered, and English restored exactly. Ledger 407 / 0 regressed; predeploy strict ok;
CM/DB ok.
