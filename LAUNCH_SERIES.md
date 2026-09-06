# LAUNCH SERIES — MarketSquare video calendar

*Corrected 5 Sep 2026 (RUL-102/103): ten finished 4K films were sitting unpublished while this file
called every YouTube entry an "idea". Status here means what is ON DISK, verified by ffprobe.*
*6 Sep 2026: all ten now QC'd and packaged, every link tracked, and the posting order below is set.*

## THE PLAN IN ONE PARAGRAPH

Ten finished Shorts exist. Nine were unpackaged; they are packaged now, and every one carries a
tracked link (`?src=yt-NN-name`) so the funnel can say which film sent a person and whether that
person listed anything — visibility is a co-equal output (RUL-103) but the goal is still the 20
publishers by 31 Oct (RUL-096). Posting runs Tuesday and Friday at 18:00 SAST from the day the
channel exists, strongest hooks first, seasonal ones in their season. That empties the shelf by
9 Oct, three weeks before the deadline, which is deliberate: a film posted in the last fortnight
cannot compound. **The one thing not on disk is the channel itself** — see THE ONE BLOCKER below.

## QC — all ten pass (PROBED 6 Sep 2026)

`ffprobe` on every finished cut: 2160×3840 h264 + aac 44.1 kHz stereo, 42–69 s, mean volume
−20.8 to −21.7 dB with peaks near 0 (consistent master across the set), no mid-film black. Six of
the ten fade to black over the last ~0.9 s; four end hard. Cosmetic only — nothing blocks posting.

## THE SCHEDULE

Cadence: **two a week, Tuesday and Friday 18:00 SAST.** Not the earlier "one a week" note — that
was a session's editorial, not David's ruling, and it does not survive contact with the deadline:
ten weekly films would run to 10 Nov, ten days past the 31 Oct goal date, so the last three could
not contribute at all. Two a week also gives a new Shorts channel something to test, which one
video a week does not. Dates assume the channel exists by Tue 8 Sep; if it lands later, the whole
column shifts by the same number of days — the ORDER is what matters.

