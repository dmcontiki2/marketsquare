#!/usr/bin/env python3
"""v2 (P1, 17 Jul 2026): AI Provider REGISTRY card for Page-4 (dashboard.html), IN PLACE, idempotent.
Replaces the v1 two-pill card. Fixes DASH-AIPROV-1: v1's JS could land inside another
script's closure (onclick handlers resolve on window -> ReferenceError). v2 injects ALL
JS as its own <script> before </body>, self-contained (own base-url + token helpers).
Run on the SERVER's pulled-down copy (deploy_bit_monitoring.bat flow). Exit 0 = ok."""
import sys, re
f = sys.argv[1] if len(sys.argv) > 1 else "dashboard.html"
s = open(f, encoding="utf-8").read()
orig = len(s)

if 'id="ai-prov-card-v2"' in s:
    print("v2 registry card already present — no change"); sys.exit(0)

# ── strip v1 remnants (card div, any copy of the v1 JS, the aiProvLoad view hook) ──
# card div: index-based excision (server copies vary in whitespace — regex proved brittle)
_ci = s.find('id="ai-prov-card"')
if _ci != -1:
    _start = s.rfind('<div', 0, _ci)                      # opening <div ... id="ai-prov-card">
    _cm = s.rfind('<!-- AI PROVIDER SWAP', max(0, _start-400), _start)
    if _cm != -1: _start = _cm                            # include the leading comment if present
    # depth-walk to the card's closing </div> — immune to card-variant drift (v1a/v1b)
    _pos, _depth, _end = _start, 0, -1
    while True:
        _o = s.find('<div', _pos); _c = s.find('</div>', _pos)
        if _c == -1: break
        if _o != -1 and _o < _c:
            _depth += 1; _pos = _o + 4
        else:
            _depth -= 1; _pos = _c + 6
            if _depth <= 0: _end = _pos; break
    if _end != -1:
        s = s[:_start] + s[_end:]
s = re.sub(r'window\._aiProv\s*=\s*\{active:"anthropic".*?catch\(function\(e\)\{\s*if\(out\)\s*out\.textContent=.Test failed:.\s*\+\s*e;\s*\}\);\n\}\n?', "", s, flags=re.S)
s = s.replace(" try{aiProvLoad();}catch(e){} ", " ")

CARD = """
  <!-- AI PROVIDER REGISTRY v2 (P1) — per-provider status, per-task chains, test-any-provider -->
  <div class="ls-card" id="ai-prov-card-v2">
    <div class="ls-h">&#128268; AI Providers <span id="apv2-sub" style="color:var(--muted);font-weight:600;text-transform:none;letter-spacing:0">— registry</span></div>
    <div style="font-size:12px;color:var(--muted);margin:-4px 0 10px">Per-provider status and live test. Activate swaps the vendor for all seam-routed features (21 of 22), no restart.</div>
    <div id="apv2-rows" style="display:flex;flex-direction:column;"><div style="color:var(--muted);font-size:12px;padding:8px 0">Loading registry&hellip;</div></div>
    <div id="apv2-out" style="font-size:12px;color:var(--muted);margin-top:10px;white-space:pre-wrap"></div>
  </div>
"""

