/* ms_gate.js -- SEC-GATE-1 (24 Sep 2026)
   The server now refuses, in one central gate, any action on an account that the caller has not
   proven with a sign-in (typing an email is not proof). This file turns that refusal into the
   right next step instead of a silent failure: when the app's own server answers 401
   "signin_required", the person is taken to the sign-in screen (email -> 6-digit code) with one
   plain sentence; "not_owner" / "not_you" gets one plain sentence too.
   Loaded before ms.js; wraps window.fetch for same-origin calls only and never changes a request. */
(function () {
  if (window.__tsGateFetch) return;
  window.__tsGateFetch = true;
  var _fetch = window.fetch.bind(window);
  var lastPrompt = 0;

  function sameOrigin(input) {
    try {
      var url = typeof input === 'string' ? input : (input && input.url) || '';
      if (url.indexOf('http') !== 0) return true;
      return url.indexOf(location.origin) === 0 || url.indexOf('https://trustsquare.co') === 0;
    } catch (e) { return false; }
  }

  function say(text) {
    try { if (typeof showToast === 'function') { showToast(text); return; } } catch (e) {}
    try { console.warn(text); } catch (e) {}
  }

  function onRefusal(code) {
    var now = Date.now();
    if (now - lastPrompt < 8000) return;
    lastPrompt = now;
    if (code === 'signin_required') {
      say('Please sign in first — we’ll email you a 6-digit code.');
      try { if (typeof goTo === 'function') goTo('signin'); } catch (e) {}
    } else if (code === 'not_owner' || code === 'not_you') {
      say('That belongs to another account. Sign in with the account that owns it.');
    }
  }

  window.fetch = function (input, init) {
    var p = _fetch(input, init);
    if (!sameOrigin(input)) return p;
    // Only an action the person started (a POST/PUT/DELETE, not a background read or a keepalive
    // ping) earns a prompt; background reads that are refused simply stay empty, as before.
    var method = ((init && init.method) || (typeof input !== 'string' && input && input.method) || 'GET').toUpperCase();
    if (method === 'GET' || method === 'HEAD' || (init && init.keepalive)) return p;
    return p.then(function (r) {
      if (r.status === 401 || r.status === 403) {
        try {
          r.clone().json().then(function (d) {
            if (d && d.code) onRefusal(d.code);
          }).catch(function () {});
        } catch (e) {}
      }
      return r;
    });
  };
})();
