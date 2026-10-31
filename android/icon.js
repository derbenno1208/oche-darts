// Erzeugt das App-Icon aus dem Oche-Ringlogo (Legacy-PNG + adaptive Ebenen)
const {chromium}=require('playwright');
const BG='#0d1512';
// Logo wie in der App: viewBox -20..20
const mark=`<circle r="19" fill="#1c1f1d" stroke="#9aa39e" stroke-width="1"/><circle r="15" fill="none" stroke="#d9473b" stroke-width="3"/><circle r="9" fill="none" stroke="#2f9e5f" stroke-width="2.5"/><circle r="3.2" fill="#d9473b"/>`;
(async()=>{const b=await chromium.launch();const p=await b.newPage();
const out=process.argv[2]||'res';
const sizes={mdpi:[48,108],hdpi:[72,162],xhdpi:[96,216],xxhdpi:[144,324],xxxhdpi:[192,432]};
const shot=async(w,svg,path)=>{await p.setViewportSize({width:w,height:w});await p.setContent(`<body style="margin:0;background:transparent">${svg}</body>`);await p.screenshot({path,omitBackground:true})};
// Legacy-Icon: abgerundetes Quadrat, Logo groß
const legacy=w=>`<svg width="${w}" height="${w}" viewBox="-24 -24 48 48"><rect x="-23" y="-23" width="46" height="46" rx="10.5" fill="${BG}"/><g transform="scale(.9)">${mark}</g></svg>`;
// Adaptiver Vordergrund: Logo innerhalb der sicheren Zone (66 von 108 dp)
const fg=w=>`<svg width="${w}" height="${w}" viewBox="-54 -54 108 108"><g transform="scale(1.74)">${mark}</g></svg>`;
const bgOnly=w=>`<svg width="${w}" height="${w}" viewBox="0 0 10 10"><rect width="10" height="10" fill="${BG}"/></svg>`;
if(out==='web'){
  const dir=process.argv[3];
  await shot(192,legacy(192),dir+'/icon-192.png');await shot(512,legacy(512),dir+'/icon-512.png');
  await shot(512,`<svg width="512" height="512" viewBox="-30 -30 60 60"><rect x="-30" y="-30" width="60" height="60" fill="${BG}"/><g transform="scale(.95)">${mark}</g></svg>`,dir+'/icon-maskable-512.png');
} else if(out==='preview'){
  await shot(512,legacy(512),process.argv[3]+'/big.png');
  await p.setViewportSize({width:512,height:512});
  await p.setContent(`<body style="margin:0;background:#888"><div style="width:512px;height:512px;border-radius:50%;overflow:hidden;position:relative">${bgOnly(512).replace('<svg','<svg style="position:absolute"')}${fg(512).replace('<svg','<svg style="position:absolute"')}</div></body>`);
  await p.screenshot({path:process.argv[3]+'/adaptive.png'});
} else for(const [d,[l,f]] of Object.entries(sizes)){
  await shot(l,legacy(l),`${out}/mipmap-${d}/ic_launcher.png`);
  await shot(f,fg(f),`${out}/mipmap-${d}/ic_fg.png`);
  await shot(f,bgOnly(f),`${out}/mipmap-${d}/ic_bg.png`);
}
await b.close()})();
