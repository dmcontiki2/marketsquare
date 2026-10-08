## 2026-10-08 — PHOTO-FIRST-1: an advert's first photo arrives first

David, 8 Oct: yes to the next step on the 6 Oct audit's F6 after MINIFY-1.

Measured on the Quick hand-over (/?listing=264) on a phone over Fast 3G: the advert showed at 6.2 s but its first photo only at 17.3 s, because all six gallery photos (120-244 KB each; the thumbs are the same files) and the Nearby Wonders pictures 2 000 px down the page downloaded at the same time and shared the line. (The page's "loaded" moment was never held up by pictures -- ms.js was the gate there -- so this is about when she sees the photo, not that number.) Now the first photo is fetched first and alone, at high priority; the rest of the gallery and its thumbs start the moment it has arrived, when she swipes, or after 8 s at most; a Wonders picture waits until she scrolls near it. Nothing is dropped, only ordered: the first photo now shows 1.8 s after the advert instead of 11 s. Ledger RG-0944.

Cost model impact: none.
