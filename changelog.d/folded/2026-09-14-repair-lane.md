## 2026-09-14 — The repair lane: the banner stops lying, and the worker is finally registered

Both faults were found on the live site on 13 Sep and neither was actioned then. They are repaired
now and deliberately NOT held by the baseline batch — [[RUL-126]] governs design, not repair.

### OFFLINE-TRUTH-1 — the banner could never be talked down

The old code raised the banner on a bare `offline` event and lowered it only on an `online` event.
One spurious event pinned *"You're offline — browsing cached content"* to the top of the app for
good, which is exactly what David read while `navigator.onLine` was true and same-origin fetches
returned 200 — on the screen where his listings looked empty, so the app was pointing him at his
router instead of at his account.

Fixed at the class rather than at the symptom: **the banner re-proves itself.** It rises only after
a real same-origin probe fails, and while it is up a probe runs every four seconds and takes it
down the moment the network answers — no event required. The copy is corrected too: the service
worker caches nothing by design (RG-0358), so the banner no longer promises cached content that does
not exist. It now reads *"You're offline — some things won't load"*, in `ms.js` and in the static
markup.

### SW-REGISTER-1 — three green entries, and the feature still could not happen

`navigator.serviceWorker.controller` was **null** for every visitor. The worker was served
(RG-0356), had a fetch handler (RG-0358) and could sign a push (RG-0359) — but the only
`register()` call in the app sat inside the push opt-in. Anyone who had not opted into push had no
controller at all, so Chrome could never fire `beforeinstallprompt`, and **RUL-123's
add-to-home-screen offer and RUL-122's web push were both finished and both unreachable.**

Three ledger entries were green while the thing they exist for was impossible. The gap: not one of
them asserted REGISTRATION. `_msRegisterSW()` now runs from `_msInit()` on every page load, wrapped
so a failed registration can never break app start; the push lane keeps its own call, and
`register()` is idempotent.

### Proven in a rendered browser, not read off disk

Headless Chromium at 412×915 against the edited files:

- one registration after a plain page load; the worker **controls** the page on the next navigation;
- no banner while online; a **spurious** `offline` event while online no longer raises it;
- a real outage does raise it, with the corrected copy;
- with the network restored and **no `online` event ever dispatched**, the probe flipped it to
  "Back online ✓" within 4s and it retracted on its own.

New ledger entries **RG-0363** (banner cannot latch) and **RG-0364** (worker registered at app
start) both run green. `node --check ms.js` clean. `ms.js?v=` bumped 488 → 489.

### Not deployed

`git status` carries another session's in-flight work today — `bea_main.py` (+246), `ms.css` (+38)
and `genie/HARNESS.html` — and a deploy would carry it. Stated rather than assumed: the deploy is
David's to time.
