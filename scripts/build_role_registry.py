#!/usr/bin/env python3
"""build_role_registry.py -- ROLE_SLATE_REVIEW.md -> roles/role_registry.json

The review file is the ONE source of the role decisions (RUL-154). This script only READS it
and adds the per-role data the spec s13 row needs. Never hand-edit role_registry.json:
change the slate or the maps below, then re-run. A second hand-kept copy of the slate is
exactly the forked-file failure spec s13 warns about.

Rulings honoured: RUL-150 (roles are rows; the employer never creates a listing),
RUL-153 (police-clearance gate), RUL-154 (LATER / routed rows are carried with a status),
RUL-155/156 (licence gate), RUL-157 (one picture of the WORK, never a person),
s13 naming (role name only, no collective noun).
"""
import io, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trainer_photo_prompts as TP   # TRAINER-PHOTOS-1 (David 10 Oct 2026): coach + people being coached

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SLATE = os.path.join(ROOT, "ROLE_SLATE_REVIEW.md")
OUT = os.path.join(ROOT, "roles", "role_registry.json")

# ---- class defaults: the four taps after the role pick (RUL-117 click budget) ----
# RUL-159: the door is  group -> role -> 3 class taps  = 5 taps to a draft (RUL-117). The old "what"
# tap is gone (the role says what she does); role-specific questions live on the FINISH screen.
PICKER_STEPS = [
    {"key": "group", "q": "What kind of work?", "kind": "tile", "source": "registry.group"},
    {"key": "role",  "q": "Which one are you?", "kind": "tile", "source": "registry.role", "photo": "role_picture"},
]
CASUALS_STEPS = [
    {"key": "where", "q": "Where can you work?",         "kind": "tile", "free": True},
    {"key": "days",  "q": "Which days are you open?",    "kind": "week"},
    {"key": "price", "q": "What do you charge a day?",   "kind": "chip"},
]
TECH_STEPS = [
    {"key": "qualification", "q": "What do you hold?", "kind": "tile",
     "tiles": [{"t": "Trade-tested"}, {"t": "Certificate"}, {"t": "Experience only"}]},
    {"key": "where",   "q": "Where can you work?",        "kind": "tile", "free": True},
    {"key": "callout", "q": "How do you charge?",         "kind": "chip",
     "tiles": [{"t": "Call-out fee"}, {"t": "Per hour"}, {"t": "Per day"}, {"t": "I quote"}]},
]
CAS_SIGNALS = ["clearance", "nqf", "exp_2_4", "exp_5plus", "ref_1", "ref_2", "profile"]
TECH_SIGNALS = ["trade_cert", "body_reg", "coc", "cidb", "insurance", "tickets",
                "exp_3_7", "exp_7plus", "strong_cv"]

# ---- role-specific overrides (RUL-153(d) and the sitting-1 calls) ----
AGES = {"key": "ages", "q": "Which ages do you care for?", "kind": "tile", "multi": True,
        "tiles": [{"t": "Babies"}, {"t": "Toddlers"}, {"t": "School age"}, {"t": "Teenagers"}]}
STEP_OVERRIDES = {
    "nanny": {"what": AGES},
    "creche_assistant": {"what": AGES},
    "caregiver": {"what": {"key": "cares_for", "q": "Who do you care for?", "kind": "tile", "multi": True,
                  "tiles": [{"t": "An older person"}, {"t": "A person with a disability"},
                            {"t": "Someone recovering at home"}]}},
    "housekeeper": {"days": {"key": "days", "q": "Which days are you open?", "kind": "week",
                    "extra": [{"t": "Live-in"}, {"t": "Live-out"}]}},
}

# ---- gates (RUL-153 / RUL-155 / RUL-156): listed at once, publicly visible once verified ----
CLEAR = {"type": "police_clearance", "ruling": "RUL-153"}
def LIC(*l): return {"type": "licence", "licences": list(l), "ruling": "RUL-156"}
GATES = {
    "nanny": CLEAR, "caregiver": CLEAR, "creche_assistant": CLEAR,
    # LICENCE-SHOWN-1 (RUL-198, David 3 Oct 2026): a plain driving licence is no longer a gate -- see SHOWN below.
    "code_10_code_14_driver": LIC("driving_licence", "prdp_g"),
    "taxi_shuttle_driver": LIC("driving_licence", "prdp_p"),
    "security_guard": LIC("psira"), "car_guard": LIC("psira"),
    "cctv_alarm_installer": LIC("psira"), "gate_garage_door_technician": LIC("psira"),
    "locksmith": LIC("psira"),
    "electrician": LIC("doel_electrician_registration"),
    "gas_installer": LIC("saqcc_gas"),
    "air_con_refrigeration_technician": LIC("saqcc_refrigerant"),
}

