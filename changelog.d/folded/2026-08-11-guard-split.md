## 2026-08-11 — GUARD-SPLIT-1: autonomous pre-launch fixing, without buying it with anonymity

- **David's ask:** "I do need autonomous fixing pre-launch." Checking what `MAINT_PHASE=prelaunch`
  actually does before arming it showed the flag was doing **two unrelated jobs**:
  1. **The design lane** — prelaunch implements micro design changes instead of batching them.
     This is the autonomy David wants. Unchanged.
  2. **The trust core** — prelaunch dropped the `identity` / `anonym` / `reveal` / `seller_email`
     / `auth` / `login` / `kyc` / `schema` / `migration` / `database` / `safety` refusals
     **entirely**. Nobody asked for this; it rode along on the same switch.
- **Why the premise had expired:** the 9 Aug ruling justified (2) with "no real users/sellers/
  money". Three real people now file faults from real addresses, and Maroushka has a live
  listing (335) carrying 8 real photos. RG-0045 asserts no endpoint may ever return seller
  identity — anonymity IS the product. **Leaking a real seller is irreversible; batching a
  dark-mode toggle is not.** The two risks do not belong on one lever.
- **The change:** `TRUST_CORE_GUARD` is now its own control, defaulting **ON in both phases**.
  `MAINT_PHASE` keeps deciding the design lane and nothing else. The old all-or-nothing
  behaviour is still reachable — `MAINT_TRUST_CORE_GUARD=0` — but only as an explicit act, and
  the run banner then prints `trust-core=OFF`, so a dropped guard can never be silent.
- **Evidence (AIK-VERIFY-1):** the B4 synthetic storm at `MAINT_PHASE=prelaunch`, before and
  after. Before: **2/6 FAIL** — `SYN-ANON` ("the listing showed the seller_email to everyone")
  and `SYN-SAFETY` both routed `PATH_B` instead of escalating. After: **6/6 PASS**, banner
  reading `phase=prelaunch  trust-core=GUARDED`.
- **Ledger RG-0056 LOCKED** — asserts the trust core is never re-welded to the phase, that the
  guard defaults ON, that the banner states it, and that no marker is quietly deleted from the
  refuse list. 56 entries, 53 holding, 0 regressed.
- **Caveat kept honest:** Tier 1 uses a deterministic classify stub, so it exercises the *guard*
  in prelaunch but not the *design lane* — `SYN-DESIGN` still shows `PATH_B` there because the
  stub says so, not because the agent decided it. Proving prelaunch design autonomy needs Tier 2
  with the real brain.
