## 2026-09-24 — STATUS-CARD-1: her WhatsApp Status card (proposal 2 of the casual-workers plan, inside RUL-146)

One tap after publishing — on the You're-live screen and on every live advert in the Seller Hub ("Share to
Status") — makes a 1080×1920 card: the role picture (or her own first photo), her first name (only when her own
session asks; the public read never carries a name), area, days and rate, the trust badge, a QR and the link with
`?src=status`. The share sheet gets the image + text on Android/iOS (Web Share with files); elsewhere the card opens
in a new tab and the text is copied. Two doors on every card: *Ask me on TrustSquare* and *Make your own advert —
free* (`/quick/?src=status`); services adverts also carry the "Make your own" line under the detail view
(`?src=status-make`). Renderer `status_card.py` (Pillow + `qrcode`, installed in the venv), route
`GET /listings/{id}/status-card.png` (live adverts only). Every arrival is counted by the existing `?src=` funnel.

Also this fragment: the model's mid run now uses the measured click rate (`PM.click.obs = 0.0037`, 2 human
clickers of 534 openers; David's decision 24 Sep) — the dashboard's pinned medians are the 29 Aug baseline and stay.
Posters ×5 languages (A5, QR + `?src=poster`, number line blank until the WORK number exists), the WhatsApp Business
greeting, the SA Youth / job-group texts and the Door 1 estate-gate pack are in CityLauncher/doors/.
