#!/usr/bin/env python3
"""TRADERS-FIT-1 (David 25 Sep 2026: "I selected housecleaner ... these options are all wrong, it should
be applicable to the previous selection and then also clearly indicate these are examples ... not a 1947
penny, but rather a related question to the housecleaner's other employers"). The phone-around screen
showed the collectors' contacts and question for EVERY category. It now shows contacts and a question
that fit the category (and, in Services, whether it is home help or a trade), marked as examples.
Idempotent; asserts every anchor."""
import io, json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p): return io.open(os.path.join(R, p), encoding="utf-8").read()
def wr(p, s):
    io.open(os.path.join(R, p), "w", encoding="utf-8").write(s); assert rd(p) == s, p
def rep(s, a, b, name):
    if b in s: return s
    assert s.count(a) == 1, "anchor %s: %d" % (name, s.count(a)); return s.replace(a, b)

q = rd("quick.html")
OLD = """var TRADERS=[
  {name:'Marie Fourie',  last:'coins, last year'},
  {name:'Johan de Wet',  last:'stamps, March'},
  {name:'Anna Pretorius',last:'militaria, twice'},
  {name:'Pieter Nel',    last:'watches, 2024'},
  {name:'Elsa Joubert',  last:'art, once'},
  {name:'Kobus Venter',  last:'cards, last month'}
];"""
NEW = """/* TRADERS-FIT-1 (David 25 Sep 2026): the contacts and the question follow what she is looking for,
   and are marked as EXAMPLES -- in the app she picks from her own contacts. One naming tradition per list. */
var TRADER_NAMES=['Marie Fourie','Johan de Wet','Anna Pretorius','Pieter Nel','Elsa Joubert','Kobus Venter'];
var TRADER_SETS={
  collectors:{ph:'e.g. Anyone got a 1947 penny?', who:['coins, last year','stamps, March','militaria, twice','watches, 2024','art, once','cards, last month']},
  homehelp:{ph:'e.g. Does your cleaner have a free day? We are looking.', who:['neighbour, has a cleaner','friend, Menlyn','your sister','colleague','neighbour, two doors down','church friend']},
  trades:{ph:'e.g. Know a plumber who actually pitches up?', who:['neighbour, had a plumber in','friend, renovated last year','your brother-in-law','colleague','neighbour, new roof','body corporate chair']},
  tutors:{ph:'e.g. Anyone know a maths tutor for Grade 10?', who:['parent, same class','parent, soccer club','teacher friend','your cousin','parent, lift club','neighbour, child in matric']},
  cars:{ph:'e.g. Know anyone selling a bakkie under R150k?', who:['your mechanic','friend, sold his car','colleague','your brother','neighbour','friend at a dealership']},
  property:{ph:'e.g. Heard of a 2-bedroom to rent near Menlyn?', who:['friend, estate agent','neighbour','colleague, moved recently','your sister','your landlord','friend, body corporate']},
  adventures:{ph:'e.g. Anyone know a good guesthouse in Clarens for May?', who:['friend, went last year','colleague, travels a lot','your cousin','neighbour','friend, hiking club','your aunt']},
  localmarket:{ph:'e.g. Anyone selling fresh eggs nearby?', who:['neighbour','friend, market stall','church friend','colleague','your sister','neighbour, keeps chickens']}
};
function tradersFor(){
  var k=cat().key;
  if(k==='services'){
    var w=pickOf('what'), g=pickOf('group'), r=null;
    try{ if(w && typeof SVC_ROLES!=='undefined') for(var i=0;i<SVC_ROLES.length;i++) if(SVC_ROLES[i].l===w.label){ r=SVC_ROLES[i]; break; } }catch(e){}
    k = ((r && r.c==='C') || (g && /home/i.test(g.label))) ? 'homehelp' : 'trades';
  }
  var s=TRADER_SETS[k]||TRADER_SETS.trades;
  return {ph:s.ph, list:TRADER_NAMES.map(function(n,i){ return {name:n, last:s.who[i]}; })};
}
var TRADERS=[];"""
q = rep(q, OLD, NEW, "TRADERS")
q = rep(q, """function drawTraders(){
  var picked={};""", """function drawTraders(){
  var picked={}, TR=tradersFor(); TRADERS=TR.list;""", "drawTraders head")
