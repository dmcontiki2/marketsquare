#!/usr/bin/env python3
"""apply_snap_i18n.py -- QUICK-SNAP-1 (QUICK_SNAP_BRIEF.md, 19 Oct 2026): every new word of the Snap lane ("Snap it", "Say it",
the one screen, its lines) in every Quick language. Claude's drafts (RUL-160) for all 15 columns of roles/quick_i18n.json; app
words stay English (Quick, Publish). isiZulu, isiXhosa and Sepedi are drafts until a first-language reader has read them
(RUL-165). Idempotent: adds only keys that are missing. Then regenerates the QUICK-I18N block in quick.html EXACTLY as
scripts/sync_quick_roles.py does (that script also wants the role pictures, which the IP-hold worktree does not carry), and
copies quick.html to genie/HARNESS.html. No AI model is named anywhere."""
import io, json, os, re, shutil, datetime, sys
MS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(MS, 'roles', 'quick_i18n.json')
QH = os.path.join(MS, 'quick.html')
ORDER = ['af', 'zu', 'st', 'xh', 'nso', 'es', 'zh', 'tl', 'vi', 'cy', 'pl', 'ro', 'pa', 'ar', 'yue']
W = {
 'Snap it': ['Kiek dit', 'Yithwebule', 'E nke setshwantsho', 'Yifote', 'E tšee seswantšho', 'Fotografíalo', '拍一下', 'Kunan mo', 'Chụp nó',
   'Tynnwch lun', 'Pstryknij', 'Pozează-l', 'ਫੋਟੋ ਖਿੱਚੋ', 'صوّرها', '影一張'],
 'Say it': ['Sê dit', 'Yisho', 'E bue', 'Yithethe', 'E bolele', 'Dilo', '说一下', 'Sabihin mo', 'Nói nó', 'Dywedwch', 'Powiedz', 'Spune-l',
   'ਬੋਲੋ', 'قلها', '講一句'],
 'Snap or say': ['Kiek of sê', 'Thwebula noma usho', 'Nka setshwantsho kapa o bue', 'Fota okanye uthethe', 'Tšea seswantšho goba o bolele',
   'Fotografía o di', '拍照或说一句', 'Kunan o sabihin', 'Chụp hoặc nói', 'Tynnu llun neu ddweud', 'Pstryknij albo powiedz', 'Pozează sau spune',
   'ਫੋਟੋ ਖਿੱਚੋ ਜਾਂ ਬੋਲੋ', 'صوّر أو قل', '影相或者講'],
 'A photo, a sentence, or both — the app writes the advert; you check it and tap Publish.': [
   "'n Foto, 'n sin, of albei — die app skryf die advertensie; jy kyk dit na en tik Publiseer.",
   'Isithombe, umusho, noma kokubili — i-app ibhala isikhangiso; wena uyasihlola bese uthepha Shicilela.',
   'Setshwantsho, polelo, kapa tsohle — app e ngola papatso; o e hlahloba ebe o tobetsa Phatlalatsa.',
   'Ifoto, isivakalisi, okanye zombini — i-app ibhala isibhengezo; wena uyasijonga uze ucofe Papasha.',
   'Seswantšho, lefoko, goba ka bobedi — app e ngwala papatšo; o a e lekola gomme o kgotla Phatlalatša.',
   'Una foto, una frase o ambas: la app escribe el anuncio; tú lo revisas y tocas Publicar.',
   '一张照片、一句话，或两者都有——应用替你写广告；你检查一下，点“发布”。',
   'Isang litrato, isang pangungusap, o pareho — isusulat ng app ang anunsyo; titingnan mo at i-tap ang Publish.',
   'Một tấm ảnh, một câu, hoặc cả hai — ứng dụng viết quảng cáo; bạn kiểm tra rồi chạm Đăng.',
   "Llun, brawddeg, neu'r ddau — mae'r ap yn ysgrifennu'r hysbyseb; chi sy'n ei wirio ac yn tapio Cyhoeddi.",
   'Zdjęcie, zdanie albo jedno i drugie — aplikacja pisze ogłoszenie; ty je sprawdzasz i dotykasz Opublikuj.',
   'O poză, o propoziție sau amândouă — aplicația scrie anunțul; tu îl verifici și atingi Publică.',
   'ਇੱਕ ਫੋਟੋ, ਇੱਕ ਵਾਕ, ਜਾਂ ਦੋਵੇਂ — ਐਪ ਇਸ਼ਤਿਹਾਰ ਲਿਖਦੀ ਹੈ; ਤੁਸੀਂ ਜਾਂਚ ਕੇ ਪ੍ਰਕਾਸ਼ਿਤ ਕਰੋ ਦਬਾਓ।',
   'صورة أو جملة أو كلاهما — التطبيق يكتب الإعلان؛ أنت تراجعه وتنقر نشر.',
   '一張相、一句話，或者兩樣都有——App 幫你寫廣告；你睇一睇，撳「發佈」。'],
 'What kind of advert?': ['Watter soort advertensie?', 'Isikhangiso sohlobo luni?', 'Papatso ya mofuta ofe?', 'Isibhengezo sohlobo luni?',
   'Papatšo ya mohuta mang?', '¿Qué tipo de anuncio?', '哪一类广告？', 'Anong uri ng anunsyo?', 'Loại quảng cáo nào?', 'Pa fath o hysbyseb?',
   'Jaki rodzaj ogłoszenia?', 'Ce fel de anunț?', 'ਕਿਸ ਕਿਸਮ ਦਾ ਇਸ਼ਤਿਹਾਰ?', 'أي نوع من الإعلانات؟', '邊類廣告？'],
 'Or say it in one sentence': ['Of sê dit in een sin', 'Noma kusho ngomusho owodwa', 'Kapa e bue ka polelo e le nngwe', 'Okanye yithethe ngesivakalisi esinye',
   'Goba e bolele ka lefoko le tee', 'O dilo en una frase', '或者用一句话说出来', 'O sabihin sa isang pangungusap', 'Hoặc nói bằng một câu',
   'Neu dywedwch mewn un frawddeg', 'Albo powiedz to w jednym zdaniu', 'Sau spune-l într-o propoziție', 'ਜਾਂ ਇੱਕ ਵਾਕ ਵਿੱਚ ਬੋਲੋ',
   'أو قلها في جملة واحدة', '或者用一句話講'],
 'e.g. Home cleaner, Mamelodi, Tuesdays and Thursdays, R350 a day': ['bv. Huisskoonmaker, Mamelodi, Dinsdae en Donderdae, R350 per dag',
   'isib. Umhlanzi wasekhaya, Mamelodi, ngoLwesibili nangoLwesine, R350 ngosuku', 'mohl. Mohlwekisi wa lapeng, Mamelodi, Labobedi le Labone, R350 ka letsatsi',
   'umz. Umcoci wasekhaya, Mamelodi, ngoLwesibini nangoLwesine, R350 ngosuku', 'mohl. Mohlwekiši wa gae, Mamelodi, Labobedi le Labone, R350 ka letšatši',
   'p. ej. Limpiadora de casa, Mamelodi, martes y jueves, R350 al día', '例如：家庭保洁，Mamelodi，周二和周四，每天 R350',
   'hal. Tagalinis ng bahay, Mamelodi, Martes at Huwebes, R350 kada araw', 'vd. Người dọn nhà, Mamelodi, thứ Ba và thứ Năm, R350 một ngày',
   'e.e. Glanhawr cartref, Mamelodi, dydd Mawrth a dydd Iau, R350 y dydd', 'np. Sprzątaczka domowa, Mamelodi, wtorki i czwartki, R350 dziennie',
   'ex. Menajeră, Mamelodi, marțea și joia, R350 pe zi', 'ਜਿਵੇਂ: ਘਰ ਦੀ ਸਫ਼ਾਈ, Mamelodi, ਮੰਗਲਵਾਰ ਤੇ ਵੀਰਵਾਰ, R350 ਪ੍ਰਤੀ ਦਿਨ',
   'مثال: عاملة تنظيف منزلي، Mamelodi، الثلاثاء والخميس، R350 في اليوم', '例如：家居清潔，Mamelodi，星期二同星期四，每日 R350'],
 'Tap the microphone and say it, or type it. The price, the area and the days help.': [
   'Tik die mikrofoon en sê dit, of tik dit in. Die prys, die area en die dae help.',
   'Thepha imakrofoni bese uyasho, noma ukuthayiphe. Intengo, indawo nezinsuku kuyasiza.',
   'Tobetsa maekrofono ebe o e bua, kapa o e ngole. Theko, sebaka le matsatsi di a thusa.',
   'Cofa imakrofoni uze uyithethe, okanye uyichwetheze. Ixabiso, indawo neentsuku ziyanceda.',
   'Kgotla maekrofouno gomme o e bolele, goba o e thaepe. Theko, lefelo le matšatši di a thuša.',
   'Toca el micrófono y dilo, o escríbelo. El precio, la zona y los días ayudan.',
   '点麦克风说出来，或直接输入。价格、区域和日期会有帮助。',
   'I-tap ang mikropono at sabihin, o i-type. Nakakatulong ang presyo, lugar at mga araw.',
   'Chạm micro rồi nói, hoặc gõ vào. Giá, khu vực và các ngày sẽ giúp ích.',
   "Tapiwch y meicroffon a'i ddweud, neu ei deipio. Mae'r pris, yr ardal a'r dyddiau'n helpu.",
   'Dotknij mikrofonu i powiedz, albo wpisz. Cena, okolica i dni pomagają.',
   'Atinge microfonul și spune-l, sau scrie-l. Prețul, zona și zilele ajută.',
   'ਮਾਈਕ੍ਰੋਫ਼ੋਨ ਦਬਾ ਕੇ ਬੋਲੋ, ਜਾਂ ਟਾਈਪ ਕਰੋ। ਕੀਮਤ, ਇਲਾਕਾ ਅਤੇ ਦਿਨ ਮਦਦ ਕਰਦੇ ਹਨ।',
   'انقر على الميكروفون وقلها، أو اكتبها. السعر والمنطقة والأيام تساعد.',
   '撳咪高峰講出嚟，或者打字。價錢、地區同日子都有幫助。'],
 'Type it. The price, the area and the days help.': ['Tik dit in. Die prys, die area en die dae help.', 'Kuthayiphe. Intengo, indawo nezinsuku kuyasiza.',
   'E ngole. Theko, sebaka le matsatsi di a thusa.', 'Yichwetheze. Ixabiso, indawo neentsuku ziyanceda.', 'E thaepe. Theko, lefelo le matšatši di a thuša.',
   'Escríbelo. El precio, la zona y los días ayudan.', '输入即可。价格、区域和日期会有帮助。', 'I-type mo. Nakakatulong ang presyo, lugar at mga araw.',
   'Gõ vào. Giá, khu vực và các ngày sẽ giúp ích.', "Teipiwch ef. Mae'r pris, yr ardal a'r dyddiau'n helpu.", 'Wpisz. Cena, okolica i dni pomagają.',
   'Scrie-l. Prețul, zona și zilele ajută.', 'ਟਾਈਪ ਕਰੋ। ਕੀਮਤ, ਇਲਾਕਾ ਅਤੇ ਦਿਨ ਮਦਦ ਕਰਦੇ ਹਨ।', 'اكتبها. السعر والمنطقة والأيام تساعد.', '打字就得。價錢、地區同日子都有幫助。'],
 'Make my advert': ['Maak my advertensie', 'Yenza isikhangiso sami', 'Etsa papatso ya ka', 'Yenza isibhengezo sam', 'Dira papatšo ya ka', 'Crear mi anuncio',
   '生成我的广告', 'Gawin ang anunsyo ko', 'Tạo quảng cáo của tôi', 'Gwnewch fy hysbyseb', 'Stwórz moje ogłoszenie', 'Fă-mi anunțul', 'ਮੇਰਾ ਇਸ਼ਤਿਹਾਰ ਬਣਾਓ',
   'أنشئ إعلاني', '整我嘅廣告'],
 'Your phone cannot listen here — type it instead.': ['Jou foon kan nie hier luister nie — tik dit eerder in.', 'Ifoni yakho ayikwazi ukulalela lapha — kunalokho kuthayiphe.',
   'Fono ya hao e ke ke ya mamela mona — e ngole ho e na le hoo.', 'Ifowuni yakho ayikwazi ukumamela apha — yichwetheze endaweni yoko.',
   'Founu ya gago e ka se theeletše mo — e thaepe go e na le moo.', 'Tu teléfono no puede escuchar aquí; escríbelo.', '你的手机在这里无法听写——请直接输入。',
   'Hindi makakapakinig ang telepono mo dito — i-type na lang.', 'Điện thoại của bạn không nghe được ở đây — hãy gõ vào.',
   "Ni all eich ffôn wrando yma — teipiwch ef yn lle hynny.", 'Twój telefon nie może tu słuchać — wpisz zamiast tego.',
   'Telefonul tău nu poate asculta aici — scrie-l în schimb.', 'ਤੁਹਾਡਾ ਫ਼ੋਨ ਇੱਥੇ ਸੁਣ ਨਹੀਂ ਸਕਦਾ — ਇਸ ਦੀ ਬਜਾਏ ਟਾਈਪ ਕਰੋ।',
   'هاتفك لا يستطيع الاستماع هنا — اكتبها بدلًا من ذلك.', '你部電話喺度聽唔到——改為打字啦。'],
 'Listening…': ['Luister…', 'Iyalalela…', 'E a mamela…', 'Iyamamela…', 'E a theeletša…', 'Escuchando…', '正在聆听…', 'Nakikinig…', 'Đang nghe…', 'Yn gwrando…',
   'Słucham…', 'Ascult…', 'ਸੁਣ ਰਿਹਾ ਹੈ…', 'جارٍ الاستماع…', '聽緊…'],
 'The microphone is off for this site — type it instead.': ['Die mikrofoon is af vir hierdie werf — tik dit eerder in.',
   'Imakrofoni ivaliwe kule sayithi — kunalokho kuthayiphe.', 'Maekrofono e tinngwe bakeng sa sebaka sena — e ngole ho e na le hoo.',
   'Imakrofoni ivaliwe kule sayithi — yichwetheze endaweni yoko.', 'Maekrofouno e timilwe setšheng se — e thaepe go e na le moo.',
   'El micrófono está desactivado para este sitio; escríbelo.', '此网站的麦克风已关闭——请直接输入。', 'Naka-off ang mikropono para sa site na ito — i-type na lang.',
   'Micro đang tắt cho trang này — hãy gõ vào.', "Mae'r meicroffon wedi'i ddiffodd ar gyfer y wefan hon — teipiwch ef yn lle hynny.",
   'Mikrofon jest wyłączony dla tej strony — wpisz zamiast tego.', 'Microfonul este oprit pentru acest site — scrie-l în schimb.',
   'ਇਸ ਸਾਈਟ ਲਈ ਮਾਈਕ੍ਰੋਫ਼ੋਨ ਬੰਦ ਹੈ — ਇਸ ਦੀ ਬਜਾਏ ਟਾਈਪ ਕਰੋ।', 'الميكروفون مغلق لهذا الموقع — اكتبها بدلًا من ذلك.', '呢個網站嘅咪高峰關咗——改為打字啦。'],
 'Could not hear that — try again, or type it.': ['Kon dit nie hoor nie — probeer weer, of tik dit in.', 'Akuzwakalanga — zama futhi, noma kuthayiphe.',
   'Ha e a utlwa — leka hape, kapa o e ngole.', 'Ayivakalanga — zama kwakhona, okanye yichwetheze.', 'Ga se ya kwagala — leka gape, goba o e thaepe.',
   'No se oyó bien; inténtalo otra vez o escríbelo.', '没听清——再试一次，或直接输入。', 'Hindi narinig — subukan ulit, o i-type.', 'Không nghe rõ — thử lại, hoặc gõ vào.',
   "Methwyd clywed hynny — rhowch gynnig arall, neu teipiwch ef.", 'Nie udało się usłyszeć — spróbuj ponownie albo wpisz.',
   'Nu s-a auzit — încearcă din nou sau scrie-l.', 'ਸੁਣ ਨਹੀਂ ਸਕਿਆ — ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ, ਜਾਂ ਟਾਈਪ ਕਰੋ।', 'لم نسمع ذلك — حاول مرة أخرى أو اكتبها.', '聽唔到——再試一次，或者打字。'],
 'Add a photo or say one sentence.': ["Voeg 'n foto by of sê een sin.", 'Faka isithombe noma usho umusho owodwa.', 'Kenya setshwantsho kapa o bue polelo e le nngwe.',
   'Faka ifoto okanye uthethe isivakalisi esinye.', 'Tsenya seswantšho goba o bolele lefoko le tee.', 'Añade una foto o di una frase.', '添加一张照片或说一句话。',
   'Magdagdag ng litrato o sabihin ang isang pangungusap.', 'Thêm một tấm ảnh hoặc nói một câu.', 'Ychwanegwch lun neu dywedwch un frawddeg.',
   'Dodaj zdjęcie albo powiedz jedno zdanie.', 'Adaugă o poză sau spune o propoziție.', 'ਇੱਕ ਫੋਟੋ ਪਾਓ ਜਾਂ ਇੱਕ ਵਾਕ ਬੋਲੋ।', 'أضف صورة أو قل جملة واحدة.', '加一張相或者講一句。'],
 'Reading your photo…': ['Lees jou foto…', 'Ifunda isithombe sakho…', 'E bala setshwantsho sa hao…', 'Ifunda ifoto yakho…', 'E bala seswantšho sa gago…',
   'Leyendo tu foto…', '正在识别你的照片…', 'Binabasa ang litrato mo…', 'Đang đọc ảnh của bạn…', 'Yn darllen eich llun…', 'Odczytuję zdjęcie…', 'Citesc poza ta…',
   'ਤੁਹਾਡੀ ਫੋਟੋ ਪੜ੍ਹ ਰਿਹਾ ਹੈ…', 'جارٍ قراءة صورتك…', '睇緊你張相…'],
 'Reading…': ['Lees…', 'Iyafunda…', 'E a bala…', 'Iyafunda…', 'E a bala…', 'Leyendo…', '正在识别…', 'Binabasa…', 'Đang đọc…', 'Yn darllen…', 'Odczytuję…',
   'Citesc…', 'ਪੜ੍ਹ ਰਿਹਾ ਹੈ…', 'جارٍ القراءة…', '讀緊…'],
 'That did not work — nothing was lost. Please try again.': ['Dit het nie gewerk nie — niks is verloor nie. Probeer asseblief weer.',
   'Lokho akusebenzanga — akukho okulahlekile. Sicela uzame futhi.', 'Hoo ha ho a sebetsa — ha ho letho le lahlehileng. Ka kopo leka hape.',
   'Oko akusebenzanga — akukho nto ilahlekileyo. Nceda uzame kwakhona.', 'Seo ga se a šoma — ga go selo se se lahlegilego. Hle leka gape.',
   'Eso no funcionó; no se perdió nada. Inténtalo de nuevo.', '没有成功——什么都没丢失。请再试一次。', 'Hindi gumana — walang nawala. Pakisubukan ulit.',
   'Không thành công — không mất gì cả. Vui lòng thử lại.', "Ni weithiodd hynny — ni chollwyd dim. Rhowch gynnig arall.",
   'To się nie udało — nic nie przepadło. Spróbuj ponownie.', 'Nu a mers — nu s-a pierdut nimic. Te rog încearcă din nou.',
   'ਇਹ ਕੰਮ ਨਹੀਂ ਕੀਤਾ — ਕੁਝ ਵੀ ਗੁੰਮ ਨਹੀਂ ਹੋਇਆ। ਕਿਰਪਾ ਕਰਕੇ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।', 'لم ينجح ذلك — لم يُفقد شيء. يرجى المحاولة مرة أخرى.', '唔成功——冇嘢唔見咗。請再試一次。'],
 'Area from your phone — change it on the advert if you work somewhere else.': [
   'Area vanaf jou foon — verander dit op die advertensie as jy elders werk.',
   'Indawo evela efonini yakho — yishintshe esikhangisweni uma usebenza kwenye indawo.',
   'Sebaka ho tswa fonong ya hao — se fetole papatsong haeba o sebetsa sebakeng se seng.',
   'Indawo evela kwifowuni yakho — yitshintshe kwisibhengezo ukuba usebenza kwenye indawo.',
   'Lefelo go tšwa founung ya gago — le fetole papatšong ge o šoma lefelong le lengwe.',
   'Zona según tu teléfono: cámbiala en el anuncio si trabajas en otro lugar.',
   '区域来自你的手机——如果你在别处工作，请在广告上修改。',
   'Lugar mula sa telepono mo — palitan sa anunsyo kung sa ibang lugar ka nagtatrabaho.',
   'Khu vực lấy từ điện thoại của bạn — đổi trên quảng cáo nếu bạn làm ở nơi khác.',
   "Ardal o'ch ffôn — newidiwch hi ar yr hysbyseb os ydych yn gweithio yn rhywle arall.",
   'Okolica z twojego telefonu — zmień ją w ogłoszeniu, jeśli pracujesz gdzie indziej.',
   'Zona din telefonul tău — schimb-o pe anunț dacă lucrezi în altă parte.',
   'ਇਲਾਕਾ ਤੁਹਾਡੇ ਫ਼ੋਨ ਤੋਂ — ਜੇ ਤੁਸੀਂ ਕਿਤੇ ਹੋਰ ਕੰਮ ਕਰਦੇ ਹੋ ਤਾਂ ਇਸ਼ਤਿਹਾਰ ਤੇ ਬਦਲੋ।',
   'المنطقة من هاتفك — غيّرها في الإعلان إذا كنت تعمل في مكان آخر.',
   '地區嚟自你部電話——如果你喺第二度做嘢，喺廣告度改。'],
 'Nearly there — one or two things the photo and your words did not say.': [
   'Amper daar — een of twee dinge wat die foto en jou woorde nie gesê het nie.',
   'Sekuseduze — into eyodwa noma ezimbili isithombe namazwi akho angazishongo.',
   'Re haufi — ntho e le nngwe kapa tse pedi tseo setshwantsho le mantswe a hao a sa di buang.',
   'Sele kufuphi — into enye okanye ezimbini ezingathethwanga yifoto namazwi akho.',
   'Re kgauswi — selo se tee goba tše pedi tšeo seswantšho le mantšu a gago a sa di bolelago.',
   'Casi listo: una o dos cosas que la foto y tus palabras no dijeron.',
   '快好了——还有一两件事照片和你的话没有说到。',
   'Malapit na — isa o dalawang bagay na hindi nasabi ng litrato at ng mga salita mo.',
   'Sắp xong — còn một hai điều ảnh và lời bạn chưa nói.',
   "Bron yno — un neu ddau o bethau na ddywedodd y llun na'ch geiriau.",
   'Prawie gotowe — jedna lub dwie rzeczy, których zdjęcie i twoje słowa nie powiedziały.',
   'Aproape gata — unul sau două lucruri pe care poza și cuvintele tale nu le-au spus.',
   'ਲਗਭਗ ਹੋ ਗਿਆ — ਇੱਕ-ਦੋ ਗੱਲਾਂ ਜੋ ਫੋਟੋ ਅਤੇ ਤੁਹਾਡੇ ਸ਼ਬਦਾਂ ਨੇ ਨਹੀਂ ਦੱਸੀਆਂ।',
   'اقتربنا — شيء أو شيئان لم تقلهما الصورة ولا كلماتك.',
   '就快得——仲有一兩樣嘢張相同你啲話未講到。'],
 'We could not read that photo. Carry on the normal way — your photo stays on the advert.': [
   'Ons kon nie daardie foto lees nie. Gaan op die gewone manier voort — jou foto bly op die advertensie.',
   'Asikwazanga ukufunda leso sithombe. Qhubeka ngendlela ejwayelekile — isithombe sakho sihlala esikhangisweni.',
   'Ha re a kgona ho bala setshwantsho seo. Tswela pele ka tsela e tlwaelehileng — setshwantsho sa hao se dula papatsong.',
   'Asikwazanga ukuyifunda loo foto. Qhubeka ngendlela eqhelekileyo — ifoto yakho ihlala kwisibhengezo.',
   'Ga se ra kgona go bala seswantšho seo. Tšwela pele ka tsela ya ka mehla — seswantšho sa gago se dula papatšong.',
   'No pudimos leer esa foto. Sigue por el camino normal; tu foto se queda en el anuncio.',
   '我们无法识别那张照片。请按正常步骤继续——你的照片仍会留在广告上。',
   'Hindi namin mabasa ang litratong iyon. Magpatuloy sa karaniwang paraan — mananatili ang litrato mo sa anunsyo.',
   'Chúng tôi không đọc được ảnh đó. Tiếp tục theo cách thường — ảnh của bạn vẫn ở trên quảng cáo.',
   "Methwyd darllen y llun hwnnw. Ewch ymlaen y ffordd arferol — mae eich llun yn aros ar yr hysbyseb.",
   'Nie udało się odczytać tego zdjęcia. Przejdź zwykłą drogą — zdjęcie zostaje w ogłoszeniu.',
   'Nu am putut citi poza aceea. Continuă pe calea obișnuită — poza ta rămâne pe anunț.',
   'ਅਸੀਂ ਉਹ ਫੋਟੋ ਪੜ੍ਹ ਨਹੀਂ ਸਕੇ। ਆਮ ਤਰੀਕੇ ਨਾਲ ਜਾਰੀ ਰੱਖੋ — ਤੁਹਾਡੀ ਫੋਟੋ ਇਸ਼ਤਿਹਾਰ ਤੇ ਰਹਿੰਦੀ ਹੈ।',
   'تعذّر قراءة تلك الصورة. تابع بالطريقة المعتادة — صورتك تبقى في الإعلان.',
   '我哋讀唔到嗰張相。照平時嘅步驟繼續——你張相會留喺廣告度。'],
}
q = json.load(io.open(P, encoding='utf-8'))
assert q['langs'] == ORDER, q['langs']
add = {k: v for k, v in W.items() if k not in q['w']}
for k, v in W.items():
    assert len(v) == len(ORDER) and all(str(x).strip() for x in v), k
