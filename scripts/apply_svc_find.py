#!/usr/bin/env python3
"""SVC-FIND-1 + CUSTOMER-REF-2 (RUL-172, David 25 Sep 2026). (a) A Services search for a role returns THAT role only:
every live role has its own match, applied to title + description + service_type, so Car guard never returns Security
guard, Shop assistant never returns Creche assistant, and a whole-category fetch (no one-word server term) lets a
listing written in the app's own words ('Gardening', 'Electrical') still be found. (b) The mostly self-employed casual
roles are vouched for by 'A customer' and buzz 'your regular customers' (RUL-172(c), amending RUL-169(b)).
Idempotent; asserts every anchor. Then run sync_quick_roles.py and copy quick.html over genie/HARNESS.html."""
import io, os, json
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p): return io.open(os.path.join(R, p), encoding="utf-8").read()
def wr(p, s):
    io.open(os.path.join(R, p), "w", encoding="utf-8").write(s); assert rd(p) == s, p
def rep(s, a, b, name):
    if b in s: return s
    assert s.count(a) == 1, "anchor %s: %d" % (name, s.count(a)); return s.replace(a, b)
q = rd("quick.html")
q = rep(q, "  function groupRx(){ return cat().key==='localmarket' ? (GROUP_RX[roleLabel()]||null) : null; }",
           "  function groupRx(){ return (cat().key==='localmarket' || (window.svcIs && svcIs(cat()))) ? (GROUP_RX[roleLabel()]||null) : null; }   /* SVC-FIND-1 */",
        "groupRx")
q = rep(q, "  function typeFilter(list){ var g=groupRx(); if(g) return list.filter(function(l){ return g.test((l.title||'')+' '+(l.description||'')); });",
           "  function typeFilter(list){ var g=groupRx(); if(g) return list.filter(function(l){ return g.test((l.title||'')+' '+(l.description||'')+' '+(l.service_type||'')); });",
        "typeFilter")
q = rep(q, "  if(k==='homehelp' || (k==='services' && r && r.c==='C')) return {subj:'Your employer', demo:'You employed her'};",
           "  if(r && window.SVC_CUSTOMER && SVC_CUSTOMER[r.k]) return {subj:'A customer', demo:'You have used their work'};   /* RUL-172(c) */\n"
           "  if(k==='homehelp' || (k==='services' && r && r.c==='C')) return {subj:'Your employer', demo:'You employed her'};",
        "vouchWho customer roles")
