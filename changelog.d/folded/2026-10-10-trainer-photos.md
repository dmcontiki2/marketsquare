## 2026-10-10 — TRAINER-PHOTOS-1 (RUL-218): every trainer role now opens on a real-looking photo of the coaching itself

David, 10 Oct 2026: "i still have $15 for Higgsfield photos; can you please replace all of the trainer/coaches artificial pictures to real photos as we have for services, but to be relevant to the trainer/coach activity - chess coach with chess set and clock, judo with judo looking trainer and child in right gear etc."

- 47 new photos (Higgsfield, the same lane as the Services role pictures): each shows a coaching session in that sport -- the coach with the client, class or child, in the sport's proper kit and place (judo instructor and child in judogi on a tatami, chess coach at a board with a clock, swimming coach on the pool deck, ...).
- Rules kept: nobody recognisable (from behind, side-on, at a distance), no text, logos or brands; a child appears only in the sports commonly coached to children, fully in kit, in an ordinary supervised moment. This amends RUL-157 for the Trainers door only -- Services pictures stay "the work, never a person".
- The prompts live in scripts/trainer_photo_prompts.py (read by build_role_registry.py). One prompt ("leotard") was refused by the image service and was reworded to gym shorts and a t-shirt.
- The photos are served at a new address (?v=photo1) in Quick and in the AI examples, because the CDN and phones keep a picture for a year.
- Spend: about US$3 of David's US$15 Higgsfield balance (48 pictures, one refused). Interim illustrations kept in roles/pictures/_interim_trainers/.
- Ledger RG-0950; rulings_check RUL-218.

Cost model impact: none recurring.
