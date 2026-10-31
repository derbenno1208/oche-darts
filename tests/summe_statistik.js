const {chromium}=require('playwright');
const OUT=require('path').join(__dirname,'out')+'/';require('fs').mkdirSync(OUT,{recursive:true});const URL=process.env.OCHE_URL||'http://127.0.0.1:8765/test.html';
const SP=''+OUT+'';
(async()=>{const b=await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});const c=await b.newContext({userAgent:'Mozilla/5.0 OcheApp',viewport:{width:400,height:860},deviceScaleFactor:2});const p=await c.newPage();
const errs=[];p.on('pageerror',e=>errs.push(e.stack));
await p.addInitScript(()=>{localStorage.setItem('oche.cfg',JSON.stringify({mode:'x01',opts:{x01:{start:301}},players:[{name:'Lena',bot:0},{name:'Max',bot:0}]}))});
await p.goto(''+URL+'');
await p.click('#go');await p.click('[data-input="sum"]');
const enter=async v=>{for(const ch of String(v))await p.click(`[data-num="${ch}"]`);await p.click('[data-num="ok"]')};
const score=()=>p.$eval('.strip',e=>e.innerText.replace(/\s+/g,' '));
await enter(100);await enter(60);           // L 201, M 241
await p.click('[data-sumq="140"]');         // L 61 -> 2-dart checkout exists? 61 needs 2 darts (T15 D8 / 25 D18) -> double dialog
console.log('dialog after 140?',!!await p.$('.overlay'));
if(await p.$('.overlay'))await p.click('.overlay [data-dd="0"]');
await enter(180);                             // M 61
console.log('dialog?',!!await p.$('.overlay'));if(await p.$('.overlay'))await p.click('.overlay [data-dd="0"]');
await p.screenshot({path:SP+'sum.png'});
await enter(61);                              // L checkout 61
console.log('checkout dialog:',await p.$eval('.overlay h3',e=>e.textContent));
await p.click('.overlay [data-nd="3"]');await p.click('.overlay [data-dd="2"]');await p.click('#adok');
await p.waitForSelector('.winner');console.log('winner',await p.$eval('.wn',e=>e.textContent));
console.log(await p.$eval('.stats',e=>e.innerText.replace(/\s+/g,' ')));
// caller pro loaded?
await p.waitForTimeout(1500);console.log('pro caller en ready:',await p.evaluate(()=>!!(window.__ocheCaller.en&&window.__ocheCaller.en.ready)));
// second game: per-dart to get a chart point; then stats view
await p.click('#again');await p.click('[data-input="keys"]');
for(const pl of [0,1,0,1,0]){for(let i=0;i<3;i++){await p.click('[data-mult="3"]');await p.click('[data-k="20"]')}}
// Lena at 301-360? 301: 180,  M 121... just end game by quitting? play until finish: Lena 301-180=121, then T20 S11 D25
await p.waitForTimeout(200);console.log(await score());
await p.click('#quit');await p.click('#qyes');
await p.click('[data-tab=stats]');await p.waitForSelector('.statsview');
console.log('kpis:',await p.$eval('.kpis',e=>e.innerText.replace(/\s+/g,' ')));
await p.screenshot({path:SP+'stats.png',fullPage:true});
// landscape phone
await p.setViewportSize({width:860,height:400});await p.click('[data-tab=play]');await p.click('#go');
for(let i=0;i<2;i++){await p.click('[data-mult="3"]');await p.click('[data-k="20"]')}
await p.screenshot({path:SP+'land.png'});
console.log('overflowX',await p.evaluate(()=>document.documentElement.scrollWidth));
console.log('errors',errs);await b.close()})();
