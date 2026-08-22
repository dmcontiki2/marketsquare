// DEMO-BANNER-1 self-test (RUL-040). Run: node scripts/demo_banner_selftest.js  (from the repo root)
// Minimal DOM shim: prove ts_demo_banner.js actually mounts and places the tab,
// with and without the REPORT tab present. EXECUTED-grade evidence, no jsdom.
function mkEl(tag){
  return { tagName:tag.toUpperCase(), id:'', title:'', style:{cssText:'',top:'',transform:''},
    children:[], innerHTML:'', textContent:'', offsetHeight:88, parentNode:null,
    setAttribute(){}, appendChild(c){c.parentNode=this;this.children.push(c);return c},
    removeChild(c){this.children=this.children.filter(x=>x!==c);c.parentNode=null},
    getBoundingClientRect(){ return {top:344, bottom:456, height:112}; } };
}
const body = mkEl('body');
global.document = {
  readyState:'complete', body,
  createElement:mkEl,
  getElementById(id){ return body.children.find(c=>c.id===id) || (id==='ts-report-tab'?global.__report:null) || null; },
  addEventListener(){}, removeEventListener(){}
};
global.window = { innerHeight:900, innerWidth:400, addEventListener(){}, };
global.MutationObserver = function(){ return {observe(){}}; };
global.setInterval = () => 0; global.clearInterval = () => {}; global.setTimeout = () => 0;
global.localStorage = { getItem:()=>null, setItem(){}, removeItem(){} };

// case 1: REPORT tab present (pre-launch)
global.__report = { id:'ts-report-tab', getBoundingClientRect:()=>({top:344,bottom:456,height:112}) };
const src = require('fs').readFileSync('ts_demo_banner.js','utf8');
const run = new Function('window','document','MutationObserver','setInterval','clearInterval','setTimeout','localStorage', src);
run(global.window, global.document, global.MutationObserver, global.setInterval, global.clearInterval, global.setTimeout, global.localStorage);
let tab = body.children.find(c=>c.id==='ts-demo-tab');
if(!tab) throw new Error('FAIL: DEMO tab not mounted');
if(!/background:#e63946/.test(tab.style.cssText)) throw new Error('FAIL: tab not red');
if(tab.innerHTML!=='DEMO') throw new Error('FAIL: label is '+tab.innerHTML);
const withReport = tab.style.top;
console.log('with REPORT (bottom 456, gap 10, h/2 44) -> top =', withReport, '(expect 510px)');
if(withReport!=='510px') throw new Error('FAIL: unexpected placement '+withReport);

// case 2: REPORT removed (soft launch) -- must re-centre
global.__report = null;
global.window.tsDemoBannerPlace();
console.log('without REPORT (viewport 900) -> top =', tab.style.top, '(expect 450px, dead centre)');
if(tab.style.top!=='450px') throw new Error('FAIL: did not re-centre, got '+tab.style.top);
console.log('PASS: mounts red, labelled DEMO, steps below REPORT, re-centres when REPORT goes');