JS = """
<script>
/* AI Provider Registry v2 (P1) — all-global, self-contained (DASH-AIPROV-1 fix) */
window._apv2B = (location.protocol==='file:' ? 'https://trustsquare.co' : '');
window._apv2Tok = function(){ try{ return sessionStorage.getItem('ms_admin_token')||''; }catch(e){ return ''; } };
window._apv2 = {active:'anthropic', providers:[]};
window.apv2Render = function(){
  var box=document.getElementById('apv2-rows'); if(!box) return;
  var d=window._apv2, h='';
  (d.providers||[]).forEach(function(p){
    var active=(p.id===d.active), avail=!!p.available;
    var st = active?['#22c55e','ACTIVE']:(avail?['#22c55e','STANDBY']:['#6b7280','DISABLED — no key']);
    var models=p.models?('fast '+ (p.models.haiku||'—').split('-20')[0] +' &middot; reason '+ (p.models.sonnet||'—') +' &middot; vision '+ (p.models.vision||'—')):'';
    h+='<div style="display:flex;gap:10px;align-items:center;padding:9px 0;border-bottom:1px solid var(--border);">'
      +'<span style="width:9px;height:9px;border-radius:50%;background:'+st[0]+';opacity:'+(active?'1':(avail?'.55':'.6'))+';flex:0 0 auto;"></span>'
      +'<div style="flex:1;min-width:0;"><div style="font-size:13px;font-weight:600;color:var(--text)">'+p.label+' <span style="color:var(--muted);font-weight:400;font-size:11px">'+(p.jurisdiction||'')+'</span></div>'
      +'<div style="font-size:10.5px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+models+'</div></div>'
      +'<span style="font-size:10.5px;font-weight:700;color:'+(active?'#22c55e':(avail?'var(--text)':'var(--muted)'))+';flex:0 0 auto">'+st[1]+'</span>'
      +'<button type="button" onclick="apv2Test(\\''+p.id+'\\')" '+(avail?'':'disabled ')+'style="flex:0 0 auto;padding:5px 10px;border-radius:7px;border:1px solid var(--border);background:var(--surface2);color:var(--text);font-size:11px;cursor:'+(avail?'pointer':'not-allowed')+';font-family:inherit;opacity:'+(avail?'1':'.4')+'">Test</button>'
      +(!active&&avail?('<button type="button" onclick="apv2Activate(\\''+p.id+'\\')" style="flex:0 0 auto;padding:5px 10px;border-radius:7px;border:1px solid var(--border);background:none;color:var(--muted);font-size:11px;cursor:pointer;font-family:inherit">Activate</button>'):'')
      +'</div>';
  });
  box.innerHTML=h||'<div style="color:var(--muted);font-size:12px">Registry unavailable.</div>';
  var sub=document.getElementById('apv2-sub'); if(sub) sub.textContent='— active: '+d.active;
};
window.apv2Load = function(){
  fetch(window._apv2B+'/flags').then(function(r){return r.json();}).then(function(f){
    if(f&&f.ai_provider){ window._apv2={active:f.ai_provider.active, providers:(f.ai_provider.providers||[])}; window.apv2Render(); }
  }).catch(function(){});
};
window.apv2Test = function(p){
  var out=document.getElementById('apv2-out'); if(out) out.textContent='Testing '+p+'\\u2026';
  fetch(window._apv2B+'/admin/ai-test',{method:'POST',headers:{'Content-Type':'application/json','X-Admin-Token':window._apv2Tok()},body:JSON.stringify({provider:p})})
   .then(function(r){ if(r.status===401){ if(out) out.textContent='Admin session expired \\u2014 reload + PIN.'; return null; } return r.json(); })
   .then(function(d){ if(!d) return; if(out) out.textContent=(d.ok?'\\u2713 ':'\\u2717 ')+d.provider+' ('+d.model+'): '+(d.text||d.detail||'(no text)')+(d.in_tokens?('  ['+d.in_tokens+'+'+d.out_tokens+' tok]'):''); })
   .catch(function(e){ if(out) out.textContent='Test failed: '+e; });
};
window.apv2Activate = function(p){
  if(!confirm('Switch the LIVE AI vendor to '+p+'? All seam-routed features swap immediately (no restart). Note: golden-set eval for non-Anthropic lanes is still pending \\u2014 outage use only until evals pass.')) return;
  fetch(window._apv2B+'/admin/flags',{method:'POST',headers:{'Content-Type':'application/json','X-Admin-Token':window._apv2Tok()},body:JSON.stringify({ai_active:p})})
   .then(function(r){ if(r.status===401){ alert('Admin session expired \\u2014 reload and log in.'); return null; } if(r.status===400){ alert('Server rejected provider.'); return null; } return r.json(); })
   .then(function(f){ if(f&&f.ai_provider){ window._apv2={active:f.ai_provider.active, providers:(f.ai_provider.providers||[])}; window.apv2Render(); } })
   .catch(function(e){ console.warn('activate failed', e); });
};
try{ window.apv2Load(); setInterval(window.apv2Load, 60000); }catch(e){}
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
print(f"v2 registry card applied to {f}: {orig}->{len(s)}")
sys.exit(0)
