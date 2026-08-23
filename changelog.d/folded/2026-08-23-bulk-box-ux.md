## 2026-08-23 — AGENCY-BULK-UX-1: Bulk-add box readable by humans (David's eyeball pass)

- Overflow fixed: the 17-column code string now wraps inside its card (word-break +
  box-sizing on box and textarea) instead of running off the right edge.
- Copy rewritten for a non-technical agency admin: leads with the truth that ONLY the
  email column is required (backend-verified — everything else is optional), columns
  grouped basics / estate / cars / travel, and two one-tap buttons: Copy the column
  header · Copy a filled example (skin-aware: estate/dealer/operator samples).
- Error honesty: an EMPTY box now says "the grey text is just an example — paste your
  list" instead of the parse-failure message David hit; real parse failures explain
  the first-line-is-column-names rule and point at the example button.
