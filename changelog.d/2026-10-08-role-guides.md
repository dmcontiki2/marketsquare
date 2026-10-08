## 2026-10-08 — ROLE-GUIDES-1: every work role gets its own How guide (RG-0942)

- David: a car washer tapping How saw the home cleaner's guide. 65 roles borrowed a walked guide (home cleaner 38, plumber 17, electrician 7, nanny 3).
- Each now has stories/<role>.json, built by scripts/build_role_guides.py from its parent's walked story: its own name in the title and label, step 2 "Pick [[its group]], then [[its job]]", its own price step (per car with the four packages for a car washer; per visit for hair braider, hairdresser, nail technician, pool cleaner; per job for seamstress and carpet washer), a caregiver's "who you care for", and its own live Quick screens (job tile, areas, days or qualification, price, its listing card) captured by scripts/role_guide_screens.py.
- Steps after saving (Seller Hub, publish, Buzz, a customer's view) keep the parent's walked screens. Changed steps in isiZulu, isiXhosa and Sepedi show in English until a first-language reader supplies them (RUL-165).
- The /help/ gallery still lists only the walked guides; Quick's How opens the role's own one.
