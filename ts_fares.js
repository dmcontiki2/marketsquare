/* ══════════════════════════════════════════════════════════════════════════
   TrustSquare — indicative fare card  (TP-FARES-1, 25 Aug 2026)

   Shows "getting there costs about R x" on a journey map, as FREE
   pre-information, and hands the traveller onward to a real agency.

   FIRST-PARTY ONLY. No CDN, no third-party script, no affiliate JS, no
   dependency on ms.js or ms.css — the same rule ts_demo_banner.js follows and
   the rule the 3 Aug 2026 breach was about (RG-0025). The ONLY network call
   this file makes is to our own /flights/indicative on our own origin, which
   reads our own cache. Travelpayouts is contacted by our server, on a
   schedule, never by this page and never by the traveller's browser.

   RENDERS NOTHING unless there is something true to say:
     * flag off        -> endpoint 404s      -> nothing
     * no cached fare  -> available:false    -> nothing
     * fare too stale  -> available:false    -> nothing
     * any error       -> caught             -> nothing
   A map that says nothing is correct. A map that shows a price it cannot
   stand behind is not. There is deliberately no placeholder, no spinner and
   no "loading fares…" — an empty state that promises a price is a small lie.

   HONESTY, STRUCTURAL:
     * the age of the fare is printed next to the price, always
     * the words "indicative", "not a quote" and "not live availability" are
       not optional copy — the card cannot render without them
     * the outward link is rel="nofollow sponsored", opens in a new tab, and
       carries the commission disclosure IN the card, not in a footer
     * it states we are not a travel agency, because we never replace one
   ═══════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  if (window.__tsFaresLoaded) return;
  window.__tsFaresLoaded = true;

  var NAVY = '#0c1a2e', INK = '#1f2d3d', MUTED = '#5b6b7d', GOLD = '#b8860b';

  /* Which map is this? Explicit attribute wins; filename is the fallback so a
     map that forgets the attribute still works rather than silently doing
     nothing (silence is the correct FAILURE state, not the correct default). */
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

  function ageWords(d) {
    if (d == null) return '';
    if (d < 1) return 'seen today';
    if (d < 2) return 'seen yesterday';
    return 'seen ' + Math.round(d) + ' days ago';
  }

  function render(f) {
    var card = document.createElement('div');
    card.id = 'ts-fare-card';
    card.style.cssText =
      'position:fixed;left:14px;bottom:14px;z-index:9001;max-width:268px;' +
      'background:#fff;color:' + INK + ';border:1px solid #dfe5ec;border-left:4px solid ' + NAVY + ';' +
      'border-radius:12px;padding:13px 15px;' +
      'font-family:Inter,system-ui,Arial,sans-serif;font-size:12.5px;line-height:1.5;' +
      'box-shadow:0 6px 22px rgba(8,12,20,.18);';

    var price = (f.currency === 'ZAR' ? 'R' : (f.currency + ' ')) +
                String(f.price).replace(/\B(?=(\d{3})+(?!\d))/g, ',');

    var html =
      '<div style="font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;' +
      'color:' + MUTED + ';margin-bottom:3px">Getting there</div>' +
      '<div style="font-weight:700;font-size:13px;color:' + NAVY + '">' +
        esc(f.origin) + ' &rarr; ' + esc(f.destination) + '</div>' +
      '<div style="margin:5px 0 2px"><span style="font-size:21px;font-weight:800;color:' + NAVY + '">' +
        esc(price) + '</span>' +
      '<span style="color:' + MUTED + ';font-size:11.5px"> one-way, ' + esc(ageWords(f.age_days)) + '</span></div>' +
      '<div style="color:' + MUTED + ';font-size:11px;margin-bottom:8px">' +
        (f.airline ? esc(f.airline) + ' &middot; ' : '') + 'lowest recently cached fare</div>' +
      '<div style="background:#fbf7ec;border-radius:8px;padding:8px 10px;font-size:11px;' +
      'color:' + INK + ';margin-bottom:9px;border-left:3px solid ' + GOLD + '">' +
        '<b>Indicative only.</b> Not a quote and not live availability. ' +
        'Confirm with a travel agency before you plan around it.</div>';

    if (f.book_url) {
      html += '<a href="' + esc(f.book_url) + '" target="_blank" rel="nofollow sponsored noopener" ' +
              'style="display:block;text-align:center;background:' + NAVY + ';color:#fff;' +
              'text-decoration:none;border-radius:8px;padding:8px 10px;font-weight:700;' +
              'font-size:12px">Check current fares</a>' +
              '<div style="color:' + MUTED + ';font-size:10.5px;margin-top:7px">' +
              'We may earn a commission if you book — it costs you nothing extra, and we are ' +
              'not the seller.</div>';
    }
    html += '<div style="color:' + MUTED + ';font-size:10.5px;margin-top:7px;' +
            'border-top:1px solid #eef1f5;padding-top:7px">' +
            'MarketSquare is not a travel agency. We give you the picture, then introduce ' +
            'you to people who book it properly.</div>';

    var close = document.createElement('button');
    close.setAttribute('aria-label', 'Close fare card');
    close.textContent = '×';
    close.style.cssText = 'position:absolute;top:6px;right:9px;background:none;border:none;' +
                          'font-size:17px;line-height:1;color:' + MUTED + ';cursor:pointer;padding:2px';
    close.onclick = function () { if (card.parentNode) card.parentNode.removeChild(card); };

    card.innerHTML = html;
    card.appendChild(close);
    document.body.appendChild(card);
  }

  function start() {
    var slug = mapSlug();
    if (!slug) return;                       /* not a journey map — say nothing */
    var req = new XMLHttpRequest();
    req.open('GET', '/flights/indicative?map=' + encodeURIComponent(slug), true);
    req.timeout = 8000;
    req.onreadystatechange = function () {
      if (req.readyState !== 4) return;
      if (req.status !== 200) return;        /* 404 = lane dark. Correct. Silent. */
      try {
        var f = JSON.parse(req.responseText);
        if (f && f.available && f.price) render(f);
      } catch (e) { /* never let a fare card break a map */ }
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
