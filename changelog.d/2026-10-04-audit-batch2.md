
**Ledger assertions that followed the code (behaviour unchanged, not weakened):** RG-0293 (the magic-link `src` read is now
validated by `_mlWord`), RG-0331 (`class Listing` gained the `_PhotoSafe` mixin) and RG-0488 (FIND-HONOUR-1, another lane,
widened Quick's no-keyword rule to groups OR property; the group half is unchanged). Full board after the deploy: no regressions.
Note: the deploy also carried FIND-HONOUR-1 (418357b), which was waiting for this batch's files to be committed.
