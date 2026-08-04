## 2026-08-05 — The REPORT tab reaches every page a tester can land on (MAINT-B1b addendum)

**David caught it:** *"this maintenance add is throughout the app visible? I may as a tester want
to report a fix or issue on any page, not just the ones where I list."* He was right, and the
tripwire was green while he was right — which is the more serious half of the finding.

**The gap.** The widget was wired into 14 pages from a list typed by hand. The site actually
deploys 18. Three tester-reachable pages had no way to report a fault: `ranking_explainer.html`,
`agency_import_guide.html`, `agents_as_a_service.html`. Now wired — 17 of 18.

**The class fix, not just the instance.** `test_tester_intake.py` no longer carries a hardcoded
page list. It derives the set from `ops/autodeploy/deploy_manifest.txt` — the one file that
already decides what ships — minus an explicit `NOT_TESTER_FACING` set (currently just
`dashboard.server.html`, David's own console, where he tells us directly). **Any new deployable
page now fails the tripwire until it carries the tab.** A hand-typed list could read green while
a tester stood on a page with no way to report; a manifest-derived one cannot.

**Proved it bites.** Copied the tree, removed the tag from one page, re-ran: the tripwire failed
with *"a tester could land on these pages with no way to report a fault: ranking_explainer.html"*.
A tripwire nobody has watched fail is not yet a tripwire.

**Coverage now.** `index.html` is the whole marketplace — one document carrying browse, sell,
wallet, listing detail and My Space — so the tab is present on every screen inside the app, not
just listing pages. Plus admin, support, terms, privacy, the nine adventure maps, the ranking
explainer, the agency import guide and agents-as-a-service.