RX = {
 "Home cleaner": r"(home|house|domestic)\W*(clean|help|work)|\bdomestic\b|laundry|ironing|^(?![\s\S]*(office|commercial|contract|carpet|window|pool|car)\W*(clean|wash))[\s\S]*\bclean(er|ers|ing)\b",
 "Housekeeper": r"housekeep",
 "Nanny": r"nann(y|ies)|child\W?mind|babysit|child\W?care",
 "Caregiver": r"care\W?giv|\bcarer\b|elderly|frail\W?care|home\W?nurs|companion",
 "Cook": r"\bcook",
 "Chef": r"\bchef",
 "Gardener": r"garden(er|ing|\s+service)|\blawn|landscap|grounds",
 "Handyman": r"handy\W?m[ae]n|odd\W?jobs|home\W?maintenance",
 "Pool cleaner": r"pool\W*(clean|service|care|maint)|swimming\W*pool",
 "Window cleaner": r"window\W*(clean|wash)",
 "Pet sitter / dog walker": r"dog\W*walk|pet\W*(sit|care|mind)|dog\W*sit|cat\W*sit",
 "Carpet washer": r"carpet|rug\W*clean|upholster",
 "Au pair": r"au\W?pair",
 "Tree cutter": r"tree\W*(cut|fell|remov|surg|trim|prun|work)|arborist",
 "Garden waste removal": r"garden\W*(waste|refuse|rubbish)|refuse\W*remov|waste\W*remov|rubble\W*remov",
 "Room attendant": r"room\W*attend|chamber\W?maid|hotel\W*(clean|housekeep)",
 "Kitchen assistant": r"kitchen\W*(assist|hand|porter|help)|dish\W?wash|scullery",
 "Cashier": r"cashier|till\W*operat",
 "Waiter": r"\bwait(er|ers|ress|ron|ing\s+staff)",
 "Bartender": r"bar\W?(tender|man|men|maid|lady|person|staff)",
 "Griller / braai": r"braai|griller|\bgrill",
 "Hotel porter": r"^(?![\s\S]*kitchen\W*porter)[\s\S]*(porter|bell\W?(boy|man|hop)|luggage)",
 "Lodge staff": r"lodge\W*(staff|work|host|attend|all\W?round)|game\W*lodge",
 "Caterer": r"cater(er|ing)",
 "Petrol attendant": r"petrol|fuel\W*attend|forecourt",
 "Shelf packer": r"shelf\W*(pack|stack|fill)|stock\W*assist",
 "Shop assistant": r"(shop|sales|store|retail)\W*assist",
 "Merchandiser": r"merchandis",
 "Car guard": r"car\W*guard|parking\W*attend",
 "Picker / packer": r"^(?![\s\S]*shelf\W*pack)[\s\S]*(\bpicker|order\W*pick|warehouse\W*(pack|pick)|\bpacker)",
 "Removals helper": r"removals|remover|furniture\W*mov|moving\W*help|house\W*mov|\bmovers?\b",
 "Delivery rider": r"deliver(y|ies)|courier",
 "Farm worker": r"farm\W*(work|hand|labour)|farmhand",
 "General worker": r"general\W*(work|labour)|labourer|\bloader\b|factory\W*work",
 "Painter": r"^(?![\s\S]*spray\W*paint)[\s\S]*paint(er|ers|ing)",
 "Builder's assistant": r"builder\W?s?\W*assist|build(ing)?\W*assist|construction\W*(help|assist|labour)",
 "Office cleaner": r"office\W*clean|commercial\W*clean|contract\W*clean",
 "Seamstress / tailor": r"seamstress|tailor|alteration|dress\W?mak",
 "Sewing machinist": r"sewing\W*machin|machinist",
 "Hair braider": r"braid",
 "Hairdresser": r"hair\W*(dress|styl|salon|cut)|barber",
 "Nail technician": r"\bnail",
 "Car washer": r"car\W*wash|valet",
 "Event staff": r"event\W*(staff|help|crew|work)|function\W*staff|banquet",
 "Crèche assistant": r"cr[eè]che|day\W?care|pre\W?school|nursery\W*school",
 "Security guard": r"^(?![\s\S]*(car\W*guard|body\W?guard))[\s\S]*(security|\bguard|watch\W?man|night\W*watch|psira)",
 "Bodyguard": r"body\W?guard|close\W*protection|vip\W*protection",
 "Plant operator (TLB / excavator)": r"plant\W*operat|\btlb\b|excavator|backhoe|grader|bulldozer",
 "Boilermaker": r"boiler\W?mak",
 "Welder": r"\bweld",
 "Forklift operator": r"fork\W?lift",
 "Driver": r"^(?![\s\S]*(taxi|shuttle|code\W*1[04]\b|long\W?haul))[\s\S]*(driver|chauffeur)",
 "Code 10 / Code 14 driver": r"code\W*1[04]\b|truck\W*driv|long\W?haul|heavy\W*vehicle",
 "Taxi / shuttle driver": r"taxi|shuttle",
 "Diesel mechanic": r"diesel",
 "Motor mechanic": r"^(?![\s\S]*diesel)[\s\S]*mechanic",
 "Auto electrician": r"auto\W*electric",
 "Electrician": r"^(?![\s\S]*auto\W*electric)[\s\S]*electric",
 "Gas installer": r"\bgas\b",
 "Plumber": r"plumb",
 "Bricklayer": r"brick",
 "Plasterer": r"plaster",
 "Tiler": r"\btil(er|ers|ing|es)\b",
 "Carpenter": r"carpent|joiner|woodwork",
 "Roofer": r"roof|waterproof",
 "Paver": r"\bpav(er|ers|ing)\b",
 "Air-con & refrigeration technician": r"air\W?con|refrigerat|hvac",
 "Solar PV installer": r"solar",
 "Borehole & pump technician": r"borehole|\bpump",
 "CCTV / alarm installer": r"cctv|alarm",
 "Gate & garage-door technician": r"gate\W*(motor|repair|automat|technic)|garage\W*door",
 "Locksmith": r"lock\W?smith",
 "Appliance repair": r"appliance",
}
reg = json.loads(rd("roles/role_registry.json"))
live = [x["label"]["en"] for x in reg["roles"] if x["status"] == "in"]
missing = [l for l in live if l not in RX]; extra = [l for l in RX if l not in live]
assert not missing and not extra, "role match table out of step: missing %s extra %s" % (missing, extra)
CUST = ["hair_braider", "hairdresser", "nail_technician", "car_washer", "seamstress_tailor", "handyman", "pool_cleaner",
        "window_cleaner", "pet_sitter_dog_walker", "carpet_washer", "tree_cutter", "garden_waste_removal", "griller_braai", "caterer"]
BLOCK = ("\n/* ===========================================================================\n"
 "   SVC-FIND-1 + CUSTOMER-REF-2 (RUL-172, David 25 Sep 2026). A Services search returns that role only; the\n"
 "   self-employed are vouched for by a customer and buzz their regular customers.\n"
 "   ------------------------------------------------------------------------- */\n"
 "var SVC_CUSTOMER=" + json.dumps({k: 1 for k in CUST}) + ";\n"
 "(function(){\n"
 "  var RX=" + json.dumps(RX, ensure_ascii=False) + ";\n"
 "  Object.keys(RX).forEach(function(l){ try{ window.GROUP_RX[l]=new RegExp(RX[l],'i'); }catch(e){} });\n"
 "  var _cm=comms;\n"
 "  comms=function(){ var c=_cm();\n"
 "    try{ var w=pickOf('what'), r=null; if(w) for(var i=0;i<SVC_ROLES.length;i++) if(SVC_ROLES[i].l===w.label){ r=SVC_ROLES[i]; break; }\n"
 "      if(r && SVC_CUSTOMER[r.k] && cat().key==='homehelp'){ var s=COMMS.services, o={}; for(var k in c) o[k]=c[k];\n"
 "        o.bRole=qTr('your regular customer, Menlyn'); o.card=s.sellCard; o.sellCard=s.sellCard; o.sample=s.sample; o.many=s.many; return o; } }catch(e){}\n"
 "    return c; };\n"
 "})();\n")
