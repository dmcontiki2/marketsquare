#!/usr/bin/env python3
"""VOUCH-WHO-1 (RUL-169, David 25 Sep 2026): the one-tap reference is worded for who the seller
actually works for -- an employer for a housekeeper, a parent for a tutor, a customer for a trade --
and the Buzz card on the seller's own draft speaks from the seller's side. Same signal, same points.
Idempotent: re-running changes nothing. Asserts every anchor, so a moved anchor fails loudly."""
import io, json, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p): return io.open(os.path.join(R, p), encoding="utf-8").read()
def wr(p, s):
    io.open(os.path.join(R, p), "w", encoding="utf-8").write(s)
    assert rd(p) == s, p
def rep(s, a, b, name):
    if b in s: return s
    assert s.count(a) == 1, "anchor %s: %d" % (name, s.count(a))
    return s.replace(a, b)

q = rd("quick.html")
if "VOUCH-WHO-1" not in q:
    fn = ("/* VOUCH-WHO-1 (RUL-169, David 25 Sep 2026): \"the tutor - it says 'your employer' but he is self\n"
          "   employed ... could this be from an existing customer rather than an employer? A referral.\" The\n"
          "   one-tap confirmation is one signal -- somebody you have worked for -- so only the WORDS follow\n"
          "   who that somebody is. Same link, same points. */\n"
          "function vouchWho(){\n"
          "  var k=cat().key, w=pickOf('what'), r=null;\n"
          "  try{ if(w && typeof SVC_ROLES!=='undefined') for(var i=0;i<SVC_ROLES.length;i++) if(SVC_ROLES[i].l===w.label){ r=SVC_ROLES[i]; break; } }catch(e){}\n"
          "  if(k==='homehelp' || (k==='services' && r && r.c==='C')) return {subj:'Your employer', demo:'You employed her'};\n"
          "  if(k==='tutors') return {subj:'A parent or student you teach', demo:'You have used them as a tutor'};\n"
          "  if(k==='services') return {subj:'A customer you have worked for', demo:'You have used their work'};\n"
          "  if(k==='adventures') return {subj:'A guest you have hosted', demo:'You have stayed with them'};\n"
          "  return {subj:'Someone you have worked for', demo:'They have worked for you'};\n"
          "}\n")
    q = rep(q, "function drawDraft(){", fn + "function drawDraft(){", "drawDraft")
q = rep(q, "+'<p>Your employer says <b>one sentence</b> about you. That is what opens your trust score '",
           "+'<p>'+vouchWho().subj+' says <b>one sentence</b> about you. That is what opens your trust score '", "vouch card")
q = rep(q, "+'<p>'+comms().card+' They have exactly the same button for you. One line each way, no '\n   +'thread to scroll, and email catches it if their push is off.</p>'",
           "+'<p><span>'+(comms().sellCard||comms().card)+'</span> <span>They have exactly the same button for you. One line each way, no '\n   +'thread to scroll, and email catches it if their push is off.</span></p>'", "buzz card")
q = rep(q, "+'<div class=\"vlede\">You employed her, so you are the only person who can say this. '",
           "+'<div class=\"vlede\">'+vouchWho().demo+', so you are the only person who can say this. '", "demo lede")
SELL = {
 "One line to the agency holding your place - viewings, offers, show days.'":
   "One line to the agency holding your place - viewings, offers, show days.',\n    sellCard:'One line to everyone who asked about your place - viewings, offers, show days.'",
 "One line to every place you asked - dates, late arrivals, one more bed.'":
   "One line to every place you asked - dates, late arrivals, one more bed.',\n    sellCard:'One line to every guest who asked - dates, late arrivals, one more bed.'",
 "One line to the trade you use - on my way, running late, job done.'":
   "One line to the trade you use - on my way, running late, job done.',\n    sellCard:'One line to your regular customers - on my way, running late, job done.'",
 "One line to the tutor - a moved lesson, an exam week, a late child.'":
   "One line to the tutor - a moved lesson, an exam week, a late child.',\n    sellCard:'One line to the parents you teach for - a moved lesson, an exam week, a late child.'",
}
for a, b in SELL.items():
    q = rep(q, "card:'" + a, "card:'" + b, a[:30])
