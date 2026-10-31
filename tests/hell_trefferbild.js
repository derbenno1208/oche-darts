const {chromium}=require('playwright');const SP=''+OUT+'';
const OUT=require('path').join(__dirname,'out')+'/';require('fs').mkdirSync(OUT,{recursive:true});const URL=process.env.OCHE_URL||'http://127.0.0.1:8765/test.html';
(async()=>{const b=await chromium.launch();
const c=await b.newContext({userAgent:'Mozilla/5.0 OcheApp',viewport:{width:390,height:844},deviceScaleFactor:2,colorScheme:'light'});const p=await c.newPage();
const errs=[];p.on('pageerror',e=>errs.push(e.stack));
await p.addInitScript(()=>{if(!localStorage.getItem('oche.cfg'))localStorage.setItem('oche.cfg',JSON.stringify({mode:'x01',opts:{x01:{start:301}},players:[{name:'Lena',bot:0},{name:'Bot',bot:1}]}));localStorage.setItem('oche.caller',JSON.stringify('off'))});
await p.goto(''+URL+'');
console.log('bg light:',await p.evaluate(()=>getComputedStyle(document.body).backgroundColor));
await p.screenshot({path:SP+'light_play.png'});
// Spiel per Scheibe: Lena wirft auf T20-Region, um Trefferbild zu erzeugen
await p.click('#go');await p.click('[data-input=board]');
const toPx=async(mx,my)=>{const box=await p.$eval('#board',e=>{e.scrollIntoView({block:'center'});const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width}});return {x:box.x+(mx+225)/450*box.w,y:box.y+(my+225)/450*box.w}};
let guard=0;
while(!(await p.$('.winner'))&&guard++<400){
  const mine=await p.evaluate(()=>!!document.querySelector('.input')&&!document.querySelector('.input.locked'));
  if(mine){const rest=await p.$eval('.hero',e=>parseInt(e.textContent));
    let tgt=[0,-103]; // T20
    if(rest<=40&&rest%2===0){const n=rest/2;const ORDER=[20,1,18,4,13,6,10,15,2,17,3,19,7,16,8,11,14,9,12,5];const i=ORDER.indexOf(n);if(i>=0){const a=i*18*Math.PI/180;tgt=[166*Math.sin(a),-166*Math.cos(a)]}}
    else if(rest<60){const ORDER=[20,1,18,4,13,6,10,15,2,17,3,19,7,16,8,11,14,9,12,5];const n=Math.min(20,rest-32>0?rest-32:1);const i=ORDER.indexOf(n);const a=i*18*Math.PI/180;tgt=[134*Math.sin(a),-134*Math.cos(a)]}
    const q=await toPx(tgt[0]+(Math.random()-.5)*14,tgt[1]+(Math.random()-.5)*14);await p.mouse.click(q.x,q.y);
  } else await p.waitForTimeout(150);
}
await p.screenshot({path:SP+'light_result.png',fullPage:true});
console.log('Neue Erfolge:',await p.$eval('.newach',e=>e.innerText.replace(/\s+/g,' ')).catch(()=>'keine'));
await p.click('#menu');await p.click('[data-tab=stats]');
console.log('KPI:',await p.$eval('.kpis',e=>e.innerText.replace(/\s+/g,' ')));
console.log('Checkout-Balken:',await p.$eval('.cobars',e=>e.innerText.replace(/\s+/g,' ')).catch(()=>'fehlt'));
console.log('Top-Felder:',await p.$eval('.topfields',e=>e.innerText.replace(/\s+/g,' ')).catch(()=>'fehlt'));
await p.screenshot({path:SP+'light_stats.png',fullPage:true});
// Dunkel erzwingen über Optionen
await p.click('[data-tab=settings]');await p.click('[data-theme-set=dark]');
console.log('bg dark forced:',await p.evaluate(()=>getComputedStyle(document.body).backgroundColor));
await p.click('[data-theme-set=system]');
// Großanzeige quer
await p.setViewportSize({width:1280,height:720});await p.click('[data-tab=play]');await p.click('#go');await p.click('#tvBtn');
await p.screenshot({path:SP+'tv.png'});
console.log('errors',errs);await b.close()})();
