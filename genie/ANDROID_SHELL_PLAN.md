# Android shell for Quick — plan (David, 25 Sep 2026: "Plan it now")

**Why:** the web "Pass Quick on" (QUICK-PASS-1) already works on every phone through a QR and the phone's share
sheet. What a web page cannot do is be the radio: it cannot pretend to be an NFC tag and cannot talk
phone-to-phone over Bluetooth/Wi-Fi. A small Android shell adds exactly those two things and nothing else.

## What the shell adds
1. **Phones held head to head (NFC tag emulation).** When she opens *Pass Quick on*, the shell's native NFC
   service serves her single-use invite link as an NFC tag. She holds her phone to the other phone: an Android
   phone with NFC on opens the link, an iPhone XS or newer shows "Open in Safari". The receiver needs nothing
   installed. Both approvals stay: her flick opens the invite; the receiver taps Accept.
2. **Offline hand-over (Google Nearby Connections, Bluetooth + Wi-Fi, no data).** Between two phones that both
   have the shell: both people accept the connection, the invite travels, and the receiver's Accept is sent to
   the server when data returns. Payload is the invite token only (well under the 32 KB byte-payload limit).

## Shape (recommended): Trusted Web Activity + two native pieces
- **Trusted Web Activity (TWA)**: the Play Store app opens trustsquare.co/quick/ in Chrome itself, so she keeps the
  same sign-in, cookies and storage as the browser and every web fix ships without a store update.
- **Bridge**: the page and the native side talk through the TWA postMessage channel (Chrome 115+; the native
  side opens it). The page posts `{invite_url}`; the native side posts back `{nfc: ready|off, nearby: ...}`.
- **Native NFC service** (Android HostApduService serving an NDEF Type 4 tag with the invite URL; off when the
  Pass screen closes).
- **Native Nearby module** (P2P point-to-point strategy; both sides accept).
- Alternative if the TWA bridge proves brittle on budget phones: Capacitor (WebView + plugins). Cost: a WebView
  has its own cookie jar, so she would sign in once more inside the shell.

## Steps
| # | Step | Who |
|---|------|-----|
| 1 | Google Play developer account for TrustSquare (Pty) Ltd (one-time registration fee, about US$25) and the store listing | **David (money, listing)** |
| 2 | `/.well-known/assetlinks.json` served by the site (proves the app and the site are one owner) | Claude |
| 3 | TWA project (package `co.trustsquare.quick`), Quick's violet icon, signing key kept with the backups | Claude |
| 4 | NFC service + bridge; test Android→Android and Android→iPhone on two real handsets | Claude + one test phone pair |
| 5 | Nearby module; offline test (both phones in flight mode with Bluetooth on) | Claude |
| 6 | Internal test track → closed test with 3 cleaners → production | Claude builds; David approves release |

## Limits that stay
- An iPhone as the **sender** stays on QR / AirDrop: Apple does not let an ordinary app act as an NFC tag.
- Huawei phones without Google services cannot install from Play; they keep the web version (QR).
- Measure first: the web beacons `q_pass_open`, `q_pass_send`, `q_pass_accepted` show how often Pass it on is used
  and on which phones, before step 4 is started.
