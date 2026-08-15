- **EULA v1.13 — AI disclosure written, three-way EULA fork closed (EULA-FORK-1).** Added an
  up-front AI disclosure block before §1, a new §7.7 (built with AI; AI-generated demo/marketing
  imagery; demo listings are not offerings; C2PA/invisible provenance markers never stripped; no
  misrepresenting AI uploads) and a new §8.3 bullet that Your Content is never supplied for
  external AI-model training. Found en route: `terms.html` was v1.12 while `eula_clean.html` and
  the `ms.js` **acceptance-modal** copy were still v1.11 without §6.1B — users were accepting text
  the site did not publish. `scripts/eula_sync.py` is now the one writer (`eula_clean.html` =
  source, `--check` exits 1 on drift); RG-0077 LOCKED asserts the copies stay identical and the AI
  disclosure stays in. All three copies byte-identical at 100,775 bytes; ledger clean; canon
  pointers in line. **On disk, not deployed** — `ms.js` + `terms.html` ship on the next `deploy`
  push. Open for David: the §8.3 no-external-training commitment is a genuine business constraint
  (escape valve already in §8.3: change requires individual notice + fresh consent), and A6 counsel
  review now also covers §7.7.
