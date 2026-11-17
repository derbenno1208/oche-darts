"""Baut die Web-Version für GitHub Pages nach docs/: installierbar (Manifest, Service Worker), mit Online-Spiel,
Versionsdatei für den Update-Hinweis der App und der aktuellen APK zum Herunterladen.
Aufruf: python3 tools/build_web.py VERSION CODE "Neuerung 1" "Neuerung 2" ..."""
import os, sys, json, shutil, hashlib, subprocess, datetime
from app_html import ROOT as R, SITE, read_source, web_page, description
WWW = os.path.join(R, "android", "www"); OUT = os.path.join(R, "docs")
version = sys.argv[1] if len(sys.argv) > 1 else "0"; code = int(sys.argv[2]) if len(sys.argv) > 2 else 0; notes = sys.argv[3:]
source = read_source()
html = web_page(source)
if os.path.isdir(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(html)
for f in ["peerjs.min.js", "fonts.css"]: shutil.copy(os.path.join(WWW, f), OUT)
for d in ["fonts", "caller"]: shutil.copytree(os.path.join(WWW, d), os.path.join(OUT, d))
subprocess.run(["node", os.path.join(R, "android", "icon.js"), "web", OUT], check=True, cwd=os.path.join(R, "android"))
json.dump({"name": "Oche Darts", "short_name": "Oche", "start_url": "./", "scope": "./", "display": "standalone", "orientation": "any",
           "background_color": "#0d1512", "theme_color": "#0d1512", "lang": "de",
           "description": description(source),
           "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
                     {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]},
          open(os.path.join(OUT, "manifest.webmanifest"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
assets = ["./", "index.html", "fonts.css", "peerjs.min.js", "manifest.webmanifest", "icon-192.png", "icon-512.png", "icon-maskable-512.png"]
assets += ["fonts/" + f for f in sorted(os.listdir(os.path.join(OUT, "fonts")))] + ["caller/" + f for f in sorted(os.listdir(os.path.join(OUT, "caller")))]
h = hashlib.sha1(html.encode()).hexdigest()[:10]
open(os.path.join(OUT, "sw.js"), "w", encoding="utf-8").write(f"""/* Service Worker: hält App, Schriften und Caller-Stimmen offline bereit */
const CACHE="oche-{version}-{h}";
const ASSETS={json.dumps(assets)};
self.addEventListener("install",e=>{{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting()))}});
self.addEventListener("activate",e=>{{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))}});
self.addEventListener("fetch",e=>{{
  const u=new URL(e.request.url);
  if(e.request.method!=="GET"||u.origin!==location.origin||/version\\.json$|\\.apk$/.test(u.pathname))return;
  e.respondWith(caches.match(e.request,{{ignoreSearch:true}}).then(r=>r||fetch(e.request).then(res=>{{if(res.ok){{const cp=res.clone();caches.open(CACHE).then(c=>c.put(e.request,cp))}}return res}})).catch(()=>caches.match("index.html")));
}});
""")
apk = os.path.join(R, "OcheDarts.apk")
if os.path.exists(apk): shutil.copy(apk, os.path.join(OUT, "OcheDarts.apk"))
json.dump({"version": version, "code": code, "apk": SITE + "OcheDarts.apk", "date": datetime.date.today().isoformat(), "notes": notes},
          open(os.path.join(OUT, "version.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open(os.path.join(OUT, ".nojekyll"), "w").write("")
for f in os.listdir(os.path.join(R, "web")): shutil.copy(os.path.join(R, "web", f), OUT)  # z. B. Datenschutzerklärung
print("docs/ gebaut:", sorted(os.listdir(OUT)))
