"""Baut die Web-Version für GitHub Pages nach docs/ (gleiche App wie in der APK, inklusive Online-Spiel)."""
import os, re, shutil
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WWW = os.path.join(R, "android", "www"); OUT = os.path.join(R, "docs")
s = open(os.path.join(R, "src", "oche.html")).read()
s = re.sub(r'<link rel="preconnect"[^>]*>\n', '', s)
s = re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>\n', '', s)
s = s.replace('<!--APP-HEAD-->', '<link rel="stylesheet" href="fonts.css">\n<link rel="icon" href="icon.png">\n<meta name="theme-color" content="#0d1512">\n<meta name="description" content="Oche Darts: Dart-Zähler mit 12 Spielmodi, Online-Spiel, Turnieren und Profi-Caller.">\n<script src="peerjs.min.js"></script>')
head = ('<!doctype html>\n<html lang="de"><head><meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font-size:14px}img{max-width:100%}[hidden]{display:none!important}button,a{-webkit-tap-highlight-color:transparent}</style>\n')
i = s.index('<div class="wrap"')
if os.path.isdir(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
open(os.path.join(OUT, "index.html"), "w").write(head + s[:i] + '</head><body>\n' + s[i:] + '</body></html>\n')
for f in ["peerjs.min.js", "fonts.css"]: shutil.copy(os.path.join(WWW, f), OUT)
for d in ["fonts", "caller"]: shutil.copytree(os.path.join(WWW, d), os.path.join(OUT, d))
shutil.copy(os.path.join(R, "android", "res", "mipmap-xxxhdpi", "ic_launcher.png"), os.path.join(OUT, "icon.png"))
open(os.path.join(OUT, ".nojekyll"), "w").write("")
print("docs/ gebaut:", sorted(os.listdir(OUT)))
