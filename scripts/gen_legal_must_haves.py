# -*- coding: utf-8 -*-
"""MarketSquare 'Absolute Must-Haves' legal cards — per country, per category.
Usage: python3 gen_legal_must_haves.py [ZA|US|UK|AU|all]
Output: assets/legal-must-haves/<CC>/must-haves-<CC>-<category>.{svg,png}
Content is data-only below; layout is shared. Update rows when laws change.
Content last reviewed: 2026-07-17.
"""
import html, textwrap, os, sys

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "legal-must-haves")
W = 1080
NAVY = "#14213d"
E = html.escape
def wrap(t, n): return textwrap.wrap(t, n) or [""]

def icon(name, a):
    g = {
    'doc':   '<rect x="-11" y="-15" width="22" height="30" rx="3" fill="#fff"/>' + ''.join(f'<rect x="-7" y="{y}" width="14" height="2.6" rx="1.3" fill="{a}"/>' for y in (-9,-4,1,6)),
    'bolt':  '<path d="M 2,-16 L -9,2 L -1,2 L -3,16 L 9,-3 L 1,-3 Z" fill="#fff"/>',
    'bank':  '<path d="M -14,-6 L 0,-15 L 14,-6 Z" fill="#fff"/>' + ''.join(f'<rect x="{x}" y="-4" width="4.5" height="14" fill="#fff"/>' for x in (-13,-6,1,8)) + '<rect x="-14" y="11" width="28" height="4" fill="#fff"/>',
    'lock':  '<rect x="-10" y="-3" width="20" height="17" rx="3" fill="#fff"/><path d="M -6,-3 v-4 a 6 6 0 0 1 12 0 v 4" fill="none" stroke="#fff" stroke-width="3.4"/>',
    'id':    f'<rect x="-15" y="-11" width="30" height="22" rx="3" fill="#fff"/><circle cx="-7" cy="-2" r="4" fill="{a}"/><rect x="-11" y="4" width="8" height="2.4" fill="{a}"/><rect x="2" y="-6" width="11" height="2.4" fill="{a}"/><rect x="2" y="-1" width="11" height="2.4" fill="{a}"/><rect x="2" y="4" width="11" height="2.4" fill="{a}"/>',
    'car':   f'<path d="M -14,4 L -11,-4 Q -10,-7 -6,-7 L 6,-7 Q 9,-7 11,-4 L 14,4 Z" fill="#fff"/><rect x="-15" y="3" width="30" height="7" rx="3" fill="#fff"/><circle cx="-8" cy="11" r="3.4" fill="{a}" stroke="#fff" stroke-width="2"/><circle cx="8" cy="11" r="3.4" fill="{a}" stroke="#fff" stroke-width="2"/>',
    'form':  f'<rect x="-11" y="-15" width="22" height="30" rx="3" fill="#fff"/><path d="M -6,0 L -2,5 L 7,-6" fill="none" stroke="{a}" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>',
    'shield':f'<path d="M 0,-15 C 5,-12 10,-11 13,-11 C 13,2 9,11 0,15 C -9,11 -13,2 -13,-11 C -10,-11 -5,-12 0,-15 Z" fill="#fff"/><path d="M -5,-1 L -1,4 L 7,-6" fill="none" stroke="{a}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>',
    'grad':  '<path d="M 0,-12 L 16,-5 L 0,2 L -16,-5 Z" fill="#fff"/><path d="M -8,-1 v 7 q 8,6 16,0 v -7" fill="#fff"/><rect x="14" y="-5" width="2.4" height="12" fill="#fff"/>',
    'house': f'<path d="M 0,-15 L 15,-1 L 11,-1 L 11,13 L -11,13 L -11,-1 L -15,-1 Z" fill="#fff"/><rect x="-4" y="3" width="8" height="10" fill="{a}"/>',
    'flame': '<path d="M 0,-15 C 6,-8 11,-3 11,4 A 11 11 0 0 1 -11,4 C -11,-1 -8,-5 -5,-8 C -5,-4 -3,-2 0,-1 C -2,-6 -2,-10 0,-15 Z" fill="#fff"/>',
    'cross': f'<rect x="-13" y="-13" width="26" height="26" rx="4" fill="#fff"/><path d="M 0,-8 v 16 M -8,0 h 16" stroke="{a}" stroke-width="5" stroke-linecap="round"/>',
    'tree':  '<path d="M 0,-16 L 9,-4 L 5,-4 L 12,6 L -12,6 L -5,-4 L -9,-4 Z" fill="#fff"/><rect x="-2.4" y="6" width="4.8" height="8" fill="#fff"/>',
    'star':  '<path d="M 0,-15 L 4,-5 L 15,-5 L 6,2 L 9,13 L 0,7 L -9,13 L -6,2 L -15,-5 L -4,-5 Z" fill="#fff"/>',
    'gem':   f'<path d="M -9,-11 L 9,-11 L 15,-3 L 0,14 L -15,-3 Z" fill="#fff"/><path d="M -9,-11 L 0,14 L 9,-11 M -15,-3 L 15,-3" stroke="{a}" stroke-width="2" fill="none"/>',
    'cash':  f'<rect x="-15" y="-9" width="30" height="18" rx="3" fill="#fff"/><circle cx="0" cy="0" r="5.5" fill="{a}"/><rect x="-12" y="-6" width="3" height="3" fill="{a}"/><rect x="9" y="3" width="3" height="3" fill="{a}"/>',
    }
    return g.get(name, g['doc'])

