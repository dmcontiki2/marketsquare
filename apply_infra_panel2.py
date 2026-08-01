#!/usr/bin/env python3
"""INFRA-PANEL-2 (1 Aug 2026) — idempotent dashboard patcher.

Root-cause fix for the Infrastructure card sitting silently on "Loading checks…":
  1. The admin PIN gate dispatches `ms-admin-auth` on every successful sign-in
     (stored-token verify, PIN login, PIN change) via hideGate().
  2. The infra card listens for that event and reloads instantly on sign-in.
  3. A 401 renders a LOUD amber "Checks paused" row state + Retry — the static
     "Loading checks…" placeholder can never be the resting state again.
  4. Network failure with nothing cached renders a red "Checks could not load" + Retry.
  5. Token-aware bootstrap + 5-minute poll: no doomed 401 round-trips while signed out.

Runs in deploy_bit_monitoring.bat step [2c/6], AFTER apply_bit_panel.py and
apply_ai_provider_card.py, so the fix survives the bat's server->local pre-pull
(the pull is exactly how the first application of this fix got clobbered).

Usage: python apply_infra_panel2.py <dashboard.server.html>
Exit 0 = applied or already present.  Exit 1 = an anchor was not found — tell Claude.
"""
import sys

MARK = 'ms-admin-auth'

def main(path):
    raw = open(path, 'rb').read()
    crlf = raw.count(b'\r\n') > 0
    src = raw.decode('utf-8')
    if crlf:
        src = src.replace('\r\n', '\n')

    if MARK in src:
        print('  [OK] INFRA-PANEL-2 already present - nothing to do.')
        return 0

    edits = []

    # 1. Gate: dispatch ms-admin-auth on every successful auth path.
    edits.append((
"""function hideGate(){
    gate.style.display = 'none';
    _tempPin = null;
  }""",
"""function hideGate(){
    gate.style.display = 'none';
    _tempPin = null;
    /* INFRA-PANEL-2 (1 Aug 2026): announce successful admin auth so token-gated
       cards (Infrastructure checks, etc.) reload themselves instead of sitting
       on their "Loading…" placeholder until the next 5-minute poll. */
    try{ document.dispatchEvent(new Event('ms-admin-auth')); }catch(e){}
  }"""))

    # 2. Loud paused/failed renderers + 401 branch swap.
    edits.append((
"""window.infraLoad = function(one){""",
"""/* INFRA-PANEL-2 (1 Aug 2026): the checks must load or fail LOUDLY — never sit on
   "Loading checks…". A 401 (no PIN yet / session expired) renders this paused state,
   and the gate's ms-admin-auth event re-runs the load the moment sign-in succeeds. */
window.infraAuthWait = function(){
  var box=document.getElementById('infra-rows');
  if(box) box.innerHTML='<div style="display:flex;gap:10px;align-items:center;padding:9px 0;font-size:12px;">'
    +'<span style="width:9px;height:9px;border-radius:50%;background:#eab308;flex:0 0 auto;"></span>'
    +'<span style="flex:1;color:#eab308;font-weight:600;">Checks paused — admin session signed out.</span>'
    +'<span style="color:var(--muted);font-size:11px;">resumes automatically after PIN sign-in</span>'
    +'<button type="button" onclick="infraLoad()" style="flex:0 0 auto;padding:5px 10px;border-radius:7px;border:1px solid var(--border);background:var(--surface2);color:var(--text);font-size:11px;cursor:pointer;font-family:inherit">Retry</button>'
    +'</div>';
  var out=document.getElementById('infra-out'); if(out) out.textContent='';
};
window.infraFailLoud = function(msg){
  var box=document.getElementById('infra-rows');
  if(box && !window._infraD) box.innerHTML='<div style="display:flex;gap:10px;align-items:center;padding:9px 0;font-size:12px;">'
    +'<span style="width:9px;height:9px;border-radius:50%;background:#ef4444;flex:0 0 auto;"></span>'
    +'<span style="flex:1;color:#ef4444;font-weight:600;">Checks could not load.</span>'
    +'<button type="button" onclick="infraLoad()" style="flex:0 0 auto;padding:5px 10px;border-radius:7px;border:1px solid var(--border);background:var(--surface2);color:var(--text);font-size:11px;cursor:pointer;font-family:inherit">Retry</button>'
    +'</div>';
  var out=document.getElementById('infra-out'); if(out) out.textContent=msg;
};
window.infraLoad = function(one){"""))

    edits.append((
"""   .then(function(r){ if(r.status===401){ if(out) out.textContent='Admin session expired — reload + PIN.'; return null; } return r.json(); })
   .then(function(d){ if(!d) return;
     if(one&&window._infraD){""",
"""   .then(function(r){ if(r.status===401){ window.infraAuthWait(); return null; } return r.json(); })
   .then(function(d){ if(!d) return;
     if(one&&window._infraD){"""))

    # 3. Loud network-failure branch.
    edits.append((
"""   .catch(function(e){ if(out) out.textContent='Check failed: '+e; });
};
/* APV2-TESTALL-1""",
"""   .catch(function(e){ window.infraFailLoud('Check failed: '+e); });
};
/* APV2-TESTALL-1"""))

    # 4. Token-aware bootstrap + auth listener + poll guard.
    edits.append((
"""try{ window.infraLoad(); setInterval(function(){window.infraLoad();}, 300000); }catch(e){}""",
"""/* INFRA-PANEL-2 (1 Aug 2026): token-aware bootstrap. No token yet -> show the paused
   state (no doomed 401 round-trip); the gate's ms-admin-auth event triggers the real
   load on sign-in. The 5-minute poll also skips while signed out. */
try{
  document.addEventListener('ms-admin-auth', function(){ window.infraLoad(); });
  if(window._apv2Tok()) window.infraLoad(); else window.infraAuthWait();
  setInterval(function(){ if(window._apv2Tok()) window.infraLoad(); }, 300000);
}catch(e){}"""))

    for i, (old, new) in enumerate(edits, 1):
        n = src.count(old)
        if n != 1:
            print(f'  ERROR: INFRA-PANEL-2 anchor {i} matched {n} times (need exactly 1) - tell Claude.')
            return 1
        src = src.replace(old, new)

    if MARK not in src:
        print('  ERROR: INFRA-PANEL-2 marker missing after patch - tell Claude.')
        return 1

    if crlf:
        src = src.replace('\n', '\r\n')
    open(path, 'wb').write(src.encode('utf-8'))
    print('  [OK] INFRA-PANEL-2 applied (auth-aware infra card: reload on PIN sign-in, loud 401/network states).')
    return 0

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: apply_infra_panel2.py <dashboard.server.html>'); sys.exit(1)
    sys.exit(main(sys.argv[1]))
