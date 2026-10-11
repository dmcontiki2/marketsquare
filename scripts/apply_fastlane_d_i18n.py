#!/usr/bin/env python3
"""apply_fastlane_d_i18n.py -- QUICK-FAST-2 (RUL-223, David 10 Oct 2026, option D): the four new words for 'her quick
icons live in Quick' in every Quick language. Claude's drafts (RUL-160) for all 15 columns of roles/quick_i18n.json;
app words stay English (Quick). isiZulu, isiXhosa and Sepedi are drafts until a first-language reader has read them
(RUL-165). Idempotent: adds only keys that are missing. Then: python3 scripts/sync_quick_roles.py; cp quick.html genie/HARNESS.html."""
import io, json, os, shutil, datetime
MS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(MS, 'roles', 'quick_i18n.json')
ORDER = ['af', 'zu', 'st', 'xh', 'nso', 'es', 'zh', 'tl', 'vi', 'cy', 'pl', 'ro', 'pa', 'ar', 'yue']
W = {
 'Your quick icons': ['Jou vinnige ikone', 'Izimpawu zakho ezisheshayo', 'Matshwao a hao a potlakileng', 'Iimpawu zakho ezikhawulezayo',
   'Diswantšhetšo tša gago tša go akgofa', 'Tus iconos rápidos', '你的快捷图标', 'Ang mga quick icon mo', 'Biểu tượng nhanh của bạn',
   'Eich eiconau cyflym', 'Twoje szybkie ikony', 'Pictogramele tale rapide', 'ਤੁਹਾਡੇ ਤੇਜ਼ ਆਈਕਨ', 'أيقوناتك السريعة', '你嘅快捷圖示'],
 'It now sits at the top of Quick, ready to tap.': ['Dit sit nou bo-aan Quick, gereed om te tik.',
   'Manje lusesiqongweni se-Quick, selulungele ukuthephwa.', 'Jwale le kaholimo ho Quick, le loketse ho tobetswa.',
   'Ngoku lukwincopho ye-Quick, lulungele ukucofwa.', 'Bjale se godimo ga Quick, se loketše go kgotlwa.',
   'Ahora está arriba del todo en Quick, listo para tocar.', '它现在就在 Quick 的最上方，点一下即可。', 'Nasa itaas na ito ng Quick, handang i-tap.',
   'Giờ nó nằm ở đầu Quick, sẵn sàng để chạm.', "Mae bellach ar frig Quick, yn barod i'w dapio.", 'Jest teraz na górze Quick, gotowa do dotknięcia.',
   'Acum stă în partea de sus a Quick, gata de atins.', 'ਹੁਣ ਇਹ Quick ਦੇ ਸਭ ਤੋਂ ਉੱਪਰ ਹੈ, ਟੈਪ ਕਰਨ ਲਈ ਤਿਆਰ।', 'أصبحت الآن في أعلى Quick، جاهزة للنقر.',
   '而家佢喺 Quick 最上面，一撳就得。'],
 'Also put it on my home screen': ['Sit dit ook op my tuisskerm', 'Kufake futhi esikrinini sami sasekhaya', 'E behe hape skrineng sa ka sa lehae',
   'Kufake kananjalo kwisikrini sam sasekhaya', 'E bee gape sekirining sa ka sa gae', 'Ponerlo también en mi pantalla de inicio', '也放到我的主屏幕',
   'Ilagay din sa home screen ko', 'Cũng đặt lên màn hình chính của tôi', 'Ei roi ar fy sgrin gartref hefyd', 'Dodaj ją też do mojego ekranu głównego',
   'Pune-o și pe ecranul meu principal', 'ਇਸਨੂੰ ਮੇਰੀ ਹੋਮ ਸਕ੍ਰੀਨ ਤੇ ਵੀ ਰੱਖੋ', 'ضعها أيضًا على شاشتي الرئيسية', '都放埋喺我嘅主畫面'],
 'Tip: press and hold the Quick icon to jump straight in.': ['Wenk: druk en hou die Quick-ikoon om reguit in te spring.',
   'Ithiphu: cindezela futhi ubambe uphawu lwe-Quick ukuze ungene ngqo.', 'Keletso: tobetsa o tshware letshwao la Quick ho kena ka kotloloho.',
   'Icebiso: cinezela uze ubambe uphawu lwe-Quick ukuze ungene ngqo.', 'Keletšo: kgotla o swarelele seswantšhetšo sa Quick go tsena thwii.',
   'Consejo: mantén pulsado el icono de Quick para entrar directamente.', '提示：长按 Quick 图标即可直接进入。',
   'Tip: pindutin nang matagal ang Quick icon para dumiretso.', 'Mẹo: nhấn giữ biểu tượng Quick để vào thẳng.',
   "Awgrym: pwyswch a daliwch eicon Quick i neidio'n syth i mewn.", 'Wskazówka: przytrzymaj ikonę Quick, aby od razu wejść.',
   'Sfat: ține apăsat pe pictograma Quick ca să intri direct.', 'ਸੁਝਾਅ: ਸਿੱਧਾ ਅੰਦਰ ਜਾਣ ਲਈ Quick ਆਈਕਨ ਨੂੰ ਦਬਾ ਕੇ ਰੱਖੋ।',
   'نصيحة: اضغط مطولًا على أيقونة Quick للدخول مباشرة.', '貼士：撳住 Quick 圖示就可以直接入去。'],
}
q = json.load(io.open(P, encoding='utf-8'))
assert q['langs'] == ORDER, q['langs']
add = {k: v for k, v in W.items() if k not in q['w']}
for k, v in add.items():
    assert len(v) == len(ORDER) and all(str(x).strip() for x in v), k
if add:
    for k, v in add.items():
        q['w'][k] = v
    shutil.copy2(P, P + '.bak-fastD-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
    with io.open(P, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(q, fh, ensure_ascii=False, indent=1)
    json.load(io.open(P, encoding='utf-8'))
print('quick_i18n.json: %d word(s) added for option D' % len(add))
