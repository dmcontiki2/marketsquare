## 8 Sep 2026 — RUL-110: "a global marketplace", no country of origin in the opening line

David, on run 7's wording *"a global marketplace, founded in South Africa"*: *"just change it to say a
global marketplace. Companies don't say they are from a specific company in the statement they open up
with, it is unnecessary and will immediately biase many people."*

- Club letter, outfitter letter and the federation letter (which still said "South African marketplace"
  twice — missed by RUL-104) now open with "a global marketplace that opened on 1 September".
- The legal footer (registered company, number, postal address) is unchanged — the law requires it and
  it is not positioning (RUL-110 b).
- `rulings_check.py`: RUL-104's must-not lists widened; RUL-110 added as NEGATIVE assertions ("founded
  in", "based in South Africa", "from South Africa") on all three letters and the YouTube boilerplate —
  RUL-104 had only a positive assertion, which is how the qualifier slipped past it.
