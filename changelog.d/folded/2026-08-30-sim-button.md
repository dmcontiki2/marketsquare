## 2026-08-30 — SIM-DASH-3: sim link promoted to a button

David could not find the footnote-sized "Open the full simulation →" link (page 4, Beat
the Model card fine print) — his request: a proper blue button. Done: link removed from the
footnote; a standalone blue "Simulation" button (#2563eb) now sits under the card text,
same gated /orchestrator/simulation.html target. Shipped by David via ms-deploy (Release
08b1d4b, Sun 30 Aug 08:29); probed live in-gate: button present, old link gone, sim page
200. Ledger green — RG-0210 asserts the href, unaffected by the label change.
