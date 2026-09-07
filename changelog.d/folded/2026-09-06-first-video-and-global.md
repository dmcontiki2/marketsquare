## 2026-09-06 - First video published, and "global" replaces "South African" (RUL-104)

David created the TrustSquare YouTube channel and asked Claude to set up the first upload. Done in
his browser: film 01 (collectables), title, description, 14 tags, audience set to not-made-for-kids,
and **the AI-use disclosure set to YES** - the films use AI-generated people who look real, which is
exactly what YouTube's altered-content disclosure is for, so it was the honest setting and it was
taken without asking. Visibility set to Public; the Publish click itself is David's, as publishing
public content always is.

**Mid-upload, David caught a positioning error** in the description - "TrustSquare is a South African
marketplace" - and ruled it should say **global**. RUL-104. Corrected in the live description and in
all ten upload packages the same minute.

**Grepping for the phrase we had just corrected found something worse.** Seven AI system prompts in
`bea_main.py` tell the model *"TrustSquare, a South African marketplace"*: the pricing analyst, the
local market expert, the advert slot writer, the one-sentence seller helper and two Trust Score
coaches. Every US club we are emailing nightly lands on an app whose pricing analyst has been told
the market is South African. That is behaviour, not wording, and the honest fix threads the
listing's own country through seven call sites - which the app already knows (ADV_COUNTRY_CURRENCY,
RG-0001). Logged as **RG-0307 OPEN** rather than half-done in a session that was publishing a video.

**Two limits hit, recorded so the next session does not rediscover them:**
- `file_upload` is unavailable in this session, and the video is 61 MB against a 10 MB cap either
  way, so the file-picker steps (the video, and the custom cover image) are David's to click. Every
  other field can be filled by Claude.
- Pressing Escape inside the YouTube upload dialog closes the whole dialog. It saves a draft, so
  nothing was lost, but do not use Escape to dismiss the hashtag autocomplete - click a neutral spot.

Still open on the video itself: the custom cover image (needs the file picker) and clickable
external links, which YouTube gates behind a one-off channel verification.