if "SVC-FIND-1 + CUSTOMER-REF-2 (RUL-172" not in q:
    a = "\ndrawDoor();\n</script>"; assert q.count(a) == 1; q = q.replace(a, BLOCK + a)
wr("quick.html", q)
f = "roles/quick_i18n.json"; d = json.loads(rd(f))
W = {  # af, zu, st, xh, nso -- Claude's draft; the language reviewer (RUL-160) and first-month feedback correct it
 "Pool cleaner": ["Swembadskoonmaker", "Umhlanzi wamachibi okubhukuda", "Mohloekisi wa letamo la ho sesa", "Umcoci wamadama okuqubha", "Mohlwekiši wa bodiba bja go rutha"],
 "Window cleaner": ["Vensterskoonmaker", "Umhlanzi wamafasitela", "Mohloekisi wa difenstere", "Umcoci weefestile", "Mohlwekiši wa mafasetere"],
 "Pet sitter / dog walker": ["Troeteldieroppasser / hondestapper", "Umgcini wezilwane / umhambisi wezinja", "Mohlokomedi wa diphoofolo / mohatisi wa dintja", "Umgcini wezilwanyana / umhambisi wezinja", "Mohlokomedi wa diphoofolo / mosepediši wa dimpša"],
 "Carpet washer": ["Matskoonmaker", "Umgezi wokhaphethi", "Mohlatswi wa dikhapete", "Umhlambi weekhaphethi", "Mohlatswi wa dikhapete"],
 "Au pair": ["Au pair", "I-au pair", "Au pair", "I-au pair", "Au pair"],
 "Tree cutter": ["Boomafkapper", "Umgawuli wezihlahla", "Morema difate", "Umgawuli wemithi", "Moremi wa dihlare"],
 "Garden waste removal": ["Tuinvullisverwydering", "Ukususwa kwemfucuza yengadi", "Ho tlosa matlakala a serapa", "Ukususwa kwenkunkuma yegadi", "Go tloša ditlakala tša serapa"],
 "Griller / braai": ["Braaier", "Umosi wenyama / braai", "Mohadiki wa nama / braai", "Umoji wenyama / braai", "Mohadiki wa nama / braai"],
 "Hotel porter": ["Hotelportier", "Umthwali wemithwalo ehhotela", "Mojari wa thoto hoteleng", "Umthwali wemithwalo ehotele", "Mojari wa dithoto hoteleng"],
 "Lodge staff": ["Lodge-personeel", "Abasebenzi be-lodge", "Basebetsi ba lodge", "Abasebenzi be-lodge", "Bašomi ba lodge"],
 "Caterer": ["Spysenier", "Umphakeli wokudla", "Mofepi wa mekete", "Umlungiseleli wokutya", "Mofepi wa menyanya"],
 "Bodyguard": ["Lyfwag", "Unogada womuntu", "Molebeledi wa motho", "Unogada womntu", "Mohlapetši wa motho"],
 "Which pets do you look after?": ["Watter troeteldiere versorg jy?", "Unakekela iziphi izilwane?", "O hlokomela diphoofolo dife?", "Ukhathalela eziphi izilwanyana?", "O hlokomela diphoofolo dife?"],
 "Dogs": ["Honde", "Izinja", "Dintja", "Izinja", "Dimpša"],
 "Cats": ["Katte", "Amakati", "Dikatse", "Iikati", "Dikatse"],
 "Birds": ["Voëls", "Izinyoni", "Dinonyana", "Iintaka", "Dinonyana"],
 "Other pets": ["Ander troeteldiere", "Ezinye izilwane", "Diphoofolo tse ding", "Ezinye izilwanyana", "Diphoofolo tše dingwe"],
 "your regular customer, Menlyn": ["jou vaste klant, Menlyn", "ikhasimende lakho elivamile, eMenlyn", "moreki wa hao wa kamehla, Menlyn", "umthengi wakho oqhelekileyo, eMenlyn", "moreki wa gago wa ka mehla, Menlyn"],
}
for k, v in W.items(): d["w"].setdefault(k, v)
wr(f, json.dumps(d, ensure_ascii=False, indent=1))
print("SVC-FIND-1 + CUSTOMER-REF-2 applied (%d role matches, %d customer roles)" % (len(RX), len(CUST)))