STYLE = {  # per-category accent colours, identical across countries
 "property":   ("#3f51b5","#e8eaf6","#dfe3f5","PROPERTY"),
 "cars":       ("#2e7d54","#e3f2e9","#d5ecdd","CARS"),
 "tutors":     ("#c07a10","#fdf3e3","#f7e8cc","TUTORS"),
 "services":   ("#00838f","#e0f2f4","#cfe9ec","SERVICES"),
 "adventures_accommodation": ("#0277bd","#e3f1fa","#d2e8f6","ADVENTURES — ACCOMMODATION"),
 "adventures_experiences":   ("#d84315","#fbe9e2","#f6dccf","ADVENTURES — EXPERIENCES"),
 "collectors": ("#6a3ab2","#efe8f9","#e4d8f4","COLLECTORS"),
}
TITLES = {
 "property":"SELLING YOUR HOUSE PRIVATELY","cars":"SELLING YOUR CAR PRIVATELY",
 "tutors":"TUTORING PRIVATELY","services":"OFFERING TRADE SERVICES PRIVATELY",
 "adventures_accommodation":"HOSTING GUESTS PRIVATELY","adventures_experiences":"OFFERING EXPERIENCES PRIVATELY",
 "collectors":"SELLING COLLECTABLES PRIVATELY",
}
COUNTRY_NAMES = {"ZA":"SOUTH AFRICA","US":"UNITED STATES","UK":"UNITED KINGDOM","AU":"AUSTRALIA"}
FOOT_NOTE_R = {"ZA":"South Africa","US":"the United States","UK":"the United Kingdom","AU":"Australia"}

# ---------------- content: CONTENT[country][category] = (rows, foot, note) ----------------
CONTENT = {}

