#!/usr/bin/env python3
"""apply_quick_close_words.py -- FIND-CLOSE-1 words (5 Oct 2026, RUL-207). Claude's drafts (RUL-160 / RUL-204) for all 15
columns of roles/quick_i18n.json; readers' grammar flags drive corrections. Idempotent. Then run scripts/sync_quick_roles.py."""
import io, json, os, shutil, datetime
MS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(MS, 'roles', 'quick_i18n.json')
ORDER = ['af', 'zu', 'st', 'xh', 'nso', 'es', 'zh', 'tl', 'vi', 'cy', 'pl', 'ro', 'pa', 'ar', 'yue']
W = {
 'Close matches': ['Byna wat jy soek', 'Okusondelene', 'Tse haufi', 'Ezikufuphi', 'Tše kgauswi', 'Coincidencias cercanas', '相近结果', 'Malapit na tugma', 'Kết quả gần đúng', 'Cyfatebiaethau agos', 'Podobne wyniki', 'Potriviri apropiate', 'ਨੇੜਲੇ ਮੇਲ', 'نتائج قريبة', '相近結果'],
 'Close match': ['Byna', 'Kusondelene', 'Haufi', 'Kufutshane', 'Kgauswi', 'Casi', '相近', 'Malapit', 'Gần đúng', 'Bron', 'Prawie', 'Aproape', 'ਲਗਭਗ', 'قريب', '相近'],
 'close matches and AI examples': ['byna wat jy soek en KI-voorbeelde', 'okusondelene nezibonelo ze-AI', 'tse haufi le mehlala ya AI', 'ezikufuphi nemizekelo ye-AI', 'tše kgauswi le mehlala ya AI', 'coincidencias cercanas y ejemplos de IA', '相近结果和 AI 示例', 'malapit na tugma at mga halimbawa ng AI', 'kết quả gần đúng và ví dụ AI', 'cyfatebiaethau agos ac enghreifftiau AI', 'podobne wyniki i przykłady AI', 'potriviri apropiate și exemple AI', 'ਨੇੜਲੇ ਮੇਲ ਅਤੇ AI ਉਦਾਹਰਣਾਂ', 'نتائج قريبة وأمثلة بالذكاء الاصطناعي', '相近結果同 AI 例子'],
 'Not exactly what you asked — the difference is shown on each.': ['Nie presies wat jy gevra het nie — die verskil staan op elkeen.', 'Akukhona ngqo obukucelile — umehluko ukhonjiswe kuyileso naleso.', 'Ha se hantle seo o se kopileng — phapang e bontshitswe ho e nngwe le e nngwe.', 'Asiyonto oyicelileyo ngqo — umahluko uboniswe kwinye nenye.', 'Ga se seo o se kgopetšego ka nepo — phapano e bontšhitšwe go se sengwe le se sengwe.', 'No es exactamente lo que pediste: la diferencia se muestra en cada uno.', '不完全符合你的要求——每条都标出了不同之处。', 'Hindi eksaktong hiningi mo — nakasaad sa bawat isa ang pagkakaiba.', 'Không hoàn toàn như bạn tìm — điểm khác được ghi trên từng tin.', 'Ddim yn union beth ofynnaist ti — mae’r gwahaniaeth i’w weld ar bob un.', 'Nie dokładnie to, czego szukasz — różnica jest podana przy każdym.', 'Nu exact ce ai cerut — diferența apare la fiecare.', 'ਬਿਲਕੁਲ ਉਹ ਨਹੀਂ ਜੋ ਤੁਸੀਂ ਮੰਗਿਆ — ਹਰ ਇੱਕ ’ਤੇ ਫ਼ਰਕ ਦਿਖਾਇਆ ਗਿਆ ਹੈ।', 'ليست مطابقة تمامًا لطلبك — الفرق مبيّن على كل واحدة.', '唔係完全啱你要嘅 — 每個都寫咗分別。'],
}
q = json.load(io.open(P, encoding='utf-8'))
assert q['langs'] == ORDER, q['langs']
add = {k: v for k, v in W.items() if k not in q['w']}
if add:
    for k, v in add.items():
        assert len(v) == len(ORDER), k
        q['w'][k] = v
    shutil.copy2(P, P + '.bak-closewords-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
    with io.open(P, 'w', encoding='utf-8', newline='\n') as fh: json.dump(q, fh, ensure_ascii=False, indent=1)
    json.load(io.open(P, encoding='utf-8'))
print('quick_i18n.json: %d word(s) added' % len(add))