| slot | date (18:00 SAST) | film | why here | tracked link |
|------|-------------------|------|----------|--------------|
| 1 | **PUBLISHED Sun 6 Sep** | 01 · Collectables | strongest single number in the set ($1,505 for one card) | `?src=yt-01-collectables` · [live](https://youtube.com/shorts/oULMIsCAPnk) |
| 2 | Fri 11 Sep | 05 · Car | biggest ZA search volume — Hilux, price check, known faults | `?src=yt-05-car` |
| 3 | Tue 15 Sep | 09 · Exam study plan | **seasonal** — "six weeks to finals" only lands before finals | `?src=yt-09-exam` |
| 4 | Fri 18 Sep | 08 · Weekend | cheapest, most shareable, most local | `?src=yt-08-weekend` |
| 5 | Tue 22 Sep | 04 · Property | high-intent audience, biggest ticket | `?src=yt-04-property` |
| 6 | Fri 25 Sep | 10 · Offer strategy | shortest and punchiest; good re-cut source | `?src=yt-10-offer` |
| 7 | Tue 29 Sep | 07 · Liquidation | the seller-side film — closest to the onboarding number | `?src=yt-07-liquidation` |
| 8 | Fri 2 Oct  | 02 · Heritage tour | travel block starts | `?src=yt-02-heritage` |
| 9 | Tue 6 Oct  | 06 · Retirement | narrow audience, high intent | `?src=yt-06-retirement` |
| 10 | Fri 9 Oct | 03 · Expedition | most aspirational — good note to end the first run on | `?src=yt-03-expedition` |

After 9 Oct the shelf is empty. What keeps the channel alive: **11 · Aunty Ester tutor spotlight**
(script + prompts ready, not shot) and **UGC shorts wave 1, S1–S7** (`shorts/SHORTS_WAVE1.md`,
spiel-ready). Neither is made; both are cheap next to a new feature film.

## CURRENCY — the films read in dollars as well as rand (David, 6 Sep 2026)

The YouTube audience is global, so the money has to be legible to someone who does not think in
rand — and none of it could be re-done in Higgsfield. David chose **show both**.

What was measured before anything was changed: all ten films were transcribed. **Three of them say
a rand amount out loud** — film 01 ("twenty-four thousand rand for one card"), film 08 ("under a
thousand rand") and film 10 ("is R4,500 fair", and again in the narration). In those three,
*replacing* rand with dollars would have made the picture argue with the soundtrack. Showing both
cannot.

What changed, and only this:

- **The input screen** of six films now reads `R420,000 · $25,400` (and equivalents). The field is
  static for the whole window, so the patch is drawn in the insert's own font and field colour,
  inside the field border. Films 04 and 07 have no money on their input screen.
- **The report screen** scrolls rand figures for about ten seconds and cannot be re-typed without
  rebuilding the film, so a line sits in the empty navy band beneath the phone:
  `prices in rand · $1 = R16.5`. Every figure on screen then converts.
- **Nothing else.** The audio is stream-copied — decoded audio of each new cut is byte-identical to
  its master, which is the proof no seam was introduced.
- **Rate: R16.52 = $1**, which is the rate film 01's own report already prints. The app shows both
  currencies in its reports, so the films now match the product rather than contradicting it.
- **Film 01 needed nothing** (its report already prints R and $ side by side with the rate) and
  **film 09 has no money on screen at all**.

The cuts to post are the `-USD.mp4` files; each package's first line names the exact file. Rebuild
them with `python3 scripts/usd_dual_patch.py --only 05-car`. Originals are never modified.
Ledger RG-0302 asserts every package names its dual-currency cut.

Titles, thumbnails and descriptions are in dollars throughout, and the ZA-narrow search tags were
broadened (the genuinely South African ones — Kruger, CAPS, matric, the D7 visa — stay).

## THE PACKAGES — all ten ready

Each film's folder carries `<cut>_youtube/` with `metadata.md` — its first line names the file
to upload — plus (three titles ≤ 60 characters,
description with beats, tracked link, 14 tags, pinned comment, end-screen line, publish slot) and
`thumbnail.jpg` (1080×1920 cover). Rebuild any of them with
`python3 scripts/youtube_pack_build.py --only 05-car`.

Posting one is: open `metadata.md`, pick a title, upload the mp4 as a Short, paste the description,
paste the tags, post the pinned comment. Two minutes.

## THE CHANNEL EXISTS — first film live 6 Sep 2026

David created the TrustSquare channel himself on 6 Sep and published film 01 the same afternoon:
**https://youtube.com/shorts/oULMIsCAPnk** — title "Six old Magic cards. $2,574. Priced and listed
in a minute", tracked link in the description, 14 tags, not-made-for-kids, and the AI-use disclosure
set to YES (the films use AI-generated people who look real; that is what the setting is for, and it
applies to every film in this series).

Two things stay open on that video, and on every one after it:

1. **The custom cover image** needs the Windows file picker, which Claude cannot drive (and the
   file-upload tool caps at 10 MB, so the video itself is the same story). Everything else on the
   upload form Claude can fill. It is NOT behind the verification gate -- film 01's cover was
   uploaded and saved on 6 Sep and is live, PROBED on the video details page.
2. **Channel verification gates BOTH the clickable link and pinning a comment.** Phone
   verification is not enough -- YouTube's "advanced features" gate wants a six-second video of the
   owner, a photo of an ID, or about two months of channel history. David submitted the six-second
   video on 6 Sep; **it is in review, a few hours**. Until it clears, the link in the description is
   plain text and the funnel under-counts, and the pinned comment (posted 6 Sep, not yet pinned)
   cannot be pinned. First thing to do once it clears: pin that comment and confirm the link is live.

Publishing itself is always David's click — Claude sets the whole form up and stops there.

## WHAT WAS THE BLOCKER — the channel (closed 6 Sep 2026)

There is **no YouTube channel on record anywhere on disk**, and no YouTube connector exists in the
registry (searched 6 Sep 2026), so posting cannot be automated even in principle today. Creating
the account is David's act, not Claude's — and the channel's name, handle, banner and positioning
are launch scope, which is his under RUL-103(f)/RUL-096(f). Everything else is done and waiting.

## MEASUREMENT — how we will know if any of this worked

Each film has its own src tag, and CAMPAIGN-SRC-1 (6 Sep 2026) makes the app record a `src` on any
public arrival, not only on invite links — before that fix a viewer arriving from a film was
invisible to the funnel and YouTube's contribution would have been pure guesswork.

- `GET https://trustsquare.co/onboard/funnel?days=7` — `by_src` carries a `yt-*` row per film.
- A film that sends nobody says so plainly; a film that sends people who all stop at `landed` is
  the same fault class as RG-0299 and gets the same treatment.
- Ledger: RG-0300 asserts no package ever ships a bare link, and that the app still records src.

## CHANNEL ORDER (RUL-102/103, David 5 Sep 2026)

**YouTube → Twitter/X → possibly content creators and digital marketers.** The third step is
explicitly tentative and is not built ahead of his word.

## NOT YET MADE

| # | title | goal | platform | status |
|---|-------|------|----------|--------|
| 11 | Seller spotlight — Aunty Ester, 83 (tutor) | trust + recruit | YouTube | script + prompts ready, `feature-videos/11-tutor-spotlight/` |
| 12 | Study Abroad — know before you go (full length) | feature | YouTube + app | SHELVED (RUL-043) until the dossier spec is approved |
| 13 | Work Abroad — the matric gap year, honestly | feature | YouTube + app | SHELVED (RUL-043) — script after spec |
| — | A LANDSCAPE main-feed piece | awareness | YouTube | **not made.** Everything finished is vertical; do not assume a main-feed channel is stocked |
| S1–S7 | UGC shorts Wave 1 | reach | Shorts / TikTok | spiel-ready, `shorts/SHORTS_WAVE1.md` |

In-app set: LIVE baseline (introduction v2 shipped 12 Jul + how-to library).
