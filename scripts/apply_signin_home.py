#!/usr/bin/env python3
"""apply_signin_home.py -- SIGNIN-HOME-1 (5 Oct 2026). David: "on selecting Google for the first time the user ends up
on the sell page and it would have been better for the first time to end up on the Home page." After a Google / Apple
sign-in (the server returns to /?signedin=1) the app now lands on Home with a welcome line -- unless a Quick draft is
waiting in this tab, which DRAFT-AFTER-SIGNIN-1 opens in the Hub on purpose. Idempotent; works on a text or a file."""
import io, sys
A = """  if(sp.get('signin')){
    const _tok = sp.get('signin');"""
B = """  /* SIGNIN-HOME-1 (5 Oct 2026, David: "on selecting Google for the first time the user ends up on the sell page ... it
     would have been better for the first time to end up on the Home page"): a Google / Apple sign-in returns to
     /?signedin=1 -- land on Home with a welcome, never on a selling screen. A Quick draft waiting in this tab still
     opens in the Hub (DRAFT-AFTER-SIGNIN-1): that person came to publish it. */
  if(sp.get('signedin')==='1' && !sp.get('signin')){
    window.history.replaceState({}, '', window.location.pathname);
    let _siFirst=false; try{ _siFirst=!localStorage.getItem('ms_joined_date'); }catch(_){}
    msAdoptSession().then(function(){
      let _siDraft=false; try{ _siDraft=!!sessionStorage.getItem('ts_land_draft'); }catch(_){}
      if(_siDraft) return;
      try{ if(!localStorage.getItem('ms_joined_date')) localStorage.setItem('ms_joined_date', new Date().toISOString()); }catch(_){}
      setTimeout(function(){ try{
        goTo('home');
        if(typeof updateHeaderAuthBtn==='function') updateHeaderAuthBtn();
        showToast(_siFirst ? '\\u2713 Signed in \\u2014 welcome to TrustSquare! Look around; tap Sell when you are ready.'
                           : '\\u2713 Signed in \\u2014 welcome back!', 5000);
      }catch(_){} }, 300);
    });
  }
""" + A
def apply(s):
    if "SIGNIN-HOME-1" in s:
        return s
    assert s.count(A) == 1, "anchor"
    return s.replace(A, B)
if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else "ms.js"
    s = io.open(p, encoding="utf-8", newline="").read()
    io.open(p, "w", encoding="utf-8", newline="").write(apply(s)); print(p, "ok")
