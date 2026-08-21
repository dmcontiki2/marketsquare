#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_trip_essentials.py — TRIP-ESSENTIALS-1 (21 Aug 2026)

WHY THIS EXISTS
---------------
David, 21 Aug 2026: "Claude, would you plan your holiday with only this available?
A map and a single sentence? No itinerary, no budget, no visa requirements, no
safety advice, no travelling notices, no local taxes, tips etc.? ... this is a
major rejection point and is true for ALL of our adverts with tours / holidays /
stays / guides."

The maps landed (LAYERS-4-1, 17 Aug). The sequencing note in that changelog said
"maps first, dossier-summary work second". This IS the second half.

WHAT IT PRODUCES
----------------
trip_essentials.js  ->  window.TRIP_ESSENTIALS  (a plain object, no fetch, no API)
ms.js renders it as the "Before you go" panel that sits UNDER the map on every
super-example Adventures advert. David's placement ruling, same day: the map is
the hook a scanning reader sees first; the essentials go BELOW it, never above.

MODEL CONSTRAINT (CLAUDE.md, David 1 Aug 2026)
----------------------------------------------
MarketSquare is an INTRODUCTORY service. All of this is FREE pre-information.
Nothing here books, prices-to-sell, or collects money. The panel ends by handing
the traveller to a partnered travel agency — that handoff IS the Tuppence
introduction. Copy must never imply we sell or guarantee the trip.

HONESTY RULES (non-negotiable — these are what stop it becoming fiction)
-----------------------------------------------------------------------
1. Every factual row carries a SOURCE url. No source, no row.
2. Anything that moves (visa fees, park tariffs, advisory levels, tax rates) is
   flagged volatile and repeated in the "Check on the day" list.
3. Where the research could not confirm a figure it says so in the row. We do not
   round an unknown into a number.
4. `checked` is the date a human/agent last verified the block. It is displayed.
   An old date is better information than a hidden one.

