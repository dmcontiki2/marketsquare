## 2026-09-04 — RUL-098: credentials rated generously on purpose, and the cap that makes it safe

**David's ruling:** *"rate the task specific credential initially slightly higher than we judge
it to make it more accessible to those experienced people, giving them the bonus for their
already achieved experience. Even if they should be slightly less we then channel true
'do-ers' to reap the benefits above fakers."*

The principle underneath, written down so future sessions apply it rather than re-derive it:
**weight a signal by how expensive it is to FAKE, not by our own view of how important the
skill is.** A credential that took five years and an external examiner is a strong signal even
where the skill it certifies is only moderately relevant — a faker cannot cheaply obtain it.
Cheap-to-self-assert signals stay weighted low.

**Verifying the ruling was safe produced the proof, and caught my own error.** The canonical
formula in `bea_main._trust_math()` is
`score = min(100, 40 + min(30,Universal) + min(30,Track) + min(40,Category))`. The
category-credential group is **hard-capped at 40**, so credentials carry a seller from 40 to 80
and no further. The final 20 points come only from a verified identity and completed
introductions with none ignored — which no certificate buys. So generosity **cannot** inflate a
faker past 80. What it actually buys is that an experienced person reaches the category ceiling
with FEWER documents, which is exactly the accessibility David asked for, and surplus points
above 40 are headroom rather than score, so over-rating costs the ranking nothing.

**TRUST-LADDER-TRUE-1 / RG-0268 LOCKED.** That same read caught the generator built hours
earlier summing credentials with no caps at all: it published plumbers at **101** — impossible,
the ceiling is 100 — and chess at 97 where the product shows 95. Nobody had seen the pages, so
the cost was zero. But the shape is precisely the one RG-0267 exists to prevent, and I walked
into it one message after writing that entry. **A rule against over-promising is not
self-executing; the arithmetic behind the promise has to be asserted too.** The generator now
carries the caps, states why the duplication of the formula is permitted, and RG-0268 checks it
behaviourally on the exact failing case. All six pages regenerated: every one now shows 95, the
number the product would actually display, with a line explaining that certificates worth more
than 40 on paper are headroom — which is itself the argument for holding more of them.

RG-0267 stands unchanged: generosity never extends to showing a badge that does not exist.
