## 2026-10-10 — SEARCH-EX-1: search finds the role and sport examples

David, 10 Oct: "Why doesn't the filter find the Badminton coach if I search it in the trustsquare filter search, even though there is a demo card?"

Cause: TrustSquare's search asks the server, and the server's search only knows stored adverts. The AI examples for each work role and sport (GENERIC-EX-1, TRAINERS-EX-1) are made by the server on request and live only in the app, so a search never matched one -- "badminton" showed nothing. Now the app also matches those examples on the same words (every word must be in the example's name, its English role name, its sport or its city line; a short word must be a whole word, so "car" never finds "carpet"; "coaches" finds "coach"), adds them to the results as examples (marked, after real adverts), and a hit stops the search from widening to the whole category. "coach", "coaching" and "instructor" now point a search at Tutors, where the Trainers door is. Checked in a phone-sized browser, Pretoria: badminton, "badminton coach", "Badminton coach Pretoria", "car washer", "swim", "tennis coaches" each show the right example; "apartment" and "maths tutor" unchanged. Ledger RG-0953.

Cost model impact: none.
