## 2026-10-05 — EMAIL-EXAMPLES-2: every example card in every outreach letter opens its advert

David: the example phone cards in the tutors letter (and the other types) did not open, while the cars/stays/travel
ones did — "the links that work are where we do have examples... should we generate examples as per these emails?"
PROBED: 10 letters showed three cards each that opened nothing, on stock photos that did not match the card text.
Built: migration 065 (scripts/create_email_examples_2.py) created eight AI-example adverts 476–483 on our own Quick
pictures (watch, stamps, English, coding, plumber, solar, home cleaner, moving help); each trio pairs them with the
existing super example (Krugerrand 269, maths tutor 266, electrician 267, garden service 268). Property and
experiences cards now link to their existing adverts 315–317 / 321–323. Every card's title, price, area and score is
copied from the live row (area as the app shows it: Pretoria / Pretoria East / Gauteng), with "Click to view" links;
the card blocks in the collectors and experiences letters became South-Africa-only (they show rand prices). Synced to
the wave server; Email Templates view rebuilt. Ledger RG-0881; RG-0880 / RG-0344 green.