if add:
    for k, v in add.items():
        q['w'][k] = v
    shutil.copy2(P, P + '.bak-snap-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
    with io.open(P, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(q, fh, ensure_ascii=False, indent=1)
    json.load(io.open(P, encoding='utf-8'))
print('quick_i18n.json: %d word(s) added for Snap (%d in the set)' % (len(add), len(W)))

# the QUICK-I18N block in quick.html, regenerated exactly as scripts/sync_quick_roles.py generates it
src = json.load(io.open(P, encoding='utf-8'))
L = src['langs']
d = {'w': {en: dict(zip(L, v)) for en, v in src['w'].items()},
     'p': [dict(zip(['en'] + L, x)) for x in src['p']],
     'r': [dict(zip(['en'] + L, x)) for x in src['r']]}
ib = ('/* QUICK-I18N:BEGIN -- generated by scripts/sync_quick_roles.py from roles/quick_i18n.json; do not edit */\n'
      'var QI18N = %s;\n/* QUICK-I18N:END */' % json.dumps(d, ensure_ascii=False))
ipat = re.compile(r'/\* QUICK-I18N:BEGIN.*?/\* QUICK-I18N:END \*/', re.S)
html = io.open(QH, encoding='utf-8').read()
assert html.rstrip().endswith('</html>') and len(ipat.findall(html)) == 1
new = ipat.sub(lambda m: ib, html)
if new != html:
    io.open(QH, 'w', encoding='utf-8', newline='').write(new)
chk = io.open(QH, encoding='utf-8').read()
assert chk.rstrip().endswith('</html>') and ib in chk and all(k in chk for k in W)
shutil.copyfile(QH, os.path.join(MS, 'genie', 'HARNESS.html'))
print('quick.html QI18N block regenerated (%d words); HARNESS.html copied' % len(d['w']))
