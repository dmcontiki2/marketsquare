#!/usr/bin/env python3
"""apply_door_i18n.py -- ONE-DOOR-1 (DOOR_BRIEF.md U5): the door's and the AI PA pages' words in the 15 Quick languages.
Claude's draft, 23 Oct 2026, for the Language reviewer (RUL-160) exactly like the rest of roles/quick_i18n.json.
1. keeps the door's own words in roles/door_i18n.json (same shape as roles/quick_i18n.json; never overwrites a word a
   reviewer already corrected there) -- kept OUT of quick_i18n.json so Quick's generated QI18N block is untouched;
2. writes the DI18N / LANGS blocks into door.html, pa.html and pa_about.html (only the words each page uses), taking the
   category names from roles/quick_i18n.json (read only).
Keys are the exact English on screen. Order of columns = quick_i18n.json "langs". No AI model is named anywhere.
Usage: python3 scripts/apply_door_i18n.py        (idempotent)"""
import io, json, os, re
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QI = os.path.join(HERE, "roles", "quick_i18n.json")
# af, zu, st, xh, nso, es, zh, tl, vi, cy, pl, ro, pa, ar, yue
W = {
"Tap to continue in {app}": ["Tik om voort te gaan in {app}","Thepha ukuze uqhubeke ku-{app}","Tobetsa ho tswela pele ho {app}","Cofa ukuze uqhubeke ku-{app}","Kgotla go tšwela pele go {app}","Toca para seguir en {app}","轻触继续使用 {app}","I-tap para magpatuloy sa {app}","Chạm để tiếp tục trong {app}","Tapiwch i barhau yn {app}","Dotknij, aby kontynuować w {app}","Atinge pentru a continua în {app}","{app} ਵਿੱਚ ਜਾਰੀ ਰੱਖਣ ਲਈ ਛੋਹਵੋ","انقر للمتابعة في {app}","輕按繼續用 {app}"],
"Tap to open {app}": ["Tik om {app} oop te maak","Thepha ukuze uvule i-{app}","Tobetsa ho bula {app}","Cofa ukuze uvule i-{app}","Kgotla go bula {app}","Toca para abrir {app}","轻触打开 {app}","I-tap para buksan ang {app}","Chạm để mở {app}","Tapiwch i agor {app}","Dotknij, aby otworzyć {app}","Atinge pentru a deschide {app}","{app} ਖੋਲ੍ਹਣ ਲਈ ਛੋਹਵੋ","انقر لفتح {app}","輕按打開 {app}"],
"where you left off": ["waar jy opgehou het","lapho ugcine khona","moo o emisitseng teng","apho uyeke khona","moo o emišitšego gona","donde lo dejaste","从上次离开的地方","kung saan ka huminto","nơi bạn đã dừng lại","lle gwnaethoch adael","tam, gdzie skończyłeś","de unde ai rămas","ਜਿੱਥੇ ਤੁਸੀਂ ਛੱਡਿਆ ਸੀ","من حيث توقفت","由上次停低嘅地方"],
"Your interest: {cats}": ["Jou belangstelling: {cats}","Okukuthandayo: {cats}","Seo o se ratang: {cats}","Umdla wakho: {cats}","Seo o se ratago: {cats}","Tu interés: {cats}","你的兴趣：{cats}","Ang interes mo: {cats}","Sở thích của bạn: {cats}","Eich diddordeb: {cats}","Twoje zainteresowania: {cats}","Interesul tău: {cats}","ਤੁਹਾਡੀ ਦਿਲਚਸਪੀ: {cats}","اهتمامك: {cats}","你嘅興趣：{cats}"],
"from your previous use": ["uit jou vorige gebruik","kusukela ekusebenziseni kwakho kwangaphambili","ho tswa tshebedisong ya hao ya pele","ukusuka ekusebenziseni kwakho kwangaphambili","go tšwa tšhomišong ya gago ya peleng","según tu uso anterior","根据你以往的使用","mula sa dati mong paggamit","từ lần sử dụng trước của bạn","o'ch defnydd blaenorol","na podstawie wcześniejszego korzystania","din utilizarea ta anterioară","ਤੁਹਾਡੀ ਪਿਛਲੀ ਵਰਤੋਂ ਤੋਂ","من استخدامك السابق","根據你之前嘅使用"],
"from your public adverts": ["uit jou openbare advertensies","kusukela ezikhangisweni zakho zomphakathi","ho tswa dipapatsong tsa hao tsa setjhaba","ukusuka kwiintengiso zakho zoluntu","go tšwa dipapatšong tša gago tša setšhaba","según tus anuncios públicos","根据你公开的广告","mula sa mga pampublikong anunsiyo mo","từ các quảng cáo công khai của bạn","o'ch hysbysebion cyhoeddus","na podstawie Twoich publicznych ogłoszeń","din anunțurile tale publice","ਤੁਹਾਡੇ ਜਨਤਕ ਇਸ਼ਤਿਹਾਰਾਂ ਤੋਂ","من إعلاناتك العامة","根據你公開嘅廣告"],
"Everything near you": ["Alles naby jou","Konke okuseduze nawe","Tsohle tse haufi le wena","Yonke into ekufutshane nawe","Tšohle tše kgauswi le wena","Todo cerca de ti","你附近的一切","Lahat ng malapit sa iyo","Mọi thứ gần bạn","Popeth yn agos atoch","Wszystko w pobliżu","Tot ce e aproape de tine","ਤੁਹਾਡੇ ਨੇੜੇ ਸਭ ਕੁਝ","كل ما هو قريب منك","你附近嘅一切"],
"Executive report": ["Bestuursverslag","Umbiko omkhulu","Tlaleho ya botsamaisi","Ingxelo yolawulo","Pego ya taolo","Informe ejecutivo","管理报告","Ulat pang-ehekutibo","Báo cáo điều hành","Adroddiad gweithredol","Raport zarządczy","Raport executiv","ਕਾਰਜਕਾਰੀ ਰਿਪੋਰਟ","تقرير تنفيذي","管理報告"],
"Sell opportunity": ["Verkoopgeleentheid","Ithuba lokuthengisa","Monyetla wa ho rekisa","Ithuba lokuthengisa","Sebaka sa go rekiša","Oportunidad de venta","出售机会","Pagkakataong magbenta","Cơ hội bán","Cyfle i werthu","Okazja sprzedaży","Oportunitate de vânzare","ਵੇਚਣ ਦਾ ਮੌਕਾ","فرصة بيع","放售機會"],
"Buy opportunity": ["Koopgeleentheid","Ithuba lokuthenga","Monyetla wa ho reka","Ithuba lokuthenga","Sebaka sa go reka","Oportunidad de compra","购买机会","Pagkakataong bumili","Cơ hội mua","Cyfle i brynu","Okazja zakupu","Oportunitate de cumpărare","ਖਰੀਦਣ ਦਾ ਮੌਕਾ","فرصة شراء","購入機會"],
"Watch setup": ["Waginstelling","Ukusetha ukuqapha","Ho seta tebelo","Ukuseta ukujonga","Go beakanya tebelelo","Configurar vigilancia","监看设置","Ayos ng pagbabantay","Thiết lập theo dõi","Gosod gwyliadwriaeth","Ustawienia obserwacji","Setări de urmărire","ਨਿਗਰਾਨੀ ਸੈਟਅੱਪ","إعداد المراقبة","監察設定"],
"Your weekly report": ["Jou weeklikse verslag","Umbiko wakho wesonto","Tlaleho ya hao ya beke","Ingxelo yakho yeveki","Pego ya gago ya beke","Tu informe semanal","你的每周报告","Ang lingguhang ulat mo","Báo cáo hằng tuần của bạn","Eich adroddiad wythnosol","Twój raport tygodniowy","Raportul tău săptămânal","ਤੁਹਾਡੀ ਹਫ਼ਤਾਵਾਰੀ ਰਿਪੋਰਟ","تقريرك الأسبوعي","你嘅每週報告"],
"Buyers are looking for what you sell": ["Kopers soek wat jy verkoop","Abathengi bafuna lokho okuthengisayo","Bareki ba batla seo o se rekisang","Abathengi bafuna oko ukuthengisayo","Bareki ba nyaka seo o se rekišago","Hay compradores buscando lo que vendes","有买家在找你卖的东西","May mga mamimiling naghahanap ng ibinebenta mo","Người mua đang tìm thứ bạn bán","Mae prynwyr yn chwilio am yr hyn rydych yn ei werthu","Kupujący szukają tego, co sprzedajesz","Cumpărătorii caută ce vinzi","ਖਰੀਦਦਾਰ ਉਹ ਲੱਭ ਰਹੇ ਹਨ ਜੋ ਤੁਸੀਂ ਵੇਚਦੇ ਹੋ","مشترون يبحثون عما تبيعه","有買家搵緊你賣嘅嘢"],
"A bargain matches your watch": ["'n Winskoop pas by jou wag","Okushibhile kufana nokuqapha kwakho","Theko e tlase e tsamaisana le tebelo ya hao","Into enexabiso eliphantsi ihambelana nokujonga kwakho","Theko ya fase e swanela tebelelo ya gago","Una ganga coincide con tu vigilancia","有一笔划算的交易符合你的监看","May murang alok na tugma sa binabantayan mo","Một món hời khớp với mục theo dõi của bạn","Mae bargen yn cyfateb i'ch gwyliadwriaeth","Okazja pasuje do Twojej obserwacji","O ofertă bună se potrivește cu ce urmărești","ਇੱਕ ਸਸਤਾ ਸੌਦਾ ਤੁਹਾਡੀ ਨਿਗਰਾਨੀ ਨਾਲ ਮੇਲ ਖਾਂਦਾ ਹੈ","صفقة رابحة تطابق مراقبتك","有平嘢啱晒你監察嘅條件"],
"Your watches, set your way": ["Jou wagte, soos jy dit wil hê","Ukuqapha kwakho, ngendlela yakho","Ditebelo tsa hao, ka tsela ya hao","Ukujonga kwakho, ngendlela yakho","Ditebelelo tša gago, ka tsela ya gago","Tus vigilancias, a tu manera","你的监看，按你的方式设置","Ang mga bantay mo, ayon sa gusto mo","Mục theo dõi của bạn, theo cách của bạn","Eich gwyliadwriaethau, eich ffordd chi","Twoje obserwacje, po Twojemu","Urmăririle tale, așa cum vrei","ਤੁਹਾਡੀਆਂ ਨਿਗਰਾਨੀਆਂ, ਤੁਹਾਡੇ ਤਰੀਕੇ ਨਾਲ","مراقباتك، بطريقتك","你嘅監察，照你嘅方式設定"],
"Example": ["Voorbeeld","Isibonelo","Mohlala","Umzekelo","Mohlala","Ejemplo","示例","Halimbawa","Ví dụ","Enghraifft","Przykład","Exemplu","ਉਦਾਹਰਨ","مثال","示例"],
"Tap to meet your AI PA": ["Tik om jou AI PA te ontmoet","Thepha ukuze uhlangane ne-AI PA yakho","Tobetsa ho kopana le AI PA ya hao","Cofa ukuze udibane ne-AI PA yakho","Kgotla go kopana le AI PA ya gago","Toca para conocer a tu AI PA","轻触认识你的 AI PA","I-tap para makilala ang AI PA mo","Chạm để gặp AI PA của bạn","Tapiwch i gwrdd â'ch AI PA","Dotknij, aby poznać swojego AI PA","Atinge pentru a-ți cunoaște AI PA","ਆਪਣੇ AI PA ਨੂੰ ਮਿਲਣ ਲਈ ਛੋਹਵੋ","انقر للتعرّف على مساعدك AI PA","輕按認識你嘅 AI PA"],
"Your listing here": ["Jou advertensie hier","Uhlu lwakho lapha","Papatso ya hao mona","Intengiso yakho apha","Papatšo ya gago mo","Tu anuncio aquí","你的广告放这里","Ang listing mo rito","Tin đăng của bạn ở đây","Eich hysbyseb yma","Twoje ogłoszenie tutaj","Anunțul tău aici","ਤੁਹਾਡਾ ਇਸ਼ਤਿਹਾਰ ਇੱਥੇ","إعلانك هنا","你嘅廣告擺呢度"],
"Be the first seller in {city}": ["Wees die eerste verkoper in {city}","Yiba ngumthengisi wokuqala e-{city}","Eba morekisi wa pele {city}","Yiba ngumthengisi wokuqala e-{city}","Eba morekiši wa mathomo ka {city}","Sé el primer vendedor en {city}","成为{city}的第一位卖家","Maging unang nagbebenta sa {city}","Hãy là người bán đầu tiên ở {city}","Byddwch y gwerthwr cyntaf yn {city}","Bądź pierwszym sprzedawcą w {city}","Fii primul vânzător din {city}","{city} ਵਿੱਚ ਪਹਿਲੇ ਵਿਕਰੇਤਾ ਬਣੋ","كن أول بائع في {city}","做{city}第一個賣家"],
}
EXTRA = {}   # pa.html / pa_about.html words are appended by U4 (see PA_WORDS below)
PA_WORDS_FILE = os.path.join(HERE, "roles", "door_pa_words.json")
if os.path.exists(PA_WORDS_FILE):
    EXTRA = json.load(io.open(PA_WORDS_FILE, encoding="utf-8"))
