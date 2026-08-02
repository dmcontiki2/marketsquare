# Retired 2 Aug 2026 — DEPLOY-CONSOLIDATION-1 (see ONE_DEPLOY.md)

One deploy engine now: publish the `deploy` ref; the server does the rest.
These bats were uncoordinated second engines. Replacements:

| Retired bat                    | Its job now lives in                          |
|--------------------------------|-----------------------------------------------|
| deploy_frontend_only.bat       | the ONE deploy (manifest: ms.js/ms.css/index) |
| deploy_frontend_nops.bat       | the ONE deploy (server needs no PowerShell)   |
| deploy_bea_safe.bat            | the ONE deploy (engine health-check + auto-rollback) |
| deploy_bit_monitoring.bat      | manifest line `dashboard.server.html | dashboard.html` |
| deploy_eula_v19.bat            | the ONE deploy (terms.html + index in manifest) |
| deploy_files.bat               | the ONE deploy (add a manifest line instead)  |
| deploy_collectables_video.bat  | media_push.bat (hash-gated videos section)    |
| deploy_intro_video.bat         | media_push.bat (hash-gated videos section)    |
| deploy_n8n_templates.bat       | media_push.bat (n8n templates section); its %PROJECT% root sources no longer exist |
| add_travelpayouts_key.bat      | job DONE 1 Aug (token live). Pattern survives WITHOUT the code-ship step: env drop-in + restart + verify only — code ships via the deploy ref |

David: this folder is safe to delete whenever you like.
