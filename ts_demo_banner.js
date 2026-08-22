/* ══════════════════════════════════════════════════════════════════════════
   TrustSquare — DEMO banner  (DEMO-BANNER-1, 22 Aug 2026, David's ruling)
   The permanent honesty label on demonstration pages. First-party only: no
   CDN, no third-party script, no dependency on ms.js or ms.css (RG-0025).

   Why it exists: the AI-made example adverts read as real, buyable listings.
   The badge on the card now says "AI EXAMPLE GENERATED ADVERT"; this says the
   same thing at PAGE level, on the demo maps.

   Deliberately NOT gated on the tester flag. The gold REPORT tab
   is a tester instrument and is removed at Soft Launch; this red DEMO tab is
   for customers and stays. It takes the REPORT slot on the right edge, and
   self-centres in that slot the moment REPORT is gone — no second change
   needed at Soft Launch.
   ═══════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  if (window.__tsDemoBannerLoaded) return;
  window.__tsDemoBannerLoaded = true;

  var RED = '#e63946', NAVY = '#0c1a2e';
  var tab = null, note = null;

  function el(tag, css, html) {
    var n = document.createElement(tag);
    n.style.cssText = css;
    if (html != null) n.innerHTML = html;
    return n;
  }

  /* ── the explainer: one tap, plain words, no jargon ── */
  function toggleNote() {
    if (note && note.parentNode) { note.parentNode.removeChild(note); note = null; return; }
    note = el('div',
      'position:fixed;right:52px;z-index:9002;max-width:250px;' +
      'background:' + NAVY + ';color:#fff;border-radius:12px;padding:14px 16px;' +
      'font-family:Inter,system-ui,Arial,sans-serif;font-size:12.5px;line-height:1.55;' +
      'box-shadow:0 6px 22px rgba(8,12,20,.34);',
      '<b style="display:block;margin-bottom:4px;font-size:13px;color:' + RED + '">This is a demonstration</b>' +
      'The routes, adverts and prices on this page are <b>AI-generated examples</b>. ' +
      'They are not real listings, not for sale, and no introduction can be bought against them. ' +
      'They are here to show how the real thing looks.');
    var got = el('button', 'display:block;margin-top:11px;background:' + RED + ';color:#fff;border:none;' +
                           'border-radius:7px;padding:7px 12px;font:inherit;font-size:12px;font-weight:700;' +
                           'cursor:pointer;', 'Got it');
    got.onclick = toggleNote;
    note.appendChild(got);
    note.id = 'ts-demo-note';
    document.body.appendChild(note);
    place();
  }

  /* ── the tab shares the right-edge slot with REPORT: below it while the
       tester tab exists, dead centre once it is gone (Soft Launch) ── */
  function place() {
    if (!tab) return;
    var rep = document.getElementById('ts-report-tab');
    var h = tab.offsetHeight || 88;
    var top;
    if (rep) {
      var r = rep.getBoundingClientRect();
      top = r.bottom + 10 + h / 2;
      // no room below the tester tab: sit above it instead
      if (top + h / 2 > window.innerHeight - 8) top = r.top - 10 - h / 2;
    } else {
      top = window.innerHeight / 2;
    }
    // never off-screen, whatever the viewport
    top = Math.max(h / 2 + 8, Math.min(top, window.innerHeight - h / 2 - 8));
    tab.style.top = top + 'px';
    tab.style.transform = 'translateY(-50%)';
    if (note && note.parentNode) {
      var nh = note.offsetHeight || 140;
      note.style.top = Math.max(8, Math.min(top - nh / 2, window.innerHeight - nh - 8)) + 'px';
    }
  }

  function mount() {
    if (document.getElementById('ts-demo-tab')) return;
    tab = el('button',
      'position:fixed;right:0;top:50%;transform:translateY(-50%);z-index:9000;' +
      'background:' + RED + ';color:#fff;border:none;border-radius:12px 0 0 12px;' +
      'padding:16px 9px;cursor:pointer;font-family:Inter,system-ui,Arial,sans-serif;' +
      'font-size:12px;font-weight:800;letter-spacing:1.6px;writing-mode:vertical-rl;' +
      'box-shadow:-2px 2px 16px rgba(230,57,70,.5);opacity:1;', 'DEMO');
    tab.id = 'ts-demo-tab';
    tab.title = 'Demonstration page — AI-generated examples, not real listings';
    tab.setAttribute('aria-label', 'Demonstration page. AI-generated examples, not real listings.');
    tab.onclick = toggleNote;
    document.body.appendChild(tab);
    place();

    // REPORT mounts asynchronously (it waits on a server flag) and disappears at
    // Soft Launch; re-place on both events rather than assuming either state.
    try {
      new MutationObserver(place).observe(document.body, { childList: true });
    } catch (e) { /* old browser: the timed retries below still cover it */ }
    var n = 0, iv = setInterval(function () { place(); if (++n > 12) clearInterval(iv); }, 500);
    window.addEventListener('resize', place);
  }

  window.tsDemoBannerPlace = place;                 // console escape hatch for David
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();
