## 2026-10-04 · AI-DESC-SHOWN-1 + AI-PRICE-HINT-1 (Goal run 29, RG-0876)

- **The photo read's description is shown before it can be published.** It used to lead the advert unseen when the
  seller left her story box empty. It now fills her first story box ("What makes it special?" on Local Market; the
  first textarea of every flow) with a note: "I drafted this from your photo — buyers will read it as written."
  Clearing the box means no AI text in the advert.
- **Notes-to-self are dropped** from the AI text (sentences about what is not visible or cannot be confirmed, props,
  styling), and the vision prompt now says description_draft is buyer-facing advert text.
- **A low-confidence price guess (< 0.5) is a hint, not her price**: the box stays empty with the placeholder
  "Photo guess R80 — your price".
- Evidence: docs/E2E_2026-10-04_run29.md — a marmalade seller's advert would have gone live describing honey, bread
  loaves, a jug and flowers "as market styling", ending "…and pricing are not visible."; R80 (confidence 0.28) sat in
  her price box.
