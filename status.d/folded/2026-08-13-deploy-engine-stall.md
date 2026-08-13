- **CORRECTION — there was NO deploy-engine stall (Claude's timezone error, owned):**
  David's 06:43 SAST wrapper press deployed at 04:45 UTC, two minutes later, exactly
  as designed; the morning "stall" was SAST commit stamps compared against UTC probe
  times. Timer verified healthy (2-min ticks, 102ms no-ops, exit 0). The evening
  paste showed the true residue: **all 29 missing demo images are DEAD SOURCE URLs**
  — truncated params (q=8) and mangled IDs in the original seed data — meaning those
  29 demo cards were broken on the live site all along; the self-host work exposed,
  not caused, them. 017's stand-in rung has each at 1 tracked failure; the next
  deploy takes them to 2 → fills all 29 from landed neighbours (recorded in
  ATTRIBUTION.json) → rewrites live demo_sellers.json → exit 0 → RG-0063 READY TO
  LOCK. One wrapper press completes DW-025 end-to-end.
