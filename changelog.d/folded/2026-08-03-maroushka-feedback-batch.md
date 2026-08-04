## 2026-08-03 — Maroushka's six listings: what she reported, and the three faults behind them (MAROUSHKA-2026-08-03)

**Source.** Maroushka Conradie, founding seller (letting agent), by email after publishing 6 property
listings through the guided sell flow. Four points. All four confirmed against the code; two were
worse than she was able to describe, because the app gave her no way to see the rest.

**1 · "I couldn't go back and replace a photo once it was uploaded."** Two separate faults.
In the wizard, `sfPickFile` hard-refused a filled slot — `sfToast('Photo already added — it uploads
when you finish')` — with no remove control anywhere in the `sf*` namespace. A filled slot now
re-opens the picker and carries a ✕ (`sfClearSlot`), extras included, so the photo cap stops being a
one-way door (MAROUSHKA-PHOTO-1). Behind that: the post-publish 🔄 Replace button *said* "✓ Photo
replaced" and then wrote the **old** URL back, because `elReplacePhoto` patched the `<img>` and
`elCurrentRaw` but never `_elPhotoUrls` — the array `saveEditedListing()` actually serialises. Index 0
silently reverted; index >0 never persisted at all (MAROUSHKA-PHOTO-2). The Edit button was also
hidden entirely on any listing with a pending introduction, so a seller with live enquiries could not
reach the edit screen at all — condition removed.

**2 · "We charge a flat fee for these utilities but there is no option for it given."** Correct:
`SF_PROP_RENTAL_SEC_C` hard-coded three electricity options and two water options, none of them a flat
fee. Added, plus an explicit *Not applicable* (MAROUSHKA-UTIL-1).

**3 · "Additional services look to buyers like additional costs."** Her diagnosis was wrong and her
instinct was right. Blank fields never reached buyers — `sfComposeDescription` already dropped them.
But blank also scored 0 and triggered "Complete Tenant Costs & Responsibilities (n left)", which is
what pushes a seller to type something misleading rather than leave a true blank. *Not applicable* now
scores as a real answer and is suppressed from the buyer-facing description (MAROUSHKA-UTIL-2).

**4 · "It refused to upload or publish the listing. I don't know why."** She could not know why. The
guided flow never captures a seller email and has no field for one; with none, `goHandoff` skipped
draft creation and photo upload **in silence** (`if (BEA_ENABLED && goState.email)`), `POST /listings`
had no `else` on `res.ok`, failures went to `console.warn` on a phone, photo refusals — including the
400 an iPhone HEIC file earns — were swallowed by `.catch(() => null)`, and the only visible output was
`No draft found (drafts=0, email=none)` in 12px red. Every one of those exits now speaks, in a
seller's sentence rather than a developer's, and `sfFinish` asks for the email at the last moment it
can still be fixed (MAROUSHKA-PUB-1…6). Root cause of *her* specific failure is still unproven —
the app server logs live only on the Hetzner box — but the next attempt will now say what went wrong
instead of nothing.

**5 · "It doesn't give me an easy option for uploading my FFC and the mandate" / "I could not add my
agency info."** Also correct, and structural. The agent profile form had no agency field, no PPRA
field, no FFC field and no certificate upload of any kind — only a paragraph pointing at
*My Space → Trust Score*, a screen that cannot accept an FFC — while `_go_live_gaps` blocked her
profile for not having provided one. The profile now renders one upload row per credential slot the
vertical defines (server-supplied from `estate_agents.py`, so form and catalog cannot drift), posting
to `/users/{email}/documents` **with the correct `signal_id`**; previously the only reachable uploader
never sent one, so an FFC was filed by `_next_signal_for_doc()` as a Local-Market certificate and
earned the wrong points entirely. The agent's agency is resolved from membership and shown
(MAROUSHKA-CRED-1, MAROUSHKA-CRED-2).

**Also fixed, found en route.** Agency membership set `seller_tier='starter'`, so no user was ever on
the `agency` tier that `_SELLER_SUB_TIERS` and `_FADE_WINDOWS` define — agency agents silently got the
60-day fade window instead of 90 (AGENCY-TIER-1). `agency_members.status` was written `'invited'` at
invite time and never advanced; first successful sign-in now sets `'active'` and `joined_at`
(AGENCY-MEMBER-1).

**Status.** Local. Not deployed — `/TSL` is a separate, deliberate act.
