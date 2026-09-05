/* ═══════════════════════════════════════════════════════════════════════════
   admin_gate.js — THE ONE SOURCE of the TrustSquare admin gate (GATE-ONESOURCE-1,
   5 Sep 2026). Closes RG-0196; the consolidation RG-0075 was written for.

   This file is not loaded by a <script src>. It is INLINED into every admin surface
   by scripts/sync_admin_gate.py, between the ADMIN-GATE-SRC markers. That is
   deliberate and it is the reason this took so long to fix: dashboard.html is opened
   over file://, where a page at origin 'null' cannot load /static/admin_gate.js at
   all — so the obvious script-tag fix would have broken the very copy David actually
   opens (RG-0076). Inlining from one source gives the same single-edit property
   without touching how any page is served.

   EDIT HERE, NEVER IN THE HTML. Then run:  python3 scripts/sync_admin_gate.py
   Ledger RG-0196 fails if any copy diverges from this file, so an edit made in the
   wrong place is caught the same day rather than after eight (GATE-DRIFT-1).

   WHY THIS EXISTS AT ALL. The gate was written once in May 2026 and copied by hand.
   Every fix since landed in whichever copy was in front of the person fixing it:
   GATE-COOKIE-1, GATE-CACHE-1, GATE-CREDS-1, DW-040, GATE-TRUTH-1/2, GATE-NOLOCK-1,
   GATE-DRIFT-1 — the same collision patched again and again, per file. On 27 Aug two
   copies were EIGHT DAYS behind on a message that told David his CORRECT password was
   a wrong reviewer code. On 5 Sep the copies had drifted again: DEVICE-ENROL-1 (3 Sep)
   had reached two of the three. Counting the copies never fixed it. Deleting them did.
   ═══════════════════════════════════════════════════════════════════════════ */
  function showLoginError(msg){
    err.textContent = msg; err.style.display = 'block';
    inp.value = ''; inp.focus();
  }
  function showChangePINScreen(name, currentPin){
    _tempPin = currentPin;
    document.getElementById('gate-change-name').textContent = 'Welcome, ' + name;
    loginScreen.style.display = 'none';
    changeScreen.style.display = 'block';
    setTimeout(function(){ document.getElementById('gate-new-pin').focus(); }, 100);
  }

  // Check existing token on load
  var stored = sessionStorage.getItem('ms_admin_token');
  if(stored){
    fetch(BEA + '/admin/verify', {headers:{'X-Admin-Token': stored}})
      .then(function(r){
        return r.text().then(function(t){
          var d = null; try { d = JSON.parse(t); } catch(e) {}
          if(d && d.valid){ hideGate(); return; }
          /* GATE-TRUTH-2: an nginx HTML 401 is the GATE refusing, not the token expiring.
             Dropping the token here logged people out of a still-valid session, silently. */
          if(!d && (r.status === 401 || r.status === 403)){ showGate(); return; }
          sessionStorage.removeItem('ms_admin_token'); showGate();
        });
      })
      .catch(function(){ showGate(); });
  } else {
    /* DEVICE-ENROL-1 (3 Sep 2026): an enrolled phone mints its token silently. */
    fetch(BEA + '/admin/device-token', {credentials: 'same-origin'})
      .then(function(r){ return r.ok ? r.json() : null; })
      .then(function(d){
        if(d && d.token){ sessionStorage.setItem('ms_admin_token', d.token); hideGate(); }
        else { showGate(); }
      })
      .catch(function(){ showGate(); });
  }

  window.adminGateSubmit = function(){
    var pw = inp.value.trim();
    if(!pw) return;
    err.style.display = 'none';
    fetch(BEA + '/admin/login', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({password: pw})
    })
    .then(function(r){
      return r.text().then(function(t){
        var d = null; try { d = JSON.parse(t); } catch(e) {}
        if(d && d.token){
          sessionStorage.setItem('ms_admin_token', d.token);
          hideGate();
        }
        else if(d && d.must_change_pin){ showChangePINScreen(d.name, pw); }
        else if(d && d.detail){ showLoginError(d.detail); }
        else if(r.status === 401 || r.status === 403){
          /* GATE-TRUTH-2 (14 Aug 2026) — the dashboard copy of GATE-TRUTH-1.
             The origin gate (GATE-ENFORCE-2, migrations/016) refuses anonymous /admin/login
             with an nginx HTML 401 before the app ever sees it; /admin/login is deliberately
             NOT on the exempt list (migrations/018). The old code called r.json() blind, the
             parse threw, and the .catch mislabelled EVERY refusal as a network failure. That
             single wrong message is why this fault kept being re-diagnosed from zero. */
          /* GATE-NOLOCK-1 (19 Aug 2026): /admin/login is now EXEMPT at the origin
             (migrations/025) and a correct admin credential grants the gate cookie
             itself, so the dashboard no longer needs the reviewer code first. A 401
             here therefore means the password/PIN really is wrong — the old message
             sent David to perform a step that was impossible and told him his correct
             password was an incorrect reviewer code. */
          showLoginError('Password or PIN not accepted. If this box is new, open ' +
                         'https://trustsquare.co/ once and unlock it there first.');
        }
        else if(r.status === 503){
          showLoginError('Server auth not configured (503) \u2014 MS_ADMIN_PASSWORD or MS_JWT_SECRET is unset on the box.');
        }
        else { showLoginError('Sign-in failed (' + r.status + '). Please try again.'); }
      });
    })
    .catch(function(){ showLoginError('Network error \u2014 the browser could not reach ' + BEA + '. If this page was opened from a file:// path, open it from https://trustsquare.co/ instead (CORS allows that origin only).'); });
  };

  window.adminGateChangePIN = function(){
    var newPin  = document.getElementById('gate-new-pin').value.trim();
    var confirm = document.getElementById('gate-confirm-pin').value.trim();
    changeErr.style.display = 'none';
    if(!/^[0-9]{6}$/.test(newPin)){
      changeErr.textContent = 'PIN must be exactly 6 digits.';
      changeErr.style.display = 'block'; return;
    }
    if(newPin !== confirm){
      changeErr.textContent = 'PINs do not match. Please try again.';
      changeErr.style.display = 'block';
      document.getElementById('gate-confirm-pin').value = ''; return;
    }
    if(newPin === _tempPin){
      changeErr.textContent = 'New PIN must be different from your current PIN.';
      changeErr.style.display = 'block'; return;
    }
    fetch(BEA + '/admin/change-pin', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({current_pin: _tempPin, new_pin: newPin})
    })
    .then(function(r){
      return r.text().then(function(t){
        var d = null; try { d = JSON.parse(t); } catch(e) {}
        if(d && d.token){
          sessionStorage.setItem('ms_admin_token', d.token);
          hideGate();
        } else if(d && d.detail){
          changeErr.textContent = d.detail;
          changeErr.style.display = 'block';
        } else if(r.status === 401 || r.status === 403){
          /* GATE-TRUTH-2: the change-PIN path was left blind by GATE-TRUTH-1, which only
             patched the login path in this file. Same origin gate, same blind parse. */
          /* GATE-NOLOCK-1: /admin/change-pin is exempt at the origin too (migrations/025). */
          changeErr.textContent = 'Current PIN not accepted. If this box is new, open https://trustsquare.co/ once and unlock it there first.';
          changeErr.style.display = 'block';
        } else {
          changeErr.textContent = 'PIN change failed (' + r.status + '). Please try again.';
          changeErr.style.display = 'block';
        }
      });
    })
    .catch(function(){
      changeErr.textContent = 'Connection error. Please try again.';
      changeErr.style.display = 'block';
    });
  };