CONTENT["ZA"] = {
 "property": ([
  ("doc","Compliance Certificates (CoCs)","Electrical, gas, electric fence*","Seller contracts & pays electrician / specialists","REQUIRED BY CONVEYANCER FOR TRANSFER"),
  ("bank","Rates Clearance Figures","From the municipality","Conveyancing attorney requests figures — seller pays advance amounts","REQUIRED BY DEEDS OFFICE"),
  ("house","Body Corporate / HOA Clearance","If applicable (sectional title / estate)","Conveyancing attorney requests figures — seller pays levy advance","REQUIRED BY DEEDS OFFICE"),
  ("lock","Bond Cancellation (get Title Deed)","Original deed held by the bank","Seller notifies bank — conveyancer manages cancellation, bank releases original title deed","HELD BY BANK UNTIL CANCELLED"),
  ("id","Proof of Identity (FICA)","ID + proof of address","Seller provides to conveyancer","FICA COMPLIANCE"),
 ],"A private sale doesn't mean “no legal process.” A conveyancer is still needed for the transfer.",
   "*Beetle / plumbing CoCs are context-dependent (e.g. coastal areas, City of Cape Town)."),
 "cars": ([
  ("id","Original NaTIS Certificate (RC1)","Proves ownership","Seller pays off finance (if any) — bank then provides the RC1","MANDATORY FOR SALE"),
  ("form","NCO (Yellow Form) — Change of Ownership","Notification of Change of Ownership","Seller completes & submits to the licensing department — releases seller from liability","SELLER RESPONSIBILITY"),
  ("doc","RLV (Blue Form) — Buyer's Application","Application for registration & licensing","Seller provides to buyer","FOR BUYER TO REGISTER CAR"),
  ("car","Roadworthy Certificate (RWC)","Needed to register in buyer's name","Buyer's responsibility to obtain — buyer must register within 21 days of sale","BUYER'S RESPONSIBILITY"),
  ("form","Sales Agreement (Voetstoots)","Documents price, condition, parties","Both parties sign","PROTECTS SELLER, DOCUMENTS TRANSACTION"),
  ("id","Identity Documents","Certified copies","Copies exchanged by both parties","REQUIRED FOR NCO & RLV"),
 ],"A private sale doesn't mean “no legal process.” Paperwork protects the seller from fines & liability.",
   "Seller submits the NCO; buyer applies with RLV & RWC and must register within 21 days."),
 "tutors": ([
  ("shield","Sex Offenders Register Clearance","Children's Act s126 — working with minors","Tutor applies for a clearance certificate (Form 29, Dept of Justice)","LEGALLY REQUIRED WHEN TUTORING MINORS"),
  ("grad","Qualifications / SACE Registration","SACE applies to qualified educators","Tutor provides certified copies to parents on request","BUILDS TRUST — REQUIRED FOR SCHOOL-BASED WORK"),
  ("form","Written Service Agreement","Rates, cancellation, refund terms","Both parties sign — CPA-compliant terms","PROTECTS BOTH PARTIES"),
  ("lock","POPIA Consent for Learner Data","Minors' information needs guardian consent","Parent / guardian signs consent for records & progress reports","REQUIRED BY POPIA"),
  ("cash","Declare Tutoring Income (SARS)","Provisional tax may apply","Tutor invoices and declares income","SARS REQUIREMENT"),
 ],"Working with children is regulated — clearance and consent are not optional extras.",
   "For in-home tutoring of minors, a parent or guardian present is strongly recommended."),
 "services": ([
  ("bolt","Trade Registration / Licence","Electricians: Dept of Employment & Labour. Plumbers: PIRB","Provider registers before doing regulated work","REQUIRED TO ISSUE COMPLIANCE CERTIFICATES"),
  ("form","Written Quote & Contract (CPA)","Itemised, agreed before work starts","No work beyond the quote without client consent","CPA REQUIREMENT"),
  ("shield","Public Liability Insurance","Covers damage & injury on site","Provider arranges own cover","PROTECTS CLIENT & PROVIDER"),
  ("id","COIDA Registration","If the provider employs workers","Register with the Compensation Fund","LEGALLY REQUIRED FOR EMPLOYERS"),
  ("star","CPA Workmanship Warranty","Implied 6-month warranty on services & goods","Applies automatically — put it in writing anyway","AUTOMATIC UNDER CPA s56/57"),
 ],"Unregistered work on regulated trades can void insurance and CoCs.",
   "CIDB registration is required for public-sector construction work above thresholds."),
 "adventures_accommodation": ([
  ("house","Zoning / Land-Use Consent","Consent use for guesthouse or B&B","Host applies to the municipality","REQUIRED BY MUNICIPALITY"),
  ("flame","Health & Fire Safety Compliance","Occupancy certificate, fire equipment","Host arranges inspection & equipment","REQUIRED BY MUNICIPAL BYLAWS"),
  ("form","Guest Indemnity & House Rules","Signed at check-in","Host provides & keeps signed copies","PROTECTS HOST"),
  ("shield","Hospitality / Public Liability Insurance","Standard home policies usually exclude paying guests","Host arranges specific cover","PROTECTS HOST & GUESTS"),
  ("lock","POPIA-Compliant Guest Register","Guest ID details stored securely","Host keeps register, protects data","REQUIRED BY POPIA"),
  ("star","TGCSA Star Grading","Optional but boosts credibility & bookings","Host applies to the Tourism Grading Council","OPTIONAL — RECOMMENDED"),
 ],"Paying guests change your legal position — zoning, insurance and safety rules apply.",
   "Some municipalities require a specific accommodation licence — check local bylaws."),
 "adventures_experiences": ([
  ("id","Registered Tour Guide","Tourism Act — if guiding tourists","Guide registers with the provincial registrar","LEGALLY REQUIRED FOR GUIDING"),
  ("form","Risk Disclosure & Indemnity (CPA s49)","Written notice of risk for hazardous activities","Signed by participants before the activity","REQUIRED BY CPA FOR RISKY ACTIVITIES"),
  ("shield","Public Liability Insurance","Adequate cover for the activity","Operator arranges own cover","ESSENTIAL PROTECTION"),
  ("cross","First Aid Certification","Level appropriate to the activity","Operator / guide keeps certification current","INDUSTRY REQUIREMENT"),
  ("tree","Permits for Protected Areas","SANParks, CapeNature, landowner permission","Operator obtains per activity & area","REQUIRED PER ACTIVITY & AREA"),
 ],"Adventure operators carry real liability — waivers only work if done properly.",
   "Minors need indemnities signed by a parent or guardian."),
 "collectors": ([
  ("gem","Provenance & Authenticity","Certificates, receipts, grading reports","Seller provides documentation to buyer","PROTECTS VALUE & BUYER TRUST"),
  ("id","Second-Hand Goods Act Registration","If dealing / trading regularly","Dealer registers with SAPS","REQUIRED FOR DEALERS — NOT ONE-OFF SALES"),
  ("tree","Heritage & Wildlife Permits","NHRA export permits; CITES (ivory, horn, etc.)","Seller obtains before sale or export","LEGALLY REQUIRED — SEVERE PENALTIES"),
  ("form","Sales Agreement (Voetstoots)","Condition & authenticity documented","Both parties sign","PROTECTS SELLER"),
  ("cash","Traceable Payment","Avoid large cash transactions","Use bank transfer / platform payment","STRONGLY RECOMMENDED"),
 ],"Rare items attract rare rules — provenance and permits before price.",
   "One-off private sales are generally exempt from dealer registration."),
}

