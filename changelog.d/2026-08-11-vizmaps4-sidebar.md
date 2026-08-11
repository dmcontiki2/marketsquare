## 2026-08-11 — VIZ-MAPS-4: dashboard left sidebar removed (David's ask)

David: "on the Dashboard page there is a left hand column called Launch Blockers, please
remove it." Removed the whole sidebar column (Launch Blockers / Session Rules / Auctions —
Live State already gone via VIZ-MAPS-2): markup replaced with a dated tombstone, grid to
single column at every width (VIZ-MAPS-3's phone media block retired — its behaviour is now
the default), the three populate() blocks removed so nothing dereferences missing elements,
dead sidebar CSS dropped. Blockers remain visible via the Launch Blockers direction card;
/dashboard/summary still ships blockers/knownRules/auctions server-side (VIZ-MAPS-2
precedent: presentation removed, data path intact). File is fetch-driven (not generated) —
verified before editing. Backup: dashboard.server.html.bak-*-vizmaps4. Rides the manifest
(→ dashboard.html on the server) at next deploy; David's local file:// view updates on F5.
