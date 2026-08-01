#!/usr/bin/env python3
"""v3 (1 Aug 2026): adds the FUNNEL STRIP (order + gate types only) and the MANUAL PIN
(operator precedence with decay — David's ruling 1 Aug 2026). Based on v2 (P1, 17 Jul 2026): AI Provider REGISTRY card for Page-4 (dashboard.html), IN PLACE, idempotent.
Replaces the v1 two-pill card. Fixes DASH-AIPROV-1: v1's JS could land inside another
script's closure (onclick handlers resolve on window -> ReferenceError). v2 injects ALL
JS as its own <script> before </body>, self-contained (own base-url + token helpers).
Run on the SERVER's pulled-down copy (deploy_bit_monitoring.bat flow). Exit 0 = ok."""
import sys, re
f = sys.argv[1] if len(sys.argv) > 1 else "dashboard.html"
s = open(f, encoding="utf-8").read()
orig = len(s)

# SELF-REPAIRING (1 Aug 2026, DASH-AIPROV-2): an existing v3 card/script is STRIPPED and
# re-injected fresh — re-running the deploy always converges on a known-good card.
def _strip_div_by_id(s, marker, comment_prefix):
    _ci = s.find(marker)
    if _ci == -1: return s
    _start = s.rfind('<div', 0, _ci)
    _cm = s.rfind(comment_prefix, max(0, _start-400), _start)
    if _cm != -1: _start = _cm
    _pos, _depth, _end = _start, 0, -1
    while True:
        _o = s.find('<div', _pos); _c = s.find('</div>', _pos)
        if _c == -1: break
        if _o != -1 and _o < _c: _depth += 1; _pos = _o + 4
        else:
            _depth -= 1; _pos = _c + 6
            if _depth <= 0: _end = _pos; break
    while _start > 0 and s[_start-1] in ' \t\r\n': _start -= 1
    return s[:_start] + s[_end:] if _end != -1 else s
s = _strip_div_by_id(s, 'id="ai-prov-card-v3"', '<!-- AI PROVIDER REGISTRY v3')
s = re.sub(r'\s*<script>(?:(?!</script>).)*?window\._apv3B(?:(?!</script>).)*?</script>\s*', '', s, flags=re.S)
s = _strip_div_by_id(s, 'id="ai-prov-card-v2"', '<!-- AI PROVIDER REGISTRY v2')
s = re.sub(r'<script>(?:(?!</script>).)*?window\\._apv2B(?:(?!</script>).)*?</script>\\s*', '', s, flags=re.S)

CARD = """
  <!-- AI PROVIDER REGISTRY v3 — funnel strip (order+types) · manual pin with decay -->
  <script>/* EARLY SHIM (DASH-AIPROV-3): later cards (Infrastructure/services) read these v2-era
  globals AT PARSE TIME — they must exist before those scripts run, not only at page bottom. */
  window._apv2B=(location.protocol==='file:'?'https://trustsquare.co':'');
  window._apv2Tok=function(){try{return sessionStorage.getItem('ms_admin_token')||'';}catch(e){return '';}};
  window._apv2=window._apv2||{providers:[]};</script>
  <div class="ls-card" id="ai-prov-card-v3">
    <div class="ls-h">&#128268; AI Providers <span id="apv3-sub" style="color:var(--muted);font-weight:600;text-transform:none;letter-spacing:0">— registry</span></div>
    <div id="apv3-pin" style="display:none;font-size:12px;margin:-2px 0 8px;padding:7px 10px;border-radius:8px;background:rgba(59,130,246,.12);border:1px solid rgba(59,130,246,.4);"></div>
    <div style="font-size:12px;color:var(--muted);margin:-4px 0 10px">Pin = manual precedence for a limited time; when it expires the standing lane resumes automatically. Standing-lane changes go through the Model Register process, not this card.</div>
    <div id="apv3-rows" style="display:flex;flex-direction:column;"><div style="color:var(--muted);font-size:12px;padding:8px 0">Loading registry&hellip;</div></div>
    <div class="ls-h" style="margin-top:12px;font-size:12px;">Latest funnel (order &middot; gate only)</div>
    <div id="apv3-funnel" style="font-size:11px;color:var(--muted);line-height:1.7"></div>
    <div id="apv3-out" style="font-size:12px;color:var(--muted);margin-top:10px;white-space:pre-wrap"></div>
  </div>
"""

