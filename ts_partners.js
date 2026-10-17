/* ══════════════════════════════════════════════════════════════════════════
   TrustSquare — "Plan the rest of your trip" partner card (LINKOUT-ON-1,
   17 Oct 2026, RUL-236: David, "Please switch it on").

   FIRST-PARTY ONLY, exactly like ts_fares.js. No CDN, no third-party script,
   no affiliate JS (RG-0025, the 3 Aug 2026 breach). The ONLY network call is to
   our own /go/partners. Every link points at our own /go/partner/<slug>, which
   records the click and 302s to the partner. The partner never runs code here.

   RENDERS NOTHING unless there is something true to say:
     * lane switched off -> /go/partners 404s -> nothing
     * empty list        -> nothing
     * any error         -> caught            -> nothing

   HONESTY, STRUCTURAL: the commission disclosure is IN the card, every link is
   rel="nofollow sponsored", and the card says we are not a travel agency.
   ═══════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  if (window.__tsPartnersLoaded) return;
  window.__tsPartnersLoaded = true;

  var NAVY = '#0c1a2e', INK = '#1f2d3d', MUTED = '#5b6b7d', GOLD = '#b8860b';

  /* Customer words for each partner category, in the order a traveller needs them.
     Colour per group so the list scans at a glance. */
  var GROUPS = [
    { label: 'Flights',               cats: ['Flights'],                  col: '#1f5fbf' },
    { label: 'Airport transfers',     cats: ['Transfers'],                col: '#0f8a6a' },
    { label: 'Car & bike hire',       cats: ['Car rental', 'Bike rental'], col: '#7a4fbf' },
    { label: 'Tours & activities',    cats: ['Tours & Activities'],       col: '#c2581b' },
    { label: 'Mobile data (eSIM)',    cats: ['eSIM'],                     col: '#0a7ea4' },
    { label: 'Travel insurance',      cats: ['Travel insurance'],         col: '#a3283a' },
    { label: 'Delayed-flight claims', cats: ['Flight compensation'],      col: '#5b6b7d' },
    { label: 'Luggage storage',       cats: ['Luggage storage'],          col: '#8a6d1f' }
  ];

  function mapSlug() {
    var attr = document.body && document.body.getAttribute('data-ts-map');
    if (attr) return attr;
    var m = (location.pathname || '').match(/adventures_([a-z0-9_]+)_map\.html/i);
    return m ? m[1] : null;
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function render(data) {
    var progs = (data && data.programs) || [];
    if (!progs.length) return;

    var wrap = document.createElement('div');
    wrap.id = 'ts-partner-card';
    wrap.style.cssText =
      'position:fixed;right:14px;bottom:34px;z-index:9001;' +
      'font-family:Inter,system-ui,Arial,sans-serif;color:' + INK + ';';

    var pill = document.createElement('button');
    pill.type = 'button';
    pill.setAttribute('aria-expanded', 'false');
    pill.textContent = 'Plan the rest of your trip';
    pill.style.cssText =
      'background:' + NAVY + ';color:#fff;border:none;border-radius:999px;' +
      'padding:9px 15px;font-weight:700;font-size:12.5px;cursor:pointer;' +
      'box-shadow:0 6px 22px rgba(8,12,20,.25);';

    var panel = document.createElement('div');
    panel.style.cssText =
      'display:none;width:min(300px,calc(100vw - 28px));max-height:min(62vh,520px);overflow:auto;' +
      'background:#fff;border:1px solid #dfe5ec;border-left:4px solid ' + NAVY + ';' +
      'border-radius:12px;padding:13px 15px;margin-bottom:8px;font-size:12.5px;line-height:1.45;' +
      'box-shadow:0 6px 22px rgba(8,12,20,.18);';

    var html =
      '<div style="font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:' + MUTED +
      ';margin-bottom:2px">Partner services</div>' +
      '<div style="font-weight:700;font-size:13px;color:' + NAVY + ';margin-bottom:8px">' +
      'Plan the rest of your trip</div>';

    GROUPS.forEach(function (g) {
      var inGroup = progs.filter(function (p) { return g.cats.indexOf(p.category) >= 0; });
      if (!inGroup.length) return;
      html += '<div style="margin:0 0 8px">' +
        '<div style="font-size:11px;font-weight:700;color:' + g.col + ';margin-bottom:4px;' +
        'border-left:3px solid ' + g.col + ';padding-left:6px">' + esc(g.label) + '</div>' +
        '<div style="display:flex;flex-wrap:wrap;gap:5px">';
      inGroup.forEach(function (p) {
        html += '<a href="/go/partner/' + encodeURIComponent(p.slug) + '" target="_blank" ' +
          'rel="nofollow sponsored noopener" style="display:inline-block;text-decoration:none;' +
          'color:' + INK + ';background:#f4f6f9;border:1px solid #e3e8ef;border-radius:7px;' +
          'padding:4px 8px;font-size:11.5px">' + esc(p.brand) + ' &#8599;</a>';
      });
      html += '</div></div>';
    });

    html += '<div style="background:#fbf7ec;border-radius:8px;padding:8px 10px;font-size:11px;' +
      'margin-top:4px;border-left:3px solid ' + GOLD + '">' +
      esc(data.disclosure || 'We may earn a commission if you book. It costs you nothing extra.') +
      '</div>' +
      '<div style="color:' + MUTED + ';font-size:10.5px;margin-top:7px;border-top:1px solid #eef1f5;' +
      'padding-top:7px">MarketSquare is not a travel agency. These are other companies; ' +
      'you book and pay with them directly.</div>';

    panel.innerHTML = html;

    pill.onclick = function () {
      var open = panel.style.display === 'none';
      panel.style.display = open ? 'block' : 'none';
      pill.setAttribute('aria-expanded', open ? 'true' : 'false');
      pill.textContent = open ? 'Close partner list' : 'Plan the rest of your trip';
    };

    wrap.appendChild(panel);
    wrap.appendChild(pill);
    document.body.appendChild(wrap);

    /* On a narrow phone the fare card (bottom-left) and this pill would collide:
       lift the pill above the fare card when both are present. */
    function place() {
      var fare = document.getElementById('ts-fare-card');
      if (window.innerWidth < 640 && fare) {
        wrap.style.bottom = (fare.getBoundingClientRect().height + 24) + 'px';
      } else {
        wrap.style.bottom = '34px';
      }
    }
    place();
    setTimeout(place, 1500);
    window.addEventListener('resize', place);
  }

  function start() {
    if (!mapSlug()) return;                  /* journey maps only */
    var req = new XMLHttpRequest();
    req.open('GET', '/go/partners', true);
    req.timeout = 8000;
    req.onreadystatechange = function () {
      if (req.readyState !== 4) return;
      if (req.status !== 200) return;        /* 404 = lane switched off. Silent. */
      try { render(JSON.parse(req.responseText)); } catch (e) { /* never break a map */ }
    };
    req.ontimeout = req.onerror = function () { /* silence */ };
    try { req.send(); } catch (e) { /* silence */ }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
