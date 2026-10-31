const {chromium}=require('playwright');
const OUT=require('path').join(__dirname,'out')+'/';require('fs').mkdirSync(OUT,{recursive:true});const URL=process.env.OCHE_URL||'http://127.0.0.1:8765/test.html';
(async()=>{const b=await chromium.launch();const c=await b.newContext({userAgent:'Mozilla/5.0 OcheApp',viewport:{width:1200,height:900}});const pg=await c.newPage();
const errs=[];pg.on('pageerror',e=>errs.push(e.stack));
await pg.addInitScript(()=>{window.OCHE_FAST=0.004;if(!localStorage.getItem('oche.cfg'))localStorage.setItem('oche.cfg',JSON.stringify({mode:'x01',opts:{x01:{sets:2,legs:2}},players:[{name:'A',bot:4},{name:'B',bot:6},{name:'C',bot:2}]}))});
await pg.goto(''+URL+'');
for(const mode of ['x01','cricket','atc','shanghai','killer','bobs27','halveit','highscore','c121','gotcha','doubles','scram']){
 await pg.click('#modePick');await pg.click(`[data-mode=${mode}]`);
 if(mode==='scram') await pg.click('[data-del="2"]');
 await pg.click('#go');
 try{await pg.waitForSelector('.winner',{timeout:180000});console.log(mode,'|',await pg.$eval('.wn',e=>e.textContent),'|',await pg.$eval('.stats tbody',e=>e.innerText.replace(/\s+/g,' ').slice(0,150)));}catch(e){console.log(mode,'TIMEOUT')}
 await pg.click('#menu').catch(()=>{});
}
console.log('errors',errs);await b.close()})();
