## 2026-09-06 - The ten films get a posting plan, and a way to tell if it worked (VIDEO-LAUNCH-1, CAMPAIGN-SRC-1)

David asked what the plan is for launching the videos against the onboarding goal. There was not
one: RUL-103 (5 Sep) had found ten finished 4K films unpublished and set the channel order, and a
session had packaged film 01 the same night, but nine films had no package, nothing was scheduled,
and -- the part that mattered -- **nothing could have been measured**.

**The measurement fault, found by reading the code.** ms.js captured `?src=` and fired the
`landed` beacon inside `if(sp.get('magic')==='1')`. That gate is the invite link. A person
arriving from a YouTube Short carries a src but no magic, so the whole block skipped them: the
funnel would have shown nothing, and "did YouTube work" would have been answered by opinion.
RUL-096(b) scores the goal by probes that must agree, never by self-report -- so an unmeasurable
channel is not a channel, it is a story. **CAMPAIGN-SRC-1**: a public arrival carrying `?src=` now
records the source and beacons once. `magicLink.active` stays false -- no routing, flow or UI
change, and `cat` is deliberately not set, because pre-selecting a category for a stranger is a
product change rather than measurement and should wait for evidence.

**The packages.** `scripts/youtube_pack_build.py` (new, reusable) builds the upload package for
each film: three titles at 60 characters or under, a description with beats read off a frame strip
of the finished cut, 14 tags, a pinned comment, an end-screen line, and a 1080x1920 cover. Nine
built; film 01's hand-built package retro-fitted with its tracked link. Two faults caught by
looking at the output rather than trusting it: eleven titles ran 61-68 characters (fixed), and
ffmpeg drawtext cropped five covers because it cannot measure text -- the cover is now drawn with
PIL, which can, and auto-fits (verified by eye at thumbnail size).

**Every link is tracked.** `https://trustsquare.co/?src=yt-05-car` and so on, one tag per film, so
`GET /onboard/funnel?days=7` answers per film: how many landed, how many went further.

**QC, all ten (PROBED).** 2160x3840 h264 + aac 44.1 kHz stereo, 42-69 s, mean volume -20.8 to
-21.7 dB with peaks near 0, no mid-film black. Six fade to black over the last ~0.9 s, four end
hard -- cosmetic, nothing blocks posting.

**The schedule** is in LAUNCH_SERIES.md: two a week, Tuesday and Friday 18:00 SAST, strongest hook
first, the matric study-plan film pulled early because "six weeks to finals" only lands before
finals. That empties the shelf by 9 Oct, three weeks inside the 31 Oct goal date -- deliberate,
because a film posted in the last fortnight cannot compound. The earlier "one a week" line was a
session's editorial, not David's ruling; ten weekly films would have run to 10 Nov, past the goal.

**What is NOT done, and it is the only thing:** there is no YouTube channel on record anywhere on
disk, and the connector registry has no YouTube connector (searched today), so posting cannot be
automated even in principle. Creating the account is David's act; the channel's name, handle and
positioning are launch scope, his under RUL-103(f).

Ledger: **RG-0301** LOCKED -- the app records a campaign src on a public arrival, and no upload
package ever ships a bare trustsquare.co link. Same family as RG-0299: two lists that must agree,
failing silently when they drift.
