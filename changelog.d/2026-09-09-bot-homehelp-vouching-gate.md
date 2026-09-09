## 2026-09-09 — Home Help BOT, third pass: the vouching gate built, and visibility split into three tiers

David endorsed the safety rule and named the reason that matters most: *"This also protects her,
which matters more and is easier to forget. A listing that puts a woman's open days and her suburb
in front of anybody at all, with no accountability on the other side, is not a service to her."*
It was one sentence on her listing. It is now machinery, with a fifth screen — **A stranger** —
showing the marketplace from the other side before and after somebody vouches.

**Absent, not greyed out.** Before any vouching a buyer searching "housekeeping, Menlyn, Wednesday"
does not see her at all. A visible-but-locked card still leaks her free days and her area to anyone
who looks, which is the harm the gate exists to prevent. After one employer confirmation she appears
at 85 with an introduction worth 1 Tuppence.

**Three tiers, not two** (RUL-115):
- PUBLIC once vouched — the trade, **the suburbs she travels to**, her rate, her free days, her
  rating, her photos.
- ON ACCEPTANCE — her full name, her phone number, **the area she lives in**. That release is what
  the Tuppence buys, and she can refuse it.
- NEVER PUBLISHED — her ID document, and **the identity of the employer who vouched**.

**Publish where she works, not where she lives.** The first version published Mamelodi as her main
area. A buyer in Menlyn needs to know she can get to Menlyn; they do not need to know where to find
her. Home suburb now matches internally, shows to her, and releases only on acceptance.

**The voucher is never named** — "confirmed by an employer of 3 years", not "confirmed by Mrs van
Wyk". If vouching cost the employer their own privacy, far fewer would vouch and the cold start dies
with it. **Taken days** show to strangers as unavailable only; whose house she is at is not published.

Class ruling, not a Home Help feature: any category where a seller admits a stranger to their home,
or is exposed by their own listing, inherits it.

Verified in a rendered browser: pre-vouch DOM contains neither her home suburb nor the voucher's
name; post-vouch DOM shows her travel-to suburbs and free days and still contains neither. Passes
one and two still green. Console clean.

Files: `genie/bots/homehelp/BOT_HOMEHELP.html`, `genie/bots/README.md` (THIRD PASS), `RULINGS.md`
(RUL-115). Design only — nothing wired, no flag, no deploy manifest line.