CONTENT["US"] = {
 "property": ([
  ("doc","Clear Title & Title Search","Title company confirms ownership & liens","Title company / closing attorney runs the search — buyer takes title insurance","REQUIRED FOR CLOSING"),
  ("form","Seller Disclosure Form","Property condition — required in most states","Seller completes honestly — known defects must be declared","STATE LAW REQUIREMENT"),
  ("house","Lead-Paint Disclosure","Federal law — homes built before 1978","Seller provides EPA pamphlet & disclosure; buyer gets a 10-day inspection window","FEDERAL REQUIREMENT"),
  ("bank","Mortgage Payoff & Lien Release","Cleared through escrow at closing","Seller requests payoff statement — escrow pays the lender from proceeds","CLEARED AT CLOSING"),
  ("id","Closing Agent or Attorney","Escrow states vs attorney-closing states","Seller engages per state practice — deed, transfer taxes, recording","REQUIRED — FORM VARIES BY STATE"),
 ],"A FSBO sale still closes through a title company or attorney — state rules differ.",
   "Requirements vary by state — disclosure forms, attorney involvement and transfer taxes are state-specific."),
 "cars": ([
  ("id","Certificate of Title","Sign over to buyer; lien must be released first","Seller signs & dates exactly as printed — errors delay the transfer","MANDATORY FOR SALE"),
  ("form","Bill of Sale","Required in many states, wise everywhere","Both parties sign — VIN, price, odometer, as-is terms","PROTECTS BOTH PARTIES"),
  ("car","Odometer Disclosure","Federal law — vehicles up to 20 model years","Seller declares exact mileage on the title or federal form","FEDERAL REQUIREMENT"),
  ("shield","Release of Liability","Time-critical — notice of transfer to the DMV","Seller files by the state deadline — ends liability for tickets & accidents","SELLER RESPONSIBILITY"),
  ("bolt","Smog / Safety Inspection","State-dependent (e.g. California smog check)","Seller or buyer obtains per state rules","VARIES BY STATE"),
 ],"Miss the release-of-liability deadline and the new owner's tickets are yours.",
   "Plates usually stay with the seller — check your state DMV."),
 "tutors": ([
  ("shield","Background Check","Expected for minors; mandatory for school programs","Tutor obtains state / FBI check as required","REQUIRED FOR SCHOOL-LINKED WORK"),
  ("form","Written Tutoring Agreement","Rates, cancellation, refunds","Both parties sign","PROTECTS BOTH PARTIES"),
  ("lock","Parental Consent & Student Data Care","Minors' records handled with consent","Parent / guardian consents in writing","BEST PRACTICE — STATE PRIVACY LAWS"),
  ("cash","Self-Employment Tax (IRS)","Schedule C; 1099-K may apply","Tutor reports income — quarterly estimates if needed","IRS REQUIREMENT"),
  ("star","Liability Insurance","Professional & general liability","Tutor arranges own cover","RECOMMENDED"),
 ],"Working with minors: checks and consent first — trust is the product.",
   "Rules are state-specific; school-district work has stricter requirements."),
 "services": ([
  ("bolt","State Contractor / Trade License","Electrical, plumbing, HVAC, general contracting","Provider licenses with the state board before quoting regulated work","LEGALLY REQUIRED — VARIES BY STATE"),
  ("form","Written Contract","Home-improvement contracts regulated in many states","Itemised scope & price, signed before work starts","STATE LAW / BEST PRACTICE"),
  ("shield","Liability Insurance & Bonding","Many states require proof for licensure","Provider arranges cover — bond where required","PROTECTS CLIENT & PROVIDER"),
  ("house","EPA RRP Lead-Safe Certification","Renovating homes built before 1978","Firm certifies & follows lead-safe practices","FEDERAL REQUIREMENT"),
  ("id","Workers' Comp (if employees)","State-mandated","Provider registers with the state fund / insurer","LEGALLY REQUIRED FOR EMPLOYERS"),
 ],"Unlicensed contracting is a crime in several states — and can void your right to payment.",
   "Licensing thresholds differ by state (e.g. California: jobs over $500 need a license)."),
 "adventures_accommodation": ([
  ("house","Short-Term Rental Permit","City / county registration — many require a permit number","Host registers with the local authority & displays the permit on listings","REQUIRED BY LOCAL LAW"),
  ("cash","Occupancy / Lodging Taxes","Transient occupancy tax","Host registers & remits — platforms sometimes collect","TAX REQUIREMENT"),
  ("flame","Safety Equipment","Smoke & CO detectors, extinguishers, exits","Host installs & maintains per code","REQUIRED BY CODE"),
  ("shield","STR / Liability Insurance","Homeowner policies usually exclude paying guests","Host arranges short-term-rental cover","PROTECTS HOST & GUESTS"),
  ("form","House Rules & Rental Agreement","Occupancy limits, quiet hours","Guest accepts before the stay","PROTECTS HOST"),
 ],"STR rules are hyper-local — cities ban, cap or license short-term rentals.",
   "Check HOA / lease terms too — many prohibit short-term letting."),
 "adventures_experiences": ([
  ("form","Liability Waiver","Enforceability varies by state","Participants sign before the activity — properly drafted, not a template","ESSENTIAL — STATE LAW VARIES"),
  ("shield","Commercial Liability Insurance","Adequate cover for the activity","Operator arranges own cover","ESSENTIAL PROTECTION"),
  ("tree","Public Lands Permits","Commercial Use Authorization (NPS / USFS / BLM)","Operator obtains before guiding on public land","FEDERAL / STATE REQUIREMENT"),
  ("id","Guide / Outfitter License","State-specific (fishing, hunting, rafting)","Guide licenses with the state agency","REQUIRED PER STATE & ACTIVITY"),
  ("cross","First Aid / CPR Certification","Level appropriate to the activity","Operator keeps certification current","INDUSTRY STANDARD"),
 ],"Waivers don't replace insurance — courts scrutinize both.",
   "Minors need parent / guardian-signed waivers."),
 "collectors": ([
  ("gem","Provenance & Authentication","Certificates, receipts, grading reports","Seller provides documentation to buyer","PROTECTS VALUE & BUYER TRUST"),
  ("tree","Wildlife & Cultural Property Laws","ESA / ivory, eagle feathers, Native American items","Seller confirms the item is legal to sell — permits where applicable","FEDERAL LAW — SEVERE PENALTIES"),
  ("form","Bill of Sale (As-Is)","Condition & authenticity documented","Both parties sign","PROTECTS SELLER"),
  ("cash","IRS Form 8300 — Cash Over $10,000","Trade or business receipts","Report within 15 days — better: traceable payment","IRS REQUIREMENT"),
  ("bank","Sales Tax Obligations","If selling regularly","Seller checks state nexus / marketplace rules","VARIES BY STATE"),
 ],"Rare items attract rare rules — check federal wildlife & heritage law before listing.",
   "One-off private sales are usually tax-simple; regular dealing isn't."),
}