# ---- who enrols them (RUL-150 employer_kinds; the enrolment join) ----
EK = {
 "home_cleaner": ["household", "contract_cleaner"], "housekeeper": ["household"], "nanny": ["household"],
 "caregiver": ["household"], "cook": ["household"], "chef": ["hotel_group", "restaurant", "caterer"],
 "gardener": ["household", "municipality", "estate"], "handyman": ["household", "estate"],
 "creche_assistant": ["creche"], "room_attendant": ["hotel_group"],
 "kitchen_assistant": ["fast_food_franchise", "hotel_group", "restaurant"],
 "cashier": ["fast_food_franchise", "retailer", "fuel_station_dealer"],
 "waiter": ["restaurant", "hotel_group"], "bartender": ["restaurant", "hotel_group"],
 "event_staff": ["hotel_group", "caterer"], "petrol_attendant": ["fuel_station_dealer"],
 "shelf_packer": ["retailer"], "shop_assistant": ["retailer"], "merchandiser": ["retailer", "brand"],
 "car_guard": ["security_company"], "picker_packer": ["freight_operator", "retailer", "factory"],
 "removals_helper": ["freight_operator"], "delivery_rider": ["fast_food_franchise", "retailer"],
 "general_worker": ["municipality", "factory", "mine", "farm", "construction"],
 "farm_worker": ["farm"], "builders_assistant": ["construction"], "painter": ["construction"],
 "office_cleaner": ["contract_cleaner", "municipality"], "seamstress_tailor": ["clothing_factory"],
 "sewing_machinist": ["clothing_factory"], "security_guard": ["security_company"],
 "plant_operator_tlb_excavator": ["construction", "mine", "municipality"],
 "welder": ["mine", "factory", "construction"], "boilermaker": ["mine", "factory"],
 "forklift_operator": ["freight_operator", "factory", "retailer"],
 "driver": ["freight_operator", "municipality", "mine", "farm"],
 "code_10_code_14_driver": ["freight_operator", "mine"], "taxi_shuttle_driver": ["transport_operator"],
 "diesel_mechanic": ["mine", "freight_operator", "farm"], "motor_mechanic": ["dealership"],
 "auto_electrician": ["mine", "freight_operator", "dealership"],
 "electrician": ["mine", "construction", "municipality"], "plumber": ["construction", "municipality"],
}

