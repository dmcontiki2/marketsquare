#!/usr/bin/env python3
"""Apply the BIT Self-Test panel to a dashboard.html IN PLACE (idempotent).
Run it on the SERVER's pulled-down copy so the live version isn't overwritten by an older local one.
Usage: python3 apply_bit_panel.py /path/to/dashboard.html
Exits 0 on success (or if already applied); non-zero if anchors are missing (then tell Claude)."""
import sys, re
f=sys.argv[1] if len(sys.argv)>1 else "dashboard.html"
s=open(f,encoding="utf-8").read()
if 'id="bit-summary"' in s and 'function loadBIT' in s:
    print("already applied — no change"); sys.exit(0)
orig=len(s)

a1='<div class="health-grid" id="health-grid"></div>'
if s.count(a1)!=1: print("ANCHOR a1 missing/dup",s.count(a1)); sys.exit(2)
s=s.replace(a1, a1+'\n      <div id="bit-summary" style="margin-top:8px;font-size:13px;"></div>')

a2='<div id="ops-view" style="display:none;padding:24px 20px;max-width:900px;margin:0 auto;">'
if s.count(a2)!=1: print("ANCHOR a2 missing/dup",s.count(a2)); sys.exit(2)
s=s.replace(a2, a2+'''
  <div class="health-panel" id="bit-ops-panel">
    <div class="health-title">\U0001F9EA BIT SELF-TEST
      <span id="bit-ops-dot" style="margin-left:6px;color:#10b981;">●</span>
      <span class="health-updated" id="bit-ops-updated">loading…</span>
    </div>
    <div id="bit-ops-summary" style="font-size:13px;margin:6px 0 10px;"></div>
    <div id="bit-ops-list"></div>
  </div>
''')

a3='function loadHealth() {'
if s.count(a3)!=1: print("ANCHOR a3 missing/dup",s.count(a3)); sys.exit(2)
s=s.replace(a3, '''function _bitColor(st){return st==='pass'?'#10b981':(st==='critical'?'#ef4444':(st==='degraded'?'#f59e0b':'#94a3b8'));}
function _bitWord(st){return st==='pass'?'healthy':(st==='critical'?'CRITICAL':(st==='degraded'?'degraded':'unknown'));}
function renderBIT(b){
  var c=_bitColor(b.state||'unknown'), ran=(b.ran_at||'').replace('T',' ').replace('Z',' UTC');
  var sum=document.getElementById('bit-summary');
  if(sum){var f=(b.failing&&b.failing.length)?(' · failing: '+b.failing.join(', ')):'';
    sum.innerHTML='<span style="color:'+c+';">●</span> <b>BIT '+(b.pass||0)+'/'+(b.total||0)+' PASS</b> <span style="color:#94a3b8;">('+_bitWord(b.state)+')</span><span style="color:#ef4444;">'+f+'</span> <span style="color:#94a3b8;font-size:11px;">'+(ran?('· '+ran):'')+'</span>';}
  var dot=document.getElementById('bit-ops-dot'); if(dot)dot.style.color=c;
  var upd=document.getElementById('bit-ops-updated'); if(upd)upd.textContent=ran||'';
  var osum=document.getElementById('bit-ops-summary'); if(osum)osum.innerHTML='<b style="color:'+c+';">'+(b.pass||0)+'/'+(b.total||0)+' PASS — '+_bitWord(b.state)+'</b>';
  var list=document.getElementById('bit-ops-list');
  if(list){var rows=(b.results||[]).map(function(r){var rc=r.state==='PASS'?'#10b981':(r.sev==='S1'?'#ef4444':'#f59e0b');
    return '<div style="display:flex;justify-content:space-between;gap:10px;padding:4px 0;border-bottom:1px solid rgba(148,163,184,.15);font-size:12px;"><span><span style="color:'+rc+';">●</span> <b>'+r.id+'</b> <span style="color:#94a3b8;">['+r.sev+' '+r.type+']</span></span><span style="color:'+(r.state==='PASS'?'#10b981':'#ef4444')+';">'+r.state+'</span></div><div style="font-size:11px;color:#94a3b8;margin:-2px 0 4px;">'+(r.detail||'')+'</div>';}).join('');
    list.innerHTML=rows||'<div style="color:#94a3b8;font-size:12px;">No BIT run recorded yet.</div>';}
}
function loadBIT(){fetch((window.location.protocol==='file:'?'https://trustsquare.co':'')+'/dashboard/bit').then(function(r){return r.json();}).then(function(b){renderBIT(b);}).catch(function(){var s=document.getElementById('bit-summary');if(s)s.innerHTML='<span style="color:#94a3b8;">● BIT status unavailable</span>';});}

function loadHealth() {''')

a4='loadHealth(); // Start health polling'
if s.count(a4)!=1: print("ANCHOR a4 missing/dup",s.count(a4)); sys.exit(2)
s=s.replace(a4, a4+'\n    loadBIT();\n    if(!window._bitTimer) window._bitTimer=setInterval(loadBIT, 60000);')

open(f,"w",encoding="utf-8").write(s)
print(f"applied BIT panel to {f}: {orig} -> {len(s)} bytes")
sys.exit(0)