CONTENT["UK"] = {
 "property": ([
  ("doc","Energy Performance Certificate (EPC)","Legally required before marketing; valid 10 years","Seller commissions an assessor — unless a valid EPC exists","LEGAL REQUIREMENT TO MARKET"),
  ("form","TA6 Property Information Form","6th edition compulsory from 30 March 2026","Seller completes fully & honestly — disputes, flooding, knotweed, alterations","REQUIRED — MISSTATEMENT = LIABILITY"),
  ("star","Upfront Material Information","Trading Standards — before viewings","Tenure, price, council tax band & known issues disclosed in the listing","REQUIRED IN LISTINGS"),
  ("bank","Title Deeds / Land Registry Copies","Proof of ownership","Conveyancing solicitor obtains official copies","REQUIRED FOR CONVEYANCING"),
  ("house","Building Regs & Warranty Certificates","FENSA, Gas Safe, electrical works","Seller gathers certificates & guarantees","BUYER'S SOLICITOR WILL ASK"),
  ("id","ID & Anti-Money-Laundering Checks","Proof of identity & address","Seller provides to solicitor","AML COMPLIANCE"),
 ],"A private sale still needs a conveyancing solicitor — and upfront information is now the law.",
   "England & Wales shown — Scotland requires a Home Report and uses a different process."),
 "cars": ([
  ("id","V5C Registration Certificate (Logbook)","Proves the registered keeper","Seller uses the V5C to transfer the vehicle — buyer gets the new-keeper slip","MANDATORY — DVLA"),
  ("form","Notify DVLA of Sale","Instant online — ends the seller's liability","Seller reports the transfer; remaining road tax is refunded automatically","SELLER RESPONSIBILITY"),
  ("car","MOT Certificate","Required if the car is over 3 years old","Buyer can verify MOT history free at gov.uk","LEGAL TO DRIVE = VALID MOT"),
  ("cash","Settle Outstanding Finance","A car can't legally be sold with finance owing","Seller settles first — buyer should run an HPI check","MANDATORY BEFORE SALE"),
  ("doc","Receipt & Service History","Private sale — “sold as seen”","Both parties sign a dated receipt; seller hands over history","PROTECTS BOTH PARTIES"),
 ],"Tell DVLA immediately — until then, speeding fines and tolls come to you.",
   "Buyer must tax the vehicle before driving away — road tax no longer transfers."),
 "tutors": ([
  ("shield","Enhanced DBS Check","Expected when tutoring children","Tutor obtains via an umbrella body — parents may ask to see it","EXPECTED FOR MINORS — REQUIRED FOR SCHOOLS"),
  ("form","Written Tutoring Agreement","Rates, cancellation, refunds","Both parties sign — Consumer Rights Act applies","PROTECTS BOTH PARTIES"),
  ("lock","UK GDPR — Pupil Data","Consent & secure records","Parent / guardian consents for minors' data","REQUIRED BY UK GDPR"),
  ("cash","Register with HMRC","Self-assessment for tutoring income","Tutor registers & declares income","HMRC REQUIREMENT"),
  ("star","Public Liability / Professional Indemnity","Especially for in-person tuition","Tutor arranges own cover","RECOMMENDED"),
 ],"Safeguarding first — a current DBS is the baseline parents expect.",
   "Self-employed tutors can't apply for their own enhanced DBS directly — use an umbrella body."),
 "services": ([
  ("bolt","Gas Safe / Part P Registration","Gas work legally requires Gas Safe; electrics fall under Part P","Provider registers before doing regulated work","LEGALLY REQUIRED"),
  ("form","Written Quote & Contract","Consumer Rights Act 2015 — reasonable care & skill","Itemised quote agreed before work starts","CONSUMER LAW REQUIREMENT"),
  ("doc","14-Day Cooling-Off Notice","Contracts agreed in the customer's home","Provider gives cancellation rights notice — or can't enforce payment","CONSUMER CONTRACTS REGS"),
  ("shield","Public Liability Insurance","Covers damage & injury","Provider arranges own cover","PROTECTS CLIENT & PROVIDER"),
  ("id","CIS Registration (Construction)","Subcontracting in construction","Provider registers with HMRC","REQUIRED FOR SUBCONTRACTORS"),
 ],"Illegal gas work is a criminal offence — registration isn't optional.",
   "Notifiable building work needs certificates the homeowner will be asked for at resale."),
 "adventures_accommodation": ([
  ("house","Planning Permission / Change of Use","Guesthouse or B&B may need consent; London: 90-night rule","Host checks with the local council","REQUIRED BY COUNCIL"),
  ("flame","Fire Risk Assessment","Fire Safety Order 2005 applies to paying guests","Host completes & documents — alarms, extinguishers, escape routes","LEGAL REQUIREMENT"),
  ("bolt","Annual Gas Safety Certificate","If guests use gas appliances","Gas Safe engineer inspects yearly","LEGAL REQUIREMENT"),
  ("shield","Public Liability Insurance","Home policies exclude paying guests","Host arranges guest-house / STR cover","PROTECTS HOST & GUESTS"),
  ("lock","UK GDPR Guest Records","ID details stored securely","Host keeps a register & protects data","REQUIRED BY UK GDPR"),
 ],"Paying guests trigger fire law — the risk assessment is where inspections start.",
   "Some councils require registration or licensing of short lets — check locally."),
 "adventures_experiences": ([
  ("id","AALA Licence","Adventure activities for under-18s (climbing, caving, trekking, watersports)","Operator licenses before taking young people","LEGALLY REQUIRED FOR UNDER-18s"),
  ("form","Risk Assessment & Waivers","HSE duty of care — waivers can't exclude injury liability","Operator documents risks; participants acknowledge them","HSE REQUIREMENT"),
  ("shield","Public Liability Insurance","Adequate for the activity","Operator arranges own cover","ESSENTIAL PROTECTION"),
  ("cross","First Aid Certification","Appropriate to activity & remoteness","Guides keep certification current","INDUSTRY REQUIREMENT"),
  ("tree","Landowner / Access Permissions","National parks, private estates","Operator obtains permission per venue","REQUIRED PER VENUE"),
 ],"UK law won't let a waiver excuse negligence causing injury — run the activity safely.",
   "AALA licensing applies in Britain for listed activities with under-18s."),
 "collectors": ([
  ("gem","Provenance & Authentication","Certificates, receipts, grading reports","Seller provides documentation to buyer","PROTECTS VALUE & BUYER TRUST"),
  ("tree","UK Ivory Act & CITES","Near-total ivory ban; permits for listed species","Seller checks legality / registers an exemption before listing","CRIMINAL OFFENCE IF BREACHED"),
  ("doc","Export Licences (Cultural Goods)","Arts Council licence for older / valuable items leaving the UK","Seller applies before export","REQUIRED FOR EXPORT"),
  ("form","Receipt / Sale Agreement (Sold As Seen)","Condition & authenticity documented","Both parties sign","PROTECTS SELLER"),
  ("cash","Traceable Payment","Avoid large cash deals","Bank transfer / platform payment","STRONGLY RECOMMENDED"),
 ],"Rare items attract rare rules — ivory and cultural exports are criminal-law territory.",
   "Art-market dealers over €10,000 must register with HMRC for AML — private one-offs generally exempt."),
}

