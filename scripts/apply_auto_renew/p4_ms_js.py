#!/usr/bin/env python3
"""AUTO-RENEW-1 patch 4/8 -- ms.js: the tick box on every plan checkout surface, the renewal line on the
subscriber's plan card (Plans screen, Subscription screen, Wallet/Billing tab), Cancel renewal / Renew again.
Flag-dark: with /flags effective.auto_renew off, each checkout runs its old code path and no card changes."""
import os, subprocess
from patchlib import load, save, rep, root

HERE = os.path.dirname(os.path.abspath(__file__))
R = root()
P = os.path.join(R, "ms.js")
s, crlf, orig = load(P)
if "AUTO-RENEW-1" in s:
    print("ms.js already carries AUTO-RENEW-1 -- skipped")
    raise SystemExit(0)
block = open(os.path.join(HERE, "js_block.txt"), encoding="utf-8").read()
n0 = s.count("\n")

# 1. the helper block, ahead of the first checkout that uses it
s = rep(s, "async function _subSelectTier(tierId, tierLabel, usdPrice, isDowngrade) {\n",
        block + "async function _subSelectTier(tierId, tierLabel, usdPrice, isDowngrade) {\n")

# 2. Subscription screen: the top line
s = rep(s, "    : (billEnd ? 'Renews ' + billEnd : meta.usd > 0 ? 'Monthly billing' : 'No billing required');",
        "    : (billEnd ? _arBillingLine(d, billEnd) : meta.usd > 0 ? 'Monthly billing' : 'No billing required');   // AUTO-RENEW-1: 'Renews ' + billEnd unless renewal data came back")

# 3. Subscription screen: the current plan's card
s = rep(s, """      ${isDown && !isCur ? '<div style="font-size:11px;color:#f59e0b;margin-top:4px;">⏳ Takes effect at end of billing period</div>' : ''}
    `;
    container.appendChild(card);
""", """      ${isDown && !isCur ? '<div style="font-size:11px;color:#f59e0b;margin-top:4px;">⏳ Takes effect at end of billing period</div>' : ''}
    `;
    if (isCur) { const _arl = _arPlanLine(d, t.id); if (_arl) card.insertAdjacentHTML('beforeend', _arl); }   // AUTO-RENEW-1: 'Renews on <date>' + Cancel renewal
    container.appendChild(card);
""")

# 4. Wallet / Billing tab: the current plan's card
s = rep(s, """      ${isDown && (Number(t.usd) || 0) > 0 ? '<div style="font-size:11px;color:#f59e0b;margin-top:4px;">⏳ Takes effect at end of billing period</div>' : ''}
    `;
    container.appendChild(card);
""", """      ${isDown && (Number(t.usd) || 0) > 0 ? '<div style="font-size:11px;color:#f59e0b;margin-top:4px;">⏳ Takes effect at end of billing period</div>' : ''}
    `;
    if (isCur) { const _arl = _arPlanLine(d, t.id); if (_arl) card.insertAdjacentHTML('beforeend', _arl); }   // AUTO-RENEW-1: 'Renews on <date>' + Cancel renewal
    container.appendChild(card);
""")

# 5. checkout surface: Subscription screen + Billing tab (both call _subSelectTier)
s = rep(s, """  const confirmMsg = isDowngrade
    ? `Downgrade to ${tierLabel} ($${usdPrice}/mo, takes effect at end of billing period)?` + _subDownWarning(tierId)
    : `Upgrade to ${tierLabel} ($${usdPrice}/mo)?\\nYou'll be redirected to Paystack to complete payment.`;
  if (!confirm(confirmMsg)) return;

  try {
    const r = await _tsWithTerms(email, function(){ return fetch(BEA_URL + '/payment/seller-subscription/initialize?email=' +
      encodeURIComponent(email) + '&tier=' + tierId + '&callback_url=' + encodeURIComponent(window.location.origin + window.location.pathname + '?ps_sub_return=1'), { method: 'POST' }); }, { seller: true });   // BUYER-TERMS-1: a plan is a Seller's purchase
""", """  // AUTO-RENEW-1 (RUL-224): with the switch on, the checkout step carries the tick box (default ON) and the
  // renewal line; with it off, the old confirm below runs exactly as before and _arQuery(null) adds nothing.
  let _ar = null;
  if (_arOn() && _arTierReady(tierId)) {
    _ar = await _arCheckout({ tierId: tierId, label: tierLabel, usd: usdPrice,
      note: isDowngrade ? ('Takes effect at the end of your billing period.' + _subDownWarning(tierId)) : '' });
    if (!_ar) return;
  } else {
  const confirmMsg = isDowngrade
    ? `Downgrade to ${tierLabel} ($${usdPrice}/mo, takes effect at end of billing period)?` + _subDownWarning(tierId)
    : `Upgrade to ${tierLabel} ($${usdPrice}/mo)?\\nYou'll be redirected to Paystack to complete payment.`;
  if (!confirm(confirmMsg)) return;
  }

  try {
    const r = await _tsWithTerms(email, function(){ return fetch(BEA_URL + '/payment/seller-subscription/initialize?email=' +
      encodeURIComponent(email) + '&tier=' + tierId + '&callback_url=' + encodeURIComponent(window.location.origin + window.location.pathname + '?ps_sub_return=1') + _arQuery(_ar), { method: 'POST' }); }, { seller: true });   // BUYER-TERMS-1: a plan is a Seller's purchase
""")

