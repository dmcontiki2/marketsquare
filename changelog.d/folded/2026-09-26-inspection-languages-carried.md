## 2026-09-26 — Inspection follow-up: every language carried through the new wording; the QA bot reads the code it judges (INSPECT-FIX-3)

Found while verifying INSPECT-FIX-2 in the live app, not by the inspection itself:

- **Quick in isiZulu, isiXhosa and Sepedi went partly English** — the wave's whole-sentence keys were written in Afrikaans
  only, so the door line, the save step, the saved screen and the Buzz explainer fell back to English for three of the
  five live languages, and 14 lines that had been translated regressed. RUL-165 makes Claude's drafts the live versions,
  so every Quick phrase (478) and pattern (25) now carries Claude's isiZulu, isiXhosa and Sepedi, three save-step lines
  got their missing Afrikaans, and the door no longer tells those readers that categories are in English
  (window.QLANG_PARTIAL is empty; the notice returns by itself for the next language that is partial). Walked in all four
  languages with every write faked: door, draft, Buzz explainer, saved screen and menu show no English phrase.
- **Three Sepedi role names** lost their English words (langq-37): 'Mootledi wa Khoutu 10 / 14', 'Mootledi wa metšhene
  (TLB / motšhene wa go epa)', 'Mootledi wa thekisi / khombi' — Claude's words under RUL-165, for the Sepedi reader to confirm.
- **The app's reworded English** (introduction, sign-in link, the free plan's line, the trust levels the Seller Hub now
  names, the fresh-version bar's Refresh) got checked Afrikaans (migration 056) and Claude's isiZulu, isiXhosa and Sepedi
  drafts (migration 057), instead of the runtime machine lane; ms.js DICTV 5 so every browser drops its copy.
- **QA-SRC-LIVE-1** — the QA bot's rulings and appeals read `/var/www/marketsquare/bea_main.py`, a 12 Sep copy nothing
  updates (the manifest ships bea_main.py to main.py). Three appeals on 26 Sep were judged against code that no longer
  ran. `app_source()` now reads main.py first.
- **Deploy purge**: the first deploy of INSPECT-FIX-2 ran the OLD engine (it parses itself before the checkout), which
  purged without a key after the exemption was gone — 401, logged non-fatal. The CDN was purged by hand with the running
  app's key at 09:58Z; the new engine's key read was proven on the box (GET /dashboard/scan -> 200).

Ledger: RG-0325 re-aimed (the invited seller's city seed moved into sfNewState() when Sell stopped wiping a listing in
progress; the check followed it, red on a seed without the invited city, green on the old and new shape); RG-0499 LOCKED after the live check (every corrected Afrikaans word served live); RG-0501 (every Quick phrase in
all four live languages, the page equal to its source, no false 'still in English' notice) and RG-0502 (the QA bot reads
main.py) added, each proven red on a deliberately broken copy and green on the real files.
- **AI search help needs a sign-in (qa-15)** — the security judge, now reading the running code, kept its ruling that
  POST /search/interpret must require a signed-in person (a per-address cap is not proof of a person). The route is
  'user' level; plain search stays open to everyone, a signed-out caller gets 401 and the app keeps its plain results.
  AI search is switched off today (SEARCH_AI_ENABLED dark), so nobody sees a difference yet. The other two appeals
  (per-city advert counts, 'pass Quick on') were won once the judge read the right code; GET /quick/me was won earlier.
- **The paid green-tick card no longer sounds compulsory (langt-02 follow-up, ID-WORDS-2)** — the 25 Sep wording said
  buyers 'can only request introductions once you are verified' on the 1 Tuppence Home Affairs card. The server opens
  introductions once the seller's UPLOADED ID is confirmed (free); the paid check is optional (RUL-039). The card now
  says exactly that. The success screen already pointed to the free upload.
- **Session counter** brought up to date (208): the day's fragments had put it one sitting behind the evidence (RG-0154).
