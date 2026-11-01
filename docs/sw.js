/* Service Worker: hält App, Schriften und Caller-Stimmen offline bereit */
const CACHE="oche-2.0-b527f18299";
const ASSETS=["./", "index.html", "fonts.css", "peerjs.min.js", "manifest.webmanifest", "icon-192.png", "icon-512.png", "icon-maskable-512.png", "fonts/Barlow-400.woff2", "fonts/Barlow-500.woff2", "fonts/Barlow-600.woff2", "fonts/Barlow-700.woff2", "fonts/BarlowCondensed-500.woff2", "fonts/BarlowCondensed-600.woff2", "fonts/BarlowCondensed-700.woff2", "fonts/BigShouldersDisplay-600.woff2", "fonts/BigShouldersDisplay-800.woff2", "fonts/BigShouldersDisplay-900.woff2", "caller/de.json", "caller/de.mp3", "caller/en.json", "caller/en.mp3"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting()))});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener("fetch",e=>{
  const u=new URL(e.request.url);
  if(e.request.method!=="GET"||u.origin!==location.origin||/version\.json$|\.apk$/.test(u.pathname))return;
  e.respondWith(caches.match(e.request,{ignoreSearch:true}).then(r=>r||fetch(e.request).then(res=>{if(res.ok){const cp=res.clone();caches.open(CACHE).then(c=>c.put(e.request,cp))}return res})).catch(()=>caches.match("index.html")));
});
