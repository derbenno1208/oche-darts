// Erzeugt die Grafiken für den Play-Store-Eintrag nach store/:
// Symbol 512×512, Vorstellungsgrafik 1024×500 und je 6 Handy-Screenshots (1080×1920) auf Deutsch und Englisch.
// Voraussetzung: android/www/test.html (python3 tools/make_test_page.py) und ein Webserver auf Port 8765 in android/www.
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const R=path.join(__dirname,'..');const OUT=path.join(R,'store');const URL=process.env.OCHE_URL||'http://127.0.0.1:8765/test.html';
fs.mkdirSync(path.join(OUT,'screenshots','de'),{recursive:true});fs.mkdirSync(path.join(OUT,'screenshots','en'),{recursive:true});

// Beispielprofil für die Statistik-Ansicht (Werte im Rahmen eines Liga-Spielers)
function sampleStats(){
  const games=[];let t=Date.now()-30*864e5;
  for(let i=0;i<26;i++){t+=1.1*864e5;const avg=52+i*0.6+Math.sin(i*1.7)*7;const darts=60+Math.round(Math.random()*30);const pts=Math.round(avg*darts/3);const won=Math.sin(i*2.3)>-0.3;
    games.push({id:'s'+i,t,mode:'x01',sub:'501 · Double Out',won,draw:false,darts,opp:[{name:i%3?'Bot':'Lena',bot:i%3?4:0,won:!won}],
      x:{pts,n180:i%7===0?1:0,n140:i%3===0?1:0,n100:2+(i%3),high:i%7===0?180:140,best:i%5===0?15+(i%4):null,hiFin:[40,64,81,100,121][i%5],dd:9,dh:won?3:1,legs:won?3:1,f9p:Math.round((avg+9)*3),f9d:9,coA:[3,2,1],coH:[won?2:1,i%4===0?1:0,i%9===0?1:0]},
      pos:Array.from({length:12},()=>{const a=(Math.random()-.5)*0.55,r=103+(Math.random()-.5)*60;return[Math.round(r*Math.sin(a)),Math.round(-r*Math.cos(a))]})});}
  return {ben:{name:'Ben',games,ach:{first:t,win:t,g10:t,ton40:t,max:t,tonco:t,d15:t,a60:t,pro:t},daily:{'2026-10-30':1,'2026-10-31':1}}};
}