# ---- what the ROLE PICTURE shows (RUL-157): the work, never a person, never hands ----
PIC = {
 "home_cleaner": "a spotless sunlit lounge with a neatly folded cleaning cloth, spray bottle and bucket on a gleaming tiled floor",
 "housekeeper": "a perfectly made bed with crisp white linen, folded towels and a tidy bedside table",
 "nanny": "a bright playroom with wooden building blocks, a picture book and a small backpack neatly arranged",
 "caregiver": "a comfortable armchair beside a window with a folded blanket, reading glasses, a cup of tea and a walking stick",
 "cook": "a home kitchen counter with a pot of stew simmering, chopped vegetables on a board and fresh bread",
 "chef": "a professional stainless-steel kitchen pass with plated dishes under warm lights and a chef's knife",
 "gardener": "a freshly mown suburban lawn with neat flower beds, a rake and a wheelbarrow",
 "handyman": "an open toolbox with a drill, spirit level and screwdrivers beside a newly hung door",
 "pool_cleaner": "a crystal-clear blue swimming pool with a pool net and a brush resting on the paving",
 "window_cleaner": "a squeegee and bucket beside a streak-free window reflecting a blue sky",
 "pet_sitter_dog_walker": "a dog lead, water bowl and ball on a garden path",
 "house_sitter": "a front door with a set of house keys on a hook and potted plants on the step",
 "creche_assistant": "a colourful creche room with small tables, crayons, drawings on the wall and tiny chairs",
 "room_attendant": "a hotel room with a freshly made bed, folded towels and a housekeeping trolley in the doorway",
 "kitchen_assistant": "a busy commercial kitchen prep station with stacked clean plates and chopped ingredients",
 "cashier": "a tidy shop till counter with a card machine and a neat row of receipts",
 "waiter": "a restaurant table set with glasses, cutlery and a tray carrying two plated meals",
 "barista": "an espresso machine pouring coffee with a latte-art cup on the counter",
 "bartender": "a bar counter with polished glasses, a cocktail shaker and bottles on backlit shelves",
 "baker": "fresh loaves and rolls cooling on racks in a bakery",
 "butchery_assistant": "a clean butchery display counter with neatly cut meat and a scale",
 "event_staff": "a function hall with round tables set with white cloths, glasses and centrepieces",
 "petrol_attendant": "a fuel pump nozzle in a car's fuel inlet at a South African forecourt, with a squeegee on the island",
 "shelf_packer": "a supermarket aisle with perfectly faced, fully stocked shelves",
 "shop_assistant": "a neat small shop counter with goods displayed on shelves behind it",
 "merchandiser": "a branded promotional shelf display being fully stocked in a supermarket, with a clipboard (no readable brand names)",
 "car_guard": "a bright reflective vest folded on a bollard in a shopping-centre parking lot",
 "picker_packer": "a warehouse aisle with a pallet of packed, taped boxes and a handheld scanner",
 "removals_helper": "a moving truck with its doors open, wrapped furniture and stacked boxes inside",
 "delivery_rider": "a delivery motorbike with a top box parked at a kerb",
 "general_worker": "a pair of work gloves, a shovel and a wheelbarrow on a work site",
 "farm_worker": "rows of crops in a South African field at golden hour with a crate of harvested produce",
 "builders_assistant": "a half-built brick wall with a trowel, mortar tub and stacked bricks",
 "painter": "a freshly painted wall with a roller tray, roller and drop sheet",
 "office_cleaner": "a clean open-plan office with a cleaning trolley at the end of the row",
 "seamstress_tailor": "a sewing machine with measuring tape, pins and a half-finished garment",
 "sewing_machinist": "an industrial sewing machine with a stack of cut fabric pieces",
 "hair_braider": "a set of neat finished braids on a salon mannequin head with combs and hair extensions",
 "hairdresser": "a salon station with scissors, combs, a hairdryer and a mirror",
 "nail_technician": "a manicure station with polish bottles, a nail file and a neatly finished set of nail tips on a display",
 "car_washer": "a gleaming freshly washed car with a bucket, sponge and foam",
 "cobbler": "a shoe repair bench with a resoled shoe, a hammer and leather offcuts",
 "security_guard": "a guardhouse at a boom gate at dusk with a torch and a logbook",
 "plant_operator_tlb_excavator": "a yellow TLB digging a trench on a building site",
 "rigger": "steel slings and shackles hooked to a crane load on a site",
 "boilermaker": "heavy steel plate being cut with sparks in a workshop",
 "millwright": "an opened industrial gearbox with tools laid out beside it",
 "fitter_turner": "a metal lathe turning a steel shaft with coolant spray",
 "welder": "a welding bead glowing with bright sparks on a steel joint, welding helmet on the bench",
 "crane_operator": "a mobile crane lifting a steel beam against a blue sky",
 "forklift_operator": "a forklift lifting a pallet in a warehouse",
 "driver": "a clean light delivery vehicle parked at a loading bay",
 "code_10_code_14_driver": "a truck and trailer on an open South African highway",
 "taxi_shuttle_driver": "a white minibus shuttle parked at a pickup point",
 "diesel_mechanic": "an open diesel engine bay of a truck with a torque wrench",
 "motor_mechanic": "a car on a lift in a workshop with tools on a trolley",
 "auto_electrician": "a multimeter clipped to a car battery with wiring harness exposed",
 "panel_beater": "a car door panel mid-repair with filler and a sanding block",
 "spray_painter": "a freshly sprayed glossy car panel in a spray booth",
 "tyre_fitter": "a tyre on a balancing machine with new tyres stacked beside it",
 "electrician": "an open distribution board with neat wiring and a voltage tester",
 "gas_installer": "a gas hob connected to a gas bottle with new copper piping and a regulator",
 "plumber": "new copper pipes and a geyser installation with a pipe wrench",
 "bricklayer": "a straight brick wall with a spirit level and trowel",
 "plasterer": "a smoothly plastered wall with a plastering float and hawk",
 "tiler": "a freshly tiled floor with spacers, a tile cutter and grout float",
 "carpenter": "a workbench with a hand plane, wood shavings and a finished cabinet door",
 "roofer": "a corrugated iron roof being fitted with roofing screws and a sealed flashing",
 "glazier": "a large glass pane being fitted into an aluminium window frame",
 "ceiling_partition_installer": "a new ceiling grid with boards partly installed in an office",
 "paver": "freshly laid interlocking paving in a driveway with a rubber mallet",
 "air_con_refrigeration_technician": "a wall-mounted air conditioner with its cover off and refrigerant gauges attached",
 "solar_pv_installer": "solar panels mounted on a South African roof under a clear sky with an inverter on the wall",
 "borehole_pump_technician": "a borehole pump and pressure tank beside a green water tank",
 "cctv_alarm_installer": "a CCTV camera mounted under the eaves of a house with an alarm keypad",
 "gate_garage_door_technician": "a sliding gate motor with its cover open beside a steel gate",
 "locksmith": "a door lock cylinder taken apart with keys and locksmith picks",
 "appliance_repair": "a washing machine with its back panel off and a toolkit",
 "it_networking_technician": "a neat network cabinet with patched cables and a router",
 "small_engine_repair": "a lawnmower engine on a workbench with a spark plug and tools",
}

