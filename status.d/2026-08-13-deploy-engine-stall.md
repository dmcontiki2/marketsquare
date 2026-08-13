- **DEPLOY ENGINE STALLED (confirmed, 3 ignored ref advances):** worked through the
  ~05:4x deploy (017 run 1 executed, 244/273 images landed), then stopped — refs
  8691602 (Kenya sweep, ~06:0x) and c93d59b (David's deploy_marketsquare.bat press,
  06:43, commit+push verified client-side) both unacted 10+ min. Site itself healthy
  throughout (/health 200, gate up). Leading hypotheses for tonight's SSH paste, in
  order: (1) box's GitHub fetch failing every tick — engine warns "git fetch failed
  (network?) — leaving live site untouched" and exits 0; expired/revoked read token
  fits the worked-then-stopped timeline; (2) deploy timer dead; (3) hung run holding
  the flock. Tonight's 17:45 scheduled session diagnoses FIRST, then one wrapper press
  finishes DW-025 (migration 017 run 2) → RG-0063 READY TO LOCK → promote.