JS = r"""
<script>
/* AI Provider Registry v3 — funnel strip + manual pin with decay (1 Aug 2026) */
window._apv3B = (location.protocol==='file:' ? 'https://trustsquare.co' : '');
window._apv3Tok = function(){ try{ return sessionStorage.getItem('ms_admin_token')||''; }catch(e){ return ''; } };
window._apv3 = {active:'anthropic', standing:'anthropic', override:null, ttl:24, providers:[], funnel:null};
/* Back-compat shims (DASH-AIPROV-2): the Infrastructure/services card was built on v2's
   globals — keep them alive so removing the v2 script never strands another card again. */
window._apv2B = window._apv3B; window._apv2Tok = window._apv3Tok; window._apv2 = window._apv3;
window.apv3Render = function(){
  var d=window._apv3, box=document.getElementById('apv3-rows'); if(!box) return;
  var pin=document.getElementById('apv3-pin');
  if(pin){
    if(d.override){
      var until=new Date(d.override.expires_at+'Z');
      pin.style.display='block';
      pin.innerHTML='&#128204; <b>PINNED to '+d.override.provider+'</b> until '+until.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})+' (local) — standing lane <b>'+d.standing+'</b> resumes on expiry &nbsp;<button type="button" onclick="apv3Pin(\'\')" style="padding:3px 9px;border-radius:6px;border:1px solid var(--border);background:var(--surface2);color:var(--text);font-size:11px;cursor:pointer;font-family:inherit">Unpin now</button>';
    } else pin.style.display='none';
  }
  var h='';
  (d.providers||[]).forEach(function(p){
    var active=(p.id===d.active), avail=!!p.available;
    var st = active?['#22c55e','ACTIVE'+(d.override&&d.override.provider===p.id?' (PIN)':'')]:(avail?['#22c55e','STANDBY']:['#6b7280','DISABLED — no key']);
    var models=p.models?('fast '+(p.models.haiku||'—').split('-20')[0]+' &middot; reason '+(p.models.sonnet||'—')):'';
    h+='<div style="display:flex;gap:10px;align-items:center;padding:9px 0;border-bottom:1px solid var(--border);">'
      +'<span style="width:9px;height:9px;border-radius:50%;background:'+st[0]+';opacity:'+(active?'1':(avail?'.55':'.6'))+';flex:0 0 auto;"></span>'
      +'<div style="flex:1;min-width:0;"><div style="font-size:13px;font-weight:600;color:var(--text)">'+p.label+' <span style="color:var(--muted);font-weight:400;font-size:11px">'+(p.jurisdiction||'')+'</span></div>'
      +'<div style="font-size:10.5px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+models+'</div></div>'
      +'<span style="font-size:10.5px;font-weight:700;color:'+(active?'#22c55e':(avail?'var(--text)':'var(--muted)'))+';flex:0 0 auto">'+st[1]+'</span>'
      +'<button type="button" onclick="apv3Test(\''+p.id+'\')" '+(avail?'':'disabled ')+'style="flex:0 0 auto;padding:5px 10px;border-radius:7px;border:1px solid var(--border);background:var(--surface2);color:var(--text);font-size:11px;cursor:'+(avail?'pointer':'not-allowed')+';font-family:inherit;opacity:'+(avail?'1':'.4')+'">Test</button>'
      +(avail&&!(d.override&&d.override.provider===p.id)?('<button type="button" onclick="apv3Pin(\''+p.id+'\')" style="flex:0 0 auto;padding:5px 10px;border-radius:7px;border:1px solid var(--border);background:none;color:var(--muted);font-size:11px;cursor:pointer;font-family:inherit">Pin '+(d.ttl||24)+'h</button>'):'')
      +'</div>';
  });
  box.innerHTML=h||'<div style="color:var(--muted);font-size:12px">Registry unavailable.</div>';
  var fb=document.getElementById('apv3-funnel');
  if(fb){
    if(d.funnel&&d.funnel.tiers){
      var fh='';
      Object.keys(d.funnel.tiers).forEach(function(t){
        fh+='<div><b style="color:var(--text)">'+t+':</b> '+d.funnel.tiers[t].map(function(x,i){
          return (i+1)+'. '+x.provider+' <span style="opacity:.7">('+x.gate+')</span>';}).join(' &rarr; ')+'</div>';
      });
      fh+='<div style="opacity:.6">card '+(d.funnel.card_version||'')+' &middot; order &amp; gate only — dollars live in the Model Register</div>';
      fb.innerHTML=fh;
    } else fb.innerHTML='<span style="opacity:.6">No funnel snapshot on the server yet (scripts/price_truth.py --snapshot, then deploy).</span>';
  }
  var sub=document.getElementById('apv3-sub'); if(sub) sub.textContent='— active: '+d.active+(d.override?' (pinned)':'')+' · standing: '+d.standing;
};
window.apv3Load = function(){
  fetch(window._apv3B+'/flags').then(function(r){return r.json();}).then(function(f){
    if(f&&f.ai_provider){ var a=f.ai_provider;
      window._apv3={active:a.active, standing:a.standing||a.active, override:a.override||null, ttl:a.override_ttl_hours||24, providers:(a.providers||[]), funnel:a.funnel||null};
      window._apv2=window._apv3;   /* keep the shim's provider list fresh */
      window.apv3Render(); }
  }).catch(function(){});
};
window.apv3Test = function(p){
  var out=document.getElementById('apv3-out'); if(out) out.textContent='Testing '+p+'…';
  fetch(window._apv3B+'/admin/ai-test',{method:'POST',headers:{'Content-Type':'application/json','X-Admin-Token':window._apv3Tok()},body:JSON.stringify({provider:p})})
   .then(function(r){ if(r.status===401){ if(out) out.textContent='Admin session expired — reload + PIN.'; return null; } return r.json(); })
   .then(function(d){ if(!d) return; if(out) out.textContent=(d.ok?'✓ ':'✗ ')+d.provider+' ('+d.model+'): '+(d.text||d.detail||'(no text)'); })
   .catch(function(e){ if(out) out.textContent='Test failed: '+e; });
};
window.apv3Pin = function(p){
  var msg = p ? ('PIN the live AI vendor to '+p+' for '+(window._apv3.ttl||24)+' hours? This outranks any automatic selection; the standing lane ('+window._apv3.standing+') resumes when the pin expires.') : 'Remove the pin now? The standing lane resumes immediately.';
  if(!confirm(msg)) return;
  fetch(window._apv3B+'/admin/flags',{method:'POST',headers:{'Content-Type':'application/json','X-Admin-Token':window._apv3Tok()},body:JSON.stringify({ai_active_override:p})})
   .then(function(r){ if(r.status===401){ alert('Admin session expired — reload and log in.'); return null; } if(r.status===400){ alert('Server rejected provider.'); return null; } return r.json(); })
   .then(function(f){ if(f&&f.ai_provider){ window.apv3Load(); } })
   .catch(function(e){ console.warn('pin failed', e); });
};
try{ window.apv3Load(); setInterval(window.apv3Load, 60000); }catch(e){}
</script>
"""

vi = s.find('id="launch-switch-view"')
if vi == -1: print("ANCHOR launch-switch-view missing"); sys.exit(2)
sc = s.find("</style>", vi)
if sc == -1: print("ANCHOR </style> missing"); sys.exit(2)
at = sc + len("</style>")
s = s[:at] + CARD + s[at:]
bi = s.rfind("</body>")
if bi == -1: print("ANCHOR </body> missing"); sys.exit(2)
s = s[:bi] + JS + s[bi:]
open(f, "w", encoding="utf-8").write(s)
print(f"v3 registry card applied to {f}: {orig}->{len(s)}")
sys.exit(0)
