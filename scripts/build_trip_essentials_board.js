/* build_trip_essentials_board.js — TRIP-ESSENTIALS-1 (21 Aug 2026)
   Renders all 13 "Before you go" panels into one standalone page David can open and
   re-read: MarketSquare/TRIP_ESSENTIALS_BOARD.html, indexed by Visuals/refresh_visuals.py.
   It lifts the renderer straight out of ms.js, so the board always shows what actually
   ships. NOTE the filename: refresh_visuals.py skips *_PREVIEW.* as throwaway build
   output, so a board meant for the gallery must never be called a preview.
   Run:  node scripts/build_trip_essentials_board.js
   Then: python3 ../Visuals/refresh_visuals.py                                        */
const fs=require('fs'),path=require('path');
const ROOT=path.join(__dirname,'..');
global.window={};
eval(fs.readFileSync(path.join(ROOT,'trip_essentials.js'),'utf8'));
const TE=global.window.TRIP_ESSENTIALS;
const ms=fs.readFileSync(path.join(ROOT,'ms.js'),'utf8');
const START='function tripEssentialsFor(l){', END="\n    + '</div>';\n}";
const i=ms.indexOf(START), j=ms.indexOf(END, ms.indexOf('function tripEssentialsPanel'));
function tourKeyOf(l){ if(l&&l.tour) return String(l.tour).toLowerCase(); var c=((l&&l.country)||'').toString().toUpperCase(); return c==='NA'?'na':c==='MZ'?'mz':c==='BW'?'bw':''; }
eval(ms.slice(i,j+END.length));
function openModal(){}
const panels=TE.trips.map(t=>{
  const l = t.match.tour?{super_example:1,tour:t.match.tour,country:'ZA'}:{super_example:1,country:t.match.country};
  return '<section class="trip"><div class="trip-h"><span class="k">'+t.key+'</span>'+t.title+'</div>'+tripEssentialsPanel(l,'preview')+'</section>';
}).join('\n');
const nav=TE.trips.map(t=>'<a href="#t-'+t.key+'">'+t.key+'</a>').join('');
let out=`<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Before you go — TRIP-ESSENTIALS-1 preview</title>
<style>
:root{--surface:#fff;--surface-2:#f6f7f9;--border:#e3e6ea;--text:#111827;--text-2:#243043;--text-3:#6b7280;--accent:#6d28d9;--r-sm:10px;}
*{box-sizing:border-box}
body{margin:0;background:#eef1f5;color:var(--text);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;}
header{background:#12233d;color:#fff;padding:22px 20px;}
header h1{margin:0 0 4px;font-size:20px;letter-spacing:-.01em}
header p{margin:0;font-size:13px;color:#a9b8cc;max-width:60em}
nav{position:sticky;top:0;background:#0d1b2e;padding:8px 20px;display:flex;gap:6px;flex-wrap:wrap;z-index:9}
nav a{color:#cfe0f5;text-decoration:none;font-size:12px;font-weight:700;background:rgba(255,255,255,.08);padding:4px 10px;border-radius:20px}
main{max-width:820px;margin:0 auto;padding:20px}
.trip{margin:0 0 26px;background:var(--surface);border:1px solid var(--border);border-radius:14px;overflow:hidden;box-shadow:0 2px 14px rgba(16,32,58,.07)}
.trip-h{background:#12233d;color:#fff;padding:11px 16px;font-weight:800;font-size:14px;display:flex;align-items:center;gap:10px}
.trip-h .k{background:#c8892a;border-radius:5px;padding:2px 8px;font-size:11px;letter-spacing:.05em}
.dsec{padding:16px}
.dsec h3{margin:0;font-size:15px;font-family:inherit}
.mapstub{margin:0 16px;padding:26px 14px;text-align:center;background:linear-gradient(160deg,#16324f,#0d1b2e);color:#8fb0d8;border-radius:10px;font-size:12.5px;font-weight:700;border:1px dashed rgba(255,255,255,.18)}
details summary::-webkit-details-marker{display:none}
@media print{nav,header{display:none}.trip{break-inside:avoid;box-shadow:none}}
</style></head><body>
<header><h1>“Before you go” — TRIP-ESSENTIALS-1</h1>
<p>The panel that now sits <strong>under</strong> the journey map on every super-example Adventures advert. Free pre-information: itinerary, real cost, entry and visas, health, safety notices, money, taxes and tipping — ending in the introduction, not a booking. Facts verified ${TE.checked}; every row carries its source; volatile figures are flagged <b>RE-CHECK</b>.</p></header>
<nav>${nav}</nav><main>
${panels}
</main></body></html>`;
// anchor ids + a stub showing where the map sits above each panel
TE.trips.forEach(t=>{ out=out.replace('<section class="trip"><div class="trip-h"><span class="k">'+t.key+'</span>',
  '<section class="trip" id="t-'+t.key+'"><div class="trip-h"><span class="k">'+t.key+'</span>'); });
out=out.split('</div><div class="dsec trip-essentials">').join('</div><div class="mapstub">🗺️ &nbsp;the journey map sits HERE — the essentials go below it (David’s placement ruling, 21 Aug 2026)</div><div class="dsec trip-essentials">');
fs.writeFileSync(path.join(ROOT,'TRIP_ESSENTIALS_BOARD.html'), out, 'utf8');
const css = fs.readFileSync(path.join(ROOT,'ms.css'),'utf8');
const marker = '/* \u2500\u2500 TRIP-ESSENTIALS-1';
const k = css.indexOf(marker);
if (k > -1) {
  const anchor = 'details summary::-webkit-details-marker{display:none}';
  out = out.replace(anchor, anchor + '\n' + css.slice(k));
  fs.writeFileSync(path.join(ROOT,'TRIP_ESSENTIALS_BOARD.html'), out, 'utf8');
}
console.log('written', out.length, 'bytes');
