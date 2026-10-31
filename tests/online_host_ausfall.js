const {chromium}=require('playwright');
const OUT=require('path').join(__dirname,'out')+'/';require('fs').mkdirSync(OUT,{recursive:true});const URL=process.env.OCHE_URL||'http://127.0.0.1:8765/test.html';
const log=(...a)=>console.log(new Date().toISOString().slice(14,19),...a);
(async()=>{const b=await chromium.launch();
const ctxs={};
const mk=async(n)=>{const c=await b.newContext({userAgent:'Mozilla/5.0 OcheApp',viewport:{width:420,height:900}});ctxs[n]=c;const p=await c.newPage();p.on('pageerror',e=>log(n,'ERR',e.message));await p.goto(''+URL+'');return p};
const H=await mk('host'),A=await mk('anna'),B=await mk('bob'),S=await mk('spec');
const strip=p=>p.$eval('.strip',e=>e.innerText.replace(/\s+/g,' ')).catch(()=>'(no strip)');
const status=p=>p.evaluate(()=>document.querySelector('.waitmsg')?.innerText||'');
const canPlay=p=>p.evaluate(()=>!!document.querySelector('.input')&&!document.querySelector('.input.locked'));
// host setup: just "Ben" human, remove second player (Bot)
await H.click('[data-del="1"]');
await H.click('[data-tab=online]');await H.click('#hostRoom');await H.waitForSelector('.roomcode',{timeout:30000});const code=await H.$eval('.roomcode',e=>e.textContent);await H.click('[data-tab=play]');log('room',code);
const join=async(p,name,spect)=>{await p.click('[data-tab=online]');await p.fill('#joinName',name);await p.fill('#joinCode',code);if(spect)await p.check('#joinSpect');await p.click('#joinRoom');await p.waitForSelector('.lobby h2',{timeout:30000})};
await join(A,'Anna');await join(B,'Bob');await H.waitForFunction(()=>[...document.querySelectorAll('.prow input')].filter(i=>i.value==='Anna'||i.value==='Bob').length===2,{timeout:15000});
await join(S,'Zoe',true);await H.waitForTimeout(500);

await H.click('#go');await A.waitForSelector('.hero');await S.waitForSelector('.hero');log('started; spectator msg:',await status(S));
const play=async(rounds)=>{for(let i=0;i<rounds;i++){for(const p of [H,A,B]){if(await canPlay(p)){await p.click('[data-mult="3"]');await p.click('[data-k="20"]');break}}await H.waitForTimeout(200)}};
await play(9);log('after 9 darts H:',await strip(H));
// 1) Anna reloads the app mid game
await A.reload();log('anna reloaded');await A.waitForFunction(()=>document.body.innerText.includes('Wieder verbunden')||document.querySelector('.strip'),{timeout:30000});
await A.waitForTimeout(3000);log('anna strip after reload:',await strip(A));
await play(6);log('after 6 more H:',await strip(H));log('A:',await strip(A));
// 2) Host dies hard
await ctxs.host.close();log('HOST KILLED');
const t0=Date.now();
let newHost=null;
for(let i=0;i<60&&!newHost;i++){await A.waitForTimeout(500);for(const [n,p] of [['anna',A],['bob',B],['spec',S]]){const r=await p.evaluate(()=>document.querySelector('.tools .badge')?.textContent||'');if(r.includes('Host'))newHost=n}}
log('new host:',newHost,'after',Math.round((Date.now()-t0)/1000),'s');
for(let i=0;i<40;i++){const w=await B.evaluate(()=>document.querySelector('.tools .badge')?.className||'');const w2=await S.evaluate(()=>document.querySelector('.tools .badge')?.className||'');if(!w.includes('gold')&&!w2.includes('gold'))break;await A.waitForTimeout(500)}log('all reconnected, since kill',Math.round((Date.now()-t0)/1000),'s');
for(const [n,p] of [['anna',A],['bob',B],['spec',S]])log(n,'badge',await p.evaluate(()=>document.querySelector('.tools .badge')?.innerText),'| wait:',await status(p));
for(let i=0;i<9;i++){for(const p of [A,B]){if(await canPlay(p)){await p.click('[data-mult="3"]');await p.click('[data-k="20"]');break}}await A.waitForTimeout(250)}
log('A:',await strip(A));log('B:',await strip(B));log('S:',await strip(S));
await b.close()})();
