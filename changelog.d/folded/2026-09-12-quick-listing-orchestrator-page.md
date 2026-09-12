## 2026-09-12 — Quick Listing gets its own Orchestrator page, on the Ops Dashboard

David, after seeing the two design visuals: *"Please add both of these to the Ops Dashboard as a
separate new Orchestrator page we will be using for the Quick Listing."*

### What was built

- **The page** — `genie/QUICK_LISTING_ORCH.html`, composed from the two originals
  (`genie/QUICK_INTRO_FLOW.html`, `genie/SHARE_CHAIN.html`): a ruled / built / next board at the
  top, then Visual 1 (the whole path from five taps to a live listing) and Visual 2 (the share
  chain), each with its lede, caption and legend. Dark and light themes, phone-scrollable.
- **Where it lives** — `orchestrator/quick_listing.html`, the same gated prefix as the contagion
  simulation and the defence map. The whole prefix is the Orchestrator sign-in realm; probed 401
  anonymously at the origin and through the edge. Deploy-manifest row added so every future deploy
  carries it.
- **How it is reached** — a new **⚡ Quick Listing** tab on the Ops Dashboard, next to Live Users.
  It frames the page in place, with an "open full page" link; in file:// mode it points at the
  local original so the dashboard still works offline.

### Verified before it went live

The dashboard was rendered in a real headless browser from the repo copy: the tab is present,
clicking it shows the Quick Listing view and hides the dashboard, the tab goes active, the frame
loads the page with both figures (first figure rendered at 1420 × 895 px), switching to Horizon
hides it and switching back shows it, and there were zero page errors. All eighteen inline
scripts in the dashboard still parse. The repo dashboard was byte-identical to the server's before
the edit, so nothing anyone else deployed today was overwritten.

One false alarm worth recording: the first screenshot of the framed page was black. The page's
Google Fonts stylesheet was stalling in the sandbox, and a render-blocking stylesheet that never
answers leaves a blank frame. With that one request failing fast the page painted at once. On a
real machine the fonts load and this never shows; it is noted here so the next person does not
chase it.

### Ledger

- **RG-0360 — LOCKED.** The page answers 401 anonymously (never public), the manifest row is
  present, the page carries both figures, and the dashboard carries the tab, the view, the switch
  branch and the gated address. Proven red with the manifest row and the tab removed.

### Also today, in the same family

The install offer's moment was put to David and ruled: it stays at the **first successful
publish** (RUL-123). The Visuals gallery was refreshed; both originals are tiled under
MarketSquare, and this page will tile with them on the next refresh.
