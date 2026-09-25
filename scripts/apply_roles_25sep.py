#!/usr/bin/env python3
"""ROLES-25SEP-1 (RUL-172, David 25 Sep 2026, answering "Bring them in now?" with "All of them").
Brings the 3 LATER roles on the 42-type board (Pool cleaner, Window cleaner, Pet sitter / dog walker) IN, and adds
the 9 board types that were never on the slate: Carpet washer, Au pair, Tree cutter, Garden waste removal,
Griller / braai, Hotel porter, Lodge staff, Caterer, Bodyguard. Au pair takes the RUL-153 clearance gate, Bodyguard
the RUL-156 PSIRA gate. Edits the SLATE (the registry's one source) and the build script's tables; then run
build_role_registry.py and sync_quick_roles.py. Idempotent; asserts every anchor."""
import io, os, re
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p): return io.open(os.path.join(R, p), encoding="utf-8").read()
def wr(p, s):
    io.open(os.path.join(R, p), "w", encoding="utf-8").write(s); assert rd(p) == s, p
NOTE = "25 Sep 2026: IN (RUL-172, David: 'All of them')."
s = rd("ROLE_SLATE_REVIEW.md")
for lab in ("Pool cleaner", "Window cleaner", "Pet sitter / dog walker"):
    m = re.search(r"^\| %s \|  \| LATER \| (.*) \|$" % re.escape(lab), s, re.M)
    if m:
        s = s.replace(m.group(0), "| %s |  | IN | %s %s |" % (lab, NOTE, m.group(1)), 1)
        # leave the LATER register (RUL-154): a role leaves it by a Decision change in its own row
        s = re.sub(r"^\| %s \| Home & care \| .*\n" % re.escape(lab), "", s, count=1, flags=re.M)
    assert re.search(r"^\| %s \|  \| IN \|" % re.escape(lab), s, re.M), lab
NEW = {
 "| House sitter |  | LATER |": [
  "| Carpet washer |  | IN | %s Carpets and upholstery in homes and offices; self-employed, so the reference reads 'A customer'. |" % NOTE,
  "| Au pair |  | IN | %s Lives with the family and minds the children. **Police clearance gates public visibility (RUL-153)**, same as Nanny. Tap override: *children's ages*. |" % NOTE,
  "| Tree cutter |  | IN | %s Felling, trimming and removal; the customer is the household or estate. |" % NOTE,
  "| Garden waste removal |  | IN | %s Refuse and garden-waste runs with a bakkie or trailer; a customer, not an employer. |" % NOTE],
 "| Banqueting / function staff |  | OUT |": [
  "| Griller / braai |  | IN | %s The braai at functions, shisanyamas and events; paid by the customer or the venue. |" % NOTE,
  "| Hotel porter |  | IN | %s Luggage and guest service at hotels; the hotel group enrols. |" % NOTE,
  "| Lodge staff |  | IN | %s Game-lodge and guest-lodge all-rounders (rooms, dining, guest care); the lodge enrols. |" % NOTE,
  "| Caterer |  | IN | %s Food for functions from her own kitchen; self-employed, so the reference reads 'A customer'. |" % NOTE],
 "| Security guard |  | IN |": [
  "| Bodyguard |  | IN | %s Close protection. PSIRA registration is a legal requirement: licence gate (RUL-156), publicly visible once PSIRA is verified. |" % NOTE],
}
for anchor, rows in NEW.items():
    if rows[0] in s: continue
    lines = s.split("\n"); idx = [i for i, l in enumerate(lines) if l.startswith(anchor)]
    assert len(idx) == 1, "slate anchor %s: %d" % (anchor, len(idx))
    lines[idx[0] + 1:idx[0] + 1] = rows; s = "\n".join(lines)
LOG = ("- **25 Sep 2026, RUL-172 (David + Claude):** the 42-type board on orchestrator/quick_listing.html was checked "
       "against the slate. David: 'All of them'. Pool cleaner, Window cleaner and Pet sitter / dog walker move LATER -> IN; "
       "nine board types never on the slate are added IN: Carpet washer, Au pair (clearance gate), Tree cutter, Garden waste "
       "removal, Griller / braai, Hotel porter, Lodge staff, Caterer, Bodyguard (PSIRA gate). House sitter stays LATER.")
if LOG not in s: s = s.rstrip("\n") + "\n" + LOG + "\n"
wr("ROLE_SLATE_REVIEW.md", s)

