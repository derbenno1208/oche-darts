const {chromium}=require('playwright');const SP=''+OUT+'';
const OUT=require('path').join(__dirname,'out')+'/';require('fs').mkdirSync(OUT,{recursive:true});const URL=process.env.OCHE_URL||'http://127.0.0.1:8765/test.html';
(async()=>{const b=await chromium.launch();const c=await b.newContext({userAgent:'Mozilla/5.0 OcheApp',viewport:{width:390,height:844},deviceScaleFactor:2});const p=await c.newPage();
const errs=[];p.on('pageerror',e=>errs.push(e.stack));
await p.addInitScript(()=>{if(!localStorage.getItem('oche.cfg'))localStorage.setItem('oche.cfg',JSON.stringify({mode:'x01',opts:{x01:{start:301}},players:[{name:'Anna',bot:5},{name:'Bert',bot:4},{name:'Cleo',bot:3},{name:'Dirk',bot:2},{name:'Emil',bot:6}]}));localStorage.setItem('oche.caller',JSON.stringify('off'))});
await p.goto(''+URL+'');
// Checkout-Hinweis 61
// KO-Turnier mit 5 Bots
await p.click('[data-tab=tour]');await p.screenshot({path:SP+'tour_setup.png'});
await p.click('#tourNew');
let games=0;
while(games<10){
  const btn=await p.$('[data-tm]');if(!btn)break;
  await btn.click();await p.waitForSelector('.winner',{timeout:120000});games++;
  await p.click('#toTour');
}
console.log('KO Spiele:',games,'Sieger:',await p.$eval('.champ b',e=>e.textContent).catch(()=>'kein'));
await p.screenshot({path:SP+'tour_ko.png',fullPage:true});
// Liga mit 3
await p.click('#tourEnd');
await p.click('[data-tab=play]');for(let i=0;i<2;i++)await p.click('[data-del="3"]');
await p.click('[data-tab=tour]');await p.click('[data-tourtype=league]');await p.click('#tourNew');
games=0;while(games<10){const btn=await p.$('[data-tm]');if(!btn)break;await btn.click();await p.waitForSelector('.winner',{timeout:120000});games++;await p.click('#toTour')}
console.log('Liga Spiele:',games,'Sieger:',await p.$eval('.champ b',e=>e.textContent).catch(()=>'kein'));
console.log(await p.$eval('.stats tbody',e=>e.innerText.replace(/\s+/g,' ')));
await p.screenshot({path:SP+'tour_league.png',fullPage:true});
// Settings: Lieblingsdoppel + Backup
await p.click('[data-tab=settings]');await p.click('[data-prefdbl="16"]');
await p.screenshot({path:SP+'settings2.png',fullPage:true});
await p.click('#bkExport');await p.waitForTimeout(400);
const txt=await p.evaluate(()=>{const t=document.querySelector('#bktxt');return t?t.value:null});
console.log('Backup-Text Länge',txt&&txt.length);
if(await p.$('#bkok'))await p.click('#bkok');
// Import: Statistik löschen, dann Backup einspielen
const before=await p.evaluate(()=>Object.keys(JSON.parse(localStorage.getItem('oche.stats')||'{}')).length);
await p.evaluate(()=>{localStorage.removeItem('oche.stats')});
require('fs').writeFileSync(SP+'bk.json',txt||'');
await p.setInputFiles('#bkFile',SP+'bk.json');await p.waitForSelector('#ibyes');console.log('Dialog:',await p.$eval('.dialog .rules',e=>e.textContent));
await p.click('#ibyes');await p.waitForTimeout(1500);
const after=await p.evaluate(()=>Object.keys(JSON.parse(localStorage.getItem('oche.stats')||'{}')).length);
console.log('Profile vorher',before,'nach Import',after,'prefdbl',await p.evaluate(()=>localStorage.getItem('oche.prefdbl')));
// Checkout-Vorschlag mit Lieblingsdoppel 16 bei 64 / 61
await p.click('[data-tab=play]');
console.log('errors',errs);await b.close()})();
