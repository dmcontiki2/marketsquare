## Current Session

**The Email Templates view now shows the letters that actually send — and the launch special that
should have closed on 1 Sep is closed.** David asked whether the Ops Dashboard's email templates were
the latest. They were a 23 Aug snapshot of a folder nothing sends from; the sending copies
(CityLauncher/emailer/templates) had four later passes and six letters the page never showed. A new
script is the page's one writer: it mirrors every letter in the emailer's own send lane in its as-sent
form and computes every badge from the file (RG-0344 LOCKED). While mirroring, the special state was
probed: .env still armed, no date gate, 645 numbers issued after the close and ~500 letters sent 2–5 Sep
carrying "valid until 1 September 2026". Fixed at class level with a date gate + env un-arm
(RG-0345 LOCKED). Also surfaced: the agency letters that SEND never got the 23 Aug three-lane block —
RG-0346 OPEN, design drafts kept under orchestration_v2/templates/agency_lane_design/. One self-inflicted
hot journal on prospects.db from a ledger probe, recovered by the documented method the same minute;
the probe now targets a temp DB path. Ledger green (22 open), rulings 0 FAIL, deploy requested.