CONTENT["AU"] = {
 "property": ([
  ("form","Contract of Sale + Vendor Disclosure","VIC: Section 32; NSW: contract required before marketing","Solicitor / conveyancer prepares BEFORE the property is listed","LEGALLY REQUIRED TO MARKET"),
  ("cash","ATO Clearance Certificate","All sellers, every price level (since Jan 2025)","Seller applies early (up to 28 days) — without it the buyer withholds 15% at settlement","REQUIRED — 15% WITHHELD WITHOUT IT"),
  ("bank","Title Search & Mortgage Discharge","Conveyancer obtains title; lender notified","Seller instructs discharge of mortgage","REQUIRED FOR SETTLEMENT"),
  ("house","Compliance Certificates","Pool safety (QLD / NSW), smoke alarms","Seller obtains state-required certificates","STATE REQUIREMENT"),
  ("id","Verification of Identity (VOI)","100-point identity check","Seller verifies with the conveyancer / Australia Post","REQUIRED FOR TRANSFER"),
 ],"In most states the contract must exist before you market — in Australia, paperwork comes first.",
   "Rules vary by state — vendor statements, pool and smoke-alarm certificates are state-specific."),
 "cars": ([
  ("car","Roadworthy / Safety Certificate","VIC: RWC. QLD: safety certificate. NSW: tied to rego (pink slip)","Seller obtains from a licensed tester before sale — state-dependent","REQUIRED IN MOST STATES"),
  ("form","Transfer of Registration","Lodged with the state transport authority","Buyer & seller complete the transfer — usually within 14 days","STATE REQUIREMENT"),
  ("shield","Notice of Disposal","Ends the seller's liability for tolls & fines","Seller lodges immediately after the sale","SELLER RESPONSIBILITY"),
  ("cash","PPSR Check & Finance Payout","No selling with money owing","Seller clears finance — buyer checks the PPSR ($2 online)","MANDATORY BEFORE SALE"),
  ("doc","Receipt / Contract of Sale","Price, date, odometer, both parties","Both parties sign","PROTECTS BOTH PARTIES"),
 ],"Lodge the notice of disposal the same day — until then, tolls and fines are yours.",
   "Each state's transport authority (Service NSW, VicRoads, TMR…) has its own forms."),
 "tutors": ([
  ("shield","Working With Children Check (WWCC)","Legally required in every state when tutoring minors","Tutor applies to the state screening body — number shown to parents","LEGALLY REQUIRED — HEAVY PENALTIES"),
  ("form","Written Tutoring Agreement","Rates, cancellation, refunds — ACL applies","Both parties sign","PROTECTS BOTH PARTIES"),
  ("cash","ABN & Income Declaration","ATO — sole trader","Tutor registers an ABN & declares income","ATO REQUIREMENT"),
  ("lock","Consent for Student Records","Minors' data handled with guardian consent","Parent / guardian consents in writing","PRIVACY BEST PRACTICE"),
  ("star","Public Liability Insurance","For in-person tuition","Tutor arranges own cover","RECOMMENDED"),
 ],"No WWCC, no tutoring minors — it's that simple in Australia.",
   "WWCC names differ by state (Blue Card in QLD; WWC Check in NSW / VIC…)."),
 "services": ([
  ("bolt","Trade Licence","Electrical & plumbing licensed in every state; building thresholds apply (e.g. QBCC over $3,300)","Provider licenses with the state regulator","LEGALLY REQUIRED"),
  ("form","Written Quote & Contract","Australian Consumer Law guarantees apply","Itemised quote agreed before work starts","ACL REQUIREMENT"),
  ("doc","Compliance Certificates","Electrical / plumbing certificates after regulated work","Provider issues to the homeowner","REQUIRED AFTER REGULATED WORK"),
  ("shield","Public Liability Insurance","Often required for licensing","Provider arranges own cover","PROTECTS CLIENT & PROVIDER"),
  ("id","Workers' Comp (if employees)","State schemes","Provider registers","LEGALLY REQUIRED FOR EMPLOYERS"),
 ],"Unlicensed electrical work is illegal Australia-wide — including DIY.",
   "Home-building contracts above state thresholds carry extra mandatory terms."),
 "adventures_accommodation": ([
  ("house","Council Approval / STRA Registration","NSW: STRA register & night caps; other states vary","Host registers with the council / state scheme","REQUIRED BY STATE / COUNCIL"),
  ("flame","Fire Safety Compliance","Interconnected smoke alarms, evacuation plan","Host installs & maintains per state code","LEGAL REQUIREMENT"),
  ("shield","Public Liability / STR Insurance","Home policies exclude paying guests","Host arranges specific cover","PROTECTS HOST & GUESTS"),
  ("form","House Rules & Guest Agreement","Strata by-laws may restrict letting","Guest accepts before the stay — host checks strata first","PROTECTS HOST"),
  ("cash","Declare Rental Income (ATO)","GST considerations may apply","Host declares income","ATO REQUIREMENT"),
 ],"Strata and councils can both say no — check before you list.",
   "NSW STRA caps nights in Greater Sydney; QLD and VIC rules differ."),
 "adventures_experiences": ([
  ("form","Recreational-Activity Waiver","ACL s139A — liability for recreational services can be limited, if worded correctly","Participants sign a compliant waiver before the activity","MUST BE DRAFTED CORRECTLY"),
  ("shield","Public Liability Insurance","Adequate for the activity","Operator arranges own cover","ESSENTIAL PROTECTION"),
  ("tree","Parks / Commercial Operator Licence","National-park commercial activity permits","Operator obtains per park & state","REQUIRED PER ACTIVITY & AREA"),
  ("cross","First Aid Certification","Appropriate to activity & remoteness","Guides keep certification current","INDUSTRY REQUIREMENT"),
  ("star","Australian Adventure Activity Standard","Good-practice framework (AAAS)","Operator aligns operations","INDUSTRY STANDARD"),
 ],"The ACL protects consumers even in adventure sports — a bad waiver is no waiver.",
   "Minors need parent / guardian-signed waivers."),
 "collectors": ([
  ("gem","Provenance & Authentication","Certificates, receipts, grading reports","Seller provides documentation to buyer","PROTECTS VALUE & BUYER TRUST"),
  ("tree","Cultural Heritage & Wildlife Permits","PMCH Act export permits; EPBC / CITES species","Seller obtains before sale or export","LEGALLY REQUIRED — SEVERE PENALTIES"),
  ("id","Second-Hand Dealer Licence","If trading regularly (state laws)","Dealer registers with the state","REQUIRED FOR DEALERS"),
  ("form","Sale Agreement (As-Is)","Condition & authenticity documented","Both parties sign","PROTECTS SELLER"),
  ("cash","AUSTRAC — Cash Over $10,000","Reporting threshold","Use traceable payment instead","STRONGLY RECOMMENDED"),
 ],"Rare items attract rare rules — export permits before price.",
   "One-off private sales are generally exempt from dealer licensing."),
}

