"""verify_auto_renew.py -- AUTO-RENEW-1 (RUL-224): the RENDERED proof, on the rig.

The real app (marketsquare.html + ms.js + bea_main.py, security gate on) in headless Chromium at 412x915,
signed in as QA accounts (dmcontiki2+qa-...), against a throwaway database and the local Paystack STAND-IN.
Never David's Chrome, never his account, never the live site (IDENTITY-GUARD-1): every request that is not
to the rig itself is refused in the browser.

Each step asserts what a person would see, then saves a screenshot.
"""
import sys, os, json, re, time
sys.path.insert(0, '/home/claude/rigkit')
from rig_lib import *
from playwright.sync_api import sync_playwright

SHOTS = os.environ.get('SHOT_DIR', '/home/claude/shots/AUTO_RENEW_shots')
os.makedirs(SHOTS, exist_ok=True)
QA1 = 'dmcontiki2+qa-autorenew@gmail.com'       # buys Starter with the tick box ON
QA2 = 'dmcontiki2+qa-monthly@gmail.com'         # buys Starter with the tick box OFF
fails, log = [], []
def check(ok, msg):
    log.append(('OK  ' if ok else 'FAIL') + ' ' + msg); print(('  [OK] ' if ok else '  [X]  ') + msg)
    if not ok: fails.append(msg)

for em, nm in ((QA1, 'QA Auto Renew'), (QA2, 'QA Month By Month')):
    sql("INSERT INTO users (email, name, eula_accepted_at) VALUES (?, ?, '2026-10-12T00:00:00Z') ON CONFLICT(email) DO NOTHING", em, nm)
sql("UPDATE launch_switches SET auto_renew=0 WHERE id=1")

def context(br, email, demo=False):
    ctx = br.new_context(viewport={'width': 412, 'height': 915}, is_mobile=True, has_touch=True, device_scale_factor=2)
    ck = [{'name': 'ts_review', 'value': review_token(), 'domain': '127.0.0.1', 'path': '/'}]
    if email: ck.append({'name': 'ts_user', 'value': user_token(email), 'domain': '127.0.0.1', 'path': '/'})
    ctx.add_cookies(ck)
    if email: ctx.add_init_script("try{localStorage.setItem('ms_aa_email', '%s');}catch(e){}" % email)
    # nothing leaves the rig: only 127.0.0.1 (the app, the stand-in) and the two font hosts are answered
    def gate(route):
        u = route.request.url
        if u.startswith('http://127.0.0.1:') or 'fonts.googleapis.com' in u or 'fonts.gstatic.com' in u or u.startswith('data:'):
            return route.continue_()
        return route.abort()
    ctx.route('**/*', gate)
    return ctx

def boot(page, path='/'):
    page.goto(ORIGIN + path, wait_until='domcontentloaded')
    page.wait_for_function("typeof goTo==='function' && typeof openPlans==='function' && window.FEATURES && window.FEATURES._loaded", timeout=40000)
    page.wait_for_timeout(1200)

def quiet(page):
    """hide a toast that is not the subject of the picture"""
    page.evaluate("(function(){var t=document.getElementById('toast'); if(t) t.classList.remove('show');})()")
def shot(page, name, sel=None):
    p = os.path.join(SHOTS, name)
    if sel: page.locator(sel).first.scroll_into_view_if_needed()
    page.wait_for_timeout(350); page.screenshot(path=p); print('     shot ' + name)
def text(page, sel): return page.evaluate("(s)=>{var e=document.querySelector(s);return e?e.innerText:null}", sel)
def sub_screen(page):
    page.evaluate("openSubscriptionScreen('myspace')")
    page.wait_for_function("document.querySelectorAll('#sub-screen-plans > div').length >= 4", timeout=15000); page.wait_for_timeout(500)
def billing_tab(page):
    page.evaluate("goTo('myspace'); msTab('billing', document.querySelectorAll('.ms-tab')[ [...document.querySelectorAll('.ms-tab')].findIndex(t=>/Billing/.test(t.textContent)) ])")
    page.wait_for_function("document.querySelectorAll('#billing-plans-list > div').length >= 4", timeout=15000); page.wait_for_timeout(500)
def plans_screen(page):
    page.evaluate("openPlans('dashboard')"); page.wait_for_timeout(1500)