# 6. checkout surface: the static Plans screen (setPlan)
s = rep(s, """  if (!email) { showToast('Sign in first to upgrade'); return; }
  // Initiate Paystack subscription payment
  const cb = encodeURIComponent(window.location.origin + window.location.pathname + '?ps_sub_return=1');""",
        """  if (!email) { showToast('Sign in first to upgrade'); return; }
  // AUTO-RENEW-1 (RUL-224): with the switch on, the checkout step (tick box, default ON) comes first;
  // with it off this goes straight to Paystack exactly as before.
  if (_arOn() && _arTierReady(tier)) {
    _arCheckout({ tierId: tier, label: label }).then(function(ar){ if (ar) _setPlanPay(email, tier, ar); });
    return;
  }
  _setPlanPay(email, tier, null);
}
function _setPlanPay(email, tier, _ar){
  // Initiate Paystack subscription payment
  const cb = encodeURIComponent(window.location.origin + window.location.pathname + '?ps_sub_return=1');""")
s = rep(s, """        '&tier=' + tier + '&callback_url=' + cb, { method: 'POST' }); }, { seller: true })   // BUYER-TERMS-1: a plan is a Seller's purchase""",
        """        '&tier=' + tier + '&callback_url=' + cb + _arQuery(_ar), { method: 'POST' }); }, { seller: true })   // BUYER-TERMS-1: a plan is a Seller's purchase""")

# 7. checkout surface: seller onboarding (the tier step)
s = rep(s, """  const email = sobState.email;
  if (!email) { showToast('Session expired — open your latest sign-in link.'); return; }   // SIGNIN-WORDS-1 (langt-23)

  const btn = document.getElementById('sob-p2-next');
  if (btn) { btn.disabled = true; btn.textContent = 'Redirecting…'; }
""", """  const email = sobState.email;
  if (!email) { showToast('Session expired — open your latest sign-in link.'); return; }   // SIGNIN-WORDS-1 (langt-23)

  // AUTO-RENEW-1 (RUL-224): with the switch on, the checkout step (tick box, default ON) comes first
  let _ar = null;
  if (_arOn() && _arTierReady(tier)) {
    const _t = _SUB_TIERS.find(function(x){ return x.id === tier; }) || {};
    _ar = await _arCheckout({ tierId: tier, label: _t.label || tier });
    if (!_ar) return;
  }

  const btn = document.getElementById('sob-p2-next');
  if (btn) { btn.disabled = true; btn.textContent = 'Redirecting…'; }
""")
s = rep(s, """      + '&tier='  + encodeURIComponent(tier)
      + '&callback_url=' + callbackUrl;""", """      + '&tier='  + encodeURIComponent(tier)
      + '&callback_url=' + callbackUrl + _arQuery(_ar);""")

# 8. the static Plans screen: the renewal line under the current plan
s = rep(s, """        if (btn) { btn.textContent = '✓ Current plan'; btn.className = 'plan-btn secondary'; btn.disabled = true; }
      }).catch(() => {});
  }
  goTo('plans');""", """        if (btn) { btn.textContent = '✓ Current plan'; btn.className = 'plan-btn secondary'; btn.disabled = true; }
        try { _arPlansScreenLine(d); } catch(_) {}   // AUTO-RENEW-1: nothing is drawn unless renewal data came back
      }).catch(() => {});
  }
  goTo('plans');""")

# 9. back from Paystack: say when it renews (the file spells the dash as a JS escape)
_ESC = chr(92) + "u2014"
s = rep(s, "              showToast((d.label ? d.label : 'Your new plan') + ' is active " + _ESC + " thank you.', 5000);",
        "              showToast((d.label ? d.label : 'Your new plan') + ' is active " + _ESC + " thank you.' + _arReturnNote(d), 5000);")

save(P, s, crlf, orig)
r = subprocess.run(["node", "--check", P], capture_output=True, text=True)
assert r.returncode == 0, "node --check failed:\n" + r.stderr[-800:]
print("ms.js OK (node --check); lines %d -> %d" % (n0, s.count("\n")))
