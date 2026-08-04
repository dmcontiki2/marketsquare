/* ══════════════════════════════════════════════════════════════════════════
   TrustSquare — tester fault reporter  (MAINT-B1b, 5 Aug 2026)
   The in-app NCR channel. First-party only: no CDN, no third-party script,
   no dependency on ms.js or ms.css — this file must work identically on the
   index, the admin tool, the legal pages and the nine adventure maps.
   Visible only to gated pre-launch testers, and only while the server flag
   launch_switches.fault_report is on. Fail-closed on every error path.
   ═══════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  if (window.__tsReportLoaded) return;
  window.__tsReportLoaded = true;

  var BEA = 'https://trustsquare.co';
  var NAVY = '#0c1a2e', GOLD = '#C8873A', LINE = '#e2e8f0';

  /* ── console tail: the last few errors, so a report carries evidence ── */
  var tail = [];
  function cap(kind, orig) {
    return function () {
      try {
        var parts = [];
        for (var i = 0; i < arguments.length; i++) {
          var a = arguments[i];
          parts.push(typeof a === 'string' ? a : (a && a.message) ? a.message : String(a));
        }
        tail.push(kind + ': ' + parts.join(' ').slice(0, 200));
        if (tail.length > 8) tail.shift();
      } catch (e) { /* never break the page */ }
      return orig.apply(console, arguments);
    };
  }
  try {
    console.error = cap('error', console.error);
    console.warn = cap('warn', console.warn);
    window.addEventListener('error', function (e) {
      try { tail.push('uncaught: ' + String(e.message).slice(0, 200)); if (tail.length > 8) tail.shift(); } catch (x) {}
    });
  } catch (e) {}

  /* ── who is this, and may they see the button ── */
  function ls(k) { try { return localStorage.getItem(k) || ''; } catch (e) { return ''; } }
  function ss(k) { try { return sessionStorage.getItem(k) || ''; } catch (e) { return ''; } }
  function reviewToken() { return ss('ms_review_token'); }
  function hasReviewCookie() { return /(^|;\s*)ts_review=/.test(document.cookie || ''); }
  function testerEmail() { return ss('aa_email') || ls('ms_aa_email') || ls('ms_user_email') || ''; }
  function testerName() { return ls('ms_aa_name') || ls('ms_user_name') || ''; }
  function isTester() { return ls('ms_superuser') === '1' || !!reviewToken() || hasReviewCookie(); }
  function appVersion() {
    try {
      var m = (document.documentElement.innerHTML.match(/ms\.js\?v=(\d+)/) || [])[1];
      return m ? 'ms.js v' + m : (document.title || 'page').slice(0, 40);
    } catch (e) { return ''; }
  }

  var AREAS = [
    ['MISC', 'Not sure / something else'],
    ['AUTH', 'Signing in, my account'],
    ['LIST', 'Listings and adverts'],
    ['TRUST', 'Trust score, badges, ranking'],
    ['INTRO', 'Introductions, Tuppence, payment'],
    ['BROWSE', 'Search, browsing, categories'],
    ['ADV', 'Adventures and maps'],
    ['MAIL', 'Emails I received'],
    ['PERF', 'Slow, stuck or would not load'],
    ['COPY', 'Wrong wording or a typo']
  ];
  var SEVS = [
    ['blocker', 'Blocked me completely'],
    ['major', 'Got in my way'],
    ['minor', 'Small / cosmetic']
  ];

  function el(tag, css, html) {
    var n = document.createElement(tag);
    if (css) n.style.cssText = css;
    if (html != null) n.innerHTML = html;
    return n;
  }
  var FLD = 'width:100%;box-sizing:border-box;border:1px solid ' + LINE + ';border-radius:8px;' +
            'padding:10px 11px;font:inherit;font-size:14px;color:#1e293b;background:#fff;margin-top:5px;';
  var LBL = 'display:block;font-size:12px;font-weight:700;color:#475569;letter-spacing:.2px;margin-top:14px;';

  /* ── the modal ── */
  function open() {
    if (document.getElementById('ts-report-ov')) return;
    if (window.DEMO_MODE === true) { alert('This is a demo — fault reporting is live-mode only.'); return; }

    var ov = el('div', 'position:fixed;inset:0;background:rgba(8,12,20,.55);z-index:9998;display:flex;' +
                       'align-items:flex-end;justify-content:center;');
    ov.id = 'ts-report-ov';
    var sheet = el('div', 'background:#fff;border-radius:18px 18px 0 0;width:100%;max-width:520px;' +
                          'max-height:92vh;display:flex;flex-direction:column;overflow:hidden;' +
                          'font-family:Inter,system-ui,-apple-system,Segoe UI,Arial,sans-serif;');
    var hdr = el('div', 'display:flex;align-items:center;justify-content:space-between;padding:15px 18px 12px;' +
                        'border-bottom:1px solid ' + LINE + ';flex-shrink:0;',
                 '<span style="font-size:15px;font-weight:800;color:' + NAVY + '">Report a problem</span>');
    var x = el('button', 'background:#f1f5f9;border:none;border-radius:50%;width:30px;height:30px;' +
                         'font-size:14px;cursor:pointer;color:#64748b;font-weight:700;', '&#10005;');
    x.setAttribute('aria-label', 'Close');
    x.onclick = close;
    hdr.appendChild(x);

    var body = el('div', 'overflow-y:auto;padding:4px 18px 22px;flex:1;');
    body.appendChild(el('p', 'font-size:13px;color:#64748b;line-height:1.6;margin:12px 0 2px;',
      'You are testing before launch — thank you. Tell us what happened and we will fix it, ' +
      'then write to you so you can check the fix yourself.'));

    var f = {};
    function field(key, label, node) {
      body.appendChild(el('label', LBL, label));
      body.appendChild(node); f[key] = node; return node;
    }
    field('title', 'What went wrong? <span style="color:' + GOLD + '">*</span>',
          el('input', FLD)).placeholder = 'One line — e.g. "Publish button does nothing"';
    field('detail', 'What were you doing? What did you expect?',
          el('textarea', FLD + 'height:88px;resize:vertical;')).placeholder =
            'Steps you took, what happened instead, anything else that helps us reproduce it.';

    var sev = el('select', FLD);
    SEVS.forEach(function (s) { var o = el('option'); o.value = s[0]; o.textContent = s[1]; sev.appendChild(o); });
    sev.value = 'major';
    field('severity', 'How badly did it affect you?', sev);

    var area = el('select', FLD);
    AREAS.forEach(function (a) { var o = el('option'); o.value = a[0]; o.textContent = a[1]; area.appendChild(o); });
    field('bin', 'Which part of the app?', area);

    var em = field('reporter_email', 'Your email <span style="color:' + GOLD + '">*</span>', el('input', FLD));
    em.type = 'email'; em.value = testerEmail();
    em.placeholder = 'So we can tell you when it is fixed';

    var shot = field('file', 'Screenshot (optional)', el('input', FLD + 'padding:8px;'));
    shot.type = 'file'; shot.accept = 'image/png,image/jpeg,image/webp';

    body.appendChild(el('p', 'font-size:11px;color:#94a3b8;line-height:1.6;margin:14px 0 0;',
      'We store your report with the page address, your browser details and any screenshot you attach, ' +
      'so we can reproduce and fix the fault and reply to you. Testers only, and only until launch.'));

    var note = el('div', 'font-size:13px;font-weight:600;margin:14px 0 0;min-height:18px;');
    body.appendChild(note);

    var send = el('button', 'width:100%;border:none;border-radius:9px;padding:14px;font:inherit;' +
                            'font-size:14px;font-weight:700;cursor:pointer;margin-top:16px;color:#fff;' +
                            'background:' + NAVY + ';', 'Send report');
    body.appendChild(send);
    var cancel = el('button', 'width:100%;background:none;border:none;color:#94a3b8;font:inherit;' +
                              'font-size:13px;font-weight:600;padding:11px;cursor:pointer;', 'Cancel');
    cancel.onclick = close;
    body.appendChild(cancel);

    send.onclick = function () {
      var t = (f.title.value || '').trim(), e = (f.reporter_email.value || '').trim();
      if (!t) { note.style.color = '#b91c1c'; note.textContent = 'Please tell us in one line what went wrong.'; return; }
      if (!e || e.indexOf('@') < 1) { note.style.color = '#b91c1c'; note.textContent = 'We need your email so we can tell you it is fixed.'; return; }
      send.disabled = true; send.textContent = 'Sending…';
      note.style.color = '#64748b'; note.textContent = '';

      var fd = new FormData();
      fd.append('title', t);
      fd.append('detail', f.detail.value || '');
      fd.append('reporter_email', e);
      fd.append('reporter_name', testerName());
      fd.append('bin', f.bin.value);
      fd.append('severity', f.severity.value);
      fd.append('page_url', location.href.slice(0, 500));
      fd.append('app_version', appVersion());
      fd.append('viewport', window.innerWidth + 'x' + window.innerHeight);
      fd.append('console_tail', tail.join(' | ').slice(0, 2000));
      if (f.file.files && f.file.files[0]) fd.append('file', f.file.files[0]);

      var h = {};
      var rt = reviewToken(); if (rt) h['X-Review-Token'] = rt;
      if (window.API_KEY) h['X-Api-Key'] = window.API_KEY;

      fetch(BEA + '/app/fault', { method: 'POST', headers: h, body: fd, credentials: 'same-origin' })
        .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
        .then(function (res) {
          if (!res.ok) throw new Error((res.d && res.d.detail) || 'Could not send');
          done(res.d.ref, res.d.ack_sent);
        })
        .catch(function (err) {
          send.disabled = false; send.textContent = 'Send report';
          note.style.color = '#b91c1c';
          note.textContent = String(err.message || err) + ' — nothing was lost, try once more.';
        });
    };

    function done(ref, acked) {
      body.innerHTML = '';
      body.appendChild(el('div', 'text-align:center;padding:26px 6px 10px;',
        '<div style="font-size:34px">&#10003;</div>' +
        '<h3 style="color:' + NAVY + ';font-size:17px;margin:10px 0 6px">Logged as ' + ref + '</h3>' +
        '<p style="font-size:13px;color:#64748b;line-height:1.65;margin:0 auto;max-width:340px">' +
        (acked ? 'A confirmation is on its way to your inbox. ' : '') +
        'We will fix it and then email you what changed, so you can retest and confirm it is right. ' +
        'Nothing more is needed from you.</p>'));
      var okb = el('button', 'width:100%;border:none;border-radius:9px;padding:13px;font:inherit;' +
                             'font-size:14px;font-weight:700;cursor:pointer;margin-top:20px;color:#fff;' +
                             'background:' + GOLD + ';', 'Back to testing');
      okb.onclick = close;
      body.appendChild(okb);
    }

    sheet.appendChild(hdr); sheet.appendChild(body); ov.appendChild(sheet);
    ov.addEventListener('click', function (ev) { if (ev.target === ov) close(); });
    document.addEventListener('keydown', esc);
    document.body.appendChild(ov);
    setTimeout(function () { try { f.title.focus(); } catch (e) {} }, 60);
  }

  function esc(ev) { if (ev.key === 'Escape') close(); }
  function close() {
    var ov = document.getElementById('ts-report-ov');
    if (ov) ov.parentNode.removeChild(ov);
    document.removeEventListener('keydown', esc);
  }

  /* ── the tab: right edge, vertically centred — the one fixed slot no other
       element on any page already claims (bnav 200 / toast 500 / gate 99999) ── */
  function mountTab() {
    if (document.getElementById('ts-report-tab')) return;
    var b = el('button',
      'position:fixed;right:0;top:50%;transform:translateY(-50%);z-index:9000;' +
      'background:' + NAVY + ';color:#fff;border:none;border-radius:10px 0 0 10px;' +
      'padding:13px 7px;cursor:pointer;font-family:Inter,system-ui,Arial,sans-serif;' +
      'font-size:11px;font-weight:800;letter-spacing:1.4px;writing-mode:vertical-rl;' +
      'box-shadow:0 2px 12px rgba(8,12,20,.28);opacity:.92;', 'REPORT');
    b.id = 'ts-report-tab';
    b.title = 'Report a problem (testers)';
    b.setAttribute('aria-label', 'Report a problem');
    b.onclick = open;
    document.body.appendChild(b);
  }

  function start() {
    if (!isTester()) return;                       // not a tester: nothing renders
    fetch(BEA + '/flags', { credentials: 'same-origin' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) { if (d && d.fault_report) mountTab(); })   // fail-closed
      .catch(function () { /* flag unreadable: stay hidden */ });
  }

  window.tsReportOpen = open;                      // console escape hatch for David
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
