# -*- coding: utf-8 -*-
"""The two EXAMPLE dossiers (SAW-3, RUL-044). Facts verified 23 Aug 2026; volatile
figures carry (RE-CHECK). FX indicative 23 Aug 2026: EUR~R20.5, USD~R18.2, HUF~R0.053."""
RC = ' <font color="#C55A11"><b>(RE-CHECK)</b></font>'

HUNGARY = {
 "cover_title": ["Study in Hungary,", "fully funded."],
 "cover_sub": "The Stipendium Hungaricum route - example dossier",
 "cover_contents": [
   "Your question, answered straight - and the five routes graded",
   "The route at a glance - application to arrival",
   "What the scholarship gives you - and what it does not",
   "The plan, month by month, to the September 2027 intake",
   "The money, honestly - year-1 family totals, city by city",
   "Risks stated plainly - and the opportunities beyond the degree",
   "Your next three actions, and the agency handoff",
 ],
 "cover_lines": [
   'Prepared for: "Lerato", 18 - Pretoria East   |   Route: STUDY - BSc Computer Science',
   "Profile: matric average 78% (Maths 82%)  |  Family budget R150,000/year  |  Target intake: September 2027",
   "Verdict: HIGH viability - the strongest fully funded route open to this profile.",
   "Facts verified 23 August 2026. Rand figures use an indicative rate of that date.",
 ],
 "sections": [
  ("h1","1 - Your question, answered straight"),
  ("p","You asked: <b>can I study Computer Science abroad on a R150,000/year family budget?</b> "
      "Yes - one route stands clearly above the rest. Hungary's government scholarship, "
      "<b>Stipendium Hungaricum</b>, reserves <b>up to 100 full scholarships a year for South "
      "Africans</b>, channelled through our own Department of Higher Education and Training "
      "(DHET). It covers your full tuition, housing (dorm or a contribution), medical insurance "
      "and a monthly stipend. Your 78% average clears the 60% bar comfortably. The catch is a "
      "hard January deadline - this dossier plans you to the <b>September 2027 intake</b>."),
  ("chips",[("Hungary - Stipendium","HIGH"),("SA + EU exchange","HIGH"),("Germany EUR 0 tuition","MEDIUM"),("Netherlands","LOW"),("United Kingdom","LOW")]),
  ("small","The five routes from your options session, for the record. This dossier deep-dives the winner; "
      "Germany (no tuition, but R245k/yr living proof) and the SA-base-plus-exchange sequence remain solid fallbacks."),
  ("h1","2 - The route at a glance"),
  ("route",[{"name":"Pretoria","sub":"documents + portal","v":"HIGH"},
            {"name":"Application","sub":"Nov 2026 - Jan 2027","v":"HIGH"},
            {"name":"Exams online","sub":"Feb - Apr 2027","v":"HIGH"},
            {"name":"Award + visa","sub":"May - Jul 2027","v":"HIGH"},
            {"name":"Budapest / Debrecen","sub":"arrive Sep 2027","v":"HIGH"}]),
  ("photos",[("sw_hu_1_airport.jpg","OR Tambo - where it starts"),("sw_hu_2_aerial.jpg","Wheels down over the Danube"),("sw_hu_3_arrival.jpg","First morning on campus")]),
  ("h2","What the scholarship actually gives you"),
  ("table",["Item","What you get","Detail"],
   [["Tuition","<b>100% covered</b>","Full exemption for the whole degree, not one year"+RC],
    ["Housing","Free dormitory place OR HUF 40,000/month (~R2,100)","The contribution does NOT cover a Budapest flat - dorms or a regional city are the smart play"+RC],
    ["Stipend","HUF 43,700/month (~R2,300), 12 months/yr","A contribution to living costs, not a full ride - see the money page"+RC],
    ["Medical","Hungarian state health insurance","Per Hungarian law for scholarship holders"],
    ["Language","Degree taught in English","Daily life is Hungarian - free courses usually offered"+RC]],
   [70,150,None]),
  ("h2","Universities to shortlist for Computer Science"),
  ("p","Strong Stipendium-participating candidates"+RC+": <b>Obuda University</b> (Budapest - applied "
      "computing, strong international cohort) - <b>ELTE</b> (Budapest - top theoretical CS faculty) - "
      "<b>BME</b> (Budapest - the technical university) - <b>University of Debrecen</b> and "
      "<b>University of Szeged</b> (excellent CS, far cheaper cities, dorms easier). You may list two "
      "programme choices"+RC+" - our recommendation: one Budapest option plus one regional option. That "
      "one decision is worth thousands of rand a month."),
  ("pagebreak",0),
  ("h1","3 - The plan, month by month"),
  ("table",["When","What you do","Watch"],
   [["Sep-Oct 2026","Passport application (if none). Certified matric certificate + results. Two reference letters. Draft motivation letter. Shortlist your 2 programmes.","Apostille and certification queues eat weeks - start here"],
    ["Nov 2026","Stipendium application portal opens"+RC+". Create your account. Register on DHET's international scholarships portal and follow the SA-specific instructions.","You apply BOTH sides: Tempus portal + DHET nomination"],
    ["Dec 2026 - 10 Jan 2027","Submit everything - aim two weeks BEFORE the ~15 Jan deadline"+RC+". Medical certificate. English-proficiency proof per your universities' rules"+RC+".","The deadline is annual and hard. Miss it, wait a year"],
    ["Feb - Apr 2027","University entrance exams / interviews, online. CS usually tests maths + logic.","Practice papers exist on university sites"],
    ["May - Jun 2027","Results and award letters.","If waitlisted, regional choices clear faster"],
    ["Jul 2027","Student visa / residence permit at the Hungarian mission (Pretoria). Book flights. Confirm dorm or plan the HUF 40,000 contribution route.","Visa needs the award letter - it moves quickly after that"+RC],
    ["Aug - Sep 2027","Fly. Register at university. Finalise residence permit in-country within the set window"+RC+".","Arrive a week early; orientation matters"]],
   [78,None,120]),
  ("h1","4 - The money, honestly"),
  ("p","Indicative FX 23 Aug 2026: HUF 1 ~ R0.053, EUR 1 ~ R20.50. The live feature quotes live rates."),
  ("table",["Item","Amount","Who pays"],
   [["Tuition, whole degree","R0","<b>Scholarship</b>"],
    ["Housing","R0 (dorm) or ~R2,100/mo contribution","<b>Scholarship</b>"],
    ["Stipend to you","~R2,300/month","<b>Scholarship</b>"],
    ["Flights JNB-Budapest, return","R13,000 - 17,000"+RC,"Family, once a year"],
    ["Visa / residence permit + admin","R2,000 - 4,000"+RC,"Family, year 1"],
    ["Setup (bedding, sim, deposit, winter clothes)","R8,000 - 12,000","Family, year 1"],
    ["Monthly top-up - Budapest","HUF 80-120k = R4,200 - 6,400/mo"+RC,"Family"],
    ["Monthly top-up - Debrecen/Szeged","HUF 40-80k = R2,100 - 4,200/mo"+RC,"Family"],
    ["<b>Year-1 family total - Budapest</b>","<b>~ R75,000 - 95,000</b>",""],
    ["<b>Year-1 family total - regional city</b>","<b>~ R50,000 - 70,000</b>",""]],
   [150,150,None]),
  ("callout","Your R150,000/year budget covers this route with real headroom - in a regional city, roughly half the budget stays home. The scholarship runs the length of the degree, so year 2 and 3 look like year 1 without the setup costs.",("#E7F2E3","#538135"),"THE BOTTOM LINE"),
  ("pagebreak",0),
  ("h1","5 - Risks, stated plainly"),
  ("table",["Risk","Grade","What you do about it"],
   [["The January deadline is annual and absolute","HIGH","This plan starts your paperwork in September - two months of slack built in"],
    ["Competition: up to 100 awards nationally","MEDIUM","78% average + a sharp motivation letter + a regional second choice maximises odds"],
    ["Stipend does not cover full living costs","MEDIUM","The money page is built on that truth - budget the top-up, prefer the dorm"],
    ["Budapest rents if no dorm place","MEDIUM","Regional second choice; accept dorm if offered"],
    ["Hungarian in daily life","LOW","Degree is English; universities offer Hungarian courses; young cohort is English-friendly"],
    ["Rules shift year to year","MEDIUM","Every flagged figure gets re-checked at the official source before you submit - your adviser does exactly that"],
    ["Homesickness, winters","LOW","12 months of stipend means summers can come home; strong SA student community in Hungary"]],
   [190,55,None]),
  ("h2","The surroundings"),
  ("photos",[("sw_hu_4_campus.jpg","The campus courtyard"),("sw_hu_5_city.jpg","Parliament across the water - the free evening"),("sw_hu_6_life.jpg","Great Market Hall - groceries at student prices")]),
  ("mapshot","sw_hu_mapshot.jpg","The surroundings, mapped - the interactive layered version (journey / campuses / student life / smart alternatives) lives in the app."),
  ("h1","6 - Opportunities beyond the degree"),
  ("p","- <b>Zero tuition debt</b> - you graduate owing nothing.<br/>"
      "- <b>EU mobility:</b> as an enrolled EU-university student, Erasmus+ exchange semesters across Europe open up.<br/>"
      "- <b>Budapest tech scene:</b> real CS internships within tram distance.<br/>"
      "- <b>The degree travels:</b> EU-accredited BSc - masters doors across Europe, or come home with scarce skills.<br/>"
      "- <b>The UK, revisited:</b> the route your options session graded LOW at undergrad turns realistic at masters level, with scholarships."),
  ("h1","7 - Your next three actions"),
  ("p","<b>1.</b> Start the passport and certified-copies pile this month - it is the slowest, dumbest bottleneck.<br/>"
      "<b>2.</b> Shortlist two programmes (one Budapest, one regional) from the current Stipendium list"+RC+".<br/>"
      "<b>3.</b> Take this dossier to a registered education consultant who knows the DHET/Stipendium lane - "
      "MarketSquare introduces you to one, and that introduction is part of what your 5 Tuppence bought."),
  ("callout","MarketSquare never replaces education professionals - and says so. This dossier is preparation: what is possible, what it takes, what to expect. Your consultant turns it into your application, your submissions, your plan. We prepare you; they plan with you. MarketSquare never touches tuition, visa fees or bookings.",("#EAF0FA","#2F5496"),"THE HANDOFF"),
  ("h1","8 - Sources and dates"),
  ("small","All checked 23 Aug 2026. DHET international scholarships portal (Stipendium Hungaricum for South Africa - up to 100 awards, 60% minimum, 15 Jan 2026 deadline for the 2026 cycle; next cycle expected to open late 2026) - stipendiumhungaricum.hu (programme scope, coverage; provisions: tuition exemption, dorm or HUF 40,000/mo, stipend HUF 43,700/mo bachelor, medical insurance) - university admission pages (entrance exams, English proof) - flight fares: current market quotes. Items marked RE-CHECK change annually or seasonally and MUST be confirmed at the official source before submission. Indicative FX of 23 Aug 2026 throughout."),
 ],
}