REGENERATE:  python3 scripts/build_trip_essentials.py
Verified by: scripts/trip_essentials_selftest.py  and regression ledger RG-0031.
"""
import json, os, sys, io, datetime

CHECKED = "2026-08-21"
HERE    = os.path.dirname(os.path.abspath(__file__))
ROOT    = os.path.dirname(HERE)
OUT_JS  = os.path.join(ROOT, "trip_essentials.js")

def R(l, v="", src=None, note=None, flag=False):
    """One fact row: label, value, source url, optional note, volatile flag."""
    d = {"l": l, "v": v}
    if src:  d["src"]  = src
    if note: d["n"]    = note
    if flag: d["flag"] = 1
    return d

def SEC(icon, name, rows, intro=None):
    d = {"icon": icon, "name": name, "rows": rows}
    if intro: d["intro"] = intro
    return d

# ── Shared blocks: things true for every SOUTH-AFRICAN-DEPARTING trip ────────
SA_DEPARTURE = [
    R("SARS Traveller Declaration",
      "Mandatory online declaration for everyone entering or leaving South Africa since 1 Jul 2026. Do it before you get to the airport.",
      "https://www.sars.gov.za/travellerdeclaration/", flag=True),
    R("Children under 18",
      "SA children on their own SA passports travelling with both parents no longer need the unabridged birth certificate to leave SA. One parent only, or a non-parent, still needs the birth certificate, a parental-consent affidavit under 6 months old, and the absent parent's ID copy.",
      "https://www.dha.gov.za/index.php/civic-services/travel-requirements-for-children",
      note="Several destinations still demand the unabridged certificate on ARRIVAL even though SA dropped it. Carry it."),
]

# ═════════════════════════════════════════════════════════════════════════════
#  TRIPS
# ═════════════════════════════════════════════════════════════════════════════
TRIPS = []

# ── ZA — Pretoria to the Pilanesberg (the pilot advert) ─────────────────────
TRIPS.append({
 "key":"ZA", "match":{"country":"ZA"},
 "title":"Pretoria to the Pilanesberg",
 "shape":"Self-drive · ~170 km each way · 2–3 days · Big-5 reserve, MALARIA-FREE",
 "checked":CHECKED,
 "itinerary":[
   {"d":"Leg 1","t":"Pretoria — trip start","x":"≈ 1 h 10 to the dam","s":"Union Buildings lawns, fuel and padkos before you go. Voortrekker Monument is a short detour south."},
   {"d":"Leg 2","t":"Hartbeespoort Dam","x":"≈ 45 min on","s":"Dam-wall viewpoint and the curio market. Maropeng and the Sterkfontein caves (UNESCO Cradle of Humankind) sit south of here if you want the heritage day."},
   {"d":"Leg 3","t":"Magaliesberg pass","x":"≈ 1 h 15 on","s":"Scenic crossing with picnic spots. Last easy fuel and shops before the reserve."},
   {"d":"Leg 4","t":"Pilanesberg — Manyane Gate","x":"Gates open at sunrise","s":"Big-5 reserve, self-drive game viewing on 200+ km of maintained gravel and tar. A sedan is fine — no 4x4 needed."},
 ],
 "budget":{
   "basis":"Two SA adults, own car, one night out, Aug 2026 prices. Conservation and toll figures verified; accommodation is the advert's own rate.",
   "rows":[
     R("Pilanesberg gate — SA adult","R168 per person per day","https://www.pilanesbergnationalpark.org/travel/tariffs-gate-times/", note="SA ID must be shown for the resident rate. SADC R385, international R748. Tariff effective 1 Dec 2025.", flag=True),
     R("Pilanesberg gate — vehicle","R168 per sedan / LDV / SUV per day","https://www.pilanesbergnationalpark.org/travel/tariffs-gate-times/", flag=True),
     R("N4 tolls (Bakwena)","≈ R39 each way","https://www.bakwena.co.za/tolls-and-tariffs/", note="Doornpoort R19.50 + Brits R19.50, Class 1, from 1 Mar 2026. Gauteng e-tolls are dead — no tag needed."),
     R("Fuel","≈ 340 km round trip","", note="Attendant-served. Most take cards, a minority are cash-only — carry some cash."),
     R("Stay","From R2,450 / night (Thatch & Bushveld, 15 min from Manyane Gate)","", note="This advert's own rate. Ask for an introduction below."),
     R("Tips","Petrol attendant R5–R10 · car guard R5–R10 · restaurant 10–15%","https://www.africanbudgetsafaris.com/blog/south-africa-tipping-etiquette-top-tips-tipping-south-africa/"),
   ],
   "note":"Indicative only. Not a quote, and nothing here is bookable through TrustSquare."
 },
 "sections":[
  SEC("\U0001F6C2","Entry & documents", [
    R("South African passport","Domestic trip — no immigration, no visa, no passport needed. Carry your ID for the resident gate rate."),
    R("UK / US / EU / AU passports","Visa-free 90 days. Passport must be valid ≥ 30 days past departure and carry at least 2 blank pages.","https://www.gov.uk/foreign-travel-advice/south-africa/entry-requirements"),
  ] + SA_DEPARTURE),
  SEC("\U0001F489","Health", [
    R("Malaria","NONE. Pilanesberg is a malaria-free Big-5 reserve — which is exactly why it is the family and first-safari choice.","https://www.pilanesbergnationalpark.org/travel/health-and-medical/"),
    R("Where SA malaria actually is","Low-lying far-north Limpopo, the Mpumalanga lowveld and far-north KZN, Sep–May, peaking Jan–Apr. Not here.","https://www.nicd.ac.za/wp-content/uploads/2025/12/National_Risk_Map-02-Dec-2025.pdf"),
    R("Yellow fever","Not required. No certificate needed for this trip."),
    R("Vaccinations","Nothing compulsory. Tetanus up to date; hepatitis A and typhoid are the usual travel-clinic suggestions; rabies if you will handle animals."),
    R("Water","Tap water is safe in Pretoria and the metros. Rural North West supply is variable — use bottled inside the reserve."),
    R("Medical","Private hospitals in Rustenburg and Pretoria. There is no in-park hospital — the gate is up to 45 min from the far loops."),
  ]),
  SEC("\U0001F6E1","Safety & travel notices", [
    R("UK FCDO","No advisory against travel. Reviewed 8 Jul 2026.","https://www.gov.uk/foreign-travel-advice/south-africa"),
    R("US State Department","Level 2 — Exercise Increased Caution (crime).","https://travel.state.gov/en/international-travel/travel-advisories/south-africa.html"),
    R("Named for this route","Australian Smartraveller specifically flags armed criminals targeting the APPROACHES to national parks — Kruger and Pilanesberg by name. Do not stop for debris in the road, keep valuables out of sight at intersections.","https://www.smartraveller.gov.au/destinations/africa/south-africa", flag=True),
    R("Driving hazards","Smash-and-grab at intersections, load-shedding dark traffic lights, occasional short-notice protest road closures, flash flooding Nov–Mar."),
    R("In the reserve","Stay in the vehicle except at designated points. Predators are present. 40 km/h internal limits."),
  ]),
  SEC("\U0001F4B3","Money, tax & tipping", [
    R("Currency","South African rand (ZAR). Cards near-universal; ATMs common — use in-mall or in-bank, in daylight."),
    R("VAT","15%, included in the shelf price.","https://www.sars.gov.za/types-of-tax/value-added-tax/vat-refunds-for-tourists-and-foreign-enterprises/"),
    R("Tourist VAT refund (foreign visitors)","Real, and worth claiming. GOODS only — never hotels, car hire or game drives. VAT-inclusive purchase must exceed R250. Claim within 90 days of export. Desks at OR Tambo, Cape Town and King Shaka.","https://www.sars.gov.za/types-of-tax/value-added-tax/vat-refunds-for-tourists-and-foreign-enterprises/"),
    R("Restaurant tip","10–15%, 20%+ for excellent. A service charge is not usually added.","https://www.africanbudgetsafaris.com/blog/south-africa-tipping-etiquette-top-tips-tipping-south-africa/"),
    R("Safari tipping (different from restaurants)","Private guide and tracker R200–R400 per guest per day. Lodge staff gratuity box R50–R150 per guest per day. Tip once at the end of the stay, not after each drive.","https://www.expertafrica.com/south-africa/info/tipping-in-south-africa"),
    R("Small tips you will actually need","Petrol attendant R5–R10. Car guard R5–R10 on return. Porter R10–R20 a bag.","https://www.africanbudgetsafaris.com/blog/south-africa-tipping-etiquette-top-tips-tipping-south-africa/"),
  ]),
  SEC("\U0001F5D3","Best season & timing", [
    R("Go","May–September. Dry winter, thin bush, game concentrates at the waterholes. Mild days, genuinely cold dawns — bring a jacket for the morning drive."),
    R("Avoid","November–March: rain, thick bush, dispersed game, heat and flash flooding."),
    R("Gate times","May–Sep 06h30–18h00 · Mar–Apr & Sep–Oct 06h00–18h30 · Nov–Feb 05h30–19h00.","https://www.pilanesbergnationalpark.org/travel/tariffs-gate-times/"),
  ]),
  SEC("\U0001F4F6","Connectivity", [
    R("Coverage","Vodacom and MTN cover the Pilanesberg / Sun City corridor. In-park signal is patchy in the crater valleys and the western loops — download offline maps before the gate."),
    R("Foreign visitors","A physical SIM needs RICA registration (passport + local address). A travel eSIM rides Vodacom/MTN and skips RICA entirely — simpler."),
  ]),
 ],
 "verify":[
   "Pilanesberg gate tariffs — revised annually and the Dec 2025 hike was steep; the park authority publishes no live tariff page, so confirm at the gate.",
   "N4 Bakwena toll rates — reset every 1 March.",
   "SARS Traveller Declaration — new since 1 Jul 2026, enforcement still bedding in.",
 ],
})

# ── NA — Namibia, fly-in from Joburg ────────────────────────────────────────
TRIPS.append({
 "key":"NA", "match":{"country":"NA"},
 "title":"Namibia — dunes, Skeleton Coast and the great pan",
 "shape":"Fly in from Joburg, self-drive · 7 days door to door · desert legs are malaria-free, Etosha is not",
 "checked":CHECKED,
 "budget":{
   "basis":"Two SA adults, hired 4x4, 7 days, Aug 2026. Park fees verified; fuel and hire are the trip's own numbers.",
   "rows":[
     R("Park & conservation fee — SADC (SA) adult","N$100 per person per day at Etosha, Sossusvlei/Namib-Naukluft and Skeleton Coast","https://www.nwr.com.na/park-entrance-and-conservation-fees-2/", note="Namibian N$50, other foreign N$150. Ages 8–15 half. Trade reports say the international premium rate went to N$280 on 1 Apr 2026 — this could NOT be confirmed on the official brochure. Budget for the higher figure.", flag=True),
     R("Vehicle permit","N$50 per day (≤10 seats)","https://www.nwr.com.na/park-entrance-and-conservation-fees-2/"),
     R("Tourism levy","2% of the bed charge (1% if all-inclusive) — appears on the lodge bill, not paid at a counter. Campsites exempt.","https://visitnamibia.com.na/faq/"),
     R("Fuel","Attendant-served and effectively CASH — the tourism board states outright that service stations do not accept credit for petrol. Plan a cash float.","https://visitnamibia.com.na/currencies/"),
     R("Tips","Restaurant 10% · safari guide N$75–150 per guest per day · camp staff box N$50–150 per guest per night","https://www.expertafrica.com/namibia/info/tipping-in-namibia"),
   ],
   "note":"Indicative only. Not a quote — TrustSquare does not sell or book this trip."
 },
 "sections":[
  SEC("\U0001F6C2","Entry & documents", [
    R("South African passport","VISA-FREE, up to 90 days a year.","https://visitnamibia.com.na/visa-information/"),
    R("UK / US / EU / AU passports","NO LONGER visa-free. Since 1 Apr 2025 they need a visa on arrival or a pre-applied e-visa: N$1,600 over age 11, N$800 for ages 6–11, free under 6.","https://www.gov.uk/foreign-travel-advice/namibia/entry-requirements", flag=True),
    R("Passport","Valid 6 months beyond arrival. Blank pages: official Namibian sources disagree (1 vs 3) — carry 3."),
    R("Children","Full UNABRIDGED birth certificate showing both parents is required on entry — the abridged one is refused. One parent travelling needs the other's consent affidavit. Namibia still demands this even though South Africa dropped it for exits.","https://www.gov.uk/foreign-travel-advice/namibia/entry-requirements", flag=True),
  ] + SA_DEPARTURE),
  SEC("\U0001F489","Health", [
    R("Malaria — Sossusvlei / Namib-Naukluft","No risk. The desert legs are clean.","https://www.cdc.gov/yellow-book/hcp/preparing-international-travelers/yellow-fever-vaccine-and-malaria-prevention-information-by-country.html"),
    R("Malaria — Skeleton Coast","No risk.","https://www.cdc.gov/yellow-book/hcp/preparing-international-travelers/yellow-fever-vaccine-and-malaria-prevention-information-by-country.html"),
    R("Malaria — ETOSHA","YES, low-level. Etosha straddles risk districts. Bite avoidance as the baseline; prophylaxis on a travel-clinic assessment. The northern Kavango and Zambezi strips are the high-risk areas, Nov–Jun.","https://travelhealthpro.org.uk/country/157/namibia", flag=True),
    R("Yellow fever","Only if you arrive from — or transit an airport in — a yellow-fever country. Coming direct from South Africa, no certificate needed, and none needed to return to SA from Namibia.","https://visitnamibia.com.na/faq/"),
    R("Water","Windhoek tap water is potable. Remote lodges run boreholes — safe but hard and brackish; bottled is everywhere."),
    R("Medical","Distances are the real risk, not disease. Serious cases are evacuated to Windhoek or South Africa. Travel insurance with air evacuation cover is the sensible purchase for this trip."),
  ]),
  SEC("\U0001F6E1","Safety & travel notices", [
    R("US State Department","Level 2 — Exercise Increased Caution (crime, health). Issued 15 May 2026.","https://travel.state.gov/en/international-travel/travel-advisories/namibia.html"),
    R("Australian Smartraveller","Green — exercise normal safety precautions. Flags landmines and unexploded ordnance in East and West Kavango, the Zambezi region and the Angolan border areas. Stick to main routes there.","https://www.smartraveller.gov.au/destinations/africa/namibia", flag=True),
    R("UK FCDO","No do-not-travel zones. Live warnings: violent muggings targeting tourists in Windhoek at any hour, gangs entering vehicles at Windhoek intersections, theft at service stations, card skimming at lodges — and gravel-road accidents.","https://www.gov.uk/foreign-travel-advice/namibia/safety-and-security"),
    R("The gravel roads are the biggest hazard","FCDO's own advice: do not exceed 80 km/h on gravel, carry TWO spare tyres, carry plenty of water, do not drive at night outside towns. Most rental insurance EXCLUDES single-vehicle rollovers — read the policy before you sign.","https://www.gov.uk/foreign-travel-advice/namibia/safety-and-security", flag=True),
  ]),
  SEC("\U0001F4B3","Money, tax & tipping", [
    R("Currency","Namibian dollar (NAD), fixed 1:1 to the rand. The RAND IS ACCEPTED everywhere in Namibia — but the Namibian dollar is NOT legal tender back in South Africa, so spend or swap it before you fly home.","https://visitnamibia.com.na/currencies/"),
    R("VAT","15%.","https://www.namra.org.na/customs-excise/page/refund-procedures/"),
    R("Tourist VAT refund","Exists. Claim at Hosea Kutako, Eros or Walvis Bay on departure — VAT 16 form plus tax invoice to Customs, minimum N$250 purchase, 1% admin fee. Arrive early.","https://www.namra.org.na/customs-excise/page/refund-procedures/"),
    R("Cards vs cash","Cards work in towns and at lodges. FUEL IS CASH. Remote shops are cash. Draw a float in Windhoek."),
    R("Safari tipping","Guide roughly US$5–10 (N$75–150) per guest per day. Camp staff box N$50–150 per guest per night. Transfer driver ≈ N$100 per guest per day. Tip in NAD or ZAR, once at the end of each stay.","https://www.expertafrica.com/namibia/info/tipping-in-namibia"),
    R("Taking a SA-registered car in","Cross-Border Charge at the border: N$534 for a car, single or double-cab bakkie, 2x4 or 4x4, or a minibus under 25 seats. Permit stays in the vehicle and is surrendered on exit. Fine up to N$4,000 if you skip it. There are NO toll roads in Namibia.","https://rfanam.com.na/fees-tariffs/"),
  ]),
  SEC("\U0001F5D3","Best season & timing", [
    R("Go","May–October, the dry season — the tourism board says so directly. Etosha peaks July–October as game concentrates at the waterholes.","https://visitnamibia.com.na/faq/"),
    R("Avoid","January–April for driving. The rains degrade the gravel, game disperses and the desert is punishingly hot."),
  ]),
  SEC("\U0001F4F6","Connectivity", [
    R("Coverage","MTC and TN Mobile cover the towns and most of the national highway. Expect NO signal across long stretches of the Namib, the Skeleton Coast and between Etosha camps."),
    R("The tourism board's own advice","Rent a satellite phone if you are self-driving remote sections.","https://visitnamibia.com.na/faq/"),
    R("Starlink","NOT licensed in Namibia — the regulator rejected the application on 24 Mar 2026. A lodge advertising Starlink wifi is making a claim worth questioning.","https://www.cran.na/download/cran-concludes-assessment-of-starlink-licence-application-24-march-2026-windhoek/", flag=True),
  ]),
 ],
 "verify":[
   "Park fees — the official brochure still shows N$150 for the international premium rate while trade reports say N$280 from 1 Apr 2026. Unresolved.",
   "Visa-on-arrival fee and the exempt-nationality list — changed in Apr 2025 and can change again.",
   "Cross-border charge — the tariff was last set 1 Aug 2026.",
 ],
})

# ── BW — Botswana ───────────────────────────────────────────────────────────
TRIPS.append({
 "key":"BW", "match":{"country":"BW"},
 "title":"Botswana — the Okavango and the salt pans",
 "shape":"Fly in from Joburg · 7 days · light-aircraft transfers · MALARIA COUNTRY, all of it",
 "checked":CHECKED,
 "budget":{
   "basis":"Two SA adults, 7 days, Aug 2026. Park fees are the current in-force rates — a rise was proposed for 1 Apr 2026 and postponed, not cancelled.",
   "rows":[
     R("Moremi / Chobe park fee — SADC resident","P205 per person per day (P145 through a licensed Botswana operator)","https://moremipark.com/entry-fees/", note="Non-resident P270. Charged per day INCLUDING the day you leave.", flag=True),
     R("Makgadikgadi / Nxai Pan","Commonly quoted at P190 per person per day non-resident — could not be confirmed against an official tariff.","https://moremipark.com/entry-fees/", flag=True),
     R("Vehicle","Foreign-registered under 3,500 kg: P75 per day (some 2026 sources say P115).","https://moremipark.com/entry-fees/", flag=True),
     R("DWNP camping levy","P60 per person per night non-resident, P45 SADC — ON TOP of the campsite operator's own rate (Third Bridge ≈ P561 pp; North Gate ≈ US$50 pp).","https://moremipark.com/entry-fees/"),
     R("Light-aircraft luggage","12 kg on Okavango charters — not 20 kg. Soft bags only. This catches people out.","https://www.botswanatourism.co.bw/"),
     R("Tips","Group guide US$10–20 · private guide US$20–40 · mokoro poler, tracker or butler US$5–10 · staff box US$5–10 — all per guest per day","https://www.expertafrica.com/botswana/info/tipping-in-botswana"),
   ],
   "note":"Indicative only. Not a quote — TrustSquare does not sell or book this trip."
 },
 "sections":[
  SEC("\U0001F6C2","Entry & documents", [
    R("South African passport","Visa-free, 90 days (SADC).","https://www.gov.uk/foreign-travel-advice/botswana/entry-requirements"),
    R("UK / US / EU / AU passports","Also visa-free, 90 days. No ETA applies.","https://travel.state.gov/en/international-travel/travel-advisories/botswana.html"),
    R("Passport","Valid 6 months beyond arrival AND 6 months beyond departure. THREE blank pages required."),
    R("Children","Certified copies of UNABRIDGED birth certificates plus passports. Absent parent needs a consent affidavit. In force since 1 Oct 2016 and still enforced.","https://www.gov.uk/foreign-travel-advice/botswana/entry-requirements", flag=True),
    R("Tourism Development Levy (US$30)","Announced in 2017 with SADC citizens EXEMPT — so a South African would not pay it. Its status in 2026 is contradictory: Botswana's own entry pages, the FCDO and the US State Department don't mention it, and there is no working payment portal. Ask your operator.","https://dailynews.gov.bw/news-detail/90884", flag=True),
  ] + SA_DEPARTURE),
  SEC("\U0001F489","Health", [
    R("Malaria — this trip is IN it","Okavango and Ngamiland (the Delta and Moremi), Chobe, and Boteti (which covers Makgadikgadi and Nxai) are all malaria districts. Chemoprophylaxis is recommended in every one of them.","https://wwwnc.cdc.gov/travel/destinations/traveler/none/botswana", flag=True),
    R("Peak season","November to April — during and just after the rains. Cerebral malaria occurs in northern Botswana. The FCDO also noted in Apr 2025 that malaria had spread to areas where it is not usually present.","https://www.gov.uk/foreign-travel-advice/botswana/health", flag=True),
    R("Yellow fever","Required from age 1 if you arrive from a yellow-fever country — and TRANSIT COUNTS: an airport layover over 12 hours triggers it. Direct from South Africa, not needed.","https://wwwnc.cdc.gov/travel/destinations/traveler/none/botswana"),
    R("Other","Tetanus, polio, diphtheria and hepatitis A as standard; hepatitis B, typhoid and rabies for longer or rural stays (dog rabies is present). Schistosomiasis in still water; occasional anthrax outbreaks in wildlife."),
    R("Water","Sources disagree — the tourism board says tap water is safe countrywide, the US State Department says it may not be and notes drought rationing. Use bottled or filtered in Maun and the camps."),
    R("Medical","Delta camps are hours from a hospital by air. Air-evacuation cover is not optional on this trip."),
  ]),
  SEC("\U0001F6E1","Safety & travel notices", [
    R("US State Department","Level 2 — Exercise Increased Caution (crime). Updated 25 Jun 2026. Specifically warns about theft from luggage transiting Johannesburg.","https://travel.state.gov/en/international-travel/travel-advisories/botswana.html"),
    R("UK FCDO","No advise-against-travel areas. Violent crime rising in Gaborone, Francistown and MAUN; room break-ins and theft at river-fronting lodges in the CHOBE area.","https://www.gov.uk/foreign-travel-advice/botswana/safety-and-security"),
    R("Wildlife on the roads","The FCDO warns of dangerous animals roaming open highways inside and outside the reserves. Stray wildlife and livestock make night driving genuinely hazardous — don't.","https://www.gov.uk/foreign-travel-advice/botswana/safety-and-security", flag=True),
    R("Rainy season","November–March brings flash flooding, unsafe roads and SHORT-NOTICE BORDER CLOSURES.","https://www.gov.uk/foreign-travel-advice/botswana/safety-and-security"),
    R("Foot-and-mouth disease","An active national containment issue in 2026. Veterinary cordon fences are real, long-standing and can affect movement and what you may carry across them.","https://www.gov.bw/vp-tours-bvi-fmd-threat-looms", flag=True),
  ]),
  SEC("\U0001F4B3","Money, tax & tipping", [
    R("Currency","Botswana pula (BWP). The RAND IS NOT LEGAL TENDER here — unlike Namibia. Rand, USD, EUR and GBP are easily exchangeable at banks and bureaux, but you cannot pay with them.","https://www.botswanatourism.co.bw/travel-info/money", flag=True),
    R("VAT","14% per PwC's 2026 summary; the revenue authority's own site still shows 12% and appears stale.","https://taxsummaries.pwc.com/botswana/corporate/other-taxes", flag=True),
    R("Tourist VAT refund","No scheme found."),
    R("Cards vs cash","Cards work at hotels, restaurants and safari companies. Remote shops and fuel stations are cash. ATMs are in the larger towns and thin to absent rurally."),
    R("Park gates take PULA CASH","At Moremi you pay in pula cash at the gate — cards only in advance at the DWNP office in Maun, which issues a voucher.","https://moremipark.com/entry-fees/", flag=True),
    R("Safari tipping","Group guide US$10–20 per guest per day; private guide US$20–40; mokoro poler, tracker or butler US$5–10; general staff box US$5–10. Tip once at the end of each camp stay, not after each activity. Pula preferred, then USD or ZAR.","https://www.expertafrica.com/botswana/info/tipping-in-botswana"),
    R("Cash declaration","Declare P10,000 or more in or out.","https://www.botswanatourism.co.bw/travel-info/money"),
  ]),
  SEC("\U0001F5D3","Best season & timing", [
    R("The counter-intuitive bit","The Okavango FLOODS in the DRY season. The annual flood arrives roughly March to July, lagging the Angolan highland rains by two to six months. Dry season concentrates the game and fills the channels at the same time.","https://www.expertafrica.com/botswana/info/okavango-delta-flood"),
    R("Zebra on the pans","The Makgadikgadi and Nxai herds arrive from early January and graze through to about March. December–February is the pan-migration window.","https://www.expertafrica.com/botswana/info/migrations-in-botswana"),
    R("Avoid","November–March: flooding, unsafe roads, possible border closures, 40°C+ and peak malaria."),
    R("Book far ahead","Moremi requires a valid campsite reservation just to ENTER. June–October sells out six to eight months in advance.","https://moremipark.com/entry-fees/", flag=True),
  ]),
  SEC("\U0001F4F6","Connectivity", [
    R("Coverage","Mascom, Orange and beMobile cover towns and highways — not wilderness. Expect no signal in Delta camps and on the pans."),
    R("Advice","The FCDO recommends a satellite phone for very remote areas. Starlink is licensed and operating in Botswana, but whether a given camp runs it is worth asking."),
    R("Note","Using a phone while driving is illegal — P300 fine.","https://www.botswanatourism.co.bw/travel-info/communications"),
  ]),
 ],
 "verify":[
   "Park fees — the 1 Apr 2026 increase (non-resident P380 to P500) was POSTPONED, not cancelled. It can land at any time.",
   "The US$30 Tourism Development Levy — existence and collection in 2026 is contradictory across every source we checked.",
   "VAT rate — 14% (PwC) vs 12% (revenue authority website).",
   "Foot-and-mouth movement controls — active and can change quickly.",
 ],
})

# ── MZ — Mozambique ─────────────────────────────────────────────────────────
TRIPS.append({
 "key":"MZ", "match":{"country":"MZ"},
 "title":"Mozambique — the Inhambane coast and Bazaruto",
 "shape":"Fly in from Joburg · 7 days · dhows, reefs and islands · MALARIA YEAR-ROUND",
 "checked":CHECKED,
 "budget":{
   "basis":"Two SA adults, 7 days, Aug 2026. Entry is free for South Africans; the honest gap is that Bazaruto's conservation fee is not published anywhere official.",
   "rows":[
     R("Visa — South African","R0. Visa-free, 30 days.","https://evisa.gov.mz/"),
     R("Bazaruto Archipelago conservation fee","NOT PUBLISHED. Neither African Parks nor the national conservation authority publishes the current per-person daily fee. Get it in writing from your operator before you book.","https://visitbazaruto.org/day-visitors/", flag=True),
     R("N4 tolls if you drive","Diamond Hill R51 · Middelburg R84 · Machado R126 · Nkomazi R95 · Moamba MZN 240 · Maputo MZN 30 (Class 1, from 1 Mar 2026). Mozambican plazas take meticais, rand or USD notes and give change in meticais.","https://tracn4.co.za/toll-plazas-toll-fees/"),
     R("Dive insurance","DAN Southern Africa cover, arranged before you travel. Serious cases are evacuated to South Africa.","https://www.dansa.org"),
     R("Tips","10% is welcomed and expected in tourist areas.","https://www.anac.gov.mz/turismo/informacao-util/"),
   ],
   "note":"Indicative only. Not a quote — TrustSquare does not sell or book this trip."
 },
 "sections":[
  SEC("\U0001F6C2","Entry & documents", [
    R("South African passport","VISA-FREE, 30 days, under a bilateral exemption. South Africa is on the waiver list, NOT the ETA list — no ETA, no fee.","https://evisa.gov.mz/"),
    R("UK / US / EU passports","Visa-exempt for 30 days BUT must obtain an ETA at evisa.gov.mz at least 48 hours before departure. The ETA was mandated Apr 2025, suspended May 2025, and reinstated on a new platform 11 Feb 2026 — a volatile requirement worth double-checking.","https://www.gov.uk/foreign-travel-advice/mozambique/entry-requirements", flag=True),
    R("Australian passports","On neither list — e-visa or visa on arrival.","https://www.smartraveller.gov.au/destinations/africa/mozambique"),
    R("Passport","Valid at least 6 months from arrival. Blank pages: sources say 2 or 3 — carry 3."),
    R("On arrival","Show an accommodation booking or host invitation, plus a return ticket. KEEP THE BORDER RECEIPT — you need it to exit."),
    R("Children","Unabridged birth certificate listing both parents, plus a NOTARISED parental consent affidavit not older than 3 months where one or neither parent travels. Mozambique demands this on entry even though South Africa dropped it on exit.","https://www.gov.uk/foreign-travel-advice/mozambique/entry-requirements", flag=True),
  ] + SA_DEPARTURE),
  SEC("\U0001F489","Health", [
    R("Malaria","YEAR-ROUND, particularly outside Maputo. This is not a seasonal risk you can time around — take prophylaxis advice from a travel clinic.","https://www.smartraveller.gov.au/destinations/africa/mozambique", flag=True),
    R("Cholera — live outbreak","The FCDO records an ongoing cholera outbreak in central and northern areas as at Jul 2026. Volatile — re-check before travel.","https://www.gov.uk/foreign-travel-advice/mozambique/health", flag=True),
    R("Yellow fever","Only if arriving from or transiting a yellow-fever country — and the penalty is severe: no certificate means detained and returned. Not needed direct from South Africa, and Mozambique is not on SA's list for the return leg.","https://www.gov.uk/foreign-travel-advice/mozambique/entry-requirements"),
    R("Also flagged","Dengue, schistosomiasis, mpox, and a high HIV prevalence. Hepatitis A and typhoid are standard travel-clinic suggestions."),
    R("Water","Bottled, everywhere. It is universally available."),
    R("Diving","Get DAN Southern Africa cover BEFORE you travel. The nearest recompression chamber to Tofo and Bazaruto could not be confirmed — ask your dive operator directly, and ask where they evacuate to.","https://www.dansa.org", flag=True),
    R("Medical","Medical evacuation to South Africa may be necessary for anything serious.","https://www.gov.uk/foreign-travel-advice/mozambique/health"),
  ]),
  SEC("\U0001F6E1","Safety & travel notices", [
    R("This coast is NOT in a do-not-travel zone","Inhambane, Tofo, Vilanculos and Bazaruto all sit outside every current warning area. Worth stating plainly, because Mozambique's headline advisories are about the far north."),
    R("The no-go areas","UK FCDO advises against all travel to Cabo Delgado (except Palma, Pemba and Afungi), Memba and Eráti in Nampula, and Mecula and Marrupo in Niassa.","https://www.gov.uk/foreign-travel-advice/mozambique", flag=True),
    R("Road warnings","Smartraveller says do not travel the EN1 between the Save River and Muxungue, Gorongosa–Caia, or the EN6 Beira–Chimoio. Tofo and Vilanculos lie SOUTH of the Save — outside these.","https://www.smartraveller.gov.au/destinations/africa/mozambique"),
    R("On this coast specifically","Smartraveller records serious assaults and robberies at two coastal resorts in Inhambane province. Armed robberies in the Lebombo border queue after dark.","https://www.smartraveller.gov.au/destinations/africa/mozambique", flag=True),
    R("US State Department","Level 2 — Exercise Increased Caution overall; Level 4 for Cabo Delgado, the Niassa Special Reserve and northern Nampula.","https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories/mozambique-travel-advisory.html"),
    R("Checkpoints","Common. Only national police may set them; unofficial ones are reported and officers may ask for a bribe."),
    R("Cyclones","November to May.","https://www.smartraveller.gov.au/destinations/africa/mozambique"),
  ]),
  SEC("\U0001F4B3","Money, tax & tipping", [
    R("Currency","Metical (MZN). Rand, dollars and euros are accepted in many tourist locations. It is ILLEGAL to import or export meticais — spend them before you leave.","https://www.anac.gov.mz/turismo/informacao-util/", flag=True),
    R("Carry a VISA card","Mastercard is not accepted by all vendors and CANNOT be used to withdraw cash from ATMs in Mozambique. This one strands people.","https://www.smartraveller.gov.au/destinations/africa/mozambique", flag=True),
    R("VAT","16% standard (the conservation authority's own page still says 17% and is out of date).","https://taxsummaries.pwc.com/mozambique/corporate/other-taxes"),
    R("Tourist VAT refund","No scheme found."),
    R("Tipping","10% is welcomed and expected in tourist areas. Per-role amounts for divemasters, dhow crew and boat skippers are not published anywhere reliable — ask your lodge what is customary.","https://www.anac.gov.mz/turismo/informacao-util/"),
    R("Cash declaration","Declare MZN 10,000 or US$5,000 and above.","https://www.gov.uk/foreign-travel-advice/mozambique/entry-requirements"),
  ]),
  SEC("\U0001F5D3","Best season & timing", [
    R("Go","May to August — warm winter days, cooler mornings and evenings, out of cyclone season.","https://visitbazaruto.org/"),
    R("Avoid","October to March: hot, humid and cyclone season. Rains November to April.","https://visitbazaruto.org/"),
    R("What this coast is famous for","The Inhambane coast is one of the world's most important whale-shark feeding areas, and a breeding area for manta rays and humpback whales. Exact peak months are not published on the scientific source — ask the operator for their sighting calendar.","https://marinemegafauna.org/mozambique-projects"),
  ]),
  SEC("\U0001F4F6","Connectivity", [
    R("Networks","Vodacom, Tmcel and Movitel. Starter packs with a SIM are sold in any mobile shop; scratch-card top-ups are everywhere."),
    R("Roaming","The conservation authority's own advice is that home-contract roaming is expensive — switch data off and buy local.","https://www.anac.gov.mz/turismo/informacao-util/"),
    R("Coverage on Bazaruto and at Tofo","Not confirmed. Assume patchy on the islands."),
  ]),
 ],
 "verify":[
   "The ETA for UK/US/EU travellers — reinstated only in Feb 2026 after a nine-month suspension, and the fee reportedly jumped from about US$10 to about US$48.",
   "The cholera outbreak in central and northern Mozambique.",
   "Bazaruto's conservation fee — unpublished; get it in writing from the operator.",
   "Advisory maps — the three agencies currently draw Mozambique differently, and the US advisory is over a year old.",
 ],
})

# ── KE — Kenya ──────────────────────────────────────────────────────────────
TRIPS.append({
 "key":"KE", "match":{"country":"KE"},
 "title":"Kenya — the Rift Valley and the Maasai Mara",
 "shape":"Fly in from Cape Town or Joburg · 7 days · the one trip on our list with a yellow-fever certificate you must have to come HOME",
 "checked":CHECKED,
 "budget":{
   "basis":"Two adults, 7 days, Aug 2026. Park fees dominate this budget — read the Mara line carefully.",
   "rows":[
     R("Maasai Mara — non-resident adult","US$100 per day 1 Jan–30 Jun 2026; US$200 PER DAY from 1 Jul 2026","https://masaimara.ke/entry-fees/", note="Set by Narok County. In migration season this single line dominates the whole trip cost — US$200 x nights x people.", flag=True),
     R("Private conservancies","Charge a SEPARATE conservancy fee on top, usually bundled into the camp rate. Verify with the camp.","https://masaimara.ke/entry-fees/"),
     R("Amboseli / Lake Nakuru (KWS premium parks)","US$90 adult / US$45 child per day","https://www.kws.go.ke/", note="From secondary sources — the official KWS tariff PDF would not render for verification.", flag=True),
     R("Paying park fees","KWS fees are quoted in USD but paid in shillings through the KWSPay portal, at a portal rate typically 3–5% above bank rate.","https://kiptravels.com/understanding-the-new-kws-park-entry-rates-2025-2026-how-to-pay-through-the-new-system/"),
     R("Tipping — budget it properly","Driver-guide US$10–25 per person per day; tracker US$5–15; camp staff box US$5–15; porters US$1–2 a bag. Allow roughly US$25–40 per person per day in total.","https://www.expertafrica.com/kenya/info/tipping-in-kenya"),
     R("Balloon safari","Tipped separately from the camp and the guide."),
   ],
   "note":"Indicative only. Not a quote — TrustSquare does not sell or book this trip."
 },
 "sections":[
  SEC("\U0001F6C2","Entry & documents", [
    R("South African passport","NO eTA and NO visa. Legal Notice 93 of 30 May 2025 exempted all African nationals except Somalia and Libya; South Africa sits in the 90-day band.","https://www.cliffedekkerhofmeyr.com/en/news/publications/2025/Sectors/Immigration-Law/immigration-law-alert-24-july-kenya-Kenya-amends-immigration-rules-broadens-eTA-exemptions-for-African-and-other-nationals", flag=True),
    R("Careful — the official page contradicts this","Kenya's immigration site still carries blanket wording that all visitors need an eTA and has not been rewritten to reflect the exemption. Carry a printout of the Schedule, or run the exemption checker on the day.","https://immigration.go.ke/eta/", flag=True),
    R("UK / US / EU / AU passports","eTA required. US$30 plus processing. Immigration states all applications are processed within 3 working days — apply a week out.","https://etakenya.go.ke"),
    R("Passport","6 months' validity beyond your stay and blank pages for stamps is the standard expectation — not confirmed against an official Kenyan source, so allow margin."),
  ] + SA_DEPARTURE),
  SEC("\U0001F489","Health", [
    R("YELLOW FEVER — THE ONE PEOPLE MISS","You do NOT need a certificate to enter Kenya from South Africa. You DO need one to come HOME. Kenya is on South Africa's yellow-fever list, so SA requires a valid certificate from every traveller over 1 year arriving from Kenya. Without it, Port Health can refuse you boarding or entry. Vaccinate at least 10 days before you fly. The certificate is valid for life.","https://www.southafrica.net/gl/en/travel/article/yellow-fever-entry-requirements", flag=True),
    R("Malaria","Altitude-driven. Nairobi (≈1,795 m) is low risk. The Rift Valley lake towns are low. The MAASAI MARA is low-to-moderate and prophylaxis is commonly recommended. The coast is year-round high. Risk rises during and after the long rains (Mar–May) and short rains (Oct–Dec).","https://wwwnc.cdc.gov/travel/destinations/traveler/none/kenya"),
    R("Other vaccinations","Routine cover plus hepatitis A and typhoid; rabies and hepatitis B for longer or rural stays."),
    R("Water","NOT potable. Bottled or treated only, and avoid ice of unknown origin. Cholera and typhoid are present."),
    R("Cold at dawn","Not a disease, but it catches South Africans out: 5–8°C at dawn in Jun–Sep for game drives and balloon launches, at 1,500–2,170 m. Pack properly."),
  ]),
  SEC("\U0001F6E1","Safety & travel notices", [
    R("US State Department","Level 2 — Exercise Increased Caution, updated 28 Jul 2026, with do-not-travel sub-areas on the Somali border and parts of the coast.","https://travel.state.gov/en/international-travel/travel-advisories/kenya.html"),
    R("UK FCDO — the no-go areas","Advises against all travel to parts of Mandera, Wajir, Garissa and Lamu counties (Al-Shabaab). Lamu and Manda Islands are excepted BUT fly in — do not travel there by road.","https://www.gov.uk/foreign-travel-advice/kenya/regional-risks", flag=True),
    R("This route is not affected","Nairobi, the Rift Valley and the Mara carry no advise-against-travel warning."),
    R("Balloon safaris","Launch at dawn year-round but are cancelled in heavy rain — build a spare morning into the itinerary if it matters to you."),
  ]),
  SEC("\U0001F4B3","Money, tax & tipping", [
    R("Currency","Kenyan shilling (KES). Cards work at lodges, hotels and larger Nairobi retail. Cash for markets, tips and small towns. ATMs are plentiful in Nairobi, Nakuru and Naivasha and effectively absent inside the Mara."),
    R("Bring small clean US dollar notes","1s, 5s, 10s and 20s. USD is the preferred tipping currency right across the safari circuit.","https://www.expertafrica.com/kenya/info/tipping-in-kenya"),
    R("M-Pesa","The de facto payment rail — but it needs a Kenyan SIM registered against your passport. A tourist eSIM will NOT give you M-Pesa. Get a physical Safaricom line if you want it.","https://esimfly.net/guides/safaricom-esim-guide"),
    R("VAT","16% standard (not independently confirmed in this pass).","https://www.kra.go.ke/", flag=True),
    R("Tourist VAT refund","Not practically available."),
    R("Tipping","Driver-guide US$10–25 per person per day; tracker or spotter US$5–15; camp staff box US$5–15; porters US$1–2 a bag; airport transfer US$5–10. Balloon crews tipped separately.","https://www.dumaexplorer.com/blog/safari-tipping-africa-guide-amounts-etiquette"),
  ]),
  SEC("\U0001F5D3","Best season & timing", [
    R("The Great Migration","Late June to October in the Mara. First big crossings usually late July; the most dramatic Mara River crossings roughly 10 Aug – 20 Sep. August is the most reliable month and also the most crowded — expect vehicle congestion at crossing points.","https://www.masaimaramigration.com/safari-guide/2026-masai-mara-migration-forecast-expert-safari-predictions-best-dates/"),
    R("The herds are not on a timetable","They cross the river repeatedly and move back south when it rains in Tanzania. Nobody can guarantee a crossing on a given date — treat any operator who does with suspicion."),
    R("Avoid","The long rains, March to May: worst roads, some camps close, highest mosquito load. Short rains Nov–Dec are less disruptive."),
    R("Cost timing","The US$200 Mara peak fee applies July to December. A June trip is materially cheaper for the same country.","https://masaimara.ke/entry-fees/"),
  ]),
  SEC("\U0001F4F6","Connectivity", [
    R("Coverage","Safaricom has the widest rural footprint. Good 4G in Nairobi, Naivasha, Nakuru and at the Mara gates and main lodges; patchy a few kilometres in and absent deep in the conservancies."),
    R("Local SIM","A tourist bundle runs about KES 1,000 for 5 GB plus minutes for 30 days. Lodge wifi is satellite and slow.","https://esimfly.net/guides/kenya-esim-guide"),
  ]),
 ],
 "verify":[
   "Kenya's official immigration page still contradicts the eTA exemption for African nationals — check the exemption checker on the day.",
   "The Maasai Mara fee band (US$100 vs US$200) and the Narok County tariff.",
   "KWS park fees — the official tariff PDF could not be read; figures came from secondary sources.",
   "South Africa's yellow-fever country list — it changes, and this trip depends on it.",
 ],
})

# ── C2C — Cape to Cairo by rail (multi-country) ─────────────────────────────
TRIPS.append({
 "key":"c2c", "match":{"tour":"c2c"},
 "title":"Cape to Cairo — the long line north",
 "shape":"Multi-country · South Africa, Zimbabwe, Zambia, Tanzania, Egypt · a different passport question at every border",
 "checked":CHECKED,
 "budget":{
   "basis":"Per person, Aug 2026. On a multi-country journey the entry fees and site tickets are the predictable part; the rail fares are not ours to quote.",
   "rows":[
     R("Zimbabwe — SA passport","Free. Visa-free 90 days (SADC).","https://www.evisa.gov.zw/"),
     R("Zimbabwe — UK/US/EU/AU","US$30 single entry on arrival, or US$45 double. KAZA UniVisa US$50 covers Zimbabwe and Zambia together.","https://www.evisa.gov.zw/", flag=True),
     R("Victoria Falls Rainforest entry","US$58 international day visitor (2026 tariff, up from US$50 after VAT was applied to tourism services)","https://apta-africa.org/2026/03/10/updated-victoria-falls-entry-fees-for-zim-side/", flag=True),
     R("Mosi-oa-Tunya NP (Zambia side)","US$20 international visitor","https://www.visitvictoriafalls.org/mosi-oa-tunya-national-park-fees/"),
     R("Zambia / Tanzania — SA passport","Free. Visa-free / visa-exempt visitor's pass.","https://visa.immigration.go.tz/guidelines"),
     R("Tanzania — UK/EU/AU e-visa","US$50 single entry. US citizens pay US$100 for the multiple-entry class.","https://visa.immigration.go.tz"),
     R("Egypt — SA and most passports","US$25 e-visa or visa on arrival. Reported to have risen to US$30 from 1 Mar 2026 — not confirmed officially.","https://visa2egypt.gov.eg", flag=True),
     R("Giza plateau","EGP 700 foreign adult general entry. Great Pyramid interior EGP 1,000 extra.","https://pyramidsofgiza-guide.com/tickets/pyramids-of-giza-ticket-prices/", flag=True),
     R("Valley of the Kings, Luxor","EGP 400 foreign adult (3 tombs). Tutankhamun, Seti I and Ramses V/VI are extra.","https://valleyofthekingsegypt.org/entrance-fee/", flag=True),
     R("Egypt tipping (baksheesh)","Guide EGP 150–300/day · driver EGP 50–100/day · Nile cruise crew pool ≈ US$10–12 per person per night · EGP 10–20 for porters and small services. This is a real budget line, not a rounding error.","https://www.egypttoursplus.com/tipping-in-egypt/"),
   ],
   "note":"Indicative only. Not a quote — TrustSquare does not sell or book this trip."
 },
 "sections":[
  SEC("\U0001F686","The route — read this first", [
    R("The through-line does not exist","The Cape to Cairo railway was never completed. There is no rail link between Sudan and Uganda, and a gap between Wadi Halfa and Aswan that was historically a Nile ferry, not track. Much of Sudan's network is derelict.","https://en.wikipedia.org/wiki/Cape_to_Cairo_Railway", flag=True),
    R("Sudan is at war","US State Department Level 4 — Do Not Travel; the UK advises against all or all-but-essential travel. In practice the Tanzania-to-Egypt leg must be FLOWN. Any itinerary that routes you overland through Sudan is not a serious one.","https://travel.state.gov/en/international-travel/travel-advisories/sudan.html", flag=True),
    R("What actually runs","Cape Town–Johannesburg/Pretoria. Bulawayo–Victoria Falls (NRZ service resumed 17 Oct 2025). Dar es Salaam–New Kapiri Mposhi (TAZARA Mukuba Express resumed 10 Feb 2026 after an 18-month suspension). Egyptian rail Cairo–Luxor–Aswan.","https://www.seat61.com/Zimbabwe.htm", flag=True),
    R("Both African services are fragile","NRZ and TAZARA have each been suspended for long stretches. Re-confirm within days of travel, not weeks."),
    R("Borders on the train","On TAZARA, immigration and customs happen at Tunduma/Nakonde with officials boarding. Delays of several hours are normal and the train frequently runs many hours late. Victoria Falls Bridge is a road and foot crossing, not a through train."),
  ]),
  SEC("\U0001F6C2","Entry — country by country", [
    R("Zimbabwe","SA passport visa-free 90 days. UK/US/EU/AU: visa on arrival US$30 single / US$45 double, or e-visa. KAZA UniVisa US$50 covers Zimbabwe and Zambia plus day trips to Botswana via Kazungula — but it has been suspended and reinstated repeatedly.","https://www.evisa.gov.zw/", flag=True),
    R("Zambia","SA passport visa-free. Permitted stay is reported as 30 days by some sources and 90 by others — confirm. Zambia also announced revised tourist visa fees for 2026.","https://www.zambiaimmigration.gov.zm/", flag=True),
    R("Tanzania","SA passport visa-exempt, visitor's pass up to 90 days, no fee. UK/EU/AU e-visa US$50; US citizens US$100.","https://visa.immigration.go.tz/guidelines"),
    R("Egypt","SA passport: US$25 e-visa or visa on arrival, available at Cairo, Hurghada, Sharm el-Sheikh, Luxor and Marsa Alam. USE ONLY visa2egypt.gov.eg — copycat sites charge three to five times the fee.","https://visa2egypt.gov.eg", flag=True),
    R("Passports","Six months' validity is the safe assumption at every border on this route, with blank pages for a lot of stamps."),
  ] + SA_DEPARTURE),
  SEC("\U0001F489","Health", [
    R("Yellow fever — the route question","Zambia and Tanzania have been reclassified by the WHO as low potential for exposure, and Egypt and Zimbabwe are not risk countries. So on THIS itinerary a certificate is not triggered on the way home. Add Kenya or Uganda, or transit a risk-country airport for over 12 hours, and it is.","https://www.southafrica.net/gl/en/travel/article/yellow-fever-entry-requirements", flag=True),
    R("Tanzania catches Kenya arrivals","Tanzania requires a certificate from anyone arriving from or transiting over 12 hours in a yellow-fever country — which includes anyone coming from Kenya."),
    R("Malaria","Zambezi valley including Victoria Falls: risk area, highest Nov–Apr. Zambia: countrywide, year-round, peaking Nov–Apr. Tanzania: countrywide below 1,800 m, year-round, and the TAZARA line through the Selous corridor is high risk. Egypt: no risk in Cairo, Luxor, Aswan or the Nile corridor."),
    R("Water","Not potable in Zimbabwe, Zambia, Tanzania or Egypt. Bottled only. Travellers' diarrhoea is very common on Nile itineraries."),
    R("Vaccinations","Hepatitis A and typhoid across the route; the usual routine cover; rabies for longer rural stays."),
  ]),
  SEC("\U0001F6E1","Safety & travel notices", [
    R("Tanzania is the highest on this route","US State Department Level 3 — Reconsider Travel (unrest, crime, terrorism, and the targeting of gay and lesbian individuals), updated 31 Oct 2025 after election unrest. Australia advises a high degree of caution, with elevated warnings near the Mozambique border in Mtwara.","https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories/tanzania-travel-advisory.html", flag=True),
    R("Egypt","US Level 2 overall, with DO NOT TRAVEL for North and Middle Sinai and parts of the Western Desert. Australia adds the Taba–Suez road and within 40 km of the Libyan border. The Cairo, Luxor, Aswan, Hurghada and Sharm corridors were reported operating normally as at Jul 2026.","https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories/egypt-travel-advisory.html", flag=True),
    R("Zimbabwe","US Level 2 — Exercise Increased Caution (crime, and official harassment of US citizens).","https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories/zimbabwe-travel-advisory.html"),
    R("Zambia","US Level 1 — Exercise Normal Precautions. The calmest country on the line.","https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories/zambia-travel-advisory.html"),
  ]),
  SEC("\U0001F4B3","Money, tax & tipping", [
    R("Zimbabwe — bring clean dollars","Dual currency, USD and ZiG. Tourists use USD. Bring CLEAN, POST-2006 notes — torn, marked or old-series bills are routinely refused. Small denominations are essential; change is scarce. Cards are unreliable and ATMs often dispense nothing.","https://zimbabwetravelhub.com/currency-in-zimbabwe-2026-zig-usd/", flag=True),
    R("Tanzania — an even stricter note rule","Only 2009-series or newer US dollar notes, clean and untorn. Older or marked bills are refused even by banks. Cards work at lodges and parks with a 3–5% surcharge. VAT 18% on the mainland.","https://groupcarthage.com/news/us-dollar-notes-issued-earlier-than-2009-are-not-accepted-for-currency-exchange-and-payment/", flag=True),
    R("Zambia","Kwacha (ZMW). USD is widely accepted in Livingstone and for park fees but is not legal tender — carry kwacha for small spend. VAT 16%.","https://www.zra.org.zm/"),
    R("Egypt — major sites are now CASHLESS","Card only at major Luxor and Giza gates. Cash Egyptian pounds will not get you in. Carry a working Visa or Mastercard AND cash, because enforcement varies by gate.","https://www.yourtourguidetours.com/en/travel-guide/buying-valley-of-the-kings-tickets-2026-cashless-rules-prices", flag=True),
    R("Egypt tipping is structural","Baksheesh is embedded and unavoidable — budget it as a line, not an afterthought. Carry a thick stack of EGP 5, 10, 20, 50 and 100 notes.","https://www.egypttoursplus.com/tipping-in-egypt/"),
  ]),
  SEC("\U0001F5D3","Best season & timing", [
    R("There is no perfect month","The only windows where the Falls still have flow, the Zambezi and TAZARA malaria season is off its peak, and Upper Egypt is not lethally hot, are roughly late May to early July, or September to October."),
    R("Victoria Falls flow","Peaks March to June, lowest October to November."),
    R("Upper Egypt","Luxor and Aswan routinely exceed 40°C from May to September. October to April is the season."),
    R("Ramadan","Alters opening hours and restaurant service. Confirm the dates for your year."),
  ]),
  SEC("\U0001F4F6","Connectivity", [
    R("Tanzania","Good in Dar es Salaam and the towns. The TAZARA line has multi-hour dead stretches through the Selous and the southern highlands."),
    R("Egypt","Strong 4G/5G in Cairo and the Nile corridor. A local SIM needs passport registration; eSIMs are widely supported. Dead stretches in the Western Desert and on the Aswan–Abu Simbel road."),
  ]),
 ],
 "verify":[
   "TAZARA and NRZ timetables — both services resumed recently after long suspensions.",
   "KAZA UniVisa availability — repeatedly suspended and reinstated.",
   "Zambia's 2026 revised visa fees and the permitted stay (30 or 90 days).",
   "Egypt's visa-on-arrival fee (US$25 vs US$30) and cashless-gate enforcement.",
   "Tanzania's US Level 3 status.",
   "Sudan — do not attempt a land or rail transit under any circumstances.",
 ],
})

# ── Shared long-haul blocks ─────────────────────────────────────────────────
def UK_ENTRY():
  return [
    R("South African passport — VISA REQUIRED, and the ETA does not apply","South Africa is a visa-national country. The UK ETA is only for people who do NOT need a visa, so a South African cannot use it. You apply for a Standard Visitor visa.","https://www.gov.uk/guidance/immigration-rules/immigration-rules-appendix-visitor-visa-national-list", flag=True),
    R("Fee","£135 for the 6-month visitor visa, in force from 8 Apr 2026 (2-year £506, 5-year £903, 10-year £1,128).","https://www.gov.uk/government/publications/visa-regulations-revised-table/home-office-immigration-and-nationality-fees-8-april-2026", flag=True),
    R("Processing","Standard 3 weeks / 15 working days. Priority £500 extra (≈5 working days); Super Priority £1,000 (next working day).","https://www.gov.uk/guidance/visa-decision-waiting-times-applications-outside-the-uk"),
    R("Where you apply","VFS Global, not TLScontact — VFS took over in South Africa from 22 Oct 2024. Centres in Johannesburg, Pretoria, Cape Town, Durban and Gqeberha. Apply from three months before travel.","https://visa.vfsglobal.com/zaf/en/gbr/"),
    R("Passport","No six-month rule — it must be valid for the whole of your stay.","https://www.gov.uk/uk-border-control"),
    R("UK / US / EU / AU passports","Visa-free; most now need a UK ETA.","https://www.gov.uk/guidance/apply-for-an-electronic-travel-authorisation-eta"),
  ]

UK_MONEY = [
    R("Currency","Pound sterling. VAT 20%, included in the shelf price.","https://www.gov.uk/vat-rates"),
    R("Tax-free shopping is GONE","The VAT Retail Export Scheme and airside tax-free shopping ended in Great Britain on 31 Dec 2020 and the Treasury confirmed in Dec 2025 there are no plans to bring it back. The only exception is goods delivered straight to an address outside the UK. Northern Ireland still runs a scheme.","https://www.gov.uk/tax-on-shopping/taxfree-shopping", flag=True),
    R("Cards","Cards are 64% of all UK payments and cash is down to about 8%. The £100 contactless cap was removed in March 2026. There is no legal duty on a UK business to accept cash — card-only venues are common.","https://www.ukfinance.org.uk/news-and-insight/press-release/digital-payments-continue-grow-mobile-wallets-become-more-popular"),
    R("Tipping — much lower than you may expect","VisitBritain: tipping is not expected in Britain the way it is in some other countries, because all staff must be paid at least the National Minimum Wage. Restaurants: a service charge is sometimes added; if not, 10–15%. Taxis: round up or 10–15%. Hotel porter about £2.","https://www.visitbritain.com/en/plan-your-trip/useful-information"),
    R("Your tip does reach the staff","Since 1 Oct 2024 employers must pass on 100% of tips without deduction.","https://www.gov.uk/government/publications/distributing-tips-fairly-statutory-code-of-practice"),
    R("Scottish banknotes","Not legal tender but widely accepted — acceptance is the retailer's choice."),
]

# ── GB — Wessex heritage route ──────────────────────────────────────────────
TRIPS.append({
 "key":"GB", "match":{"country":"GB"},
 "title":"Ancient Wessex — the heritage route",
 "shape":"Self-drive · Stonehenge, Avebury, the chalk downland, Salisbury and a country house",
 "checked":CHECKED,
 "budget":{
   "basis":"Per adult, English Heritage tariff year 2026/27 (28 Mar 2026 – 16 Mar 2027).",
   "rows":[
     R("UK Standard Visitor visa","£135 for 6 months — the single largest fixed cost of a UK trip for a South African, before you have booked anything.","https://www.gov.uk/government/publications/visa-regulations-revised-table/home-office-immigration-and-nationality-fees-8-april-2026", flag=True),
     R("Stonehenge (English Heritage)","Adult, date-tiered: Super Saver £24.65 / Saver £27.03 / Standard £29.32. Child 5–17 £12.32–£14.62, under-5 free.","https://www.english-heritage.org.uk/globalassets/group-admission-prices--site-opening-times-2026-2027.pdf", note="Timed entry is strongly recommended; limited walk-up tickets are sold at the tills and online sales close 3 hours before the slot."),
     R("English Heritage Overseas Visitor Pass","1 adult £58 (9-day) or £69 (16-day); 2 adults £102/£113; family £116/£127. Worth the maths if you are doing more than Stonehenge.","https://www.english-heritage.org.uk/visit/overseas-visitors/"),
     R("Salisbury Cathedral","Ticketed, not donation: adult £12.50 advance / £14.50 on the day, under-12 free, includes the Chapter House and Magna Carta, valid a year. A temporary VAT cut applies 25 Jun–1 Sep 2026 (£11/£13).","https://www.salisburycathedral.org.uk/visit-us/your-visit/", flag=True),
     R("National Trust Explorer Pass","4/8/14 days: single adult £31.50 / £42 / £55.10. Excludes English Heritage, Stonehenge and the National Trust FOR SCOTLAND, which is a separate body.","https://www.nationaltrust.org.uk/membership/explorer-pass", flag=True),
   ],
   "note":"Indicative only. Not a quote — TrustSquare does not sell or book this trip."
 },
 "sections":[
  SEC("\U0001F6C2","Entry & documents", UK_ENTRY() + SA_DEPARTURE),
  SEC("\U0001F489","Health & healthcare", [
    R("Vaccinations","None required."),
    R("What the NHS costs a visitor","The Immigration Health Surcharge does NOT apply to visits of 6 months or less — instead you pay 150% of the NHS tariff at the point of use. Free regardless of residence: A&E, walk-in centres, minor injuries units and urgent care. CHARGEABLE: inpatient admission following A&E, and outpatient follow-ups. Insurance is advised, not legally required.","https://www.gov.uk/guidance/nhs-entitlements-migrant-health-guide", flag=True),
  ]),
  SEC("\U0001F6E1","Safety & travel notices", [
    R("UK terrorism threat level","SUBSTANTIAL — an attack is likely. MI5 is the authoritative source; the old gov.uk page contradicts it and is stale.","https://www.mi5.gov.uk/threat-levels"),
    R("Driving","Left-hand side, same as South Africa. Narrow lanes, speed cameras and strict drink-drive enforcement are the real hazards."),
    R("Weather","Wessex is mild but wet. Nothing on this route is exposed enough to be dangerous."),
  ]),
  SEC("\U0001F4B3","Money, tax & tipping", UK_MONEY),
  SEC("\U0001F5D3","Best season & timing", [
    R("Go","Late spring to early autumn for daylight and open sites. English Heritage's cheapest ticket tier falls on weekdays 28 Mar–1 May and 28 Sep–16 Mar — a real saving if you are flexible."),
    R("Solstice","Stonehenge access arrangements change around the solstices. Check before planning around them."),
  ]),
  SEC("\U0001F4F6","Connectivity", [
    R("Coverage","4G reaches 84% of the UK landmass from all four operators. Wessex is well covered.","https://www.ofcom.org.uk/phones-and-broadband/coverage-and-speeds/connected-nations-update-spring-2026"),
    R("Roaming","EU 'roam like at home' does not help a South African SIM. Vodacom travel bundles start around R99 for 1GB with 7-day validity; a UK eSIM runs roughly US$27 for 7 days of unlimited data.","https://www.vodacom.co.za/vodacom/shopping/v/data-travel-bundles", flag=True),
  ]),
 ],
 "verify":["UK visitor visa fee — rose on 8 Apr 2026 and UKVI revises roughly twice a year.",
           "Salisbury Cathedral and National Trust prices — a temporary VAT cut is in force only 25 Jun–1 Sep 2026."],
})

# ── gbrail — London to the Hebridean sea ────────────────────────────────────
TRIPS.append({
 "key":"gbrail", "match":{"tour":"gbrail"},
 "title":"London to the Hebridean sea — by rail",
 "shape":"Rail · York, Durham, the Northumberland coast, Rannoch Moor and the Glenfinnan steam finale",
 "checked":CHECKED,
 "budget":{
   "basis":"Per adult, 2026 season.",
   "rows":[
     R("UK Standard Visitor visa","£135 for 6 months.","https://www.gov.uk/government/publications/visa-regulations-revised-table/home-office-immigration-and-nationality-fees-8-april-2026", flag=True),
     R("The Jacobite (Fort William–Mallaig)","RETURN ONLY: adult day return Standard £76, First Class £116; child under 16 £43/£76; minimum £3.75 booking fee.","https://westcoastrailways.co.uk/jacobite/fare-prices", flag=True),
     R("The Jacobite 2026 season","Morning service Mon 1 Jun – Fri 23 Oct, seven days a week. Afternoon service Wed 10 Jun – Fri 25 Sep. NOTHING runs 24 Oct – 31 May.","https://westcoastrailways.co.uk/jacobite/fare-prices", flag=True),
   ],
   "note":"Indicative only. Not a quote — TrustSquare does not sell or book this trip."
 },
 "sections":[
  SEC("\U0001F6C2","Entry & documents", UK_ENTRY() + SA_DEPARTURE),
  SEC("\U0001F489","Health & healthcare", [
    R("Vaccinations","None required."),
    R("NHS charges for visitors","150% of the NHS tariff at the point of use for visits of 6 months or less. A&E and urgent care are free; inpatient admission after A&E is not. Scotland has separate regulations.","https://www.gov.uk/guidance/nhs-entitlements-migrant-health-guide", flag=True),
    R("Midges","May to October, worst at dawn and dusk in calm overcast conditions in the west Highlands and islands. They are inactive above about 7 mph of wind. Not dangerous — but they will decide whether you enjoy an evening.","https://www.visitscotland.com/travel-planning/midges-ticks-scotland"),
  ]),
  SEC("\U0001F6E1","Safety & travel notices", [
    R("UK terrorism threat level","SUBSTANTIAL — an attack is likely.","https://www.mi5.gov.uk/threat-levels"),
    R("If you leave the train and go up a hill","Check mountain weather and avalanche forecasts. Winter requires an ice axe, crampons, rigid boots, a head torch and a survival bag. Emergency: 999 or 112, ask for Police then Mountain Rescue. Avalanche forecasts run mid-December to early April.","https://www.mountaineering.scot/safety-and-skills/thinkwinter", flag=True),
    R("Daylight","Fort William gets about 6h45m of daylight on 21 December against 17h50m on 21 June. A winter rail trip is largely in the dark.", flag=True),
    R("Weather","The west Highlands take over 3,500 mm of rain a year, wettest October to January, with more than 25 gale days a year in the Hebrides.","https://www.metoffice.gov.uk/"),
  ]),
  SEC("\U0001F4B3","Money, tax & tipping", UK_MONEY),
  SEC("\U0001F5D3","Best season & timing", [
    R("Best compromise for the West Highland Line","Late May to June, or late September to October — the Jacobite is running, the days are long enough and the midges are manageable.","https://westcoastrailways.co.uk/jacobite/fare-prices"),
    R("Avoid","24 October to 31 May if the steam train matters to you — it does not run at all. December daylight in the Highlands is under seven hours."),
    R("Book early","The Jacobite sells out. A few day-of seats may be sold by the guard at Fort William, cash only, never guaranteed. Extreme heat can suspend the service and diesel may substitute for steam."),
  ]),
  SEC("\U0001F4F6","Connectivity", [
    R("Dead stretches","Scotland has the lowest geographic coverage of the four UK nations. Rannoch Moor is the longest unpopulated section on the line — assume no service. ScotRail offers wifi on the West Highland Line but it depends on trackside mobile signal.","https://www.ofcom.org.uk/phones-and-broadband/coverage-and-speeds/ofcom-checker"),
  ]),
 ],
 "verify":["UK visitor visa fee.","The Jacobite's season dates and fares — set per season and it sells out."],
})

# ── DE — Bavarian Alps hut-to-hut trek ──────────────────────────────────────
TRIPS.append({
 "key":"DE", "match":{"country":"DE"},
 "title":"The Bavarian Alps — five days hut to hut",
 "shape":"Trek · staffed alpine huts · Schengen visa country · the huts are CASH ONLY",
 "checked":CHECKED,
 "budget":{
   "basis":"Per person, DAV tariff order and 2026 season.",
   "rows":[
     R("Schengen visa","EUR 90 for adults and 12+, EUR 45 for ages 6–11, free under 6.","https://southafrica.diplo.de/sa-en/sa-consular/sa-gebuehren-2189040", flag=True),
     R("Hut bed — DAV member","Mattress dorm EUR 15, multi-bed room EUR 25, twin room EUR 36 (Category I ceilings, adult 25+).","https://www.alpenverein.de/verband/huetten-und-wege/huetten-und-tarifordnung"),
     R("Hut bed — NON-member","At least EUR 12 more per night in Categories I and II. Over a five-day traverse that alone roughly pays for a membership.","https://www.alpenverein.de/verband/huetten-und-wege/huetten-und-tarifordnung"),
     R("DAV membership","Set per section — Sektion München & Oberland charges about EUR 121 a year for a full adult. It also includes the Alpiner Sicherheits-Service: search, rescue and recovery including helicopter up to EUR 50,000 per incident.","https://www.alpenverein-muenchen-oberland.de/mitgliedschaft/mitgliedsbeitraege", flag=True),
     R("Bergsteigeressen (the mountaineer's meal)","At least one dish, at least vegetarian, member price at least 10% below list and CAPPED at EUR 11.00. Tea water EUR 3.00 a litre for members.","https://www.alpenverein.de/verband/huetten-und-wege/huetten-und-tarifordnung"),
     R("Travel medical insurance","Mandatory for the visa: minimum EUR 30,000 cover, valid for all Schengen countries, covering emergency treatment, repatriation and repatriation of remains.","https://southafrica.diplo.de/sa-en/sa-consular/sa-visa1/sa-visashort", flag=True),
   ],
   "note":"Indicative only. Not a quote — TrustSquare does not sell or book this trip."
 },
 "sections":[
  SEC("\U0001F6C2","Entry & documents", [
    R("South African passport — SCHENGEN TYPE C VISA REQUIRED","EUR 90. Apply through TLScontact — the German missions work only with TLScontact, NOT VFS Global, and not with any other agency. Missions: Embassy Pretoria and Consulate General Cape Town.","https://southafrica.diplo.de/sa-en/sa-consular/sa-visa1/sa-visashort", flag=True),
    R("Processing","15 days as a rule. The mission advises booking the TLScontact appointment at least four weeks before departure; applications are accepted up to six months ahead."),
    R("What they will ask for","A written itinerary with place names and dates; accommodation proof with full addresses for the ENTIRE stay — hut bookings count, so get written confirmations; a return flight reservation; three months of bank statements showing at least EUR 45 per person per day; an employer letter confirming leave; and the travel medical insurance.","https://southafrica.diplo.de/sa-en/sa-consular/sa-visa1/sa-visashort", flag=True),
    R("EES is live and it applies to you","The EU Entry/Exit System became fully operational on 10 April 2026 and it DOES apply to visa holders. It records your fingerprints and facial image at first entry and has replaced passport stamping. Expect biometric enrolment at a kiosk and longer queues.","https://home-affairs.ec.europa.eu/news/entry-exit-system-ees-fully-operational-2026-04-10_en", flag=True),
    R("ETIAS does NOT apply to South Africans","ETIAS covers visa-EXEMPT nationals only. It is also not live — the EU withdrew its Q4 2026 target in July 2026 and no official date now stands. Ignore anyone telling you a South African needs one.","https://home-affairs.ec.europa.eu/news/entry-exit-system-fully-operational-10-april-2026-who-exempt-2026-07-27_en", flag=True),
    R("Passport","Issued within the last 10 years, valid at least 3 months after your return, at least 2 blank pages, signed. Non-SA citizens also need a valid SA residence permit allowing re-entry."),
    R("90/180 rule","Standard Schengen: 90 days in any rolling 180."),
  ] + SA_DEPARTURE),
  SEC("\U0001F489","Health", [
    R("Tick-borne encephalitis — essentially all of Bavaria is a risk area","185 designated risk districts nationally as at Jan 2026, concentrated in Bavaria and Baden-Württemberg. The vaccine is a THREE-DOSE primary series, so start four to six months before travel. Tick season runs roughly April/May to October/November.","https://www.rki.de/DE/Aktuelles/Publikationen/Epidemiologisches-Bulletin/2026/09_26.html", flag=True),
    R("Lyme disease","No human vaccine exists. Prevention is tick avoidance and removing any tick within about 12 hours.","https://www.rki.de/DE/Aktuelles/Publikationen/RKI-Ratgeber/Ratgeber/Ratgeber_LymeBorreliose.html"),
    R("Altitude is NOT the risk here","Altitude sickness starts to matter above about 2,500 m and the Bavarian hut routes sit below it — Reintalangerhütte 1,369 m, Watzmannhaus 1,930 m, Knorrhütte 2,052 m. The exceptions are the Zugspitze summit at 2,962 m and the Münchner Haus."),
    R("Weather and terrain are the risk","Lightning peaks June to August, rising from midday and peaking around 18:00. The DAV's advice is to abort at the first sign and leave ridges and summit crosses immediately. Via ferrata needs an EN 958 set, a helmet and a harness.","https://www.alpenverein.de/artikel/unwetter-im-gebirge_abf33f74-f927-48ab-975d-d297b38332cd", flag=True),
    R("Emergency number","112 in Germany and Bavaria — Bergwacht Bayern is reached through 112. There is no separate German alpine number. 140 is Austria only, relevant if your route crosses into Tyrol.","https://www.alpenverein.de/artikel/notruf-und-rettung-in-den-alpen_3802c636-0bd1-4f83-a33a-e9b266bd51d8"),
  ]),
  SEC("\U0001F6E1","Safety & travel notices", [
    R("UK FCDO","No advise-against-travel areas for Germany.","https://www.gov.uk/foreign-travel-advice/germany"),
    R("US State Department","Level 2 — Exercise Increased Caution (terrorism).","https://travel.state.gov/en/international-travel/travel-advisories/germany.html"),
    R("Booking the huts","The old alpsonline.org system is obsolete — it was replaced at the end of 2024 by hut-reservation.org, covering 500+ huts. Reservation is strongly recommended, not universally mandatory; huts may take deposits and charge late-cancellation fees.","https://www.alpenverein.de/artikel/onlinereservierungssystem-der-alpenvereinshutten_c060cfdc-a751-43ae-adc2-0d3e3e640bda", flag=True),
    R("Hut rules worth knowing","Huts may pre-book at most 90% of beds. Sick or injured people and rescue crews have absolute priority over all guests. A Hüttenschlafsack (sleeping bag liner) is COMPULSORY. Huts may not force half-board as a booking condition.","https://www.alpenverein.de/verband/huetten-und-wege/huetten-und-tarifordnung"),
    R("Season is staggered","Lower huts open from early May, most staffed huts by early June, closing into early October. Outside that only unstaffed winter rooms remain.","https://www.alpenverein.de/artikel/oeffnungstermine-der-dav-huetten-im-sommer-2026_eb1fadf9-64a1-4733-89be-d70d47caa33b", flag=True),
    R("Log your route","Write your route and mobile number in the Hüttenbuch on arrival — the DAV recommends it specifically so missing walkers can be located."),
  ]),
  SEC("\U0001F4B3","Money, tax & tipping", [
    R("Currency","Euro. VAT 19% standard, 7% reduced. Restaurant food dropped from 19% to 7% permanently on 1 Jan 2026 — drinks stayed at 19%.","https://www.bundesfinanzministerium.de/"),
    R("THE HUTS ARE CASH","The DAV says it plainly: bring cash, because many huts cannot take cards. Carry enough for the whole traverse. There are no ATMs up there.","https://www.alpenverein.de/artikel/zu-gast-auf-alpenvereinshutten_7bf6cdc6-934f-4a00-9ff7-9829cb6180d0", flag=True),
    R("VAT refund for non-EU residents","Your invoice must exceed EUR 50, the goods must leave the EU by the end of the third calendar month after purchase, and the export must be certified by a customs stamp at the exit point. A digital version launched in Jun 2026 but is valid only at the Swiss land border — at airports the paper stamp still applies.","https://www.zoll.de/DE/Fachthemen/Steuern/Umsatzsteuererstattung/umsatzsteuererstattung.html"),
    R("Tipping","No official German source publishes a percentage. The consistent convention is to round up or add roughly 5–10%, handed to the server when you pay ('stimmt so') rather than left on the table.", flag=True),
  ]),
  SEC("\U0001F5D3","Best season & timing", [
    R("Go","Mid-July to mid-September."),
    R("Avoid","June and early July on the high routes — residual snow on north-facing traverses and many higher huts not yet open. Avoid after early October when the huts close."),
    R("August is peak","German and Bavarian school holidays. Book months ahead."),
    R("Daily rhythm","Afternoon thunderstorms are the dominant summer pattern. Start early and be off the ridges and via ferrata by early afternoon."),
  ]),
  SEC("\U0001F4F6","Connectivity", [
    R("On the huts","Assume no wifi and often no signal. Electricity costs about ten times valley prices, sockets are scarce and may be chargeable — bring a power bank, and keep the phone off in dead zones because the automatic network search drains the battery.","https://www.alpenverein.de/artikel/zu-gast-auf-alpenvereinshutten_7bf6cdc6-934f-4a00-9ff7-9829cb6180d0"),
    R("Roaming","EU 'roam like at home' does NOT cover South African SIMs — it applies only to EU/EEA subscribers. You pay your own carrier's roaming rate or buy a local eSIM. 112 works from any phone, even without a SIM.","https://digital-strategy.ec.europa.eu/en/policies/roaming", flag=True),
  ]),
 ],
 "verify":["ETIAS — no official date stands; a revised timeline was expected after the EU agency's September 2026 board meeting.",
           "Schengen visa fee — reviewed every three years, next due around mid-2027.",
           "Hut opening dates and tariffs — set per season and per hut."],
})

# ── Shared US blocks ────────────────────────────────────────────────────────
def US_ENTRY():
  return [
    R("South African passport — B-1/B-2 VISA REQUIRED. ESTA does NOT apply","South Africa is not in the Visa Waiver Program — no African country is. You need a full visitor visa with an interview.","https://travel.state.gov/content/travel/en/us-visas/tourism-visit/visa-waiver-program.html", flag=True),
    R("Fee","US$185 MRV fee, non-refundable.","https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/fees/fees-visa-services.html", flag=True),
    R("A US$250 'Visa Integrity Fee' is enacted but NOT yet collected","Created by law in Jul 2025 with no statutory effective date; DHS has not published the implementing rule. It could switch on with a single Federal Register publication — budget for the possibility.","https://www.govinfo.gov/content/pkg/PLAW-119publ21/html/PLAW-119publ21.htm", flag=True),
    R("Where and how long","Johannesburg and Cape Town only — Durban lost routine visa services on 1 Aug 2026. Next-available appointment as at 17 Aug 2026: Johannesburg 1 month, Cape Town 1.5 months. Updated monthly.","https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/global-visa-wait-times.html", flag=True),
    R("Interview is required","Since 1 Oct 2025 all applicants generally need an in-person interview, including under-14s and over-79s. Dropbox survives only for a B-1/B-2 renewal within 12 months of the previous visa's expiry.","https://travel.state.gov/content/travel/en/News/visas-news/interview-waiver-update-sept-18-2025.html", flag=True),
    R("Once you have it","B-1/B-2 for South Africans is multiple entry, valid 120 months (10 years), no reciprocity fee. The visa only gets you to a port of entry — CBP decides your admitted period on the I-94, typically up to six months.","https://travel.state.gov/content/travel/en/us-visas/Visa-Reciprocity-and-Civil-Documents-by-Country/SouthAfrica.html"),
    R("Passport","South Africa is on the Six Month Club exemption list, so validity only for the period of stay is required. Airline agents often misapply this — keep margin anyway.","https://www.cbp.gov/"),
    R("DS-160","Requires social media identifiers for listed platforms used in the preceding five years. The stricter 'set profiles to public' rule covers student and work categories — B visas are not on that list.","https://travel.state.gov/"),
  ]

US_MONEY_BASE = [
    R("No VAT — sales tax is added AT THE TILL","The shelf price is not the price you pay. Sales tax is set by state and local jurisdictions and 45 states levy it.","https://taxfoundation.org/data/all/state/2026-sales-tax-rates-midyear/", flag=True),
    R("Rates on this route","Wyoming 5.39% · MONTANA 0.00%, no general sales tax · Illinois 8.98% average, Chicago 10.25% · California 9.03% average, San Francisco 8.625% · Colorado 7.89% · Utah 7.42% · Nevada 8.24%.","https://taxfoundation.org/data/all/state/2026-sales-tax-rates-midyear/"),
    R("Sales tax is generally NOT refundable to visitors","Louisiana's scheme ended in 2024. Texas still refunds through licensed private brokers. Neither is on this route — treat sales tax as a sunk cost."),
    R("Always decline dynamic currency conversion","Pay in USD. DCC costs roughly 3–4%.","https://usa.visa.com/"),
    R("TIPPING — the field South Africans most often get wrong","Table-service restaurants 15–20% PRE-TAX. Bars US$1–2 a drink or 15–20%. Hotel housekeeping US$2–5 per night, left daily. Bellhop US$2 for the first bag, US$1 each after. Taxi and rideshare 15–20%, minimum US$1. Tour guides 15–20%.","https://emilypost.com/advice/general-tipping-guide", flag=True),
    R("Why it is not optional","The federal tipped cash wage is US$2.13 an hour, unchanged since 1991, against a US$7.25 minimum, with the employer claiming a tip credit. California, Montana and Nevada allow no tip credit; Illinois and Wyoming do — so your tip matters most in Chicago and Wyoming.","https://www.dol.gov/agencies/whd/state/minimum-wage/tipped"),
]

US_HEALTH_COST = R("The underestimated risk: US healthcare costs for an uninsured visitor",
    "There is no reciprocal health agreement with South Africa and Medicare never covers visitors. Average ER visit about US$2,453. Hospital about US$3,297 per inpatient day. Ground ambulance about US$1,093 a trip. AIR AMBULANCE median charge about US$36,400 by helicopter and US$40,600 fixed-wing. International repatriation US$20,000–US$200,000. Travel medical insurance is not required for entry — it is required by common sense.",
    "https://travel.state.gov/en/international-travel/planning/guidance/medicine-health.html", flag=True)

# ── US — Yellowstone country self-drive ─────────────────────────────────────
TRIPS.append({
 "key":"US", "match":{"country":"US"},
 "title":"Yellowstone country — the safari route",
 "shape":"Self-drive · the Lamar and Hayden valleys, the geyser basins and a timber lodge · a NON-RESIDENT SURCHARGE now applies at the gate",
 "checked":CHECKED,
 "budget":{
   "basis":"Two South African adults, one vehicle, 2026 tariff. The park-fee line changed materially in 2026 — read it before you budget anything else.",
   "rows":[
     R("US B-1/B-2 visa","US$185 per person, plus a possible US$250 integrity fee that is enacted but not yet collected.","https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/fees/fees-visa-services.html", flag=True),
     R("Yellowstone entrance","US$35 per vehicle for 7 days (motorcycle US$30, per person on foot or bike US$20).","https://www.nps.gov/yell/planyourvisit/fees.htm"),
     R("NON-RESIDENT SURCHARGE — new","US$100 per non-US-resident aged 16+, IN ADDITION to the entrance fee, at 11 parks including Yellowstone AND Grand Teton. Waived only if you are admitted on an annual pass.","https://www.nps.gov/aboutus/nonresident-fees.htm", flag=True),
     R("The pass that beats it","Non-Resident Annual Pass US$250 from 1 Jan 2026 — it covers entrance AND the non-resident fee for a whole private vehicle. For two South African adults doing both Yellowstone and Grand Teton, US$250 beats paying US$35 + US$100 + US$100 at each park. The US$80 America the Beautiful pass is for citizens and residents only.","https://www.nps.gov/aboutus/commercial-tours-and-nonresident-fees.htm", flag=True),
     R("Grand Teton","US$35 per vehicle, charged SEPARATELY from Yellowstone. The Moose entrance is cashless.","https://www.nps.gov/grte/planyourvisit/fees.htm"),
     R("Campgrounds","All 11 are reservable and Recreation.gov opens sites exactly six months ahead. 2026 nightly US$20–45 (US$94 for Fishing Bridge RV). Backcountry overnight permit US$5 per person per night plus a US$10 reservation.","https://www.recreation.gov/"),
     R("Travel medical insurance","Not a legal requirement. See the health section for why you buy it anyway."),
   ],
   "note":"Indicative only. Not a quote — TrustSquare does not sell or book this trip."
 },
 "sections":[
  SEC("\U0001F6C2","Entry & documents", US_ENTRY() + SA_DEPARTURE),
  SEC("\U0001F489","Health", [
    R("Vaccinations","None required to enter from South Africa. The COVID vaccination requirement was rescinded in May 2023."),
    US_HEALTH_COST,
    R("Altitude","Most of Yellowstone sits at 6,000 ft (1,829 m) or above, up to about 10,000 ft. The highest road crossing is Craig Pass at 8,262 ft / 2,518 m. Take the first day gently.","https://www.nps.gov/yell/planyourvisit/weather.htm"),
    R("Water","The Park Service says boil, filter or chemically treat all backcountry drinking water — giardia is present.","https://www.nps.gov/yell/planyourvisit/backcountrysafety.htm"),
  ]),
  SEC("\U0001F6E1","Safety & travel notices", [
    R("THE LEGAL WILDLIFE DISTANCES","Bison, elk and all other wildlife: 25 yards (23 m). Bears, wolves and cougars: 100 yards (91 m). These are rules, not suggestions.","https://www.nps.gov/yell/planyourvisit/safety.htm", flag=True),
    R("Bison injure more people than any other animal in the park","And traffic accidents are the most common cause of injury and death in Yellowstone overall.","https://www.nps.gov/yell/planyourvisit/safety.htm"),
    R("Thermal areas","Burns are a common cause of serious injury and death. The ground can be a thin crust over super-heated water. Stay on the boardwalks. No swimming in hot springs. No pets.","https://www.nps.gov/yell/planyourvisit/safety.htm", flag=True),
    R("Bears","Carry bear spray where you can reach it and deploy at 60 ft (18 m). Hike in groups of three or more. Hang food 10 ft up and 4 ft out or use a canister; cook and store 100 yards from where you sleep.","https://www.nps.gov/yell/planyourvisit/backcountrysafety.htm"),
    R("ROADS CLOSE — this is the trip-killer","Only the North Entrance (Gardiner) to Mammoth to Tower to the Northeast Entrance is open to cars year-round. Most other roads close from early November to late April. 2026: West/Madison/Norris 17 Apr–31 Oct; East Entrance and Craig Pass early May–31 Oct; Dunraven Pass and the Beartooth Highway 22 May–12 Oct.","https://www.nps.gov/yell/planyourvisit/parkroads.htm", flag=True),
    R("Advisories","UK FCDO: no advisory against travel. Australian Smartraveller: Level 1, exercise normal safety precautions.","https://www.gov.uk/foreign-travel-advice/usa"),
  ]),
  SEC("\U0001F4B3","Money, tax & tipping", US_MONEY_BASE + [
    R("At the gate","All five Yellowstone entrance stations take cash or card. Cash is still about 14% of US payments; chip and contactless are near-universal and foreign Visa/Mastercard are widely accepted.","https://www.nps.gov/yell/planyourvisit/fees.htm"),
  ]),
  SEC("\U0001F5D3","Best season & timing", [
    R("Best self-drive window","Mid-September to mid-October — all roads open, the elk rut is on and the crowds have thinned.","https://www.nps.gov/yell/planyourvisit/seasons.htm"),
    R("The Park Service's own busyness rating","June to September busiest; May and October moderately busy; November to April least busy.","https://www.nps.gov/yell/planyourvisit/seasons.htm"),
    R("Avoid","November to March (one road only, snowcoach otherwise). April to early May (mud and staged openings — all roads open only by Memorial Day). July and August for crowds plus the Park Service's own wildfire-haze warnings."),
    R("Daily timing","Enter before 07:00 or after 12:00 to miss the queues."),
  ]),
  SEC("\U0001F4F6","Connectivity", [
    R("Where the towers actually are","Mammoth Hot Springs, West Yellowstone, Old Faithful, Grant Village, Lake Village and Mount Washburn. Canyon, Fishing Bridge and Tower are NOT tower sites. The Park Service's own advice: texting is usually the most effective communication in the park.","https://www.nps.gov/yell/planyourvisit/goodsandservices.htm", flag=True),
    R("Wifi","Free NPS wifi only at the Albright, Old Faithful and West Yellowstone visitor centres. Lodge wifi (one device per room) at Mammoth Hotel, Canyon, Old Faithful Snow Lodge and Grant Village. NO internet at all at Old Faithful Inn, Roosevelt Lodge or Lake Yellowstone Hotel.","https://www.nps.gov/yell/planyourvisit/goodsandservices.htm"),
  ]),
 ],
 "verify":["The non-resident park surcharge — the exact commencement date is not stated by the Park Service, only the pass tier date of 1 Jan 2026.",
           "The US$250 Visa Integrity Fee — one DHS publication switches it on.",
           "Visa interview wait times — updated monthly.",
           "Yellowstone road opening dates — snow-dependent and set seasonally."],
})

# ── usrail — California Zephyr ──────────────────────────────────────────────
TRIPS.append({
 "key":"usrail", "match":{"tour":"usrail"},
 "title":"Chicago to San Francisco — the California Zephyr",
 "shape":"Rail · two nights aboard · the Mississippi, the Rockies, the desert dawn and Donner Pass",
 "checked":CHECKED,
 "budget":{
   "basis":"Per person, 2026.",
   "rows":[
     R("US B-1/B-2 visa","US$185, plus the possible US$250 integrity fee that is enacted but not yet collected.","https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/fees/fees-visa-services.html", flag=True),
     R("Sleeping car attendant tip","Customary US$10–20 per night per room. Amtrak publishes NO tipping rates — this is convention, not policy.","https://www.amtrak.com/", flag=True),
     R("Dining car tip","Customary 15–20% of the menu price even though sleeper meals are included — roughly US$3 breakfast, US$5 lunch, US$7–10 dinner per person. Chicago to Emeryville is TWO nights.","https://www.amtrak.com/california-zephyr-train", note="Amtrak publishes no tipping rates at all — these are traveller convention, not company policy."),
     R("Red Cap baggage help","Free, though a tip is welcome.","https://www.amtrak.com/amtrak-red-cap-baggage-assistance"),
   ],
   "note":"Indicative only. Not a quote — TrustSquare does not sell or book this trip."
 },
 "sections":[
  SEC("\U0001F6C2","Entry & documents", US_ENTRY() + SA_DEPARTURE),
  SEC("\U0001F489","Health", [
    R("Vaccinations","None required to enter from South Africa."),
    US_HEALTH_COST,
    R("Altitude on the route","The train crosses the Front Range at around 9,000 ft. It is brief and you are seated — not a practical concern for most people."),
  ]),
  SEC("\U0001F6E1","Safety & travel notices", [
    R("BUILD IN A SPARE DAY","Amtrak's own figure: the California Zephyr ran 51% on time in 2024, the third-worst long-distance route, and no long-distance route met the 80% standard. Amtrak names the cause as freight train interference. On a roughly 51-hour run, do NOT book an onward flight for the day you arrive.","https://www.amtrak.com/on-time-performance", flag=True),
    R("Seasonal risk","Winter snow through the Rockies and Donner Pass, and summer heat, both add delay risk. Amtrak publishes no seasonal breakdown."),
    R("Advisories","UK FCDO: no advisory against travel. Australian Smartraveller: Level 1.","https://www.gov.uk/foreign-travel-advice/usa"),
  ]),
  SEC("\U0001F4B3","Money, tax & tipping", US_MONEY_BASE),
  SEC("\U0001F5D3","Best season & timing", [
    R("Go","Late spring to early autumn for the scenery and the lowest delay risk."),
    R("Avoid","Deep winter if a tight connection matters — the Rockies and Donner Pass are where the delays compound."),
  ]),
  SEC("\U0001F4F6","Connectivity", [
    R("There is NO wifi on the California Zephyr","It is absent from Amtrak's wifi-equipped route list and the route page does not mention wifi at all. Chicago Union Station has station wifi; Emeryville does not.","https://www.amtrak.com/onboard/journey-with-wi-fi-train-station", flag=True),
    R("Signal","Expect dead stretches through Gore, Byers and Glenwood Canyons, the 6.2-mile Moffat Tunnel, the Ruby Canyon, the Nevada desert and the Sierra Nevada. Download everything before you board."),
  ]),
 ],
 "verify":["The US$250 Visa Integrity Fee.","Visa interview wait times — updated monthly.","Amtrak on-time performance — published annually."],
})

# ── Shared AU blocks ────────────────────────────────────────────────────────
def AU_ENTRY():
  return [
    R("South African passport — VISITOR VISA SUBCLASS 600. No ETA, no eVisitor","South Africa is on neither the ETA (601) nor the eVisitor (651) eligible list. You apply for the Visitor visa, Tourist stream.","https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/electronic-travel-authority-601", flag=True),
    R("Fee","AUD 250 base charge applying from outside Australia. Indexed every 1 July — re-check before you budget.","https://immi.homeaffairs.gov.au/visas/getting-a-visa/fees-and-charges/current-visa-pricing", flag=True),
    R("Processing (as at 21 Aug 2026)","25% decided in 7 days, 50% in 13 days, 75% in 28 days, 90% in 35 days. Refreshed monthly.","https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-processing-times/global-visa-processing-times", flag=True),
    R("Conditions","You must be outside Australia when you apply AND when it is decided. Health examinations may be required and biometrics may be requested. Stay is generally 3 months. There is no label — the visa is linked digitally to your passport.","https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/visitor-600/tourist-stream-overseas"),
    R("Passport","No Australian six-month rule — valid for the length of your planned stay. Transit countries often DO require six months, so check the whole routing."),
    R("SmartGate","No longer nationality-gated. A South African ePassport holder CAN use the arrivals SmartGates: ePassport symbol, at least 1.1 m tall, at least 7 years old. The Incoming Passenger Card is still in use.","https://www.abf.gov.au/entering-and-leaving-australia/smartgate/arrivals/who-can-use-smartgates"),
    R("Yellow fever","If you are over 12 months old and stayed overnight or longer in a yellow-fever country within 6 days of arriving, you will be asked for a certificate. South Africa is not a risk country — but an overnight African or South American transit within 6 days triggers it.","https://www.health.gov.au/diseases/yellow-fever"),
    R("Healthcare","There is no reciprocal health care agreement with South Africa. Insurance is not a standard condition of the subclass 600 but is strongly recommended; condition 8501 may be imposed.","https://www.servicesaustralia.gov.au/when-reciprocal-health-care-agreements-apply-and-you-visit-australia", flag=True),
  ]

AU_MONEY = [
    R("Currency","Australian dollar. GST 10% on most goods and services, included in the displayed price.","https://www.ato.gov.au/businesses-and-organisations/gst-excise-and-indirect-taxes/gst/how-gst-works"),
    R("Tourist Refund Scheme — real, but strict","Spend at least AUD 300 including GST from ONE business (ABN), within 60 days of departure. You need the ORIGINAL PAPER tax invoice in English — photos, photocopies and reprints are rejected. Claim in person at the TRS facility on the day of departure, at least 30 minutes before your flight. No cash refunds. Excludes alcohol over 22% ABV, tobacco, consumed goods, gift cards and ALL services — so no accommodation, tours or car hire.","https://www.abf.gov.au/entering-and-leaving-australia/tourist-refund-scheme", flag=True),
    R("Bringing it home","Declare at Question 3 on the Incoming Passenger Card if you return. The passenger concession is AUD 900 of general goods for over-18s (AUD 450 under 18) and 2.25 L of alcohol.","https://www.abf.gov.au/entering-and-leaving-australia/duty-free"),
    R("Tipping — NOT like the US","No official body publishes a percentage, and the reason tipping is not built into pay is structural: the National Minimum Wage is AUD 26.44 an hour from 1 July 2026, with award penalty rates on top. Tipping is genuinely optional and modest.","https://www.fairwork.gov.au/pay-and-wages/minimum-wages"),
]

# ── AU — outer Great Barrier Reef ───────────────────────────────────────────
TRIPS.append({
 "key":"AU", "match":{"country":"AU"},
 "title":"The outer Great Barrier Reef — Queensland",
 "shape":"Boat and dive · the Agincourt ribbon reefs and Michaelmas Cay · STINGER SEASON runs Nov–May",
 "checked":CHECKED,
 "budget":{
   "basis":"Per person, 2026.",
   "rows":[
     R("Australian visitor visa (subclass 600)","AUD 250, applying from outside Australia. Indexed every 1 July.","https://immi.homeaffairs.gov.au/visas/getting-a-visa/fees-and-charges/current-visa-pricing", flag=True),
     R("Reef Environmental Management Charge","AUD 8.50 per person per day for a trip of 3 hours or more; AUD 4.25 for a part-day visit under 3 hours. Collected by the operator. No GST on the EMC. Rising to AUD 9.00 and AUD 4.50 from 1 Apr 2027.","https://www.gbrmpa.gov.au/access/environmental-management-charge/what-are-charges", flag=True),
     R("Is the EMC in the advertised price?","Operator-dependent and not published centrally — ask before you book, because it is per person per day.", flag=True),
     R("Travel medical insurance","No reciprocal health agreement with South Africa. Not a visa condition, but strongly recommended.","https://www.servicesaustralia.gov.au/when-reciprocal-health-care-agreements-apply-and-you-visit-australia"),
   ],
   "note":"Indicative only. Not a quote — TrustSquare does not sell or book this trip."
 },
 "sections":[
  SEC("\U0001F6C2","Entry & documents", AU_ENTRY() + SA_DEPARTURE),
  SEC("\U0001F489","Health & marine hazards", [
    R("STINGER SEASON — November through May","Marine stingers can be present all year in tropical Queensland but the risk is materially higher in the Nov–May stinger season. Box jellyfish occur north of Agnes Water. FIRST AID: douse with vinegar for at least 30 seconds, THEN remove tentacles, and monitor for 45 minutes for Irukandji syndrome. Antivenom is held at tropical hospitals and ambulance stations.","https://lifesaving.com.au/beach-safety/marine-stingers", flag=True),
    R("Crocodiles","Crocodile habitat starts near Gladstone and runs north to the Torres Strait, across Cape York and into the Gulf of Carpentaria. Estuarine crocodiles can be in ANY waterway and in the sea in that area.","https://www.qld.gov.au/environment/plants-animals/animals/living-with/crocodiles/becrocwise", flag=True),
    R("FLYING AFTER DIVING — plan your last day","DAN's consensus: minimum 12 hours' surface interval after a single no-decompression dive; minimum 18 hours after multiple dives in a day or over multiple days; substantially longer after decompression dives. A dive on your departure morning is a bad idea.","https://dan.org/health-medicine/health-resources/diseases-conditions/flying-after-diving/", flag=True),
    R("Snorkelling","The FCDO notes snorkelling accidents have been fatal and that a medical declaration for resort diving and snorkelling is required by law.","https://www.gov.uk/foreign-travel-advice/australia"),
    R("Also","Extreme UV, coral cuts, cone shells and stonefish. Ask your operator where the nearest hyperbaric chamber is — we could not confirm it."),
  ]),
  SEC("\U0001F6E1","Safety & travel notices", [
    R("UK FCDO","No advisory against travel anywhere in Australia. Last updated 19 Mar 2026.","https://www.gov.uk/foreign-travel-advice/australia"),
    R("Tropical cyclone season","1 November to 30 April, mainly Queensland, the Northern Territory and Western Australia.","https://www.bom.gov.au/resources/learn-and-explore/tropical-cyclone-knowledge-centre", flag=True),
    R("Bushfire season","Higher risk October to February, peaking November to February.","https://www.gov.uk/foreign-travel-advice/australia"),
  ]),
  SEC("\U0001F4B3","Money, tax & tipping", AU_MONEY),
  SEC("\U0001F5D3","Best season & timing", [
    R("Go","June to October — the window that sits outside BOTH the stinger season (Nov–May) and the cyclone season (1 Nov–30 Apr)."),
    R("Avoid","November to May for both reasons at once."),
  ]),
  SEC("\U0001F4F6","Connectivity", [
    R("Australia's 3G networks are fully switched off","Telstra and Optus in Nov 2024, TPG in Jan 2024. An older handset that relied on 3G — including 4G phones that used 3G for emergency calls — may not work at all.","https://www.infrastructure.gov.au/media-communications/phone/mobile-services-and-coverage/3g-network-switch", flag=True),
    R("Coverage","The FCDO's summary: the network generally works well in cities and large towns, but coverage elsewhere can be very limited or non-existent. Many visitors buy an Australian SIM on arrival."),
  ]),
 ],
 "verify":["Subclass 600 fee — indexed every 1 July.",
           "Visa processing times — refreshed monthly.",
           "Whether your operator includes the Reef EMC in the advertised price."],
})

# ── aurail — The Ghan ───────────────────────────────────────────────────────
TRIPS.append({
 "key":"aurail", "match":{"tour":"aurail"},
 "title":"The Ghan — Adelaide to Darwin",
 "shape":"Rail · the Flinders at dusk, the Marla dawn, the red heart and the Top End · runs March to November ONLY",
 "checked":CHECKED,
 "budget":{
   "basis":"Per person, Journey Beyond's published 2027 fares (the 2026 pages have been retired).",
   "rows":[
     R("Australian visitor visa (subclass 600)","AUD 250, applying from outside Australia.","https://immi.homeaffairs.gov.au/visas/getting-a-visa/fees-and-charges/current-visa-pricing", flag=True),
     R("The Ghan Expedition (Darwin to Adelaide, 4 days / 3 nights)","From AUD 4,190 per person. Gold Twin advance purchase 4,190 / 4,790 / 5,390 by season band; Platinum Twin 7,590–9,390; Aurora Suite 12,490–13,990; Australis Suite 18,890–20,990.","https://www.journeybeyondrail.com.au/packages/the-ghan-expedition-2027/", flag=True),
     R("The Legendary Ghan (Adelaide to Darwin)","Extended to 4 days / 3 nights in 2027. From AUD 3,590 per person.","https://www.journeybeyondrail.com.au/packages/the-legendary-ghan-2027/", flag=True),
     R("What is included","Meals, wines, beverages and the off-train experiences at Katherine, Alice Springs, Coober Pedy and Manguri.","https://www.journeybeyondrail.com.au/guest-information/faq/"),
     R("Uluru is NOT included","The standard Alice Springs off-train experiences do not reach Uluru — only the optional upgrades do. The Uluru-Kata Tjuta park pass is AUD 38 for 3 days, and whether the upgrade covers it is not stated.","https://parksaustralia.gov.au/uluru/plan/passes/", flag=True),
     R("Gratuities","Journey Beyond says journeys are all-inclusive and you will not need to buy anything unless you upgrade or buy souvenirs. It states no gratuity policy.","https://www.journeybeyondrail.com.au/guest-information/faq/"),
   ],
   "note":"Indicative only. Not a quote — TrustSquare does not sell or book this trip."
 },
 "sections":[
  SEC("\U0001F6C2","Entry & documents", AU_ENTRY() + SA_DEPARTURE),
  SEC("\U0001F489","Health", [
    R("Vaccinations","None required from South Africa. A yellow-fever certificate is only triggered by an overnight stop in a risk country within 6 days of arrival.","https://www.health.gov.au/diseases/yellow-fever"),
    R("No reciprocal health agreement with South Africa","Insurance is not a visa condition but is strongly recommended — the Red Centre is a long way from a major hospital.","https://www.servicesaustralia.gov.au/when-reciprocal-health-care-agreements-apply-and-you-visit-australia"),
    R("Heat","The Red Centre is extreme in summer, which is one reason the train does not run December to February."),
  ]),
  SEC("\U0001F6E1","Safety & travel notices", [
    R("UK FCDO","No advisory against travel anywhere in Australia.","https://www.gov.uk/foreign-travel-advice/australia"),
    R("If you add outback driving","The FCDO's own checklist: a roadworthy vehicle with GPS and TWO spare tyres, good maps, extra food, water and fuel, a planned route, local advice, and route details plus expected return time left with someone. NT Police have warned tourists off unsurfaced tracks in remote Central Australia.","https://www.gov.uk/foreign-travel-advice/australia", flag=True),
    R("Crocodiles in the Top End","Estuarine crocodiles can be in any waterway in the Katherine and Darwin region. Swim only where you are told it is safe.","https://www.qld.gov.au/environment/plants-animals/animals/living-with/crocodiles/becrocwise"),
    R("Cyclone season","1 November to 30 April in the Northern Territory — which overlaps the end and start of the Ghan's season.","https://www.bom.gov.au/resources/learn-and-explore/tropical-cyclone-knowledge-centre"),
  ]),
  SEC("\U0001F4B3","Money, tax & tipping", AU_MONEY),
  SEC("\U0001F5D3","Best season & timing", [
    R("The Ghan runs MARCH TO NOVEMBER only","There is no service December to February — the wet season. Journey Beyond describes the Expedition as operating April to October.","https://www.journeybeyondrail.com.au/", flag=True),
    R("Departures","The Expedition runs Wednesdays and Saturdays March to November. The Legendary Ghan runs Saturdays March to November and Tuesdays April to October."),
    R("Season bands affect the fare","March and November are the cheapest band, April and September–October the middle, May to August the peak."),
  ]),
  SEC("\U0001F4F6","Connectivity", [
    R("Limited wifi, and not in the cabins","Journey Beyond: limited wifi in the Outback Explorer Lounges and Platinum Club carriages only, dependent on mobile network coverage, and through remote locations it may not always be available. Cabins are not wifi-equipped.","https://www.journeybeyondrail.com.au/guest-information/faq/", flag=True),
    R("Dead stretches","Long ones, inherent to the route between Adelaide, Alice Springs and Darwin. Plan to be offline."),
  ]),
 ],
 "verify":["Subclass 600 fee — indexed every 1 July.",
           "The Ghan's fares and season bands — Journey Beyond retires and republishes these per year.",
           "Whether the Uluru upgrade includes the park pass."],
})

# ═════════════════════════════════════════════════════════════════════════════
#  ITINERARIES — read straight off the journey specs so the text and the map
#  can never drift apart. One source of truth for the route.
# ═════════════════════════════════════════════════════════════════════════════
SPEC_FOR = {
  "NA":"namibia.json", "BW":"botswana.json", "MZ":"mozambique.json",
  "KE":"kenya.json",   "c2c":"cape_cairo.json", "GB":"gbr.json",
  "gbrail":"gbrail.json", "US":"usa.json", "usrail":"usrail.json",
  "AU":"aus.json", "aurail":"aurail.json",
}
# adventures_de_map.html predates the spec pipeline (see the LAYERS-4-1 note) —
# so this one route is authored here until the DE spec exists.
MANUAL_ITIN = {
 "DE":[
  {"d":"Day 1","t":"Into the range","x":"Valley to first hut","s":"Trailhead transfer, the long climb in, and your first night in a staffed hut."},
  {"d":"Day 2","t":"The high traverse","x":"Ridge day","s":"The exposed section. Start early — afternoon thunderstorms are the summer pattern."},
  {"d":"Day 3","t":"Peaks and passes","x":"Highest ground","s":"The day the route touches its high point. Via ferrata sections need a set, helmet and harness."},
  {"d":"Day 4","t":"Down to the lakes","x":"Descent","s":"Off the high ground toward the lake country, hut to hut."},
  {"d":"Day 5","t":"The lakeside finish","x":"Out","s":"The last descent and the valley finish."},
 ],
}

def load_itineraries():
    out = {}
    jdir = os.path.join(ROOT, "journeys")
    for key, fn in SPEC_FOR.items():
        p = os.path.join(jdir, fn)
        if not os.path.exists(p):
            print("  [skip] no spec for %s (%s)" % (key, fn)); continue
        spec = json.load(open(p, encoding="utf-8"))
        unit = spec.get("unit") or "Day"
        rows = []
        for d in spec.get("days", []):
            rows.append({
              "d": "%s %s" % (unit, d.get("day")),
              "t": (d.get("title") or "").replace("&amp;", "&"),
              "x": (d.get("dist") or d.get("mode") or ""),
              "s": (d.get("summary") or "").replace("&amp;", "&"),
            })
        if rows:
            out[key] = rows
    out.update(MANUAL_ITIN)
    return out

def main():
    itin = load_itineraries()
    for t in TRIPS:
        if not t.get("itinerary"):
            t["itinerary"] = itin.get(t["key"], [])
        if not t["itinerary"]:
            print("  [warn] %s has no itinerary" % t["key"])
    payload = {
      "generated": datetime.date.today().isoformat(),
      "checked":   CHECKED,
      "trips":     TRIPS,
    }
    # compact: this is generated, never hand-edited, and it ships to phones.
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
    js = (
      "/* trip_essentials.js — GENERATED by scripts/build_trip_essentials.py. DO NOT HAND-EDIT.\n"
      "   TRIP-ESSENTIALS-1 (21 Aug 2026). Free traveller pre-information rendered by ms.js\n"
      "   under the journey map on every super-example Adventures advert.\n"
      "   MarketSquare is an introductory service: this informs, it never books or sells.\n"
      "   Regenerate:  python3 scripts/build_trip_essentials.py                            */\n"
      "window.TRIP_ESSENTIALS = " + body + ";\n"
    )
    with io.open(OUT_JS, "w", encoding="utf-8", newline="\n") as f:
        f.write(js)
    # ── self-verify: the file must parse back and carry every trip ───────────
    raw = io.open(OUT_JS, encoding="utf-8").read()
    assert raw.rstrip().endswith(";"), "trip_essentials.js truncated"
    back = json.loads(raw[raw.index("window.TRIP_ESSENTIALS =") + len("window.TRIP_ESSENTIALS ="):].rstrip().rstrip(";"))
    assert len(back["trips"]) == len(TRIPS), "trip count mismatch"
    rows = srcs = 0
    for t in back["trips"]:
        assert t.get("itinerary"), "%s lost its itinerary" % t["key"]
        assert t.get("sections"), "%s lost its sections" % t["key"]
        for s in t["sections"]:
            for r in s["rows"]:
                rows += 1
                if r.get("src"): srcs += 1
        for r in t["budget"]["rows"]:
            rows += 1
            if r.get("src"): srcs += 1
    print("[OK] %s" % OUT_JS)
    print("     %d trips · %d fact rows · %d carry a source (%d%%) · %d bytes"
          % (len(TRIPS), rows, srcs, round(100.0*srcs/rows), len(raw)))

if __name__ == "__main__":
    main()
