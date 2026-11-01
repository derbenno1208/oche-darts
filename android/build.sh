#!/bin/bash
# Baut Oche Darts mit Gradle.
#   ./build.sh          → OcheDarts.apk  (Fassung "github": werbefrei, eigener Update-Hinweis)
#   ./build.sh play     → OcheDarts.aab  (Fassung "play": Werbung nach dem Spiel, Freikauf über Google Play)
#   ./build.sh both     → beides
# Umgebungsvariablen: SDK (Android-SDK-Ordner, Standardaufbau mit platforms/ und build-tools/),
#                     VERSION_CODE, VERSION_NAME, HTML (Pfad zur App-Datei, Standard ../src/oche.html)
set -e
cd "$(dirname "$0")"
SDK=${SDK:?Bitte SDK=/pfad/zum/android-sdk setzen (siehe README)}
HTML=${HTML:-../src/oche.html}
WHAT=${1:-apk}
echo "sdk.dir=$SDK" > local.properties
[ -f app/oche-release.jks ] || { echo "Signierschlüssel app/oche-release.jks fehlt (aus dem Backup kopieren)."; exit 1; }

# Web-App einbauen: lokale Schriften und PeerJS statt Google Fonts/CDN
OUT=app/build/generated/oche-assets/www
rm -rf app/build/generated/oche-assets && mkdir -p $OUT
HTML="$HTML" OUT="$OUT" python3 - <<'PY'
import os,re
s=open(os.environ["HTML"]).read()
s=re.sub(r'<link rel="preconnect"[^>]*>\n','',s)
s=re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>\n','',s)
s=s.replace('<!--APP-HEAD-->','<link rel="stylesheet" href="fonts.css">\n<script src="peerjs.min.js"></script>')
head='<!doctype html>\n<html lang="de"><head><meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no">\n<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font-size:14px}img{max-width:100%}[hidden]{display:none!important}button,a{-webkit-tap-highlight-color:transparent}</style>\n'
i=s.index('<div class="wrap"')
open(os.path.join(os.environ["OUT"],'index.html'),'w').write(head+s[:i]+'</head><body>\n'+s[i:]+'</body></html>\n')
PY
cp www/peerjs.min.js www/fonts.css $OUT/ && cp -r www/fonts www/caller $OUT/

PROPS=""
[ -n "$VERSION_CODE" ] && PROPS="$PROPS -PocheVersionCode=$VERSION_CODE"
[ -n "$VERSION_NAME" ] && PROPS="$PROPS -PocheVersionName=$VERSION_NAME"
TASKS=""
[ "$WHAT" = "apk" -o "$WHAT" = "both" ] && TASKS="$TASKS :app:assembleGithubRelease"
[ "$WHAT" = "play" -o "$WHAT" = "both" ] && TASKS="$TASKS :app:bundlePlayRelease"
gradle --console=plain -q $PROPS $TASKS
[ -f app/build/outputs/apk/github/release/app-github-release.apk ] && [ "$WHAT" != "play" ] && cp app/build/outputs/apk/github/release/app-github-release.apk ../OcheDarts.apk && echo "→ OcheDarts.apk"
[ -f app/build/outputs/bundle/playRelease/app-play-release.aab ] && [ "$WHAT" != "apk" ] && cp app/build/outputs/bundle/playRelease/app-play-release.aab ../OcheDarts.aab && echo "→ OcheDarts.aab"