def build(cc, cat):
    a, tint, chipbg, catlabel = STYLE[cat]
    rows, foot, note = CONTENT[cc][cat]
    title = TITLES[cat]; cname = COUNTRY_NAMES[cc]
    parts=[]; y=0
    parts.append(f'<rect x="0" y="0" width="{W}" height="86" fill="{NAVY}"/>')
    parts.append(f'<text x="40" y="34" font-family="DejaVu Sans" font-size="15" font-weight="bold" fill="#9fb3d9" letter-spacing="2">ABSOLUTE MUST-HAVES · PRIVATE SALES · {cname}</text>')
    parts.append(f'<text x="40" y="66" font-family="DejaVu Sans" font-size="27" font-weight="bold" fill="#ffffff">{E(title)}</text>')
    parts.append(f'<rect x="{W-116}" y="24" width="76" height="38" rx="8" fill="#ffffff" opacity="0.14"/><text x="{W-78}" y="50" font-family="DejaVu Sans" font-size="20" font-weight="bold" fill="#ffffff" text-anchor="middle">{cc}</text>')
    parts.append(f'<rect x="0" y="86" width="{W}" height="46" fill="{a}"/>')
    parts.append(f'<text x="40" y="117" font-family="DejaVu Sans" font-size="19" font-weight="bold" fill="#ffffff" letter-spacing="1.5">{E(catlabel)}</text>')
    y = 132
    for i,(ic,ttl,sub,action,chip) in enumerate(rows):
        tl = wrap(ttl, 29); sl = wrap(sub, 44); al = wrap(action, 40); cl = wrap(chip, 24)
        h = max(96, 30 + max(len(tl)*22+len(sl)*17, len(al)*19, len(cl)*17) + 18)
        bg = "#ffffff" if i%2==0 else tint
        parts.append(f'<rect x="0" y="{y}" width="{W}" height="{h}" fill="{bg}"/>')
        cy = y + h/2
        parts.append(f'<circle cx="72" cy="{cy:.0f}" r="27" fill="{a}"/><g transform="translate(72,{cy:.0f})">{icon(ic,a)}</g>')
        ty = cy - (len(tl)*22+len(sl)*17)/2 + 17
        for ln in tl:
            parts.append(f'<text x="118" y="{ty:.0f}" font-family="DejaVu Sans" font-size="17" font-weight="bold" fill="#1a1a2e">{E(ln)}</text>'); ty+=22
        for ln in sl:
            parts.append(f'<text x="118" y="{ty:.0f}" font-family="DejaVu Sans" font-size="12.5" fill="#6b7280">{E(ln)}</text>'); ty+=17
        parts.append(f'<path d="M 448,{cy:.0f} h 26 m -8,-7 l 8,7 l -8,7" stroke="{a}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
        ay = cy - (len(al)*19)/2 + 14
        for ln in al:
            parts.append(f'<text x="492" y="{ay:.0f}" font-family="DejaVu Sans" font-size="14" font-weight="bold" fill="#2d3348">{E(ln)}</text>'); ay+=19
        ch = len(cl)*17+20
        parts.append(f'<rect x="838" y="{cy-ch/2:.0f}" width="212" height="{ch}" rx="6" fill="{chipbg}"/>')
        qy = cy - ch/2 + 24
        for ln in cl:
            parts.append(f'<text x="944" y="{qy-4:.0f}" font-family="DejaVu Sans" font-size="12" font-weight="bold" fill="#2d3348" text-anchor="middle">{E(ln)}</text>'); qy+=17
        y += h
        parts.append(f'<rect x="0" y="{y-1}" width="{W}" height="1" fill="#d8dbe4"/>')
    y += 14
    parts.append(f'<text x="{W/2}" y="{y+18}" font-family="DejaVu Sans" font-size="15.5" font-weight="bold" fill="{a}" text-anchor="middle">Accredited agencies on MarketSquare manage what they may, and facilitate the rest with the right professionals.</text>')
    y += 34
    fl = wrap(foot, 88); ph = len(fl)*21+22
    parts.append(f'<rect x="90" y="{y}" width="{W-180}" height="{ph}" rx="10" fill="{NAVY}"/>')
    fy = y+27
    for ln in fl:
        parts.append(f'<text x="{W/2}" y="{fy}" font-family="DejaVu Sans" font-size="14.5" font-weight="bold" fill="#ffffff" text-anchor="middle">{E(ln)}</text>'); fy+=21
    y += ph + 12
    parts.append(f'<text x="40" y="{y+14}" font-family="DejaVu Sans" font-size="11.5" fill="#6b7280">{E(note)}</text>')
    parts.append(f'<text x="{W-40}" y="{y+14}" font-family="DejaVu Sans" font-size="11.5" fill="#9aa1ad" text-anchor="end">General guidance for {FOOT_NOTE_R[cc]} — not legal advice.</text>')
    y += 34
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{y}" viewBox="0 0 {W} {y}"><rect width="{W}" height="{y}" fill="#ffffff"/>' + "".join(parts) + '</svg>'

if __name__ == "__main__":
    import cairosvg
    want = sys.argv[1].upper() if len(sys.argv)>1 else "ALL"
    ccs = list(CONTENT) if want=="ALL" else [want]
    for cc in ccs:
        outdir = os.path.join(BASE, cc); os.makedirs(outdir, exist_ok=True)
        for cat in CONTENT[cc]:
            svg = build(cc, cat)
            open(os.path.join(outdir, f"must-haves-{cc}-{cat}.svg"),"w",encoding="utf-8").write(svg)
            cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(outdir, f"must-haves-{cc}-{cat}.png"), output_width=W*2)
            print(cc, cat, "ok")
