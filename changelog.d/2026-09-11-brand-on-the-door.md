## 2026-09-11 — The TrustSquare lockup on every category door, and nowhere after it

David: *"We should have the TrustSquare logo displayed across all of the category first screens at
the top, not the follow up screens; lets keep them as uncluttered and simple as possible."*

Built into `genie/HARNESS.html`. The lockup sits at the top of all eight category doors and
disappears the moment a flow starts — the step dots take its place in the same bar, so nothing
shifts and the bar never changes height. Verified: logo on the door, gone on step one, gone on the
draft, back on return.

**New asset: `Marketsqaure logo/TrustSquare_BrandLogo_transparent.png`.** The existing
`TrustSquare_BrandLogo_TM.jpeg` is white-and-green on a **solid black square**, so it cannot sit on
any of the eight coloured washes without showing a black box. The transparent version was derived
from that exact artwork — alpha from luminance, colour un-premultiplied — so it is the same drawing,
not a redraw. Use it anywhere the background is not black.

**A write was lost, and it is a class problem.** The "what the harness is for" section committed on
10 Sep was gone from `genie/README.md` by the 11th — no error, no conflict, last writer wins. That
is exactly the failure `CHANGELOG.md` and `STATUS.md` have fragment compilers to prevent, and this
file has neither. Restored, and recorded in the file itself as README-COLLISION-1: re-stage
immediately before writing, never write from a copy staged earlier in the session, always commit
with the mtime guard.
