#!/usr/bin/env python3
"""apply_quick_missing_words.py -- LANG-OPEN-1 follow-through (5 Oct 2026).

PROBED 5 Oct 2026 while switching on the US/UK/AU languages: seven words Quick asks qTr() for had
NO entry in roles/quick_i18n.json, so they stayed English in EVERY language, South Africa's too --
e.g. the door's own 'Listed with us before? Sign in'. Claude's drafts (RUL-160) for all 15 columns.
Idempotent: adds only keys that are missing. Then run scripts/sync_quick_roles.py."""
import io, json, os, shutil, datetime
MS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(MS, 'roles', 'quick_i18n.json')
ORDER = ['af', 'zu', 'st', 'xh', 'nso', 'es', 'zh', 'tl', 'vi', 'cy', 'pl', 'ro', 'pa', 'ar', 'yue']
W = {
 'Continue with Google': ['Gaan voort met Google', 'Qhubeka nge-Google', 'Tswela pele ka Google', 'Qhubeka nge-Google', 'Tšwela pele ka Google', 'Continuar con Google', '使用 Google 继续', 'Magpatuloy gamit ang Google', 'Tiếp tục với Google', 'Parhau gyda Google', 'Kontynuuj z Google', 'Continuă cu Google', 'Google ਨਾਲ ਜਾਰੀ ਰੱਖੋ', 'المتابعة باستخدام Google', '用 Google 繼續'],
 'Listed with us before? Sign in': ['Al voorheen by ons gelys? Teken in', 'Wake wafaka ohlwini nathi? Ngena', 'O kile wa ngolisa le rona? Kena', 'Wakhe wadwelisa nathi? Ngena', 'O kile wa ngwala le rena? Tsena', '¿Ya publicaste con nosotros? Inicia sesión', '以前在这里发布过？登录', 'Nakapag-lista ka na sa amin? Mag-sign in', 'Đã từng đăng với chúng tôi? Đăng nhập', 'Wedi rhestru gyda ni o’r blaen? Mewngofnoda', 'Masz już u nas ogłoszenie? Zaloguj się', 'Ai mai publicat la noi? Conectează-te', 'ਪਹਿਲਾਂ ਸਾਡੇ ਨਾਲ ਲਿਸਟ ਕੀਤਾ ਹੈ? ਸਾਈਨ ਇਨ ਕਰੋ', 'هل نشرت معنا من قبل؟ سجّل الدخول', '之前喺度刊登過？登入'],
 'My TrustSquare': ['My TrustSquare', 'I-TrustSquare yami', 'TrustSquare ya ka', 'I-TrustSquare yam', 'TrustSquare ya ka', 'Mi TrustSquare', '我的 TrustSquare', 'Ang TrustSquare ko', 'TrustSquare của tôi', 'Fy TrustSquare', 'Mój TrustSquare', 'TrustSquare-ul meu', 'ਮੇਰਾ TrustSquare', 'TrustSquare الخاص بي', '我嘅 TrustSquare'],
 'My listings': ['My advertensies', 'Izikhangiso zami', 'Dipapatso tsa ka', 'Izibhengezo zam', 'Dipapatšo tša ka', 'Mis anuncios', '我的发布', 'Mga listing ko', 'Tin đăng của tôi', 'Fy hysbysebion', 'Moje ogłoszenia', 'Anunțurile mele', 'ਮੇਰੀਆਂ ਲਿਸਟਿੰਗਾਂ', 'إعلاناتي', '我嘅刊登'],
 'See, edit or publish what you have listed': ['Sien, wysig of publiseer wat jy gelys het', 'Bona, lungisa noma ushicilele okufakile', 'Bona, fetola kapa phatlalatsa seo o se ngolisitseng', 'Bona, hlela okanye upapashe oko ukudwelisileyo', 'Bona, fetola goba o phatlalatše seo o se ngwadilego', 'Ve, edita o publica lo que has anunciado', '查看、编辑或发布你发布的内容', 'Tingnan, i-edit o i-publish ang mga inilista mo', 'Xem, sửa hoặc đăng những gì bạn đã đăng', 'Gweld, golygu neu gyhoeddi beth rwyt ti wedi’i restru', 'Zobacz, edytuj lub opublikuj swoje ogłoszenia', 'Vezi, editează sau publică ce ai pus', 'ਜੋ ਤੁਸੀਂ ਲਿਸਟ ਕੀਤਾ ਹੈ ਉਹ ਵੇਖੋ, ਬਦਲੋ ਜਾਂ ਪ੍ਰਕਾਸ਼ਿਤ ਕਰੋ', 'شاهد أو عدّل أو انشر ما أضفته', '睇、改或者發佈你刊登咗嘅嘢'],
 'Your listing is waiting — open it to publish': ['Jou advertensie wag — maak dit oop om te publiseer', 'Isikhangiso sakho siyalinda — sivule ukuze usishicilele', 'Papatso ya hao e a emela — e bule ho e phatlalatsa', 'Isibhengezo sakho silindile — sivule ukuze usipapashe', 'Papatšo ya gago e a leta — e bule go e phatlalatša', 'Tu anuncio te espera — ábrelo para publicarlo', '你的发布在等你 — 打开即可发布', 'Naghihintay ang listing mo — buksan ito para i-publish', 'Tin đăng của bạn đang chờ — mở ra để đăng', 'Mae dy hysbyseb yn aros — agor hi i’w chyhoeddi', 'Twoje ogłoszenie czeka — otwórz je, aby opublikować', 'Anunțul tău așteaptă — deschide-l ca să-l publici', 'ਤੁਹਾਡੀ ਲਿਸਟਿੰਗ ਉਡੀਕ ਕਰ ਰਹੀ ਹੈ — ਪ੍ਰਕਾਸ਼ਿਤ ਕਰਨ ਲਈ ਇਸਨੂੰ ਖੋਲ੍ਹੋ', 'إعلانك بانتظارك — افتحه لنشره', '你嘅刊登等緊你 — 打開佢就可以發佈'],
 'or use your email': ['of gebruik jou e-pos', 'noma usebenzise i-imeyili yakho', 'kapa sebedisa imeile ya hao', 'okanye usebenzise i-imeyile yakho', 'goba o šomiše imeile ya gago', 'o usa tu correo', '或使用你的邮箱', 'o gamitin ang email mo', 'hoặc dùng email của bạn', 'neu defnyddia dy e-bost', 'albo użyj swojego e-maila', 'sau folosește e-mailul tău', 'ਜਾਂ ਆਪਣੀ ਈਮੇਲ ਵਰਤੋ', 'أو استخدم بريدك الإلكتروني', '或者用你嘅電郵'],
}
q = json.load(io.open(P, encoding='utf-8'))
assert q['langs'] == ORDER, q['langs']
add = {k: v for k, v in W.items() if k not in q['w']}
if add:
    for k, v in add.items():
        assert len(v) == len(ORDER), k
        q['w'][k] = v
    shutil.copy2(P, P + '.bak-missingwords-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
    with io.open(P, 'w', encoding='utf-8', newline='\n') as fh: json.dump(q, fh, ensure_ascii=False, indent=1)
    json.load(io.open(P, encoding='utf-8'))
print('quick_i18n.json: %d word(s) added' % len(add))
