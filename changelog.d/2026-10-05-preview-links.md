## 2026-10-05 — PREVIEW-LINKS-1: the Email Templates previews' buttons open real pages

David clicked "Open Quick", the phone picture and "Open it in the full TrustSquare app" in the Ops Dashboard's Email
Templates view and got 404 Not Found. Cause: the preview mirror served the sending copies raw, so `{{quick_link}}`,
`{{magic_link}}` and `{{language_row}}` reached the browser as relative paths. build_email_templates_page.py now fills
every LINK placeholder for a sample reader in Pretoria (Quick door per category, app front door, ZA language links,
inert unsubscribe anchor); text placeholders stay visible. The CityLauncher sending copies are untouched — real letters
were never affected. All 37 distinct links answer 200. Ledger RG-0880; RG-0344 still green.
