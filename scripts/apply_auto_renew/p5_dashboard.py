#!/usr/bin/env python3
"""AUTO-RENEW-1 patch 5/8 -- dashboard.server.html: the +1 page switch (David arms it) and four renewal tiles."""
import os, re, subprocess, tempfile
from patchlib import load, save, rep, root

R = root()
P = os.path.join(R, "dashboard.server.html")
s, crlf, orig = load(P)
if "ls_m_autorenew" in s:
    print("dashboard.server.html already carries the auto-renew switch -- skipped")
    raise SystemExit(0)

# 1. the switch row, after the Regulars limits row
s = rep(s, '''<label class="ls-sw"><input type="checkbox" id="ls_m_circle" onchange="lsRender()"><span class="ls-sl"></span></label></div>
''', '''<label class="ls-sw"><input type="checkbox" id="ls_m_circle" onchange="lsRender()"><span class="ls-sl"></span></label></div>
   <div class="ls-row"><div class="ls-tip" data-tip="OFF: a paid plan is one payment for 30 days, exactly as today. Nothing renews.
ON: the plan checkout shows one tick box, already ticked: Renew automatically each month. Left ticked, Paystack charges the same card every month and the plan carries on. Unticked, it is one payment for 30 days as today. A subscriber sees Renews on (date) and a one-tap Cancel renewal; after cancelling, the paid days still run to the end.
Implication: switching on makes the monthly plans at Paystack once (Starter, Pro, Agency Pro seat). Switching off again only stops NEW renewals being started - a seller who already renews keeps renewing and can always cancel. Reversible at any time; no deploy. RUL-224."><div class="ls-nm">Automatic plan renewal</div><div class="ls-ds">paid plans renew every month on the checkout card &middot; one tick box for month-by-month &middot; plans ready: <span id="ls-ar-plans">&hellip;</span></div></div><label class="ls-sw"><input type="checkbox" id="ls_m_autorenew" onchange="lsRender()"><span class="ls-sl"></span></label></div>
''')

# 2. state, id map, server read, save body
s = rep(s, "photo_replace_request:1,circle_caps:0,verified_tier:0,", "photo_replace_request:1,circle_caps:0,auto_renew:0,verified_tier:0,")
s = rep(s, "ls_m_circle:'circle_caps',ls_v_tier:'verified_tier',", "ls_m_circle:'circle_caps',ls_m_autorenew:'auto_renew',ls_v_tier:'verified_tier',")
s = rep(s, "S.circle_caps=f.circle_caps?1:0; ",
        "S.circle_caps=f.circle_caps?1:0; S.auto_renew=f.auto_renew?1:0; "
        "try{var _arp=document.getElementById('ls-ar-plans'); if(_arp)_arp.textContent=f.auto_renew?(((f.auto_renew_tiers||[]).map(function(t){return t.charAt(0).toUpperCase()+t.slice(1);}).join(', '))||'none yet (retried every hour)'):'made when you switch it on';}catch(_e){} ")
s = rep(s, "photo_replace_request:!!S.photo_replace_request,circle_caps:!!S.circle_caps};",
        "photo_replace_request:!!S.photo_replace_request,circle_caps:!!S.circle_caps,auto_renew:!!S.auto_renew};")

# 2b. like the Regulars limits switch, this one is never locked by launch mode -- it has nothing to do with it
s = rep(s, "e.disabled=(S.mode==='launch' && id!=='ls_m_fault' && id!=='ls_m_circle');",
        "e.disabled=(S.mode==='launch' && id!=='ls_m_fault' && id!=='ls_m_circle' && id!=='ls_m_autorenew');")

# 3. the launch-metrics tiles
s = rep(s, """  var ORDER = ['paystack_balance','fnb_balance','subscriptions','complaints_24h',
               'sellers','buyers','intro_requests','intro_accepts'];""",
        """  var ORDER = ['paystack_balance','fnb_balance','subscriptions','complaints_24h',
               'sellers','buyers','intro_requests','intro_accepts',
               /* AUTO-RENEW-1 (RUL-224): renewals this month, failed, cancelled, share of paid plans that renew */
               'renewals_month','renewals_failed_month','renewals_cancelled_month','auto_renew_share'];""")

assert s.rstrip().endswith("</html>"), "dashboard tail lost"
# every inline script must still parse
tmpd = tempfile.mkdtemp()
n = 0
for i, m in enumerate(re.finditer(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", s, re.S)):
    body = m.group(1)
    if not body.strip() or "application/json" in m.group(0)[:200] or "application/ld+json" in m.group(0)[:200]:
        continue
    f = os.path.join(tmpd, "s%d.js" % i)
    open(f, "w", encoding="utf-8").write(body)
    r = subprocess.run(["node", "--check", f], capture_output=True, text=True)
    assert r.returncode == 0, "inline script %d no longer parses:\n%s" % (i, r.stderr[-600:])
    n += 1
save(P, s, crlf, orig)
print("dashboard.server.html OK (%d inline scripts parse, tail intact)" % n)
