## 2026-08-20 — EULA v1.14: Country Schedules D–G (France, Portugal, New Zealand, Argentina)

David's ruling after the twelve-jurisdiction outreach-law research: cover the sendable countries
in the EULA, Namibia deliberately EXCLUDED (one prospect; admitting it to §13.5 is an affirmative
statement that we offer the service in a country whose ETA Chapter 4 can be commenced by a single
ministerial gazette notice, with liability extending to the advertiser).

Added Schedule D (France, D1–D8), E (Portugal, E1–E9), F (New Zealand, F1–F6) and G (Argentina,
G1–G7), matching the existing A/B/C pattern: mandatory rights, service standard, withdrawal/
revocation, liability, data protection naming the local regulator, unfair/abusive terms, language,
dispute resolution. §13.5's Scheduled-Countries list, §13.6's opener, the document header and the
footer all updated; v1.13 → v1.14. §14.4 needed no change — it already survives "Section 13
including Sections 13.5–13.6 and the Country Schedules".

**LANGUAGE CLAUSES CORRECTED BEFORE SHIPPING (D7/E8/G7).** The draft had the local-language version
PREVAIL, which would have made a translation we do not yet have into the binding legal text. As
shipped: English governs, translations are informational, and where local mandatory law requires a
consumer contract in the local language we commit to supplying it, prevailing only to the extent
that law requires. FR (Loi Toubon), PT (DL 446/85) and AR (Ley 24.240 art.10) each require the local
language for CONSUMER contracts — a real obligation before consumer volume in those markets, but
not one that binds the B2B seller campaign. Translation is now an open work item, not a silent gap.

**EULA-ANCHOR-1 — a tooling fault fixed at class level, same session.** Both `scripts/eula_sync.py`
and regression ledger RG-0077 hardcoded the FULL Country-Schedule list as their end anchor
("...United Kingdom · United States · Australia</em></p>"). Adding schedules therefore (a) made
eula_sync.py REFUSE to run at all, and (b) made RG-0077 report an EULA fork that did not exist —
the three copies were byte-identical throughout. The artefact was right; the assertions were wrong.
Both now anchor on the stable prefix "· Republic of South Africa · Country Schedules:" plus the
paragraph close, so the list can grow without disarming the one writer or reddening the ledger.
Per the standing rule, the assertion was fixed and the RG-0077 ref records why. Verified:
eula_sync.py --check exits 0 (112,434 bytes identical across eula_clean.html, terms.html, ms.js)
and RG-0077 returns green with no FAIL rows.

NOT YET DEPLOYED — rides the next publish of the deploy ref. Whether to force a re-accept prompt for
existing users (who accepted v1.13) is David's call; the change is additive.

Cost model impact: none — no new services. Translation into FR/PT/ES, if commissioned, is a future
cost tied to consumer volume in those markets, not to the seller campaign.