b = rd("scripts/build_role_registry.py")
EXTRA = '''
# ---- RUL-172 (David, 25 Sep 2026: "All of them") -- the board's types brought in ----
PIC.update({
 "pet_sitter_dog_walker": "a dog lead, a water bowl and a tennis ball on a leafy suburban garden path",
 "carpet_washer": "a carpet-cleaning machine on a half-cleaned lounge carpet, the clean stripe clearly brighter",
 "au_pair": "a family kitchen table with a child's lunchbox, school books and a car key ready for the school run",
 "tree_cutter": "a freshly felled tree trunk cut into rounds on a lawn, with a chainsaw and safety helmet beside it",
 "garden_waste_removal": "a bakkie load bin piled with branches and bagged garden refuse beside a tidy garden",
 "griller_braai": "meat and boerewors sizzling on a hot braai grid over glowing coals at an outdoor function",
 "hotel_porter": "a brass luggage trolley stacked with suitcases in a bright hotel lobby",
 "lodge_staff": "a game-lodge deck set for breakfast overlooking the bushveld at sunrise",
 "caterer": "a long buffet table of covered chafing dishes and platters set up for a function",
 "bodyguard": "a black sedan's open rear door at a hotel entrance at night with an earpiece on the seat",
})
AF.update({"pet_sitter_dog_walker": "Troeteldieroppasser / hondestapper", "carpet_washer": "Matskoonmaker",
 "au_pair": "Au pair", "tree_cutter": "Boomafkapper", "garden_waste_removal": "Tuinvullisverwydering",
 "griller_braai": "Braaier", "hotel_porter": "Hotelportier", "lodge_staff": "Lodge-personeel",
 "caterer": "Spysenier", "bodyguard": "Lyfwag"})
GATES.update({"au_pair": CLEAR, "bodyguard": LIC("psira")})
EK.update({"pool_cleaner": ["household", "estate"], "window_cleaner": ["household", "contract_cleaner"],
 "pet_sitter_dog_walker": ["household"], "carpet_washer": ["household", "contract_cleaner"], "au_pair": ["household"],
 "tree_cutter": ["household", "estate", "municipality"], "garden_waste_removal": ["household", "estate"],
 "griller_braai": ["restaurant", "caterer"], "hotel_porter": ["hotel_group"], "lodge_staff": ["hotel_group"],
 "caterer": ["caterer", "hotel_group"], "bodyguard": ["security_company"]})
STEP_OVERRIDES.update({"au_pair": {"what": AGES},
 "pet_sitter_dog_walker": {"what": {"key": "pets", "q": "Which pets do you look after?", "kind": "tile", "multi": True,
   "tiles": [{"t": "Dogs"}, {"t": "Cats"}, {"t": "Birds"}, {"t": "Other pets"}]}}})
'''
if "RUL-172 (David, 25 Sep 2026" not in b:
    a = "\ndef main():"; assert b.count(a) == 1; b = b.replace(a, EXTRA + a)
b = b.replace('"_rulings": ["RUL-150", "RUL-153", "RUL-154", "RUL-155", "RUL-156", "RUL-157"]',
              '"_rulings": ["RUL-150", "RUL-153", "RUL-154", "RUL-155", "RUL-156", "RUL-157", "RUL-172"]')
wr("scripts/build_role_registry.py", b)

r = rd("RULINGS.md")
RUL = ("| RUL-172 | 2026-09-25 | **EVERY TYPE ON THE 42-TYPE SERVICES BOARD IS A LIVE QUICK ROLE, AND THE SELF-EMPLOYED ARE "
       "VOUCHED FOR BY A CUSTOMER.** David, 25 Sep 2026, checking orchestrator/quick_listing.html against Quick (\"If a dog walker "
       "wants to list ... or if they are searching for a dog walker, do they end up with the right adverts?\"), answering both "
       "questions put to him: *\"All of them\"* and *\"Yes, 'A customer'\"*. RULED: **(a)** Pool cleaner, Window cleaner and Pet "
       "sitter / dog walker leave the RUL-154 LATER register and go IN; **(b)** nine board types never on the 19 Sep slate go IN: "
       "Carpet washer, Au pair (RUL-153 clearance gate, as Nanny), Tree cutter, Garden waste removal, Griller / braai, Hotel porter, "
       "Lodge staff, Caterer, Bodyguard (RUL-156 PSIRA gate) -- each with its own work picture (RUL-157), the Casuals taps and "
       "its own search match; **(c)** amending [[RUL-169]](b): the mostly self-employed casual roles -- Hair braider, "
       "Hairdresser, Nail technician, Car washer, Seamstress / tailor, Handyman, and the new Pool cleaner, Window cleaner, Pet "
       "sitter / dog walker, Carpet washer, Tree cutter, Garden waste removal, Griller / braai, Caterer -- read 'A customer' on "
       "the reference card and buzz 'your regular customers'; employed roles keep 'Your employer'; **(d)** a Services search for "
       "a role returns that role only (Car guard never returns Security guard). House sitter stays LATER. | "
       "ROLE_SLATE_REVIEW.md · scripts/build_role_registry.py · quick.html ROLES-25SEP-1 / SVC-FIND-1 · RG-0488 |")
if "| RUL-172 |" not in r:
    a = "\n\n## DECISIONS LOG"
    if a in r: r = r.replace(a, "\n" + RUL + a, 1)
    else:
        lines = r.split("\n"); last = max(i for i, l in enumerate(lines) if l.startswith("| RUL-171 |"))
        lines.insert(last + 1, RUL); r = "\n".join(lines)
wr("RULINGS.md", r)
print("ROLES-25SEP-1 slate + build tables + RUL-172 applied")
