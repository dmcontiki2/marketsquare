## TRUST-ONE-SET-1 — one evidence set behind every trust surface

David: *"lets fix the scores to be consistent, and this is not the 60/80 which i now
understand as being correct."* So: the seller Trust Score reading 80 on the dashboard,
57 on the seller profile, and 75 after a publish.

**Third bug in this family, and the first the guards could not see.** `test_trust_evidence_true`
checks a headline against its OWN list — both were right together, so it passed.
`test_trust_base40` checks the ARITHMETIC canon — the panel used `_trust_math` correctly, so it
passed too. What differed was the **evidence set**: the buyer-facing panel hand-rolled its own
universal and track-record SQL, which counts a narrower set than the scorer reads, and then wrote
its lower answer over `users.trust_score` **and over every one of that seller's listings**. So the
number moved depending on which screen was opened last.

**One builder.** `_trust_evidence(conn, email, cat_key)` is now the only place a seller's evidence
is assembled — `_build_breakdown_items` + `_sum_earned_with_replaces` + `_trust_math`, once.
`trust_score_breakdown` and `seller_public_credentials` both read from it, so two surfaces can now
only disagree about a seller if they were asked about different CATEGORIES, which is a real
difference and not drift. `_norm_cat_key` replaces the category map that existed in one endpoint
and nowhere else, and it takes `service_class` so a listing and its seller resolve to the same set.

**List and total in one pass.** `_earned_display` returns the visible items and the number they
sum to together, so evidence-true is enforced by construction rather than by a warning logged
after the fact.

**Write authority narrowed to what each surface knows.** The panel's heal stays — JNR-FIX-2 exists
because a stored score sat above its evidence — but it now writes the category score the scorer
would compute, touches `users.trust_score` only when this advert's category IS the seller's
primary one, and syncs listing badges only for listings **in that category**, mirroring the rule
the scorer already followed for `?category=` overrides.

**Everything ruled stays ruled:** the base-40 foundation, the LM-uncapped credential group
(SUPER-CRED-2 still scores an LM seller under the LM model on all their adverts), EVIDENCE-TRUE-1's
per-listing mandate filter with agency peers, PEN-CAP-1 penalties after the cap, and anonymity —
names and points only, never documents or identity.

**One honest consequence:** the panel used to count earned credentials from EVERY category
(`LIKE 'category.%'`). It now counts the advert's own category, like the scorer. A multi-category
seller's public panel can therefore read lower than it did yesterday — that is the correction, not
a loss.

**New guard: `test_trust_one_set.py`,** wired into `predeploy_check.py` beside the other two. It
asserts there is exactly one evidence builder, that nothing else calls the raw reader, that the
panel holds no private evidence SQL, and that its writes are category-scoped. Run against the
pre-fix file it fails 7 of 8 — including *"the panel wrote a per-listing score to EVERY listing"*.