AF = {  # Afrikaans labels (David reads Afrikaans; zu / st / xh need a native speaker, RUL-149)
 "home_cleaner": "Huisskoonmaker", "housekeeper": "Huishoudster", "nanny": "Kinderoppasser",
 "caregiver": "Versorger", "cook": "Kok", "chef": "Sjef", "gardener": "Tuinier", "handyman": "Handwerksman",
 "pool_cleaner": "Swembadskoonmaker", "window_cleaner": "Vensterskoonmaker",
 "pet_sitter_dog_walker": "Troeteldieroppasser / honde-stapper", "house_sitter": "Huisoppasser",
 "creche_assistant": "Crèche-assistent", "room_attendant": "Kamerbediende", "kitchen_assistant": "Kombuisassistent",
 "cashier": "Kassier", "waiter": "Kelner", "barista": "Barista", "bartender": "Kroegman",
 "baker": "Bakker", "butchery_assistant": "Slaghuisassistent", "event_staff": "Funksiepersoneel",
 "petrol_attendant": "Petroljoggie", "shelf_packer": "Rakpakker", "shop_assistant": "Winkelassistent",
 "merchandiser": "Uitstaller", "car_guard": "Motorwag", "picker_packer": "Uitsoeker / pakker",
 "removals_helper": "Verhuishelper", "delivery_rider": "Afleweringsryer", "general_worker": "Algemene werker",
 "farm_worker": "Plaaswerker", "builders_assistant": "Bouersassistent", "painter": "Verwer",
 "office_cleaner": "Kantoorskoonmaker", "seamstress_tailor": "Naaldwerkster / kleremaker",
 "sewing_machinist": "Naaimasjienwerker", "hair_braider": "Haarvlegter", "hairdresser": "Haarkapper",
 "nail_technician": "Naelterapeut", "car_washer": "Karwasser", "cobbler": "Skoenmaker",
 "security_guard": "Sekuriteitswag", "plant_operator_tlb_excavator": "Masjienoperateur (TLB / graaf)",
 "rigger": "Tuier", "boilermaker": "Ketelmaker", "millwright": "Meulmaker", "fitter_turner": "Passer en draaier",
 "welder": "Sweiser", "crane_operator": "Hyskraanoperateur", "forklift_operator": "Vurkhyseroperateur",
 "driver": "Bestuurder", "code_10_code_14_driver": "Kode 10 / Kode 14-bestuurder",
 "taxi_shuttle_driver": "Taxi- / pendelbestuurder", "diesel_mechanic": "Dieselwerktuigkundige",
 "motor_mechanic": "Motorwerktuigkundige", "auto_electrician": "Motorelektrisiën", "panel_beater": "Duikklopper",
 "spray_painter": "Spuitverwer", "tyre_fitter": "Bandpasser", "electrician": "Elektrisiën",
 "gas_installer": "Gasinstalleerder", "plumber": "Loodgieter", "bricklayer": "Messelaar", "plasterer": "Pleisteraar",
 "tiler": "Teëlêer", "carpenter": "Timmerman", "roofer": "Dakwerker", "glazier": "Glaswerker",
 "ceiling_partition_installer": "Plafon- en afskortinginstalleerder", "paver": "Plaveier",
 "air_con_refrigeration_technician": "Lugversorging- en verkoelingstegnikus",
 "solar_pv_installer": "Sonkraginstalleerder", "borehole_pump_technician": "Boorgat- en pomptegnikus",
 "cctv_alarm_installer": "Kringtelevisie- en alarminstalleerder",
 "gate_garage_door_technician": "Hek- en motorhuisdeurtegnikus", "locksmith": "Slotmaker",
 "appliance_repair": "Toestelherstelwerk", "it_networking_technician": "IT- en netwerktegnikus",
 "small_engine_repair": "Kleinenjinherstelwerk",
}

PICTURE_STYLE = ("Photorealistic photograph, natural daylight, a South African setting. Subject: {subject}. "
 "The picture must make the job instantly recognisable from the work alone. "
 "ABSOLUTELY NO people, no faces, no hands, no body parts, no silhouettes. "
 "No text, no letters, no logos, no brand names, no watermarks. "
 "Square 1:1, clean uncluttered composition, subject centred, gentle depth of field, warm and dignified mood.")

def slug(s):
    s = s.replace("è", "e").replace("'", "")
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")

