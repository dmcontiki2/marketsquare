// prove_audit_b3_app.js -- AUDIT-4OCT Batch 3 (4 Oct 2026): runs the shipped ms.js price, Adventures-chip, currency and
// trust-category functions in Node and checks their answers. Run: node scripts/prove_audit_b3_app.js ms.js
const fs=require('fs'), vm=require('vm');
const src=fs.readFileSync(process.argv[2],'utf8');
function grab(name){ const i=src.indexOf('function '+name+'('); if(i<0) throw new Error('no '+name); let d=0,j=src.indexOf('{',i); for(let k=j;k<src.length;k++){ if(src[k]==='{')d++; else if(src[k]==='}'){d--; if(!d) return src.slice(i,k+1);} } }
function grabConst(name){ const i=src.indexOf('const '+name+' = ['); const j=src.indexOf('];',i); return src.slice(i,j+2); }
const ctx={console}; vm.createContext(ctx);
vm.runInContext(['_lmEsc','_priceIsCompound','_msPriceNum','formatZAR','_advCatKey','aaCurrency','_elTrustCat'].map(grab).join('\n')
  + '\n' + grabConst('ADV_EXP_CATS') + grabConst('ADV_ACCOM_CATS') + grabConst('_ADV_EXP_RULES') + grabConst('_ADV_ACC_RULES')
  + "\nconst ADV_COUNTRY_CURRENCY = { ZA:'R', NA:'N$', MZ:'MT', BW:'P', KE:'KSh', US:'$', CA:'CA$', GB:'£', DE:'€', EU:'€', AU:'A$', NZ:'NZ$' }; var activeCountry={iso2:'KE'};", ctx);
const t=(e)=>vm.runInContext(e,ctx);
for (const p of ['R85 000 (2019 model)','R1.5 million','R850k','R99,99','R 1 250 000,00','R450 per day (min 2 days)','R1 200']) console.log('formatZAR', JSON.stringify(p), '->', t('formatZAR('+JSON.stringify(p)+')'));
console.log('price for batch', t("String(_msPriceNum({price:'R1,200-R1,500'})||'')"));
for (const l of [{activity_type:'Wildlife & Birding',title:'Big 5 drive'},{title:'Blue Train to Cape Town'},{activity_type:'Water Sports'},{experience_type:'luxury_safari'}]) console.log('exp', JSON.stringify(l), '->', t('_advCatKey('+JSON.stringify(l)+', false)'));
for (const l of [{accommodation_type:'Guest House'},{accommodation_type:'Chalet'},{accommodation_type:'Caravan / Camp site'},{accommodation_type:'Bush Camp'}]) console.log('acc', JSON.stringify(l), '->', t('_advCatKey('+JSON.stringify(l)+', true)'));
console.log('currency KE', JSON.stringify(t('aaCurrency()'))); t("activeCountry={iso2:'FR'}"); console.log('currency FR', JSON.stringify(t('aaCurrency()')));
console.log('trust', t("_elTrustCat('Services',{service_class:'casual'})"), t("_elTrustCat('Adventures',{category:'adventures_accommodation'})"), t("_elTrustCat('Property',{})"));
const want=[['formatZAR("R85 000 (2019 model)")','R85,000'],['formatZAR("R1.5 million")','R1,500,000'],['formatZAR("R99,99")','R99.99'],['formatZAR("R1 200")','R1,200'],
 ["String(_msPriceNum({price:'R1,200-R1,500'}))",'1200'],["_advCatKey({activity_type:'Wildlife & Birding'},false)",'luxury_safari'],["_advCatKey({accommodation_type:'Guest House'},true)",'boutique_hotel'],
 ["_elTrustCat('Services',{service_class:'casual'})",'Services-Casuals']];
t("activeCountry={iso2:'KE'}"); want.push(['aaCurrency().symbol','KSh']);
let bad=want.filter(([e,v])=>String(t(e))!==v);
if(bad.length){ console.log('RESULT: FAIL', JSON.stringify(bad)); process.exit(1); } console.log('RESULT: OK');