wr("quick.html", q)

c = rd("confirm.html")
c = rep(c, "Their listing will say only that a previous employer confirmed them.",
           "Their listing will say only that someone they worked for confirmed them.", "confirm fine print")
wr("confirm.html", c)

b = rd("bea_main.py")
b = rep(b, '"name": "A previous employer confirmed you",', '"name": "Someone you worked for confirmed you",', "signal 1")
b = rep(b, '"name": "A second previous employer confirmed you",', '"name": "A second person you worked for confirmed you",', "signal 2")
wr("bea_main.py", b)

f = "roles/quick_i18n.json"; d = json.loads(rd(f))
W = {
 "Your employer says": ["Jou werkgewer sê","Umqashi wakho uthi","Mohiri wa hao o re","Umqeshi wakho uthi","Mothwadi wa gago o re"],
 "A parent or student you teach says": ["'n Ouer of leerder vir wie jy klas gee sê","Umzali noma umfundi omfundisayo uthi","Motswadi kapa moithuti eo o mo rutang o re","Umzali okanye umfundi omfundisayo uthi","Motswadi goba moithuti yo o mo rutago o re"],
 "A customer you have worked for says": ["'n Klant vir wie jy gewerk het sê","Ikhasimende osebenzele lona lithi","Moreki eo o kileng wa mo sebeletsa o re","Umthengi omsebenzeleyo uthi","Moreki yo o kilego wa mo šomela o re"],
 "A guest you have hosted says": ["'n Gas wat jy ontvang het sê","Isivakashi osake wasamukela sithi","Moeti eo o kileng wa mo amohela o re","Undwendwe owakhe walwamkela luthi","Moeng yo o kilego wa mo amogela o re"],
 "Someone you have worked for says": ["Iemand vir wie jy gewerk het sê","Umuntu osake wamsebenzela uthi","Motho eo o kileng wa mo sebeletsa o re","Umntu owakhe wamsebenzela uthi","Motho yo o kilego wa mo šomela o re"],
 "one sentence": ["een sin","umusho owodwa","polelo e le nngwe","isivakalisi esinye","lefoko le tee"],
 "about you. That is what opens your trust score — nothing you write about yourself can do it. Four taps on their side, and they never have to use TrustSquare again.":
   ["oor jou. Dit is wat jou vertrouenstelling oopmaak — niks wat jy oor jouself skryf kan dit doen nie. Vier tikke aan hulle kant, en hulle hoef nooit weer TrustSquare te gebruik nie.",
    "ngawe. Yilokho okuvula amaphuzu akho okwethenjwa — akukho lutho olubhala ngawe ongakwenza lokho. Ukuthinta okune ohlangothini lwabo, futhi abasoze bawusebenzise futhi uTrustSquare.",
    "ka wena. Ke sona se bulang sekoro sa hao sa tshepo — ha ho letho leo o le ngolang ka wena le ka etsang seo. Ho tobetsa hane ka lehlakoreng la bona, mme ha ba sa tla hlola ba sebedisa TrustSquare.",
    "ngawe. Yiyo evula amanqaku akho okuthenjwa — akukho nto oyibhalayo ngawe enokwenza oko. Ukucofa kane kwicala labo, kwaye abasoze baphinde basebenzise iTrustSquare.",
    "ka wena. Ke sona se bulago sekoro sa gago sa go tshepega — ga go selo seo o se ngwalago ka wena se ka dirago seo. Dikgotlo tše nne ka lehlakoreng la bona, gomme ga ba sa swanela go šomiša TrustSquare gape."],
 "Buzz — one line to the other phone": ["Buzz — een reël na die ander foon","Buzz — umugqa owodwa kwenye ifoni","Buzz — mola o le mong ho fono e nngwe","Buzz — umgca omnye kwenye ifowuni","Buzz — mothaladi o tee go founo ye nngwe"],
 "They have exactly the same button for you. One line each way, no thread to scroll, and email catches it if their push is off.":
   ["Hulle het presies dieselfde knoppie vir jou. Een reël elke kant toe, geen draad om deur te rol nie, en e-pos vang dit as hul kennisgewings af is.",
    "Nabo banenkinobho efanayo ngqo yakho. Umugqa owodwa ngapha nangapha, ayikho intambo yokuskrola, futhi i-imeyili iyakubamba uma izaziso zabo zivaliwe.",
    "Le bona ba na le konopo e tshwanang hantle bakeng sa hao. Mola o le mong ka nqa ka nngwe, ha ho puisano e telele, mme imeile e e tshwara ha ditsebiso tsa bona di timilwe.",
    "Nabo banenqaku elifanayo ncam lakho. Umgca omnye kwicala ngalinye, akukho mtya wokuskrola, kwaye i-imeyile iyayibamba ukuba izaziso zabo zicinyiwe.",
    "Le bona ba na le konopo ye e swanago gabotse ya gago. Mothaladi o tee ka lehlakore le lengwe le le lengwe, ga go poledišano ye telele, gomme imeile e e swara ge ditsebišo tša bona di timilwe."],
 "One line to the parents you teach for - a moved lesson, an exam week, a late child.":
   ["Een reël na die ouers vir wie jy klas gee - 'n geskuifde les, 'n eksamenweek, 'n laat kind.","Umugqa owodwa kubazali obafundisela - isifundo esihanjisiwe, isonto lezivivinyo, ingane efike sekwephuzile.","Mola o le mong ho batswadi bao o ba rutelang - thuto e sutisitsweng, beke ya ditlhahlobo, ngwana ya diehang.","Umgca omnye kubazali obafundisela - isifundo esishenxisiweyo, iveki yeemviwo, umntwana ofika emva kwexesha.","Mothaladi o tee go batswadi bao o ba rutelago - thuto ye e šuthišitšwego, beke ya ditlhahlobo, ngwana yo a diegilego."],
 "One line to your regular customers - on my way, running late, job done.":
   ["Een reël na jou vaste kliënte - op pad, laat, werk klaar.","Umugqa owodwa kumakhasimende akho ajwayelekile - ngisendleleni, ngizophuza, umsebenzi uqediwe.","Mola o le mong ho bareki ba hao ba kamehla - ke tseleng, ke tla dieha, mosebetsi o phethilwe.","Umgca omnye kubathengi bakho abaqhelekileyo - ndisendleleni, ndiza kufika emva kwexesha, umsebenzi ugqityiwe.","Mothaladi o tee go bareki ba gago ba ka mehla - ke tseleng, ke tla diega, mošomo o phethilwe."],
 "One line to every guest who asked - dates, late arrivals, one more bed.":
   ["Een reël na elke gas wat gevra het - datums, laat aankomste, nog een bed.","Umugqa owodwa kuso sonke isivakashi esibuzile - izinsuku, ukufika sekwephuzile, omunye umbhede.","Mola o le mong ho moeti e mong le e mong ya botsitseng - matsatsi, ho fihla ka morao, bethe e nngwe.","Umgca omnye kulo lonke undwendwe olubuzileyo - imihla, ukufika emva kwexesha, enye ibhedi.","Mothaladi o tee go moeng yo mongwe le yo mongwe yo a botšišitšego - matšatši, go fihla morago, malao a mangwe."],
 "One line to everyone who asked about your place - viewings, offers, show days.":
   ["Een reël na almal wat oor jou plek gevra het - besigtigings, aanbiedinge, skoudae.","Umugqa owodwa kubo bonke ababuze ngendawo yakho - ukubuka, izithembiso, izinsuku zokubukisa.","Mola o le mong ho bohle ba botsitseng ka sebaka sa hao - ho sheba, dinyehelo, matsatsi a pontsho.","Umgca omnye kubo bonke ababuze ngendawo yakho - ukujonga, izithembiso, iintsuku zomboniso.","Mothaladi o tee go bohle bao ba botšišitšego ka lefelo la gago - go lebelela, dithekišo, matšatši a pontšho."],
}
for k, v in W.items(): d["w"].setdefault(k, v)
wr(f, json.dumps(d, ensure_ascii=False, indent=1))
print("VOUCH-WHO-1 applied")