MERGED = {  # OUT rows that live on as a search alias of a live role (explicit, not parsed)
 "home_nurse_aide": "caregiver", "laundry_ironing": "home_cleaner",
 "dishwasher_kitchen_porter": "kitchen_assistant", "banqueting_function_staff": "event_staff",
 "stock_assistant": "shelf_packer", "loader": "general_worker", "factory_worker_general": "general_worker",
 "municipal_worker_general": "general_worker", "grounds_landscaping_help": "gardener",
 "long_haul_driver": "code_10_code_14_driver", "painter_qualified": "painter", "waterproofing": "roofer",
}
SPLIT = {"miner_general", "industry_worker_skilled"}  # buckets: the person picks the real trade

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
# ---- LICENCE-SHOWN-1 (RUL-198, David 3 Oct 2026, amends RUL-156 (a)/(b) for the plain driving licence): "We are
# denying this listing based on us not having verified the drivers license but this is not the same as the caretakers
# checks that is legally required ... still allow him to list but we just show his TS as license not verified." A role
# whose only licence is a driving licence is listed publicly at once; buyers see 'Driving licence not verified' until
# our team checks it, it earns nothing until then, and introductions go ahead. A PrDP (a professional permit) stays a gate.
SHOWN = {"driver": ["driving_licence"], "delivery_rider": ["driving_licence_code_a"]}
EK.update({"pool_cleaner": ["household", "estate"], "window_cleaner": ["household", "contract_cleaner"],
 "pet_sitter_dog_walker": ["household"], "carpet_washer": ["household", "contract_cleaner"], "au_pair": ["household"],
 "tree_cutter": ["household", "estate", "municipality"], "garden_waste_removal": ["household", "estate"],
 "griller_braai": ["restaurant", "caterer"], "hotel_porter": ["hotel_group"], "lodge_staff": ["hotel_group"],
 "caterer": ["caterer", "hotel_group"], "bodyguard": ["security_company"]})
STEP_OVERRIDES.update({"au_pair": {"what": AGES},
 "pet_sitter_dog_walker": {"what": {"key": "pets", "q": "Which pets do you look after?", "kind": "tile", "multi": True,
   "tiles": [{"t": "Dogs"}, {"t": "Cats"}, {"t": "Birds"}, {"t": "Other pets"}]}}})

# ---- TRAINERS-DOOR-1 (RUL-217, David 8 Oct 2026): "the same for tutors, but for a branch of tutors namely Trainers ...
# all of the sports types one can get a trainer for ... the same flows, Hows etc ... To also make it Global". A door inside
# Tutors, built the way Casuals were built inside Services: adverts write category Tutors, service_class Trainers (Trust
# Score key Tutors-Trainers -> the Tutors evidence set). Prices are per session / per month / per package: no wage floor. ----
TRAINER_STEPS = [
    {"key": "where", "q": "Where do you train people?", "kind": "tile", "free": True},
    {"key": "price", "q": "What do you charge?", "kind": "chip",
     "tiles": [{"t": "Per session"}, {"t": "Per month"}, {"t": "Per package"}], "floor": None, "ruling": "RUL-217(c)"},
]
TRAINER_SIGNALS = ["category.tutors.clearance", "category.tutors.specialisation", "category.tutors.safeguarding",
                   "category.tutors.cert_diploma", "category.tutors.exp_2_5", "category.tutors.exp_5plus"]
TRAINER_DOOR = {"category": "Tutors", "service_class": "Trainers", "trust_key": "Tutors-Trainers",
                "entry_tile": "Sport & fitness", "picker_steps": ["what=Sport & fitness", "group", "role"],
                "taps_to_draft": 5, "price_units": ["session", "month", "package"], "wage_floor": False,
                "ruling": "RUL-217"}
