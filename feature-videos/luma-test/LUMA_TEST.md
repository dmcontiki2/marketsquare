# Luma Ray Flash 2 — bake-off test (vs the Veo/Flow Heritage clips)

Goal: generate the **same shot** on Luma Ray Flash 2 (US, ~$0.48 for 8s) and judge realism + lip-sync against our Veo/Flow version. Cost for this test: well under $1.

## Where
lumalabs.ai/dream-machine → sign in (free account; free trial credits). Choose the **Ray Flash 2** model, portrait **9:16**, ~5–8s.

## Two ways to run it

### Option A — image-to-video (fairest like-for-like; matches our couple)
1. Upload `couple-start-frame.png` (in this folder) as the **start frame**.
2. Prompt:
> The middle-aged couple sit at their kitchen table in warm morning light, Table Mountain through the window behind them. The wife (colourful scarf) turns to her husband, excited, and says: "We need a proper tour — I want to see the Kruger National Park." The husband (glasses, blue golf shirt) smiles and replies: "Let's use TrustSquare for the planning." Natural candid performance, gentle handheld camera, shallow depth of field, lips synced to the dialogue.

### Option B — text-to-video (no upload; pure quality read)
> Photorealistic vertical 9:16, 8 seconds. A middle-aged South African couple at a bright kitchen table, soft morning light, Table Mountain through the window. The wife in a colourful scarf turns to her husband and says, excited: "We need a proper tour — I want to see the Kruger National Park." Her husband, glasses and a blue golf shirt, smiles: "Let's use TrustSquare for the planning." Warm tones, shallow depth of field, handheld documentary feel, natural lip-sync.

## What to judge (side by side with `02-heritage/clips/hook-couple.mp4`)
1. **Lip-sync** — does Luma actually sync mouths to the spoken lines? (This is Veo's strength; it's the main thing to verify on Luma.)
2. **Face realism / skin** — convincing vs plasticky.
3. **Two-person dialogue** — can it handle both people speaking in one clip, or is it better one speaker per clip?
4. **Motion** — natural micro-movements vs stiff or warpy.
5. **Audio quality** — clear voices vs muffled/robotic.

> Tip: if Luma's two-person dialogue is weak, test a single-speaker shot instead (the husband alone: "I pick my heritage sites — Kruger first — set our dates and budget, from Cape Town.") — that's closer to most of our walkthrough clips anyway.

## If it passes
The whole pipeline carries over unchanged — only the generator swaps. I can convert all the Heritage + Collectables prompts to Luma format and we run the campaign there instead of Flow, US-based and ~$3–13 per finished video.