with sync_playwright() as p:
    br = p.chromium.launch(executable_path='/opt/pw-browsers/chromium', args=['--no-sandbox'])
    ctx = context(br, QA1); page = ctx.new_page()
    errs, inits = [], []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.on('request', lambda r: inits.append(r.url) if '/payment/seller-subscription/initialize' in r.url else None)

    # ════════ 1. SWITCH OFF -- today's flow ════════
    print('1 -- switch OFF: the plan checkout is today\'s')
    boot(page)
    check(page.evaluate("window.FEATURES.auto_renew") is False, 'the app reads the switch as OFF')
    plans_screen(page); quiet(page)
    shot(page, '01_off_plans_screen.png', '#plan-card-starter')
    check(page.locator('.ar-plan-line').count() == 0, 'OFF: no renewal line anywhere on the Plans screen')
    with page.expect_navigation(url=re.compile(r'127\.0\.0\.1:8999/pay/'), timeout=20000):
        page.click('#plan-btn-starter')
    check(len(inits) == 1 and 'auto_renew' not in inits[-1] and 'channel=' not in inits[-1], 'OFF: tapping Starter goes straight to Paystack with today\'s request (no tick box sent)')
    check(page.locator('#oneoff-note').count() == 1 and page.locator('#sub-note').count() == 0, 'OFF: the payment page is a single payment, not a subscription')
    shot(page, '02_off_payment_page_one_payment.png')
    page.click('#pay-cancel'); page.wait_for_function("typeof goTo==='function'", timeout=30000); page.wait_for_timeout(1500)
    boot(page); sub_screen(page); quiet(page)
    shot(page, '03_off_subscription_screen.png')
    dialogs = []
    def on_dialog(d):
        dialogs.append(d.message); d.dismiss()
    page.on('dialog', on_dialog)
    page.locator('#sub-screen-plans button', has_text='Upgrade').first.click(); page.wait_for_timeout(800)
    check(len(dialogs) == 1 and dialogs[0] == "Upgrade to Starter ($5/mo)?\nYou'll be redirected to Paystack to complete payment.",
          'OFF: the Subscription screen asks today\'s question, word for word: %r' % (dialogs[:1],))
    check(page.locator('#ar-checkout').count() == 0, 'OFF: no tick box, no checkout sheet')
    page.remove_listener('dialog', on_dialog)
    st = standin()
    check(not st['plans'] and not st['subs'] and all(t['plan'] is None for t in st['tx'].values()), 'OFF: Paystack holds no plan and no subscription')

    # ════════ 2. DAVID ARMS THE SWITCH on the +1 page ════════
    print('2 -- arming: the +1 page switch')
    actx = context(br, None); apage = actx.new_page()
    actx.add_init_script("try{sessionStorage.setItem('ms_admin_token', '%s');}catch(e){}" % admin_token())
    apage.goto(ORIGIN + '/dashboard.html', wait_until='domcontentloaded'); apage.wait_for_timeout(2500)
    apage.evaluate("switchView('launch')"); apage.wait_for_timeout(2500)
    row = apage.locator('.ls-row', has=apage.locator('#ls_m_autorenew'))
    check(row.count() == 1 and 'Automatic plan renewal' in row.inner_text(), 'the +1 page shows the switch: "Automatic plan renewal"')
    check(apage.evaluate("document.getElementById('ls_m_autorenew').checked") is False, 'it ships OFF')
    row.scroll_into_view_if_needed(); apage.wait_for_timeout(400)
    apage.screenshot(path=os.path.join(SHOTS, '04_dashboard_switch_off.png')); print('     shot 04_dashboard_switch_off.png')
    row.locator('.ls-sw').click(); apage.wait_for_timeout(4000)
    fl = api('GET', '/flags')[1]
    check(fl['auto_renew'] is True and fl['auto_renew_tiers'] == ['starter', 'pro'], 'one tap arms it: /flags auto_renew true, Starter + Pro ready')
    st = standin()
    check(sorted((x['name'], x['amount'], x['interval']) for x in st['plans']) ==
          [('TrustSquare Agency Pro seat', 9000, 'monthly'), ('TrustSquare Pro', 36000, 'monthly'), ('TrustSquare Starter', 9000, 'monthly')],
          'arming made the three monthly plans at Paystack, once')
    apage.evaluate("lsLoad && lsLoad()") if apage.evaluate("typeof lsLoad==='function'") else None
    apage.wait_for_timeout(1500); row.scroll_into_view_if_needed(); apage.wait_for_timeout(400)
    check('Starter, Pro' in row.inner_text(), 'the row now says which plans are ready: %r' % row.inner_text()[-70:])
    apage.screenshot(path=os.path.join(SHOTS, '05_dashboard_switch_armed.png')); print('     shot 05_dashboard_switch_armed.png')

    # ════════ 3. SWITCH ON -- the checkout step with the tick box ════════
    print('3 -- switch ON: the tick box (default ON) on the Plans screen checkout')
    boot(page)
    check(page.evaluate("window.FEATURES.auto_renew") is True, 'the app reads the switch as ON')
    plans_screen(page); quiet(page)
    page.locator('#plan-btn-starter').scroll_into_view_if_needed(); page.click('#plan-btn-starter'); page.wait_for_selector('#ar-checkout', timeout=8000)
    check(page.evaluate("document.getElementById('ar-tick').checked && !document.getElementById('ar-tick').disabled") is True, 'the tick box is there and ticked by default')
    check(text(page, '#ar-tick-label') == 'Renew automatically each month — cancel any time with one tap.', 'its label is the ruled wording')
    check(text(page, '#ar-line') == 'Renews automatically every month until you cancel. Cancelling takes one tap and your paid days still run to the end.',
          'the acceptance line under it is the ruled disclosure')
    shot(page, '06_on_checkout_tick_box_on.png')
    page.click('#ar-ch-other'); page.wait_for_timeout(300)
    check(page.evaluate("document.getElementById('ar-tick').disabled && !document.getElementById('ar-tick').checked") is True
          and 'Automatic renewal needs a card payment' in text(page, '#ar-line'), 'not paying by card: the tick box is shown disabled with "Automatic renewal needs a card payment"')
    shot(page, '07_on_checkout_not_a_card.png')
    page.click('#ar-ch-card'); page.wait_for_timeout(200)
    check(page.evaluate("document.getElementById('ar-tick').checked") is True, 'back on Card the tick box is ticked again')
    page.click('#ar-tick'); page.wait_for_timeout(200)
    check(page.evaluate("document.getElementById('ar-tick').checked") is False and text(page, '#ar-line').startswith('One payment for 30 days'), 'unticked: it says one payment for 30 days')
    shot(page, '08_on_checkout_tick_box_off.png')
    page.click('#ar-tick'); page.wait_for_timeout(200)
    n_init = len(inits)
    with page.expect_navigation(url=re.compile(r'127\.0\.0\.1:8999/pay/'), timeout=20000):
        page.click('#ar-go')
    check(len(inits) == n_init + 1 and 'auto_renew=1' in inits[-1] and 'channel=card' in inits[-1], 'Continue sends the tick box with the checkout request')
    check(page.locator('#sub-note').count() == 1 and 'TrustSquare Starter' in text(page, '#sub-note'), 'the payment page is now a monthly subscription on the Starter plan')
    shot(page, '09_on_payment_page_subscription.png')
    page.click('#pay-card')
    page.wait_for_function("typeof goTo==='function' && typeof openPlans==='function'", timeout=40000)
    page.wait_for_function("(document.getElementById('toast')||{}).textContent && /is active/.test(document.getElementById('toast').textContent)", timeout=20000)
    toast = text(page, '#toast')
    check('Starter is active' in toast and 'It renews on' in toast, 'back in the app she is told the plan is active and when it renews: %r' % toast)
    shot(page, '10_on_back_in_app_plan_active.png')
    page.wait_for_timeout(3500)                                # let the stand-in's webhooks land
    st = standin(); subs = [s for s in st['subs'] if s['email'] == QA1]
    check(len(subs) == 1 and subs[0]['status'] == 'active', 'a Paystack subscription exists for the QA customer (stand-in): %s' % (subs[0]['subscription_code'] if subs else None))
    u = sql("SELECT seller_tier, slot_limit, billing_period_end, auto_renew, paystack_subscription_code AS code FROM users WHERE email=?", QA1)[0]
    check(u['seller_tier'] == 'starter' and u['code'] == subs[0]['subscription_code'] and u['auto_renew'] == 1, 'her account is on Starter with that subscription stored')
    end1 = u['billing_period_end']

    print('4 -- the subscriber\'s plan card: Renews on <date> + Cancel renewal, on all three surfaces')
    boot(page); sub_screen(page); quiet(page)
    line = text(page, '#sub-screen-plans .ar-plan-line') or ''
    check(line.startswith('Renews on') and 'Cancel renewal' in line, 'Subscription screen: %r' % line.replace('\n', ' | '))
    check((text(page, '#sub-screen-billing') or '').startswith('Renews on '), 'the header line says: %r' % text(page, '#sub-screen-billing'))
    shot(page, '11_on_subscription_screen_renews_on.png')
    billing_tab(page); quiet(page)
    line = text(page, '#billing-plans-list .ar-plan-line') or ''
    check(line.startswith('Renews on') and 'Cancel renewal' in line, 'Wallet (Billing tab): %r' % line.replace('\n', ' | '))
    shot(page, '12_on_wallet_billing_renews_on.png', '#billing-plans-list .ar-plan-line')
    plans_screen(page); quiet(page)
    line = text(page, '#plan-card-starter .ar-plan-line') or ''
    check(line.startswith('Renews on') and 'Cancel renewal' in line, 'Plans screen: %r' % line.replace('\n', ' | '))
    shot(page, '13_on_plans_screen_renews_on.png', '#plan-card-starter .ar-plan-line')

    print('5 -- Cancel renewal: one tap')
    sub_screen(page); quiet(page)
    page.locator('#sub-screen-plans .ar-plan-line button', has_text='Cancel renewal').click()
    page.wait_for_function("/Renewal cancelled/.test((document.getElementById('toast')||{}).textContent||'')", timeout=15000)
    page.wait_for_function("/Runs to/.test((document.querySelector('#sub-screen-plans .ar-plan-line')||{}).innerText||'')", timeout=15000)
    line = text(page, '#sub-screen-plans .ar-plan-line')
    check('Runs to' in line and 'then Free' in line and 'Renew again' in line, 'after one tap the card says: %r' % line.replace('\n', ' | '))
    check('Nothing more will be charged' in text(page, '#toast'), 'and she is told: %r' % text(page, '#toast'))
    shot(page, '14_on_renewal_cancelled.png')
    st = standin(); s1 = [s for s in st['subs'] if s['email'] == QA1][0]
    u = sql("SELECT seller_tier, billing_period_end, auto_renew FROM users WHERE email=?", QA1)[0]
    check(s1['status'] == 'non-renewing', 'the Paystack subscription is disabled (stand-in status: %s)' % s1['status'])
    check(u['auto_renew'] == 0 and u['seller_tier'] == 'starter' and u['billing_period_end'] == end1, 'her plan and its end date are untouched')
    page.wait_for_timeout(3000); quiet(page)
    shot(page, '14b_on_renewal_cancelled_card.png', '#sub-screen-plans .ar-plan-line')
    page.locator('#sub-screen-plans .ar-plan-line button', has_text='Renew again').click()
    page.wait_for_function("/Renews on/.test((document.querySelector('#sub-screen-plans .ar-plan-line')||{}).innerText||'')", timeout=15000)
    check([s for s in standin()['subs'] if s['email'] == QA1][0]['status'] == 'active', 'Renew again switches the same subscription back on')
    shot(page, '15_on_renew_again.png')

    print('6 -- a renewal, then a failed renewal')
    r = standin('/__standin/renew', {'code': s1['subscription_code'], 'ok': True, 'paid_at': end1}); time.sleep(2.5)
    u = sql("SELECT billing_period_end, renewal_failed_at FROM users WHERE email=?", QA1)[0]
    check(u['billing_period_end'] > end1 and u['billing_period_end'][:10] != end1[:10], 'Paystack\'s renewal charge moved the end date on by 30 days: %s -> %s' % (end1[:10], u['billing_period_end'][:10]))
    standin('/__standin/renew', {'code': s1['subscription_code'], 'ok': True, 'paid_at': end1}) if False else None
    boot(page); sub_screen(page); quiet(page)
    shot(page, '16_on_after_a_renewal.png')
    standin('/__standin/renew', {'code': s1['subscription_code'], 'ok': False}); time.sleep(2.5)
    boot(page); sub_screen(page); quiet(page)
    line = text(page, '#sub-screen-plans .ar-plan-line') or ''
    check('did not go through' in line and 'Pay again' in line and 'Cancel renewal' not in line, 'after a failed renewal the card says so and offers Pay again: %r' % line.replace('\n', ' | '))
    shot(page, '17_on_renewal_failed.png')
    page.locator('#sub-screen-plans .ar-plan-line button', has_text='Pay again').click(); page.wait_for_selector('#ar-checkout', timeout=8000)
    check('Starter plan' in text(page, '#ar-checkout') and page.evaluate("document.getElementById('ar-tick').checked") is True, 'Pay again opens the same checkout step for her plan')
    page.click('#ar-no'); page.wait_for_timeout(300)

    # ════════ 4. tick box OFF = one-off, on the Subscription-screen surface ════════
    print('7 -- tick box OFF on the Subscription screen surface: one payment, no subscription')
    ctx2 = context(br, QA2); page2 = ctx2.new_page(); inits2 = []
    page2.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page2.on('request', lambda r: inits2.append(r.url) if '/payment/seller-subscription/initialize' in r.url else None)
    boot(page2); sub_screen(page2); quiet(page2)
    page2.locator('#sub-screen-plans button', has_text='Upgrade').first.click(); page2.wait_for_selector('#ar-checkout', timeout=8000)
    check(page2.evaluate("document.getElementById('ar-tick').checked") is True, 'the same checkout step, ticked by default, on the Subscription screen')
    shot(page2, '18_on_subscription_screen_checkout.png')
    page2.click('#ar-tick'); page2.wait_for_timeout(200)
    with page2.expect_navigation(url=re.compile(r'127\.0\.0\.1:8999/pay/'), timeout=20000):
        page2.click('#ar-go')
    check('auto_renew' not in inits2[-1], 'unticked: today\'s request is sent (nothing added)')
    check(page2.locator('#oneoff-note').count() == 1, 'the payment page is a single payment')
    page2.click('#pay-card')
    page2.wait_for_function("typeof goTo==='function' && typeof openPlans==='function'", timeout=40000); page2.wait_for_timeout(4500)
    check(not [s for s in standin()['subs'] if s['email'] == QA2], 'no subscription was created for her at Paystack')
    boot(page2); sub_screen(page2); quiet(page2)
    line = text(page2, '#sub-screen-plans .ar-plan-line') or ''
    check(line.startswith('Runs to') and 'then Free' in line and 'Cancel renewal' not in line, 'her card says: %r' % line.replace('\n', ' '))
    shot(page2, '19_on_month_by_month_runs_to.png')
    print('8 -- the onboarding surface carries the same tick box')
    page2.evaluate("(function(){ sobState.email='%s'; sobState.selectedTier='pro'; sobContinueFromTier(); return 1; })()" % QA2); page2.wait_for_selector('#ar-checkout', timeout=8000)
    check(page2.evaluate("document.getElementById('ar-tick').checked") is True and 'Pro plan' in text(page2, '#ar-checkout'), 'the seller-onboarding tier step opens the same checkout, ticked by default')
    shot(page2, '20_on_onboarding_checkout.png')
    page2.click('#ar-no'); page2.wait_for_timeout(300)
    check(page2.locator('#ar-checkout').count() == 0, '"Not now" closes it and nothing is charged')

    # ════════ 5. DEMO_MODE: the new calls are guarded ════════
    print('9 -- demo mode: no call is made')
    dctx = context(br, QA1); dpage = dctx.new_page(); dcalls = []
    dpage.on('request', lambda r: dcalls.append(r.url) if '/seller-subscription/cancel' in r.url or '/seller-subscription/resume' in r.url else None)
    boot(dpage, '/?demo=1')
    check(dpage.evaluate("DEMO_MODE") is True, 'the app is in demo mode')
    dpage.evaluate("(function(){ _arCancelRenewal(null); _arRenewAgain(null); _arRefresh(); return 1; })()"); dpage.wait_for_timeout(1200)
    check(not dcalls and 'demo' in (text(dpage, '#toast') or '').lower(), 'Cancel renewal / Renew again make no call in demo mode and say why: %r' % text(dpage, '#toast'))
    shot(dpage, '21_demo_mode_guard.png')

    real = [e for e in errs if 'r2Fallback' not in e]
    check(not real, 'no page errors in any step: %s' % real[:3])
    br.close()

open(os.path.join(SHOTS, 'verify_log.txt'), 'w').write(
    'AUTO-RENEW-1 rendered proof on the rig (headless Chromium 412x915, QA accounts, Paystack STAND-IN - not Paystack)\n'
    + time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()) + '\n\n' + '\n'.join(log) + '\n\n'
    + ('FAILED: %d' % len(fails) if fails else 'ALL RENDERED CHECKS PASS') + '\n')
print()
if fails:
    print('FAILED: %d' % len(fails)); [print('  - ' + f) for f in fails]; sys.exit(1)
print('ALL RENDERED CHECKS PASS (412x915)')