TRAINER_ALIASES = {
 "personal_trainer": ["Gym trainer", "Fitness trainer", "Bodybuilding coach"],
 "functional_fitness_coach": ["CrossFit coach", "Bootcamp instructor"], "dance_fitness_instructor": ["Dance instructor"],
 "kickboxing_coach": ["Muay Thai coach"], "mma_coach": ["Mixed martial arts coach"], "jiu_jitsu_instructor": ["BJJ coach"],
 "soccer_coach": ["Football coach"], "hockey_coach": ["Field hockey coach", "Ice hockey coach"],
 "baseball_coach": ["Softball coach"], "swimming_coach": ["Swimming teacher", "Learn-to-swim instructor"],
 "diving_instructor": ["Scuba instructor", "Freediving instructor"],
 "rowing_canoeing_coach": ["Rowing coach", "Canoeing coach", "Kayaking coach"],
 "running_athletics_coach": ["Running coach", "Athletics coach", "Track coach"],
 "horse_riding_instructor": ["Riding instructor", "Equestrian coach"],
 "climbing_instructor": ["Rock climbing instructor", "Bouldering coach"],
 "skating_coach": ["Ice skating coach", "Roller skating coach", "Skateboarding coach"],
 "ski_snowboard_instructor": ["Ski instructor", "Snowboard instructor"],
}
PIC.update({
 "personal_trainer": "a gym floor with a rack of dumbbells, a weight bench and a kettlebell in morning light",
 "aerobics_instructor": "a bright aerobics studio with step platforms, a mirror wall and a speaker on the floor",
 "dance_fitness_instructor": "an empty dance studio with a wooden sprung floor, a ballet barre and a sound system",
 "yoga_instructor": "rolled-out yoga mats with blocks and a strap in a calm sunlit studio with plants",
 "pilates_instructor": "a Pilates reformer machine with a Pilates ring and a mat in a light studio",
 "functional_fitness_coach": "a functional training box with kettlebells, a rowing machine, battle ropes and plyo boxes",
 "strength_conditioning_coach": "a loaded barbell on a lifting platform with bumper plates, chalk and a stopwatch",
 "boxing_coach": "a boxing ring corner with a pair of red gloves and pads hanging on the ropes",
 "kickboxing_coach": "a heavy kick bag, shin guards and gloves on a gym mat",
 "wrestling_coach": "a wrestling mat with its circle markings in an empty school gym",
 "judo_instructor": "a neatly folded white judogi with a belt on a tatami mat",
 "karate_instructor": "a folded white karate gi with a black belt on a polished dojo floor",
 "taekwondo_instructor": "a taekwondo dobok, a head guard and a kicking paddle on a blue mat",
 "jiu_jitsu_instructor": "a folded jiu-jitsu gi with a brown belt on a grappling mat",
 "mma_coach": "an empty MMA cage with fingerless gloves on the canvas",
 "fencing_coach": "a fencing mask and two foils crossed on a fencing piste",
 "soccer_coach": "a soccer ball and training cones on a green pitch in front of a goal",
 "rugby_coach": "a rugby ball on a kicking tee on a grass field with the posts behind",
 "cricket_coach": "a cricket bat, ball and stumps on a green practice net pitch",
 "hockey_coach": "a field hockey stick and ball on an artificial turf pitch",
 "netball_coach": "a netball resting under a netball hoop on an outdoor court",
 "basketball_coach": "a basketball on a polished indoor court under the hoop",
 "volleyball_coach": "a volleyball by the net on a beach volleyball court",
 "baseball_coach": "a baseball glove, ball and bat on a diamond infield",
 "american_football_coach": "an American football on a turf field at the yard line",
 "tennis_coach": "a tennis racket and a basket of yellow balls on a hard court by the net",
 "squash_coach": "a squash racket and ball on the wooden floor of a squash court",
 "padel_coach": "a padel racket and ball on a blue padel court with glass walls",
 "badminton_coach": "a badminton racket and shuttlecock on an indoor court by the net",
 "table_tennis_coach": "a table tennis bat and ball on a blue table with the net",
 "golf_coach": "a golf ball on a tee with a driver on a driving-range mat at sunrise",
 "archery_coach": "a recurve bow and arrows in front of a target on an outdoor archery range",
 "swimming_coach": "an outdoor swimming pool with lane ropes, a kickboard and goggles on the edge",
 "diving_instructor": "scuba tanks, a mask and fins on a boat deck over clear blue water",
 "surfing_coach": "a surfboard on the sand at the water's edge with rolling waves",
 "rowing_canoeing_coach": "a canoe with paddles at the edge of a calm dam at dawn",
 "sailing_instructor": "a small sailing dinghy with its sail up at a jetty on a lake",
 "running_athletics_coach": "an athletics track with lane lines, starting blocks and running shoes",
 "cycling_coach": "a road bicycle and a helmet on a quiet tarred road at sunrise",
 "triathlon_coach": "a triathlon transition rack with a bike, running shoes, goggles and a swim cap",
 "horse_riding_instructor": "a saddled horse's tack: a saddle, bridle and riding helmet on a stable fence by an arena",
 "climbing_instructor": "a coiled climbing rope, harness and chalk bag at the foot of a rock face",
 "skating_coach": "a pair of ice skates on the edge of a smooth ice rink",
 "ski_snowboard_instructor": "skis, poles and a snowboard in fresh snow on a mountain slope",
 "gymnastics_coach": "a balance beam and gymnastics mats in a bright gym hall",
 "acrobatics_coach": "an acrobatics hall with a tumbling track, crash mats and aerial silks hanging",
 "chess_coach": "a wooden chess board mid-game with a chess clock on a table",
})
AF.update({
 "personal_trainer": "Persoonlike afrigter", "aerobics_instructor": "Aërobiese instrukteur",
 "dance_fitness_instructor": "Dansfiksheid-instrukteur", "yoga_instructor": "Joga-instrukteur",
 "pilates_instructor": "Pilates-instrukteur", "functional_fitness_coach": "Funksionele fiksheidsafrigter",
 "strength_conditioning_coach": "Krag- en kondisioneringsafrigter", "boxing_coach": "Boksafrigter",
 "kickboxing_coach": "Skopboksafrigter", "wrestling_coach": "Stoei-afrigter", "judo_instructor": "Judo-instrukteur",
 "karate_instructor": "Karate-instrukteur", "taekwondo_instructor": "Taekwondo-instrukteur",
 "jiu_jitsu_instructor": "Jiu-jitsu-instrukteur", "mma_coach": "MMA-afrigter", "fencing_coach": "Skermafrigter",
 "soccer_coach": "Sokkerafrigter", "rugby_coach": "Rugbyafrigter", "cricket_coach": "Krieketafrigter",
 "hockey_coach": "Hokkie-afrigter", "netball_coach": "Netbalafrigter", "basketball_coach": "Basketbalafrigter",
 "volleyball_coach": "Vlugbalafrigter", "baseball_coach": "Bofbalafrigter",
 "american_football_coach": "Amerikaanse voetbalafrigter", "tennis_coach": "Tennisafrigter",
 "squash_coach": "Muurbalafrigter", "padel_coach": "Padel-afrigter", "badminton_coach": "Pluimbalafrigter",
 "table_tennis_coach": "Tafeltennisafrigter", "golf_coach": "Gholfafrigter", "archery_coach": "Boogskietafrigter",
 "swimming_coach": "Swemafrigter", "diving_instructor": "Duikinstrukteur", "surfing_coach": "Branderplankafrigter",
 "rowing_canoeing_coach": "Roei- en kano-afrigter", "sailing_instructor": "Seilinstrukteur",
 "running_athletics_coach": "Hardloop- en atletiekafrigter", "cycling_coach": "Fietsryafrigter",
 "triathlon_coach": "Driekamp-afrigter", "horse_riding_instructor": "Perdry-instrukteur",
 "climbing_instructor": "Klim-instrukteur", "skating_coach": "Skaats-afrigter",
 "ski_snowboard_instructor": "Ski- en sneeuplankinstrukteur", "gymnastics_coach": "Gimnastiekafrigter",
 "acrobatics_coach": "Akrobatiekafrigter", "chess_coach": "Skaakafrigter",
})
# RUL-217(d) AMENDED by RUL-219 (David 10 Oct 2026): trainer types that commonly coach children carry NO visibility gate --
# a police clearance is a Trust Score signal for them (category.tutors.clearance), never a blocker. Set kept for guides/hints.
TRAINER_CLEAR = {"wrestling_coach", "judo_instructor", "karate_instructor", "taekwondo_instructor", "soccer_coach",
 "rugby_coach", "cricket_coach", "hockey_coach", "netball_coach", "basketball_coach", "volleyball_coach", "baseball_coach",
 "american_football_coach", "tennis_coach", "squash_coach", "badminton_coach", "table_tennis_coach", "golf_coach",
 "swimming_coach", "surfing_coach", "running_athletics_coach", "horse_riding_instructor", "climbing_instructor",
 "skating_coach", "ski_snowboard_instructor", "gymnastics_coach", "acrobatics_coach", "chess_coach"}