ALL = dict(W); ALL.update(EXTRA)
CATS = ["Property", "Cars", "Collectors", "Adventures", "Services", "Tutors", "Local Market"]

def main():
    q = json.loads(io.open(QI, encoding="utf-8").read())
    langs = q["langs"]; assert len(langs) == 15, langs
    DI = os.path.join(HERE, "roles", "door_i18n.json")
    d = json.loads(io.open(DI, encoding="utf-8").read()) if os.path.exists(DI) else {
        "_about": "ONE-DOOR-1 door + AI PA page words (DOOR_BRIEF.md). Claude's first draft 23 Oct 2026, for the Language reviewer (RUL-160). "
                  "Keys are the exact English on screen; columns follow 'langs'. Category names come from roles/quick_i18n.json.",
        "langs": langs, "w": {}}
    assert d["langs"] == langs
    added = 0
    for k, v in ALL.items():
        assert len(v) == 15, (k, len(v))
        if k not in d["w"]:
            d["w"][k] = v; added += 1
    io.open(DI, "w", encoding="utf-8").write(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    w = dict(d["w"])
    for c in CATS:
        w[c] = q["w"][c]
    pages = {"door.html": list(W.keys()) + CATS}
    if EXTRA:
        pages["pa.html"] = list(EXTRA.keys()) + CATS + ["Executive report", "Sell opportunity", "Buy opportunity", "Watch setup", "Example"]
        pages["pa_about.html"] = pages["pa.html"]
    for page, keys in pages.items():
        p = os.path.join(HERE, page)
        if not os.path.exists(p):
            continue
        h = io.open(p, encoding="utf-8").read()
        block = json.dumps({k: w[k] for k in keys if k in w}, ensure_ascii=False, separators=(",", ":"))
        h2 = re.sub(r"/\*DI18N\*/.*?/\*END-DI18N\*/", lambda m: "/*DI18N*/" + block + "/*END-DI18N*/", h, flags=re.S)
        h2 = re.sub(r"/\*LANGS\*/.*?/\*END-LANGS\*/", lambda m: "/*LANGS*/" + json.dumps(langs) + "/*END-LANGS*/", h2, flags=re.S)
        assert h2.count("/*DI18N*/") == 1 and h2.count("/*END-LANGS*/") == 1, page
        io.open(p, "w", encoding="utf-8").write(h2)
        print("  %s: %d words" % (page, len(keys)))
    print("door_i18n.json: %d words added (%d total)" % (added, len(d["w"])))

if __name__ == "__main__":
    main()
