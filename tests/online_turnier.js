const {chromium}=require('playwright');
const OUT=require('path').join(__dirname,'out')+'/';require('fs').mkdirSync(OUT,{recursive:true});const URL=process.env.OCHE_URL||'http://127.0.0.1:8765/test.html';
const log=(...a)=>console.log(new Date().toISOString().slice(14,19),...a);
(async()=>{const b=await chromium.launch();
const mk=async(n)=>{const c=await b.newContext({userAgent:'Mozilla/5.0 OcheApp',viewport:{width:420,height:900}});const p=await c.newPage();p.on('pageerror',e=>log(n,'ERR',e.message));
 await p.addInitScript(()=>{localStorage.setItem('oche.caller',JSON.stringify('off'));localStorage.setItem('oche.cfg',JSON.stringify({mode:'x01',opts:{x01:{start:101}},players:[{name:'Ben',bot:0}]}))});
 await p.goto(''+URL+'');return p};
const H=await mk('host'),A=await mk('anna'),B=await mk('bob');
await H.click('[data-tab=online]');await H.click('#hostRoom');await H.waitForSelector('.roomcode',{timeout:30000});const code=await H.$eval('.roomcode',e=>e.textContent);
for(const [p,n] of [[A,'Anna'],[B,'Bob']]){await p.click('[data-tab=online]');await p.fill('#joinName',n);await p.fill('#joinCode',code);await p.click('#joinRoom');await p.waitForSelector('.lobby h2',{timeout:30000})}
await H.waitForFunction(()=>[...document.querySelectorAll('.prow input')].length===3,{timeout:15000}).catch(()=>{});
await H.click('[data-tab=tour]');await H.click('[data-tourtype=league]');await H.click('#tourNew');
await A.waitForSelector('.lobbytour',{timeout:15000});log('Gast sieht Turnier:',(await A.$eval('.lobbytour',e=>e.innerText.replace(/\s+/g,' '))).slice(0,120));
const pages={host:H,anna:A,bob:B};
for(let m=0;m<3;m++){
  await H.click('[data-tab=tour]');const btn=await H.$('[data-tm]');if(!btn)break;await btn.click();
  for(let i=0;i<80;i++){
    if(await H.$('.winner'))break;
    for(const p of [H,A,B]){const can=await p.evaluate(()=>!!document.querySelector('.input')&&!document.querySelector('.input.locked'));
      if(can){const rest=await p.$eval('.hero',e=>parseInt(e.textContent));
        if(rest===101){await p.click('[data-mult="3"]');await p.click('[data-k="17"]')}   // 51 -> 50
        else if(rest===50){await p.click('[data-mult="2"]');await p.click('[data-k="25"]')}
        else {await p.click('[data-k="0"]')}
        break}}
    await H.waitForTimeout(150);
  }
  log('Spiel',m+1,'Sieger:',await H.$eval('.wn',e=>e.textContent).catch(()=>'?'));
  await H.click('#toTour');
}
await A.waitForTimeout(1500);
log('Host Tabelle:',await H.$eval('.stats tbody',e=>e.innerText.replace(/\s+/g,' ')).catch(()=>'-'));
log('Gast Tabelle:',await A.$eval('.lobbytour .stats tbody',e=>e.innerText.replace(/\s+/g,' ')).catch(()=>'-'));
log('Champion beim Gast:',await A.$eval('.lobbytour .champ b',e=>e.textContent).catch(()=>'-'));
await b.close()})();
