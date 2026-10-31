"""Erzeugt android/www/test.html aus src/oche.html für die Browser-Tests (mit lokalem PeerJS)."""
import os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s=open(os.path.join(R,"src","oche.html")).read().replace("<!--APP-HEAD-->",'<script src="peerjs.min.js"></script>')
open(os.path.join(R,"android","www","test.html"),"w").write('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>[hidden]{display:none!important}body{margin:0}</style>'+s+"</html>")
print("android/www/test.html erzeugt")
