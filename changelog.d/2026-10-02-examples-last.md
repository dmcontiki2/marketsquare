## 2026-10-02 — RUL-194 EXAMPLES-LAST-1: real listings always first, and an "AI examples on/off" switch

David: the AI example adverts were "a little bit chaotically mixed randomly with the live listings". He weighed a DEMO
switch against "always show them last", and chose the combination: "Excellent, you combined the two ideas - that is the
best suggestion. Please do it." After Claude corrected itself (this reverses SUPER-PIN-1): "Please change it Claude, and then deploy."

- **Order (server):** every /listings sort variant (newest, price up/down, trust, smart, default) and the Local Market list
  put every real listing before every AI example (`_ex_last`; example = super_example, is_demo or a house account — the
  RUL-187 definition). The zoom funnel's order does the same (`zoom_engine.is_example`).
- **Order (TrustSquare app):** Browse, Adventures, Local Market, the map and the category counts all run `msExOrder()` —
  real listings, then AI examples, then "Coming soon" placeholders. The count line reads "N real listings · M AI examples".
- **The switch:** "AI examples on/off" beside the results count; starts ON; remembered on the device (`ts_show_examples`),
  and Quick reads the same key. Off hides the examples from the lists, the map and the counts; an empty view says how many
  examples are hidden, with one tap to show them.
- **Quick:** find results show real listings first; a "Hide AI examples" / "Show AI examples" button (3 new phrases in all
  five languages, RUL-165 drafts).
- Unchanged: every example stays marked and takes no introduction (RUL-040, RUL-187).
- Supersedes SUPER-PIN-1 (20 Jul 2026). RG-0052 amended to the stronger form; new ledger RG-0700; rulings_check RUL-194.

Cost model impact: none. Schema: none.
