## 2026-10-06 — Casuals wave fixes: the Quick casuals audit closed (RUL-209)

David ran the casuals audit at 06:00 (QUICK_CASUALS_AUDIT_2026-10-06.html) and at 06:40 said "please fix all of the faults" and answered its four decisions (RUL-209).

FIELD-SCRUB-1 (AUD-117): a phone number, e-mail or street address typed into area, price, availability or any other short text field is now scrubbed on create, edit and Local Market create, with the same conservative regex E2E-HMI-1 runs on title and description (prices, sizes and suburb names untouched). Ledger RG-0896.

BUZZ-ANON-2 + BUZZ-NOINBOX-1 (AUD-127, AUD-090): the Buzz e-mail no longer puts the sender's address in Reply-To (RUL-171(d)); it tells the receiver to answer in My Space > Buzz. A buzz to an inbox-less key account with no push is reported as not delivered, with what the other side must switch on, never as "went to their email". RG-0533 amended; RG-0897.

SVC-FILTER-MATCH-1 (AUD-173 class): TrustSquare's Services filters match Quick adverts by meaning: Weekdays finds "Mon, Wed, Fri", Domestic finds "Home cleaner", Child Minding finds "Nanny", and an area matches any of a multi-area advert's areas. RG-0898.

GATE-WORDS-2 (AUD-208): Quick's saved screen checks the role's own gate first, so car guards, security guards and licensed trades are told their licence is checked. RG-0899.

LOGO-LIGHT-1 (F6 / L16): the app logo is a 17 KB SVG instead of the 183 KB PNG every landing from Quick downloaded first. RG-0900.

ROLE-FIND-STRICT-1: Quick's Find judges a Services advert that names its trade on its title and trade, so an electrician whose description says "domestic work" no longer answers a Home cleaner search. RG-0901.

KEY-TYPED-1 (AUD-131): a typed @key.trustsquare.co address is refused at Quick's save. RG-0902.

COWORKER-VOUCH-1 (RUL-209(a)): the confirm page offers "Yes, they worked for me" and "Yes, I worked with them"; either is the same vouch and opens the RUL-115 gate. The worker's Hub and reference wording say "worked for or with". RG-0903.

HELP-PUBLIC-1 (RUL-209(d)): Quick's How button opens the story guides for everyone. RG-0547 amended.

Not changed: Pretoria's area tiles keep Midrand and Sandton (by design they carry their own Johannesburg city); SMS sign-in codes stay off (RUL-209(b)).

Cost model impact: none.