USA_FARM = {
 "cover_title": ["Work an American farm,", "with your degree working too."],
 "cover_sub": "The USA agricultural work route - example dossier",
 "cover_contents": [
   "Your question, answered straight - two real doors, one closing",
   "Door one: J-1 Agricultural Intern - the 12-month graduation window",
   "Door two: H-2A seasonal - no cap, housing provided, repeatable",
   "The plan, month by month - documents, consulate, host farm",
   "The money, honestly - launch costs, earnings, taxes, the Scam Wall",
   "The pathway you have heard about - handled honestly",
   "Risks, opportunities, your next three actions, the agency handoff",
 ],
 "cover_lines": [
   'Prepared for: "Pieter", 23 - Bothaville, Free State   |   Route: WORK - agriculture, USA',
   "Profile: BSc Agric, graduated this year  |  Code EB licence, combine + planter hours  |  Goal: 1-2 seasons, earn and learn",
   "Verdict: HIGH viability - two real doors, and one of them is closing in months. Move now.",
   "Facts verified 23 August 2026. Rand figures use an indicative rate of that date.",
 ],
 "sections": [
  ("h1","1 - Your question, answered straight"),
  ("p","You asked: <b>can a young South African agri graduate go work on an American farm?</b> "
      "Yes - and South Africans are actively sought after: thousands go every season, prized for "
      "combine and heavy-machinery experience exactly like yours. There are two real doors. "
      "<b>Door one, urgent:</b> the J-1 Agricultural Intern visa takes graduates <b>within 12 months of "
      "graduation</b> - your window is open NOW and closes around this time next year. "
      "<b>Door two, repeatable:</b> the H-2A seasonal agricultural visa - no annual cap, employer-"
      "petitioned, housing provided, and the lane where SA machine operators earn the numbers that "
      "make the news. This dossier runs both in parallel, J-1 first."),
  ("chips",[("J-1 Agri Intern","HIGH"),("H-2A seasonal","HIGH"),("H-2B non-agri","MEDIUM"),("Canada agri (LMIA)","MEDIUM"),("Refugee pathway","SEE PANEL")]),
  ("h1","2 - The route at a glance"),
  ("route",[{"name":"Free State","sub":"documents + CV","v":"HIGH"},
            {"name":"Provider + host farm","sub":"matching, 2-4 months","v":"HIGH"},
            {"name":"Consulate JHB","sub":"DS-2019, interview","v":"HIGH"},
            {"name":"Host farm, USA","sub":"12 months J-1","v":"HIGH"},
            {"name":"Season 2 option","sub":"H-2A, no cap","v":"MEDIUM"}]),
  ("photos",[("sw_us_1_airport.jpg","OR Tambo - duffel and work gloves"),("sw_us_2_aerial.jpg","The Midwest quilt from seat 34A"),("sw_us_3_arrival.jpg","The host farm gate")]),
  ("h2","Door one - J-1 Agricultural Intern (start this month)"),
  ("table",["Fact","Detail"],
   [["Who qualifies","Enrolled students OR graduates within 12 months of programme start - <b>your BSc Agric qualifies you today, and stops qualifying you next year</b>"],
    ["Length","12 months on a structured training plan (DS-7002) with a host farm; Trainee visa (18 months) becomes possible later with work experience"],
    ["Pay","Paid placement or stipend, typically with housing - varies by host"+RC],
    ["Who runs it","US State-Department-designated sponsors, reached through SA providers - OVC and Epic Exchange are established examples (references, not endorsements)"],
    ["Launch cost","~R30,000 - 50,000 all-in (programme, SEVIS, visa, flights), much of it recovered from pay"+RC]],
   [120,None]),
  ("h2","Door two - H-2A seasonal agricultural work"),
  ("table",["Fact","Detail"],
   [["The big one","<b>No annual cap</b> - unlike H-2B, H-2A never 'runs out'. The employer petitions for YOU"],
    ["Wages","AEWR wage floor, state-based; system moved to a two-tier BLS-based structure in Oct 2025"+RC+". SA operators' earnings of ~R62,700/month have been reported in SA media - treat as indicative, read YOUR contract"],
    ["Housing","Provided by the employer at no cost - a programme requirement. Inbound/outbound transport reimbursed per the rules"],
    ["Season","6-10 month contracts; planting and harvest windows. Repeatable year after year"],
    ["Launch cost","Modest: visa fee + medicals + police clearance; the employer carries the petition"+RC]],
   [120,None]),
  ("pagebreak",0),
  ("h1","3 - The plan, month by month"),
  ("table",["When","What you do","Watch"],
   [["Month 0 (now)","Pick the J-1 provider; start host-farm matching (2-4 months typical). In parallel, register with H-2A-experienced SA recruiters.","The 12-month graduation window is burning - this is the step that cannot wait"],
    ["Month 1","US-format CV (machinery hours, GPS/precision-ag, certificates). Reference letters from every farm you have worked. Passport valid 18+ months.","US CVs lead with equipment hours - be specific: brands, models, seasons"],
    ["Month 1-2","Police clearance (SAPS) + apostille. Medicals. Certified degree + transcripts.","SAPS clearance + apostille can take 6-10 weeks - start month 1"+RC],
    ["Month 2-3","Host farm matched; DS-7002 training plan signed; sponsor issues DS-2019. Pay SEVIS fee. DS-160 form.","Read the training plan - it is your contract for the year"],
    ["Month 3-4","Visa interview, US Consulate Johannesburg. Bring proof of home ties: family farm links, return plans, the degree.","Weak 'return intent' is the #1 refusal reason for young single applicants"],
    ["Month 4-5","Fly. Arrive at the host farm. US bank account, SSN application, state ID.","Keep every payslip - you will file a US tax return and often get money back"],
    ["Months 5-16","The year: work the seasons, log everything you learn, bank the surplus.","Mid-year: decide season 2 - H-2A with your new US references"],
    ["Month 12+","Option A: home with capital + US experience. Option B: H-2A next season (employer petitions from SA). Option C: J-1 Trainee (18 months) later in your career.","Never overstay - one clean record keeps every future door open"]],
   [70,None,125]),
  ("h1","4 - The money, honestly"),
  ("p","Indicative FX 23 Aug 2026: USD 1 ~ R18.20. The live feature quotes live rates."),
  ("table",["Item","Amount","Note"],
   [["J-1 launch: programme + SEVIS + visa + flights","R30,000 - 50,000"+RC,"Provider-dependent; instalments common"],
    ["H-2A launch (if that door goes first)","~R8,000 - 15,000"+RC,"Visa fee, medicals, clearance; employer carries petition + housing + transport"],
    ["J-1 income","varies by host; placements typically paid with housing"+RC,"Confirm in the DS-7002 before signing"],
    ["H-2A income","AEWR floor by state"+RC+"; reported SA operator averages ~R62,700/mo","Free housing makes the savings rate the real story"],
    ["US taxes","File a return; treaty refunds common","Budget a tax-filing service ~R1,500"],
    ["<b>Realistic year-1 outcome (J-1, paid host)</b>","<b>Launch cost recovered + meaningful savings + a US year on the CV</b>",""]],
   [170,150,None]),
  ("callout","Nobody can sell you an H-2A or J-1 visa. The employer petitions (H-2A) or the designated sponsor issues the DS-2019 (J-1). A recruiter demanding thousands upfront for 'guaranteed visas' is a scam - legitimate players are paid by employers or charge published programme fees with contracts. Check any US recruiter against the state's licensing and the sponsor against the State Department's designated list.",("#FFF4E5","#C55A11"),"THE SCAM WALL"),
  ("pagebreak",0),
  ("h1","5 - The pathway you have heard about - handled honestly"),
  ("callout","There is a US refugee resettlement pathway for Afrikaners (opened Feb 2025; the FY2026 refugee ceiling of 7,500 was primarily allocated to South Africans, later expanded; over 7,700 admitted by mid-2026, resettled mainly in Texas, Florida and California). <b>This dossier does not grade it as a work route, because it is not one.</b> It is permanent refugee resettlement: a claim of persecution, decided by US authorities, for a family emigrating for good - not a visa for a season of farm work with a return ticket. It is politically contested, legally challenged, and could change abruptly with no notice. If permanent emigration is truly the question on your family's table, that is a different decision for a different table - taken with a registered US immigration attorney, not with a gap-year plan. <b>Your stated goal - work an American farm, learn, earn, come home stronger - is fully served by the two visas in this dossier.</b>",("#F4F4F5","#595959"),"ADJACENT PATHWAY - NOT A WORK ROUTE"),
  ("h1","6 - Risks, stated plainly"),
  ("table",["Risk","Grade","What you do about it"],
   [["The J-1 12-month graduation window closes","HIGH","Provider contact THIS MONTH - it is the one deadline nothing else can fix"],
    ["Visa refusal on weak home ties","MEDIUM","Documented return intent: family farm involvement, the H-2A repeat plan, no burnt bridges"],
    ["Wage/hours disputes (documented in this lane)","MEDIUM","Know your AEWR rate, keep timesheets, sponsors have hotlines - use them"],
    ["Recruitment scams","MEDIUM","The Scam Wall above - employer petitions, published fees only"],
    ["Isolation on remote farms","LOW","SA crews are common in the H-2A lane; ask your recruiter where compatriots are placed"],
    ["Programme rules shift","MEDIUM","Every flagged figure is re-checked before you sign - your placement agency does exactly that"]],
   [190,55,None]),
  ("h2","The surroundings"),
  ("photos",[("sw_us_4_farm.jpg","Row-crop scale - the office"),("sw_us_5_town.jpg","Main street and the elevator"),("sw_us_6_life.jpg","The farmstead evening - rent-free")]),
  ("mapshot","sw_us_mapshot.jpg","Farm country, mapped - the interactive layered version (journey / farm belt / town life / seasons) lives in the app."),
  ("h1","7 - What this year buys your career"),
  ("p","- <b>Large-scale mechanised experience</b> - US row-crop scale is CV gold back home.<br/>"
      "- <b>Capital:</b> free housing on H-2A makes this the rare year abroad you SAVE through.<br/>"
      "- <b>Repeatability:</b> H-2A has no cap - good references make it an annual door.<br/>"
      "- <b>Progression:</b> J-1 Trainee (18 months) later; farm-management roles; precision-ag skills SA farms pay for.<br/>"
      "- <b>Networks:</b> two seasons in, you know operators, agronomists and employers on two continents."),
  ("h1","8 - Your next three actions"),
  ("p","<b>1.</b> Contact a J-1 agriculture provider this month (OVC and Epic Exchange are established SA examples) - the graduation clock is the whole game.<br/>"
      "<b>2.</b> Start the SAPS police clearance + apostille pile now; it is the slowest queue on the critical path.<br/>"
      "<b>3.</b> Take this dossier to a registered placement agency - MarketSquare introduces you to one, and that introduction is part of what your 5 Tuppence bought."),
  ("callout","MarketSquare never replaces placement professionals - and says so. This dossier is preparation: what is possible, what it takes, what to expect. Your agency turns it into your placement, your contract, your flight date. We prepare you; they place you. MarketSquare never touches wages, visa fees or contracts.",("#EAF0FA","#2F5496"),"THE HANDOFF"),
  ("h1","9 - Sources and dates"),
  ("small","All checked 23 Aug 2026. DHS/USCIS H-2A/H-2B eligible-country lists (South Africa eligible, Jan 2026 - re-issued annually, RE-CHECK) - US Dept of Labor AEWR (two-tier BLS-based structure since Oct 2025; state rates vary, RE-CHECK your contract) - SA media reporting on SA H-2A operator earnings (~R62,700/mo average - indicative only) - J-1 BridgeUSA intern/trainee programme rules (12-month post-graduation window; DS-7002/DS-2019 process) - SA provider programme pages (OVC, Epic Exchange - examples, not endorsements) - US Embassy Pretoria refugee-admissions notices and reporting on the FY2026 ceiling (7,500, primarily South Africans; 7,700+ admitted by mid-2026). Items marked RE-CHECK change annually or seasonally and MUST be confirmed at the official source before you sign or pay anything. Indicative FX of 23 Aug 2026 throughout."),
 ],
}

DOSSIERS = {
 "Dossier_EXAMPLE_Study_Hungary.pdf": HUNGARY,
 "Dossier_EXAMPLE_Work_USA_Farm.pdf": USA_FARM,
}
