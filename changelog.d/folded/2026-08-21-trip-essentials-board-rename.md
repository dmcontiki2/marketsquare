## 2026-08-21 — TRIP-ESSENTIALS-1 correction: the preview board is TRIP_ESSENTIALS_BOARD.html

The 21 Aug TRIP-ESSENTIALS-1 entry named the standalone panel board
`TRIP_ESSENTIALS_PREVIEW.html`. `Visuals/refresh_visuals.py` deliberately skips any
`*_PREVIEW.*` file as a throwaway build preview, so the board never reached David's gallery —
which is the whole point of his 4 Aug standing instruction. Renamed to
**`MarketSquare/TRIP_ESSENTIALS_BOARD.html`** and re-indexed; the generator writes the new name.
The skip rule itself is correct and was left alone.
