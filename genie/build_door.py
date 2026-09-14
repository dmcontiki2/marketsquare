#!/usr/bin/env python3
"""build_door.py - turn the harness into the PUBLIC front door served at /q/<category>.

The harness is the design prototype: tap-only, self-contained, and its Publish
button is a dry run. The door is the same file with three changes, so there is
one source and no second app to keep in step:

  1. the category comes from the URL (/q/cars, /q/tutors, ...) instead of a swipe
     default, and an unknown word still opens on Housekeeping - nobody ever gets
     a page-not-found;
  2. the demo switch is gone - a real visitor is a stranger until they sign in;
  3. Publish does a REAL thing: it posts the email to /auth/request-link, which is
     the app's own live sign-in, and it keeps the four answers on the phone so the
     advert is waiting when they arrive. It never claims a draft was filed.

Run:  python3 build_door.py     ->  q_index.html
"""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
s = io.open(os.path.join(HERE, 'HARNESS.html'), encoding='utf-8', errors='replace').read()
orig = len(s)

# ---- 1. the demo switch never ships to the public door -----------------------
old_sw = """  $('screen').innerHTML +=
    '<div class="dswitch'+(QUICK.member?' on':'')+'" id="dsw"><i></i><span>'
   +(QUICK.member
      ? 'Demo: returning member &mdash; nothing is re-asked'
      : 'Demo: new here &mdash; asked once, at the very end')+'</span></div>';"""
assert s.count(old_sw) == 1, 'demo switch anchor'
s = s.replace(old_sw, """  /* DOOR: no demo switch in public. A visitor is a stranger until they sign in. */""", 1)
s = s.replace("""  $('dsw').onclick=function(){
    QUICK.member=!QUICK.member;
    QUICK.name=QUICK.member?'Hannes Roux':''; QUICK.city=QUICK.member?LOC.suburb:'';
    drawDoor();
  };""", "", 1)

# ---- 2. the category comes from the URL --------------------------------------
old_boot = "drawDoor();\n</script>"
assert s.count(old_boot) == 1, 'boot anchor'
new_boot = """/* DOOR: /q/<category> picks the category. An unknown word is not an error - it
   opens on the first category, so a mistyped or old link still lands somewhere
   real. This is the whole reason the door exists at a path per category. */
(function(){
  try{
    var seg = (location.pathname.replace(/\\/+$/,'').split('/').pop()||'').toLowerCase();
    var q   = (location.search.match(/[?&]c=([a-z]+)/i)||[])[1];
    var want = (q||seg||'').toLowerCase().replace(/[^a-z]/g,'');
    var ALIAS = {housekeeping:'homehelp', home:'homehelp', help:'homehelp', casual:'homehelp',
                 car:'cars', tutor:'tutors', service:'services', trade:'services',
                 collector:'collectors', adventure:'adventures', travel:'adventures',
                 local:'localmarket', market:'localmarket', localmarket:'localmarket'};
    want = ALIAS[want] || want;
    for(var i=0;i<CATS.length;i++) if(CATS[i].key===want){ ci=i; break; }
  }catch(e){}
})();
drawDoor();
</script>"""
s = s.replace(old_boot, new_boot, 1)

# ---- 3. Publish does a real thing -------------------------------------------
old_pub = s[s.index('  function doPublish(btn){'):s.index("  /* THE ONE ASK, AND IT IS THE LAST THING")]
new_pub = """  function doPublish(btn){
    /* DOOR: the live app's own sign-in. No API key can live in a public page, so the
       door never writes a listing itself - it starts the real account and carries the
       answers. Nothing here claims more than that. */
    var mail = (window._doorMail||'').trim();
    btn.disabled=true; btn.textContent='Sending your link…';
    try{
      localStorage.setItem('ts_quick_draft', JSON.stringify({
        category: cat().name, title: cat().draftTitle(picks),
        body: cat().draftBody(picks),
        answers: picks.map(function(p){return {key:p.key,label:p.label};}),
        taps: taps, at: new Date().toISOString()}));
    }catch(e){}
    fetch('/auth/request-link',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({email:mail})})
      .then(function(r){ return r.json().then(function(j){ return {ok:r.ok,j:j}; }); })
      .then(function(res){
        var box=$('hres'); box.style.display='block';
        if(!res.ok){
          btn.disabled=false; btn.textContent='Publish it';
          box.style.borderColor='#e06a5a';
          box.textContent=(res.j && res.j.detail) ? res.j.detail
            : 'That did not go through. Check the address and try again.';
          $('pubhint').textContent='Nothing was sent.';
          return;
        }
        btn.textContent='\\u2713 Check your email';
        box.innerHTML='<b>Your sign-in link is on its way to '+mail.replace(/[<>&]/g,'')+'.</b> '
          +'Open it on this phone and your advert is waiting, filled in exactly as you see it '
          +'above. Nothing is published until you say so in the app.';
        $('pubhint').textContent='Composed from '+taps+' taps. Your answers are saved on this phone.';
      })
      .catch(function(e){
        var box=$('hres'); box.style.display='block'; box.style.borderColor='#e06a5a';
        box.textContent='No connection just now - try again in a moment.';
        btn.disabled=false; btn.textContent='Publish it';
      });
  }
"""
s = s.replace(old_pub, new_pub, 1)

# the email the person typed has to reach doPublish
s = s.replace("""      var m=$('jmail').value.trim();
      QUICK.member=true; QUICK.name=nameFromMail(m); QUICK.city=LOC.suburb;""",
              """      var m=$('jmail').value.trim();
      window._doorMail=m;
      QUICK.member=true; QUICK.name=nameFromMail(m); QUICK.city=LOC.suburb;""", 1)

# a member on the door would skip the ask entirely; on the public door there is no member
s = s.replace("var QUICK={member:false, name:'', city:''};",
              "var QUICK={member:false, name:'', city:''};   /* DOOR: always false in public */", 1)

# ---- honest wording where the harness talked about a hand-over ---------------
s = s.replace('Draft &mdash; publish now, polish it in the app', 'Draft &mdash; finish it in the app')
s = s.replace('<title>The Harness</title>', '<title>TrustSquare \\u2014 put it on the board</title>')

out = os.path.join(HERE, 'q_index.html')
io.open(out, 'w', encoding='utf-8').write(s)
print('q_index.html written: %d bytes (harness was %d)' % (len(s), orig))
for must in ['/auth/request-link', 'ts_quick_draft', 'ALIAS', 'Check your email']:
    print('  contains %-22s %s' % (must, must in s))
print('  demo switch gone:      %s' % ('dswitch' not in s.split('<style>')[1].split('</style>')[1]))
