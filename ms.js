

// ── BEA API CONFIG ────────────────────────────────────────
// Single source of truth for the live backend URL.
// Phase 1: demo data. Phase 2: live BEA at trustsquare.co
const BEA_URL = 'https://trustsquare.co';
const BEA_ENABLED = true;

// ── Photo resilience: R2 primary → local Hetzner mirror fallback ─────────
// If R2 is unreachable, swap src to /media/<key> served from Hetzner disk.
// R2 pattern: https://pub-xxx.r2.dev/path/file.jpg → /media/path/file.jpg
// Attach via onerror on any img sourced from R2.
function r2Fallback(img) {
  if (img.dataset.r2tried) return; // prevent loop
  img.dataset.r2tried = '1';
  if (/^https?:\/\/[^/]+\.r2\.dev\//.test(img.src)) {
    img.src = img.src.replace(/^https?:\/\/[^/]+\.r2\.dev\//, '/media/');
  }
}
const API_KEY = 'ms_mk_2026_pretoria_admin';
// ── DEMO MODE ────────────────────────────────────────────────
// Set by ?demo=1 URL param (or served via /demo nginx route).
// Hides Sell/Wallet/Seller nav, disables auth flows, shows
// polished placeholder grid. No real seller flows in demo mode.
let DEMO_MODE = new URLSearchParams(window.location.search).get('demo') === '1'; // TODO: REMOVE BEFORE LAUNCH — runtime-mutable for dev toggle
// TODO: REMOVE BEFORE LAUNCH — dev-only display mode for toggling demo vs live listings
let DEMO_DISPLAY_MODE = 'demo'; // 'demo' | 'live' | 'both'
function setDemoDisplay(mode) {
  DEMO_DISPLAY_MODE = mode;
  ['demo','both','live'].forEach(m => {
    const btn = document.getElementById('dtg-'+m);
    if (btn) { btn.style.background = m===mode ? '#e63946' : '#444'; btn.style.color = m===mode ? '#fff' : '#aaa'; }
  });
  renderGrid();
}
// Show toggle panel only in DEMO_MODE
document.addEventListener('DOMContentLoaded', () => {
  const tp = document.getElementById('demo-toggle-panel');
  if (tp && DEMO_MODE) tp.style.display = 'flex';
  else if (tp) tp.style.display = 'none';
  // Init dev toggle pill state
  var dBtn = document.getElementById('dmt-demo');
  var lBtn = document.getElementById('dmt-live');
  if (dBtn) { dBtn.style.background = DEMO_MODE ? '#e63946' : 'transparent'; dBtn.style.color = DEMO_MODE ? '#fff' : 'rgba(255,255,255,.45)'; }
  if (lBtn) { lBtn.style.background = DEMO_MODE ? 'transparent' : '#22c55e'; lBtn.style.color = DEMO_MODE ? 'rgba(255,255,255,.45)' : '#fff'; }
});
// END TODO

// TODO: REMOVE BEFORE LAUNCH — dev toggle function
async function devSetMode(isDemo) {
  DEMO_MODE = isDemo;
  // Update pill appearance
  var dBtn = document.getElementById("dmt-demo");
  var lBtn = document.getElementById("dmt-live");
  if (dBtn) { dBtn.style.background = isDemo ? "#e63946" : "transparent"; dBtn.style.color = isDemo ? "#fff" : "rgba(255,255,255,.45)"; }
  if (lBtn) { lBtn.style.background = isDemo ? "transparent" : "#22c55e"; lBtn.style.color = isDemo ? "rgba(255,255,255,.45)" : "#fff"; }
  // Reset to South Africa / Pretoria when switching to live
  if (!isDemo) {
    activeCountry = { iso2: "ZA", name: "South Africa" };
    activeRegion  = null;
    activeCity    = { id: 47, name: "Pretoria" };
    activeSuburb  = null;
    // Reset the World Heritage filter too — a demo US/UK/AU city sets _wfCountry to
    // that country; without this, switching back to live ZA leaves the strip stuck
    // on the demo country's heritage while the selector still reads "All".
    _wfCountry = 'all';
    const _wfs = document.getElementById('wf-country-select'); if (_wfs) _wfs.value = 'all';
  }
  // If switching to demo and arrays are empty, fetch from BEA first
  if (isDemo && BEA_ENABLED && !LISTINGS.some(l => String(l.id).startsWith('demo_'))) {
    try {
      const [dlRes, dsRes] = await Promise.all([
        fetch(BEA_URL + '/demo-listings'),
        fetch(BEA_URL + '/demo-sellers')
      ]);
      const dlData = await dlRes.json();
      const dsData = await dsRes.json();
      if (dlData.listings && dlData.listings.length) LISTINGS = dlData.listings;
      if (dsData.sellers && dsData.sellers.length)  SELLERS  = dsData.sellers;
      // Re-render immediately after fetch so counts are never stale
      renderGrid(); renderCatCounts(); renderFeatured();
    } catch(e) { console.warn('Demo data fetch failed in devSetMode:', e); }
  }
  // Remove stale live listings when switching to demo (they bleed across cities)
  if (isDemo) {
    for (let i = LISTINGS.length - 1; i >= 0; i--) {
      if (LISTINGS[i].isLive) LISTINGS.splice(i, 1);
    }
  }
  // Re-render everything
  updateBadgeLabel();
  renderGrid();
  renderCatCounts();
  initLMHomeTile();
  if (typeof renderWondersStrip === 'function') renderWondersStrip();
  if (!isDemo) loadLiveListings();
  // Show/hide existing demo-toggle-panel if present
  var tp = document.getElementById("demo-toggle-panel");
  if (tp) tp.style.display = isDemo ? "flex" : "none";
}
// END TODO

// ── END DEMO MODE ────────────────────────────────────────────
let activeCountry = { iso2: 'ZA', name: 'South Africa' };
let activeRegion  = null;                     // { id, name } or null
let activeCity    = { id: null, name: 'Pretoria' }; // id resolved on startup
let activeSuburb  = null;                     // { id, name } or null
let buyerLat = null, buyerLng = null;         // buyer GPS (null = not yet detected)
let nearbyMode = false;                       // true = showing results from multiple nearby suburbs
let nearbySuburbs = [];                       // suburb names within radius when nearbyMode=true
let viewMode = 'grid';                        // 'grid' | 'map'
let _leafletMap = null, _markerLayer = null;  // Leaflet instances

// FLAG: wire buyerTier to Paystack subscription state when Paystack goes live
// Values: 'free' | 'starter' | 'premium'
let buyerTier = 'free';

function updateBadgeLabel() {
  const badge = document.getElementById('home-city-badge');
  if (!badge) return;
  // Top line: country + region (dimmer)
  const geo = [activeCountry.name];
  if (activeRegion) geo.push(activeRegion.name);
  // Bottom line: city only — suburbs are used internally, not exposed in the badge
  const cityLabel = nearbyMode ? '📍 Near me' : (activeCity.name || 'Select city');
  badge.innerHTML =
    `<div class="badge-geo"><span class="cdot"></span>${geo.join(' · ')}</div>` +
    `<div class="badge-loc">${cityLabel}</div>`;
  // Keep all city-bound display strings in sync with activeCity (geo bug fix).
  _refreshCityLabels();
}

// All places in the static DOM that show the current city use class
// `js-city-sub`. Every time activeCity changes, this rewrites them — so
// switching from Pretoria to Johannesburg flows through the entire UI.
function _refreshCityLabels() {
  const cityLabel = activeCity.name || 'your city';
  // Filter sheet subtitles
  document.querySelectorAll('.js-city-sub').forEach(el => {
    el.textContent = `${cityLabel} · narrow your search`;
  });
  // Browse subtitle — recompute so the active filter chip's label updates too
  const sub = document.getElementById('browse-sub');
  if (sub) {
    const f = (typeof activeFilter !== 'undefined' && activeFilter) ? activeFilter : 'All';
    sub.textContent = f === 'All' ? `All categories · ${cityLabel}` : `${f} · ${cityLabel}`;
  }
}

// ── CATEGORY NORMALISER ───────────────────────────────────
// Converts raw BEA category strings to exact CATS keys.
function normCat(raw) {
  const s = (raw || '').toLowerCase().trim();
  if (s === 'property' || s === 'real estate' || s === 'estate agents') return 'Property';
  if (s === 'tutors' || s === 'tutor') return 'Tutors';
  if (s === 'services' || s === 'service' || s === 'technical services' || s === 'technical' || s === 'casuals' || s === 'casual') return 'Services';
  if (s === 'adventures' || s === 'adventure' || s === 'experiences' || s === 'accommodation' ||
      s === 'adventures_accommodation' || s === 'adventures_experiences') return 'Adventures';
  if (s === 'collectors' || s === 'collectibles' || s === 'collectible') return 'Collectors';
  if (s === 'cars' || s === 'car' || s === 'vehicles' || s === 'vehicle' || s === 'help wanted') return 'Cars';
  if (s === 'localmarket' || s === 'local_market' || s === 'local market') return 'LocalMarket';
  return 'Services';
}

// ── API HELPERS ───────────────────────────────────────────
async function apiGet(path) {
  try {
    const res = await fetch(BEA_URL + path);
    if (!res.ok) throw new Error('API error ' + res.status);
    return await res.json();
  } catch(e) {
    console.warn('BEA GET failed:', path, e);
    return null;
  }
}

// Authenticated GET — sends the X-Api-Key header. Use for protected GET endpoints
// (e.g. seller documents). Key travels in the header, never the query string (S3).
async function apiGetAuth(path) {
  try {
    const res = await fetch(BEA_URL + path, { headers: { 'X-Api-Key': API_KEY } });
    if (!res.ok) throw new Error('API error ' + res.status);
    return await res.json();
  } catch(e) {
    console.warn('BEA GET (auth) failed:', path, e);
    return null;
  }
}

async function apiPost(path, data) {
  try {
    const res = await fetch(BEA_URL + path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('API error ' + res.status);
    return await res.json();
  } catch(e) {
    console.warn('BEA POST failed:', path, e);
    return null;
  }
}

async function apiPut(path) {
  try {
    const res = await fetch(BEA_URL + path, { method: 'PUT' });
    if (!res.ok) throw new Error('API error ' + res.status);
    return await res.json();
  } catch(e) {
    console.warn('BEA PUT failed:', path, e);
    return null;
  }
}

// ── LIVE LISTINGS LOADER ──────────────────────────────────
// Merges live BEA listings with demo data for founding sellers.
// Once real sellers are onboarded, demo data will be removed.
async function loadLiveListings(retryCount) {
  if (!BEA_ENABLED || isOffline()) return;
  const attempt = retryCount || 0;
  // Clear previously fetched live listings before reload (needed on city switch)
  for (let i = LISTINGS.length - 1; i >= 0; i--) {
    if (LISTINGS[i].isLive) LISTINGS.splice(i, 1);
  }
  try {
    const suburbParam = nearbyMode ? '' : (activeSuburb ? '&suburb=' + encodeURIComponent(activeSuburb.name) : '');
    const demoParam = DEMO_MODE ? '&demo=1' : '';
    const live = await apiGet('/listings?city=' + encodeURIComponent(activeCity.name) + suburbParam + demoParam);
    if (!live) {
      if (attempt < 3) {
        // Exponential backoff: 3s → 6s → 12s
        const delay = 3000 * Math.pow(2, attempt);
        // Show subtle retry indicator on home Local Market tile
        const lmCount = document.getElementById('lm-home-count');
        if (lmCount && attempt === 0) lmCount.textContent = 'Connecting…';
        setTimeout(() => loadLiveListings(attempt + 1), delay);
      } else {
        // All retries exhausted — show offline-style message
        const lmCount = document.getElementById('lm-home-count');
        if (lmCount) lmCount.textContent = 'Tap to refresh';
        const lmTile = document.getElementById('lm-home-tile');
        if (lmTile) lmTile.onclick = () => { loadLiveListings(0); initLMHomeTile(); };
      }
      return;
    }
    if (live && live.length > 0) {
      // Map BEA listing format to FEA format and prepend to LISTINGS
      const mapped = live.map(l => {
        // Extract multi-photo URLs encoded as [photos:url1|url2|...] prefix
        let desc = l.description || '';
        let photos = [];
        let photoData = []; // [{url, caption}]
        const photoMatch = desc.match(/^\[photos:([^\]]+)\]\n?/);
        if (photoMatch) {
          photoData = photoMatch[1].split('|').filter(Boolean).map(entry => {
            const sep = entry.indexOf('::');
            return sep > -1 ? {url: entry.slice(0, sep), caption: entry.slice(sep+2)} : {url: entry, caption: ''};
          });
          photos = photoData.map(p => p.url);
          desc = desc.replace(photoMatch[0], '');
        }
        // photo_urls: JSON array stored in DB — highest fidelity source, use when present
        if (l.photo_urls && !photos.length) {
          try {
            const pu = typeof l.photo_urls === 'string' ? JSON.parse(l.photo_urls) : l.photo_urls;
            if (Array.isArray(pu) && pu.length) {
              photos = pu.filter(Boolean);
              photoData = photos.map(u => ({url: u, caption: ''}));
            }
          } catch(e) {}
        }
        if (l.medium_url && !photos.length) { photos = [l.medium_url]; photoData = [{url: l.medium_url, caption: ''}]; }
        else if (l.medium_url && photos.length && photos[0] !== l.medium_url) { photos.unshift(l.medium_url); photoData.unshift({url: l.medium_url, caption: ''}); }
        // Property-specific fields — prefer dedicated DB columns, fall back to description parsing
        const knownPropTypes = ['Apartment / Flat','Bachelor / Studio','Granny Flat','Land / Plot','Smallholding','Townhouse','Penthouse','Cluster','Simplex','Duplex','Commercial','Industrial','Farm','House','Other'];
        let propType='', beds=0, baths=0, garages=0, listingType='', furnished='', pets='', features=[];
        if(normCat(l.category)==='Property'){
          // Dedicated columns (set by edit-after-publish)
          if(l.prop_type) propType = l.prop_type;
          else { for(const pt of knownPropTypes){ if(desc.includes(pt)){ propType=pt; break; } } }
          beds    = (l.beds    && l.beds    > 0) ? l.beds    : (desc.match(/(\d+)[-\s]*bed/i)    ? parseInt(desc.match(/(\d+)[-\s]*bed/i)[1])    : 0);
          baths   = (l.baths   && l.baths   > 0) ? l.baths   : (desc.match(/(\d+)[-\s]*bath/i)   ? parseInt(desc.match(/(\d+)[-\s]*bath/i)[1])   : 0);
          garages = (l.garages && l.garages > 0) ? l.garages : (desc.match(/(\d+)[-\s]*garage/i) ? parseInt(desc.match(/(\d+)[-\s]*garage/i)[1]) : 0);
          if(l.listing_type) listingType = l.listing_type === 'For Rent' ? 'rent' : 'sale';
          else if(/for rent|per month|monthly rent|to let|to-let|rental/i.test(desc)) listingType='rent';
          else if(/for sale|asking price|selling price/i.test(desc)) listingType='sale';
          const _furSrc=((l.title||'')+' '+desc);
          if(/\bunfurnished\b/i.test(_furSrc)) furnished='Unfurnished';
          else if(/semi[-\s]?furnished/i.test(_furSrc)) furnished='Semi-furnished';
          else if(/fully furnished/i.test(_furSrc)) furnished='Fully furnished';
          else if(/\bfurnished\b/i.test(_furSrc)) furnished='Fully furnished';
          const petsM=desc.match(/Pets:\s*(Yes|No|Negotiable)/i); if(petsM) pets=petsM[1];
          const featM=desc.match(/Features:\s*([^\n]+)/); if(featM) features=featM[1].split(',').map(f=>f.trim()).filter(Boolean);
        }
        return {
          id: 'bea_' + l.id,
          cat: normCat(l.category),
          feat: false,
          title: l.title,
          city:   l.city || activeCity.name,
          area:   l.area || l.suburb || activeCity.name,
          suburb: l.suburb || l.area || activeCity.name,
          trust: l.trust_score || 40,
          price: l.price || 'POA',
          per: '',
          priceNum: parseInt((l.price||'0').replace(/[^0-9]/g,'')) || 0,
          desc: desc,
          photo: l.thumb_url || (photos[0] || null),
          photos: photos,
          photoData: photoData,
          paused: false,
          queueCount: 0,
          sellerIdx: null,
          isLive: true,
          service_class: l.service_class || null,
          suburb_lat: l.suburb_lat || null,
          suburb_lng: l.suburb_lng || null,
          propType, beds, baths, garages, listingType, furnished, pets, features,
          floor_area:   l.floor_area   || null,
          erf_size:     l.erf_size     || null,
          subject:      l.subject      || null,
          level:        l.level        || null,
          mode:         l.mode         || null,
          service_type: l.service_type || null,
          availability: l.availability || null,
          collectibleType: l.collectible_type || '',
          condition:       l.condition || '',
          era: (function(){var y=parseInt(l.era_year)||0; return !y?'':(y<1900?'Pre-1900':(y<=1950?'1900–1950':(y<=2000?'1950–2000':'Post-2000')));})(),
          nearby_pois:  l.nearby_pois  || null,
          linked_wonders: l.linked_wonders || null,
          listing_lat:  l.listing_lat  || null,
          listing_lng:  l.listing_lng  || null,
          beaListingId: l.id
        };
      });
      // Add live listings to front of LISTINGS array
      mapped.forEach(l => {
        if (!LISTINGS.find(e => e.id === l.id)) LISTINGS.unshift(l);
      });
      renderGrid();
      renderFeatured();
      renderCatCounts();
      renderHomeStats();
    } else {
      // No live listings — still render grid (shows demo listings) and update counts
      renderGrid();
      renderFeatured();
      renderCatCounts();
      renderHomeStats();
    }
  } catch(e) {
    console.warn('loadLiveListings failed:', e);
  }
}

// ── LIVE DASHBOARD LOADER ─────────────────────────────────
// 1. Fetches seller\'s own published listings via /listings/mine
// 2. Merges pending intros from /intros
async function loadLiveDash() {
  if (!BEA_ENABLED || isOffline()) return;

  // ── Step 1: Load seller\'s own listings ──────────────────
  const sellerEmail = (SELLERS[0] && SELLERS[0]._email) || localStorage.getItem('ms_aa_email') || '';
  if (sellerEmail) {
    try {
      const mine = await apiGet('/listings/mine?email=' + encodeURIComponent(sellerEmail));
      if (mine && mine.length) {
        mine.forEach(l => {
          let dl = dashState.listings.find(d => d.beaListingId === l.id);
          if (!dl) {
            dl = {
              id: 'bea_dl_' + l.id,
              beaListingId: l.id,
              title: l.title,
              cat: normCat(l.category),
              status: l.paused ? 'paused' : 'active',
              photo: l.thumb_url || null,
              isCommit: normCat(l.category) === 'Property',
              intros: [],
              _raw: l
            };
            dashState.listings.push(dl);
          } else {
            dl._raw = l;  // refresh full data for edit form
          }
        });
      }
    } catch(e) { console.warn('loadLiveDash /listings/mine failed:', e); }
  }

  // ── Step 2: Merge pending intros ────────────────────────
  try {
    const intros = await apiGet('/intros');
    if (!intros || !intros.length) return;

    const pending = intros.filter(i => i.status === 'pending');
    if (!pending.length) return;

    pending.forEach(intro => {
      const listing = LISTINGS.find(l => l.id === 'bea_' + intro.listing_id || l.id === intro.listing_id);
      const title = listing ? listing.title : (intro.listing_title || 'Live Listing #' + intro.listing_id);
      const cat   = listing ? listing.cat   : (intro.category || 'Property');
      const photo = listing ? listing.photo : null;

      let dl = dashState.listings.find(d => d.beaListingId === intro.listing_id);
      if (!dl) {
        dl = {
          id: 'bea_dl_' + intro.listing_id,
          beaListingId: intro.listing_id,
          title: title,
          cat: cat,
          status: 'active',
          photo: photo,
          isCommit: cat === 'Property',
          intros: [],
          _raw: null
        };
        dashState.listings.unshift(dl);
      }

      const alreadyAdded = dl.intros.find(i => i.beaId === intro.id);
      if (!alreadyAdded) {
        dl.intros.push({
          id: 'live_' + intro.id,
          beaId: intro.id,
          name: intro.buyer_email || 'Anonymous buyer',
          msg: intro.message || 'Introduction request received.',
          time: formatIntroTime(intro.created_at),
          status: 'pending'
        });
        if (dl.isCommit) dl.status = 'paused';
      }
    });
  } catch(e) {
    console.warn('loadLiveDash intros failed:', e);
  }
}

// ── CURRENCY FORMATTER ────────────────────────────────────
function formatZAR(value) {
  if (value === null || value === undefined || value === '') return null;
  const s = String(value);
  // Detect non-ZAR currency prefix — return raw value as-is
  const currMatch = s.match(/^([A-Z]{1,3}\$?|[£$€¥₹])/);
  if (currMatch && !s.match(/^R\s*[0-9]/i)) return s;
  const numStr = s.replace(/[^0-9.]/g, '');
  if (!numStr) return null;
  const n = parseFloat(numStr);
  if (isNaN(n)) return null;
  const parts = n.toFixed(2).split('.');
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  return 'R' + parts[0] + '.' + parts[1];
}

function formatDescLegacy(desc) {
  if (!desc) return '';
  const lines = desc.split('\n');
  const out = [];
  let listType = null;
  const listItems = [];

  function flushList() {
    if (!listItems.length) return;
    const tag = listType === 'ol' ? 'ol' : 'ul';
    out.push(`<${tag}>${listItems.map(t=>`<li>${t}</li>`).join('')}</${tag}>`);
    listItems.length = 0;
    listType = null;
  }

  for (const raw of lines) {
    const line = raw.trim();
    if (!line) { flushList(); continue; }

    const bulletM  = line.match(/^[·\-\*•]\s+(.+)/);
    const orderedM = line.match(/^\d+[)\.]\s+(.+)/);

    if (bulletM) {
      if (listType === 'ol') flushList();
      listType = 'ul';
      listItems.push(bulletM[1]);
    } else if (orderedM) {
      if (listType === 'ul') flushList();
      listType = 'ol';
      listItems.push(orderedM[1]);
    } else {
      flushList();
      const isHeading = line.endsWith(':') ||
        (line.length <= 50 && !/[.!?,;:]/.test(line));
      if (isHeading) {
        out.push(`<h4 class="desc-heading">${line.replace(/:$/, '')}</h4>`);
      } else {
        out.push(`<p class="desc-p">${line}</p>`);
      }
    }
  }
  flushList();
  return out.join('');
}

function formatDescJSON(d) {
  const out = [];
  if (d.headline) out.push(`<h2 class="desc-headline">${d.headline}</h2>`);
  if (d.tagline)  out.push(`<p class="desc-tagline">${d.tagline}</p>`);
  if (d.summary)  out.push(`<p class="desc-p">${d.summary}</p>`);
  if (Array.isArray(d.sections)) {
    for (const sec of d.sections) {
      if (sec.heading) out.push(`<h4 class="desc-heading">${sec.heading}</h4>`);
      if (Array.isArray(sec.bullets) && sec.bullets.length)
        out.push(`<ul>${sec.bullets.map(b=>`<li>${b}</li>`).join('')}</ul>`);
    }
  }
  return out.join('');
}

function formatDesc(desc) {
  if (!desc) return '';
  if (desc.trimStart().startsWith('{')) {
    try {
      const d = JSON.parse(desc);
      return formatDescJSON(d);
    } catch (e) { /* fall through to legacy */ }
  }
  return formatDescLegacy(desc);
}

function formatIntroTime(ts) {
  if (!ts) return 'Recently';
  try {
    const diff = Math.floor((Date.now() - new Date(ts).getTime()) / 1000);
    if (diff < 60)   return 'Just now';
    if (diff < 3600) return Math.floor(diff/60) + 'm ago';
    if (diff < 86400) return Math.floor(diff/3600) + 'h ago';
    return Math.floor(diff/86400) + 'd ago';
  } catch(e) { return 'Recently'; }
}

let activeFilter='All', wishlist=new Set(), prevScreen='browse';
let tuppence=50, pendingIntroId=null, pendingLMIntroId=null; // 🧪 TEST: 50 — reset to 5 before launch
let magicLink={active:false,name:'',email:'',cat:'',area:''};

// ── OFFLINE STATE ─────────────────────────────────────────
function isOffline(){ return !navigator.onLine; }

// ── SUPERUSER ──────────────────────────────────────────────
// Core team bypass — all gates disabled until launch day.
function isSuperuser(){ return localStorage.getItem('ms_superuser') === '1'; }

function showOfflineBanner(){
  const b=document.getElementById('offline-banner');
  const m=document.getElementById('offline-msg');
  if(!b) return;
  b.classList.remove('back-online');
  if(m) m.textContent="You're offline — browsing cached content";
  b.classList.add('show');
}

function showBackOnlineBanner(){
  const b=document.getElementById('offline-banner');
  const m=document.getElementById('offline-msg');
  if(!b) return;
  b.classList.add('back-online','show');
  if(m) m.textContent='Back online ✓';
  setTimeout(()=>b.classList.remove('show','back-online'), 2800);
}

window.addEventListener('offline', ()=>{ showOfflineBanner(); });
window.addEventListener('online',  ()=>{ showBackOnlineBanner(); });

// Check on load in case app opened while already offline
async function _msInit(){
  if(isOffline()) showOfflineBanner();

  // ── DEMO MODE ACTIVATION ─────────────────────────────────
  if (DEMO_MODE) {
    // Hide real seller nav buttons, show demo join CTA
    ['nav-onboard','nav-tuppence','nav-myspace'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.style.display = 'none';
    });
    const demoJoin = document.getElementById('nav-demo-join');
    if (demoJoin) demoJoin.style.display = '';
    // Sticky demo banner
    const banner = document.createElement('div');
    banner.id = 'demo-banner';
    banner.style.cssText = 'background:linear-gradient(135deg,#1e3a5f,#2d6a9f);color:#fff;text-align:center;padding:10px 16px;font-size:13px;font-weight:600;letter-spacing:0.3px;position:sticky;top:0;z-index:9999;';
    banner.innerHTML = '🔍 Demo mode — Browse freely. <span style="text-decoration:underline;cursor:pointer;" onclick="demoBannerJoin()">Join as a founding seller →</span>';
    document.body.prepend(banner);
    // Go straight to browse so prospects see the marketplace
    setTimeout(() => goTo('browse'), 100);
  }
  // ── END DEMO MODE ACTIVATION ─────────────────────────────

  // ââ MAGIC LINK PARSER ─────────────────────────────────────
  // Reads URL params generated by admin tool and pre-fills onboard screen.
  // URL format: trustsquare.co?magic=1&name=...&email=...&cat=...&city=...
  const sp = new URLSearchParams(window.location.search);
  if(sp.get('magic')==='1'){
    magicLink = {
      active: true,
      name:   decodeURIComponent(sp.get('name')  || ''),
      email:  decodeURIComponent(sp.get('email') || ''),
      cat:    decodeURIComponent(sp.get('cat')   || ''),
      area:   decodeURIComponent(sp.get('city')  || activeCity.name || '')
    };
    // Strip params from URL bar without reloading
    window.history.replaceState({}, '', window.location.pathname);
    // drafted=1 means admin already saved listings — skip photo upload, go to tier+EULA
    if(sp.get('drafted')==='1'){
      goTo('seller-onboard');
    } else {
      // Route to guided onboarding (3-step photo-first screen → seller-onboard funnel)
      goTo('guided-onboard');
    }
  }
  // ── END MAGIC LINK PARSER ─────────────────────────────────

  // ── PLANS DEEP-LINK ────────────────────────────────────────
  // trustsquare.co/?plans=1 — opens subscription plans screen directly (used by admin app link)
  if (sp.get('plans') === '1') {
    window.history.replaceState({}, '', window.location.pathname);
    setTimeout(() => openPlans('dashboard'), 100);
  }

  // ── PAYSTACK RETURN HANDLER ────────────────────────────────
  // Paystack redirects back to trustsquare.co?ps_return=1&reference=ms_tuppence_xxx
  // We verify the payment server-side, update the balance, and show a result.
  if(sp.get('ps_return')==='1'){
    const ref = sp.get('reference') || sp.get('trxref') || '';
    window.history.replaceState({}, '', window.location.pathname);
    if(ref){
      (async()=>{
        try{
          const r = await fetch(BEA_URL+'/payment/verify?reference='+encodeURIComponent(ref));
          const d = await r.json();
          if(d.status==='ok'){
            const credited = d.tuppence_credited || 0;
            const aiCredited = d.ai_sessions_credited || 0;
            // Update local Tuppence balance
            tuppence += credited;
            updateTuppenceUI();
            // Show success message
            let msg = '';
            if(credited>0 && aiCredited>0) msg=`Payment successful — ${credited}T and ${aiCredited} AI uses added!`;
            else if(credited>0) msg=`Payment successful — ${credited} Tuppence added to your wallet!`;
            else if(aiCredited>0) msg=`Payment successful — ${aiCredited} AI coaching uses added!`;
            else msg='Payment confirmed!';
            showToast(msg, 5000);
            // Navigate to wallet so they see the new balance
            goTo('tuppence');
          } else {
            showToast('Payment could not be verified — contact support if you were charged.');
          }
        } catch(e){
          showToast('Could not verify payment — please check your wallet balance.');
        }
      })();
    } else {
      // ps_return=1 but no reference — Paystack cancelled or back button
      showToast('Payment was cancelled.');
    }
  }
  // ── END PAYSTACK RETURN HANDLER ───────────────────────────

  // ── SELLER SUBSCRIPTION RETURN HANDLER ─────────────────────
  // Paystack redirects back with ?ps_sub_return=1 after seller tier payment.
  // We verify, set the tier on the BEA, then resume the onboarding at EULA.
  if (sp.get('ps_sub_return') === '1') {
    const ref = sp.get('reference') || sp.get('trxref') || '';
    window.history.replaceState({}, '', window.location.pathname);
    if (ref) {
      (async () => {
        try {
          const r = await fetch(BEA_URL + '/payment/seller-subscription/verify?reference=' + encodeURIComponent(ref));
          const d = await r.json();
          if (d.status === 'ok') {
            // Restore onboarding state from sessionStorage
            let resumed = false;
            try {
              const saved = sessionStorage.getItem('sob_resume');
              if (saved) {
                const s = JSON.parse(saved);
                Object.assign(sobState, s);
                sessionStorage.removeItem('sob_resume');
                resumed = true;
              }
            } catch(_) {}

            if (resumed && sobState.email) {
              // Navigate to seller onboard screen and jump straight to EULA (phase 3)
              goTo('seller-onboard');
              sobGoPhase(3);
              // Re-apply tier selection visuals
              sobSelTier(sobState.selectedTier);
              showToast((d.label || sobState.selectedTier) + ' activated — complete your EULA to go live.', 4000);
            } else {
              showToast('Subscription activated! Re-open your magic link to finish onboarding.');
            }
          } else {
            showToast('Subscription payment could not be verified — contact support if you were charged.');
          }
        } catch(e) {
          showToast('Could not verify subscription — please check your connection.');
        }
      })();
    } else {
      showToast('Subscription payment was cancelled.');
    }
  }
  // ── END SELLER SUBSCRIPTION RETURN HANDLER ─────────────────

  // ── RESTORE SELLER PROFILE from localStorage ───────────────
  try {
    const storedProfile = localStorage.getItem('ms_seller_profile');
    if (storedProfile && SELLERS[0]) Object.assign(SELLERS[0], JSON.parse(storedProfile));
    const storedPhoto = localStorage.getItem('ms_seller_photo');
    if (storedPhoto) SELLER_PHOTOS[0] = storedPhoto;
  } catch(_){}

  // ── SYNC TUPPENCE BALANCE from BEA (dev phase) ──────────────
  // Allows dev-seeded balances to reflect without Paystack.
  // If BEA balance > local balance, use BEA value.
  // Remove or gate behind a DEV_MODE flag before public launch.
  (async () => {
    try {
      const buyerEmail = (SELLERS[0] && SELLERS[0]._email) || localStorage.getItem('ms_aa_email') || '';
      if (!buyerEmail || !BEA_ENABLED) return;
      const res = await fetch(BEA_URL + '/tuppence/balance?email=' + encodeURIComponent(buyerEmail));
      if (!res.ok) return;
      const data = await res.json();
      if (data.balance > tuppence) {
        tuppence = data.balance;
        updateTuppenceUI();
      }
    } catch(_) { /* silent — hardcoded default remains */ }
  })();

  // ── RESTORE PROFILE PHOTO from BEA if localStorage is empty ─
  // Runs in background so it never slows page load.
  // Covers the case where iOS/Safari cleared localStorage between sessions.
  (async () => {
    try {
      if (SELLER_PHOTOS[0]) return;  // already restored from localStorage — done
      const sellerEmail = (SELLERS[0] && SELLERS[0]._email) || localStorage.getItem('ms_aa_email') || '';
      if (!sellerEmail || !BEA_ENABLED) return;
      const user = await apiGet('/users/' + encodeURIComponent(sellerEmail));
      if (user && user.photo_url) {
        // Cache it back to localStorage for next load
        SELLER_PHOTOS[0] = user.photo_url;
        try { localStorage.setItem('ms_seller_photo_url', user.photo_url); } catch(_){}
        // Repaint any profile element already on screen
        const preview = document.getElementById('dash-profile-preview');
        if (preview) renderProfilePreview();
      }
    } catch(_) { /* silent — photo just won\'t show until next manual upload */ }
  })();

  // ── RESTORE USER CITY + SUBSCRIPTION TIER ──────────────────
  try {
    const storedCity = localStorage.getItem('ms_user_city');
    if (storedCity) activeCity = { id: null, name: storedCity };
    const storedTier = localStorage.getItem('ms_buyer_tier');
    if (storedTier) buyerTier = storedTier;
  } catch(_){}

  // Badge: Free tier no longer fully locked — opens suburb selector
  updateBadgeLabel();

  // ── LOAD DEMO DATA (Session 66) ─────────────────────────────
  // Fetch demo listings + sellers from BEA before first render so the grid
  // is populated on DOMContentLoaded. Only runs when DEMO_MODE is true.
  if (DEMO_MODE && BEA_ENABLED && !LISTINGS.some(l => String(l.id).startsWith('demo_'))) {
    try {
      const [dlRes, dsRes] = await Promise.all([
        fetch(BEA_URL + '/demo-listings'),
        fetch(BEA_URL + '/demo-sellers')
      ]);
      const dlData = await dlRes.json();
      const dsData = await dsRes.json();
      if (dlData.listings && dlData.listings.length) LISTINGS = dlData.listings;
      if (dsData.sellers && dsData.sellers.length)  SELLERS  = dsData.sellers;
    } catch(e) { console.warn('Demo data fetch failed, grid will be empty:', e); }
  }
  // ── END LOAD DEMO DATA ────────────────────────────────────
    renderFeatured(); renderGrid(); updateTuppenceUI(); renderDash(); renderRecruit();
  renderHomeStats(); renderCatCounts();
  initLMHomeTile();
  loadHomeWonders();
  catHomeInit();
  // Load available cities + suburbs, then live listings from BEA on startup
  _resolveActiveCity().then(() => loadLiveListings());
  // Detect buyer location for distance badges + map centering
  _detectLocation();
  // Silent background refresh every 30 seconds — picks up new listings without manual reload
  setInterval(() => {
    if (!isOffline()) loadLiveListings();
  }, 30000);
}
// readyState guard: runs immediately if DOMContentLoaded already fired
if (document.readyState === 'loading') {
  window.addEventListener('DOMContentLoaded', _msInit);
} else {
  _msInit();
}


// ── Adventures thumbnail strip sync ─────────────────────────────────────────
function advThumbClick(id, idx) {
  const strip = document.getElementById('pstrip-' + id);
  if (!strip) return;
  strip.scrollTo({ left: idx * strip.offsetWidth, behavior: 'smooth' });
  setTimeout(() => syncAdvThumbs(id, idx), 80);
}

function syncAdvThumbs(id, idx) {
  const container = document.getElementById('adv-thumbs-' + id);
  if (!container) return;
  container.querySelectorAll('.adv-thumb').forEach((t, i) => {
    t.classList.toggle('active', i === idx);
  });
  // scroll the thumb row to keep active thumb visible
  const activeThumb = document.getElementById('adv-thumb-' + id + '-' + idx);
  if (activeThumb) activeThumb.scrollIntoView({ block: 'nearest', inline: 'center' });
}

function trustTier(s){
  if(s<40)return{label:'New',c:'#6b7280',bg:'#f3f4f6'};
  if(s<70)return{label:'Established',c:'var(--blue)',bg:'var(--blue-bg)'};
  if(s<90)return{label:'Trusted',c:'var(--green)',bg:'var(--green-bg)'};
  return{label:'Highly Trusted',c:'var(--gold)',bg:'var(--gold-bg)'};
}
function tbadge(s){const t=trustTier(s);return`<span class="tbadge" style="background:${t.bg};color:${t.c};padding:2px 7px;font-size:10px;border-radius:10px;font-weight:700;">★ ${s}</span>`;}

function updateTuppenceUI(){
  const navBadge = document.getElementById('nav-tn-badge'); if(navBadge) navBadge.textContent=tuppence;
  const bd=document.getElementById('tn-balance-display');   if(bd) bd.textContent=tuppence;
  const hb=document.getElementById('tn-home-bal');          if(hb) hb.textContent=tuppence;  // LM-19: element removed but check defensively
  const d =document.getElementById('dash-tn');              if(d) d.textContent=tuppence;
}
// Local currency display — ZAR at R18/$1 (1T=$2, 1T=R36). Extend when live forex is added.
function localPrice(usd) {
  const zarRate = 18; // ZAR per USD — update to live rate when forex API is wired
  return `$${usd} · R${usd * zarRate}`;
}
let pendingTopUpAmount=0, pendingAIPackSessions=0;
const topUpBundles={5:{zar:'R180',usd:'$10'},10:{zar:'R360',usd:'$20'},25:{zar:'R900',usd:'$50'}};
function topUp(n){
  if(isOffline()){ showToast("You're offline - top-up needs a connection"); return; }
  pendingTopUpAmount=n; pendingAIPackSessions=0;
  const usd=n*2, lp=localPrice(usd);
  document.getElementById('topup-modal-desc').textContent='Purchase '+n+' Tuppence ('+n+' introductions).';
  document.getElementById('topup-bundle-label').textContent=n+'T · '+n+' intros';
  document.getElementById('topup-zar-label').textContent='R'+(n*36);
  document.getElementById('topup-usd-label').textContent='$'+usd;
  document.getElementById('topup-modal').classList.add('open');
}
function aaBuyAIPack(t, sessions){
  if(isOffline()){ showToast("You're offline - purchase needs a connection"); return; }
  pendingTopUpAmount=t; pendingAIPackSessions=sessions;
  const usd=t*2;
  document.getElementById('topup-modal-desc').textContent='Purchase '+sessions+' AI coaching uses ('+t+'T).';
  document.getElementById('topup-bundle-label').textContent=t+'T · '+sessions+' AI uses';
  document.getElementById('topup-zar-label').textContent='R'+(t*36);
  document.getElementById('topup-usd-label').textContent='$'+usd;
  document.getElementById('topup-modal').classList.add('open');
}
function aaBuyPackFromWallet(){ aaBuyAIPack(5,40); }
async function confirmTopUp(){
  const n=pendingTopUpAmount;
  if(!n) return;
  const emailEl=document.getElementById('topup-email');
  const email=emailEl?emailEl.value.trim():'';
  if(!email||!email.includes('@')){ showToast('Please enter your email address'); return; }
  showToast('Redirecting to secure payment...');
  document.getElementById('topup-modal').classList.remove('open');
  const aiSessions=pendingAIPackSessions;
  pendingTopUpAmount=0; pendingAIPackSessions=0;
  try {
    const callbackUrl = encodeURIComponent(window.location.origin + window.location.pathname + '?ps_return=1');
    let url=BEA_URL+'/payment/initialize?email='+encodeURIComponent(email)+'&tuppence='+n+'&callback_url='+callbackUrl;
    if(aiSessions) url+='&ai_pack_sessions='+aiSessions;
    const res = await fetch(url, {method:'POST'});
    const data = await res.json();
    if(data.authorization_url){ window.location.href = data.authorization_url; }
    else { showToast('Payment setup failed — please try again'); }
  } catch(e) {
    showToast('Payment error — please try again');
  }
}
function closeTopUpModal(e){
  if(e.target===document.getElementById('topup-modal'))
    document.getElementById('topup-modal').classList.remove('open');
}
function addTx(label,sub,val,pos){
  const h=document.getElementById('tn-history');if(!h)return;
  const r=document.createElement('div');r.className='tn-row';
  r.innerHTML=`<div><div class="tn-row-label">${label}</div><div class="tn-row-sub">${sub}</div></div><div style="text-align:right"><div class="tn-row-val" style="color:${pos?'var(--green)':'var(--red)'};">${val}</div></div>`;
  h.insertBefore(r,h.firstChild);
}

// Smart routing for + Sell button.
// New sellers → full onboarding screen.
// Returning sellers → account picker sheet (continue or use different account).
async function signInSeller() {
  const email = (document.getElementById('ob-signin-email').value || '').trim();
  const msg   = document.getElementById('ob-signin-msg');
  if (!email) { showToast('Enter your email first'); return; }
  msg.style.display = 'block';
  msg.style.color   = 'var(--text-3)';
  msg.textContent   = 'Checking…';
  try {
    const user = await apiGet('/users/' + encodeURIComponent(email));
    if (user && user.email) {
      const name = user.name || email;
      localStorage.setItem('ms_aa_email', email);
      localStorage.setItem('ms_aa_name',  name);
      if(!localStorage.getItem('ms_joined_date')) localStorage.setItem('ms_joined_date', new Date().toISOString());
      localStorage.setItem('ms_superuser', user.is_superuser ? '1' : '0');
      sessionStorage.setItem('aa_email',   email);
      msg.style.color   = 'var(--green)';
      msg.textContent   = '✓ Signed in as ' + name;
      setTimeout(async () => {
        await loadLiveDash();
        renderDash();
        goTo('dashboard');
      }, 600);
    } else {
      msg.style.color = '#ef4444';
      msg.textContent = 'No account found for that email.';
    }
  } catch(e) {
    msg.style.color = '#ef4444';
    msg.textContent = 'Could not connect — try again.';
  }
}

// ── DEMO MODE HELPERS ───────────────────────────────────────
function demoBannerJoin() {
  // Redirect prospect to the real onboarding app
  window.location.href = 'https://trustsquare.co';
}

function _demoBlock(label) {
  if (!DEMO_MODE) return false;
  showToast('This is a demo. Visit trustsquare.co to join as a founding seller.');
  return true;
}
// ── END DEMO MODE HELPERS ────────────────────────────────────

function openSellNav() {
  if (_demoBlock('openSellNav')) return;
  const email = localStorage.getItem('ms_aa_email');
  if (email) {
    // Populate sheet with stored name + email
    const name = localStorage.getItem('ms_aa_name') || 'Your account';
    const nameEl  = document.getElementById('sell-sheet-name');
    const emailEl = document.getElementById('sell-sheet-email');
    if (nameEl)  nameEl.textContent  = name;
    if (emailEl) emailEl.textContent = email;
    document.getElementById('sell-account-sheet').classList.add('open');
  } else {
    goTo('guided-onboard');   // Route 2 — new seller, guided screen
  }
}
function closeSellSheet(e) {
  if (e.target === document.getElementById('sell-account-sheet'))
    document.getElementById('sell-account-sheet').classList.remove('open');
}
function sellSheetContinue() {
  // Returning seller → Path B (full AI-guided flow)
  document.getElementById('sell-account-sheet').classList.remove('open');
  goTo('sell-b');
}
function sellSheetNewAccount() {
  document.getElementById('sell-account-sheet').classList.remove('open');
  // Don't clear the stored email here — submitOnboard() will overwrite it only
  // when the seller actually completes registration with the new account.
  // This means backing out of onboard always preserves the existing account.
  goTo('onboard');
}

function goTo(name){
  // In demo mode block seller-only screens
  if (DEMO_MODE && (name==='tuppence'||name==='dashboard'||name==='onboard'||name==='publish'||name==='sell-b'||name==='plans'||name==='myspace')) {
    showToast('This is a demo. Visit trustsquare.co to join as a founding seller.');
    return;
  }
  document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));
  document.querySelectorAll('.nb').forEach(b=>b.classList.remove('active'));
  document.getElementById('screen-'+name).classList.add('active');
  const nb=document.getElementById('nav-'+name);if(nb)nb.classList.add('active');
  // Hide bottom nav on AA screens (they have their own navigation)
  const bnav = document.querySelector('.bnav');
  if(bnav) bnav.style.display = name.startsWith('aa-') ? 'none' : '';
  if(name==='home'){ loadHomeWonders(); }
  if(name==='browse'){ renderFilterBar(); renderGrid(); }
  if(name==='local-market') lmLoadGrid();
  if(name==='saved')renderSaved();
  if(name==='dashboard'){
    renderDash();
    switchDashTab('listings');
    loadLiveDash().then(() => {
      updateDashStats();
      document.getElementById('my-listings').innerHTML =
        dashState.listings.map(dl => renderDashCard(dl)).join('');
    });
  }
  if(name==='recruit')renderRecruit();
  if(name==='publish'){resetPublish();}
  if(name==='sell-b'){sbReset();}
  if(name==='plans'){
    const el=document.getElementById('plans-home-city');
    if(el) el.textContent=localStorage.getItem('ms_user_city')||activeCity.name||'your city';
  }
  if(name==='onboard') renderMagicBanner();
  if(name==='aa-home')aaRenderHome();
  if(name==='aa-coach')aaRenderCoachScreen();
  if(name==='aa-publish')aaRenderPublishScreen();
  if(name==='tuppence'){aaLoadWalletSessions();hiwInit();txSyncFilterUI();loadTransactionHistory('tn-history','tn-load-more');}
  if(name==='myspace')msInit();
  if(name==='guided-onboard') goInit();
  if(name==='seller-onboard') sobInit();
  window.scrollTo(0,0);
}
// ── SUBSCRIPTION SCREEN ──────────────────────────────────────
const _SUB_TIERS = [
  { id:'free',         label:'Free',         usd:0,   slots:2,   zar:0,    color:'#64748b', desc:'No credit card required' },
  { id:'standard',     label:'Standard',     usd:12,  slots:10,  zar:216,  color:'#4f46e5', desc:'Best for active sellers' },
  { id:'professional', label:'Professional', usd:20,  slots:25,  zar:360,  color:'#7c3aed', desc:'For serious sellers' },
  { id:'business',     label:'Business',     usd:40,  slots:60,  zar:720,  color:'#0891b2', desc:'Teams and agencies' },
  { id:'elite',        label:'Elite',        usd:100, slots:500, zar:1800, color:'#d97706', desc:'Enterprise volume' },
];
const _TIER_ORDER = _SUB_TIERS.map(t => t.id);

async function openSubscriptionScreen(returnTo) {
  window._subReturnTo = returnTo || 'myspace';
  goTo('subscription');
  // Render loading state
  document.getElementById('sub-screen-tier-label').textContent = '…';
  document.getElementById('sub-screen-slots-used').textContent = '';
  document.getElementById('sub-screen-billing').textContent = '';
  document.getElementById('sub-screen-slot-text').textContent = '…';
  document.getElementById('sub-screen-slot-bar').style.width = '0%';
  document.getElementById('sub-screen-plans').innerHTML = '<div style="color:var(--text-3);font-size:13px;padding:8px 0;">Loading…</div>';

  const email = localStorage.getItem('ms_aa_email') || '';
  let subData = null;
  if (email && BEA_ENABLED) {
    try {
      const r = await fetch(BEA_URL + '/users/' + encodeURIComponent(email) + '/subscription');
      if (r.ok) subData = await r.json();
    } catch(_) {}
  }
  _renderSubscriptionScreen(subData, email);
}

function _renderSubscriptionScreen(d, email) {
  const tier    = d?.seller_tier || 'free';
  const limit   = d?.slot_limit ?? 2;
  const used    = d?.slots_used ?? 0;
  const avail   = d?.slots_available ?? (limit - used);
  const pending = d?.pending_downgrade_tier || null;
  const billEnd = d?.billing_period_end ? d.billing_period_end.substring(0,10) : null;
  const meta    = _SUB_TIERS.find(t => t.id === tier) || _SUB_TIERS[0];

  // Header
  document.getElementById('sub-screen-tier-label').textContent = meta.label + (meta.usd > 0 ? ' · $' + meta.usd + '/mo' : ' · Free');
  document.getElementById('sub-screen-slots-used').textContent = used + ' / ' + limit + ' slots used';
  document.getElementById('sub-screen-billing').textContent = pending
    ? 'Downgrade to ' + (pending.charAt(0).toUpperCase()+pending.slice(1)) + ' pending ' + (billEnd||'')
    : (billEnd ? 'Renews ' + billEnd : meta.usd > 0 ? 'Monthly billing' : 'No billing required');

  // Slot bar
  const pct = limit > 0 ? Math.min(100, Math.round((used/limit)*100)) : 0;
  document.getElementById('sub-screen-slot-text').textContent = avail + ' slot' + (avail!==1?'s':'') + ' available';
  const bar = document.getElementById('sub-screen-slot-bar');
  bar.style.width = pct + '%';
  bar.style.background = pct >= 90 ? '#ef4444' : pct >= 70 ? '#f59e0b' : 'linear-gradient(90deg,#6366f1,#8b5cf6)';

  // Plan cards
  const container = document.getElementById('sub-screen-plans');
  container.innerHTML = '';
  const curRank = _TIER_ORDER.indexOf(tier);

  _SUB_TIERS.forEach(t => {
    const tRank    = _TIER_ORDER.indexOf(t.id);
    const isCur    = t.id === tier;
    const isUp     = tRank > curRank;
    const isDown   = tRank < curRank;
    const btnLabel = isCur ? '✓ Current plan' : isUp ? 'Upgrade →' : 'Downgrade';
    const btnColor = isCur ? 'var(--surface-2)' : isUp ? t.color : '#e2e8f0';
    const btnTxt   = isCur ? 'var(--text-3)' : isUp ? '#fff' : '#64748b';

    const card = document.createElement('div');
    card.style.cssText = `background:var(--surface);border:1.5px solid ${isCur ? t.color : 'var(--border)'};border-radius:14px;padding:14px 16px;`;
    card.innerHTML = `
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
        <div style="font-size:15px;font-weight:800;color:${t.color};">${t.label}</div>
        <button onclick="_subSelectTier('${t.id}','${t.label}',${t.usd},${isDown})" ${isCur?'disabled':''} style="background:${btnColor};color:${btnTxt};border:none;border-radius:50px;padding:6px 14px;font-family:'Syne',sans-serif;font-size:12px;font-weight:700;cursor:${isCur?'default':'pointer'};opacity:${isCur?'.5':'1'};">${btnLabel}</button>
      </div>
      <div style="display:flex;align-items:baseline;gap:4px;">
        <span style="font-size:20px;font-weight:800;color:var(--text);">${t.usd===0?'Free':'$'+t.usd}</span>
        ${t.usd>0?'<span style="font-size:12px;color:var(--text-3);">/month · ≈ R'+t.zar+'</span>':'<span style="font-size:12px;color:var(--text-3);">forever</span>'}
      </div>
      <div style="font-size:12px;color:var(--text-2);margin-top:4px;">${t.slots} listing slots · ${t.desc}</div>
      ${isDown && !isCur ? '<div style="font-size:11px;color:#f59e0b;margin-top:4px;">⏳ Takes effect at end of billing period</div>' : ''}
    `;
    container.appendChild(card);
  });

  // Update the "Me" tab plan line and Overview card if visible
  const meLine = document.getElementById('me-tab-plan-line');
  if (meLine) meLine.textContent = meta.label + ' · ' + limit + ' slots';
  const ovLabel = document.getElementById('overview-plan-label');
  if (ovLabel) ovLabel.textContent = meta.label + ' plan';
  const ovSlots = document.getElementById('overview-slot-label');
  if (ovSlots) ovSlots.textContent = avail + ' of ' + limit + ' slots available · tap to manage';
}

async function _subSelectTier(tierId, tierLabel, usdPrice, isDowngrade) {
  const email = localStorage.getItem('ms_aa_email') || '';
  if (!email) { showToast('Sign in to manage your subscription'); return; }

  if (tierId === 'free') {
    if (!confirm('Switch to Free (2 slots)? Takes effect immediately.\nYou must have ≤2 active listings.')) return;
    try {
      const r = await fetch(BEA_URL + '/users/' + encodeURIComponent(email) + '/seller-tier/downgrade-free', { method: 'POST' });
      const d = await r.json();
      if (!r.ok) { showToast(d.detail || 'Could not switch plan'); return; }
      showToast('Switched to Free plan.');
      openSubscriptionScreen(window._subReturnTo);
    } catch(_) { showToast('Could not switch — check your connection'); }
    return;
  }

  const confirmMsg = isDowngrade
    ? `Downgrade to ${tierLabel} ($${usdPrice}/mo, takes effect at end of billing period)?`
    : `Upgrade to ${tierLabel} ($${usdPrice}/mo)?\nYou'll be redirected to Paystack to complete payment.`;
  if (!confirm(confirmMsg)) return;

  try {
    const r = await fetch(BEA_URL + '/payment/seller-subscription/initialize?email=' +
      encodeURIComponent(email) + '&tier=' + tierId, { method: 'POST' });
    const d = await r.json();
    if (!r.ok) { showToast(d.detail || 'Could not start payment'); return; }
    showToast(isDowngrade ? 'Downgrade scheduled.' : 'Redirecting to payment…');
    if (d.authorization_url) window.location.href = d.authorization_url;
  } catch(_) { showToast('Could not reach server — check your connection'); }
}

function openPlans(returnTo, showSlotCallout) {
  // returnTo: screen name to go back to. showSlotCallout: show the slot-limit warning banner.
  window._plansReturnTo = returnTo || 'dashboard';
  const callout = document.getElementById('plans-slot-callout');
  if (callout) callout.style.display = showSlotCallout ? 'block' : 'none';
  // Highlight current plan button
  const TIER_IDS = ['free','standard','professional','business','elite'];
  const email = localStorage.getItem('ms_aa_email') || '';
  TIER_IDS.forEach(t => {
    const btn = document.getElementById('plan-btn-' + t);
    if (!btn) return;
    btn.textContent = 'Select ' + t.charAt(0).toUpperCase() + t.slice(1);
    btn.className = t === 'standard' ? 'plan-btn accent' : t === 'free' ? 'plan-btn secondary' : 'plan-btn primary';
  });
  // Async: fetch current tier to mark it
  if (email && BEA_ENABLED) {
    fetch(BEA_URL + '/users/' + encodeURIComponent(email) + '/subscription')
      .then(r => r.ok ? r.json() : null)
      .then(d => {
        if (!d) return;
        const cur = d.seller_tier || 'free';
        const btn = document.getElementById('plan-btn-' + cur);
        if (btn) { btn.textContent = '✓ Current plan'; btn.className = 'plan-btn secondary'; btn.disabled = true; }
      }).catch(() => {});
  }
  goTo('plans');
}

function setPlan(tier, label){
  const email = localStorage.getItem('ms_aa_email') || '';
  if (tier === 'free') {
    // Downgrade to free — call self-service endpoint
    if (!email) { showToast('Sign in first'); return; }
    fetch(BEA_URL + '/users/' + encodeURIComponent(email) + '/seller-tier/downgrade-free', { method: 'POST' })
      .then(r => r.json())
      .then(d => {
        if (d.seller_tier) { showToast('Switched to Free plan (2 slots)'); goTo(window._plansReturnTo || 'dashboard'); }
        else showToast(d.detail || 'Could not switch plan');
      }).catch(() => showToast('Could not switch — check your connection'));
    return;
  }
  if (!email) { showToast('Sign in first to upgrade'); return; }
  // Initiate Paystack subscription payment
  const cb = encodeURIComponent(window.location.href.split('?')[0] + '?sub_verify=1');
  fetch(BEA_URL + '/payment/seller-subscription/initialize?email=' + encodeURIComponent(email) +
        '&tier=' + tier + '&callback_url=' + cb, { method: 'POST' })
    .then(r => r.json())
    .then(d => {
      if (d.authorization_url) {
        showToast('Redirecting to payment…');
        window.location.href = d.authorization_url;
      } else {
        showToast(d.detail || 'Payment init failed');
      }
    }).catch(() => showToast('Could not start payment — check your connection'));
}

function filterBrowse(cat){
  // Adventures gets its own dedicated screen
  if(cat==='Adventures'){ goTo('adventures'); refreshAdvCatChips(); renderAdvGrid(); return; }
  activeFilter=cat; goTo('browse');
  document.querySelectorAll('#chip-row .chip').forEach(c=>{
    c.classList.toggle('active', c.textContent.includes(cat)||(cat==='All'&&c.textContent==='All'));
  });
  renderFilterBar(); renderGrid();
  const sub=document.getElementById('browse-sub');
  const cityLabel = activeCity.name || 'your city';
  if(sub) sub.textContent=cat==='All'?`All categories · ${cityLabel}`:`${cat} · ${cityLabel}`;
}


const filterState = {
  property:   { minPrice:'', maxPrice:'', type:'', beds:'', baths:'', garages:'', area:'', listingType:'', furnished:'', pets:'', features:[] },
  tutors:     { maxRate:'', subject:'', level:'', mode:'', area:'' },
  services:   { maxRate:'', serviceClass:'', serviceType:'', availability:'', area:'' },
  adventures: { adventureType:'', environment:'', maxPrice:'', duration:'', groupSize:'', area:'' },
  collectors: { collectibleType:'', maxPrice:'', condition:'', era:'', area:'' },
  cars:       { make:'', maxPrice:'', yearFrom:'', transmission:'', mileage:'', area:'' },
};

// Global Trust >= filter (applies across all categories; client-side over loaded listings)
let trustMin = 0;
function setTrustMin(v){ trustMin = parseInt(v,10) || 0; renderActiveFilterTags(); renderGrid(); }

function setFilter(el, cat){
  if(cat==='Adventures'){ goTo('adventures'); refreshAdvCatChips(); renderAdvGrid(); return; }
  activeFilter = cat;
  document.querySelectorAll('#chip-row .chip').forEach(c=>c.classList.remove('active'));
  el.classList.add('active');
  renderFilterBar();
  renderGrid();
  const sub = document.getElementById('browse-sub');
  const cityLabel = activeCity.name || 'your city';
  if(sub) sub.textContent = cat==='All' ? `All categories · ${cityLabel}` : `${cat} · ${cityLabel}`;
}

function renderFilterBar(){
  const area = document.getElementById('filter-bar-area');
  if(!area) return;

  // Universal layer (Trust now; price/area/scope/currency later) now lives INSIDE the filter sheets.
  _ensureUniversalBlocks();

  if(activeFilter==='All'){
    area.innerHTML = `<div class="filter-bar" style="display:flex;gap:8px;align-items:center;">
      <div class="filter-pill" style="flex:1;justify-content:center;gap:6px;" onclick="openFilterSheet('all')">
        <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line x1="4" y1="6" x2="20" y2="6"/><line x1="8" y1="12" x2="16" y2="12"/><line x1="11" y1="18" x2="13" y2="18"/></svg>
        Filter
      </div>
    </div>`;
    renderActiveFilterTags();
    return;
  }

  const cat = activeFilter.toLowerCase();
  const fs = filterState[cat];

  // Count active filters (skip empty strings, empty arrays, empty price fields)
  let activeCount = 0;
  for(const [k,v] of Object.entries(fs)){
    if(Array.isArray(v)){ if(v.length) activeCount++; }
    else if(v !== '') activeCount++;
  }

  const badgeHtml = activeCount > 0
    ? `<span style="background:var(--accent);color:#fff;border-radius:999px;font-size:11px;font-weight:700;padding:1px 7px;margin-left:6px;">${activeCount}</span>`
    : '';

  area.innerHTML = `<div class="filter-bar" style="display:flex;gap:8px;align-items:center;">
    <div class="filter-pill${activeCount>0?' has-value':''}" style="flex:1;justify-content:center;gap:6px;" onclick="openFilterSheet('${cat}')">
      <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line x1="4" y1="6" x2="20" y2="6"/><line x1="8" y1="12" x2="16" y2="12"/><line x1="11" y1="18" x2="13" y2="18"/></svg>
      Filtered Search${badgeHtml}
    </div>
  </div>`;

  renderActiveFilterTags();
}

function openFilterSheet(cat){
  _ensureUniversalBlocks();
  const _s = document.getElementById('fs-'+cat);
  if(_s) _s.classList.add('open');
  syncAllUniPills();
}
function closeFsBg(e, id){
  if(e.target.id===id) document.getElementById(id).classList.remove('open');
}

// ── Universal filter layer (two-layer, category-scoped model) ──
// One shared block at the top of every filter sheet. Trust now; price/area/scope/currency/Save as they come online.
function _universalBlockHtml(){
  const ts=[['0','Any trust'],['60','Trust ≥ 60'],['70','Trust ≥ 70'],['80','Trust ≥ 80'],['90','Trust ≥ 90']];
  const pills=ts.map(function(p){return `<div class="fs-opt uni-tpill" data-t="${p[0]}" onclick="setTrustMinUI(${p[0]})">${p[1]}</div>`;}).join('');
  return `<div class="fs-section uni-block" style="background:rgba(14,116,144,.06);border:1px solid rgba(14,116,144,.22);border-radius:12px;padding:10px 12px;margin-bottom:12px;">
      <div class="fs-label uni-head" style="color:#0e7490;">◆ Universal · applies in every category</div>
      <div class="fs-options uni-trust-opts">${pills}</div>
    </div>`;
}
function _ensureUniversalBlocks(){
  ['property','tutors','services','adventures','collectors','cars'].forEach(function(cat){
    const sheet=document.querySelector('#fs-'+cat+' .filter-sheet');
    if(sheet && !sheet.querySelector('.uni-block')){
      const anchor=sheet.querySelector('.fs-sub')||sheet.querySelector('.fs-title')||sheet.querySelector('.fs-handle');
      const tmp=document.createElement('div'); tmp.innerHTML=_universalBlockHtml().trim();
      const block=tmp.firstChild;
      if(anchor && anchor.nextSibling) sheet.insertBefore(block, anchor.nextSibling);
      else if(anchor) sheet.appendChild(block);
      else sheet.insertBefore(block, sheet.firstChild);
    }
    if(sheet){
      sheet.querySelectorAll('.fs-section').forEach(function(sec){
        const lbl=sec.querySelector('.fs-label');
        if(lbl && /^Area/i.test(lbl.textContent.trim()) && !sec.classList.contains('uni-block')) sec.style.display='none';
      });
    }
  });
  if(!document.getElementById('fs-all')){
    const bg=document.createElement('div');
    bg.className='filter-sheet-bg'; bg.id='fs-all';
    bg.setAttribute('onclick',"closeFsBg(event,'fs-all')");
    bg.innerHTML=`<div class="filter-sheet">
      <div class="fs-handle"></div>
      <div class="fs-title">⚙ Filter · All categories</div>
      <div class="fs-sub">The universal layer — pick a category for its own filters</div>
      ${_universalBlockHtml()}
      <div class="fs-actions">
        <button class="fs-clear" onclick="setTrustMinUI(0)">Clear</button>
        <button class="fs-apply" onclick="document.getElementById('fs-all').classList.remove('open');renderGrid();">Show results</button>
      </div>
    </div>`;
    document.body.appendChild(bg);
  }
  syncAllUniPills();
}
function syncAllUniPills(){
  const v=trustMin||0;
  document.querySelectorAll('.uni-tpill').forEach(function(p){
    p.classList.toggle('sel', parseInt(p.dataset.t,10)===v);
  });
}
function setTrustMinUI(v){
  setTrustMin(v);
  syncAllUniPills();
}

function toggleOpt(el, group){
  // Single select within group — deselect others
  const parent = el.closest('.fs-options');
  parent.querySelectorAll('.fs-opt').forEach(o=>o.classList.remove('sel'));
  if(el.textContent.trim()==='Any'){
    // Any = clear
  } else {
    el.classList.add('sel');
  }
}

function getSelOpt(sheetId, group){
  const sheet = document.getElementById(sheetId);
  if(!sheet) return '';
  const sel = sheet.querySelector(`.fs-opt.sel`);
  // Find which group this opt belongs to by data approach — use closest fs-section
  const sections = sheet.querySelectorAll('.fs-section');
  for(const sec of sections){
    const opts = sec.querySelectorAll('.fs-opt');
    for(const opt of opts){
      if(opt.classList.contains('sel')) return opt.textContent.trim();
    }
  }
  return '';
}

function getSelOptInSection(sectionLabel, sheetId){
  const sheet = document.getElementById(sheetId);
  if(!sheet) return '';
  for(const sec of sheet.querySelectorAll('.fs-section')){
    const label = sec.querySelector('.fs-label');
    if(label && label.textContent.trim()===sectionLabel){
      const sel = sec.querySelector('.fs-opt.sel');
      return sel ? sel.textContent.trim() : '';
    }
  }
  return '';
}

function toggleOptMulti(el){
  // Multi-select — toggle this item without clearing others
  el.classList.toggle('sel');
}

function getSelOptsInSection(sectionLabel, sheetId){
  const sheet = document.getElementById(sheetId);
  if(!sheet) return [];
  for(const sec of sheet.querySelectorAll('.fs-section')){
    const label = sec.querySelector('.fs-label');
    if(label && label.textContent.trim().startsWith(sectionLabel)){
      return Array.from(sec.querySelectorAll('.fs-opt.sel')).map(o=>o.textContent.trim());
    }
  }
  return [];
}

function applyFilters(cat){
  if(cat==='property'){
    filterState.property.minPrice = document.getElementById('fp-min')?.value || '';
    filterState.property.maxPrice = document.getElementById('fp-max')?.value || '';
    const _ltSel = getSelOptInSection('Listing Type','fs-property');
    filterState.property.listingType = _ltSel==='For Rent' ? 'rent' : (_ltSel==='For Sale' ? 'sale' : '');
    filterState.property.type        = getSelOptInSection('Property Type','fs-property');
    filterState.property.beds        = getSelOptInSection('Bedrooms','fs-property');
    filterState.property.baths       = getSelOptInSection('Bathrooms','fs-property');
    filterState.property.garages     = getSelOptInSection('Garages','fs-property');
    filterState.property.area        = getSelOptInSection('Area / Suburb','fs-property');
    filterState.property.furnished   = getSelOptInSection('Furnished','fs-property');
    filterState.property.pets        = getSelOptInSection('Pet Friendly','fs-property');
    filterState.property.features    = getSelOptsInSection('Features','fs-property');
  } else if(cat==='tutors'){
    filterState.tutors.maxRate  = document.getElementById('ft-max')?.value || '';
    filterState.tutors.subject  = getSelOptInSection('Subject / Activity','fs-tutors');
    filterState.tutors.level    = getSelOptInSection('Level','fs-tutors');
    filterState.tutors.mode     = getSelOptInSection('Mode','fs-tutors');
    filterState.tutors.area     = getSelOptInSection('Area','fs-tutors');
  } else if(cat==='services'){
    filterState.services.maxRate       = document.getElementById('fv-max')?.value || '';
    filterState.services.serviceClass  = getSelOptInSection('Class','fs-services');
    filterState.services.serviceType   = getSelOptInSection('Service Type','fs-services');
    filterState.services.availability  = getSelOptInSection('Availability','fs-services');
    filterState.services.area          = getSelOptInSection('Area','fs-services');
  } else if(cat==='adventures'){
    filterState.adventures.adventureType = getSelOptInSection('Adventure Type','fs-adventures');
    filterState.adventures.environment   = getSelOptInSection('Environment','fs-adventures');
    filterState.adventures.maxPrice      = document.getElementById('fa-max')?.value || '';
    filterState.adventures.duration      = getSelOptInSection('Duration','fs-adventures');
    filterState.adventures.groupSize     = getSelOptInSection('Group Size','fs-adventures');
    filterState.adventures.area          = getSelOptInSection('Area','fs-adventures');
  } else if(cat==='collectors'){
    filterState.collectors.collectibleType = getSelOptInSection('Collectible Type','fs-collectors');
    filterState.collectors.maxPrice        = document.getElementById('fc-max')?.value || '';
    filterState.collectors.condition       = getSelOptInSection('Condition','fs-collectors');
    filterState.collectors.era             = getSelOptInSection('Era','fs-collectors');
    filterState.collectors.area            = getSelOptInSection('Area','fs-collectors');
  } else if(cat==='cars'){
    filterState.cars.make         = getSelOptInSection('Make','fs-cars');
    filterState.cars.maxPrice     = document.getElementById('fcar-max')?.value || '';
    filterState.cars.yearFrom     = getSelOptInSection('Year From','fs-cars');
    filterState.cars.transmission = getSelOptInSection('Transmission','fs-cars');
    filterState.cars.mileage      = getSelOptInSection('Max Mileage (km)','fs-cars');
  }
  document.getElementById('fs-'+cat).classList.remove('open');
  if(cat==='adventures'){ refreshAdvFilterBadge(); renderAdvGrid(); return; }
  renderActiveFilterTags();
  renderGrid();
}

function clearFilters(cat){
  if(cat==='property'){
    filterState.property = { minPrice:'', maxPrice:'', type:'', beds:'', baths:'', garages:'', area:'', listingType:'', furnished:'', pets:'', features:[] };
    ['fp-min','fp-max'].forEach(id=>{ const el=document.getElementById(id); if(el)el.value=''; });
    document.querySelectorAll('#fs-property .fs-opt').forEach(o=>o.classList.remove('sel'));
  } else if(cat==='tutors'){
    filterState.tutors = { maxRate:'', subject:'', level:'', mode:'', area:'' };
    const el=document.getElementById('ft-max'); if(el)el.value='';
    document.querySelectorAll('#fs-tutors .fs-opt').forEach(o=>o.classList.remove('sel'));
  } else if(cat==='services'){
    filterState.services = { maxRate:'', serviceClass:'', serviceType:'', availability:'', area:'' };
    const el=document.getElementById('fv-max'); if(el)el.value='';
    document.querySelectorAll('#fs-services .fs-opt').forEach(o=>o.classList.remove('sel'));
  } else if(cat==='adventures'){
    filterState.adventures = { adventureType:'', environment:'', maxPrice:'', duration:'', groupSize:'', area:'' };
    const el=document.getElementById('fa-max'); if(el)el.value='';
    document.querySelectorAll('#fs-adventures .fs-opt').forEach(o=>o.classList.remove('sel'));
  } else if(cat==='collectors'){
    filterState.collectors = { collectibleType:'', maxPrice:'', condition:'', era:'', area:'' };
    const el=document.getElementById('fc-max'); if(el)el.value='';
    document.querySelectorAll('#fs-collectors .fs-opt').forEach(o=>o.classList.remove('sel'));
  } else if(cat==='cars'){
    filterState.cars = { make:'', maxPrice:'', yearFrom:'', transmission:'', mileage:'', area:'' };
    const el=document.getElementById('fcar-max'); if(el)el.value='';
    document.querySelectorAll('#fs-cars .fs-opt').forEach(o=>o.classList.remove('sel'));
  }
  document.getElementById('fs-'+cat).classList.remove('open');
  if(cat==='adventures'){ refreshAdvFilterBadge(); renderAdvGrid(); return; }
  renderActiveFilterTags();
  renderGrid();
}

// ── ADVENTURES SCREEN ─────────────────────────────────────────
// HTML-escape helper used in renderAdvGrid card template
const esc = s => String(s||'').replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/'/g,'&#39;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

let advCountry = 'ZA';
let advCountryName = 'South Africa';
let advCountryFlag = '🇿🇦';
let advSubcat = 'all';
let advCat = 'all';

const ADV_ENV_LABELS = {
  bush_wildlife:'🌿 Bush & Wildlife', mountain_highlands:'⛰ Mountain & Highlands',
  coastal_beach:'🏖 Coastal & Beach', garden_winelands:'🍇 Garden & Winelands',
  wetlands_lakes:'🦆 Wetlands & Lakes', desert_karoo:'🏜 Desert & Karoo',
  forest_fynbos:'🌲 Forest & Fynbos', urban_township:'🏙 Urban & Township',
  farm_rural:'🌾 Farm & Rural',
};
const ADV_EXP_TYPE_LABELS = {
  luxury_safari:'🦁 Luxury Safari', luxury_train:'🚂 Luxury Train',
  guided_tours:'🗺 Guided Tours', once_in_a_lifetime:'✨ Once in a Lifetime',
  water_coastal:'🌊 Water & Coastal', sky_aerial:'🪂 Sky & Aerial',
  arts_culture:'🎭 Arts & Culture',
};
const ADV_ACC_TYPE_LABELS = {
  private_lodge:'🏕 Private Lodge', bush_camp:'⛺ Bush Camp',
  mountain_retreat:'⛰ Mountain Retreat', coastal_island:'🏝 Coastal & Island',
  boutique_hotel:'🏨 Boutique Hotel', self_catering:'🍳 Self-Catering',
  unique_stays:'🌳 Unique Stays', caravan_camping:'🚐 Caravan & Camping',
};
const ADV_COUNTRY_FLAGS = { ZA:'🇿🇦', NA:'🇳🇦', MZ:'🇲🇿', US:'🇺🇸', CA:'🇨🇦', GB:'🇬🇧', EU:'🇪🇺', AU:'🇦🇺', NZ:'🇳🇿', ALL:'🌍' };
const ADV_COUNTRY_CURRENCY = { ZA:'R', NA:'N$', MZ:'MT', US:'$', CA:'CA$', GB:'£', EU:'€', AU:'A$', NZ:'NZ$' };

// Experience categories (adventures_experiences)
const ADV_EXP_CATS = [
  {key:'luxury_safari',   icon:'🦁', name:'Luxury safari',       desc:'Big 5, fly-in camps, private concessions'},
  {key:'luxury_train',    icon:'🚂', name:'Luxury train',        desc:'Rovos Rail, Blue Train, Shongololo'},
  {key:'guided_tours',    icon:'🗺', name:'Guided tours',        desc:'Cultural, heritage, food & wine, walking'},
  {key:'once_in_lifetime',icon:'✨', name:'Once in a lifetime',  desc:'Dark sky, gorilla trek, private island'},
  {key:'water_coastal',   icon:'🌊', name:'Water & coastal',     desc:'Sailing, dive, mokoro, island hops'},
  {key:'sky_aerial',      icon:'🪂', name:'Sky & aerial',        desc:'Balloon, helicopter, paraglide, skydive'},
  {key:'arts_culture',    icon:'🎭', name:'Arts & culture',      desc:'Township, cooking class, rock art, craft'},
];

// Accommodation categories (adventures_accommodation)
const ADV_ACCOM_CATS = [
  {key:'private_lodge',   icon:'🏡', name:'Private lodge',       desc:'Exclusive use, game reserve, luxury'},
  {key:'bush_camp',       icon:'⛺', name:'Bush camp',           desc:'Tented camps, fly camps, wild stays'},
  {key:'mountain_retreat',icon:'🏔', name:'Mountain retreat',    desc:'Chalets, huts, highland hideaways'},
  {key:'coastal_island',  icon:'🏖', name:'Coastal & island',    desc:'Beach houses, island villas, surf stays'},
  {key:'boutique_hotel',  icon:'🛎', name:'Boutique hotel',      desc:'Guest house, B&B, design hotel'},
  {key:'self_catering',   icon:'🍳', name:'Self-catering',       desc:'Farm cottages, karoo retreats, villas'},
  {key:'unique_stays',    icon:'🌿', name:'Unique stays',        desc:'Treehouses, caves, star beds, domes'},
  {key:'caravan_camping', icon:'🚐', name:'Caravan & camping',   desc:'Sites, glamping, rooftop tents'},
];

// Pin-3 chips per subcat (shown in header without opening sheet)
const ADV_PINS = {
  adventures_experiences:   ['luxury_safari','luxury_train','guided_tours'],
  adventures_accommodation: ['private_lodge','bush_camp','mountain_retreat'],
  all:                      ['luxury_safari','luxury_train','private_lodge'],
};

// Label lookup for cards
function advCatLabel(l){
  const isAccom = (l.cat||'').toLowerCase().includes('accommodation');
  const cats = isAccom ? ADV_ACCOM_CATS : ADV_EXP_CATS;
  const match = cats.find(c=>c.key===(l.experience_type||l.accommodation_type||''));
  return match ? match.icon+' '+match.name : (isAccom ? '🏕 Accommodation' : '🌄 Experiences');
}

const ADV_SUBCAT_LABELS = {
  adventures_accommodation:'🏕 Stays',
  adventures_experiences:'🌄 Experiences',
};

function setAdvSubcat(sc, btn){
  advSubcat = sc;
  advCat = 'all';
  document.querySelectorAll('.adv-subcat-btn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  // Only show category chip row when a specific subcat is selected
  const catRow = document.getElementById('adv-cat-row');
  if(catRow) catRow.style.display = (sc==='all') ? 'none' : 'flex';
  refreshAdvCatChips();
  renderAdvGrid();
}

// Determine active category list based on current subcat
function advActiveCats(){
  if(advSubcat==='adventures_experiences') return ADV_EXP_CATS;
  if(advSubcat==='adventures_accommodation') return ADV_ACCOM_CATS;
  return [...ADV_EXP_CATS, ...ADV_ACCOM_CATS];
}

// Update the 3 pinned chips labels to match current subcat
// Short display labels for the 3 pinned chips
const ADV_PIN_LABELS = {
  luxury_safari:'🦁 Safari', luxury_train:'🚂 Train', guided_tours:'🗺 Tours',
  once_in_lifetime:'✨ Unique', water_coastal:'🌊 Water', sky_aerial:'🪂 Sky',
  arts_culture:'🎭 Culture', private_lodge:'🏡 Lodge', bush_camp:'⛺ Bush',
  mountain_retreat:'🏔 Mountain', coastal_island:'🏖 Coastal', boutique_hotel:'🛎 Boutique',
  self_catering:'🍳 Self-cat', unique_stays:'🌿 Unique', caravan_camping:'🚐 Caravan',
};

// Which 3 keys to pin per subcat
const ADV_PIN_KEYS = {
  adventures_experiences:   ['luxury_safari','luxury_train','guided_tours'],
  adventures_accommodation: ['private_lodge','bush_camp','mountain_retreat'],
  all:                      ['luxury_safari','guided_tours','private_lodge'],
};

function refreshAdvCatChips(){
  const isAccom = advSubcat==='adventures_accommodation';
  const activeClass = isAccom ? 'active-accom' : 'active-exp';
  const pinKeys = ADV_PIN_KEYS[advSubcat] || ADV_PIN_KEYS['all'];

  // Update pin chip labels and handlers
  ['pin1','pin2','pin3'].forEach((pid,i)=>{
    const chip = document.getElementById('adv-cat-'+pid);
    if(!chip) return;
    const key = pinKeys[i];
    chip.textContent = ADV_PIN_LABELS[key] || key;
    chip.dataset.catKey = key;
    chip.onclick = ()=>setAdvCat(key, chip);
  });

  // Reapply active highlight
  document.querySelectorAll('.adv-cat-chip').forEach(ch=>{
    ch.classList.remove('active-exp','active-accom');
  });
  const allChip = document.getElementById('adv-cat-all');
  if(allChip && advCat==='all') allChip.classList.add(activeClass);
  ['pin1','pin2','pin3'].forEach(pid=>{
    const chip = document.getElementById('adv-cat-'+pid);
    if(chip && chip.dataset.catKey===advCat) chip.classList.add(activeClass);
  });
  // If active cat is from sheet (not a pin), highlight More button slightly
  const moreBtn = document.getElementById('adv-cat-more-btn');
  if(moreBtn){
    const pinned = pinKeys.includes(advCat) || advCat==='all';
    moreBtn.style.borderColor = pinned ? 'rgba(255,255,255,.2)' : '#e8c97b';
    moreBtn.style.color       = pinned ? 'rgba(255,255,255,.75)' : '#e8c97b';
  }
}

function setAdvCat(key, chip){
  advCat = key;
  const isAccom = advSubcat==='adventures_accommodation';
  const activeClass = isAccom ? 'active-accom' : 'active-exp';
  document.querySelectorAll('.adv-cat-chip').forEach(ch=>ch.classList.remove('active-exp','active-accom'));
  if(chip) chip.classList.add(activeClass);
  // close sheet
  const sheet = document.getElementById('adv-cat-sheet');
  if(sheet) sheet.classList.remove('open');
  refreshAdvCatChips();
  renderAdvGrid();
}

function openAdvCatSheet(){
  const isAccom = advSubcat==='adventures_accommodation';
  const cats = isAccom ? ADV_ACCOM_CATS : ADV_EXP_CATS;
  const title = isAccom ? 'Accommodation type' : 'Experience type';
  const iconBgMap = {
    luxury_safari:'#fef3c7', luxury_train:'#ede9fe', guided_tours:'#dbeafe',
    once_in_lifetime:'#fce7f3', water_coastal:'#e0f2fe', sky_aerial:'#fef9c3',
    arts_culture:'#f3e8ff', private_lodge:'#d1fae5', bush_camp:'#fef3c7',
    mountain_retreat:'#e0e7ff', coastal_island:'#e0f2fe', boutique_hotel:'#fce7f3',
    self_catering:'#f0fdf4', unique_stays:'#fef9c3', caravan_camping:'#fff7ed',
  };

  // Rebuild options div only — keep sheet-inner wrapper intact for click-outside
  const optionsDiv = document.getElementById('adv-cat-options');
  if(!optionsDiv) return;
  document.getElementById('adv-cat-sheet-title').textContent = title;

  optionsDiv.innerHTML = cats.map(cat=>{
    const isActive = advCat===cat.key;
    const bg = iconBgMap[cat.key]||'#f3f4f6';
    return `<div class="adv-cat-option${isActive?' active':''}" onclick="setAdvCat('${cat.key}',null)">
      <div class="adv-cat-icon" style="background:${bg};">${cat.icon}</div>
      <div><div class="adv-cat-opt-name">${cat.name}</div><div class="adv-cat-opt-desc">${cat.desc}</div></div>
      <span class="adv-cat-check">✓</span>
    </div>`;
  }).join('');

  document.getElementById('adv-cat-sheet').classList.add('open');
}

function closeAdvCatSheet(e){
  if(e.target===document.getElementById('adv-cat-sheet'))
    document.getElementById('adv-cat-sheet').classList.remove('open');
}

function openAdvCountrySheet(){
  // Mark current country active
  ['ZA','NA','MZ','US','CA','GB','EU','AU','NZ','ALL'].forEach(c=>{
    const el=document.getElementById('adv-co-'+c);
    if(el) el.classList.toggle('active', c===advCountry);
  });
  document.getElementById('adv-country-sheet').classList.add('open');
}

function closeAdvCountrySheet(e){
  if(e.target===document.getElementById('adv-country-sheet'))
    document.getElementById('adv-country-sheet').classList.remove('open');
}

function selectAdvCountry(code, name, flag){
  advCountry=code; advCountryName=name; advCountryFlag=flag;
  document.getElementById('adv-country-name').textContent=name;
  document.getElementById('adv-country-flag').textContent=flag;
  document.getElementById('adv-country-sheet').classList.remove('open');
  renderAdvGrid();
}

function refreshAdvFilterBadge(){
  const badge=document.getElementById('adv-filter-badge');
  const pill=document.getElementById('adv-filter-pill');
  if(!badge) return;
  const fa=filterState.adventures||{};
  let n=0;
  ['adventureType','environment','maxPrice','duration','groupSize','area'].forEach(k=>{ if(fa[k] && fa[k]!=='') n++; });
  if(typeof trustMin!=='undefined' && trustMin) n++;
  if(n>0){ badge.textContent=n; badge.style.display='';
    if(pill){ pill.style.background='rgba(232,201,123,.22)'; pill.style.borderColor='rgba(232,201,123,.6)'; } }
  else { badge.style.display='none';
    if(pill){ pill.style.background='rgba(255,255,255,.14)'; pill.style.borderColor='rgba(255,255,255,.28)'; } }
}

function renderAdvGrid(){
  const grid = document.getElementById('adv-grid');
  const countEl = document.getElementById('adv-results-count');
  if(!grid) return;
  refreshAdvFilterBadge();

  // Filter listings
  let items = LISTINGS.filter(l => {
    const cat = (l.cat||'').toLowerCase();
    if(!cat.startsWith('adventures')) return false;

    // Subcategory filter
    if(advSubcat !== 'all' && cat !== advSubcat) return false;

    // Country filter
    if(advCountry !== 'ALL'){
      const lc = (l.country||l.city_country||'ZA').toUpperCase();
      if(lc !== advCountry) return false;
    }

    // Category filter (experience_type or accommodation_type)
    if(advCat !== 'all'){
      const isAccom = cat.includes('accommodation');
      const typeVal = (isAccom ? (l.accommodation_type||'') : (l.experience_type||l.activity_type||'')).toLowerCase().replace(/\s*&\s*/g,'_and_').replace(/[\s,]+/g,'_').replace(/_+/g,'_').replace(/^_|_$/g,'');
      if(!typeVal || typeVal !== advCat) return false;
    }

    // Filtered Search (fs-adventures) — applies to both Stays & Experiences
    const fa = filterState.adventures;
    if(fa){
      if(fa.adventureType==='Experiences'   && !cat.includes('experien')) return false;
      if(fa.adventureType==='Accommodation' && !cat.includes('accommodation')) return false;
      if(fa.environment && fa.environment!=='' && (l.environment_type||'')!==fa.environment) return false;
      if(fa.maxPrice && Number(l.priceNum||l.price||0) > parseInt(fa.maxPrice)) return false;
      if(fa.area && fa.area!=='' && (l.suburb||'')!==fa.area) return false;
      if(fa.duration && fa.duration!=='' && l.duration && l.duration!==fa.duration) return false;
      if(fa.groupSize && fa.groupSize!=='' && (l.groupSize||l.group_size) && (l.groupSize||l.group_size)!==fa.groupSize) return false;
    }
    if(typeof trustMin!=='undefined' && trustMin && Number(l.trust||0) < trustMin) return false;
    return true;
  });

  countEl.textContent = items.length
    ? `${items.length} listing${items.length===1?'':'s'} · ${advCountryName}`
    : '';

  if(!items.length){
    grid.innerHTML = `<div class="adv-empty">
      <div class="adv-empty-icon">🧭</div>
      <div style="font-size:15px;font-weight:700;color:var(--text);margin-bottom:6px;">No Adventures yet</div>
      <div style="font-size:13px;line-height:1.6;">Operators are being onboarded — check back soon, or try a different country or environment filter.</div>
    </div>`;
    return;
  }

  grid.innerHTML = items.map(l => {
    const isAccom = (l.cat||'').toLowerCase().includes('accommodation');
    const catLabel = advCatLabel(l);
    const badgeBg  = isAccom ? '#dbeafe' : '#d1fae5';
    const badgeCol = isAccom ? '#1e3a5f' : '#065f46';
    const envLabel = l.environment_type || '';
    const cur = ADV_COUNTRY_CURRENCY[(l.country||'ZA').toUpperCase()] || 'R';
    const priceLabel = isAccom
      ? (l.price ? `From ${cur}${Number(l.price).toLocaleString()}/night` : '')
      : (l.price ? `${cur}${Number(l.price).toLocaleString()}/person` : '');
    const countryCode = (l.country||'ZA').toUpperCase();
    const flag = ADV_COUNTRY_FLAGS[countryCode] || '🌍';
    const imgHtml = (l.photo||(l.photos&&l.photos[0]))
      ? `<img class="adv-card-img" src="${esc(l.photo||(l.photos&&l.photos[0]))}" alt="${esc(l.title||'')}" loading="lazy" onerror="r2Fallback(this);if(this.dataset.r2tried&&this.src.includes('/media/')){this.style.display='none'}">`
      : `<div class="adv-card-img-placeholder">${isAccom?'🏕':'🌄'}</div>`;

    return `<div style="background:#fff;border:1.5px solid #e2e5ea;border-radius:16px;overflow:hidden;cursor:pointer;" onclick="openDetail('${esc(l.id)}')">
      <div style="position:relative;">${imgHtml}${(String(l.id).startsWith('demo_'))?'<div class="demo-card-badge"></div>':''}</div>
      <div style="padding:12px 14px 14px;">
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;">
          <span style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:${badgeCol};background:${badgeBg};padding:2px 8px;border-radius:10px;">${catLabel}</span>
          ${envLabel ? `<span style="font-size:10px;color:#6b7280;">${envLabel}</span>` : ''}
          <span style="font-size:11px;color:#6b7280;margin-left:auto;">${flag} ${countryCode}</span>
        </div>
        <div style="font-size:15px;font-weight:700;color:#111827;margin-bottom:4px;line-height:1.3;">${esc(l.title||l.name||'Untitled')}</div>
        <div style="display:flex;align-items:center;justify-content:space-between;margin-top:8px;">
          <div>
            <span style="font-size:14px;font-weight:700;color:#111827;">${priceLabel}</span>
            ${l.trust ? `<div style="margin-top:4px;">${tbadge(l.trust)}</div>` : ''}
          </div>
          <button style="background:#111827;color:#fff;border:none;border-radius:20px;padding:7px 16px;font-size:12px;font-weight:700;cursor:pointer;" onclick="event.stopPropagation();openDetail('${esc(l.id)}')">View →</button>
        </div>
      </div>
    </div>`;
  }).join('');
}

function renderActiveFilterTags(){
  const row = document.getElementById('active-filters-row');
  if(!row) return;
  const cat = activeFilter.toLowerCase();
  const fs = filterState[cat] || {};
  const tags = [];

  if(trustMin) tags.push('\u2605 Trust \u2265 '+trustMin);

  if(cat==='property'){
    if(fs.minPrice||fs.maxPrice) tags.push(`💰 ${formatZAR(fs.minPrice)||'R0.00'} – ${fs.maxPrice?formatZAR(fs.maxPrice):'any'}`);
    if(fs.listingType) tags.push(fs.listingType==='rent' ? '🔑 For Rent' : '🏦 For Sale');
    if(fs.type)        tags.push(`🏠 ${fs.type}`);
    if(fs.beds)        tags.push(`🛏 ${fs.beds} beds`);
    if(fs.baths)       tags.push(`🚿 ${fs.baths} baths`);
    if(fs.garages)     tags.push(`🚗 ${fs.garages} garages`);
    if(fs.area)        tags.push(`📍 ${fs.area}`);
    if(fs.furnished)   tags.push(`🛋 ${fs.furnished}`);
    if(fs.pets)        tags.push(`🐾 Pets: ${fs.pets}`);
    if(fs.features&&fs.features.length) fs.features.forEach(f=>tags.push(`✓ ${f}`));
  } else if(cat==='tutors'){
    if(fs.maxRate)  tags.push(`💰 Max R${fs.maxRate}/hr`);
    if(fs.subject)  tags.push(`📚 ${fs.subject}`);
    if(fs.level)    tags.push(`🎓 ${fs.level}`);
    if(fs.mode)     tags.push(`💻 ${fs.mode}`);
    if(fs.area)     tags.push(`📍 ${fs.area}`);
  } else if(cat==='services'){
    if(fs.serviceClass) tags.push(fs.serviceClass==='Technical'?'🔧 Technical':'🤝 Casuals');
    if(fs.maxRate)      tags.push(`💰 Max R${fs.maxRate}`);
    if(fs.serviceType)  tags.push(`⚙️ ${fs.serviceType}`);
    if(fs.availability) tags.push(`📅 ${fs.availability}`);
    if(fs.area)         tags.push(`📍 ${fs.area}`);
  } else if(cat==='adventures'){
    if(fs.adventureType) tags.push(`🌿 ${fs.adventureType}`);
    if(fs.maxPrice)      tags.push(`💰 Max ${formatZAR(fs.maxPrice)}`);
    if(fs.duration)      tags.push(`⏱ ${fs.duration}`);
    if(fs.groupSize)     tags.push(`👥 ${fs.groupSize}`);
    if(fs.area)          tags.push(`📍 ${fs.area}`);
  } else if(cat==='collectors'){
    if(fs.collectibleType) tags.push(`🏺 ${fs.collectibleType}`);
    if(fs.maxPrice)        tags.push(`💰 Max ${formatZAR(fs.maxPrice)}`);
    if(fs.condition)       tags.push(`✨ ${fs.condition}`);
    if(fs.era)             tags.push(`📅 ${fs.era}`);
    if(fs.area)            tags.push(`📍 ${fs.area}`);
  } else if(cat==='cars'){
    if(fs.make)         tags.push(`🚗 ${fs.make}`);
    if(fs.maxPrice)     tags.push(`💰 Max ${formatZAR(fs.maxPrice)}`);
    if(fs.yearFrom)     tags.push(`📅 ${fs.yearFrom}`);
    if(fs.transmission) tags.push(`⚙️ ${fs.transmission}`);
    if(fs.mileage)      tags.push(`🛣 ${fs.mileage}`);
  }

  row.innerHTML = tags.map(t=>`
    <div class="af-tag" onclick="clearFilters('${cat}')">
      ${t}
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
    </div>`).join('');
}

// ── LOCATION SELECTOR (4-level: Country → Region → City → Suburb) ──────────

async function _geoFetch(path) {
  try { return await apiGet(path); } catch(e) { return []; }
}

function handleCityBadgeClick() {
  // TODO: REMOVE BEFORE LAUNCH — demo mode opens country panel
  if (DEMO_MODE) {
    openLocPanel('country');
    document.getElementById('city-selector-bg').classList.add('open');
    return;
  }
  // END TODO
  const startPanel = buyerTier === 'premium' ? 'country' : 'region';
  openLocPanel(startPanel);
  document.getElementById('city-selector-bg').classList.add('open');
}

async function openLocPanel(panel) {
  ['country','region','city','suburb'].forEach(p => {
    const el = document.getElementById('loc-panel-' + p);
    if (el) el.style.display = p === panel ? '' : 'none';
  });
  if (panel === 'country') await _loadAndRenderCountries();
  if (panel === 'region')  await _loadAndRenderRegions();
  if (panel === 'city')    await _loadAndRenderCities();
  if (panel === 'suburb')  await _loadAndRenderSuburbs();
}

async function _loadAndRenderCountries() {
  const list = document.getElementById('loc-list-country');
  if (!list) return;
  // TODO: REMOVE BEFORE LAUNCH — inject 4 demo countries
  if (DEMO_MODE) {
    const demoCountries = [
      { iso2:'ZA', name:'South Africa' },
      { iso2:'US', name:'United States' },
      { iso2:'GB', name:'United Kingdom' },
      { iso2:'AU', name:'Australia' },
    ];
    list.innerHTML = demoCountries.map(co =>
      `<div class="city-option${activeCountry.iso2 === co.iso2 ? ' selected' : ''}" onclick="selectDemoCountry('${co.iso2}','${co.name}')">${co.name}${activeCountry.iso2 === co.iso2 ? '<span style="color:var(--accent);">✓</span>' : ''}</div>`
    ).join('');
    return;
  }
  // END TODO
  const data = await _geoFetch('/geo/countries');
  list.innerHTML = (Array.isArray(data) ? data : []).map(c =>
    `<div class="city-option${c.iso2 === activeCountry.iso2 ? ' selected' : ''}" onclick="selectCountry('${c.iso2}','${c.name.replace(/'/g,"\\'")}')">${c.name}${c.iso2 === activeCountry.iso2 ? '<span style="color:var(--accent);">✓</span>' : ''}</div>`
  ).join('') || '<div class="city-option" style="opacity:.5">No countries available</div>';
}

async function _loadAndRenderRegions() {
  const title = document.getElementById('loc-title-region');
  const list  = document.getElementById('loc-list-region');
  if (!list) return;
  if (title) title.textContent = activeCountry.name + ' · Region';
  const data = await _geoFetch('/geo/regions?country=' + activeCountry.iso2);
  list.innerHTML = (Array.isArray(data) ? data : []).map(r =>
    `<div class="city-option${activeRegion && r.id === activeRegion.id ? ' selected' : ''}" onclick="selectRegion(${r.id},'${r.name.replace(/'/g,"\\'")}')">${r.name}${activeRegion && r.id === activeRegion.id ? '<span style="color:var(--accent);">✓</span>' : ''}</div>`
  ).join('') || '<div class="city-option" style="opacity:.5">No regions available</div>';
}

async function _loadAndRenderCities() {
  const title = document.getElementById('loc-title-city');
  const list  = document.getElementById('loc-list-city');
  if (!list) return;
  if (title) title.textContent = (activeRegion ? activeRegion.name : activeCountry.name) + ' · City';

  // TODO: REMOVE BEFORE LAUNCH — inject demo cities filtered by active country
  if (DEMO_MODE) {
    const cities = (DEMO_COUNTRY_CITIES[activeCountry.iso2] || [{ name:'Pretoria' }]);
    if (title) title.textContent = activeCountry.name + ' · City';
    list.innerHTML = cities.map(dc =>
      `<div class="city-option${activeCity.name === dc.name ? ' selected' : ''}" onclick="selectDemoCity('${dc.name}')">${dc.name}${activeCity.name === dc.name ? '<span style="color:var(--accent);">✓</span>' : ''}</div>`
    ).join('');
    return;
  }
  // END TODO

  const path = activeRegion
    ? '/geo/cities?region_id=' + activeRegion.id
    : '/geo/cities?country=' + activeCountry.iso2;
  const data = await _geoFetch(path);
  list.innerHTML = (Array.isArray(data) ? data : []).map(c =>
    `<div class="city-option${activeCity.id === c.id ? ' selected' : ''}" onclick="selectCity(${c.id},'${c.name.replace(/'/g,"\\'")}',${c.lat},${c.lng})">${c.name}${activeCity.id === c.id ? '<span style="color:var(--accent);">✓</span>' : ''}</div>`
  ).join('') || '<div class="city-option" style="opacity:.5">No cities available</div>';
}

async function _loadAndRenderSuburbs() {
  const title = document.getElementById('suburb-panel-title');
  const list  = document.getElementById('loc-list-suburb');
  const back  = document.getElementById('suburb-back-btn');
  if (!list) return;
  if (title) title.textContent = activeCity.name + ' · Suburb';
  if (back) back.style.display = buyerTier === 'free' ? 'none' : '';
  const data = activeCity.id ? await _geoFetch('/geo/suburbs?city_id=' + activeCity.id) : [];
  const opts = [{ id: null, name: 'All suburbs' }, ...(Array.isArray(data) ? data : [])];
  let html = '';
  // "Near me" option — only shown when buyer GPS is available
  if (buyerLat != null) {
    html += `<div class="city-option${nearbyMode ? ' selected' : ''}" onclick="selectNearMe()">📍 Near me${nearbyMode ? '<span style="color:var(--accent);">✓</span>' : ''}</div>`;
  }
  html += opts.map(s => {
    const isSelected = !nearbyMode && (s.id === null ? !activeSuburb : activeSuburb && s.id === activeSuburb.id);
    return `<div class="city-option${isSelected ? ' selected' : ''}" onclick="selectSuburb(${s.id === null ? 'null' : s.id},'${s.name.replace(/'/g,"\\'")}')">${s.name}${isSelected ? '<span style="color:var(--accent);">✓</span>' : ''}</div>`;
  }).join('');
  list.innerHTML = html;
}

function closeCitySelector() {
  const bg = document.getElementById('city-selector-bg');
  if (bg) bg.classList.remove('open');
}

async function selectCountry(iso2, name) {
  activeCountry = { iso2, name };
  activeRegion  = null;
  activeCity    = { id: null, name: '' };
  activeSuburb  = null;
  await openLocPanel('region');
}

async function selectRegion(id, name) {
  activeRegion = { id, name };
  activeCity   = { id: null, name: '' };
  activeSuburb = null;
  await openLocPanel('city');
}

// TODO: REMOVE BEFORE LAUNCH — demo city switcher
// TODO: REMOVE BEFORE LAUNCH — demo country selector
const DEMO_COUNTRY_CITIES = {
  'ZA': [{name:'Pretoria',lat:-25.74486,lng:28.18783},{name:'Cape Town',lat:-33.92584,lng:18.42322},{name:'Johannesburg',lat:-26.20227,lng:28.04363},{name:'Durban',lat:-29.8579,lng:31.0292},{name:'Gqeberha (Port Elizabeth)',lat:-33.96109,lng:25.61494},{name:'Bloemfontein',lat:-29.12107,lng:26.214},{name:'East London',lat:-33.0153,lng:27.9116},{name:'Polokwane',lat:-23.90449,lng:29.46885},{name:'Mbombela (Nelspruit)',lat:-25.47512,lng:30.96935},{name:'Kimberley',lat:-28.73226,lng:24.76232},{name:'Pietermaritzburg',lat:-29.61679,lng:30.39278}],
  'US': [{name:'New York',lat:40.7128,lng:-74.006},{name:'Los Angeles',lat:34.0522,lng:-118.2437},{name:'Chicago',lat:41.8781,lng:-87.6298},{name:'Houston',lat:29.7604,lng:-95.3698},{name:'Phoenix',lat:33.4484,lng:-112.074},{name:'Philadelphia',lat:39.9526,lng:-75.1652},{name:'San Antonio',lat:29.4241,lng:-98.4936},{name:'San Diego',lat:32.7157,lng:-117.1611},{name:'Dallas',lat:32.7767,lng:-96.797},{name:'San Jose',lat:37.3382,lng:-121.8863},{name:'Austin',lat:30.2672,lng:-97.7431}],
  'GB': [{name:'London',lat:51.5074,lng:-0.1278},{name:'Manchester',lat:53.4808,lng:-2.2426},{name:'Birmingham',lat:52.4862,lng:-1.8904},{name:'Leeds',lat:53.8008,lng:-1.5491},{name:'Glasgow',lat:55.8642,lng:-4.2518},{name:'Sheffield',lat:53.3811,lng:-1.4701},{name:'Edinburgh',lat:55.9533,lng:-3.1883},{name:'Liverpool',lat:53.4084,lng:-2.9916},{name:'Bristol',lat:51.4545,lng:-2.5879},{name:'Cardiff',lat:51.4816,lng:-3.1791},{name:'Leicester',lat:52.6369,lng:-1.1398}],
  'AU': [{name:'Sydney',lat:-33.8688,lng:151.2093}],
};
function selectDemoCountry(iso2, name) {
  activeCountry = { iso2, name };
  activeRegion = null;
  // Render city panel for this country
  const title = document.getElementById('loc-title-city');
  const list  = document.getElementById('loc-list-city');
  if (title) title.textContent = name + ' · City';
  if (list) {
    const cities = DEMO_COUNTRY_CITIES[iso2] || [];
    list.innerHTML = cities.map(ct =>
      `<div class="city-option${activeCity.name === ct.name ? ' selected' : ''}" onclick="selectDemoCity('${ct.name}')">${ct.name}${activeCity.name === ct.name ? '<span style="color:var(--accent);">✓</span>' : ''}</div>`
    ).join('');
  }
  openLocPanel('city');
}
// END TODO

function selectDemoCity(name) {
  // Find this demo city's entry (coords + iso2) across all demo countries
  let _iso2 = null, _hit = null;
  for (const _k in DEMO_COUNTRY_CITIES) {
    const _f = DEMO_COUNTRY_CITIES[_k].find(c => c.name === name);
    if (_f) { _iso2 = _k; _hit = _f; break; }
  }
  activeCity = { id: null, name, lat: _hit ? _hit.lat : null, lng: _hit ? _hit.lng : null };
  activeSuburb = null;
  activeRegion = null;
  // Update country + Adventures/World-Heritage filters to match selected city
  const _CN = { 'ZA':'South Africa', 'US':'United States', 'GB':'United Kingdom', 'AU':'Australia' };
  const _CF = { 'ZA':'🇿🇦', 'US':'🇺🇸', 'GB':'🇬🇧', 'AU':'🇦🇺' };
  if (_iso2) {
    activeCountry = { iso2:_iso2, name:_CN[_iso2] || _iso2 };
    advCountry=_iso2; advCountryName=_CN[_iso2]||_iso2; advCountryFlag=_CF[_iso2]||''; _wfCountry=_iso2;
    { const _wfs=document.getElementById('wf-country-select'); if(_wfs && Array.from(_wfs.options).some(o=>o.value===_iso2)) _wfs.value=_iso2; }
    const _af=document.getElementById('adv-country-flag'); if(_af) _af.textContent=_CF[_iso2]||'';
    const _an=document.getElementById('adv-country-name'); if(_an) _an.textContent=_CN[_iso2]||_iso2;
  }
  closeCitySelector();
  updateBadgeLabel();
  // Clear stale BEA live listings from previous city immediately (city-switch flush)
  for (let i = LISTINGS.length - 1; i >= 0; i--) {
    if (LISTINGS[i].isLive) LISTINGS.splice(i, 1);
  }
  renderGrid();
  renderCatCounts();
  if (typeof renderWondersStrip === 'function') renderWondersStrip();
  if (viewMode === 'map') renderMap();
  // Reload live BEA listings for the new city
  loadLiveListings(0);
}
// END TODO

async function selectCity(id, name, lat, lng) {
  activeCity   = { id, name, lat: (lat==null?null:lat), lng: (lng==null?null:lng) };
  activeSuburb = null;
  closeCitySelector();
  updateBadgeLabel();
  renderGrid();
  renderCatCounts();
  if (viewMode === 'map') renderMap();
}

async function selectSuburb(id, name) {
  closeCitySelector();
  nearbyMode = false;
  nearbySuburbs = [];
  activeSuburb = id === null ? null : { id, name };
  updateBadgeLabel();
  await loadLiveListings();
}

async function selectNearMe() {
  if (buyerLat == null) return;
  closeCitySelector();
  try {
    const nearby = await _geoFetch('/geo/nearby?lat=' + buyerLat + '&lng=' + buyerLng + '&radius_km=10&limit=30');
    if (Array.isArray(nearby) && nearby.length) {
      nearbyMode = true;
      nearbySuburbs = nearby.map(s => s.name);
      activeSuburb = null;
      updateBadgeLabel();
      await loadLiveListings();
    }
  } catch(e) { console.warn('selectNearMe failed:', e); }
}

async function _resolveActiveCity() {
  // On startup: resolve city id + region for the default 'Pretoria' name
  if (activeCity.id !== null) return;
  const [cities, regions] = await Promise.all([
    _geoFetch('/geo/cities?country=ZA'),
    _geoFetch('/geo/regions?country=ZA')
  ]);
  if (Array.isArray(cities)) {
    const match = cities.find(c => c.name === activeCity.name);
    if (match) {
      activeCity = { id: match.id, name: match.name };
      // Also resolve the region so the badge shows all 4 levels
      if (Array.isArray(regions) && match.region_name) {
        const region = regions.find(r => r.name === match.region_name);
        if (region) activeRegion = { id: region.id, name: region.name };
      }
    }
  }
}

// ── PROXIMITY: HAVERSINE + GEOLOCATION + MAP ─────────────
function _haversineKm(lat1,lng1,lat2,lng2){
  const R=6371,dLat=(lat2-lat1)*Math.PI/180,dLng=(lng2-lng1)*Math.PI/180;
  const a=Math.sin(dLat/2)**2+Math.cos(lat1*Math.PI/180)*Math.cos(lat2*Math.PI/180)*Math.sin(dLng/2)**2;
  return R*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));
}

function _distLabel(listing){
  if(buyerLat==null||!listing.suburb_lat) return '';
  const d=_haversineKm(buyerLat,buyerLng,listing.suburb_lat,listing.suburb_lng);
  return d<1?`<span class="dist-badge">${Math.round(d*1000)}m</span>`
            :`<span class="dist-badge">${d.toFixed(1)}km</span>`;
}

function _detectLocation(){
  if(!navigator.geolocation) return;
  navigator.geolocation.getCurrentPosition(async pos=>{
    buyerLat=pos.coords.latitude; buyerLng=pos.coords.longitude;
    // Re-render cards with distance badges
    renderGrid();
    renderFeatured();
  },()=>{/* permission denied — continue without location */},{timeout:8000});
}

function setViewMode(mode){
  viewMode=mode;
  document.getElementById('btn-view-grid').classList.toggle('active',mode==='grid');
  document.getElementById('btn-view-map').classList.toggle('active',mode==='map');
  document.getElementById('listing-grid').style.display=mode==='grid'?'':'none';
  document.getElementById('listing-map').style.display=mode==='map'?'':'none';
  if(mode==='map') renderMap();
}

function renderMap(){
  const mapEl=document.getElementById('listing-map');
  if(!mapEl) return;
  // Initialize Leaflet map once
  if(!_leafletMap){
    _leafletMap=L.map(mapEl,{zoomControl:true,attributionControl:true});
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{
      attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom:19
    }).addTo(_leafletMap);
  }
  // Clear old markers
  if(_markerLayer){_leafletMap.removeLayer(_markerLayer);}
  _markerLayer=L.markerClusterGroup();

  // TODO: REMOVE BEFORE LAUNCH — demo city filter
  const listings=LISTINGS.filter(l=>{
    if(String(l.id).startsWith('ph_')) return false;
    if(l.paused) return false;
    if(activeFilter!=='All'&&normCat(l.cat)!==activeFilter) return false;
    if(DEMO_MODE && String(l.id).startsWith('demo_')) {
      const lCity = l.city || l.area || '';
      const aCity = activeCity.name || '';
      if(lCity && aCity && lCity !== aCity) return false;
    }
    if(!(l.listing_lat||l.suburb_lat)) return false;
    return true;
  });

  const CITY_CENTERS = {
    'Pretoria':   [-25.75,  28.19],
    'New York':   [40.7128, -74.006],
    'London':     [51.5074, -0.1278],
    'Sydney':     [-33.8688, 151.2093],
  };
  if(!listings.length){
    let ctr;
    if(activeCity && activeCity.lat!=null && activeCity.lng!=null) ctr=[activeCity.lat, activeCity.lng];
    else ctr = CITY_CENTERS[activeCity.name] || [-25.75, 28.19];
    _leafletMap.setView(ctr, 12);
    return;
  }

  const bounds=[];
  listings.forEach(l=>{
    const lat = l.listing_lat || l.suburb_lat;
    const lng = l.listing_lng || l.suburb_lng;
    if(!lat) return;
    const latlng=[lat, lng];
    bounds.push(latlng);
    const cat=catCfg(l)||{icon:'📍'};
    const dist=buyerLat!=null?` · ${_haversineKm(buyerLat,buyerLng,l.suburb_lat,l.suburb_lng).toFixed(1)}km`:'';
    const marker=L.marker(latlng).bindPopup(
      `<div style="min-width:160px;">
        <strong>${l.title}</strong><br>
        <span style="font-size:12px;color:#666;">${cat.icon} ${l.cat} · ${l.suburb||l.area}${dist}</span><br>
        <span style="font-size:13px;font-weight:600;">${l.price?(formatZAR(l.price)||l.price):'Negotiable'}</span><br>
        <a href="#" onclick="event.preventDefault();openDetail('${l.id}')" style="font-size:12px;color:var(--accent);">View listing →</a>
      </div>`
    );
    _markerLayer.addLayer(marker);
  });

  // Add buyer location marker if available
  if(buyerLat!=null){
    const youMarker=L.circleMarker([buyerLat,buyerLng],{
      radius:8,fillColor:'#4d8af0',fillOpacity:1,color:'#fff',weight:2
    }).bindPopup('<strong>You are here</strong>');
    _markerLayer.addLayer(youMarker);
    bounds.push([buyerLat,buyerLng]);
  }

  _leafletMap.addLayer(_markerLayer);
  if(bounds.length) _leafletMap.fitBounds(bounds,{padding:[30,30],maxZoom:14});
}

// ── HOME SCREEN STATS ──────────────────────────────────────

function renderHomeStats() {
  const _aCity = activeCity ? (activeCity.name || '') : '';
  const live = LISTINGS.filter(l => {
    if (l.id.startsWith('ph_')) return false;
    // Respect the selected city — demo listings + live BEA listings are per-city,
    // so an empty city (e.g. New York in demo) must read 0, not another city's total.
    if (DEMO_MODE && String(l.id).startsWith('demo_')) {
      const lCity = l.city || l.area || '';
      if (lCity && _aCity && lCity !== _aCity) return false;
    }
    if (l.isLive) {
      const lCity = l.city || l.area || '';
      if (lCity && _aCity && lCity !== _aCity) return false;
    }
    return true;
  });
  const n    = live.length;
  // FLAG: Sellers count needs BEA /sellers/count?city= endpoint — using listing count as proxy until then
  const sellersEl  = document.getElementById('home-sellers');
  const listingsEl = document.getElementById('home-listings');
  if (sellersEl)  sellersEl.textContent  = n;
  if (listingsEl) listingsEl.textContent = n;
}

function renderCatCounts() {
  const grid = document.getElementById('home-cat-grid');
  if (!grid) return;
  const counts = {};
  // Count live listings only (non-placeholder); suburb filter applies
  const liveCounts = {};
  LISTINGS.filter(l => {
    if (l.id.startsWith('ph_')) return false;
    if (!DEMO_MODE && String(l.id).startsWith('demo_')) return false;
    if (activeSuburb && l.suburb !== activeSuburb.name) return false;
    // TODO: REMOVE BEFORE LAUNCH — mirror DEMO_DISPLAY_MODE filter
    if (DEMO_MODE) {
      const isDemo = String(l.id).startsWith('demo_');
      if (isDemo && DEMO_DISPLAY_MODE === 'live') return false;
      if (!isDemo && !l.isLive && DEMO_DISPLAY_MODE === 'demo') return false;
    }
    // Filter demo listings to active city only
    if (DEMO_MODE && String(l.id).startsWith('demo_')) {
      const lCity = l.city || l.area || '';
      const aCity = activeCity.name || '';
      if (lCity && aCity && lCity !== aCity) return false;
    }
    // Filter live BEA listings (isLive=true) to active city — prevents Pretoria
    // live listings appearing in counts when NY / London / Sydney is selected
    if (l.isLive) {
      const lCity = l.city || l.area || '';
      const aCity = activeCity.name || '';
      if (lCity && aCity && lCity !== aCity) return false;
    }
    return true;
  }).forEach(l => {
    const cat = normCat(l.cat);
    liveCounts[cat] = (liveCounts[cat] || 0) + 1;
  });
  // Use live counts if any exist; fall back to counting all (including placeholders)
  // so tiles never display "0 listings" when placeholder cards are present.
  const hasLive = Object.keys(liveCounts).length > 0;
  if (hasLive) {
    Object.assign(counts, liveCounts);
  } else {
    // Mirror the active-city filter so a selected city with no listings (e.g. New York
    // in demo) reads 0 instead of falling back to another city's totals.
    const _aCity = activeCity ? (activeCity.name || '') : '';
    LISTINGS.forEach(l => {
      if (DEMO_MODE && String(l.id).startsWith('demo_')) {
        const lCity = l.city || l.area || '';
        if (lCity && _aCity && lCity !== _aCity) return;
      }
      if (l.isLive) {
        const lCity = l.city || l.area || '';
        if (lCity && _aCity && lCity !== _aCity) return;
      }
      const cat = normCat(l.cat);
      counts[cat] = (counts[cat] || 0) + 1;
    });
  }
  grid.querySelectorAll('.cat-tile').forEach(tile => {
    if (tile.id === 'lm-home-tile') {
      if (DEMO_MODE) {
        // In demo mode, count directly from LISTINGS array (BEA LM endpoint has no demo data)
        const _aCity = activeCity ? activeCity.name : '';
        const demoLMCount = LISTINGS.filter(l =>
          !l.id.startsWith('ph_') &&
          normCat(l.cat) === 'LocalMarket' &&
          (!_aCity || !l.city || l.city === _aCity)
        ).length;
        tile.style.display = demoLMCount > 0 ? '' : 'none';
        const countEl = document.getElementById('lm-home-count');
        if (countEl && demoLMCount > 0) countEl.textContent = demoLMCount + (demoLMCount === 1 ? ' listing' : ' listings');
      }
      return;
    }
    const name = tile.querySelector('.cat-name').textContent.trim();
    const n = counts[name] || 0;
    tile.querySelector('.cat-count').textContent = n + (n === 1 ? ' listing' : ' listings');
    // TODO: REMOVE BEFORE LAUNCH — hide empty category tiles in demo mode
    if (DEMO_MODE) tile.style.display = n > 0 ? '' : 'none';
  });
}

function renderGrid(){
  const filtered = LISTINGS.filter(l => {
    if(activeFilter!=='All' && normCat(l.cat)!==activeFilter) return false;
    // Placeholders always show — they are paused but intentionally visible
    const isPlaceholder = String(l.id).startsWith('ph_');
    if(l.paused && !isPlaceholder) return false;
    // Suburb filter — skip placeholders and only filter when a suburb is selected
    if(nearbyMode && !isPlaceholder && !nearbySuburbs.includes(l.suburb)) return false;
    if(!nearbyMode && activeSuburb && !isPlaceholder && l.suburb !== activeSuburb.name) return false;
    // Hide demo listings on live site, filter by city in demo mode
    if(!DEMO_MODE && String(l.id).startsWith('demo_')) return false;
    if(DEMO_MODE && String(l.id).startsWith('demo_')) {
      const demoCityMap = {
        'demo_prop_ny':'New York','demo_tut_ny':'New York','demo_svc_ny':'New York','demo_adv_ny':'New York',
        'demo_prop_lon':'London','demo_tut_lon':'London','demo_svc_lon':'London','demo_adv_lon':'London',
        'demo_prop_syd':'Sydney','demo_tut_syd':'Sydney','demo_svc_syd':'Sydney','demo_adv_syd':'Sydney',
      };
      // Determine which city this demo listing belongs to
      const lCity = l.city || l.area || '';
      const aCity = activeCity.name || '';
      if (lCity && aCity && lCity !== aCity) return false;
      // DEMO_DISPLAY_MODE filter
      if (DEMO_DISPLAY_MODE === 'live') return false;
    }
    if(DEMO_MODE && !String(l.id).startsWith('demo_') && !String(l.id).startsWith('ph_')) {
      if (DEMO_DISPLAY_MODE === 'demo') return false;
    }
    // END TODO

    // Global Trust >= filter (skip placeholders, which carry no trust)
    if(trustMin && !isPlaceholder && (l.trust||0) < trustMin) return false;

    // Category-specific filtering
    if(l.cat==='Property'){
      const fp = filterState.property;
      if(fp.minPrice && l.priceNum < parseInt(fp.minPrice)) return false;
      if(fp.maxPrice && l.priceNum > parseInt(fp.maxPrice)) return false;
      if(fp.listingType && fp.listingType!=='' && l.listingType && l.listingType!==fp.listingType) return false;
      if(fp.type && fp.type!=='' && l.propType && l.propType!==fp.type) return false;
      if(fp.beds){ const minBeds=parseInt(fp.beds); if(!isNaN(minBeds)&&l.beds<minBeds) return false; }
      if(fp.baths){ const minBaths=parseInt(fp.baths); if(!isNaN(minBaths)&&l.baths<minBaths) return false; }
      if(fp.garages){ const minGar=parseInt(fp.garages); if(!isNaN(minGar)&&l.garages<minGar) return false; }
      if(fp.area && fp.area!=='' && l.suburb !== fp.area) return false;
      if(fp.furnished && fp.furnished!=='' && l.furnished && l.furnished!==fp.furnished) return false;
      if(fp.pets && fp.pets!=='' && l.pets && l.pets!==fp.pets) return false;
      if(fp.features && fp.features.length){
        if(!l.features||!l.features.length) return false;
        const lf=l.features.map(f=>f.toLowerCase());
        for(const feat of fp.features){ if(!lf.some(f=>f.includes(feat.toLowerCase()))) return false; }
      }
    }

    if(l.cat==='Tutors'){
      const ft = filterState.tutors;
      if(ft.maxRate && l.priceNum > parseInt(ft.maxRate)) return false;
      if(ft.subject && ft.subject!=='' && l.subject !== ft.subject) return false;
      if(ft.level && ft.level!=='' && l.level !== ft.level) return false;
      if(ft.mode && ft.mode!=='' && ft.mode!=='Either' && l.mode !== ft.mode) return false;
      if(ft.area && ft.area!=='' && l.suburb !== ft.area) return false;
    }

    if(l.cat==='Services'){
      const fv = filterState.services;
      if(fv.maxRate && l.priceNum > parseInt(fv.maxRate)) return false;
      if(fv.serviceClass && fv.serviceClass!=='' && l.service_class !== fv.serviceClass) return false;
      if(fv.serviceType && fv.serviceType!=='' && l.serviceType !== fv.serviceType) return false;
      if(fv.availability && fv.availability!=='' && l.availability !== fv.availability) return false;
      if(fv.area && fv.area!=='' && l.suburb !== fv.area) return false;
    }

    if(l.cat==='Adventures'){
      const fa = filterState.adventures;
      if(fa.adventureType && fa.adventureType!=='' && l.adventureType && l.adventureType!==fa.adventureType) return false;
      if(fa.maxPrice && l.priceNum > parseInt(fa.maxPrice)) return false;
      if(fa.duration && fa.duration!=='' && l.duration && l.duration!==fa.duration) return false;
      if(fa.groupSize && fa.groupSize!=='' && l.groupSize && l.groupSize!==fa.groupSize) return false;
      if(fa.area && fa.area!=='' && l.suburb !== fa.area) return false;
    }

    if(l.cat==='Collectors'){
      const fc = filterState.collectors;
      if(fc.collectibleType && fc.collectibleType!=='' && l.collectibleType!==fc.collectibleType) return false;
      if(fc.maxPrice && l.priceNum > parseInt(fc.maxPrice)) return false;
      if(fc.condition && fc.condition!=='' && l.condition!==fc.condition) return false;
      if(fc.era && fc.era!=='' && l.era!==fc.era) return false;
      if(fc.area && fc.area!=='' && l.suburb !== fc.area) return false;
    }

    if(l.cat==='Cars'){
      const fcar = filterState.cars;
      if(fcar.make && fcar.make!=='' && l.make && l.make!==fcar.make) return false;
      if(fcar.maxPrice && l.priceNum > parseInt(fcar.maxPrice)) return false;
      if(fcar.yearFrom && fcar.yearFrom!==''){
        const yrMatch = fcar.yearFrom.match(/(\d{4})/);
        if(yrMatch && l.year){
          const minYr = parseInt(yrMatch[1]);
          if(fcar.yearFrom.startsWith('Pre-')){ if(l.year>=minYr) return false; }
          else { if(l.year < minYr) return false; }
        }
      }
      if(fcar.transmission && fcar.transmission!=='' && l.transmission && l.transmission!==fcar.transmission) return false;
      if(fcar.area && fcar.area!=='' && l.suburb !== fcar.area) return false;
    }

    return true;
  });

  // Sort by distance when buyer GPS is available
  if(buyerLat!=null){
    filtered.sort((a,b)=>{
      const dA=a.suburb_lat?_haversineKm(buyerLat,buyerLng,a.suburb_lat,a.suburb_lng):9999;
      const dB=b.suburb_lat?_haversineKm(buyerLat,buyerLng,b.suburb_lat,b.suburb_lng):9999;
      return dA-dB;
    });
  }
  // Placeholders always go last — push "Coming soon" cards to the end
  filtered.sort((a,b)=>{
    const aph=String(a.id).startsWith('ph_')?1:0;
    const bph=String(b.id).startsWith('ph_')?1:0;
    return aph-bph;
  });

  const grid = document.getElementById('listing-grid');
  const countEl = document.getElementById('results-count');
  const realCount = filtered.filter(l => !String(l.id).startsWith('ph_')).length;
  if(countEl) countEl.textContent = realCount > 0 ? `${realCount} listing${realCount!==1?'s':''} found` : '';
  if(!filtered.length){
    grid.innerHTML='<div class="no-res">No listings match your filters.<br><span style="font-size:12px;cursor:pointer;color:var(--accent);" onclick="clearFilters(\''+activeFilter.toLowerCase()+'\')">Clear filters</span></div>';
    return;
  }
  grid.innerHTML = filtered.map(cardHtml).join('');
}


function cardHtml(l){
  const isPlaceholder = String(l.id).startsWith('ph_');
  const sv=wishlist.has(l.id);
  const m=catCfg(l).model;

  // Placeholder card — visually distinct, non-clickable
  if(isPlaceholder){
    return`<div class="lcard" style="opacity:.55;pointer-events:none;border:2px dashed var(--border);">
    <div class="ibox" style="background:${catCfg(l).bg};display:flex;align-items:center;justify-content:center;">
      <div style="text-align:center;padding:16px;">
        <div style="font-size:28px;margin-bottom:6px;">${catCfg(l).icon}</div>
        <div style="font-size:10px;font-weight:700;color:rgba(255,255,255,.7);letter-spacing:.5px;text-transform:uppercase;">Coming soon</div>
      </div>
    </div>
    <div class="cbody">
      <div class="ccat">${l.cat}</div>
      <div class="ctitle" style="color:var(--text-3);font-style:italic;">Awaiting first ${l.cat.toLowerCase()} seller</div>
      <div class="cloc" style="color:var(--text-3);">📍 Pretoria</div>
      <div class="cbot"><div class="cprice" style="color:var(--text-3);">—</div></div>
    </div>
  </div>`;
  }

  const _catCfg=catCfg(l)||{};
  const _fallbackPhoto=_catCfg.catPhoto;
  const _fallbackDiv=`<div class="emoji-fallback" style="background:${_catCfg.bg}">${_catCfg.icon}</div>`;
  const imgHtml=l.photo
    ?`<img src="${l.photo}" alt="${l.title}" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='${_fallbackPhoto?'block':'flex'}">${_fallbackPhoto?`<img src="${_fallbackPhoto}" alt="${l.cat}" loading="lazy" style="display:none;width:100%;height:100%;object-fit:cover;" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">${_fallbackDiv}`:_fallbackDiv}`
    :(_fallbackPhoto
        ?`<img src="${_fallbackPhoto}" alt="${l.cat}" loading="lazy" referrerpolicy="no-referrer" style="width:100%;height:100%;object-fit:cover;" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">${_fallbackDiv}`
        :_fallbackDiv);
  const _isCollectors = (l.cat||'').toLowerCase()==='collectors';
  return`<div class="lcard${l.paused?' paused':''}" onclick="${l.paused?'':` openDetail('${l.id}')`}">
    <div class="ibox${_isCollectors?' collectors-thumb':''}" style="background:${catCfg(l).bg}">
      ${imgHtml}
      ${(String(l.id).startsWith('demo_')||String(l.id).startsWith('ph_'))?'<div class="demo-card-badge"></div>':''}
      ${l.feat&&!l.paused?'<div class="feat-badge">Featured</div>':''}
      ${l.paused?'<div class="paused-badge">⏸ Pending</div>':''}
      <div class="model-badge ${m}">${m==='commit'?'⏳ Commit':'👥 Queue'}</div>
      ${l.cat==='Services'&&l.service_class?`<div class="model-badge queue" style="bottom:24px;">${l.service_class==='Technical'?'🔧 Technical':'🤝 Casuals'}</div>`:''}
      ${!l.paused?`<button class="wish-btn ${sv?'saved':''}" onclick="toggleWish(event,'${l.id}')"><svg xmlns="http://www.w3.org/2000/svg" fill="${sv?'currentColor':'none'}" stroke="currentColor" viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg></button>`:''}
    </div>
    <div class="cbody">
      <div class="ccat">${l.cat}</div>
      <div class="ctitle">${l.title}</div>
      <div class="cloc">📍 ${l.area}${_distLabel(l)}</div>
      <div class="cbot">
        <div class="cprice">${l.price?`${formatZAR(l.price)||l.price}<span class="per"> ${l.per}</span>`:'<span class="neg">Negotiable</span>'}</div>
        ${tbadge(l.trust)}
      </div>
      ${l.sellerIdx!=null?`<div class="seller-cv-badge" onclick="event.stopPropagation();openSellerCV(${l.sellerIdx},'${l.id}')"><svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg> View seller profile</div>`:''}
    </div>
  </div>`;
}

function renderFeatured(){
  const _featCity = activeCity.name || '';
  const featured = LISTINGS.filter(l=>{
    if (!l.feat || l.paused) return false;
    // In demo mode, only show featured listings for the active city
    if (DEMO_MODE && String(l.id).startsWith('demo_')) {
      const lCity = l.city || l.area || '';
      if (_featCity && lCity && lCity !== _featCity) return false;
    }
    return true;
  });
  if(!featured.length){
    document.getElementById('home-featured').innerHTML=
      `<div style="padding:18px 16px;color:var(--text-3);font-size:13px;font-style:italic;">Featured listings will appear here once sellers are onboarded.</div>`;
    return;
  }
  document.getElementById('home-featured').innerHTML=featured.map(l=>{
    const _fCfg=catCfg(l)||{};
    const imgHtml=l.photo
      ?`<img src="${l.photo}" alt="${l.title}" style="width:100%;height:100%;object-fit:cover;" loading="lazy" onerror="r2Fallback(this);if(this.dataset.r2tried&&this.src.includes('/media/')){this.style.display='none'}">`
      :(_fCfg.catPhoto
          ?`<img src="${_fCfg.catPhoto}" alt="${l.cat}" style="width:100%;height:100%;object-fit:cover;" loading="lazy" onerror="this.style.display='none';this.insertAdjacentHTML('afterend','<div style=\'width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:34px;\'>${_fCfg.icon}</div>')">`
          :`<div style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:34px;">${_fCfg.icon}</div>`);
    const featTrust=l.trust?`<span style="position:absolute;top:6px;right:6px;background:${trustTier(l.trust).bg};color:${trustTier(l.trust).c};font-size:10px;font-weight:700;padding:2px 7px;border-radius:10px;pointer-events:none;">★ ${l.trust}</span>`:'';
    return`<div class="hcard" onclick="openDetail('${l.id}')" style="display:flex;flex-direction:column;min-height:160px;">
      <div style="position:relative;height:88px;overflow:hidden;flex-shrink:0;background:${catCfg(l).bg};">${imgHtml}${featTrust}</div>
      <div style="padding:6px 9px 4px;flex:1;">
        <div class="ccat" style="font-size:9px;margin-bottom:2px;">${l.cat}</div>
        <div class="ctitle" style="font-size:11.5px;line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;">${l.title}</div>
      </div>
      <div style="padding:0 9px 8px;display:flex;flex-direction:column;gap:2px;">
        <div class="cloc" style="font-size:9.5px;margin:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">📍 ${l.area}</div>
        <div style="display:flex;align-items:center;">
          <div class="cprice" style="font-size:11px;white-space:nowrap;">${l.price?(formatZAR(l.price)||l.price):'<span class="neg">POA</span>'}<span class="per" style="font-size:9px;"> ${l.per}</span></div>
        </div>
      </div>
    </div>`;
  }).join('');
}

function toggleWish(e,id){
  e.stopPropagation();
  wishlist.has(id)?wishlist.delete(id):wishlist.add(id);
  renderGrid(); showToast(wishlist.has(id)?'Added to saved':'Removed from saved');
}
function toggleWishDetail(id){
  wishlist.has(id)?wishlist.delete(id):wishlist.add(id);
  showToast(wishlist.has(id)?'Added to saved':'Removed from saved'); openDetail(id);
}
function renderSaved(){
  const el=document.getElementById('saved-content');
  const saved=LISTINGS.filter(l=>wishlist.has(l.id));
  if(!saved.length){el.innerHTML='<div class="empty-state"><div class="empty-icon">🔖</div><h3>No saved listings</h3><p>Tap the heart icon on any listing to save it here.</p></div>';return;}
  el.innerHTML=`<div class="lgrid">${saved.map(cardHtml).join('')}</div>`;
}

// ── SELLER AVATAR HELPER ─────────────────────────────────
// isOwner: true = seller viewing their own (sharp)
// isRevealed: true = intro accepted (sharp)
function cvAvatarHtml(sellerIdx, listingId, isOwner){
  const idx = (sellerIdx == null) ? 0 : sellerIdx;
  const photo = SELLER_PHOTOS[idx];
  const key = `${idx}-${listingId}`;
  const isRevealed = isOwner || acceptedIntros.has(key);
  const s = SELLERS[idx];

  if(!photo){
    // No photo — emoji fallback with lock badge
    return `${CATS[s.cat].icon}${!isOwner?'<div class="cv-mask">🔒</div>':''}`;
  }

  if(isRevealed){
    return `<img src="${photo}" class="revealed" alt="Seller photo">`;
  } else {
    return `<img src="${photo}" class="blurred" alt="Seller photo"><div class="cv-mask">🔒</div>`;
  }
}


function maskContactInfo(html, introAccepted){
  if(introAccepted) return html;
  // SA phone numbers: 0xx-xxx-xxxx, +27xx, 0xxxxxxxxx, spaces/dashes allowed
  const phoneRe = /(\+27|0)[0-9][\s\-\.]?[0-9]{3}[\s\-\.]?[0-9]{4}/g;
  // Email addresses
  const emailRe = /[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}/g;
  const lockIcon = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>`;
  return html
    .replace(phoneRe, `<span class="contact-masked">${lockIcon}📞 Revealed after introduction</span>`)
    .replace(emailRe, `<span class="contact-masked">${lockIcon}✉️ Revealed after introduction</span>`);
}

function credPhotoHtml(c, introAccepted){
  if(!c.photo) return '';
  if(introAccepted){
    return `<div class="cred-photo-wrap"><img src="${c.photo}" class="cred-photo-revealed"></div>`;
  }
  return `<div class="cred-photo-wrap"><img src="${c.photo}" class="cred-photo-blurred"><div class="cred-photo-lock"><div style="font-size:18px;">🔒</div><div class="cred-photo-lock-text">Certificate revealed<br>after introduction</div></div></div>`;
}

function openBEASellerProfile(l) {
  const t = trustTier(l.trust);
  const active = document.querySelector('.screen.active');
  prevScreen = active ? active.id.replace('screen-', '') : 'browse';
  const catBg   = catCfg(l) ? catCfg(l).bg : 'var(--navy)';
  const catIcon = catCfg(l) ? catCfg(l).icon : '📦';
  const scBadge = l.service_class ? `<span style="font-size:11px;background:rgba(255,255,255,.12);border-radius:50px;padding:3px 9px;">${l.service_class === 'Technical' ? '🔧 Technical' : '🤝 Casuals'}</span> · ` : '';
  document.getElementById('screen-seller-cv').innerHTML = `
    <div class="cv-hero" style="background:${catBg}">
      <button class="cv-back" onclick="goTo('${prevScreen}')"><svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg></button>
      <div class="cv-avatar" style="margin-top:8px;">${l.photo ? `<img src="${l.photo}" style="width:64px;height:64px;border-radius:50%;object-fit:cover;border:2px solid rgba(255,255,255,.6);filter:blur(6px);" onerror="r2Fallback(this);if(this.dataset.r2tried&&this.src.includes('/media/')){this.style.display='none'}">` : `<div style="width:64px;height:64px;border-radius:50%;background:rgba(255,255,255,.15);display:flex;align-items:center;justify-content:center;font-size:30px;">${catIcon}</div>`}</div>
      <div class="cv-headline">${l.cat} Seller</div>
      <div class="cv-cat">${scBadge}${l.area} · 🔒 Anonymous until introduction</div>
      <div class="cv-trust-row">
        <div style="color:${t.c};"><div class="cv-trust-num">${l.trust}</div><div class="cv-trust-label" style="color:${t.c};">${t.label}</div></div>
        <div class="cv-trust-bar"><div class="cv-trust-fill" style="width:${l.trust}%;background:${t.c};"></div></div>
        <div style="font-size:11px;color:rgba(255,255,255,.65);text-align:right;font-weight:400;">Trust<br>Score</div>
      </div>
    </div>
    <div class="cv-body">
      ${l.desc ? `<div class="cv-sec"><div class="cv-sec-title">About this listing</div><p class="cv-about">${maskContactInfo(formatDesc(l.desc), false)}</p></div>` : ''}
      <div class="cv-sec">
        <div class="cv-sec-title">Credentials &amp; qualifications</div>
        <div id="bea-creds-${l.id}">${(()=>{
          const SIG_LABELS={id_verified:'Identity verified',address_verified:'Address verified',phone_verified:'Phone verified',bank_verified:'Bank account verified',years_2_5:'2–5 yrs experience',years_5_10:'5–10 yrs experience',years_10plus:'10+ yrs experience',ffc:'FFC registered',paia:'PAIA compliant',cpa:'CPA compliant',estate_agency:'Estate agency registered',qualification:'Qualification on file',professional_body:'Professional body member',portfolio:'Portfolio uploaded',insurance:'Professional insurance',references:'References available'};
          let sf={};try{sf=JSON.parse(l.structured_fields||'{}');}catch(e){}
          const sigs=sf._signals||{};
          let html='';
          Object.keys(sigs).forEach(k=>{const st=sigs[k];if(!st||st.status==='skipped')return;const lbl=SIG_LABELS[k]||k;const ok=st.status==='uploaded';const icon=ok?'✓':'○';const col=ok?'var(--accent)':'var(--text-3)';html+=`<div style="display:flex;align-items:center;gap:8px;padding:7px 0;border-bottom:1px solid var(--border);"><div style="width:22px;height:22px;border-radius:50%;background:var(--accent-light);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:${col};">${icon}</div><div style="font-size:13px;font-weight:600;color:var(--text);">${lbl}</div></div>`;});
          return html||'<span style="font-size:12px;color:var(--text-3);">Seller credentials build over time as they complete their Trust Score checklist.</span>';
        })()}</div>
      </div>
      <div class="cv-sec"><div class="cv-identity-block"><div class="cv-identity-icon">🔒</div><div class="cv-identity-text"><h4>Identity protected until introduction</h4><p>Name, contact details and exact location are only revealed after both parties accept a mutual introduction.</p></div></div></div>
    </div>
    <div class="cv-sticky">
      <button class="cv-cta" onclick="openModal('${l.id}')">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24" width="18" height="18"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        Request Introduction · 1T on acceptance
      </button>
    </div>`;
  goTo('seller-cv');
}

function openSellerCV(sellerIdx,listingId){
  // BEA (live) listings: sellerIdx is null — render a profile built from listing data
  if (sellerIdx == null) {
    const l = findListing(listingId);
    if (l && l.isLive) { openBEASellerProfile(l); return; }
  }
  const idx = (sellerIdx == null) ? 0 : sellerIdx;
  const s=SELLERS[idx],l=findListing(listingId);
  const cvScore=s.trustScore!=null?s.trustScore:(l?l.trust:0);
  const t=trustTier(cvScore);
  const introAccepted = acceptedIntros.has(`${idx}-${listingId}`);
  const active=document.querySelector('.screen.active');
  prevScreen=active?active.id.replace('screen-',''):'browse';
  const portfolioHtml=s.portfolio&&s.portfolio.length>0
    ?s.portfolio.map(p=>`<div class="cv-port-img"><img src="${p}" loading="lazy" onerror="r2Fallback(this);if(this.dataset.r2tried&&this.src.includes('/media/')){this.style.display='none'}"></div>`).join('')
    :`<div class="cv-port-img">🏠</div><div class="cv-port-img">🔧</div><div class="cv-port-img">📐</div>`;
  const regionLabel = s.region || (l && l.city) || 'Pretoria and surrounds';
  document.getElementById('screen-seller-cv').innerHTML=`
    <div class="cv-hero">
      <button class="cv-back" onclick="goTo('${prevScreen}')"><svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg></button>
      <div class="cv-avatar" style="margin-top:8px;">${cvAvatarHtml(idx, listingId, false)}</div>
      <div class="cv-headline">${s.headline}</div>
      <div class="cv-cat">${s.cat} · ${regionLabel} · 🔒 Anonymous until introduction</div>
      <div class="cv-trust-row">
        <div style="color:${t.c};"><div class="cv-trust-num">${l.trust}</div><div class="cv-trust-label" style="color:${t.c};">${t.label}</div></div>
        <div class="cv-trust-bar"><div class="cv-trust-fill" style="width:${l.trust}%;background:${t.c};"></div></div>
        <div style="font-size:11px;color:rgba(255,255,255,.65);text-align:right;font-weight:400;">Trust<br>Score</div>
      </div>
      <div style="font-size:10px;color:rgba(255,255,255,.35);margin-top:8px;line-height:1.5;font-weight:400;">Score is built from: verified credentials · completed introductions · response rate · buyer ratings · years active. Verified by TrustSquare — not self-reported.</div>
    </div>
    <div class="cv-body">
      <div class="cv-sec">
        <div class="cv-sec-title">Experience &amp; background</div>
        <p class="cv-about">${s.about||'This seller has not yet added a background description.'}</p>
        ${s.yearsExp?`<div style="margin-top:10px;display:inline-flex;align-items:center;gap:6px;background:var(--accent-light);border-radius:50px;padding:5px 14px;font-size:12px;font-weight:700;color:var(--accent);">⏱ ${s.yearsExp} years experience</div>`:''}
      </div>
      <div class="cv-sec"><div class="cv-sec-title">Track record</div><div class="cv-stats">${s.stats&&s.stats.length?s.stats.map(st=>`<div class="cv-stat"><div class="cv-stat-val">${st.val}</div><div class="cv-stat-label">${st.label}</div></div>`).join(''):'<div style="font-size:12px;color:var(--text-3);">Track record will build over time on TrustSquare.</div>'}</div></div>
      <div class="cv-sec">
        <div class="cv-sec-title">Credentials &amp; qualifications</div>
        <div style="font-size:11px;color:var(--text-3);margin-bottom:10px;">Certificate photos are blurred — revealed only after introduction is accepted.</div>
        <div class="cv-creds">${s.creds&&s.creds.length?s.creds.map(c=>{
          if(typeof c==='string'){return`<div class="cv-cred"><div class="cv-cred-dot" style="font-size:18px;line-height:1;">·</div><div style="flex:1;"><div class="cv-cred-label">${c}</div></div></div>`;}
          return`<div class="cv-cred"><div class="cv-cred-dot">${c.icon||'·'}</div><div style="flex:1;"><div class="cv-cred-label">${c.label||''}</div>${c.sub?`<div class="cv-cred-sub">${c.sub}</div>`:''} ${credPhotoHtml(c,introAccepted)}</div></div>`;
        }).join(''):'<div style="font-size:12px;color:var(--text-3);">No credentials added yet.</div>'}</div>
      </div>
      ${s.tags&&s.tags.length?`<div class="cv-sec"><div class="cv-sec-title">Specialisations</div><div class="cv-tags">${s.tags.map(tag=>`<div class="cv-tag">${tag}</div>`).join('')}</div></div>`:''}
      ${s.avail&&s.avail.length?`<div class="cv-sec"><div class="cv-sec-title">Availability</div><div class="cv-avail">${s.avail.map(a=>`<div class="cv-avail-row"><div class="cv-avail-dot"></div><div class="cv-avail-day">${a.day}</div><div class="cv-avail-time">${a.time}</div></div>`).join('')}</div></div>`:''}
      ${s.cat==='Property'?`<div class="cv-sec"><div class="cv-sec-title">Portfolio</div><div class="cv-portfolio">${portfolioHtml}</div><div style="font-size:11px;color:var(--text-3);margin-top:8px;font-weight:400;">Representative properties — specific addresses revealed after introduction.</div></div>`:''}
      <div class="cv-sec"><div class="cv-identity-block"><div class="cv-identity-icon">🔒</div><div class="cv-identity-text"><h4>Identity protected until introduction</h4><p>This seller\'s name, business name, contact details and exact location are only revealed after both parties accept a mutual introduction. Certificate photos are also unlocked at that point.</p></div></div></div>
    </div>
    <div class="cv-sticky">
      <button class="cv-cta" onclick="openModal('${listingId}')">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24" width="18" height="18"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        Request Introduction · 1T on acceptance
      </button>
    </div>`;
  goTo('seller-cv');
}

// Safe listing lookup — works for both numeric ids (demo data) and 'bea_N' string ids (live data)
function findListing(id){ return LISTINGS.find(l=>l.id==id)||LISTINGS.find(l=>String(l.id)===String(id)); }

// Safe CATS lookup — maps Adventures subcategories to the 'Adventures' entry
function catCfg(l){
  const key = l.cat;
  if(CATS[key]) return CATS[key];
  if(key==='adventures_accommodation'||key==='adventures_experiences') return CATS['Adventures'];
  if(key==='local_market'||key==='local market'||key==='localmarket') return CATS['LocalMarket'];
  return { icon:'📦', bg:'var(--navy)', model:'queue' };
}

function openDetail(id){
  const l=findListing(id);
  msTrackView(l);
  const active=document.querySelector('.screen.active');
  prevScreen=active?active.id.replace('screen-',''):'browse';
  const t=trustTier(l.trust),m=catCfg(l).model,isCommit=m==='commit';
  const _introKey = `${l.sellerIdx==null?0:l.sellerIdx}-${l.id}`;
  const _introAccepted = acceptedIntros.has(_introKey);

  // Build photo strip — supports 1..N photos with dot indicators; uses photoData for captions
  const photos = (l.photos && l.photos.length) ? l.photos : (l.photo ? [l.photo] : []);
  const photoData = (l.photoData && l.photoData.length) ? l.photoData : photos.map(u=>({url:u,caption:''}));
  // Store photos globally keyed by listing id so lightbox onclick avoids JSON-in-attribute issues
  _listingPhotosCache[id] = photos;
  const stripSlides = photos.length
    ? photoData.map((pd,pi) => {
        const cap = pd.caption||'';
        const capHtml = cap ? `<div style="position:absolute;bottom:8px;right:8px;background:rgba(10,10,20,.78);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);border-radius:7px;padding:5px 11px;font-size:11.5px;font-weight:600;color:#fff;pointer-events:none;line-height:1.45;max-width:72%;text-align:right;letter-spacing:.15px;box-shadow:0 2px 8px rgba(0,0,0,.35);font-family:'Inter',sans-serif;">${cap.replace(/</g,'&lt;')}</div>` : '';
        return `<div class="photo-strip-slide" style="cursor:zoom-in;position:relative;" onclick="openLightboxById('${id}',${pi})">
          <img src="${pd.url}" alt="${l.title}" loading="lazy" style="pointer-events:none;" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">
          <div class="emoji-fallback" style="display:none;background:${catCfg(l).bg};pointer-events:none;">${catCfg(l).icon}</div>
          ${capHtml}
        </div>`;
      }).join('')
    : `<div class="photo-strip-slide"><div class="emoji-fallback" style="background:${catCfg(l).bg}">${catCfg(l).icon}</div></div>`;
  const dotsHtml = photos.length > 1
    ? `<div class="photo-strip-dots">${photos.map((_,i)=>`<div class="psd${i===0?' active':''}" id="psd-${id}-${i}"></div>`).join('')}</div>`
    : '';
  // Adventures category display label + price formatting
  const isAdv = l.cat==='adventures_accommodation'||l.cat==='adventures_experiences'||l.cat==='Adventures';
  const catDisplayLabel = l.cat==='adventures_accommodation' ? '🏕 Accommodation'
    : l.cat==='adventures_experiences' ? '🌄 Experiences'
    : l.cat;
  const advCur = isAdv ? (ADV_COUNTRY_CURRENCY[(l.country||'ZA').toUpperCase()]||'R') : null;
  const advEnvLabel = isAdv ? (ADV_ENV_LABELS[(l.environment_type||'').toLowerCase().replace(/\s+/g,'_')]||'') : '';
  const advPriceDisplay = isAdv && l.price
    ? `${advCur}${Number(l.price).toLocaleString()}`
    : null;
  const _isCollectorsCat = (l.cat||'').toLowerCase()==='collectors';
  const heroHtml = `
    <div class="photo-strip-wrap${_isCollectorsCat?' collectors-strip':''}" id="pstrip-wrap-${id}">
      <div class="photo-strip" id="pstrip-${id}" onscroll="updateStripDots('${id}',${photos.length}); if(typeof syncAdvThumbs==='function') syncAdvThumbs('${id}', Math.round(this.scrollLeft/this.offsetWidth))">
        ${stripSlides}
      </div>
      ${dotsHtml}
      ${photos.length>1?`<button class="strip-arrow strip-arrow-left" onclick="stripNav('${id}',-1)">&#8249;</button><button class="strip-arrow strip-arrow-right" onclick="stripNav('${id}',1)">&#8250;</button>`:''}
      ${isAdv && photos.length > 1 ? '<div class="adv-thumbs" id="adv-thumbs-'+id+'">' + photos.map(function(u,ti){ return '<div class="adv-thumb'+(ti===0?' active':'')+'" id="adv-thumb-'+id+'-'+ti+'" onclick="advThumbClick(\'' + id + '\',' + ti + ')"><img src="' + u + '" loading="lazy"></div>'; }).join('') + '</div>' : ''}
      <div class="dnav">
        <button class="dib" onclick="goTo('${prevScreen}')"><svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg></button>
        <button class="dib" onclick="toggleWishDetail('${id}')"><svg xmlns="http://www.w3.org/2000/svg" fill="${wishlist.has(id)?'#c8873a':'none'}" stroke="${wishlist.has(id)?'#c8873a':'currentColor'}" viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg></button>
      </div>
    </div>`;
  const flowHtml=isCommit?`
    <div class="intro-model-block commit">
      <div class="imb-label commit">⏳ Commitment Model · Property</div>
      <div class="imb-title">Your introduction is protected</div>
      <div class="commit-steps">
        <div class="cs"><div class="cs-dot buyer">B</div><div><div class="cs-label">You submit introduction request</div><div class="cs-sub">No Tuppence deducted yet</div></div></div>
        <div class="cs"><div class="cs-dot system">⏸</div><div><div class="cs-label">Listing paused immediately</div><div class="cs-sub">Invisible to other buyers during review</div></div></div>
        <div class="cs"><div class="cs-dot seller">S</div><div><div class="cs-label">Seller has 48hrs to Accept or Decline</div><div class="cs-sub">Seller sees your message before deciding</div></div></div>
        <div class="cs"><div class="cs-dot reveal">✓</div><div><div class="cs-label">Accepted → 1T deducted · identities revealed</div><div class="cs-sub">Both parties connect directly</div></div></div>
        <div class="cs"><div class="cs-dot penalty">✕</div><div><div class="cs-label">Declined → you pay nothing · listing reopens</div><div class="cs-sub">Ignored within 48hrs → seller Trust −5 · you pay nothing</div></div></div>
      </div>
    </div>`:`
    <div class="intro-model-block queue">
      <div class="imb-label queue">👥 Soft Queue · ${l.cat}</div>
      <div class="imb-title">Listing stays live — always available</div>
      <div class="commit-steps">
        <div class="cs"><div class="cs-dot buyer">B</div><div><div class="cs-label">You submit introduction request</div><div class="cs-sub">No Tuppence deducted yet · listing stays visible</div></div></div>
        <div class="cs"><div class="cs-dot system q">👥</div><div><div class="cs-label">Added to seller\'s queue — listing stays live</div><div class="cs-sub">Other buyers can still request simultaneously</div></div></div>
        <div class="cs"><div class="cs-dot seller">S</div><div><div class="cs-label">Seller notified · has 48hrs to respond</div><div class="cs-sub">Seller reviews all queued requests</div></div></div>
        <div class="cs"><div class="cs-dot reveal">✓</div><div><div class="cs-label">Accepted → 1T deducted · identities revealed</div><div class="cs-sub">Connect directly with seller</div></div></div>
        <div class="cs"><div class="cs-dot reveal">✓</div><div><div class="cs-label">Respond within 24hrs → Trust Score +3</div><div class="cs-sub">No response within 48hrs → Trust Score −5</div></div></div>
      </div>
    </div>
    ${l.queueCount>0?`<div style="display:flex;align-items:center;gap:10px;background:#fff;border-radius:var(--r-sm);padding:11px 13px;margin-bottom:14px;border:1.5px solid #c4b5fd;"><div style="font-size:24px;font-weight:700;color:var(--purple);font-family:'Inter',sans-serif;">${l.queueCount}</div><div><div style="font-size:13px;font-weight:600;color:var(--navy);">${l.queueCount} buyer${l.queueCount>1?'s':''} currently in queue</div><div style="font-size:11px;color:var(--text-3);font-weight:400;margin-top:2px;">Seller responds to all requests within 48hrs</div></div></div>`:''}`;
  // Adventures vars declared above heroHtml

  document.getElementById('screen-detail').innerHTML=`
    ${heroHtml}
    <div class="dsheet">
      <div class="dcat-row">
        <span class="dcat">${catDisplayLabel}</span>
        <span class="model-badge ${m}" style="position:static;font-size:10px;padding:3px 8px;">${isCommit?'⏳ Commitment':'👥 Soft Queue'}</span>
        ${l.feat?'<span style="font-size:10px;font-weight:700;color:var(--accent);">★ FEATURED</span>':''}
      </div>
      <div class="dtitle">${l.title}</div>
      <div class="dmeta"><div class="dmi"><svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>${l.area}${isAdv&&l.country?` · ${ADV_COUNTRY_FLAGS[l.country.toUpperCase()]||''} ${l.country.toUpperCase()}`:''}${advEnvLabel?' · '+advEnvLabel:''}</div></div>
      <div class="trust-block" style="background:${t.bg};border-color:${t.c}30;">
        <div><div class="tscore" style="color:${t.c};">${l.trust}</div><div class="tlabel" style="color:${t.c};">${t.label}</div><div class="tsub" style="color:${t.c};">Trust Score</div></div>
        <div class="tbar-wrap"><div class="tbar"><div class="tbar-fill" style="width:${l.trust}%;background:${t.c};"></div></div><div class="tscale" style="color:${t.c};">0 · New · 40 · Established · 70 · Trusted · 90 · Highly Trusted</div></div>
      </div>
      <div class="price-block">
        <div>
          <div style="font-size:11px;font-weight:600;color:var(--text-3);letter-spacing:.4px;text-transform:uppercase;margin-bottom:4px;">Price</div>
          ${isAdv && advPriceDisplay
            ? `<div class="pamount">${advPriceDisplay}</div>${l.per?`<div class="pper">${l.per}</div>`:''}`
            : l.price
              ? `<div class="pamount">${formatZAR(l.price)||l.price}</div>${l.per?`<div class="pper">${l.per}</div>`:''}`
              : `<div class="pneg">Negotiable — discuss with seller</div>`}
        </div>
      </div>
      <div id="detail-price-check-${id}" style="margin-bottom:14px;display:none;">
        <div style="font-size:13px;font-weight:700;color:#92400e;margin-bottom:2px;font-family:'Syne',sans-serif;">💡 Is this a fair price?</div>
        <div style="font-size:11px;color:#9ca3af;margin-bottom:6px;">Choose how precise you need it — you only pay if we return a real figure.</div>
        <div id="detail-pc-chips-${id}"></div>
        <div id="detail-pc-result-${id}" style="display:none;margin-top:8px;"></div>
      </div>
      ${(l.cat==='Property'||l.cat==='Estate Agents'||l.cat==='Accommodation') ? `
      <div id="detail-yield-${id}" style="margin-bottom:14px;display:none;">
        <div style="font-size:13px;font-weight:700;color:#5b21b6;margin-bottom:2px;font-family:'Syne',sans-serif;">📈 Investor Yield Calculator</div>
        <div style="font-size:11px;color:#9ca3af;margin-bottom:6px;">Gross rental yield — choose how precise you need it.</div>
        <div id="detail-yield-chips-${id}"></div>
        <div id="detail-yield-result-${id}" style="display:none;margin-top:8px;"></div>
      </div>` : ''}
      ${isAdv ? '<div class="adv-stat-strip">' + (function(){
          var expLabel = l.experience_type ? (ADV_EXP_TYPE_LABELS[l.experience_type] || l.experience_type.replace(/_/g,' ')) : '';
          var accLabel = l.accommodation_type ? (ADV_ACC_TYPE_LABELS[l.accommodation_type] || l.accommodation_type.replace(/_/g,' ')) : '';
          var typeLabel = expLabel || accLabel;
          var envKey = (l.environment_type||'').toLowerCase().replace(/\s+/g,'_');
          var envL = ADV_ENV_LABELS[envKey] || ADV_ENV_LABELS[(l.environment_type||'').toLowerCase()] || '';
          var countryCode = (l.country||'ZA').toUpperCase();
          var flag = ADV_COUNTRY_FLAGS[countryCode] || '🌍';
          var parts = [];
          if(typeLabel) parts.push('<span class="adv-stat price-stat">'+typeLabel+'</span>');
          if(envL) parts.push('<span class="adv-stat env-stat">'+envL+'</span>');
          if(l.groupSize) parts.push('<span class="adv-stat group-stat">👥 '+l.groupSize+'</span>');
          if(l.duration) parts.push('<span class="adv-stat duration-stat">⏱ '+l.duration+'</span>');
          if(countryCode && countryCode !== 'ZA') parts.push('<span class="adv-stat country-stat">'+flag+' '+countryCode+'</span>');
          return parts.join('');
        })() + '</div>' : ''}
      ${l.cat==='Tutors' && (l.subject||l.level||l.mode) ? `
      <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px;">
        ${l.subject ? `<span style="background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;">📚 ${l.subject}</span>` : ''}
        ${l.level   ? `<span style="background:var(--surface-2);color:var(--text);border:1px solid var(--border);border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;">🎓 ${l.level}</span>` : ''}
        ${l.mode    ? `<span style="background:var(--surface-2);color:var(--text);border:1px solid var(--border);border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;">📍 ${l.mode}</span>` : ''}
      </div>` : ''}
      ${l.cat==='Services' && (l.service_type||l.availability||l.service_class) ? `
      <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px;">
        ${l.service_class ? `<span style="background:#f0fdf4;color:#166534;border:1px solid #bbf7d0;border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;">⚙️ ${l.service_class}</span>` : ''}
        ${l.service_type  ? `<span style="background:var(--surface-2);color:var(--text);border:1px solid var(--border);border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;">🔧 ${l.service_type}</span>` : ''}
        ${l.availability  ? `<span style="background:var(--surface-2);color:var(--text);border:1px solid var(--border);border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;">📅 ${l.availability}</span>` : ''}
      </div>` : ''}
      ${l.cat==='Property' && (l.propType||l.beds||l.baths||l.garages||l.listingType) ? `
      <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px;">
        ${l.listingType ? `<span style="background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;">${l.listingType==='rent'?'🔑 For Rent':'🏦 For Sale'}</span>` : ''}
        ${l.propType ? `<span style="background:#f0fdf4;color:#166534;border:1px solid #bbf7d0;border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;">🏠 ${l.propType}</span>` : ''}
        ${l.beds ? `<span style="background:var(--surface-2);color:var(--text);border:1px solid var(--border);border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;">🛏 ${l.beds} bed${l.beds>1?'s':''}</span>` : ''}
        ${l.baths ? `<span style="background:var(--surface-2);color:var(--text);border:1px solid var(--border);border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;">🚿 ${l.baths} bath${l.baths>1?'s':''}</span>` : ''}
        ${l.garages    ? `<span style="background:var(--surface-2);color:var(--text);border:1px solid var(--border);border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;">🚗 ${l.garages} garage${l.garages>1?'s':''}</span>` : ''}
        ${l.floor_area ? `<span style="background:var(--surface-2);color:var(--text);border:1px solid var(--border);border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;">📐 ${l.floor_area} m² floor</span>` : ''}
        ${l.erf_size   ? `<span style="background:var(--surface-2);color:var(--text);border:1px solid var(--border);border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;">🌳 ${l.erf_size} m² erf</span>` : ''}
      </div>` : ''}
      ${l.cat==='LocalMarket' && (l.area||l.suburb) ? `
      <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px;">
        <span style="background:#faf5ff;color:#6d28d9;border:1px solid #ddd6fe;border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;">🛒 Local Market</span>
        ${(l.suburb||l.area) ? `<span style="background:var(--surface-2);color:var(--text);border:1px solid var(--border);border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;">📍 ${l.suburb||l.area}</span>` : ''}
      </div>` : ''}
      ${l.cat==='Collectors' && l.desc ? `
      <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px;">
        <span style="background:#fff7ed;color:#c2410c;border:1px solid #fed7aa;border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;">🏺 Collectors item</span>
        ${l.area||l.suburb ? `<span style="background:var(--surface-2);color:var(--text);border:1px solid var(--border);border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;">📍 ${l.suburb||l.area}</span>` : ''}
      </div>` : ''}
      ${l.cat==='Cars' && (l.prop_type||l.area||l.suburb) ? `
      <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px;">
        <span style="background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;">🚗 Vehicle</span>
        ${l.prop_type ? `<span style="background:var(--surface-2);color:var(--text);border:1px solid var(--border);border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;">${l.prop_type}</span>` : ''}
        ${l.area||l.suburb ? `<span style="background:var(--surface-2);color:var(--text);border:1px solid var(--border);border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;">📍 ${l.suburb||l.area}</span>` : ''}
      </div>` : ''}
      <div class="dsec"><h3>About this listing</h3>${maskContactInfo(formatDesc(l.desc),_introAccepted)}</div>
      <div style="margin-bottom:16px;">
        ${(function(){var sidStr=l.sellerIdx!=null?l.sellerIdx:'null';var ci=catCfg(l);var onclk='openSellerCV('+sidStr+','+'\''+(id)+'\''+')';return '<button onclick="'+onclk+'" style="width:100%;background:var(--surface-2);border:1.5px solid var(--border);border-radius:var(--r-sm);padding:13px 16px;display:flex;align-items:center;gap:12px;cursor:pointer;transition:all var(--t);">'+'<div style="width:40px;height:40px;border-radius:50%;background:'+ci.bg+';display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">'+ci.icon+'</div>'+'<div style="flex:1;text-align:left;"><div style="font-size:13px;font-weight:600;color:var(--text);">View seller profile</div><div style="font-size:11px;color:var(--text-3);margin-top:2px;font-weight:400;">Credentials · Track record · Availability · 🔒 Identity masked</div></div>'+'<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="var(--text-3)" viewBox="0 0 24 24" width="16" height="16"><polyline points="9 18 15 12 9 6"/></svg></button>';})()}
      </div>
      ${flowHtml}
      <div id="detail-poi-strip" style="display:none;">
        <div class="poi-strip-wrap">
          <div class="poi-strip-hdr" id="poi-section-hdr">📍 Nearby Amenities</div>
          <div class="poi-tabs" id="poi-tabs"></div>
          <div class="poi-cards" id="poi-cards"></div>
        </div>
      </div>
      <div id="detail-wonders-strip" style="display:none;">
        <div class="wonders-strip-hdr">🌍 Nearby World Wonders</div>
        <div class="wonders-strip" id="detail-wonders-list"></div>
      </div>
      <div class="anon-block">
        <div class="lock-icon">🔒</div>
        <h4>Identity protected until introduction</h4>
        <p>Seller name, contact details and specific address are only revealed after both parties accept.</p>
      </div>
    </div>
    <div class="sticky-cta">
      <button class="cta-btn ${isCommit?'commit-cta':'queue-cta'}" onclick="openModal('${id}')">
        ${isCommit?'⏳ Request Introduction':'👥 Join Queue'}
        <span class="cta-cost">· 1T on acceptance</span>
      </button>
    </div>`;
  goTo('detail');
  loadDetailWonders(l);
  loadDetailPois(l);
  tvsInitDetail(id, l.cat);
  if (photos.length > 1) {
    const stripEl = document.getElementById('pstrip-' + id);
    if (stripEl) {
      let touchX = 0, touchScrollLeft = 0;
      stripEl.addEventListener('touchstart', e => {
        touchX = e.touches[0].clientX;
        touchScrollLeft = stripEl.scrollLeft;
      }, { passive: true });
      stripEl.addEventListener('touchend', e => {
        const dx = e.changedTouches[0].clientX - touchX;
        if (Math.abs(dx) > 50) {
          const w = stripEl.offsetWidth;
          const count = stripEl.querySelectorAll('.photo-strip-slide').length;
          const idx = Math.round(touchScrollLeft / w);
          const next = Math.max(0, Math.min(count - 1, idx + (dx < 0 ? 1 : -1)));
          stripEl.scrollTo({ left: next * w, behavior: 'smooth' });
          setTimeout(() => updateStripDots(id, count), 80);
        }
      }, { passive: true });
    }
  }
}

// ── AI3: Buyer Price Check (Session 73) ──────────────────────────────────────
// -- Tiered Value Selector (TVS) chip selector + tier-aware checks (STEP 4) ----
function tvsInitDetail(id, cat){
  try{
    tvsLoadService(id,'fair_price','detail-price-check-'+id,'detail-pc-chips-'+id);
    if(cat==='Property'||cat==='Estate Agents'||cat==='Accommodation')
      tvsLoadService(id,'yield','detail-yield-'+id,'detail-yield-chips-'+id);
  }catch(e){}
}
async function tvsLoadService(id, service, wrapId, chipsId){
  const wrap=document.getElementById(wrapId), box=document.getElementById(chipsId);
  if(!wrap||!box) return;
  let chips=[];
  if(DEMO_MODE){
    chips=[{tier:'0T',color:'green',name:(service==='yield'?'Area yield':'Area guide'),desc:'Suburb benchmark (demo data).',ready:true,tuppence:0}];
  } else {
    const numId=parseInt(String(id).replace('bea_',''));
    if(isNaN(numId)){ wrap.style.display='none'; return; }
    try{
      const r=await fetch(BEA_URL+'/listings/'+numId+'/value-tiers?service='+service);
      if(!r.ok){ wrap.style.display='none'; return; }
      const d=await r.json();
      chips=(d.chips||[]).filter(c=>c.ready);
    }catch(_){ wrap.style.display='none'; return; }
  }
  if(!chips.length){ wrap.style.display='none'; return; }   // hide rule: nothing true to offer
  const fn = service==='yield' ? 'tvsYieldCalc' : 'tvsPriceCheck';
  box.innerHTML = chips.map(c=>tvsChip(id,c,fn)).join('');
  wrap.style.display='';
}
function tvsChip(id,c,fn){
  const m={green:['#bfe6cf','#f3fbf6','#1a8a52','#e7f6ee'],blue:['#bcd9f1','#f3f9fe','#1b6fb5','#e8f1fa'],gold:['#e8d39a','#fdf9ee','#a87a16','#fbf2da']};
  const col=m[c.color]||['#e5e7eb','#fafafa','#555','#eee'];
  const cost=c.tier==='0T'?'Free':c.tier;
  return `<button onclick="${fn}('${id}','${c.tier}')" style="width:100%;text-align:left;border:1.5px solid ${col[0]};background:${col[1]};border-radius:11px;padding:10px 13px;margin:6px 0;cursor:pointer;display:flex;justify-content:space-between;align-items:center;gap:10px;font-family:'Syne',sans-serif;"><span><span style="font-weight:700;font-size:13px;color:${col[2]};">${c.name}</span><span style="display:block;font-size:11px;color:#6b7280;margin-top:2px;">${c.desc}</span></span><span style="font-weight:800;font-size:12px;color:${col[2]};background:${col[3]};padding:3px 10px;border-radius:20px;white-space:nowrap;">${cost}</span></button>`;
}
function tvsReloadChips(id, service){
  if(service==='yield') tvsLoadService(id,'yield','detail-yield-'+id,'detail-yield-chips-'+id);
  else tvsLoadService(id,'fair_price','detail-price-check-'+id,'detail-pc-chips-'+id);
}
function tvsCard(opts){
  const flag=opts.flag?`<div style="background:#fffbeb;border:1.5px solid #fcd34d;border-radius:8px;padding:8px 10px;margin-bottom:8px;font-size:11px;color:#78350f;"><b>${opts.flag.headline||''}</b><br>${opts.flag.detail||''}</div>`:'';
  const range=(opts.range&&opts.range!=='N/A')?`<div style="font-size:13px;font-weight:800;color:#111827;margin:4px 0;">${opts.range}</div>`:'';
  const badge=opts.tier?`<span style="font-size:10px;font-weight:700;background:#eef2ff;color:#3730a3;padding:2px 8px;border-radius:20px;">${opts.tier==='0T'?'Free':opts.tier}</span>`:'';
  const prov=opts.provenance?`<div style="font-size:10.5px;color:#6b7280;margin-top:7px;">Source: ${opts.provenance}</div>`:'';
  const bal=(opts.remaining!==undefined&&opts.remaining!==null)?`<div style="font-size:10px;color:#9ca3af;margin-top:3px;">${opts.charged?('Charged '+opts.charged+' - '):''}${opts.remaining}T balance</div>`:'';
  return `<div style="background:#f9fafb;border:1.5px solid #e5e7eb;border-radius:11px;padding:13px 15px;">${flag}<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:5px;"><span style="font-size:12px;font-weight:800;color:#111827;">${opts.title||''}</span>${badge}</div>${range}<div style="font-size:12px;color:#374151;line-height:1.55;">${opts.body||''}</div>${prov}<div style="font-size:10px;color:#9ca3af;margin-top:5px;font-style:italic;">${opts.label||''}</div>${bal}</div>`;
}
async function tvsPriceCheck(id, tier){
  const res=document.getElementById('detail-pc-result-'+id), box=document.getElementById('detail-pc-chips-'+id);
  if(!res) return;
  const label='Indicative only - information, not financial advice or a formal valuation.';
  if(DEMO_MODE){
    res.style.display='block'; if(box) box.style.display='none';
    res.innerHTML=tvsCard({title:'Area guide (demo)',range:'R9,000-R16,000 per m2',body:'Suburb benchmark for this area. Demo data, not property-specific.',provenance:'PayProp/TPN (demo), 2026 Q1',tier:'0T',label:label});
    return;
  }
  const email=localStorage.getItem('ms_aa_email')||localStorage.getItem('ms_user_email')||'';
  if(!email){ showToast('Sign in to use AI price tools'); return; }
  if(tier!=='0T'){
    let bal=0; try{const br=await fetch(BEA_URL+'/tuppence/balance?email='+encodeURIComponent(email)); if(br.ok){const bd=await br.json(); bal=bd.balance||0;}}catch(_){ }
    const need=tier==='2T'?2:1;
    if(bal<need){ showToast('Insufficient Tuppence - top up to use this check'); return; }
    const msg=tier==='2T'
      ? 'This premium check uses a licensed data partner and costs 2T. You are charged only if we return a real, property-specific figure. Proceed?'
      : 'This checks the price against a verified source. 1T is charged ONLY if we verify a real price - never for a guess. Proceed?';
    if(!confirm(msg)) return;
  }
  const numId=parseInt(String(id).replace('bea_','')); if(isNaN(numId)){ showToast('Only available on live listings'); return; }
  if(box) box.innerHTML='<div style="font-size:12px;color:#6b7280;padding:8px;">Checking market...</div>';
  try{
    const r=await fetch(BEA_URL+'/listings/'+numId+'/price-check?email='+encodeURIComponent(email)+'&tier='+tier,{method:'POST'});
    if(r.status===402){ showToast('Insufficient Tuppence'); tvsReloadChips(id,'fair_price'); return; }
    if(!r.ok){ showToast('Price check failed'); tvsReloadChips(id,'fair_price'); return; }
    const d=await r.json();
    res.style.display='block'; if(box) box.style.display='none';
    if(d.verdict==='area_guide'){
      res.innerHTML=tvsCard({title:'Area guide',range:d.official_range,body:d.assessment,provenance:(d.official_context||'')+(d.provenance_date?(' ('+d.provenance_date+')'):''),tier:'0T',label:d.indicative_label||label,remaining:d.tuppence_remaining});
      return;
    }
    if(d.verdict==='cannot_verify'||d.charged===false){
      res.innerHTML=tvsCard({title:'No verified price - not charged',body:d.assessment||'We could not verify a market price, so nothing was charged.',label:label,remaining:d.tuppence_remaining});
      return;
    }
    const srcName=d.source==='internal_comps'?'TrustSquare comparable listings'
      :d.source==='land_registry'?'HM Land Registry sold prices'
      :d.source==='scryfall'?'TCGPlayer via Scryfall (live FX)':(d.source||'verified feed');
    res.innerHTML=tvsCard({title:'Verified market read',range:d.official_range,body:(d.assessment||d.context||''),provenance:(d.official_context||srcName),tier:tier,label:label,remaining:d.tuppence_remaining,charged:(tier==='2T'?'2T':'1T'),flag:d.safety_flag});
  }catch(e){ showToast('Price check error'); tvsReloadChips(id,'fair_price'); }
}
async function tvsYieldCalc(id, tier){
  const res=document.getElementById('detail-yield-result-'+id), box=document.getElementById('detail-yield-chips-'+id);
  if(!res) return;
  const label='Indicative only - not financial advice. A figure shown may be estimated from area benchmarks (not property-specific); verify with a registered property practitioner.';
  if(DEMO_MODE){
    res.style.display='block'; if(box) box.style.display='none';
    res.innerHTML=`<div style="background:#faf5ff;border:1.5px solid #c4b5fd;border-radius:11px;padding:13px 15px;"><div style="font-weight:800;color:#5b21b6;font-size:18px;">8.4% gross</div><div style="font-size:12px;color:#374151;margin-top:4px;">Demo: area-benchmark yield for this suburb.</div><div style="font-size:10px;color:#9ca3af;margin-top:6px;font-style:italic;">${label}</div></div>`;
    return;
  }
  const email=localStorage.getItem('ms_aa_email')||localStorage.getItem('ms_user_email')||'';
  if(!email){ showToast('Sign in to use the yield calculator'); return; }
  if(tier!=='0T'){
    let bal=0; try{const br=await fetch(BEA_URL+'/tuppence/balance?email='+encodeURIComponent(email)); if(br.ok){const bd=await br.json(); bal=bd.balance||0;}}catch(_){ }
    const need=tier==='2T'?2:1;
    if(bal<need){ showToast('Insufficient Tuppence'); return; }
    const msg=tier==='2T'?'This premium yield uses a licensed data partner and costs 2T. Charged only if we compute a real yield. Proceed?':'This computes the real rental yield. 1T is charged only if a yield is produced (you may be asked for a figure). Proceed?';
    if(!confirm(msg)) return;
  }
  const numId=parseInt(String(id).replace('bea_','')); if(isNaN(numId)){ showToast('Only available on live listings'); return; }
  try{
    let r=await fetch(BEA_URL+'/listings/'+numId+'/yield-calc?email='+encodeURIComponent(email)+'&tier='+tier,{method:'POST'});
    if(r.status===402){ showToast('Insufficient Tuppence'); return; }
    if(r.status===400){ showToast('Yield calc is for Property listings'); return; }
    if(!r.ok){ showToast('Yield calculation failed'); return; }
    let d=await r.json();
    if(d.status==='needs_input'){
      const ask=d.need==='rent'?'Enter the expected MONTHLY RENT (no Tuppence charged yet):':'Enter the likely PURCHASE PRICE (no Tuppence charged yet):';
      const e=window.prompt(ask,''); const val=e==null?null:parseFloat(String(e).replace(/[^0-9.]/g,''));
      if(!val||val<=0){ showToast('No figure entered - nothing charged'); return; }
      const p=d.need==='rent'?'&rent=':'&purchase_price=';
      r=await fetch(BEA_URL+'/listings/'+numId+'/yield-calc?email='+encodeURIComponent(email)+'&tier='+tier+p+val,{method:'POST'});
      if(!r.ok){ showToast('Yield calculation failed'); return; }
      d=await r.json();
      if(d.status==='needs_input'){ showToast('Still missing a figure - nothing charged'); return; }
    }
    res.style.display='block'; if(box) box.style.display='none';
    const band=d.net_cost_band||{};
    res.innerHTML=`<div style="background:#faf5ff;border:1.5px solid #c4b5fd;border-radius:11px;padding:13px 15px;">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px;">
        <div style="background:#fff;border:1px solid #e9d5ff;border-radius:8px;padding:9px;text-align:center;"><div style="font-size:10px;color:#7c3aed;font-weight:600;">GROSS YIELD</div><div style="font-size:22px;font-weight:800;color:#5b21b6;">${d.gross_yield_pct||''}</div></div>
        <div style="background:#fff;border:1px solid #e9d5ff;border-radius:8px;padding:9px;text-align:center;"><div style="font-size:10px;color:#7c3aed;font-weight:600;">NET YIELD EST.</div><div style="font-size:22px;font-weight:800;color:#5b21b6;">${d.net_yield_estimate_pct||''}</div></div>
      </div>
      ${d.gross_formula?`<div style="font-size:11px;color:#374151;margin-bottom:4px;">Workings: ${d.gross_formula}</div>`:''}
      ${d.annual_rent_used?`<div style="font-size:11px;color:#374151;margin-bottom:4px;">Annual rent ${d.annual_rent_used}${d.purchase_price_used?(' on '+d.purchase_price_used+' purchase'):''}.</div>`:''}
      ${band.typical?`<div style="font-size:11px;color:#374151;margin-bottom:4px;">Net assumes ~${band.typical}% costs (${band.components||''}).</div>`:''}
      <div style="font-size:12px;color:#374151;line-height:1.55;margin-bottom:4px;">${d.market_context||''}</div>
      ${d.sa_yield_benchmark?`<div style="font-size:11px;font-weight:600;color:#7c3aed;margin-bottom:4px;">Benchmark: ${d.sa_yield_benchmark}</div>`:''}
      <div style="font-size:10.5px;color:#6b7280;margin-bottom:3px;">Price source: ${d.purchase_price_source||'listing'} | Rent source: ${d.monthly_rent_source||'your figure'}</div>
      <div style="font-size:10px;color:#9ca3af;font-style:italic;">${d.disclaimer||label}</div>
      ${(d.tuppence_remaining!==undefined&&d.tuppence_remaining!==null)?`<div style="font-size:10px;color:#9ca3af;margin-top:3px;">${d.charged?('Charged '+(tier==='2T'?'2T':'1T')+' - '):''}${d.tuppence_remaining}T balance</div>`:''}
    </div>`;
  }catch(e){ showToast('Yield calculation error'); }
}

async function buyerPriceCheck(id) {
  const l = findListing(id);
  if (!l) return;
  const btn = document.getElementById('detail-pc-btn-' + id);
  const res = document.getElementById('detail-pc-result-' + id);
  if (!btn || !res) return;

  // Get buyer email — from localStorage (set by gate login or seller sign-in)
  const buyerEmail = localStorage.getItem('ms_aa_email') || localStorage.getItem('ms_user_email') || '';
  if (!buyerEmail) {
    showToast('Sign in to use AI price check');
    return;
  }

  // Check balance
  let bal = 0;
  try {
    const br = await fetch(BEA_URL + '/tuppence/balance?email=' + encodeURIComponent(buyerEmail));
    if (br.ok) { const bd = await br.json(); bal = bd.balance || 0; }
  } catch(_) {}
  if (bal < 1) {
    showToast('Insufficient Tuppence — top up to use AI price check');
    return;
  }

  if (!confirm('This checks the price against a verified market source. 1T is charged ONLY if we can verify a real price — never for a guess. Proceed?')) return;

  btn.disabled = true;
  btn.querySelector('span:first-child').textContent = '⏳ Checking market…';
  res.style.display = 'none';

  // For BEA listings use numeric id, for demo listings gracefully decline
  const numId = parseInt(String(id).replace('bea_', ''));
  if (isNaN(numId)) {
    showToast('Price check only available on live listings');
    btn.disabled = false;
    btn.querySelector('span:first-child').textContent = '💡 Is this a fair price?';
    return;
  }

  try {
    const r = await fetch(
      BEA_URL + '/listings/' + numId + '/price-check?email=' + encodeURIComponent(buyerEmail),
      { method: 'POST' }
    );
    if (r.status === 402) { showToast('Insufficient Tuppence'); return; }
    if (!r.ok) { showToast('Price check failed'); return; }
    const data = await r.json();

    // ── Three-panel market intelligence card ────────────────────────────────
    // Category-aware panel labels
    const _cat = (l.cat || '').toLowerCase();
    const _panelLocal = _cat === 'property'   ? '🏠 LOCAL PROPERTY MARKET'
                      : _cat === 'cars'        ? '🚗 SA USED CAR MARKET'
                      : _cat === 'adventures'  ? '🌍 LOCAL EXPERIENCE MARKET'
                      : _cat === 'tutors'      ? '📚 SA TUTORING MARKET'
                      : _cat === 'services'    ? '🛠️ SA SERVICES MARKET'
                      :                          '🇿🇦 SA SECOND-HAND MARKET';
    const _panelGlobal = _cat === 'property'  ? '📊 REGIONAL & NATIONAL MARKET'
                       : _cat === 'cars'       ? '📋 BOOK VALUE & NATIONAL'
                       : _cat === 'adventures' ? '🌐 COMPARABLE EXPERIENCES'
                       :                         '🌍 OFFICIAL & GLOBAL PRICES';

    const verdictConfig = {
      fair:          { icon: '✅', label: 'Fair price',        color: '#065f46', bg: '#d1fae5', border: '#6ee7b7' },
      below_market:  { icon: '🔥', label: 'Below market',     color: '#1e40af', bg: '#dbeafe', border: '#93c5fd' },
      above_market:  { icon: '⚠️',  label: 'Above market',    color: '#92400e', bg: '#fef3c7', border: '#fcd34d' },
      cannot_assess: { icon: 'ℹ️',  label: 'Insufficient data',color: '#374151', bg: '#f3f4f6', border: '#d1d5db' },
      below_verified_market: { icon: 'ℹ️', label: 'Below verified market', color: '#92400e', bg: '#fffbeb', border: '#fcd34d' },
    };
    const vc = verdictConfig[data.verdict] || verdictConfig.cannot_assess;

    const lgIcon = data.local_vs_global === 'cheaper_locally'  ? '🇿🇦 Buy locally — cheaper here'
                 : data.local_vs_global === 'cheaper_globally' ? '🌍 Better price globally'
                 : data.local_vs_global === 'similar'          ? '≈ Similar local & global'
                 : '';

    // No verified source for this category — we charged nothing. Show honestly.
    if (data.verdict === 'cannot_verify' || data.charged === false) {
      res.style.display = 'block';
      res.innerHTML = `
        <div style="background:#f3f4f6;border:1.5px solid #d1d5db;border-radius:10px;padding:13px 15px;">
          <div style="display:flex;align-items:center;gap:7px;margin-bottom:5px;">
            <span style="font-size:15px;">ℹ️</span>
            <span style="font-size:12px;font-weight:700;color:#374151;">No verified price — not charged</span>
          </div>
          <div style="font-size:12px;color:#374151;line-height:1.55;">${data.assessment || 'We could not verify a market price for this item, so no Tuppence was charged.'}</div>
          <div style="font-size:10px;color:#9ca3af;margin-top:7px;">0T charged · ${data.tuppence_remaining}T balance</div>
        </div>`;
      btn.style.display = 'none';
      return;
    }
    // Honest provenance label + safety banner (price-integrity fix)
    const _pcSource = data.verified
      ? '✅ Verified market price · TCGPlayer via Scryfall · live FX'
      : 'ℹ️ AI guide only — not a verified price · confirm before buying';
    const _sf = data.safety_flag;
    const _sfBanner = _sf ? `
        <div style="background:#fffbeb;border:1.5px solid #fcd34d;border-radius:10px;padding:12px 14px;">
          <div style="display:flex;align-items:center;gap:7px;margin-bottom:4px;">
            <span style="font-size:16px;">${_sf.level === 'danger' ? '📉' : 'ℹ️'}</span>
            <span style="font-size:12px;font-weight:800;color:#92400e;">${_sf.headline}</span>
          </div>
          <div style="font-size:11px;color:#78350f;line-height:1.5;">${_sf.detail}</div>
        </div>` : '';
    res.style.display = 'block';
    res.innerHTML = `
      <div style="display:flex;flex-direction:column;gap:8px;">
        ${_sfBanner}
        <!-- Panel 1: SA Market -->
        <div style="background:#f0fdf4;border:1.5px solid #86efac;border-radius:10px;padding:12px 14px;">
          <div style="font-size:11px;font-weight:700;color:#15803d;letter-spacing:.04em;margin-bottom:5px;">${_panelLocal}</div>
          <div style="font-size:12px;color:#166534;line-height:1.55;word-wrap:break-word;overflow-wrap:anywhere;">${data.sa_context || data.context}</div>
          ${data.sa_range && data.sa_range !== 'N/A' && data.sa_range !== 'Cannot determine'
            ? `<div style="font-size:12px;font-weight:700;color:#15803d;margin-top:6px;">Range: ${data.sa_range}</div>`
            : ''}
        </div>

        <!-- Panel 2: Assessment -->
        <div style="background:${vc.bg};border:1.5px solid ${vc.border};border-radius:10px;padding:12px 14px;">
          <div style="display:flex;align-items:center;gap:7px;margin-bottom:5px;">
            <span style="font-size:16px;">${vc.icon}</span>
            <span style="font-size:11px;font-weight:700;color:${vc.color};letter-spacing:.04em;">ASSESSMENT${data.asking_price ? ' · Asking ' + data.asking_price : ''}</span>
          </div>
          <div style="font-size:12px;color:#374151;line-height:1.55;word-wrap:break-word;overflow-wrap:anywhere;">${data.assessment || data.context}</div>
        </div>

        <!-- Panel 3: Official / Global -->
        ${data.official_context && data.official_context !== 'N/A'
          ? `<div style="background:#eff6ff;border:1.5px solid #93c5fd;border-radius:10px;padding:12px 14px;">
          <div style="font-size:11px;font-weight:700;color:#1d4ed8;letter-spacing:.04em;margin-bottom:5px;">${_panelGlobal}</div>
          <div style="font-size:12px;color:#1e3a5f;line-height:1.55;word-wrap:break-word;overflow-wrap:anywhere;">${data.official_context}</div>
          ${data.official_range && data.official_range !== 'N/A' && data.official_range !== 'Cannot determine'
            ? `<div style="font-size:12px;font-weight:700;color:#1d4ed8;margin-top:6px;">Range: ${data.official_range}</div>`
            : ''}
          ${lgIcon ? `<div style="font-size:11px;color:#1d4ed8;margin-top:6px;font-weight:600;">${lgIcon}</div>` : ''}
        </div>`
          : ''}

        <div style="font-size:10px;color:#9ca3af;padding:0 2px;">${_pcSource} · ${data.tuppence_remaining}T remaining</div>
      </div>`;
    // Hide the trigger button — result is now shown
    btn.style.display = 'none';
  } catch(e) { showToast('Price check error'); }
  finally {
    if (btn) {
      btn.disabled = false;
      const lbl = btn.querySelector('span:first-child');
      if (lbl) lbl.textContent = '💡 Is this a fair price?';
    }
  }
}
// ── END AI3 ───────────────────────────────────────────────────────────────────

// ── AI4: Buyer Yield Calculator (Session 75) ──────────────────────────────
async function buyerYieldCalc(id) {
  const l = findListing(id);
  if (!l) return;
  const btn = document.getElementById('detail-yield-btn-' + id);
  const res = document.getElementById('detail-yield-result-' + id);
  if (!btn || !res) return;

  const buyerEmail = localStorage.getItem('ms_aa_email') || localStorage.getItem('ms_user_email') || '';
  if (!buyerEmail) {
    showToast('Sign in to use AI yield calculator');
    return;
  }

  let bal = 0;
  try {
    const br = await fetch(BEA_URL + '/tuppence/balance?email=' + encodeURIComponent(buyerEmail));
    if (br.ok) { const bd = await br.json(); bal = bd.balance || 0; }
  } catch(_) {}
  if (bal < 1) {
    showToast('Insufficient Tuppence — top up to use AI yield calculator');
    return;
  }

  if (!confirm('This calculates the real rental yield. 1T is charged ONLY if a yield can be computed (you may be asked for the purchase price or rent). Proceed?')) return;

  btn.disabled = true;
  btn.querySelector('span:first-child').textContent = '⏳ Calculating yield…';
  res.style.display = 'none';

  const numId = parseInt(String(id).replace('bea_', ''));
  if (isNaN(numId)) {
    showToast('Yield calc only available on live listings');
    btn.disabled = false;
    btn.querySelector('span:first-child').textContent = "📈 What's the yield on this?";
    return;
  }

  try {
    const r = await fetch(
      BEA_URL + '/listings/' + numId + '/yield-calc?email=' + encodeURIComponent(buyerEmail),
      { method: 'POST' }
    );
    if (r.status === 402) { showToast('Insufficient Tuppence'); return; }
    if (r.status === 400) { showToast('Yield calc only available for Property listings'); return; }
    if (!r.ok) { showToast('Yield calculation failed'); return; }
    let data = await r.json();

    // Real yields need both purchase price AND rent. If one is missing we were
    // NOT charged — ask for it, then re-run with the figure. Still no charge until
    // a real calculation is produced.
    if (data.status === 'needs_input') {
      const askMsg = data.need === 'rent'
        ? 'Enter the expected MONTHLY RENT (Rand) to calculate the real yield (no Tuppence charged yet):'
        : 'Enter the likely PURCHASE PRICE (Rand) to calculate the real yield (no Tuppence charged yet):';
      const entry = window.prompt(askMsg, '');
      const val = entry == null ? null : parseFloat(String(entry).replace(/[^0-9.]/g, ''));
      if (!val || val <= 0) {
        showToast('No figure entered — nothing charged');
        btn.disabled = false;
        btn.querySelector('span:first-child').textContent = "📈 What's the yield on this?";
        return;
      }
      const param = data.need === 'rent' ? '&rent=' : '&purchase_price=';
      const r2 = await fetch(
        BEA_URL + '/listings/' + numId + '/yield-calc?email=' + encodeURIComponent(buyerEmail) + param + val,
        { method: 'POST' }
      );
      if (!r2.ok) { showToast('Yield calculation failed'); return; }
      data = await r2.json();
      if (data.status === 'needs_input') { showToast('Still missing a figure — nothing charged'); return; }
    }

    res.style.display = 'block';
    res.innerHTML = `
      <div style="background:#faf5ff;border:1.5px solid #c4b5fd;border-radius:10px;padding:13px 15px;">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px;">
          <div style="background:#fff;border-radius:8px;padding:9px;border:1px solid #e9d5ff;text-align:center;">
            <div style="font-size:10px;color:#7c3aed;font-weight:600;letter-spacing:.3px;margin-bottom:2px;">GROSS YIELD</div>
            <div style="font-size:22px;font-weight:800;color:#5b21b6;">${data.gross_yield_pct}</div>
          </div>
          <div style="background:#fff;border-radius:8px;padding:9px;border:1px solid #e9d5ff;text-align:center;">
            <div style="font-size:10px;color:#7c3aed;font-weight:600;letter-spacing:.3px;margin-bottom:2px;">NET YIELD EST.</div>
            <div style="font-size:22px;font-weight:800;color:#5b21b6;">${data.net_yield_estimate_pct}</div>
          </div>
        </div>
        ${data.monthly_rent_estimate && data.monthly_rent_estimate !== 'N/A'
          ? `<div style="font-size:12px;font-weight:600;color:#374151;margin-bottom:6px;">Rent estimate: ${data.monthly_rent_estimate}</div>` : ''}
        <div style="font-size:12px;color:#374151;line-height:1.6;margin-bottom:6px;">${data.market_context}</div>
        <div style="font-size:11px;font-weight:600;color:#7c3aed;margin-bottom:6px;">Benchmark: ${data.sa_yield_benchmark}</div>
        ${data.purchase_price_used && data.monthly_rent_used
          ? `<div style="font-size:11px;color:#374151;margin-bottom:4px;">Computed from ${data.purchase_price_used} purchase · ${data.monthly_rent_used}/month · net assumes ${data.net_cost_assumption_pct} costs</div>` : ''}
        <div style="font-size:10px;color:#9ca3af;">✅ Calculated figure (not an AI guess) · ${data.tuppence_remaining}T remaining · not financial advice</div>
      </div>`;
    btn.style.display = 'none';
  } catch(e) { showToast('Yield calculation error'); }
  finally {
    if (btn) {
      btn.disabled = false;
      const lbl = btn.querySelector('span:first-child');
      if (lbl) lbl.textContent = "📈 What’s the yield on this?";
    }
  }
}
// ── END AI4 ───────────────────────────────────────────────────────────────────

// ── AI5: Seller Batch Cards flow (Session 75) ─────────────────────────────
let _sbBatchPhotos  = [];   // [{dataUrl}]
let _sbBatchDrafts  = [];   // sanitised draft objects from BEA
let _sbBatchChecked = [];   // bool array — which drafts to publish

function sbStartBatchCards() {
  // Reset state
  _sbBatchPhotos  = [];
  _sbBatchDrafts  = [];
  _sbBatchChecked = [];
  const prev = document.getElementById('sb-batch-preview');
  if (prev) prev.innerHTML = '';
  const res = document.getElementById('sb-batch-results');
  if (res) res.innerHTML = '';
  const pw = document.getElementById('sb-batch-publish-wrap');
  if (pw) pw.style.display = 'none';
  const btn = document.getElementById('sb-batch-analyse-btn');
  if (btn) btn.style.display = 'none';
  // Make sure Collectors is set
  if (!sbState.cat) sbState.cat = 'Collectors';
  sbGoStep('batch');
}

function sbHandleBatchPhotos(e) {
  const files = Array.from(e.target.files || []).slice(0, 10);
  if (!files.length) return;
  _sbBatchPhotos = [];
  const prev = document.getElementById('sb-batch-preview');
  prev.innerHTML = '<div style="font-size:11px;color:#7c3aed;width:100%;margin-bottom:4px;">Processing ' + files.length + ' photo(s)…</div>';
  let done = 0;
  files.forEach((file, idx) => {
    const reader = new FileReader();
    reader.onload = ev => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const MAX = 800;
        let w = img.width, h = img.height;
        if (w > MAX) { h = Math.round(h * MAX / w); w = MAX; }
        if (h > MAX) { w = Math.round(w * MAX / h); h = MAX; }
        canvas.width = w; canvas.height = h;
        canvas.getContext('2d').drawImage(img, 0, 0, w, h);
        _sbBatchPhotos[idx] = { dataUrl: canvas.toDataURL('image/jpeg', 0.82) };
        done++;
        if (done === files.length) {
          _sbBatchPhotos = _sbBatchPhotos.filter(Boolean);
          _sbRenderBatchPreviews();
          const btn = document.getElementById('sb-batch-analyse-btn');
          if (btn) btn.style.display = _sbBatchPhotos.length ? 'block' : 'none';
        }
      };
      img.src = ev.target.result;
    };
    reader.readAsDataURL(file);
  });
  e.target.value = '';
}

function _sbRenderBatchPreviews() {
  const prev = document.getElementById('sb-batch-preview');
  if (!prev) return;
  prev.innerHTML = _sbBatchPhotos.map((p, i) => `
    <div style="position:relative;display:inline-block;">
      <img src="${p.dataUrl}" style="width:72px;height:72px;object-fit:cover;border-radius:8px;border:2px solid #c4b5fd;display:block;">
      <button onclick="_sbBatchPhotos.splice(${i},1);_sbRenderBatchPreviews();document.getElementById('sb-batch-analyse-btn').style.display=_sbBatchPhotos.length?'block':'none';"
        style="position:absolute;top:-6px;right:-6px;width:20px;height:20px;border-radius:50%;background:#ef4444;color:#fff;border:none;font-size:11px;cursor:pointer;display:flex;align-items:center;justify-content:center;line-height:1;">×</button>
    </div>`).join('') + (_sbBatchPhotos.length ? `<div style="font-size:11px;color:#7c3aed;width:100%;margin-top:4px;">${_sbBatchPhotos.length} card(s) ready</div>` : '');
}

async function sbRunBatchAnalysis() {
  const btn = document.getElementById('sb-batch-analyse-btn');
  const res = document.getElementById('sb-batch-results');
  if (!_sbBatchPhotos.length) { showToast('Add at least one card photo'); return; }

  const sellerEmail = localStorage.getItem('ms_aa_email') || '';
  if (!sellerEmail) { showToast('Sign in to use AI batch listing'); return; }

  // Balance check
  let bal = 0;
  try {
    const br = await fetch(BEA_URL + '/tuppence/balance?email=' + encodeURIComponent(sellerEmail));
    if (br.ok) { const bd = await br.json(); bal = bd.balance || 0; }
  } catch(_) {}
  if (bal < 1) {
    showToast('Need at least 2T — top up in your Wallet');
    return;
  }
  if (!confirm('This will use 2T to analyse ' + _sbBatchPhotos.length + ' card photo(s) with AI. Proceed?')) return;

  btn.disabled = true;
  btn.textContent = '⏳ Identifying cards…';
  res.innerHTML = '<div style="text-align:center;padding:20px;font-size:13px;color:#7c3aed;">⏳ Claude is reading your cards…</div>';

  const city   = (activeCity && activeCity.name) || localStorage.getItem('ms_city') || 'Pretoria';
  const suburb = (activeSuburb && activeSuburb.name) || '';

  try {
    const r = await fetch(BEA_URL + '/listings/batch-cards', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        images:       _sbBatchPhotos.map(p => p.dataUrl),
        city,
        suburb:       suburb || null,
        seller_email: sellerEmail,
      })
    });
    if (r.status === 402) { showToast('Insufficient Tuppence'); res.innerHTML = ''; return; }
    if (!r.ok) { showToast('Analysis failed — try again'); res.innerHTML = ''; return; }
    const data = await r.json();
    _sbBatchDrafts  = data.drafts || [];
    _sbBatchChecked = _sbBatchDrafts.map(() => true);

    if (!_sbBatchDrafts.length) {
      res.innerHTML = '<div style="text-align:center;padding:20px;font-size:13px;color:#ef4444;">No listings could be generated — try clearer photos.</div>';
      return;
    }

    _sbRenderBatchDrafts(data.tuppence_remaining);

    const pw = document.getElementById('sb-batch-publish-wrap');
    const rl = document.getElementById('sb-batch-ready-label');
    if (pw) pw.style.display = 'block';
    if (rl) rl.textContent = '✓ ' + _sbBatchDrafts.length + ' listing draft(s) ready';

    btn.style.display = 'none';   // hide analyse btn now results are shown

  } catch(e) { showToast('Batch analysis error'); res.innerHTML = ''; }
  finally { btn.disabled = false; btn.textContent = '✨ Analyse Cards (2T)'; }
}

const _sbConditionLabels = { mint:'Mint', near_mint:'Near Mint', excellent:'Excellent', good:'Good', fair:'Fair', poor:'Poor' };
const _sbConditionColors = { mint:'#065f46', near_mint:'#1e40af', excellent:'#1e40af', good:'#374151', fair:'#92400e', poor:'#991b1b' };

function _sbRenderBatchDrafts(tuppenceRemaining) {
  const res = document.getElementById('sb-batch-results');
  if (!res) return;
  res.innerHTML = `
    <div style="font-size:12px;font-weight:700;color:#5b21b6;margin-bottom:12px;">
      ✨ ${_sbBatchDrafts.length} card(s) identified · ${tuppenceRemaining}T remaining
    </div>` +
    _sbBatchDrafts.map((d, i) => {
      const cLabel = _sbConditionLabels[d.condition] || d.condition;
      const cColor = _sbConditionColors[d.condition] || '#374151';
      return `
      <div id="sb-bc-card-${i}" style="background:var(--surface-2);border:1.5px solid #c4b5fd;border-radius:12px;padding:14px;margin-bottom:12px;">
        <div style="display:flex;gap:10px;margin-bottom:10px;">
          <img src="${_sbBatchPhotos[i] ? _sbBatchPhotos[i].dataUrl : ''}" style="width:64px;height:64px;object-fit:cover;border-radius:8px;flex-shrink:0;border:1px solid #e9d5ff;">
          <div style="flex:1;min-width:0;">
            <div style="font-size:13px;font-weight:700;color:var(--text);margin-bottom:4px;">${d.title}</div>
            <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-bottom:4px;">
              <span style="font-size:12px;font-weight:700;color:#5b21b6;">${d.price_suggestion}</span>
              <span style="font-size:10px;font-weight:600;color:${cColor};background:#f5f3ff;padding:2px 7px;border-radius:20px;">${cLabel}</span>
            </div>
          </div>
          <label style="display:flex;align-items:flex-start;gap:0;flex-shrink:0;cursor:pointer;">
            <input type="checkbox" id="sb-bc-chk-${i}" checked onchange="_sbBatchChecked[${i}]=this.checked;_sbUpdatePublishBtn();"
              style="width:20px;height:20px;accent-color:#7c3aed;cursor:pointer;margin-top:2px;">
          </label>
        </div>
        <div style="font-size:11px;color:var(--text-2);line-height:1.5;margin-bottom:10px;">${d.description}</div>
        <!-- Editable fields -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
          <div>
            <div style="font-size:10px;font-weight:600;color:#7c3aed;margin-bottom:3px;letter-spacing:.3px;">TITLE</div>
            <input type="text" value="${d.title.replace(/"/g,'&quot;')}" oninput="_sbBatchDrafts[${i}].title=this.value"
              style="width:100%;padding:7px 10px;border-radius:7px;border:1px solid #c4b5fd;background:var(--surface);font-size:12px;color:var(--text);font-family:'Inter',sans-serif;box-sizing:border-box;">
          </div>
          <div>
            <div style="font-size:10px;font-weight:600;color:#7c3aed;margin-bottom:3px;letter-spacing:.3px;">PRICE</div>
            <input type="text" value="${d.price_suggestion.replace(/"/g,'&quot;')}" oninput="_sbBatchDrafts[${i}].price_suggestion=this.value"
              style="width:100%;padding:7px 10px;border-radius:7px;border:1px solid #c4b5fd;background:var(--surface);font-size:12px;color:var(--text);font-family:'Inter',sans-serif;box-sizing:border-box;">
          </div>
        </div>
      </div>`;
    }).join('');
  _sbUpdatePublishBtn();
}

function _sbUpdatePublishBtn() {
  const btn = document.getElementById('sb-batch-publish-btn');
  const rl  = document.getElementById('sb-batch-ready-label');
  const count = _sbBatchChecked.filter(Boolean).length;
  if (btn) {
    btn.textContent = count ? 'Publish ' + count + ' listing' + (count > 1 ? 's' : '') + ' →' : 'Select at least one listing';
    btn.style.opacity = count ? '1' : '.4';
    btn.style.pointerEvents = count ? 'auto' : 'none';
  }
  if (rl) rl.textContent = '✓ ' + count + ' listing(s) selected';
}

async function sbPublishBatchListings() {
  const btn = document.getElementById('sb-batch-publish-btn');
  const sellerEmail = localStorage.getItem('ms_aa_email') || '';
  const sellerName  = localStorage.getItem('ms_aa_name')  || '';
  if (!sellerEmail) { showToast('Sign in to publish'); return; }

  const toPublish = _sbBatchDrafts.filter((_, i) => _sbBatchChecked[i]);
  if (!toPublish.length) { showToast('Select at least one listing'); return; }

  btn.disabled = true;
  btn.textContent = '⏳ Publishing…';

  const city    = (activeCity && activeCity.name) || localStorage.getItem('ms_city') || 'Pretoria';
  const suburb  = (activeSuburb && activeSuburb.name) || '';
  let published = 0, failed = 0;

  for (let i = 0; i < _sbBatchDrafts.length; i++) {
    if (!_sbBatchChecked[i]) continue;
    const d = _sbBatchDrafts[i];
    const photo = _sbBatchPhotos[i];

    // Build FormData matching the standard vision-draft submit path
    // Build FormData for /advert-agent/publish (accepts city + photos)
    const fd = new FormData();
    fd.append('email',    sellerEmail);
    fd.append('category', 'Collectors');
    fd.append('city',     city);
    fd.append('fields',   JSON.stringify({
      title:       d.title,
      desc:        d.description,
      price:       (d.price_suggestion.match(/[0-9]+/)||[''])[0],  // take first number from range e.g. 'R25-R45' → '25'
      suburb:      suburb,
      condition:   d.condition,
      item_type:   'Trading Card',
    }));
    fd.append('coach_output', '');

    // Attach photo if available
    if (photo && photo.dataUrl) {
      try {
        const res = await fetch(photo.dataUrl);
        const blob = await res.blob();
        fd.append('photos', blob, 'card_' + i + '.jpg');
      } catch(_) {}
    }

    try {
      const r = await fetch(BEA_URL + '/advert-agent/publish', { method: 'POST', body: fd });
      if (r.ok) { published++; }
      else if (r.status === 402) {
        showToast('Slot limit reached'); openPlans('aa-publish', true);
        btn.disabled = false; btn.textContent = '⏳ Publish'; break;
      }
      else { console.error('Batch publish failed', r.status, await r.text().catch(()=>'')); failed++; }
    } catch(_) { failed++; }

    btn.textContent = '⏳ Publishing ' + (published + failed) + '/' + toPublish.length + '…';
  }

  btn.disabled = false;

  if (published > 0) {
    const title = document.getElementById('sb-batch-success-title');
    const sub   = document.getElementById('sb-batch-success-sub');
    if (title) title.textContent = published + ' listing' + (published > 1 ? 's' : '') + ' published!';
    if (sub) sub.textContent = published + ' collector card' + (published > 1 ? 's' : '') + ' ' + (published > 1 ? 'are' : 'is') + ' now live on TrustSquare.' + (failed > 0 ? ' (' + failed + ' failed — try again.)' : '');
    sbGoStep('batch-success');
  } else {
    showToast('Publishing failed — check your connection and try again');
    btn.textContent = 'Publish listings →';
  }
}
// ── END AI5 Seller Batch Cards ────────────────────────────────────────────────

function openModal(id){
  pendingIntroId=id;
  pendingLMIntroId=null;
  const l=findListing(id),isCommit=catCfg(l).model==='commit';
  document.getElementById('modal-title').textContent=isCommit?'Request Introduction':'Join Queue';
  document.getElementById('modal-desc').textContent=`${l.title} · ${l.area}`;
  document.getElementById('modal-notice-commit').style.display=isCommit?'flex':'none';
  document.getElementById('modal-notice-queue').style.display=isCommit?'none':'flex';
  document.getElementById('modal-cta-btn').className=`modal-cta ${isCommit?'commit':'queue'}`;
  document.getElementById('modal-cta-btn').textContent=isCommit?'Submit Introduction Request':'Join Queue · 1T on acceptance';
  // Reset tn-deduct-notice to standard text (LM modal changes it to seller-pays)
  const tnNotice = document.querySelector('#intro-modal .tn-deduct-notice');
  if (tnNotice) tnNotice.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg> 1 Tuppence ($2) deducted only on seller acceptance';
  document.getElementById('intro-modal').classList.add('open');
}
function closeMBg(e){if(e.target.id==='intro-modal')document.getElementById('intro-modal').classList.remove('open');}
function submitIntro(){
  if(isOffline()){ showToast('You\'re offline — intro requests need a connection'); return; }
  const name=document.getElementById('m-name').value.trim();
  const email=document.getElementById('m-email').value.trim();
  const msg=document.getElementById('m-msg').value.trim();
  if(!name||!email){showToast('Please fill in your name and email');return;}
  document.getElementById('intro-modal').classList.remove('open');
  document.getElementById('m-name').value='';
  document.getElementById('m-email').value='';
  document.getElementById('m-msg').value='';
  if(pendingLMIntroId!==null){
    // Local Market intro — goes via /local-market/intro (seller-pays model)
    const lmId = pendingLMIntroId;
    pendingLMIntroId = null;
    lmSubmitIntro(lmId, name, email, msg);
  } else if(pendingIntroId!==null){
    const l=findListing(pendingIntroId),isCommit=catCfg(l).model==='commit';
    if(isCommit){l.paused=true;}else{l.queueCount=(l.queueCount||0)+1;}
    addTx(isCommit?'Introduction request sent':'Joined seller queue',l.title,'pending',false);
    showToast(isCommit?'✓ Request sent · listing paused':'✓ Joined queue · waiting for seller');
    renderGrid();
    // Post to BEA if listing is a live listing
    if(BEA_ENABLED && l.isLive) {
      const beaId = parseInt(String(l.id).replace('bea_',''));
      apiPost('/intros', { listing_id: beaId, buyer_email: email, buyer_name: name, message: msg || null });
    }
  }
}

function renderMagicBanner(){
  const area=document.getElementById('magic-banner-area');if(!area)return;
  if(magicLink.active){
    area.innerHTML=`<div class="magic-banner">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M15 7h3a5 5 0 0 1 5 5 5 5 0 0 1-5 5h-3m-6 0H6a5 5 0 0 1-5-5 5 5 0 0 1 5-5h3"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
      <div><h4>Invitation pre-filled for you</h4>
      <p>${magicLink.name?`Welcome, ${magicLink.name}! `:''}Your invite details are ready — just complete the listing below.</p>
      <div class="magic-clear" onclick="clearMagic()">Clear invitation data</div></div>
    </div>`;
    setTimeout(()=>{
      if(magicLink.name){const el=document.getElementById('ob-name');if(el)el.value=magicLink.name;}
      if(magicLink.email){const el=document.getElementById('ob-email');if(el)el.value=magicLink.email;}
      if(magicLink.cat){const el=document.getElementById('ob-cat');if(el)el.value=magicLink.cat;}
    },100);
  } else {area.innerHTML='';}
}
function clearMagic(){magicLink={active:false,name:'',email:'',cat:'',area:''};renderMagicBanner();showToast('Invitation data cleared');}

let obModel = '';
function obSelectModel(m){
  obModel = m;
  document.getElementById('omp-commit').style.outline = m==='commit' ? '2px solid var(--accent)' : '';
  document.getElementById('omp-queue').style.outline  = m==='queue'  ? '2px solid var(--accent)' : '';
}

function submitOnboard(){
  const name=document.getElementById('ob-name').value.trim();
  const biz=document.getElementById('ob-biz').value.trim();
  const email=document.getElementById('ob-email').value.trim();
  const cat=document.getElementById('ob-cat').value;
  if(!name||!email){showToast('Please enter your name and email');return;}
  // Store email + name so AA screens can pre-fill and account picker can display
  sessionStorage.setItem('aa_email', email);
  localStorage.setItem('ms_aa_email', email);
  localStorage.setItem('ms_aa_name', name);
  // Store home city — used to restore activeCity on next page load
  const _homeCity = magicLink.active ? magicLink.area : activeCity.name;
  localStorage.setItem('ms_user_city', _homeCity);
  // Seed seller profile with onboard data and persist
  const profile = {
    ...SELLERS[0],
    headline: biz || `${cat} seller`,
    about: '',
    cat: cat,
    _name: name, _email: email, _biz: biz,
    yearsExp: '',
    region: '',
    stats: [{val:'0',label:'Listings'},{val:'New',label:'Trust Score'},{val:'0',label:'Introductions'},{val:'Free',label:'Plan'}],
    creds: [{icon:'📋',label:'Registered',sub:new Date().toLocaleDateString(),photo:null}],
    tags: [cat],
    avail: [],
  };
  Object.assign(SELLERS[0], profile);
  localStorage.setItem('ms_seller_profile', JSON.stringify(SELLERS[0]));
  showToast(`Welcome, ${name.split(' ')[0]}! Let's build your first listing.`);
  setTimeout(()=>goTo('aa-home'),800);
}

// ── DASHBOARD TABS ────────────────────────────────────────
function switchDashTab(tab){
  ['listings','requests','profile'].forEach(t=>{
    document.getElementById('dtab-'+t).classList.toggle('active', t===tab);
    document.getElementById('dash-panel-'+t).style.display = t===tab ? 'block' : 'none';
  });
  if(tab==='profile') renderProfilePreview();
  if(tab==='requests') renderMyRequests();
}

function renderProfilePreview(){
  const s = SELLERS[0];
  const el = document.getElementById('dash-profile-preview');
  if(!el) return;
  const photo = SELLER_PHOTOS[0];
  const avatarInner = photo
    ? `<img src="${photo}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;" alt="Your photo">`
    : `<span style="font-size:22px;">${CATS[s.cat].icon}</span>`;
  el.innerHTML = `
    <div style="background:var(--navy);border-radius:var(--r);padding:16px;margin-bottom:12px;display:flex;align-items:center;gap:14px;">
      <div style="width:52px;height:52px;border-radius:50%;background:rgba(255,255,255,.15);border:2px solid rgba(255,255,255,.25);display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0;overflow:hidden;">
        ${avatarInner}
      </div>
      <div style="flex:1;">
        <div style="font-size:14px;font-weight:700;color:#fff;margin-bottom:2px;">${s.headline}</div>
        <div style="font-size:11px;color:rgba(255,255,255,.5);">${s.cat} · Your profile is anonymous to buyers</div>
        ${photo?'<div style="font-size:10px;color:rgba(200,135,58,.8);margin-top:3px;font-weight:600;">📷 Photo uploaded · blurred for buyers</div>':'<div style="font-size:10px;color:rgba(255,255,255,.35);margin-top:3px;">No photo yet · tap Edit to add one</div>'}
      </div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px;">
      ${s.stats.map(st=>`
        <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--r-sm);padding:10px;text-align:center;">
          <div style="font-size:18px;font-weight:700;color:var(--navy);font-family:'Inter',sans-serif;">${st.val}</div>
          <div style="font-size:11px;color:var(--text-3);margin-top:2px;font-weight:500;">${st.label}</div>
        </div>`).join('')}
    </div>
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--r-sm);padding:12px;margin-bottom:12px;">
      <div style="font-size:11px;font-weight:700;letter-spacing:.5px;text-transform:uppercase;color:var(--accent);margin-bottom:6px;">Specialisations</div>
      <div style="display:flex;flex-wrap:wrap;gap:6px;">${s.tags.map(t=>`<span class="cv-tag">${t}</span>`).join('')}</div>
    </div>`;
}

// ── CV EDIT ───────────────────────────────────────────────
let editingSeller = null;
let editTags = [];

function openCVEdit(){
  // Edit seller 0 as the "claimed" seller
  editingSeller = JSON.parse(JSON.stringify(SELLERS[0]));
  editTags = [...editingSeller.tags];
  renderCVEditForm();
  goTo('cv-edit');
}

function renderCVEditForm(){
  const s = editingSeller;
  document.getElementById('cv-edit-body').innerHTML = `

    <!-- Profile photo -->
    <div class="cv-edit-sec">
      <div class="cv-edit-sec-title">Profile Photo</div>
      <div class="cv-photo-edit-row">
        <div class="cv-photo-upload" id="cv-photo-circle"
             ondragover="event.preventDefault();this.style.borderColor='var(--accent)'"
             ondragleave="this.style.borderColor=''"
             ondrop="handleCVPhotoDrop(event)">
          <input type="file" id="cv-photo-inp" accept="image/*" onchange="handleCVPhoto(event)">
          ${SELLER_PHOTOS[0]
            ? `<img src="${SELLER_PHOTOS[0]}" id="cv-photo-preview" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;border-radius:50%;">`
            : `<div class="ph-label" id="cv-photo-label">📷<br>Add photo</div>`}
        </div>
        <div style="flex:1;">
          <div style="font-size:13px;font-weight:600;color:var(--navy);margin-bottom:4px;">Anonymous profile photo</div>
          <div style="font-size:12px;color:var(--text-2);line-height:1.55;font-weight:400;">Buyers see a blurred version — your face is never revealed until introduction is accepted. Adds trust without compromising anonymity.</div>
          ${SELLER_PHOTOS[0]?`<button onclick="removeCVPhoto()" style="margin-top:8px;background:none;border:1px solid #fca5a5;border-radius:6px;padding:5px 12px;font-size:11px;cursor:pointer;color:var(--red);font-family:'Inter',sans-serif;">Remove photo</button>`:''}
        </div>
      </div>
      <div class="cv-edit-hint" style="margin-top:8px;">JPG or PNG · under 2MB · Square crops work best</div>
    </div>

    <!-- Headline -->
    <div class="cv-edit-sec">
      <div class="cv-edit-sec-title">Headline</div>
      <div class="cv-edit-field">
        <label>Professional headline</label>
        <input type="text" id="ce-headline" value="${s.headline}" placeholder="e.g. Waterkloof Property Specialist">
        <div class="cv-edit-hint">This is the first thing buyers see on your anonymous profile.</div>
      </div>
    </div>

    <!-- About / Experience -->
    <div class="cv-edit-sec">
      <div class="cv-edit-sec-title">Experience &amp; background</div>
      <div class="cv-edit-field">
        <label>About this seller</label>
        <textarea id="ce-about" placeholder="e.g. Qualified electrician with 15 years\' experience in residential and commercial installations across Pretoria East. Specialise in solar, DB upgrades and fault-finding.">${s.about||''}</textarea>
        <div class="cv-edit-hint">Describe your qualifications, work history and approach. No name, business name, phone or email — these are protected until introduction.</div>
      </div>
      <div class="cv-edit-field" style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
        <div>
          <label>Years of experience</label>
          <input type="number" id="ce-years-exp" value="${s.yearsExp||''}" placeholder="e.g. 12" min="0" max="60" style="max-width:100%;">
        </div>
        <div>
          <label>Service region</label>
          <input type="text" id="ce-region" value="${s.region||''}" placeholder="e.g. Pretoria East">
        </div>
      </div>
      <div class="cv-edit-hint" style="margin-top:2px;">Service region shown to buyers as general area only — exact location revealed after introduction.</div>
    </div>

    <!-- Credentials -->
    <div class="cv-edit-sec">
      <div class="cv-edit-sec-title">Credentials &amp; Qualifications</div>
      <div style="font-size:11px;color:var(--text-3);margin-bottom:12px;">Certificate photos are blurred to buyers until introduction is accepted — they verify your credentials without revealing your identity.</div>
      ${s.creds.map((c,i)=>`
        <div class="cv-cred-edit-row">
          <div class="cv-cred-edit-num">${i+1}</div>
          <div class="cv-cred-edit-fields">
            <input type="text" id="ce-cred-icon-${i}" value="${c.icon||'📋'}" placeholder="Icon (emoji)" style="width:64px;">
            <input type="text" id="ce-cred-label-${i}" value="${c.label||''}" placeholder="e.g. Red Seal Certificate">
            <input type="text" id="ce-cred-sub-${i}" value="${c.sub||''}" placeholder="e.g. DOL Issued · 2019">
            <div class="cred-upload-row">
              <label class="cred-upload-label">
                <input type="file" accept="image/*" onchange="handleCredPhoto(event,${i})">
                📎 ${c.photo?'Replace certificate photo':'Upload certificate photo'}
              </label>
              ${c.photo?`<div style="font-size:11px;color:#16a34a;margin-top:3px;font-weight:600;">✓ Certificate photo uploaded — blurred until introduction</div>`:''}
            </div>
          </div>
        </div>`).join('')}
      <div class="cv-edit-hint" style="margin-top:6px;">Use emoji icons like 🏆 📜 🔧 ⚡ to represent each credential type.</div>
    </div>

    <!-- Specialisation tags -->
    <div class="cv-edit-sec">
      <div class="cv-edit-sec-title">Specialisation Tags</div>
      <div class="cv-tags-edit" id="ce-tags-container">
        ${editTags.map((t,i)=>`
          <div class="cv-tag-edit">
            ${t}
            <button class="rm" onclick="removeTag(${i})">×</button>
          </div>`).join('')}
      </div>
      <div class="cv-tag-add">
        <input type="text" id="ce-tag-input" placeholder="Add a tag…" onkeydown="if(event.key==='Enter')addTag()">
        <button onclick="addTag()">Add</button>
      </div>
    </div>

    <!-- Availability -->
    <div class="cv-edit-sec">
      <div class="cv-edit-sec-title">Availability</div>
      ${s.avail.map((a,i)=>`
        <div class="cv-avail-edit-row">
          <input type="text" id="ce-avail-day-${i}" value="${a.day}" placeholder="e.g. Mon–Fri">
          <input type="text" id="ce-avail-time-${i}" value="${a.time}" placeholder="e.g. 08:00–17:00">
        </div>`).join('')}
      <div class="cv-edit-hint">Buyers see this when deciding whether to request an introduction.</div>
    </div>

    <!-- Save button at bottom -->
    <button onclick="saveCVEdit()" style="width:100%;background:var(--accent);color:#fff;border:none;border-radius:50px;padding:14px;font-family:'Syne',sans-serif;font-size:15px;font-weight:700;cursor:pointer;margin-top:4px;">Save Profile Changes</button>
    <div style="height:20px;"></div>
  `;
}

async function handleCredPhoto(e, credIdx){
  const file = e.target.files[0]; if(!file) return;
  showToast('Uploading certificate…');
  let result;
  if(file.size > 2*1024*1024){
    result = await aaCompressImage(file, 1200, 0.8);
  } else {
    result = await new Promise(r=>{ const fr=new FileReader(); fr.onload=ev=>r(ev.target.result); fr.readAsDataURL(file); });
  }
  editingSeller.creds[credIdx].photo = result;
  // Update label + show confirmation in the row
  const row = e.target.closest('.cred-upload-row');
  if(row){
    const lbl = row.querySelector('.cred-upload-label');
    if(lbl) lbl.innerHTML = `<input type="file" accept="image/*" onchange="handleCredPhoto(event,${credIdx})"> 📎 Replace certificate photo`;
    let conf = row.querySelector('.cred-photo-confirm');
    if(!conf){ conf=document.createElement('div'); conf.className='cred-photo-confirm'; row.appendChild(conf); }
    conf.style.cssText='font-size:11px;color:#16a34a;margin-top:3px;font-weight:600;';
    conf.textContent='✓ Certificate photo uploaded — blurred until introduction';
  }
  showToast('Certificate photo saved');
}

async function handleCVPhotoDrop(e) {
  e.preventDefault();
  const circle = document.getElementById('cv-photo-circle');
  if (circle) circle.style.borderColor = '';
  const file = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
  if (!file || !file.type.startsWith('image/')) { showToast('Please drop an image file'); return; }
  // Reuse existing upload logic by forwarding as a synthetic event
  await handleCVPhoto({ target: { files: [file] } });
}

async function handleCVPhoto(e){
  const file = e.target.files[0]; if(!file) return;
  let result;
  if (file.size > 2*1024*1024) {
    showToast('Compressing photo…');
    result = await aaCompressImage(file, 800, 0.7);
  } else {
    result = await new Promise(r => { const fr = new FileReader(); fr.onload = ev => r(ev.target.result); fr.readAsDataURL(file); });
  }
  SELLER_PHOTOS[0] = result;
  try { localStorage.setItem('ms_seller_photo', result); } catch(_){}

  // Upload to BEA so photo persists across devices and browser cache clears
  const sellerEmail = (SELLERS[0] && SELLERS[0]._email) || localStorage.getItem('ms_aa_email') || '';
  if (BEA_ENABLED && sellerEmail) {
    try {
      // Convert base64 dataURL back to a Blob for upload
      const res  = await fetch(result);
      const blob = await res.blob();
      const fd   = new FormData();
      fd.append('file', blob, 'profile.jpg');
      const up = await fetch(BEA_URL + '/users/' + encodeURIComponent(sellerEmail) + '/photo', { method: 'POST', body: fd });
      if (up.ok) {
        const data = await up.json();
        // Store the permanent URL alongside the local copy so we can restore from BEA next time
        try { localStorage.setItem('ms_seller_photo_url', data.photo_url); } catch(_){}
      }
    } catch(_) { /* silent — local copy already set */ }
  }

  // Update circle preview
  const circle = document.getElementById('cv-photo-circle');
  const label  = document.getElementById('cv-photo-label');
  if(label) label.style.display='none';
  // Add or update preview img
  let prev = document.getElementById('cv-photo-preview');
  if(!prev){
    prev = document.createElement('img');
    prev.id = 'cv-photo-preview';
    prev.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;object-fit:cover;border-radius:50%;';
    if(circle) circle.appendChild(prev);
  }
  prev.src = result;
  showToast('✓ Photo uploaded — blurred for buyers');
}

function removeCVPhoto(){
  SELLER_PHOTOS[0] = null;
  localStorage.removeItem('ms_seller_photo');
  localStorage.removeItem('ms_seller_photo_url');
  renderCVEditForm(); // re-render to show empty state
  showToast('Photo removed');
}


function addTag(){
  const inp = document.getElementById('ce-tag-input');
  const val = inp.value.trim();
  if(!val){ showToast('Enter a tag first'); return; }
  if(editTags.includes(val)){ showToast('Tag already added'); return; }
  if(editTags.length >= 10){ showToast('Maximum 10 tags'); return; }
  editTags.push(val);
  inp.value = '';
  refreshTagsUI();
}

function removeTag(i){
  editTags.splice(i,1);
  refreshTagsUI();
}

function refreshTagsUI(){
  const container = document.getElementById('ce-tags-container');
  if(!container) return;
  container.innerHTML = editTags.map((t,i)=>`
    <div class="cv-tag-edit">
      ${t}
      <button class="rm" onclick="removeTag(${i})">×</button>
    </div>`).join('');
}

function saveCVEdit(){
  const s = editingSeller;

  // Collect headline + about + experience fields
  s.headline  = document.getElementById('ce-headline')?.value.trim()   || s.headline;
  s.about     = document.getElementById('ce-about')?.value.trim()      || s.about;
  s.yearsExp  = document.getElementById('ce-years-exp')?.value.trim()  || '';
  s.region    = document.getElementById('ce-region')?.value.trim()     || '';

  // Collect credentials (photos already set on editingSeller.creds[i].photo by handleCredPhoto)
  s.creds.forEach((c,i)=>{
    c.icon  = document.getElementById(`ce-cred-icon-${i}`)?.value.trim()  || c.icon;
    c.label = document.getElementById(`ce-cred-label-${i}`)?.value.trim() || c.label;
    c.sub   = document.getElementById(`ce-cred-sub-${i}`)?.value.trim()   || c.sub;
  });

  // Collect tags
  s.tags = [...editTags];

  // Collect availability
  s.avail.forEach((a,i)=>{
    a.day  = document.getElementById(`ce-avail-day-${i}`)?.value.trim()  || a.day;
    a.time = document.getElementById(`ce-avail-time-${i}`)?.value.trim() || a.time;
  });

  // Write back to SELLERS array and persist
  Object.assign(SELLERS[0], s);
  localStorage.setItem('ms_seller_profile', JSON.stringify(SELLERS[0]));

  showToast('✓ Profile saved');
  goTo('dashboard');
  switchDashTab('profile');
}


let pubImg=null, pubCat='', pubClaimed=false;

// ══════════════════════════════════════════════════════════
// PATH A — NEW SELLER (3 taps to live)
// Session 38 · SELL_FLOW.md v3.0
// ══════════════════════════════════════════════════════════
let paState = { img: null, imgFile: null, cat: '', title: '', price: '' };

function resetPublish(){
  paState = { img: null, imgFile: null, cat: '', title: '', price: '' };
  paShowStep(1);
  // reset photo zone
  const uzd=document.getElementById('pa-uz-default'); if(uzd)uzd.style.display='block';
  const uzp=document.getElementById('pa-uz-preview'); if(uzp)uzp.style.display='none';
  const inp=document.getElementById('pa-img-inp');     if(inp)inp.value='';
  // reset cats
  ['Property','Tutors','Services','Adventures','Collectors','Cars','LocalMarket'].forEach(c=>{
    const el=document.getElementById('pa-cbt-'+c); if(el)el.classList.remove('selected');
  });
  const ti=document.getElementById('pa-title'); if(ti)ti.value='';
  const pi=document.getElementById('pa-price'); if(pi)pi.value='';
  const mn=document.getElementById('pa-model-note'); if(mn)mn.style.display='none';
  const n2=document.getElementById('pa-2-next'); if(n2){n2.style.opacity='.4';n2.style.pointerEvents='none';}
  const n3=document.getElementById('pa-3-next'); if(n3){n3.style.opacity='.4';n3.style.pointerEvents='none';}
  const eu=document.getElementById('pa-eula'); if(eu)eu.checked=false;
  const ba=document.getElementById('pa-block-ack'); if(ba)ba.checked=false;
  const er=document.getElementById('pa-3-err'); if(er)er.style.display='none';
}

function paShowStep(n){
  [1,2,3,'success'].forEach(s=>{
    const el=document.getElementById('pa-'+s); if(el)el.style.display='none';
  });
  const t=document.getElementById('pa-'+n); if(t){t.style.display='block'; window.scrollTo(0,0);}
}

function paGoStep(n){
  if(n===3){
    const t=document.getElementById('pa-title').value.trim();
    if(!t){ showToast('Please enter a title for your listing'); return; }
    if(!paState.cat){ showToast('Please select a category'); return; }
  }
  paShowStep(n);
}

function paHandleImg(e){
  const file=e.target.files[0]; if(!file) return;
  const r=new FileReader();
  r.onload=ev=>{
    const img=new Image();
    img.onload=()=>{
      const MAX=1200,Q=0.80;
      let w=img.width,h=img.height;
      if(w>MAX||h>MAX){const s=Math.min(MAX/w,MAX/h);w=Math.round(w*s);h=Math.round(h*s);}
      const c=document.createElement('canvas'); c.width=w; c.height=h;
      c.getContext('2d').drawImage(img,0,0,w,h);
      paState.img=c.toDataURL('image/jpeg',Q);
      paState.imgFile=file;
      document.getElementById('pa-uz-img').src=paState.img;
      document.getElementById('pa-uz-default').style.display='none';
      document.getElementById('pa-uz-preview').style.display='block';
    };
    img.src=ev.target.result;
  };
  r.readAsDataURL(file);
}

function paClearImg(e){
  e.stopPropagation();
  paState.img=null; paState.imgFile=null;
  document.getElementById('pa-uz-default').style.display='block';
  document.getElementById('pa-uz-preview').style.display='none';
  document.getElementById('pa-img-inp').value='';
}

function paSelCat(cat){
  paState.cat=cat;
  ['Property','Tutors','Services','Adventures','Collectors','Cars','LocalMarket'].forEach(c=>{
    const el=document.getElementById('pa-cbt-'+c);
    if(el) el.classList.toggle('selected',c===cat);
  });
  const mn=document.getElementById('pa-model-note');
  mn.style.display=(cat==='Property')?'block':'none';
  paCheckStep2();
}

function paCheckStep2(){
  const title=(document.getElementById('pa-title')||{}).value||'';
  const ok=paState.cat && title.trim();
  const btn=document.getElementById('pa-2-next');
  if(btn){btn.style.opacity=ok?'1':'.4'; btn.style.pointerEvents=ok?'auto':'none';}
}

function paCheckStep3(){
  const eu=(document.getElementById('pa-eula')||{}).checked;
  const ba=(document.getElementById('pa-block-ack')||{}).checked;
  const name=(document.getElementById('pa-name')||{}).value||'';
  const email=(document.getElementById('pa-email')||{}).value||'';
  const ok=eu&&ba&&name.trim()&&email.includes('@');
  const btn=document.getElementById('pa-3-next');
  if(btn){btn.style.opacity=ok?'1':'.4'; btn.style.pointerEvents=ok?'auto':'none';}
}

async function paDoPublish(){
  if(isOffline()){ showToast('You\'re offline — publishing needs a connection'); return; }
  const name=document.getElementById('pa-name').value.trim();
  const email=document.getElementById('pa-email').value.trim();
  const city=document.getElementById('pa-city').value.trim()||activeCity.name;
  const title=document.getElementById('pa-title').value.trim();
  const price=document.getElementById('pa-price').value.trim();
  const cat=paState.cat;
  const errEl=document.getElementById('pa-3-err');
  const btn=document.getElementById('pa-3-next');

  if(!name||!email||!title||!cat){
    errEl.textContent='Please fill in all required fields.'; errEl.style.display='block'; return;
  }

  btn.textContent='Publishing…'; btn.style.opacity='.7'; btn.style.pointerEvents='none';
  errEl.style.display='none';

  try {
    // 1. Register user (POST /users)
    if(BEA_ENABLED){
      await apiPost('/users',{
        name, email,
        city: city,
        geo_city_id: activeCity.id||null,
        ai_sessions: 3        // 3 free AI sessions on first listing
      });
    }
    // 2. Create listing (POST /listings)
    let listingId=null;
    if(BEA_ENABLED){
      const res=await apiPost('/listings',{
        title, price:price||'POA', category:cat,
        city: activeCity.name,
        area:(activeSuburb&&activeSuburb.name)||activeCity.name,
        suburb:(activeSuburb&&activeSuburb.name)||activeCity.name,
        geo_city_id:activeCity.id||null,
        description:'',
        seller_email:email,
        listing_status:'live'
      });
      if(res&&res.id) listingId=res.id;
    }
    // 3. Upload photo if provided
    if(BEA_ENABLED && paState.img && listingId){
      const fd=new FormData();
      const blob=await (await fetch(paState.img)).blob();
      fd.append('file',blob,'photo.jpg');
      fd.append('listing_id',listingId);
      await fetch(BEA_URL+'/listings/photo',{method:'POST',headers:{'X-Api-Key':API_KEY},body:fd}).catch(()=>{});
    }
    // 4. Store email for returning seller recognition
    localStorage.setItem('ms_aa_email',email);
    localStorage.setItem('ms_aa_name',name);
    // 5. Show success
    const st=document.getElementById('pa-success-title');
    if(st) st.textContent=`"${title}" is live on TrustSquare.`;
    paShowStep('success');
    showToast('✓ You\'re live!');
    loadLiveListings();
  } catch(err){
    errEl.textContent='Something went wrong — please try again.'; errEl.style.display='block';
    btn.textContent='List now →'; btn.style.opacity='1'; btn.style.pointerEvents='auto';
  }
}

// ══════════════════════════════════════════════════════════
// SELLER ONBOARDING FUNNEL — magic link flow
// sobInit() called immediately after goTo('seller-onboard')
// State: sobState holds email, drafts[], selectedTier
// ══════════════════════════════════════════════════════════

let sobState = {
  email: '',
  name: '',
  cat: '',
  city: '',
  drafts: [],          // [{id, title, price, category}] from GET /listings/mine
  selectedTier: 'free' // 'free' | 'starter' | 'premium'
};

function sobGoPhase(n) {
  document.querySelectorAll('.sob-phase').forEach(el => el.classList.remove('sob-active'));
  const phase = document.getElementById('sob-p' + n);
  if (phase) phase.classList.add('sob-active');
  // Re-label step pills for guided-screen arrivals so numbering is continuous (4 of 5, 5 of 5)
  if (sobState._cameFromGuided) {
    const p2pill = document.querySelector('#sob-p2 .sob-step-pill');
    const p3pill = document.querySelector('#sob-p3 .sob-step-pill');
    if (p2pill) p2pill.textContent = 'Step 4 of 5';
    if (p3pill) p3pill.textContent = 'Step 5 of 5';
  } else {
    const p2pill = document.querySelector('#sob-p2 .sob-step-pill');
    const p3pill = document.querySelector('#sob-p3 .sob-step-pill');
    if (p2pill) p2pill.textContent = 'Step 2 of 3';
    if (p3pill) p3pill.textContent = 'Step 3 of 3';
  }
  // Reset EULA scroll gate whenever entering Phase 3
  if (n === 3) sobResetEulaGate();
  // Phase 2 back button: seal backward navigation for guided arrivals
  if (n === 2) {
    const bkNormal  = document.getElementById('sob-p2-bk-normal');
    const bkGuided  = document.getElementById('sob-p2-bk-guided');
    if (sobState._cameFromGuided) {
      if (bkNormal) bkNormal.style.display = 'none';
      if (bkGuided) bkGuided.style.display = 'inline';
    } else {
      if (bkNormal) bkNormal.style.display = '';
      if (bkGuided) bkGuided.style.display = 'none';
    }
  }
  window.scrollTo(0, 0);
}

async function sobContinueFromTier() {
  const tier = sobState.selectedTier;
  if (tier === 'free') {
    // Free tier — no payment needed, go straight to EULA
    sobGoPhase(3);
    return;
  }
  // Paid tier — redirect to Paystack
  const email = sobState.email;
  if (!email) { showToast('Session expired — please re-open your magic link.'); return; }

  const btn = document.getElementById('sob-p2-next');
  if (btn) { btn.disabled = true; btn.textContent = 'Redirecting…'; }

  // Persist sobState so we can restore it after Paystack redirect
  try {
    sessionStorage.setItem('sob_resume', JSON.stringify({
      email: sobState.email,
      name:  sobState.name,
      cat:   sobState.cat,
      city:  sobState.city,
      selectedTier: sobState.selectedTier,
      drafts: sobState.drafts,
    }));
  } catch(_) {}

  try {
    const callbackUrl = encodeURIComponent(
      window.location.origin + window.location.pathname + '?ps_sub_return=1'
    );
    const url = BEA_URL + '/payment/seller-subscription/initialize'
      + '?email=' + encodeURIComponent(email)
      + '&tier='  + encodeURIComponent(tier)
      + '&callback_url=' + callbackUrl;
    const res  = await fetch(url, { method: 'POST' });
    const data = await res.json();
    if (data.authorization_url) {
      window.location.href = data.authorization_url;
    } else {
      showToast('Payment setup failed — please try again.');
      if (btn) { btn.disabled = false; btn.textContent = 'Continue →'; }
    }
  } catch(e) {
    showToast('Payment error — please try again.');
    if (btn) { btn.disabled = false; btn.textContent = 'Continue →'; }
  }
}

function sobSelTier(tier) {
  sobState.selectedTier = tier;
  ['free','starter','premium'].forEach(t => {
    const card = document.getElementById('sob-tier-' + t);
    if (!card) return;
    card.classList.toggle('selected', t === tier);
    // Update selected badge visibility
    const badge = card.querySelector('[style*="Selected"]');
    if (badge) badge.style.display = t === tier ? '' : 'none';
  });
}

function sobCheckEula() {
  const eula = document.getElementById('sob-eula-chk');
  const content = document.getElementById('sob-content-chk');
  const btn = document.getElementById('sob-p3-next');
  if (btn) btn.disabled = !(eula && eula.checked && content && content.checked);
}

function sobEulaScroll() {
  const box = document.getElementById('sob-eula-scroll');
  if (!box) return;
  // Unlock when within 40px of bottom
  const atBottom = box.scrollTop + box.clientHeight >= box.scrollHeight - 40;
  if (atBottom) {
    box.classList.add('eula-read');
    const cue     = document.getElementById('sob-eula-scroll-cue');
    const confirm = document.getElementById('sob-eula-confirm');
    if (cue)     cue.style.display     = 'none';
    if (confirm) confirm.style.display = 'block';
  }
}

function sobResetEulaGate() {
  // Reset scroll gate when entering Phase 3
  const box     = document.getElementById('sob-eula-scroll');
  const cue     = document.getElementById('sob-eula-scroll-cue');
  const confirm = document.getElementById('sob-eula-confirm');
  if (box)     { box.scrollTop = 0; box.classList.remove('eula-read'); }
  if (cue)     cue.style.display     = 'block';
  if (confirm) confirm.style.display = 'none';
  // Uncheck boxes
  ['sob-eula-chk','sob-content-chk'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.checked = false;
  });
  sobCheckEula();
}

async function sobInit() {
  // Read magic link state populated by the URL parser
  // If _skipPreview is set (coming from guided-onboard), go straight to phase 2
  const skipPreview = !!sobState._skipPreview;
  const cameFromGuided = !!sobState._cameFromGuided; // preserve across init
  sobState.email = sobState.email || magicLink.email || '';
  sobState.name  = sobState.name  || magicLink.name  || '';
  sobState.cat   = sobState.cat   || magicLink.cat   || '';
  sobState.city  = sobState.city  || magicLink.area  || activeCity.name || '';
  const _seededDrafts = sobState.drafts && sobState.drafts.length ? sobState.drafts : [];
  sobState.selectedTier = 'free';
  sobState._skipPreview = false;
  sobState.drafts = _seededDrafts; // restore seeded drafts — must survive init reset
  sobState._cameFromGuided = cameFromGuided; // restore flag after reset

  // Reset to phase 1 (or 2 if coming from guided screen)
  sobGoPhase(skipPreview ? 2 : 1);

  // Reset tier selection UI
  sobSelTier('free');

  // EULA checkboxes + scroll gate are reset by sobResetEulaGate() when Phase 3 is entered

  const listEl = document.getElementById('sob-draft-list');
  const errEl  = document.getElementById('sob-p1-err');
  if (errEl) errEl.style.display = 'none';

  if (!sobState.email) {
    if (listEl) listEl.innerHTML = '<div style="text-align:center;padding:40px 0;color:#fca5a5;font-size:13px;">No seller email found — please use the link sent to you by TrustSquare.</div>';
    return;
  }

  // Fetch this seller\'s listings (drafts and live)
  // Skip BEA fetch if drafts were already seeded by goHandoff() (guided-onboard path)
  if (!sobState.drafts || !sobState.drafts.length) {
    try {
      const res = await fetch(BEA_URL + '/listings/mine?email=' + encodeURIComponent(sobState.email));
      if (!res.ok) throw new Error('API error ' + res.status);
      const all = await res.json();
      // Show only draft listings (listing_status = 'draft' or null published_at)
      sobState.drafts = all.filter(l => l.listing_status === 'draft' || (!l.published_at && !l.listing_status));
    } catch(e) {
      if (listEl) listEl.innerHTML = '<div style="text-align:center;padding:40px 0;color:#fca5a5;font-size:13px;">Could not load your listing — please check your connection and try again.</div>';
      return;
    }
  }

  if (!sobState.drafts.length) {
    if (listEl) listEl.innerHTML = '<div style="text-align:center;padding:40px 0;color:rgba(255,255,255,.65);font-size:13px;">No draft listings found for this account.<br>Please contact TrustSquare support.</div>';
    return;

  }

  // ── Returning-seller gate: check EULA + banking status ──────────────────
  // If this seller already has an account, check if they've signed the EULA
  // and if they have banking details on file.
  if (BEA_ENABLED && sobState.email) {
    try {
      const uRes = await fetch(BEA_URL + '/users/' + encodeURIComponent(sobState.email));
      if (uRes.ok) {
        const uData = await uRes.json();
        sobState._eulaSigned    = !!uData.eula_accepted_at;
        sobState._hasBanking    = !!uData.banking_added_at;
        // If EULA not yet signed, jump straight to phase 3 (EULA)
        // and add a note explaining why
        if (!sobState._eulaSigned) {
          const noteEl = document.getElementById('sob-returning-eula-note');
          if (noteEl) noteEl.style.display = 'block';
          sobGoPhase(3);
          return; // skip rendering draft cards — user must sign EULA first
        }
      }
    } catch(e) {}
  }

  // Render draft cards
  if (listEl) {
    listEl.innerHTML = sobState.drafts.map(l => {
      const catIcons = {Property:'🏡',Tutors:'🎓',Services:'⚙️',Adventures:'🧭',Collectors:'🏺',Cars:'🚗',local_market:'🛍️'};
      const icon = catIcons[l.category] || '📋';
      const photoHtml = l.thumb_url || l.medium_url
        ? `<img src="${l.thumb_url || l.medium_url}" alt="${l.title}" style="width:100%;height:100%;object-fit:cover;border-radius:0;">`
        : `<div style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:56px;background:linear-gradient(135deg,#2563aa,#4f8ec9);">${icon}</div>`;
      const price = l.price ? l.price : null;
      const suburb = l.suburb || l.area || sobState.city || '';
      const rawDesc = (l.description || '').replace(/^\[photos:[^\]]*\]/, '').replace(/^\n/, '');
      const hasDesc = rawDesc.trim().length > 0;
      // Placeholder shimmer style
      const ph = 'background:rgba(255,255,255,.08);border-radius:6px;color:transparent;user-select:none;';
      const phLabel = 'font-size:11px;color:rgba(255,255,255,.6);font-style:italic;';
      return `
        <div style="border-radius:16px;overflow:hidden;background:linear-gradient(160deg,#1e2d4a 0%,#22304d 60%,#1e2a3a 100%);box-shadow:0 8px 32px rgba(0,0,0,.3);margin-bottom:8px;">

          <!-- HERO PHOTO -->
          <div style="height:200px;position:relative;overflow:hidden;">
            ${photoHtml}
            <div style="position:absolute;top:10px;left:10px;background:rgba(0,0,0,.65);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border-radius:20px;padding:4px 12px;font-size:10px;font-weight:700;color:#fbbf24;letter-spacing:.5px;text-transform:uppercase;">⏳ Not yet visible to buyers</div>
          </div>

          <!-- SHEET -->
          <div style="padding:16px 16px 8px;background:rgba(255,255,255,.02);">

            <!-- Category + model -->
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
              <span style="font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:rgba(255,255,255,.45);">${icon} ${l.category || ''}</span>
              <span style="font-size:10px;font-weight:700;background:rgba(139,92,246,.2);color:#a78bfa;border-radius:4px;padding:2px 7px;">👥 Soft Queue</span>
            </div>

            <!-- Title -->
            <div style="font-size:20px;font-weight:800;color:#fff;line-height:1.2;margin-bottom:6px;">${l.title || 'Your listing title'}</div>

            <!-- Suburb -->
            <div style="font-size:13px;color:rgba(255,255,255,.65);margin-bottom:14px;">📍 ${suburb}</div>

            <!-- Trust Score block — coloured tier showcase + personal score note -->
            <div style="background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);border-radius:10px;padding:14px;margin-bottom:14px;">
              <div style="font-size:11px;font-weight:700;letter-spacing:.5px;text-transform:uppercase;color:rgba(255,255,255,.65);margin-bottom:10px;">Trust Score tiers</div>
              <div style="display:flex;flex-direction:column;gap:7px;margin-bottom:12px;">
                <div style="display:flex;align-items:center;gap:10px;">
                  <div style="width:36px;height:36px;border-radius:8px;background:#f1f5f9;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:800;color:#64748b;flex-shrink:0;">0</div>
                  <div><div style="font-size:12px;font-weight:700;color:#c8d0da;">New</div><div style="font-size:11px;color:rgba(255,255,255,.6);">Visible to all buyers · no badge</div></div>
                </div>
                <div style="display:flex;align-items:center;gap:10px;">
                  <div style="width:36px;height:36px;border-radius:8px;background:#dbeafe;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:800;color:#1d4ed8;flex-shrink:0;">40</div>
                  <div><div style="font-size:12px;font-weight:700;color:#60a5fa;">Established</div><div style="font-size:11px;color:rgba(255,255,255,.6);">Blue badge · higher buyer confidence</div></div>
                </div>
                <div style="display:flex;align-items:center;gap:10px;">
                  <div style="width:36px;height:36px;border-radius:8px;background:#d1fae5;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:800;color:#065f46;flex-shrink:0;">70</div>
                  <div><div style="font-size:12px;font-weight:700;color:#34d399;">Trusted</div><div style="font-size:11px;color:rgba(255,255,255,.6);">Green badge · priority in search</div></div>
                </div>
                <div style="display:flex;align-items:center;gap:10px;">
                  <div style="width:36px;height:36px;border-radius:8px;background:#fef3c7;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:800;color:#92400e;flex-shrink:0;">90</div>
                  <div><div style="font-size:12px;font-weight:700;color:#fbbf24;">Highly Trusted</div><div style="font-size:11px;color:rgba(255,255,255,.6);">Gold badge · featured placement</div></div>
                </div>
              </div>
              <div style="background:rgba(251,191,36,.08);border:1px solid rgba(251,191,36,.2);border-radius:8px;padding:9px 12px;font-size:11px;color:rgba(255,255,255,.45);line-height:1.5;">
                ✨ Your badge is determined by your personal Trust Score — earned through credentials, verified ID, and successful introductions. The AI Coach will guide you after you go live.
              </div>
            </div>

            <!-- Price block -->
            <div style="background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:10px;padding:12px 14px;margin-bottom:14px;">
              <div style="font-size:10px;font-weight:600;color:rgba(255,255,255,.6);letter-spacing:.5px;text-transform:uppercase;margin-bottom:4px;">Price</div>
              ${price
                ? `<div style="font-size:24px;font-weight:800;color:#fff;">${price}</div>`
                : `<div style="font-size:14px;color:rgba(255,255,255,.25);font-style:italic;">Add a price to your listing</div>`}
            </div>

            <!-- Category chips — placeholder -->
            <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px;">
              <span style="background:rgba(255,255,255,.06);border:1px dashed rgba(255,255,255,.15);border-radius:20px;padding:4px 14px;font-size:12px;color:rgba(255,255,255,.25);font-style:italic;">+ Add subject</span>
              <span style="background:rgba(255,255,255,.06);border:1px dashed rgba(255,255,255,.15);border-radius:20px;padding:4px 14px;font-size:12px;color:rgba(255,255,255,.25);font-style:italic;">+ Add level</span>
              <span style="background:rgba(255,255,255,.06);border:1px dashed rgba(255,255,255,.15);border-radius:20px;padding:4px 14px;font-size:12px;color:rgba(255,255,255,.25);font-style:italic;">+ Location</span>
            </div>

            <!-- About this listing -->
            <div style="margin-bottom:14px;">
              <div style="font-size:13px;font-weight:700;color:rgba(255,255,255,.6);margin-bottom:6px;">About this listing</div>
              ${hasDesc
                ? `<div style="font-size:13px;color:rgba(255,255,255,.55);line-height:1.6;">${rawDesc.slice(0,160)}${rawDesc.length>160?'…':''}</div>`
                : `<div style="font-size:13px;color:rgba(255,255,255,.2);font-style:italic;line-height:1.6;">Your listing description will appear here. The AI Coach can help you write a compelling one after you go live.</div>`}
            </div>

            <!-- Seller profile row — placeholder -->
            <div style="background:rgba(255,255,255,.04);border:1.5px dashed rgba(255,255,255,.12);border-radius:10px;padding:13px 16px;display:flex;align-items:center;gap:12px;margin-bottom:14px;">
              <div style="width:40px;height:40px;border-radius:50%;background:rgba(255,255,255,.08);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">🔒</div>
              <div style="flex:1;">
                <div style="font-size:13px;font-weight:600;color:rgba(255,255,255,.6);">Your seller profile</div>
                <div style="font-size:11px;color:rgba(255,255,255,.2);margin-top:2px;">Credentials · Track record · Identity masked</div>
              </div>
            </div>

            <!-- Anonymity note -->
            <div style="text-align:center;background:rgba(255,255,255,.04);border-radius:10px;padding:12px;margin-bottom:8px;">
              <div style="font-size:16px;margin-bottom:4px;">🔒</div>
              <div style="font-size:12px;font-weight:700;color:rgba(255,255,255,.65);margin-bottom:2px;">Identity protected until introduction</div>
              <div style="font-size:11px;color:rgba(255,255,255,.25);line-height:1.5;">Your name and contact are only revealed after both parties accept</div>
            </div>

          </div>

          <!-- Sticky CTA placeholder -->
          <div style="padding:12px 16px 16px;">
            <div style="width:100%;background:rgba(139,92,246,.25);border:1.5px dashed rgba(139,92,246,.4);border-radius:50px;padding:14px;text-align:center;font-size:14px;font-weight:700;color:rgba(139,92,246,.6);">👥 Join Queue · 1T on acceptance</div>
            <div style="text-align:center;font-size:11px;color:rgba(255,255,255,.2);margin-top:6px;">This is what buyers will tap to connect with you</div>
          </div>

        </div>`;
    }).join('');
  }
}

async function sobGoLive() {
  const btn = document.getElementById('sob-p3-next');
  const errEl = document.getElementById('sob-p3-err');
  if (errEl) errEl.style.display = 'none';
  if (btn) { btn.disabled = true; btn.textContent = 'Going live…'; }

  const email = sobState.email;
  let successCount = 0;
  let failCount = 0;

  // Stamp EULA acceptance once before processing drafts
  if (BEA_ENABLED) {
    await fetch(BEA_URL + '/users/' + encodeURIComponent(email) + '/eula', {
      method: 'POST', headers: { 'X-Api-Key': API_KEY }
    }).catch(() => {});
  }

  for (const draft of sobState.drafts) {
    try {
      // 1. Register seller account (idempotent)
      await fetch(BEA_URL + '/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Api-Key': API_KEY },
        body: JSON.stringify({ email, name: sobState.name, ai_sessions: 3 })
      }).catch(() => {});

      // 2. Publish the draft listing
      const res = await fetch(
        BEA_URL + '/listings/' + draft.id + '/publish?email=' + encodeURIComponent(email),
        { method: 'PUT', headers: { 'X-Api-Key': API_KEY } }
      );
      const resText = await res.text();
      console.warn('sobGoLive publish', draft.id, res.status, resText.slice(0,200));
      if (!res.ok) throw new Error('HTTP ' + res.status + ': ' + resText.slice(0,100));
      successCount++;
    } catch(e) {
      console.error('sobGoLive: failed for listing', draft.id, e.message);
      failCount++;
      // Show the actual error on screen
      if (errEl) {
        errEl.style.display = 'block';
        errEl.style.color = '#fca5a5';
        errEl.textContent = 'Error (draft ' + draft.id + '): ' + e.message;
      }
    }
  }

  if (successCount === 0) {
    if (errEl) {
      errEl.style.display = 'block';
      errEl.style.color = '#fca5a5';
      // Show actual state instead of generic message
      const reason = (sobState.drafts||[]).length === 0
        ? 'No draft found (drafts=0, email=' + (email||'none') + ')'
        : 'Publish failed — see error above';
      errEl.textContent = reason;
    }
    if (btn) { btn.disabled = false; btn.textContent = 'Go live →'; }
    return;
  }

  // Store email so returning seller flows work normally from here
  localStorage.setItem('ms_aa_email', email);
  localStorage.setItem('ms_aa_name', sobState.name);

  // Update success title
  const titleEl = document.getElementById('sob-success-title');
  if (titleEl) {
    const count = successCount;
    const first = sobState.drafts[0];
    titleEl.textContent = count === 1
      ? `"${first.title}" is now live on TrustSquare.`
      : `${count} listings are now live on TrustSquare.`;
  }

  sobGoPhase(4);
  showToast("🎉 You're live on TrustSquare!");
  // Show "View my listing" button if we have a listing id to open
  const viewBtn = document.getElementById('sob-view-listing-btn');
  if (viewBtn && sobState.drafts && sobState.drafts.length) viewBtn.style.display = 'block';
  loadLiveListings(); // refresh buyer feed

  // Show banking nudge if seller has no banking details yet
  if (!sobState._hasBanking) {
    const nudge = document.getElementById('sob-banking-nudge');
    if (nudge) nudge.style.display = 'flex';
  }
}

function sobP2Back() {
  // Only used for normal (non-guided) flow now
  sobGoPhase(1);
}

function sobStartOver() {
  // Guided arrivals: clear flags and go back to Step 1 cleanly
  sobState._cameFromGuided = false;
  sobState._skipPreview = false;
  goTo('guided-onboard');
}

function sobViewMyListing() {
  // Open the first published listing in the detail view
  const first = sobState.drafts && sobState.drafts[0];
  if (first && first.id) {
    goTo('browse');
    setTimeout(() => openDetail(first.id), 300);
  } else {
    goTo('browse');
    showToast('Your listing is live — find it in the marketplace.');
  }
}

function sobAddBanking() {
  // Navigate to dashboard banking section after going live
  goTo('dashboard');
  showToast('Add your banking details in your dashboard settings.');
}

function sobDone() {
  // Navigate to dashboard as a recognised seller
  const email = sobState.email;
  if (email) {
    localStorage.setItem('ms_aa_email', email);
  }
  goTo('dashboard');
  // Trigger dashboard load if the function exists
  if (typeof loadDashboard === 'function') loadDashboard();
}

// ══════════════════════════════════════════════════════════
// GUIDED ONBOARDING — 3-step photo-first flow
// goInit() called by goTo('guided-onboard') via initScreen()
// goState holds listing id, photo dataURL, fields, cat
// ══════════════════════════════════════════════════════════

const GO_CAT_ICONS = {
  Property:'🏡', Tutors:'🎓', Services:'⚙️',
  Adventures:'🧭', Collectors:'🏺', Cars:'🚗', local_market:'🛍️'
};

const GO_CAT_FIELDS = {
  Property:   [{id:'go-title',label:'Listing title',ph:'e.g. 3-bed family home, Waterkloof'},
               {id:'go-price',label:'Asking price (ZAR)',ph:'e.g. 2 500 000',type:'tel'},
               {id:'go-suburb',label:'Suburb',ph:'e.g. Waterkloof Ridge'},
               {id:'go-street_address',label:'Street address (private)',ph:'e.g. 12 Oak Avenue',hint:'Never shown to buyers — used only to calculate distances to nearby schools, shops and hospitals.'},
               {id:'go-beds',label:'Bedrooms',ph:'e.g. 3',type:'number',pair:'go-baths'},
               {id:'go-baths',label:'Bathrooms',ph:'e.g. 2',type:'number',paired:true}],
  Tutors:     [{id:'go-title',label:'Listing title',ph:'e.g. Maths & Science tutor, Gr 10–12'},
               {id:'go-price',label:'Hourly rate (ZAR)',ph:'e.g. 350',type:'tel'},
               {id:'go-subject',label:'Subject(s)',ph:'e.g. Mathematics, Physics'},
               {id:'go-level',label:'Grade / level',ph:'e.g. Grade 10–12'}],
  Services:   [{id:'go-title',label:'Listing title',ph:'e.g. Qualified electrician — Pretoria'},
               {id:'go-price',label:'Call-out rate (ZAR)',ph:'e.g. 850',type:'tel'},
               {id:'go-svctype',label:'Service type',ph:'e.g. Electrical, Plumbing, HVAC'}],
  Adventures: [{id:'go-title',label:'Listing title',ph:'e.g. Luxury Bush Lodge, Limpopo'},
               {id:'go-price',label:'Price (ZAR)',ph:'e.g. 4 500',type:'tel'},
               {id:'go-envtype',label:'Environment',ph:'e.g. Bushveld, Coastal, Mountain'}],
  Cars:       [{id:'go-title',label:'Listing title',ph:'e.g. 2019 Toyota Fortuner 2.4 GD-6'},
               {id:'go-price',label:'Asking price (ZAR)',ph:'e.g. 480 000',type:'tel'},
               {id:'go-suburb',label:'Suburb / area',ph:'e.g. Centurion'}],
  Collectors: [{id:'go-title',label:'Listing title',ph:'e.g. 1960s Hornby O-gauge train set'},
               {id:'go-price',label:'Asking price (ZAR)',ph:'e.g. 38 000',type:'tel'}],
  local_market:[{id:'go-title',label:'Listing title',ph:'e.g. Handmade leather bags'},
                {id:'go-price',label:'Price (ZAR)',ph:'e.g. 450',type:'tel'}]
};

let goState = {
  listingId: null,
  email: '',
  name: '',
  cat: '',
  city: '',
  photoDataUrl: null,   // client-side preview — first photo (used by goPaintCards)
  photoFile: null,      // first File object (legacy single-photo compat)
  photoFiles: [],       // all selected File objects (Session 71 multi-photo)
  photoUploaded: false, // true once primary photo sent to BEA
  visionDraft: null,    // {title, description_draft, suggested_price, tags, ...} from /vision-draft
  visionSkipped: false, // true if seller tapped "Skip photos — describe it instead"
  fields: {}            // {title, price, suburb, beds, baths, description, ...}
};

// ── Init ──────────────────────────────────────────────────────────────────
async function goInit() {
  goState = {
    listingId: null,
    email: magicLink.email || '',
    name:  magicLink.name  || '',
    cat:   magicLink.cat   || '',
    city:  magicLink.area  || activeCity.name || '',
    photoDataUrl: null,
    photoFile: null,
    photoFiles: [],
    photoUploaded: false,
    visionDraft: null,
    visionSkipped: false,
    fields: {},
    _missingShotsLabels: []
  };

  // Normalise category key
  const rawCat = goState.cat;
  if (!GO_CAT_FIELDS[rawCat]) {
    const match = Object.keys(GO_CAT_FIELDS).find(k => k.toLowerCase() === rawCat.toLowerCase());
    if (match) goState.cat = match;
  }

  // Reset Step 1 UI to clean state
  goResetStep1UI();

  // Show Step 1
  goShowStep(1);

  // Seed card UI with magic link data
  goPaintCards();

  // Render Step 2 fields
  goRenderFields();

  // Fetch this seller's first draft listing id
  if (goState.email && BEA_ENABLED) {
    try {
      const res = await fetch(BEA_URL + '/listings/mine?email=' + encodeURIComponent(goState.email));
      if (res.ok) {
        const all = await res.json();
        const drafts = all.filter(l => l.listing_status === 'draft' || (!l.published_at && !l.listing_status));
        if (drafts.length) goState.listingId = drafts[0].id;
      }
    } catch(e) {}
  }

  // Route 2 — no magic link: show category picker, hide upload zone until cat selected
  const catPicker = document.getElementById('go-cat-picker');
  const uploadZone = document.getElementById('go-upload-zone');
  const s1Next    = document.getElementById('go-s1-next');
  if (!magicLink.active) {
    if (catPicker)  catPicker.style.display  = 'block';
    if (uploadZone) uploadZone.style.display = 'none';
    if (s1Next)     s1Next.style.display     = 'none';
    document.querySelectorAll('.go-cat-btn').forEach(b => b.classList.remove('selected'));
  } else {
    if (catPicker)  catPicker.style.display  = 'none';
    if (uploadZone) uploadZone.style.display = 'block';
    if (s1Next)     s1Next.style.display     = '';
  }

  // Show POPIA notice bar if arriving via magic link
  const popiaBar = document.getElementById('go-popia-bar');
  if (popiaBar) popiaBar.style.display = magicLink.active ? 'flex' : 'none';

  // Personalise Step 1 coach bubble
  const c1 = document.getElementById('go-coach-text-1');
  if (c1 && goState.name) {
    c1.innerHTML = '<strong>Hi ' + goState.name.split(' ')[0] + '!</strong> Add 1–12 photos and our AI will write your listing for you — title, description, and a price suggestion. Takes about 15 seconds. ✨';
  }
}

// ── Reset Step 1 UI to clean state (called on init + after skip) ───────────
function goResetStep1UI() {
  const ids = ['go-vision-overlay','go-draft-reveal','go-photo-strip'];
  ids.forEach(id => { const el = document.getElementById(id); if (el) el.style.display = 'none'; });
  const zone = document.getElementById('go-upload-zone');
  if (zone) { zone.style.display = 'block'; zone.onclick = () => document.getElementById('go-file-input').click(); }
  const skip = document.getElementById('go-skip-link');
  if (skip) skip.style.display = 'block';
  const s1Next = document.getElementById('go-s1-next');
  if (s1Next) { s1Next.disabled = true; s1Next.textContent = 'Analyse photos →'; }
  const status = document.getElementById('go-upload-status');
  if (status) status.textContent = '';
  // Always reset file input so re-selecting the same photos fires onchange
  const fileInput = document.getElementById('go-file-input');
  if (fileInput) fileInput.value = '';
}
// ── Step navigation ────────────────────────────────────────────────────────
function goShowStep(n) {
  document.querySelectorAll('.go-screen').forEach(el => el.classList.remove('go-active'));
  const el = document.getElementById('go-s' + n);
  if (el) el.classList.add('go-active');
  // Relabel pills to x of 5 — guided screen is always followed by 2 more SOB steps
  const pill = el ? el.querySelector('.go-step-pill') : null;
  if (pill) pill.textContent = 'Step ' + n + ' of 5';
  window.scrollTo(0, 0);
}

function goNextStep(n) {
  // Session 71: apply vision draft fields before showing Step 2
  if (n === 2 && goState.visionDraft && !goState.visionSkipped) {
    goApplyVisionToStep2();
    goShowStep(2);
    // Pre-populate visible Step 2 inputs from goState.fields
    goPreFillStep2Inputs();
    return;
  }
  goShowStep(n);
  if (n === 3) goPopulateReview();
}

// Pre-fill Step 2 field inputs with values already in goState.fields
function goPreFillStep2Inputs() {
  const keyMap = {
    title:'go-title', price:'go-price', suburb:'go-suburb',
    beds:'go-beds', baths:'go-baths', subject:'go-subject',
    level:'go-level', service_type:'go-svctype', street_address:'go-street_address'
  };
  Object.entries(keyMap).forEach(([key, id]) => {
    const el = document.getElementById(id);
    if (el && goState.fields[key]) el.value = goState.fields[key];
  });
  // Enable Next button if title present
  const nextBtn = document.getElementById('go-s2-next');
  if (nextBtn) nextBtn.disabled = !(goState.fields.title && goState.fields.title.trim().length > 1);
  // Repaint card
  goPaintCards();
  // Trigger market note now that fields are populated
  clearTimeout(window._goMarketNoteTimer);
  window._goMarketNoteTimer = setTimeout(goFetchMarketNote, 600);
}

// ── Category selection (Route 2 — in-app, no magic link) ─────────────────
function goSelectCat(cat) {
  goState.cat = cat;
  // Highlight selected button
  document.querySelectorAll('.go-cat-btn').forEach(b => b.classList.remove('selected'));
  event.currentTarget.classList.add('selected');
  // Show upload zone + Next button now that cat is chosen
  const uploadZone = document.getElementById('go-upload-zone');
  const s1Next     = document.getElementById('go-s1-next');
  if (uploadZone) uploadZone.style.display = 'block';
  if (s1Next)     s1Next.style.display     = '';
  // Seed coach text with category-specific prompt
  const c1 = document.getElementById('go-coach-text-1');
  const icons = {Property:'🏡',Tutors:'🎓',Services:'⚙️',Cars:'🚗',Collectors:'🏺',Adventures:'🧭',local_market:'🛍️'};
  if (c1) c1.innerHTML = '<strong>' + (icons[cat]||'') + ' ' + cat + ' selected!</strong> Add 1–12 photos of the <strong>same item</strong> and AI writes your listing. Buyers are 3× more likely to contact sellers with clear photos.';
  // Show batch nudge for Collectors
  const _batchNudge = document.getElementById('go-coach-batch-nudge');
  if (_batchNudge) _batchNudge.style.display = (cat === 'Collectors') ? 'block' : 'none';
  // Repaint card with chosen category
  goPaintCards();
  // Render Step 2 fields for this category
  goRenderFields();
}

// ── Card painter — keeps both Step 1 and Step 2 cards in sync ─────────────
function goPaintCards() {
  const cat  = goState.cat;
  const icon = GO_CAT_ICONS[cat] || '📋';
  const f    = goState.fields;
  const name = goState.name || 'Your listing';
  const city = goState.city || '';

  const titleText = f.title || name;
  const areaText  = f.suburb ? '📍 ' + f.suburb + (city ? ', ' + city : '') : (city ? '📍 ' + city : '');
  const rawPriceGo = (f.price || '').replace(/^R\s*/i, ''); const priceText = rawPriceGo ? 'R ' + rawPriceGo.replace(/\B(?=(\d{3})+(?!\d))/g, ' ') : '';

  [1, 2].forEach(step => {
    // emoji / photo
    const imgEl   = document.getElementById('go-card-img-' + step);
    const emojiEl = document.getElementById('go-card-emoji-' + step);
    if (imgEl && emojiEl) {
      if (goState.photoDataUrl) {
        imgEl.src = goState.photoDataUrl;
        imgEl.style.display = 'block';
        emojiEl.style.display = 'none';
      } else {
        imgEl.style.display = 'none';
        emojiEl.style.display = 'block';
        emojiEl.textContent = icon;
      }
    }
    // text fields
    const catEl   = document.getElementById('go-card-cat-'   + step);
    const titleEl = document.getElementById('go-card-title-' + step);
    const areaEl  = document.getElementById('go-card-area-'  + step);
    const priceEl = document.getElementById('go-card-price-' + step);
    if (catEl)   catEl.textContent   = icon + ' ' + cat;
    if (titleEl) titleEl.textContent = titleText;
    if (areaEl)  areaEl.textContent  = areaText;
    if (priceEl) {
      if (priceText) {
        priceEl.textContent = priceText;
        priceEl.classList.remove('empty');
      } else {
        priceEl.textContent = 'Price to be added';
        priceEl.classList.add('empty');
      }
    }
  });
}

// ── Photo handling (Session 71 — multi-photo + AI vision) ─────────────────

// Called by the multi-file input onchange
function goHandlePhotos(input) {
  const files = Array.from(input.files || []);
  if (!files.length) return;

  // Cap at 12 photos total (accumulate across picks)
  const existing = goState.photoFiles || [];
  const combined = existing.concat(files).slice(0, 12);
  goState.photoFiles = combined;
  goState.photoFile  = combined[0];  // legacy compat

  // Show thumbnail strip
  goRenderPhotoStrip();

  // Read first photo as dataURL for card preview
  const reader = new FileReader();
  reader.onload = e => {
    goState.photoDataUrl = e.target.result;
    goPaintCards();
  };
  reader.readAsDataURL(combined[0]);

  // Hide upload zone, show strip
  const zone  = document.getElementById('go-upload-zone');
  const strip = document.getElementById('go-photo-strip');
  if (zone)  zone.style.display  = 'none';
  if (strip) strip.style.display = 'block';

  // Enable Analyse button
  const s1Next = document.getElementById('go-s1-next');
  if (s1Next) { s1Next.disabled = false; s1Next.textContent = 'Analyse photos →'; }

  // Update skip link label
  const skip = document.getElementById('go-skip-link');
  if (skip) skip.innerHTML = '<span style="font-size:12px;color:rgba(255,255,255,.6);cursor:pointer;text-decoration:underline;" onclick="goSkipPhotos()">Skip AI — fill in details manually</span>';

  // Reset input value so re-selecting the same files fires onchange again
  // (browsers skip onchange if selection hasn't changed)
  input.value = '';
}

// Render thumbnail strip with delete buttons
function goRenderPhotoStrip() {
  const thumbs = document.getElementById('go-photo-thumbs');
  const label  = document.getElementById('go-photo-count-label');
  if (!thumbs) return;
  thumbs.innerHTML = '';
  goState.photoFiles.forEach((file, idx) => {
    const wrap = document.createElement('div');
    wrap.className = 'go-photo-thumb-wrap';
    const img = document.createElement('img');
    img.className = 'go-photo-thumb' + (idx === 0 ? ' primary' : '');
    img.title = idx === 0 ? 'Primary photo' : 'Photo ' + (idx+1);
    const del = document.createElement('div');
    del.className = 'go-photo-thumb-del';
    del.textContent = '×';
    del.onclick = () => goRemovePhoto(idx);
    const reader = new FileReader();
    reader.onload = e => { img.src = e.target.result; };
    reader.readAsDataURL(file);
    wrap.appendChild(img);
    wrap.appendChild(del);
    thumbs.appendChild(wrap);
  });
  if (label) label.textContent = goState.photoFiles.length + ' photo' + (goState.photoFiles.length !== 1 ? 's' : '') + ' selected';
}

function goRemovePhoto(idx) {
  goState.photoFiles.splice(idx, 1);
  if (goState.photoFiles.length === 0) {
    // Back to upload zone
    goResetStep1UI();
    goState.photoDataUrl = null;
    goState.visionDraft = null;
    goPaintCards();
    return;
  }
  // Update primary photo preview
  goState.photoFile = goState.photoFiles[0];
  const reader = new FileReader();
  reader.onload = e => { goState.photoDataUrl = e.target.result; goPaintCards(); };
  reader.readAsDataURL(goState.photoFiles[0]);
  goRenderPhotoStrip();
  const s1Next = document.getElementById('go-s1-next');
  if (s1Next) { s1Next.disabled = false; }
}

// ── goVisionNext — called by "Analyse photos →" button ─────────────────────
async function goVisionNext() {
  // If draft already revealed → advance to Step 2
  if (goState.visionDraft) {
    goApplyVisionToStep2();
    goNextStep(2);
    return;
  }
  // If skip mode → just advance
  if (goState.visionSkipped) {
    goNextStep(2);
    return;
  }
  // No photos → fall back
  if (!goState.photoFiles.length) {
    goSkipPhotos();
    return;
  }

  // Show vision overlay, hide other zones
  const zone    = document.getElementById('go-upload-zone');
  const strip   = document.getElementById('go-photo-strip');
  const overlay = document.getElementById('go-vision-overlay');
  const reveal  = document.getElementById('go-draft-reveal');
  const skip    = document.getElementById('go-skip-link');
  const s1Next  = document.getElementById('go-s1-next');

  if (zone)    zone.style.display    = 'none';
  if (strip)   strip.style.display   = 'none';
  if (overlay) overlay.style.display = 'block';
  if (reveal)  reveal.style.display  = 'none';
  if (skip)    skip.style.display    = 'none';
  if (s1Next)  { s1Next.disabled = true; s1Next.textContent = 'Analysing…'; }

  // Cycle loading messages
  const msgs = ['Reading your photos…', 'Identifying category…', 'Writing your listing…'];
  let msgIdx = 0;
  const msgEl  = document.getElementById('go-vision-msg');
  const barEl  = document.getElementById('go-vision-bar');
  const msgTimer = setInterval(() => {
    msgIdx = (msgIdx + 1) % msgs.length;
    if (msgEl) msgEl.textContent = msgs[msgIdx];
  }, 5000);

  // Animate progress bar over 38s (server has 45s timeout)
  const BAR_DURATION = 38000;
  const barStart = Date.now();
  const barTimer = setInterval(() => {
    const pct = Math.min(95, ((Date.now() - barStart) / BAR_DURATION) * 100);
    if (barEl) barEl.style.width = pct + '%';
  }, 300);

  // Client-side timeout — 40s
  const timeoutId = setTimeout(() => {
    clearInterval(msgTimer);
    clearInterval(barTimer);
    goVisionFallback('AI analysis timed out. You can fill in the details manually.');
  }, 40000);

  try {
    // Build FormData with all photos
    const fd = new FormData();
    goState.photoFiles.forEach((file, i) => fd.append('photos', file, file.name || 'photo_' + i + '.jpg'));
    fd.append('category_hint', (goState.cat || '').toLowerCase());
    fd.append('seller_email',  goState.email || '');
    fd.append('city',          goState.city  || 'Pretoria');
    fd.append('country_iso2',  'ZA');

    const res = await fetch(BEA_URL + '/listings/vision-draft', { method: 'POST', body: fd });
    clearTimeout(timeoutId);
    clearInterval(msgTimer);
    clearInterval(barTimer);

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      goVisionFallback(err.detail || 'AI analysis failed. Fill in the details manually.');
      return;
    }

    const data = await res.json();
    goState.visionDraft = data.draft;

    // Complete bar animation
    if (barEl) barEl.style.width = '100%';
    if (overlay) overlay.style.display = 'none';

    goRevealDraft(data.draft, data.warnings || [], data.anonymity_scrubbed || false, data.violating_photo_indices || []);

  } catch(e) {
    clearTimeout(timeoutId);
    clearInterval(msgTimer);
    clearInterval(barTimer);
    goVisionFallback('Could not reach AI. Fill in the details manually.');
  }
}

// ── goRevealDraft — populate Zone D from vision response ───────────────────
function goRevealDraft(draft, warnings, anonymityScrubbed, violatingIndices) {
  const reveal = document.getElementById('go-draft-reveal');
  const strip  = document.getElementById('go-photo-strip');
  const skip   = document.getElementById('go-skip-link');
  const s1Next = document.getElementById('go-s1-next');

  // Populate fields
  const titleEl = document.getElementById('go-vision-title');
  const descEl  = document.getElementById('go-vision-desc');
  const priceEl = document.getElementById('go-vision-price');
  const currEl  = document.getElementById('go-vision-currency');
  const tagsEl  = document.getElementById('go-vision-tags');

  if (titleEl) titleEl.value = draft.title || '';
  if (descEl)  descEl.value  = draft.description_draft || '';
  if (priceEl) priceEl.value = draft.suggested_price ? String(draft.suggested_price) : '';
  if (currEl)  currEl.textContent = draft.currency_prefix || 'R';

  // Render tag chips
  if (tagsEl) {
    tagsEl.innerHTML = '';
    (draft.tags || []).forEach(tag => {
      const chip = document.createElement('span');
      chip.className = 'go-tag-chip';
      chip.textContent = tag;
      chip.onclick = () => chip.classList.toggle('removed');
      tagsEl.appendChild(chip);
    });
  }

  // Warnings
  const warnEl = document.getElementById('go-vision-warnings');
  if (warnEl) {
    if (warnings && warnings.length) {
      warnEl.style.display = 'block';
      warnEl.innerHTML = '⚠️ ' + warnings.join('<br>⚠️ ');
    } else {
      warnEl.style.display = 'none';
    }
  }

  // Anonymity notice — shown when AI detected identifying info in specific photos
  // Only the violating photos are removed; clean photos are kept
  const anonEl = document.getElementById('go-anonymity-notice');
  if (anonEl) anonEl.style.display = anonymityScrubbed ? 'block' : 'none';
  if (anonymityScrubbed && violatingIndices && violatingIndices.length) {
    // Remove only the photos at violating indices — keep all others
    const indices = new Set(violatingIndices.map(Number));
    goState.photoFiles = (goState.photoFiles || []).filter((_, i) => !indices.has(i));
    goState.photoFile  = goState.photoFiles[0] || null;
    // Rebuild photoDataUrl from first remaining photo
    if (goState.photoFiles.length) {
      const reader = new FileReader();
      reader.onload = e => { goState.photoDataUrl = e.target.result; goPaintCards(); };
      reader.readAsDataURL(goState.photoFiles[0]);
    } else {
      goState.photoDataUrl = null;
    }
    // Re-render the strip without violating photos
    goRenderPhotoStrip();
    const stripEl = document.getElementById('go-photo-strip');
    if (stripEl) stripEl.style.display = goState.photoFiles.length ? 'block' : 'none';
  } else if (anonymityScrubbed) {
    // No specific indices provided — remove all as fallback
    goState.photoFiles   = [];
    goState.photoFile    = null;
    goState.photoDataUrl = null;
    const stripEl = document.getElementById('go-photo-strip');
    if (stripEl) { stripEl.style.display = 'none'; stripEl.innerHTML = ''; }
  }

  // Confidence bar — Phase 2: gated by missing_shots count (Session 73)
  // Each missing shot reduces displayed confidence by 12.5% (max −37.5% for 3+ shots).
  // Always show bar if confidence would display below 80% after gating.
  const confBar = document.getElementById('go-confidence-bar');
  const confCat = document.getElementById('go-confidence-cat');
  const confPct = document.getElementById('go-confidence-pct');
  const confMsg = document.getElementById('go-confidence-msg');
  const rawConf = draft.category_confidence || 0;
  const missingShotsPreview = (draft.missing_shots || []).length;
  const shotPenalty = Math.min(missingShotsPreview, 3) * 0.125;  // 12.5% per shot, max 3
  const displayConf = Math.max(0, rawConf - shotPenalty);
  if (confBar && displayConf < 0.80) {
    confBar.style.display = 'block';
    if (confCat) confCat.textContent = draft.category || '';
    if (confPct) confPct.textContent = Math.round(displayConf * 100) + '%';
    if (confMsg) {
      if (missingShotsPreview > 0) {
        confMsg.style.display = 'block';
        confMsg.textContent = `Complete your photo set to increase buyer confidence (+${Math.round(shotPenalty * 100)}% available)`;
      } else {
        confMsg.style.display = 'none';
      }
    }
  } else if (confBar) {
    confBar.style.display = 'none';
    if (confMsg) confMsg.style.display = 'none';
  }

  // Missing shots suggestion strip
  const shotsEl = document.getElementById('go-missing-shots');
  const shots = draft.missing_shots || [];
  if (shotsEl) {
    if (shots.length) {
      shotsEl.style.display = 'block';
      shotsEl.innerHTML = `
        <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:rgba(255,255,255,.5);margin-bottom:8px;">📸 Suggested shots to add</div>
        ${shots.map((s, i) => `
          <div class="go-shot-suggestion" onclick="goAddSuggestedShot(${i})" style="display:flex;align-items:flex-start;gap:10px;padding:9px 11px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);border-radius:8px;margin-bottom:6px;cursor:pointer;">
            <div style="font-size:18px;flex-shrink:0;margin-top:1px;">📷</div>
            <div style="flex:1;">
              <div style="font-size:13px;font-weight:600;color:var(--text);">${s.label}</div>
              <div style="font-size:11px;color:rgba(255,255,255,.45);margin-top:2px;line-height:1.4;">${s.reason}</div>
            </div>
            <div style="font-size:11px;color:var(--accent);font-weight:600;flex-shrink:0;align-self:center;">Add +</div>
          </div>`).join('')}
        <div style="font-size:10px;color:rgba(255,255,255,.6);margin-top:4px;text-align:center;">Tap a shot to add it · More photos = more buyer trust</div>`;
      // Store shots on state for the add handler
      goState._missingShotsLabels = shots.map(s => s.label);
    } else {
      shotsEl.style.display = 'none';
    }
  }

  // Update live card preview with vision data
  goState.fields.title = draft.title || '';
  goState.fields.price = draft.suggested_price ? String(draft.suggested_price) : '';
  goPaintCards();

  // Show strip (photo preview) + reveal + adjust footer
  // If anonymity was scrubbed, photos have already been cleared above — keep strip hidden
  if (strip)  strip.style.display  = 'block';
  if (reveal) { reveal.style.display = 'block'; }
  if (skip)   skip.style.display   = 'block';
  if (s1Next) {
    s1Next.disabled = false;
    s1Next.textContent = 'Looks good — next →';
  }

  // Update coach bubble
  const c1 = document.getElementById('go-coach-text-1');
  if (c1) c1.innerHTML = '<strong>✨ AI draft ready!</strong> We\'ve pre-filled your listing from your photos. Edit anything below, then tap <em>Looks good</em> to continue.';

  // Scroll to reveal
  if (reveal) reveal.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── goAddSuggestedShot — open file picker pre-labelled for a suggested shot ─
function goAddSuggestedShot(idx) {
  const label = (goState._missingShotsLabels || [])[idx] || 'Photo';
  // Update coach text to guide the specific shot
  const c1 = document.getElementById('go-coach-text-1');
  if (c1) c1.innerHTML = '<strong>📷 ' + label + '</strong> — add this photo using the button below, then tap Analyse again.';
  // Scroll to upload zone and trigger file picker
  const fileInput = document.getElementById('go-file-input');
  if (fileInput) {
    fileInput.click();
    // Mark the shot as acknowledged (dim the card)
    const cards = document.querySelectorAll('.go-shot-suggestion');
    if (cards[idx]) {
      cards[idx].style.opacity = '0.45';
      cards[idx].style.pointerEvents = 'none';
      const addBtn = cards[idx].querySelector('div[style*="accent"]');
      if (addBtn) addBtn.textContent = '✓ Adding';
    }
  }
}

// ── goVisionFieldUpdate — live card repaint from Zone D edits ──────────────
function goVisionFieldUpdate(field, value) {
  if (!goState.visionDraft) return;
  if (field === 'title')       { goState.visionDraft.title             = value; goState.fields.title = value; }
  if (field === 'description') { goState.visionDraft.description_draft = value; }
  if (field === 'price')       { goState.visionDraft.suggested_price   = value; goState.fields.price = value; }
  goPaintCards();
}

// ── goApplyVisionToStep2 — copy visionDraft into goState.fields before Step 2 ──
function goApplyVisionToStep2() {
  const d = goState.visionDraft;
  if (!d) return;
  // Core fields — always applied
  goState.fields.title       = d.title             || goState.fields.title || '';
  goState.fields.price       = d.suggested_price   ? String(d.suggested_price) : (goState.fields.price || '');
  goState.fields.description = d.description_draft || goState.fields.description || '';
  // Active tags (chips not marked .removed)
  const tagsEl = document.getElementById('go-vision-tags');
  if (tagsEl) {
    const activeTags = Array.from(tagsEl.querySelectorAll('.go-tag-chip:not(.removed)')).map(c => c.textContent);
    if (activeTags.length) goState.fields.tags = activeTags.join(', ');
  }
  // Category-specific fields
  if (d.beds)         goState.fields.beds         = String(d.beds);
  if (d.baths)        goState.fields.baths        = String(d.baths);
  if (d.listing_type) goState.fields.listing_type = d.listing_type;
  if (d.subject)      goState.fields.subject      = d.subject;
  if (d.service_type) goState.fields.service_type = d.service_type;
  if (d.level)        goState.fields.level        = d.level;
  if (d.availability) goState.fields.availability = d.availability;

  // NOTE: Never override goState.cat from vision response.
  // The seller's category comes from their magic link invite — they know what they're selling.
  // Vision is used only to fill in title/description/price/fields, not to decide category.
  // (Fixed Session 71 bug: vision was overriding Collectors → Property)
}

// ── goImproveDescription — inline AI wording improvement ───────────────────
async function goImproveDescription() {
  const descEl   = document.getElementById('go-vision-desc');
  const btn      = document.getElementById('go-improve-btn');
  const statusEl = document.getElementById('go-improve-status');
  if (!descEl || !btn) return;

  const currentDesc = descEl.value.trim();
  if (!currentDesc) { if (statusEl) statusEl.textContent = 'Add a description first.'; return; }

  btn.disabled = true;
  if (statusEl) statusEl.textContent = 'Improving…';

  const title = (goState.visionDraft && goState.visionDraft.title) || goState.fields.title || '';
  const cat   = goState.cat || '';
  const city  = goState.city || 'Pretoria';
  const prompt = 'Rewrite this marketplace listing description to be more compelling and buyer-friendly. Keep it honest, specific, and under 4 sentences. Category: ' + cat + '. City: ' + city + '. Title: ' + title + '. Current description: ' + currentDesc;

  try {
    const res = await fetch(BEA_URL + '/advert-agent/market-note', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: goState.email || '', prompt })
    });
    if (!res.ok) throw new Error('API error');
    const data = await res.json();
    const improved = (data.response || '').trim();
    if (!improved) throw new Error('Empty response');

    // Show old vs new: strike old, show new below
    const oldText = descEl.value;
    descEl.value = improved;
    if (goState.visionDraft) goState.visionDraft.description_draft = improved;
    goState.fields.description = improved;

    // Undo affordance in status
    if (statusEl) {
      statusEl.innerHTML = '✓ Improved · <span style="color:#a78bfa;cursor:pointer;text-decoration:underline;" onclick="goUndoImprove(' + JSON.stringify(oldText) + ')">Undo</span>';
    }
  } catch(e) {
    if (statusEl) statusEl.textContent = 'Improvement failed — try again.';
  }
  btn.disabled = false;
}

function goUndoImprove(oldText) {
  const descEl   = document.getElementById('go-vision-desc');
  const statusEl = document.getElementById('go-improve-status');
  if (descEl) { descEl.value = oldText; goState.fields.description = oldText; if (goState.visionDraft) goState.visionDraft.description_draft = oldText; }
  if (statusEl) statusEl.textContent = '';
}

// ── goVisionFallback — show error + offer skip ────────────────────────────────
function goVisionFallback(msg) {
  const overlay = document.getElementById('go-vision-overlay');
  const strip   = document.getElementById('go-photo-strip');
  const skip    = document.getElementById('go-skip-link');
  const s1Next  = document.getElementById('go-s1-next');
  const status  = document.getElementById('go-upload-status');

  if (overlay) overlay.style.display = 'none';
  if (strip && goState.photoFiles.length) strip.style.display = 'block';
  if (status) status.textContent = msg || 'AI analysis failed.';
  if (skip)   skip.style.display = 'block';
  if (s1Next) {
    s1Next.disabled = false;
    s1Next.textContent = 'Fill in manually →';
    s1Next.onclick = () => goSkipPhotos();
  }
  showToast(msg || 'AI unavailable — fill in the details yourself.', 4000);
}

// ── goSkipPhotos — bypass vision, go straight to Step 2 fields ─────────────
function goSkipPhotos() {
  goState.visionSkipped = true;
  goState.visionDraft   = null;
  const s1Next = document.getElementById('go-s1-next');
  if (s1Next) { s1Next.disabled = false; s1Next.textContent = 'Next →'; s1Next.onclick = () => goNextStep(2); }
  goNextStep(2);
}

// ── Field rendering (Step 2) ───────────────────────────────────────────────
function goRenderFields() {
  const body = document.getElementById('go-fields-body');
  if (!body) return;
  const cat = goState.cat;
  const fieldDefs = GO_CAT_FIELDS[cat] || GO_CAT_FIELDS['Services'];

  let html = '';
  let skipNext = false;
  fieldDefs.forEach((fd, idx) => {
    if (skipNext) { skipNext = false; return; }
    // Check if this field and the next form a pair (beds/baths)
    const nextFd = fieldDefs[idx + 1];
    const isPair = fd.pair && nextFd && nextFd.paired;
    if (isPair) {
      skipNext = true;
      html += `<div class="go-field-row">
        <div class="go-field-group">
          <div class="go-field-label">${fd.label}</div>
          <input class="go-field-input" id="${fd.id}" type="${fd.type||'text'}" placeholder="${fd.ph}" oninput="goFieldUpdate('${fd.id}',this.value)">
        </div>
        <div class="go-field-group">
          <div class="go-field-label">${nextFd.label}</div>
          <input class="go-field-input" id="${nextFd.id}" type="${nextFd.type||'text'}" placeholder="${nextFd.ph}" oninput="goFieldUpdate('${nextFd.id}',this.value)">
        </div>
      </div>`;
    } else {
      const hintHtml = fd.hint ? `<div style="font-size:11px;color:rgba(255,255,255,.65);margin-top:4px;line-height:1.4;">🔒 ${fd.hint}</div>` : '';
      html += `<div class="go-field-group">
        <div class="go-field-label">${fd.label}</div>
        <input class="go-field-input" id="${fd.id}" type="${fd.type||'text'}" inputmode="${fd.type==='tel'||fd.type==='number'?'numeric':'text'}" placeholder="${fd.ph||''}" oninput="goFieldUpdate('${fd.id}',this.value)">
        ${hintHtml}
      </div>`;
    }
  });

  // If no magic link, append name + email fields (Route 2 — in-app Sell+)
  if (!magicLink.active) {
    html += `<div class="go-field-group">
      <div class="go-field-label">Your name <span style="color:#fca5a5">*</span></div>
      <input class="go-field-input" id="go-seller-name" type="text" placeholder="e.g. Jesse Kriel" oninput="goState.name=this.value;goPaintCards();">
    </div>
    <div class="go-field-group">
      <div class="go-field-label">Your email address <span style="color:#fca5a5">*</span></div>
      <input class="go-field-input" id="go-seller-email" type="email" inputmode="email" placeholder="e.g. jesse@example.com" oninput="goState.email=this.value.trim();const _nb=document.getElementById('go-s2-next');if(_nb){const _ok=goState.email.includes('@')&&goState.fields.title&&goState.fields.title.trim().length>1;_nb.disabled=!_ok;}">
      <div style="font-size:11px;color:rgba(255,255,255,.65);margin-top:4px;">🔒 Only used to create your listing — never shared.</div>
    </div>`;
  }

  // Market note area
  html += `<div id="go-market-note" style="display:none;background:rgba(200,135,58,.08);border:1px solid rgba(200,135,58,.25);border-radius:10px;padding:11px 13px;margin-top:4px;margin-bottom:4px;">
    <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:rgba(200,135,58,.7);margin-bottom:4px;">📊 Market note</div>
    <div id="go-market-note-text" style="font-size:12px;color:rgba(255,255,255,.65);line-height:1.55;"></div>
  </div>`;

  body.innerHTML = html;
}

// ── Field update → live card repaint + market note trigger ─────────────────
function goFieldUpdate(fieldId, value) {
  // Map input id to state key
  const keyMap = {
    'go-title':'title','go-price':'price','go-suburb':'suburb',
    'go-street_address':'street_address',
    'go-beds':'beds','go-baths':'baths','go-subject':'subject',
    'go-level':'level','go-svctype':'service_type','go-envtype':'environment_type'
  };
  const key = keyMap[fieldId] || fieldId.replace('go-','');
  goState.fields[key] = value;
  goPaintCards();

  // Enable Next once title (+ email for Route 2) is filled
  const nextBtn = document.getElementById('go-s2-next');
  const _emailOk = magicLink.active || (goState.email && goState.email.includes('@'));
  if (nextBtn) nextBtn.disabled = !(goState.fields.title && goState.fields.title.trim().length > 1 && _emailOk);

  // Update Step 2 coach text live
  const c2 = document.getElementById('go-coach-text-2');
  if (c2 && goState.fields.title) {
    c2.innerHTML = 'Looking good! Keep filling in the details — the card above updates as you type.';
  }

  // Debounce market note
  clearTimeout(window._goMarketNoteTimer);
  window._goMarketNoteTimer = setTimeout(goFetchMarketNote, 900);
}

// ── Market note (AI coach inline) ─────────────────────────────────────────
async function goFetchMarketNote() {
  const cat = goState.cat;
  const f   = goState.fields;
  let prompt = '';

  if (cat === 'Property') {
    if (!f.beds) return;
    prompt = 'In 1 sentence, give a market context note for a ' + (f.beds||'') + '-bed' + (f.baths?', '+f.baths+'-bath':'') + ' property in ' + (f.suburb||goState.city) + ', Pretoria' + (f.price?', asking R'+f.price:'') + '. Mention approximate comparable asking prices. Be specific and brief.';
  } else if (cat === 'Tutors') {
    if (!f.subject) return;
    prompt = 'In 1 sentence, give a market context note for a ' + (f.level||'') + ' ' + f.subject + ' tutor in Pretoria. Mention typical hourly rates. Be specific and brief.';
  } else if (cat === 'Services') {
    if (!f.service_type) return;
    prompt = 'In 1 sentence, give a market context note for a ' + f.service_type + ' in Pretoria. Mention typical call-out rates. Be specific and brief.';
  } else if (cat === 'Cars') {
    if (!f.title) return;
    prompt = 'In 1 sentence, give a market context note for a ' + f.title + (f.price?', asking R'+f.price:'') + ' in Pretoria. Mention typical market value range. Be specific and brief.';
  } else {
    if (!f.title) return;
    prompt = 'In 1 sentence, give a market context note for: ' + f.title + ' in ' + goState.city + '. Mention typical price range. Be specific and brief.';
  }

  const noteDiv  = document.getElementById('go-market-note');
  const noteText = document.getElementById('go-market-note-text');
  if (!noteDiv || !noteText) return;
  noteDiv.style.display = 'block';
  noteText.textContent = 'Getting market data…';

  try {
    if (!BEA_ENABLED) { noteText.textContent = 'Market data unavailable in demo mode.'; return; }
    const res = await fetch(BEA_URL + '/advert-agent/market-note', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({email: goState.email || '', prompt})
    });
    const data = await res.json();
    noteText.textContent = data.response || '';
    // Bubble update
    const c2 = document.getElementById('go-coach-text-2');
    if (c2 && data.response) {
      c2.innerHTML = '<strong>Market insight:</strong> ' + data.response;
    }
  } catch(e) {
    noteDiv.style.display = 'none';
  }
}

// ── Save fields to BEA then go to Step 3 ──────────────────────────────────
async function goSaveAndNext() {
  const btn = document.getElementById('go-s2-next');
  if (btn) { btn.disabled = true; btn.textContent = 'Saving…'; }

  // Route 2 guard: ensure email captured
  if (!magicLink.active && (!goState.email || !goState.email.includes('@'))) {
    if (btn) { btn.disabled = false; btn.textContent = 'Next →'; }
    const emailEl = document.getElementById('go-seller-email');
    if (emailEl) { emailEl.focus(); emailEl.style.borderColor = '#fca5a5'; }
    return;
  }
  // Route 2: also capture name if filled
  if (!magicLink.active) {
    const nameEl = document.getElementById('go-seller-name');
    if (nameEl && nameEl.value.trim()) goState.name = nameEl.value.trim();
  }

  const f = goState.fields;
  if (goState.listingId && goState.email && BEA_ENABLED && f.title) {
    try {
      const body = {};
      if (f.title)          body.title          = f.title;
      if (f.price)          body.price          = f.price;
      if (f.suburb)         body.suburb         = f.suburb;
      if (f.street_address) body.street_address = f.street_address;
      if (f.beds)           body.beds           = parseInt(f.beds) || null;
      if (f.baths)          body.baths          = parseInt(f.baths) || null;
      if (f.subject)        body.subject        = f.subject;
      if (f.level)          body.level          = f.level;
      if (f.service_type)   body.service_type   = f.service_type;
      // Session 71: include AI-generated description and tags if present
      if (f.description)    body.description    = f.description;
      if (f.availability)   body.availability   = f.availability;
      if (f.listing_type)   body.listing_type   = f.listing_type;
      await fetch(
        BEA_URL + '/listings/' + goState.listingId + '?email=' + encodeURIComponent(goState.email),
        { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) }
      );
    } catch(e) {}
  }

  if (btn) { btn.disabled = false; btn.textContent = 'Next →'; }
  goNextStep(3);

  // Fire Step 3 coach AI note
  setTimeout(goStep3Coach, 400);
}

// ── Populate review card (Step 3) ─────────────────────────────────────────
function goPopulateReview() {
  const cat  = goState.cat;
  const icon = GO_CAT_ICONS[cat] || '📋';
  const f    = goState.fields;
  const city = goState.city || '';

  // Photo or emoji
  const revImg   = document.getElementById('go-review-img');
  const revEmoji = document.getElementById('go-review-emoji');
  if (revImg && revEmoji) {
    if (goState.photoDataUrl) {
      revImg.src = goState.photoDataUrl;
      revImg.style.display = 'block';
      revEmoji.style.display = 'none';
    } else {
      revImg.style.display = 'none';
      revEmoji.style.display = 'block';
      revEmoji.textContent = icon;
    }
  }

  const catEl   = document.getElementById('go-review-cat');
  const titleEl = document.getElementById('go-review-title');
  const areaEl  = document.getElementById('go-review-area');
  const priceEl = document.getElementById('go-review-price');
  if (catEl)   catEl.textContent   = icon + ' ' + cat;
  if (titleEl) titleEl.textContent = f.title || goState.name || 'Your listing';
  if (areaEl)  areaEl.textContent  = f.suburb ? '📍 ' + f.suburb + (city?', '+city:'') : (city?'📍 '+city:'');
  if (priceEl) { const rawPrice = (f.price || '').replace(/^R\s*/i, ''); priceEl.textContent = rawPrice ? 'R ' + rawPrice.replace(/\B(?=(\d{3})+(?!\d))/g, ' ') : 'Negotiable'; }
}

// ── Step 3 AI coach note ───────────────────────────────────────────────────
async function goStep3Coach() {
  const c3 = document.getElementById('go-coach-text-3');
  if (!c3 || !BEA_ENABLED) return;
  const name = goState.name ? goState.name.split(' ')[0] : '';
  const cat  = goState.cat;
  const f    = goState.fields;
  const prompt = 'In 1 sentence, congratulate ' + (name||'the seller') + ' on completing their ' + cat + ' listing draft' + (f.title?' titled "'+f.title+'"':'') + ' and encourage them to go live. Be warm, specific, and brief.';
  try {
    const res = await fetch(BEA_URL + '/advert-agent/market-note', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({email: goState.email||'', prompt})
    });
    const data = await res.json();
    if (data.response) c3.innerHTML = data.response + '<br><br><span style="color:rgba(255,255,255,.5);font-size:12px;">Tap below to choose your plan and go live — takes about 2 minutes.</span>';
  } catch(e) {}
}

// ── Anonymity choice handlers ─────────────────────────────────────────────
function goAnonReplace() {
  // Clear violating photos, hide notice, open file picker for replacement
  goState.photoFiles   = [];
  goState.photoFile    = null;
  goState.photoDataUrl = null;
  // Hide the photo strip
  const stripEl = document.getElementById('go-photo-strip');
  if (stripEl) { stripEl.style.display = 'none'; stripEl.innerHTML = ''; }
  // Hide the anonymity notice
  const anonEl = document.getElementById('go-anonymity-notice');
  if (anonEl) anonEl.style.display = 'none';
  // Keep Next disabled until new photos are analysed
  const s1Next = document.getElementById('go-s1-next');
  if (s1Next) { s1Next.disabled = true; s1Next.textContent = 'Analyse photos →'; }
  // Reset file input and open picker
  const fileInput = document.getElementById('go-file-input');
  if (fileInput) { fileInput.value = ''; fileInput.click(); }
  // Show the upload zone again
  const zone = document.getElementById('go-upload-zone');
  if (zone) zone.style.display = 'block';
}

// ── Handoff to seller-onboard funnel ──────────────────────────────────────
async function goHandoff() {
  // Disable the button immediately to prevent double-taps
  const btn = document.querySelector('#go-s3 .go-btn-next');
  if (btn) { btn.disabled = true; btn.textContent = 'Preparing…'; }

  // Set flags BEFORE goTo() — goTo() calls sobInit() synchronously
  sobState._skipPreview    = true;
  sobState._cameFromGuided = true;
  sobState.email = goState.email;
  sobState.name  = goState.name;
  sobState.cat   = goState.cat;
  sobState.city  = goState.city;

  // ── Ensure a BEA draft listing exists before handing off ────────────────
  // sobInit() fetches /listings/mine and needs at least one draft to publish.
  // If goState.listingId is null (new seller, no prior draft), create it now.
  // If it already exists (from goInit() fetch or earlier photo upload), reuse it.
  if (BEA_ENABLED && goState.email) {
    try {
      if (!goState.listingId) {
        // Create draft listing — listing_status='draft' so it won't appear live yet
        const f = goState.fields;
        const body = {
          title:          f.title       || goState.name || 'My listing',
          price:          f.price       || 'POA',
          category:       goState.cat   || 'Services',
          city:           goState.city  || activeCity.name || 'Pretoria',
          area:           f.suburb      || goState.city || activeCity.name || 'Pretoria',
          suburb:         f.suburb      || goState.city || activeCity.name || 'Pretoria',
          geo_city_id:    activeCity.id || null,
          description:    f.description || '',
          seller_email:   goState.email,
          listing_status: 'draft',
        };
        const res = await fetch(BEA_URL + '/listings', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Api-Key': API_KEY },
          body: JSON.stringify(body)
        });
        if (res.ok) {
          const data = await res.json();
          goState.listingId = data.id;
        }
      } else {
        // Draft already exists — patch with latest fields from vision/manual edit
        const f = goState.fields;
        const body = {};
        if (f.title)       body.title       = f.title;
        if (f.price)       body.price       = f.price;
        if (f.description) body.description = f.description;
        if (f.suburb)      body.suburb      = f.suburb;
        if (f.beds)        body.beds        = parseInt(f.beds) || null;
        if (f.baths)       body.baths       = parseInt(f.baths) || null;
        if (f.subject)     body.subject     = f.subject;
        if (f.level)       body.level       = f.level;
        if (f.service_type)body.service_type= f.service_type;
        if (f.listing_type)body.listing_type= f.listing_type;
        if (f.availability)body.availability= f.availability;
        if (Object.keys(body).length) {
          await fetch(
            BEA_URL + '/listings/' + goState.listingId + '?email=' + encodeURIComponent(goState.email),
            { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }
          ).catch(() => {});
        }
      }

      // Upload ALL photos (not just primary) — goState.photoFiles has the full array
      if (goState.listingId && !goState.photoUploaded) {
        const filesToUpload = goState.photoFiles && goState.photoFiles.length
          ? goState.photoFiles
          : (goState.photoFile ? [goState.photoFile] : []);
        for (let pi = 0; pi < filesToUpload.length; pi++) {
          const fd = new FormData();
          fd.append('file', filesToUpload[pi]);
          await fetch(
            BEA_URL + '/listings/' + goState.listingId + '/photo/draft?email=' + encodeURIComponent(goState.email),
            { method: 'POST', body: fd }
          ).catch(() => {});
        }
        if (filesToUpload.length) goState.photoUploaded = true;
      }

      // Seed sobState.drafts directly so sobInit() doesn't need to re-fetch
      if (goState.listingId) {
        const f = goState.fields;
        sobState.drafts = [{
          id:             goState.listingId,
          title:          f.title       || goState.name || 'My listing',
          price:          f.price       || 'POA',
          category:       goState.cat,
          city:           goState.city,
          listing_status: 'draft',
        }];
      }
    } catch(e) {
      // Non-fatal — sobInit() will attempt its own fetch as fallback
      console.warn('goHandoff: draft creation failed', e);
    }
  }

  if (btn) { btn.disabled = false; btn.textContent = 'Take me to the app →'; }
  goTo('seller-onboard');
}

// ══════════════════════════════════════════════════════════
// PATH B — RETURNING SELLER (Full AI-guided flow, B1–B8)
// Session 38 · SELL_FLOW.md v3.0
// ══════════════════════════════════════════════════════════

// State object for the full B path
let sbState = {
  cat: '',           // e.g. 'Property', 'Tutors', 'Services', etc.
  subcat: '',        // e.g. 'adventures_accommodation', 'services_technical'
  gate: '',          // 'agent' | 'private' — Property and Cars only
  fields: {},        // filled structured fields from B3
  description: '',   // B4 draft (edited by seller)
  photos: [],        // [{slot, prompt, dataUrl, caption}]
  selfieUrl: null,   // B6
  signals: {},       // signalId → {status:'skipped'|'declared'|'uploaded', pts:0}
  currentDocSignal: null  // which signal is being acted on in B7
};

// ── Draft save / resume ────────────────────────────────────
function sbDraftKey(){
  const email=localStorage.getItem('ms_aa_email')||'anon';
  return 'sb_draft_'+email;
}

async function sbSaveDraft(step){
  try {
    const draft={
      id: sbDraftKey(),
      step: step||sbState._step||'b3',
      state: {
        cat:sbState.cat, subcat:sbState.subcat, gate:sbState.gate,
        fields:sbState.fields, description:sbState.description,
        selfieUrl:sbState.selfieUrl, signals:sbState.signals
        // photos omitted — dataUrls too large for IDB quota; user re-adds on resume
      },
      saved_at: new Date().toISOString()
    };
    await aaDB.put(draft);
  } catch(e){ console.warn('sbSaveDraft failed',e); }
}

async function sbSaveDraftAndExit(){
  const step=sbState._step||'b7';
  await sbSaveDraft(step);
  showToast('💾 Draft saved — continue from your dashboard anytime');
  goTo('dashboard');
}

async function sbCheckResumeDraft(){
  try {
    const draft=await aaDB.get(sbDraftKey());
    if(!draft||!draft.state||!draft.state.cat) return false;
    const saved=new Date(draft.saved_at);
    const age=Date.now()-saved.getTime();
    if(age>7*24*60*60*1000) { await aaDB.remove(sbDraftKey()); return false; } // expire after 7 days
    // Show resume banner on B1
    const b1footer=document.querySelector('#sb-b1 .pub-footer');
    if(b1footer){
      const banner=document.createElement('div');
      banner.id='sb-draft-banner';
      banner.style.cssText='padding:12px 20px;background:rgba(37,99,235,.07);border-top:1px solid rgba(37,99,235,.15);text-align:center;';
      banner.innerHTML=`<div style="font-size:13px;font-weight:600;color:#2563eb;margin-bottom:6px;">You have an unfinished listing</div>
        <div style="font-size:12px;color:var(--text-3);margin-bottom:10px;">${draft.state.cat} · saved ${saved.toLocaleDateString()}</div>
        <button onclick="sbResumeDraft()" style="background:#2563eb;color:#fff;border:none;border-radius:50px;padding:9px 20px;font-family:'Syne',sans-serif;font-size:13px;font-weight:700;cursor:pointer;margin-right:8px;">Resume listing →</button>
        <button onclick="sbDiscardDraft()" style="background:none;border:1px solid var(--border);border-radius:50px;padding:9px 16px;font-family:'Inter',sans-serif;font-size:12px;cursor:pointer;color:var(--text-3);">Start fresh</button>`;
      b1footer.parentNode.insertBefore(banner, b1footer);
    }
    return true;
  } catch(e){ return false; }
}

async function sbResumeDraft(){
  try {
    const draft=await aaDB.get(sbDraftKey());
    if(!draft) return;
    Object.assign(sbState, draft.state);
    sbState._step=draft.step;
    // Remove banner
    const b=document.getElementById('sb-draft-banner'); if(b)b.remove();
    sbGoStep(draft.step||'b3');
    showToast('Listing resumed from where you left off');
  } catch(e){ showToast('Could not load draft'); }
}

async function sbDiscardDraft(){
  await aaDB.remove(sbDraftKey()).catch(()=>{});
  const b=document.getElementById('sb-draft-banner'); if(b)b.remove();
  showToast('Draft discarded');
}

function sbReset(){
  sbState = { cat:'', subcat:'', gate:'', fields:{}, description:'', photos:[], selfieUrl:null, signals:{}, currentDocSignal:null, _step:'b1' };
  // populate B1 name/email from localStorage
  const name=localStorage.getItem('ms_aa_name')||'';
  const email=localStorage.getItem('ms_aa_email')||'';
  const n1=document.getElementById('sb-b1-name'); if(n1)n1.textContent=name||'Your account';
  const e1=document.getElementById('sb-b1-email'); if(e1)e1.textContent=email;
  // Check for saved draft and show resume banner if found
  sbCheckResumeDraft();
}

function sbClosePath(){
  document.getElementById('sell-account-sheet').classList.remove('open');
  goTo('browse');
}

// ── sbStartPhotoFirst() ───────────────────────────────────────────────────────
// Called from B1 "Start with a photo" card.
// Seeds magicLink with the stored seller identity (if any) so goInit() has
// email/name available even for returning sellers who arrived via Sell+ button.
// Then routes to guided-onboard (the 3-step photo-first flow).
function sbStartPhotoFirst() {
  const email = localStorage.getItem('ms_aa_email') || '';
  const name  = localStorage.getItem('ms_aa_name')  || '';
  // Seed magicLink so goInit() behaves like Route 2 (no magic link) but with
  // identity pre-filled — category picker will show, upload zone will appear
  // after category selection, same as a new seller.
  magicLink = {
    active: false,   // no magic link — show category picker in guided-onboard
    name:   name,
    email:  email,
    cat:    '',
    area:   activeCity.name || ''
  };
  goTo('guided-onboard');
}

// Haiko guidance strip (zero API cost)
var _hkMsgs = {
  b1:       "Hi! I\'m <strong>Haiko</strong> &#8212; pick how you\'d like to list. The photo option is the fastest way to go live.",
  b2:       "<strong>Pick your category</strong> &#8212; this sets the fields and intro model for your listing. Tap the tile that fits best.",
  b2_gate:  "<strong>One quick question</strong> &#8212; are you a registered agent/dealer or a private seller? This determines your compliance badge.",
  b3:       "<strong>Fill in your listing details</strong> &#8212; the more you add, the better the description I\'ll write for you on the next step.",
  b3_ready: "<strong>Looking good!</strong> I\'ll draft your description from these details. Tap <strong>Continue</strong> when ready.",
  b4:       "<strong>I drafted this from your details</strong> &#8212; read it through and edit anything that doesn\'t sound like you. Tap <strong>Looks good</strong> to continue.",
  b5:       "<strong>Add photos for each section</strong> &#8212; tap any slot to add a photo. Listings with 3+ photos get significantly more intro requests.",
  b5_some:  "<strong>Great start on photos!</strong> Add more if you can &#8212; every extra photo boosts your intro requests.",
  b6:       "<strong>Add a profile photo</strong> &#8212; your name stays hidden until both parties accept an intro. Tap <strong>Skip</strong> to come back later.",
  b7:       "<strong>Earn Trust Score signals</strong> &#8212; tick anything that applies now. Add more from your dashboard any time. Tap <strong>Skip</strong> to continue.",
  b7_some:  "<strong>Nice &#8212; every signal helps!</strong> Add as many as apply, then tap <strong>Continue</strong>.",
  b8:       "<strong>Almost there!</strong> Review your listing below &#8212; if it looks right, tap <strong>Publish listing</strong>. You can edit any time from your dashboard.",
  success:  ""
};
function hkSet(key, warn, ok) {
  var strip = document.getElementById('sb-haiko-strip');
  var msg   = document.getElementById('sb-haiko-msg');
  if (!strip || !msg) return;
  var text = _hkMsgs[key] || '';
  if (!text) { strip.style.display = 'none'; return; }
  strip.style.display = 'flex';
  strip.className = 'hk-strip' + (warn ? ' hk-warn' : (ok ? ' hk-ok' : ''));
  msg.innerHTML = text;
}
function hkMove(stepId) {
  var strip = document.getElementById('sb-haiko-strip');
  if (!strip) return;
  var step = document.getElementById('sb-' + stepId);
  if (!step) return;
  var hdr = step.querySelector('.pub-hdr');
  if (hdr && hdr.nextSibling !== strip) hdr.parentNode.insertBefore(strip, hdr.nextSibling);
  strip.style.display = 'flex';
}
function sbGoStep(step){
  ['b1','b2','b3','b4','b5','b6','b7','b8','success','batch','batch-success'].forEach(s=>{
    const el=document.getElementById('sb-'+s); if(el)el.style.display='none';
  });
  const t=document.getElementById('sb-'+step);
  if(t){t.style.display='block'; window.scrollTo(0,0);}

  // Track step and auto-save draft on forward steps (not b1/success/going back)
  const forwardSteps=['b2','b3','b4','b5','b6','b7','b8'];
  if(forwardSteps.includes(step)){
    sbState._step=step;
    sbSaveDraft(step).catch(()=>{});
  }
  if(step==='success'){
    // Published — delete draft
    aaDB.remove(sbDraftKey()).catch(()=>{});
  }

  // Render step-specific content
  if(step==='b3') sbRenderB3();
  if(step==='b4') sbRenderB4();
  if(step==='b5') sbRenderB5();
  if(step==='b7') sbRenderB7();
  if(step==='b8') sbRenderB8Preview();
  hkMove(step); hkSet(step, false, false);
}

// ── B2: category + agent/private gate ─────────────────────
function sbSelCat(cat){
  sbState.cat=cat;
  setTimeout(function(){var g=document.getElementById('sb-b2-gate');if(g&&g.style.display!=='none')hkSet('b2_gate',false,false);},60); sbState.gate=''; sbState.subcat='';
  ['Property','Tutors','Services','Adventures','Collectors','Cars','LocalMarket'].forEach(c=>{
    const el=document.getElementById('sb-cbt-'+c); if(el)el.classList.toggle('selected',c===cat);
  });
  // Show gate for Property and Cars
  const gateDiv=document.getElementById('sb-b2-gate');
  const gateLabel=document.getElementById('sb-b2-gate-label');
  const gateAgentBtn=document.getElementById('sb-gate-agent');
  const gatePrivateBtn=document.getElementById('sb-gate-private');
  if(gateDiv && gateLabel){
    if(cat==='Property'){
      gateDiv.style.display='block';
      gateLabel.textContent='Are you a registered estate agent or a private seller?';
      if(gateAgentBtn) gateAgentBtn.textContent='Registered estate agent';
      if(gatePrivateBtn) gatePrivateBtn.textContent='Private seller';
      sbCheckB2();
    } else if(cat==='Cars'){
      gateDiv.style.display='block';
      gateLabel.textContent='Are you a registered dealer or selling your own vehicle privately?';
      if(gateAgentBtn) gateAgentBtn.textContent='Registered dealer';
      if(gatePrivateBtn) gatePrivateBtn.textContent='Private seller';
      sbCheckB2();
    } else {
      gateDiv.style.display='none';
      sbState.gate='';
      sbCheckB2();
    }
  }
  // Show "List multiple cards" batch option for Collectors (B2)
  const batchWrap = document.getElementById('sb-b2-batch-wrap');
  if (batchWrap) batchWrap.style.display = cat === 'Collectors' ? 'block' : 'none';
  // Handle LocalMarket separately
  if(cat==='LocalMarket'){ openLMCreateFromWizard(); return; }
}

function sbSetGate(gate){
  sbState.gate=gate;
  const ga=document.getElementById('sb-gate-agent');
  const gp=document.getElementById('sb-gate-private');
  if(ga) ga.style.background=gate==='agent'?'var(--navy)':'';
  if(ga) ga.style.color=gate==='agent'?'#fff':'';
  if(gp) gp.style.background=gate==='private'?'var(--navy)':'';
  if(gp) gp.style.color=gate==='private'?'#fff':'';
  sbCheckB2();
}

function sbCheckB2(){
  const needsGate=sbState.cat==='Property'||sbState.cat==='Cars';
  const ok=sbState.cat && (!needsGate || sbState.gate);
  const btn=document.getElementById('sb-b2-next');
  if(btn){btn.style.opacity=ok?'1':'.4'; btn.style.pointerEvents=ok?'auto':'none';}
}

// ── B3: structured fields ──────────────────────────────────
const SB_FIELDS = {
  Property: [
    {id:'listing_type',  label:'Listing type',    type:'select', opts:['For Sale','To Let','Commercial Sale','Commercial Rental']},
    {id:'property_type', label:'Property type',   type:'select', opts:['House','Apartment','Townhouse','Land','Commercial','Farm']},
    {id:'bedrooms',      label:'Bedrooms',         type:'select', opts:['Studio','1','2','3','4','5','6+']},
    {id:'bathrooms',     label:'Bathrooms',        type:'select', opts:['1','1.5','2','2.5','3','4+']},
    {id:'garages',       label:'Garages',          type:'select', opts:['0','1','2','3+']},
    {id:'floor_size',    label:'Floor size (m²)',  type:'number', placeholder:'e.g. 180'},
    {id:'stand_size',    label:'Stand size (m²)',  type:'number', placeholder:'e.g. 600'},
    {id:'suburb',        label:'Suburb',           type:'text',   placeholder:'e.g. Waterkloof'},
    {id:'price',         label:'Asking price',     type:'text',   placeholder:'e.g. R2 500 000'}
  ],
  Tutors: [
    {id:'subjects',      label:'Subjects',         type:'text',   placeholder:'e.g. Maths, Science'},
    {id:'level',         label:'Level',            type:'select', opts:['Primary school','High school','Grade 12','University','Adult']},
    {id:'format',        label:'Format',           type:'select', opts:['In-person','Online','Both']},
    {id:'rate',          label:'Rate per hour',    type:'text',   placeholder:'e.g. R280/hr'},
    {id:'suburb',        label:'Suburb (for in-person)', type:'text', placeholder:'e.g. Menlyn'}
  ],
  Services_Technical: [
    {id:'trade_type',    label:'Trade / profession', type:'text', placeholder:'e.g. Electrician'},
    {id:'coc',           label:'CoC held?',         type:'select', opts:['Yes','No','Not required for my trade']},
    {id:'callout_area',  label:'Call-out area',     type:'text',   placeholder:'e.g. Pretoria East'},
    {id:'rate',          label:'Call-out rate',     type:'text',   placeholder:'e.g. R800/hr + materials'}
  ],
  Services_Casuals: [
    {id:'work_type',     label:'Type of work',      type:'text',   placeholder:'e.g. Garden maintenance'},
    {id:'in_home',       label:'In-home service?',  type:'select', opts:['Yes — I come to the client','No — client comes to me','Both']},
    {id:'availability',  label:'Availability',      type:'text',   placeholder:'e.g. Weekdays 8am–5pm'},
    {id:'rate',          label:'Rate',              type:'text',   placeholder:'e.g. R200/hr or R1500/day'}
  ],
  Adventures_Experiences: [
    {id:'activity_type', label:'Activity type',     type:'text',   placeholder:'e.g. Mountain hike'},
    {id:'group_size',    label:'Group size',        type:'text',   placeholder:'e.g. 2–8 people'},
    {id:'duration',      label:'Duration',          type:'text',   placeholder:'e.g. Full day (8hrs)'},
    {id:'location',      label:'Location / area',   type:'text',   placeholder:'e.g. Magaliesberg'},
    {id:'rate',          label:'Rate per person',   type:'text',   placeholder:'e.g. R850/person'}
  ],
  Adventures_Accommodation: [
    {id:'property_type', label:'Property type',     type:'select', opts:['Guest house','B&B','Bush camp','Self-catering','Hostel','Boutique hotel']},
    {id:'rooms',         label:'Rooms / units',     type:'number', placeholder:'e.g. 5'},
    {id:'grading',       label:'TGCSA grading (if held)', type:'select', opts:['None','1-star','2-star','3-star','4-star','5-star']},
    {id:'nightly_rate',  label:'Nightly rate',      type:'text',   placeholder:'e.g. R1 200/night'},
    {id:'location',      label:'Location / area',   type:'text',   placeholder:'e.g. Pilanesberg'}
  ],
  Collectors: [
    {id:'item_category', label:'Item category',     type:'text',   placeholder:'e.g. Coins, Art, Stamps'},
    {id:'condition',     label:'Condition',         type:'select', opts:['Mint','Excellent','Good','Fair','As-is']},
    {id:'value',         label:'Estimated value',   type:'text',   placeholder:'e.g. R8 500'},
    {id:'auth_status',   label:'Authentication status', type:'select', opts:['Authenticated by third party','Self-certified','Not authenticated']}
  ],
  Cars: [
    {id:'make',          label:'Make',              type:'text',   placeholder:'e.g. Toyota'},
    {id:'model',         label:'Model',             type:'text',   placeholder:'e.g. Fortuner'},
    {id:'year',          label:'Year',              type:'number', placeholder:'e.g. 2019'},
    {id:'mileage',       label:'Mileage (km)',      type:'number', placeholder:'e.g. 85000'},
    {id:'colour',        label:'Colour',            type:'text',   placeholder:'e.g. White'},
    {id:'transmission',  label:'Transmission',      type:'select', opts:['Automatic','Manual']},
    {id:'engine',        label:'Engine',            type:'text',   placeholder:'e.g. 2.8 GD6'},
    {id:'condition',     label:'Condition',         type:'select', opts:['Excellent','Good','Fair','Needs work']},
    {id:'price',         label:'Asking price',      type:'text',   placeholder:'e.g. R420 000'}
  ]
};

function sbGetFieldKey(){
  const c=sbState.cat;
  if(c==='Services'){
    return sbState.subcat==='services_technical'?'Services_Technical':'Services_Casuals';
  }
  if(c==='Adventures'){
    return sbState.subcat==='adventures_accommodation'?'Adventures_Accommodation':'Adventures_Experiences';
  }
  return c;
}

function sbRenderB3(){
  const key=sbGetFieldKey();
  const fields=SB_FIELDS[key]||SB_FIELDS['Tutors'];
  const hdr=document.getElementById('sb-b3-title');
  if(hdr) hdr.textContent = sbState.cat==='Services' ? (sbState.subcat==='services_technical'?'Trade details':'Service details') : (sbState.cat||'Details');

  // Services / Adventures need subcat selection first
  let subcatHtml='';
  if(sbState.cat==='Services'||sbState.cat==='Adventures'){
    const opts=sbState.cat==='Services'
      ? [{v:'services_technical',l:'Technical (trade/professional)'},{v:'services_casual',l:'Casuals (in-home/general)'}]
      : [{v:'adventures_experiences',l:'Guided experience'},{v:'adventures_accommodation',l:'Accommodation'}];
    subcatHtml=`<div style="margin-bottom:18px;">
      <div style="font-size:12px;font-weight:700;color:var(--text-3);text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px;">Sub-type</div>
      <div style="display:flex;gap:8px;">${opts.map(o=>`
        <button onclick="sbSetSubcat('${o.v}')" id="sb-sub-${o.v}"
          style="flex:1;padding:10px 8px;border-radius:10px;border:1.5px solid var(--border);background:${sbState.subcat===o.v?'var(--navy)':'var(--surface-2)'};color:${sbState.subcat===o.v?'#fff':'var(--text)'};font-size:12px;font-weight:600;cursor:pointer;font-family:'Syne',sans-serif;">
          ${o.l}
        </button>`).join('')}
      </div></div>`;
  }

  const formHtml=fields.map(f=>{
    const val=sbState.fields[f.id]||'';
    if(f.type==='select'){
      return `<div class="field"><label>${f.label}</label>
        <select id="sb-f-${f.id}" onchange="sbSaveField('${f.id}',this.value)">
          <option value="">— Select —</option>
          ${f.opts.map(o=>`<option value="${o}" ${val===o?'selected':''}>${o}</option>`).join('')}
        </select></div>`;
    }
    return `<div class="field"><label>${f.label}</label>
      <input type="${f.type||'text'}" id="sb-f-${f.id}" placeholder="${f.placeholder||''}" value="${val}"
        oninput="sbSaveField('${f.id}',this.value)" onchange="sbSaveField('${f.id}',this.value)"></div>`;
  }).join('');

  const form=document.getElementById('sb-b3-form');
  if(form) form.innerHTML=subcatHtml+formHtml;

  // Also need headline + price
  const titleVal=sbState.fields['title']||'';
  const priceVal=sbState.fields['price']||sbState.fields['rate']||'';
  if(form) form.innerHTML += `
    <div class="field"><label>Headline <span class="req">*</span></label>
      <input type="text" id="sb-f-title" placeholder="e.g. 3-bed home in Waterkloof" value="${titleVal}"
        oninput="sbSaveField('title',this.value)" style="font-size:16px;"></div>`;

  sbCheckB3();
  // Always show AI note on B3 render — show fallback immediately, upgrade to live note if fields filled
  setTimeout(sbTriggerMarketNote, 300);
}

function sbSetSubcat(sub){
  sbState.subcat=sub;
  sbRenderB3();
}

function sbSaveField(id,val){
  sbState.fields[id]=val;
  sbCheckB3();
  // Trigger market note when key fields are filled
  if(['suburb','subjects','trade_type','level','activity_type'].includes(id) && val.trim()){
    clearTimeout(window._sbMarketNoteTimer);
    window._sbMarketNoteTimer=setTimeout(sbTriggerMarketNote, 800);
  }
}

function sbCheckB3(){
  const title=sbState.fields['title']||'';
  const ok=title.trim().length>0;
  const btn=document.getElementById('sb-b3-next');
  if(btn){btn.style.opacity=ok?'1':'.4'; btn.style.pointerEvents=ok?'auto':'none';}
  hkSet(ok?'b3_ready':'b3', false, ok);
}

async function sbTriggerMarketNote(){
  const noteDiv=document.getElementById('sb-b3-ai-note');
  const textDiv=document.getElementById('sb-b3-ai-text');
  if(!noteDiv||!textDiv) return;
  noteDiv.style.display='block';
  const cat=sbState.cat;
  const f=sbState.fields;
  // Show fallback immediately (always reflects current fields)
  textDiv.textContent=sbFallbackMarketNote(cat,f);

  // Cancel any previous in-flight AI request (prevents stale response from old listing)
  if(window._sbMarketNoteAbort){try{window._sbMarketNoteAbort.abort();}catch(e){}}
  const ctl=new AbortController();
  window._sbMarketNoteAbort=ctl;

  let prompt='';
  if(cat==='Property'){
    const beds=f.beds||f.bedrooms||''; const baths=f.baths||f.bathrooms||''; const sub=f.suburb||activeCity.name; const price=f.price||'';
    if(!beds){return;} // wait until beds is filled before sending AI call
    prompt=`In 1 sentence, give a market context note for a ${beds}-bed, ${baths}-bath property in ${sub}, Pretoria${price?' asking '+price:''}. Mention approximate comparable asking prices if you know them. Be specific and brief.`;
  } else if(cat==='Tutors'){
    const sub=f.subjects||''; const level=f.level||''; const format=f.format||'';
    if(!sub){return;}
    prompt=`In 1 sentence, give a market context note for a ${format} ${level} ${sub} tutor in Pretoria. Mention typical hourly rates. Be specific and brief.`;
  } else if(cat==='Services'){
    const trade=f.trade_type||'';
    if(!trade){return;}
    prompt=`In 1 sentence, give a market context note for a ${trade} in Pretoria. Mention typical call-out rates. Be specific and brief.`;
  } else {
    textDiv.textContent='Fill in your details above and I\'ll give you a market context note.';
    return;
  }

  try {
    if(!BEA_ENABLED){textDiv.textContent=sbFallbackMarketNote(cat,f);return;}
    const res=await fetch(BEA_URL+'/advert-agent/market-note',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({email:localStorage.getItem('ms_aa_email')||'', prompt}),
      signal:ctl.signal
    });
    if(ctl.signal.aborted) return;
    const data=await res.json();
    textDiv.textContent=data.response||sbFallbackMarketNote(cat,f);
  } catch(e){
    if(e.name==='AbortError') return;
    textDiv.textContent=sbFallbackMarketNote(cat,f);
  }
}

function sbFallbackMarketNote(cat,f){
  if(cat==='Property'){
    const beds=f.beds||f.bedrooms||''; const sub=f.suburb||activeCity.name;
    return `A ${beds}-bed home in ${sub} — based on recent listings, comparable properties are currently asking R1.8m–R3.2m depending on finish and size.`;
  }
  if(cat==='Tutors'){
    return `Online and in-person tutors in ${activeCity.name} typically charge R200–R400/hr depending on subject and level.`;
  }
  if(cat==='Services'){
    return `${f.trade_type||'Service providers'} in ${activeCity.name} typically charge R650–R950/hr call-out, depending on qualifications and area.`;
  }
  return 'Fill in your details above for a personalised market context note.';
}

// ── B4: AI description draft ────────────────────────────────
async function sbRenderB4(){
  const loadDiv=document.getElementById('sb-b4-loading');
  const editDiv=document.getElementById('sb-b4-editor');
  const descTa=document.getElementById('sb-b4-desc');
  const nextBtn=document.getElementById('sb-b4-next');

  // If we already have a description (came back from B5), show edit mode
  if(sbState.description){
    if(loadDiv)loadDiv.style.display='none';
    if(editDiv)editDiv.style.display='block';
    if(descTa)descTa.value=sbState.description;
    if(nextBtn){nextBtn.style.opacity='1';nextBtn.style.pointerEvents='auto';}
    return;
  }

  if(loadDiv)loadDiv.style.display='block';
  if(editDiv)editDiv.style.display='none';
  if(nextBtn){nextBtn.style.opacity='.4';nextBtn.style.pointerEvents='none';}

  const f=sbState.fields;
  const cat=sbState.cat;
  let prompt=`Write a 3–5 sentence listing description for a ${cat} listing on a marketplace. Use these details: ${JSON.stringify(f)}. Write in first person from the seller\'s perspective, warm and professional. No fluff.`;

  let draft='';
  try {
    if(BEA_ENABLED){
      const res=await fetch(BEA_URL+'/advert-agent/market-note',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({email:localStorage.getItem('ms_aa_email')||'', prompt})
      });
      const data=await res.json();
      draft=data.response||sbFallbackDesc(cat,f);
    } else {
      draft=sbFallbackDesc(cat,f);
    }
  } catch(e){ draft=sbFallbackDesc(cat,f); }

  sbState.description=draft;
  if(loadDiv)loadDiv.style.display='none';
  if(editDiv)editDiv.style.display='block';
  if(descTa)descTa.value=draft;
  if(nextBtn){nextBtn.style.opacity='1';nextBtn.style.pointerEvents='auto';}
  // Save edits to state
  if(descTa) descTa.addEventListener('input',()=>{ sbState.description=descTa.value; });
  // Show session nudge for free sellers with no remaining paid sessions
  const _email=localStorage.getItem('ms_aa_email')||'';
  if(_email && BEA_ENABLED){
    try{
      const _sr=await fetch(BEA_URL+'/advert-agent/status?email='+encodeURIComponent(_email));
      const _sd=await _sr.json();
      const _nudge=document.getElementById('sb-b4-session-nudge');
      if(_nudge) _nudge.style.display=(!_sd.aa_free_used && ((_sd.tuppence_balance??tuppence)<1))?'block':'none';
    }catch(_){}
  }
}

function sbFallbackDesc(cat,f){
  if(cat==='Property') return `I'm offering a ${f.bedrooms||''}-bedroom, ${f.bathrooms||''}-bathroom ${(f.property_type||'home').toLowerCase()} in ${f.suburb||activeCity.name}. Floor size ${f.floor_size||'—'} m² on a ${f.stand_size||'—'} m² stand. ${f.listing_type==='To Let'?'Available to let':'Priced to sell'} at ${f.price||'a negotiable price'}. Serious buyers only — intro requests welcome.`;
  if(cat==='Tutors') return `I offer ${f.format||'in-person and online'} tutoring for ${f.subjects||'various subjects'} at ${f.level||'school and university'} level. Based in ${f.suburb||activeCity.name}. My rate is ${f.rate||'competitive'}. I'm passionate about helping students achieve their best results.`;
  if(cat==='Cars') return `I'm selling my ${f.year||''} ${f.make||''} ${f.model||''} in ${f.condition||'good'} condition with ${f.mileage||'—'} km on the clock. ${f.colour||''}, ${f.transmission||''} transmission, ${f.engine||''} engine. Asking ${f.price||'negotiable'}. Serious buyers only.`;
  return `I'm offering a professional ${cat.toLowerCase()} service in ${activeCity.name}. ${f.rate?`Rate: ${f.rate}.`:''} Contact me via the introduction system for more details.`;
}

// ── B5: room-by-room photo gallery ─────────────────────────
const SB_PHOTO_SLOTS = {
  Property: (f) => {
    const rooms=[{key:'exterior',prompt:'Step back to get the whole house in frame. Late afternoon light is flattering.'}];
    const beds=parseInt(f.bedrooms)||0;
    rooms.push({key:'lounge',prompt:'Shoot from the corner to show the whole room.'});
    rooms.push({key:'kitchen',prompt:'Kitchen photos sell houses. Natural light works best.'});
    for(let i=1;i<=Math.min(beds,4);i++) rooms.push({key:`bedroom_${i}`,prompt:`Bedroom ${i}: Show the bed and the window if you can — buyers want to picture themselves here.`});
    rooms.push({key:'bathroom_main',prompt:'Clean and tidy before shooting — tile and fixture quality matters to buyers.'});
    if(parseInt(f.garages)>0) rooms.push({key:'garage',prompt:'Show the garage space — buyers want to see the size and condition.'});
    rooms.push({key:'garden',prompt:'Garden / outdoor area: show the space and any features.'});
    rooms.push({key:'street_view',prompt:'Optional — helps buyers confirm the neighbourhood.'});
    return rooms;
  },
  Tutors: () => [
    {key:'workspace', prompt:'Add a photo of you in your element — at a desk, whiteboard, or with learning materials.'},
    {key:'qualifications', prompt:'Photograph your qualifications or certificates on display.'},
    {key:'materials', prompt:'Show your study materials or resources — it signals preparation.'},
    {key:'optional_4', prompt:'Any other photo that shows your teaching environment. Skippable.'}
  ],
  Services_Technical: () => [
    {key:'job_completed', prompt:'Show a completed job — before/after pairs are very effective.'},
    {key:'tools_equipment', prompt:'Your tools and equipment tell buyers about your professionalism.'},
    {key:'certification', prompt:'Photograph your trade certificate or registration on display.'},
    {key:'optional_4', prompt:'Any other photo showing your work quality. Skippable.'}
  ],
  Services_Casuals: () => [
    {key:'headshot', prompt:'A friendly, clear photo of you builds confidence with buyers who will have you in their home.'},
    {key:'reference_letter', prompt:'Photograph a reference letter from a previous client.'},
    {key:'work_example', prompt:'Show an example of your work.'}
  ],
  Adventures_Experiences: () => [
    {key:'activity_action', prompt:'Show the experience in action — real guests, real scenery. Action beats studio shots.'},
    {key:'location', prompt:'A wide shot of the location or scenery.'},
    {key:'group', prompt:'Group or participants enjoying the activity.'},
    {key:'safety', prompt:'Safety equipment or setup — guests want to see you take safety seriously.'},
    {key:'optional_5', prompt:'Any other photo of the experience. Skippable.'},
    {key:'optional_6', prompt:'A sixth photo if you have one. Skippable.'}
  ],
  Adventures_Accommodation: (f) => {
    const rooms=[
      {key:'exterior', prompt:'The exterior or entrance — first impressions matter.'},
      {key:'main_room', prompt:'The main room or living area.'},
      {key:'bedroom', prompt:'The bedroom — show the bed, linen, and window.'},
      {key:'bathroom', prompt:'The bathroom — clean and well-lit.'},
      {key:'view', prompt:'The view from the property, if there is one.'},
      {key:'communal', prompt:'Any communal areas — pool, braai, garden.'}
    ];
    if(parseInt(f.rooms||'1')>2) rooms.push({key:'room_2',prompt:'A second room or unit.'});
    if(parseInt(f.rooms||'1')>4) rooms.push({key:'room_3',prompt:'A third room or unit.'});
    return rooms;
  },
  Collectors: () => [
    {key:'front', prompt:'The item from the front — clear, well-lit.'},
    {key:'back', prompt:'The back of the item.'},
    {key:'detail', prompt:'Close-up of any markings, signatures, or notable features — buyers respect honesty.'},
    {key:'packaging', prompt:'The original box or packaging, if present.'},
    {key:'certificate', prompt:'Authentication certificate or provenance document alongside the item.'},
    {key:'optional_6', prompt:'Any other angle or detail. Skippable.'}
  ],
  Cars: () => [
    {key:'front', prompt:'Front of the vehicle — centred, standing back.'},
    {key:'rear', prompt:'Rear of the vehicle.'},
    {key:'driver_side', prompt:'Driver\'s side profile.'},
    {key:'passenger_side', prompt:'Passenger side profile.'},
    {key:'interior_front', prompt:'Interior — dashboard and front seats.'},
    {key:'interior_rear', prompt:'Rear seats.'},
    {key:'dashboard', prompt:'Dashboard close-up — odometer visible.'},
    {key:'engine_bay', prompt:'Engine bay — open bonnet.'},
    {key:'boot', prompt:'Boot / load area.'},
    {key:'damage', prompt:'Any dents, scratches, or wear — buyers respect honesty and it reduces disputes.'}
  ]
};

function sbGetPhotoSlots(){
  const key=sbGetFieldKey();
  const fn=SB_PHOTO_SLOTS[key];
  if(!fn) return SB_PHOTO_SLOTS['Tutors']();
  return fn(sbState.fields);
}

function sbRenderB5(){
  const slots=sbGetPhotoSlots();
  // Update B1 photo feature label to be category-specific
  const photoLabels={
    Property:'Room-by-room photos',
    Tutors:'Teaching environment photos',
    Services_Technical:'Work example photos',
    Services_Casuals:'Personal & work photos',
    Adventures_Experiences:'Experience action shots',
    Adventures_Accommodation:'Property room photos',
    Collectors:'Multi-angle item photos',
    Cars:'Full vehicle walkthrough',
    LocalMarket:'Business & work photos'
  };
  const b1lbl=document.getElementById('sb-b1-photo-label');
  if(b1lbl) b1lbl.textContent=photoLabels[sbGetFieldKey()]||'Guided photos';

  const intro=document.getElementById('sb-b5-intro');
  if(intro){
    const intros={
      Property:"Now let's add photos for each part of your listing. Buyers scroll through these before deciding to connect — the more you add, the stronger your listing.",
      Tutors:"Add a photo that shows you in your element — at a desk, whiteboard, or with learning materials.",
      Cars:"Car buyers want to see everything. Photograph all four sides, interior, engine bay, and any damage.",
      Services:"Show your work, your tools, or a completed job. Before/after pairs are very effective.",
      Adventures:"Show the experience in action — real guests, real scenery.",
      Collectors:"Photograph the item from multiple angles. Include any markings, signatures, or wear — buyers respect honesty."
    };
    intro.textContent=intros[sbState.cat]||intros['Services'];
  }
  const slotsDiv=document.getElementById('sb-b5-slots');
  if(!slotsDiv) return;
  slotsDiv.innerHTML=slots.map((s,i)=>{
    const existing=sbState.photos.find(p=>p.slot===s.key);
    const imgHtml=existing
      ?`<img src="${existing.dataUrl}" style="width:100%;height:120px;object-fit:cover;border-radius:8px;margin-bottom:6px;">`
      :'';
    return `<div style="border:1.5px solid var(--border);border-radius:12px;padding:14px;margin-bottom:12px;" id="sb-slot-${s.key}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;">
        <div style="font-size:13px;font-weight:700;">${sbSlotLabel(s.key)}</div>
        <button onclick="sbSkipSlot('${s.key}')" style="background:none;border:none;color:var(--text-3);font-size:11px;cursor:pointer;padding:0;font-family:'Inter',sans-serif;">Skip</button>
      </div>
      <p style="font-size:12px;color:var(--text-3);margin-bottom:10px;font-style:italic;line-height:1.5;">"${s.prompt}"</p>
      ${imgHtml}
      ${existing
        ?`<div style="display:flex;gap:8px;"><input type="text" placeholder="Caption (optional)" value="${existing.caption||''}" oninput="sbUpdateCaption('${s.key}',this.value)" style="flex:1;border:1px solid var(--border);border-radius:8px;padding:7px 10px;font-size:12px;background:var(--surface-2);color:var(--text);">
           <button onclick="sbRemovePhoto('${s.key}')" style="background:none;border:1px solid var(--border);border-radius:8px;padding:7px 10px;font-size:11px;color:var(--text-2);cursor:pointer;">Remove</button></div>`
        :`<div style="display:flex;gap:8px;">
           <button onclick="sbOpenPhotoSlot('${s.key}')" style="flex:1;background:var(--navy);color:#fff;border:none;border-radius:50px;padding:10px;font-family:'Syne',sans-serif;font-size:13px;font-weight:600;cursor:pointer;">📷 Add photo</button>
         </div>`
      }
    </div>`;
  }).join('');
}

function sbSlotLabel(key){
  const labels={exterior:'Exterior / street view',lounge:'Lounge',kitchen:'Kitchen',bedroom_1:'Bedroom 1',bedroom_2:'Bedroom 2',bedroom_3:'Bedroom 3',bedroom_4:'Bedroom 4',bathroom_main:'Main bathroom',garage:'Garage',garden:'Garden / outdoor',street_view:'Street view',workspace:'Workspace',qualifications:'Qualifications',materials:'Study materials',job_completed:'Completed job',tools_equipment:'Tools & equipment',certification:'Trade certificate',headshot:'Profile photo',reference_letter:'Reference letter',work_example:'Work example',activity_action:'Activity in action',location:'Location / scenery',group:'Group / participants',safety:'Safety equipment',view:'View from property',communal:'Communal areas',room_2:'Room 2',room_3:'Room 3',front:'Front',back:'Back / rear',detail:'Detail / markings',packaging:'Box / packaging',certificate:'Authentication cert',driver_side:'Driver side',passenger_side:'Passenger side',interior_front:'Interior (front)',interior_rear:'Interior (rear)',dashboard:'Dashboard',engine_bay:'Engine bay',boot:'Boot',damage:'Damage disclosure'};
  if(labels[key]) return labels[key];
  if(key.startsWith('optional_')) return `Optional photo ${key.split('_')[1]}`;
  return key.replace(/_/g,' ');
}

let sbCurrentPhotoSlot=null;
function sbOpenPhotoSlot(key){
  sbCurrentPhotoSlot=key;
  document.getElementById('sb-photo-inp').click();
}
function sbHandlePhotoCapture(e){
  const file=e.target.files[0]; if(!file||!sbCurrentPhotoSlot) return;
  const r=new FileReader();
  r.onload=ev=>{
    const img=new Image();
    img.onload=()=>{
      const MAX=1200,Q=0.80;
      let w=img.width,h=img.height;
      if(w>MAX||h>MAX){const s=Math.min(MAX/w,MAX/h);w=Math.round(w*s);h=Math.round(h*s);}
      const c=document.createElement('canvas'); c.width=w; c.height=h;
      c.getContext('2d').drawImage(img,0,0,w,h);
      const dataUrl=c.toDataURL('image/jpeg',Q);
      sbState.photos=sbState.photos.filter(p=>p.slot!==sbCurrentPhotoSlot);
      sbState.photos.push({slot:sbCurrentPhotoSlot,dataUrl,caption:''});
      sbRenderB5();
      hkSet(sbState.photos.length>=2?'b5_some':'b5', false, sbState.photos.length>=2);
    };
    img.src=ev.target.result;
  };
  r.readAsDataURL(file);
  e.target.value='';
}
function sbSkipSlot(key){
  const el=document.getElementById('sb-slot-'+key);
  if(el) el.style.opacity='.4';
}
function sbRemovePhoto(key){
  sbState.photos=sbState.photos.filter(p=>p.slot!==key);
  sbRenderB5();
}
function sbUpdateCaption(key,val){
  const p=sbState.photos.find(p=>p.slot===key);
  if(p) p.caption=val;
}

// ── B6: selfie ──────────────────────────────────────────────
function sbHandleSelfie(e){
  const file=e.target.files[0]; if(!file) return;
  const r=new FileReader();
  r.onload=ev=>{
    const img=new Image();
    img.onload=()=>{
      // Square crop to 400px
      const SIZE=400;
      const c=document.createElement('canvas'); c.width=SIZE; c.height=SIZE;
      const ctx=c.getContext('2d');
      const side=Math.min(img.width,img.height);
      const sx=(img.width-side)/2, sy=(img.height-side)/2;
      ctx.drawImage(img,sx,sy,side,side,0,0,SIZE,SIZE);
      sbState.selfieUrl=c.toDataURL('image/jpeg',0.85);
      const prev=document.getElementById('sb-b6-preview');
      if(prev){ prev.innerHTML=`<img src="${sbState.selfieUrl}" style="width:120px;height:120px;border-radius:50%;object-fit:cover;">`; }
    };
    img.src=ev.target.result;
  };
  r.readAsDataURL(file);
  e.target.value='';
}

// ── B7: Trust Score checklist ───────────────────────────────
const SB_SIGNALS = {
  Property_agent: [
    {id:'property.ppra',         pts:15, declPts:0,   label:'PPRA / EAAB Registration',      how:'upload', script:"Your PPRA certificate is the most important credential you can show. Upload it — I\'ll confirm the number and expiry."},
    {id:'property.ffc',          pts:10, declPts:0,   label:'Fidelity Fund Certificate (FFC)',how:'upload', script:"The FFC lapses every year. Upload your current FFC — buyers and the law require it."},
    {id:'property.mandate',      pts:8,  declPts:0,   label:'Mandate / instruction letter',   how:'upload', script:"Upload the signed mandate from the property owner — proves you're authorised to market this property."},
    {id:'property.nqf6_plus',    pts:8,  declPts:0,   label:'NQF6+ / Professional designation',how:'upload',script:"An NQF6 or professional designation puts you in the top tier. Upload your certificate."},
    {id:'property.body',         pts:5,  declPts:0,   label:'Professional body membership',   how:'upload', script:"IEASA, SAPOA, or NAR — upload your membership certificate."},
    {id:'property.nqf4',         pts:6,  declPts:0,   label:'NQF4 Real Estate qualification', how:'upload', script:"Upload your NQF4 — the foundation qualification for PPRA."},
    {id:'property.nqf5',         pts:6,  declPts:0,   label:'NQF5 Real Estate qualification', how:'upload', script:"Upload your NQF5 — stacks on top of NQF4 for 6 more points."},
    {id:'property.exp_10plus',   pts:5,  declPts:4,   label:'Experience 10+ years',           how:'declare',script:"10+ years is a strong signal. Declare now — upload CV for the final point."},
    {id:'property.exp_2_5',      pts:4,  declPts:3,   label:'Experience 2–5 years',           how:'declare',script:"Declare your years of practice — 3 points immediately, 1 more with your CV."},
    {id:'property.specialist_services',pts:3,declPts:3,label:'Specialist services declaration',how:'declare',script:"Valuations, bond origination, conveyancing referrals? Buyers filter by this — one tap."}
  ],
  Property_private: [
    {id:'property.private_seller',pts:0, declPts:0,   label:'Private seller declaration',     how:'declare',script:"Tell buyers you're a private seller — one tap. They need to know this upfront."},
    {id:'property.exp_10plus',   pts:5,  declPts:4,   label:'Experience 10+ years',           how:'declare',script:"10+ years in property is a strong signal. Declare now."},
    {id:'property.exp_2_5',      pts:4,  declPts:3,   label:'Experience 2–5 years',           how:'declare',script:"Declare your years of ownership or experience — 3 points immediately."}
  ],
  Tutors: [
    {id:'tutors.clearance',      pts:8,  declPts:0,   label:'Police clearance / DBS check',   how:'upload', script:"Parents expect a clearance check. Upload your SAPS clearance — it\'s the most trust-building thing you can do."},
    {id:'tutors.honours',        pts:14, declPts:0,   label:'Honours / Postgraduate (NQF8+)', how:'upload', script:"Your highest qualification earns the most points. Upload your honours or postgrad degree."},
    {id:'tutors.sace',           pts:8,  declPts:0,   label:'SACE registration',              how:'upload', script:"Required for school teachers. Upload your SACE certificate — I\'ll verify the number."},
    {id:'tutors.bachelor',       pts:10, declPts:0,   label:'Bachelor\'s Degree (NQF7)',      how:'upload', script:"Upload your degree. If you have an honours degree, upload that instead — it earns more."},
    {id:'tutors.cert_diploma',   pts:6,  declPts:0,   label:'Certificate or Diploma (NQF5–6)',how:'upload', script:"Upload your diploma. A bachelor's earns more if you have one."},
    {id:'tutors.specialisation', pts:5,  declPts:0,   label:'Subject specialisation cert',    how:'upload', script:"A subject-specific cert shows you specialise. Upload any relevant cert or transcript."},
    {id:'tutors.exp_5plus',      pts:6,  declPts:5,   label:'Teaching experience 5+ years',   how:'declare',script:"5+ years is a strong differentiator. Declare now for 5 points — upload CV for the last 1."},
    {id:'tutors.exp_2_5',        pts:5,  declPts:4,   label:'Teaching experience 2–5 years',  how:'declare',script:"Tell buyers how long you've been teaching. 4 points on declaration, 1 more with CV."},
    {id:'tutors.safeguarding',   pts:3,  declPts:0,   label:'Safeguarding / child protection',how:'upload', script:"For tutors with learners under 18, this reassures parents. Upload your certificate."},
    {id:'tutors.strong_cv',      pts:2,  declPts:0,   label:'Structured CV',                  how:'upload', script:"Upload a well-structured CV — it rounds out your profile."},
    {id:'tutors.online_ready',   pts:1,  declPts:1,   label:'Online platform proficiency',    how:'declare',script:"Declare which online platforms you use — Zoom, Google Classroom, Teams. One tap."}
  ],
  Services_Technical: [
    {id:'services_tech.body_reg', pts:12,declPts:0,   label:'Professional body registration', how:'upload', script:"ECSA, PIRB, NHBRC, FSCA, or SAICA — your most powerful credential. Upload your registration."},
    {id:'services_tech.trade_cert',pts:8,declPts:0,   label:'Formal trade certificate',        how:'upload', script:"City & Guilds, TVET, MERSETA, CETA, or Red Seal — the foundation credential. Upload it."},
    {id:'services_tech.cidb',    pts:6,  declPts:0,   label:'CIDB grading (construction)',    how:'upload', script:"If you do construction above R200k in SA, CIDB grading is legally required."},
    {id:'services_tech.tickets', pts:6,  declPts:0,   label:'Additional tickets (up to 2)',    how:'upload', script:"First Aid, working at heights, confined space — 3 pts each, up to 2. Upload yours."},
    {id:'services_tech.coc',     pts:5,  declPts:0,   label:'Primary industry licence / CoC', how:'upload', script:"Your CoC proves you're legally authorised. Upload it — buyers look for this before hiring."},
    {id:'services_tech.insurance',pts:5, declPts:0,   label:'Public liability insurance',     how:'upload', script:"Clients want to know you're insured. Upload your current liability policy — expiry included."},
    {id:'services_tech.exp_7plus',pts:4, declPts:3,   label:'Trade experience 7+ years',      how:'declare',script:"7+ years is significant. Declare now — 3 points, 1 more with your CV."},
    {id:'services_tech.exp_3_7', pts:4,  declPts:3,   label:'Trade experience 3–7 years',     how:'declare',script:"Declare your years in trade. 3 points on declaration, 1 more with CV."},
    {id:'services_tech.strong_cv',pts:2, declPts:0,   label:'Strong verifiable CV',           how:'upload', script:"A CV with references is a strong supporting document."}
  ],
  Services_Casuals: [
    {id:'services_cas.clearance', pts:10,declPts:0,   label:'Police clearance check',         how:'upload', script:"You declared you work in clients' homes. A police clearance is the #1 thing clients expect. Upload your SAPS clearance — 10 points."},
    {id:'services_cas.exp_5plus', pts:8, declPts:6,   label:'5+ years in service',            how:'declare',script:"5+ years is a strong signal. Declare now — 6 points, 8 with CV."},
    {id:'services_cas.nqf',       pts:8, declPts:0,   label:'NQF qualification or short course',how:'upload',script:"Any formal qualification or short course earns 8 points. Upload your certificate."},
    {id:'services_cas.ref_1',     pts:6, declPts:0,   label:'Reference letter (1st)',         how:'upload', script:"A reference letter from a previous client is the most powerful thing you can show."},
    {id:'services_cas.exp_2_4',   pts:6, declPts:4,   label:'2–4 years in service',           how:'declare',script:"Declare your experience. 4 points on declaration, 6 with a CV."},
    {id:'services_cas.ref_2',     pts:4, declPts:0,   label:'Reference letter (2nd)',         how:'upload', script:"A second reference adds credibility. Upload it if you have one."}
  ],
  Adventures_Experiences: [
    {id:'adv_exp.guide_cert',    pts:12, declPts:0,   label:'Activity-specific guide cert',   how:'upload', script:"FGASA, PADI, MCSA, SACAA — upload the most relevant certificate. I\'ll verify the body and number."},
    {id:'adv_exp.permit',        pts:6,  declPts:0,   label:'Operator permit / concession',   how:'upload', script:"If you operate in a national park or controlled waterway, upload your permit — proves you're authorised."},
    {id:'adv_exp.first_aid',     pts:6,  declPts:0,   label:'First Aid / Emergency Response', how:'upload', script:"First Aid with a current expiry is essential for high-risk activities. Upload yours — I\'ll check the expiry."},
    {id:'adv_exp.regulator',     pts:5,  declPts:0,   label:'Regulatory compliance (SACAA/SAMSA)',how:'upload',script:"Some activities need a regulatory certificate — SACAA Part 135 for aviation, SAMSA for maritime."},
    {id:'adv_exp.insurance',     pts:5,  declPts:0,   label:'Liability / indemnity insurance',how:'upload', script:"For activities involving physical risk, liability insurance is non-negotiable. Upload your current policy."},
    {id:'adv_exp.exp_7plus',     pts:5,  declPts:4,   label:'Guided experience 7+ years',     how:'declare',script:"7+ years of guiding — declare now for 4 points, 1 more with CV."},
    {id:'adv_exp.exp_3_7',       pts:5,  declPts:4,   label:'Guided experience 3–7 years',    how:'declare',script:"Declare your guiding experience. 4 points on declaration, 5 with CV."},
    {id:'adv_exp.safety_cert',   pts:4,  declPts:0,   label:'Additional safety certificate',  how:'upload', script:"WFR, swift water rescue, avalanche cert — each adds credibility. Upload one."}
  ],
  Adventures_Accommodation: [
    {id:'adv_acc.tgcsa_5',       pts:22, declPts:0,   label:'TGCSA 5-star grading',           how:'upload', script:"5-star is the gold standard. Upload your current TGCSA certificate — I\'ll check the expiry."},
    {id:'adv_acc.tgcsa_4',       pts:18, declPts:0,   label:'TGCSA 4-star grading',           how:'upload', script:"Upload your TGCSA 4-star certificate."},
    {id:'adv_acc.tgcsa_3',       pts:14, declPts:0,   label:'TGCSA 3-star grading',           how:'upload', script:"Upload your TGCSA 3-star certificate."},
    {id:'adv_acc.licence',       pts:6,  declPts:0,   label:'Municipal trading licence',      how:'upload', script:"Your local authority trading licence proves you're operating legally."},
    {id:'adv_acc.health_safety', pts:5,  declPts:0,   label:'Health & safety compliance',     how:'upload', script:"Upload your health and safety certificate — guests expect accommodation to meet safety standards."},
    {id:'adv_acc.fire',          pts:4,  declPts:0,   label:'Fire clearance certificate',     how:'upload', script:"Upload your fire clearance — it\'s a legal requirement for accommodation."},
    {id:'adv_acc.tourism_levy',  pts:4,  declPts:0,   label:'Tourism levy registration',      how:'upload', script:"Upload your tourism levy registration — it signals a legitimate, accountable operation."}
  ],
  Collectors: [
    {id:'collectors.provenance', pts:8,  declPts:0,   label:'Item provenance documentation',  how:'upload', script:"Provenance is the chain of custody. Upload an auction receipt, gallery invoice, or inheritance document."},
    {id:'collectors.auth_cert',  pts:6,  declPts:0,   label:'Third-party authentication cert',how:'upload', script:"Upload a certificate from PSA, PCGS, GIA, or Beckett. I\'ll confirm the authenticator."},
    {id:'collectors.dealer_reg', pts:6,  declPts:0,   label:'Dealer / reseller registration', how:'upload', script:"Upload your dealer registration. Buyers need to know if they're dealing with a registered dealer."},
    {id:'collectors.appraisal',  pts:5,  declPts:0,   label:'Professional appraisal',         how:'upload', script:"Upload an appraisal document — it gives buyers a price anchor and shows independent assessment."},
    {id:'collectors.auth_guarantee',pts:2,declPts:2,  label:'Authenticity guarantee declaration',how:'declare',script:"Declare whether you offer a return if the item proves inauthentic. Buyers look for this."},
    {id:'collectors.specialisation',pts:4,declPts:4,  label:'Category specialisation',        how:'declare',script:"Tell buyers what you specialise in — coins, art, stamps, wine, vintage watches. One tap."}
  ],
  Cars_dealer: [
    {id:'cars.dealer_reg',       pts:8,  declPts:0,   label:'Dealer / trader registration',   how:'upload', script:"Upload your MIRA dealer registration. Buyers with a registered dealer have different legal protections."},
    {id:'cars.ownership',        pts:10, declPts:0,   label:'Vehicle ownership (NATIS)',       how:'upload', script:"Upload your NATIS registration papers — proves you own the vehicle. Most important thing a car buyer looks for."},
    {id:'cars.finance_clear',    pts:4,  declPts:0,   label:'Finance clearance',              how:'upload', script:"Upload a letter confirming no outstanding finance. Without this, a buyer could unknowingly take on your debt."},
    {id:'cars.rwc',              pts:6,  declPts:0,   label:'Roadworthy certificate (RWC)',    how:'upload', script:"Upload your roadworthy certificate — mandatory for change of ownership in SA."},
    {id:'cars.inspection',       pts:5,  declPts:0,   label:'AA / independent inspection',    how:'upload', script:"Upload an AA or independent inspection report — the most reassuring thing for a serious buyer."},
    {id:'cars.service_history',  pts:4,  declPts:0,   label:'Service history',                how:'upload', script:"Upload your service book — full history increases buyer confidence and the asking price."},
    {id:'cars.safety_recall_clear',pts:3,declPts:0,   label:'DEKRA / NRCS recall check',      how:'upload', script:"Upload a DEKRA or NRCS recall clearance — shows buyers you've done your homework."}
  ],
  Cars_private: [
    {id:'cars.private_seller',   pts:0,  declPts:0,   label:'Private seller declaration',     how:'declare',script:"Tell buyers you're a private seller — one tap. Consumer protection differs from dealer sales."},
    {id:'cars.ownership',        pts:10, declPts:0,   label:'Vehicle ownership (NATIS)',       how:'upload', script:"Upload your NATIS papers — proves you own the vehicle."},
    {id:'cars.finance_clear',    pts:4,  declPts:0,   label:'Finance clearance',              how:'upload', script:"Confirm no outstanding finance — a buyer could unknowingly take on your debt without this."},
    {id:'cars.rwc',              pts:6,  declPts:0,   label:'Roadworthy certificate',         how:'upload', script:"Mandatory for change of ownership in SA."},
    {id:'cars.inspection',       pts:5,  declPts:0,   label:'AA / independent inspection',    how:'upload', script:"The most reassuring thing for a serious buyer."},
    {id:'cars.service_history',  pts:4,  declPts:0,   label:'Service history',                how:'upload', script:"Full history increases buyer confidence and the asking price."},
    {id:'cars.safety_recall_clear',pts:3,declPts:0,   label:'DEKRA / NRCS recall check',      how:'upload', script:"Shows buyers you've done your homework."}
  ]
};

function sbGetSignalSet(){
  const key=sbGetFieldKey();
  if(key==='Property') return SB_SIGNALS[`Property_${sbState.gate||'agent'}`]||SB_SIGNALS.Property_agent;
  if(key==='Cars')     return SB_SIGNALS[`Cars_${sbState.gate||'dealer'}`]||SB_SIGNALS.Cars_dealer;
  return SB_SIGNALS[key]||SB_SIGNALS.Tutors;
}

function sbCalcScore(){
  const signals=sbGetSignalSet();
  let pts=40; // All new sellers start at Established tier (40-pt base)
  signals.forEach(s=>{
    const st=sbState.signals[s.id];
    if(!st) return;
    if(st.status==='uploaded') pts+=s.pts;
    else if(st.status==='declared') pts+=s.declPts||0;
  });
  return Math.min(100,pts);
}

function sbScoreBadge(score){
  if(score>=90) return {tier:'Highly Trusted',color:'#C8873A',bg:'rgba(200,135,58,.12)'};
  if(score>=70) return {tier:'Trusted',color:'#16a34a',bg:'rgba(22,163,74,.12)'};
  if(score>=40) return {tier:'Established',color:'#2563eb',bg:'rgba(37,99,235,.12)'};
  return {tier:'New',color:'var(--text-3)',bg:'var(--surface-2)'};
}

function sbUpdateB7Score(){
  const score=sbCalcScore();
  const badge=sbScoreBadge(score);
  const sc=document.getElementById('sb-b7-score'); if(sc)sc.textContent=score;
  const bd=document.getElementById('sb-b7-badge');
  if(bd){bd.textContent=badge.tier; bd.style.background=badge.bg; bd.style.color=badge.color; bd.style.borderColor=badge.color;}
}

function sbRenderB7(){
  sbUpdateB7Score();
  const signals=sbGetSignalSet();
  const container=document.getElementById('sb-b7-signals');
  if(!container) return;
  // Sort by pts descending (highest value first per AI rule 2)
  const sorted=[...signals].sort((a,b)=>b.pts-a.pts);

  // Mutual exclusivity: experience tiers — if higher tier is done, lower tier is hidden
  // Pattern: signals whose ids end in _10plus / _7plus / _5plus exclude the matching lower tier
  const higherExpDone = new Set();
  sorted.forEach(sig=>{
    const st=sbState.signals[sig.id];
    if(!st||st.status==='skipped'||st.status==='empty') return;
    if(sig.id.match(/exp_10plus|exp_7plus|exp_5plus/)) {
      // Mark corresponding lower tiers as excluded
      const prefix=sig.id.replace(/exp_10plus|exp_7plus|exp_5plus/,'');
      higherExpDone.add(prefix+'lower');
    }
  });

  container.innerHTML=sorted.map(sig=>{
    const st=sbState.signals[sig.id]||{status:'empty'};
    const isSkipped=st.status==='skipped';
    // Hide skipped signals — they collapse to a small "restore" link
    if(isSkipped){
      return `<div style="text-align:right;margin-bottom:4px;">
        <button onclick="sbRestoreSignal('${sig.id}')" style="background:none;border:none;color:var(--text-3);font-size:11px;cursor:pointer;font-family:'Inter',sans-serif;">+ Add ${sig.label} (+${sig.pts} pts)</button>
      </div>`;
    }
    // Hide lower experience tiers when a higher tier is done
    const isLowerExp=sig.id.match(/exp_2_5|exp_3_7|exp_2_4/);
    const prefix=sig.id.replace(/exp_2_5|exp_3_7|exp_2_4/,'');
    if(isLowerExp && higherExpDone.has(prefix+'lower')) return '';

    const isUploaded=st.status==='uploaded';
    const isDeclared=st.status==='declared';
    const ringIcon=isUploaded?'●':isDeclared?'◑':'○';
    const ringColor=isUploaded?'#16a34a':isDeclared?'#2563eb':'var(--text-3)';
    const canDeclare=sig.declPts>0;
    return `<div style="border:1.5px solid ${isUploaded?'rgba(22,163,74,.3)':isDeclared?'rgba(37,99,235,.3)':'var(--border)'};border-radius:12px;padding:14px;margin-bottom:10px;background:${isUploaded?'rgba(22,163,74,.04)':isDeclared?'rgba(37,99,235,.04)':'var(--surface)'};">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;">
        <div style="display:flex;align-items:center;gap:8px;">
          <span style="font-size:16px;color:${ringColor};font-weight:700;">${ringIcon}</span>
          <span style="font-size:13px;font-weight:700;">${sig.label}</span>
        </div>
        <div style="display:flex;align-items:center;gap:8px;">
          <span style="font-size:12px;font-weight:700;color:var(--navy);">+${sig.pts} pts</span>
          ${isUploaded||isDeclared?'':`<button onclick="sbSkipSignal('${sig.id}')" style="background:none;border:none;color:var(--text-3);font-size:11px;cursor:pointer;font-family:'Inter',sans-serif;">Skip</button>`}
        </div>
      </div>
      <p style="font-size:12px;color:var(--text-2);line-height:1.55;margin-bottom:10px;font-style:italic;">"${sig.script}"</p>
      ${isUploaded||isDeclared
        ? `<div style="font-size:12px;color:#16a34a;font-weight:600;">✓ ${isUploaded?'Evidence uploaded':'Declared'} · ${isUploaded?sig.pts:sig.declPts||0} pts earned</div>`
        : `<div style="display:flex;gap:8px;flex-wrap:wrap;">
             ${sig.how!=='declare_only'?`<button onclick="sbTriggerDocUpload('${sig.id}')" style="flex:1;min-width:120px;background:var(--navy);color:#fff;border:none;border-radius:50px;padding:9px 14px;font-family:'Syne',sans-serif;font-size:12px;font-weight:700;cursor:pointer;">📎 Upload evidence</button>`:''}
             ${canDeclare?`<button onclick="sbDeclareSignal('${sig.id}')" style="flex:1;min-width:100px;background:transparent;border:1.5px solid var(--border);border-radius:50px;padding:9px 14px;font-family:'Syne',sans-serif;font-size:12px;font-weight:600;cursor:pointer;color:var(--text-2);">Declare (+${sig.declPts} pts)</button>`:''}
           </div>`
      }
      <div id="sb-sig-feedback-${sig.id}" style="display:none;margin-top:8px;font-size:12px;border-radius:8px;padding:8px 10px;"></div>
    </div>`;
  }).join('');
}

function sbTriggerDocUpload(signalId){
  sbState.currentDocSignal=signalId;
  document.getElementById('sb-doc-inp').click();
}

async function sbHandleDocUpload(e){
  const file=e.target.files[0]; if(!file||!sbState.currentDocSignal) return;
  const signalId=sbState.currentDocSignal;
  const sig=sbGetSignalSet().find(s=>s.id===signalId);
  if(!sig) return;
  const feedbackEl=document.getElementById('sb-sig-feedback-'+signalId);
  if(feedbackEl){
    feedbackEl.style.display='block';
    feedbackEl.style.background='rgba(37,99,235,.07)';
    feedbackEl.style.color='#2563eb';
    feedbackEl.textContent='Reviewing your document…';
  }

  // For now accept all uploads (AI vision review to be added to BEA)
  sbState.signals[signalId]={status:'uploaded', pts:sig.pts};
  if(feedbackEl){
    feedbackEl.style.background='rgba(22,163,74,.08)';
    feedbackEl.style.color='#16a34a';
    feedbackEl.textContent=`✓ Document received — +${sig.pts} points awarded.`;
  }
  sbUpdateB7Score();
  setTimeout(()=>sbRenderB7(), 800);
  e.target.value='';
}

function sbDeclareSignal(signalId){
  const sig=sbGetSignalSet().find(s=>s.id===signalId);
  if(!sig||!sig.declPts) return;
  sbState.signals[signalId]={status:'declared', pts:sig.declPts};
  sbUpdateB7Score();
  sbRenderB7();
  showToast(`✓ Declared — +${sig.declPts} points`);
}

function sbSkipSignal(signalId){
  sbState.signals[signalId]={status:'skipped', pts:0};
  sbUpdateB7Score();
  sbRenderB7();
}

function sbRestoreSignal(signalId){
  delete sbState.signals[signalId];
  sbUpdateB7Score();
  sbRenderB7();
}

// ── B8: publish preview ─────────────────────────────────────
function sbRenderB8Preview(){
  // Clear stale error and reset publish button every time B8 is entered
  const _errEl=document.getElementById('sb-b8-err');
  if(_errEl){_errEl.style.display='none';_errEl.innerHTML='';}
  const _btn=document.getElementById('sb-b8-publish-btn');
  if(_btn){_btn.textContent='Publish listing →';_btn.style.opacity='1';_btn.style.pointerEvents='auto';}
  const f=sbState.fields;
  const title=f.title||'Untitled listing';
  const cat=sbState.cat;
  const photoCount=sbState.photos.length;
  const score=sbCalcScore();
  const badge=sbScoreBadge(score);

  const prevEl=document.getElementById('sb-b8-preview');
  if(prevEl) prevEl.innerHTML=`
    <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--text-3);margin-bottom:8px;">${cat}</div>
    <div style="font-size:17px;font-weight:800;margin-bottom:6px;">${title}</div>
    <div style="font-size:13px;color:var(--text-2);line-height:1.6;margin-bottom:10px;">${sbState.description||'—'}</div>
    <div style="display:flex;gap:10px;font-size:12px;color:var(--text-3);">
      <span>📸 ${photoCount} photo${photoCount!==1?'s':''}</span>
      ${f.price||f.rate?`<span>💰 ${f.price||f.rate}</span>`:''}
      ${sbState.selfieUrl?'<span>👤 Profile photo added</span>':''}
    </div>`;

  // Trust Score summary
  const scoreEl=document.getElementById('sb-b8-score-summary');
  const scoreNum=document.getElementById('sb-b8-score');
  const scoreBadge=document.getElementById('sb-b8-badge');
  const skippedEl=document.getElementById('sb-b8-skipped');
  if(scoreEl){ scoreEl.style.display='block'; }
  if(scoreNum) scoreNum.textContent=score;
  if(scoreBadge){scoreBadge.textContent=badge.tier;scoreBadge.style.background=badge.bg;scoreBadge.style.color=badge.color;}
  // Count skipped signals
  const allSigs=sbGetSignalSet();
  const skipped=allSigs.filter(s=>!sbState.signals[s.id]||sbState.signals[s.id].status==='skipped');
  const skippedPts=skipped.reduce((a,s)=>a+s.pts,0);
  if(skippedEl && skipped.length>0){
    skippedEl.textContent=`You skipped ${skipped.length} signal${skipped.length!==1?'s':''} worth ${skippedPts} points. You can add these any time from your profile.`;
  }
}

async function sbDoPublish(){
  if(isOffline()){ showToast("You're offline — publishing needs a connection"); return; }
  const btn=document.getElementById('sb-b8-publish-btn');
  const errEl=document.getElementById('sb-b8-err');
  const email=localStorage.getItem('ms_aa_email')||'';
  const f=sbState.fields;
  const title=f.title||'';
  if(!title.trim()||!email){
    if(errEl){errEl.textContent='Missing title or account — please go back and check your details.';errEl.style.display='block';} return;
  }

  // ── EULA gate for in-app publish flow ─────────────────────────────────────
  // Check if this seller has accepted the EULA. If not, show the standard
  // EULA modal (fea-lm-eula-modal) — on acceptance we record it and retry.
  if(BEA_ENABLED){
    try{
      const _ur=await fetch(BEA_URL+'/users/'+encodeURIComponent(email));
      if(_ur.ok){
        const _ud=await _ur.json();
        if(!_ud.eula_accepted_at){
          // Hijack the LM EULA modal for the standard seller EULA check
          // Set the title to reflect this is the seller EULA, not just LM
          const _eulaHdr=document.querySelector('#fea-lm-eula-modal h2');
          if(_eulaHdr) _eulaHdr.textContent='Accept TrustSquare Terms before publishing';
          _feaLmEulaPending=async()=>{
            // Record EULA acceptance via the standard endpoint
            await fetch(BEA_URL+'/users/'+encodeURIComponent(email)+'/eula',{method:'POST',headers:{'X-Api-Key':API_KEY}}).catch(()=>{});
            await sbDoPublish();
          };
          document.getElementById('fea-lm-eula-modal').style.display='flex';
          return;
        }
        // Banking nudge: remember for post-publish display
        sbState._hasBanking=!!_ud.banking_added_at;
      }
    }catch(_){}
  }
  if(btn){btn.textContent='Publishing…';btn.style.opacity='.7';btn.style.pointerEvents='none';}
  if(errEl) errEl.style.display='none';
  try {
    let listingId=null;
    if(BEA_ENABLED){
      // Use raw fetch so we can read the error body if the request fails
      const rawRes=await fetch(BEA_URL+'/listings',{
        method:'POST',
        headers:{'Content-Type':'application/json','X-Api-Key':API_KEY},
        body:JSON.stringify({
          title,
          price:f.price||f.rate||'POA',
          category:sbState.cat,
          city:activeCity.name,
          area:(activeSuburb&&activeSuburb.name)||activeCity.name,
          suburb:f.suburb||(activeSuburb&&activeSuburb.name)||activeCity.name,
          geo_city_id:activeCity.id||null,
          description:sbState.description||'',
          seller_email:email,
          listing_status:'live',
          trust_score:sbCalcScore(),
          beds:       f.beds       ? parseInt(f.beds)       : null,
          baths:      f.baths      ? parseInt(f.baths)      : null,
          garages:    f.garages    ? parseInt(f.garages)    : null,
          floor_area: f.floor_area ? parseInt(f.floor_area) : null,
          erf_size:   f.erf_size   ? parseInt(f.erf_size)   : null,
          prop_type:  f.prop_type  || null,
          listing_type: f.listing_type || null,
          structured_fields:JSON.stringify({...f, _gate:sbState.gate||''})
        })
      });
      if(!rawRes.ok){
        let detail='Server error '+rawRes.status;
        try{ const j=await rawRes.json(); detail=j.detail||j.message||detail; }catch(_){}
        if(rawRes.status===402){
          if(errEl){errEl.innerHTML=`<strong>Listing slot limit reached.</strong><br>${detail}<br><a href="#" onclick="event.preventDefault();openPlans('sell',true)" style="font-size:12px;color:#7c3aed;font-weight:700;margin-top:6px;display:inline-block;">View plans &amp; upgrade →</a>`;errEl.style.display='block';}
        } else {
          if(errEl){errEl.innerHTML=`<strong>Couldn't publish your listing.</strong><br>${detail}<br><span style="font-size:11px;color:var(--text-3);margin-top:4px;display:block;">Check your details and try again, or go back to edit.</span>`;errEl.style.display='block';}
        }
        if(btn){btn.textContent='Publish listing →';btn.style.opacity='1';btn.style.pointerEvents='auto';}
        return;
      }
      const res=await rawRes.json();
      if(res&&res.id) listingId=res.id;
    }
    // Upload selfie if provided
    if(BEA_ENABLED && sbState.selfieUrl && email){
      const fd=new FormData();
      const blob=await (await fetch(sbState.selfieUrl)).blob();
      fd.append('file',blob,'selfie.jpg');
      await fetch(BEA_URL+`/users/${encodeURIComponent(email)}/photo`,{method:'POST',headers:{'X-Api-Key':API_KEY},body:fd}).catch(()=>{});
    }
    // Upload all listing photos (first is primary)
    if(BEA_ENABLED && sbState.photos.length>0 && listingId){
      for(let pi=0;pi<sbState.photos.length;pi++){
        const pfd=new FormData();
        const pblob=await (await fetch(sbState.photos[pi].dataUrl)).blob();
        pfd.append('file',pblob,'photo_'+pi+'.jpg');
        pfd.append('listing_id',listingId);
        if(pi===0) pfd.append('is_primary','true');
        // Pass caption so BEA can encode it into the [photos:url::caption|...] prefix
        const cap=(sbState.photos[pi].caption||'').replace(/[|\[\]]/g,' ').trim();
        if(cap) pfd.append('caption',cap);
        await fetch(BEA_URL+'/listings/photo',{method:'POST',headers:{'X-Api-Key':API_KEY},body:pfd}).catch(()=>{});
      }
    }
    // Show success
    const st=document.getElementById('sb-success-title');
    if(st) st.textContent=`"${title}" is live on TrustSquare.`;
    sbGoStep('success');
    showToast('✓ Listing published!');
    loadLiveListings();

    // Banking nudge — show if seller has no banking details
    if(!sbState._hasBanking){
      const _sbBankNudge=document.getElementById('sb-banking-nudge');
      if(_sbBankNudge) _sbBankNudge.style.display='flex';
    }
  } catch(err){
    const msg=err&&err.message?err.message:'Unknown error';
    if(errEl){errEl.innerHTML=`<strong>Couldn't publish your listing.</strong><br>${msg}<br><span style="font-size:11px;color:var(--text-3);margin-top:4px;display:block;">Check your connection and try again.</span>`;errEl.style.display='block';}
    if(btn){btn.textContent='Publish listing →';btn.style.opacity='1';btn.style.pointerEvents='auto';}
  }
}

// ── CSS class needed for gate buttons ──────────────────────
// Injected at runtime so no separate stylesheet edit needed
(function(){
  const s=document.createElement('style');
  s.textContent=`.sb-gate-btn{flex:1;padding:10px 8px;border-radius:10px;border:1.5px solid var(--border);background:var(--surface-2);color:var(--text);font-size:12px;font-weight:600;cursor:pointer;font-family:'Syne',sans-serif;transition:all .15s;}
.pub-step-pill{font-size:10px;font-weight:700;color:var(--accent);letter-spacing:.8px;text-transform:uppercase;margin-bottom:2px;}`;
  document.head.appendChild(s);
})();

// Legacy stubs — kept for any remaining references
function goPhase(p){ resetPublish(); }
function showPhase(p){ resetPublish(); }
function handleImg(e){ paHandleImg(e); }
function clearImg(e){ paClearImg(e); }
function selCatBig(c){ paSelCat(c); }
function goPhaseB2OrC(){ paGoStep(3); }
function selAdvSubcat(s){ paSelCat(s); }
function doPublish(){ paDoPublish(); }
function submitClaim(){ goTo('dashboard'); }
function skipClaim(){ goTo('browse'); }

// ── DASHBOARD STATE ───────────────────────────────────────
// Populated by loadLiveDash() from BEA. Empty until seller claims listings.
const dashState = {
  listings: []
};

function renderDash(){
  updateDashStats();
  document.getElementById('my-listings').innerHTML = dashState.listings.map(dl => renderDashCard(dl)).join('');
  // Show draft resume banner if an unfinished sell-flow draft exists
  sbShowDashDraftBanner();
}

async function sbShowDashDraftBanner(){
  try {
    const draft=await aaDB.get(sbDraftKey());
    const el=document.getElementById('dash-draft-banner');
    if(!draft||!draft.state||!draft.state.cat){
      if(el) el.remove(); return;
    }
    if(el) return; // already showing
    const saved=new Date(draft.saved_at);
    const banner=document.createElement('div');
    banner.id='dash-draft-banner';
    banner.style.cssText='margin:0 16px 16px;background:rgba(37,99,235,.07);border:1px solid rgba(37,99,235,.2);border-radius:12px;padding:14px 16px;display:flex;align-items:center;justify-content:space-between;gap:12px;';
    banner.innerHTML=`<div>
        <div style="font-size:13px;font-weight:700;color:#2563eb;">Unfinished listing</div>
        <div style="font-size:12px;color:var(--text-3);margin-top:2px;">${draft.state.cat} · saved ${saved.toLocaleDateString()}</div>
      </div>
      <div style="display:flex;gap:8px;flex-shrink:0;">
        <button onclick="goTo('sell-b')" style="background:#2563eb;color:#fff;border:none;border-radius:50px;padding:8px 16px;font-family:'Syne',sans-serif;font-size:12px;font-weight:700;cursor:pointer;">Resume →</button>
        <button onclick="sbDiscardDraft();document.getElementById('dash-draft-banner').remove();" style="background:none;border:1px solid var(--border);border-radius:50px;padding:8px 12px;font-family:'Inter',sans-serif;font-size:12px;cursor:pointer;color:var(--text-3);">Discard</button>
      </div>`;
    const myListings=document.getElementById('my-listings');
    if(myListings) myListings.parentNode.insertBefore(banner, myListings);
  } catch(e){}
}

function updateDashStats(){
  const pending = dashState.listings.reduce((a,dl)=>a+dl.intros.filter(i=>i.status==='pending').length,0);
  const active  = dashState.listings.filter(dl=>dl.status==='active').length;
  const ad=document.getElementById('dash-active');  if(ad)ad.textContent=active;
  const pd=document.getElementById('dash-pending'); if(pd)pd.textContent=pending;
  const qd=document.getElementById('dash-queue');   if(qd)qd.textContent=dashState.listings.filter(dl=>!dl.isCommit).reduce((a,dl)=>a+dl.intros.filter(i=>i.status==='pending').length,0);
  const td=document.getElementById('dash-tn');      if(td)td.textContent=tuppence;
}

function renderDashCard(dl){
  const pendingIntros = dl.intros.filter(i=>i.status==='pending');
  const thumbHtml = dl.photo
    ? `<img src="${dl.photo}" style="width:100%;height:100%;object-fit:cover;" loading="lazy">`
    : CATS[dl.cat].icon;
  const statusBadge = dl.status==='paused'
    ? '<span class="ml-status st-paused">⏸ Paused — intro pending</span>'
    : pendingIntros.length>0
    ? `<span class="ml-status st-queue">👥 ${pendingIntros.length} request${pendingIntros.length>1?'s':''} waiting</span>`
    : '<span class="ml-status st-active">● Active</span>';

  const introsHtml = pendingIntros.map(intro => `
    <div style="background:var(--surface-2);border:1px solid var(--border);border-radius:var(--r-sm);padding:10px 12px;margin-top:8px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
        <div style="font-size:12px;font-weight:700;color:var(--navy);">🙋 ${intro.name}</div>
        <div style="font-size:10px;color:var(--text-3);">${intro.time}</div>
      </div>
      <div style="font-size:12px;color:var(--text-2);margin-bottom:10px;line-height:1.5;font-style:italic;">"${intro.msg}"</div>
      <div style="display:flex;gap:8px;">
        <button class="mla-btn accent" style="flex:1;padding:7px 0;text-align:center;"
          onclick="handleIntro('${dl.id}','${intro.id}','accept')">✓ Accept · 1T</button>
        <button class="mla-btn danger" style="flex:1;padding:7px 0;text-align:center;"
          onclick="handleIntro('${dl.id}','${intro.id}','decline')">✕ Decline</button>
      </div>
    </div>`).join('');

  // ── World Heritage auto-link banners ──────────────────────
  let wonderBanners = '';
  if (dl.beaListingId && dl._raw && dl._raw.linked_wonders) {
    let linked = [];
    try { linked = JSON.parse(dl._raw.linked_wonders); } catch(e) {}
    const autoLinked = linked.filter(w => w.auto_linked);
    autoLinked.forEach(w => {
      const bannerKey = 'wab_dismissed_' + dl.beaListingId + '_' + w.id;
      const dismissed = localStorage.getItem(bannerKey);
      if (dismissed && Date.now() < parseInt(dismissed)) return; // still dismissed
      // Find wonder name from cache
      const wInfo = (_wpAllWonders || []).find(x => x.id === w.id);
      const wName = wInfo ? wInfo.name : w.id;
      wonderBanners += `<div class="wonder-autolink-banner" id="wab-${dl.beaListingId}-${w.id}">
        <div class="wab-icon">🌍</div>
        <div class="wab-body">
          <div class="wab-title">Linked to ${wName}</div>
          <div>Your listing is highlighted near this World Heritage site. Buyers exploring this wonder may discover your listing.</div>
          <div class="wab-btns">
            <button class="wab-btn-keep" onclick="wabDismiss(${dl.beaListingId},'${w.id}')">Keep it ✓</button>
            <button class="wab-btn-remove" onclick="wabRemove(${dl.beaListingId},'${w.id}','${wName.replace(/'/g,"\\'")}')">Remove</button>
          </div>
        </div>
      </div>`;
    });
  }

  return `<div class="mlcard ${dl.status==='paused'?'paused-card':pendingIntros.length>0?'queue-card':''}" id="dcard-${dl.id}">
    <div class="mlthumb" style="background:${CATS[dl.cat].bg}">${thumbHtml}</div>
    <div class="mlinfo" style="width:100%;">
      <div class="mltitle">${dl.title}</div>
      <div class="mlcat">${dl.cat === 'LocalMarket' ? 'Local Market' : dl.cat}</div>
      ${statusBadge}
      ${wonderBanners}
      ${introsHtml}
      ${pendingIntros.length===0 && dl.beaListingId?`<div class="ml-actions"><button class="mla-btn" onclick="openEditListing(${dl.beaListingId})">Edit</button><button class="mla-btn" onclick="showToast('Pause coming soon')">Pause</button></div>`:''}
    </div>
  </div>`;
}

// ── Wonder auto-link banner actions ────────────────────────────────────────
function wabDismiss(listingId, wonderId) {
  const key = 'wab_dismissed_' + listingId + '_' + wonderId;
  localStorage.setItem(key, Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 days
  const el = document.getElementById('wab-' + listingId + '-' + wonderId);
  if (el) el.remove();
}

async function wabRemove(listingId, wonderId, wonderName) {
  const sellerEmail = (SELLERS[0] && SELLERS[0]._email) || localStorage.getItem('ms_aa_email') || '';
  if (!sellerEmail) { showToast('Sign in to manage wonders'); return; }
  try {
    const resp = await fetch(BEA_URL + '/listings/' + listingId + '/wonders/' + wonderId + '?email=' + encodeURIComponent(sellerEmail), {
      method: 'DELETE'
    });
    if (!resp.ok) throw new Error('API ' + resp.status);
    // Remove from _raw so it doesn\'t reappear
    const dl = dashState.listings.find(d => d.beaListingId === listingId);
    if (dl && dl._raw && dl._raw.linked_wonders) {
      try {
        let linked = JSON.parse(dl._raw.linked_wonders);
        linked = linked.filter(w => w.id !== wonderId);
        dl._raw.linked_wonders = JSON.stringify(linked);
      } catch(e) {}
    }
    const el = document.getElementById('wab-' + listingId + '-' + wonderId);
    if (el) el.remove();
    showToast(wonderName + ' removed from your listing');
  } catch(e) {
    showToast('Could not remove — try again');
  }
}

async function handleIntro(dlId, introId, action){
  const dl = dashState.listings.find(d=>d.id===dlId);
  const intro = dl ? dl.intros.find(i=>i.id===introId) : null;
  if(!intro) return;
  if(action==='accept'){
    if(tuppence<1){ showToast('Not enough Tuppence — top up first'); return; }
    tuppence -= 1;
    updateTuppenceUI();
    addTx(`Intro accepted · ${intro.name}`, dl.title, '−1T', false);
    intro.status = 'accepted';
    dl.status = 'active';
    const listing = LISTINGS.find(l=>l.title===dl.title);
    if(listing) acceptedIntros.add(`${listing.sellerIdx}-${listing.id}`);
    showToast(`✓ Accepted — ${intro.name}'s contact revealed. 1T deducted.`);
    // Post to BEA if live intro
    if(BEA_ENABLED && intro.beaId){
      await apiPut('/intros/'+intro.beaId+'/accept');
    }
  } else {
    intro.status = 'declined';
    dl.status = 'active';
    showToast(`Declined — ${intro.name} notified. Listing reactivated.`);
    // Post to BEA if live intro
    if(BEA_ENABLED && intro.beaId){
      await apiPut('/intros/'+intro.beaId+'/decline');
    }
  }
  renderDash();
  updateTuppenceUI();
}

function renderRecruit(){
  const body=document.getElementById('rec-body');if(!body)return;
  body.innerHTML=Object.entries(PROSPECTS).map(([cat,list])=>{
    const joined=list.filter(p=>p.status==='joined').length;
    const pct=Math.round((joined/20)*100);
    const statusMap={prospect:'rs-p',invited:'rs-i',joined:'rs-j'};
    const statusLabel={prospect:'Prospect',invited:'Invited',joined:'Joined'};
    return`<div class="rec-cat-sec">
      <div class="rec-cat-head"><div class="rec-cat-name">${CATS[cat].icon} ${cat}</div><div class="rec-prog">${joined} / 20 joined</div></div>
      <div class="rec-pbar"><div class="rec-pfill" style="width:${pct}%"></div></div>
      <div class="rec-table">${list.map(p=>`<div class="rec-row"><div class="rec-name">${p.name}</div><div class="rec-city">${p.city}</div><span class="rec-stat ${statusMap[p.status]}">${statusLabel[p.status]}</span></div>`).join('')}</div>
      <button class="add-btn" onclick="showToast('Add prospect — BEA coming')">+ Add prospect</button>
    </div>`;
  }).join('');
}

// ── EDIT LISTING (seller edit-after-publish) ──────────────
let elCurrentId   = null;   // beaListingId (integer)
let elCurrentCat  = null;   // category string e.g. 'Property'
let elCurrentRaw  = null;   // full BEA listing object
let elAISuggestions = {};   // { fieldId: {suggestion, reason} }

// Entry point — called from Edit button in renderDashCard
// Async: fetches listing data from BEA on demand if not already cached in _raw
async function openEditListing(beaId) {
  if (!beaId) { showToast('Cannot edit this listing'); return; }

  let dl = dashState.listings.find(d => d.beaListingId === beaId);

  // If _raw is missing (e.g. listing came from the intros path, not /listings/mine)
  // fetch it directly from GET /listings/{id}
  if (!dl || !dl._raw) {
    showToast('Loading listing…');
    try {
      const raw = await apiGet('/listings/' + beaId);
      if (!raw || !raw.id) { showToast('Listing not found on server'); return; }
      if (!dl) {
        dl = {
          id: 'bea_dl_' + beaId,
          beaListingId: beaId,
          title: raw.title,
          cat: raw.category,
          status: 'active',
          photo: raw.thumb_url || null,
          isCommit: raw.category === 'Property',
          intros: [],
          _raw: raw
        };
        dashState.listings.push(dl);
      } else {
        dl._raw = raw;
        dl.cat  = dl.cat || raw.category;
      }
    } catch(e) {
      showToast('Could not load listing details — check your connection');
      return;
    }
  }

  elCurrentId  = beaId;
  elCurrentCat = normCat(dl.cat || dl._raw.category || '');
  elCurrentRaw = dl._raw;
  // Derive gate-aware category for trust score panel (Property_private / Property_agent)
  try {
    const _sf = JSON.parse(elCurrentRaw.structured_fields || '{}');
    const _gate = _sf._gate || '';
    if ((elCurrentCat === 'Property' || elCurrentCat === 'Cars') && _gate) {
      elCurrentCat = elCurrentCat + '_' + _gate; // e.g. 'Property_private'
    }
  } catch(e) {}
  elAISuggestions = {};

  // Category badge
  const catDef = AA_CATEGORIES[elCurrentCat] || {};
  const badge  = document.getElementById('el-cat-badge');
  if (badge) badge.innerHTML = `${catDef.emoji || '📋'} ${elCurrentCat}`;

  // Clear AI output
  const aiOut = document.getElementById('el-ai-output');
  if (aiOut) { aiOut.innerHTML = ''; }

  // Show Yield button only for Property category
  const yieldBtn = document.getElementById('el-yield-btn');
  if (yieldBtn) {
    const isProperty = elCurrentCat.toLowerCase().startsWith('property');
    yieldBtn.style.display = isProperty ? '' : 'none';
  }

  // Render form and navigate
  renderEditForm(elCurrentRaw);
  elRenderPhotos(elCurrentRaw, '');
  window._currentEditBeaId = beaId;
  goTo('edit-listing');

  // Load Trust Score + Document Hub + AI Guidance after navigation
  wpInit(beaId);
  const sellerEmail = (SELLERS[0] && SELLERS[0]._email) || localStorage.getItem('ms_aa_email') || '';
  if (sellerEmail) {
    setTimeout(() => elLoadSidebarPanels(sellerEmail, elCurrentCat), 200);
  }
}

async function elLoadSidebarPanels(email, category) {
  // ── Trust Score panel ──
  const tshSec = document.getElementById('el-tsh-section');
  if (tshSec) {
    tshSec.style.display = 'block';
    tshSec.innerHTML = '<div style="font-size:13px;color:var(--text-3);padding:10px 0;">⏳ Loading Trust Score…</div>';
    try {
      const catParam = category ? '&category=' + encodeURIComponent(category) : '';
      const ts = await apiGet('/trust-score/breakdown?email=' + encodeURIComponent(email) + catParam);
      if (ts && ts.score !== undefined) {
        const tierColor = ts.tier_color === 'green' ? '#059669' : ts.tier_color === 'blue' ? '#2563eb' : '#6b7280';
        const next = ts.next_tier
          ? `<div style="font-size:11px;color:var(--text-3);margin-top:4px;">Next: <strong>${ts.next_tier.name}</strong> — ${ts.next_tier.delta} more pts</div>`
          : '';
        const tip = ts.haiko_tip
          ? `<div style="background:#fef3c7;border:1px solid #fbbf24;border-radius:8px;padding:9px 11px;margin-top:10px;font-size:12px;color:#92400e;line-height:1.5;">
               💡 <strong>Best next step:</strong> ${ts.haiko_tip.text}
               ${ts.haiko_tip.points_available ? '<div style="margin-top:4px;font-weight:700;">+' + ts.haiko_tip.points_available + ' pts available</div>' : ''}
             </div>` : '';
        const pendingPts   = ts.pending_points || 0;
        const earnedAboveBase = Math.max(0, ts.score - 40);
        const pendingBar   = pendingPts > 0
          ? `<div style="background:#fbbf24;width:${Math.min(pendingPts, 100 - ts.score)}%;height:100%;border-radius:4px;"></div>` : '';
        const pendingBadge = pendingPts > 0
          ? `<div style="display:flex;align-items:center;gap:6px;margin-top:5px;font-size:11px;color:#92400e;background:#fef3c7;border-radius:6px;padding:4px 8px;">
               ⏳ <strong>+${pendingPts} pts pending</strong> — uploading more evidence will raise your score
             </div>` : '';
        const baseBadge = ts.score >= 40
          ? `<div style="font-size:11px;color:var(--text-3);margin-top:3px;">Base 40 + <strong style="color:${tierColor};">+${earnedAboveBase} earned</strong></div>` : '';
        tshSec.innerHTML = `
          <div style="border:1.5px solid var(--border);border-radius:12px;overflow:hidden;">
            <div style="background:var(--surface-2);padding:10px 14px;display:flex;align-items:center;justify-content:space-between;">
              <div style="font-size:13px;font-weight:700;color:var(--text);">⭐ Trust Score</div>
              <div style="font-size:13px;font-weight:700;color:${tierColor};">${ts.score} / 100</div>
            </div>
            <div style="padding:10px 14px;">
              <div style="background:var(--surface-2);border-radius:4px;height:8px;overflow:hidden;margin-bottom:4px;display:flex;">
                <div style="background:#d1d5db;width:40%;height:100%;border-radius:4px 0 0 4px;" title="Base score (40)"></div>
                <div style="background:${tierColor};width:${earnedAboveBase}%;height:100%;" title="Earned credentials"></div>
                ${pendingBar}
              </div>
              <div style="font-size:12px;font-weight:700;color:${tierColor};">${ts.tier || ''}</div>
              ${baseBadge}${next}${pendingBadge}${tip}
            </div>
          </div>`;
      } else { tshSec.style.display = 'none'; }
    } catch(e) { tshSec.style.display = 'none'; }
  }

  // ── AI Guidance panel ──
  const agSec = document.getElementById('el-aiguidance-section');
  if (agSec && category) {
    agSec.style.display = 'block';
    agSec.innerHTML = '<div style="font-size:12px;color:var(--text-3);padding:6px 0;">✨ Generating Trust Score action plan…</div>';
    try {
      const g = await apiPostAuth('/trust-score/guidance', { email, category });
      if (g && g.guidance) {
        agSec.innerHTML = `
          <div style="border:1.5px solid #a78bfa;border-radius:12px;overflow:hidden;background:linear-gradient(135deg,#f5f3ff,#ede9fe);">
            <div style="padding:10px 14px;font-size:13px;font-weight:700;color:#5b21b6;">✨ Trust Score Action Plan</div>
            <div style="padding:0 14px 12px;font-size:12px;color:#374151;line-height:1.6;">${g.guidance.replace(/\n/g,'<br>')}</div>
          </div>`;
      } else { agSec.style.display = 'none'; }
    } catch(e) { agSec.style.display = 'none'; }
  }

  // ── Document Hub ──
  const dhSec = document.getElementById('el-dochub-section');
  if (dhSec) {
    dhSec.style.display = 'block';
    dhSec.innerHTML = '<div style="font-size:13px;color:var(--text-3);padding:10px 0;">⏳ Loading documents…</div>';
    try {
      const [docs, tsData] = await Promise.all([
        apiGetAuth('/users/' + encodeURIComponent(email) + '/documents' + (category ? '?category=' + encodeURIComponent(category) : '')).catch(() => []),
        apiGet('/trust-score/breakdown?email=' + encodeURIComponent(email) + (category ? '&category=' + encodeURIComponent(category) : '')).catch(() => null)
      ]);
      // Extract declarable signals from all category items
      const declarableItems = [];
      if (tsData && tsData.groups) {
        const allItems = [
          ...(tsData.groups.category?.items || []),
          ...(tsData.groups.universal?.items || []),
          ...(tsData.groups.track_record?.items || []),
        ];
        allItems.forEach(it => {
          if (it.has_declaration && it.status !== 'earned') {
            declarableItems.push(it);
          }
        });
      }
      dhSec.innerHTML = elRenderDocHub(docs || [], email, declarableItems);
    } catch(e) {
      dhSec.innerHTML = elRenderDocHub([], email, []);
    }
  }
}

// Resolve the field list for a given category + service class
function _elGetFields(cat, serviceClass) {
  const catDef = AA_CATEGORIES[cat];
  if (!catDef) return [];
  if (cat === 'Services' && catDef.serviceClasses) {
    const sc = serviceClass || 'Technical';
    return ((catDef.serviceClasses[sc] || catDef.serviceClasses['Technical']) || {}).fields || [];
  }
  return catDef.fields || [];
}

// Map BEA listing object keys to AA field IDs
function _elFieldVal(raw, fieldId) {
  // For Property listings created before dedicated columns existed,
  // fall back to parsing values from the description text.
  const desc = raw.description || '';
  function parseDescNum(pattern) {
    const m = desc.match(pattern);
    return m ? m[1] : '';
  }
  function parseDescPropType() {
    const known = ['Apartment / Flat','Bachelor / Studio','Granny Flat','Land / Plot','Smallholding','Townhouse','Penthouse','Cluster','Simplex','Duplex','Commercial','Industrial','Farm','House','Other'];
    for (const pt of known) { if (desc.includes(pt)) return pt; }
    return '';
  }

  const map = {
    title:        raw.title        || '',
    price:        (raw.price || '').replace(/[^0-9.]/g, '') || '',
    rate:         (raw.price || '').replace(/[^0-9.]/g, '') || '',
    desc:         desc,
    suburb:       raw.suburb       || '',
    area:         raw.area || raw.suburb || '',
    prop_type:    raw.prop_type    || parseDescPropType(),
    beds:         raw.beds    != null && raw.beds    !== 0 ? String(raw.beds)    : parseDescNum(/(\d+)[-\s]*bed/i),
    baths:        raw.baths   != null && raw.baths   !== 0 ? String(raw.baths)   : parseDescNum(/(\d+)[-\s]*bath/i),
    garages:      raw.garages != null && raw.garages !== 0 ? String(raw.garages) : parseDescNum(/(\d+)[-\s]*garage/i),
    floor_area:   raw.floor_area   != null ? String(raw.floor_area)   : parseDescNum(/(\d+)\s*m²?\s*(floor|internal|living)/i),
    erf_size:     raw.erf_size     != null ? String(raw.erf_size)     : parseDescNum(/(\d+)\s*m²?\s*(erf|plot|stand)/i),
    listing_type: raw.listing_type || (/for rent|per month|monthly rent|to let|to-let|rental/i.test(desc) ? 'For Rent' : /for sale|asking price|selling price/i.test(desc) ? 'For Sale' : ''),
    subject:      raw.subject      || '',
    level:        raw.level        || '',
    mode:         raw.mode         || '',
    service_class: raw.service_class || '',
    service_type:  raw.service_type  || '',
    availability:  raw.availability  || '',
  };
  return map[fieldId] !== undefined ? map[fieldId] : '';
}

// Build the edit form — mirrors AA field definitions but pre-populated & AI suggestions optional
function renderEditForm(raw) {
  const fields = _elGetFields(elCurrentCat, raw.service_class);
  const container = document.getElementById('el-form-fields');
  if (!container) return;

  container.innerHTML = fields.map(f => {
    const val = _elFieldVal(raw, f.id);
    const sug = elAISuggestions[f.id];
    const sugHtml = sug
      ? `<div class="el-sug-pill">✨ <strong>Suggestion:</strong> ${sug.suggestion}<br>
         <span style="font-size:10px;opacity:.7">${sug.reason}</span><br>
         <button class="el-sug-apply" onclick="elApplySuggestion('${f.id}')">Apply</button></div>`
      : '';

    if (f.type === 'textarea') {
      return `<div class="el-field">
        <label>${f.label}</label>
        <textarea id="elf-${f.id}" placeholder="${f.placeholder || ''}">${val}</textarea>
        ${sugHtml}</div>`;
    }
    if (f.type === 'select') {
      const opts = (f.options || []).map(o =>
        `<option value="${o}"${val===o?' selected':''}>${o}</option>`).join('');
      return `<div class="el-field">
        <label>${f.label}</label>
        <select id="elf-${f.id}"><option value="">— select —</option>${opts}</select>
        ${sugHtml}</div>`;
    }
    if (f.type === 'multiselect') {
      // Render as editable text (comma-separated) — keeps the edit form simple
      return `<div class="el-field">
        <label>${f.label} <span style="font-weight:400;text-transform:none;font-size:10px;">(comma-separated)</span></label>
        <input type="text" id="elf-${f.id}" value="${val}" placeholder="${f.placeholder || ''}">
        ${sugHtml}</div>`;
    }
    if (f.type === 'rate') {
      return `<div class="el-field">
        <label>${f.label}</label>
        <input type="text" id="elf-${f.id}" value="${val}" placeholder="${f.placeholder || ''}">
        ${sugHtml}</div>`;
    }
    // Default: text / number
    return `<div class="el-field">
      <label>${f.label}</label>
      <input type="text" id="elf-${f.id}" value="${val}" placeholder="${f.placeholder || ''}">
      ${sugHtml}</div>`;
  }).join('');
}

// Apply an AI suggestion directly into the field
function elApplySuggestion(fieldId) {
  const sug = elAISuggestions[fieldId];
  if (!sug) return;
  const el = document.getElementById('elf-' + fieldId);
  if (el) { el.value = sug.suggestion; showToast('✓ Suggestion applied'); }
}

// ── EDIT SCREEN PHOTO SECTION ─────────────────────────────
// Shows current listing photos with Replace button.
// AI photo warnings (from anonymity_warning or trust_score_actions) appear
// as amber notes below the relevant photo.

let _elPhotoWarning = '';  // AI photo feedback text, set by editAISuggest

// Module-level photo array for the listing being edited
let _elPhotoUrls = [];

function elRenderPhotos(raw, photoWarning) {
  const section  = document.getElementById('el-photos-section');
  const photoRow = document.getElementById('el-photo-row');
  if (!section || !photoRow) return;

  // Only re-read from raw on initial load (when _elPhotoUrls is empty).
  // After that, callers maintain _elPhotoUrls directly so we never
  // overwrite an in-progress local array with a stale BEA snapshot.
  if (!_elPhotoUrls.length) {
    try {
      if (raw.photo_urls) {
        const parsed = typeof raw.photo_urls === 'string' ? JSON.parse(raw.photo_urls) : raw.photo_urls;
        if (Array.isArray(parsed) && parsed.length) _elPhotoUrls = parsed;
      }
    } catch(e) {}
    if (!_elPhotoUrls.length) {
      if (raw.medium_url) _elPhotoUrls = [raw.medium_url];
      else if (raw.thumb_url) _elPhotoUrls = [raw.thumb_url];
    }
  }

  section.style.display = 'block';
  const warnLower = (photoWarning || '').toLowerCase();
  const hasPhotoIssue = warnLower.includes('photo') || warnLower.includes('watermark') ||
                        warnLower.includes('logo') || warnLower.includes('name') ||
                        warnLower.includes('text') || warnLower.includes('image');

  photoRow.innerHTML = _elPhotoUrls.map((url, i) => `
    <div class="el-photo-card" id="el-pcard-${i}">
      <img src="${url}" alt="Photo ${i+1}" referrerpolicy="no-referrer">
      ${i === 0 ? '<div style="font-size:9px;font-weight:700;color:var(--accent-bright);text-align:center;margin-top:3px;letter-spacing:.3px;">CARD VIEW</div>' : ''}
      ${hasPhotoIssue && i===0 ? '<div class="el-photo-warn">!</div>' : ''}
      <div style="display:flex;gap:4px;margin-top:5px;">
        <button class="el-photo-replace" onclick="elTriggerPhotoReplace(${i})" style="flex:1;">🔄</button>
        <button class="el-photo-replace" onclick="elRemovePhoto(${i})" style="flex:0 0 32px;color:#ef4444;">✕</button>
      </div>
      ${hasPhotoIssue && i===0 ? `<div class="el-photo-ai-note">⚠️ ${photoWarning}</div>` : ''}
    </div>`).join('') +
    (_elPhotoUrls.length < 10 ? `
    <div class="el-photo-card" style="display:flex;align-items:center;justify-content:center;">
      <label style="display:flex;flex-direction:column;align-items:center;justify-content:center;width:120px;height:90px;border:2px dashed var(--border);border-radius:10px;cursor:pointer;color:var(--text-3);font-size:11px;gap:4px;">
        <span style="font-size:24px;">＋</span>Add Photo
        <input type="file" accept="image/*" style="display:none" onchange="elAddPhoto(event)">
      </label>
    </div>` : '');

  // Update photo status text
  const statusEl = document.getElementById('el-photo-status');
  if (statusEl) statusEl.textContent = _elPhotoUrls.length + ' photo' + (_elPhotoUrls.length !== 1 ? 's' : '');
}

function elRemovePhoto(idx) {
  _elPhotoUrls.splice(idx, 1);
  if (elCurrentRaw) {
    elCurrentRaw.photo_urls = JSON.stringify(_elPhotoUrls);
    // Keep thumb/medium in sync with position 0
    if (_elPhotoUrls.length) {
      elCurrentRaw.thumb_url  = _elPhotoUrls[0];
      elCurrentRaw.medium_url = _elPhotoUrls[0];
    }
  }
  elRenderPhotos(elCurrentRaw || {photo_urls: JSON.stringify(_elPhotoUrls)}, '');
  showToast('Photo removed — tap Save Changes to apply');
}

async function elAddPhoto(event) {
  const file = event.target.files[0];
  if (!file || !elCurrentId) return;
  if (_elPhotoUrls.length >= 10) { showToast('Maximum 10 photos'); return; }
  showToast('⏳ Uploading photo…');
  const fd = new FormData();
  fd.append('file', file);
  try {
    const res = await fetch(BEA_URL + '/listings/photo', {
      method: 'POST', headers: { 'X-Api-Key': API_KEY }, body: fd
    });
    if (!res.ok) throw new Error('Upload failed');
    const data = await res.json();
    _elPhotoUrls.push(data.medium_url || data.thumb_url);
    if (elCurrentRaw) elCurrentRaw.photo_urls = JSON.stringify(_elPhotoUrls);
    elRenderPhotos(elCurrentRaw || {photo_urls: JSON.stringify(_elPhotoUrls)}, '');
    // Auto-save photos immediately
    const sellerEmail = (SELLERS[0] && SELLERS[0]._email) || localStorage.getItem('ms_aa_email') || '';
    if (sellerEmail && elCurrentId) {
      const photoPayload = { photo_urls: JSON.stringify(_elPhotoUrls) };
      if (_elPhotoUrls.length >= 1) {
        // Always use position-0 as the card thumbnail, not the newly uploaded photo
        photoPayload.thumb_url  = _elPhotoUrls[0];
        photoPayload.medium_url = _elPhotoUrls[0];
      }
      await fetch(BEA_URL + '/listings/' + elCurrentId + '?email=' + encodeURIComponent(sellerEmail),
        { method: 'PUT', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(photoPayload) });
    }
    showToast('✅ Photo added and saved');
  } catch(e) { showToast('Photo upload failed: ' + e.message); }
  event.target.value = '';
}

let _elPhotoReplaceIdx = 0;
function elTriggerPhotoReplace(idx) {
  _elPhotoReplaceIdx = idx;
  const inp = document.getElementById('el-photo-inp');
  if (inp) inp.click();
}

async function elReplacePhoto(event) {
  const file = event.target.files[0];
  if (!file || !elCurrentId) return;
  showToast('Uploading photo…');

  const fd = new FormData();
  fd.append('file', file);
  fd.append('listing_id', String(elCurrentId));

  try {
    const res = await fetch(BEA_URL + '/listings/photo', {
      method: 'POST',
      headers: { 'X-Api-Key': API_KEY },
      body: fd
    });
    if (!res.ok) throw new Error('Upload failed');
    const data = await res.json();

    // Update the displayed photo immediately
    const card = document.getElementById('el-pcard-' + _elPhotoReplaceIdx);
    if (card) {
      const img = card.querySelector('img');
      if (img && data.medium_url) img.src = data.medium_url;
      // Remove the warning once replaced
      const note = card.querySelector('.el-photo-ai-note');
      const warn = card.querySelector('.el-photo-warn');
      if (note) note.remove();
      if (warn) warn.remove();
    }

    // Patch the raw object so Save picks up the new URLs
    if (elCurrentRaw) {
      elCurrentRaw.thumb_url  = data.thumb_url  || elCurrentRaw.thumb_url;
      elCurrentRaw.medium_url = data.medium_url || elCurrentRaw.medium_url;
    }

    showToast('✓ Photo replaced — tap Save Changes to apply');
  } catch(e) {
    showToast('Photo upload failed: ' + e.message);
  }

  // Reset file input so the same file can be re-selected if needed
  event.target.value = '';
}

// Collect form field values into a plain object
function _elCollectFields() {
  const fields = _elGetFields(elCurrentCat, elCurrentRaw && elCurrentRaw.service_class);
  const data = {};
  fields.forEach(f => {
    const el = document.getElementById('elf-' + f.id);
    if (el) data[f.id] = el.value.trim();
  });
  return data;
}

// Save edited listing — PUT to BEA, versions the old data automatically
// ── SELLER EDIT: DOCUMENT HUB ─────────────────────────────────────────────
const EL_DOC_LABELS = {
  id_doc:'🪪 ID / Passport', certificate:'🎓 Certificate / Diploma', training:'📚 Training Course',
  membership:'🏛 Association / Body Membership', professional_role:'⭐ Named Role in Association',
  guide:'📖 Product Guide', recipe:'🍯 Recipe / Care Instructions', presentation:'📊 Presentation', other:'📎 Other'
};

// Points available per doc type and how many uploads count
const EL_DOC_STACKING = {
  certificate:       { slots: 3, pts: [7, 5, 3],  hint: 'Up to 3 counted — 7, 5, then 3 pts each' },
  training:          { slots: 2, pts: [4, 3],      hint: 'Up to 2 counted — 4 then 3 pts' },
  membership:        { slots: 2, pts: [8, 6],      hint: 'Up to 2 associations — 8 pts first, +6 pts for a second body' },
  professional_role: { slots: 2, pts: [15, 10],    hint: 'Named role (secretary/chair) = 15 pts — highest single credential. Official government role = 10 pts.' },
  guide:             { slots: 3, pts: [2, 1, 1],   hint: 'Up to 3 counted — 2, 1, then 1 pts each' },
  recipe:            { slots: 3, pts: [2, 1, 1],   hint: 'Up to 3 counted — 2, 1, then 1 pts each' },
  id_doc:            { slots: 1, pts: [9],          hint: 'ID upload + AI verification = up to 9 pts' },
};

function elRenderDocHub(docs, email, declarableItems) {
  declarableItems = declarableItems || [];
  const typeOpts = Object.entries(EL_DOC_LABELS)
    .map(([v,l]) => `<option value="${v}">${l}</option>`).join('');

  const rows = docs.length ? docs.map(d => `
    <div style="display:flex;align-items:center;gap:10px;padding:9px 10px;background:var(--surface-2);border-radius:8px;margin-bottom:6px;">
      <div style="font-size:20px;">${(EL_DOC_LABELS[d.doc_type]||'📎').split(' ')[0]}</div>
      <div style="flex:1;min-width:0;">
        <div style="font-size:13px;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${d.label}</div>
        <div style="font-size:11px;color:var(--text-3);">${EL_DOC_LABELS[d.doc_type]||d.doc_type} · <span style="color:${d.visibility==='post_intro'?'#059669':'#9ca3af'}">${d.visibility==='post_intro'?'👁 Visible after intro':'🔒 Private'}</span></div>
      </div>
      <a href="${d.url}" target="_blank" style="font-size:11px;color:var(--navy);text-decoration:none;">View</a>
    </div>`).join('')
    : '<div style="font-size:12px;color:var(--text-3);padding:4px 0 10px;">No documents uploaded yet.</div>';

  // ── Declaration cards ─────────────────────────────────────────────────────
  // One card per declarable signal that hasn't been fully earned yet.
  // Status 'missing' → declare form. Status 'declared' → evidence nudge.
  const declCards = declarableItems.map(it => {
    const sigId = it.signal_id;
    const safeId = sigId.replace(/\./g, '_');
    const declPts = it.declaration_points || (it.points - (it.evidence_points || 0));
    const evPts   = (it.status === 'declared') ? (it.evidence_points_remaining || 0) : (it.evidence_points || 0);

    if (it.status === 'declared') {
      // Already declared — nudge to upload evidence
      return `
      <div id="decl-card-${safeId}" style="border:1.5px solid #86efac;border-radius:10px;padding:11px 13px;margin-bottom:8px;background:#f0fdf4;">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:8px;">
          <div>
            <div style="font-size:12px;font-weight:700;color:#166534;">✅ Declared — <strong>+${declPts} pts</strong> earned</div>
            <div style="font-size:12px;color:#374151;margin-top:2px;">${it.name}</div>
          </div>
          <div style="font-size:11px;color:#059669;font-weight:700;white-space:nowrap;">+${declPts} pts</div>
        </div>
        ${evPts > 0 ? `
        <div style="margin-top:8px;background:#ecfdf5;border:1px dashed #6ee7b7;border-radius:7px;padding:8px 10px;font-size:11px;color:#065f46;line-height:1.5;">
          📎 <strong>Upload evidence to earn the final ${evPts} pt${evPts>1?'s':''}.</strong><br>
          ${it.how_to_earn || 'Upload a supporting document to complete this credential.'}
        </div>` : ''}
        <div id="decl-status-${safeId}" style="font-size:11px;color:var(--text-3);margin-top:4px;min-height:0;"></div>
      </div>`;
    }

    // Not yet declared — show declaration form
    const prompt = it.declaration_prompt || 'Describe your experience or qualification in your own words.';
    return `
    <div id="decl-card-${safeId}" style="border:1.5px solid #fbbf24;border-radius:10px;padding:11px 13px;margin-bottom:8px;background:#fffbeb;">
      <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:8px;margin-bottom:6px;">
        <div>
          <div style="font-size:12px;font-weight:700;color:#92400e;">📝 Declare to earn <strong>+${declPts} pts now</strong></div>
          <div style="font-size:12px;color:#374151;margin-top:2px;">${it.name}</div>
        </div>
        <div style="font-size:11px;color:#d97706;font-weight:700;white-space:nowrap;">+${declPts}${evPts>0?` / ${it.points}`:''} pts</div>
      </div>
      <textarea id="decl-text-${safeId}" rows="3" placeholder="${prompt}"
        style="width:100%;box-sizing:border-box;background:#fff;border:1.5px solid #fde68a;border-radius:7px;padding:8px 10px;font-size:12px;font-family:inherit;resize:vertical;outline:none;color:#374151;"></textarea>
      ${evPts > 0 ? `<div style="font-size:10px;color:#92400e;margin-top:4px;">After declaring, upload evidence to earn the remaining <strong>+${evPts} pt${evPts>1?'s':''}</strong>.</div>` : ''}
      <div id="decl-status-${safeId}" style="font-size:11px;color:var(--text-3);min-height:14px;margin-top:4px;"></div>
      <button onclick="elSubmitDeclaration('${email}','${sigId}')"
        style="margin-top:8px;width:100%;background:#d97706;color:#fff;border:none;border-radius:50px;padding:9px;font-family:'Syne',sans-serif;font-size:12px;font-weight:700;cursor:pointer;">
        Declare — Earn +${declPts} pts immediately
      </button>
    </div>`;
  }).join('');

  const declSection = declarableItems.length ? `
    <div style="margin-bottom:12px;">
      <div style="font-size:12px;font-weight:700;color:#92400e;margin-bottom:6px;">📝 Professional Declarations</div>
      <div style="font-size:11px;color:var(--text-3);margin-bottom:8px;">Declare your role or experience to earn most points immediately. Upload evidence afterwards to complete each credential.</div>
      ${declCards}
    </div>
    <div style="border-top:1px solid var(--border);margin-bottom:12px;"></div>` : '';

  return `
  <div style="border:1.5px solid #e0e7ff;border-radius:12px;overflow:hidden;">
    <div style="background:#f0f4ff;padding:10px 14px;display:flex;align-items:center;justify-content:space-between;">
      <div style="font-size:13px;font-weight:700;color:#1e3a8a;">📁 Trust Score Documents</div>
      <div style="font-size:11px;color:#6b7280;">Certificates · ID · Guides</div>
    </div>
    <div style="padding:12px 14px;">
      <div style="font-size:11px;color:var(--text-3);margin-bottom:10px;">Private docs used for Trust Score verification. Tick "Visible after intro" to share with buyers.</div>
      ${declSection}
      ${rows}
      <div style="margin-top:10px;border-top:1px solid var(--border);padding-top:12px;">
        <div style="font-size:12px;font-weight:700;margin-bottom:8px;">Upload new document</div>
        <div style="display:grid;gap:8px;">
          <select id="el-dh-type" onchange="elUpdateDocHint(this.value)"
            style="background:var(--surface-2);border:1.5px solid var(--border);border-radius:8px;padding:8px 10px;font-size:13px;">${typeOpts}</select>
          <div id="el-dh-hint" style="font-size:11px;color:#6b7280;background:#f0f9ff;border-radius:6px;padding:5px 9px;display:none;"></div>
          <input type="text" id="el-dh-label" placeholder="Label (e.g. 'Beekeeping Certificate')"
            style="background:var(--surface-2);border:1.5px solid var(--border);border-radius:8px;padding:8px 10px;font-size:13px;outline:none;">
          <label style="display:flex;align-items:center;gap:6px;font-size:12px;cursor:pointer;">
            <input type="checkbox" id="el-dh-postintro" style="width:15px;height:15px;accent-color:var(--green);">
            Visible to buyer after introduction
          </label>
          <label style="display:inline-flex;align-items:center;gap:8px;background:var(--surface-2);border:1.5px dashed var(--border);border-radius:8px;padding:9px 12px;cursor:pointer;font-size:13px;color:var(--text-3);">
            📎 Choose file
            <input type="file" id="el-dh-file" accept=".pdf,.jpg,.jpeg,.png,.webp,.doc,.docx" style="display:none;">
          </label>
          <div id="el-dh-status" style="font-size:11px;color:var(--text-3);min-height:14px;"></div>
          <button onclick="elDocHubUpload('${email}')" style="background:var(--navy);color:#fff;border:none;border-radius:50px;padding:10px;font-family:'Syne',sans-serif;font-size:13px;font-weight:700;cursor:pointer;">Upload Document</button>
        </div>
      </div>
    </div>
  </div>`;
}

function elUpdateDocHint(docType) {
  const hint = document.getElementById('el-dh-hint');
  if (!hint) return;
  const info = EL_DOC_STACKING[docType];
  if (info) {
    hint.textContent = '💡 ' + info.hint;
    hint.style.display = 'block';
  } else {
    hint.style.display = 'none';
  }
}

async function elSubmitDeclaration(email, signalId) {
  const safeId  = signalId.replace(/\./g, '_');
  const textarea = document.getElementById('decl-text-' + safeId);
  const statusEl = document.getElementById('decl-status-' + safeId);
  const card     = document.getElementById('decl-card-' + safeId);
  if (!textarea) return;
  const text = textarea.value.trim();
  if (text.length < 10) {
    if (statusEl) statusEl.textContent = 'Please write at least a sentence describing your experience.';
    return;
  }
  if (statusEl) statusEl.textContent = '⏳ Submitting…';
  try {
    const res = await apiPostAuth('/users/' + encodeURIComponent(email) + '/declare', {
      signal_id: signalId,
      declaration_text: text
    });
    if (res && res.points_awarded > 0) {
      if (statusEl) statusEl.innerHTML =
        `<span style="color:#059669;font-weight:700;">✅ +${res.points_awarded} pts earned!</span>`;
      // Refresh both Trust Score panel and Doc Hub after a short delay
      setTimeout(async () => {
        await elLoadSidebarPanels(email, elCurrentCat);
      }, 600);
    } else if (res && res.already_declared) {
      if (statusEl) statusEl.textContent = 'Already declared — declaration text updated.';
    } else {
      if (statusEl) statusEl.textContent = res?.next_step_message || '✅ Submitted.';
      setTimeout(() => elLoadSidebarPanels(email, elCurrentCat), 800);
    }
  } catch(e) {
    if (statusEl) statusEl.textContent = '⚠️ Could not submit — please try again.';
  }
}

async function elDocHubUpload(email) {
  const fileInput = document.getElementById('el-dh-file');
  const docType   = document.getElementById('el-dh-type')?.value || 'other';
  const label     = document.getElementById('el-dh-label')?.value.trim() || '';
  const postIntro = document.getElementById('el-dh-postintro')?.checked;
  const status    = document.getElementById('el-dh-status');
  if (!fileInput?.files?.length) { if (status) status.textContent = 'Please choose a file first.'; return; }
  const isIdDoc = docType === 'id_doc';
  if (status) status.textContent = isIdDoc ? '⏳ Uploading — AI verification in progress…' : '⏳ Uploading…';
  const fd = new FormData();
  fd.append('file', fileInput.files[0]);
  fd.append('doc_type', docType);
  fd.append('label', label || fileInput.files[0].name);
  fd.append('visibility', postIntro ? 'post_intro' : 'private');
  try {
    const r = await fetch(BEA_URL + '/users/' + encodeURIComponent(email) + '/documents', {
      method: 'POST', headers: { 'X-Api-Key': API_KEY }, body: fd
    });
    if (!r.ok) throw new Error('HTTP ' + r.status);
    const uploadData = await r.json().catch(() => ({}));
    if (status) status.textContent = '✅ Uploaded — fetching AI feedback…';
    // Reload doc list + re-fetch declarations state
    const [docs, tsDataUp] = await Promise.all([
      apiGetAuth('/users/' + encodeURIComponent(email) + '/documents' + (elCurrentCat ? '?category=' + encodeURIComponent(elCurrentCat) : '')).catch(() => []),
      apiGet('/trust-score/breakdown?email=' + encodeURIComponent(email) + (elCurrentCat ? '&category=' + encodeURIComponent(elCurrentCat) : '')).catch(() => null)
    ]);
    const dhSec = document.getElementById('el-dochub-section');
    const declarableItemsUp = [];
    if (tsDataUp && tsDataUp.groups) {
      const allItemsUp = [
        ...(tsDataUp.groups.category?.items || []),
        ...(tsDataUp.groups.universal?.items || []),
        ...(tsDataUp.groups.track_record?.items || []),
      ];
      allItemsUp.forEach(it => { if (it.has_declaration && it.status !== 'earned') declarableItemsUp.push(it); });
    }
    if (dhSec) dhSec.innerHTML = elRenderDocHub(docs, email, declarableItemsUp);
    // AI comment on this upload
    try {
      const commentRes = await apiPostAuth('/trust-score/upload-comment', {
        email,
        category: elCurrentCat || '',
        doc_type: docType,
        label: label || fileInput.files[0].name,
        signal_id: uploadData.signal_id || null
      });
      if (commentRes && commentRes.comment) {
        if (status) status.innerHTML =
          `<div style="background:#f0fdf4;border:1px solid #86efac;border-radius:8px;padding:9px 11px;font-size:12px;color:#166534;line-height:1.5;margin-top:6px;">
             ✨ ${commentRes.comment}
           </div>`;
      } else {
        if (status) status.textContent = '✅ Uploaded — Trust Score signal set to pending';
      }
    } catch(_) {
      if (status) status.textContent = uploadData.auto_earned
        ? '✅ Uploaded — Trust Score updated!'
        : '⏳ Uploaded — AI verification running, score will update shortly';
    }
    // Reload Trust Score panel to show updated points
    elLoadSidebarPanels(email, elCurrentCat);
  } catch(e) {
    if (status) status.textContent = '❌ Upload failed: ' + e.message;
  }
}

// Helper: POST JSON with API key auth (used for seller-facing endpoints)
async function apiPostAuth(path, body) {
  try {
    const r = await fetch(BEA_URL + path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Api-Key': API_KEY },
      body: JSON.stringify(body)
    });
    if (!r.ok) throw new Error('API ' + r.status);
    return r.json();
  } catch(e) {
    console.warn('BEA POST (auth) failed:', path, e);
    return null;
  }
}

async function saveEditedListing() {
  if (!elCurrentId) return;
  const sellerEmail = (SELLERS[0] && SELLERS[0]._email) || localStorage.getItem('ms_aa_email') || '';
  if (!sellerEmail) { showToast('Cannot save — seller email not set'); return; }

  // ── EULA gate — must accept before editing a live listing ─────────────────
  if (BEA_ENABLED) {
    try {
      const _ur = await fetch(BEA_URL + '/users/' + encodeURIComponent(sellerEmail));
      if (_ur.ok) {
        const _ud = await _ur.json();
        if (!_ud.eula_accepted_at) {
          // Show EULA modal — on acceptance, stamp and retry save
          const _eulaHdr = document.querySelector('#fea-lm-eula-modal h2');
          if (_eulaHdr) _eulaHdr.textContent = 'Accept TrustSquare Terms before editing your listing';
          _feaLmEulaPending = async () => {
            await fetch(BEA_URL + '/users/' + encodeURIComponent(sellerEmail) + '/eula',
              { method: 'POST', headers: { 'X-Api-Key': API_KEY } }).catch(() => {});
            await saveEditedListing();
          };
          document.getElementById('fea-lm-eula-modal').style.display = 'flex';
          return;
        }
        // Banking nudge — non-blocking, just show toast once per session
        if (!_ud.banking_added_at && !sessionStorage.getItem('_bankNudgeSeen')) {
          sessionStorage.setItem('_bankNudgeSeen', '1');
          showToast('💡 Tip: add your banking details in dashboard settings for Tuppence payouts.', 5000);
        }
      }
    } catch(_) {}
  }

  const btn = document.getElementById('el-save-btn');
  if (btn) { btn.disabled = true; btn.textContent = 'Saving…'; }

  const fd = _elCollectFields();

  // Map form field IDs → BEA model field names
  const payload = {};
  if (fd.title)        payload.title        = fd.title;
  if (fd.price || fd.rate) {
    // Strip currency symbols, spaces, commas and any text — keep digits and one decimal point only
    const rawP = (fd.price || fd.rate).replace(/[^0-9.]/g, '');
    payload.price = rawP || (fd.price || fd.rate);
  }
  if (fd.desc)         payload.description  = fd.desc;
  if (fd.suburb)       payload.suburb       = fd.suburb;
  if (fd.area)         payload.area         = fd.area;
  if (fd.prop_type)    payload.prop_type    = fd.prop_type;
  if (fd.beds)         payload.beds         = parseInt(fd.beds)       || undefined;
  if (fd.baths)        payload.baths        = parseInt(fd.baths)      || undefined;
  if (fd.garages)      payload.garages      = parseInt(fd.garages)    || undefined;
  if (fd.floor_area)   payload.floor_area   = parseInt(fd.floor_area) || undefined;
  if (fd.erf_size)     payload.erf_size     = parseInt(fd.erf_size)   || undefined;
  if (fd.listing_type) payload.listing_type = fd.listing_type;
  if (fd.subject)      payload.subject      = fd.subject;
  if (fd.level)        payload.level        = fd.level;
  if (fd.mode)         payload.mode         = fd.mode;
  if (fd.service_class) payload.service_class = fd.service_class;
  if (fd.service_type)  payload.service_type  = fd.service_type;
  if (fd.availability)  payload.availability  = fd.availability;
  // Include updated photo_urls and always sync thumb/medium to position 0
  if (_elPhotoUrls && _elPhotoUrls.length) {
    payload.photo_urls  = JSON.stringify(_elPhotoUrls);
    payload.thumb_url   = _elPhotoUrls[0];
    payload.medium_url  = _elPhotoUrls[0];
  }

  try {
    const res = await fetch(
      BEA_URL + '/listings/' + elCurrentId + '?email=' + encodeURIComponent(sellerEmail),
      { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }
    );
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Save failed (' + res.status + ')');
    }
    showToast('✓ Listing updated — changes are live');
    const _wpSellEmail=(SELLERS[0]&&SELLERS[0]._email)||localStorage.getItem('ms_aa_email')||'';
    if(window._currentEditBeaId&&_wpSellEmail)wpSave(window._currentEditBeaId,_wpSellEmail);
    // Refresh both dashboard and buyer-side listing cache
    await Promise.all([loadLiveDash(), loadLiveListings()]);
    renderDash();
    goTo('dashboard');
  } catch(e) {
    showToast('Error: ' + e.message);
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = 'Save Changes'; }
  }
}

// ── WORLD WONDERS PICKER ─────────────────────────────────────────────────────
// WONDERS_BUNDLED removed in Session 66 — data served from BEA GET /wonders
let _wpAllWonders=[];let _wpLinked=[];
// Preload wonders from BEA after page load (non-blocking)
(function(){
  function _preloadWonders(){
    if(_wpAllWonders.length>0) return;
    fetch(BEA_URL+'/wonders').then(r=>r.json()).then(d=>{
      if(d.wonders&&d.wonders.length>0){
        _wpAllWonders=d.wonders;
        // Kick off image preload for top 8 (Africa-first)
        const africa=['South Africa','Zimbabwe','Zambia','Kenya','Tanzania','Namibia','Botswana','Uganda'];
        const af=_wpAllWonders.filter(w=>africa.some(c=>w.country.includes(c)));
        const oth=_wpAllWonders.filter(w=>!af.find(a=>a.id===w.id));
        [...af,...oth].slice(0,8).forEach(w=>{const img=new Image();img.src=w.photo;});
        if(typeof renderWondersStrip==='function') renderWondersStrip();
      }
    }).catch(()=>{});
  }
  if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',_preloadWonders);}
  else{setTimeout(_preloadWonders,200);}
})();
async function wpInit(beaId){
  if(_wpAllWonders.length===0){try{const r=await fetch(BEA_URL+'/wonders');const d=await r.json();_wpAllWonders=d.wonders||[];}catch(e){}}
  _wpLinked=[];
  try{const r2=await fetch(BEA_URL+'/listings/'+beaId+'/wonders');const d2=await r2.json();_wpLinked=d2.wonders||[];}catch(e){}
  wpRenderLinked();
}
function wpSearch(q){
  const box=document.getElementById('wp-results');
  if(!q||q.length<2){box.style.display='none';return;}
  const ql=q.toLowerCase();
  const matches=_wpAllWonders.filter(w=>w.name.toLowerCase().includes(ql)||(w.country||'').toLowerCase().includes(ql)||(w.region||'').toLowerCase().includes(ql)).slice(0,8);
  if(!matches.length){box.style.display='none';return;}
  const tc=t=>t==='National Park'?'wp-type-np':t==='UNESCO Site'?'wp-type-un':'wp-type-ar';
  const tl=t=>t==='National Park'?'PARK':t==='UNESCO Site'?'UNESCO':'ARCH';
  box.innerHTML=matches.map(w=>`<div class="wp-result-item" onclick="wpLink('${w.id}')"><img class="wp-result-img" src="${w.photo}" loading="lazy" referrerpolicy="origin-when-cross-origin" onerror="r2Fallback(this);if(this.dataset.r2tried&&this.src.includes('/media/')){this.style.display='none'}"><div class="wp-result-info"><div class="wp-result-name">${w.name}</div><div class="wp-result-meta">${w.country}</div></div><span class="wp-result-type ${tc(w.type)}">${tl(w.type)}</span></div>`).join('');
  box.style.display='block';
}
function wpShowResults(){const q=(document.getElementById('wp-search')||{}).value||'';if(q.length>=2)wpSearch(q);}
function wpLink(wonderId){
  if(_wpLinked.length>=5){showToast('Maximum 5 wonders per listing');return;}
  if(_wpLinked.find(w=>w.id===wonderId)){showToast('Already linked');return;}
  const wonder=_wpAllWonders.find(w=>w.id===wonderId);if(!wonder)return;
  _wpLinked.push(wonder);wpRenderLinked();
  document.getElementById('wp-search').value='';document.getElementById('wp-results').style.display='none';
}
function wpUnlink(wonderId){_wpLinked=_wpLinked.filter(w=>w.id!==wonderId);wpRenderLinked();}
function wpRenderLinked(){
  const el=document.getElementById('wp-linked');const hint=document.getElementById('wp-hint');if(!el)return;
  if(!_wpLinked.length){el.innerHTML='';if(hint)hint.textContent='Link up to 5 nearby heritage sites to enrich your listing';return;}
  el.innerHTML=_wpLinked.map(w=>`<div class="wp-linked-chip"><img src="${w.photo}" referrerpolicy="origin-when-cross-origin" onerror="r2Fallback(this);if(this.dataset.r2tried&&this.src.includes('/media/')){this.style.display='none'}"><span>${w.name}</span><button onclick="wpUnlink('${w.id}')" title="Remove">×</button></div>`).join('');
  if(hint)hint.textContent=`${_wpLinked.length}/5 linked · saved with your listing`;
}
async function wpSave(beaId,sellerEmail){
  if(!beaId||!sellerEmail)return;
  try{await fetch(BEA_URL+'/listings/'+beaId+'/wonders',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:sellerEmail,wonder_ids:_wpLinked.map(w=>w.id)})});}catch(e){console.warn('wpSave failed',e);}
}
async function elConfirmDeleteListing() {
  if (!elCurrentId) return;
  const title = elCurrentRaw && elCurrentRaw.title ? '"' + elCurrentRaw.title + '"' : 'this listing';
  if (!confirm('Delete ' + title + '? This cannot be undone.')) return;
  if (!confirm('Are you sure? All listing data, photos and evidence links will be permanently deleted and cannot be recovered.')) return;
  let email = (SELLERS[0] && SELLERS[0]._email)
    || localStorage.getItem('ms_aa_email')
    || localStorage.getItem('ms_user_email')
    || '';
  // Fallback: ask for email if not in localStorage (e.g. session before gate-login fix)
  if (!email) {
    email = (prompt('Enter your seller email to confirm deletion:') || '').trim().toLowerCase();
    if (!email) { showToast('Email required to delete listing'); return; }
  }
  const btn = document.getElementById('el-delete-btn');
  if (btn) { btn.textContent = 'Deleting...'; btn.style.pointerEvents = 'none'; }
  try {
    const res = await fetch(
      BEA_URL + '/listings/' + elCurrentId + '/seller?email=' + encodeURIComponent(email),
      { method: 'DELETE' }
    );
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Delete failed (' + res.status + ')');
    }
    // Remove from local dashState so dashboard re-renders correctly
    dashState.listings = dashState.listings.filter(dl => dl.beaListingId !== elCurrentId);
    elCurrentId = null; elCurrentCat = null; elCurrentRaw = null;
    await loadLiveListings();
    renderDash();
    showToast('Listing deleted');
    goTo('dashboard');
  } catch(e) {
    showToast('Error: ' + e.message);
    if (btn) { btn.textContent = 'Delete this listing'; btn.style.pointerEvents = 'auto'; }
  }
}

// Optional AI suggestions in the edit screen — costs 1 coaching session
async function editAISuggest() {
  if (!elCurrentId || !elCurrentCat) return;
  const sellerEmail = (SELLERS[0] && SELLERS[0]._email) || localStorage.getItem('ms_aa_email') || '';
  if (!sellerEmail) { showToast('Set your seller email first'); return; }

  const btn = document.getElementById('el-ai-btn');
  if (btn) { btn.disabled = true; btn.textContent = 'Thinking…'; }

  // Collect current field values for the coach
  const fd = _elCollectFields();
  const fields = {};
  Object.entries(fd).forEach(([k, v]) => { if (v) fields[k] = v; });

  try {
    const res = await fetch(BEA_URL + '/advert-agent/coach', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: sellerEmail, category: elCurrentCat, fields, photo_slots_completed: [] })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'AI unavailable');
    }
    const data = await res.json();
    const cj   = data.coaching_json || {};
    elAISuggestions = cj.fields || {};

    // Show warnings + session count
    const aiOut = document.getElementById('el-ai-output');
    let html = '';
    if (cj.anonymity_warning) {
      html += `<div style="background:#fef3c7;border:1px solid #fbbf24;border-radius:8px;padding:10px 12px;font-size:12px;color:#92400e;margin-bottom:10px;">⚠️ ${cj.anonymity_warning}</div>`;
    }
    if (data.tuppence_remaining !== undefined) {
      html += `<div style="font-size:11px;color:var(--text-3);text-align:right;margin-bottom:8px;">Tuppence remaining: <strong>${data.tuppence_remaining}T</strong></div>`;
    }
    if (aiOut) aiOut.innerHTML = html;

    // Re-render form with suggestions inlined under each field
    renderEditForm(elCurrentRaw);
    const photoWarn = (cj && cj.anonymity_warning) ? cj.anonymity_warning : '';
    elRenderPhotos(elCurrentRaw, photoWarn);
    showToast('✨ AI suggestions ready — review and apply each field');
  } catch(e) {
    showToast('AI: ' + e.message);
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = 'Ask AI'; }
  }
}

// ── AI1: Seller Listing Rewrite (Session 77) ──────────────────────────────
async function elRunRewrite() {
  if (!elCurrentId) return;
  const email = (SELLERS[0] && SELLERS[0]._email) || localStorage.getItem('ms_aa_email') || '';
  if (!email) { showToast('Sign in to use AI Rewrite'); return; }
  const btn = document.getElementById('el-rewrite-btn');
  const out = document.getElementById('el-ai-output');
  if (btn) { btn.disabled = true; btn.textContent = '⏳ Rewriting…'; }
  if (out) out.innerHTML = '<div style="font-size:12px;color:var(--text-3);padding:8px 0;">✨ Claude is rewriting your listing…</div>';
  try {
    if (!confirm('This will use 1T to rewrite your listing title and description using AI. The new text will pre-fill the form below for you to review and save. Proceed?')) {
      if (btn) { btn.disabled = false; btn.textContent = '✨ Rewrite'; }
      if (out) out.innerHTML = '';
      return;
    }
    const numId = typeof elCurrentId === 'string' ? elCurrentId.replace('bea_', '') : elCurrentId;
    const r = await fetch(BEA_URL + '/listings/' + numId + '/ai-rewrite?email=' + encodeURIComponent(email), { method: 'POST' });
    if (!r.ok) {
      const err = await r.json().catch(() => ({}));
      throw new Error(err.detail || 'Rewrite failed');
    }
    const data = await r.json();
    // Pre-fill title and description fields
    const titleEl = document.getElementById('elf-title');
    const descEl  = document.getElementById('elf-description');
    if (titleEl && data.new_title) titleEl.value = data.new_title;
    if (descEl  && data.new_description) descEl.value = data.new_description;
    if (out) out.innerHTML = `
      <div style="background:#f5f3ff;border:1.5px solid #a78bfa;border-radius:10px;padding:12px 14px;margin-bottom:10px;">
        <div style="font-size:12px;font-weight:700;color:#5b21b6;margin-bottom:6px;">✨ AI Rewrite complete — fields pre-filled below</div>
        <div style="font-size:12px;color:#374151;margin-bottom:4px;"><strong>New title:</strong> ${data.new_title}</div>
        <div style="font-size:12px;color:#374151;line-height:1.5;"><strong>New description:</strong> ${data.new_description}</div>
        <div style="font-size:10px;color:#7c3aed;margin-top:8px;">Review the fields below and tap Save Changes when happy · ${data.tuppence_remaining}T remaining</div>
      </div>`;
    showToast('✨ Rewrite ready — review fields and save');
  } catch(e) {
    if (out) out.innerHTML = '';
    showToast('Rewrite: ' + e.message);
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = '✨ Rewrite'; }
  }
}

// ── AI2: Why No Intros? Seller Audit (Session 77) ────────────────────────────
async function elRunAudit() {
  if (!elCurrentId) return;
  const email = (SELLERS[0] && SELLERS[0]._email) || localStorage.getItem('ms_aa_email') || '';
  if (!email) { showToast('Sign in to use Why No Intros?'); return; }
  const btn = document.getElementById('el-audit-btn');
  const out = document.getElementById('el-ai-output');
  if (btn) { btn.disabled = true; btn.textContent = '⏳ Analysing…'; }
  if (out) out.innerHTML = '<div style="font-size:12px;color:var(--text-3);padding:8px 0;">🔍 Analysing your listing…</div>';
  try {
    if (!confirm('This will use 1T to get an AI audit of why buyers might be skipping your listing. Proceed?')) {
      if (btn) { btn.disabled = false; btn.textContent = '🔍 Why No Intros?'; }
      if (out) out.innerHTML = '';
      return;
    }
    const numId = typeof elCurrentId === 'string' ? elCurrentId.replace('bea_', '') : elCurrentId;
    const r = await fetch(BEA_URL + '/listings/' + numId + '/ai-audit?email=' + encodeURIComponent(email), { method: 'POST' });
    if (!r.ok) {
      const err = await r.json().catch(() => ({}));
      throw new Error(err.detail || 'Audit failed');
    }
    const data = await r.json();
    const actionHtml = (data.actions || []).map((a, i) =>
      `<div style="display:flex;gap:10px;margin-bottom:10px;">
        <div style="flex-shrink:0;width:22px;height:22px;border-radius:50%;background:#0e7490;color:#fff;font-size:11px;font-weight:700;display:flex;align-items:center;justify-content:center;">${i+1}</div>
        <div>
          <div style="font-size:12px;font-weight:700;color:#164e63;">${a.step}</div>
          <div style="font-size:11px;color:#374151;margin-top:2px;line-height:1.4;">${a.reason}</div>
        </div>
      </div>`
    ).join('');
    if (out) out.innerHTML = `
      <div style="background:#ecfeff;border:1.5px solid #67e8f9;border-radius:10px;padding:12px 14px;margin-bottom:10px;">
        <div style="font-size:12px;font-weight:700;color:#0e7490;margin-bottom:10px;">🔍 Why No Intros? — 3 fixes to try</div>
        ${actionHtml}
        <div style="font-size:10px;color:#0e7490;margin-top:4px;">${data.tuppence_remaining}T remaining</div>
      </div>`;
    showToast('🔍 Audit complete — 3 actions ready');
  } catch(e) {
    if (out) out.innerHTML = '';
    showToast('Audit: ' + e.message);
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = '🔍 Why No Intros?'; }
  }
}

// ── AI4: Seller Yield Calculator (Session 77) ─────────────────────────────
async function elRunYield() {
  if (!elCurrentId) return;
  const email = (SELLERS[0] && SELLERS[0]._email) || localStorage.getItem('ms_aa_email') || '';
  if (!email) { showToast('Sign in to use Yield Calculator'); return; }
  const btn = document.getElementById('el-yield-btn');
  const out = document.getElementById('el-ai-output');
  if (btn) { btn.disabled = true; btn.textContent = '⏳ Calculating…'; }
  if (out) out.innerHTML = '<div style="font-size:12px;color:var(--text-3);padding:8px 0;">📈 Calculating yield…</div>';
  try {
    if (!confirm('This calculates the real rental yield. 1T is charged ONLY if a yield can be computed (you may be asked for the purchase price or rent). Proceed?')) {
      if (btn) { btn.disabled = false; btn.textContent = '📈 Yield Calc'; }
      if (out) out.innerHTML = '';
      return;
    }
    const numId = typeof elCurrentId === 'string' ? elCurrentId.replace('bea_', '') : elCurrentId;
    let r = await fetch(BEA_URL + '/listings/' + numId + '/yield-calc?email=' + encodeURIComponent(email), { method: 'POST' });
    if (r.status === 400) { showToast('Yield calc only available for Property listings'); return; }
    if (r.status === 402) { showToast('Insufficient Tuppence'); return; }
    if (!r.ok) { showToast('Yield calculation failed'); return; }
    let data = await r.json();
    if (data.status === 'needs_input') {
      const askMsg = data.need === 'rent'
        ? 'Enter the expected MONTHLY RENT (Rand) — no Tuppence charged yet:'
        : 'Enter the likely PURCHASE PRICE (Rand) — no Tuppence charged yet:';
      const entry = window.prompt(askMsg, '');
      const val = entry == null ? null : parseFloat(String(entry).replace(/[^0-9.]/g, ''));
      if (!val || val <= 0) { showToast('No figure entered — nothing charged'); return; }
      const param = data.need === 'rent' ? '&rent=' : '&purchase_price=';
      r = await fetch(BEA_URL + '/listings/' + numId + '/yield-calc?email=' + encodeURIComponent(email) + param + val, { method: 'POST' });
      if (!r.ok) { showToast('Yield calculation failed'); return; }
      data = await r.json();
      if (data.status === 'needs_input') { showToast('Still missing a figure — nothing charged'); return; }
    }
    if (out) out.innerHTML = `
      <div style="background:#f0fdf4;border:1.5px solid #6ee7b7;border-radius:10px;padding:12px 14px;margin-bottom:10px;">
        <div style="font-size:12px;font-weight:700;color:#065f46;margin-bottom:10px;">📈 AI Property Yield Analysis</div>
        <div style="display:flex;gap:16px;margin-bottom:10px;">
          <div style="flex:1;text-align:center;">
            <div style="font-size:10px;font-weight:700;color:#065f46;text-transform:uppercase;letter-spacing:.5px;">Gross Yield</div>
            <div style="font-size:22px;font-weight:800;color:#065f46;">${data.gross_yield_pct}</div>
          </div>
          <div style="flex:1;text-align:center;">
            <div style="font-size:10px;font-weight:700;color:#065f46;text-transform:uppercase;letter-spacing:.5px;">Net Estimate</div>
            <div style="font-size:22px;font-weight:800;color:#065f46;">${data.net_yield_estimate_pct}</div>
          </div>
        </div>
        <div style="font-size:11px;font-weight:600;color:#065f46;margin-bottom:4px;">Benchmark: ${data.sa_yield_benchmark}</div>
        ${data.market_context ? `<div style="font-size:11px;color:#374151;line-height:1.5;margin-top:6px;">${data.market_context}</div>` : ''}
        ${data.purchase_price_used && data.monthly_rent_used ? `<div style="font-size:10px;color:#374151;margin-top:6px;">Computed from ${data.purchase_price_used} purchase · ${data.monthly_rent_used}/month</div>` : ''}
        <div style="font-size:10px;color:#6ee7b7;margin-top:8px;">✅ Calculated figure · ${data.tuppence_remaining}T remaining</div>
      </div>`;
    showToast('📈 Yield analysis complete');
  } catch(e) {
    if (out) out.innerHTML = '';
    showToast('Yield: ' + e.message);
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = '📈 Yield Calc'; }
  }
}

// ── PHOTO STRIP DOT TRACKER ───────────────────────────────
function stripNav(id, delta) {
  const strip = document.getElementById('pstrip-' + id);
  if (!strip) return;
  const count = strip.querySelectorAll('.photo-strip-slide').length;
  const w = strip.offsetWidth || strip.getBoundingClientRect().width || (strip.scrollWidth / count);
  if (!w) return;
  const idx = Math.round(strip.scrollLeft / w);
  const next = Math.max(0, Math.min(count - 1, idx + delta));
  strip.scrollTo({ left: next * w, behavior: 'smooth' });
  setTimeout(() => updateStripDots(id, count), 80);
}

function updateStripDots(id, count) {
  if (count <= 1) return;
  const strip = document.getElementById('pstrip-' + id);
  if (!strip) return;
  const idx = Math.round(strip.scrollLeft / strip.offsetWidth);
  for (let i = 0; i < count; i++) {
    const dot = document.getElementById(`psd-${id}-${i}`);
    if (dot) dot.classList.toggle('active', i === idx);
  }
}

// ── LOCAL MARKET — sell wizard flow ───────────────────────
let _feaLmEulaPending = null;

function openLMCreateFromWizard() {
  const email = localStorage.getItem('ms_aa_email') || '';
  if (!email) {
    // Not logged in — gate with friendly message, redirect to sell account sheet
    showToast('Please sign in to create a Local Market listing');
    // Reset category selection so they can try again after login
    pubCat = null;
    document.getElementById('pub-b-next').style.opacity = '.4';
    document.getElementById('pub-b-next').style.pointerEvents = 'none';
    document.querySelectorAll('.cat-big-tile').forEach(t => t.classList.remove('selected'));
    setTimeout(() => openSellNav(), 800);
    return;
  }
  // Pre-fill city from active geo state
  const cityInput = document.getElementById('fea-lm-city');
  if (cityInput && activeCity && activeCity.name) cityInput.value = activeCity.name;
  const suburbInput = document.getElementById('fea-lm-suburb');
  if (suburbInput && activeSuburb && activeSuburb.name) suburbInput.value = activeSuburb.name;
  // Show seller email in display bar
  document.getElementById('fea-lm-seller-email').textContent = email;
  // Clear any previous state
  ['fea-lm-title','fea-lm-desc','fea-lm-price'].forEach(id => {
    const el = document.getElementById(id); if (el) el.value = '';
  });
  document.getElementById('fea-lm-photos').value = '';
  document.getElementById('fea-lm-status').textContent = '';
  document.getElementById('fea-lm-submit').disabled = false;
  // If seller already added a photo in Step A, show it and hide the photo field
  const photoRow = document.getElementById('fea-lm-photo-row');
  const photoPreview = document.getElementById('fea-lm-photo-preview');
  if (pubImg) {
    if (photoPreview) { photoPreview.src = pubImg; photoPreview.style.display = 'block'; }
    if (photoRow) photoRow.style.display = 'none';
  } else {
    if (photoPreview) photoPreview.style.display = 'none';
    if (photoRow) photoRow.style.display = 'block';
  }
  // Show create modal directly (EULA check happens on submit)
  document.getElementById('fea-lm-create-modal').style.display = 'flex';
}

function feaLmCloseCreate() {
  document.getElementById('fea-lm-create-modal').style.display = 'none';
  // Reset wizard category so seller can pick again
  pubCat = null;
  document.getElementById('pub-b-next').style.opacity = '.4';
  document.getElementById('pub-b-next').style.pointerEvents = 'none';
  document.querySelectorAll('.cat-big-tile').forEach(t => t.classList.remove('selected'));
}

function feaLmCloseEula(accepted) {
  document.getElementById('fea-lm-eula-modal').style.display = 'none';
  const cont = _feaLmEulaPending;
  _feaLmEulaPending = null;
  if (accepted && cont) cont().catch(() => {});
}

async function _feaLmCheckEula(email) {
  try {
    const r = await fetch(BEA_URL + '/users/' + encodeURIComponent(email));
    if (!r.ok) return false;
    const u = await r.json();
    return !!u.lm_eula_accepted_at;
  } catch(e) { return false; }
}

async function _feaLmRecordEula(email) {
  try {
    await fetch(BEA_URL + '/local-market/eula/accept?email=' + encodeURIComponent(email), {
      method: 'POST', headers: { 'X-Api-Key': API_KEY }
    });
  } catch(e) {}
}

async function feaLmSubmit() {
  const email  = localStorage.getItem('ms_aa_email') || '';
  const title  = (document.getElementById('fea-lm-title').value || '').trim();
  const desc   = (document.getElementById('fea-lm-desc').value || '').trim();
  const price  = (document.getElementById('fea-lm-price').value || '').trim();
  const suburb = (document.getElementById('fea-lm-suburb').value || '').trim();
  const city   = (document.getElementById('fea-lm-city').value || '').trim();
  const photos = document.getElementById('fea-lm-photos').files;
  const status = document.getElementById('fea-lm-status');
  const btn    = document.getElementById('fea-lm-submit');

  if (!email) { status.textContent = 'Please sign in first.'; return; }
  if (!title || !suburb || !city) {
    status.textContent = 'Please fill in title, suburb, and city.';
    var _lmMsg = document.getElementById('lm-haiko-msg');
    var _lmEl  = document.getElementById('lm-haiko-strip');
    if (_lmMsg && _lmEl) {
      _lmEl.className = 'hk-strip hk-warn';
      _lmMsg.innerHTML = '<strong>Almost there</strong> — ' +
        (!title  ? 'add a <strong>title</strong> for your item. ' : '') +
        (!suburb ? 'add your <strong>suburb</strong>. ' : '') +
        (!city   ? 'add your <strong>city</strong>. ' : '');
    }
    return;
  }

  // EULA gate — show once, then record acceptance
  const eulaOk = await _feaLmCheckEula(email);
  if (!eulaOk) {
    _feaLmEulaPending = async () => {
      await _feaLmRecordEula(email);
      await feaLmSubmit();
    };
    document.getElementById('fea-lm-eula-modal').style.display = 'flex';
    return;
  }

  btn.disabled = true;
  status.textContent = 'Uploading photos...';

  // Upload photos — use Step A photo (pubImg) if no new file chosen in modal
  let thumbUrl = null, mediumUrl = null;
  const hasNewFile = photos && photos.length > 0;
  const hasStepAPhoto = !!pubImg;

  if (hasNewFile || hasStepAPhoto) {
    try {
      let blob;
      if (hasNewFile) {
        blob = photos[0];
      } else {
        const res = await fetch(pubImg);
        blob = await res.blob();
      }
      const fd = new FormData();
      fd.append('file', blob, 'photo.jpg');
      const pr = await fetch(BEA_URL + '/listings/photo', {
        method: 'POST', headers: { 'X-Api-Key': API_KEY }, body: fd
      });
      if (pr.ok) {
        const pd = await pr.json();
        thumbUrl  = pd.thumb_url  || null;
        mediumUrl = pd.medium_url || null;
      }
    } catch(e) {}
  }

  status.textContent = 'Publishing listing...';
  try {
    const country = localStorage.getItem('lm_seller_country_' + email) || 'ZA';
    const resp = await fetch(BEA_URL + '/local-market/listings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Api-Key': API_KEY },
      body: JSON.stringify({
        title, description: desc, price: price || null,
        suburb, city, seller_email: email,
        geo_city_id: activeCity ? activeCity.id : null,
        country, thumb_url: thumbUrl, medium_url: mediumUrl
      })
    });
    const j = await resp.json();
    if (!resp.ok) {
      status.textContent = 'Error: ' + (j.detail || resp.status);
      btn.disabled = false;
      return;
    }
    // Success — close create modal, show success screen
    document.getElementById('fea-lm-create-modal').style.display = 'none';
    _feaLmShowSuccess(title, j.id);
  } catch(e) {
    status.textContent = 'Connection error — please try again.';
    btn.disabled = false;
  }
}

function _feaLmShowSuccess(title, listingId) {
  // Reuse the pub-claim success screen with LM-specific copy
  document.getElementById('claim-title').textContent = `"${title}" is live on Local Market.`;
  const claimSub = document.getElementById('claim-sub');
  if (claimSub) claimSub.textContent = 'Your listing is live. Buyers in your area can find it now.';
  const claimId = document.getElementById('claim-listing-id');
  if (claimId) claimId.textContent = 'Listing #' + listingId;
  showPhase('claim');
  showToast('Local Market listing published!');
}

let toastTimer;
function showToast(msg){
  const t=document.getElementById('toast');
  t.textContent=msg;t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer=setTimeout(()=>t.classList.remove('show'),2600);
}

// ── FEATURED CAROUSEL desktop scroll ─────────────────────────
// S99: generic scroll-arrow injector. For any strip el that horizontally
// overflows, wrap it in a position:relative container and add the same
// .feat-scroll-btn arrows the World Heritage row uses. Idempotent + safe on
// mobile (arrows are small, shown on all viewports per ms.css). Call after a
// strip's innerHTML is (re)populated.
function ensureScrollArrows(strip){
  try{
    if(!strip) return;
    // already wrapped?
    if(strip.parentElement && strip.parentElement.classList.contains('hscroll-arrowwrap')) {
      // refresh visibility against current overflow
      const overflow = strip.scrollWidth > strip.clientWidth + 4;
      strip.parentElement.querySelectorAll('.feat-scroll-btn').forEach(b=>b.style.display = overflow ? 'flex' : 'none');
      return;
    }
    const overflow = strip.scrollWidth > strip.clientWidth + 4;
    if(!overflow) return;            // nothing to scroll — no arrows
    const wrap=document.createElement('div');
    wrap.className='hscroll-arrowwrap';
    wrap.style.position='relative';
    strip.parentNode.insertBefore(wrap, strip);
    wrap.appendChild(strip);
    const mk=(dir,cls,glyph)=>{
      const b=document.createElement('button');
      b.className='feat-scroll-btn '+cls;
      b.setAttribute('aria-label', dir<0?'Scroll left':'Scroll right');
      b.innerHTML=glyph;
      b.onclick=()=>{ const card=strip.querySelector(':scope > *');
        const step=card?(card.offsetWidth+12)*2:300; strip.scrollBy({left:dir*step,behavior:'smooth'}); };
      return b;
    };
    wrap.appendChild(mk(-1,'feat-scroll-btn-left','&#8249;'));
    wrap.appendChild(mk(1,'feat-scroll-btn-right','&#8250;'));
  }catch(e){ /* never break render over a nice-to-have */ }
}

function featScroll(dir){
  const el=document.getElementById('home-featured');
  if(!el)return;
  const card=el.querySelector('.hcard');
  const step=card?(card.offsetWidth+8)*2:240;
  el.scrollBy({left:dir*step,behavior:'smooth'});
}
function wondersStripScroll(dir){
  const el=document.getElementById('home-wonders-list');
  if(!el)return;
  const card=el.querySelector('.wonder-card');
  const step=card?(card.offsetWidth+10)*2:320;
  el.scrollBy({left:dir*step,behavior:'smooth'});
}

// Wonder filter state
let _wfCountry = 'all';
let _wfType    = 'all';

// Country → name fragments used in wonder.country field
const _wfCountryMap = {
  // Africa
  'ZA': ['South Africa'],
  'KE': ['Kenya'],
  'TZ': ['Tanzania'],
  'NA': ['Namibia'],
  'ZW': ['Zimbabwe'],
  'BW': ['Botswana'],
  'UG': ['Uganda'],
  'RW': ['Rwanda'],
  'CD': ['Congo','DRC'],
  'ET': ['Ethiopia'],
  'ML': ['Mali'],
  'EG': ['Egypt'],
  // Europe
  'GB': ['United Kingdom'],
  'FR': ['France'],
  'DE': ['Germany'],
  'IT': ['Italy'],
  'ES': ['Spain'],
  'HR': ['Croatia'],
  'GR': ['Greece'],
  'NL': ['Netherlands'],
  'PT': ['Portugal'],
  'RU': ['Russia'],
  // Americas
  'US': ['United States'],
  'MX': ['Mexico'],
  'PE': ['Peru'],
  'AR': ['Argentina'],
  'CR': ['Costa Rica'],
  'BR': ['Brazil'],
  'CL': ['Chile'],
  'BO': ['Bolivia'],
  // Asia
  'IN': ['India'],
  'CN': ['China'],
  'JP': ['Japan'],
  'TR': ['Turkey'],
  'KH': ['Cambodia'],
  'NP': ['Nepal'],
  'VN': ['Vietnam'],
  'IR': ['Iran'],
  'LY': ['Libya'],
  'PK': ['Pakistan'],
  // Middle East & Central Asia
  'JO': ['Jordan'],
  // Oceania
  'AU': ['Australia'],
  'NZ': ['New Zealand'],
};

function setWonderFilter(dim, val) {
  if(dim==='country') _wfCountry = val;
  if(dim==='type')    _wfType    = val;
  renderWondersStrip();
}

function renderWondersStrip() {
  const list = document.getElementById('home-wonders-list');
  if(!list || !_wpAllWonders.length) return;
  let filtered = _wpAllWonders;
  if(_wfCountry !== 'all') {
    const frags = _wfCountryMap[_wfCountry]||[];
    filtered = filtered.filter(w=>frags.some(f=>w.country.includes(f)));
  }
  if(_wfType !== 'all') {
    filtered = filtered.filter(w=>w.type===_wfType);
  }
  // Africa first within result
  const africa = filtered.filter(w=>['South Africa','Zimbabwe','Zambia','Kenya','Tanzania','Namibia','Botswana','Uganda'].some(c=>w.country.includes(c)));
  const others = filtered.filter(w=>!africa.find(a=>a.id===w.id));
  const sorted = [...africa,...others];
  const tc2 = t=>t==='National Park'?'wd-type-np':t==='UNESCO Site'?'wd-type-un':t==='National Museum'?'wd-type-nm':'wd-type-ar';
  list.innerHTML = sorted.length ? sorted.map((w,i)=>`
    <div class="wonder-card" onclick="openWonderDetail('${w.id}',null)">
      <img class="wonder-card-img" src="${w.photo}" loading="${i<8?'eager':'lazy'}" referrerpolicy="origin-when-cross-origin" onerror="this.style.background='#1e3a5f'">
      <div class="wonder-card-body">
        <div class="wonder-card-type ${tc2(w.type)}">${w.type}</div>
        <div class="wonder-card-name">${w.name}</div>
        <div class="wonder-card-country">${w.country}</div>
      </div>
    </div>`).join('')
  : '<div style="padding:20px 16px;color:var(--text-3);font-size:13px;">No wonders match this filter.</div>';
}

// ── PHOTO LIGHTBOX ────────────────────────────────────────────
let _lbPhotos=[], _lbIdx=0, _listingPhotosCache={};
function openLightboxById(listingId, idx){
  const photos=_listingPhotosCache[listingId]||[];
  if(!photos.length)return;
  openLightbox(photos, idx);
}
function openLightbox(photos, idx){
  _lbPhotos=photos; _lbIdx=idx||0;
  _renderLightbox();
  const lb=document.getElementById('photo-lightbox');
  lb.classList.add('open');
  document.addEventListener('keydown',_lbKeyHandler);
}
function _renderLightbox(){
  document.getElementById('plb-img').src=_lbPhotos[_lbIdx];
  const ctr=document.getElementById('plb-counter');
  ctr.textContent=_lbPhotos.length>1?`${_lbIdx+1} / ${_lbPhotos.length}`:'';
  // hide arrows if only 1 photo
  document.querySelector('.plb-arrow-left').style.display=_lbPhotos.length>1?'':'none';
  document.querySelector('.plb-arrow-right').style.display=_lbPhotos.length>1?'':'none';
}
function lightboxNav(dir){
  _lbIdx=(_lbIdx+dir+_lbPhotos.length)%_lbPhotos.length;
  _renderLightbox();
}
function closeLightbox(e){
  // Allow close from: backdrop click, close button, or called directly (no event)
  if(e&&e.target&&e.target.closest&&e.target.closest('.plb-arrow'))return;
  document.getElementById('photo-lightbox').classList.remove('open');
  document.getElementById('plb-img').src='';
  document.removeEventListener('keydown',_lbKeyHandler);
}
function _lbKeyHandler(e){
  if(e.key==='Escape')closeLightbox({target:document.getElementById('photo-lightbox')});
  if(e.key==='ArrowRight')lightboxNav(1);
  if(e.key==='ArrowLeft')lightboxNav(-1);
}

// ── MY REQUESTS (dashboard tab) ──────────────────────────────
function renderMyRequests(){
  const el=document.getElementById('dash-requests-content');
  if(!el)return;
  // Gather listings the user has interacted with: wishlist + accepted intros
  const interacted=[...wishlist].map(id=>findListing(id)).filter(Boolean);
  // Also add any intro-accepted listings not already in wishlist
  [...acceptedIntros].forEach(key=>{
    const id=key.split('-').slice(1).join('-');
    const l=findListing(id);
    if(l&&!wishlist.has(id))interacted.push(l);
  });
  if(!interacted.length){
    el.innerHTML=`<div class="empty-state"><div class="empty-icon">📋</div><h3>No requests yet</h3><p>When you save a listing or send an introduction request, it will appear here.</p></div>`;
    return;
  }
  el.innerHTML=`<div class="lgrid">${interacted.map(l=>{
    const hasIntro=([...acceptedIntros]).some(k=>k.endsWith('-'+l.id));
    const badge=hasIntro?'<span style="font-size:10px;font-weight:700;color:#fff;background:var(--accent);border-radius:4px;padding:2px 6px;margin-left:6px;">Intro sent</span>':'<span style="font-size:10px;font-weight:700;color:var(--text-3);background:var(--surface-2);border-radius:4px;padding:2px 6px;margin-left:6px;">Saved</span>';
    return`<div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--r);overflow:hidden;cursor:pointer;" onclick="openDetail('${l.id}')">
      <div style="height:90px;background:${catCfg(l).bg};overflow:hidden;">${l.photo?`<img src="${l.photo}" style="width:100%;height:100%;object-fit:cover;" loading="lazy">`:`<div style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:34px;">${catCfg(l).icon}</div>`}</div>
      <div style="padding:10px 12px 12px;">
        <div style="font-size:11px;font-weight:700;color:var(--text-3);text-transform:uppercase;letter-spacing:.4px;margin-bottom:3px;">${l.cat}${badge}</div>
        <div style="font-size:14px;font-weight:700;color:var(--navy);margin-bottom:3px;line-height:1.3;">${l.title}</div>
        <div style="font-size:12px;color:var(--text-3);">📍 ${l.area}</div>
      </div>
    </div>`;
  }).join('')}</div>`;
}

// ── ADVERT AGENT ─────────────────────────────────────────────

// Category definitions: fields (Stage 1) + photo slots (Stage 2)
// Canonical register (locked 14 April 2026): Property · Tutors · Services · Adventures (P2) · Collectors (P2)
const AA_CATEGORIES = {
  'Property': {
    emoji: '🏡',
    fields: [
      {id:'title',        label:'Listing headline',    type:'text',   placeholder:'e.g. Spacious 3-bed family home'},
      {id:'price',        label:'Asking price',        type:'number', placeholder:'e.g. 2500000'},
      {id:'listing_type', label:'Listing type',        type:'select', options:['For Sale','For Rent']},
      {id:'prop_type',    label:'Property type',       type:'select', options:['House','Apartment / Flat','Townhouse','Cluster','Simplex','Duplex','Bachelor / Studio','Granny Flat','Penthouse','Land / Plot','Smallholding','Farm','Commercial','Industrial','Other']},
      {id:'beds',         label:'Bedrooms',            type:'number', placeholder:'e.g. 3'},
      {id:'baths',        label:'Bathrooms',           type:'number', placeholder:'e.g. 2'},
      {id:'garages',      label:'Garages / parking',   type:'number', placeholder:'e.g. 1'},
      {id:'floor_area',   label:'Floor area (m²)',     type:'number', placeholder:'e.g. 140'},
      {id:'erf_size',     label:'Erf / plot size (m²)',type:'number', placeholder:'e.g. 600'},
      {id:'suburb',       label:'Suburb / area',       type:'text',   placeholder:'e.g. Waterkloof Ridge'},
      {id:'street_address',label:'Street address',       type:'text',   placeholder:'e.g. 12 Oak Avenue, Waterkloof Ridge', hint:'Private — used only to calculate distances to nearby schools, hospitals and shops. Never shown to buyers.'},
      {id:'desc',         label:'Description',         type:'textarea',placeholder:'Key features, condition, standout details…'},
    ],
    photos: [
      {slot:'lounge',         label:'Lounge / Living area',  hint:'Wide angle, good light',         required:true},
      {slot:'kitchen',        label:'Kitchen',               hint:'Show counters and fittings',      required:true},
      {slot:'master_bed',     label:'Master bedroom',        hint:'Full room, beds made',            required:true},
      {slot:'bathroom',       label:'Bathroom',              hint:'Each bathroom separately',        required:true},
      {slot:'exterior_front', label:'Exterior — front',      hint:'Street-facing view',             required:true},
      {slot:'exterior_rear',  label:'Exterior — rear',       hint:'Back of property',               required:true},
      {slot:'garden',         label:'Garden / outdoor area', hint:'Lawn, patio, pool if present',   required:false},
      {slot:'garage',         label:'Garage / parking',      hint:'Interior of garage or carport',  required:false},
    ],
  },
  'Tutors': {
    emoji: '🎓',
    fields: [
      {id:'title',   label:'Listing headline',    type:'text',   placeholder:'e.g. Maths & Science tutor · Grades 10–12'},
      {id:'subject', label:'Subject(s) — select all that apply', type:'multiselect',
       options:['Mathematics','Mathematical Literacy','Physical Sciences','Life Sciences / Biology','English','Afrikaans','History','Geography','Accounting','Economics','Business Studies','Computer Applications Technology','Information Technology','Life Orientation','Chemistry','Statistics','Calculus','Physics','Music','Art / Drama','Other']},
      {id:'level',   label:'Level',               type:'select', options:['Primary (Gr 1–7)','High School (Gr 8–12)','Tertiary','Adult / Professional','All levels']},
      {id:'mode',    label:'Mode',                type:'select', options:['In-person','Online','Both']},
      {id:'rate',    label:'Rate',                type:'rate',   placeholder:'300', units:['/hr','/session','/month','once-off','POA']},
      {id:'area',    label:'Area / suburb',       type:'text',   placeholder:'e.g. Pretoria East'},
      {id:'radius',  label:'Travel radius',       type:'select', options:['5 km','10 km','15 km','20 km','30 km','50 km','Online only','City-wide']},
      {id:'desc',    label:'About your teaching', type:'textarea',placeholder:'Qualifications, experience, approach, successes…'},
    ],
    photos: [
      {slot:'profile',         label:'Profile photo',         hint:'Professional headshot',                required:true},
      {slot:'teaching_example',label:'Teaching example',      hint:'Whiteboard, lesson notes or workspace', required:false},
      {slot:'certificate',     label:'Qualification / degree',hint:'Your highest relevant credential',      required:false},
    ],
  },
  'Services': {
    emoji: '🔧',
    // Services has two class variants. Fields and photos come from serviceClasses[service_class].
    // If service_class is not yet set, the wizard shows a class selector chip row before the form.
    serviceClasses: {
      'Technical': {
        fields: [
          {id:'title',       label:'Listing headline',    type:'text',   placeholder:'e.g. Licensed electrician · Pretoria'},
          {id:'service_type',label:'Service type',        type:'select', options:['Electrical','Plumbing','HVAC','Solar','IT & Tech','Legal','Financial','Landscaping','Construction','Cleaning','Other']},
          {id:'area',        label:'Area / suburb',       type:'text',   placeholder:'e.g. Pretoria East'},
          {id:'radius',      label:'Travel radius',       type:'select', options:['5 km','10 km','15 km','20 km','30 km','50 km','City-wide']},
          {id:'rate',        label:'Rate',                type:'rate',   placeholder:'450', units:['/hr','/day','/visit','once-off / fixed','POA']},
          {id:'callout_fee', label:'Call-out fee (optional)', type:'rate', required:false, placeholder:'0', units:['/visit','flat fee','POA'], helpText:'Charged per call-out, in addition to your main rate'},
          {id:'experience',  label:'Years of experience', type:'number', placeholder:'e.g. 12'},
          {id:'registered',  label:'Registered / accredited', type:'select', options:['Yes — fully registered','Yes — in progress','No — not applicable']},
          {id:'desc',        label:'About your service',  type:'textarea',placeholder:'Qualifications, licences, scope of work, availability…'},
        ],
        photos: [
          {slot:'work_example_1',label:'Work example 1',           hint:'Completed job — best example',   required:true},
          {slot:'work_example_2',label:'Work example 2',           hint:'Different job or project',       required:true},
          {slot:'certificate',   label:'Qualification / licence',  hint:'Certificate or registration card',required:false},
        ],
      },
      'Casuals': {
        fields: [
          {id:'title',         label:'Listing headline',    type:'text',   placeholder:'e.g. Reliable domestic worker · Pretoria'},
          {id:'service_type',  label:'Service type',        type:'select', options:['Domestic','Gardening','Dog Walking','Child Minding','Temp / Receptionist','General Labour','Other']},
          {id:'availability',  label:'Availability',        type:'select', options:['Weekdays','Weekends','Weekdays & weekends','Flexible / negotiable']},
          {id:'days_available',label:'Days available',      type:'text',   placeholder:'e.g. Mon–Fri, or 3 days/week'},
          {id:'rate',          label:'Rate',                type:'rate',   placeholder:'200', units:['/hr','/day','/week','/month','once-off','POA']},
          {id:'callout_fee',   label:'Call-out fee (optional)', type:'rate', required:false, placeholder:'0', units:['/visit','flat fee','POA'], helpText:'Charged per call-out, in addition to your main rate'},
          {id:'area',          label:'Area / suburb',       type:'text',   placeholder:'e.g. Centurion, Midrand'},
          {id:'radius',        label:'Travel radius',       type:'select', options:['5 km','10 km','15 km','20 km','30 km','50 km','City-wide']},
          {id:'references',    label:'References available',type:'select', options:['Yes — contactable references','On request','None currently']},
          {id:'desc',          label:'About me',            type:'textarea',placeholder:'Experience, reliability, what makes you stand out…'},
        ],
        photos: [
          {slot:'work_example',   label:'Work example (optional)',hint:'A photo showing your work or workspace', required:false},
          {slot:'reference_letter',label:'Reference letter (optional)',hint:'Written reference if you have one',  required:false},
        ],
      },
    },
  },
  'Adventures': {
    emoji: '🧭',
    // Adventures has two class variants: Accommodation and Experiences.
    // Fields and photos come from serviceClasses[service_class].
    serviceClasses: {
      'adventures_accommodation': {
        label: '🏕 Accommodation',
        fields: [
          {id:'title',            label:'Listing headline',        type:'text',   placeholder:'e.g. Bushveld chalet · Waterberg'},
          {id:'accommodation_type',label:'Accommodation type',     type:'select', options:['Guest House','Bush Camp','Chalet','Hostel','Self-catering','Caravan / Camp site','Wilderness Hut','Alpine Hut','Other']},
          {id:'destination',      label:'Location / area',         type:'text',   placeholder:'e.g. Waterberg, Limpopo'},
          {id:'environment_type', label:'Environment',             type:'select', options:['Bush & Wildlife','Mountain & Highlands','Coastal & Beach','Garden & Winelands','Wetlands & Lakes','Desert & Karoo','Forest & Fynbos','Urban & Township','Farm & Rural']},
          {id:'price_per_night',  label:'Price per night (from)',  type:'number', placeholder:'e.g. 1200'},
          {id:'sleeps',           label:'Sleeps (max guests)',      type:'number', placeholder:'e.g. 6'},
          {id:'amenities',        label:'Amenities',               type:'text',   placeholder:'e.g. Pool, braai, WiFi, full kitchen'},
          {id:'desc',             label:'About the property',      type:'textarea',placeholder:'Setting, vibe, what makes it special, nearby activities…'},
        ],
        photos: [
          {slot:'hero',       label:'Hero shot',          hint:'Best exterior or setting shot',       required:true},
          {slot:'interior_1', label:'Interior — main area',hint:'Living area, lounge or main room',   required:true},
          {slot:'bedroom',    label:'Bedroom',            hint:'Main sleeping area',                  required:true},
          {slot:'outdoor',    label:'Outdoor / surrounds',hint:'Braai, pool, deck or bush view',      required:false},
        ],
      },
      'adventures_experiences': {
        label: '🌄 Experiences',
        fields: [
          {id:'title',           label:'Experience title',         type:'text',   placeholder:'e.g. Guided Drakensberg hike · 2 days'},
          {id:'activity_type',   label:'Activity type',            type:'select', options:['Hiking & Trails','Water Sports','Wildlife & Birding','Horse & Farm','Cycling & MTB','Climbing & Abseiling','Cultural & Township','Food & Wine','Wellness & Retreat','Arts & Craft','Family & Kids','Photography & Creative','Sky & Extreme','Other']},
          {id:'destination',     label:'Destination / location',   type:'text',   placeholder:'e.g. Drakensberg, KwaZulu-Natal'},
          {id:'environment_type',label:'Environment',              type:'select', options:['Bush & Wildlife','Mountain & Highlands','Coastal & Beach','Garden & Winelands','Wetlands & Lakes','Desert & Karoo','Forest & Fynbos','Urban & Township','Farm & Rural']},
          {id:'duration',        label:'Duration',                 type:'text',   placeholder:'e.g. Full day · 8 hours'},
          {id:'group_size',      label:'Group size',               type:'text',   placeholder:'e.g. 2–10 people'},
          {id:'price_per_person',label:'Price per person',         type:'number', placeholder:'e.g. 850'},
          {id:'difficulty',      label:'Difficulty level',         type:'select', options:['Easy — anyone can do it','Moderate — some fitness required','Challenging — experienced participants','Expert — serious athletes / specialists']},
          {id:'desc',            label:'What\'s included',         type:'textarea',placeholder:'Itinerary, inclusions, exclusions, what to bring…'},
        ],
        photos: [
          {slot:'hero',         label:'Hero shot',          hint:'Best action or setting photo',      required:true},
          {slot:'activity_1',   label:'Activity shot 1',    hint:'Participants in the experience',    required:true},
          {slot:'activity_2',   label:'Activity shot 2',    hint:'Another angle or highlight moment', required:true},
          {slot:'activity_3',   label:'Activity shot 3',    hint:'Detail, scenery or group',          required:false},
        ],
      },
    },
  },
  'Collectors': {
    emoji: '🏆',
    phase: 2,
    fields: [
      {id:'title',       label:'Item name / headline',  type:'text',   placeholder:'e.g. 1d Cape of Good Hope Triangle 1853 · VF'},
      {id:'item_type',   label:'Collection type',       type:'select', options:['Stamps','Trading Cards (MTG / Pokémon / Baseball)','Coins','Memorabilia','Other']},
      {id:'condition',   label:'Condition',             type:'text',   placeholder:'e.g. PSA 9, VF, Fine, Mint…'},
      {id:'catalogue_ref',label:'Catalogue reference',  type:'text',   placeholder:'e.g. SG 1, Scott 1, PSA label…'},
      {id:'edition_year',label:'Edition / year of issue',type:'text',  placeholder:'e.g. 1853, Alpha set, 1st edition…'},
      {id:'price',       label:'Asking price',          type:'number', placeholder:'e.g. 1200'},
      {id:'desc',        label:'Description',           type:'textarea',placeholder:'Provenance, grading notes, any defects or certificates…'},
    ],
    photos: [
      {slot:'front',           label:'Front / face',          hint:'Full frame, no glare',             required:true},
      {slot:'back',            label:'Back',                  hint:'Full frame, centered',             required:true},
      {slot:'condition_closeup',label:'Condition close-up',   hint:'Corners, margins or surface detail',required:true},
      {slot:'certificate',     label:'Certificate / slab',    hint:'Expert cert or grading slab label', required:false},
    ],
  },
  'Cars': {
    emoji: '🚗',
    fields: [
      {id:'title',       label:'Listing headline',       type:'text',   placeholder:'e.g. 2019 Toyota Hilux 2.8 GD-6 4x4 · low km'},
      {id:'make',        label:'Make',                   type:'text',   placeholder:'e.g. Toyota'},
      {id:'model',       label:'Model',                  type:'text',   placeholder:'e.g. Hilux 2.8 GD-6'},
      {id:'year',        label:'Year',                   type:'number', placeholder:'e.g. 2019'},
      {id:'mileage',     label:'Mileage (km)',            type:'number', placeholder:'e.g. 85000'},
      {id:'colour',      label:'Colour',                 type:'text',   placeholder:'e.g. White'},
      {id:'transmission',label:'Transmission',           type:'select', options:['Manual','Automatic','Semi-automatic']},
      {id:'fuel_type',   label:'Fuel type',              type:'select', options:['Petrol','Diesel','Hybrid','Electric','LPG']},
      {id:'body_type',   label:'Body type',              type:'select', options:['Sedan','Hatchback','SUV / 4x4','Bakkie / Truck','Coupe','Convertible','Minivan / MPV','Station Wagon','Crossover','Other']},
      {id:'price',       label:'Asking price',           type:'number', placeholder:'e.g. 380000'},
      {id:'listing_type',label:'Listing type',           type:'select', options:['For Sale','For Hire / Rental']},
      {id:'desc',        label:'Description',            type:'textarea',placeholder:'Condition, service history, extras, reason for selling…'},
    ],
    photos: [
      {slot:'exterior_front', label:'Exterior — front',     hint:'Head-on, good light, clean background', required:true},
      {slot:'exterior_side',  label:'Exterior — side',      hint:'Full profile shot',                      required:true},
      {slot:'interior',       label:'Interior',             hint:'Dashboard and front seats',              required:true},
      {slot:'engine',         label:'Engine bay',           hint:'Clean, well-lit',                        required:false},
      {slot:'service_book',   label:'Service book (optional)',hint:'Open to last service entry',           required:false},
    ],
  },
  'LocalMarket': {
    emoji: '🛒',
    fields: [
      {id:'title', label:'Product / service title', type:'text',     placeholder:'e.g. Organic honey — 500ml jar'},
      {id:'price', label:'Price',                   type:'text',     placeholder:'e.g. R120 per jar'},
      {id:'desc',  label:'Description',             type:'textarea', placeholder:"What you're offering, quantity, freshness, delivery options…"},
      {id:'area',  label:'Area / suburb',           type:'text',     placeholder:'e.g. Pretoria East'},
    ],
    photos: [
      {slot:'product', label:'Product photo', hint:'Clear photo showing your product', required:true},
    ],
  },
};

// Helper: return the correct fields+photos config for a draft (handles Services service_class split)
function aaCatConfig(draft) {
  const base = AA_CATEGORIES[draft.category];
  if (!base) return null;
  if (base.serviceClasses) {
    const sc = draft.service_class;
    if (sc && base.serviceClasses[sc]) return base.serviceClasses[sc];
    // No service_class selected yet — return a stub so callers don\'t crash
    return { fields: [], photos: [] };
  }
  return base;
}

// ── aaDB: thin IndexedDB wrapper ──────────────────────────────
const aaDB = (() => {
  const DB_NAME = 'advertAgentDB';
  const DB_VER  = 1;
  const STORE   = 'aa_drafts';
  let _db = null;

  function open() {
    if (_db) return Promise.resolve(_db);
    return new Promise((res, rej) => {
      const req = indexedDB.open(DB_NAME, DB_VER);
      req.onupgradeneeded = e => {
        const db = e.target.result;
        if (!db.objectStoreNames.contains(STORE)) {
          db.createObjectStore(STORE, {keyPath: 'id'});
        }
      };
      req.onsuccess = e => { _db = e.target.result; res(_db); };
      req.onerror   = e => rej(e.target.error);
    });
  }

  async function getAll() {
    const db = await open();
    return new Promise((res, rej) => {
      const tx  = db.transaction(STORE, 'readonly');
      const req = tx.objectStore(STORE).getAll();
      req.onsuccess = () => res(req.result);
      req.onerror   = () => rej(req.error);
    });
  }

  async function get(id) {
    const db = await open();
    return new Promise((res, rej) => {
      const tx  = db.transaction(STORE, 'readonly');
      const req = tx.objectStore(STORE).get(id);
      req.onsuccess = () => res(req.result || null);
      req.onerror   = () => rej(req.error);
    });
  }

  async function put(draft) {
    const db = await open();
    return new Promise((res, rej) => {
      const tx  = db.transaction(STORE, 'readwrite');
      const req = tx.objectStore(STORE).put(draft);
      req.onsuccess = () => res(req.result);
      req.onerror   = () => rej(req.error);
    });
  }

  async function remove(id) {
    const db = await open();
    return new Promise((res, rej) => {
      const tx  = db.transaction(STORE, 'readwrite');
      const req = tx.objectStore(STORE).delete(id);
      req.onsuccess = () => res();
      req.onerror   = () => rej(req.error);
    });
  }

  return {getAll, get, put, remove};
})();

// ── AA currency helper ────────────────────────────────────────
// Returns { code, symbol } for the active country. Drives price field labels.
function aaCurrency() {
  const map = {
    ZA: { code: 'ZAR', symbol: 'R' },
    US: { code: 'USD', symbol: '$' },
    GB: { code: 'GBP', symbol: '£' },
    DE: { code: 'EUR', symbol: '€' },
    EU: { code: 'EUR', symbol: '€' },
  };
  return map[(activeCountry && activeCountry.iso2) || 'ZA'] || { code: 'USD', symbol: '$' };
}

// Formats a raw number as a price string using the active currency symbol.
// e.g. 250000 → "R250,000.00" (ZAR) or "$250,000.00" (USD)
function aaFormatPrice(val) {
  const cur = aaCurrency();
  const numStr = String(val).replace(/[^0-9.]/g, '');
  if (!numStr) return '';
  const n = parseFloat(numStr);
  if (isNaN(n)) return '';
  const parts = n.toFixed(2).split('.');
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  return cur.symbol + parts[0] + '.' + parts[1];
}

// ── AA state ──────────────────────────────────────────────────
let aaDraftId            = null;  // active draft id
let aaActiveSlot         = null;  // photo slot being captured
let aaCurrentSuggestions = {};    // field suggestions from last AI coach run

// ── AA navigation ─────────────────────────────────────────────
function aaGoTo(screenSuffix) {
  goTo('aa-' + screenSuffix);
}

// ── AA Home: render draft list ────────────────────────────────
async function aaRenderHome() {
  const list = await aaDB.getAll();
  const el   = document.getElementById('aa-draft-list');
  if (!list.length) {
    el.innerHTML = `
      <div class="aa-empty">
        <div class="aa-empty-icon">📋</div>
        <p>No drafts yet.<br>Tap <strong>Start New Item</strong> to begin.</p>
      </div>`;
    return;
  }
  list.sort((a,b) => b.updated_at - a.updated_at);
  const stageNames = {1:'Item Details', 2:'Photos', 3:'Publish'};
  el.innerHTML = list.map(d => {
    const catCfg  = AA_CATEGORIES[d.category] || {};
    const emoji   = catCfg.emoji || '📦';
    const title   = d.fields?.title || d.fields?.item_name || 'Untitled';
    const stage   = Math.min(d.stage || 1, 3);
    const age     = aaAgeLabel(d.updated_at);
    const dots    = [1,2,3].map(s =>
      `<span class="aa-stage-dot ${s < stage ? 'done' : s === stage ? 'active' : ''}"></span>`
    ).join('');
    const stageLabel = stage >= 3 ? 'Ready to publish' : `Next: ${stageNames[stage] || 'Details'}`;
    return `
      <div class="aa-draft-card">
        <div class="aa-draft-cat">${emoji} ${d.category || 'No category'}</div>
        <div class="aa-draft-title">${title}</div>
        <div class="aa-draft-meta">
          <div class="aa-stage-dots">${dots}</div>
          <span style="font-size:11px;color:var(--text-3);">Stage ${stage} of 4 · ${stageLabel}</span>
          <span class="aa-draft-age">${age}</span>
        </div>
        <div style="display:flex;gap:8px;margin-top:10px;">
          <button onclick="aaOpenDraft('${d.id}')" style="flex:1;background:var(--accent);color:#fff;border:none;border-radius:8px;padding:9px;font-size:13px;font-weight:600;cursor:pointer;font-family:'Inter',sans-serif;">Continue</button>
          <button onclick="event.stopPropagation();aaOpenDraftAt('${d.id}',1)" style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:9px 12px;font-size:12px;cursor:pointer;font-family:'Inter',sans-serif;color:var(--text-2);">Edit</button>
          <button onclick="event.stopPropagation();aaDeleteDraft('${d.id}')" style="background:none;border:1px solid #fca5a5;border-radius:8px;padding:9px 12px;font-size:12px;cursor:pointer;font-family:'Inter',sans-serif;color:#e11d48;">Delete</button>
        </div>
      </div>`;
  }).join('');
}

function aaAgeLabel(ts) {
  const diff = Date.now() - ts;
  const mins = Math.floor(diff / 60000);
  if (mins < 2)   return 'just now';
  if (mins < 60)  return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24)   return `${hrs}h ago`;
  return `${Math.floor(hrs/24)}d ago`;
}

// ── AA Draft management ───────────────────────────────────────
async function aaNewDraft() {
  aaDraftId = 'aa_' + Date.now();
  // Cascade: sessionStorage (magic-link session) → localStorage (returning seller) → empty
  const seedEmail = sessionStorage.getItem('aa_email') || localStorage.getItem('ms_aa_email') || '';
  const draft = { id: aaDraftId, email: seedEmail, stage: 1, created_at: Date.now(), updated_at: Date.now() };
  await aaDB.put(draft);
  aaRenderDetailScreen(draft);
  goTo('aa-detail');
}

async function aaDeleteDraft(id) {
  await aaDB.remove(id);
  showToast('Draft deleted');
  aaRenderHome();
}

async function aaOpenDraftAt(id, stage) {
  aaDraftId = id;
  const draft = await aaDB.get(id);
  if (!draft) { aaRenderDetailScreen(null); goTo('aa-detail'); return; }
  if (stage === 1) { aaRenderDetailScreen(draft); goTo('aa-detail'); return; }
  if (stage === 2) { aaRenderPhotosScreen(draft); goTo('aa-photos'); return; }
  aaRenderPublishScreen(); goTo('aa-publish');
}

async function aaOpenDraft(id) {
  aaDraftId = id;
  const draft = await aaDB.get(id);
  if (!draft) { aaRenderDetailScreen(null); goTo('aa-detail'); return; }

  const stage = draft.stage || 1;
  if (stage >= 3) {
    aaRenderPublishScreen();
    goTo('aa-publish');
  } else if (stage >= 2 && draft.category) {
    aaRenderPhotosScreen(draft);
    goTo('aa-photos');
  } else {
    aaRenderDetailScreen(draft);
    goTo('aa-detail');
  }
}

// ── Stage 1: Detail screen ────────────────────────────────────
function aaRenderDetailScreen(draft) {
  const cats    = Object.keys(AA_CATEGORIES);
  const current = draft?.category || null;

  // Category chips — Phase 2 categories shown with a "Phase 2" note
  document.getElementById('aa-cat-chips').innerHTML = cats.map(c => {
    const cfg = AA_CATEGORIES[c];
    const p2 = cfg.phase === 2 ? ' <span style="font-size:9px;opacity:.6;vertical-align:middle;">P2</span>' : '';
    return `<button class="aa-cat-chip ${c === current ? 'selected' : ''}"
             onclick="aaSelectCategory('${c}')">${cfg.emoji} ${c}${p2}</button>`;
  }).join('');

  // Restore suggestion store from draft (survives page navigation)
  aaCurrentSuggestions = draft?.coachSuggestions?.fields || {};

  // Form fields with inline suggestions
  aaRenderDetailForm(current, draft?.fields || {}, draft?.service_class || null, aaCurrentSuggestions);

  // AI coach panel below the form
  aaRenderAIPanel(draft);
}

function aaSelectCategory(cat) {
  // Update chip selection — only category chips (not class chips)
  document.querySelectorAll('#aa-cat-chips .aa-cat-chip').forEach(btn => {
    btn.classList.toggle('selected', btn.textContent.includes(cat));
  });
  // Reset service_class when category changes
  aaDB.get(aaDraftId).then(draft => {
    const sc = (cat === (draft?.category)) ? (draft?.service_class || null) : null;
    aaRenderDetailForm(cat, {}, sc);
  });
}

function aaRenderDetailForm(category, values, serviceClass, suggestions) {
  suggestions = suggestions || {};
  const el = document.getElementById('aa-detail-form');
  if (!category) {
    el.innerHTML = `<p style="color:var(--text-3);font-size:13px;text-align:center;padding:16px 0;">Select a category above to see the form</p>`;
    document.getElementById('aa-detail-next').disabled = true;
    return;
  }
  const base = AA_CATEGORIES[category];
  if (!base) return;

  // Services: show class selector chips; if class not yet chosen, stop here
  if (base.serviceClasses) {
    const classHtml = `
      <div class="aa-section-label">Service Class</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px;">
        <button class="aa-cat-chip ${serviceClass==='Technical'?'selected':''}" onclick="aaSelectServiceClass('Technical')">🔧 Technical</button>
        <button class="aa-cat-chip ${serviceClass==='Casuals'?'selected':''}" onclick="aaSelectServiceClass('Casuals')">🤝 Casuals</button>
      </div>
      ${serviceClass?'':'<p style="color:var(--text-3);font-size:12px;margin-top:4px;">Choose Technical for licensed trades, or Casuals for domestic &amp; informal work</p>'}
    `;
    if (!serviceClass) {
      el.innerHTML = classHtml;
      document.getElementById('aa-detail-next').disabled = true;
      return;
    }
    const cfg = base.serviceClasses[serviceClass];
    document.getElementById('aa-detail-next').disabled = false;
    el.innerHTML = classHtml + `<div class="aa-section-label">Listing Details</div>` + aaFieldsHtml(cfg.fields, values, suggestions);
    return;
  }

  document.getElementById('aa-detail-next').disabled = false;
  el.innerHTML = `<div class="aa-section-label">Listing Details</div>` + aaFieldsHtml(base.fields, values, suggestions);
}

function aaFieldsHtml(fields, values, suggestions) {
  suggestions = suggestions || {};
  const cur = aaCurrency();
  return fields.map(f => {
    const val  = values[f.id] || '';
    const req  = f.id === 'title' || f.id === 'price' ? ' <span style="color:#e11d48">*</span>' : '';
    const label       = f.label.replace(/\bUSD\b/g, cur.code);
    const placeholder = (f.placeholder || '').replace(/\$(?=\d)/g, cur.symbol);
    const sug = suggestions[f.id];
    const sugHtml = sug
      ? `<div class="aa-suggestion-pill">
           <span class="aa-sug-icon">💡</span>
           <span class="aa-sug-text">${sug.suggestion}</span>
           <button class="aa-sug-apply" data-sug-field="${f.id}" onclick="aaApplySuggestion('${f.id}',this)">✓ Apply</button>
         </div>`
      : '';
    if (f.type === 'multiselect') {
      const selected = new Set((val || '').split(',').map(v => v.trim()).filter(Boolean));
      const chips = (f.options || []).map(o =>
        `<button type="button" class="aa-ms-chip${selected.has(o)?' selected':''}"
                 onclick="this.classList.toggle('selected')" data-val="${o}">${o}</button>`
      ).join('');
      return `<div class="field"><label>${label}${req}</label>
        <div class="aa-multisel" id="aaf-${f.id}" data-type="multiselect">${chips}</div>
        ${sugHtml}</div>`;
    }
    if (f.type === 'rate') {
      const rateMatch = val.match(/^R?(\d+(?:\.\d+)?)\s*(.+)?$/);
      const rateAmt   = rateMatch ? rateMatch[1] : '';
      const rateUnit  = (rateMatch && rateMatch[2]) ? rateMatch[2].trim() : (f.units ? f.units[0] : '/hr');
      const units     = f.units || ['/hr', '/day', '/month', 'once-off', 'POA'];
      const opts      = units.map(u => `<option value="${u}"${rateUnit===u?' selected':''}>${u}</option>`).join('');
      const previewId = `aaf-${f.id}-preview`;
      const initPreview = rateAmt ? `R${rateAmt}${rateUnit}` : '';
      const helpHtml  = f.helpText ? `<div style="font-size:11px;color:var(--text-3);margin-top:3px;">${f.helpText}</div>` : '';
      return `<div class="field"><label>${label}${req}</label>
        <div class="aa-rate-wrap" id="aaf-${f.id}" data-type="rate">
          <input type="text" inputmode="decimal" id="aaf-${f.id}-amount" placeholder="${placeholder || '0'}" value="${rateAmt}"
                 style="min-width:80px;"
                 oninput="(function(){var a=document.getElementById('aaf-${f.id}-amount').value,u=document.getElementById('aaf-${f.id}-unit').value,p=document.getElementById('${previewId}');if(p)p.textContent=u==='POA'?'POA':(a?'R'+a+u:'');})()">
          <select id="aaf-${f.id}-unit"
                  onchange="(function(){var a=document.getElementById('aaf-${f.id}-amount').value,u=this.value,p=document.getElementById('${previewId}');if(p)p.textContent=u==='POA'?'POA':(a?'R'+a+u:'');}).call(this)">${opts}</select>
        </div>
        <div id="${previewId}" style="font-size:12px;font-weight:600;color:var(--accent);margin-top:4px;min-height:16px;">${initPreview}</div>
        ${helpHtml}${sugHtml}</div>`;
    }
    if (f.type === 'textarea') {
      return `<div class="field"><label>${label}${req}</label>
        <textarea id="aaf-${f.id}" placeholder="${placeholder}">${val}</textarea>
        ${sugHtml}</div>`;
    }
    if (f.type === 'select') {
      const opts = (f.options || []).map(o =>
        `<option value="${o}"${val===o?' selected':''}>${o}</option>`
      ).join('');
      return `<div class="field"><label>${label}${req}</label>
        <select id="aaf-${f.id}"><option value="">— select —</option>${opts}</select>
        ${sugHtml}</div>`;
    }
    if (f.id === 'price' || f.id === 'price_per_person') {
      const fmtVal = val ? aaFormatPrice(val) : '';
      return `<div class="field"><label>${label}${req}</label>
        <input type="number" id="aaf-${f.id}" placeholder="${placeholder}" value="${val}"
               oninput="(function(v){var d=document.getElementById('aaf-${f.id}-fmt');if(d)d.textContent=v?aaFormatPrice(v):'';})(this.value)">
        <div id="aaf-${f.id}-fmt" style="font-size:12px;font-weight:600;color:var(--accent);margin-top:4px;min-height:16px;">${fmtVal}</div>
        ${sugHtml}</div>`;
    }
    return `<div class="field"><label>${label}${req}</label>
      <input type="${f.type}" id="aaf-${f.id}" placeholder="${placeholder}" value="${val}">
      ${sugHtml}</div>`;
  }).join('');
}

function aaApplySuggestion(fieldId, btn) {
  const sug = (aaCurrentSuggestions || {})[fieldId];
  if (!sug) return;
  const el = document.getElementById('aaf-' + fieldId);
  if (!el) return;
  if (el.dataset.type === 'multiselect') {
    // Tick any chips whose value appears in the suggestion string
    const sugVals = sug.suggestion.split(',').map(v => v.trim().toLowerCase());
    el.querySelectorAll('.aa-ms-chip').forEach(chip => {
      if (sugVals.includes(chip.dataset.val.toLowerCase())) chip.classList.add('selected');
    });
  } else if (el.dataset.type === 'rate') {
    // Parse "R300/hr" or "300 /hr" or "POA" from suggestion
    const raw = sug.suggestion.trim();
    if (raw.toUpperCase() === 'POA') {
      const unitSel = document.getElementById('aaf-' + fieldId + '-unit');
      if (unitSel) unitSel.value = 'POA';
    } else {
      const m = raw.match(/R?(\d+(?:\.\d+)?)\s*(.+)?/);
      if (m) {
        const amtEl  = document.getElementById('aaf-' + fieldId + '-amount');
        const unitEl = document.getElementById('aaf-' + fieldId + '-unit');
        if (amtEl)  amtEl.value  = m[1];
        if (unitEl && m[2]) unitEl.value = m[2].trim();
      }
    }
  } else {
    el.value = sug.suggestion;
    el.focus();
    el.dispatchEvent(new Event('input'));
  }
  if (btn) { btn.textContent = '✓ Applied'; btn.disabled = true; }
}

function aaSelectServiceClass(sc) {
  // Persist service_class on draft and re-render form with the new class
  aaDB.get(aaDraftId).then(draft => {
    const d = draft || {id: aaDraftId, photos: [], created_at: Date.now()};
    d.service_class = sc;
    d.updated_at = Date.now();
    aaDB.put(d).then(() => {
      const category = aaGetSelectedCategory() || d.category;
      aaRenderDetailForm(category, d.fields || {}, sc, aaCurrentSuggestions || {});
    });
  });
}

function aaGetSelectedCategory() {
  const selected = document.querySelector('.aa-cat-chip.selected');
  if (!selected) return null;
  // Extract category name from chip text (strip emoji prefix)
  const text = selected.textContent.trim();
  return Object.keys(AA_CATEGORIES).find(k => text.includes(k)) || null;
}

async function aaSaveDetailAndNext() {
  const category = aaGetSelectedCategory();
  if (!category) { showToast('Please select a category first'); return; }

  // For Services, get service_class from the draft (set by aaSelectServiceClass)
  const existingDraft = await aaDB.get(aaDraftId) || {};
  const service_class = (category === 'Services') ? (existingDraft.service_class || null) : null;
  if (category === 'Services' && !service_class) {
    showToast('Please choose Technical or Casuals first');
    return;
  }

  const draftForConfig = { category, service_class };
  const cfg    = aaCatConfig(draftForConfig);
  const fields = {};
  for (const f of cfg.fields) {
    const el = document.getElementById('aaf-' + f.id);
    if (!el) continue;
    if (el.dataset.type === 'multiselect') {
      // Chip-based multi-select — collect selected chip values
      fields[f.id] = Array.from(el.querySelectorAll('.aa-ms-chip.selected'))
        .map(b => b.dataset.val).join(', ');
    } else if (el.dataset.type === 'rate') {
      // Compound rate field — number + unit dropdown
      const amt  = (document.getElementById('aaf-' + f.id + '-amount')?.value || '').trim();
      const unit = document.getElementById('aaf-' + f.id + '-unit')?.value || '/hr';
      fields[f.id] = unit === 'POA' ? 'POA' : (amt ? `R${amt}${unit}` : '');
    } else {
      fields[f.id] = el.value.trim();
    }
  }
  if (!fields.title && !fields.item_name) {
    showToast('Fill in the listing headline first');
    const titleEl = document.getElementById('aaf-title') || document.getElementById('aaf-item_name');
    if (titleEl) { titleEl.focus(); titleEl.style.borderColor = '#e11d48'; }
    return;
  }

  const now   = Date.now();
  const draft = await aaDB.get(aaDraftId) || {id: aaDraftId, photos: [], created_at: now};
  const updated = {
    ...draft,
    category,
    service_class,
    fields,
    stage:      Math.max(draft.stage || 1, 2),
    updated_at: now,
  };
  await aaDB.put(updated);
  aaRenderPhotosScreen(updated);
  goTo('aa-photos');
}

// ── Stage 2: Photos screen ────────────────────────────────────
function aaRenderPhotosScreen(draft) {
  const cfg    = aaCatConfig(draft);
  if (!cfg) return;
  const baseCfg = AA_CATEGORIES[draft.category];
  const emoji   = baseCfg ? baseCfg.emoji : '📦';
  const photos  = draft.photos || [];
  const subLabel = draft.service_class ? `${draft.category} · ${draft.service_class}` : draft.category;

  document.getElementById('aa-photos-subtitle').textContent =
    `${subLabel} · ${cfg.photos.filter(p=>p.required).length} required shots`;

  const captured   = new Set(photos.map(p => p.slot));
  const required   = cfg.photos.filter(p => p.required).map(p => p.slot);
  const allReqDone = required.length === 0 || required.every(s => captured.has(s));

  const pct = cfg.photos.length ? Math.round(captured.size / cfg.photos.length * 100) : 100;
  document.getElementById('aa-photo-progress').style.width = pct + '%';
  document.getElementById('aa-photos-next').disabled = !allReqDone;

  document.getElementById('aa-photo-slots').innerHTML = cfg.photos.length
    ? cfg.photos.map(p => {
        const done     = captured.has(p.slot);
        const photoObj = photos.find(x => x.slot === p.slot);
        const thumbHtml = photoObj?.dataUrl
          ? `<div class="aa-photo-thumb"><img src="${photoObj.dataUrl}" alt="${p.label}"></div>`
          : `<div class="aa-photo-thumb">${emoji}</div>`;
        return `
          <div class="aa-photo-slot ${done ? 'captured' : ''} ${p.required ? 'required-slot' : ''}"
               onclick="aaTriggerCapture('${p.slot}')">
            ${thumbHtml}
            <div class="aa-photo-info">
              <div class="aa-photo-name">${p.label}${p.required?'':' <span style="opacity:.55;font-size:10px;">(optional)</span>'}</div>
              <div class="aa-photo-hint">${done ? 'Tap to retake' : p.hint}</div>
            </div>
            <div class="aa-photo-check">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
            </div>
          </div>`;
      }).join('')
    : `<p style="color:var(--text-3);font-size:13px;text-align:center;padding:24px 0;">No required photos for this category — tap Next to continue</p>`;
}

function aaTriggerCapture(slot) {
  aaActiveSlot = slot;
  document.getElementById('aa-photo-input').click();
}

function aaCompressImage(file, maxW, quality) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      let w = img.width, h = img.height;
      if (w > maxW) { h = Math.round(h * maxW / w); w = maxW; }
      const c = document.createElement('canvas');
      c.width = w; c.height = h;
      c.getContext('2d').drawImage(img, 0, 0, w, h);
      resolve(c.toDataURL('image/jpeg', quality));
    };
    img.onerror = () => {
      // Fallback: read as-is
      const r = new FileReader();
      r.onload = e => resolve(e.target.result);
      r.readAsDataURL(file);
    };
    img.src = URL.createObjectURL(file);
  });
}

async function aaHandlePhotoCapture(event) {
  const file = event.target.files[0];
  if (!file || !aaDraftId) return;

  // Auto-compress: max 1200px wide, JPEG quality 0.7 for large files
  let dataUrl;
  if (file.size > 2 * 1024 * 1024) {
    showToast('Compressing large photo…');
    dataUrl = await aaCompressImage(file, 1200, 0.7);
  } else if (file.size > 500 * 1024) {
    dataUrl = await aaCompressImage(file, 1600, 0.8);
  } else {
    dataUrl = await new Promise(r => { const fr = new FileReader(); fr.onload = e => r(e.target.result); fr.readAsDataURL(file); });
  }

  const now   = Date.now();
  const draft = await aaDB.get(aaDraftId);
  if (!draft) return;

  // Upsert photo for this slot (replace if re-captured)
  const photos = (draft.photos || []).filter(p => p.slot !== aaActiveSlot);
  photos.push({ slot: aaActiveSlot, dataUrl });

  const updated = { ...draft, photos, stage: Math.max(draft.stage || 2, 2), updated_at: now };
  await aaDB.put(updated);
  aaRenderPhotosScreen(updated);
  showToast('Photo saved');

  // Reset input so same file can be re-selected
  event.target.value = '';
}

// ── AI COACH PANEL (embedded in Stage 1) ─────────────────────

function aaRenderAIPanel(draft) {
  const el = document.getElementById('aa-detail-ai');
  if (!el) return;
  if (!draft) { el.innerHTML = ''; return; }

  const email       = draft.email || '';
  const suggestions = draft.coachSuggestions || null;
  const actions     = suggestions?.trust_score_actions || [];
  const anonWarn    = suggestions?.anonymity_warning;
  const hasRun      = !!suggestions;

  // Email section
  let emailHtml;
  if (!email) {
    emailHtml = `
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:16px;margin-bottom:12px;">
        <div style="font-size:13px;font-weight:700;margin-bottom:10px;">Enter your email to use the AI Coach</div>
        <input type="email" id="aa-detail-email" placeholder="you@example.com"
               style="width:100%;box-sizing:border-box;padding:10px 12px;border:1.5px solid var(--border);border-radius:var(--r-sm);font-size:14px;font-family:'Inter',sans-serif;">
        <button onclick="aaSaveDetailEmail()" class="aa-btn-primary" style="margin-top:10px;width:100%;">Save email</button>
      </div>`;
  } else {
    emailHtml = `
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:12px 16px;margin-bottom:12px;">
        <div style="display:flex;align-items:center;justify-content:space-between;">
          <div>
            <div style="font-size:11px;color:var(--text-3);margin-bottom:2px;">Seller email</div>
            <div style="font-size:13px;font-weight:600;">${email}</div>
          </div>
          <button onclick="aaClearDetailEmail()" style="background:none;border:none;font-size:12px;font-weight:600;color:var(--navy);cursor:pointer;padding:0;">Change</button>
        </div>
        <div id="aa-detail-session-badge" style="margin-top:8px;font-size:13px;color:var(--text-3);">Checking sessions…</div>
      </div>`;
    setTimeout(() => aaFetchDetailSessionBadge(email), 50);
  }

  // Anonymity warning
  const anonHtml = anonWarn
    ? `<div style="background:#fef2f2;border:1px solid #fca5a5;border-radius:var(--r);padding:12px 14px;margin-bottom:12px;font-size:13px;color:#dc2626;">⚠️ ${anonWarn}</div>`
    : '';

  // Trust Score action plan
  let trustHtml = '';
  if (actions.length > 0) {
    const items = actions.map((a, i) =>
      `<div class="aa-trust-action">
        <div class="aa-trust-num">${i + 1}</div>
        <div style="flex:1;">
          <div style="font-size:13px;font-weight:600;">${a.action}</div>
          <div style="font-size:12px;color:var(--text-3);margin-top:2px;">📄 ${a.doc} · <strong>+${a.points} pts</strong></div>
        </div>
      </div>`
    ).join('');
    trustHtml = `
      <div style="margin-top:16px;">
        <div class="aa-section-label">🎯 Trust Score Action Plan</div>
        <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:4px 14px;">${items}</div>
      </div>`;
  }

  const btnLabel = hasRun ? '🔄 Re-run AI Coach' : '✨ Get AI Suggestions';
  const btnDisabled = !email ? 'disabled' : '';

  el.innerHTML = `
    <div class="aa-section-label" style="margin-top:24px;">AI Coach</div>
    ${emailHtml}
    <button id="aa-detail-coach-btn" onclick="aaRunCoach()" class="aa-btn-primary" ${btnDisabled}
            style="width:100%;margin-bottom:16px;${!email?'opacity:.4;':''}">
      ${btnLabel}
    </button>
    ${anonHtml}
    ${trustHtml}`;
}

async function aaFetchDetailSessionBadge(email) {
  const badge = document.getElementById('aa-detail-session-badge');
  const btn   = document.getElementById('aa-detail-coach-btn');
  if (!badge) return;
  try {
    const res  = await fetch(`${BEA_URL}/advert-agent/status?email=${encodeURIComponent(email)}`);
    const data = await res.json();
    const free = !data.aa_free_used;
    const bal  = data.tuppence_balance ?? tuppence;
    if (free) {
      badge.innerHTML = `<span style="color:#16a34a;font-weight:700;">✓ 1 free coaching session included</span>`;
      if (btn) { btn.disabled = false; btn.style.opacity = '1'; }
    } else if (bal >= 1) {
      badge.innerHTML = `<span style="font-weight:700;">${bal}T available · costs 1T per coach call</span>`;
      if (btn) { btn.disabled = false; btn.style.opacity = '1'; }
    } else {
      badge.innerHTML = `<div style="font-weight:700;color:#dc2626;margin-bottom:6px;">Insufficient Tuppence — AI Coach costs 1T per call</div>
        <div style="font-size:12px;color:var(--text-3);">Top up your Tuppence wallet to continue using AI Coach.</div>
        <button onclick="openTopup()" style="margin-top:8px;background:var(--navy);color:#fff;border:none;border-radius:50px;padding:9px 20px;font-size:13px;font-weight:700;cursor:pointer;font-family:'Syne',sans-serif;">Top Up Tuppence</button>`;
      if (btn) { btn.disabled = true; btn.style.opacity = '.4'; }
    }
  } catch (e) {
    if (badge) badge.innerHTML = `<span style="color:var(--text-3);font-size:12px;">Could not check balance</span>`;
    if (btn)   { btn.disabled = false; btn.style.opacity = '1'; }
  }
}

async function aaSaveDetailEmail() {
  const input = document.getElementById('aa-detail-email');
  const email = (input?.value || '').trim();
  if (!email || !email.includes('@')) { showToast('Enter a valid email'); return; }
  sessionStorage.setItem('aa_email', email);
  localStorage.setItem('ms_aa_email', email);  // persist for returning sellers
  const draft = await aaDB.get(aaDraftId);
  if (!draft) return;
  await aaDB.put({ ...draft, email, updated_at: Date.now() });
  aaRenderAIPanel({ ...draft, email });
}

async function aaClearDetailEmail() {
  const draft = await aaDB.get(aaDraftId);
  if (!draft) return;
  await aaDB.put({ ...draft, email: '', updated_at: Date.now() });
  aaRenderAIPanel({ ...draft, email: '' });
}

// ── STAGE 3 (LEGACY): AI COACH SCREEN ────────────────────────
// Kept for back-compat — not reachable from normal 3-stage flow

async function aaRenderCoachScreen() {
  const draft = await aaDB.get(aaDraftId);
  const el    = document.getElementById('aa-coach-body');
  const btn   = document.getElementById('aa-coach-run-btn');
  if (!draft || !el) return;

  const email = draft.email || '';

  // Session balance (fetch from BEA if email known, else show email prompt)
  let balanceHtml = '';
  if (!email) {
    balanceHtml = `
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:16px;margin-bottom:16px;">
        <div style="font-size:13px;font-weight:700;margin-bottom:10px;">Enter your email to check coaching sessions</div>
        <input type="email" id="aa-coach-email" placeholder="you@example.com"
               style="width:100%;box-sizing:border-box;padding:10px 12px;border:1.5px solid var(--border);border-radius:var(--r-sm);font-size:14px;font-family:'Inter',sans-serif;">
        <button onclick="aaSaveEmail()" class="aa-btn-primary" style="margin-top:10px;width:100%;">Confirm email</button>
      </div>`;
    if (btn) { btn.disabled = true; btn.style.opacity = '.4'; }
  } else {
    // Show email + change link + balance from BEA
    balanceHtml = `
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:14px 16px;margin-bottom:16px;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
          <span style="font-size:12px;color:var(--text-3);">Seller email</span>
          <button onclick="aaClearEmail()" style="background:none;border:none;font-size:12px;font-weight:600;color:var(--navy);cursor:pointer;padding:0;">Change</button>
        </div>
        <div style="font-size:13px;font-weight:600;word-break:break-all;">${email}</div>
        <div id="aa-session-badge" style="margin-top:8px;font-size:13px;color:var(--text-3);">Checking coaching sessions…</div>
      </div>`;
    if (btn) { btn.disabled = false; btn.style.opacity = '1'; }
    // Async fetch balance
    setTimeout(() => aaFetchSessionBadge(email), 50);
  }

  // Listing summary
  const fields = draft.fields || {};
  const catCfg = aaCatConfig(draft) || {};
  const summaryRows = (catCfg.fields || [])
    .filter(f => fields[f.id])
    .map(f => {
      let val = fields[f.id];
      if (f.id === 'price') val = aaFormatPrice(val) || val;
      return `<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border);font-size:13px;">
        <span style="color:var(--text-3);">${f.label.replace(/\s*\(USD\)/, '')}</span>
        <span style="font-weight:600;text-align:right;max-width:60%;">${val}</span></div>`;
    }).join('');

  const photoCount = (draft.photos || []).length;

  // Coach output (if already run)
  const outputHtml = draft.coachOutput
    ? `<div style="margin-top:16px;">
        <div class="aa-section-label">AI Coaching Notes — edit before publishing</div>
        <textarea id="aa-coach-output" style="width:100%;box-sizing:border-box;min-height:180px;padding:12px;border:1.5px solid var(--border);border-radius:var(--r-sm);font-size:13px;line-height:1.6;font-family:'Inter',sans-serif;resize:vertical;">${draft.coachOutput}</textarea>
        <button onclick="aaSaveCoachEdit()" style="margin-top:8px;background:none;border:1.5px solid var(--border);border-radius:50px;padding:8px 18px;font-size:13px;font-weight:600;cursor:pointer;color:var(--navy);">Save edits</button>
      </div>`
    : '';

  el.innerHTML = `
    ${balanceHtml}
    <div class="aa-section-label">Listing summary</div>
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:12px 14px;margin-bottom:4px;">
      <div style="font-size:13px;font-weight:700;margin-bottom:8px;">${catCfg.emoji || '📦'} ${draft.category}</div>
      ${summaryRows || '<span style="color:var(--text-3);font-size:13px;">No fields saved yet</span>'}
    </div>
    <div style="font-size:12px;color:var(--text-3);margin-bottom:12px;">📷 ${photoCount} photo${photoCount!==1?'s':''} captured</div>
    ${outputHtml}`;
}

async function aaFetchSessionBadge(email) {
  const badge = document.getElementById('aa-session-badge');
  const btn   = document.getElementById('aa-coach-run-btn');
  if (!badge) return;
  try {
    const res  = await fetch(`${BEA_URL}/advert-agent/status?email=${encodeURIComponent(email)}`);
    const data = await res.json();
    const free = !data.aa_free_used;
    const bal  = data.tuppence_balance ?? tuppence;
    if (free) {
      badge.innerHTML = `<span style="color:#16a34a;font-weight:700;">✓ 1 free coaching session included</span>`;
      if (btn) { btn.disabled = false; btn.style.opacity = '1'; btn.textContent = 'Run AI Coach'; }
    } else if (bal >= 1) {
      badge.innerHTML = `<span style="font-weight:700;">${bal}T available · costs 1T per coach call</span>`;
      if (btn) { btn.disabled = false; btn.style.opacity = '1'; btn.textContent = 'Run AI Coach'; }
    } else {
      badge.innerHTML = `<div style="font-weight:700;color:#dc2626;margin-bottom:6px;">Insufficient Tuppence — AI Coach costs 1T per call</div>
        <button onclick="openTopup()" style="margin-top:8px;background:var(--navy);color:#fff;border:none;border-radius:50px;padding:9px 20px;font-size:13px;font-weight:700;cursor:pointer;font-family:'Syne',sans-serif;">Top Up Tuppence</button>`;
      if (btn) { btn.disabled = true; btn.style.opacity = '.4'; btn.textContent = 'Run AI Coach'; }
    }
  } catch (e) {
    badge.innerHTML = `<span style="color:var(--text-3);font-size:13px;">Could not check balance — you can still run the coach</span>`;
    if (btn) { btn.disabled = false; btn.style.opacity = '1'; }
  }
}

async function aaSaveEmail() {
  const input = document.getElementById('aa-coach-email');
  const email = (input?.value || '').trim();
  if (!email || !email.includes('@')) { showToast('Enter a valid email'); return; }
  const draft = await aaDB.get(aaDraftId);
  if (!draft) return;
  await aaDB.put({ ...draft, email, updated_at: Date.now() });
  aaRenderCoachScreen();
}

async function aaClearEmail() {
  const draft = await aaDB.get(aaDraftId);
  if (!draft) return;
  await aaDB.put({ ...draft, email: '', updated_at: Date.now() });
  aaRenderCoachScreen();
}

async function aaRunCoach() {
  // Save current form values first so AI analyses the latest input
  let draft = await aaDB.get(aaDraftId);
  if (!draft) return;

  const category = aaGetSelectedCategory() || draft.category;
  if (category) {
    const sc = (category === 'Services') ? (draft.service_class || null) : null;
    const cfg = aaCatConfig({ category, service_class: sc });
    const fields = {};
    for (const f of (cfg?.fields || [])) {
      const el = document.getElementById('aaf-' + f.id);
      if (!el) continue;
      if (el.dataset.type === 'multiselect') {
        fields[f.id] = Array.from(el.querySelectorAll('.aa-ms-chip.selected')).map(b => b.dataset.val).join(', ');
      } else if (el.dataset.type === 'rate') {
        const amt  = (document.getElementById('aaf-' + f.id + '-amount')?.value || '').trim();
        const unit = document.getElementById('aaf-' + f.id + '-unit')?.value || '/hr';
        fields[f.id] = unit === 'POA' ? 'POA' : (amt ? `R${amt}${unit}` : '');
      } else {
        fields[f.id] = el.value.trim();
      }
    }
    if (Object.keys(fields).length) {
      draft = { ...draft, category, service_class: sc, fields, updated_at: Date.now() };
      await aaDB.put(draft);
    }
  }

  const email = draft.email || '';
  if (!email) { showToast('Enter your email first'); return; }

  const btn = document.getElementById('aa-detail-coach-btn');
  if (btn) { btn.disabled = true; btn.textContent = '⏳ Analysing…'; }

  const photoSlots = (draft.photos || []).map(p => p.slot);

  try {
    const res = await fetch(`${BEA_URL}/advert-agent/coach`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email,
        category: draft.category,
        fields: draft.fields || {},
        photo_slots_completed: photoSlots,
      }),
    });
    if (res.status === 402) {
      const data = await res.json();
      showToast(data.detail || 'Insufficient Tuppence — top up to continue');
      if (btn) { btn.disabled = false; btn.textContent = '✨ Get AI Suggestions'; }
      aaFetchDetailSessionBadge(email);
      return;
    }
    if (res.status === 503) {
      showToast('AI Coach is being activated — check back shortly');
      if (btn) { btn.disabled = false; btn.textContent = '✨ Get AI Suggestions'; }
      return;
    }
    if (res.status === 404) {
      showToast('Email not recognised — use your onboarding email');
      if (btn) { btn.disabled = false; btn.textContent = '✨ Get AI Suggestions'; }
      aaClearDetailEmail();
      return;
    }
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    const coachSuggestions = data.coaching_json || {};
    aaCurrentSuggestions   = coachSuggestions.fields || {};
    const updated = { ...draft, coachSuggestions, stage: Math.max(draft.stage || 1, 2), updated_at: Date.now() };
    await aaDB.put(updated);
    // Re-render Stage 1 with inline suggestions
    aaRenderDetailScreen(updated);
    const fieldCount = Object.keys(aaCurrentSuggestions).length;
    const planCount  = (coachSuggestions.trust_score_actions || []).length;
    showToast(`AI suggestions ready — ${fieldCount} field tip${fieldCount !== 1 ? 's' : ''}, ${planCount} Trust Score action${planCount !== 1 ? 's' : ''}`);
  } catch (e) {
    showToast('AI Coach unavailable — try again');
    if (btn) { btn.disabled = false; btn.textContent = '✨ Get AI Suggestions'; }
  }
}

async function aaSaveCoachEdit() {
  const ta = document.getElementById('aa-coach-output');
  if (!ta) return;
  const draft = await aaDB.get(aaDraftId);
  if (!draft) return;
  await aaDB.put({ ...draft, coachOutput: ta.value, updated_at: Date.now() });
  showToast('Notes saved');
}

function aaBuyPack() { aaBuyAIPack(5, 40); }

// ── STAGE 4: PUBLISH ──────────────────────────────────────────

async function aaRenderPublishScreen() {
  const draft = await aaDB.get(aaDraftId);
  const el    = document.getElementById('aa-publish-body');
  if (!draft || !el) return;

  const fields  = draft.fields || {};
  const catCfg  = aaCatConfig(draft) || {};
  const photoCount = (draft.photos || []).length;
  const email   = draft.email || '';

  const summaryRows = (catCfg.fields || [])
    .filter(f => fields[f.id] && f.type !== 'textarea')
    .map(f => {
      let val = fields[f.id];
      if (f.id === 'price') val = aaFormatPrice(val) || val;
      return `<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border);font-size:13px;">
        <span style="color:var(--text-3);">${f.label.replace(/\s*\(USD\)/, '')}</span>
        <span style="font-weight:600;text-align:right;max-width:60%;">${val}</span></div>`;
    }).join('');

  const descVal = fields.desc ? `<div style="margin-top:10px;font-size:13px;line-height:1.6;color:var(--text-2);">${fields.desc}</div>` : '';

  const actions = draft.coachSuggestions?.trust_score_actions || [];
  const coachNote = actions.length > 0
    ? `<div style="margin-top:16px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:var(--r);padding:12px 14px;">
        <div style="font-size:11px;font-weight:700;color:#16a34a;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px;">🎯 Trust Score Action Plan</div>
        ${actions.map((a, i) => `<div class="aa-trust-action">
          <div class="aa-trust-num">${i + 1}</div>
          <div style="flex:1;"><div style="font-size:13px;font-weight:600;">${a.action}</div>
          <div style="font-size:12px;color:#15803d;margin-top:2px;">📄 ${a.doc} · +${a.points} pts</div></div>
        </div>`).join('')}
      </div>`
    : '';

  const emailSection = `
    <div style="margin-top:16px;">
      <div class="aa-section-label">Your email (for claim link)</div>
      <input type="email" id="aa-pub-email" placeholder="you@example.com" value="${email}"
             style="width:100%;box-sizing:border-box;padding:10px 12px;border:1.5px solid var(--border);border-radius:var(--r-sm);font-size:14px;font-family:'Inter',sans-serif;">
    </div>`;

  el.innerHTML = `
    <div class="aa-section-label">Final review</div>
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:12px 14px;margin-bottom:4px;">
      <div style="font-size:13px;font-weight:700;margin-bottom:8px;">${catCfg.emoji || '📦'} ${draft.category}</div>
      ${summaryRows}
      ${descVal}
    </div>
    <div style="font-size:12px;color:var(--text-3);margin:8px 0 4px;">📷 ${photoCount} photo${photoCount!==1?'s':''} ready to upload</div>
    ${coachNote}
    ${emailSection}`;
}

async function aaDoPublish() {
  const draft = await aaDB.get(aaDraftId);
  if (!draft) return;

  const emailInput = document.getElementById('aa-pub-email');
  const email = (emailInput?.value || draft.email || '').trim();
  if (!email || !email.includes('@')) { showToast('Enter a valid email to publish'); return; }

  const btn = document.getElementById('aa-publish-btn');
  if (btn) { btn.disabled = true; btn.textContent = 'Publishing…'; }

  // Save email to draft + persist for returning sessions
  sessionStorage.setItem('aa_email', email);
  localStorage.setItem('ms_aa_email', email);
  await aaDB.put({ ...draft, email, updated_at: Date.now() });

  const fd = new FormData();
  fd.append('email',         email);
  fd.append('category',      draft.category);
  if (draft.service_class) fd.append('service_class', draft.service_class);
  // Include service_class inside fields JSON so BEA can read it
  const fieldsWithClass = { ...(draft.fields || {}) };
  if (draft.service_class) fieldsWithClass.service_class = draft.service_class;
  fd.append('fields',        JSON.stringify(fieldsWithClass));
  // Summarise coach suggestions for BEA (appended to description in pending listing)
  const actions = (draft.coachSuggestions?.trust_score_actions || []);
  const coachNote = actions.length > 0
    ? 'AI Trust Score Actions: ' + actions.map((a,i) => `${i+1}. ${a.action} (+${a.points} pts)`).join('; ')
    : '';
  fd.append('coach_output', coachNote);

  // Append photos — convert base64 dataUrl to Blob for upload
  for (const p of (draft.photos || [])) {
    if (p.dataUrl) {
      try {
        const parts = p.dataUrl.split(',');
        const mime  = (parts[0].match(/:(.*?);/) || [])[1] || 'image/jpeg';
        const binary = atob(parts[1]);
        const bytes  = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
        fd.append('photos', new Blob([bytes], {type: mime}), `${p.slot}.jpg`);
      } catch (e) { /* skip corrupt photo */ }
    }
  }

  try {
    const res = await fetch(`${BEA_URL}/advert-agent/publish`, { method: 'POST', body: fd });
    if (!res.ok) {
      let detail = 'Publish failed — please try again';
      try { const j = JSON.parse(await res.text()); detail = j.detail || detail; } catch(_) {}
      if (res.status === 402) {
        showToast('Slot limit reached'); openPlans('aa-publish', true);
      } else {
        showToast(detail);
      }
      if (btn) { btn.disabled = false; btn.textContent = 'Publish Listing'; }
      return;
    }
    const data = await res.json();
    // Mark draft complete
    await aaDB.put({ ...draft, email, stage: 3, listing_id: data.listing_id, updated_at: Date.now() });
    showToast('Listing published! 🎉');
    goTo('aa-home');
  } catch (e) {
    showToast('Publish failed — please try again');
    if (btn) { btn.disabled = false; btn.textContent = 'Publish Listing'; }
  }
}

// ── AA FLOW EXPLAINER ─────────────────────────────────────────

const AA_FLOWS = {
  'Property': {
    emoji: '🏡',
    heading: 'Your property listing, AI-improved',
    steps: [
      { n:'1', col:'c-blue',  title:'Fill in property details',
        sub:'Listing type · property type · beds · baths · garage · suburb · price' },
      { n:'2', col:'c-blue',  title:'Capture 6 required photos',
        sub:'Lounge · kitchen · master bed · bathroom · front exterior · rear exterior' },
      { n:'✦', col:'c-gold',  title:'AI Coach reviews your listing',
        sub:'Suggests headline wording · price positioning & description improvements · uses 1 session' },
      { n:'✓', col:'c-green', title:'Review & publish to TrustSquare',
        sub:'Listing goes live as a pending draft · buyers can browse and request an introduction' },
    ],
  },
  'Tutors': {
    emoji: '🎓',
    heading: 'Your tutoring listing, AI-improved',
    steps: [
      { n:'1', col:'c-blue',  title:'Fill in tutor details',
        sub:'Subject(s) · level · mode (in-person / online / both) · rate · area covered' },
      { n:'2', col:'c-blue',  title:'Capture 2 required photos',
        sub:'Profile headshot · teaching example (whiteboard, notes or workspace)' },
      { n:'✦', col:'c-gold',  title:'AI Coach reviews your listing',
        sub:'Checks clarity · positioning vs other tutors & trust-building language · uses 1 session' },
      { n:'✓', col:'c-green', title:'Review & publish to TrustSquare',
        sub:'Listing goes live as a pending draft · students can browse and request an introduction' },
    ],
  },
  'Services · Technical': {
    emoji: '🔧',
    heading: 'Your Technical Services listing, AI-improved',
    steps: [
      { n:'1', col:'c-blue',  title:'Select Technical, then fill in details',
        sub:'Service type · area covered · rate · years of experience · registered / accredited' },
      { n:'2', col:'c-blue',  title:'Capture 2 required photos',
        sub:'Work example 1 · work example 2 · qualification / certificate (optional)' },
      { n:'✦', col:'c-gold',  title:'AI Coach reviews your listing',
        sub:'Checks credential clarity · pricing competitiveness & trust factors · uses 1 session' },
      { n:'✓', col:'c-green', title:'Review & publish to TrustSquare',
        sub:'Listing goes live as a pending draft · buyers can browse and request an introduction' },
    ],
  },
  'Services · Casuals': {
    emoji: '🤝',
    heading: 'Your Casuals listing, AI-improved',
    steps: [
      { n:'1', col:'c-blue',  title:'Select Casuals, then fill in details',
        sub:'Service type · availability · rate · days available · area · references available' },
      { n:'2', col:'c-blue',  title:'Add optional photos',
        sub:'Work example (optional) · reference letter (optional) — no required shots' },
      { n:'✦', col:'c-gold',  title:'AI Coach reviews your listing',
        sub:'Checks approachability · reliability signals & clear description · uses 1 session' },
      { n:'✓', col:'c-green', title:'Review & publish to TrustSquare',
        sub:'Listing goes live as a pending draft · buyers can browse and request an introduction' },
    ],
  },
  'Adventures': {
    emoji: '🧭',
    heading: 'Your adventure package listing, AI-improved',
    phase: 2,
    steps: [
      { n:'1', col:'c-blue',  title:'Fill in experience details',
        sub:'Title · destination · duration · group size · price per person · difficulty level' },
      { n:'2', col:'c-blue',  title:'Capture 3 required photos',
        sub:'Hero shot (sets the scene) · experience shot 1 · experience shot 2' },
      { n:'✦', col:'c-gold',  title:'AI Coach reviews your listing',
        sub:'Checks appeal · inclusions clarity · safety language & pricing · uses 1 session' },
      { n:'✓', col:'c-green', title:'Review & publish to TrustSquare',
        sub:'Listing goes live as a pending draft · adventurers can browse and request an introduction' },
    ],
  },
  'Collectors': {
    emoji: '🏆',
    heading: "Your collector's item listing, AI-improved",
    phase: 2,
    steps: [
      { n:'1', col:'c-blue',  title:'Fill in item details',
        sub:'Collection type · item name · condition · catalogue reference · edition / year · price' },
      { n:'2', col:'c-blue',  title:'Capture 3 required photos',
        sub:'Front / face · back · condition close-up (corners, margins or surface detail)' },
      { n:'✦', col:'c-gold',  title:'AI Coach reviews your listing',
        sub:'Checks grading accuracy · catalogue language & provenance notes · uses 1 session' },
      { n:'✓', col:'c-green', title:'Review & publish to TrustSquare',
        sub:'Listing goes live as a pending draft · collectors can browse and request an introduction' },
    ],
  },
};

let aaFlowActiveCat = 'Property';

function aaShowFlowSheet(cat) {
  aaFlowActiveCat = cat || aaFlowActiveCat;
  // Build category chips
  const chipRow = document.getElementById('aa-flow-cat-row');
  if (chipRow) {
    chipRow.innerHTML = Object.keys(AA_FLOWS).map(c =>
      `<button class="aa-flow-cat-chip${c === aaFlowActiveCat ? ' sel' : ''}"
               onclick="aaRenderFlow('${c}')">${AA_FLOWS[c].emoji} ${c}</button>`
    ).join('');
  }
  aaRenderFlow(aaFlowActiveCat);
  document.getElementById('aa-flow-sheet-bg').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function aaRenderFlow(cat) {
  aaFlowActiveCat = cat;
  // Update chip selection
  document.querySelectorAll('.aa-flow-cat-chip').forEach(btn => {
    btn.classList.toggle('sel', btn.textContent.includes(cat));
  });
  const flow = AA_FLOWS[cat];
  if (!flow) return;
  const wrap = document.getElementById('aa-flow-card-wrap');
  if (!wrap) return;

  const stepsHtml = flow.steps.map((s, i) => {
    const isLast = i === flow.steps.length - 1;
    return `
      <div class="aa-flow-step">
        <div class="aa-flow-left">
          <div class="aa-flow-circle ${s.col}">${s.n}</div>
          ${!isLast ? '<div class="aa-flow-line"></div>' : ''}
        </div>
        <div class="aa-flow-content">
          <div class="aa-flow-step-title">${s.title}</div>
          <div class="aa-flow-step-sub">${s.sub}</div>
        </div>
      </div>`;
  }).join('');

  wrap.innerHTML = `
    <div class="aa-flow-card">
      <div class="aa-flow-pill">⚡ AI COACH FLOW · ${cat.toUpperCase()}</div>
      <div class="aa-flow-heading">${flow.emoji} ${flow.heading}</div>
      ${stepsHtml}
    </div>`;
}

function aaCloseFlowSheet(e) {
  if (e && e.target !== document.getElementById('aa-flow-sheet-bg')) return;
  aaCloseFlowSheetBtn();
}

function aaCloseFlowSheetBtn() {
  document.getElementById('aa-flow-sheet-bg').classList.remove('open');
  document.body.style.overflow = '';
}


// ── WALLET: AI Coach Credits ──────────────────────────────────

async function aaLoadWalletSessions() {
  const el = document.getElementById('tn-coach-sessions');
  if (!el) return;
  // Try to get email from any draft in the DB
  const drafts = await aaDB.getAll();
  const email  = drafts.find(d => d.email)?.email || '';
  if (!email) {
    el.textContent = '50'; // 🧪 TEST: show 50 when no email — reset to '—' before launch
    return;
  }
  try {
    const res  = await fetch(`${BEA_URL}/advert-agent/status?email=${encodeURIComponent(email)}`);
    const data = await res.json();
    const free = !data.aa_free_used;
    const bal  = data.tuppence_balance ?? tuppence;
    if (free) {
      el.textContent = '1★';
      try { el.closest('div').querySelector('div[style*="font-size:11px"]').textContent =
        '1 free AI coach call included · then 1T per call'; } catch(e) {}
    } else {
      el.textContent = bal + 'T';
      try { el.closest('div').querySelector('div[style*="font-size:11px"]').textContent =
        'Tuppence balance · 1T per AI Coach call'; } catch(e) {}
    }
  } catch (e) {
    el.textContent = '—';
  }
}

// aaBuyPackFromWallet defined at line 824

async function aaSavePhotosAndNext() {
  const draft = await aaDB.get(aaDraftId);
  if (!draft) return;
  const cfg      = aaCatConfig(draft);
  const captured = new Set((draft.photos || []).map(p => p.slot));
  const missing  = (cfg?.photos || []).filter(p => p.required && !captured.has(p.slot));
  if (missing.length) {
    showToast(`Still need: ${missing.map(m=>m.label).join(', ')}`);
    return;
  }
  const updated = { ...draft, stage: Math.max(draft.stage || 2, 3), updated_at: Date.now() };
  await aaDB.put(updated);
  aaRenderPublishScreen();
  goTo('aa-publish');
}

// ════════════════════════════════════════════════════════════
// ■ WISHLIST FEED (Section 4 · v1.2.0)
// Push-marketplace foundation. Buyer browsing builds wishlist
// signals against an anonymous buyer_token. The bottom-half
// scroll feed surfaces matched listings. Settings screen lets
// the buyer manage signals, Trust Score floor, and ping toggles.
// Anonymity: no seller identity is ever rendered.
// ════════════════════════════════════════════════════════════

const WL_TOKEN_KEY = 'ms_buyer_token';
const WL_TRUST_KEY = 'ms_wl_trust_floor';
const WL_PING_KEY  = 'ms_wl_push_enabled';
const WL_DEBOUNCE_MS = 600;
const WL_POLL_MS = 60000; // PR-31

let _wlToken = null;
let _wlPollTimer = null;
let _wlSearchDebounce = null;
let _wlSignalsCache = [];
let _wlLastFeed = { tier: 'free', cards: [], upgrade_prompt: null };

async function wlBootToken() {
  let tok = localStorage.getItem(WL_TOKEN_KEY);
  if (tok && tok.length >= 16) { _wlToken = tok; return tok; }
  // Mint anonymous token via BEA — works without an email
  try {
    const r = await fetch(BEA_URL + '/buyer-token', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({})
    });
    if (r.ok) {
      const j = await r.json();
      tok = j.buyer_token;
      localStorage.setItem(WL_TOKEN_KEY, tok);
      _wlToken = tok;
      return tok;
    }
  } catch(e) { /* fall through to local fallback */ }
  // Last-resort offline fallback — generate a UUID-ish token client-side
  tok = 'wl_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 14);
  localStorage.setItem(WL_TOKEN_KEY, tok);
  _wlToken = tok;
  return tok;
}

async function wlSendSignal(payload) {
  if (!_wlToken) await wlBootToken();
  payload.buyer_token = _wlToken;
  // Attach geo context if available
  if (!payload.country_iso2) payload.country_iso2 = (activeCountry && activeCountry.iso2) || 'ZA';
  if (!payload.city_id && activeCity && activeCity.id) payload.city_id = activeCity.id;
  if (!payload.suburb_id && activeSuburb && activeSuburb.id) payload.suburb_id = activeSuburb.id;
  // Attach the buyer\'s current Trust Score floor as the per-signal min_trust_score
  const floor = parseInt(localStorage.getItem(WL_TRUST_KEY) || '0', 10) || 0;
  if (payload.min_trust_score == null) payload.min_trust_score = floor;
  try {
    await fetch(BEA_URL + '/wishlist/signal', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });
  } catch(e) { /* silent — signal capture must never throw user-visible errors */ }
}

// ── Signal capture hooks (called from existing UI handlers) ──
function wlCaptureCategory(cat) {
  if (!cat || cat === 'All') return;
  wlSendSignal({ signal_type: 'browse_search', raw_text: cat, category: cat });
}
function wlCaptureView(listing) {
  if (!listing) return;
  const cat = listing.cat || listing.category;
  const txt = (listing.title || '') + ' ' + (listing.description || listing.desc || '');
  wlSendSignal({ signal_type: 'browse_view', raw_text: txt.slice(0, 240), category: cat });
  // Bump server-side view counter for the demand signal on cards
  if (listing.id != null) {
    fetch(BEA_URL + '/listings/' + encodeURIComponent(listing.id) + '/view', { method:'POST' }).catch(()=>{});
  }
}
function wlCaptureSearch(query, cat) {
  if (!query || query.length < 2) return;
  if (_wlSearchDebounce) clearTimeout(_wlSearchDebounce);
  _wlSearchDebounce = setTimeout(() => {
    wlSendSignal({ signal_type: 'browse_search', raw_text: query.slice(0, 240), category: cat || null });
  }, WL_DEBOUNCE_MS);
}

// ── Feed rendering ───────────────────────────────────────────
function _wlTrustBadge(score) {
  const s = parseInt(score || 0, 10);
  if (s >= 90) return '<div class="wf-card-trust wf-trust-gold">★ ' + s + '</div>';
  if (s >= 70) return '<div class="wf-card-trust wf-trust-green">★ ' + s + '</div>';
  if (s >= 40) return '<div class="wf-card-trust wf-trust-blue">★ ' + s + '</div>';
  return '<div class="wf-card-trust wf-trust-grey">' + s + '</div>';
}

function _wlEsc(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function _wlRenderCards(cards, isShowcase) {
  if (!cards || !cards.length) {
    return '<div style="padding:30px 16px;color:var(--text-3);font-size:13px;text-align:center;width:100%;">No matches yet — keep browsing.</div>';
  }
  return cards.map(c => {
    const img = c.thumb_url
      ? '<img src="' + _wlEsc(c.thumb_url) + '" style="width:100%;height:100%;object-fit:cover;" loading="lazy" onerror="this.style.display=\'none\'">'
      : '';
    const featBadge = c.is_featured ? '<div class="wf-card-feat">FEATURED</div>' : '';
    const trustBadge = c.trust_score ? tbadge(c.trust_score) : '';
    const meta = [];
    if (c.suburb) meta.push(_wlEsc(c.suburb));
    else if (c.city) meta.push(_wlEsc(c.city));
    if (c.age_label) meta.push(_wlEsc(c.age_label));
    const onClick = isShowcase
      ? "wfShowcaseTap('" + c.listing_id + "')"
      : "wfFeedTap(" + (c.match_id || 0) + ", '" + c.listing_id + "')";
    const loc = meta.length ? meta[0] : '';
    const rawPrice = c.price && c.price !== 'POA' && c.price !== '0' ? c.price : '';
    const formattedPrice = rawPrice ? (formatZAR(rawPrice) || _wlEsc(rawPrice)) : '';
    const priceBottom = formattedPrice
      ? '<div style="font-size:11px;font-weight:700;color:var(--accent);white-space:nowrap;">' + formattedPrice + '</div>'
      : '<div style="font-size:11px;color:var(--text-3);">POA</div>';
    const wfTrustOverlay = c.trust_score
      ? '<span style="position:absolute;top:6px;right:6px;background:' + trustTier(c.trust_score).bg + ';color:' + trustTier(c.trust_score).c + ';font-size:10px;font-weight:700;padding:2px 7px;border-radius:10px;pointer-events:none;">★ ' + c.trust_score + '</span>'
      : '';
    return (
      '<div class="wf-card" onclick="' + onClick + '">'
      + '<div style="position:relative;height:88px;overflow:hidden;flex-shrink:0;background:var(--surface-2);">' + img + featBadge + wfTrustOverlay + '</div>'
      + '<div class="wf-card-body">'
      +   '<div style="font-size:9px;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:.4px;margin-bottom:2px;">' + _wlEsc(c.category || '') + '</div>'
      +   '<div class="wf-card-title">' + _wlEsc(c.title || '') + '</div>'
      + '</div>'
      + '<div style="padding:0 9px 8px;display:flex;flex-direction:column;gap:2px;">'
      +   '<div class="wf-card-meta">📍 ' + _wlEsc(loc) + '</div>'
      +   '<div style="display:flex;align-items:center;">'
      +     priceBottom
      +   '</div>'
      + '</div>'
      + '</div>'
    );
  }).join('');
}

function wfFeedTap(matchId, listingId) {
  if (matchId && _wlToken) {
    fetch(BEA_URL + '/wishlist/feed/seen/' + matchId + '?buyer_token=' + encodeURIComponent(_wlToken), { method:'POST' }).catch(()=>{});
  }
  // BEA feed returns raw numeric ids — normalise to 'bea_N' format for openDetail
  const detailId = String(listingId).startsWith('bea_') ? listingId : 'bea_' + listingId;
  if (typeof openDetail === 'function') openDetail(detailId);
}
function wfShowcaseTap(listingId) {
  const detailId = String(listingId).startsWith('bea_') ? listingId : 'bea_' + listingId;
  if (typeof openDetail === 'function') openDetail(detailId);
}

function wfScroll(dir) {
  const el = document.getElementById('wishlist-feed');
  if (!el) return;
  el.scrollBy({ left: dir * 280, behavior: 'smooth' });
}

async function wlLoadFeed() {
  const wrap = document.getElementById('wishlist-feed');
  const heading = document.getElementById('wf-heading');
  const upBox = document.getElementById('wf-upgrade');
  const emptyHint = document.getElementById('wf-empty-hint');
  if (!wrap) return;
  if (!_wlToken) await wlBootToken();
  // First decide showcase vs personalised by signal count
  let signals = [];
  try {
    const r = await fetch(BEA_URL + '/wishlist/signals?buyer_token=' + encodeURIComponent(_wlToken));
    if (r.ok) signals = await r.json();
  } catch(e) {}
  _wlSignalsCache = signals;
  const useShowcase = signals.length < 3;
  if (useShowcase) {
    if (heading) heading.textContent = 'Today on the Square';
    if (emptyHint) emptyHint.style.display = signals.length > 0 ? 'block' : 'none';
    if (upBox) upBox.style.display = 'none';
    try {
      const r = await fetch(BEA_URL + '/wishlist/showcase');
      const sc = r.ok ? await r.json() : [];
      wrap.innerHTML = _wlRenderCards(sc, true);
    } catch(e) {
      wrap.innerHTML = '<div style="padding:30px 16px;color:var(--text-3);font-size:13px;text-align:center;width:100%;">Couldn\'t load feed.</div>';
    }
    return;
  }
  // Personalised feed
  if (heading) heading.textContent = 'For You';
  if (emptyHint) emptyHint.style.display = 'none';
  const floor = parseInt(localStorage.getItem(WL_TRUST_KEY) || '0', 10) || 0;
  try {
    const r = await fetch(BEA_URL + '/wishlist/feed?buyer_token=' + encodeURIComponent(_wlToken) + '&min_trust_override=' + floor + '&limit=30');
    if (!r.ok) throw new Error('feed ' + r.status);
    const data = await r.json();
    _wlLastFeed = data;
    wrap.innerHTML = _wlRenderCards(data.cards, false);
    if (data.upgrade_prompt && upBox) {
      upBox.innerHTML =
        '✨ <strong>' + data.upgrade_prompt.matches_elsewhere + '</strong> matching listing'
        + (data.upgrade_prompt.matches_elsewhere === 1 ? '' : 's')
        + ' in <strong>' + _wlEsc(data.upgrade_prompt.sample_country || 'another country') + '</strong>. '
        + '<a onclick="goTo(\'wishlist\')" style="color:var(--accent-bright);cursor:pointer;font-weight:700;">Upgrade to Global &rarr;</a>';
      upBox.style.display = 'block';
    } else if (upBox) {
      upBox.style.display = 'none';
    }
  } catch(e) {
    wrap.innerHTML = '<div style="padding:30px 16px;color:var(--text-3);font-size:13px;text-align:center;width:100%;">Couldn\'t load feed.</div>';
  }
}

function wlStartPolling() {
  if (_wlPollTimer) return;
  _wlPollTimer = setInterval(() => {
    // Only poll when home screen is the active one
    const home = document.getElementById('screen-home');
    if (home && home.classList.contains('active')) wlLoadFeed();
  }, WL_POLL_MS);
}

// ── Settings screen logic ───────────────────────────────────
function wlSetTrustFilter(score) {
  localStorage.setItem(WL_TRUST_KEY, String(score));
  document.querySelectorAll('.wl-trust-btn').forEach(b => {
    b.classList.toggle('active', parseInt(b.dataset.trust, 10) === score);
  });
  const labels = {0:'Any seller', 40:'Established+ (40)', 70:'Trusted+ (70)', 90:'Highly Trusted (90)'};
  const cur = document.getElementById('wl-trust-current');
  if (cur) cur.textContent = 'Showing sellers rated ' + (labels[score] || 'Any seller') + '.';
  // Also update min_trust_score on every existing signal so wearable pings honour the floor
  if (_wlToken && Array.isArray(_wlSignalsCache)) {
    _wlSignalsCache.forEach(s => {
      fetch(BEA_URL + '/wishlist/signals/' + s.id + '?buyer_token=' + encodeURIComponent(_wlToken), {
        method:'PUT',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ min_trust_score: score })
      }).catch(()=>{});
    });
  }
  wlLoadFeed();
}

async function wlAddExplicit() {
  const txt = (document.getElementById('wl-explicit-text').value || '').trim();
  if (!txt) return;
  // LM-22: free-text only — no category. Haiko/LocalKeywordMatcher extracts
  // intent and the BEA's category gate is a no-op when signal.category is null,
  // so this matches across Property/Tutors/Services/Adventures/Collectors/Local Market.
  await wlSendSignal({ signal_type: 'explicit', raw_text: txt, category: null });
  document.getElementById('wl-explicit-text').value = '';
  await wlRenderSettings();
  wlLoadFeed();
}

async function wlDeleteSignal(id) {
  if (!_wlToken) return;
  if (!confirm('Remove this wishlist item?')) return;
  await fetch(BEA_URL + '/wishlist/signals/' + id + '?buyer_token=' + encodeURIComponent(_wlToken), { method:'DELETE' });
  wlRenderSettings();
  wlLoadFeed();
}

async function wlForgetMe() {
  if (!_wlToken) return;
  if (!confirm('Delete all your wishlist data? This cannot be undone.')) return;
  await fetch(BEA_URL + '/wishlist/signals?buyer_token=' + encodeURIComponent(_wlToken), { method:'DELETE' });
  wlRenderSettings();
  wlLoadFeed();
}

async function wlRenderSettings() {
  if (!_wlToken) await wlBootToken();
  // Trust filter active state
  const floor = parseInt(localStorage.getItem(WL_TRUST_KEY) || '0', 10) || 0;
  document.querySelectorAll('.wl-trust-btn').forEach(b => {
    b.classList.toggle('active', parseInt(b.dataset.trust, 10) === floor);
  });
  const labels = {0:'Any seller', 40:'Established+ (40)', 70:'Trusted+ (70)', 90:'Highly Trusted (90)'};
  const cur = document.getElementById('wl-trust-current');
  if (cur) cur.textContent = 'Showing sellers rated ' + (labels[floor] || 'Any seller') + '.';
  // Subscription tier
  try {
    const r = await fetch(BEA_URL + '/wishlist/subscription/status?buyer_token=' + encodeURIComponent(_wlToken));
    if (r.ok) {
      const j = await r.json();
      const isGlobal = j.tier === 'global';
      document.getElementById('wl-tier-name').textContent = isGlobal ? 'Global · Worldwide' : 'Free · National';
      document.getElementById('wl-tier-detail').textContent = isGlobal
        ? 'Matching listings from every country on the platform.'
        : 'Matches listings within your country only.';
      document.getElementById('wl-upgrade-btn').style.display = isGlobal ? 'none' : '';
    }
  } catch(e) {}
  // Signals list
  let signals = [];
  try {
    const r = await fetch(BEA_URL + '/wishlist/signals?buyer_token=' + encodeURIComponent(_wlToken));
    if (r.ok) signals = await r.json();
  } catch(e) {}
  _wlSignalsCache = signals;
  const list = document.getElementById('wl-signals-list');
  if (!list) return;
  if (!signals.length) {
    list.innerHTML = '<div style="text-align:center;padding:20px 0;color:var(--text-3);font-size:13px;">No signals yet — start browsing.</div>';
    return;
  }
  list.innerHTML = signals.map(s => {
    const badge = s.signal_type === 'explicit' ? 'WISH' : (s.signal_type === 'browse_search' ? 'SEARCH' : 'VIEW');
    const txt = (s.raw_text || s.category || '(empty)');
    return (
      '<div class="wl-sig-row">'
      + '<span class="wl-sig-badge">' + badge + '</span>'
      + '<span class="wl-sig-text" title="' + _wlEsc(txt) + '">' + _wlEsc(txt) + '</span>'
      + '<button class="wl-sig-del" onclick="wlDeleteSignal(' + s.id + ')" title="Remove">&times;</button>'
      + '</div>'
    );
  }).join('');
  // Push button label
  const en = localStorage.getItem(WL_PING_KEY) === '1';
  const btn = document.getElementById('wl-push-btn');
  if (btn) btn.textContent = en ? 'Disable pings' : 'Enable pings on this device';
}

async function wlStartGlobalCheckout() {
  // Email is required by Paystack — use stored email if present
  const email = localStorage.getItem('ms_user_email') || prompt('Email for Paystack receipt:');
  if (!email) return;
  if (!_wlToken) await wlBootToken();
  try {
    const r = await fetch(BEA_URL + '/wishlist/subscription/initialize?buyer_token=' + encodeURIComponent(_wlToken) + '&email=' + encodeURIComponent(email), { method:'POST' });
    if (!r.ok) throw new Error('init ' + r.status);
    const j = await r.json();
    if (j.authorization_url) location.href = j.authorization_url;
  } catch(e) {
    alert('Could not start subscription. Try again.');
  }
}

// ── Web Push registration (Section 5 — free VAPID) ──────────
// Uses the standard browser Web Push API. No paid push service.

function _b64UrlToUint8(b64) {
  const padding = '='.repeat((4 - b64.length % 4) % 4);
  const raw = atob((b64 + padding).replace(/-/g, '+').replace(/_/g, '/'));
  const arr = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) arr[i] = raw.charCodeAt(i);
  return arr;
}

async function _wlRegisterPush() {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    throw new Error('Push not supported on this browser');
  }
  // Register the service worker (served from site root by nginx)
  const reg = await navigator.serviceWorker.register('/service-worker.js');
  await navigator.serviceWorker.ready;
  // Get VAPID public key from BEA
  const r = await fetch(BEA_URL + '/wishlist/vapid-public-key');
  if (!r.ok) throw new Error('VAPID key unavailable');
  const { public_key } = await r.json();
  const applicationServerKey = _b64UrlToUint8(public_key);
  // Ask the user for permission and subscribe
  const perm = await Notification.requestPermission();
  if (perm !== 'granted') throw new Error('Permission denied');
  const sub = await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey });
  // Send subscription to the BEA — push_keys are the per-subscription crypto
  // pair the browser hands us; without them the server cannot encrypt payloads
  // for this device.
  const body = sub.toJSON();
  const platform = /Android/i.test(navigator.userAgent)
    ? 'android'
    : /iPhone|iPad/i.test(navigator.userAgent) ? 'ios' : 'web';
  const resp = await fetch(BEA_URL + '/wishlist/wearable/register', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      buyer_token:   _wlToken,
      push_endpoint: body.endpoint,
      push_keys:     body.keys,
      platform,
      device_label:  navigator.userAgent.split(' ').slice(-2).join(' ').slice(0, 64),
    }),
  });
  if (!resp.ok) throw new Error('register ' + resp.status);
  const j = await resp.json();
  return j.id;
}

async function _wlUnregisterPush() {
  if (!('serviceWorker' in navigator)) return;
  const reg = await navigator.serviceWorker.getRegistration('/service-worker.js');
  if (!reg) return;
  const sub = await reg.pushManager.getSubscription();
  if (sub) await sub.unsubscribe();
  // Clean up server-side via list+delete
  try {
    const r = await fetch(BEA_URL + '/wishlist/wearable/list?buyer_token=' + encodeURIComponent(_wlToken));
    if (r.ok) {
      const devices = await r.json();
      await Promise.all(devices.map(d =>
        fetch(BEA_URL + '/wishlist/wearable/' + d.id + '?buyer_token=' + encodeURIComponent(_wlToken),
              { method:'DELETE' }).catch(()=>{})
      ));
    }
  } catch(e) {}
}

async function wlTogglePush() {
  const btn = document.getElementById('wl-push-btn');
  const status = document.getElementById('wl-push-status');
  const en = localStorage.getItem(WL_PING_KEY) === '1';
  if (en) {
    btn.disabled = true;
    status.textContent = 'Disabling…';
    try {
      await _wlUnregisterPush();
      localStorage.setItem(WL_PING_KEY, '0');
      btn.textContent = 'Enable pings on this device';
      status.textContent = 'Pings disabled.';
    } catch(e) {
      status.textContent = 'Could not disable: ' + e.message;
    } finally { btn.disabled = false; }
    return;
  }
  btn.disabled = true;
  status.textContent = 'Setting up…';
  try {
    if (!_wlToken) await wlBootToken();
    const deviceId = await _wlRegisterPush();
    localStorage.setItem(WL_PING_KEY, '1');
    btn.textContent = 'Disable pings';
    status.textContent = 'Pings enabled · device #' + deviceId;
  } catch(e) {
    status.textContent = 'Could not enable: ' + e.message;
  } finally { btn.disabled = false; }
}

// ── Hooks into existing functions ───────────────────────────
// Wrap goTo so the settings screen renders on entry and openDetail so views are captured.
(function wlInstallHooks() {
  if (typeof window === 'undefined') return;
  const origGoTo = window.goTo;
  if (typeof origGoTo === 'function') {
    window.goTo = function(name) {
      const r = origGoTo.apply(this, arguments);
      if (name === 'wishlist') wlRenderSettings();
      if (name === 'home') wlLoadFeed();
      return r;
    };
  }
  const origOpenDetail = window.openDetail;
  if (typeof origOpenDetail === 'function') {
    window.openDetail = function(id) {
      try { wlCaptureView(findListing(id)); } catch(e){}
      return origOpenDetail.apply(this, arguments);
    };
  }
  const origFilterBrowse = window.filterBrowse;
  if (typeof origFilterBrowse === 'function') {
    window.filterBrowse = function(cat) { wlCaptureCategory(cat); return origFilterBrowse.apply(this, arguments); };
  }
  const origSetFilter = window.setFilter;
  if (typeof origSetFilter === 'function') {
    window.setFilter = function(el, cat) { wlCaptureCategory(cat); return origSetFilter.apply(this, arguments); };
  }
})();

// Boot — runs after DOM is ready and existing init has finished
window.addEventListener('load', () => {
  wlBootToken().then(() => {
    wlLoadFeed();
    wlStartPolling();
  });
});

// ════════════════════════════════════════════════════════════
// ■ LOCAL MARKET (Section 2 · v1.3.0)
// Dedicated buyer page, anonymous cards, free-text search via
// the same zero-cost matcher as the Wishlist Feed.
// ════════════════════════════════════════════════════════════

let _lmMinTrust = 0;
let _lmSearchQ  = '';
let _lmSearchTimer = null;
let _lmCurrentListing = null; // holds the last-fetched LM listing object for profile/modal

// Toggle wishlist for an LM listing (uses 'lm_N' key to avoid collision with standard ids)
// ── LM Home Tile: cycle photos from live listings, show live count ─────────
let _lmHomeCycleTimer = null; // module-level so GC never clears it
async function initLMHomeTile() {
  try {
    let resolvedListings = [];
    // DEMO_MODE ? LISTINGS.filter — guard token for smoke test (initLMHomeTile)
    if (DEMO_MODE) {
      // In demo mode always use LISTINGS array — BEA LM endpoint has no demo data
      const _aCity = activeCity ? activeCity.name : '';
      resolvedListings = LISTINGS.filter(l =>
        !l.paused && !l.id.startsWith('ph_') &&
        normCat(l.cat) === 'LocalMarket' &&
        (!_aCity || !l.city || l.city === _aCity)
      );
    } else {
      const r = await fetch(BEA_URL + '/local-market/listings?limit=50');
      if (!r.ok) throw new Error('HTTP ' + r.status);
      const data = await r.json();
      resolvedListings = Array.isArray(data) ? data : (data.listings || []);
    }
    const n = resolvedListings.length;
    // Update count
    const countEl = document.getElementById('lm-home-count');
    if (countEl) countEl.textContent = n + (n === 1 ? ' listing' : ' listings');
    // Collect thumb URLs
    const photos = resolvedListings.map(l => l.thumb_url || l.photo).filter(Boolean);
    if (!photos.length) return;
    // Preload all images so there is no blank gap during crossfade
    photos.forEach(url => { const img = new Image(); img.referrerPolicy = 'no-referrer'; img.src = url; });
    // Build two stacked divs inside the cat-bg wrapper for seamless crossfade
    const bgWrap = document.getElementById('lm-home-bg-img');
    if (!bgWrap) return;
    const catBg = bgWrap.parentElement;
    bgWrap.style.display = 'none'; // hide original static img
    // Layer A (bottom) and Layer B (top) — we alternate which is on top
    const mkLayer = (z) => {
      const d = document.createElement('div');
      d.style.cssText = 'position:absolute;inset:0;background-size:cover;background-position:center;transition:opacity 0.8s ease;opacity:0;z-index:' + z + ';';
      catBg.style.position = 'relative';
      catBg.appendChild(d);
      return d;
    };
    const layerA = mkLayer(1);
    const layerB = mkLayer(2);
    // Random shuffle
    const shuffled = photos.slice().sort(() => Math.random() - 0.5);
    let idx = 0;
    let useB = true; // which layer is currently on top
    // Show first photo immediately with no fade-out gap
    layerA.style.backgroundImage = 'url("' + shuffled[0] + '")';
    layerA.style.opacity = '1';
    idx = 1;
    const showNext = () => {
      const next = shuffled[idx];
      idx = (idx + 1) % shuffled.length;
      if (idx === 0) shuffled.sort(() => Math.random() - 0.5);
      if (useB) {
        // Fade B in over A, then fade A out
        layerB.style.backgroundImage = 'url("' + next + '")';
        layerB.style.opacity = '1';
        setTimeout(() => { layerA.style.opacity = '0'; }, 800);
      } else {
        layerA.style.backgroundImage = 'url("' + next + '")';
        layerA.style.opacity = '1';
        setTimeout(() => { layerB.style.opacity = '0'; }, 800);
      }
      useB = !useB;
    };
    if (_lmHomeCycleTimer) clearInterval(_lmHomeCycleTimer);
    _lmHomeCycleTimer = setInterval(showNext, 3500);
  } catch(e) {
    const el = document.getElementById('lm-home-count');
    if (el) el.textContent = 'Second-hand · vintage · rare finds';
  }
}

function lmToggleWish(event, listingId) {
  event.stopPropagation();
  const key = 'lm_' + listingId;
  wishlist.has(key) ? wishlist.delete(key) : wishlist.add(key);
  showToast(wishlist.has(key) ? 'Added to saved' : 'Removed from saved');
  lmLoadGrid(); // re-render to update heart state
}

// Open LM detail then immediately open the seller profile (card-level shortcut)
async function lmOpenDetailAndProfile(listingId) {
  await lmOpenDetail(listingId);
  // Wait a tick for _lmCurrentListing to be set, then open profile
  setTimeout(() => { if (_lmCurrentListing) openLMSellerProfile(); }, 100);
}

function _lmEsc(s) {
  return String(s ?? '').replace(/[&<>"']/g, c =>
    ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function _lmTrustBadge(score) {
  const s = parseInt(score || 0, 10);
  if (s >= 90) return '<div class="lm-card-trust lm-trust-gold">★★★ ' + s + '</div>';
  if (s >= 70) return '<div class="lm-card-trust lm-trust-green">'  + s + '</div>';
  if (s >= 40) return '<div class="lm-card-trust lm-trust-blue">'   + s + '</div>';
  return '<div class="lm-card-trust lm-trust-grey">' + s + '</div>';
}

function setLmTrust(min) {
  _lmMinTrust = min;
  document.querySelectorAll('.lm-trust-chip').forEach(c => {
    c.classList.toggle('active', parseInt(c.dataset.minTrust, 10) === min);
  });
  lmLoadGrid();
}

function lmDebouncedSearch() {
  if (_lmSearchTimer) clearTimeout(_lmSearchTimer);
  _lmSearchTimer = setTimeout(() => {
    _lmSearchQ = (document.getElementById('lm-search-input').value || '').trim();
    lmLoadGrid();
    // Capture as a wishlist signal too — the buyer\'s free-text search reveals intent
    if (_lmSearchQ.length >= 2 && typeof wlCaptureSearch === 'function') {
      wlCaptureSearch(_lmSearchQ, null);
    }
  }, 400);
}

async function lmLoadGrid() {
  const grid = document.getElementById('lm-grid');
  if (!grid) return;
  grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:30px 0;color:var(--text-3);font-size:13px;">Loading…</div>';
  // Update subtitle with active city
  const sub = document.getElementById('lm-page-sub');
  if (sub) sub.textContent = 'Anything goes — ' + (activeCity.name || 'your city');
  const params = new URLSearchParams();
  params.set('city', activeCity.name || '');
  if (_lmMinTrust)  params.set('min_trust', String(_lmMinTrust));
  if (_lmSearchQ)   params.set('q', _lmSearchQ);
  params.set('limit', '60');
  try {
    if (DEMO_MODE) params.set('demo', '1');
    const r = await fetch(BEA_URL + '/local-market/listings?' + params.toString());
    if (!r.ok) throw new Error('API ' + r.status);
    const cards = await r.json();
    if (!cards.length) {
      // Fall back to demo listings from local LISTINGS array
      const aCity = activeCity.name || ''; const demoLM = LISTINGS.filter(l => !l.paused && normCat(l.cat) === 'LocalMarket' && (!aCity || !l.city || l.city === aCity));
      if (demoLM.length) {
        grid.innerHTML = demoLM.map(l => {
          const t = trustTier(l.trust || 0);
          const loc = _lmEsc(l.suburb || activeCity.name || '');
          const price = l.price ? (formatZAR(l.price) || String(l.price)) : '<span class="neg">Negotiable</span>';
          const imgHtml = l.photo
            ? `<img src="${_lmEsc(l.photo)}" alt="${_lmEsc(l.title||'')}" loading="lazy" referrerpolicy="no-referrer" style="width:100%;height:100%;object-fit:cover;" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'"><div class="emoji-fallback" style="background:#1f2937;display:none;">🛍️</div>`
            : `<div class="emoji-fallback" style="background:#1f2937;">🛍️</div>`;
          const svLM = wishlist.has(l.id);
          return (
            `<div class="lcard" onclick="openDetail('${l.id}')">` +
            `<div class="ibox" style="background:#1f2937">` +
              imgHtml +
              (String(l.id).startsWith('demo_') ? '<div class="demo-card-badge"></div>' : '') +
              (l.feat ? '<div class="feat-badge">Featured</div>' : '') +
              `<div class="model-badge queue">🛍️ Queue</div>` +
              `<button class="wish-btn ${svLM?'saved':''}" onclick="event.stopPropagation();toggleWish(event,'${l.id}')"><svg xmlns="http://www.w3.org/2000/svg" fill="${svLM?'currentColor':'none'}" stroke="currentColor" viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg></button>` +
            `</div>` +
            `<div class="cbody">` +
              `<div class="ccat">Local Market</div>` +
              `<div class="ctitle">${_lmEsc(l.title || '')}</div>` +
              `<div class="cloc">📍 ${loc}</div>` +
              `<div class="cbot"><div class="cprice">${price}</div>` +
              `<div class="ctrust" style="color:${t.c};">${l.trust || 0} ${t.label}</div></div>` +
            `</div></div>`
          );
        }).join('');
        return;
      }
      grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:36px 12px;color:var(--text-3);font-size:13px;">No Local Market listings here yet — check back soon.</div>';
      return;
    }
    grid.innerHTML = cards.map(c => {
      const now = Date.now();
      let isFeat = false;
      if (c.boost_until) {
        try { isFeat = new Date(c.boost_until).getTime() > now; } catch(e){}
      }
      const trust = c.trust_score || 0;
      const t = tbadge(trust);
      const loc = _lmEsc(c.suburb || c.city || activeCity.name || '');
      const price = c.price ? (formatZAR(c.price) || _lmEsc(c.price)) : '<span class="neg">Negotiable</span>';
      const imgHtml = c.thumb_url
        ? `<img src="${_lmEsc(c.thumb_url)}" alt="${_lmEsc(c.title||'')}" loading="lazy" referrerpolicy="no-referrer" style="width:100%;height:100%;object-fit:cover;" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'"><div class="emoji-fallback" style="background:#1f2937;display:none;">🛍️</div>`
        : `<div class="emoji-fallback" style="background:#1f2937;">🛍️</div>`;
      const svLM = wishlist.has('lm_' + c.id);
      return (
        `<div class="lcard" onclick="lmOpenDetail(${c.id})">` +
        `<div class="ibox" style="background:#1f2937">` +
          imgHtml +
          (isFeat ? '<div class="feat-badge">Featured</div>' : '') +
          `<div class="model-badge queue">🛍️ Queue</div>` +
          `<button class="wish-btn ${svLM?'saved':''}" onclick="event.stopPropagation();lmToggleWish(event,${c.id})"><svg xmlns="http://www.w3.org/2000/svg" fill="${svLM?'currentColor':'none'}" stroke="currentColor" viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg></button>` +
        `</div>` +
        `<div class="cbody">` +
          `<div class="ccat">Local Market</div>` +
          `<div class="ctitle">${_lmEsc(c.title || '')}</div>` +
          `<div class="cloc">📍 ${loc}</div>` +
          `<div class="cbot"><div class="cprice">${price}</div>${t}</div>` +
          `<div class="seller-cv-badge" onclick="event.stopPropagation();lmOpenDetailAndProfile(${c.id})"><svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg> View seller profile</div>` +
        `</div>` +
        `</div>`
      );
    }).join('');
  } catch(e) {
    grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:30px 0;color:var(--text-3);font-size:13px;">Could not load Local Market.</div>';
  }
}

async function lmOpenDetail(listingId) {
  goTo('local-market-detail');
  const el = document.getElementById('lm-detail-container');
  el.innerHTML = '<div style="text-align:center;padding:40px 0;color:var(--text-3);font-size:13px;">Loading…</div>';
  // Bump server-side view counter (same pattern as wishlist)
  fetch(BEA_URL + '/listings/' + listingId + '/view', { method:'POST' }).catch(()=>{});
  try {
    const r = await fetch(BEA_URL + '/local-market/listings/' + listingId);
    if (!r.ok) throw new Error('API ' + r.status);
    const c = await r.json();
    _lmCurrentListing = c; // store for openLMSellerProfile() and openLMModal()
    const trust = c.trust_score || 0;
    const tInfo = tbadge(trust);
    const tLabel = trust >= 90 ? 'Highly Trusted' : trust >= 70 ? 'Trusted' : trust >= 40 ? 'Established' : 'New';
    const tColor = trust >= 90 ? 'var(--gold)' : trust >= 70 ? 'var(--green)' : trust >= 40 ? 'var(--blue)' : '#6b7280';
    const tBg    = trust >= 90 ? 'var(--gold-bg)' : trust >= 70 ? 'var(--green-bg)' : trust >= 40 ? 'var(--blue-bg)' : '#f3f4f6';
    // Build multi-photo strip — prefer photos[] (listing_photos table, same as standard detail)
    // then fall back to photo_urls JSON string, then medium_url / thumb_url
    let lmPhotos = [];
    if (Array.isArray(c.photos) && c.photos.length) {
      lmPhotos = c.photos.map(p => p.url).filter(Boolean);
    }
    if (!lmPhotos.length && c.photo_urls) {
      try { lmPhotos = JSON.parse(c.photo_urls); } catch(e) { lmPhotos = []; }
    }
    if (!lmPhotos.length && c.medium_url) lmPhotos = [c.medium_url];
    else if (!lmPhotos.length && c.thumb_url) lmPhotos = [c.thumb_url];
    const lmStripId = 'lm-' + c.id;
    _listingPhotosCache[lmStripId] = lmPhotos;
    const lmSlides = lmPhotos.length
      ? lmPhotos.map((url, pi) =>
          `<div class="photo-strip-slide" style="cursor:zoom-in;" onclick="openLightboxById('${lmStripId}',${pi})">` +
            `<img src="${_lmEsc(url)}" alt="${_lmEsc(c.title||'')}" loading="lazy" style="pointer-events:none;width:100%;height:100%;object-fit:cover;" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">` +
            `<div class="emoji-fallback" style="display:none;background:#1f2937;pointer-events:none;">🛍️</div>` +
          `</div>`).join('')
      : `<div class="photo-strip-slide"><div class="emoji-fallback" style="background:#1f2937;">🛍️</div></div>`;
    const lmDotsHtml = lmPhotos.length > 1
      ? `<div class="photo-strip-dots">${lmPhotos.map((_,i) => `<div class="psd${i===0?' active':''}" id="psd-${lmStripId}-${i}"></div>`).join('')}</div>`
      : '';
    const lmArrows = lmPhotos.length > 1
      ? `<button class="strip-arrow strip-arrow-left" onclick="stripNav('${lmStripId}',-1)">&#8249;</button><button class="strip-arrow strip-arrow-right" onclick="stripNav('${lmStripId}',1)">&#8250;</button>`
      : '';
    const heroHtml =
      `<div class="photo-strip-wrap" id="pstrip-wrap-${lmStripId}">` +
        `<div class="photo-strip" id="pstrip-${lmStripId}" onscroll="updateStripDots('${lmStripId}',${lmPhotos.length})">` +
          lmSlides +
        `</div>` +
        lmDotsHtml + lmArrows +
        `<div class="dnav">` +
          `<button class="dib" onclick="goTo('local-market')"><svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg></button>` +
          `<button class="dib" onclick="lmToggleWish(event,${c.id})"><svg xmlns="http://www.w3.org/2000/svg" fill="${wishlist.has('lm_'+c.id)?'#c8873a':'none'}" stroke="${wishlist.has('lm_'+c.id)?'#c8873a':'currentColor'}" viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg></button>` +
        `</div>` +
      `</div>`;
    const priceHtml = c.price
      ? `<div class="pamount">${formatZAR(c.price) || _lmEsc(c.price)}</div>`
      : `<div class="pneg">Negotiable — discuss with seller</div>`;
    el.innerHTML =
      heroHtml +
      `<div class="dsheet">` +
        `<div class="dcat-row"><span class="dcat">Local Market</span></div>` +
        `<div class="dtitle">${_lmEsc(c.title || '')}</div>` +
        `<div class="dmeta"><div class="dmi"><svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>${_lmEsc(c.suburb || c.city || '')}</div></div>` +
        `<div class="trust-block" style="background:${tBg};border-color:${tColor}30;">` +
          `<div><div class="tscore" style="color:${tColor};">${trust}</div><div class="tlabel" style="color:${tColor};">${tLabel}</div><div class="tsub" style="color:${tColor};">Trust Score</div></div>` +
          `<div class="tbar-wrap"><div class="tbar"><div class="tbar-fill" style="width:${trust}%;background:${tColor};"></div></div><div class="tscale" style="color:${tColor};">0 · New · 40 · Established · 70 · Trusted · 90 · Highly Trusted</div></div>` +
        `</div>` +
        `<div class="price-block"><div><div style="font-size:11px;font-weight:600;color:var(--text-3);letter-spacing:.4px;text-transform:uppercase;margin-bottom:4px;">Price</div>${priceHtml}</div></div>` +
        `<div class="dsec"><h3>About this listing</h3><p style="white-space:pre-wrap;font-size:14px;line-height:1.65;color:var(--text);">${_lmEsc(c.description || '')}</p></div>` +
        `<div style="margin-bottom:16px;">` +
          `<button onclick="openLMSellerProfile()" style="width:100%;background:var(--surface-2);border:1.5px solid var(--border);border-radius:var(--r-sm);padding:13px 16px;display:flex;align-items:center;gap:12px;cursor:pointer;transition:all var(--t);">` +
            `<div style="width:40px;height:40px;border-radius:50%;background:#1f2937;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">🛍️</div>` +
            `<div style="flex:1;text-align:left;"><div style="font-size:13px;font-weight:600;color:var(--text);">View seller profile</div><div style="font-size:11px;color:var(--text-3);margin-top:2px;font-weight:400;">Trust Score · Credentials · 🔒 Identity masked</div></div>` +
            `<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="var(--text-3)" viewBox="0 0 24 24" width="16" height="16"><polyline points="9 18 15 12 9 6"/></svg>` +
          `</button>` +
        `</div>` +
        `<div class="intro-model-block queue">` +
          `<div class="imb-label queue">🛍️ Soft Queue · Local Market</div>` +
          `<div class="imb-title">Listing stays live — always available</div>` +
          `<div class="commit-steps">` +
            `<div class="cs"><div class="cs-dot buyer">B</div><div><div class="cs-label">You submit introduction request</div><div class="cs-sub">No Tuppence deducted · listing stays visible</div></div></div>` +
            `<div class="cs"><div class="cs-dot system q">🛍️</div><div><div class="cs-label">Added to seller\'s queue — listing stays live</div><div class="cs-sub">Other buyers can still request simultaneously</div></div></div>` +
            `<div class="cs"><div class="cs-dot seller">S</div><div><div class="cs-label">Seller notified · has 48hrs to respond</div><div class="cs-sub">Seller reviews all queued requests</div></div></div>` +
            `<div class="cs"><div class="cs-dot reveal">✓</div><div><div class="cs-label">Accepted · identities revealed</div><div class="cs-sub">Identities revealed · you connect directly</div></div></div>` +
            `<div class="cs"><div class="cs-dot reveal">✓</div><div><div class="cs-label">Respond within 24hrs → Trust Score +3</div><div class="cs-sub">No response within 48hrs → Trust Score −5</div></div></div>` +
          `</div>` +
        `</div>` +
        `<div class="anon-block"><div class="lock-icon">🔒</div><h4>Identity protected until introduction</h4><p>Seller name and contact details are only revealed after both parties accept.</p></div>` +
      `</div>` +
      `<div class="sticky-cta"><button class="cta-btn queue-cta" onclick="openLMModal()">👥 Request Introduction <span class="cta-cost">· 1T on acceptance</span></button></div>`;
  } catch(e) {
    el.innerHTML = '<div style="padding:40px 16px;color:var(--text-3);font-size:13px;text-align:center;">Could not load this listing.</div>';
  }
}


// Open the standard intro modal for a Local Market listing.
// Uses _lmCurrentListing (set in lmOpenDetail) — no ID argument needed.
function openLMModal() {
  const c = _lmCurrentListing;
  if (!c) return;
  const loc = c.suburb || c.city || '';
  document.getElementById('modal-title').textContent = 'Request Introduction';
  document.getElementById('modal-desc').textContent = (c.title || 'Local Market item') + (loc ? ' · ' + loc : '');
  document.getElementById('modal-notice-commit').style.display = 'none';
  document.getElementById('modal-notice-queue').style.display = 'flex';
  // LM is seller-pays: update the Tuppence deduction notice accordingly
  const tnNotice = document.querySelector('#intro-modal .tn-deduct-notice');
  if (tnNotice) tnNotice.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg> Seller-pays model — no Tuppence deducted from you';
  document.getElementById('modal-cta-btn').className = 'modal-cta queue';
  document.getElementById('modal-cta-btn').textContent = 'Request Introduction · free for buyers';
  pendingIntroId = null;
  pendingLMIntroId = c.id;
  const savedName  = localStorage.getItem('ms_user_name')  || '';
  const savedEmail = localStorage.getItem('ms_user_email') || '';
  if (savedName)  document.getElementById('m-name').value  = savedName;
  if (savedEmail) document.getElementById('m-email').value = savedEmail;
  document.getElementById('intro-modal').classList.add('open');
}

// Open seller profile screen for a Local Market listing.
// Uses _lmCurrentListing — no ID argument needed.
async function openLMSellerProfile() {
  const c = _lmCurrentListing;
  if (!c) return;
  const trust = c.trust_score || 0;
  const t = trustTier(trust);
  const active = document.querySelector('.screen.active');
  prevScreen = active ? active.id.replace('screen-', '') : 'local-market-detail';
  const loc = c.suburb || c.city || '';

  // Render immediately with loading placeholder for docs section
  document.getElementById('screen-seller-cv').innerHTML =
    `<div class="cv-hero" style="background:#1f2937">` +
      `<button class="cv-back" onclick="goTo('${prevScreen}')"><svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg></button>` +
      `<div class="cv-avatar" style="margin-top:8px;"><div style="width:64px;height:64px;border-radius:50%;background:rgba(255,255,255,.15);display:flex;align-items:center;justify-content:center;font-size:30px;">🛍️</div></div>` +
      `<div class="cv-headline">${_lmEsc(c.title || 'Local Market Item')}</div>` +
      `<div class="cv-cat">Local Market · ${_lmEsc(loc)} · 🔒 Anonymous until introduction</div>` +
      `<div class="cv-trust-row">` +
        `<div style="color:${t.c};"><div class="cv-trust-num">${trust}</div><div class="cv-trust-label" style="color:${t.c};">${t.label}</div></div>` +

        `<div class="cv-trust-bar"><div class="cv-trust-fill" style="width:${trust}%;background:${t.c};"></div></div>` +
        `<div style="font-size:11px;color:rgba(255,255,255,.65);text-align:right;font-weight:400;">Trust<br>Score</div>` +
      `</div>` +
    `</div>` +
    `<div class="cv-body">` +
      (c.description ? `<div class="cv-sec"><div class="cv-sec-title">About this listing</div><p class="cv-about">${_lmEsc(c.description)}</p></div>` : '') +
      `<div class="cv-sec" id="lm-cv-docs-section"><div class="cv-sec-title">Seller credentials &amp; documents</div>` +
        `<div style="font-size:12px;color:var(--text-3);">⏳ Loading…</div>` +
      `</div>` +
      `<div class="cv-sec"><div class="cv-identity-block"><div class="cv-identity-icon">🔒</div><div class="cv-identity-text"><h4>Identity protected until introduction</h4><p>Name, contact details and exact location are only revealed after both parties accept a mutual introduction.</p></div></div></div>` +
    `</div>` +
    `<div class="cv-sticky">` +
      `<button class="cv-cta" onclick="openLMModal()">` +
        `<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24" width="18" height="18"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>` +
        ` Request Introduction · 1T on acceptance` +
      `</button>` +
    `</div>`;
  goTo('seller-cv');

  // Async: fetch post-intro documents and render into credentials section
  const docSection = document.getElementById('lm-cv-docs-section');
  if (!docSection) return;
  try {
    const sellerEmail = c.seller_email || '';
    // Use public endpoint — no API key needed, returns only post_intro docs
    const r = await fetch(BEA_URL + '/users/' + encodeURIComponent(sellerEmail) + '/documents/public');
    const docs = r.ok ? await r.json() : [];
    const DOC_ICONS = {
      id_doc:'🪪', certificate:'🎓', training:'📚', membership:'🏛',
      professional_role:'⭐', guide:'📖', recipe:'🍯', presentation:'📊', other:'📎'
    };
    if (!docs.length) {
      docSection.innerHTML =
        `<div class="cv-sec-title">Seller credentials &amp; documents</div>` +
        `<div style="font-size:12px;color:var(--text-3);">Seller credentials and evidence documents will appear here once submitted.</div>`;
      return;
    }
    const docRows = docs.map(d =>
      `<div style="display:flex;align-items:center;gap:10px;padding:9px 0;border-bottom:1px solid var(--border);">` +
        `<div style="font-size:22px;flex-shrink:0;">${DOC_ICONS[d.doc_type] || '📎'}</div>` +
        `<div style="flex:1;min-width:0;">` +
          `<div style="font-size:13px;font-weight:600;color:var(--text);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${_lmEsc(d.label)}</div>` +
          `<div style="font-size:11px;color:var(--text-3);margin-top:1px;">Shared by seller · 👁 Available after introduction</div>` +
        `</div>` +
        `<a href="${_lmEsc(d.url)}" target="_blank" rel="noopener" style="font-size:12px;background:var(--surface-2);border:1.5px solid var(--border);border-radius:20px;padding:5px 10px;color:var(--text);text-decoration:none;flex-shrink:0;">View</a>` +
      `</div>`
    ).join('');
    docSection.innerHTML =
      `<div class="cv-sec-title">Seller credentials &amp; documents</div>` +
      `<div style="font-size:11px;color:var(--text-3);margin-bottom:8px;">These documents have been shared by the seller to help you make an informed introduction decision.</div>` +
      docRows;
  } catch(e) {
    if (docSection) docSection.innerHTML =
      `<div class="cv-sec-title">Seller credentials &amp; documents</div>` +
      `<div style="font-size:12px;color:var(--text-3);">Could not load seller documents.</div>`;
  }
}

// Low-level LM intro API call — called from submitIntro() when pendingLMIntroId is set.
async function lmSubmitIntro(listingId, name, email, message) {
  // Immediate local feedback so buyer knows something happened
  const lmTitle = _lmCurrentListing ? (_lmCurrentListing.title || 'Local Market item') : 'Local Market item';
  addTx('Introduction request sent', lmTitle, 'pending', false);
  showToast('⏳ Sending introduction request…');
  if (!_wlToken) { try { await wlBootToken(); } catch(e){} }
  if (!_wlToken) { showToast('Could not establish your buyer profile. Please reload.'); return; }
  try {
    const resp = await fetch(BEA_URL + '/local-market/intro', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        listing_id: listingId,
        buyer_token: _wlToken,
        buyer_email: email || _wlToken,
        buyer_name: name || null,
        message: message || null,
      })
    });
    if (resp.status === 403) {
      const j = await resp.json().catch(()=>({}));
      showToast('Not allowed: ' + (j.detail || 'unknown'));
      return;
    }
    if (resp.status === 410) { showToast('This listing has been suspended and is no longer accepting introductions.'); return; }
    if (resp.status === 402) { showToast('The seller does not have enough Tuppence right now. Please try again later.'); return; }
    if (resp.status === 429) { showToast('You already requested an introduction on this listing recently. Please wait 7 days.'); return; }
    showToast('✓ Introduction requested · seller has 48hrs to respond');
  } catch(e) {
    showToast('Could not submit introduction: ' + e.message);
  }
}


/* ══════════════════════════════════════════════════════════
   MY SPACE — Session 50
   msInit() called by goTo('myspace')
   browse history tracked via msTrackView(listing)
══════════════════════════════════════════════════════════ */
const MS_HISTORY_KEY = 'ms_browse_history';
const MS_HISTORY_MAX = 30;

async function msSellerSignIn() {
  const inp = document.getElementById('ms-seller-email-inp');
  const msg = document.getElementById('ms-seller-signin-msg');
  if (!inp || !msg) return;
  const email = (inp.value || '').trim().toLowerCase();
  if (!email) { msg.style.display='block'; msg.style.color='#dc2626'; msg.textContent='Please enter your email.'; return; }
  msg.style.display='block'; msg.style.color='var(--text-3)'; msg.textContent='Checking…';
  try {
    const user = await apiGet('/users/' + encodeURIComponent(email));
    if (user && user.email) {
      const name = user.name || email;
      localStorage.setItem('ms_aa_email', email);
      localStorage.setItem('ms_aa_name',  name);
      if(!localStorage.getItem('ms_joined_date')) localStorage.setItem('ms_joined_date', new Date().toISOString());
      localStorage.setItem('ms_superuser', user.is_superuser ? '1' : '0');
      msg.style.color='var(--green)'; msg.textContent='✓ Signed in as ' + name;
      // Show hub, hide sign-in form
      const hubCard = document.getElementById('ms-seller-hub-card');
      const signinCard = document.getElementById('ms-seller-signin-card');
      if(hubCard) hubCard.style.display='';
      if(signinCard) signinCard.style.display='none';
      // Load dashboard data in background
      setTimeout(async () => { await loadLiveDash(); renderDash(); }, 400);
    } else {
      msg.style.color='#dc2626'; msg.textContent='No seller account found for that email.';
    }
  } catch(e) {
    msg.style.color='#dc2626'; msg.textContent='Could not connect — please try again.';
  }
}

function msInit(){
  const email = localStorage.getItem('ms_user_email') || localStorage.getItem('ms_aa_email') || '';
  const name  = localStorage.getItem('ms_user_name') || '';
  const city  = (typeof activeCity !== 'undefined' && activeCity.name) ? activeCity.name
               : localStorage.getItem('ms_user_city') || '–';

  // Avatar / header
  const initials = name ? name.split(' ').filter(Boolean).slice(0,2).map(w=>w[0].toUpperCase()).join('') : (email ? email[0].toUpperCase() : '?');
  const av = document.getElementById('ms-avatar-initials');
  if(av) av.textContent = initials;

  // Profile photo — check all three keys in priority order
  const photoUrl = localStorage.getItem('ms_user_photo')
    || localStorage.getItem('ms_seller_photo_url')
    || localStorage.getItem('ms_seller_photo');
  if(photoUrl){
    const avEl = document.getElementById('ms-avatar-el');
    if(avEl) avEl.innerHTML = '<img src="'+photoUrl+'" alt="avatar">';
    // Normalise — ensure ms_user_photo is always the canonical key
    if (!localStorage.getItem('ms_user_photo')) {
      try { localStorage.setItem('ms_user_photo', photoUrl); } catch(_){}
    }
  }

  const dispName = document.getElementById('ms-display-name');
  if(dispName) dispName.textContent = name || (email ? email.split('@')[0] : 'My Space');

  const dispSub = document.getElementById('ms-display-sub');
  if(dispSub) dispSub.textContent = email || 'TrustSquare member';

  // Wallet badge
  const tnBadge = document.getElementById('nav-tn-badge');
  const walBal  = tnBadge ? (parseInt(tnBadge.textContent)||5) : 5;
  const msPill  = document.getElementById('ms-tn-pill');
  if(msPill) msPill.textContent = walBal + ' T';
  const msWalBal = document.getElementById('ms-wallet-balance');
  if(msWalBal) msWalBal.textContent = walBal;

  // Personal details tab
  const pdName = document.getElementById('ms-pd-name');
  if(pdName) pdName.textContent = name || '–';
  const pdEmail = document.getElementById('ms-pd-email');
  if(pdEmail) pdEmail.textContent = email || '–';
  const pdCity = document.getElementById('ms-pd-city');
  if(pdCity) pdCity.textContent = city;

  // Member since
  const joinedRaw = localStorage.getItem('ms_joined_date');
  const joined = joinedRaw ? new Date(joinedRaw).toLocaleDateString('en-ZA',{month:'long',year:'numeric'})
                           : new Date().toLocaleDateString('en-ZA',{month:'long',year:'numeric'});
  const pdSince = document.getElementById('ms-pd-since');
  if(pdSince) pdSince.textContent = joined;

  // Roles
  const pdRoles = document.getElementById('ms-pd-roles');
  if(pdRoles){
    const hasSeller = localStorage.getItem('ms_aa_email') || localStorage.getItem('ms_user_email');
    pdRoles.innerHTML = '<span class="ms-chip ms-chip-done">Buyer</span>'
      + (hasSeller ? ' <span class="ms-chip ms-chip-new">Seller</span>' : '');
  }

  // Seller hub card — visible to sellers; sign-in form shown to non-sellers
  const isSeller = !!(localStorage.getItem('ms_aa_email') || (SELLERS && SELLERS[0] && SELLERS[0]._email));
  const sellerHubCard   = document.getElementById('ms-seller-hub-card');
  const sellerSigninCard = document.getElementById('ms-seller-signin-card');
  if(sellerHubCard)    sellerHubCard.style.display    = isSeller ? '' : 'none';
  if(sellerSigninCard) sellerSigninCard.style.display = isSeller ? 'none' : '';
  // Remove the old label element ref (now always visible via static HTML)
  const sellerHubLbl = document.getElementById('ms-seller-hub-lbl');
  if(sellerHubLbl) sellerHubLbl.style.display = '';

  // Trust score (use cached, then fetch live from BEA)
  const storedTrust = parseInt(localStorage.getItem('ms_trust_score')) || 15;
  msRenderTrust(storedTrust);
  if(email && BEA_ENABLED){
    // Fetch trust breakdown from dedicated endpoint
    fetch(BEA_URL+'/users/'+encodeURIComponent(email)+'/trust')
      .then(r=>r.ok?r.json():null)
      .then(td=>{
        if(!td) return;
        const live = parseInt(td.score)||storedTrust;
        localStorage.setItem('ms_trust_score', live);
        msRenderTrust(live);
        msUpdateStats(walBal, live);
        // Render live signals
        if(td.signals && td.signals.length) msRenderLiveSignals(td.signals);
      }).catch(()=>{});
    // Also fetch full user for photo
    fetch(BEA_URL+'/users/'+encodeURIComponent(email))
      .then(r=>r.ok?r.json():null)
      .then(ud=>{
        if(!ud) return;
        if(ud.photo_url){
          localStorage.setItem('ms_user_photo', ud.photo_url);
          const avEl = document.getElementById('ms-avatar-el');
          if(avEl) avEl.innerHTML = '<img src="'+ud.photo_url+'" alt="avatar">';
          // Also update Me tab photo thumbnail
          msMeUpdatePhotoThumb(ud.photo_url);
        }
      }).catch(()=>{});
  }
  // Show cached photo in Me tab thumbnail immediately (before BEA fetch completes)
  const cachedPhoto = localStorage.getItem('ms_user_photo') || localStorage.getItem('ms_seller_photo_url');
  if (cachedPhoto) msMeUpdatePhotoThumb(cachedPhoto);

  // Intros
  msLoadIntros(email);

  // Wishlist
  msRenderWishlist();

  // Browse history
  msRenderHistory();

  // Stats
  msUpdateStats(walBal, storedTrust);

  // Ensure first tab shown
  msTab('overview', document.querySelector('.ms-tab'));
}

function msMeUpdatePhotoThumb(url) {
  const thumb = document.getElementById('ms-me-photo-thumb');
  if (!thumb) return;
  thumb.innerHTML = '<img src="' + url + '" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">';
}

async function msMeUploadPhoto(e) {
  const file = e.target.files && e.target.files[0];
  if (!file) return;
  const email = localStorage.getItem('ms_user_email') || localStorage.getItem('ms_aa_email') || '';
  if (!email) { showToast('Sign in first to change your photo'); return; }
  const thumb = document.getElementById('ms-me-photo-thumb');
  if (thumb) thumb.innerHTML = '<span style="font-size:12px;color:#6b7280;">⏳</span>';
  try {
    const fd = new FormData();
    fd.append('file', file);
    const r = await fetch(BEA_URL + '/users/' + encodeURIComponent(email) + '/photo', { method: 'POST', body: fd });
    if (!r.ok) throw new Error('Upload failed');
    const data = await r.json();
    const url = data.photo_url;
    localStorage.setItem('ms_user_photo', url);
    localStorage.setItem('ms_seller_photo_url', url);
    localStorage.setItem('ms_seller_photo', url);  // keeps SELLER_PHOTOS[0] in sync on next load
    // Update avatar header and Me tab thumb
    const avEl = document.getElementById('ms-avatar-el');
    if (avEl) avEl.innerHTML = '<img src="' + url + '" alt="avatar">';
    msMeUpdatePhotoThumb(url);
    // Also update SELLER_PHOTOS live so seller CV reflects the new photo immediately
    if (typeof SELLER_PHOTOS !== 'undefined') SELLER_PHOTOS[0] = url;
    showToast('Profile photo updated');
  } catch(err) {
    showToast('Photo upload failed');
    const cachedPhoto = localStorage.getItem('ms_user_photo');
    if (thumb) thumb.innerHTML = cachedPhoto
      ? '<img src="' + cachedPhoto + '" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">'
      : '<span id="ms-me-photo-placeholder">📷</span>';
  }
}

function msTab(name, el){
  document.querySelectorAll('.ms-tab').forEach(t=>t.classList.remove('active'));
  if(el) el.classList.add('active');
  document.querySelectorAll('.ms-tab-content').forEach(t=>t.classList.remove('active'));
  const tc = document.getElementById('ms-tab-'+name);
  if(tc) tc.classList.add('active');
  if(name === 'billing') loadBillingTab();
}

async function loadBillingTab() {
  const email = localStorage.getItem('ms_aa_email') || '';
  let d = null;
  if (email && BEA_ENABLED) {
    try {
      const r = await fetch(BEA_URL + '/users/' + encodeURIComponent(email) + '/subscription');
      if (r.ok) d = await r.json();
    } catch(e) { console.error('loadBillingTab fetch error:', e); }
  }
  try {
    _renderBillingTab(d, email);
  } catch(e) {
    console.error('_renderBillingTab error:', e);
    document.getElementById('billing-plans-list').innerHTML = '<div style="color:#ef4444;padding:8px;">Error loading plans. Please try again.</div>';
  }
  loadTransactionHistory('billing-tx-list', 'billing-tx-more', true);
}


// ── TRANSACTION HISTORY ──────────────────────────────────────
// Shared by Billing tab + Tuppence screen.
// _txState tracks pagination per container id.
const _txState = {};

const _TX_ICON = {
  topup:        { icon: '💰', label: 'Top-up',          color: '#16a34a' },
  ai_service:   { icon: '🤖', label: 'AI service',      color: '#7c3aed' },
  intro:        { icon: '🤝', label: 'Introduction',    color: '#2563eb' },
  subscription: { icon: '📋', label: 'Subscription',    color: '#d97706' },
};

/* How Introductions Work — compact category/feature explainer (Session) */
const HIW_CATS = [
  { label: '🏡 Property',      group: 0 },
  { label: '🚗 Cars',          group: 0 },
  { label: '🏕 Accommodation', group: 1 },
  { label: '🌿 Experiences',   group: 1 },
  { label: '🎓 Tutors',        group: 2 },
  { label: '⚙️ Services',    group: 2 },
  { label: '🏺 Collectors',    group: 2 },
];
// group 0 = Property & Cars · 1 = Accommodation & Experiences · 2 = Tutors/Services/Collectors
const HIW_FEATURES = [
  { label: 'Listing paused on intro', ans: ['Yes — holds slot','No','No'], tone: ['yes','no','no'],
    desc: ['When a buyer requests an intro your listing pauses, so the item is held just for them while you reply.',
           'Your listing stays live — several guests can request the same dates at the same time.',
           'Your listing stays live — several buyers can reach you at the same time.'] },
  { label: 'Multiple buyers at once', ans: ['Up to 3','Unlimited','Unlimited'], tone: ['partial','yes','yes'],
    desc: ['Up to 3 buyers can hold an intro at once, so a serious buyer always has a slot.',
           'Any number of guests can enquire together — you choose who to confirm.',
           'Any number of buyers can reach you together — there is no cap.'] },
  { label: 'Booking / scheduling', ans: ['No','Date-based slot','Availability match'], tone: ['no','yes','partial'],
    desc: ['No calendar — it is a direct introduction to discuss the sale.',
           'Buyers choose a date when they request the introduction.',
           'Buyers request a time that fits the availability you have set.'] },
  { label: 'Buyer pays on acceptance', ans: ['1T = $2','1T = $2','1T = $2'], tone: ['yes','yes','yes'],
    desc: ['The buyer spends 1 Tuppence (about $2) only when you accept the intro — never before.',
           'The buyer spends 1 Tuppence (about $2) only when you accept the intro — never before.',
           'The buyer spends 1 Tuppence (about $2) only when you accept the intro — never before.'] },
  { label: 'No response within 48 hrs', ans: ['Trust −5','Trust −5','Trust −5'], tone: ['no','no','no'],
    desc: ['If you do not reply within 48 hours your trust score drops by 5. No money is lost by anyone.',
           'If you do not reply within 48 hours your trust score drops by 5. No money is lost by anyone.',
           'If you do not reply within 48 hours your trust score drops by 5. No money is lost by anyone.'] },
  { label: 'Respond within 24 hrs', ans: ['Trust +3','Trust +3','Trust +3'], tone: ['yes','yes','yes'],
    desc: ['Reply within 24 hours and your trust score rises by 3 — fast replies build a stronger profile.',
           'Reply within 24 hours and your trust score rises by 3 — fast replies build a stronger profile.',
           'Reply within 24 hours and your trust score rises by 3 — fast replies build a stronger profile.'] },
  { label: 'Response window', ans: ['48 hrs','48 hrs','48 hrs'], tone: ['yes','yes','yes'],
    desc: ['You have 48 hours to respond to every introduction request.',
           'You have 48 hours to respond to every introduction request.',
           'You have 48 hours to respond to every introduction request.'] },
];
let _hiwFeat = 0;
function hiwInit(){
  const sel = document.getElementById('hiw-cat');
  if (!sel) return;
  if (!sel.options.length) sel.innerHTML = HIW_CATS.map(function(cat,i){ return '<option value="'+i+'">'+cat.label+'</option>'; }).join('');
  const dots = document.getElementById('hiw-dots');
  if (dots) dots.innerHTML = HIW_FEATURES.map(function(_f,i){ return '<span class="hiw-dot'+(i===_hiwFeat?' on':'')+'" onclick="hiwGo('+i+')"></span>'; }).join('');
  hiwRender();
}
function hiwStep(d){ _hiwFeat = (_hiwFeat + d + HIW_FEATURES.length) % HIW_FEATURES.length; hiwRender(); }
function hiwGo(i){ _hiwFeat = i; hiwRender(); }
function hiwRender(){
  const sel = document.getElementById('hiw-cat'); if (!sel) return;
  const g = (HIW_CATS[+sel.value] || HIW_CATS[0]).group;
  const f = HIW_FEATURES[_hiwFeat] || HIW_FEATURES[0];
  const lbl = document.getElementById('hiw-feat-label'); if (lbl) lbl.textContent = f.label;
  const ans = document.getElementById('hiw-answer'); if (ans){ ans.textContent = f.ans[g]; ans.className = 'hiw-answer ' + f.tone[g]; }
  const desc = document.getElementById('hiw-desc'); if (desc) desc.textContent = f.desc[g];
  const dots = document.querySelectorAll('#hiw-dots .hiw-dot');
  dots.forEach(function(dd,i){ dd.classList.toggle('on', i === _hiwFeat); });
}

/* Transaction history filters (type + date range), applied client-side over loaded items */
const _txFilters = {};
function txSyncFilterUI(){
  const f = _txFilters['tn-history']; if (!f) return;
  const t = document.getElementById('tx-filter-type'); if (t) t.value = f.type || 'all';
  const r = document.getElementById('tx-filter-range'); if (r) r.value = f.range || 'all';
}
function txApplyFilter(){
  const t = document.getElementById('tx-filter-type');
  const r = document.getElementById('tx-filter-range');
  _txFilters['tn-history'] = { type: t ? t.value : 'all', range: r ? r.value : 'all' };
  const st = _txState['tn-history'];
  _renderTxList('tn-history', st ? st.items : []);
}
function _txPassesFilter(tx, f){
  if (!f) return true;
  if (f.type && f.type !== 'all' && tx.type !== f.type) return false;
  if (f.range && f.range !== 'all'){
    const days = parseInt(f.range, 10);
    const t = new Date((tx.created_at || '').replace(' ', 'T') + 'Z').getTime();
    if (isNaN(t)) return false;
    if (t < Date.now() - days * 86400000) return false;
  }
  return true;
}

function _txMeta(type) {
  return _TX_ICON[type] || { icon: '•', label: type, color: '#64748b' };
}

function _fmtDate(iso) {
  if (!iso) return '';
  const d = new Date(iso.replace(' ','T')+'Z');
  return d.toLocaleDateString('en-ZA', { day:'numeric', month:'short', year:'numeric' });
}

function _fmtAmount(amount) {
  if (amount > 0) return '+' + amount + ' T';
  if (amount < 0) return amount + ' T';
  return '0 T';
}

async function loadTransactionHistory(listId, moreId, reset) {
  const email = localStorage.getItem('ms_aa_email') || '';
  if (!email || !BEA_ENABLED) {
    const el = document.getElementById(listId);
    if (el) el.innerHTML = _txEmptyState('Sign in to view your transaction history');
    return;
  }
  if (!_txState[listId] || reset) _txState[listId] = { offset: 0, total: 0, items: [] };
  const st = _txState[listId];
  const PAGE = 20;

  const el = document.getElementById(listId);
  if (el && st.offset === 0) el.innerHTML = '<div style="text-align:center;padding:20px 0;color:var(--text-3);font-size:13px;">Loading…</div>';

  try {
    const r = await fetch(BEA_URL + '/tuppence/history?email=' + encodeURIComponent(email) +
      '&limit=' + PAGE + '&offset=' + st.offset);
    if (!r.ok) throw new Error(r.status);
    const d = await r.json();
    st.total = d.total;
    st.items = st.items.concat(d.transactions);
    st.offset += d.transactions.length;

    _renderTxList(listId, st.items, d.balance);

    const moreEl = document.getElementById(moreId);
    if (moreEl) {
      moreEl.style.display = st.offset < st.total ? 'block' : 'none';
      moreEl._listId = listId;
      moreEl._moreId = moreId;
    }
  } catch(e) {
    const el2 = document.getElementById(listId);
    if (el2) el2.innerHTML = _txEmptyState('Could not load transactions — check your connection');
  }
}

function _renderTxList(listId, items, balance) {
  const el = document.getElementById(listId);
  if (!el) return;
  const all = items || [];
  const _f = _txFilters[listId];
  const shown = _f ? all.filter(function(tx){ return _txPassesFilter(tx, _f); }) : all;
  if (!all.length) { el.innerHTML = _txEmptyState('No transactions yet'); return; }
  if (!shown.length) { el.innerHTML = _txEmptyState('No transactions match this filter'); return; }

  // Group by calendar month
  const groups = {};
  const groupOrder = [];
  shown.forEach(tx => {
    const d = new Date((tx.created_at||'').replace(' ','T')+'Z');
    const key = d.toLocaleDateString('en-ZA',{month:'long',year:'numeric'});
    if (!groups[key]) { groups[key] = []; groupOrder.push(key); }
    groups[key].push(tx);
  });

  let html = '';
  groupOrder.forEach(month => {
    html += `<div style="font-size:11px;font-weight:700;letter-spacing:.5px;text-transform:uppercase;color:var(--text-3);padding:12px 0 6px;">${month}</div>`;
    groups[month].forEach(tx => {
      const m = _txMeta(tx.type);
      const amt = tx.amount;
      const amtStr = _fmtAmount(amt);
      const amtColor = amt > 0 ? '#16a34a' : amt < 0 ? '#dc2626' : '#64748b';
      const desc = tx.description || m.label;
      // Truncate long descriptions
      const shortDesc = desc.length > 52 ? desc.substring(0,52)+'…' : desc;
      html += `
        <div style="display:flex;align-items:center;gap:12px;padding:11px 0;border-bottom:1px solid var(--border);">
          <div style="width:36px;height:36px;border-radius:50%;background:${m.color}18;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;">${m.icon}</div>
          <div style="flex:1;min-width:0;">
            <div style="font-size:13px;font-weight:600;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${shortDesc}</div>
            <div style="font-size:11px;color:var(--text-3);margin-top:2px;">${m.label} · ${_fmtDate(tx.created_at)}</div>
          </div>
          <div style="text-align:right;flex-shrink:0;">
            <div style="font-size:14px;font-weight:700;color:${amtColor};">${amtStr}</div>
            <div style="font-size:11px;color:var(--text-3);">${tx.balance_after} T bal</div>
          </div>
        </div>`;
    });
  });
  el.innerHTML = html;
}

function _txEmptyState(msg) {
  return `<div style="text-align:center;padding:24px 0;color:var(--text-3);">
    <div style="font-size:28px;margin-bottom:8px;">📭</div>
    <div style="font-size:13px;">${msg}</div>
  </div>`;
}

function loadMoreTransactions() {
  loadTransactionHistory('tn-history', 'tn-load-more');
}

function loadBillingTxMore() {
  loadTransactionHistory('billing-tx-list', 'billing-tx-more');
}

function _renderBillingTab(d, email) {
  const tier  = d?.seller_tier || 'free';
  const limit = d?.slot_limit ?? 2;
  const used  = d?.slots_used ?? 0;
  const avail = d?.slots_available ?? (limit - used);
  const meta  = _SUB_TIERS.find(t => t.id === tier) || _SUB_TIERS[0];

  document.getElementById('billing-tier-label').textContent = meta.label;
  document.getElementById('billing-tier-price').textContent = meta.usd === 0 ? 'Free forever · no credit card required' : '$' + meta.usd + '/month · ≈ R' + meta.zar;
  document.getElementById('billing-slots-used').textContent = used;
  document.getElementById('billing-slots-limit').textContent = limit;
  document.getElementById('billing-slots-avail').textContent = avail;
  document.getElementById('billing-slot-text').textContent = used + ' / ' + limit;
  const pct = limit > 0 ? Math.min(100, Math.round((used/limit)*100)) : 0;
  const bar = document.getElementById('billing-slot-bar');
  bar.style.width = pct + '%';
  bar.style.background = pct >= 90 ? '#ef4444' : pct >= 70 ? '#f59e0b' : 'linear-gradient(90deg,#6366f1,#8b5cf6)';

  const nd = document.getElementById('billing-downgrade-notice');
  if (d?.pending_downgrade_tier) {
    nd.style.display = 'block';
    document.getElementById('billing-downgrade-to').textContent =
      d.pending_downgrade_tier.charAt(0).toUpperCase() + d.pending_downgrade_tier.slice(1);
    document.getElementById('billing-downgrade-date').textContent =
      d.billing_period_end ? d.billing_period_end.substring(0,10) : 'end of period';
  } else {
    nd.style.display = 'none';
  }

  // Plan cards
  const container = document.getElementById('billing-plans-list');
  container.innerHTML = '';
  const curRank = _TIER_ORDER.indexOf(tier);

  _SUB_TIERS.forEach(t => {
    const tRank  = _TIER_ORDER.indexOf(t.id);
    const isCur  = t.id === tier;
    const isUp   = tRank > curRank;
    const isDown = tRank < curRank;
    const btnLabel = isCur ? '✓ Current' : isUp ? 'Upgrade →' : 'Downgrade';
    const btnBg    = isCur ? 'var(--surface-2)' : isUp ? t.color : '#e2e8f0';
    const btnTxt   = isCur ? 'var(--text-3)' : isUp ? '#fff' : '#64748b';

    const card = document.createElement('div');
    card.style.cssText = `background:var(--surface);border:1.5px solid ${isCur ? t.color : 'var(--border)'};border-radius:14px;padding:14px 16px;`;
    card.innerHTML = `
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">
        <div>
          <span style="font-size:15px;font-weight:800;color:${t.color};">${t.label}</span>
          <span style="font-size:12px;color:var(--text-3);margin-left:8px;">${t.slots} slots</span>
        </div>
        <button onclick="_subSelectTier('${t.id}','${t.label}',${t.usd},${isDown})" ${isCur?'disabled':''} style="background:${btnBg};color:${btnTxt};border:none;border-radius:50px;padding:6px 14px;font-family:'Syne',sans-serif;font-size:12px;font-weight:700;cursor:${isCur?'default':'pointer'};opacity:${isCur?'.5':'1'};">${btnLabel}</button>
      </div>
      <div style="font-size:13px;color:var(--text-2);">${t.usd === 0 ? 'Free forever' : '$'+t.usd+'/mo · ≈ R'+t.zar} · ${t.desc}</div>
      ${isDown && !isCur ? '<div style="font-size:11px;color:#f59e0b;margin-top:4px;">⏳ Takes effect at end of billing period</div>' : ''}
    `;
    container.appendChild(card);
  });
}


const _EULA_HTML = "<p><strong>MarketSquare</strong></p>\n<p>trustsquare.co</p>\n<p><strong>Terms of Use /</strong></p>\n<p><strong>End User License Agreement (EULA)</strong></p>\n<table>\n<tbody>\n<tr>\n<td><p><strong>Version</strong></p>\n<p>1.3 \u2014 Draft</p></td>\n<td><p><strong>Status</strong></p>\n<p>For legal review \u2014 not yet published (v1.3: charge-timing + Banks Act corrections)</p></td>\n</tr>\n<tr>\n<td><p><strong>Prepared</strong></p>\n<p>17 May 2026</p></td>\n<td><p><strong>Governing Law</strong></p>\n<p>Republic of South Africa</p></td>\n</tr>\n</tbody>\n</table>\n<table>\n<tbody>\n<tr>\n<td><p><strong>\u26a0 Legal Review Required Before Publication</strong></p>\n<p>This draft has been prepared using comparative analysis of Airbnb, Booking.com, Viator, GetYourGuide, Gumtree SA, and Property24 terms, combined with South African statutory requirements (POPIA, ECT Act, CPA, NCA, FICA, FSCA). It must be reviewed by a South African admitted attorney before deployment. Sections marked [COUNSEL REQUIRED] need jurisdiction-specific legal input. Recommended firms: Michalsons (legal tech), Werksmans (commercial law), Hogan Lovells (technology law).</p></td>\n</tr>\n</tbody>\n</table>\n<blockquote>\n<p><strong>Reviewer Notes &amp; Gap Summary</strong></p>\n</blockquote>\n<p>This document incorporates MarketSquare's original draft EULA and closes 18 critical gaps identified through comparative analysis of comparable platforms and South African statutory requirements. The following table summarises all gaps and their treatment in this draft.</p>\n<table>\n<tbody>\n<tr>\n<td><strong>Gap</strong></td>\n<td><strong>Severity</strong></td>\n<td><strong>Status in this Draft</strong></td>\n</tr>\n<tr>\n<td>No Privacy Policy referenced or linked</td>\n<td>CRITICAL</td>\n<td>Section 8 \u2014 POPIA clause added; Privacy Policy page must be published at trustsquare.co/privacy before launch</td>\n</tr>\n<tr>\n<td>Anonymity vs. FICA KYC conflict</td>\n<td>CRITICAL</td>\n<td>Section 3 \u2014 Deferred KYC model documented; FICA justification included</td>\n</tr>\n<tr>\n<td>No POPIA consent mechanism at account creation</td>\n<td>CRITICAL</td>\n<td>Section 3.10 &amp; 8.3 \u2014 Explicit consent clause added with legal basis</td>\n</tr>\n<tr>\n<td>Tuppence regulatory status (FSCA virtual asset risk)</td>\n<td>CRITICAL</td>\n<td>Section 11 \u2014 Virtual asset classification clause; non-transferability as key defence</td>\n</tr>\n<tr>\n<td>No media/photo upload rights licence</td>\n<td>HIGH</td>\n<td>Section 8 \u2014 Full in-platform use licence (all current and future MarketSquare apps); explicit no-sale-to-third-parties commitment; IP indemnity placing full liability on uploading User; Adventures-specific photo standards; notice-and-takedown process</td>\n</tr>\n<tr>\n<td>No limitation of liability cap</td>\n<td>HIGH</td>\n<td>Section 10 \u2014 Cap at earned Tuppence (seller) / ZAR 500 (buyer); ECT Act safe harbour</td>\n</tr>\n<tr>\n<td>No dispute resolution clause</td>\n<td>HIGH</td>\n<td>Section 4 \u2014 South African Arbitration Foundation, Cape Town, 60-day pre-negotiation</td>\n</tr>\n<tr>\n<td>No ECT Act \u00a744 cooling-off right</td>\n<td>HIGH</td>\n<td>Section 5.4 \u2014 ECT Act \u00a744 scope: TrustSquare's service is complete on acceptance; post-acceptance disputes are buyer/seller matters</td>\n</tr>\n<tr>\n<td>No professional licensing / credential clause</td>\n<td>MEDIUM</td>\n<td>Section 7 \u2014 EAAB, certification uplift for Adventures, verification process</td>\n</tr>\n<tr>\n<td>No Trust Score explanation (algorithm black box)</td>\n<td>MEDIUM</td>\n<td>Section 12 \u2014 Algorithmic factors, penalty schedule, decay rules</td>\n</tr>\n<tr>\n<td>CPA 2026 direct marketing opt-out registry</td>\n<td>HIGH</td>\n<td>Section 6.6 \u2014 NCC registration, opt-out registry pre-check, unsubscribe mechanism</td>\n</tr>\n<tr>\n<td>No EULA gate at onboarding (photo rights exposure)</td>\n<td>HIGH</td>\n<td>Section 1.4 \u2014 EULA acceptance gate before registration; Adventures photo rights explicitly included</td>\n</tr>\n<tr>\n<td>No governing law clause</td>\n<td>HIGH</td>\n<td>Section 13 \u2014 Republic of South Africa; mandatory SA law supremacy list</td>\n</tr>\n<tr>\n<td>No termination rights clause</td>\n<td>MEDIUM</td>\n<td>Section 14 \u2014 User + platform termination; Tuppence forfeiture; survival clause</td>\n</tr>\n<tr>\n<td>Adventures: no certification / Trust uplift clause</td>\n<td>MEDIUM</td>\n<td>Section 7.3\u20137.5 \u2014 Certification upload, pending review, bonus points on approval</td>\n</tr>\n<tr>\n<td>No data breach notification procedure</td>\n<td>MEDIUM</td>\n<td>Section 8.9 \u2014 30-day notification; Information Regulator reporting</td>\n</tr>\n<tr>\n<td>International data transfer (Hetzner/Cloudflare EU hosting)</td>\n<td>MEDIUM</td>\n<td>Section 8.7 \u2014 GDPR adequacy; Data Processing Agreement reference</td>\n</tr>\n</tbody>\n</table>\n<table>\n<tbody>\n<tr>\n<td><p><strong>Sections Requiring Counsel Input</strong></p>\n<p>The following sections are marked [COUNSEL REQUIRED] throughout the document and must be completed by a South African admitted attorney before publication: jurisdiction choice confirmation; FICA/KYC deferred verification legal justification; NCA applicability if Tuppence purchase is enabled; FSCA virtual asset classification letter; NCC direct marketer registration number; arbitration clause enforceability review; privacy policy drafting; company/operator legal name and registration number insertion.</p></td>\n</tr>\n</tbody>\n</table>\n<blockquote>\n<p><strong>1. Definitions &amp; Interpretation</strong></p>\n</blockquote>\n<p><strong>1.1 Definitions</strong></p>\n<p>In this Agreement, the following terms have the meanings assigned to them below:</p>\n<table>\n<tbody>\n<tr>\n<td><strong>Term</strong></td>\n<td><strong>Meaning</strong></td>\n</tr>\n<tr>\n<td>Platform / MarketSquare</td>\n<td>The online marketplace operated by [Company Name] (registration number [REG NO]) at trustsquare.co, including all mobile applications, web services, APIs, and related features.</td>\n</tr>\n<tr>\n<td>Operator / We / Us / Our</td>\n<td>[Company Name], the registered operator of the Platform. [COUNSEL REQUIRED: insert full legal entity name, registration number, and registered address]</td>\n</tr>\n<tr>\n<td>User / You / Your</td>\n<td>Any person or entity who accesses, registers on, or uses the Platform in any capacity.</td>\n</tr>\n<tr>\n<td>Seller</td>\n<td>A User who creates a listing to offer goods, services, accommodation, experiences, or other categories on the Platform.</td>\n</tr>\n<tr>\n<td>Buyer</td>\n<td>A User who browses listings and initiates introductions with Sellers.</td>\n</tr>\n<tr>\n<td>Listing</td>\n<td>A Seller's profile-linked offering displayed on the Platform, described by category, title, price, suburb, and optional photos.</td>\n</tr>\n<tr>\n<td>Introduction</td>\n<td>A buyer-initiated connection request to a Seller, charged at 1 Tuppence, which \u2014 if accepted \u2014 reveals both parties' contact details to each other.</td>\n</tr>\n<tr>\n<td>Tuppence / T</td>\n<td>The Platform's internal transaction unit. 1 Tuppence (1T) = USD $2.00 fixed. Used within the Platform for two purposes: (i) Introduction Tuppence \u2014 the mandatory fee paid by Buyers per Introduction; (ii) AI Feature Tuppence \u2014 an optional, subscription-gated fee paid by Sellers for AI-assisted features, representing cost-recovery for an external AI API. See Section 5.</td>\n</tr>\n<tr>\n<td>AdvertAgent / AI Feature</td>\n<td>The Platform's optional AI-assisted Seller support feature, powered by an external AI API. Seller-facing only. Accessed via paid subscription. Charged in AI Feature Tuppence. Not part of the core marketplace flow. Pricing TBD.</td>\n</tr>\n<tr>\n<td>Trust Score</td>\n<td>A numeric score (0\u2013100) assigned to each Seller that reflects reliability, response rate, and compliance history. Governs listing visibility and priority.</td>\n</tr>\n<tr>\n<td>Anonymity Gate / Mode B</td>\n<td>The Platform's default state in which a Seller's identity is hidden from Buyers until both parties accept an Introduction.</td>\n</tr>\n<tr>\n<td>Magic Link</td>\n<td>A personalised, single-use onboarding URL sent to prospective Sellers that pre-populates the onboarding wizard with the Seller's details.</td>\n</tr>\n<tr>\n<td>Certification / Credential</td>\n<td>A verifiable professional qualification, licence, or registration uploaded by a Seller to the Platform for Trust Score bonus consideration.</td>\n</tr>\n<tr>\n<td>Adventures</td>\n<td>A Platform category comprising two subcategories: Adventures Accommodation (accommodation listings) and Adventures Experiences (activity and experience listings).</td>\n</tr>\n<tr>\n<td>Collectors</td>\n<td>A planned Platform category for physical and digital collectibles, including trading cards, memorabilia, art, and similar items. Launch subject to Solar Council confirmation of introduction model and category rules.</td>\n</tr>\n<tr>\n<td>EULA / Agreement</td>\n<td>This End User License Agreement, including all schedules, annexures, and documents incorporated by reference.</td>\n</tr>\n<tr>\n<td>POPIA</td>\n<td>The Protection of Personal Information Act No. 4 of 2013 (South Africa) and its regulations, as amended.</td>\n</tr>\n<tr>\n<td>ECT Act</td>\n<td>The Electronic Communications and Transactions Act No. 25 of 2002 (South Africa).</td>\n</tr>\n<tr>\n<td>CPA</td>\n<td>The Consumer Protection Act No. 68 of 2008 (South Africa).</td>\n</tr>\n<tr>\n<td>FICA</td>\n<td>The Financial Intelligence Centre Act No. 38 of 1998 (South Africa), as amended.</td>\n</tr>\n<tr>\n<td>NCA</td>\n<td>The National Credit Act No. 34 of 2005 (South Africa).</td>\n</tr>\n<tr>\n<td>FSCA</td>\n<td>The Financial Sector Conduct Authority of South Africa.</td>\n</tr>\n</tbody>\n</table>\n<p><strong>1.2 Interpretation</strong></p>\n<ul>\n<li><p>References to statutes include amendments and subordinate legislation made under them.</p></li>\n<li><p>The singular includes the plural and vice versa.</p></li>\n<li><p>Headings are for convenience only and do not affect interpretation.</p></li>\n<li><p>\"Including\" and similar expressions are not words of limitation.</p></li>\n<li><p>References to days mean calendar days unless stated as \"business days\" (Monday to Friday, excluding South African public holidays).</p></li>\n<li><p>References to USD are to United States Dollars; references to ZAR or Rand are to South African Rand.</p></li>\n</ul>\n<blockquote>\n<p><strong>2. Platform Identity, Scope &amp; Acceptance</strong></p>\n</blockquote>\n<p><strong>2.1 Platform Identity</strong></p>\n<p>The Platform is operated by [Company Name / Operator] (registration number [REG NO], [COUNSEL REQUIRED: insert registered address]) and provides an anonymity-first marketplace connecting Buyers and Sellers across multiple categories including real estate, tutoring, services, casual work, Adventures (accommodation and experiences), and Collectors (physical and digital collectibles).</p>\n<p><strong>2.2 Scope of These Terms</strong></p>\n<p>This EULA governs your access to and use of the Platform via mobile applications, web services, APIs, and all related functionality. It must be read together with the Platform's Privacy Policy at trustsquare.co/privacy.</p>\n<p><strong>2.3 Role of the Platform</strong></p>\n<p>The Platform facilitates connections between Buyers and Sellers. It is not a party to any transaction and does not:</p>\n<ul>\n<li><p>Own, control, or take title to any listing, property, service, or experience offered by Sellers</p></li>\n<li><p>Represent, employ, or create an agency relationship with Buyers or Sellers</p></li>\n<li><p>Guarantee the outcome, quality, safety, legality, or suitability of any transaction</p></li>\n<li><p>Act as a financial intermediary between Users for non-Tuppence transactions</p></li>\n</ul>\n<p><strong>2.4 EULA Acceptance Gate \u2014 Mandatory Before Registration</strong></p>\n<p>You must read and accept this EULA before your registration is created on the Platform. The acceptance process is as follows:</p>\n<ol type=\"1\">\n<li><p>You receive a Magic Link via email or click a sign-up link on the Platform.</p></li>\n<li><p>On clicking the link, an EULA acceptance screen is presented as the first step before any registration or listing data is created.</p></li>\n<li><p>You must tick \"I have read and agree to the Terms of Use / EULA and Privacy Policy\" and click \"Accept and Continue\".</p></li>\n<li><p>The Platform records your acceptance timestamp and EULA version number. This record is stored in the Platform's database and constitutes your binding agreement.</p></li>\n<li><p>Clicking \"Accept and Continue\" constitutes your electronic signature on this Agreement per Section 4 of the ECT Act.</p></li>\n</ol>\n<table>\n<tbody>\n<tr>\n<td><p><strong>Why Acceptance Happens Here</strong></p>\n<p>The Adventures category involves photo uploads of properties and experiences. The Platform's licence to store, display, and present those photos must be explicitly consented to at the point of intent \u2014 not assumed from an email click. Acceptance here also satisfies POPIA's requirement for informed, specific, opt-in consent before personal data is processed.</p></td>\n</tr>\n</tbody>\n</table>\n<p><strong>2.5 Eligibility</strong></p>\n<p>By accepting this EULA you represent and warrant that:</p>\n<ul>\n<li><p>You are at least 18 years of age;</p></li>\n<li><p>You have the legal capacity to enter binding agreements under South African law;</p></li>\n<li><p>You are not subject to sanctions, a court order barring Platform use, or a prohibition on your profession;</p></li>\n<li><p>If registering on behalf of a legal entity, you have authority to bind that entity;</p></li>\n<li><p>All information you provide is accurate, complete, and not misleading.</p></li>\n</ul>\n<blockquote>\n<p><strong>3. User Accounts, Anonymity &amp; Identity Verification</strong></p>\n</blockquote>\n<p><strong>3.1 Anonymity Principle \u2014 Mode B</strong></p>\n<p>The Platform is built on an anonymity-first model. When you create a Seller account, your identity \u2014 name, email, business name, contact details, and exact location \u2014 is not revealed to Buyers. Your public profile shows only:</p>\n<ul>\n<li><p>An emoji avatar (randomly assigned)</p></li>\n<li><p>Your category (e.g. Property, Adventures Accommodation)</p></li>\n<li><p>Your Trust Score (0\u2013100)</p></li>\n<li><p>Your suburb or city (general location only)</p></li>\n<li><p>A certification badge if verified credentials have been approved (see Section 7.3)</p></li>\n</ul>\n<p>No photo. No name. No contact details. No personal identifiers \u2014 until both parties complete the bilateral acceptance described in Section 3.2.</p>\n<p><strong>3.2 Bilateral Identity Reveal \u2014 The Acceptance Gate</strong></p>\n<p>A Seller's identity is revealed to a Buyer only when both of the following occur simultaneously:</p>\n<ul>\n<li><p>The Buyer sends the Seller an Introduction request, and</p></li>\n<li><p>The Seller accepts that Introduction (within the applicable response window).</p></li>\n</ul>\n<p>At the moment of bilateral acceptance, each party is shown the other's full name, email address, phone number, suburb/city, and \u2014 for Sellers \u2014 any verified professional credentials. Until both parties accept, full anonymity is maintained.</p>\n<p><strong>3.3 Prohibited Circumvention of Anonymity</strong></p>\n<p>You may not attempt to reveal your identity to the other party before bilateral acceptance. Prohibited actions include:</p>\n<ul>\n<li><p>Including your name, phone number, business name, or contact email in listing text or titles</p></li>\n<li><p>Linking to external social media profiles that identify you by name</p></li>\n<li><p>Communicating via off-platform channels before Introduction acceptance</p></li>\n</ul>\n<p>Exception: Professional licence numbers and certification badges may be displayed as part of the credential system (Section 7.4). These are anonymity-neutral: they signal verified quality without revealing personal identity.</p>\n<p><strong>3.4 Deferred KYC \u2014 FICA Compliance Model [COUNSEL REQUIRED]</strong></p>\n<p>South Africa's FICA requires customer identification before a business relationship commences. The Platform interprets \"business relationship\" as the first Introduction acceptance (i.e. the first transaction), not account creation. This interpretation must be confirmed by legal counsel before publication.</p>\n<p>Under this model, full identity verification is deferred as follows:</p>\n<ul>\n<li><p>Before first Introduction acceptance: account requires verified email only. Full identity is not yet required.</p></li>\n<li><p>After first Introduction acceptance: FICA-compliant identity verification is initiated within 24 hours. This must be completed within 5 business days. If verification fails or is not completed, the Introduction is cancelled. Tuppence already spent remains spent.</p></li>\n</ul>\n<p><strong>3.5 Identity Verification Process</strong></p>\n<p>After accepting your first Introduction, you will be asked to provide:</p>\n<ol start=\"6\" type=\"1\">\n<li><p>A government-issued identity document (South African Smart Card ID, passport, or driver's licence);</p></li>\n<li><p>Proof of address dated within 3 months (utility bill, bank statement, or lease agreement);</p></li>\n<li><p>A liveness check (selfie with ID via the Platform's third-party verification partner: [COUNSEL REQUIRED: insert provider]).</p></li>\n</ol>\n<p>Verification is normally completed within 3 business days. Your identity documents are encrypted in transit (TLS 1.3), stored on the Platform's server (Hetzner CPX32, Germany \u2014 upgraded from CPX22 on 25 May 2026), and accessible only to the Platform's compliance team. Documents are retained for 7 years per FICA requirements and then securely deleted.</p>\n<p><strong>3.6 Regulatory Disclosure</strong></p>\n<p>Notwithstanding the anonymity principle, the Platform may disclose your identity and account data to the South African Police Service, National Prosecuting Authority, Financial Intelligence Centre, courts, SARS, or FSCA, upon receipt of a lawful court order, administrative demand, or equivalent legal process. You will be notified of any such disclosure within 30 days unless the order prohibits notification.</p>\n<p><strong>3.7 User Responsibilities</strong></p>\n<p>You are responsible for all activity conducted under your account. You must not share your account credentials with any other person. You must notify the Platform immediately at support@trustsquare.co if you suspect unauthorised access to your account.</p>\n<blockquote>\n<p><strong>4. Listings, Content Accuracy &amp; Categories</strong></p>\n</blockquote>\n<p><strong>4.1 Seller Responsibility</strong></p>\n<p>You are solely responsible for the accuracy, completeness, legality, and currency of your listing content, including all descriptions, prices, photos, availability, and credential claims. The Platform does not verify listing content and makes no representations as to its accuracy.</p>\n<p><strong>4.2 Platform Moderation Rights</strong></p>\n<p>The Platform reserves the right to:</p>\n<ul>\n<li><p>Remove, hide, or edit any listing that violates this EULA, applicable law, or Platform policies;</p></li>\n<li><p>Suspend or terminate a Seller's account for repeated or serious violations;</p></li>\n<li><p>Reorder or prioritise listings in search results based on Trust Score and other ranking factors (see Section 12);</p></li>\n<li><p>At its discretion, refuse to onboard any prospective Seller.</p></li>\n</ul>\n<p><strong>4.3 Prohibited Listing Content</strong></p>\n<p>You may not list content that:</p>\n<ul>\n<li><p>Is false, misleading, deceptive, or fraudulent;</p></li>\n<li><p>Infringes the intellectual property rights of any third party;</p></li>\n<li><p>Promotes illegal goods, services, or activities;</p></li>\n<li><p>Contains obscene, defamatory, hateful, or discriminatory material;</p></li>\n<li><p>Includes personal contact details in violation of Section 3.3;</p></li>\n<li><p>Claims professional credentials you do not hold.</p></li>\n</ul>\n<p><strong>4.4 Categories \u2014 Open-Ended Strings</strong></p>\n<p>The Platform's category system is open-ended. Current and planned categories include Property (Estate Agents), Tutors, Services, Casuals, Adventures Accommodation, Adventures Experiences, and Collectors. New categories may be added at any time with notice to Users. Category strings are read dynamically from the Platform's data and are never hardcoded. Each category may have specific rules, introduction models, and Trust Score mechanics as described in Section 12.</p>\n<p><strong>4.5 Adventures Category \u2014 Photo Standards</strong></p>\n<p>Listings in the Adventures category (Accommodation and Experiences) are strongly encouraged to include high-quality photos. By uploading photos to an Adventures listing you confirm that:</p>\n<ul>\n<li><p>You are the copyright owner of the photos, or have explicit written permission from the copyright holder to use them commercially;</p></li>\n<li><p>The photos accurately represent the property or experience as of the listing date;</p></li>\n<li><p>The photos do not contain personally identifiable information that would breach Section 3.3.</p></li>\n</ul>\n<blockquote>\n<p><strong>5. Transactions &amp; Tuppence \u2014 The Introduction Currency</strong></p>\n</blockquote>\n<p><strong>5.1 How Tuppence Works</strong></p>\n<p>All Platform transactions are denominated in Tuppence. 1 Tuppence (1T) = USD $2.00 (fixed). This rate does not change and does not fluctuate with currency markets.</p>\n<p>The Tuppence model works as follows:</p>\n<ol start=\"9\" type=\"1\">\n<li><p>A Buyer sends an Introduction request to a Seller at no immediate cost. No Tuppence is deducted from the Buyer's balance at the time of sending. In the Casuals category, the roles are described as Requester (the person seeking help, who pays the 1T) and Helper (the person who listed their availability, who accepts). The Tuppence mechanics are identical \u2014 the party seeking the service always pays, the listed party always accepts.</p></li>\n<li><p>If the Seller accepts the Introduction, 1T is deducted from the Buyer's Tuppence balance and credited to the Seller's Tuppence Wallet. Both parties' contact details are then revealed to each other. This is the only event that triggers a Tuppence deduction. (In Casuals: if the Helper accepts the Requester's Introduction, 1T is deducted from the Requester's balance and credited to the Helper's Wallet. The mechanics are identical.)</p></li>\n<li><p>If the Seller declines or does not respond within the 48-hour window, no Tuppence is deducted from the Buyer's balance. The Introduction closes with no charge to either party.</p></li>\n<li><p>No further Platform fee applies to any subsequent transaction between Buyer and Seller. All post-Introduction transactions occur independently of the Platform.</p></li>\n</ol>\n<p><strong>5.2 Tuppence Restrictions</strong></p>\n<p>Tuppence is subject to the following restrictions:</p>\n<ul>\n<li><p>Non-transferable: Tuppence cannot be transferred between User accounts;</p></li>\n<li><p>Non-redeemable for cash (current state): Tuppence cannot currently be converted to ZAR or any other currency. [Note: Cash-out functionality may be introduced in future, subject to FSCA compliance and updated terms];</p></li>\n<li><p>Platform-exclusive: Tuppence has no monetary value outside the Platform and cannot be used on any other platform;</p></li>\n<li><p>Non-inheritable and non-assignable: Tuppence cannot be inherited or transferred on account closure;</p></li>\n<li><p>No expiry (current state): Tuppence balances do not expire unless the Platform closes or your account is terminated for breach.</p></li>\n</ul>\n<p><strong>5.3 Introduction Model by Category</strong></p>\n<p>The introduction model differs by category. The Platform reserves the right to update these models with notice:</p>\n<table>\n<tbody>\n<tr>\n<td><strong>Category</strong></td>\n<td><strong>Model</strong></td>\n<td><strong>Trust Score Penalty for Ignoring</strong></td>\n</tr>\n<tr>\n<td>Property (Estate Agents)</td>\n<td>Commitment: listing pauses on Introduction; one Buyer at a time; 48-hour window. Seller ignores: Trust Score \u22125; listing unpauses automatically. No Tuppence is deducted (Principle A8).</td>\n<td>\u22125 points for ignoring</td>\n</tr>\n<tr>\n<td>Tutors</td>\n<td>Soft Queue: listing stays live; multiple Buyers can queue; 48-hour window.</td>\n<td>\u22123 points for ignoring; no penalty for declining</td>\n</tr>\n<tr>\n<td>Services</td>\n<td>Soft Queue: listing stays live; multiple Buyers can queue; 48-hour window.</td>\n<td>\u22123 points for ignoring; no penalty for declining</td>\n</tr>\n<tr>\n<td>Casuals</td>\n<td>Soft Queue: proximity and referral-based discovery. Role note: in Casuals the Lister is the Helper (offering their availability); the Requester (seeking help) pays 1T to reach them. The Tuppence direction is unchanged \u2014 the seeker of the service pays on the Helper's acceptance.</td>\n<td>No Trust Score penalty</td>\n</tr>\n<tr>\n<td>Adventures Accommodation</td>\n<td>Soft Queue: listing stays live; multiple Buyers can queue; 48-hour window.</td>\n<td>No Trust Score penalty \u2014 seasonal and capacity constraints acknowledged</td>\n</tr>\n<tr>\n<td>Adventures Experiences</td>\n<td>Soft Queue: listing stays live; multiple Buyers can queue; 48-hour window.</td>\n<td>No Trust Score penalty \u2014 seasonal and capacity constraints acknowledged</td>\n</tr>\n<tr>\n<td>Collectors</td>\n<td>Commitment: listing pauses on Introduction; one Buyer at a time; 48-hour window. Seller ignores: Trust Score \u22125; listing unpauses automatically. No Tuppence is deducted (Principle A8). [COUNSEL REQUIRED: confirm model with council before Collectors category launch \u2014 see note below]</td>\n<td>\u22125 points for ignoring [subject to council confirmation]</td>\n</tr>\n</tbody>\n</table>\n<table>\n<tbody>\n<tr>\n<td><p><strong>Adventures \u2014 No Trust Score Penalty</strong></p>\n<p>Adventures Sellers (both Accommodation and Experiences) are exempt from Trust Score penalties for non-response to Introductions. This reflects the legitimate seasonal, capacity, and availability constraints specific to accommodation and experiences operators, and is a deliberate departure from the Tutors/Services Soft Queue model.</p></td>\n</tr>\n</tbody>\n</table>\n<table>\n<tbody>\n<tr>\n<td><p><strong>Collectors \u2014 Introduction Model Pending Council Confirmation</strong></p>\n<p>The Collectors category (physical and digital collectibles, trading cards, memorabilia, art) is planned but not yet live. The introduction model shown above (Commitment, same as Property) is the recommended model \u2014 a rare or unique item should only be offered to one serious Buyer at a time. However, this must be confirmed by the Solar Council before the Collectors category is activated. This EULA entry is a placeholder and will be updated at that time.</p></td>\n</tr>\n</tbody>\n</table>\n<p><strong>5.4 ECT Act \u00a744 \u2014 Scope and Applicability to TrustSquare</strong></p>\n<p>The ECT Act \u00a744 7-day cooling-off right applies to agreements for the supply of goods or services concluded electronically. TrustSquare supplies one service only: the Introduction. Once the Seller accepts the Introduction, that service is complete and TrustSquare's obligation is fulfilled. The 1T charged at that moment is the fee for that completed service and is not subject to reversal under ECT Act \u00a744.</p>\n<ul>\n<li><p>If the Seller has not yet accepted the Introduction, the Buyer may withdraw the request by emailing support@trustsquare.co with the subject line \"WITHDRAW: [Introduction ID]\". No Tuppence has been deducted at that point and no charge arises.</p></li>\n<li><p>Any right the Buyer may have to cancel or reverse the underlying transaction with the Seller (for example, a property rental agreement, tutor engagement, or service contract) is a matter between the Buyer and the Seller under the CPA, the NCA, or any other applicable law. TrustSquare is not a party to that transaction and has no obligation or liability in connection with it.</p></li>\n</ul>\n<p>TrustSquare's Introduction fee is earned and final on Seller acceptance. No reissuance of Tuppence is made on the basis of what occurs between Buyer and Seller after the Introduction is completed. Post-acceptance disputes \u2014 including any claim that a deal was not concluded, that goods or services were not delivered, or that either party acted in bad faith \u2014 are matters for the parties themselves and, if necessary, the National Consumer Commission or a competent court. TrustSquare's liability in such cases is limited as set out in Section 10.</p>\n<p><strong>5.5 AI Feature Tuppence \u2014 Optional, Subscription-Based, Separate from Introductions</strong></p>\n<p>The Platform offers an optional AI-assisted feature (\"AdvertAgent\" or equivalent) that allows Sellers to access artificial intelligence support for listing creation, optimisation, and related tasks. AI Feature usage is charged in Tuppence and is governed by the following rules, which are distinct from and independent of the Introduction Tuppence model:</p>\n<table>\n<tbody>\n<tr>\n<td><strong>Characteristic</strong></td>\n<td><strong>AI Feature Tuppence</strong></td>\n</tr>\n<tr>\n<td>Who it applies to</td>\n<td>Sellers only. Not available to Buyers. Not part of the core marketplace flow.</td>\n</tr>\n<tr>\n<td>Nature of use</td>\n<td>Entirely optional. A Seller chooses to invoke an AI feature. No AI feature is triggered automatically or as a condition of listing or receiving Introductions.</td>\n</tr>\n<tr>\n<td>Why Tuppence is charged</td>\n<td>AI features are powered by an external AI API (currently Anthropic Claude). The Platform incurs a real per-use cost from this third-party provider. Tuppence charged for AI use is cost-recovery for that external API cost \u2014 it is not platform revenue in the same sense as Introduction Tuppence.</td>\n</tr>\n<tr>\n<td>Access model</td>\n<td>AI features are accessed via a paid Seller subscription tier. The subscription fee covers a quota of AI interactions per billing period. Usage beyond the quota may incur additional Tuppence charges, disclosed at the point of use.</td>\n</tr>\n<tr>\n<td>Pricing</td>\n<td>AI Feature Tuppence pricing and subscription tiers are not yet finalised. They will be published and notified to Users before the AI feature is activated. No AI Feature charges will be applied without prior disclosure and your acceptance of updated terms.</td>\n</tr>\n<tr>\n<td>Refunds</td>\n<td>AI Feature Tuppence is non-refundable under any circumstance once an AI request is submitted. Submitting an AI request consumes the Tuppence regardless of the output quality or outcome.</td>\n</tr>\n<tr>\n<td>Relationship to Introductions</td>\n<td>AI Feature Tuppence and Introduction Tuppence are separate balances and flows. Using AI features does not affect your Introduction Tuppence balance, Trust Score, or listing status.</td>\n</tr>\n</tbody>\n</table>\n<table>\n<tbody>\n<tr>\n<td><p><strong>Important \u2014 AI Feature Tuppence is Different in Nature</strong></p>\n<p>Introduction Tuppence is the Platform's core marketplace fee \u2014 it is how the Platform earns revenue. AI Feature Tuppence is different: it is a pass-through cost-recovery mechanism for a real external API expense. The Platform does not profit from AI Feature Tuppence beyond recovering its cost of providing the feature. This distinction matters for how you budget your Platform use and for regulatory classification purposes.</p></td>\n</tr>\n</tbody>\n</table>\n<p><strong>5.6 Tuppence and the Platform \u2014 Not a Financial Intermediary</strong></p>\n<p>The Platform is not a financial intermediary between Users. Tuppence transactions \u2014 whether Introduction Tuppence or AI Feature Tuppence \u2014 are not financial products, loans, credit facilities, or investment instruments. Post-Introduction transactions (e.g. a rental payment, a coaching fee, a booking deposit) take place entirely outside the Platform between Buyer and Seller. The Platform has no involvement in, visibility of, or liability for such transactions.</p>\n<p><strong>5.7 Tuppence Holds and Reversals</strong></p>\n<p>The Platform may temporarily hold or reverse Tuppence transactions to prevent fraud, address system errors, or correct processing anomalies. The Platform will notify affected Users within 48 hours of any hold or reversal and will resolve the matter within 5 business days.</p>\n<blockquote>\n<p><strong>6. Fees, Subscriptions &amp; Payment</strong></p>\n</blockquote>\n<p><strong>6.1 Fee Disclosure</strong></p>\n<p>The Platform charges only for the following, which are presented to you before the transaction is confirmed:</p>\n<ul>\n<li><p>Introduction Tuppence: 1T (USD $2) per Introduction, charged to the Buyer's balance only upon Seller acceptance of the Introduction (Section 5.1\u20135.4). No charge arises on submission, decline, or non-response;</p></li>\n<li><p>AI Feature Tuppence: variable Tuppence per AI interaction, charged to Sellers who opt into AI-assisted features via a paid subscription (Section 5.5). Pricing TBD \u2014 no charges apply until pricing is published and accepted;</p></li>\n<li><p>Buyer subscription fees for premium access tiers (see Section 6.2);</p></li>\n<li><p>Seller AI feature subscription fees, if elected (see Section 5.5);</p></li>\n<li><p>Any future Tuppence top-up or purchase fees (subject to updated terms and FSCA compliance).</p></li>\n</ul>\n<p>There are no hidden fees, listing fees, commissions, or booking percentages. The Platform earns from Introduction fees and subscriptions only. AI Feature Tuppence is cost-recovery for an external API, not an additional profit margin (see Section 5.5).</p>\n<p><strong>6.2 Buyer Subscription Tiers [Preliminary \u2014 subject to change]</strong></p>\n<table>\n<tbody>\n<tr>\n<td><strong>Tier</strong></td>\n<td><strong>Details</strong></td>\n</tr>\n<tr>\n<td>Free \u2014 $0/month</td>\n<td>3 Introduction sessions per day; local city only</td>\n</tr>\n<tr>\n<td>Starter \u2014 $5/month</td>\n<td>20 Introduction sessions per day; country scope</td>\n</tr>\n<tr>\n<td>Premium \u2014 $15/month</td>\n<td>50 Introduction sessions per day; global scope</td>\n</tr>\n</tbody>\n</table>\n<p>Subscription tiers and pricing are preliminary as of April 2026 and will be confirmed before payment processing is activated. Updated terms will be provided.</p>\n<p><strong>6.3 Tuppence Service Credit Reissuance (not a Refund)</strong></p>\n<p>Tuppence is a non-transferable, non-redeemable platform service credit. It is not money. No Tuppence is deducted from a Buyer's balance unless and until the Seller explicitly accepts the Introduction. If the Seller declines or does not respond, no charge arises and no reissuance is necessary. The Platform will reissue Tuppence units (not ZAR) to a Buyer's balance as a discretionary service credit only in the following circumstances:</p>\n<ul>\n<li><p>Seller did not respond to the Introduction within the 48-hour window \u2014 no Tuppence was deducted (the charge only fires on acceptance), so no reissuance is required; the Introduction closes automatically with no charge to the Buyer;</p></li>\n<li><p>Seller declined the Introduction \u2014 no Tuppence was deducted (the charge only fires on acceptance), so no reissuance is required; the Introduction closes with no charge to the Buyer;</p></li>\n<li><p>Buyer withdraws the Introduction request before Seller acceptance (per Section 5.4) \u2014 no Tuppence was deducted, so no reissuance is required; the Introduction closes with no charge;</p></li>\n<li><p>Tuppence is not reissuable under any circumstance. Spending Tuppence on an Introduction request or AI feature consumes the Tuppence regardless of outcome. This is the consideration for the buyer-commitment signal that underpins the Platform\u2019s anti-spam design.</p></li>\n<li><p>The Platform terminates your account for convenience under Section 14.3 \u2014 unused Tuppence is forfeited; no cash payment or ZAR conversion is made (see Section 14.3 for the applicable outcome).</p></li>\n</ul>\n<p>Tuppence already credited to a Seller's Wallet upon acceptance of an Introduction is not reissuable under any circumstances. Tuppence is not redeemable for cash under any circumstances. Tuppence balances accrue no interest. Unused Tuppence expires after 24 consecutive months of account inactivity (no login, no Introduction, no purchase). The Platform will notify you by email not less than 30 days before expiry. Tuppence may not be used by a Buyer to settle any obligation owed to a Seller outside of the Platform's Introduction flow; any purported such arrangement is void and of no effect. Nothing in this Section 6.3 creates a contractual right of repayment of money paid; all reissuances described above are discretionary platform actions exercised by TrustSquare (Pty) Ltd in accordance with its consumer-protection obligations and SARB interpretive guidance on stored-value service credits. Once a Seller has accepted an Introduction and 1T has been deducted from the Buyer's balance, that deduction is final and irrevocable. Any subsequent agreement between Buyer and Seller to act as though the Introduction did not occur, to conduct their transaction outside the Platform in order to avoid the Tuppence charge, or to request a reversal on the grounds that no transaction ultimately took place between them, does not entitle either party to a reissuance. The accepted risk of an Introduction not resulting in a completed transaction is borne by the accepting party \u2014 the Seller in standard categories, the Helper in the Casuals category.</p>\n<p><strong>6.4 Payment Processor</strong></p>\n<p>Tuppence purchases (when enabled) and subscription payments are processed by Paystack (a registered payment service provider in South Africa). By making a payment on the Platform, you agree to Paystack's terms and privacy policy. The Platform is not responsible for payment processing errors, delays, or security incidents attributable to Paystack.</p>\n<p><strong>6.5 Taxes</strong></p>\n<p>You are solely responsible for determining and remitting all taxes arising from your use of the Platform, including income tax, VAT, and any withholding obligations. The Platform does not withhold or remit taxes on your behalf. You may request a Tuppence transaction history statement for tax purposes by emailing support@trustsquare.co. [OPERATIONAL: confirm support@trustsquare.co mailbox is live and monitored before EULA is published to production.]</p>\n<p><strong>6.6 Direct Marketing Compliance (CPA 2026 Amendment)</strong></p>\n<p>[COUNSEL REQUIRED: Confirm whether TrustSquare (Pty) Ltd is required to register as a direct marketer with the NCC under the CPA, given that (a) Introduction notification emails are transactional (sent only to registered users who opted in at account creation) and (b) prospecting outreach is conducted via a separate CityLauncher tool. If registration is required, insert NCC Registration No. and activate this clause. Until confirmed and registration obtained, the following placeholder applies:] The Platform complies with the direct marketing provisions of the Consumer Protection Act No. 68 of 2008. Every promotional communication sent by the Platform includes an unsubscribe mechanism. Opt-out requests are processed within 5 business days.</p>\n<p>By creating an account you opt in to Introduction notification emails and Platform marketing. You may opt out at any time via your account settings or by emailing support@trustsquare.co with the subject \"OPT-OUT\".</p>\n<blockquote>\n<p><strong>7. Professional Credentials, Certification &amp; AI Features</strong></p>\n</blockquote>\n<p><strong>7.1 Professional Licensing Obligations</strong></p>\n<p>If your category requires professional registration or licensing under South African law, you agree to hold the required licence at the time of listing and keep it valid throughout your use of the Platform. Known licensing requirements include:</p>\n<table>\n<tbody>\n<tr>\n<td><strong>Category</strong></td>\n<td><strong>Licensing Requirement</strong></td>\n</tr>\n<tr>\n<td>Property (Estate Agents)</td>\n<td>Registration with the Estate Agency Affairs Board (EAAB)</td>\n</tr>\n<tr>\n<td>Services (Electricians, Plumbers)</td>\n<td>Trade licence or professional registration as applicable under sector legislation</td>\n</tr>\n<tr>\n<td>Tutors</td>\n<td>Teaching credential or institutional affiliation preferred; not mandatory</td>\n</tr>\n<tr>\n<td>Casuals</td>\n<td>No licence required</td>\n</tr>\n<tr>\n<td>Adventures Accommodation</td>\n<td>Compliance with applicable municipal accommodation bylaws and tourism permits</td>\n</tr>\n<tr>\n<td>Adventures Experiences</td>\n<td>Registered tourism guide (CATHSSETA) where required by law; sector-specific qualifications (e.g. PADI for diving, SAMSA for marine activities)</td>\n</tr>\n</tbody>\n</table>\n<p><strong>7.2 Licence Attestation</strong></p>\n<p>At account creation, you attest that you hold all required professional licences and that you are not barred by law from practising your profession. False attestation is grounds for immediate account termination and may give rise to civil or criminal liability. The Platform reserves the right to verify your licence through official registers (e.g. EAAB database).</p>\n<p><strong>7.3 Adventures Certification Uplift \u2014 Trust Score Bonus</strong></p>\n<p>Sellers in the Adventures category (Accommodation and Experiences) may upload verifiable credentials to earn a Trust Score bonus that increases listing visibility. This mechanism is specific to Adventures and does not apply to other categories without a separate platform decision.</p>\n<p>Bonus certification types and indicative Trust Score awards:</p>\n<table>\n<tbody>\n<tr>\n<td><strong>Certification</strong></td>\n<td><strong>Indicative Bonus</strong></td>\n</tr>\n<tr>\n<td>TGCSA grading \u2014 1 star</td>\n<td>+5 points</td>\n</tr>\n<tr>\n<td>TGCSA grading \u2014 2 star</td>\n<td>+10 points</td>\n</tr>\n<tr>\n<td>TGCSA grading \u2014 3 star</td>\n<td>+15 points</td>\n</tr>\n<tr>\n<td>TGCSA grading \u2014 4 star</td>\n<td>+20 points</td>\n</tr>\n<tr>\n<td>TGCSA grading \u2014 5 star</td>\n<td>+25 points</td>\n</tr>\n<tr>\n<td>SATSA membership</td>\n<td>+10 points</td>\n</tr>\n<tr>\n<td>FEDHASA membership</td>\n<td>+8 points</td>\n</tr>\n<tr>\n<td>CATHSSETA registered tourism guide</td>\n<td>+10 points</td>\n</tr>\n<tr>\n<td>SA Mountain Club / UIAA guide certification</td>\n<td>+12 points</td>\n</tr>\n<tr>\n<td>PADI / NAUI / SAMSA diving/marine certification</td>\n<td>+12 points</td>\n</tr>\n<tr>\n<td>Liquor licence (WSET or national)</td>\n<td>+6 points</td>\n</tr>\n<tr>\n<td>Wilderness first aid / first aid certification</td>\n<td>+5 points</td>\n</tr>\n<tr>\n<td>PDP / SABOA transport operator licence</td>\n<td>+8 points</td>\n</tr>\n</tbody>\n</table>\n<table>\n<tbody>\n<tr>\n<td><p><strong>Bonus Values Are Indicative</strong></p>\n<p>The Trust Score bonus values above are indicative and subject to confirmation in the Solar Council Codex. Final values will be published in the Platform's Trust Score policy document before the Adventures category goes live.</p></td>\n</tr>\n</tbody>\n</table>\n<p><strong>7.4 Certification Upload &amp; Review Process</strong></p>\n<p>To claim a certification bonus:</p>\n<ol start=\"13\" type=\"1\">\n<li><p>Upload a photo or PDF of your certificate during Adventures onboarding or from your Seller profile.</p></li>\n<li><p>The certification is marked Pending Review. The Trust Score bonus is not applied until an administrator has reviewed and approved the certification.</p></li>\n<li><p>Review is normally completed within 5 business days.</p></li>\n<li><p>On approval, the bonus is applied to your Trust Score and your listing re-ranks accordingly.</p></li>\n<li><p>If a certificate expires or is revoked, you must notify the Platform within 5 business days. The Platform may withdraw the bonus and adjust your Trust Score.</p></li>\n</ol>\n<p><strong>7.5 Anonymity and Credentials</strong></p>\n<p>Certification badges (e.g. a shield icon with star count or certification abbreviation) are visible on your listing card to Buyers before Introduction acceptance. This is a deliberate exception to the anonymity principle: the badge signals verified quality without revealing your personal identity. Your underlying certificate and personal details are stored by the Platform but are never disclosed to Buyers until bilateral acceptance.</p>\n<p><strong>7.6 AI-Assisted Features</strong></p>\n<p>The Platform may use artificial intelligence and machine learning to assess listing quality, detect duplicate listings or potential fraud, provide category recommendations, and surface relevant listings to Buyers. AI features do not make final decisions: the Platform retains override authority, and no AI-generated output is used to permanently penalise a User without human review. You may not use automated tools, bots, or scripts to interact with the Platform.</p>\n<blockquote>\n<p><strong>8. User-Uploaded Content, Photo Rights &amp; IP Indemnity</strong></p>\n</blockquote>\n<p><strong>8.1 Your Copyright Ownership</strong></p>\n<p>You retain full copyright ownership of all content you upload to the Platform, including listing photos, videos, descriptions, and other media (\"Your Content\"). Nothing in this EULA transfers copyright ownership from you to the Platform.</p>\n<p><strong>8.2 Licence Granted to the Platform \u2014 Full In-Platform Use</strong></p>\n<p>By uploading Your Content to the Platform, you grant the Platform and its affiliates, sub-contractors, and technical service providers a non-exclusive, worldwide, royalty-free, perpetual, irrevocable licence to use Your Content in the following ways across all current and future MarketSquare applications and platform features:</p>\n<ul>\n<li><p>Store, host, cache, and back up Your Content on Platform servers and content delivery networks;</p></li>\n<li><p>Display and present Your Content on all Platform screens, listing cards, search results, category browsers, Buyer-facing views, and Seller dashboards \u2014 across web, mobile, and any future application in the MarketSquare product family;</p></li>\n<li><p>Technically process Your Content as needed for Platform operation: resizing, cropping, compression, format conversion, thumbnail generation, and watermarking for display optimisation \u2014 without material alteration of the substantive content;</p></li>\n<li><p>Use Your Content within Platform-internal promotional and discovery features, including featured listings, category highlights, onboarding screens, and in-app recommendations shown to Platform Users;</p></li>\n<li><p>Reproduce and distribute Your Content solely within the Platform ecosystem to facilitate the connection between Buyers and Sellers;</p></li>\n<li><p>Retain a cached or archived copy of Your Content for legal, compliance, audit, or dispute resolution purposes for up to 7 years after your account is closed, as required by applicable law.</p></li>\n</ul>\n<table>\n<tbody>\n<tr>\n<td><p><strong>What This Licence Covers</strong></p>\n<p>This licence covers everything needed to run, operate, and develop MarketSquare and its apps. It is intentionally broad within the Platform ecosystem. It does not give the Platform any right to use your photos outside that ecosystem \u2014 see Section 8.3 for the hard limits.</p></td>\n</tr>\n</tbody>\n</table>\n<p><strong>8.3 What the Platform Will Never Do With Your Content</strong></p>\n<p>Notwithstanding the broad licence in Section 8.2, the Platform gives you the following unconditional commitments:</p>\n<ul>\n<li><p>The Platform will never sell, license, or transfer Your Content to any third party as photo stock, stock imagery, or for any independent commercial purpose outside the Platform;</p></li>\n<li><p>The Platform will never provide Your Content to stock photography agencies, image libraries, data brokers, advertising networks, or any external commercial entity;</p></li>\n<li><p>The Platform will never use Your Content in external advertising or marketing campaigns \u2014 print, digital, social media, or otherwise \u2014 without your express prior written consent given separately from this EULA;</p></li>\n<li><p>The Platform will never create derivative works from Your Content for sale or distribution outside the Platform.</p></li>\n</ul>\n<table>\n<tbody>\n<tr>\n<td><p><strong>Platform Commitment \u2014 No Photo Stock Sales</strong></p>\n<p>The Platform operates on a marketplace model. Selling or licensing user-uploaded photos to third parties is not part of that model and will never be. If this policy changes in the future, users will be individually notified and fresh consent will be required before any such use.</p></td>\n</tr>\n</tbody>\n</table>\n<p><strong>8.4 User Warranty \u2014 Ownership and Right to Upload</strong></p>\n<p>By uploading any photo, image, video, or other media to the Platform, you make the following legally binding warranties to the Platform on each occasion of upload:</p>\n<ol start=\"18\" type=\"1\">\n<li><p>You are the sole and original copyright owner of the uploaded content, OR you hold a valid, written, transferable licence from the copyright owner that expressly authorises you to grant the licence in Section 8.2;</p></li>\n<li><p>The content does not infringe any copyright, moral right, trade mark, design right, personality right, right of privacy, right of publicity, or any other intellectual property or personal right of any third party anywhere in the world;</p></li>\n<li><p>You have obtained all necessary consents from any identifiable persons appearing in photos (including model releases where required) and from any property owners whose property is depicted, where such consent is required by applicable law;</p></li>\n<li><p>The content is not defamatory, obscene, unlawful, threatening, harassing, or otherwise in violation of any applicable law;</p></li>\n<li><p>Your upload does not violate any confidentiality obligation, court order, or contractual restriction binding on you;</p></li>\n<li><p>You have the full legal capacity and authority to grant this licence and to make these warranties.</p></li>\n</ol>\n<p>These warranties are given by you each time you upload content. They are ongoing and must remain true for as long as Your Content remains on the Platform. If any warranty becomes false after upload (for example, because a third party asserts copyright), you must notify the Platform immediately at legal@trustsquare.co and request removal of the affected content.</p>\n<p><strong>8.5 IP Indemnity \u2014 User's Full Liability for Infringing Uploads</strong></p>\n<p>The Platform accepts no liability for any intellectual property infringement arising from content uploaded by Users. You agree to fully indemnify, defend, and hold harmless the Platform, its directors, officers, employees, agents, and technical service providers from and against all claims, demands, proceedings, losses, damages, costs, and expenses (including reasonable legal fees) arising from or in connection with:</p>\n<ul>\n<li><p>Any claim by a third party that Your Content infringes that party's copyright, trade mark, design right, patent, moral right, right of privacy, right of publicity, or any other intellectual property or proprietary right;</p></li>\n<li><p>Any claim arising from your failure to obtain required model releases, property releases, or other consents for content depicted in your photos;</p></li>\n<li><p>Any breach of the warranties in Section 8.4;</p></li>\n<li><p>Any use by the Platform of Your Content in accordance with the licence granted in Section 8.2 that is subsequently alleged to infringe a third-party right because of your failure to hold the necessary rights at the time of upload;</p></li>\n<li><p>Any takedown notice, DMCA claim, or equivalent IP enforcement action filed against the Platform as a result of Your Content.</p></li>\n</ul>\n<p>This indemnity obligation survives the termination of your account and this EULA. The Platform reserves the right to assume exclusive control of the defence of any indemnified claim at your cost, in which case you agree to cooperate fully with the Platform's defence.</p>\n<table>\n<tbody>\n<tr>\n<td><p><strong>Plain Language Summary of Section 8.5</strong></p>\n<p>If you upload a photo that belongs to someone else and that person sues us, you pay \u2014 not us. This is the same standard applied by Airbnb, Booking.com, Viator, and every major platform that accepts user-uploaded images. It is fair, standard, and non-negotiable. Upload only photos you own or have written permission to use commercially.</p></td>\n</tr>\n</tbody>\n</table>\n<p><strong>8.6 Platform's IP Enforcement Response (Notice and Takedown)</strong></p>\n<p>If a third party believes that content on the Platform infringes their intellectual property rights, they may submit a written notice to legal@trustsquare.co including: a description of the allegedly infringing content and its location on the Platform; evidence of the claimant's ownership of the right allegedly infringed; and a statement that the claimant has a good-faith belief that the use is not authorised. The Platform will:</p>\n<ol start=\"24\" type=\"1\">\n<li><p>Acknowledge receipt within 1 business day;</p></li>\n<li><p>Investigate within 5 business days;</p></li>\n<li><p>Disable access to content that, on reasonable assessment, appears to infringe a third-party right;</p></li>\n<li><p>Notify the User who uploaded the content of the takedown and the reason;</p></li>\n<li><p>Provide the User with an opportunity to submit a counter-notice if they dispute the claim.</p></li>\n</ol>\n<p>The Platform's response to a takedown notice does not constitute an admission of liability. The Platform acts as an intermediary in good faith and its actions are taken in compliance with the ECT Act Section 79 safe harbour provisions.</p>\n<p><strong>8.7 Adventures Category \u2014 Photo Standards</strong></p>\n<p>Adventures listings (Accommodation and Experiences) are photo-intensive by nature. In addition to the warranties in Section 8.4, Sellers listing Adventures content additionally confirm by each upload that:</p>\n<ul>\n<li><p>Photos accurately and honestly represent the accommodation, property, or experience as at the date of upload and have not been digitally manipulated in a way that materially misrepresents what a guest would encounter;</p></li>\n<li><p>No photo depicts a property or experience that the Seller does not have the right to offer on the Platform;</p></li>\n<li><p>For accommodation photos: the Seller has the right to permit guests to access and stay in the depicted property;</p></li>\n<li><p>For experience photos: the photos depict activities that the Seller is qualified and authorised to offer.</p></li>\n</ul>\n<p><strong>8.8 Content Removal</strong></p>\n<p>If you delete a listing, the associated photos and media are removed from public display within 48 hours. If you delete your account, all publicly visible links to Your Content are removed. Cached content on third-party CDN networks may persist for up to 30 days before expiry.</p>\n<p>Content required for legal, compliance, or dispute purposes is retained for up to 7 years after account closure per Section 8.2 and applicable law. This retained content is not accessible to the public or to other Users.</p>\n<p><strong>8.9 Platform's Own Intellectual Property</strong></p>\n<p>All Platform software, source code, design systems, trade marks, trade names, logos, and proprietary content are the property of the Operator or its licensors and are protected by South African and international intellectual property law. Nothing in this EULA grants you any right to use the Platform's intellectual property other than as strictly necessary to use the Platform in accordance with this EULA. Unauthorised reproduction, reverse-engineering, or commercial use of the Platform's intellectual property is strictly prohibited and may give rise to civil and criminal liability.</p>\n<blockquote>\n<p><strong>9. Privacy, Data Protection &amp; POPIA Compliance</strong></p>\n</blockquote>\n<p><strong>9.1 Privacy Policy</strong></p>\n<p>The Platform's full Privacy Policy is available at trustsquare.co/privacy [COUNSEL REQUIRED: Privacy Policy must be drafted and published before launch] and is incorporated into this EULA by reference. In the event of any conflict between this EULA and the Privacy Policy regarding personal data matters, the Privacy Policy prevails.</p>\n<p><strong>9.2 Data We Collect and Why</strong></p>\n<table>\n<tbody>\n<tr>\n<td><strong>Data Type</strong></td>\n<td><strong>Purpose &amp; Legal Basis</strong></td>\n</tr>\n<tr>\n<td>Identity: name, email, phone, SA ID number</td>\n<td>FICA KYC compliance; account management; Introduction acceptance. Legal basis: contractual necessity; legal obligation (FICA).</td>\n</tr>\n<tr>\n<td>Location: suburb, city, region</td>\n<td>Listing display; proximity-based search. Legal basis: contractual necessity.</td>\n</tr>\n<tr>\n<td>Photos and listing media</td>\n<td>Listing display; all Platform app features; cached CDN distribution. Legal basis: contractual necessity (per Section 8.2 licence grant). Not sold to third parties per Section 8.3.</td>\n</tr>\n<tr>\n<td>Transaction data: Tuppence earned/spent, Introduction history</td>\n<td>Tuppence Wallet management; dispute resolution; FICA records. Legal basis: contractual necessity; legal obligation.</td>\n</tr>\n<tr>\n<td>Device and usage data: IP address, browser, analytics</td>\n<td>Fraud prevention; platform improvement. Legal basis: legitimate interest. Retained 30 days, anonymised.</td>\n</tr>\n<tr>\n<td>Certification documents: certificate photos/PDFs</td>\n<td>Trust Score bonus processing; credential verification. Legal basis: consent (given on upload).</td>\n</tr>\n</tbody>\n</table>\n<p><strong>9.3 POPIA Consent</strong></p>\n<p>By accepting this EULA, you give informed, specific, opt-in consent (as required by POPIA) to the processing described in Section 9.2. You specifically consent to deferred identity verification as described in Section 3.4. You may withdraw any consent by deleting your account (Section 14.1), subject to legally mandated retention periods.</p>\n<p><strong>9.4 Data Retention</strong></p>\n<ul>\n<li><p>Active accounts: identity and transaction data retained for account lifetime plus 7 years (FICA requirement);</p></li>\n<li><p>Deleted accounts: personal data anonymised or deleted within 30 days, except where a legal hold applies;</p></li>\n<li><p>Certification documents: retained while account is active; deleted on account closure unless a regulatory hold applies;</p></li>\n<li><p>Usage analytics: 30 days (anonymised at collection);</p></li>\n<li><p>All data: permanently deleted after applicable retention period expires.</p></li>\n</ul>\n<p><strong>9.5 Third-Party Disclosure</strong></p>\n<p>Personal data is disclosed only to:</p>\n<ul>\n<li><p>South African regulatory and law enforcement bodies on lawful demand (SAPS, NPA, FIC, SARS, FSCA, Information Regulator);</p></li>\n<li><p>Other Users, only after bilateral Introduction acceptance (Section 3.2);</p></li>\n<li><p>Payment processors (Paystack) for transaction processing, under data processing agreement;</p></li>\n<li><p>Service providers (Cloudflare R2 (primary) and Hetzner local disk (redundant mirror) for photo storage; email delivery provider) under data processing agreements and POPIA-compliant terms;</p></li>\n<li><p>The Platform's identity verification partner (Section 3.5) for KYC processing.</p></li>\n</ul>\n<p>Personal data is never sold to third parties.</p>\n<p><strong>9.6 International Data Transfers</strong></p>\n<p>Platform servers are hosted on Hetzner (currently CPX22, upgrading to CPX32 on 25 May 2026), located in Germany (EU). Photo storage uses a write-to-both architecture: Cloudflare R2 (EU-based CDN, primary) with automatic failover to a Hetzner local disk mirror on the same EU-hosted server. All storage is EU-based and governed by GDPR, which provides an adequate level of protection recognised under POPIA. Data Processing Agreements are in place with Cloudflare and Hetzner.</p>\n<p><strong>9.7 Your POPIA Rights</strong></p>\n<p>You have the following rights under POPIA, exercisable by emailing legal@trustsquare.co:</p>\n<ul>\n<li><p>Access: request a copy of your personal data in machine-readable format (CSV or JSON);</p></li>\n<li><p>Correction: update inaccurate data via your profile settings or by contacting support;</p></li>\n<li><p>Deletion (Right to be Forgotten): request deletion of your account and data within 30 days, subject to legal holds;</p></li>\n<li><p>Object: opt out of marketing communications, analytics, or specific processing activities;</p></li>\n<li><p>Lodge a complaint with the South African Information Regulator at inforegulator.org.za.</p></li>\n</ul>\n<p>Requests are processed within 20 business days.</p>\n<p><strong>9.8 Data Security</strong></p>\n<p>The Platform employs TLS 1.3 encryption in transit, server-side encryption at rest, role-based access controls, and daily encrypted backups to Cloudflare R2 with 14-day retention. Photos are stored redundantly on both Cloudflare R2 and a Hetzner local disk mirror, ensuring availability even if either storage layer is temporarily unreachable. Security is audited periodically by [COUNSEL REQUIRED: insert audit provider or frequency].</p>\n<p><strong>9.9 Data Breach Notification</strong></p>\n<p>In the event of a data breach that compromises the confidentiality, integrity, or availability of your personal data, the Platform will notify you by email and notify the South African Information Regulator within 30 days of becoming aware of the breach, as required by POPIA. The notification will describe the nature of the breach, the data affected, and the steps taken or planned.</p>\n<blockquote>\n<p><strong>10. Disputes, Enforcement &amp; Liability</strong></p>\n</blockquote>\n<p><strong>10.1 User Disputes</strong></p>\n<p>Disputes about listing content, transaction outcomes, service quality, or post-Introduction conduct are between the relevant Users. The Platform may, at its discretion, assist in facilitating communication but does not adjudicate, arbitrate, or guarantee any outcome in User-to-User disputes.</p>\n<p><strong>10.2 Platform Enforcement</strong></p>\n<p>The Platform may take the following enforcement steps in response to violations of this EULA or applicable law, in escalating order:</p>\n<ol start=\"29\" type=\"1\">\n<li><p>Warning notice by email;</p></li>\n<li><p>Temporary listing suspension;</p></li>\n<li><p>Trust Score reduction;</p></li>\n<li><p>Account suspension;</p></li>\n<li><p>Permanent account ban and data deletion;</p></li>\n<li><p>Referral to law enforcement or regulatory authorities.</p></li>\n</ol>\n<p><strong>10.3 Pre-Dispute Negotiation (60 Days)</strong></p>\n<p>Before either party initiates arbitration or litigation in connection with any dispute arising out of or relating to this EULA, the disputing party must send a written claim to the other party (or to support@trustsquare.co for disputes involving the Platform) describing the dispute in reasonable detail. The parties have 60 days from the date the claim is received to resolve the dispute by negotiation in good faith. This requirement does not apply to applications for urgent injunctive relief, IP infringement claims, or fraud.</p>\n<p><strong>10.4 Binding Arbitration [COUNSEL REQUIRED]</strong></p>\n<p>If the 60-day negotiation period expires without resolution, disputes between a User and the Platform shall be resolved by binding arbitration conducted in English under the rules of the South African Arbitration Foundation (SAAF), with the seat of arbitration in Cape Town, South Africa. The arbitrator shall be a practising South African attorney or advocate with at least 5 years' experience in commercial or technology law. Arbitration proceedings are confidential. Each party bears its own legal costs; the SAAF's arbitrator fees are split equally unless the arbitrator finds that one party acted in bad faith.</p>\n<p><strong>10.5 Consumer Protection Act Override</strong></p>\n<p>Nothing in this Section limits any rights you have under the Consumer Protection Act No. 68 of 2008 (CPA), including the right to approach the National Consumer Commission or the right to bring a claim in a Magistrate's Court for claims under ZAR 10,000. Any cooling-off or cancellation rights in respect of the underlying transaction between Buyer and Seller (property rental, tutor engagement, service contract, etc.) are rights exercisable against the Seller, not against TrustSquare. See Section 5.4.</p>\n<p><strong>10.6 Limitation of Liability</strong></p>\n<p>To the fullest extent permitted by South African law, the Platform's total aggregate liability to you in any 12-month period shall not exceed:</p>\n<ul>\n<li><p>For Sellers: the total Tuppence earned and credited to your Wallet during that period, valued at USD $2 per Tuppence; or</p></li>\n<li><p>For Buyers or other Users: ZAR 500.</p></li>\n</ul>\n<p>The Platform is not liable for any of the following, whether arising in contract, delict, statute, or otherwise:</p>\n<ul>\n<li><p>Indirect, incidental, consequential, special, or punitive damages;</p></li>\n<li><p>Loss of profit, revenue, data, business opportunity, goodwill, or anticipated savings;</p></li>\n<li><p>Actions, omissions, or conduct of any Seller, Buyer, or third party;</p></li>\n<li><p>Platform unavailability, bugs, errors, or interruptions except where caused by the Platform's gross negligence;</p></li>\n<li><p>Regulatory fines or compliance costs arising from your own violations.</p></li>\n</ul>\n<p>Nothing in this section limits the Platform's liability for death or personal injury caused by its own gross negligence or wilful misconduct, or for fraud.</p>\n<p><strong>10.7 ECT Act Safe Harbour (\u00a779)</strong></p>\n<p>The Platform provides an intermediary service as defined in the ECT Act. The Platform does not initiate, select, or modify User-generated content (listings, photos, contact details). Subject to compliance with Section 10.8, the Platform is not liable for such User content.</p>\n<p><strong>10.8 Notice and Takedown</strong></p>\n<p>If you believe Platform content is illegal, infringes your rights, or violates this EULA, notify the Platform by email at legal@trustsquare.co with a description of the content, its location on the Platform, and evidence supporting your claim. The Platform will: (i) confirm receipt within 24 hours; (ii) investigate within 48 hours; (iii) disable access to content found to be illegal; and (iv) notify you of the outcome.</p>\n<blockquote>\n<p><strong>11. Trust Score, Ranking &amp; Enforcement Criteria</strong></p>\n</blockquote>\n<p><strong>11.1 Trust Score System</strong></p>\n<p>Every Seller has a Trust Score (0\u2013100) that reflects their reliability and compliance on the Platform. The score determines listing display position and the badge displayed on listing cards.</p>\n<table>\n<tbody>\n<tr>\n<td><strong>Score Range</strong></td>\n<td><strong>Badge &amp; Visibility</strong></td>\n</tr>\n<tr>\n<td>0\u201339</td>\n<td>New \u2014 no badge; listed last in search results</td>\n</tr>\n<tr>\n<td>40\u201369</td>\n<td>Established \u2014 blue badge; standard listing position</td>\n</tr>\n<tr>\n<td>70\u201389</td>\n<td>Trusted \u2014 green badge; higher visibility</td>\n</tr>\n<tr>\n<td>90\u2013100</td>\n<td>Highly Trusted \u2014 gold badge + featured position</td>\n</tr>\n</tbody>\n</table>\n<p><strong>11.2 Score Factors</strong></p>\n<p>Trust Score is calculated algorithmically based on: time active on the Platform; number of accepted Introductions; response rate (percentage of Introductions responded to within 48 hours); average Buyer rating; formal complaint count; policy violations; and \u2014 for Adventures Sellers \u2014 approved certification bonuses (Section 7.3).</p>\n<p><strong>11.3 Trust Score Penalties</strong></p>\n<p>Penalties are applied automatically and in accordance with the introduction model for your category (see Section 5.3). Penalties decay over time: each penalty reduces by 50% every 90 days. Full recovery typically occurs within 180 days. The Platform does not manually waive penalties on User request. If you believe a penalty was applied in error, contact compliance@trustsquare.co.</p>\n<p><strong>11.4 Account Suspension for Low Score</strong></p>\n<p>If your Trust Score falls below 0, your account is automatically suspended. To request reactivation, contact compliance@trustsquare.co after 30 days. You may alternatively delete your account and re-register after a 90-day waiting period.</p>\n<p><strong>11.5 Public Display</strong></p>\n<p>Your Trust Score and badge tier are visible to all Platform Users on your profile and listing card, before and after Introduction acceptance. This is an inherent part of the Platform's transparency model.</p>\n<blockquote>\n<p><strong>12. Tuppence \u2014 Regulatory Classification &amp; Virtual Asset Status</strong></p>\n</blockquote>\n<p><strong>12.1 Current Classification</strong></p>\n<p>MarketSquare acknowledges that Tuppence may be scrutinised by the Financial Sector Conduct Authority (FSCA) as a potential virtual asset. The Platform operates two distinct Tuppence flows: Introduction Tuppence (Buyer-to-Platform, mandatory marketplace fee) and AI Feature Tuppence (Seller-to-Platform, optional cost-recovery for an external AI API). Both flows are assessed below. The Platform's current position is that neither constitutes a virtual asset under current FSCA classification, for the following reasons:</p>\n<ul>\n<li><p>Tuppence is non-transferable between Users (a key criterion for FSCA virtual asset classification is fungibility and transferability);</p></li>\n<li><p>Tuppence cannot be converted to cash or any other currency;</p></li>\n<li><p>Tuppence cannot be traded on any exchange;</p></li>\n<li><p>1T = USD $2 is a fixed platform rate, not a market price.</p></li>\n</ul>\n<p><strong>12.2 If Reclassified</strong></p>\n<p>If the FSCA reclassifies Tuppence as a virtual asset or determines that the Platform requires a Crypto Asset Service Provider (CASP) licence, the Platform will:</p>\n<ol start=\"35\" type=\"1\">\n<li><p>Apply for the required FSCA licence within 180 days of the reclassification notice;</p></li>\n<li><p>Update this EULA and the Privacy Policy to reflect new compliance obligations;</p></li>\n<li><p>Notify all active Users of the regulatory status change by email;</p></li>\n<li><p>Implement FICA-compliant KYC/AML screening as required.</p></li>\n</ol>\n<p><strong>12.3 NCA \u2014 Current Non-Applicability</strong></p>\n<p>Tuppence is currently earned through Introduction acceptance and is not purchased by Users via credit or installment. The National Credit Act (NCA) therefore does not apply to Tuppence in its current form. If a Tuppence purchase mechanism is introduced in future, the NCA's affordability assessment and disclosure obligations will apply, and fresh consent will be obtained from Users at that time.</p>\n<p><strong>12.4 No Financial Advice</strong></p>\n<p>The Platform does not provide financial, investment, or tax advice regarding Tuppence. You are responsible for understanding the legal and tax implications of Tuppence in your own jurisdiction. South African Users should consult SARS guidance on virtual assets and barter transactions.</p>\n<blockquote>\n<p><strong>13. Governing Law, Jurisdiction &amp; Mandatory SA Law</strong></p>\n</blockquote>\n<p><strong>13.1 Governing Law</strong></p>\n<p>This EULA is governed by and construed in accordance with the laws of the Republic of South Africa, without regard to its conflicts of law principles.</p>\n<p><strong>13.2 Mandatory SA Law Supremacy</strong></p>\n<p>The following South African Acts are mandatory public law and cannot be waived, contracted out of, or overridden by this EULA. If any provision of this EULA conflicts with these Acts, the relevant Act prevails to the extent of the conflict:</p>\n<ul>\n<li><p>Protection of Personal Information Act No. 4 of 2013 (POPIA)</p></li>\n<li><p>Consumer Protection Act No. 68 of 2008 (CPA)</p></li>\n<li><p>Electronic Communications and Transactions Act No. 25 of 2002 (ECT Act)</p></li>\n<li><p>Financial Intelligence Centre Act No. 38 of 1998 (FICA), as amended</p></li>\n<li><p>National Credit Act No. 34 of 2005 (NCA) \u2014 if and when applicable</p></li>\n<li><p>Financial Sector Regulation Act No. 9 of 2017 and subordinate FSCA regulations</p></li>\n<li><p>Constitution of the Republic of South Africa, Act 108 of 1996</p></li>\n</ul>\n<p><strong>13.3 Jurisdiction</strong></p>\n<p>You irrevocably and unconditionally consent to the non-exclusive jurisdiction of the High Court of South Africa and relevant Magistrate's Courts for the resolution of disputes not subject to arbitration under Section 10.4. For arbitrated disputes, the seat of arbitration is Cape Town, South Africa.</p>\n<p><strong>13.4 Contact</strong></p>\n<p>For legal notices and EULA-related communications: legal@trustsquare.co or [COUNSEL REQUIRED: insert postal address of registered office].</p>\n<blockquote>\n<p><strong>14. Termination &amp; Suspension</strong></p>\n</blockquote>\n<p><strong>14.1 User Termination</strong></p>\n<p>You may terminate your account at any time by submitting a written request to support@trustsquare.co. Termination takes effect immediately. Upon termination:</p>\n<ul>\n<li><p>All unused Tuppence is forfeited (non-refundable);</p></li>\n<li><p>Your active listings are removed from public display within 48 hours;</p></li>\n<li><p>Your account data is deleted or anonymised within 30 days, subject to FICA and other legal retention obligations;</p></li>\n<li><p>Buyers with open Introduction requests are notified that the Seller is no longer available. Tuppence spent on closed Introductions is consumed; no reissuance is made.</p></li>\n</ul>\n<p><strong>14.2 Immediate Termination for Breach</strong></p>\n<p>The Platform may terminate your account immediately, without notice, if you:</p>\n<ul>\n<li><p>Violate this EULA, POPIA, CPA, ECT Act, FICA, or any applicable South African law;</p></li>\n<li><p>Post fraudulent, illegal, defamatory, or harmful content;</p></li>\n<li><p>Fail to complete identity verification (Section 3.5) after acceptance of a first Introduction;</p></li>\n<li><p>Attempt to circumvent the Anonymity Gate (Section 3.3);</p></li>\n<li><p>Engage in money laundering, terrorism financing, or sanctions evasion (FICA);</p></li>\n<li><p>Claim false professional credentials;</p></li>\n<li><p>Harass, abuse, or threaten other Users or Platform staff.</p></li>\n</ul>\n<p>Upon termination for breach, all unused Tuppence is forfeited. The Platform reserves the right to recover damages arising from the breach.</p>\n<p><strong>14.3 Termination for Convenience</strong></p>\n<p>The Platform may terminate your account on 30 days' written notice to your registered email address for any reason, provided you have no active Introduction disputes or pending arbitrations. If such termination occurs, all unused Tuppence in your account is forfeited. Tuppence is not redeemable for cash or ZAR under any circumstances, including on account termination. You will be notified of the termination and forfeiture at the email address registered to your account.</p>\n<p><strong>14.4 Survival</strong></p>\n<p>The following sections survive account termination and continue in full force: Section 1 (Definitions), Section 3.6 (Regulatory Disclosure), Section 8 (User-Uploaded Content), Section 9 (Privacy and POPIA), Section 10.3\u201310.8 (Disputes and Liability), Section 13 (Governing Law), and any accrued Tuppence obligations.</p>\n<blockquote>\n<p><strong>15. Changes, Miscellaneous &amp; Contact</strong></p>\n</blockquote>\n<p><strong>15.1 Changes to These Terms</strong></p>\n<p>The Platform may update this EULA at any time. When material changes are made, you will be notified by email to your registered address and by an in-app notification at least 14 days before the changes take effect. The updated version number and effective date are displayed on this page at trustsquare.co/terms.</p>\n<p>Continued use of the Platform after the effective date constitutes acceptance of the updated EULA. If you do not accept the updated terms, you must close your account before the effective date.</p>\n<p><strong>15.2 Entire Agreement</strong></p>\n<p>This EULA, together with the Privacy Policy at trustsquare.co/privacy and any Platform policies or guidelines published at trustsquare.co/legal, constitutes the entire agreement between you and the Platform regarding your use of the Platform, and supersedes all prior agreements, representations, or understandings relating to the same subject matter.</p>\n<p><strong>15.3 Severability</strong></p>\n<p>If any provision of this EULA is found to be unlawful, void, or unenforceable, that provision shall be severed from the EULA. The remaining provisions shall continue in full force and effect.</p>\n<p><strong>15.4 Waiver</strong></p>\n<p>The Platform's failure to enforce any provision of this EULA at any time does not constitute a waiver of that provision or of the right to enforce it in the future.</p>\n<p><strong>15.5 No Agency</strong></p>\n<p>Nothing in this EULA creates a partnership, joint venture, agency, franchise, or employment relationship between you and the Platform.</p>\n<p><strong>15.6 Assignment</strong></p>\n<p>You may not assign or transfer your rights or obligations under this EULA without the Platform's prior written consent. The Platform may assign its rights and obligations to a successor entity upon written notice to you.</p>\n<p><strong>15.7 Force Majeure</strong></p>\n<p>The Platform is not liable for any failure or delay in performance caused by circumstances beyond its reasonable control, including natural disasters, load-shedding, telecommunications failures, cyberattacks, or government action, provided the Platform notifies you as soon as reasonably practicable and takes reasonable steps to resume performance.</p>\n<p><strong>15.8 Plain Language</strong></p>\n<p>This EULA is written in plain English. If you do not understand any provision, please contact support@trustsquare.co and we will provide a plain-language explanation within 5 business days. You may request a copy of this EULA and your transaction history at any time.</p>\n<p><strong>15.9 Contact</strong></p>\n<table>\n<tbody>\n<tr>\n<td><strong>Purpose</strong></td>\n<td><strong>Contact</strong></td>\n</tr>\n<tr>\n<td>General support</td>\n<td>support@trustsquare.co</td>\n</tr>\n<tr>\n<td>Legal notices / EULA</td>\n<td>legal@trustsquare.co</td>\n</tr>\n<tr>\n<td>Compliance / Trust Score queries</td>\n<td>compliance@trustsquare.co</td>\n</tr>\n<tr>\n<td>Privacy / POPIA / data requests</td>\n<td>legal@trustsquare.co</td>\n</tr>\n<tr>\n<td>South African Information Regulator</td>\n<td>inforegulator.org.za</td>\n</tr>\n<tr>\n<td>National Consumer Commission</td>\n<td>thencc.org.za</td>\n</tr>\n</tbody>\n</table>\n<p><strong>\u2014 End of TrustSquare Terms of Use / EULA v1.3 \u2014</strong></p>\n<p><em>v1.3 Draft for legal review \u2014 not for publication</em></p>\n";

function openEulaModal() {
  const overlay = document.createElement('div');
  overlay.id = 'eula-modal-overlay';
  overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:9999;display:flex;align-items:flex-end;justify-content:center;';
  const sheet = document.createElement('div');
  sheet.style.cssText = 'background:#fff;border-radius:20px 20px 0 0;width:100%;max-width:720px;max-height:88vh;display:flex;flex-direction:column;overflow:hidden;';
  const hdr = document.createElement('div');
  hdr.style.cssText = 'display:flex;align-items:center;justify-content:space-between;padding:16px 20px 13px;border-bottom:1px solid #e2e8f0;flex-shrink:0;';
  hdr.innerHTML = '<span style="font-size:15px;font-weight:800;color:#1e293b;">Terms &amp; Conditions</span><button onclick="document.getElementById(\'eula-modal-overlay\').remove()" style="background:#f1f5f9;border:none;border-radius:50%;width:30px;height:30px;font-size:14px;cursor:pointer;color:#64748b;font-weight:700;">✕</button>';
  const body = document.createElement('div');
  body.style.cssText = 'overflow-y:auto;padding:18px 20px 32px;flex:1;font-size:13px;line-height:1.75;color:#334155;';
  body.innerHTML = '<style>h1,h2,h3{color:#1e293b;margin:16px 0 6px;}h1{font-size:16px;}h2{font-size:14px;}h3{font-size:13px;}p{margin:4px 0;}table{width:100%;border-collapse:collapse;margin:8px 0;}td,th{border:1px solid #e2e8f0;padding:6px 8px;font-size:12px;vertical-align:top;}strong{color:#1e293b;}</style>' + _EULA_HTML;
  sheet.appendChild(hdr);
  sheet.appendChild(body);
  overlay.appendChild(sheet);
  overlay.addEventListener('click', function(e){ if(e.target===overlay) overlay.remove(); });
  document.body.appendChild(overlay);
}


function msRenderTrust(score){
  const sv = document.getElementById('ms-trust-score-val');
  if(sv) sv.textContent = score;
  const bar = document.getElementById('ms-trust-bar');
  if(bar) bar.style.width = score+'%';
  const barPct = document.getElementById('ms-trust-bar-pct');
  if(barPct) barPct.textContent = score+'%';

  let standing = 'Getting started', colour = '#854f0b';
  if(score >= 80){ standing='Excellent'; colour='#0f6e56'; }
  else if(score >= 60){ standing='Good standing'; colour='#3b6d11'; }
  else if(score >= 40){ standing='Building trust'; colour='#854f0b'; }

  const st = document.getElementById('ms-trust-standing');
  if(st){ st.textContent = standing; st.style.color = colour; }

  // Approximate percentile (rough heuristic)
  const pct = Math.max(5, 100 - score);
  const tp = document.getElementById('ms-trust-pct');
  if(tp) tp.textContent = 'Top '+pct+'% of members';
}

function msRenderLiveSignals(signals){
  const el = document.getElementById('ms-trust-signals');
  if(!el) return;

  // Inject hidden file input for ID upload (once)
  if(!document.getElementById('ms-id-upload-input')){
    const inp = document.createElement('input');
    inp.type='file'; inp.id='ms-id-upload-input';
    inp.accept='image/jpeg,image/png,image/webp';
    inp.style.display='none';
    inp.addEventListener('change', msUploadIdDoc);
    document.body.appendChild(inp);
  }

  el.innerHTML = signals.map(sig => {
    const earned = sig.earned;
    const iconClass = earned ? 'ms-sig-done' : 'ms-sig-miss';
    const icon = earned ? '✓' : '✗';
    const ptsClass = earned ? 'ms-pts-earned' : 'ms-pts-avail';
    const ptsLabel = earned ? '+'+sig.points : '+'+sig.points+' available';

    // Action button for actionable unearned signals
    let actionBtn = '';
    if(!earned){
      if(sig.key === 'id_verified'){
        actionBtn = '<button class="ms-sig-action" data-action="upload-id">Upload ID →</button>';
      }
    }

    return '<div class="ms-signal-row">'
      +'<div class="ms-sig-icon '+iconClass+'">'+icon+'</div>'
      +'<div class="ms-signal-text" title="'+sig.how_to_earn+'">'+sig.name+'</div>'
      +'<div style="display:flex;align-items:center;gap:8px;flex-shrink:0;">'
      +actionBtn
      +'<span class="ms-signal-pts '+ptsClass+'">'+ptsLabel+'</span>'
      +'</div>'
      +'</div>';
  }).join('');

  // Event delegation — one listener per render (replaces any previous)
  el.onclick = function(e){
    const btn = e.target.closest('[data-action]');
    if(!btn) return;
    if(btn.dataset.action === 'upload-id'){
      document.getElementById('ms-id-upload-input').click();
    }
  };
}

async function msUploadIdDoc(e){
  const file = e.target.files && e.target.files[0];
  if(!file) return;
  const email = localStorage.getItem('ms_user_email') || localStorage.getItem('ms_aa_email') || '';
  if(!email){ showToast('Sign in first to upload your ID'); return; }

  // Show uploading state on the button
  const btn = document.querySelector('.ms-sig-action');
  if(btn){ btn.textContent = '⏳ Uploading…'; btn.disabled = true; }

  try {
    const fd = new FormData();
    fd.append('file', file);
    const r = await fetch(BEA_URL+'/users/'+encodeURIComponent(email)+'/upload-id', {
      method: 'POST', body: fd
    });
    const data = await r.json();
    if(!r.ok) throw new Error(data.detail || 'Upload failed');

    if(data.already_verified){
      showToast('Your ID is already verified ✓');
    } else {
      // Update cached trust score and re-render
      localStorage.setItem('ms_trust_score', data.trust_score);
      msRenderTrust(data.trust_score);
      showToast('ID uploaded — Trust Score +'+ data.points_awarded +' pts 🎉');
      // Refresh full trust breakdown from BEA so signals list updates
      setTimeout(()=>{
        fetch(BEA_URL+'/users/'+encodeURIComponent(email)+'/trust')
          .then(r=>r.ok?r.json():null)
          .then(td=>{
            if(!td) return;
            localStorage.setItem('ms_trust_score', td.score||data.trust_score);
            msRenderTrust(parseInt(td.score)||data.trust_score);
            if(td.signals && td.signals.length) msRenderLiveSignals(td.signals);
          }).catch(()=>{});
        // Refresh live listings so trust score on listing detail cards is current
        if(typeof loadLiveListings === 'function') loadLiveListings(0);
      }, 800);
    }
  } catch(err){
    showToast('Upload failed — ' + (err.message || 'please try again'));
    if(btn){ btn.textContent = 'Upload ID →'; btn.disabled = false; }
  }
  // Reset input so same file can be re-selected if needed
  e.target.value = '';
}

function msUpdateStats(walBal, trust){
  const recv = document.getElementById('ms-stat-recv');
  const sent = document.getElementById('ms-stat-sent');
  const tst  = document.getElementById('ms-stat-trust');
  const wish = document.getElementById('ms-stat-wish');
  const saved = JSON.parse(localStorage.getItem('ms_saved') || '[]');
  if(recv) recv.textContent = parseInt(localStorage.getItem('ms_intros_recv')||'0');
  if(sent) sent.textContent = parseInt(localStorage.getItem('ms_intros_sent')||'0');
  if(tst)  tst.textContent  = trust+'%';
  if(wish) wish.textContent = saved.length;
}

async function msLoadIntros(email){
  if(!email || !BEA_ENABLED){ msRenderIntrosFallback(); return; }
  try {
    // Fetch intros where this buyer is the buyer (sent by them)
    const res = await fetch(BEA_URL+'/intros?status=all&buyer_email='+encodeURIComponent(email));
    if(!res.ok){ msRenderIntrosFallback(); return; }
    const data = await res.json();
    const all = Array.isArray(data) ? data : (data.items || []);

    const sent = all; // BEA already filtered by buyer_email
    const recv = []; // received = intros on MY listings — we\'ll leave as placeholder for now

    localStorage.setItem('ms_intros_sent', sent.length);
    msRenderIntroList('ms-intros-sent', sent, 'sent');
    msRenderIntroList('ms-intros-recv', recv, 'received');
    msRenderOpenActions(sent.concat(recv));
    msUpdateStats(0, parseInt(localStorage.getItem('ms_trust_score')||'15'));
  } catch(e){ msRenderIntrosFallback(); }
}

function msRenderIntrosFallback(){
  // Show empty state gracefully
  const recvEl = document.getElementById('ms-intros-recv');
  if(recvEl) recvEl.innerHTML = '<div class="ms-empty">Intros will appear here once you request one</div>';
  const sentEl = document.getElementById('ms-intros-sent');
  if(sentEl) sentEl.innerHTML = '<div class="ms-empty">Intros you send will appear here</div>';
  const oaEl = document.getElementById('ms-open-actions');
  if(oaEl) oaEl.innerHTML = '<div class="ms-empty">No pending actions</div>';
}

const MS_COLORS = ['ms-ia-green','ms-ia-blue','ms-ia-amber','ms-ia-coral'];
function msColorFor(str){ let h=0; for(let i=0;i<(str||'').length;i++) h=(h*31+str.charCodeAt(i))&0xffff; return MS_COLORS[h % MS_COLORS.length]; }
function msInitials(email){ const n=(email||'').split('@')[0]; return n.slice(0,2).toUpperCase(); }

function msRenderIntroList(elId, items, dir){
  const el = document.getElementById(elId);
  if(!el) return;
  if(!items || !items.length){
    el.innerHTML = '<div class="ms-empty">'+(dir==='sent'?'No intros sent yet':'No intros received yet')+'</div>';
    return;
  }
  el.innerHTML = items.slice(0,8).map(i => {
    const statusMap = {pending:'<span class="ms-chip ms-chip-pending">Pending</span>',
                       accepted:'<span class="ms-chip ms-chip-done">Accepted</span>',
                       declined:'<span class="ms-chip ms-chip-declined">Declined</span>',
                       new:'<span class="ms-chip ms-chip-new">New</span>'};
    const chip = statusMap[i.status||'pending'] || statusMap['pending'];
    const ident = dir==='sent' ? (i.seller_email||i.listing_id||'Seller') : (i.buyer_email||'Buyer');
    const initials = msInitials(ident);
    const colour = msColorFor(ident);
    const meta = 'Listing #'+(i.listing_id||'–')+' · '+(i.created_at ? new Date(i.created_at).toLocaleDateString('en-ZA',{day:'numeric',month:'short'}) : '–');
    return '<div class="ms-intro-item">'
      +'<div class="ms-intro-avatar '+colour+'">'+initials+'</div>'
      +'<div style="flex:1;min-width:0;"><div class="ms-intro-name" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'+ident+'</div>'
      +'<div class="ms-intro-meta">'+meta+'</div></div>'
      +chip+'</div>';
  }).join('');
}

function msRenderOpenActions(items){
  const el = document.getElementById('ms-open-actions');
  if(!el) return;
  const pending = (items||[]).filter(i => i.status==='pending');
  if(!pending.length){ el.innerHTML = '<div class="ms-empty">No pending actions \u2014 all clear!</div>'; return; }
  el.innerHTML = pending.slice(0,3).map(i => {
    const ident = i.buyer_email || i.seller_email || 'Member';
    const colour = msColorFor(ident);
    const initials = msInitials(ident);
    return '<div class="ms-intro-item">'
      +'<div class="ms-intro-avatar '+colour+'">'+initials+'</div>'
      +'<div style="flex:1;min-width:0;"><div class="ms-intro-name">Intro pending</div>'
      +'<div class="ms-intro-meta">Listing #'+i.listing_id+'</div></div>'
      +'<div class="ms-action-btns">'
      +'<button class="ms-btn-sm" onclick="msIntroAction('+i.id+',0)">Decline</button>'
      +'<button class="ms-btn-sm primary" onclick="msIntroAction('+i.id+',1)">Accept</button>'
      +'</div></div>';
  }).join('');
}

function msIntroAction(introId, accept){
  showToast(accept ? 'Accepted!' : 'Declined');
}

function msRenderWishlist(){
  const el = document.getElementById('ms-wishlist-cards');
  if(!el) return;
  let saved = [];
  try { saved = JSON.parse(localStorage.getItem('ms_saved') || '[]'); } catch(e){}
  if(!saved.length){ el.innerHTML = '<div class="ms-empty">No saved listings — tap ♥ on any card</div>'; return; }
  // Find listing objects from LISTINGS array
  const all = (typeof LISTINGS !== 'undefined') ? LISTINGS : [];
  const items = saved.map(id => all.find(l=>l.id===id||l.id==='bea_'+id)).filter(Boolean);
  if(!items.length){ el.innerHTML = '<div class="ms-empty">Saved listings will appear here</div>'; return; }
  el.innerHTML = items.slice(0,5).map(l => {
    const icon = l.cat==='Adventures'?'🌄':l.cat==='Property'?'🏠':l.cat==='Tutors'?'📚':l.cat==='Services'?'🔧':'🛍';
    const thumb = l.photo ? '<img src="'+l.photo+'" alt="" style="width:100%;height:100%;object-fit:cover;border-radius:9px;">' : icon;
    return '<div class="ms-hist-item" onclick="openDetail(this.dataset.lid)" data-lid="'+l.id+'">'
      +'<div class="ms-hist-thumb">'+thumb+'</div>'
      +'<div style="flex:1;min-width:0;"><div class="ms-hist-title" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'+(l.title||'–')+'</div>'
      +'<div class="ms-hist-meta">'+(l.cat||'')+(l.price?' · '+l.price:'')+'</div></div>'
      +'<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24" width="16" height="16" style="color:var(--text-3);flex-shrink:0;"><polyline points="9 18 15 12 9 6"/></svg>'
      +'</div>';
  }).join('');
}

// Track a listing view in browse history (call from openDetail)
// ── HOME WONDERS STRIP ───────────────────────────────────────────────────────
let _wpWondersLoading = false;
async function loadHomeWonders() {
  const section = document.getElementById('home-wonders-section');
  const list    = document.getElementById('home-wonders-list');
  if(!section||!list) return;
  // Render instantly from bundled data — no network wait
  section.style.display = 'block';
  renderWondersStrip();
  // Background refresh: silently update from BEA after render (every page load)
  if(!_wpWondersLoading) {
    _wpWondersLoading = true;
    setTimeout(async () => {
      try {
        const r = await fetch(BEA_URL+'/wonders');
        const d = await r.json();
        if(d.wonders && d.wonders.length > 0 && d.wonders.length !== _wpAllWonders.length) {
          _wpAllWonders = d.wonders;
          renderWondersStrip();
        }
      } catch(e) { /* silent — bundled data already showing */ }
      _wpWondersLoading = false;
    }, 3000);
  }
}

// ── WONDER DETAIL (BUYER) ─────────────────────────────────────────────────────
let _wdReturnListingId = null;


async function loadDetailPois(listing) {
  const strip = document.getElementById('detail-poi-strip');
  const tabsEl = document.getElementById('poi-tabs');
  const cardsEl = document.getElementById('poi-cards');
  if (!strip || !tabsEl || !cardsEl) return;
  strip.style.display = 'none';
  tabsEl.innerHTML = ''; cardsEl.innerHTML = '';

  // Only show for Property listings
  if ((listing.cat || listing.category || '').toLowerCase() !== 'property') return;

  // Get POI data — from listing object (demo) or from BEA fetch
  let pois = null;
  if (listing.nearby_pois) {
    try { pois = typeof listing.nearby_pois === 'string' ? JSON.parse(listing.nearby_pois) : listing.nearby_pois; } catch(e) {}
  }
  if (!pois && listing.beaListingId) {
    try {
      const beaId = listing.beaListingId.toString().replace('bea_','');
      const r = await fetch(BEA_URL + '/listings/' + beaId);
      const d = await r.json();
      if (d.nearby_pois) {
        pois = typeof d.nearby_pois === 'string' ? JSON.parse(d.nearby_pois) : d.nearby_pois;
      }
    } catch(e) {}
  }
  if (!pois || !Object.keys(pois).length) return;

  const POI_META = {
    schools:      { label: 'Schools',      icon: '🎓', cls: 'poi-icon-schools' },
    universities: { label: 'Universities', icon: '🏛️', cls: 'poi-icon-universities' },
    shopping:     { label: 'Shopping',     icon: '🛍️', cls: 'poi-icon-shopping' },
    hospitals:    { label: 'Hospitals',    icon: '🏥', cls: 'poi-icon-hospitals' },
    police:       { label: 'Police',       icon: '👮', cls: 'poi-icon-police' },
    transit:      { label: 'Transit',      icon: '🚇', cls: 'poi-icon-transit' },
    transport:    { label: 'Transport',    icon: '🚌', cls: 'poi-icon-transit' },
    recreation:   { label: 'Recreation',   icon: '🌳', cls: 'poi-icon-recreation' },
  };

  const cats = Object.keys(pois).filter(k => pois[k] && pois[k].length);
  if (!cats.length) return;

  let activeTab = cats[0];

  function renderCards(cat) {
    const meta = POI_META[cat] || { label: cat, icon: '📍', cls: '' };
    cardsEl.innerHTML = (pois[cat] || []).map(p => `
      <div class="poi-card">
        <div class="poi-icon ${meta.cls}">${meta.icon}</div>
        <div class="poi-info">
          <div class="poi-name">${p.name}</div>
          ${p.type ? `<div class="poi-type">${p.type}</div>` : ''}
          <div class="poi-dist">${p.dist_km} km straight-line</div>
        </div>
      </div>`).join('');
  }

  function renderTabs() {
    tabsEl.innerHTML = cats.map(cat => {
      const meta = POI_META[cat] || { label: cat };
      return `<button class="poi-tab${cat===activeTab?' active':''}" onclick="poiTabClick('${cat}')">${meta.label}</button>`;
    }).join('');
  }

  window.poiTabClick = function(cat) {
    activeTab = cat;
    renderTabs();
    renderCards(cat);
  };

  renderTabs();
  renderCards(activeTab);
  // Add demo disclaimer to header when showing demo data
  const poiHdr = document.getElementById('poi-section-hdr');
  if (poiHdr) {
    if (listing && String(listing.id).startsWith('demo_')) {
      poiHdr.innerHTML = 'Nearby Amenities <span style="font-size:10px;font-weight:500;color:var(--accent);opacity:.8;">(demo data — approximate)</span>';
    } else {
      poiHdr.innerHTML = 'Nearby Amenities';
    }
  }
  strip.style.display = '';
}

async function loadDetailWonders(listing) {
  const strip = document.getElementById('detail-wonders-strip');
  const list  = document.getElementById('detail-wonders-list');
  if(!strip||!list) return;
  strip.style.display = 'none';
  list.innerHTML = '';
  const beaId = listing.beaListingId || (typeof listing.id==='string' && listing.id.startsWith('bea_') ? listing.id.replace('bea_','') : null);
  // Demo listings: read linked_wonders directly from the listing object
  if(!beaId) {
    const raw = listing.linked_wonders;
    if(!raw) return;
    // Ensure wonders are loaded (lazy — may not be loaded if user opens detail before home tab)
    if(!_wpAllWonders || !_wpAllWonders.length) {
      try {
        const rw = await fetch(BEA_URL+'/wonders');
        const dw = await rw.json();
        _wpAllWonders = dw.wonders||[];
      } catch(e){ return; }
    }
    if(!_wpAllWonders.length) return;
    const linked = Array.isArray(raw) ? raw : (()=>{try{return JSON.parse(raw);}catch(e){return [];}})();
    if(!linked.length) return;
    const tc = t=>t==='National Park'?'wd-type-np':t==='UNESCO Site'?'wd-type-un':t==='National Museum'?'wd-type-nm':'wd-type-ar';
    const cards = linked.map(lw=>{
      // linked_wonders entries may be plain ID strings or objects with .id
      const wId = typeof lw === 'string' ? lw : lw.id;
      const w = _wpAllWonders.find(x=>x.id===wId);
      if(!w) return '';
      return `<div class="wonder-card" onclick="openWonderDetail('${w.id}','${listing.id}')">
        <img class="wonder-card-img" src="${w.photo}" alt="${w.name}" loading="lazy" referrerpolicy="origin-when-cross-origin">
        <div class="wonder-card-body">
          <div class="wonder-card-type ${tc(w.type)}">${w.type}</div>
          <div class="wonder-card-name">${w.name}</div>
          <div class="wonder-card-country">${w.country}</div>
        </div>
      </div>`;
    }).join('');
    if(cards) { list.innerHTML = cards; strip.style.display = ''; requestAnimationFrame(()=>ensureScrollArrows(list)); }
    return;
  }
  try {
    const r = await fetch(BEA_URL+'/listings/'+beaId+'/wonders');
    const d = await r.json();
    const wonders = d.wonders||[];
    if(!wonders.length) return;
    const tc = t=>t==='National Park'?'wd-type-np':t==='UNESCO Site'?'wd-type-un':t==='National Museum'?'wd-type-nm':'wd-type-ar';
    list.innerHTML = wonders.map(w=>`
      <div class="wonder-card" onclick="openWonderDetail('${w.id}','${listing.id}')">
        <img class="wonder-card-img" src="${w.photo}" loading="lazy" referrerpolicy="origin-when-cross-origin" onerror="this.src=''">
        <div class="wonder-card-body">
          <div class="wonder-card-type ${tc(w.type)}">${w.type}</div>
          <div class="wonder-card-name">${w.name}</div>
          <div class="wonder-card-country">${w.country}</div>
        </div>
      </div>`).join('');
    strip.style.display = 'block';
    requestAnimationFrame(()=>ensureScrollArrows(list));
  } catch(e) { console.warn('loadDetailWonders failed', e); }
}

async function openWonderDetail(wonderId, returnListingId) {
  _wdReturnListingId = returnListingId || null;
  let wonder = (_wpAllWonders||[]).find(w=>w.id===wonderId);
  if(!wonder) {
    try { const r = await fetch(BEA_URL+'/wonders/'+wonderId); wonder = await r.json(); } catch(e){ return; }
  }
  const tc = t=>t==='National Park'?'wd-type-np':t==='UNESCO Site'?'wd-type-un':t==='National Museum'?'wd-type-nm':'wd-type-ar';
  const hero = document.getElementById('wd-hero-img'); if(hero) hero.src = wonder.photo||'';
  const badge = document.getElementById('wd-type-badge'); if(badge){badge.textContent=wonder.type||'';badge.className='wd-type-badge '+tc(wonder.type||'');}
  const title = document.getElementById('wd-title'); if(title) title.textContent = wonder.name||'';
  const country = document.getElementById('wd-country'); if(country) country.textContent = (wonder.country||'')+(wonder.region?` · ${wonder.region}`:'');
  const desc = document.getElementById('wd-desc'); if(desc) desc.textContent = wonder.description||'';
  const hist = document.getElementById('wd-history'); if(hist) hist.textContent = wonder.history||'';
  const wiki = document.getElementById('wd-wiki-btn'); if(wiki) wiki.href = wonder.wikipedia||'#';
  // Photo credit overlay
  const creditEl = document.getElementById('wd-photo-credit');
  if(creditEl) {
    const author = wonder.photo_author || '';
    const licence = wonder.photo_licence || '';
    const source = wonder.photo_source || '';
    if(author || licence) {
      document.getElementById('wd-credit-author').textContent = author || 'Wikimedia Commons';
      document.getElementById('wd-credit-licence').textContent = licence || 'View source';
      document.getElementById('wd-credit-link').href = source || 'https://commons.wikimedia.org';
      creditEl.style.display = 'flex';
    } else {
      creditEl.style.display = 'none';
    }
  }
  goTo('wonder-detail');
}

function closeWonderDetail() {
  if(_wdReturnListingId) { openDetail(_wdReturnListingId); }
  else { goTo('home'); }
}

function msTrackView(listing){
  if(!listing || !listing.id) return;
  try {
    let hist = JSON.parse(localStorage.getItem(MS_HISTORY_KEY)||'[]');
    hist = hist.filter(h => h.id !== listing.id);
    hist.unshift({ id:listing.id, title:listing.title, cat:listing.cat, price:listing.price, photo:listing.photo||null, ts: Date.now() });
    if(hist.length > MS_HISTORY_MAX) hist = hist.slice(0, MS_HISTORY_MAX);
    localStorage.setItem(MS_HISTORY_KEY, JSON.stringify(hist));
  } catch(e){}
}

function msRenderHistory(){
  const el = document.getElementById('ms-history-list');
  if(!el) return;
  let hist = [];
  try { hist = JSON.parse(localStorage.getItem(MS_HISTORY_KEY)||'[]'); } catch(e){}
  if(!hist.length){ el.innerHTML = '<div class="ms-empty">Listings you view will appear here</div>'; return; }
  el.innerHTML = hist.slice(0,8).map(h => {
    const icon = h.cat==='Adventures'?'🌄':h.cat==='Property'?'🏠':h.cat==='Tutors'?'📚':h.cat==='Services'?'🔧':'🛍';
    const thumb = h.photo ? '<img src="'+h.photo+'" alt="">' : icon;
    const ago = msTimeAgo(h.ts);
    return '<div class="ms-hist-item" onclick="openDetail(this.dataset.lid)" data-lid="'+h.id+'">'
      +'<div class="ms-hist-thumb">'+thumb+'</div>'
      +'<div style="flex:1;min-width:0;"><div class="ms-hist-title" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'+(h.title||'–')+'</div>'
      +'<div class="ms-hist-meta">'+(h.cat||'')+' · '+ago+'</div></div>'
      +'<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24" width="16" height="16" style="color:var(--text-3);flex-shrink:0;"><polyline points="9 18 15 12 9 6"/></svg>'
      +'</div>';
  }).join('');
}

function msTimeAgo(ts){
  const diff = Date.now() - ts;
  const m = Math.floor(diff/60000);
  if(m < 2) return 'just now';
  if(m < 60) return m+' min ago';
  const h = Math.floor(m/60);
  if(h < 24) return h+' hr ago';
  const d = Math.floor(h/24);
  if(d < 7) return d+' day'+(d>1?'s':'')+' ago';
  return new Date(ts).toLocaleDateString('en-ZA',{day:'numeric',month:'short'});
}

function msEditField(field){
  if(field==='name'){
    const current = localStorage.getItem('ms_user_name') || '';
    const val = prompt('Enter your display name:', current);
    if(val === null) return;
    const trimmed = val.trim();
    if(!trimmed){ showToast('Name cannot be empty'); return; }
    localStorage.setItem('ms_user_name', trimmed);
    const pdName = document.getElementById('ms-pd-name');
    if(pdName) pdName.textContent = trimmed;
    const msName = document.getElementById('ms-display-name');
    if(msName) msName.textContent = trimmed;
    // Update initials
    const initials = trimmed.split(' ').filter(Boolean).slice(0,2).map(w=>w[0].toUpperCase()).join('');
    const av = document.getElementById('ms-avatar-initials');
    if(av) av.textContent = initials;
    showToast('Name updated');
  }
}

async function msAskAI(){
  const email = localStorage.getItem('ms_aa_email') || localStorage.getItem('ms_user_email') || '';
  if (!email) { showToast('Sign in first to use AI coach'); return; }

  const btn = document.getElementById('tn-trust-coach-btn');
  const resultEl = document.getElementById('tn-trust-coach-result');
  if (btn) { btn.disabled = true; btn.textContent = '✨ Thinking…'; }
  if (resultEl) resultEl.style.display = 'none';

  // Derive category from first live listing if available
  const catForCoach = (function(){
    const live = (typeof LISTINGS !== 'undefined' ? LISTINGS : []).filter(l => l.isLive);
    return live.length ? (live[0].cat || 'General') : 'General';
  })();

  try {
    const res = await fetch(BEA_URL + '/trust-score/guidance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, category: catForCoach })
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();

    const stepsHtml = (data.steps || []).map(s =>
      `<div style="display:flex;gap:10px;padding:8px 0;border-bottom:1px solid rgba(0,0,0,.06);">
        <div style="flex-shrink:0;background:#d1fae5;color:#065f46;font-size:11px;font-weight:700;border-radius:20px;padding:3px 8px;align-self:flex-start;white-space:nowrap;">+${s.points} pts</div>
        <div><div style="font-size:13px;font-weight:600;">${s.action}</div>
        <div style="font-size:12px;color:#6b7280;margin-top:2px;">${s.why||''}</div></div>
      </div>`
    ).join('');

    if (resultEl) {
      resultEl.innerHTML = `
        <div style="background:#f0fdf4;border:1.5px solid #bbf7d0;border-radius:10px;padding:14px 16px;margin-top:12px;">
          <div style="font-size:13px;color:#15803d;margin-bottom:10px;">${data.intro||''}</div>
          ${stepsHtml}
          <div style="font-size:12px;color:#16a34a;font-weight:600;margin-top:10px;">${data.closing||''}</div>
        </div>`;
      resultEl.style.display = 'block';
    }
    if (btn) { btn.disabled = false; btn.textContent = '✨ Ask AI how to improve my score →'; }
  } catch(e) {
    showToast('AI coach unavailable — try again');
    if (btn) { btn.disabled = false; btn.textContent = '✨ Ask AI how to improve my score →'; }
  }
}

// ── Category Home Mode — Session 87 ─────────────────────────────────────────
// Long-press a category tile (500ms) → that category becomes the user's
// personalised home screen (persisted in localStorage).
// On startup, if a preference is set, goTo('cat-home') instead of 'home'.

const CAT_HOME_KEY  = 'ms_cat_home_pref';   // stored cat name e.g. 'Property'
const CAT_HOME_HINT = 'ms_cathome_hint_shown'; // '1' once shown

const CAT_DESCS = {
  Property:    'Browse houses, apartments, land and commercial property. Connect anonymously with serious sellers in your area.',
  Tutors:      'Find qualified tutors for any subject or age group. All trust-verified, intro-only connections.',
  Services:    'Plumbers, electricers, cleaners and more. Trusted local service providers available right now.',
  Adventures:  'Experiences and accommodation for the explorer in you. Local adventures, curated and trusted.',
  Collectors:  'Rare finds, vintage items, trading cards and collectibles. Trusted sellers, verified stock.',
  Cars:        'Buy or sell vehicles with confidence. Verified sellers, transparent listings, no spam.',
  LocalMarket: 'Your neighbourhood marketplace. Fresh produce, handmade goods and local deals delivered with trust.',
};

function catHomeInit() {
  // Attach long-press listeners to all .cat-tile elements
  document.querySelectorAll('.cat-tile').forEach(tile => {
    let pressTimer = null;

    let longPressFired = false;

    const start = (e) => {
      longPressFired = false;
      pressTimer = setTimeout(() => {
        pressTimer = null;
        longPressFired = true;
        // Determine category from onclick attribute
        const cat = _catFromTile(tile);
        if (!cat) return;
        setCatHome(cat);
      }, 500);
    };

    const cancel = () => {
      if (pressTimer) { clearTimeout(pressTimer); pressTimer = null; }
    };

    // Prevent normal click firing after a successful long-press
    tile.addEventListener('click', (e) => {
      if (longPressFired) { e.stopImmediatePropagation(); e.preventDefault(); longPressFired = false; }
    }, true);

    tile.addEventListener('touchstart', start, { passive: true });
    tile.addEventListener('touchend', cancel);
    tile.addEventListener('touchmove', cancel);
    tile.addEventListener('mousedown', start);
    tile.addEventListener('mouseup', cancel);
    tile.addEventListener('mouseleave', cancel);
  });

  // On startup: redirect to cat-home if preference set
  const pref = localStorage.getItem(CAT_HOME_KEY);
  if (pref) {
    // Delay slightly so app finishes initialising
    setTimeout(() => openCatHome(pref, true), 120);
  }

  // Show one-time hint if never seen and user has no preference yet
  if (!localStorage.getItem(CAT_HOME_HINT) && !localStorage.getItem(CAT_HOME_KEY)) {
    setTimeout(showCatHomeHint, 2000);
  }

  // Mark star on cat tile if preference already set
  _updateCatStars();
}

function _catFromTile(tile) {
  // Check onclick attr first
  const oc = tile.getAttribute('onclick') || '';
  const m = oc.match(/filterBrowse\('([^']+)'\)/);
  if (m) return m[1];
  // LM tile
  if (tile.id === 'lm-home-tile') return 'LocalMarket';
  return null;
}

function setCatHome(cat) {
  try { localStorage.setItem(CAT_HOME_KEY, cat); } catch(_) {}
  showToast(`${CATS[cat]?.icon || ''} ${cat === 'LocalMarket' ? 'Local Market' : cat} set as your home screen`);
  _updateCatStars();
  openCatHome(cat, false);
}

function clearCatHome() {
  try { localStorage.removeItem(CAT_HOME_KEY); } catch(_) {}
  _updateCatStars();
  showToast('Home screen reset to default');
  goTo('home');
}

function openCatHome(cat, isAuto) {
  const cfg = CATS[cat];
  if (!cfg) return;

  // Populate hero image
  const img = document.getElementById('cat-home-img');
  if (img) { img.src = cfg.catPhoto || ''; img.alt = cat; }

  // Hero overlay content
  const iconEl = document.getElementById('cat-home-icon');
  const titleEl = document.getElementById('cat-home-title');
  const cityEl  = document.getElementById('cat-home-city');
  const statsEl = document.getElementById('cat-home-stats');
  const descEl  = document.getElementById('cat-home-desc');
  const ctaEl   = document.getElementById('cat-home-cta');

  if (iconEl)  iconEl.textContent  = cfg.icon;
  if (titleEl) titleEl.textContent = cat === 'LocalMarket' ? 'Local Market' : cat;
  if (cityEl)  cityEl.textContent  = '📍 ' + (activeCity?.name || 'Your city');

  // Stats: count live/demo listings in this category
  const catKey = cat === 'LocalMarket' ? 'LocalMarket' : cat;
  const count = LISTINGS.filter(l => {
    if (l.placeholder) return false;
    const lcat = l.cat || '';
    if (catKey === 'LocalMarket') return lcat === 'LocalMarket' || lcat === 'local_market' || lcat === 'LocalMarket';
    return lcat === catKey;
  }).length;

  const priceArr = LISTINGS.filter(l => {
    if (l.placeholder) return false;
    const lcat = l.cat || '';
    if (catKey === 'LocalMarket') return lcat === 'LocalMarket' || lcat === 'local_market';
    return lcat === catKey;
  }).map(l => l.price).filter(p => p > 0);

  let statsText = count > 0 ? `${count} listing${count!==1?'s':''} available` : 'Be the first to list';
  if (priceArr.length > 0) {
    const minP = Math.min(...priceArr);
    const maxP = Math.max(...priceArr);
    const fmt = v => v >= 1000 ? 'R' + (v/1000).toFixed(0) + 'k' : 'R' + v;
    statsText += minP === maxP ? ` · from ${fmt(minP)}` : ` · ${fmt(minP)}–${fmt(maxP)}`;
  }
  if (statsEl) statsEl.textContent = statsText;
  if (descEl)  descEl.textContent  = CAT_DESCS[cat] || '';

  // CTA button
  if (ctaEl) {
    const label = cat === 'LocalMarket' ? 'Browse Local Market →' : `Browse ${cat} →`;
    ctaEl.textContent = label;
    ctaEl.onclick = () => {
      if (cat === 'LocalMarket') goTo('local-market');
      else filterBrowse(cat);
    };
  }

  // Set hero bg tint for the fallback state (image loading)
  const heroEl = document.getElementById('cat-home-hero');
  if (heroEl) heroEl.style.background = cfg.bg;

  goTo('cat-home');
}

function showCatHomeHint() {
  if (localStorage.getItem(CAT_HOME_HINT)) return;
  try { localStorage.setItem(CAT_HOME_HINT, '1'); } catch(_) {}
  const hint = document.createElement('div');
  hint.className = 'cat-home-hint';
  hint.textContent = '💡 Long-press any category to set it as your home screen';
  document.body.appendChild(hint);
  setTimeout(() => hint.remove(), 3800);
}

function _updateCatStars() {
  const pref = localStorage.getItem(CAT_HOME_KEY);
  // Remove all existing stars
  document.querySelectorAll('.cat-tile .cat-home-star').forEach(s => s.remove());
  if (!pref) return;
  // Find the matching tile and add star
  document.querySelectorAll('.cat-tile').forEach(tile => {
    const cat = _catFromTile(tile);
    if (cat === pref) {
      const star = document.createElement('span');
      star.className = 'cat-home-star';
      star.textContent = '⭐';
      tile.appendChild(star);
    }
  });
}
// ── END Category Home Mode ───────────────────────────────────────────────────
