## 2026-10-24 — PHOTO-TOOLS-1 + NY-EX-PICS-1: a second photo supplier (Atlas Cloud) and 85 New York example photos

- David opened an Atlas Cloud account (pay-as-you-go, US$25, auto top-up OFF). New lane `--provider atlas` in scripts/gen_role_pictures.py; key in .secrets/atlas_api_key.txt (gitignored), never printed.
- Fair test, 5 subjects drawn at random from the 85, same prompt on 5 models: Soul 2 and Z-Image Turbo broke the no-text rule; GPT Image 2 (low) and Marketing Studio Image passed at ~US$0.011; Grok passed at US$0.040. Visual: Visuals/NY_Example_Photos_Compare_2026-10-24/fair_test.html.
- MEASURED on the Atlas bill: GPT Image 2 low = US$0.0109, high = US$0.2157. Atlas's "flat US$0.008 any quality" claim is false. Default is now low.
- 85 photos (17 groups x 5) in assets/ny_ex/, every one checked by eye; 2 redone (laptop instead of piano, collage cabin). Coins: no dates or lettering (David: no coins with dates that do not exist). Cards: 5 of David's own MtG photos (EXIF/GPS stripped) as col_cards_1..5.
- Ops dashboard: new "Photo tools" card (Atlas Cloud + Higgsfield), grey NOT MEASURED because the keys live on David's PC, not the server.
