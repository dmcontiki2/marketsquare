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
      'You are testing before launch — thank you. Say what went wrong, snip the screen if it ' +
      'helps, and send. We fix it and write back so you can check it yourself.'));

    var f = {};
    function field(key, label, node) {
      body.appendChild(el('label', LBL, label));
      body.appendChild(node); f[key] = node; return node;
    }
    /* THREE things, deliberately (David, 5 Aug 2026): "we basically paste a snip and say
       what is wrong... having it this simple will increase fix rate tremendously". The two
       fields we dropped — how bad is it, which part of the app — are ones WE can answer
       better than the tester can: the page address arrives with every report, and severity
       is a triage judgement. Never make someone classify a fault to be allowed to report it. */
    field('title', 'What&rsquo;s wrong? <span style="color:' + GOLD + '">*</span>',
          el('textarea', FLD + 'height:104px;resize:vertical;')).placeholder =
            'Just say it plainly — what you did, and what happened instead.';

    var em = field('reporter_email', 'Your email <span style="color:' + GOLD + '">*</span>', el('input', FLD));
    em.type = 'email'; em.value = testerEmail();
    em.placeholder = 'So we can tell you when it is fixed';

    var shot = field('file', 'Screenshot (optional)', el('input', FLD + 'padding:8px;'));
    shot.type = 'file'; shot.accept = 'image/png,image/jpeg,image/webp';

    /* ── Snip the screen, no library ────────────────────────────────────────
       getDisplayMedia is native to the browser, so this stays first-party (RG-0025).
       Desktop only — phones do not implement it, and there the file picker above is
       the right answer anyway because the phone's own screenshot is one button. */
    var captured = null;
    if (navigator.mediaDevices && navigator.mediaDevices.getDisplayMedia) {
      var snipRow = el('div', 'display:flex;gap:9px;align-items:center;margin-top:9px;');
      var snip = el('button', 'flex:0 0 auto;background:' + NAVY + ';color:#fff;border:none;' +
                              'border-radius:8px;padding:9px 13px;font:inherit;font-size:12.5px;' +
                              'font-weight:700;cursor:pointer;', 'Snip this screen');
      var snipNote = el('span', 'font-size:11.5px;color:#94a3b8;line-height:1.4;',
                        'Grabs one frame. You choose what to share.');
      var thumb = el('img', 'display:none;width:74px;height:auto;border:1px solid ' + LINE + ';' +
                            'border-radius:7px;');
      snipRow.appendChild(snip); snipRow.appendChild(snipNote);
      body.appendChild(snipRow); body.appendChild(thumb);

      snip.onclick = function () {
        snip.disabled = true; snip.textContent = 'Choose a window…';
        sheet.style.visibility = 'hidden';          // do not photograph our own form
        navigator.mediaDevices.getDisplayMedia({ video: { displaySurface: 'browser' }, audio: false })
          .then(function (stream) {
            var v = document.createElement('video');
            v.srcObject = stream; v.muted = true;
            return v.play().then(function () {
              return new Promise(function (res) { setTimeout(function () { res(v); }, 260); });
            });
          })
          .then(function (v) {
            var cv = document.createElement('canvas');
            cv.width = v.videoWidth; cv.height = v.videoHeight;
            cv.getContext('2d').drawImage(v, 0, 0);
            (v.srcObject.getTracks() || []).forEach(function (t) { t.stop(); });
            return new Promise(function (res) { cv.toBlob(res, 'image/png'); });
          })
          .then(function (blob) {
            sheet.style.visibility = '';
            if (!blob) throw new Error('nothing captured');
            captured = blob;
            thumb.src = URL.createObjectURL(blob); thumb.style.display = 'block';
            snip.disabled = false; snip.textContent = 'Snip again';
            snipNote.textContent = 'Attached (' + Math.round(blob.size / 1024) + ' KB).';
            snipNote.style.color = '#15803d';
          })
          .catch(function () {
            sheet.style.visibility = '';
            snip.disabled = false; snip.textContent = 'Snip this screen';
            snipNote.textContent = 'No capture — attach a file instead, or just describe it.';
          });
      };
    }

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
      if (!t) { note.style.color = '#b91c1c'; note.textContent = 'Tell us what went wrong — a sentence is plenty.'; return; }
      if (!e || e.indexOf('@') < 1) { note.style.color = '#b91c1c'; note.textContent = 'We need your email so we can tell you it is fixed.'; return; }
      send.disabled = true; send.textContent = 'Sending…';
      note.style.color = '#64748b'; note.textContent = '';

      var fd = new FormData();
      // first line becomes the headline; the whole thing is kept as the detail
      fd.append('title', t.split('\n')[0].slice(0, 160));
      fd.append('detail', t);
      fd.append('reporter_email', e);
      fd.append('reporter_name', testerName());
      // bin is derived server-side from the page address; severity is set at triage
      fd.append('page_url', location.href.slice(0, 500));
      fd.append('app_version', appVersion());
      fd.append('viewport', window.innerWidth + 'x' + window.innerHeight);
      fd.append('console_tail', tail.join(' | ').slice(0, 2000));
      if (f.file.files && f.file.files[0]) fd.append('file', f.file.files[0]);
      else if (captured) fd.append('file', captured, 'snip.png');

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
      'background:' + GOLD + ';color:#fff;border:none;border-radius:12px 0 0 12px;' +
      'padding:16px 9px;cursor:pointer;font-family:Inter,system-ui,Arial,sans-serif;' +
      'font-size:12px;font-weight:800;letter-spacing:1.6px;writing-mode:vertical-rl;' +
      'box-shadow:-2px 2px 16px rgba(200,135,58,.5);opacity:1;', 'REPORT');
    b.id = 'ts-report-tab';
    b.title = 'Report a problem (testers)';
    b.setAttribute('aria-label', 'Report a problem');
    b.onclick = open;
    document.body.appendChild(b);
  }

  /* One-time pointer. The failure this prevents: a tester who never notices the tab
     never reports anything, and silence reads exactly like "no faults found". */
  function coach() {
    try { if (localStorage.getItem('ts_report_seen') === '1') return; } catch (e) { return; }
    var c = el('div',
      'position:fixed;right:56px;top:50%;transform:translateY(-50%);z-index:9001;max-width:216px;' +
      'background:' + NAVY + ';color:#fff;border-radius:12px;padding:13px 15px;' +
      'font-family:Inter,system-ui,Arial,sans-serif;font-size:12.5px;line-height:1.5;' +
      'box-shadow:0 6px 22px rgba(8,12,20,.34);',
      '<b style="display:block;margin-bottom:3px;font-size:13px">Something wrong?</b>' +
      'Tap <b style="color:' + GOLD + '">REPORT</b> any time, on any page. We fix it and write ' +
      'back so you can check it.');
    var arrow = el('span', 'position:absolute;right:-6px;top:50%;transform:translateY(-50%) rotate(45deg);' +
                           'width:12px;height:12px;background:' + NAVY + ';');
    var got = el('button', 'display:block;margin-top:10px;background:' + GOLD + ';color:#fff;border:none;' +
                           'border-radius:7px;padding:7px 12px;font:inherit;font-size:12px;font-weight:700;' +
                           'cursor:pointer;', 'Got it');
    got.onclick = function () {
      try { localStorage.setItem('ts_report_seen', '1'); } catch (e) {}
      if (c.parentNode) c.parentNode.removeChild(c);
    };
    c.appendChild(arrow); c.appendChild(got);
    c.id = 'ts-report-coach';
    document.body.appendChild(c);
    setTimeout(function () {           // never nag: it fades itself after 12 seconds
      if (c.parentNode) { c.style.transition = 'opacity .5s'; c.style.opacity = '0';
        setTimeout(function () { if (c.parentNode) c.parentNode.removeChild(c); }, 600); }
    }, 12000);
  }

  function start() {
    if (!isTester()) return;                       // not a tester: nothing renders
    fetch(BEA + '/flags', { credentials: 'same-origin' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) { if (d && d.fault_report) { mountTab(); coach(); } })   // fail-closed
      .catch(function () { /* flag unreadable: stay hidden */ });
  }

  window.tsReportOpen = open;                      // console escape hatch for David
  window.tsReportWhere = function () {             // 'where is it?' -- flash it, re-show the pointer
    try { localStorage.removeItem('ts_report_seen'); } catch (e) {}
    var t = document.getElementById('ts-report-tab');
    if (!t) { mountTab(); t = document.getElementById('ts-report-tab'); }
    if (!document.getElementById('ts-report-coach')) coach();
    var n = 0, iv = setInterval(function () {
      t.style.transform = 'translateY(-50%) scale(' + (n % 2 ? 1 : 1.18) + ')';
      if (++n > 7) { clearInterval(iv); t.style.transform = 'translateY(-50%)'; }
    }, 220);
    return 'tab flashing on the right edge';
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