q = rep(q, """   +'<div class="trd" id="trd">'+TRADERS.map(""", """   +'<div class="trex">Examples — in the app you pick from your own contacts</div>'
   +'<div class="trd" id="trd">'+TRADERS.map(""", "trex")
q = rep(q, """autocomplete="off" placeholder="Anyone got a 1947 penny?"><button""",
           """autocomplete="off" placeholder="'+qTr(TR.ph).replace(/"/g,'&quot;')+'"><button""", "placeholder")
q = rep(q, "/* ---- ask your traders: a phone-around, five at most, never a group ---- */",
           "/* ---- ask your traders: a phone-around, five at most, never a group ---- */\n"
           ".trex{font-size:10.5px;letter-spacing:.6px;text-transform:uppercase;font-weight:800;color:var(--dim);padding:2px 2px 7px}",
           "trex css")
wr("quick.html", q)

f = "roles/quick_i18n.json"; d = json.loads(rd(f))
W = {
 "Ask the people who would know": ["Vra die mense wat sal weet","Buza abantu abangazi","Botsa batho ba ka tsebang","Buza abantu abanokwazi","Botšiša batho bao ba ka tsebago"],
 "One line, to each of them separately. They never see each other — this is the phone-around, not a group.":
   ["Een reël, aan elkeen afsonderlik. Hulle sien mekaar nooit nie — dis rondbel, nie 'n groep nie.","Umugqa owodwa, komunye nomunye ngokwehlukana. Abasoze babonane — lokhu ukushayela abantu, akulona iqembu.","Mola o le mong, ho e mong le e mong ka thoko. Ha ba bonane — ena ke ho letsetsa batho, e seng sehlopha.","Umgca omnye, komnye nomnye ngokwahlukeneyo. Abaze babonane — oku kukutsalela abantu umnxeba, asiloqela.","Mothaladi o tee, go yo mongwe le yo mongwe ka noši. Ga ba bonane — se ke go leletša batho, e sego sehlopha."],
 "Examples — in the app you pick from your own contacts": ["Voorbeelde — in die app kies jy uit jou eie kontakte","Izibonelo — ku-app ukhetha kubantu bakho","Mehlala — ho app o kgetha ho batho ba hao","Imizekelo — kwi-app ukhetha kubantu bakho","Mehlala — ka go app o kgetha go batho ba gago"],
 "Each one is an ordinary buzz, with your name on it, and each of them can switch you off on their own. There is no group and no thread — whoever knows something buzzes you back.":
   ["Elkeen is 'n gewone buzz, met jou naam daarop, en elkeen kan jou self afskakel. Daar is geen groep en geen draad nie — wie iets weet, buzz jou terug.","Ngayinye iyi-buzz ejwayelekile, enegama lakho, futhi ngamunye angakucisha yedwa. Alikho iqembu futhi ayikho intambo — noma ubani owaziyo uzokubuzela emuva.","E nngwe le e nngwe ke buzz e tlwaelehileng, e nang le lebitso la hao, mme e mong le e mong a ka o tima a le mong. Ha ho sehlopha ebile ha ho puisano — ya tsebang ho hong o tla o buzz hape.","Nganye yi-buzz eqhelekileyo, enegama lakho, kwaye nganye inokukucima yodwa. Akukho qela kwaye akukho mtya — nabani na owaziyo uya kukubuzela emva.","Ye nngwe le ye nngwe ke buzz ye e tlwaelegilego, ye e nago le leina la gago, gomme yo mongwe le yo mongwe a ka go tima a nnoši. Ga go sehlopha le poledišano — yo a tsebago se sengwe o tla go buzz morago."],
 "Ask": ["Vra","Buza","Botsa","Buza","Botšiša"],
 "Back": ["Terug","Emuva","Morao","Emva","Morago"],
 "Five is the cap — this is a phone-around, not a mailing list.": ["Vyf is die maksimum — dis rondbel, nie 'n poslys nie.","Abahlanu yibona abaningi — lokhu ukushayela abantu, akusilo uhlu lokuposa.","Ba bahlano ke bongata — ena ke ho letsetsa batho, e seng lenane la poso.","Abahlanu ngabona baninzi — oku kukutsalela abantu umnxeba, asiluhlu lokuposa.","Ba bahlano ke bontši — se ke go leletša batho, e sego lenaneo la poso."],
}
AF = {  # the per-category examples: Afrikaans now; the other four go to the language reviewer (RUL-160)
 "e.g. Anyone got a 1947 penny?":"bv. Het iemand 'n 1947-pennie?",
 "e.g. Does your cleaner have a free day? We are looking.":"bv. Het jou huishulp 'n vry dag? Ons soek.",
 "e.g. Know a plumber who actually pitches up?":"bv. Ken jy 'n loodgieter wat regtig opdaag?",
 "e.g. Anyone know a maths tutor for Grade 10?":"bv. Ken iemand 'n wiskunde-tutor vir Graad 10?",
 "e.g. Know anyone selling a bakkie under R150k?":"bv. Ken jy iemand wat 'n bakkie onder R150k verkoop?",
 "e.g. Heard of a 2-bedroom to rent near Menlyn?":"bv. Weet jy van 'n 2-slaapkamer te huur naby Menlyn?",
 "e.g. Anyone know a good guesthouse in Clarens for May?":"bv. Ken iemand 'n goeie gastehuis in Clarens vir Mei?",
 "e.g. Anyone selling fresh eggs nearby?":"bv. Verkoop iemand vars eiers naby?",
 "coins, last year":"munte, verlede jaar","stamps, March":"seëls, Maart","militaria, twice":"militaria, twee keer","watches, 2024":"horlosies, 2024","art, once":"kuns, een keer","cards, last month":"kaarte, verlede maand",
 "neighbour, has a cleaner":"buurvrou, het 'n huishulp","friend, Menlyn":"vriend, Menlyn","your sister":"jou suster","colleague":"kollega","neighbour, two doors down":"buurvrou, twee huise af","church friend":"kerkvriend",
 "neighbour, had a plumber in":"buurman, het 'n loodgieter gehad","friend, renovated last year":"vriend, het verlede jaar opgeknap","your brother-in-law":"jou swaer","neighbour, new roof":"buurman, nuwe dak","body corporate chair":"voorsitter, beheerliggaam",
 "parent, same class":"ouer, dieselfde klas","parent, soccer club":"ouer, sokkerklub","teacher friend":"onderwyser-vriend","your cousin":"jou neef","parent, lift club":"ouer, saamryklub","neighbour, child in matric":"buurvrou, kind in matriek",
 "your mechanic":"jou werktuigkundige","friend, sold his car":"vriend, het sy kar verkoop","your brother":"jou broer","neighbour":"buurman","friend at a dealership":"vriend by 'n handelaar",
 "friend, estate agent":"vriend, eiendomsagent","colleague, moved recently":"kollega, onlangs getrek","your landlord":"jou verhuurder","friend, body corporate":"vriend, beheerliggaam",
 "friend, went last year":"vriend, was verlede jaar daar","colleague, travels a lot":"kollega, reis baie","friend, hiking club":"vriend, stapklub","your aunt":"jou tannie",
 "friend, market stall":"vriend, markstalletjie","neighbour, keeps chickens":"buurvrou, hou hoenders",
}
for k, v in W.items(): d["w"].setdefault(k, v)
for k, v in AF.items(): d["w"].setdefault(k, [v, "", "", "", ""])
rx = [["^Pick up to (\\d+)\\.$","Kies tot $1.","Khetha abangafika ku-$1.","Kgetha ho fihla ho $1.","Khetha ukuya kuthi ga ku-$1.","Kgetha go fihla go $1."],
      ["^(\\d+) of (\\d+) picked$","$1 van $2 gekies","$1 kwangu-$2 okukhethiwe","$1 ho $2 tse kgethilweng","$1 kwa-$2 ekhethiweyo","$1 go $2 tše kgethilwego"]]
have = set(r[0] for r in d["r"])
for r in rx:
    if r[0] not in have: d["r"].append(r)
wr(f, json.dumps(d, ensure_ascii=False, indent=1))
print("TRADERS-FIT-1 applied")
