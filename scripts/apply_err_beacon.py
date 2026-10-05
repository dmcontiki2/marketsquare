import io,sys
P=["quick.html","genie/HARNESS.html"]
ANCH="""    window.addEventListener(ev,function(){ _qfInput=true; _qfDwellFire(); },{passive:true});
  });
}catch(e){}
"""
TRACK_OLD="function qTrack(stepName, meta){\n  try{\n    if(!_QF_BASE) return;"
TRACK_NEW="function qTrack(stepName, meta){\n  try{\n    if(!/^q_(error|api_fail|api_4xx|leave)$/.test(String(stepName||''))) _qLast=String(stepName||'').slice(0,40);   /* QUICK-ERR-BEACON-1 */\n    if(!_QF_BASE) return;"
BLOCK=r"""
/* QUICK-ERR-BEACON-1 (5 Oct 2026, David: "not to again make the same mistake we did with the emails where the app
   didnt work and we thought nobody was interested"; RUL-206(d)). Quick used to fail SILENTLY: a script error, a dead
   button or a server call that came back 500 left no trace, so 'tapped and it broke' read exactly like 'tapped and
   left'. Three beacons, on the same fire-and-forget qTrack path (never throws, never shows her anything):
     q_error     a script error or an unhandled promise, with the step she was on;
     q_api_fail  a call to OUR server that failed on the network or answered 5xx; q_api_4xx a POST we refused;
     q_leave     she hid or left the page -- with the last step she reached and how many errors she met.
   Capped (5 errors, 3 leaves a session) so a loop cannot flood the funnel. The funnel's own beacon is never wrapped. */
var _qLast='', _qeN=0, _qLeaveN=0, _qT0=Date.now();
function _qErr(kind, msg){
  if(_qeN>=5) return; _qeN++;
  try{ qTrack(kind, {m:String(msg||'').slice(0,160), at:_qLast, n:_qeN}); }catch(e){}
}
try{
  window.addEventListener('error', function(ev){
    if(ev && ev.target && ev.target!==window && ev.target.tagName) return;   /* a missing picture is not a crash */
    _qErr('q_error', String((ev&&ev.message)||'error')+' @'+String((ev&&ev.filename)||'').split('/').pop()+':'+((ev&&ev.lineno)||0));
  });
  window.addEventListener('unhandledrejection', function(ev){
    var r=ev&&ev.reason; _qErr('q_error', 'promise: '+String((r&&(r.message||r))||''));
  });
  if(window.fetch && _QF_BASE){
    var _qF=window.fetch;
    window.fetch=function(u, o){
      var url=''; try{ url=String((u&&u.url)||u||''); }catch(e){}
      var p=_qF.apply(this, arguments);
      try{
        var ours=(url.charAt(0)==='/' || url.indexOf(_QF_BASE)===0) && url.indexOf('/onboard/step')<0;
        if(ours){
          var path=url.replace(_QF_BASE,'').replace(/[?#].*$/,'').slice(0,80);
          var post=!!(o && o.method && String(o.method).toUpperCase()!=='GET');
          p.then(function(r){
            if(r && r.status>=500) _qErr('q_api_fail', r.status+' '+path);
            else if(r && post && r.status>=400 && r.status!==401) _qErr('q_api_4xx', r.status+' '+path);
          }, function(){ _qErr('q_api_fail', 'network '+path); });
        }
      }catch(e){}
      return p;
    };
  }
  var _qLeave=function(){
    if(_qLeaveN>=3) return; _qLeaveN++;
    try{ qTrack('q_leave', {at:_qLast, err:_qeN, s:Math.round((Date.now()-_qT0)/1000)}); }catch(e){}
  };
  document.addEventListener('visibilitychange', function(){ if(document.visibilityState==='hidden') _qLeave(); });
  window.addEventListener('pagehide', _qLeave);
}catch(e){}
"""
for p in P:
    s=io.open(p,encoding='utf-8').read()
    if 'QUICK-ERR-BEACON-1 (5 Oct' in s: print(p,'already'); continue
    assert s.count(ANCH)==1, (p,'anchor',s.count(ANCH))
    assert s.count(TRACK_OLD)==1, (p,'track')
    s=s.replace(TRACK_OLD,TRACK_NEW).replace(ANCH,ANCH+BLOCK)
    io.open(p,'w',encoding='utf-8',newline='').write(s); print(p,'ok')