# (no GATES entry for TRAINER_CLEAR -- INTRO-ONLY-1 / RUL-219)
TRAINER_PICTURE_STYLE = PICTURE_STYLE.replace("a South African setting", "a neutral setting that reads anywhere in the world")

ROLE_PATCH = json.loads('{"car_washer": {"note": "Mobile washers come to homes and offices — a direct hire. CARWASH-1 (David, 7 Oct 2026): priced per car and per kind of clean (wash only / wash & vacuum / wash, vacuum, tyres & dashboard / full valet), never per hour; area-bound like a cleaner; regulars rebook him through Buzz.", "questions": [{"key": "where", "q": "Where can you work?", "kind": "tile", "free": true}, {"key": "days", "q": "Which days are you open?", "kind": "week"}, {"key": "price", "q": "What do you charge per car?", "kind": "chip"}], "price_menu": ["Wash only", "Wash & vacuum", "Wash, vacuum, tyres & dashboard", "Full valet (inside & out)"], "employer_kinds": ["household", "business"]}}')

def main():
    t = io.open(SLATE, encoding="utf-8").read()
    body = t.split("## RULED")[0]
    cls = None; group = None; roles = []
    for line in body.split("\n"):
        if line.startswith("# SERVICES"):
            cls = "Casuals" if "CASUALS" in line else "Technical"
        elif line.startswith("# TUTORS"):        # TRAINERS-DOOR-1 (RUL-217)
            cls = "Trainers"
        elif line.startswith("### "):
            group = line[4:].strip()
        elif cls and line.startswith("| ") and not line.startswith("| Role"):
            c = [x.strip() for x in line.split("|")]
            label, d, dec, notes = c[1], c[2], c[3], c[4]
            if dec not in ("IN", "LATER", "OUT", "HOLD"):
                sys.exit("UNDECIDED ROW in slate: %s -- decide it in the review first" % label)
            key = slug(label)
            row = {"key": key, "label": {"en": label, "af": AF.get(key), "zu": None, "st": None, "xh": None},
                   "service_class": cls, "group": group, "status": dec.lower(),
                   "on_davids_list": d == "D"}
            if dec == "OUT":
                if "RUL-124" in notes: row["routed_to"] = "position_lane_RUL-124"
                elif key in SPLIT: row["split"] = True
                elif key in MERGED: row["merged_into"] = MERGED[key]
                row["note"] = notes
                roles.append(row); continue
            if cls == "Trainers":    # TRAINERS-DOOR-1 (RUL-217)
                row["category"] = "Tutors"; row["door"] = "tutors"
                row["questions"] = [dict(s) for s in TRAINER_STEPS]
                row["finish_questions"] = []
                row["enrol_link"] = "/q/tutors?role=%s" % key
                row["signals"] = list(TRAINER_SIGNALS) + (["category.tutors.fide_ft", "category.tutors.fide_fi"]
                                                          if key == "chess_coach" else [])
                if key in TRAINER_ALIASES: row["aliases"] = list(TRAINER_ALIASES[key])
            else:
              steps = [dict(s) for s in (CASUALS_STEPS if cls == "Casuals" else TECH_STEPS)]
              row["questions"] = steps
              row["finish_questions"] = list(STEP_OVERRIDES.get(key, {}).values())
              row["enrol_link"] = "/q/services?role=%s" % key  # employer invite skips taps 1-2 (RUL-159)
              row["signals"] = ["category.services_%s.%s" % ("cas" if cls == "Casuals" else "tech", s)
                                for s in (CAS_SIGNALS if cls == "Casuals" else TECH_SIGNALS)]
            row["gate"] = GATES.get(key)
            if key in TRAINER_CLEAR:   # RUL-219: a checked clearance earns Trust Score points; never a visibility gate
                row["clearance_score"] = {"signal": "category.tutors.clearance", "ruling": "RUL-219"}
            if key in SHOWN:   # LICENCE-SHOWN-1: shown to buyers as checked or not, never a gate
                row["licence_shown"] = {"licences": SHOWN[key], "label": "Driving licence", "ruling": "RUL-198"}
            row["employer_kinds"] = EK.get(key, ["household"] if cls == "Casuals" else [])
            if key not in PIC: sys.exit("NO ROLE PICTURE SUBJECT for %s (RUL-157)" % key)
            row["role_picture"] = {"file": "roles/pictures/%s.png" % key,
                                   "prompt": (TP.STYLE.format(subject=TP.SUBJECT[key]) if cls == "Trainers"   # TRAINER-PHOTOS-1
                                              else PICTURE_STYLE.format(subject=PIC[key]))}
            row["draft_title"] = {"en": "%s available in {where}" % label,
                                  "af": ("%s beskikbaar in {where}" % AF[key]) if AF.get(key) else None}
            row["note"] = notes
            roles.append(row)
    # CARWASH-1 (David, 7 Oct 2026) was written straight into role_registry.json, so a re-run dropped it. Carried here
    # now (found by the RUL-217 build, 10 Oct 2026) -- the builder stays the one writer.
    for r in roles:
        if r["key"] in ROLE_PATCH: r.update(json.loads(json.dumps(ROLE_PATCH[r["key"]])))
    # aliases: every OUT row merged into a live row becomes a search synonym on it
    by = {r["key"]: r for r in roles}
    for r in roles:
        tgt = r.get("merged_into")
        if tgt:
            assert tgt in by and by[tgt]["status"] != "out", "merge target %s missing" % tgt
            by[tgt].setdefault("aliases", []).append(r["label"]["en"])
    keys = [r["key"] for r in roles]
    assert len(keys) == len(set(keys)), "duplicate role key"
    out = {"_generated_by": "scripts/build_role_registry.py from ROLE_SLATE_REVIEW.md -- never hand-edit",
           "_rulings": ["RUL-150", "RUL-153", "RUL-154", "RUL-155", "RUL-156", "RUL-157", "RUL-172", "RUL-217"],
           "_invariant": "Enrolment creates an account and a sign-in link, never a listing (RUL-150).",
           "door": {"category": "services", "picker_steps": PICKER_STEPS, "taps_to_draft": 5,
                    "ruling": "RUL-159"},
           "trainers_door": TRAINER_DOOR,
           "counts": {s: sum(1 for r in roles if r["status"] == s) for s in ("in", "later", "out")},
           "roles": roles}
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print("wrote %s: %d roles %s" % (os.path.relpath(OUT, ROOT), len(roles), out["counts"]))

if __name__ == "__main__":
    main()
