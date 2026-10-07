## 2026-10-06 — PLATE-DETECTOR-1: number plates found by a local detector, blurred plate-shaped, no more blob

David, 6 Oct: "to load a car and to have AI blur the numberplate, this should be automatic, not blocking the photo or interfering with the lister — the AI keeps on blotching a big blob which looks very ugly. I have used other agents myself with no problem."

Root cause. The photo gate asked a general vision LLM to NAME coordinates for the plate (0–1000 scale). An LLM reads a photo well and measures it badly: its boxes land 5–10% of the frame off, sometimes below the plate (listing 246, 11 Jul). Because the boxes could not be trusted, every layer added since — generous boxes, zoom-refine, verify-and-repaint rounds, the last-resort rung — painted MORE blur on the same photo. That stacking was the blob. Since RUL-033 (19 Aug) the LLM lane has not blurred at all: a car photo with a plate was REJECTED with "not anonymous — replace it", which is the "blocking the lister" David describes. The tools that do this easily use a small detector trained for plates, not an LLM.

What changed. `plate_detector.py`: RT-DETRv2 licence-plate detector (justjuu/rtdetr-v2-license-plate-detection, Apache-2.0 — the YOLO plate models on the Hub are AGPL-3.0, which closed source cannot carry), exported to ONNX, running on the Hetzner box's own CPU through onnxruntime (~1 s/photo, zero per-photo cost, nothing leaves the server, hash-pinned model). Two stages in BOTH photo doors (seller upload gate and agency import):
- Stage 0 — vehicle categories: every plate is detected and blurred plate-shaped (plate + frame margin for the dealer strip, soft 2 px edge) BEFORE the LLM scan, so the scan normally comes back "clean" first time and the seller sees "we blurred the number plate".
- Stage 2 — any category: when the LLM still names a plate, the detector's pixel-accurate box replaces the LLM's guess, is blurred, and ONE verify read confirms it. Anything that is not a plate (signage, logos, the seller's own label) flows into the existing path exactly as before; RUL-033 is untouched for that lane.
Fail-safe: no package / no model / any error → both stages are no-ops and the gate behaves as it did on 5 Oct. `/health` now carries `plate_detector.ready`.

Proof. `scripts/eval_plate_detector.py` against eval_photos/TRUTH.json: 100% plate recall on all 11 plate rows (incl. the tiny background plate and the two-plate frame), 0 false boxes on the real clean photos; the cartoon traps trip it, which is exactly why it is only trusted alone in vehicle categories. Ledger RG-0904. Migration 067 installs onnxruntime; the 171 MB model rides media_push.bat (section 6b), git-ignored.

Known limit. A plate photographed at 25–40° gets a near-square patch (the detector box is axis-aligned); still only the plate area, not the car.

Also closed: the LLM-lane painter's pixel-evidence capsule (15 Jul) could leave characters readable (offline: '345' of a straight plate on syn_06); that fallback is removed — only a model-reported angle shapes a capsule, otherwise the safe axis-aligned core. No live effect today (that lane is reject-only under RUL-033); it matters the day RUL-033 is lifted.
