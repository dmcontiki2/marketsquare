# EMPLOYER LANE — the supply measurement, handed over

*Written by run 23 of the onboarding goal (RUL-096), 28 Sep 2026, for whoever owns
`org_enrol.py` (ORG-ENROL-1 / RUL-150). SO-5: the owner ships it — this file is a
measurement and a case, not a design, and nothing in `org_enrol.py` was touched.*

---

## Why you are being handed this

The onboarding goal needs **20 people who were contacted cold to publish a listing by
their own hand, by 31 Oct 2026**. It is at 0 with 33 days left.

Measured on the server tonight, the honest seller supply the nightly wave can reach is
**21 addresses** — Pretoria 20, Cape Town 1 — and they are shop and institution front
desks on the agency lane, not individuals. That pool cannot produce 20 published
listings. The arithmetic ended the argument five weeks early.

The employer door is the only untried lane that owns its own supply, and the largest
dead weight on the prospects list turns out to be exactly the kind of organisation it
was built for.

## The measurement (probed on the server, 28 Sep 2026, not inherited)

`sqlite3 -readonly /var/www/citylauncher/data/prospects.db`, rows with
`source LIKE 'teachers_trainers%'`:

| fact | number |
|---|---|
| total rows in the pool | 1,622 |
| never emailed, no verdict against them | **1,354** |
| …of those, school-named (School / Skool / College / Primary / Academy / Laerskool …) | **1,267** |
| …of those, MX state | **1,354 `mx_ok` — every one; none unchecked, none failing** |

By source: `teachers_trainers:dbe_emis` 1,249 · `:osm` 244 · `:site` 97 · `:bing` 32.

By city (never-emailed, no verdict):

| city | rows | in policy | armed | gates_green | reachable (GEO-REACH-1) |
|---|---|---|---|---|---|
| Durban | 596 | yes | yes | yes | **yes** |
| Pietermaritzburg | 535 | yes | yes | yes | **yes** |
| Cape Town | 116 | yes | yes | yes | **yes** |
| Johannesburg | 52 | yes | yes | yes | **yes** |
| Pretoria | 37 | yes | yes | yes | **yes** |
| Polokwane 7 · George 3 · Bloemfontein 3 · Mossel Bay 2 · Knysna 2 · East London 1 | 18 | yes | yes | yes | **yes** |

**Every one of these cities has a home on the live site**, so a worker enrolled there can
say where she is — which is the gate that quietly killed 1,499 of our US letters.

## Why these rows are worthless to the seller lane and valuable to yours

They are held, correctly, by two independent rules:

- **PERSON-ONLY-1** — `teachers_trainers` is a blocked category on the individual-seller lane.
- **ORG-NAME-1** — `name == business_name == "<X> Primary School"`. Measured 5 Sep and again
  27 Sep: a school principal will not publish a tutoring advert by their own hand.

Neither rule is wrong and neither should be lifted. **They are the wrong ask, not the wrong
people.** A school is an employer: it employs cleaners, groundskeepers, caretakers, kitchen
staff and assistants — who are precisely the Quick door's people, and who have no directory
anywhere that we could harvest. One conversation with a school's office enrols its whole
support staff, each with her own private link, and she publishes by her own hand behind the
EULA gate. That is the goal's definition satisfied, not bent.

Two further points in this pool's favour, both measured:

- **The addresses are published, not constructed.** `dbe_emis` is the Department of Basic
  Education's own register. This is the opposite of `property24`, which built addresses out
  of `firstname.lastname@agencydomain` and bounced 8 of 12 (RG-0507 / RG-0509 hold it).
- **The concentration is where the seller lane has nothing.** Durban's seller-sendable pool
  is 4; it holds 596 of these. Pietermaritzburg is armed and reachable and the seller lane
  has never had a single sendable row there.

## What is NOT yours to worry about, and what is

Not yours: the letter. A cold letter to a school office is an **employer** letter ("enrol
your support staff, they each get their own link, you hand out the slips") — a different ask
from the seller letter, and it does not touch the guards above, because the employer lane
does not mail an organisation *as a prospective seller*. Whoever writes it should know the
seller letter converts about 1 in 4 of the people we can prove read one.

Yours, and the reason this is a hand-off rather than a request:

1. **Does `POST /agencies/{id}/enrol` want a school?** The docstring names "an estate gate
   desk, a college, a mine, a cleaning company". A primary school is smaller than all four.
   Is there a minimum, a verification step, or a `universal.employer_confirmed` policy that
   a public school does or does not satisfy?
2. **Who does the enrolling?** The door assumes an employer's admin sends a list. For a
   school that is one administrator with no reason to help us yet. That is the real question
   in this lane and it is not a technical one.
3. **Roles and language.** `LANGS = ("en","zu","xh","af","nso")`. Durban and
   Pietermaritzburg are KwaZulu-Natal: isiZulu first. 1,131 of the 1,354 sit in those two
   cities, so this lane is a **KZN isiZulu** lane before it is anything else.

## What run 23 did and did not do

Did: measured the pool, checked every city against the policy and the reachability gate,
confirmed the two holds are independent and correct, and wrote this.

Did not: touch `org_enrol.py`, write a letter, or send anything. `org_enrol.py` is yours
under SO-5 and it is hours old.

**The one line:** 1,354 MX-clean school mailboxes in nine armed, reachable South African
cities, 84% of them in Durban and Pietermaritzburg, useless as sellers and the only
employer-shaped supply we own — the seller lane can reach 21 people and needs 20 listings,
so this lane is now the goal's only credible path.
