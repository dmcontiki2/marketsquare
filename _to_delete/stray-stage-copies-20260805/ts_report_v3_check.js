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

    var note = el('div', 'font-size:13px;font-weight:600;margin:12px 0 0;min-height:18px;');

    /* ── Paste. That is the whole interaction. ──────────────────────────────
       David, 5 Aug 2026: "instead of having a complex... can't we just have a paste
       option? open report, say 'the view button doesn't work', snip the button and
       paste it." He is right — Win+Shift+S then Ctrl+V is two things people already
       do. The getDisplayMedia button that was here asked for a permission prompt and
       a window choice to achieve the same end, so it is gone. Drag-and-drop rides the
       same handler for free; the file picker stays for phones, quietly. */
    var captured = null;

    var drop = el('div', 'margin-top:6px;border:2px dashed ' + LINE + ';border-radius:11px;' +
                         'padding:16px 14px;text-align:center;color:#94a3b8;font-size:13px;' +
                         'cursor:pointer;transition:.15s;background:#fcfdfe;',
                  '<b style="color:' + NAVY + ';font-size:13.5px">Paste a screenshot</b><br>' +
                  'Snip it (<b>Win + Shift + S</b>), then press <b>Ctrl + V</b> anywhere in here');
    var pv = el('div', 'display:none;margin-top:10px;border:2px solid #15803d;border-radius:11px;' +
                       'overflow:hidden;background:#fff;');
    var pvHead = el('div', 'display:flex;align-items:center;justify-content:space-between;gap:8px;' +
                           'background:#e8f5ec;padding:8px 11px;font-size:12px;font-weight:700;color:#15803d;');
    var pvLabel = el('span', '', 'This is what you are attaching');
    var pvDrop = el('button', 'background:#fff;border:1px solid #bfe0ca;border-radius:6px;color:#15803d;' +
                              'font:inherit;font-size:11.5px;font-weight:700;padding:3px 9px;cursor:pointer;',
                    'Remove');
    pvHead.appendChild(pvLabel); pvHead.appendChild(pvDrop);
    var thumb = el('img', 'display:block;width:100%;max-height:230px;object-fit:contain;' +
                          'background:#0c1a2e;padding:6px;');   // dark mat: a pale snip still reads
    pv.appendChild(pvHead); pv.appendChild(thumb);
    var shot = el('input', 'display:none;');
    shot.type = 'file'; shot.accept = 'image/*';
    var pick = el('button', 'background:none;border:none;color:#94a3b8;font:inherit;font-size:12px;' +
                            'text-decoration:underline;cursor:pointer;padding:7px 0 0;',
                  'or choose an image from this device');
    pick.onclick = function (ev) { ev.preventDefault(); shot.click(); };
    body.appendChild(drop); body.appendChild(pv); body.appendChild(shot); body.appendChild(pick);
    f.file = shot;

    function detach() {
      captured = null;
      pv.style.display = 'none';
      try { if (thumb.src) URL.revokeObjectURL(thumb.src); } catch (e) {}
      thumb.removeAttribute('src');
      drop.style.borderColor = LINE; drop.style.background = '#fcfdfe';
      drop.innerHTML = '<b style="color:' + NAVY + ';font-size:13.5px">Paste a screenshot</b><br>' +
                       'Snip it (<b>Win + Shift + S</b>), then press <b>Ctrl + V</b> anywhere in here';
      try { shot.value = ''; } catch (e) {}
    }
    pvDrop.onclick = function (ev) { ev.preventDefault(); detach(); };

    function attach(file) {
      if (!file || file.type.indexOf('image/') !== 0) return false;
      captured = file;
      try { thumb.src = URL.createObjectURL(file); pv.style.display = 'block'; } catch (e) {}
      drop.style.borderColor = '#bfe0ca'; drop.style.background = '#f2faf5';
      drop.innerHTML = '<b style="color:#15803d">&#10003; Screenshot attached</b> &middot; ' +
                       Math.round(file.size / 1024) + ' KB<br>' +
                       '<span style="font-size:12px">Paste again to replace it</span>';
      /* David, 5 Aug: "it pasted something but I could not identify it as the snippy."
         The paste HAD worked — the preview simply rendered below the fold of the scrolling
         sheet, so from where he sat nothing visibly happened. Attaching silently is the same
         as not attaching at all. Show it, and say so where he is already looking. */
      note.style.color = '#15803d';
      note.textContent = 'Screenshot attached — check the picture below, then send.';
      setTimeout(function () {
        try { pv.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); } catch (e) {
          pv.scrollIntoView(false);
        }
      }, 40);
      return true;
    }

    function onPaste(ev) {
      var items = (ev.clipboardData || window.clipboardData || {}).items || [];
      for (var i = 0; i < items.length; i++) {
        if (items[i].type && items[i].type.indexOf('image/') === 0) {
          var file = items[i].getAsFile();
          if (attach(file)) { ev.preventDefault(); return; }
        }
      }
    }
    sheet.addEventListener('paste', onPaste);      // catches the textarea and everything else
    _paste = onPaste;
    document.addEventListener('paste', onPaste);   // and a paste with nothing focused

    drop.onclick = function () { shot.click(); };
    shot.onchange = function () { if (shot.files && shot.files[0]) attach(shot.files[0]); };
    ['dragenter', 'dragover'].forEach(function (evt) {
      drop.addEventListener(evt, function (e) {
        e.preventDefault(); drop.style.borderColor = GOLD; drop.style.background = '#fdf8f1';
      });
    });
    drop.addEventListener('dragleave', function () {
      if (!captured) { drop.style.borderColor = LINE; drop.style.background = '#fcfdfe'; }
    });
    drop.addEventListener('drop', function (e) {
      e.preventDefault();
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) attach(e.dataTransfer.files[0]);
    });

    body.appendChild(el('p', 'font-size:11px;color:#94a3b8;line-height:1.6;margin:14px 0 0;',
      'We store your report with the page address, your browser details and any screenshot you attach, ' +
      'so we can reproduce and fix the fault and reply to you. Testers only, and only until launch.'));

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
      if (captured) fd.append('file', captured, captured.name || 'pasted.png');

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
  var _paste = null;                                 // so close() can unhook it
  function close() {
    var ov = document.getElementById('ts-report-ov');
    if (ov) ov.parentNode.removeChild(ov);
    document.removeEventListener('keydown', esc);
    if (_paste) { document.removeEventListener('paste', _paste); _paste = null; }
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
