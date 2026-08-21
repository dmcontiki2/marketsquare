/* ID-NPR-5 UI guards (RUL-039). Node, no browser needed.
   Asserts the PROPERTIES that must not rot, not the wording. */
const fs = require('fs');
const js  = fs.readFileSync('ms.js', 'utf8');
const css = fs.readFileSync('ms.css', 'utf8');
let fail = 0;
const ok  = m => console.log('  PASS  ' + m);
const bad = m => { console.log('  FAIL  ' + m); fail++; };

// 1 ── the warning must never be able to stop a buyer
const g = js.slice(js.indexOf('async function msUnverifiedGate'),
                   js.indexOf('async function msUnverifiedGate') + 1200);
g.includes('return true') ? ok('warning defaults to letting the buyer through')
                          : bad('msUnverifiedGate has no permissive default');
g.includes('catch(e){ return true; }')
  ? ok('a warning failure lets the buyer through, never blocks')
  : bad('warning failure could block a buyer — RUL-039 breach');

// 2 ── only an NPR pass may render the tick
const t = js.slice(js.indexOf('function msVerifiedTick'),
                   js.indexOf('function msVerifiedTick') + 700);
t.includes('state.green_tick') ? ok('tick keys off green_tick (NPR only)')
                               : bad('tick no longer keyed on green_tick');
/^[\s\S]*$/.test(t) && !t.includes('id_verified_at')
  ? ok('tick does not read the AI-check flag')
  : bad('tick reads the AI document check — that is not "verified"');

// 3 ── the stay warning must still name the deposit risk
g.includes('Never pay a deposit') ? ok('stay warning names the deposit risk')
                                  : bad('deposit warning removed');
g.includes('never holds deposits') ? ok('states we hold no deposits')
                                   : bad('no-deposits statement removed');

// 4 ── the seller card must be honest when the lane is down, and never charge
const c = js.slice(js.indexOf('async function msRenderIdVerifyCard'),
                   js.indexOf('async function msBuyIdVerification'));
c.includes('lane.available') ? ok('card checks lane availability before offering')
                             : bad('card offers a purchase without checking the lane');
c.includes('Nothing has been charged') ? ok('lane-down copy says nothing was charged')
                                       : bad('lane-down copy lost the no-charge reassurance');

// 5 ── 402 (insufficient Tuppence) must be handled, not thrown at the seller
const b = js.slice(js.indexOf('async function msBuyIdVerification'),
                   js.indexOf('async function msBuyIdVerification') + 1800);
b.includes('402') ? ok('insufficient-Tuppence handled explicitly')
                  : bad('402 not handled — seller would see a raw error');

// 6 ── styles exist for what the JS renders
['ms-id-tick','ms-idv','ms-idv-btn','ms-idv-field'].forEach(cl =>
  css.includes('.' + cl) ? ok('css present: .' + cl)
                         : bad('css missing for .' + cl + ' — renders unstyled'));

console.log(fail ? `\n${fail} FAILURE(S)` : '\nAll ID-NPR-5 UI guards pass');
process.exit(fail ? 1 : 0);
