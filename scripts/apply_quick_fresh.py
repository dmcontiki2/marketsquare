#!/usr/bin/env python3
"""QUICK-FRESH-1 (David 4 Oct 2026: "i dont see the 'near you' option in the live Quick app yet"). It WAS live; his Quick
had been open since before the deploy, and Start again (the circle arrow) only redrew the door -- so an open or installed
Quick kept running the code it was opened with for as long as it stayed open, and a fix could be live and unseen.
Now the door remembers which version it loaded (the page's Last-Modified); Start again, and coming back to an idle Quick
that sits at the door, load the newest version when the server has a newer one. Nothing is cached, and nothing she has
typed is lost: the reload happens only on her own Start again or while she is at the door.
Idempotent; asserts its anchor. Copies quick.html over genie/HARNESS.html."""
import io, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p): return io.open(os.path.join(R, p), encoding="utf-8", newline="").read()
def wr(p, s):
    io.open(os.path.join(R, p), "w", encoding="utf-8", newline="").write(s); assert rd(p) == s, p
A = "$('home').onclick=function(){ drawDoor(); };   /* BUGSWEEP-24SEP: call the CURRENT drawDoor (it is wrapped later) */\n"
B = A + r'''/* QUICK-FRESH-1 (David 4 Oct 2026, "i dont see the 'near you' option in the live Quick app yet"): it was live -- his Quick
   had been open since before the deploy, and Start again only redrew the door. The door now remembers the version it
   loaded; Start again, and coming back to an idle Quick at the door, load the newest one when the server has it.
   Nothing is cached and nothing she typed is lost. */
(function(){
  if(location.protocol==='file:') return;
  var mine=null, lastCheck=0;
  function ver(){ return fetch('/quick/', {method:'HEAD', cache:'no-store', credentials:'same-origin'})
      .then(function(r){ return r.ok ? (r.headers.get('last-modified') || r.headers.get('etag') || '') : ''; })
      .catch(function(){ return ''; }); }
  ver().then(function(v){ mine=v; });
  function newer(){ return ver().then(function(v){ return !!(v && mine && v!==mine); }); }
  window.qFreshCheck=newer;
  var h=$('home'), _on=h.onclick;
  h.onclick=function(){ var self=this, args=arguments;
    newer().then(function(n){ if(n){ try{ qTrack('q_fresh_reload'); }catch(e){} location.reload(); return; } _on.apply(self, args); }); };
  document.addEventListener('visibilitychange', function(){
    if(document.visibilityState!=='visible' || mode || Date.now()-lastCheck<60000) return;
    lastCheck=Date.now();
    newer().then(function(n){ if(n && !mode) location.reload(); }); });
})();
'''
q = rd("quick.html")
if "QUICK-FRESH-1 (David 4 Oct 2026" not in q:
    assert q.count(A) == 1, "anchor: %d" % q.count(A)
    q = q.replace(A, B)
assert q.rstrip().endswith("</html>"), "TRUNCATED"
wr("quick.html", q); wr("genie/HARNESS.html", q)
print("QUICK-FRESH-1 applied; genie/HARNESS.html = quick.html; %d bytes" % len(q.encode("utf-8")))
