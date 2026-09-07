## 2026-09-06 - Captions were the fourth place the currency showed up

David, watching the live video: *"the video subscript still says Rands while the video shows
Dollars"*. Correct, and it was a place nobody had looked. YouTube auto-captions transcribe the
SPOKEN words - and the whisper pass earlier the same day had already established that three of the
ten films say a rand amount out loud (01, 08, 10). The auto-captions also render the brand as
"truss square".

**What was NOT done, and why:** the caption was not changed to say dollars. Captions are what a deaf
viewer reads instead of hearing the audio; making them say something that was not said is not a
translation, it is a fabrication. The rule held even though the ask was David's.

**What was done:** a hand-written English caption track for film 01, published the same minute, with
the brand name correct and the dollar figure as a bracketed annotation beside the spoken rand
amount - standard captioning practice. Entered through Studio's **Auto-sync**, which times a pasted
transcript against the audio, so there was no per-line timing work.

**And made repeatable:** a corrected transcript for ALL TEN films is now written into
`scripts/youtube_pack_build.py` and emitted in every package's `metadata.md` under "Captions - paste
this into Subtitles > Auto-sync". Every future upload is a paste, not a discovery. The two other
films that speak rand (08 weekend, 10 offer) already carry their bracketed conversion.

Four places the currency had to be handled, all now closed: the title and cover, the description,
the picture inside the film, and the captions.
