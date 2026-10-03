## 2026-10-03 — PASSKEY-PHONE-1 + HUB-GHOST-1: Face ID offer on phones only; the Hub drops adverts the server no longer has

David, Seller Hub on his laptop: *"The face id and fingerprint message should not show on laptops or computers but only on
phones"* and *"i can not delete the 'aflewerings ryer', this is an old recurring issue."*

- **PASSKEY-PHONE-1 (ms.js):** the only device test was `isUserVerifyingPlatformAuthenticatorAvailable()`, which Windows Hello
  and Touch ID answer yes. `pkPhone()` (the browser's `userAgentData.mobile`, else an iPhone / Android-phone user agent) now gates
  `pkOn()`, so a laptop, desktop or tablet gets neither the Hub offer nor "Sign in with Face ID or fingerprint". Server unchanged.
- **HUB-GHOST-1 (ms.js):** #473 "Afleweringsryer — Menlyn, Pretoria East" was deleted on the server at 18:45:27Z. His open Hub
  read `/listings/mine` twice afterwards (18:48:23Z, 18:49:22Z) and kept the card, because `loadLiveDash` only ever added or
  refreshed cards and never removed one; Delete at 18:49:03Z got 404 and showed "Error: Listing not found". Now every good
  `/listings/mine` answer prunes the Hub to the server's list, an introduction cannot bring a deleted advert's card back, and a
  404 on Delete removes the card ("Listing removed — it was already deleted").
- Why it kept coming back: each earlier delete fault (22 May empty email, 23 Sep DELETE-BIND-1, 24 Sep DEL-STUCK-2) was fixed at
  the button; the Hub's own copy of the list was never reconciled with the server, so any advert removed elsewhere stayed as a
  ghost that no button could clear.
- Ledger RG-0807, RG-0808 (each proven to fail on a mutated copy); FEEDBACK F-026, F-027.

Cost model impact: none. Schema: none.