(async()=>{
  const b=await chromium.launch();
  // --- Symbol (vollflächig, Google rundet selbst ab) und Vorstellungsgrafik
  const pg=await b.newPage({viewport:{width:512,height:512}});
  const mark=`<circle r="19" fill="#1c1f1d" stroke="#9aa39e" stroke-width="1"/><circle r="15" fill="none" stroke="#d9473b" stroke-width="3"/><circle r="9" fill="none" stroke="#2f9e5f" stroke-width="2.5"/><circle r="3.2" fill="#d9473b"/>`;
  await pg.setContent(`<body style="margin:0"><svg width="512" height="512" viewBox="-30 -30 60 60"><rect x="-30" y="-30" width="60" height="60" fill="#0d1512"/><g transform="scale(1.15)">${mark}</g></svg></body>`);
  await pg.screenshot({path:path.join(OUT,'icon-512.png')});
  const fontsCss=fs.readFileSync(path.join(R,'android','www','fonts.css'),'utf8').replace(/url\(fonts\//g,'url('+URL.replace('test.html','fonts/'));
  for(const [lang,tag,sub] of [['de','Dart-Zähler','12 Spielmodi · Online mit Freunden · Profi-Caller · Statistik'],['en','Dart scorer','12 game modes · Play online with friends · Pro caller · Stats']]){
    await pg.setViewportSize({width:1024,height:500});
    await pg.goto(URL);
    await pg.setContent(`<html><head><style>${fontsCss}body{margin:0;width:1024px;height:500px;overflow:hidden;background:radial-gradient(900px 500px at 85% 20%,#1f4434,#0a1411 70%);font-family:Barlow,sans-serif;color:#f1e9d6}
      .w{position:absolute;inset:0;display:flex;align-items:center;gap:56px;padding:0 70px}
      h1{font-family:"Big Shoulders Display";font-weight:900;font-size:150px;line-height:.85;margin:0;letter-spacing:.01em}h1 span{color:#d9473b}
      .t{font-family:"Big Shoulders Display";font-weight:800;font-size:44px;text-transform:uppercase;color:#e6b34a;margin:10px 0 14px}
      p{font-size:25px;margin:0;color:#c9d2cc;max-width:560px;line-height:1.35}</style></head>
      <body><div class="w"><svg width="300" height="300" viewBox="-21 -21 42 42">${mark}</svg><div><h1>OCHE<span>.</span></h1><div class="t">${tag}</div><p>${sub}</p></div></div></body></html>`);
    await pg.waitForTimeout(400);await pg.screenshot({path:path.join(OUT,`feature-graphic-${lang}.png`)});
  }
  // --- Screenshots
  for(const lang of ['de','en']){
    const c=await b.newContext({viewport:{width:360,height:640},deviceScaleFactor:3,userAgent:'Mozilla/5.0 OcheApp/2.0 Play',colorScheme:'dark',locale:lang==='de'?'de-DE':'en-GB'});
    const p=await c.newPage();
    await p.addInitScript(([l,st])=>{if(!localStorage.getItem('oche.seeded')){localStorage.clear();localStorage.setItem('oche.seeded','1');localStorage.setItem('oche.lang',JSON.stringify(l));localStorage.setItem('oche.caller',JSON.stringify('off'));
      localStorage.setItem('oche.stats',JSON.stringify(st));localStorage.setItem('oche.cfg',JSON.stringify({mode:'x01',opts:{x01:{start:501,legs:3}},players:[{name:'Ben',bot:0},{name:'Bot',bot:4}]}))}},[lang,sampleStats()]);
    await p.goto(URL);await p.waitForTimeout(500);
    const shot=async n=>{await p.waitForTimeout(350);await p.screenshot({path:path.join(OUT,'screenshots',lang,n+'.png')})};
    await shot('1-start');
    // Spiel mit Checkout-Hinweis: Ben auf 121 bringen
    await p.click('#go');
    const dart=async(m,k)=>{if(m>1)await p.click(`[data-mult="${m}"]`);await p.click(`[data-k="${k}"]`)};
    const wait=()=>p.waitForFunction(()=>!document.querySelector('.input.locked'),{timeout:20000});
    await dart(3,20);await dart(3,20);await dart(3,20); await wait(); // 501 -> 321
    await dart(3,20);await dart(1,20);await dart(1,20); await wait(); // 100 -> 221
    await dart(3,20);await dart(1,20);await dart(1,20); await wait(); // 100 -> 121
    await p.waitForTimeout(1800);
    await p.evaluate(()=>document.querySelector('.active-panel').scrollIntoView({block:'start'}));await shot('2-x01-checkout');
    await p.click('[data-input=board]');await p.evaluate(()=>document.querySelector('#board').scrollIntoView({block:'center'}));await shot('3-scheibe');
    await p.click('[data-input=keys]');await p.click('#quit');await p.click('#qyes');
    await p.click('[data-tab=stats]');await shot('4-statistik');
    await p.evaluate(()=>{const e=document.querySelector('.chartwrap');e&&e.closest('section').scrollIntoView({block:'start'})});await shot('5-verlauf');
    // Turnier mit 4 Spielern
    await p.click('[data-tab=play]');await p.click('#addbot');await p.click('#addp');
    await p.click('[data-tab=tour]');await p.click('#tourNew');await shot('6-turnier');
    await c.close();
  }
  await b.close();console.log('Store-Grafiken erzeugt in',OUT);
})();
